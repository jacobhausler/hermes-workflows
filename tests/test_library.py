#!/usr/bin/env python3
"""Library verbs + /wf command: save (from run_id / inline), library list, run from=<name>,
name validation, /wf list + replay instruction. Hermetic (fake launcher, sandboxed HOME)."""
import json, os, shutil, sys, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
HOME = BUILD / "home6"
os.environ["HERMES_HOME"] = str(HOME)
# #71 (r5-corrected): HERMES_HOME alone does NOT sandbox the shelf — a lane process
# carries the context-local home override which outranks the env, so runs_root()/
# library_root() resolve to the SHARED estate shelf. And WF_RUNS_ROOT only outranks
# the home-derived DEFAULT — it does NOT outrank an owner-configured
# plugins.entries.hermes-workflows.settings.runs_root, which wins first (resolver
# precedence #42, owner design). That is why these tests pin BOTH: the env var AND,
# via wf_test_isolation.install below, the plugin's settings.runs_root to the
# identical scratch root. Set only one and these saves pollute production
# (shelf-is-live law).
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
shutil.rmtree(HOME, ignore_errors=True)
import importlib.util
spec = importlib.util.spec_from_file_location("hw", str(BUILD.parent / "__init__.py"))
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
import wf_test_isolation as _iso71; _iso71.install(hw)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT
FAKE = str(BUILD / "fake")
os.environ["HERMES_WF_HERMES_BIN"] = FAKE
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
r = call(action="run", **{"from": "lib-demo"})
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
check("L6b /wf <name> note -> atomic replay binding", 'from:"lib-demo"' in t and 'run_context:"ship the colors"' in t and "steer" not in t, t[:200])
check("L6c /wf unknown -> lists available", "Available: lib-demo" in hw._wf_command("zzz"))
check("L6d /wf bad name -> validation msg", "invalid library name" in hw._wf_command("../x"))

# L7 F-2 (#62) quarantine fixture — EXACT pair: valid good.json beside the
# malformed broken.json. Fail-closed on the entry (typed refusal), fail-open on
# the library (nothing crashes, the good entry stays fully usable).
import json as _json
good = {"name": "good", "nodes": [{"id": "e", "type": "echo", "output": 1}]}
broken = {"meta": {"description": "junk"}, "graph": {"nodes": ["oops"]}}
for stem, doc in (("good", good), ("broken", broken)):
    (Path(HOME) / "workflows" / "library" / (stem + ".json")).write_text(_json.dumps(doc))
out = call(action="library")
check("L7 library lists good beside broken, no crash",
      "good" in {x["name"] for x in out["library"]}
      and "broken" not in {x["name"] for x in out["library"]}, _json.dumps(out))
check("L7b broken is named with its typed refusal reason",
      any(q["name"] == "broken" and q["reason"] == "invalid: nodes[0] is not an object"
          for q in out.get("quarantined", [])), _json.dumps(out.get("quarantined")))
check("L7c run from=good works while broken sits there",
      bool(call(action="run", **{"from": "good"}).get("run_id")))
check("L7d run from=broken nudges, never crashes",
      "no library graph" in call(action="run", **{"from": "broken"}).get("error", ""))
check("L7e typo hint still works beside broken",
      "good" in call(action="run", **{"from": "good-typo"}).get("closest", []))
t = hw._wf_command("")
check("L7f /wf lists both rows; bad shows WHY it was refused",
      "good" in t and "broken" in t and "invalid: nodes[0] is not an object" in t, t[:200])
t = hw._wf_command("broken")
check("L7g /wf <bad> shows the refusal, not a crash",
      "refused: invalid: nodes[0] is not an object" in t, t[:160])
(Path(HOME) / "workflows" / "library" / "broken.json").unlink()
out = call(action="library")
check("L7h removing broken fully restores (no skip rows at all)",
      {x["name"] for x in out["library"]} >= {"good", "lib-demo", "lib-demo-v2"}
      and "skipped" not in out and "quarantined" not in out, _json.dumps(out)[:200])

call(action="stop", run_id=rid)
print("ALL PASS" if ok else "FAILURES PRESENT"); sys.exit(0 if ok else 1)
