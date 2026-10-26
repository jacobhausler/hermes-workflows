#!/usr/bin/env python3
"""#498: the run verb accepts launch-time concurrency args, baked like graph keys.

Run: env -u WF_RUNS_ROOT -u HERMES_HOME PYTHONPATH=/opt/hermes
     /opt/hermes/.venv/bin/python tests/test_concurrency_run_args_498.py
"""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_498", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)

BASE = {"name": "args498", "nodes": [{"id": "a", "type": "echo", "output": 1}]}


class Owner:
    def __init__(self):
        self.settings = {}

    def get_config(self, key, default=None):
        return self.settings.get(key, default)


class ConcurrencyRunArgs498(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="wf498-args-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "home").mkdir()
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root / "runs"),
                                      "HERMES_HOME": str(self.root / "home")})
        env.start()
        self.addCleanup(env.stop)
        wf_test_isolation.install(door)
        self.owner = Owner()
        ctx = patch.object(door, "_CTX", self.owner)
        ctx.start()
        self.addCleanup(ctx.stop)
        spawn = patch.object(door, "_spawn_runner")
        self.spawn = spawn.start()
        self.addCleanup(spawn.stop)

    def launch(self, **kwargs):
        result = door.act_run({"graph": dict(BASE), **kwargs})
        self.assertIn("run_id", result, result)
        path = self.root / "runs" / result["run_id"] / "run.json"
        self.assertTrue(path.is_file(), str(path))
        return json.loads(path.read_text())

    def test_args_bake_into_run_json(self):
        meta = self.launch(concurrency=3, item_concurrency=6)
        self.assertEqual((meta["concurrency"], meta["item_concurrency"]), (3, 6))

    def test_args_clamped_to_owner_caps(self):
        self.owner.settings.update(max_concurrency=2, max_item_concurrency=4)
        meta = self.launch(concurrency=16, item_concurrency=32)
        self.assertEqual((meta["concurrency"], meta["item_concurrency"]), (2, 4))

    def test_absent_args_keep_original_meta_shape(self):
        meta = self.launch(name="args498")
        self.assertNotIn("concurrency", meta)
        self.assertNotIn("item_concurrency", meta)

    def test_co_declared_key_refused_before_write(self):
        for key in ("concurrency", "item_concurrency"):
            with self.subTest(key=key):
                result = door.act_run({"graph": {**BASE, key: 2}, key: 6})
                self.assertIn(key, result.get("error", ""), result)
                self.assertFalse(list((self.root / "runs").glob("*/run.json")))

    def test_bad_arg_values_refused_before_write(self):
        for key in ("concurrency", "item_concurrency"):
            for value in (0, -1, True, 1.5, "2", None, []):
                with self.subTest(key=key, value=value):
                    result = door.act_run({"graph": dict(BASE), key: value})
                    self.assertIn(key, result.get("error", ""), result)
                    self.assertFalse(list((self.root / "runs").glob("*/run.json")))

    def test_args_never_participate_in_fingerprints(self):
        common = door._common
        self.assertEqual(common.graph_fingerprint(BASE),
                         common.graph_fingerprint({**BASE, "concurrency": 3,
                                                   "item_concurrency": 6}))


if __name__ == "__main__":
    unittest.main()
