"""Readable node-id nudges at run/dry_run are advisory, never graph edits."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


class NodeIdAdvisoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = tempfile.TemporaryDirectory(prefix=".tmp-node-id-", dir=HERE)
        cls.addClassCleanup(cls.sandbox.cleanup)
        cls.home = Path(cls.sandbox.name)
        cls.runs = cls.home / "workflows"
        cls.env = mock.patch.dict(os.environ, {
            "HERMES_HOME": str(cls.home),
            "WF_RUNS_ROOT": str(cls.runs),
            "WF_QUOTA_CACHE": str(cls.home / "quota.json"),
            "HERMES_WF_HERMES_BIN": str(HERE / "fake"),
        })
        cls.env.start()
        cls.addClassCleanup(cls.env.stop)
        for key in list(os.environ):
            if (key.startswith("HERMES_WF_") and key != "HERMES_WF_HERMES_BIN") or key in (
                "HERMES_SESSION_ID", "HERMES_UI_SESSION_ID", "HERMES_SESSION_PLATFORM"
            ):
                os.environ.pop(key, None)
        (cls.home / "config.yaml").write_text(
            "plugins:\n  entries:\n    hermes-workflows:\n      settings:\n"
            f"        runs_root: {cls.runs}\n"
        )
        spec = importlib.util.spec_from_file_location("node_id_door", ROOT / "__init__.py")
        cls.door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.door)
        import wf_test_isolation as _iso71
        _iso71.install(cls.door)
        cls.spawns = mock.Mock()
        cls.door._spawn_runner = cls.spawns

    def graph(self, *ids):
        return {"name": "node-id-probe", "nodes": [
            {"id": node_id, "type": "echo", "output": {"ok": True}}
            for node_id in ids
        ]}

    def call(self, **args):
        return json.loads(self.door.handle({"action": "run", **args}))

    def assert_nudge(self, response, node_id):
        self.assertNotIn("error", response, response)
        warnings = response.get("run_warnings", [])
        self.assertEqual(len(warnings), 1, response)
        self.assertIn(repr(node_id), warnings[0])
        self.assertIn("s12", warnings[0])
        self.assertIn("1-3", warnings[0])
        self.assertIn("readable", warnings[0])
        self.assertIn("scan_nodes", warnings[0])
        self.assertNotIn("\n", warnings[0])

    def test_short_and_vowel_ids_get_one_nudge_in_both_paths(self):
        for node_id in ("b", "x", "a", "aeiou", "AEIOU"):
            for dry_run in (True, False):
                with self.subTest(node_id=node_id, dry_run=dry_run):
                    graph = self.graph(node_id)
                    original = copy.deepcopy(graph)
                    before = self.spawns.call_count
                    response = self.call(graph=graph, dry_run=dry_run)
                    self.assert_nudge(response, node_id)
                    self.assertEqual(graph, original)
                    if dry_run:
                        self.assertTrue(response.get("ok"), response)
                        self.assertNotIn("run_id", response)
                        self.assertEqual(self.spawns.call_count, before)
                    else:
                        self.assertTrue(response.get("run_id"), response)
                        self.assertEqual(self.spawns.call_count, before + 1)
                        saved = json.loads((self.runs / response["run_id"] / "graph.json").read_text())
                        self.assertEqual(saved, self.door._common.apply_graph_defaults(original))
                        meta = json.loads((self.runs / response["run_id"] / "run.json").read_text())
                        self.assertNotIn("run_warnings", meta)

    def test_readable_ids_keep_response_without_warning_key(self):
        for dry_run in (True, False):
            response = self.call(graph=self.graph("scan_nodes", "verify_prs", "queue"), dry_run=dry_run)
            self.assertNotIn("error", response, response)
            self.assertNotIn("run_warnings", response, response)

    def test_dry_run_does_not_create_lane_or_run(self):
        before = sorted(str(path.relative_to(self.runs)) for path in self.runs.rglob("*"))
        spawns = self.spawns.call_count
        response = self.call(graph=self.graph("b"), dry_run=True, lane_key="naming-probe")
        self.assert_nudge(response, "b")
        self.assertEqual(self.spawns.call_count, spawns)
        self.assertEqual(before, sorted(str(path.relative_to(self.runs)) for path in self.runs.rglob("*")))
        launched = self.call(graph=self.graph("b"), lane_key="naming-probe")
        self.assert_nudge(launched, "b")
        deduped = self.call(graph=self.graph("b"), lane_key="naming-probe")
        self.assertTrue(deduped.get("deduped"), deduped)
        self.assertEqual(deduped.get("run_id"), launched["run_id"])
        self.assertEqual(self.spawns.call_count, spawns + 1)

    def test_each_offender_is_named_once_and_other_sources_work(self):
        graph = self.graph("b", "ae", "scan_nodes")
        response = self.call(graph=graph, dry_run=True)
        self.assertEqual(len(response.get("run_warnings", [])), 2, response)
        for node_id in ("b", "ae"):
            self.assertEqual(sum(repr(node_id) in line for line in response["run_warnings"]), 1)
        library = self.runs / "library"
        library.mkdir(parents=True, exist_ok=True)
        (library / "naming-probe.json").write_text(json.dumps(self.graph("b")))
        path = self.home / "graph.json"
        path.write_text(json.dumps(self.graph("b")))
        for source in ({"from": "naming-probe"}, {"graph_path": str(path)}):
            for dry_run in (True, False):
                with self.subTest(source=source, dry_run=dry_run):
                    self.assert_nudge(self.call(**source, dry_run=dry_run), "b")

    def test_warned_graph_still_executes_unchanged(self):
        response = self.call(graph=self.graph("b"))
        self.assert_nudge(response, "b")
        completed = subprocess.run(
            [sys.executable, str(ROOT / "wf.py"), "run", response["run_id"]],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        record = json.loads((self.runs / response["run_id"] / "nodes" / "b.json").read_text())
        self.assertEqual(record["status"], "done", record)
        self.assertEqual(record["output"], {"ok": True})


if __name__ == "__main__":
    unittest.main(verbosity=2)
