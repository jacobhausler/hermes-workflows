"""P02 read-model clocks: no scheduler, no invented total authorization."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
HOME = tempfile.TemporaryDirectory(prefix="p02-home-", dir=ROOT)
os.environ["HERMES_HOME"] = HOME.name
os.environ["WF_RUNS_ROOT"] = str(Path(HOME.name) / "workflows")
import wfcommon as c
spec = importlib.util.spec_from_file_location("p02_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)


def ts(seconds):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


class Clocks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HOME.name)
        self.r = Path(self.tmp.name)
        (self.r / "nodes").mkdir()
        (self.r / "gates").mkdir()
        self.n = {"id": "probe", "type": "agent", "goal": "inspect", "timeout": 900}
        (self.r / "graph.json").write_text(json.dumps({"nodes": [self.n]}))
        (self.r / "run.json").write_text("{}")

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self, filename, rows):
        (self.r / filename).write_text("".join(json.dumps(row) + "\n" for row in rows))

    def test_cancelled_queue_does_not_remain_active(self):
        self.rows("events.jsonl", [
            {"ts": ts(100), "event": "seat.wait", "node": "probe", "index": None, "cap": 1},
            {"ts": ts(120), "event": "run.stopped"}])
        with patch.object(c, "runner_alive", return_value=False), patch("time.time", return_value=150):
            clock = c.run_state(self.r)["nodes"]["probe"]["clocks"]
        self.assertEqual(clock["phase"], "stopped")
        self.assertEqual(clock["queue"], [])
        self.assertEqual(clock["work"]["observed_s"], 0)

    def test_malformed_and_duplicate_ledger_never_invent_work(self):
        start = {"ts": ts(100), "role": "child", "node": "probe", "pid": 11, "skey": "one"}
        self.rows("spawn-ledger.jsonl", [start, start,
            {"ts": ts(150), "role": "child_end", "node": "probe", "pid": 11, "skey": "one"},
            {"ts": ts(200), "role": "child", "node": "probe", "pid": [], "skey": {}}])
        with patch.object(c, "runner_alive", return_value=False):
            clock = c.run_state(self.r)["nodes"]["probe"]["clocks"]
        self.assertEqual(clock["work"]["observed_s"], 50)
        self.assertEqual(clock["work"]["attempts_observed"], 1)
        self.assertEqual(clock["work"]["coverage"], "best_effort")

    def test_status_exposes_item_counts_not_verified_completion(self):
        self.n["fanout"] = {"items": ["available", "missing", "partial"]}
        (self.r / "graph.json").write_text(json.dumps({"nodes": [self.n]}))
        for i, status in enumerate(("done", "failed", "partial")):
            (self.r / "nodes" / f"probe.{i}.json").write_text(json.dumps({
                "status": status, "efp": c.efp({"probe": self.n}, self.n), "fp_rule_version": c.FP_RULE_VERSION}))
        with patch.object(c, "runner_alive", return_value=False):
            st = c.run_state(self.r)
        counts = st["nodes"]["probe"].get("item_counts", {})
        self.assertEqual(counts.get("basis"), "literal fanout items")
        self.assertEqual(counts["total"], 3)
        self.assertEqual(counts["done"], 1)
        self.assertEqual(counts["failed"], 1)
        self.assertEqual(counts["partial"], 1)
        self.assertNotIn("verified", counts)
        with patch.object(door, "_resolve_read_run", return_value=(self.r, st, None)), patch.object(door._common, "run_child_metrics", return_value={}):
            out = door.act_status({"run_id": self.r.name})
        self.assertEqual(out["nodes"]["probe"]["clocks"], st["nodes"]["probe"]["clocks"])
        self.assertEqual(out["nodes"]["probe"]["item_counts"], counts)
        self.assertEqual(out["accounting"]["task_total_ceiling"], "not_enforced")

    def test_hold_expiry_does_not_claim_release_or_bounded_hold(self):
        gate = {"id": "approve", "type": "gate", "question": "Continue?", "options": ["yes", "no"], "hold_timeout": 60}
        (self.r / "graph.json").write_text(json.dumps({"nodes": [gate]}))
        marker = {"since": 100, "_def": c.efp({"approve": gate}, gate), "fp_rule_version": c.FP_RULE_VERSION}
        (self.r / "gates" / "approve.held.json").write_text(json.dumps(marker))
        with patch.object(c, "runner_alive", return_value=False), patch("time.time", return_value=170):
            st = c.run_state(self.r)
        clock = st["nodes"]["approve"]["clocks"]
        self.assertEqual(st["status"], "held")
        self.assertEqual(clock["phase"], "held")
        self.assertEqual(clock["hold"]["elapsed_s"], 70)
        self.assertEqual(clock["hold"]["remaining_s"], 0)
        self.assertTrue(clock["hold"]["expired"])
        self.assertEqual(clock["hold"]["expiry_action"], "keep_holding")
        gate.pop("hold_timeout")
        (self.r / "graph.json").write_text(json.dumps({"nodes": [gate]}))
        with patch.object(c, "runner_alive", return_value=False):
            clock = c.run_state(self.r)["nodes"]["approve"]["clocks"]
        self.assertIsNone(clock["hold"]["remaining_s"])
        self.assertEqual(clock["hold"]["ceiling"], "unbounded")

    def test_seat_timeout_is_expired_queue_not_execution(self):
        rec = {"status": "failed", "error_class": "seat_wait", "error": "original refusal",
               "ms": 900000, "efp": c.efp({"probe": self.n}, self.n), "fp_rule_version": c.FP_RULE_VERSION}
        (self.r / "nodes" / "probe.json").write_text(json.dumps(rec))
        with patch.object(c, "runner_alive", return_value=False):
            clock = c.run_state(self.r)["nodes"]["probe"]["clocks"]
        self.assertEqual(clock["phase"], "expired")
        self.assertEqual(clock["exhaustion_reason"], "queue_timeout")
        self.assertEqual(clock["queue_elapsed_s"], 900)
        self.assertEqual(clock["work"]["observed_s"], 0)

    def test_work_sums_attempts_from_spawn_not_node_start(self):
        self.rows("events.jsonl", [{"ts": ts(10), "event": "node.started", "node": "probe"}])
        self.rows("spawn-ledger.jsonl", [
            {"ts": ts(100), "role": "child", "node": "probe", "index": None, "pid": 11, "skey": "one"},
            {"ts": ts(150), "role": "child_end", "node": "probe", "index": None, "pid": 11, "skey": "one"},
            {"ts": ts(200), "role": "child", "node": "probe", "index": None, "pid": 12, "skey": "two"}])
        active = [{"pid": 12, "skey": "two", "started": ts(200)}]
        with patch.object(c, "runner_alive", return_value=True), patch.object(c, "_active_spawns", return_value=active), patch("time.time", return_value=250):
            st = c.run_state(self.r)
        clock = st["nodes"]["probe"]["clocks"]
        self.assertEqual(clock["phase"], "active")
        self.assertEqual(clock["work"]["observed_s"], 100)
        self.assertEqual(clock["work"]["attempts_observed"], 2)
        self.assertEqual(clock["work"]["unknown_intervals"], 0)
        self.assertEqual(clock["active"][0]["configured_remaining_s"], 850)
        # An unclosed old attempt is not assumed alive after interruption.
        with patch.object(c, "runner_alive", return_value=False), patch("time.time", return_value=400):
            clock = c.run_state(self.r)["nodes"]["probe"]["clocks"]
        self.assertEqual(clock["work"]["observed_s"], 50)
        self.assertEqual(clock["work"]["unknown_intervals"], 1)

    def test_queued_clock_does_not_claim_work_or_total_cap(self):
        self.rows("events.jsonl", [{"ts": ts(100), "event": "seat.wait", "node": "probe", "index": None, "cap": 4, "spawn": 0}])
        with patch.object(c, "runner_alive", return_value=True), patch("time.time", return_value=400):
            st = c.run_state(self.r)
        clock = st["nodes"]["probe"].get("clocks", {})
        self.assertEqual(clock.get("phase"), "queued")
        self.assertEqual(clock["queue"][0]["elapsed_s"], 300)
        self.assertEqual(clock["queue"][0]["remaining_upper_bound_s"], 600)
        self.assertEqual(clock["work"]["observed_s"], 0)
        self.assertEqual(clock["task_total_ceiling"], "not_enforced")


if __name__ == "__main__":
    unittest.main()
