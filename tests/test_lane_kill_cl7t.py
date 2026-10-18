#!/usr/bin/env python3
"""est-cl7t: node-targeted lane kill (action=kill / fail-lane).

Two independent agent lanes (a, b) run in parallel under the fake hermes
(FAKE_MODE=seat_timing, 8 s hold). Once both are in flight we call
act_kill(node="a"). Required behaviour:
  - lane a's in-flight child is SIGKILLed and its node record is terminal
    error_class=killed (a readable outcome, not a silent death);
  - sibling lane b keeps running and finishes status=done;
  - the run is NOT globally stopped (no stop.request marker, run not stopped).
RED before the feature: act_kill does not exist, so the kill never lands.
"""
import importlib.util
import json, os, shutil, subprocess, sys, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))

ROOT = BUILD.parent
sys.path.insert(0, str(ROOT))
HOME = BUILD / "home_cl7t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
RUNS = HOME / "workflows"
FAKE = str(BUILD / "fake")
LOG = BUILD / "fake_cl7t.log"

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1

def load_door():
    spec = importlib.util.spec_from_file_location("lane_kill_door", ROOT / "__init__.py")
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    return door

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
if LOG.exists(): LOG.unlink()

rid = "cl7t-kill"
r = RUNS / rid
(r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
nodes = [{"id": "a", "type": "agent", "goal": "lane a"},
         {"id": "b", "type": "agent", "goal": "lane b"}]
(r / "graph.json").write_text(json.dumps({"name": rid, "nodes": nodes}))
(r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 60}))

env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS), FAKE_LOG=str(LOG),
           FAKE_MODE="seat_timing", FAKE_SEAT_HOLD="8")
proc = subprocess.Popen([sys.executable, str(ROOT / "wf.py"), "run", rid], env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

t0 = time.time()
while time.time() - t0 < 60:
    if LOG.exists() and len(LOG.read_text().splitlines()) >= 2:
        break
    time.sleep(0.2)
check("both lanes in flight before the kill", LOG.exists() and len(LOG.read_text().splitlines()) >= 2)

door = load_door()
kr = door.act_kill({"run_id": rid, "node": "a"})
check("act_kill accepts a node-targeted kill", kr.get("ok") is True, json.dumps(kr))
kt = time.time()

try:
    proc.wait(timeout=240)
except subprocess.TimeoutExpired:
    proc.kill()
    check("run finished within 240s", False, "timeout")

rec_a = json.loads((r / "nodes" / "a.json").read_text()) if (r / "nodes" / "a.json").exists() else {}
rec_b = json.loads((r / "nodes" / "b.json").read_text()) if (r / "nodes" / "b.json").exists() else {}
check("lane a is terminal error_class=killed", rec_a.get("error_class") == "killed", json.dumps(rec_a)[:300])
check("lane a status failed", rec_a.get("status") == "failed", str(rec_a.get("status")))
check("lane a was cut short of its 8 s hold", 0 < (rec_a.get("ms") or 0) < 6000, f"ms={rec_a.get('ms')}")
check("sibling lane b kept running to done", rec_b.get("status") == "done", json.dumps(rec_b)[:300])
check("run was NOT globally stopped (no stop.request)", not (r / "stop.request").exists())
st = door.act_status({"run_id": rid})
check("run status is not stopped", st.get("status") != "stopped", str(st.get("status")))

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
