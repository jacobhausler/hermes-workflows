#!/usr/bin/env python3
"""pin_delta_check.py contract (revalidation-133387 rv3: the re-pin lane must scan
the CODE DELTA between the old vendor pin and the new one for NEW host effects).

The catalog entry pins a commit SHA; a re-pin moves it old->new via a PR, and today
nothing reads the code the new pin installs — a post-exit hook handing a node-
registered script to launchd (launchctl submit/bootstrap/load -w, RunAtLoad plist,
no teardown) rode in through our own re-pin and cost a maintainer round. The gate:
git diff <old>..<new>, added lines of code-suffixed files only, detectors for
launchctl / launchd plist keys / systemd / cron / detach-daemonize / fixed-path
writes outside the run dir (fixed /tmp paths, ~/Library/LaunchAgents, autostart,
/etc/init.d, shell rc files), and AST-proven module-level (import-time) sys.path
mutation. est-gbim law: `git diff -z --name-status` records take BOTH endpoints of
R (rename) and C (copy). Fail-closed: git failure, unparsable status output,
truncated records, an unattributable or unparseable changed .py — exit 2, never
green. Findings abort (exit 1) unless an allowlist evidence file names every
finding id ("<path>:<rule>") verbatim; a stale allowlist entry (names an id no
longer in the delta) is evidence drift — exit 2 as well.

RED-first witness: before scripts/pin_delta_check.py exists every case here fails
(missing script). Green requires all of them. Standalone, stdlib only, house
check()/exit style; synthetic before/after git repos prove each detector fires,
the allowlist path passes, and non-cases (pure rename, deletion, function-body and
__main__-guarded sys.path appends, docs prose) stay green.
"""
import os
import subprocess
import sys
import tempfile
from importlib import util as _ilu
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pin_delta_check.py"

_spec = _ilu.spec_from_file_location("pin_delta_check_under_test", SCRIPT)
pdc = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(pdc)

PY = sys.executable
fails = 0
total = 0


def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))
    fails += 0 if ok else 1


# --- core units: line detectors, each rule fires on its shape --------------------
def hits(added):
    return {rule for rule, _line, _ev in pdc.line_findings(added)}


check("detector: launchctl submit/bootstrap/load",
      "launchctl_submit" in hits([(1, 'subprocess.run(["launchctl", "load", "-w", str(dest)])')]))
check("detector: launchd plist RunAtLoad/KeepAlive",
      "launchd_plist_persistence" in hits([(1, '    "RunAtLoad": True, "KeepAlive": True')]))
check("detector: systemd (systemctl + unit paths)",
      "systemd_unit" in hits([(1, "subprocess.run([SYSTEMCTL, --user, enable, wf.timer])".replace("SYSTEMCTL", '"systemctl"'))])
      and "systemd_unit" in hits([(1, 'write("/etc/systemd/system/wf.service")')]))
check("detector: cron install (crontab + cron dirs)",
      "cron_install" in hits([(1, "(crontab -l 2>/dev/null; echo x) | crontab -")])
      and "cron_install" in hits([(1, 'write("/etc/cron.d/wf-watch")')]))
check("detector: detach/daemonize shapes",
      all("detach_or_daemonize" in hits([(1, s)]) for s in (
          "os.setsid()", "if os.fork() > 0:", 'os.execv("/usr/bin/nohup", ...)',
          "subprocess.Popen(argv, start_new_session=True)")))
check("detector: out-of-band writes (fixed /tmp, LaunchAgents, autostart, rc)",
      all("out_of_band_write" in hits([(1, s)]) for s in (
          'Path("/tmp/wf-handoff.json").write_text("{}")',
          'Path("~/Library/LaunchAgents/com.w.plist")',
          'open("/home/u/.config/autostart/wf.desktop", "w")',
          'echo run >> ~/.zshrc')))
check("detector: clean lines fire nothing",
      hits([(1, "def helper(x):"), (2, "    return x + 1"),
            (3, 'DATA = "/tmpdir/safe-name"'), (4, "# talks about /tmp history")]) == set())

# --- core units: AST import-time sys.path -----------------------------------------
def muts(src):
    return pdc.import_time_syspath_mutations(src)


check("ast: module-level insert fires",
      muts("import sys\nsys.path.insert(0, '/x')\n") == [2])
check("ast: function-body append does NOT fire",
      muts("import sys\ndef f():\n    sys.path.append('/x')\n") == [])
check("ast: class-body append does NOT fire",
      muts("import sys\nclass C:\n    sys.path.append('/x')\n") == [])
check("ast: __main__-guarded append does NOT fire; else-branch DOES",
      muts("import sys\nif __name__ == '__main__':\n    sys.path.append('/m')\nelse:\n    sys.path.insert(1, '/e')\n") == [5])
check("ast: __name__ != __main__ guard is import-time code",
      muts("import sys\nif __name__ != '__main__':\n    sys.path.append('/e')\n") == [3])
check("ast: module-level try wrapper counts (import time)",
      muts("import sys\ntry:\n    sys.path.extend(['/x'])\nexcept ImportError:\n    pass\n") == [3])
check("ast: bare sys.path reassignment fires",
      muts("import sys\nsys.path = ['/x']\n") == [2])
check("ast: unparsable python -> None (fail closed upstream)",
      muts("def (") is None)

# --- core units: est-gbim parser (both endpoints), stubbed git --------------------
class _R:
    def __init__(self, rc, out):
        self.returncode, self.stdout = rc, out


_orig_git_bytes = pdc._git_bytes
try:
    pdc._git_bytes = lambda rd, *a: _R(0, b"R100\0old/pkg.py\0runner/pkg.py\0M\0a.py\0")
    check("parser: rename record yields BOTH endpoints",
          pdc.changed_files(".", "base", "head")
          == [("R100", "old/pkg.py", "runner/pkg.py"), ("M", "a.py", None)])
    pdc._git_bytes = lambda rd, *a: _R(0, b"C75\0src.py\0src_copy.py\0")
    check("parser: copy record yields BOTH endpoints",
          pdc.changed_files(".", "base", "head") == [("C75", "src.py", "src_copy.py")])
    pdc._git_bytes = lambda rd, *a: _R(0, b"R100\0only.py\0")
    check("parser: truncated rename record -> None (fail closed)",
          pdc.changed_files(".", "base", "head") is None)
    pdc._git_bytes = lambda rd, *a: _R(0, b"M\0")
    check("parser: truncated single-path record -> None",
          pdc.changed_files(".", "base", "head") is None)
    pdc._git_bytes = lambda rd, *a: _R(0, b"BOGUS\0x\0")
    check("parser: unrecognized status field -> None (fail closed)",
          pdc.changed_files(".", "base", "head") is None)
    pdc._git_bytes = lambda rd, *a: _R(0, b"")
    check("parser: empty diff parses to zero records (legit green)",
          pdc.changed_files(".", "base", "head") == [])
    pdc._git_bytes = lambda rd, *a: _R(128, b"")
    check("parser: git failure -> None (fail closed)",
          pdc.changed_files(".", "base", "head") is None)
finally:
    pdc._git_bytes = _orig_git_bytes


# --- integration: synthetic before/after trees, CLI as CI will call it -----------
def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t",
                           "-c", "user.name=t", *args], check=True,
                          capture_output=True, text=True,
                          env={**os.environ, "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
                               "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}).stdout


def seed_repo(td, name):
    repo = Path(td) / name
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    return repo


def write(repo, rel, text):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def commit(repo, msg):
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", msg)


def head(repo):
    return git(repo, "rev-parse", "HEAD").strip()


def run_check(repo, old, new, allowlist=None):
    cmd = [PY, str(SCRIPT), old, new, str(repo)]
    if allowlist is not None:
        cmd += ["--allowlist", str(allowlist)]
    return subprocess.run(cmd, capture_output=True, text=True)


POST_EXIT = '''"""post-exit dispatch (synthetic witness)."""
import os
import plistlib
import subprocess
from pathlib import Path


def register(script, label="wf-postexit"):
    plist = {"Label": label, "Program": [str(script)], "RunAtLoad": True,
             "KeepAlive": True}
    dest = Path(script).parent / (label + ".plist")
    dest.write_bytes(plistlib.dumps(plist))
    subprocess.run(["launchctl", "submit", label], check=False)
    subprocess.Popen(["launchctl", "bootstrap", "gui/501", str(dest)],
                     start_new_session=True)
    subprocess.run(["launchctl", "load", "-w", str(dest)], check=False)
'''

KEEPALIVE_SH = '''#!/bin/sh
# synthetic witness: keep a watcher alive across logins
(crontab -l 2>/dev/null; echo "*/5 * * * * $HOME/.local/bin/wf-watch") | crontab -
'''

DAEMONIZE = '''import os
import sys

if os.fork() > 0:
    sys._exit(0)
os.setsid()
if os.fork() > 0:
    os._exit(0)
os.execv("/usr/bin/nohup", ["nohup", "wf", "serve-detached"])
'''

HANDOFF = '''from pathlib import Path

Path("/tmp/wf-handoff.json").write_text("{}")
Path("~/Library/LaunchAgents/com.example.wf-wake.plist").expanduser().write_text("x")
'''

POLLUTE = '''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _late():
    sys.path.append("/inside-a-function-not-import-time")


if __name__ == "__main__":
    sys.path.append("/only-under-main-not-import-time")
else:
    sys.path.insert(1, "/else-runs-at-import")
'''

PURE = '''"""pure helper — no host effects."""


def tidy(x):
    return sorted(set(x))
'''

EXPECTED_IDS = {
    "runner/post_exit_hook.py:launchctl_submit",
    "runner/post_exit_hook.py:launchd_plist_persistence",
    "runner/post_exit_hook.py:detach_or_daemonize",
    "runner/keepalive.sh:cron_install",
    "runner/daemonize.py:detach_or_daemonize",
    "runner/handoff.py:out_of_band_write",
    "runner/pathpollute.py:syspath_import_time",
}

with tempfile.TemporaryDirectory(prefix="pdc-test-") as td:
    td = Path(td)

    # case A: the re-pin that ships host effects — exit 1, every finding named
    repo = seed_repo(td, "hostile")
    write(repo, "lib/helper.py", PURE)
    write(repo, "README.md", "# synthetic fixture\n")
    commit(repo, "pin old")
    old = head(repo)
    write(repo, "runner/post_exit_hook.py", POST_EXIT)
    write(repo, "runner/keepalive.sh", KEEPALIVE_SH)
    write(repo, "runner/daemonize.py", DAEMONIZE)
    write(repo, "runner/handoff.py", HANDOFF)
    write(repo, "runner/pathpollute.py", POLLUTE)
    write(repo, "lib/helper2.py", PURE)
    commit(repo, "pin new: smuggles host effects")
    new = head(repo)
    r = run_check(repo, old, new)
    out = r.stdout + r.stderr
    check("integration: host-effect delta exits 1", r.returncode == 1,
          f"rc={r.returncode} out={out.strip()[-200:]}")
    check("integration: every expected finding id printed",
          all(i in out for i in EXPECTED_IDS),
          f"missing={sorted(i for i in EXPECTED_IDS if i not in out)}")
    check("integration: clean file raises nothing (only the 7 expected ids)",
          out.count(":launchctl_submit") == 1 and "lib/helper2.py" not in out
          and "lib/helper.py" not in out)
    check("integration: detach finding names the missing teardown leg",
        "teardown" in out.lower())
    check("integration: import-time discipline holds (function/main-guarded appends silent)",
          "/inside-a-function-not-import-time" not in out
          and "/only-under-main-not-import-time" not in out
          and "/else-runs-at-import" in out)

    # case B: allowlist evidence naming every id verbatim — exit 0
    al = td / "allowlist.txt"
    al.write_text("# pin-delta allowlist evidence\n" + "\n".join(sorted(EXPECTED_IDS)) + "\n")
    r = run_check(repo, old, new, al)
    check("integration: full allowlist passes (exit 0, findings echoed)",
          r.returncode == 0 and "launchctl_submit" in r.stdout,
          f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case B2: allowlist missing one id — still aborts, naming the gap
    al2 = td / "allowlist-partial.txt"
    al2.write_text("\n".join(sorted(EXPECTED_IDS - {"runner/handoff.py:out_of_band_write"})) + "\n")
    r = run_check(repo, old, new, al2)
    out = r.stdout + r.stderr
    check("integration: allowlist missing an id exits 1 naming it",
          r.returncode == 1 and "runner/handoff.py:out_of_band_write" in out,
          f"rc={r.returncode} out={out.strip()[-200:]}")

    # case B3: stale allowlist entry (evidence drift) — fail closed
    al3 = td / "allowlist-stale.txt"
    al3.write_text("\n".join(sorted(EXPECTED_IDS | {"runner/gone.py:launchctl_submit"})) + "\n")
    r = run_check(repo, old, new, al3)
    check("integration: stale allowlist entry -> exit 2 (never green)",
          r.returncode == 2, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case B4: allowlist path given but unreadable — fail closed
    r = run_check(repo, old, new, td / "no-such-allowlist.txt")
    check("integration: missing allowlist file -> exit 2 (fail closed)",
          r.returncode == 2, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case C: the clean re-pin — exit 0
    repo = seed_repo(td, "clean")
    write(repo, "lib/helper.py", PURE)
    commit(repo, "pin old")
    old_c = head(repo)
    write(repo, "lib/helper2.py", PURE)
    commit(repo, "pin new: pure helper only")
    r = run_check(repo, old_c, head(repo))
    check("integration: clean delta exits 0 loudly OK",
          r.returncode == 0 and "OK" in r.stdout,
          f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case D (est-gbim): rename+modify that introduces launchctl — flagged at the
    # post-image path (a rename cannot dodge the scan by moving the file)
    repo = seed_repo(td, "rename-mod")
    write(repo, "runner/tool.py", "import subprocess\n")
    commit(repo, "pin old")
    old_d = head(repo)
    git(repo, "mv", "runner/tool.py", "runner/tool_v2.py")
    write(repo, "runner/tool_v2.py",
          "import subprocess\n\n\ndef go(p):\n    subprocess.run(['launchctl', 'load', '-w', p])\n")
    commit(repo, "rename + smuggle launchctl")
    r = run_check(repo, old_d, head(repo))
    out = r.stdout + r.stderr
    check("integration: rename+modify flagged at BOTH-endpoint post image",
          r.returncode == 1 and "runner/tool_v2.py:launchctl_submit" in out,
          f"rc={r.returncode} out={out.strip()[-200:]}")

    # case D2: PURE rename (content unchanged) — pre-existing effect, not new: green
    repo = seed_repo(td, "rename-pure")
    write(repo, "runner/keep.py", "import subprocess\nsubprocess.run(['launchctl', 'load', '-w', 'x'])\n")
    commit(repo, "pin old (effect already shipped)")
    old_d2 = head(repo)
    git(repo, "mv", "runner/keep.py", "runner/keep_moved.py")
    commit(repo, "pure rename")
    r = run_check(repo, old_d2, head(repo))
    check("integration: pure rename is not a NEW effect (exit 0)",
          r.returncode == 0, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case E: deletion of an effect-bearing file is not a NEW host effect
    repo = seed_repo(td, "deletion")
    write(repo, "runner/gone.py", "import subprocess\nsubprocess.run(['launchctl', 'submit', 'x'])\n")
    commit(repo, "pin old")
    old_e = head(repo)
    git(repo, "rm", "-q", "runner/gone.py")
    commit(repo, "strip the hook")
    r = run_check(repo, old_e, head(repo))
    check("integration: deletion-only delta exits 0",
          r.returncode == 0, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case F: binary payload in a scanned suffix cannot be grepped — blocks, allowlist clears
    repo = seed_repo(td, "binary")
    write(repo, "lib/helper.py", PURE)
    commit(repo, "pin old")
    old_f = head(repo)
    (repo / "runner").mkdir(exist_ok=True)
    (repo / "runner" / "blob.py").write_bytes(b"\x00\x01launchctl\xff\x00binary")
    commit(repo, "add binary payload")
    r = run_check(repo, old_f, head(repo))
    check("integration: binary scanned-suffix file blocks (exit 1)",
          r.returncode == 1 and "runner/blob.py:binary_unscanned" in (r.stdout + r.stderr),
          f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")
    alf = td / "allowlist-bin.txt"
    alf.write_text("runner/blob.py:binary_unscanned\n")
    r = run_check(repo, old_f, head(repo), alf)
    check("integration: allowlisted binary payload passes",
          r.returncode == 0, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

    # case G: a changed .py that no longer parses — fail closed (exit 2), never green
    repo = seed_repo(td, "broken")
    write(repo, "lib/helper.py", PURE)
    commit(repo, "pin old")
    old_g = head(repo)
    write(repo, "runner/broken.py", "def (:\n")
    commit(repo, "add unparsable python")
    r = run_check(repo, old_g, head(repo))
    out = r.stdout + r.stderr
    check("integration: unparsable added .py -> exit 2 FAIL-CLOSED row",
          r.returncode == 2 and "FAIL-CLOSED" in out and "parse" in out,
          f"rc={r.returncode} out={out.strip()[-200:]}")

    # case H: bad inputs fail closed, never green
    r = run_check(repo, "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", head(repo))
    check("integration: unresolvable old sha -> exit 2",
          r.returncode == 2, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")
    r = run_check(td / "clean" / "lib", old_g, head(repo))
    check("integration: not a git repo -> exit 2",
          r.returncode == 2, f"rc={r.returncode} out={(r.stdout + r.stderr).strip()[-200:]}")

print(f"TOTAL {total} FAIL {fails}")
sys.exit(1 if fails else 0)
