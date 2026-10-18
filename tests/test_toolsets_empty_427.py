#!/usr/bin/env python3
"""issue #427 (reporter marcobox): `toolsets: []` on an agent node omitted -t
and silently BROADENED the child to the seat's full default toolsets — the
exact opposite of the author's declared minimisation, and a contradiction of
_filter_child_toolsets' own docstring ("None ONLY when the author declared
nothing at all"; omission "selects the seat's full default toolsets — a
silent broadening"). Measured on Hermes v0.22.1: a [] node called read_file
and terminal.

The core cannot express zero toolsets at -t (hermes_cli/oneshot.py
_normalize_toolsets collapses an empty value to "use config defaults"), so
the honored branch of the issue's expectation is impossible and the refused
branch is implemented: validate_graph_errors (the door) REJECTS a
declared-EMPTY selection at graph load, naming node+key+value and offering
the author's real options; the spawn seam keeps failing CLOSED but now
RECORDS one node.clamped for graphs persisted before the gate (old-run
resume), so the broadening is visible, never silent.
"""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))

ROOT = BUILD.parent
sys.path.insert(0, str(ROOT))

fails = 0
total = 0
def check(label, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1

# ---- (0) RED anchor (exact reported probe): the seam alone still says None
# ---- for every declared-empty spelling — the bug's root. Post-fix this is
# ---- NOT a honor (the door below refuses it); the seam keeps fail-closed.
spec = importlib.util.spec_from_file_location("e427_wf", ROOT / "wf.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)
probe_run = BUILD / "probe_e427"
probe_run.mkdir(parents=True, exist_ok=True)
for ts in ([], "", "  ", ","):
    out = wf._filter_child_toolsets(probe_run, {"_clamp_warned": set()},
                                    {"id": "a", "type": "agent", "goal": "g",
                                     "toolsets": ts})
    check(f"(0) seam stays fail-closed (None) for declared-empty {ts!r}", out is None,
          repr(out))
for _i, ts in enumerate((["file"], "file", "all")):   # 'none' is the omitted-
    out = wf._filter_child_toolsets(probe_run, {"_clamp_warned": set()},   # flag
                                    {"id": f"s{_i}", "type": "agent",   # sentinel
                                     "goal": "g", "toolsets": ts})   # (est-flah)
    check(f"(0) seam honors non-empty {ts!r} unchanged", out is not None, repr(out))

# ---- (1) GREEN: the door REFUSES every declared-empty spelling, naming ----
# ---- node+key+value and offering the real escape (a name, or "none").     ----
dhome = BUILD / "home_e427"
shutil.rmtree(dhome, ignore_errors=True)
dhome.mkdir(parents=True)
os.environ["HERMES_HOME"] = str(dhome)
os.environ["WF_RUNS_ROOT"] = str(dhome / "workflows")
os.environ["HERMES_WF_HERMES_BIN"] = str(BUILD / "fake")
dspec = importlib.util.spec_from_file_location("e427_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(dspec)
dspec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)

def run_err(graph):
    e = door._validation_error(dict(graph, name="e427"))
    return (e or {}).get("error", ""), json.dumps(e or {})

for bad in ([], "", "   ", ",", " ,, "):
    err, blob = run_err({"nodes": [{"id": "a", "type": "agent", "goal": "g",
                                    "toolsets": bad}]})
    ok = ("error" in blob and "toolsets" in blob and '"a"' in blob
          and "EMPTY" in blob and "BROADENS" in blob and "opt out" in blob)
    check(f"(1) door REFUSES toolsets={bad!r} naming node+key+value", ok, err[:200])

for good in (["terminal"], "terminal", ["web", "files"], "none", "all",
             ["none"], "file,mcp__x"):
    err, blob = run_err({"nodes": [{"id": "a", "type": "agent", "goal": "g",
                                    "toolsets": good}]})
    check(f"(1) door ACCEPTS toolsets={good!r} (honored shapes intact)",
          "error" not in blob, err[:200])

# ---- (2) old-run resume: a graph persisted BEFORE the gate carries []   ----
# ---- into the spawn seam anyway. The seam must still fail closed (None,  ----
# ---- -t omitted) but RECORD one node.clamped — visible, never silent.    ----
run = dhome / "run_e427"
run.mkdir(parents=True, exist_ok=True)
meta = {"_clamp_warned": set()}
out = wf._filter_child_toolsets(run, meta, {"id": "a", "type": "agent",
                                            "goal": "g", "toolsets": []})
ev = (run / "events.jsonl")
lines = [json.loads(x) for x in ev.read_text().splitlines()] if ev.exists() else []
clamped = [e for e in lines if e.get("event") == "node.clamped"
           and e.get("node") == "a" and e.get("kind") == "toolsets"]
check("(2) persisted-empty still fails closed to None (no crash, no -t)",
      out is None, repr(out))
check("(2) persisted-empty RECORDS node.clamped (never silent broadening)",
      len(clamped) == 1 and "BROADENS" in str(clamped[0].get("clamped")),
      json.dumps(lines)[:200])
out2 = wf._filter_child_toolsets(run, meta, {"id": "a", "type": "agent",
                                             "goal": "g", "toolsets": []})
lines2 = [json.loads(x) for x in ev.read_text().splitlines()]
n2 = sum(1 for e in lines2 if e.get("event") == "node.clamped"
         and e.get("node") == "a" and e.get("kind") == "toolsets")
check("(2) re-spawn does not spam: still ONE clamp event per (node,kind,shape)",
      out2 is None and n2 == 1, f"{n2} events")

# ---- (3) the contract's first leg stays honest: NO declaration and a      ----
# ---- hostile shape must return None with NO node.clamped noise.           ----
before = len([e for e in lines2 if e.get("event") == "node.clamped"])
wf._filter_child_toolsets(run, meta, {"id": "b", "type": "agent", "goal": "g"})
wf._filter_child_toolsets(run, meta, {"id": "b", "type": "agent", "goal": "g",
                                      "toolsets": {"hostile": 1}})
after = len([json.loads(x) for x in ev.read_text().splitlines()
             if json.loads(x).get("event") == "node.clamped"])
check("(3) undeclared + hostile shapes: None, NO clamp event (unchanged)",
      after == before, f"{before}->{after}")

print(f"ALL PASS ({total})" if not fails else f"{fails} FAILURE(S)")
sys.exit(0 if not fails else 1)
