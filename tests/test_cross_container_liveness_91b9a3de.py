"""91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness.
The fleet runs runners in a sibling container on the SHARED ~/.hermes volume with a
separate pid namespace — os.kill(pid, 0) there reads a LIVE runner as dead, and the
door's next=wait / respawn guards then spawn a second runner over live children (the
fb-squad-c false-'interrupted' incident). The kernel-enforced flock on <run>/runner.lock
is the ownership proof that survives pid namespaces: HELD => live, at every call site
through the ONE shared predicate wfcommon.runner_alive. Inertness is equally pinned:
free lock + dead/foreign pid reads dead exactly as before (the pid-identity law runs
verbatim as the fallback), and the fan-out ADOPTION path (wfcommon._verify_spawn_rec,
the 'same pid-only pattern' at the old :966) is deliberately NOT relaxed — adoption
runs inside the spawning runner's own container, where the pid/skey proof is verifiable;
cross-namespace adoption without identity proof would gut the skey-in-cmdline
PID-reuse guard. That is why fixing the runner-level law is safe and adoption stays.
"""
import fcntl, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
home = HERE / "home18"
if home.exists():
    shutil.rmtree(home)
home.mkdir()
os.environ["HERMES_HOME"] = str(home)
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}"
    ok += 1; print("PASS", msg)

runs = home / "workflows"; runs.mkdir(exist_ok=True)

def mkrun(name, pid=None, seed_graph=False):
    r = runs / name
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    if seed_graph:
        (r / "graph.json").write_text(json.dumps(
            {"nodes": [{"id": "a", "type": "agent", "goal": "JSON:{\"result\":\"ok\"}"}]}))
        (r / "run.json").write_text(json.dumps({"name": name}))
    if pid is not None:
        (r / "wf.pid").write_text(str(pid))
    return r

HOLDER = str(home / "holder_91b9a3de.py")   # scratch home, never tests/ (pytest would collect it)
Path(HOLDER).write_text(
    "import fcntl, os, sys, time\n"
    "fd = os.open(sys.argv[1], os.O_CREAT | os.O_RDWR, 0o644)\n"
    "fcntl.flock(fd, fcntl.LOCK_EX)\n"
    "print('held', flush=True)\n"
    "time.sleep(float(sys.argv[2]))\n")

def hold(r, secs=30):
    """A holder in ANOTHER process group — the kernel view of 'a runner in a sibling
    container': our probe process cannot see its pid semantics any other way than
    through the shared-mount flock."""
    p = subprocess.Popen([sys.executable, HOLDER, str(r / "runner.lock"), str(secs)],
                         stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "held", "holder failed to take the flock"
    return p

# --- (1) THE INCIDENT SHAPE: flock HELD by a peer, pid unreadable => live --------
# A pid no observer here can verify (the sibling-container shape: os.kill cannot
# reach it) while the mount-level flock proves the runner alive.
r = mkrun("xpeer", pid=999999, seed_graph=True)
peer = hold(r)
try:
    check(wfcommon.runner_alive(r) is True,
          "held flock + unverifiable pid reads LIVE (second-runner-over-live-children prevented)")
    st = wfcommon.run_state(r)
    check(st["status"] == "running", "run_state says running, not interrupted", st["status"])
finally:
    peer.kill(); peer.wait(); time.sleep(0.2)

# --- (2) inertness: nothing holds, pid dead => dead, exactly as before -------------
r2 = mkrun("xdead", pid=999999, seed_graph=True)
check(wfcommon.runner_alive(r2) is False, "free lock + dead pid reads DEAD (law unchanged)")
check(wfcommon.run_state(r2)["status"] == "interrupted", "unreadable pid + free lock = interrupted")

# --- (3) a live lock file with NO pid file is still live (no wf.pid to read) -------
r3 = mkrun("xnopid", pid=None, seed_graph=True)
peer3 = hold(r3)
try:
    check(wfcommon.runner_alive(r3) is True, "held lock without wf.pid reads LIVE")
finally:
    peer3.kill(); peer3.wait(); time.sleep(0.2)
check(wfcommon.runner_alive(r3) is False, "holder gone -> dead again (probe is non-blocking, release is kernel-side)")

# --- (4) foreign live pid whose argv is NOT `wf.py run <id>` + free lock => dead ---
victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
r4 = mkrun("xforeign", pid=victim.pid, seed_graph=True)
try:
    check(wfcommon.runner_alive(r4) is False, "live foreign pid with wrong argv + free lock reads DEAD")
finally:
    victim.kill(); victim.wait()

# --- (5) the REAL runner: its own lifecycle drives the predicate end-to-end -------
r5 = mkrun("xreal", seed_graph=True)
(r5 / "run.json").write_text(json.dumps({"name": "xreal", "hermes_bin": str(HERE / "fake"),
                                         "concurrency": 1, "node_timeout": 30,
                                         "started": "2099-01-01T00:00:00+00:00"}))
proc = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", "xreal"],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                        env={**os.environ, "HERMES_HOME": str(home), "FAKE_LOG": "/dev/null"})
live_seen = dead_seen = False
for _ in range(120):
    if wfcommon.runner_alive(r5):
        live_seen = True
        if (r5 / "wf.pid").exists():
            break
    time.sleep(0.05)
proc.wait(timeout=90); time.sleep(0.2)
check(live_seen, "live real runner reads live through the predicate")
check(wfcommon.runner_alive(r5) is False, "after clean exit (kernel released the flock) reads dead")

# --- (6) MUTATION CONTROL: the law must be the OR, not a stray always-true -------
src = (BUILD / "wfcommon.py").read_text()
check(src.count("if runner_lock_held(r):\n        return True") == 1,
      "flock ORs into the ONE predicate exactly once (no second liveness store)")
check("def _runner_pid_alive" in src and "return _runner_pid_alive(r, pid_path)" in src,
      "pid-identity law preserved verbatim as the fallback")
probe_src = src[src.index("def runner_lock_held"):src.index("def _runner_pid_alive")]
check("os.O_CREAT" not in probe_src,
      "the probe never CREATES a lock file (read paths must not litter run dirs)")

print(f"ALL PASS ({ok})")
