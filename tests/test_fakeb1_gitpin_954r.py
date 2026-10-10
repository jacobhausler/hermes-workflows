#!/usr/bin/env python3
"""est-954r pin — the B1 test's raw run must never dirty the tracked tree.

tests/test_sprint101w2_B1-classes.py used to default BUILD to the tests dir
when WF_TEST_BUILD was unset, so its `shutil.copy(fake_hermes.py -> fake-b1)`
OVERWROTE the tracked tests/fake-b1 in place (hit twice 2026-10-02, two
forensic passes). The default BUILD is now an ephemeral temp dir. This pin
re-runs that test exactly the way a human does — raw, no WF_TEST_BUILD — and
proves by git status (what the suite gate and the forensic pass actually
read, not just a hash) that the run introduces zero new dirt and leaves
tests/fake-b1, tests/fake and tests/fake_hermes.py untouched.

est-1nkx (PR #158 second-read): the release ZIP ships this pin but carries no
git metadata — `git status` there dies rc=128 not-a-repository (INSTALL.md
documents running all shipped tests in the extracted ZIP). A checkout without
git metadata is NOT a pass: the pin falls back to the equivalent guarantee —
snapshot SHA-256 of every tracked fixture before the raw run and re-verify it
after (the same bytes the forensic pass reads; the git path still speaks in
real checkouts). Zero-dirt over the fixture set is what the law claims; the
porcelain is its most readable witness, never its only possible one.
"""
import hashlib
import os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TARGET = HERE / "test_sprint101w2_B1-classes.py"
FIXTURES = ("tests/fake-b1", "tests/fake_hermes.py", "tests/fake")

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        ok = False

def _git_present():
    """True only where REPO is a real git checkout (the release ZIP is not — est-1nkx)."""
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-dir"],
                              capture_output=True, text=True, timeout=30).returncode == 0
    except Exception:
        return False


def porcelain():
    """Tracked-path dirt as {path: XY}, parsed from git status --porcelain."""
    r = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git status failed rc={r.returncode}: {r.stderr.strip()}")
    out = {}
    for line in r.stdout.splitlines():
        if line.strip():
            out[line[3:].split(" -> ")[-1]] = line[:2]   # renames: keep new path
    return out

# 1) raw-run the B1 test with the admission conditions: no WF_TEST_BUILD,
#    no WF_RUNS_ROOT, no HERMES_HOME — the exact invocation that dirtied the
#    tree on 2026-10-02.
env = dict(os.environ)
for k in ("WF_TEST_BUILD", "WF_RUNS_ROOT", "HERMES_HOME"):
    env.pop(k, None)
GIT = _git_present()
sha_before = {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest() for f in FIXTURES}
before = porcelain() if GIT else {}
p = subprocess.run([sys.executable, str(TARGET)], env=env, cwd=str(REPO),
                   capture_output=True, text=True, timeout=150)
check("B1 raw run (WF_TEST_BUILD unset) still passes",
      p.returncode == 0 and "ALL PASS" in p.stdout,
      f"rc={p.returncode} out={p.stdout[-200:]} err={p.stderr[-200:]}")

# 2) the pin: git status before vs after — the raw run may add zero dirt.
if GIT:
    after = porcelain()
    introduced = sorted(set(after) - set(before))
    check("est-954r: raw run introduces zero new git dirt", not introduced,
          f"new dirt: {[(k, after[k]) for k in introduced]}")
    dirty_fixtures = sorted(set(after) & set(FIXTURES))
    check("est-954r: tracked tests/fake-b1 (+ fake, fake_hermes.py) untouched after raw run",
          not dirty_fixtures, f"dirty: {[(k, after[k]) for k in dirty_fixtures]}")
else:
    # est-1nkx ZIP path: no git metadata — the byte-equivalent guarantee, never a pass.
    drifted = [f for f, sha in sha_before.items()
               if hashlib.sha256((REPO / f).read_bytes()).hexdigest() != sha]
    check("est-1nkx ZIP: raw run leaves every tracked fixture byte-identical "
          "(git-free fallback — sha256 over the same bytes porcelain reads)",
          not drifted, f"drifted: {drifted}")

print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
