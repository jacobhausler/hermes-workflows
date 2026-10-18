#!/usr/bin/env python3
"""Core-10 #89 review blocker: the EFFECTIVE synthesis prompt must not carry the
seat-only blindness prohibition.

The door bakes defaults.context ONTO every agent's own context (apply_graph_defaults
is an addition, not an override). A prohibition phrased for reviewers that lives in
defaults.context therefore reaches the synthesis seat too — which is REQUIRED to
merge and attribute the seat payloads — and the effective prompt contradicts itself.
Checking the raw `synthesis.context` field alone misses this (round-1 near-miss).

Regression law: seat-only rules live in per-seat `context`; defaults.context carries
only grounding rules every seat AND synthesis can obey. Asserted on the BAKED graph.
"""
import copy, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

SEAT_ONLY = "must not assume, guess, or address what they said"
MERGE_LAW = "You merge council verdicts"

g = json.load(open(ROOT / "examples" / "review" / "blind-council.workflow.json"))
baked = wfcommon.apply_graph_defaults(copy.deepcopy(g))
nodes = {n["id"]: n for n in baked["nodes"]}

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg}"  + (f"  << {detail}" if detail and cond is not True else "")
    ok += 1

# every reviewer seat, after baking, carries the seat-only blindness contract
for sid in ("seat-a", "seat-b", "seat-local"):
    ctx = nodes[sid].get("context", "")
    check(SEAT_ONLY in ctx, f"{sid} baked context keeps seat-only blindness contract")

# synthesis, after baking, must NOT — and must keep its merge mandate
sctx = nodes["synthesis"].get("context", "")
check(SEAT_ONLY not in sctx,
      "synthesis baked context free of seat-only prohibition (defaults is additive)")
check(MERGE_LAW in sctx, "synthesis keeps its merge mandate")

# defaults.context itself must be neutral enough for BOTH audiences
dctx = g["defaults"]["context"]
check(SEAT_ONLY not in dctx, "defaults.context carries no seat-only wording")

# terminology law: no undeclared field names in the synthesis instructions
check("open_items" not in sctx and "open_items" not in nodes["synthesis"].get("goal", ""),
      "synthesis prose names only schema fields (open_items removed; ledger is `risks`)")

# schema teeth: verify_list stays required
check("verify_list" in json.load(open(ROOT / "examples" / "review" / "blind-council.workflow.json"))
      ["nodes"][3]["schema"]["required"], "verify_list remains a required synthesis field")

# capability-class law, PINNED (est-7m6wv task-6): on a clean seat the council
# slots are unbound capability classes, and the door must refuse them BY NAME
# with the valid list — the documented "never a silent downgrade" contract is
# only real if a test says so.
import importlib.util as _ilu, os as _os, tempfile as _tf, io, contextlib
import wf_test_isolation as _iso71
_td = _tf.mkdtemp()
_os.environ["WF_RUNS_ROOT"] = _td + "/runs"; _os.environ["HERMES_HOME"] = _td
_spec = _ilu.spec_from_file_location("_bc_door", str(ROOT / "__init__.py"))
_bc = _ilu.module_from_spec(_spec)
with contextlib.redirect_stderr(io.StringIO()):   # reasoning-fallback notice is expected noise
    _spec.loader.exec_module(_bc)
_iso71.install(_bc)   # #71 law: a door caller neutralizes settings.runs_root too
with contextlib.redirect_stderr(io.StringIO()):
    _v = json.loads(_bc.handle({"action": "validate", "graph": g}))
check("clean seat: unbound capability class refuses BY NAME with the valid list",
      _v.get("ok") is False and "council_a" in json.dumps(_v), json.dumps(_v)[:160])

print(f"test_example_blind_council: {ok} checks PASS")
