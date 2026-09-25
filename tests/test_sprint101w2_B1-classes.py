#!/usr/bin/env python3
"""sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop != failure.

#7: a stop that lands while a fan-out is mid-flight must (a) record the killed items as
error_class 'cancelled', (b) NOT produce a quorum failure from them, (c) leave the run
'stopped' in the read model (never 'failed' because of a stop).
#3: every failed record/event in a fake run tree carries an error_class from wf.ERROR_CLASSES.
"""
import json, os, shutil, subprocess, sys, threading, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
HOME = BUILD / "home-b1"
RUNS = HOME / "workflows"
env = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(BUILD / "fake-b1.log"))
FAKE = str(BUILD / "fake-b1")
sys.path.insert(0, str(BUILD.parent))
import wf, wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and cond

def mk(run_id, nodes, name="t"):
    r = RUNS / run_id
    if r.exists(): shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": name, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}))
    return r

if HOME.exists(): shutil.rmtree(HOME)
RUNS.mkdir(parents=True)
shutil.copy(BUILD / "fake_hermes.py", FAKE); os.chmod(FAKE, 0o755)

# ---- #7 stop mid-fan-out ----
r = mk("b1-stop", [{"id": "fan", "type": "agent",
                    "fanout": {"items": ["x", "y", "z"], "goal": "SLEEP 20 item {item}"}},
                   {"id": "after", "type": "agent", "after": ["fan"], "goal": "never"}], "stop")
p = subprocess.Popen([sys.executable, str(BUILD.parent / "wf.py"), "run", "b1-stop"],
                     env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(2.5)                                   # children spawned and sleeping
(r / "stop.request").write_text("1")
out, _ = p.communicate(timeout=60)
out = out.strip()
check("#7 runner exits WORKFLOW_STOPPED, not FAILED", out.startswith("WORKFLOW_STOPPED b1-stop"), out[-200:])
rec = json.loads((r / "nodes/fan.json").read_text()) if (r / "nodes/fan.json").exists() else {}
check("#7 fan-out record carries error_class=cancelled (no quorum failure)",
      rec.get("error_class") == "cancelled", json.dumps(rec)[:200])
ev = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
check("#7 no node.failed with error_class=quorum in events",
      not any(e["event"] == "node.failed" and e.get("error_class") == "quorum" for e in ev),
      [e for e in ev if e["event"] == "node.failed"])
check("#7 run.stopped is the last event", ev[-1]["event"] == "run.stopped", ev[-1])
st = wfcommon.run_state(r)
check("#7 read model: run status 'stopped'", st.get("status") == "stopped", st.get("status"))
check("#7 downstream never spawned", not (r / "nodes/after.json").exists())
byid = {n["id"]: n for n in json.loads((r / "graph.json").read_text())["nodes"]}
check("#7 cancelled node reads as pending (a resume re-drives it, never 'blocked by failed')",
      wfcommon.node_rec(r, byid["fan"], byid)[0] == "pending")
out2 = subprocess.run([sys.executable, str(BUILD.parent / "wf.py"), "run", "b1-stop"], env=env,
                      capture_output=True, text=True, timeout=120).stdout.strip()
check("#7 resume after stop re-runs the fan-out to done", out2.startswith("WORKFLOW_DONE b1-stop"), out2[-200:])

# ---- #3 closed set: every failed record/event in the tree above + a real failure ----
r2 = mk("b1-fail", [{"id": "a", "type": "agent", "goal": "CRASHME"}], "fail")
subprocess.run([sys.executable, str(BUILD.parent / "wf.py"), "run", "b1-fail"], env=env,
               capture_output=True, text=True, timeout=120)
bad = []
for rd in (r, r2):
    for f in (rd / "nodes").glob("*.json"):
        d = json.loads(f.read_text())
        if d.get("status") == "failed" and d.get("error_class") not in wf.ERROR_CLASSES:
            bad.append((f.name, d.get("error_class")))
    for l in (rd / "events.jsonl").read_text().splitlines():
        e = json.loads(l)
        if e["event"] == "node.failed" and e.get("error_class") not in wf.ERROR_CLASSES:
            bad.append((e["node"], e.get("error_class")))
check("#3 every failed record/event carries a class from ERROR_CLASSES", not bad, bad)
check("#3 crash is typed 'crashed'/'unknown' never unset",
      json.loads((r2 / "nodes/a.json").read_text()).get("error_class") in wf.ERROR_CLASSES)
check("#3 old names are gone from the closed set", not ({"max_turns", "no_json"} & set(wf.ERROR_CLASSES)))

print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
