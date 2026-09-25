#!/usr/bin/env python3
"""Library verbs + /wf command: save (from run_id / inline), library list, run from=<name>,
name validation, /wf list + replay instruction. Hermetic (fake launcher, sandboxed HOME)."""
import json, os, shutil, sys, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
HOME = BUILD / "home6"
os.environ["HERMES_HOME"] = str(HOME)
shutil.rmtree(HOME, ignore_errors=True)
import importlib.util
spec = importlib.util.spec_from_file_location("hw", str(BUILD.parent / "__init__.py"))
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
FAKE = str(BUILD / "fake")
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and cond
def call(**a): return json.loads(hw.handle(a))

G = {"name": "Lib Demo", "nodes": [
    {"id": "a", "type": "agent", "goal": "LIST: go"},
    {"id": "fan", "type": "agent", "after": ["a"], "fanout": {"items_from": "a.result", "goal": "item {item}"}},
    {"id": "g", "type": "gate", "after": ["fan"], "question": "ok?", "options": ["y", "n"]}]}

# L1 empty library
check("L1 library empty", call(action="library")["library"] == [])
check("L1b /wf on empty says so", "empty" in hw._wf_command(""))

# L2 save inline (name from graph, slugged), description kept
r = call(action="save", graph=G, name="lib-demo", description="demo graph")
check("L2 save inline", r.get("saved") == "lib-demo" and r.get("nodes") == 3, json.dumps(r))
lib = call(action="library")["library"]
check("L2b library lists it with counts", lib and lib[0]["name"] == "lib-demo" and lib[0]["gates"] == 1 and lib[0]["fanouts"] == 1
      and lib[0]["description"] == "demo graph", json.dumps(lib))

# L3 bad names rejected
check("L3 bad name rejected", "invalid library name" in json.dumps(call(action="save", graph=G, name="../evil")))
check("L3b run from unknown lists library", "no library graph" in json.dumps(call(action="run", **{"from": "nope"})))

# L4 run from=<name> actually runs (fake launcher) to the gate
r = call(action="run", **{"from": "lib-demo"}, hermes_bin=FAKE)
rid = r.get("run_id"); check("L4 run from=lib-demo launches", bool(rid), json.dumps(r))
st = call(action="wait", run_id=rid, timeout=60)
check("L4b replay reaches the gate", st.get("status") == "held" and (st.get("gate") or {}).get("id") == "g", json.dumps({k: st.get(k) for k in ("status", "gate")}))
g = json.load(open(HOME / "workflows" / rid / "graph.json"))
check("L4c run's graph name = library stem", g.get("name") == "lib-demo")

# L5 save FROM a run (round-trip), overwrite semantics
r = call(action="save", run_id=rid, name="lib-demo-v2")
check("L5 save from run_id", r.get("saved") == "lib-demo-v2")
check("L5b library has two", len(call(action="library")["library"]) == 2)

# L6 /wf command text
t = hw._wf_command("")
check("L6 /wf lists both", "lib-demo" in t and "lib-demo-v2" in t and "/wf <name>" in t, t[:120])
t = hw._wf_command("lib-demo ship the colors")
check("L6b /wf <name> note -> replay instruction with from + steer", 'from:"lib-demo"' in t and "steer" in t and "ship the colors" in t, t[:200])
check("L6c /wf unknown -> lists available", "Available: lib-demo" in hw._wf_command("zzz"))
check("L6d /wf bad name -> validation msg", "invalid library name" in hw._wf_command("../x"))

call(action="stop", run_id=rid)
print("ALL PASS" if ok else "FAILURES PRESENT"); sys.exit(0 if ok else 1)
