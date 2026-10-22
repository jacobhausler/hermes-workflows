#!/usr/bin/env python3
"""hw-udg: validate warns (never rejects) on three advisory semantic classes:
a `when` reading a field the ancestor's declared schema does not declare, a machine-gate
probe whose argv[0] is not executable on the validating host, and a fan-out quorum
below the literal item count."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))


class ValidateSemanticWarnings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="wf-semwarn-")
        home = Path(cls.tmp.name)
        cls.env = patch.dict(os.environ, {
            "HERMES_HOME": str(home / "home"),
            "WF_RUNS_ROOT": str(home / "runs"),
            "HERMES_WF_HERMES_BIN": str(ROOT / "tests" / "fake"),
        })
        cls.env.start()
        spec = importlib.util.spec_from_file_location("semwarn_door", ROOT / "__init__.py")
        assert spec is not None and spec.loader is not None
        cls.door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.door)
        import wf_test_isolation as _iso
        _iso.install(cls.door)

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.tmp.cleanup()

    def validate(self, nodes):
        result = json.loads(self.door.handle({"action": "validate",
                                              "graph": {"name": "semwarn", "nodes": nodes}}))
        self.assertIs(result.get("ok"), True, result)
        self.assertEqual(result["errors"], [])
        return result

    def test_ghost_when_field_warns(self):
        # when reads out.a.ship; ancestor a's declared schema declares only `verdict`
        result = self.validate([
            {"id": "a", "type": "agent", "goal": "Judge",
             "schema": {"type": "object", "required": ["verdict"],
                        "properties": {"verdict": {"type": "string"}}}},
            {"id": "g", "type": "gate", "after": ["a"], "question": "go?",
             "options": ["yes", "no"], "when": "out.a.ship == true"},
        ])
        warnings = result.get("warnings", [])
        self.assertEqual(len(warnings), 1, result)
        row = warnings[0]
        self.assertEqual(set(row), {"node", "field", "msg"})
        self.assertEqual(row["node"], "g")
        self.assertEqual(row["field"], "when")
        self.assertIn("ship", row["msg"])

    def test_declared_when_field_does_not_warn(self):
        result = self.validate([
            {"id": "a", "type": "agent", "goal": "Judge",
             "schema": {"type": "object", "required": ["verdict"],
                        "properties": {"verdict": {"type": "string"}}}},
            {"id": "g", "type": "gate", "after": ["a"], "question": "go?",
             "options": ["yes", "no"], "when": "out.a.verdict == 'ok'"},
        ])
        self.assertNotIn("warnings", result)

    def test_missing_probe_path_warns(self):
        result = self.validate([
            {"id": "w", "type": "gate", "question": "up?", "options": ["yes", "no"],
             "wait": {"until_argv": ["/nonexistent-hwudg/probe"]}},
        ])
        warnings = result.get("warnings", [])
        self.assertEqual(len(warnings), 1, result)
        self.assertEqual(warnings[0]["node"], "w")
        self.assertEqual(warnings[0]["field"], "wait.until_argv")
        self.assertIn("/nonexistent-hwudg/probe", warnings[0]["msg"])

    def test_executable_probe_does_not_warn(self):
        result = self.validate([
            {"id": "w", "type": "gate", "question": "up?", "options": ["yes", "no"],
             "wait": {"until_argv": [sys.executable, "--version"]}},
        ])
        self.assertNotIn("warnings", result)

    def test_quorum_below_item_count_warns(self):
        result = self.validate([
            {"id": "f", "type": "agent", "goal": "x {item}",
             "fanout": {"items": ["a", "b", "c"], "quorum": 2}},
        ])
        warnings = result.get("warnings", [])
        self.assertEqual(len(warnings), 1, result)
        self.assertEqual(warnings[0]["node"], "f")
        self.assertEqual(warnings[0]["field"], "fanout.quorum")
        self.assertIn("2", warnings[0]["msg"])
        self.assertIn("3", warnings[0]["msg"])

    def test_quorum_matching_item_count_does_not_warn(self):
        result = self.validate([
            {"id": "f", "type": "agent", "goal": "x {item}",
             "fanout": {"items": ["a", "b", "c"], "quorum": 3}},
        ])
        self.assertNotIn("warnings", result)

    def test_all_three_classes_warn_together_still_ok(self):
        result = self.validate([
            {"id": "a", "type": "agent", "goal": "Judge",
             "schema": {"type": "object", "required": ["verdict"],
                        "properties": {"verdict": {"type": "string"}}}},
            {"id": "g", "type": "gate", "after": ["a"], "question": "go?",
             "options": ["yes", "no"], "when": "out.a.ship == true"},
            {"id": "w", "type": "gate", "question": "up?", "options": ["yes", "no"],
             "wait": {"until_argv": ["/nonexistent-hwudg/probe"]}},
            {"id": "f", "type": "agent", "goal": "x {item}",
             "fanout": {"items": ["a", "b", "c"], "quorum": 2}},
        ])
        self.assertEqual({row["field"] for row in result["warnings"]},
                         {"when", "wait.until_argv", "fanout.quorum"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
