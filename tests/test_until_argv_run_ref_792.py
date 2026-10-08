#!/usr/bin/env python3
"""est-2ek.1.792 — an unresolved {run.KEY} in a gate's wait.until_argv is refused at the door.

run_context renders {run.KEY} in goal/context/question/profile and fan-out goals
only; a gate's wait.until_argv is exec'd as fixed argv and is never rendered. A
parent-authored gate holding '{run.python}' was admitted, and the machine gate then
died with FileNotFoundError on the literal token, forever, with no census ever run.
The door (run and amend) now refuses any surviving {run.KEY} in wait.until_argv,
naming the node, the argv index and the key, before any run write.

Hermetic (fake launcher, sandboxed HOME): same import convention as test_include_door.
"""
import importlib.util, json, os, shutil, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = Path(tempfile.mkdtemp(prefix="wf-until-argv-792-"))
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "runs")
os.environ["HERMES_WF_HERMES_BIN"] = str(BUILD / "tests" / "fake")
spec = importlib.util.spec_from_file_location("hw_door_792", BUILD / "__init__.py")
hw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw)
sys.path.insert(0, str(HERE))
import wf_test_isolation as _iso71
_iso71.install(hw)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (" " + str(detail)[:300] if not cond and detail else ""))
    ok = ok and bool(cond)

def call(**a):
    return json.loads(hw.handle(a))

ROOT = Path(os.environ["WF_RUNS_ROOT"])
def dirs():
    return set(p.name for p in ROOT.glob("*")) if ROOT.exists() else set()

def gate_graph(argv, name="argv792"):
    return {"name": name, "nodes": [
        {"id": "census", "type": "gate", "question": "wait for the census",
         "wait": {"until_argv": argv}}]}

hw._spawn_runner = lambda rr: 0        # persistence-only: graph.json is the artifact under test

# REFUSE with a run_context that names the key: the binding does not reach argv.
before = dirs()
r = call(action="run", graph=gate_graph(["{run.python}", "-c", "pass"]),
         run_context={"python": sys.executable})
err = r.get("error", "")
check("REFUSE bound key: error names wait.until_argv[0] and run.python",
      "wait.until_argv[0]" in err and "run.python" in err and not r.get("run_id"), r)
check("REFUSE bound key: no run directory created", before == dirs(), dirs() - before)

# REFUSE without any run_context: the literal token can never resolve either.
r = call(action="run", graph=gate_graph(["true", "{run.x}"]))
check("REFUSE no run_context: error names argv index 1 and run.x",
      "wait.until_argv[1]" in r.get("error", "") and "run.x" in r.get("error", ""), r)
check("REFUSE no run_context: still no run directory", before == dirs(), dirs() - before)

# dry_run takes the same door.
r = call(action="run", dry_run=True, graph=gate_graph(["{run.python}", "-c", "pass"]),
         run_context={"python": sys.executable})
check("REFUSE dry_run too", "wait.until_argv[0]" in r.get("error", "") and before == dirs(), r)

# A literal argv still launches, and run_context still binds goals.
g = gate_graph([sys.executable, "-c", "pass"], name="literal792")
g["nodes"].append({"id": "a", "type": "agent", "goal": "use {run.thing}"})
r = call(action="run", graph=g, run_context={"thing": "bound"})
rid = r.get("run_id")
check("literal argv + bound goal launches", bool(rid), r)
if rid:
    saved = json.loads((ROOT / rid / "graph.json").read_text())
    byid = {n["id"]: n for n in saved["nodes"]}
    check("literal argv committed byte-verbatim", byid["census"]["wait"]["until_argv"] == [sys.executable, "-c", "pass"])
    check("goal binding unchanged", byid["a"]["goal"] == "use bound", byid["a"])

    # amend takes the same door and leaves graph.json untouched on refusal.
    before_bytes = (ROOT / rid / "graph.json").read_bytes()
    bad = gate_graph(["{run.python}", "-c", "pass"], name="literal792")
    bad["nodes"].append({"id": "a", "type": "agent", "goal": "use bound"})
    r = call(action="amend", run_id=rid, graph=bad)
    check("amend REFUSES a surviving {run.KEY} in wait.until_argv",
          "wait.until_argv[0]" in r.get("error", "") and "run.python" in r.get("error", ""), r)
    check("amend refusal leaves graph.json byte-identical",
          (ROOT / rid / "graph.json").read_bytes() == before_bytes)

shutil.rmtree(HOME, ignore_errors=True)
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
