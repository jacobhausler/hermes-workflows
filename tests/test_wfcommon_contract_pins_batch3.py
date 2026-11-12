"""est-ckxqk: batch-3 direct contract pins for the five wfcommon callables still at ZERO direct test references at shipped tip c7f24df (requires_errors, requires_plugin_errors, result_errors, run_context_contract_errors, wall_invariant_errors); every expectation MEASURED against that tip; pointer here (AGENTS.md hint cap full); house shape per merged #620/#624. Stdlib, serial."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/.."); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
SH = lambda rows: all(set(r) == {"node", "field", "msg"} for r in rows)
AG = lambda nid, **kw: dict({"type": "agent"}, **kw, id=nid)
REQ_MSG = 'requires must be a non-empty object {"<ancestor>": ["field", "dotted.path", ...]}'
RC_MSG = "run_context contract must be a non-empty object (required and/or defaults)"
check("row-shape + absent-key laws: every row is exactly {node, field, msg}; absent key or node-without-key is []",
      W.requires_errors([AG("n")]) == [] and SH(W.result_errors({"result": "zz", "nodes": [AG("n")]}))
      and SH(W.requires_plugin_errors({"requires_plugin": "x"})) and SH(W.run_context_contract_errors({"run_context": {}}))
      and SH(W.wall_invariant_errors([AG("g", type="gate", hold_timeout=10), AG("a", after=["g"], timeout=999)]))
      and W.result_errors({}) == [] == W.requires_plugin_errors({}) == W.run_context_contract_errors({})
      and W.result_errors("z") == [] == W.requires_plugin_errors(5) == W.requires_errors("junk")
      and W.requires_errors([AG("n"), "junk", None]) == [])
check("requires: {} / non-dict -> the ONE named object row at the offending node id",
      all(W.requires_errors([AG("n", requires=r)]) == [{"node": "n", "field": "requires", "msg": REQ_MSG}] for r in ({}, "x", 5, [])))
check("requires: closure is the TRANSITIVE after-chain (parents omitted builds it from the nodes' own after lists); outside it, refused",
      W.requires_errors([AG("a"), AG("e", after=["a"]), AG("n", after=["e"], requires={"a": ["f"]})]) == []
      and (e := W.requires_errors([AG("a"), AG("n", after=["a"], requires={"zz": ["f"]})])) == [
          {"node": "n", "field": "requires", "msg": e[0]["msg"]}] and "not an ancestor" in e[0]["msg"])
check("requires: empty path list and blank/non-str path entries refused at field requires.<ancestor>",
      all(len(e := W.requires_errors([AG("a"), AG("n", after=["a"], requires={"a": p})])) == n
          and all(r["field"] == "requires.a" and SH([r]) for r in e)
          for p, n in (([], 1), (["", 7], 2), (["ok", 5], 1)))
      and "non-empty list" in W.requires_errors([AG("a"), AG("n", after=["a"], requires={"a": []})])[0]["msg"]
      and "[0] ''" in (e := W.requires_errors([AG("a"), AG("n", after=["a"], requires={"a": ["", 7]})]))[0]["msg"])
check("requires_plugin: malformed values incl. non-str are the named dot-integer row, never a crash; well-formed passes",
      all(e == [{"node": None, "field": "requires_plugin", "msg": e[0]["msg"]}] and "must be a dot-integer version" in e[0]["msg"]
          for v in ("x", 5, "", "1.x", "1.2.0-beta") for e in [W.requires_plugin_errors({"requires_plugin": v})])
      and W.requires_plugin_errors({"requires_plugin": "1.2.0"}) == [])
check("result: missing/non-str id and gate targets are the named rows; agent target passes",
      all(e == [{"node": None, "field": "result", "msg": e[0]["msg"]}] and "must name an existing node id" in e[0]["msg"]
          for rid in ("zz", 5) for e in [W.result_errors({"result": rid, "nodes": [AG("n")]})])
      and "is a gate; name the agent, echo or join node" in (e := W.result_errors(
          {"result": "g", "nodes": [AG("g", type="gate")]}))[0]["msg"]
      and W.result_errors({"result": "n", "nodes": [AG("n")]}) == [])
check("run_context: empty/non-dict block, unknown sibling key, and the required-list grammar rows",
      all(W.run_context_contract_errors({"run_context": c}) == [{"node": None, "field": "run_context", "msg": RC_MSG}] for c in ({}, [], 5))
      and W.run_context_contract_errors({"run_context": {"zz": 1}}) == [
          {"node": None, "field": "run_context.zz", "msg": 'unknown key; allowed: ["defaults", "required"]'}]
      and all((e := W.run_context_contract_errors({"run_context": {"required": r}}))[0]["msg"] == "required must be a non-empty list of identifier strings"
              and e[0]["field"] == "run_context.required" for r in (5, [], ["a-b"], ["k", 5]))
      and (e := W.run_context_contract_errors({"run_context": {"required": ["k", "k"]}}))[0]["msg"] == "required keys must be unique")
check("run_context: declared-but-unreferenced refused; referenced in a node goal passes; defaults rows named",
      "never referenced as {run.KEY}" in (e := W.run_context_contract_errors(
          {"run_context": {"required": ["k"]}, "nodes": [AG("n", goal="{run.other}")]}))[0]["msg"]
      and e[0]["field"] == "run_context.required"
      and W.run_context_contract_errors({"run_context": {"required": ["k"]}, "nodes": [AG("n", goal="{run.k}")]}) == []
      and all((e := W.run_context_contract_errors({"run_context": {"defaults": d}}))[0]["msg"] ==
              "defaults must be a non-empty object of identifier -> non-empty string" and e[0]["field"] == "run_context.defaults" for d in ({}, 5))
      and (e := W.run_context_contract_errors({"run_context": {"defaults": {"k": "  "}}}))[0]["msg"] == "defaults['k'] must be a non-empty string")
check("wall #475: clean graph passes (non-dict nodes filtered); hold above the max lane wall -> one {node, field} row per offending gate citing #475",
      W.wall_invariant_errors([{"id": "g", "type": "gate", "hold_timeout": 10}, AG("a", after=["g"], timeout=999), "junk", None]) == []
      and len(e1 := W.wall_invariant_errors([{"id": "g", "type": "gate", "hold_timeout": 3600}, AG("a", after=["g"], timeout=600)])) == 1
      and e1[0]["node"] == "g" and e1[0]["field"] == "hold_timeout" and "#475" in e1[0]["msg"]
      and len(e2 := W.wall_invariant_errors([{"id": "g1", "type": "gate", "hold_timeout": 3600},
          {"id": "g2", "type": "gate", "hold_timeout": 7200}, AG("a", after=["g1", "g2"], timeout=600)])) == 2
      and SH(e2) and {r["node"] for r in e2} == {"g1", "g2"})
check("wall #475: defaults=None skips to the preset floor — a hold lifted by the defaults block is still refused when defaults is omitted",
      (g := [{"id": "g", "type": "gate", "hold_timeout": 2000}, AG("a", after=["g"])]) and len(W.wall_invariant_errors(g)) == 1
      and W.wall_invariant_errors(g, {"timeout": 3000}) == [])
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
