#!/usr/bin/env python3
"""bd_2026-11-13-z79 — door rejections carry minimal accepting examples.

The contract (examples are DATA on the rule, not prose-doc strings):
  every door rejection payload carries errors:[{node, field, msg, example}]
  where `example` is the structured minimal ACCEPTING fragment for the rule
  that fired — None for a rule whose example is not yet banked. The four
  classes wave-4B seats actually hit are banked on wfcommon.RULE_EXAMPLES:
  unknown graph key, unresolvable items_from ref, bad fanout shape, gate
  cycle (plus the node-key sibling of the graph-key law and the
  items_from string-shape law). The start verb's five-line teach example
  rides the same bank as RULE_EXAMPLES["start_spec"] — #706's seam consumed,
  one bank instead of a second static copy.

Each class is pinned three ways:
  (1) the rejection row for the class CARRIES the rule's banked example
      (deep-equal to RULE_EXAMPLES[rule_id], a fresh copy per row);
  (2) the example itself PASSES the door — an example that would itself be
      refused is a worse trap than no example;
  (3) the door envelope stamps `example` on EVERY row, banked or not, so the
      key is universal where seats read it, and `wf.py validate` prints the
      fragment on the human channel (the one seats without --json see).

Run (suite-style):  python3 tests/test_door_examples_z79.py
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _k, _sub in (("HERMES_HOME", "home"), ("WF_RUNS_ROOT", "home/workflows")):
    os.environ[_k] = str(HERE / _sub) if _k == "HERMES_HOME" else str(HERE / "home" / "workflows")
os.makedirs(HERE / "home" / "workflows", exist_ok=True)
sys.path.insert(0, str(ROOT))

import wfcommon as W  # noqa: E402

_spec = importlib.util.spec_from_file_location("door_z79", ROOT / "__init__.py")
door = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(door)

FAILS = []
N = 0

def check(name, cond, detail=""):
    global N
    N += 1
    if not cond:
        FAILS.append(f"FAIL {name} {detail}")
        print(f"FAIL {name} {detail}")
    else:
        print(f"ok   {name}")


def row_for(errs, *, field=None, msg_frag=None):
    hits = [e for e in errs if isinstance(e, dict)
            and (field is None or e.get("field") == field)
            and (msg_frag is None or msg_frag in e.get("msg", ""))]
    assert len(hits) == 1, f"expected exactly 1 row field={field} frag={msg_frag}, got {json.dumps(hits)}"
    return hits[0]


# The rejection graphs: one per class, each tripping exactly that rule.
SOLO = {"id": "solo", "type": "agent", "goal": "say hi"}
G_UNKNOWN_GRAPH_KEY = {"name": "z79-ukg", "nodes": [dict(SOLO)], "nodez": []}
G_UNKNOWN_NODE_KEY = {"name": "z79-unk", "nodes": [dict(SOLO, colour="red")]}
G_ITEMS_FROM = {"name": "z79-ifr", "nodes": [
    {"id": "collect", "type": "agent", "goal": "list the files"},
    {"id": "review", "type": "agent", "after": ["collect"],
     "fanout": {"items_from": ["not", "a", "string"]}}]}
G_ITEMS_FROM_HEAD = {"name": "z79-ifh", "nodes": [
    {"id": "collect", "type": "agent", "goal": "list the files"},
    {"id": "review", "type": "agent",
     "fanout": {"items_from": "nowhere.items", "goal": "review {item}"}}]}
G_FANOUT_SHAPE = {"name": "z79-fan", "nodes": [dict(SOLO, fanout="nope")]}
G_FANOUT_GOAL = {"name": "z79-fang", "nodes": [dict(SOLO, fanout={"goal": 5, "items": ["a"]})]}
G_GATE_CYCLE = {"name": "z79-cyc", "nodes": [
    {"id": "plan", "type": "agent", "goal": "draft the plan", "after": ["build"]},
    {"id": "approve", "type": "gate", "after": ["plan"], "question": "ship?"},
    {"id": "build", "type": "agent", "goal": "build it", "after": ["approve"]}]}

# ---------- (1) the four classes carry their rule's example on the row ----------
def door_errors(graph):
    bad = door._validation_error(graph)
    assert bad is not None, f"door accepted {graph.get('name')}: {bad}"
    return bad["errors"]

r = row_for(door_errors(G_UNKNOWN_GRAPH_KEY), field="nodez")
check("class unknown-graph-key: row carries the graph-key example",
      r.get("example") == W.RULE_EXAMPLES["unknown_graph_key"], json.dumps(r)[:300])

r = row_for(door_errors(G_UNKNOWN_NODE_KEY), field="colour")
check("class unknown-node-key (node sibling): row carries the node example",
      r.get("example") == W.RULE_EXAMPLES["unknown_node_key"], json.dumps(r)[:300])

r = row_for(door_errors(G_ITEMS_FROM), field="fanout.items_from")
check("class unresolvable-items-from (string shape): row carries the ref example",
      r.get("example") == W.RULE_EXAMPLES["fanout_items_from"], json.dumps(r)[:300])
r = row_for(door_errors(G_ITEMS_FROM_HEAD), field="fanout.items_from", msg_frag="must be an ancestor")
check("class unresolvable-items-from (head law): row carries the producer-pair example",
      r.get("example") == W.RULE_EXAMPLES["fanout_items_from_head"], json.dumps(r)[:300])

r = row_for(door_errors(G_FANOUT_SHAPE), field="fanout", msg_frag="must be an object")
check("class bad-fanout-shape (object law): row carries the fanout example",
      r.get("example") == W.RULE_EXAMPLES["fanout_shape"], json.dumps(r)[:300])
r = row_for(door_errors(G_FANOUT_GOAL), field="fanout.goal")
check("class bad-fanout-shape (goal law): row carries the fanout example",
      r.get("example") == W.RULE_EXAMPLES["fanout_shape"], json.dumps(r)[:300])

r = row_for(door_errors(G_GATE_CYCLE), field="after", msg_frag="cycle in graph")
check("class gate-cycle: row carries the acyclic-chain example",
      r.get("example") == W.RULE_EXAMPLES["gate_cycle"], json.dumps(r)[:300])

# structural + node halves refuse with the example AT SOURCE too (a direct
# validate_graph_errors caller is a door caller in the engine's own wording).
r = row_for(W.structural_graph_errors(G_UNKNOWN_GRAPH_KEY), field="nodez")
check("source pin: structural_graph_errors itself attaches the example",
      r.get("example") == W.RULE_EXAMPLES["unknown_graph_key"])
r = row_for(W.validate_graph_errors(G_GATE_CYCLE["nodes"]), field="after", msg_frag="cycle in graph")
check("source pin: validate_graph_errors itself attaches the cycle example",
      r.get("example") == W.RULE_EXAMPLES["gate_cycle"])

# ---------- (2) every banked example PASSES the door ----------
def accept(name, graph):
    check(f"example accepts: {name}", door._validation_error(graph) is None,
          json.dumps(door._validation_error(graph) or "")[:300])

E = W.RULE_EXAMPLES
accept("unknown_graph_key (whole graph)", copy.deepcopy(E["unknown_graph_key"]))
accept("unknown_node_key (wrapped in nodes)", {"nodes": [copy.deepcopy(E["unknown_node_key"])]})
accept("fanout_shape (wrapped on an agent)",
       {"nodes": [{"id": "fan", "type": "agent", "fanout": copy.deepcopy(E["fanout_shape"])}]})
accept("fanout_items_from (wrapped with its producer)",
       {"nodes": [{"id": "collect", "type": "agent", "goal": "list the files"},
                  {"id": "rev", "type": "agent", "after": ["collect"],
                   "fanout": copy.deepcopy(E["fanout_items_from"])}]})
accept("fanout_items_from_head (whole graph)", copy.deepcopy(E["fanout_items_from_head"]))
accept("gate_cycle (whole graph)", copy.deepcopy(E["gate_cycle"]))

for rid, frag in E.items():
    if rid == "start_spec":
        continue  # the start verb's input example is TEXT, pinned right below
    check(f"example is structured data: {rid}", isinstance(frag, (dict, list)), type(frag).__name__)

# The #706 seam, consumed: the start verb's refusal example is RENDERED FROM
# THIS BANK, not a second static copy (empty input = the purest misuse probe).
_refusal = door._wfstart.parse_input("")[1]
check("start_spec seam: the start verb's refusal example IS the banked row",
      _refusal is not None and _refusal["example"] == E["start_spec"]
      and _refusal["usage"].endswith(E["start_spec"]),
      json.dumps(_refusal)[:300])

# ---------- (3) the KEY is universal on every rejection row ----------
mixed = {"name": "z79-univ", "nodes": [dict(SOLO, timeout=-5)],
         "nodez": [], "plan": None}
errs = door_errors(mixed)
check("envelope law: every row of a door rejection carries `example`",
      all("example" in e for e in errs), json.dumps(errs)[:400])
unbanked = row_for(errs, field="timeout")
check("envelope law: an unbanked rule rides example=None (key present, honest)",
      unbanked["example"] is None, json.dumps(unbanked))

# rows are independent copies — mutating one never scribbles on the table
errs_a = door_errors(G_GATE_CYCLE)
row_for(errs_a, msg_frag="cycle in graph")["example"]["nodes"].append({"id": "junk"})
check("the table is immutable through the row (deep copy per rejection)",
      W.RULE_EXAMPLES["gate_cycle"]["nodes"].__len__() == 3
      and door_errors(G_GATE_CYCLE)[0]["example"] == E["gate_cycle"])

# ---------- the human channel of `wf.py validate` prints the fragment ----------
with tempfile.TemporaryDirectory(prefix="z79-cli-") as home:
    env = dict(os.environ, HERMES_HOME=home, WF_RUNS_ROOT=str(Path(home) / "wf"))
    gp = Path(home) / "cycle.workflow.json"
    gp.write_text(json.dumps(G_GATE_CYCLE))
    r = subprocess.run([sys.executable, str(ROOT / "wf.py"), "validate", str(gp)],
                       capture_output=True, text=True, env=env, timeout=120)
    check("wf.py validate: red verdict exits 1", r.returncode == 1, f"rc={r.returncode}")
    check("wf.py validate: human mode names the cycle defect",
          "cycle in graph" in r.stdout, r.stdout[:300])
    check("wf.py validate: human mode prints the accepting example",
          "accepting example:" in r.stdout and '"approve"' in r.stdout, r.stdout[:500])

print(f"{'FAILED' if FAILS else 'OK'}: {len(FAILS)} failure(s) across {N} checks")
sys.exit(1 if FAILS else 0)
