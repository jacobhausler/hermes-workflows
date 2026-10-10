#!/usr/bin/env python3
"""A current done aggregate supersedes leftover running fan-out spawn facts.

Read-only fixtures mirror pre-finalization runs: an efp-valid done aggregate,
two done all_results rows, and dead-pid item files still marked running. The
aggregate alone remains recovery truth; this projection never writes items.
"""
import copy
import importlib.util
import json
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon as common


def write(path, obj):
    path.write_text(json.dumps(obj))


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix="home-agg-read-", dir=ROOT) as tmp:
        run = Path(tmp) / "fixture"
        (run / "nodes").mkdir(parents=True)
        graph = {"name": "aggregate-read", "nodes": [
            {"id": "fan", "type": "agent", "fanout": {
                "items": ["first", "second"], "goal": "read {item}"}}]}
        node = graph["nodes"][0]
        byid = {node["id"]: node}
        stamp = {"efp": common.efp(byid, node), "fp_rule_version": common.FP_RULE_VERSION}
        rows = [{"status": "done", "output": {"item": i}, "ms": i + 1} for i in range(2)]
        aggregate = {**stamp, "status": "done", "output": {"items": [x["output"] for x in rows], "all_results": rows}}
        write(run / "graph.json", graph)
        write(run / "run.json", {"name": graph["name"]})
        write(run / "nodes" / "fan.json", aggregate)
        for i in range(2):
            write(run / "nodes" / f"fan.{i}.json", {**stamp, "status": "running", "pid": 0,
                  "skey": f"wf:fixture:fan:{i}", "attempt": 0, "log_path": f"item-{i}.log"})
        yield run, graph, aggregate


def test_fanout_aggregate_supersedes_running_item_facts_read_only():
    with fixture() as (run, graph, aggregate):
        before = {p: p.read_bytes() for p in run.rglob("*") if p.is_file()}
        for i, row in enumerate(aggregate["output"]["all_results"]):
            facts = common.node_facts(run, "fan", i)
            assert facts["status"] == row["status"], facts
            assert facts["output"] == row["output"], facts
            assert facts["ms"] == row["ms"]
            assert facts["superseded_by_aggregate"] == "fan.json"
            assert facts["log_path"] == f"item-{i}.log"  # spawn provenance retained
            assert common.node_facts(run, f"fan.{i}") == facts
        assert before == {p: p.read_bytes() for p in run.rglob("*") if p.is_file()}


def test_fanout_status_wait_and_item_facts_agree_without_respawn():
    spec = importlib.util.spec_from_file_location("aggregate_read_door", ROOT / "__init__.py")
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    with fixture() as (run, graph, aggregate):
        state = common.run_state(run)
        with patch.object(door, "_resolve_read_run", return_value=(run, state, None)), \
             patch.object(door, "_respawn_runner", side_effect=AssertionError("terminal fixture must not spawn")), \
             patch.object(door._common, "run_child_metrics", return_value={}):
            for verb in (door.act_status, door.act_wait):
                out = verb({"run_id": "fixture", "timeout": 0})
                assert out["status"] == out["nodes"]["fan"]["status"] == "done"
                for i, row in enumerate(out["nodes"]["fan"]["output"]["all_results"]):
                    assert common.node_facts(run, "fan", i)["status"] == row["status"]
                assert not out["nodes"]["fan"].get("active_spawns")


def test_fanout_stale_or_uncommitted_aggregate_does_not_supersede():
    with fixture() as (run, graph, aggregate):
        for status in ("running", "partial", "failed"):
            write(run / "nodes" / "fan.json", {**aggregate, "status": status})
            facts = common.node_facts(run, "fan", 0)
            assert facts["status"] == "running"
            assert "superseded_by_aggregate" not in facts
        write(run / "nodes" / "fan.json", {**aggregate, "efp": "stale"})
        assert common.node_facts(run, "fan", 0)["status"] == "running"
        write(run / "nodes" / "fan.json", aggregate)
        amended = copy.deepcopy(graph)
        amended["nodes"][0]["fanout"]["goal"] = "different {item}"
        write(run / "graph.json", amended)
        assert common.node_facts(run, "fan", 0)["status"] == "running"
        assert common.run_state(run)["nodes"]["fan"]["status"] == "pending"


def test_fanout_item_verdict_is_not_inferred_from_aggregate_success():
    with fixture() as (run, graph, aggregate):
        rows = [{"status": "partial", "output": {"answer": "banked"}, "error_class": "timeout"},
                {"status": "failed", "error_class": "cancelled", "error": "quorum straggler"}]
        aggregate["output"]["all_results"] = rows
        write(run / "nodes" / "fan.json", aggregate)
        for i, row in enumerate(rows):
            facts = common.node_facts(run, "fan", i)
            assert facts["status"] == row["status"]
            assert facts["error_class"] == row["error_class"]
            assert facts["output"] == row.get("output", "unknown")


def test_fanout_missing_row_is_superseded_not_fabricated_done():
    with fixture() as (run, graph, aggregate):
        for rows in ([], [None], [{"status": "running"}], "malformed"):
            aggregate["output"]["all_results"] = rows
            write(run / "nodes" / "fan.json", aggregate)
            facts = common.node_facts(run, "fan", 0)
            assert facts["status"] == "superseded", facts
            assert facts["superseded_by_aggregate"] == "fan.json"
            assert facts["output"] == "unknown"
        (run / "nodes" / "fan.0.json").unlink()
        assert common.node_facts(run, "fan", 0) is None  # no invented item record


def test_fanout_finalized_and_solo_records_keep_their_own_facts():
    with fixture() as (run, graph, aggregate):
        item = {"status": "failed", "error_class": "crashed", "output": {"own": True}}
        write(run / "nodes" / "fan.0.json", item)
        facts = common.node_facts(run, "fan", 0)
        assert facts["status"] == "failed" and facts["output"] == item["output"]
        assert "superseded_by_aggregate" not in facts
        assert common.node_facts(run, "fan")["output"] == aggregate["output"]
        graph["nodes"][0].pop("fanout")
        write(run / "graph.json", graph)
        assert common.node_facts(run, "fan", 1)["status"] == "running"


def test_fanout_aggregate_only_recovery_no_partial_rescue():
    with fixture() as (run, graph, aggregate):
        byid = {n["id"]: n for n in graph["nodes"]}
        node = byid["fan"]
        assert common.node_rec(run, node, byid)[0] == "done"
        (run / "nodes" / "fan.json").unlink()
        assert common.node_rec(run, node, byid)[0] == "pending"
        assert common.node_facts(run, "fan", 0)["status"] == "running"
        assert common.run_state(run)["status"] != "done"


if __name__ == "__main__":
    tests = sorted((name, fn) for name, fn in globals().items() if name.startswith("test_") and callable(fn))
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS", name)
        except Exception as exc:
            failures += 1
            print("FAIL", name, type(exc).__name__, str(exc))
    print(f"TOTAL {len(tests)} FAIL {failures}")
    sys.exit(bool(failures))
