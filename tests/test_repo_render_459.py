#!/usr/bin/env python3
"""#459 G2 (est-rza3t): agent `repo:` joins the {run.KEY} render surface, mirroring `profile`.

Before this, a portable (library-sourced or template) graph could never declare
its node-level git lane: the render surface omitted `repo`, so the mechanical
lane guards (incomplete_work / lane_wreckage) were unreachable from traveling
packs. Contracts pinned here:
  (1) inline map mode renders repo like profile;
  (2) library-sourced mode renders repo through the SHARED traversal
      (_include_text_fields yields repo for string fields);
  (3) a seed (string) binding refuses a {run.KEY} living in repo;
  (4) an unbound {run.KEY} in repo refuses library-sourced binding fail-closed;
  (5) the model-reachable schema description names agent repo lanes.

Standalone script (no pytest):
  python3 tests/test_repo_render_459.py
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_459g2", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)


def _g(repo_val):
    return {"name": "rr459", "nodes": [
        {"id": "build", "type": "agent", "goal": "work the lane", "repo": repo_val}]}


class RepoRender459(unittest.TestCase):
    def test_inline_map_renders_repo(self):
        out = door._bind_run_context(_g("/srv/lanes/{run.lane}"), {"lane": "alpha"})
        self.assertEqual(out["nodes"][0]["repo"], "/srv/lanes/alpha")

    def test_library_mode_renders_repo(self):
        out = door._bind_run_context(_g("{run.lane}"), {"lane": "/home/x/lane-a"},
                                     library_sourced=True)
        self.assertEqual(out["nodes"][0]["repo"], "/home/x/lane-a")

    def test_library_mode_unbound_refuses(self):
        with self.assertRaises(ValueError):
            door._bind_run_context(_g("{run.lane}"), {"other": "x"}, library_sourced=True)

    def test_seed_refuses_repo_ref(self):
        with self.assertRaisesRegex(ValueError, "repo"):
            door._bind_run_context(_g("/srv/lanes/{run.lane}"), "plain seed")

    def test_shared_traversal_yields_repo(self):
        import sys
        sys.path.insert(0, str(ROOT))
        import wfcommon
        fields = [lab for lab, _ in wfcommon._include_text_fields(
            {"type": "agent", "goal": "g", "repo": "{run.lane}"})]
        self.assertIn("repo", fields)
        self.assertEqual(fields, ["goal", "repo"])  # authored order preserved

    def test_schema_description_names_repo(self):
        d = door.WORKFLOW_SCHEMA["parameters"]["properties"]["run_context"]["description"]
        self.assertIn("agent repo lanes", d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
