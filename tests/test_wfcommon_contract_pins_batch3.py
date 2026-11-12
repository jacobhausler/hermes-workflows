"""est-ckxqk: batch-3 direct contract pins for the five wfcommon validators with ZERO
test references at shipped tip c7f24df (wf-nightly-dev-pass 2026-11-12 sweep-c; same
class as merged #620/#624): requires_errors, requires_plugin_errors, result_errors,
run_context_contract_errors, wall_invariant_errors. Error rows pinned at the exact
{node, field, msg} shape; absent key = no check ([]); malformed value = named error,
never a crash. Every expectation measured against the tip. Pointer lives here
(AGENTS.md hint-cap has no headroom). Stdlib, serial."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/.."); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def row(nid, field, msg): return {"node": nid, "field": field, "msg": msg}
REQ_MSG = 'requires must be a non-empty object {"<ancestor>": ["field", "dotted.path", ...]}'
check("requires: absent-key, [], None and dict-less values name ONE row; closure passes (transitive, parents arg)",
      W.requires_errors([]) == [] == W.requires_errors(None) == W.requires_errors([{"id": "a"}]) == W.requires_errors("zz")
      and all(W.requires_errors([{"id": "n", "requires": v}]) == [row("n", "requires", REQ_MSG)] for v in ("b", {}, 5, []))
      and W.requires_errors([{"id": "a"}, {"id": "b", "after": ["a"]}, {"id": "n", "after": ["b"], "requires": {"a": ["f"]}}]) == []
      and W.requires_errors([{"id": "n", "requires": {"a": ["f"]}}], {"a": [], "n": ["a"]}) == [])
check("requires: non-ancestor key, empty/str path-list, and blank entry each named at exact field",
      W.requires_errors([{"id": "b"}, {"id": "n", "after": ["b"], "requires": {"z": ["f"]}}])
      == [row("n", "requires", "requires key 'z' is not an ancestor in this node's `after` closure (requires is an input edge: only committed upstream outputs may be required)")]
      and (e := W.requires_errors([{"id": "b"}, {"id": "n", "after": ["b"], "requires": {"b": []}}]))
      == [row("n", "requires.b", 'requires[\'b\'] must be a non-empty list of field path strings ("field" or "dotted.path")')] == e
      and len(bad := W.requires_errors([{"id": "b"}, {"id": "n", "after": ["b"], "requires": {"b": ["ok", " "]}}])) == 1
      and bad[0] == row("n", "requires.b", "requires['b'][1] ' ' must be a non-empty field path string"))
check("requires_plugin: absent/non-dict [] ; dot-integer OK; every malformed value one refusal naming the value",
      W.requires_plugin_errors({}) == [] == W.requires_plugin_errors(5)
      and W.requires_plugin_errors({"requires_plugin": "1.2"}) == [] == W.requires_plugin_errors({"requires_plugin": "1.2.0"})
      and all(W.requires_plugin_errors({"requires_plugin": v}) == [row(None, "requires_plugin",
          f"requires_plugin {v!r} invalid: must be a dot-integer version string like '1.2.0' (coarse >= comparison)")]
          for v in ("latest", "", 5, None, ["1.2"])))
check("result: absent/non-dict [] ; live node OK ; unknown id, non-str id, gate target, nodes-str all one row",
      W.result_errors({}) == [] == W.result_errors(5)
      and W.result_errors({"result": "a", "nodes": [{"id": "a", "type": "agent", "goal": "g"}]}) == []
      and W.result_errors({"result": "a", "nodes": [{"id": "a"}]}) == []
      and W.result_errors({"result": "a", "nodes": "zz"}) == [row(None, "result", "result 'a' must name an existing node id")]
      and W.result_errors({"result": "a"}) == [row(None, "result", "result 'a' must name an existing node id")]
      and W.result_errors({"result": 5, "nodes": []}) == [row(None, "result", "result 5 must name an existing node id")]
      and W.result_errors({"result": "g", "nodes": [{"id": "g", "type": "gate", "question": "q?"}]})
          == [row(None, "result", "result 'g' is a gate; name the agent, echo or join node whose output is the verdict")])
RC = W.run_context_contract_errors
check("run_context: absent/non-dict [] ; empty block and non-dict one named row ; unknown keys sorted rows",
      RC({}) == [] == RC(5)
      and RC({"run_context": {}}) == RC({"run_context": 5}) == [row(None, "run_context", "run_context contract must be a non-empty object (required and/or defaults)")]
      and RC({"run_context": {"zz": 1, "yy": 2}}) == [row(None, "run_context.yy", 'unknown key; allowed: ["defaults", "required"]'),
                                                       row(None, "run_context.zz", 'unknown key; allowed: ["defaults", "required"]')])
check("run_context.required: bad list grammar, duplicates, unrefused, referenced-pass, defaults shape refusals",
      all(len(e := RC({"run_context": {"required": r}})) == 1 and e[0]["field"] == "run_context.required"
          and e[0]["msg"] == "required must be a non-empty list of identifier strings" for r in ([], "q", ["a-a"], ["9x"], [7]))
      and RC({"run_context": {"required": ["q", "q"]}})[0]["msg"] == "required keys must be unique"
      and RC({"run_context": {"required": ["q"]}, "nodes": [{"id": "n", "goal": "do {run.q} now"}]}) == []
      and RC({"run_context": {"required": ["q"]}, "nodes": [{"id": "n", "goal": "plain"}]})
          == [row(None, "run_context.required", "declared required key(s) ['q'] never referenced as {run.KEY} in operative text (goal/context/question/profile/fan-out) — bind what you declare")]
      and RC({"run_context": {"defaults": {}}}) == [row(None, "run_context.defaults", "defaults must be a non-empty object of identifier -> non-empty string")]
      and RC({"run_context": {"defaults": {"a-b": "x"}}}) == [row(None, "run_context.defaults", "invalid key 'a-b': expected identifier")]
      and RC({"run_context": {"defaults": {"a": "  "}}}) == [row(None, "run_context.defaults", "defaults['a'] must be a non-empty string")])
WE, GATE, CONS = W.wall_invariant_errors, lambda **kw: dict(id="g", type="gate", question="q?", **kw), lambda **kw: dict(id="c", after=["g"], type="agent", goal="g", **kw)
WALL_MSG = lambda h, w: f"hold_timeout {h} exceeds the enclosing graph's max lane wall {w}s — every consumer lane of this gate dies at its wall before the hold can release (#475); raise the consumer timeout(s) to >= {h} or lower hold_timeout"
check("wall: []/None/str silent; no-hold, bool/zero hold, hold<=max, non-spawning consumer all pass",
      WE([]) == [] == WE(None) == WE("zz") == WE([GATE(), CONS(timeout=3600)])
      and WE([GATE(hold_timeout=0), CONS(timeout=3600)]) == [] == WE([GATE(hold_timeout=True), CONS(timeout=3600)])
      and WE([GATE(hold_timeout=1200), CONS(timeout=3600)]) == []
      and WE([GATE(hold_timeout=99999), dict(id="e", after=["g"], type="echo", output="x")]) == [])
check("wall: hold>max is ONE exact row; wall precedence timeout>shape>defaults>build floor; bool timeout floor",
      WE([GATE(hold_timeout=99999), CONS(timeout=3600)]) == [row("g", "hold_timeout", WALL_MSG(99999, 3600))]
      and WE([GATE(hold_timeout=99999), CONS()], {"timeout": 1800}) == [row("g", "hold_timeout", WALL_MSG(99999, 1800))]
      and WE([GATE(hold_timeout=99999), CONS()]) == [row("g", "hold_timeout", WALL_MSG(99999, 1500))]
      and WE([GATE(hold_timeout=99999), CONS(shape="recon")], {"timeout": 100}) == [row("g", "hold_timeout", WALL_MSG(99999, 2400))]
      and WE([GATE(hold_timeout=99999), CONS(timeout=30, shape="recon")]) == [row("g", "hold_timeout", WALL_MSG(99999, 30))]
      and WE([GATE(hold_timeout=99999), CONS(timeout=True)]) == [row("g", "hold_timeout", WALL_MSG(99999, 1500))])
check("row shape: every refusing call across ALL FIVE validators returns only {node, field, msg} dicts",
      all(isinstance(r, dict) and set(r) == {"node", "field", "msg"}
          for rows in (W.requires_errors([{"id": "n", "requires": "b"}]),
                       W.requires_plugin_errors({"requires_plugin": "latest"}),
                       W.result_errors({"result": "zz", "nodes": []}),
                       RC({"run_context": {"required": []}}),
                       WE([GATE(hold_timeout=99999), CONS(timeout=60)]))
          for r in rows))
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
