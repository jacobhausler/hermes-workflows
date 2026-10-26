import sys, subprocess, tempfile, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import wfcommon

# hw-on5 truth law: `completed` is the single field that separates the two senses
# of 'done' - 'finished green' vs 'exited with casualties'. It is DERIVED at read
# time (a fold over states/recs), never a second stored fact; a runner_exit.json
# byte-compare therefore still sees the frozen key set.

def test_completed_is_read_derived_not_a_second_store():
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        run = root / "run"; (run / "nodes").mkdir(parents=True)
        graph = {"id": "g", "title": "t", "defaults": {"seat": "s"}, "nodes": [
            {"id": "a", "task": "t", "seat": "s", "type": "echo", "output": {"ok": True}},
            {"id": "b", "task": "t", "seat": "s", "depends_on": ["a"],
             "type": "echo", "output": {"ok": True}}]}
        (run / "graph.json").write_text(json.dumps(graph))
        (run / "run.json").write_text(json.dumps({"id": "g", "status": "done", "graph": graph}))
        (run / "runner_exit.json").write_text(json.dumps(
            {"reason": "done", "at": "x", "graph_fingerprint":
             wfcommon.graph_fingerprint(graph), "fp_rule_version":
             wfcommon.FP_RULE_VERSION}))
        byid = {n["id"]: n for n in graph["nodes"]}
        for nid in ("a", "b"):
            (run / "nodes" / f"{nid}.json").write_text(json.dumps(
                {"status": "done", "attempt": 1, "output": {"ok": True},
                 "efp": wfcommon.efp(byid, byid[nid]),
                 "fp_rule_version": wfcommon.FP_RULE_VERSION}))
        out = wfcommon.run_state(run)
        assert out["completed"] is True and out["failed_nodes"] == []
        # a failed node record flips the SAME read: done-verdict keeps the run
        # terminal, completed flips to False - the two senses are now separable
        # in one field.
        (run / "nodes" / "b.json").write_text(json.dumps(
            {"status": "failed", "attempt": 1, "error": "boom",
             "efp": wfcommon.efp(byid, byid["b"]),
             "fp_rule_version": wfcommon.FP_RULE_VERSION}))
        out = wfcommon.run_state(run)
        assert out["completed"] is False and [f["id"] for f in out["failed_nodes"]] == ["b"]
        # on-disk verdict bytes untouched: the frozen key set survives
        rec = json.loads((run / "runner_exit.json").read_text())
        assert "completed" not in rec and "failed_nodes" not in rec
        # honest absence: no verdict stamped yet -> no completed key at all
        # (the est-3acn D7 verbatim-key-set law for non-terminal runs)
        (run / "runner_exit.json").unlink()
        out = wfcommon.run_state(run)
        assert "completed" not in out
        # a crash verdict can never read completed
        (run / "runner_exit.json").write_text(json.dumps(
            {"reason": "crashed:137", "at": "x", "graph_fingerprint":
             wfcommon.graph_fingerprint(graph), "fp_rule_version":
             wfcommon.FP_RULE_VERSION}))
        out = wfcommon.run_state(run)
        assert out["completed"] is False

if __name__ == "__main__":
    test_completed_is_read_derived_not_a_second_store()
    print("on5: completed read-derivation green (5 checks)")
