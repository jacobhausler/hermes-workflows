"""est-82bzb sweep-c: batch-7 direct contract pins for the remaining zero-direct-reference `wfcommon` surface at shipped tip aa2f443 — workflow_nodes, suite_proof_token_path, plus the four #642 twin-disposal residual edges (a foreign fp_rule_version still refusing on a suite_proof producer record; the efp-EFFECTIVE amend re-freezing the proof while a timeout/concurrency-only amend does not; the wait.until_argv existence-only pass; and every apply_node_patch refusal matched by message FRAGMENT, not a bare ValueError); every expectation MEASURED against that tip; pointer here because AGENTS.md is capped (test_docs_hint_cap_73c.py makes any AGENTS.md addition born-red); house shape per merged #620/#624/#635/#639/#640/#641. Stdlib, serial, auto-discovered by scripts/suite.py; zero production lines touched."""
import json, os, sys, tempfile; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "..")); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def msg(fn):
    try: fn(); return ""
    except ValueError as e: return str(e) or "?"
def mut(byid, nid, **kw):
    return {k: (dict(v, **kw) if k == nid else v) for k, v in byid.items()}
PD7 = tempfile.mkdtemp(prefix="b7-proof-"); (Path(PD7) / "nodes").mkdir()
PB7 = {"src": {"id": "src", "type": "echo", "suite_proof": True}, "p1": {"id": "p1", "suite_proof": True, "after": ["src"]},
       "mid": {"id": "mid", "after": ["p1"]}, "pub": {"id": "pub", "publishes": True, "after": ["mid"]}}
PE7 = W.efp(PB7, PB7["p1"])
def fresh(byid=PB7, extra=None):
    (Path(PD7) / "nodes" / "p1.suite-proof.json").write_text(json.dumps({"node": "p1", "efp": PE7}))
    (Path(PD7) / "nodes" / "p1.json").write_text(json.dumps({"status": "done", "efp": PE7, **(extra or {})}))
    return W.publisher_gate_check(PD7, byid["pub"], byid)
GN = {"nodes": [{"id": "a"}, {"id": "b"}, {"id": "x"}], "on_exit": "x"}
check("workflow_nodes: the ordinary DAG minus the on_exit agent, input order kept, rows the SAME node objects (no copy); a graph without the nodes key is []; on_exit naming an unknown id excludes nothing; and the None-law edge: with NO on_exit key an id-less node is excluded too (its missing id == the missing on_exit), while that same node survives once on_exit names anything",
      [n["id"] for n in W.workflow_nodes(GN)] == ["a", "b"] and W.workflow_nodes(GN)[0] is GN["nodes"][0]
      and W.workflow_nodes({}) == []
      and [n.get("id") for n in W.workflow_nodes({"nodes": [{"id": "a"}, {}]})] == ["a"]
      and [n.get("id") for n in W.workflow_nodes({"nodes": [{"id": "a"}, {}], "on_exit": "zz"})] == ["a", None])
TP = W.suite_proof_token_path("/b7-run/1", {"id": "p.1"})
check("suite_proof_token_path: pure path arithmetic <r>/nodes/<id>.suite-proof.json — the id interpolated verbatim (dotted ids included), a str or Path run dir both fine, and ZERO filesystem side effects: a missing run dir still returns the Path and creates nothing on disk",
      TP == Path("/b7-run/1/nodes/p.1.suite-proof.json") and isinstance(TP, Path) and not TP.exists()
      and W.suite_proof_token_path(Path("/b7-run/1"), {"id": "p1"}) == Path("/b7-run/1/nodes/p1.suite-proof.json")
      and not Path("/b7-run").exists())
check("a foreign fp_rule_version on the suite_proof producer record still refuses the publish gate under the REAL validator (no own() stub): token-efp == record-efp == current efp passes unstamped and stamped under a known rule, but an int outside FP_RULES (77) — and even the right digit as a STRING '2' — reads invalid (type(rule) is int is the law): (False, ['p1']) names the producer",
      fresh() == (True, []) and fresh(extra={"fp_rule_version": 2}) == (True, [])
      and fresh(extra={"fp_rule_version": 77}) == (False, ["p1"]) and fresh(extra={"fp_rule_version": "2"}) == (False, ["p1"]))
M1 = mut(PB7, "p1", goal="work moved"); M2 = mut(PB7, "p1", timeout=4242, concurrency=9); M3 = mut(PB7, "src", output="proof text moved")
check("efp-EFFECTIVE amend law at the proof boundary: re-minting the token against an AMENDED graph — a prompt change on the producer, or on any ancestor, moves the effective fingerprint and REFREEZES the proof (gate refuses, naming p1) — while a timeout/concurrency-only change is policy not work: the fingerprint holds and the frozen proof stays valid, no re-drive of the suite_proof commit",
      W.efp(M1, M1["p1"]) != PE7 and W.efp(M3, M3["p1"]) != PE7
      and W.efp(M2, M2["p1"]) == PE7
      and fresh(M1) == (False, ["p1"]) and fresh(M3) == (False, ["p1"]) and fresh(M2) == (True, []))
NX1 = Path(PD7) / "probe-644"; NX1.write_text("#!/bin/sh\nexit 0\n"); os.chmod(NX1, 0o644)
NX2 = Path(PD7) / "probe-600"; NX2.write_text("x"); os.chmod(NX2, 0o600)
GT = lambda i, a: {"id": i, "type": "gate", "wait": {"until_argv": [a]}}
ROWS = {r["node"]: r for r in W.validate_graph_warnings([GT("ga", str(NX1)), GT("gb", str(NX2)),
                                                        GT("gg", str(Path(PD7) / "ghost")), GT("gc", "b7-bare-name-missing"), GT("gd", sys.executable)])}
check("wait.until_argv probes are linted on EXISTENCE ALONE for '/'-paths: an existing non-executable file (mode 0644 or 0600 — no exec bit at all) earns NO advisory and the gate would park re-running it to timeout_s; a missing '/' path and a bare name off PATH both earn the wait.until_argv row, whose msg says 'is not executable' while the check never read an exec bit; a PATH-resolvable argv[0] (sys.executable) is clean",
      "ga" not in ROWS and "gb" not in ROWS and "gd" not in ROWS and set(ROWS) == {"gg", "gc"}
      and all(r["field"] == "wait.until_argv" for r in ROWS.values())
      and "is not executable" in ROWS["gg"]["msg"] and str(Path(PD7) / "ghost") in ROWS["gg"]["msg"]
      and "b7-bare-name-missing" in ROWS["gc"]["msg"])
OG7 = {"name": "old", "nodes": [{"id": "a", "timeout": 10}, {"id": "b"}]}; OJB = json.dumps(OG7)
R6 = lambda p, g=OG7: (lambda: W.apply_node_patch(g, p))
REF = [(R6(["nodes"]), "patch must be an object"),
       (R6({"nodes": {"a": {"timeout": 1}}, "extra": 1}), "patch keys ['extra'] not allowed (only 'nodes' and 'name')"),
       (R6({}), "patch is empty: needs nodes and/or name"),
       (R6({"nodes": {}}), "patch.nodes must be a non-empty object"),
       (R6({"nodes": "x"}), "patch.nodes must be a non-empty object"),
       (R6({"name": "m"}, {"name": "n"}), "committed graph has no nodes to patch"),
       (R6({"name": "m"}, []), "committed graph has no nodes to patch"),
       (R6({"nodes": {"a": {}}}), "patch.nodes.a must be a non-empty object of field updates"),
       (R6({"nodes": {"a": 5}}), "patch.nodes.a must be a non-empty object of field updates"),
       (R6({"nodes": {"a": {"id": "z"}}}), "patch.nodes.a cannot change the node id"),
       (R6({"nodes": {"zz": {"timeout": 1}}}), "patch names unknown node ids ['zz']"),
       (R6({"nodes": {"zz": {"timeout": 1}}}), "adding nodes needs the full graph"),
       (R6({"name": ""}), "patch.name must be a non-empty string"),
       (R6({"name": 5}), "patch.name must be a non-empty string")]
check("apply_node_patch: EVERY refusal site is matched by its message fragment, not the bare ValueError type — patch-not-object, the closed {nodes,name} key set with the offending keys named, the empty patch, the non-empty-object law on patch.nodes AND on each per-node patch (both failure shapes each), the no-nodes graph to patch (missing key and non-dict graph), the no-re-keying law naming the node, the unknown-ids refusal naming them and the full-graph cure, the non-empty-string name law (empty str and int); a legal {'name': str} still renames and the input json stays byte-identical",
      all(frag in msg(fn) for fn, frag in REF) and len(REF) == 14
      and W.apply_node_patch(OG7, {"name": "new"})["name"] == "new" and json.dumps(OG7) == OJB)
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
