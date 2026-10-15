"""P02 read-model clocks: no scheduler, no invented total authorization."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
HOME = tempfile.TemporaryDirectory(prefix="p02-home-", dir=ROOT)
os.environ["HERMES_HOME"] = HOME.name
os.environ["WF_RUNS_ROOT"] = str(Path(HOME.name) / "workflows")
import wfcommon as c
import wf
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

    def spawn(self, pid, start, attempt=0, index=None, ledger=True):
        """Real producer contract, without launching any child processes."""
        skey = f"wf:test:probe{'' if index is None else '.' + str(index)}.deadbeef"
        title = f"{skey}#a{attempt}"
        wf.write_spawn_record(self.r, self.n, {"probe": self.n}, index, attempt,
                              ["hermes", "chat", "--continue", title],
                              self.r / "child.log", pid, skey, ts(start))
        if ledger:
            self.ledger("child", pid, skey, start, index)
        return title, skey

    def ledger(self, role, pid, skey, stamp, index=None):
        with patch.object(wf, "now", return_value=ts(stamp)):
            wf.ledger_row(self.r, role, pid, node="probe", index=index, skey=skey)

    def live_state(self, titles, now=250):
        # Only the OS liveness boundary and clock are simulated; writers,
        # fingerprint checks, _verify_spawn_rec and _active_spawns stay real.
        def ps(argv, **kwargs):
            return SimpleNamespace(stdout="S hermes chat --continue " + titles[int(argv[3])])
        with patch.object(c, "runner_alive", return_value=True), \
             patch.object(c.os, "kill"), patch.object(c.subprocess, "run", side_effect=ps), \
             patch("time.time", return_value=now):
            return c.run_state(self.r)

    def test_real_spawn_retry_reconciles_verified_title_with_ledger(self):
        pid = 999999991
        _, skey = self.spawn(pid, 100)
        self.ledger("child_end", pid, skey, 150)
        # PID reuse and the same bare key must still identify a new interval.
        title, _ = self.spawn(pid, 200, attempt=1)
        view = self.live_state({pid: title})["nodes"]["probe"]
        self.assertEqual(view["active_spawns"][0]["skey"], title)
        self.assertEqual(view["active_spawns"][0]["attempt"], 1)
        self.assertEqual(view["clocks"]["work"]["observed_s"], 100)
        self.assertEqual(view["clocks"]["work"]["attempts_observed"], 2)
        self.assertEqual(view["clocks"]["work"]["unknown_intervals"], 0)
        self.assertEqual(view["clocks"]["active"][0]["elapsed_s"], 50)
        self.assertIsNone(view["clocks"]["active"][0]["index"])
        # A previous attempt's title is not proof of current PID identity.
        view = self.live_state({pid: skey + "#a0"})["nodes"]["probe"]
        self.assertEqual(view["clocks"]["active"], [])
        self.assertEqual(view["clocks"]["work"]["observed_s"], 50)
        self.assertEqual(view["clocks"]["work"]["unknown_intervals"], 1)

    def test_real_spawn_missing_retry_start_does_not_reuse_old_pid_interval(self):
        pid = 999999991
        _, skey = self.spawn(pid, 100)
        title, _ = self.spawn(pid, 200, attempt=1, ledger=False)
        work = self.live_state({pid: title})["nodes"]["probe"]["clocks"]["work"]
        self.assertEqual(work["observed_s"], 0)
        self.assertEqual(work["unknown_intervals"], 2)  # old open + missing live start
        self.assertEqual(work["attempts_observed"], 1)
        self.ledger("child_end", pid, skey, 150)
        work = self.live_state({pid: title})["nodes"]["probe"]["clocks"]["work"]
        self.assertEqual(work["observed_s"], 50)
        self.assertEqual(work["unknown_intervals"], 1)
        (self.r / "spawn-ledger.jsonl").unlink()
        work = self.live_state({pid: title})["nodes"]["probe"]["clocks"]["work"]
        self.assertEqual(work["observed_s"], 0)
        self.assertEqual(work["unknown_intervals"], 1)
        self.assertEqual(work["completeness"], "unknown")
        self.assertTrue(work["lower_bound"])

    def test_real_spawn_ledger_append_can_follow_record_timestamp(self):
        _, skey = self.spawn(999999991, 100)
        title, _ = self.spawn(999999992, 200, attempt=1, ledger=False)
        self.ledger("child", 999999992, skey, 200.25)
        view = self.live_state({999999992: title})["nodes"]["probe"]
        self.assertEqual(view["clocks"]["work"]["observed_s"], 49.75)
        self.assertEqual(view["clocks"]["work"]["attempts_observed"], 2)
        self.assertEqual(view["clocks"]["work"]["unknown_intervals"], 1)
        self.assertEqual(view["clocks"]["active"][0]["elapsed_s"], 50)

    def test_real_fanout_active_clocks_keep_canonical_item_indexes(self):
        self.n["fanout"] = {"items": ["one", "two"]}
        (self.r / "graph.json").write_text(json.dumps({"nodes": [self.n]}))
        first, _ = self.spawn(999999991, 100, index=0)
        second, _ = self.spawn(999999992, 200, attempt=1, index=1)
        view = self.live_state({999999991: first, 999999992: second})["nodes"]["probe"]
        active = view["clocks"]["active"]
        self.assertEqual([row["index"] for row in active], [0, 1])
        self.assertEqual([row["index"] for row in view["active_spawns"]], [0, 1])
        self.assertEqual([row["elapsed_s"] for row in active], [150, 50])
        self.assertEqual([row["configured_remaining_s"] for row in active], [750, 850])
        self.assertEqual(view["clocks"]["work"]["observed_s"], 200)
        self.assertEqual(view["clocks"]["work"]["unknown_intervals"], 0)
        # Identity projection is read-only: the real writer's persisted shape
        # still carries neither an item index nor a ledger-key alias.
        for path in (self.r / "nodes").glob("*.json"):
            rec = json.loads(path.read_text())
            self.assertNotIn("index", rec)
            self.assertNotIn("ledger_skey", rec)

    def test_missing_accounting_evidence_is_explicit(self):
        for mode in ("missing", "unreadable", "invalid_utf8", "orphan", "live"):
            with self.subTest(mode=mode):
                ledger = self.r / "spawn-ledger.jsonl"
                if ledger.is_dir():
                    ledger.rmdir()
                elif ledger.exists():
                    ledger.unlink()
                if mode == "unreadable":
                    ledger.mkdir()  # deterministic OSError, even for a privileged CI user
                if mode == "invalid_utf8":
                    ledger.write_bytes(b"\xff")
                if mode == "orphan":
                    self.rows("spawn-ledger.jsonl", [{"role": "child_end", "node": "probe", "pid": 11, "skey": "one", "ts": ts(150)}])
                active = [{"pid": 11, "skey": "one", "started": ts(100)}] if mode == "live" else []
                with patch.object(c, "runner_alive", return_value=bool(active)), patch.object(c, "_active_spawns", return_value=active), patch("time.time", return_value=150):
                    st = c.run_state(self.r)
                work = st["nodes"]["probe"]["clocks"]["work"]
                self.assertEqual(work["observed_s"], 0)
                self.assertEqual(work.get("completeness"), "unknown")
                self.assertEqual(st["accounting"].get("coverage"), "best_effort")
                self.assertEqual(work["unknown_intervals"], 1 if mode in ("orphan", "live") else None)

    def test_closed_history_does_not_hide_a_missing_live_start(self):
        self.rows("spawn-ledger.jsonl", [
            {"ts": ts(100), "role": "child", "node": "probe", "pid": 11, "skey": "one"},
            {"ts": ts(150), "role": "child_end", "node": "probe", "pid": 11, "skey": "one"}])
        active = [{"pid": 11, "skey": "one", "started": ts(200)}]
        with patch.object(c, "runner_alive", return_value=True), patch.object(c, "_active_spawns", return_value=active), patch("time.time", return_value=250):
            work = c.run_state(self.r)["nodes"]["probe"]["clocks"]["work"]
        self.assertEqual(work["observed_s"], 50)
        self.assertEqual(work["unknown_intervals"], 1)

    def test_history_is_indexed_once_with_explicit_read_budget(self):
        nodes = [{**self.n, "id": f"n{i}"} for i in range(80)]
        (self.r / "graph.json").write_text(json.dumps({"nodes": nodes}))
        self.rows("spawn-ledger.jsonl", [{"node": "removed", "role": "child", "pid": i, "skey": str(i), "ts": ts(100)} for i in range(1000)])
        with patch.object(c, "runner_alive", return_value=False), patch.object(c, "execution_clocks", wraps=c.execution_clocks) as fold:
            st = c.run_state(self.r)
        self.assertEqual(sum(len(call.args[4]) for call in fold.call_args_list), 0)
        history = (self.r / "spawn-ledger.jsonl").read_text()
        self.rows("spawn-ledger.jsonl", [
            {"node": "n0", "role": "child", "pid": 1, "skey": "current", "ts": ts(100)},
            {"node": "n0", "role": "child_end", "pid": 1, "skey": "current", "ts": ts(150)}])
        with (self.r / "spawn-ledger.jsonl").open("a") as stream:
            stream.write(history)
        with patch.object(c, "CLOCK_LEDGER_MAX_BYTES", 1024), patch.object(c, "runner_alive", return_value=False):
            st = c.run_state(self.r)
        coverage = st["accounting"]["ledger"]
        self.assertEqual(coverage["status"], "partial")
        self.assertLessEqual(coverage["bytes_read"], 1024)
        self.assertIsNone(st["accounting"]["unknown_intervals"])
        self.assertEqual(st["accounting"]["observed_work_s"], 50)

    def test_list_skips_discarded_telemetry_for_every_run(self):
        runs = []
        for i in range(60):
            r = self.r / str(i)
            r.mkdir()
            (r / "graph.json").write_text(json.dumps({"nodes": [self.n]}))
            runs.append(r)
        with patch.object(door._common, "iter_run_dirs", return_value=runs), patch.object(door._common, "runner_alive", return_value=False), patch.object(door._common, "_clock_ledger", wraps=door._common._clock_ledger) as ledger:
            result = door.act_list({})
        self.assertEqual(result["total"], 60)
        self.assertEqual(len(result["runs"]), 50)
        ledger.assert_not_called()

    def test_dashboard_census_skips_discarded_telemetry(self):
        spec = importlib.util.spec_from_file_location("p02_dashboard", ROOT / "dashboard" / "plugin_api.py")
        dashboard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dashboard)
        with patch.object(dashboard, "_workflow_common", return_value=c), patch.object(c, "runner_alive", return_value=False), patch.object(c, "profiles_by_session", return_value={}), patch.object(c, "_clock_ledger", wraps=c._clock_ledger) as ledger:
            self.assertEqual(dashboard._view(self.r)["status"], "pending")
        ledger.assert_not_called()

    def test_dynamic_inventory_is_unknown_not_zero_completion(self):
        self.n["fanout"] = {"items_from": "source.items"}
        (self.r / "graph.json").write_text(json.dumps({"nodes": [self.n]}))
        with patch.object(c, "runner_alive", return_value=False):
            counts = c.run_state(self.r)["nodes"]["probe"]["item_counts"]
        self.assertIsNone(counts["total"])
        self.assertIsNone(counts["done"])
        self.assertIsNone(counts["unknown"])

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

    def test_fanout_expiration_summary_preserves_mixed_outcomes(self):
        for inventory in (["a", "b"], ["a", "b", "stale"]):
            self.n["fanout"] = {"items": inventory}
            (self.r / "graph.json").write_text(json.dumps({"nodes": [self.n]}))
            fp = {"efp": c.efp({"probe": self.n}, self.n), "fp_rule_version": c.FP_RULE_VERSION}
            for second in ("seat_wait", "done", "timeout", "cancelled"):
                results = []
                for i, outcome in enumerate(("seat_wait", second, "seat_wait")[:len(inventory)]):
                    rec = {**fp, "item": inventory[i], "status": "done" if outcome == "done" else "failed", "error_class": outcome, "error": outcome, "ms": 900000}
                    if i == 2:
                        rec["efp"] = "stale"
                    results.append(rec)
                    (self.r / "nodes" / f"probe.{i}.json").write_text(json.dumps(rec))
                # Actual fanout failure writer: no aggregate error_class; item
                # evidence is in efp-valid item records, all_results under output.
                aggregate = {**fp, "status": "failed", "error": "quorum not met",
                             "failed_detail": [{"index": i, "item": r["item"], "error": r["error"]}
                                               for i, r in enumerate(results) if r["status"] != "done" and r["error_class"] != "cancelled"],
                             "output": {"items": [], "all_results": results}}
                (self.r / "nodes" / "probe.json").write_text(json.dumps(aggregate))
                with patch.object(c, "runner_alive", return_value=False):
                    view = c.run_state(self.r)["nodes"]["probe"]
                summary = view["clocks"].get("item_expirations", {})
                self.assertEqual(summary.get("queue_timeout", {}).get("count"), 2 if second == "seat_wait" else 1)
                self.assertEqual(summary["queue_timeout"]["observed_queue_s"], 1800 if second == "seat_wait" else 900)
                self.assertEqual(summary.get("work_timeout", {}).get("count", 0), int(second == "timeout"))
                self.assertEqual(view["clocks"]["phase"], "failed")
                self.assertEqual(view["item_counts"]["unknown"], len(inventory) - 2)
                self.assertEqual(view["item_counts"]["done"], int(second == "done"))
                self.assertEqual(view["item_counts"]["cancelled"], int(second == "cancelled"))
                self.assertEqual(view["clocks"]["work"]["observed_s"], 0)

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
