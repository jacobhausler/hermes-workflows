"""est-7nn1j: batch-6 direct contract pins for the five sweep-c zero-direct-reference `wfcommon` callables at shipped tip d133e20 — run_abort_flag, wall_invariant_warnings, validate_graph_warnings, publisher_gate_check, apply_node_patch; every expectation MEASURED against that tip; pointer here (AGENTS.md hint cap full); house shape per merged #635/#639/#640. Stdlib, serial."""
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/.."); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def raises(fn, frag):
    try: fn(); return False
    except ValueError as e: return frag in str(e)
TD = tempfile.TemporaryDirectory(prefix="b6-pins-"); ROOT = Path(TD.name); RA = ROOT / "raf"; RA.mkdir(); PGD = ROOT / "pgc"; (PGD / "nodes").mkdir(parents=True)
N = lambda i, t, after=(), **kw: {"id": i, "type": t, "after": list(after), **kw}
def wiw(*ns, defaults=None):
    return W.wall_invariant_warnings({"nodes": list(ns), **({"defaults": defaults} if defaults else {})})
AD = wiw(N("g", "gate", hold_timeout=900), N("b", "agent", ["g"], timeout=300), N("c", "agent", ["g"], timeout=600), N("d", "agent", ["g"], timeout=900))
def abort(txt):
    (RA / "abort.json").write_text(txt); return W.run_abort_flag(RA)
check("run_abort_flag: a missing, garbage, non-dict, `node`-less or empty-`node` abort.json is NO flag — the verdict stands on parsed facts, never on a stub; a written flag comes back VERBATIM, the file being the durable record a runner restart still reads (first flag wins)",
      W.run_abort_flag(ROOT / "absent-dir") is None and abort("{oops") is None and abort("[]") is None and abort("{}") is None
      and abort('{"reason": "boom"}') is None and abort('{"node": ""}') is None
      and abort('{"node": "g", "source": "fanout", "reason": "no else arm", "at": "t0"}') == {"node": "g", "source": "fanout", "reason": "no else arm", "at": "t0"})
check("wall_invariant_warnings (the #475 advisory): one row per (gate, after-consumer) pair whose lane wall sits UNDER the decidable hold, name-ordered, only strictly-short walls, msg naming BOTH numbers; a gate the admission REFUSES (hold over the graph max wall) is SILENT here — one voice per defect; the walk is after-cycle-safe; wall-less consumers never row; a defaults-fed wall is the same wall; a non-graph is []",
      [(r["node"], r["field"]) for r in AD] == [("g", "hold_timeout"), ("g", "hold_timeout")] and "'b'" in AD[0]["msg"] and "300s" in AD[0]["msg"] and "900s" in AD[0]["msg"] and "'c'" in AD[1]["msg"]
      and wiw(N("g", "gate", hold_timeout=1200), N("c", "agent", ["g"], timeout=600)) == [] == W.wall_invariant_warnings("junk") == W.wall_invariant_warnings({"nodes": "x"})
      and len(wiw(N("g", "gate", ["c"], hold_timeout=500), N("c", "agent", ["g"], timeout=300), N("d", "agent", ["g"], timeout=700))) == 1
      and wiw(N("g", "gate", hold_timeout=900), N("c", "echo", ["g"])) == [] and len(wiw(N("g", "gate", hold_timeout=400), N("b", "agent", ["g"]), N("d", "agent", ["g"], timeout=500), defaults={"timeout": 300})) == 1)
PRD = N("p", "agent", suite_proof=True, prompt="orig"); MID = N("i", "agent", ["p"]); PUB = N("z", "agent", ["i"], publishes=True)
ECHO = N("e", "echo", suite_proof=True); PUB_E = N("z2", "agent", ["e"], publishes=True)
BY = {n["id"]: n for n in (PRD, MID, PUB, ECHO, PUB_E)}; EF = W.efp(BY, PRD, rule=max(W.FP_RULES))
DONE = {"id": "p", "status": "done", "efp": EF}; TOK = {"node": "p", "efp": EF}
def pgc(rec, tok, byid=None):
    (PGD / "nodes" / "p.json").write_text(json.dumps(rec)); (PGD / "nodes" / "p.suite-proof.json").write_text(json.dumps(tok))
    return W.publisher_gate_check(PGD, PUB, byid or BY)
check("publisher_gate_check (fail-closed publish law): a gate or an undeclared publisher is UNTOUCHED (True, []); a declared publisher refuses without a verified token — (False, []), and a suite-proof ECHO is no producer; an after-transitive proof producer is DISCOVERED and named while its token is absent, garbage, node-less, efp-less, mismatched, foreign-rule, or its record not `done`; a CURRENT token passes; an efp-EFFECTIVE amend re-refuses while timeout/concurrency policy never un-freezes the proof",
      W.publisher_gate_check(PGD, PUB, BY) == (False, ["p"]) and W.publisher_gate_check(PGD, {"id": "g", "type": "gate"}, BY) == (True, []) == W.publisher_gate_check(PGD, {**PUB, "publishes": None}, BY)
      and W.publisher_gate_check(PGD, PUB_E, BY) == (False, []) and pgc(DONE, TOK) == (True, []) and pgc({**DONE, "status": "failed"}, TOK) == (False, ["p"])
      and all(pgc(DONE, t) == (False, ["p"]) for t in ({**TOK, "efp": "0" * 16}, {"node": "q", "efp": EF}, {"node": "p"}, "[junk"))
      and pgc({**DONE, "fp_rule_version": 9}, TOK) == (False, ["p"]) and pgc(DONE, TOK, {**BY, "p": {**PRD, "prompt": "re-asked"}}) == (False, ["p"])
      and all(pgc(DONE, TOK, {**BY, "p": {**PRD, k: v}}) == (True, []) for k, v in (("timeout", 777), ("concurrency", 3))))
CH = N("b6c", "agent", schema={"type": "object", "properties": {"verdict": {"type": "string"}}}); UN = N("a6", "gate", ["b6c"], when="out.b6c.score >= 3")
PF = ROOT / "plain-file"; PF.write_text("not a program")
check("validate_graph_warnings (hw-udg advisory, NEVER fatal): an `out.<head>.<field>` ref whose head DECLARES an object schema missing that property rows (field `when`, the missing property named) — deep segments too; the proof is UNDECLARED, not UNEMITTABLE: a schema-less head, a segment below a declared scalar, a fan-out head (its out is the results LIST) and a malformed when (the error owns it) all stay silent; a wait probe rows on a missing argv0 while an existing non-executable absolute path passes on existence alone; quorum rows only strictly between 0 and the literal item count (a bool is no int); a graph object is accepted",
      (lambda r: len(r) == 1 and r[0]["node"] == "a6" and r[0]["field"] == "when" and "'score'" in r[0]["msg"])(W.validate_graph_warnings([CH, UN]))
      and W.validate_graph_warnings([CH, N("a7", "gate", ["b6c"], when="out.b6c.verdict == 'go'")]) == [] == W.validate_graph_warnings([CH, N("a8", "agent", ["b6c"], when="out.b6c.verdict.x == 'go'")])
      and W.validate_graph_warnings([N("b2", "agent", schema={"type": "object", "properties": {"o": {"type": "object", "properties": {"inner": {}}}}}), N("a9", "agent", ["b2"], when="out.b2.o.deeper == 1")]) != []
      and W.validate_graph_warnings([N("f6", "agent", fanout={"items": ["x"], "quorum": 1}), UN]) == [] == W.validate_graph_warnings([N("b3", "agent"), N("a5", "agent", ["b3"], when="out.b3.anything == 1")]) == W.validate_graph_warnings([CH, N("ax", "gate", ["b6c"], when="out.b6c.score ==")])
      and [r["node"] for r in W.validate_graph_warnings([N("f1", "agent", fanout={"items": ["a", "b", "c"], "quorum": 2}), N("f2", "agent", fanout={"items": ["a", "b", "c"], "quorum": 3}), N("f3", "agent", fanout={"items": ["a", "b", "c"], "quorum": 0}), N("f4", "agent", fanout={"items": ["a", "b", "c"], "quorum": True})])] == ["f1"]
      and len(W.validate_graph_warnings({"nodes": [CH, UN]})) == 1 == len(W.validate_graph_warnings([N("g8", "gate", wait={"until_argv": [str(ROOT / 'no-such-probe')]})])) != len(W.validate_graph_warnings([N("g9", "gate", wait={"until_argv": [str(PF)]}), N("h0", "gate", wait={"until_argv": ["sh"]})]))
      and W.validate_graph_warnings(None) == [] == W.validate_graph_warnings("x") == W.validate_graph_warnings({"nodes": "x"}))
OG = {"name": "old", "nodes": [{"id": "x", "timeout": 10, "extra": 1}, {"id": "y"}]}; BEF = json.dumps(OG)
OUT = W.apply_node_patch(OG, {"nodes": {"x": {"timeout": 20, "extra": None}}, "name": "new"})
check("apply_node_patch (amend's per-node edit — pure + fail-closed): every refusal NAMES itself — a non-object patch, a structural key beyond nodes/name, an empty patch, empty patch.nodes, a node-less committed graph, an id change, an unknown node id (patch EDITS, it does not author), a non-object field-update, a blank name; the merge is SHALLOW, a null value DELETES, `name` replaces the graph name, original order holds, id-less entries pass through, and the answer is a NEW graph of deep-copied nodes — the committed graph stays byte-untouched",
      raises(lambda: W.apply_node_patch(OG, "junk"), "must be an object") and raises(lambda: W.apply_node_patch(OG, {"nodez": {"x": {"timeout": 1}}}), "not allowed")
      and raises(lambda: W.apply_node_patch(OG, {}), "patch is empty") and raises(lambda: W.apply_node_patch(OG, {"nodes": {}}), "non-empty object")
      and raises(lambda: W.apply_node_patch({"name": "n"}, {"nodes": {"x": {"timeout": 1}}}), "no nodes to patch") and raises(lambda: W.apply_node_patch(OG, {"nodes": {"zz": {"timeout": 1}}}), "unknown node ids")
      and raises(lambda: W.apply_node_patch(OG, {"nodes": {"x": {"id": "q"}}}), "cannot change the node id") and raises(lambda: W.apply_node_patch(OG, {"nodes": {"x": 5}}), "non-empty object")
      and raises(lambda: W.apply_node_patch(OG, {"name": ""}), "non-empty string")
      and OUT == {"name": "new", "nodes": [{"id": "x", "timeout": 20}, {"id": "y"}]} and json.dumps(OG) == BEF and OUT["nodes"][0] is not OG["nodes"][0] and OUT["nodes"][1] is not OG["nodes"][1]
      and W.apply_node_patch(OG, {"name": "renamed"})["nodes"] == OG["nodes"] and W.apply_node_patch({"nodes": [{"timeout": 1}]}, {"name": "n"})["nodes"] == [{"timeout": 1}])
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
