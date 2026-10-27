#!/usr/bin/env python3
"""est-9ceqc (graft of atbrace:hw-r0a): bounded transient retry whose backoff
window and attempt count persist per node, so a restart mid-backoff honors the
window instead of re-driving straight into the provider blip that caused it.

Pinned law:
  * the default transient schedule is exponential: base 2 s, ceiling 30 s, and
    the ladder stays bounded (default cap 2 re-spawns = 3 total attempts);
  * an explicit two-element `retry_backoff` keeps the fixed-schedule semantics;
  * before every transient-ladder sleep the runner persists
    {deadline, attempts} for that node into run/retry-window.json, and clears
    the key once the node settles anything but the transient death;
  * a boot that finds a future deadline waits it out (stop-aware, polled, in
    the owning node's own thread) BEFORE its first spawn for that node, and a
    past deadline never waits;
  * the ladder's attempt counter seeds from the persisted count, so restarts
    cannot amplify attempts past the node's cap;
  * the wait never blocks the shared tick: a sibling worker finishes while the
    honoring wait runs, and a set stop short-circuits the wait at once.

The integration case SIGKILLs a real runner mid-backoff (FAKE_MODE=transport),
resumes it the same way an operator does, and pins: no spawn before the
persisted deadline, exactly 3 spawns total across the two processes (the
surviving cap), and a transport_exhausted verdict on the committed record.

Plain script, no pytest: exits non-zero on the first red.
"""
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
sys.path.insert(0, str(BUILD))

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}; m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r


# ---------- unit half: the policy, the window file, the honoring wait ----------

os.environ["HERMES_HOME"] = str(HERE / "home9z")
os.environ["WF_RUNS_ROOT"] = str(HERE / "home9z" / "workflows")
wf = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("wf_under_test", BUILD / "wf.py"))
importlib.util.spec_from_file_location("wf_under_test", BUILD / "wf.py").loader.exec_module(wf)

def fresh_run(name):
    r = Path(os.environ["WF_RUNS_ROOT"]) / name
    shutil.rmtree(r, ignore_errors=True)
    r.mkdir(parents=True)
    return r

def unit_meta(r, **over):
    m = {"_run": r, "_stop": threading.Event(), "_procs_lock": threading.Lock(),
         "_retries_left": 6, "_procs": {}, "_spawn_n": {}}
    m.update(over)
    return m

# U1 default schedule is the exponential acceptance policy
pol = wf._retry_conf_params({})[0]
check("default schedule is exp base 2s ceiling 30s",
      isinstance(pol, dict) and pol.get("base") == 2.0 and pol.get("ceiling") == 30.0, pol)

# U2 the exponential delay: 2, 4, 8, 16, 30, 30 (attempt i is 0-based)
delays = [wf._retry_sleep(pol, i, "hermes -z: agent failed: Connection error.")
          for i in range(6)]
check("exp delays 2/4/8/16/30/30", delays == [2.0, 4.0, 8.0, 16.0, 30.0, 30.0], delays)

# U3 an explicit fixed tuple keeps the old semantics byte-for-behaviour
fixed = (5.0, 20.0)
check("fixed tuple unchanged",
      wf._retry_sleep(fixed, 0, "Connection error.") == 5.0
      and wf._retry_sleep(fixed, 1, "Connection error.") == 20.0
      and wf._retry_sleep(fixed, 7, "Connection error.") == 20.0)

# U4 malformed exp dicts fall back to the default policy
bad = wf._retry_conf_params({"retry_backoff": {"base": -1, "ceiling": 30}})[0]
check("malformed exp dict falls to default", bad is wf.DEFAULT_RETRY_BACKOFF or
      (isinstance(bad, dict) and bad.get("base") == 2.0), bad)
tup = wf._retry_conf_params({"retry_backoff": [0.05, 0.1]})[0]
check("explicit tuple still honored", tuple(tup) == (0.05, 0.1), tup)

# U5 the window persists around the sleep and clears once the node settles done
run5 = fresh_run("u5")
snap = {}
_orig_calls = wf._attempt_api_calls
wf._attempt_api_calls = lambda *a, **k: 0
try:
    meta5 = unit_meta(run5, retry_backoff=[0.05, 0.05])
    def respawn5(**kw):
        if (run5 / "retry-window.json").exists():
            snap["window"] = json.loads((run5 / "retry-window.json").read_text())
        snap["t"] = time.time()
        return {"status": "done", "output": {"x": 1}, "spawn": 1}
    rec = wf._transient_retry(meta5, {"status": "failed", "error_class": "transport",
                                      "error": "boom", "ms": 1},
                              respawn5, "node", {"node": "n"}, node={"id": "n"})
    w = snap.get("window", {})
    check("window persisted per node during the backoff",
          rec["status"] == "done" and "n" in w
          and w["n"]["attempts"] == 1
          and -0.15 <= w["n"]["deadline"] - snap["t"] <= 0.08, json.dumps(snap))
    check("window cleared once the node settled done",
          not (run5 / "retry-window.json").exists())

    # U6 the persisted count seeds the cap: spent cap = zero re-spawns, no wait
    run6 = fresh_run("u6")
    (run6 / "retry-window.json").write_text(json.dumps(
        {"n": {"deadline": time.time() - 5.0, "attempts": 2}}))
    calls6 = []
    meta6 = unit_meta(run6, retry_backoff=[0.05, 0.05])
    rec6 = wf._transient_retry(meta6, {"status": "failed", "error_class": "transport",
                                       "error": "boom", "ms": 1},
                               lambda **kw: calls6.append(1) or {"status": "done"},
                               "node", {"node": "n"}, node={"id": "n"})
    check("persisted attempts seed the cap (no respawn over the cap)",
          rec6["status"] == "failed" and not calls6)
    keep6 = json.loads((run6 / "retry-window.json").read_text())
    check("window survives a transient verdict so restarts cannot re-grant the cap",
          keep6["n"]["attempts"] == 2)

    # U7 a future deadline is honored before the first spawn of the boot
    run7 = fresh_run("u7")
    (run7 / "retry-window.json").write_text(json.dumps(
        {"n": {"deadline": time.time() + 0.5, "attempts": 1}}))
    t0 = time.time()
    wf._honor_retry_window(unit_meta(run7), "n")
    el = time.time() - t0
    check("restart honors the window (no respawn before the deadline)",
          0.40 <= el <= 2.0, el)

    # U8 the wait is stop-aware and polled, never a wall on the shutdown path
    run8 = fresh_run("u8")
    (run8 / "retry-window.json").write_text(json.dumps(
        {"n": {"deadline": time.time() + 10.0, "attempts": 1}}))
    m8 = unit_meta(run8)
    m8["_stop"].set()
    t0 = time.time()
    wf._honor_retry_window(m8, "n")
    check("stop short-circuits the honoring wait", time.time() - t0 < 0.3)

    # U9 the wait is per node-key: a sibling worker finishes while it runs
    run9 = fresh_run("u9")
    (run9 / "retry-window.json").write_text(json.dumps(
        {"n": {"deadline": time.time() + 0.6, "attempts": 1}}))
    seen = {}
    def honor():
        wf._honor_retry_window(unit_meta(run9), "n")
        seen["honor"] = time.time()
    def sibling():
        time.sleep(0.15)
        seen["sibling"] = time.time()
    th = [threading.Thread(target=f) for f in (honor, sibling)]
    [t.start() for t in th]; [t.join() for t in th]
    check("backoff never blocks a sibling worker (shared tick stays live)",
          seen.get("sibling", 9e9) < seen.get("honor", -1), seen)
finally:
    wf._attempt_api_calls = _orig_calls

# ---------- integration half: SIGKILL mid-backoff, resume, window honored ----------

HOME = HERE / "home9y"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)

def runner_env():
    return dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
                FAKE_LOG=str(HOME / "fake.log"), FAKE_MODE="transport",
                FAKE_API_CALLS="0")   # zero-call evidence: the Q4 retry gate's precondition

def spawn_logs(r):
    return sorted((r / "logs").glob("*.log"))

r = mk("est9c-restart",
       [{"id": "a", "type": "agent", "goal": "G"}],
       retry_backoff=[3.0, 1.0])
(HOME / "fake.log").unlink(missing_ok=True)

proc = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", "est9c-restart"],
                        env=runner_env(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

deadline = None
t_end = time.time() + 25
while time.time() < t_end:
    try:
        win = json.loads((r / "retry-window.json").read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        time.sleep(0.05); continue
    if isinstance(win.get("a"), dict):
        deadline = win["a"]["deadline"]
        break
check("runner persists {deadline, attempts} before sleeping",
      deadline is not None, "no retry-window.json appeared")
if deadline is not None:
    check("persisted record carries the attempt count",
          json.loads((r / "retry-window.json").read_text())["a"]["attempts"] == 1)
    time.sleep(0.2)
    os.kill(proc.pid, signal.SIGKILL)
    proc.wait()
    t_restart = time.time()
    subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", "est9c-restart"],
                   env=runner_env(), capture_output=True, text=True, timeout=120)
    rec = json.loads((r / "nodes" / "a.json").read_text())
    logs = spawn_logs(r)
    check("restart honors the window: no spawn before the persisted deadline",
          len(logs) >= 2 and logs[1].stat().st_mtime >= deadline - 0.2,
          f"deadline={deadline} mtimes={[round(l.stat().st_mtime, 2) for l in logs]}")
    check("the resumed boot waited (the window was real, not skipped)",
          len(logs) >= 2 and logs[1].stat().st_mtime >= t_restart)
    check("the surviving cap bounds total spawns to 3 across the restart",
          len(logs) == 3, f"spawn logs: {[l.name for l in logs]}")
    check("the node settles transport_exhausted with the cross-restart attempt total",
          rec.get("error_class") == "transport_exhausted" and rec.get("attempts") == 3
          and len(rec.get("attempts_log") or []) == 1, json.dumps(rec.get("error_class")))
    w = (r / "retry-window.json")
    kept = json.loads(w.read_text()) if w.exists() else {}
    check("the transient verdict keeps the spent cap persisted",
          kept.get("a", {}).get("attempts", 0) >= 2, kept)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
