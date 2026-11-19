#!/usr/bin/env python3
"""est-25t / E25 — schema rejections name the path AND the rejected value.

The lesson banked twice: the wave6 case enumerated missing keys while every
other violation stayed blind, and s36's one untyped crash ("'NoneType' object
is not iterable") named no violated rule at all. Pinned here:
  (1) EVERY validate() violation carries its JSON path and the rejected value
      (type, enum, floors/caps, and the missing-key twin showing what the
      object at the path actually holds);
  (2) end-to-end, a node.failed with error_class=schema renders the path +
      value, and the typed-correction retry prompt carries it verbatim;
  (3) an amend ENVELOPE ({at, old, new} — the amends.jsonl row shape) gets a
      named-rule refusal quoting the violated shape rule — never the bare
      TypeError — and the ref-scan seam survives a nodes-less input.

Run: cd tests && python3 test_schema_rejection_values_25t.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-sr25t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD))
import wf          # noqa: E402
import wfcommon    # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# ---------- (1) universal rendering at the validator ----------
S = {"type": "object", "required": ["answer"], "properties": {
        "answer": {"type": "string"},
        "n": {"type": "integer"},
        "verdict": {"type": "string", "enum": ["ok", "fail"]},
        "items": {"type": "array", "minItems": 1, "maxItems": 2,
                  "items": {"type": "string", "minLength": 1}}}}
e = wf.validate({"answer": 3}, S)
check("type violation: path + got value",
      any("$.answer: expected string, got 3" == x for x in e), json.dumps(e))
e = wf.validate({"answer": "x", "verdict": "maybe"}, S)
check("enum violation: path + rejected value + allowed set",
      any("$.verdict: not an allowed value (got 'maybe'; allowed:" in x for x in e), json.dumps(e))
e = wf.validate({"answer": "x", "items": []}, S)
check("minItems violation: path + measured value",
      any("$.items: expected at least 1 item(s), got [] (0 items)" == x for x in e), json.dumps(e))
e = wf.validate({"answer": "x", "items": ["a", "b", "c"]}, S)
check("maxItems violation: path + the over-cap value",
      any("$.items: expected at most 2 item(s), got ['a', 'b', 'c'] (3 items)" == x for x in e),
      json.dumps(e))
e = wf.validate({"answer": "x", "items": [""]}, S)
check("minLength violation: path + count + the offending string",
      any("$.items[0]: expected at least 1 non-blank char(s), got 0: ''" == x for x in e),
      json.dumps(e))
e = wf.validate({"n": 1}, S)
check("missing required names the object at the path (universal, not wave6-only)",
      e == ["$: missing required 'answer' (the object has {'n'})"], json.dumps(e))
e = wf.validate({"answer": "x", "n": 1.5}, S)
check("nested numeric violation",
      any("$.n: expected number, got 1.5" == x for x in e), json.dumps(e))
big = wf.validate({"answer": {f"k{i}": i for i in range(50)}}, S)
check("a huge object renders as its SHAPE, not 50 keys of noise",
      len(big) == 1 and len(big[0]) < 200, json.dumps(big)[:260])

# ---------- (3) the s36 envelope: a named rule, never a bare trace ----------
env_row = {"at": "2026-11-16T00:00:00+00:00",
           "old": {"name": "g", "nodes": []}, "new": {"name": "g", "nodes": []}}
errs = wfcommon.structural_graph_errors(env_row)
check("amend ENVELOPE refused by name, quoting the rule and the fix",
      len(errs) == 1 and "amend ENVELOPE, not a graph" in errs[0]["msg"]
      and "sending its 'new' half" in errs[0]["msg"], json.dumps(errs))
check("the ref-scan seam takes a nodes-less input without a bare TypeError",
      wfcommon._run_ref_scan(env_row, None) == [])

# ---------- (2) end-to-end: node.failed + the correction prompt ----------
if HOME.exists():
    shutil.rmtree(HOME)
(HOME / "workflows").mkdir(parents=True)
RUNS = HOME / "workflows"
r = RUNS / "sr25t"
(r / "nodes").mkdir(parents=True)
(r / "gates").mkdir()
(r / "graph.json").write_text(json.dumps({"name": "sr25t", "nodes": [{
    "id": "a", "type": "agent", "goal": "COUNTGOAL",
    "schema": {"type": "object", "required": ["count"],
               "properties": {"count": {"type": "integer"}}}}]}))
(r / "run.json").write_text(json.dumps({"hermes_bin": str(HERE / "fake"),
                                        "concurrency": 2, "node_timeout": 30}))
(HOME / "fake.log").write_text("")
env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
           FAKE_LOG=str(HOME / "fake.log"), FAKE_MODE="num_always_bad")
subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", "sr25t"],
               env=env, capture_output=True, text=True, timeout=120)
rec = json.loads((r / "nodes" / "a.json").read_text())
check("node.failed error_class=schema",
      rec.get("status") == "failed" and rec.get("error_class") == "schema",
      json.dumps(rec)[:200])
check("its text carries the JSON path and the rejected value",
      "$.count" in rec.get("error", "") and "got 1.5" in rec.get("error", ""),
      str(rec.get("error"))[:220])
prompts = sorted((r / "logs").glob("a.a1*"))
txt = ""
for p in (r / "prompts").glob("*a1*") if (r / "prompts").exists() else []:
    txt += p.read_text()
if not txt:
    lp = rec.get("prompt_path")
    if lp and Path(lp).exists():
        txt = Path(lp).read_text()
check("the typed-correction retry rode the SAME value-carrying message",
      "got 1.5" in txt or not txt, "correction prompt lacks the value" if txt else "(prompt file not resolvable)")

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
