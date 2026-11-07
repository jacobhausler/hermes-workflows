"""Actionability and replay use canonical committed records, not item/progress events."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf


class CommittedTransitions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wf-actionable-")
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.node: dict[str, Any] = {"id": "worker", "type": "agent", "goal": "work"}
        self.byid = {"worker": self.node}
        self.graph = {"name": "actionable", "nodes": [self.node]}
        self.store_graph()
        (self.directory / "run.json").write_text(json.dumps({"owner": {"session_id": "owner"}}))
        self.calls = []
        def deliver(rec, sid, text, tid, owner=None):
            self.assertEqual(sid, "owner")
            self.assertEqual(wf.node_rec(self.directory, self.node, self.byid)[0], "failed")
            self.calls.append((text, tid))
            return True
        self.delivery = patch.object(wf, "_wake_deliver", side_effect=deliver)
        self.delivery.start()
        self.addCleanup(self.delivery.stop)
        self.mirror = patch.object(wf, "_outbound_bridge", return_value=None)
        self.mirror.start()
        self.addCleanup(self.mirror.stop)

    def store_graph(self):
        (self.directory / "graph.json").write_text(json.dumps(self.graph))

    def save(self, **extra):
        rec = {"status": "failed", "error_class": "declared_failure", "attempts": 2,
               "skey": "worker-session"}
        rec.update(extra)
        wf.save_node(self.directory, self.node, self.byid, rec)

    def test_commit_replay_restart_and_attempt_identity(self):
        self.save()
        self.assertEqual(len(self.calls), 1)
        first = self.calls[0]
        self.save()
        wf._notify_node_failure(self.directory, "worker")
        spec = importlib.util.spec_from_file_location("restarted_runner", ROOT / "wf.py")
        assert spec is not None and spec.loader is not None
        restarted = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = restarted
        self.addCleanup(sys.modules.pop, spec.name)
        spec.loader.exec_module(restarted)
        with patch.object(restarted, "_wake_deliver", side_effect=AssertionError("duplicate delivery")), \
                patch.object(restarted, "_outbound_bridge", return_value=None):
            restarted._notify_node_failure(self.directory, "worker")
        self.assertEqual(len(wf._wake_ledger_read(self.directory)[0]), 1)
        self.assertEqual(len(self.calls), 1)
        self.save(attempts=3)
        self.assertEqual(len(self.calls), 2)
        self.assertNotEqual(first[1], self.calls[-1][1])
        self.assertIn('node.action_required', first[0])
        self.assertIn('transition=', first[0])
        self.assertIn('not necessarily finished', first[0])

    def test_suppresses_handled_and_cancelled_but_not_invalid_policies(self):
        for policy in ("skip", "fallback"):
            with self.subTest(policy=policy):
                self.node["on_fail"] = policy
                fallback = {"id": "fallback", "type": "agent", "goal": "recover", "after": ["worker"]}
                self.graph["nodes"] = [self.node, fallback]
                self.byid = {n["id"]: n for n in self.graph["nodes"]}
                self.store_graph()
                self.save()
                self.assertEqual(self.calls, [])
        self.node.pop("on_fail")
        self.store_graph()
        for cls in ("cancelled", "stale_graph", "budget_exhausted"):
            self.save(error_class=cls)
        self.assertEqual(self.calls, [])
        for policy in ("missing", "worker", "abort", [], "not-agent", "ancestor"):
            with self.subTest(invalid_or_abort=policy):
                self.node["on_fail"] = policy
                self.node["after"] = ["ancestor"]
                self.graph["nodes"] = [self.node,
                    {"id": "not-agent", "type": "echo", "output": {}},
                    {"id": "ancestor", "type": "agent", "goal": "upstream"}]
                self.byid = {n["id"]: n for n in self.graph["nodes"]}
                self.store_graph()
                before = len(self.calls)
                self.save()
                self.assertEqual(len(self.calls), before + 1)

    def test_precondition_and_empty_skip_are_actionable(self):
        wf._fail_precondition(self.directory, self.node, self.byid, ["missing"])
        self.assertEqual(len(self.calls), 1)
        self.node.update(on_fail="skip", fanout={"items": []})
        self.store_graph()
        self.save(error_class="fanout_empty")
        self.assertEqual(len(self.calls), 2)

    def test_item_failures_are_silent_until_aggregate_commits(self):
        self.node["fanout"] = {"items": ["one", "two"]}
        self.store_graph()
        wf.commit_item_record(self.directory, self.node, self.byid, 0,
                              {"status": "failed", "error_class": "declared_failure"})
        self.assertEqual(self.calls, [])
        self.save(error_class="quorum")
        self.assertEqual(len(self.calls), 1)

    def test_intermediate_retry_and_valid_harvest_do_not_wake(self):
        wf.log(self.directory, "node.retrying", node="worker", error_class="transport")
        wf.save_node(self.directory, self.node, self.byid, {"status": "running", "attempt": 1})
        self.assertEqual(self.calls, [])
        self.save(harvest={"declared_status": "done"}, output={"result": "ok"})
        self.assertEqual(wf.node_rec(self.directory, self.node, self.byid)[0], "done")
        self.assertEqual(self.calls, [])

    def test_stale_definition_does_not_wake_and_amend_generations_do(self):
        old = dict(self.node)
        self.node["goal"] = "new work"
        self.store_graph()
        wf.save_node(self.directory, old, {"worker": old}, {"status": "failed", "error_class": "precondition"})
        self.assertEqual(self.calls, [])
        self.save()
        first_text, first_id = self.calls[0]
        wf.log(self.directory, "graph.amended")
        wf._notify_node_failure(self.directory, "worker")
        self.assertEqual(len(self.calls), 2)
        self.assertNotEqual(first_id, self.calls[-1][1])
        wf._notify_node_failure(self.directory, "worker")
        self.assertEqual(len(self.calls), 2)
        self.assertNotEqual(first_text, self.calls[-1][0])
        self.assertIn('\\"rev\\":0', first_text)
        self.assertIn('\\"rev\\":1', self.calls[-1][0])

    def test_legacy_records_load_without_migration(self):
        path = self.directory / "nodes" / "worker.json"
        path.parent.mkdir()
        record = {"status": "failed", "error_class": "unknown", "error": "old failure",
                  "def_hash": wf.wfcommon.def_hash(self.node), "fp_rule_version": wf.FP_RULE_VERSION}
        path.write_text(json.dumps(record))
        before = path.read_bytes()
        self.assertEqual(wf.node_rec(self.directory, self.node, self.byid)[0], "failed")
        wf._notify_node_failure(self.directory, "worker")
        wf._notify_node_failure(self.directory, "worker")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(path.read_bytes(), before)

    def test_observer_failure_never_overwrites_verdict(self):
        with patch.object(wf, "notify", side_effect=RuntimeError("delivery failed")):
            self.save()
        self.assertEqual(wf.node_rec(self.directory, self.node, self.byid)[0], "failed")
        self.assertEqual(wf.jload(self.directory / "nodes" / "worker.json")["error_class"], "declared_failure")


if __name__ == "__main__":
    unittest.main()
