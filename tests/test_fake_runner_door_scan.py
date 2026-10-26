#!/usr/bin/env python3
"""Fake-runner helper: one sanctioned way to fake a live runner for door-scan fixtures.

The identity law lives in wfcommon._runner_pid_alive: the probe reads the pid from
<run>/wf.pid and demands a live, non-zombie process whose argv ENDS with
`<path>/wf.py run <run-dir-name>`, with the runner's effective runs root matching
the run's parent. Fixtures that got this wrong learned three contracts the hard
way; the helper must satisfy all of them and this test pins them:

  (1) guard shape    — argv must actually END with wf.py run <dir-name>; a
                       sleeper -c script that merely mentions the run id in its
                       source text does NOT match;
  (2) absolute path  — door-scan fixtures match f"{os.sep}wf.py run {rid}", so
                       the path segment must be absolute (a bare `wf.py` hides
                       the fake from every scanner);
  (3) live seat twin — a real runner drives seat children; tree walkers look
                       for one under the runner pid, so the fake forks a live
                       twin.

Acceptance: GIVEN a fresh run dir, WHEN the helper spawns a fake into it, THEN
wfcommon.runner_alive() reports the fake LIVE on the first probe after its
wf.pid self-stamp lands.
"""
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "tests" / "home-fakerunner"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(ROOT))
import wfcommon                      # noqa: E402  (after the sandbox pins, as every door test does)
import fake_runner                   # noqa: E402  (RED until the helper lands)

ok = True
def check(label, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + label)
    ok = ok and cond

root = Path(os.environ["WF_RUNS_ROOT"])
if HOME.exists():
    shutil.rmtree(HOME)          # fresh scratch: a stale wf.pid would fake the fresh-run rows
root.mkdir(parents=True)
rid = "fake-runner-pinned"
r = root / rid

check("fresh run dir is not alive", not wfcommon.runner_alive(r))

p = fake_runner.spawn(r)
try:
    t0 = time.time()
    while not (r / "wf.pid").exists() and time.time() - t0 < 5:
        time.sleep(0.02)
    check("self-stamped wf.pid carries the fake pid",
          (r / "wf.pid").read_text().strip() == str(p.pid) if (r / "wf.pid").exists() else False)

    # (2) absolute-path guard shape, exactly as door-scan fixtures scan for it
    check("cmdline carries the absolute guard", f"{os.sep}wf.py run {rid}" in fake_runner.cmdline(p.pid))
    # (1) the probe's own guard: argv[-3:] == [<...>/wf.py, "run", rid]
    argv = Path(f"/proc/{p.pid}/cmdline").read_bytes().decode().split("\0")
    argv = [a for a in argv if a]
    check("argv tail matches the probe guard",
          Path(argv[-3]).name == "wf.py" and argv[-2:] == ["run", rid])
    # (3) live seat twin
    kids = [int(e) for e in os.listdir("/proc")
            if e.isdigit() and Path(f"/proc/{e}/stat").read_text(errors="replace")
            .rsplit(")", 1)[-1].split()[1] == str(p.pid)] if Path("/proc").exists() else []
    check("fake has a live seat child", any(fake_runner.alive(k) for k in kids))

    check("runners_for finds the fake", p.pid in fake_runner.runners_for(rid))
    check("runner_alive probes the fake LIVE on the first probe", wfcommon.runner_alive(r))
finally:
    p.terminate()
    p.wait(timeout=10)
time.sleep(0.2)
check("runner_alive reports dead after teardown", not wfcommon.runner_alive(r)
      and p.pid not in fake_runner.runners_for(rid))

print("ALL PASS" if ok else "FAILURES")
sys.exit(0 if ok else 1)
