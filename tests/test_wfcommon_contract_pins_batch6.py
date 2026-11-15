"""est-7nn1j sweep-c: batch-6 direct contract pins for the five zero-direct-reference `wfcommon` callables at shipped tip d133e20 — run_abort_flag, wall_invariant_warnings, validate_graph_warnings, publisher_gate_check, apply_node_patch; every expectation MEASURED against that tip; pointer here because AGENTS.md is capped (31,951/32,000 bytes at tip — test_docs_hint_cap_73c.py makes any AGENTS.md addition born-red); house shape per merged #620/#624/#635/#639/#640. Stdlib, serial, auto-discovered by scripts/suite.py; zero production lines touched."""
import json, sys, tempfile; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "..")); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def raises(fn):
    try: fn(); return ""
    except ValueError as e: return str(e) or "?"
P1 = Path(tempfile.mkdtemp(prefix="b6-abort-")) / "abort.json"; FLAG = {"node": "g", "source": "s", "reason": "r", "at": "t"}
def ab(payload):
    P1.unlink(missing_ok=True); P1.write_bytes(payload) if isinstance(payload, bytes) else payload is None or P1.write_text(json.dumps(payload))
    return W.run_abort_flag(str(P1.parent))
WG = {"nodes": [{"id": "g", "type": "gate", "hold_timeout": 600}, {"id": "a", "after": ["g"], "timeout": 200}, {"id": "c", "after": ["g"], "timeout": 300}, {"id": "e", "type": "echo", "after": ["g"]}, {"id": "gn", "type": "gate", "after": ["g"]}, {"id": "big", "timeout": 2000}]}; GATE = lambda i, **kw: dict(id=i, type="gate", **kw)
VN = [{"id": "h", "schema": {"type": "object", "properties": {"ok": {}}}}, {"id": "h2", "fanout": {"items": [1], "quorum": 1}}, {"id": "h3"},
      GATE("w1", when="out.h.nope == 1"), GATE("w2", when="out.h2.nope == 1"), GATE("w3", when="out.h3.nope == 1"), GATE("w4", when="1 == 1"),
      GATE("p1", wait={"until_argv": ["/nonexistent-b6/probe"]}), GATE("p2", wait={"until_argv": ["b6-missing-probe-x"]}), GATE("pk", wait={"until_argv": [sys.executable]}),
      {"id": "f1", "fanout": {"items": [1, 2, 3], "quorum": 2}}, {"id": "f2", "fanout": {"items": [1, 2, 3], "quorum": 3}}, {"id": "f3", "fanout": {"items": [1, 2, 3], "quorum": 0}}, {"id": "f4", "fanout": {"items": [1, 2, 3], "quorum": 4}}, {"id": "f5", "fanout": {"items": [1, 2, 3], "quorum": True}}]
VR = W.validate_graph_warnings(VN); VRB = json.dumps(VN); WR = W.wall_invariant_warnings(WG)
PD = tempfile.mkdtemp(prefix="b6-pub-"); (Path(PD) / "nodes").mkdir(); PB = {"src": {"id": "src", "type": "echo", "suite_proof": True}, "p1": {"id": "p1", "suite_proof": True, "after": ["src"]}, "mid": {"id": "mid", "after": ["p1"]}, "pub": {"id": "pub", "publishes": True, "after": ["mid"]}}
PG = lambda n: W.publisher_gate_check(PD, n, PB); TOK = lambda efp: (Path(PD) / "nodes" / "p1.suite-proof.json").write_text(json.dumps({"node": "p1", "efp": efp})); REC = lambda st, efp: (Path(PD) / "nodes" / "p1.json").write_text(json.dumps({"status": st, "efp": efp}))
def ownp(fn):
    sv = W.record_efp_valid; W.record_efp_valid = lambda *a: True
    try: return fn()
    finally: W.record_efp_valid = sv
OG = {"name": "old", "nodes": [{"id": "a", "timeout": 10}, {"id": "b", "after": ["a"], "drop": 1, "payload": {"k": [1]}}]}; OB = json.dumps(OG); PV = {"k": [2]}; NP = W.apply_node_patch(OG, {"nodes": {"b": {"timeout": 30, "drop": None, "payload": PV}}})
check("run_abort_flag: missing file, garbage bytes, a JSON array and a dict whose 'node' is falsy or absent are all no flag (None); the complete {node,source,reason,at} comes back VERBATIM",
      ab(None) is None and ab(b"{oops") is None and ab([1, 2]) is None and ab({"source": "s"}) is None and ab({"node": "", "reason": "r"}) is None and ab(FLAG) == FLAG and json.loads(P1.read_text()) == FLAG)
check("wall_invariant_warnings: non-dict graph and nodes-not-list -> []; one hold_timeout advisory per after-consumer whose wall sits under the gate's 600s hold, rows sorted by consumer id, each naming gate, consumer and BOTH numbers — but only while some node's wall reaches the hold (under it the admission error owns the surface: no rows); after-consumers that never get a wall (echo, gate) never produce a row",
      W.wall_invariant_warnings([]) == [] and W.wall_invariant_warnings({"nodes": "x"}) == [] and [(r["node"], r["field"]) for r in WR] == [("g", "hold_timeout")] * 2
      and all("can hold 600s" in r["msg"] for r in WR) and "after-consumer 'a' lane wall 200s" in WR[0]["msg"] and "after-consumer 'c' lane wall 300s" in WR[1]["msg"]
      and W.wall_invariant_warnings({"nodes": [n for n in WG["nodes"] if n["id"] != "big"]}) == [])
check("validate_graph_warnings: node list or graph dict, equal results; non-list -> []; a `when` ref out.<head>.<field> earns a when advisory naming head and segment ONLY when the head declares a schema whose properties miss the first segment (fan-out head, no-schema head, non-out./short tokens all skip); a gate wait probe earns a wait.until_argv advisory when argv[0] is a missing '/' path or a bare name off PATH (sys.executable clean); a fanout earns a fanout.quorum advisory ONLY when 0 < quorum < len(items) (==len, 0, >len and bool quorums stay clean); read-only: input bytes unchanged",
      [(r["node"], r["field"]) for r in VR] == [("w1", "when"), ("p1", "wait.until_argv"), ("p2", "wait.until_argv"), ("f1", "fanout.quorum")]
      and W.validate_graph_warnings({"nodes": VN}) == VR and "'h'" in VR[0]["msg"] and "'nope'" in VR[0]["msg"] and json.dumps(VN) == VRB and W.validate_graph_warnings("x") == [])
check("publisher_gate_check: a `gate` or publishes-not-True is untouched (True, []); a declared publisher whose only upstream suite_proof is an ECHO has no producers -> (False, []); the transitive after-walk finds p1 two hops up and keeps it MISSING while the run-dir token is absent, the token efp is null, the record is not `done`, or token-efp != record-efp — and once a valid commit (record_efp_valid under try/finally, batch5 own() pattern) is all that stands -> (True, [])",
      PG({"id": "gt", "type": "gate", "publishes": True}) == (True, []) and PG({"id": "t1", "publishes": 1, "after": ["mid"]}) == (True, [])
      and PG({"id": "pub", "publishes": True, "after": ["src"]}) == (False, []) and PG(PB["pub"]) == (False, ["p1"])
      and (TOK(None), PG(PB["pub"]))[1] == (False, ["p1"]) and (TOK("E"), REC("failed", "E"), PG(PB["pub"]))[2] == (False, ["p1"])
      and (REC("done", "F"), PG(PB["pub"]))[1] == (False, ["p1"]) and (REC("done", "E"), ownp(lambda: PG(PB["pub"])))[1] == (True, []) and W.record_efp_valid.__name__ != "<lambda>")
check("apply_node_patch: a NEW graph, original node order, unpatched nodes intact, SHALLOW field merge, patch values deep-copied (no aliasing into the result), null DELETES the field, input json byte-identical after; {'name': str} alone renames and the name must be a non-empty str; patching 'id', an unknown node id (named in the refusal), any structural key besides nodes/name, an empty patch, a non-dict graph and nodes-not-list each raise ValueError",
      json.dumps(OG) == OB and [n["id"] for n in NP["nodes"]] == ["a", "b"] and NP["nodes"][0] == OG["nodes"][0] and NP["nodes"][1] is not OG["nodes"][1] and NP["nodes"][1]["after"] == ["a"] and NP["nodes"][1]["timeout"] == 30 and "drop" not in NP["nodes"][1] and NP["nodes"][1]["payload"] == PV and NP["nodes"][1]["payload"] is not PV
      and W.apply_node_patch(OG, {"name": "new"})["name"] == "new"
      and all(raises(f) for f in (lambda: W.apply_node_patch(OG, {"nodes": {"b": {"id": "z"}}}), lambda: W.apply_node_patch(OG, {"nodes": {"zz": {"timeout": 1}}}), lambda: W.apply_node_patch(OG, {"nodes": {"b": {"timeout": 1}}, "extra": 1}), lambda: W.apply_node_patch(OG, {}), lambda: W.apply_node_patch(OG, {"name": ""}), lambda: W.apply_node_patch(OG, {"name": 5}), lambda: W.apply_node_patch([], {"name": "x"}), lambda: W.apply_node_patch({"nodes": "x"}, {"name": "x"})))
      and "zz" in raises(lambda: W.apply_node_patch(OG, {"nodes": {"zz": {"timeout": 1}}})))
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
