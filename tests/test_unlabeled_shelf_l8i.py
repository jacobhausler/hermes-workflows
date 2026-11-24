#!/usr/bin/env python3
"""l8i (instance-label-first law): the door WARNS (never blocks) a shelf launch
carrying neither lane_key nor description; the launch succeeds. The read model
(run_state) and the dashboard projection (_view) surface lane_key (run.json
identity stamp, pre-existing) and the graph description so every title surface
resolves the same label. Shelf description rides the launched graph at the door.
Hermetic: fake spawn, sandboxed home + runs root (#71 double-pin)."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_l8i", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso71_l8i; _iso71_l8i.install(door)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT

DASH_SPEC = importlib.util.spec_from_file_location("wf_dash_l8i", ROOT / "dashboard" / "plugin_api.py")
dash = importlib.util.module_from_spec(DASH_SPEC)
DASH_SPEC.loader.exec_module(dash)

ECHO = {"name": "unlabeled-tpl", "nodes": [{"id": "x", "type": "echo", "output": {"ok": True}}]}


def shelved(name, graph=None, description=None):
    args = {"action": "save", "graph": dict(graph or ECHO), "name": name}
    if description is not None:
        args["description"] = description
    out = json.loads(door.handle(args))
    assert out.get("saved") == name, out
    return name


class UnlabeledShelfDoor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root / "runs"),
                                      "HERMES_HOME": str(self.root / "home")})
        env.start()
        self.addCleanup(env.stop)
        spawn = patch.object(door, "_spawn_runner", side_effect=lambda r: None)
        spawn.start()
        self.addCleanup(spawn.stop)

    def _run_dir(self, rid):
        return Path(os.environ["WF_RUNS_ROOT"]) / rid

    def _warn(self, out):
        return [w for w in out.get("run_warnings", []) if "unlabeled shelf launch" in w]

    def test_unlabeled_shelf_launch_warns_and_succeeds(self):
        shelved("unlabeled-tpl")
        out = json.loads(door.handle({"action": "run", "from": "unlabeled-tpl"}))
        rid = out.get("run_id")
        self.assertTrue(rid, f"launch must SUCCEED (warn, don't block): {out}")
        w = self._warn(out)
        self.assertEqual(len(w), 1, out.get("run_warnings"))
        # The warning NAMES both missing data and the fix.
        self.assertIn("no lane_key", w[0])
        self.assertIn("no description", w[0])
        self.assertIn("lane_key=<label>", w[0])
        # The run record carries neither datum, so the read model stays honest.
        st = door.run_state(self._run_dir(rid))
        self.assertNotIn("lane_key", st)
        self.assertNotIn("description", st)
        self.assertEqual(dash._view(self._run_dir(rid)).get("lane_key"), None)
        self.assertEqual(dash._view(self._run_dir(rid)).get("description"), None)

    def test_shelf_description_rides_the_launch_and_silences_the_warning(self):
        shelved("described-tpl", description="Reconcile the shelf. Then prune.")
        out = json.loads(door.handle({"action": "run", "from": "described-tpl"}))
        rid = out.get("run_id")
        self.assertTrue(rid, out)
        self.assertEqual(self._warn(out), [], "description present => no door warning")
        # The envelope description is instance datum: it rides graph.json.
        graph = json.loads((self._run_dir(rid) / "graph.json").read_text())
        self.assertEqual(graph.get("description"), "Reconcile the shelf. Then prune.")
        st = door.run_state(self._run_dir(rid))
        self.assertEqual(st.get("description"), "Reconcile the shelf. Then prune.")
        self.assertNotIn("lane_key", st)
        # The dashboard projection passes it through for the resolver.
        self.assertEqual(dash._view(self._run_dir(rid)).get("description"),
                         "Reconcile the shelf. Then prune.")

    def test_labeled_shelf_launch_carries_lane_key_end_to_end(self):
        shelved("labeled-tpl")
        out = json.loads(door.handle({"action": "run", "from": "labeled-tpl",
                                      "lane_key": "ship20-m/W2c"}))
        rid = out.get("run_id")
        self.assertTrue(rid, out)
        self.assertEqual(self._warn(out), [], "lane_key present => no door warning")
        meta = json.loads((self._run_dir(rid) / "run.json").read_text())
        self.assertEqual(meta.get("lane_key"), "ship20-m/W2c")
        st = door.run_state(self._run_dir(rid))
        self.assertEqual(st.get("lane_key"), "ship20-m/W2c")
        self.assertEqual(dash._view(self._run_dir(rid)).get("lane_key"), "ship20-m/W2c")

    def test_inline_launch_is_never_warned_and_stays_golden(self):
        out = json.loads(door.handle({"action": "run", "graph": dict(ECHO)}))
        rid = out.get("run_id")
        self.assertTrue(rid, out)
        self.assertEqual(self._warn(out), [], "the door warning is shelf-only")
        meta = json.loads((self._run_dir(rid) / "run.json").read_text())
        self.assertNotIn("lane_key", meta)  # no lane => no stamp (golden key set)
        st = door.run_state(self._run_dir(rid))
        self.assertNotIn("lane_key", st)
        self.assertNotIn("description", st)

    def test_dry_run_surfaces_the_same_warning(self):
        shelved("dry-tpl")
        out = json.loads(door.handle({"action": "run", "from": "dry-tpl", "dry_run": True}))
        self.assertTrue(out.get("ok") and out.get("dry_run"), out)
        self.assertEqual(len(self._warn(out)), 1, out.get("run_warnings"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
