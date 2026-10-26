#!/usr/bin/env python3
"""#472 — the door ADMITS and the runner ENFORCES `maxItems`; `enum` widens.

Harvested from an audit wave: fix crews converting pstack playbooks to shelf
graphs hit the closed keyword set three ways — (a) `maxItems` ceilings on
fan-out item rosters (arena candidates 2-6, swarm items 2-8) refused, the cap
degrading to description prose (unenforceable); (b) `enum: [true,false]` on a
boolean gate-key field (bug-fix repro.reproduced) refused, forcing a bare
`type:'boolean'` with no message-level guard; (c) integer bounds on budget
fields (the still-unenforceable case — now named in the refusal's fallback
hint). Follows the #107/#96 law: enforce it, don't keep rejecting it — admit
EXACTLY one new keyword (`maxItems`, minItems' mirror, ENFORCED at harvest)
and widen `enum` placement onto the two extra closed domains (boolean,
integer) whose membership the harvest check trivially enforces. The door
never admits a constraint the harvester cannot enforce, and the unsupported-
keyword refusal now NAMES the set and the description-prose fallback.

Law:
  maxItems — legal only on type:"array"; non-negative int (bool refused).
             Harvest error: "{path}: expected at most N item(s)".
  enum     — placement widened to type:"string" | "boolean" | "integer";
             members homogeneous per domain (non-empty strings / booleans /
             integers; bool is never an integer member — #113's bool law).
             Still REJECTED on type-less, number-, array-, object-typed.
  minItems > maxItems (both well-formed) — unsatisfiable, refused at the door.
  The subset stays CLOSED: `uniqueItems` still gets the unsupported-keyword
  refusal, and that refusal now names the supported set + the fallback.

Covers (the four author tests of the issue's first commit, verbatim law,
plus door placement and the runner retry path):
  1. door admits maxItems (top level, nested, inside items, fanout.schema)
     and boolean/integer enums with homogeneous members;
  2. door refuses placement/value violations with typed {node, field, msg}
     errors (wrong type, omitted type, negative, float, string, bool;
     mixed-domain enum members; enum on number/array/object; unsatisfiable
     minItems>maxItems pair);
  3. harvest (wf.validate): committed-over-cap FAILS naming $.candidates;
     enum non-member FAILS for boolean and integer domains (and True never
     hits an integer enum's 1 rung); legal uses PASS at/below the cap and
     inside each enum set; malformed caps/enums IGNORED, never crash; every
     pre-existing message byte-stable;
  4. runner: over-cap answer takes the typed retry and the in-cap retry
     commits done (exactly two spawns, the retry prompt names the cap); a
     persistent over-cap answer ends error_class:"schema".
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
os.environ.pop("WF_RUNS_ROOT", None)
HOME = HERE / "home472"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")

sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402
import wf  # noqa: E402  (wf.py is stdlib-only and importable)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

V = wfcommon.validate_graph_errors

def agent_node(schema, goal="max 472"):
    return [{"id": "a", "type": "agent", "goal": goal, "schema": schema}]

CAP_SCHEMA = {"type": "object", "required": ["candidates"],
              "properties": {"candidates": {"type": "array", "minItems": 1,
                                            "maxItems": 2,
                                            "items": {"type": "string"}}}}

# ============ 1. door admits the cap and the widened enum ============
check("door accepts maxItems on type:array", V(agent_node(
    {"type": "array", "maxItems": 2, "items": {"type": "string"}})) == [],
    json.dumps(V(agent_node({"type": "array", "maxItems": 2, "items": {"type": "string"}}))))
check("door accepts maxItems:0 (non-negative, not positive)", V(agent_node(
    {"type": "array", "maxItems": 0})) == [],
    json.dumps(V(agent_node({"type": "array", "maxItems": 0}))))
check("door accepts the arena-candidates repro shape (minItems+maxItems interval)",
      V(agent_node(CAP_SCHEMA)) == [], json.dumps(V(agent_node(CAP_SCHEMA))))
_fan_cap = [{"id": "f", "type": "agent", "goal": "g",
             "fanout": {"items": ["i"], "schema": {
                 "type": "object", "properties": {
                     "rows": {"type": "array", "maxItems": 8,
                              "items": {"type": "string"}}}}}}]
check("door accepts maxItems on fanout.schema too (same schema_check runs there)",
      V(_fan_cap) == [], json.dumps(V(_fan_cap)))
check("door accepts enum:[true,false] on type:boolean (the bug-fix gate-key repro)",
      V(agent_node({"type": "boolean", "enum": [True, False]})) == [],
      json.dumps(V(agent_node({"type": "boolean", "enum": [True, False]}))))
check("door accepts an integer enum (budget-field ladder)", V(agent_node(
    {"type": "integer", "enum": [1, 2, 4]})) == [],
    json.dumps(V(agent_node({"type": "integer", "enum": [1, 2, 4]}))))
check("door keeps the string enum legal (byte-identical placement)", V(agent_node(
    {"type": "string", "enum": ["ship", "hold"]})) == [],
    json.dumps(V(agent_node({"type": "string", "enum": ["ship", "hold"]}))))
check("door accepts the cap + widened enum nested together", V(agent_node(
    {"type": "object", "properties": {
        "reproduced": {"type": "boolean", "enum": [True, False]},
        "tier": {"type": "integer", "enum": [1, 2, 4]},
        "lanes": {"type": "array", "maxItems": 6, "items": {"type": "string"}}}})) == [])

# ============ 2. door refuses dead constraints with typed errors ============
errs = [e for e in V(agent_node({"type": "string", "maxItems": 2}))
        if e["field"] == "schema.maxItems"]
check("maxItems on a NON-array schema REJECTED (enforceability law)",
      errs and "only legal on" in errs[0]["msg"], json.dumps(errs))
errs = [e for e in V(agent_node({"maxItems": 2})) if e["field"] == "schema.maxItems"]
check("maxItems with OMITTED type REJECTED (same law)", bool(errs), json.dumps(errs))
for bad in (-1, 1.5, "1", True, False, None, [1]):
    errs = [e for e in V(agent_node({"type": "array", "maxItems": bad}))
            if e["field"] == "schema.maxItems"]
    check(f"maxItems {bad!r} rejected as non-int/non-negative (bool refused)",
          errs and "non-negative integer" in errs[0]["msg"], json.dumps(errs))
errs = [e for e in V(agent_node({"type": "array", "minItems": 5, "maxItems": 2}))
        if e["field"] == "schema.maxItems"]
check("unsatisfiable minItems>maxItems REJECTED at the door (dead constraint)",
      errs and "unsatisfiable" in errs[0]["msg"], json.dumps(errs))
check("satisfiable interval admits clean", V(agent_node(
    {"type": "array", "minItems": 1, "maxItems": 6,
     "items": {"type": "string"}})) == [])
def enum_err(bad_schema):
    return [e for e in V(agent_node(bad_schema))
            if e["node"] == "a" and e["field"].endswith(".enum")]
check("boolean enum with a string member REJECTED (members must be booleans)",
      enum_err({"type": "boolean", "enum": ["a", "b"]})
      and enum_err({"type": "boolean", "enum": ["a", "b"]})[0]["msg"]
          .startswith("enum members must be a list of booleans"),
      json.dumps(enum_err({"type": "boolean", "enum": ["a", "b"]})))
check("integer enum with a bool member REJECTED (bool is never a member)",
      enum_err({"type": "integer", "enum": [1, True]})
      and "bool is never a member" in enum_err({"type": "integer", "enum": [1, True]})[0]["msg"],
      json.dumps(enum_err({"type": "integer", "enum": [1, True]})))
check("integer enum with a float member REJECTED",
      bool(enum_err({"type": "integer", "enum": [1, 2.5]})))
check("enum on type:number REJECTED (open domain, no membership law)",
      bool(enum_err({"type": "number", "enum": [1, 2]})))
check("enum on type:array REJECTED (still refused; placement law preserved)",
      bool(enum_err({"type": "array", "enum": ["a"], "items": {"type": "string"}})))
check("enum with OMITTED type REJECTED (same enforceability law)",
      bool(enum_err({"enum": ["a"]})))
check("enum placement refusal names the three admitted domains",
      enum_err({"enum": ["a"]})
      and "'string', 'boolean' or 'integer'" in enum_err({"enum": ["a"]})[0]["msg"],
      json.dumps(enum_err({"enum": ["a"]})))
errs = V(agent_node({"type": "array", "uniqueItems": True,
                     "items": {"type": "string"}}))
kw_err = [e for e in errs if "unsupported schema keyword" in e["msg"]]
check("door: uniqueItems still refused — the subset stays CLOSED", bool(kw_err),
      json.dumps(errs))
check("the refusal NAMES the supported set (now incl. maxItems)",
      kw_err and "supported: type, required, properties, items, description, enum, minItems, minLength, maxItems" in kw_err[0]["msg"],
      kw_err[0]["msg"] if kw_err else "no keyword error")
check("the refusal NAMES the description-prose fallback (the #472 ask)",
      kw_err and "description prose" in kw_err[0]["msg"]
      and "advisory" in kw_err[0]["msg"],
      kw_err[0]["msg"] if kw_err else "no keyword error")

# ============ 3. harvest-time enforcement (wf.validate direct) ============
# AUTHOR TEST 1: a committed answer OVER the cap FAILS, naming its path.
e = wf.validate({"candidates": ["a", "b", "c"]}, CAP_SCHEMA)
check("validate(): committed-over-cap refused naming $.candidates",
      e == ["$.candidates: expected at most 2 item(s)"], json.dumps(e))
check("validate(): at the cap commits clean (AUTHOR TEST: legal uses pass)",
      wf.validate({"candidates": ["a", "b"]}, CAP_SCHEMA) == [])
check("validate(): under the cap commits clean",
      wf.validate({"candidates": ["a"]}, CAP_SCHEMA) == [])
check("validate(): maxItems enforced on the top-level array itself",
      wf.validate(["a", "b"], {"type": "array", "maxItems": 1, "items": {"type": "string"}})
      == ["$: expected at most 1 item(s)"])
check("validate(): maxItems:0 accepts the empty array",
      wf.validate([], {"type": "array", "maxItems": 0}) == [])
check("validate(): over-cap on a wrong-typed value gets the type error, no pile-on",
      wf.validate({"candidates": "abc"}, CAP_SCHEMA) == ["$.candidates: expected array"])
check("validate(): malformed maxItems in a hand-built schema IGNORED, never crashes",
      wf.validate(["a"], {"type": "array", "maxItems": "two"}) == []
      and wf.validate(["a"], {"type": "array", "maxItems": True}) == []
      and wf.validate(["a"], {"maxItems": 0}) == [])
# AUTHOR TEST 2: enum NON-MEMBER FAILS in every admitted domain.
e = wf.validate({"reproduced": False}, {"type": "object", "required": ["reproduced"],
                                        "properties": {"reproduced": {
                                            "type": "boolean", "enum": [True]}}})
check("validate(): boolean enum non-member refused naming the allowed set",
      e == ["$.reproduced: not an allowed value (allowed: True)"], json.dumps(e))
e = wf.validate({"tier": 3}, {"type": "object", "required": ["tier"],
                              "properties": {"tier": {
                                  "type": "integer", "enum": [1, 2, 4]}}})
check("validate(): integer enum non-member refused naming the allowed set",
      e == ["$.tier: not an allowed value (allowed: 1, 2, 4)"], json.dumps(e))
e = wf.validate({"tier": True}, {"type": "object", "required": ["tier"],
                                 "properties": {"tier": {
                                     "type": "integer", "enum": [1, 2, 4]}}})
check("validate(): True NEVER satisfies an integer enum's 1 rung (#113 bool law)",
      e == ["$.tier: expected number"], json.dumps(e))
check("validate(): integral float may hit its integer rung (#113 contract)",
      wf.validate(2.0, {"type": "integer", "enum": [1, 2, 4]}) == [])
check("validate(): integral float outside the set still FAILS",
      wf.validate(3.0, {"type": "integer", "enum": [1, 2, 4]})
      == ["$: not an allowed value (allowed: 1, 2, 4)"])
# AUTHOR TEST 3: legal uses pass in every admitted domain.
check("validate(): boolean enum in-set passes",
      wf.validate(False, {"type": "boolean", "enum": [True, False]}) == []
      and wf.validate(True, {"type": "boolean", "enum": [True, False]}) == [])
check("validate(): integer enum in-set passes",
      wf.validate(4, {"type": "integer", "enum": [1, 2, 4]}) == [])
check("validate(): string enum keeps byte-identical refusal",
      wf.validate("maybe", {"type": "string", "enum": ["ship", "hold"]})
      == ["$: not an allowed value (allowed: 'ship', 'hold')"])
check("validate(): heterogeneous/malformed enum IGNORED, never crashes",
      wf.validate(5, {"type": "integer", "enum": [1, "x"]}) == []
      and wf.validate("x", {"enum": [True, False]}) == []
      and wf.validate(1, {"enum": ["a"]}) == [])
# byte-stability of everything the issue did not touch
classic = {"type": "object", "required": ["answer"], "properties": {"answer": {"type": "string"}}}
check("validate(): no-schema => no errors (unchanged)", wf.validate({"a": 1}, None) == [])
check("validate(): missing-required message byte-stable",
      wf.validate({}, classic) == ["$: missing required 'answer'"])
check("validate(): enum-less schema under a cap stays clean",
      wf.validate({"candidates": ["a"]},
                  {"type": "object", "required": ["candidates"],
                   "properties": {"candidates": {"type": "array", "items":
                                                 {"type": "string"}}}}) == [])

# ============ 4. runner: the typed-retry path, #96 harness shape ============
shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
(HOME / "fake.log").write_text("")

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 60}
    m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def wf_run(run_id, extra_env=None, timeout=180):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS), FAKE_LOG=str(HOME / "fake.log"),
               **(extra_env or {}))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def rec_of(r, nid):
    p = r / "nodes" / f"{nid}.json"
    return json.loads(p.read_text()) if p.exists() else {}

# AUTHOR TEST 4 (runner end of the retry ladder): over-cap answer retries into done.
r = mk("e472-retry", [{"id": "j", "type": "agent", "goal": "MINDANGLER e472-retry",
                       "schema": CAP_SCHEMA}])
(HOME / "fake.log").write_text("")
out = wf_run("e472-retry", {"FAKE_MODE": "cap_over_then_good"})
rec = rec_of(r, "j")
check("harvest: over-cap first answer is retried and the in-cap retry commits done",
      rec.get("status") == "done" and rec.get("output") == {"candidates": ["a", "b"]},
      json.dumps(rec)[:200])
n_j = (HOME / "fake.log").read_text().count("e472-retry")
check("exactly two spawns (first over-cap refused, retry committed)", n_j == 2, f"spawns={n_j}")
prompts = sorted((r / "logs").glob("j.a*.prompt.md"), key=lambda p: p.name)
check("retry prompt names the cap violation verbatim",
      len(prompts) == 2 and "failed schema validation" in prompts[1].read_text()
      and "expected at most 2 item(s)" in prompts[1].read_text(),
      prompts[1].read_text()[-300:] if len(prompts) == 2 else f"prompts={len(prompts)}")
check("first attempt's prompt carried the cap (schema_prompt_block dumps the schema dict)",
      prompts and '"maxItems"' in prompts[0].read_text())

# persistent over-cap -> error_class=schema, exactly the two attempts the
# type-violation path uses.
r = mk("e472-persist", [{"id": "k", "type": "agent", "goal": "verdict e472-persist",
                         "schema": CAP_SCHEMA}])
(HOME / "fake.log").write_text("")
out = wf_run("e472-persist", {"FAKE_MODE": "cap_always_bad"})
rec = rec_of(r, "k")
check("harvest: persistent over-cap ends the node error_class=schema (same as enum/type/min)",
      rec.get("status") == "failed" and rec.get("error_class") == "schema"
      and "schema validation" in rec.get("error", "")
      and "expected at most 2 item(s)" in rec.get("error", ""),
      json.dumps(rec)[:220])
n_k = (HOME / "fake.log").read_text().count("e472-persist")
check("persistent violation used exactly the two attempts the type-violation path uses",
      n_k == 2, f"spawns={n_k}")

print()
if ok:
    print("ALL PASS")
else:
    print("FAILURES PRESENT")
    sys.exit(1)
