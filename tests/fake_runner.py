"""Reusable fake-runner for door-scan fixtures — the sanctioned stand-in for a live runner.

The identity law lives in wfcommon._runner_pid_alive: the probe reads <run>/wf.pid and
demands a live, non-zombie process whose argv ENDS with `<abs path>/wf.py run
<run-dir-name>`, effective runs root matching the run's parent. Fixtures that
hand-rolled their own fakes learned three contracts the hard way; this helper bakes in
all three (pinned by tests/test_fake_runner_door_scan.py):

  * guard shape: the fake's argv literally ends `wf.py run <dir-name>` — a sleeper
    -c script merely mentioning the run id in its source does NOT match;
  * absolute path: fixtures scan for f"{os.sep}wf.py run {rid}", so the path segment
    must be absolute; a relative `wf.py run ...` hides the fake from every scanner;
  * live seat twin: real runners drive seat children and tree walkers expect one,
    so the fake forks a live sleeper twin.

spawn() materialises the fake-runner body as a `wf.py` shim inside the runs root
(idempotent), self-stamps wf.pid from inside the fake (the real admission law: the
runner owns its stamp), and inherits WF_RUNS_ROOT so the root-match half agrees.
Teardown: terminate() then wait() the handle (zombie-free).

Also the probe half door-scan fixtures kept duplicating verbatim: alive(),
cmdline(), runners_for(). Use these instead of hand-rolling them per test.
"""
import os
import subprocess
import sys
from pathlib import Path

_CHILD_SRC = '''\
import os, signal, subprocess, sys, time
from pathlib import Path
run_dir = Path(sys.argv[0]).resolve().parent / sys.argv[2]
(run_dir / "wf.pid").write_text(str(os.getpid()))
_twin = None
def _done(*_):
    if _twin:
        _twin.kill()
    os._exit(0)
signal.signal(signal.SIGTERM, _done)
signal.signal(signal.SIGINT, _done)
_twin = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
while _twin.poll() is None:
    time.sleep(0.2)
os._exit(1)
'''


def alive(pid):
    """os.kill-0 liveness, zombie-aware where /proc speaks (Zombie = dead)."""
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    try:
        st = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        return not st.startswith("Z")
    except OSError:
        return True


def cmdline(pid):
    """Nul-joined argv padded with spaces, so ` f" {os.sep}wf.py run {rid} " in ...` matches."""
    try:
        return " " + Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="replace").replace("\0", " ").strip() + " "
    except OSError:
        return ""


def runners_for(rid):
    """Live pids whose cmdline carries the runner guard for this run id."""
    out = []
    try:
        entries = os.listdir("/proc")
    except OSError:
        return out
    for e in entries:
        if e.isdigit() and f"{os.sep}wf.py run {rid}" in cmdline(int(e)):
            out.append(int(e))
    return out


def spawn(run_dir):
    """Fake a live runner for run_dir: guard-shaped absolute argv, self-stamped
    wf.pid, live seat twin. Returns the Popen handle — terminate()+wait() it to tear
    down. The twin dies with the fake; a TERM landing in the first ~ms (before the
    twin exists) may orphan the sleeper, which self-exits after 120s (ponytail)."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    shim = run_dir.parent / "wf.py"
    if not shim.exists() or shim.read_text() != _CHILD_SRC:
        shim.write_text(_CHILD_SRC)
    # pin the fake's effective root to this run's parent: the root-match half of the
    # identity law must hold wherever the fixture parked the run dir
    return subprocess.Popen([sys.executable, str(shim), "run", run_dir.name],
                            env=dict(os.environ, WF_RUNS_ROOT=str(run_dir.parent)))
