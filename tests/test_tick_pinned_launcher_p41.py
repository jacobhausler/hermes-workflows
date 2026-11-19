#!/usr/bin/env python3
"""P41: plugin install/update must not clobber the exec bit or the interpreter
pin of the tick script.

The law pinned here (observable outcomes only):
  * the baked tick launcher is an INTERPRETER-PINNED line — an absolute
    interpreter (``WF_TICK_PYTHON`` > the bake's ``sys.executable``) with the
    entrypoint as an argument: the launch needs neither the entrypoint's exec
    bit nor a shebang resolution, so a reinstall that lands ``wf.py`` as 0644
    (git index mode, ZIP 0644 member) or resolves ``env python3`` to the
    macOS 3.9.6 system python cannot silently revert the tick;
  * a re-arm over a RUNNING tick (job already exists) re-bakes the launcher:
    a cleared exec bit comes back and the pin follows the current
    interpreter, while a settled launcher is left byte-identical and
    mtime-stable — a rerun converges and never clobbers;
  * ``selfcheck_tick`` runs the tick once through the baked shim exactly as
    the core scheduler runs a ``.sh`` job script (bash), reports its rc, and
    repairs a clobbered launcher first; the CLI
    ``python3 cron_bridge.py selfcheck`` exits with the tick's rc — the
    post-update self-check;
  * the negative control has teeth: the pre-P41 body (``exec <wf.py> tick``
    against a 0644 entrypoint) is NOT rc=0 — that is the P41 incident.

Hermetic per est-z2heo: a fake jobs module at the ``_jobs()`` seam and
HERMES_HOME under a tmp dir — the live cron store is never touched.

Plain script, no pytest: exits non-zero on the first red.
"""
import os
import shlex
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import cron_bridge  # noqa: E402  (the module under test, flat root layout)

FAILS = []


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:600]))
    if not cond:
        FAILS.append(name)


class FakeJobs:
    def __init__(self):
        self.jobs = []
        self.create_calls = 0

    def create_job(self, **kw):
        self.create_calls += 1
        job = dict(kw)
        job["id"] = "fake%02d" % self.create_calls
        self.jobs.append(job)
        return job

    def list_jobs(self, include_disabled=False):
        return [dict(j) for j in self.jobs]

    def remove_job(self, job_id):
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j.get("id") != job_id]
        return len(self.jobs) < before


def exec_line(body):
    for line in body.splitlines():
        if line.startswith("exec "):
            return shlex.split(line)
    return []


def main():
    fake = FakeJobs()
    cron_bridge._jobs = lambda: fake
    saved_env = {k: os.environ.get(k) for k in
                 ("HERMES_HOME", "WF_TICK_PYTHON", "WF_ARGV_STABLE_ROOTS", "WF_RUNS_ROOT")}
    os.environ["WF_ARGV_STABLE_ROOTS"] = str(ROOT)
    try:
        with tempfile.TemporaryDirectory(prefix="tickpin-") as td:
            home = Path(td) / "hermes-home"
            home.mkdir()
            os.environ["HERMES_HOME"] = str(home)
            os.environ["WF_RUNS_ROOT"] = str(Path(td) / "empty-runs")
            stable = Path(td) / "stable-plugin"
            stable.mkdir()
            cron_bridge.PLUGIN_ROOT = stable
            cron_bridge.WF_PY = stable / "wf.py"
            os.environ["WF_ARGV_STABLE_ROOTS"] = str(stable)

            # A. bake shape: absolute interpreter, entrypoint as argument.
            marker = Path(td) / "invoked.marker"
            fake_py = Path(td) / "fakepy"
            fake_py.write_text('#!/bin/sh\necho "$1" > "' + str(marker) + '"\nexit 0\n')
            fake_py.chmod(0o755)
            (stable / "wf.py").write_text("# entrypoint\n")
            (stable / "wf.py").chmod(0o755)
            os.environ["WF_TICK_PYTHON"] = str(fake_py)
            jid = cron_bridge.ensure_tick()
            check("A: ensure_tick arms one job", isinstance(jid, str) and fake.create_calls == 1, jid)
            shim = home / "scripts" / (cron_bridge.TICK_NAME + ".sh")
            body = shim.read_text()
            line = exec_line(body)
            check("A: the launcher is a bash shim", body.startswith("#!/usr/bin/env bash"), body[:80])
            check("A: the pin is an absolute interpreter (not env-python3 via shebang)",
                  len(line) >= 3 and os.path.isabs(line[1]) and line[1] == str(fake_py), line)
            check("A: the entrypoint rides as an argument to the pin",
                  len(line) >= 3 and line[2] == str(cron_bridge.WF_PY) and line[3:] == ["tick"], line)
            check("A: the launcher ships executable",
                  bool(shim.stat().st_mode & stat.S_IXUSR), oct(shim.stat().st_mode))
            subprocess.run(["/bin/bash", str(shim)], check=True)
            check("A: running the launcher invokes the pinned interpreter with the entrypoint",
                  marker.is_file() and marker.read_text().strip() == str(cron_bridge.WF_PY),
                  marker.read_text() if marker.is_file() else "no marker")

            # B. update over a running tick: the reinstall lands the entrypoint
            # 0644 AND the old launcher is reverted (exec bit cleared); the
            # next arm converges it back without touching the job row.
            (stable / "wf.py").chmod(0o644)          # the P41 clobber
            shim.chmod(0o644)                        # the ops fix silently reverted
            stale = shim.read_text()
            shim.write_text("#!/usr/bin/env bash\nexec %s tick\n" % shlex.quote(str(cron_bridge.WF_PY)))
            shim.chmod(0o644)
            jid2 = cron_bridge.ensure_tick()
            check("B: re-arm returns the SAME job id, creates nothing",
                  jid2 == jid and fake.create_calls == 1 and len(fake.jobs) == 1, (jid, jid2))
            repaired = shim.read_text()
            check("B: re-arm restores the exec bit",
                  bool(shim.stat().st_mode & stat.S_IXUSR), oct(shim.stat().st_mode))
            check("B: re-arm restores the interpreter pin over the reverted body",
                  repaired == stale and exec_line(repaired)[1:] == [str(fake_py), str(cron_bridge.WF_PY), "tick"],
                  repaired)

            # C. the repaired launch works WITHOUT the entrypoint exec bit —
            # the exact state the reinstall left. (Fake interpreter: the exec
            # bit it would need is its own, set at creation.)
            r = subprocess.run(["/bin/bash", str(shim)])
            check("C: the tick runs rc=0 with the entrypoint at 0644", r.returncode == 0, r.returncode)
            neg = Path(td) / "oldshape.sh"
            neg.write_text("#!/usr/bin/env bash\nexec %s tick\n" % shlex.quote(str(cron_bridge.WF_PY)))
            neg.chmod(0o755)
            r = subprocess.run(["/bin/bash", str(neg)], capture_output=True, text=True)
            check("C: negative control — the pre-P41 body dies on the 0644 entrypoint (P41 teeth)",
                  r.returncode != 0, r.returncode)

            # D. convergence: a settled launcher is byte- and mtime-stable.
            before = (shim.read_bytes(), shim.stat().st_mtime_ns, shim.stat().st_mode)
            cron_bridge.write_shim(cron_bridge.TICK_NAME, "tick")
            cron_bridge.ensure_tick()
            after = (shim.read_bytes(), shim.stat().st_mtime_ns, shim.stat().st_mode)
            check("D: rerun converges — a settled launcher is not rewritten", before == after,
                  (before[0], after[0]))

            # E. real end-to-end with the bake's own interpreter: a 0644
            # python entrypoint, launched by the default selfcheck spawn.
            del os.environ["WF_TICK_PYTHON"]
            (stable / "wf.py").write_text(
                "import sys\n"
                "assert sys.argv[1:] == ['tick'], sys.argv\n"
                "open(%r, 'w').write('tick')\n" % str(Path(td) / "real.marker") +
                "sys.exit(0)\n")
            (stable / "wf.py").chmod(0o644)
            report = cron_bridge.selfcheck_tick()
            check("E: post-update self-check reports tick rc=0 through the baked shim",
                  report == {"rc": 0, "shim": str(shim), "ok": True}, report)
            check("E: the tick body actually ran under the absolute interpreter",
                  (Path(td) / "real.marker").read_text() == "tick", "marker missing")
            shim.chmod(0o644)
            report = cron_bridge.selfcheck_tick()
            check("E: self-check repairs a clobbered launcher and still reports rc=0",
                  report["ok"] and bool(shim.stat().st_mode & stat.S_IXUSR), (report, oct(shim.stat().st_mode)))
            os.environ["WF_TICK_PYTHON"] = "/nonexistent-generation/python3"
            shim.chmod(0o644)
            report = cron_bridge.selfcheck_tick()
            check("E: a stale pin is re-armed away (self-check re-pins to the live bake)",
                  exec_line(shim.read_text())[1] == "/nonexistent-generation/python3"
                  and report["rc"] != 0 and bool(shim.stat().st_mode & stat.S_IXUSR),
                  report)
            del os.environ["WF_TICK_PYTHON"]
            report = cron_bridge.selfcheck_tick()
            check("E: the re-pin to sys.executable restores rc=0", report["ok"] is True, report)

            # F. the operator CLI: exit code IS the tick's rc, the line names
            # the shim. Run against a minimal plugin copy: a linked-worktree
            # checkout root is residency-refused by law (#652), and the CLI
            # shape — argv, output line, exit code — is what this leg pins.
            os.environ.pop("WF_TICK_PYTHON", None)
            (stable / "cron_bridge.py").write_text((ROOT / "cron_bridge.py").read_text())
            (stable / "wfcommon.py").write_text(
                "def entrypoint_residency(path, extra=None):\n"
                "    return 'resident', ''\n")
            (stable / "wf.py").write_text(
                "import sys\n"
                "assert sys.argv[1:] == ['tick'], sys.argv\n"
                "open(%r, 'w').write('cli')\n" % str(Path(td) / "cli.marker") +
                "sys.exit(0)\n")
            cli = subprocess.run([sys.executable, str(stable / "cron_bridge.py"), "selfcheck"],
                                 capture_output=True, text=True, env=dict(os.environ))
            check("F: `python3 cron_bridge.py selfcheck` exits 0 and names the tick rc",
                  cli.returncode == 0 and cli.stdout.startswith("TICK SELFCHECK rc=0 shim="),
                  (cli.returncode, cli.stdout[:200], cli.stderr[:200]))
            check("F: the CLI ran the tick body once",
                  (Path(td) / "cli.marker").read_text() == "cli", "marker missing")
            usage = subprocess.run([sys.executable, str(ROOT / "cron_bridge.py")],
                                   capture_output=True, text=True)
            check("F: without `selfcheck` the CLI refuses with usage and rc=2",
                  usage.returncode == 2 and "usage:" in usage.stdout,
                  (usage.returncode, usage.stdout[:120]))
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        check("Z: the live cron store was never touched (core cron.jobs never imported)",
              "cron.jobs" not in sys.modules, sorted(m for m in sys.modules if m.startswith("cron")))

    print("ALL PASS" if not FAILS else f"FAILED: {FAILS}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
