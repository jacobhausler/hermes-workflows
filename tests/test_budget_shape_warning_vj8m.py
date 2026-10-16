#!/usr/bin/env python3
"""#256: validate lints low effective turn caps without rejecting or rewriting them."""
import copy
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


class BudgetShapeWarning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="wf-budget-warning-")
        cls.home = Path(cls.tmp.name)
        cls.env = patch.dict(os.environ, {
            "HERMES_HOME": str(cls.home),
            "WF_RUNS_ROOT": str(cls.home / "runs"),
            "HERMES_WF_HERMES_BIN": str(ROOT / "tests" / "fake"),
        })
        cls.env.start()
        spec = importlib.util.spec_from_file_location("budget_shape_door", ROOT / "__init__.py")
        assert spec is not None and spec.loader is not None
        cls.door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.door)
        import wf_test_isolation as _iso71
        _iso71.install(cls.door)
        # Core may initialise its sandbox home during the first config read.
        # Measure the door's no-write promise after that host bootstrap.
        warm = json.loads(cls.door.handle({"action": "validate", "graph": {
            "name": "warm", "nodes": [{"id": "warm", "type": "agent", "goal": "Inspect"}]
        }}))
        assert warm.get("ok") is True, warm

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.tmp.cleanup()

    def validate(self, node, defaults=None):
        graph = {"name": "budget-warning", "nodes": [node]}
        if defaults is not None:
            graph["defaults"] = defaults
        before = copy.deepcopy(graph)
        files = set(self.home.rglob("*"))
        result = json.loads(self.door.handle({"action": "validate", "graph": graph}))
        self.assertEqual(graph, before, "validation must not rewrite the caller's graph")
        self.assertEqual(set(self.home.rglob("*")), files, "validate must not write or spawn")
        return result

    def agent(self, **kw):
        return dict(id="lane", type="agent", goal="Inspect the lane", **kw)

    def assert_ok(self, result):
        self.assertIs(result.get("ok"), True, result)
        self.assertEqual(result["errors"], [])
        self.assertIn("lane", result["resolved_routes"])

    def test_below_equal_above_each_p95(self):
        for shape, preset in self.door._common.SHAPE_PRESETS.items():
            budget = preset["max_turns"]
            for delta in (-1, 0, 1):
                with self.subTest(shape=shape, delta=delta):
                    cap = budget + delta
                    result = self.validate(self.agent(shape=shape, max_turns=cap))
                    self.assert_ok(result)
                    if delta < 0:
                        warnings = result.get("warnings", [])
                        self.assertEqual(len(warnings), 1, result)
                        warning = warnings[0]
                        self.assertEqual(set(warning), {"node", "field", "msg"})
                        self.assertEqual(warning["node"], "lane")
                        self.assertEqual(warning["field"], "max_turns")
                        for text in (str(cap), str(budget), shape, "p95"):
                            self.assertIn(text, warning["msg"])
                    else:
                        self.assertNotIn("warnings", result)

    def test_missing_shape_uses_the_runner_default(self):
        result = self.validate(self.agent(max_turns=1))
        self.assert_ok(result)
        self.assertEqual(len(result.get("warnings", [])), 1, result)
        self.assertIn(self.door._common.DEFAULT_SHAPE, result["warnings"][0]["msg"])

    def test_defaults_cap_warns_only_when_effective(self):
        result = self.validate(self.agent(), {"max_turns": 1})
        self.assert_ok(result)
        self.assertEqual(len(result.get("warnings", [])), 1, result)
        result = self.validate(self.agent(shape="review"), {"max_turns": 1})
        self.assert_ok(result)
        self.assertNotIn("warnings", result, "named shape wins over graph defaults")
        result = self.validate(self.agent(max_turns=100), {"max_turns": 1})
        self.assert_ok(result)
        self.assertNotIn("warnings", result, "explicit node cap wins over defaults")

    def test_unset_caps_use_presets_without_warning(self):
        for shape in (None, *self.door._common.SHAPE_PRESETS):
            node = self.agent(**({"shape": shape} if shape else {}))
            result = self.validate(node)
            self.assert_ok(result)
            self.assertNotIn("warnings", result)

    def test_fanout_head_is_linted_once(self):
        node = self.agent(shape="review", max_turns=1, fanout={"items": ["a", "b"]})
        result = self.validate(node)
        self.assert_ok(result)
        self.assertEqual(len(result.get("warnings", [])), 1, result)

    def test_nonspawning_nodes_do_not_warn(self):
        for node in (
            {"id": "gate", "type": "gate", "question": "ok?", "options": ["yes", "no"]},
            {"id": "echo", "type": "echo", "output": {"ok": True}},
        ):
            result = self.validate(node, {"max_turns": 1})
            self.assertIs(result.get("ok"), True, result)
            self.assertNotIn("warnings", result)

    def test_invalid_budgets_still_fail_validation(self):
        for cap in (0, -1, True, "5", 201):
            result = self.validate(self.agent(shape="review", max_turns=cap))
            self.assertIs(result.get("ok"), False, result)
            self.assertTrue(result.get("errors"), result)
            self.assertNotIn("warnings", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
