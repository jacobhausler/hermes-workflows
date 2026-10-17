#!/usr/bin/env python3
"""#459 G3 (est-vp148): `rework` — grammar-accepted, launch-refused.

The spike pins the two halves of the contract: the validator accepts the
SHAPE (so a pack can author bounded rework today and the graph survives
validate/save), and the launch gate refuses with a typed, zero-write
error (so nothing silently degrades). Contracts pinned here:
  (1) a well-formed rework node carries NO validator defect on the key;
  (2) malformed shapes are refused by name (non-agent carrier, unknown
      to, self-loop, out-of-range max_iters, fan-out carrier);
  (3) door._rework_refusal returns None for clean graphs and a typed
      envelope naming every carrier + engine_loop_not_wired otherwise;
  (4) the error explicitly points at the zero-writes law and the track.

Standalone script (no pytest):
  python3 tests/test_rework_accept_459.py
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_459g3", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import sys
sys.path.insert(0, str(ROOT))
import wfcommon


def _nodes(rework_val, carrier_type="agent", extra=None):
    n = {"id": "verdict", "type": carrier_type, "after": ["build"]}
    if carrier_type == "agent":
        n["goal"] = "judge"
    if rework_val is not None:
        n["rework"] = rework_val
    nodes = [{"id": "build", "type": "agent", "goal": "build it"}, n]
    return nodes + (extra or [])


def _defs(nodes):
    return [d for d in wfcommon.validate_graph_errors(nodes)
            if "rework" in str(d.get("field", "")) or "rework" in str(d.get("msg", ""))]


class ReworkAccept459(unittest.TestCase):
    def test_wellformed_accepted(self):
        self.assertEqual(_defs(_nodes({"to": "build", "max_iters": 3})), [])

    def test_non_agent_carrier_refused(self):
        self.assertTrue(_defs(_nodes({"to": "build"}, carrier_type="gate")))

    def test_unknown_target_refused(self):
        self.assertTrue(_defs(_nodes({"to": "ghost"})))

    def test_self_loop_refused(self):
        self.assertTrue(_defs(_nodes({"to": "verdict"})))

    def test_max_iters_bounds(self):
        for bad in (0, 9, "3", True, 2.5):
            self.assertTrue(_defs(_nodes({"to": "build", "max_iters": bad})), f"value {bad!r} accepted")

    def test_fanout_carrier_refused(self):
        nodes = _nodes({"to": "build"})
        nodes[1]["fanout"] = {"items": ["a"]}
        self.assertTrue(_defs(nodes))

    def test_refusal_clean_graph_none(self):
        self.assertIsNone(door._rework_refusal({"name": "x", "nodes": _nodes(None)}))

    def test_refusal_typed_names_carriers(self):
        out = door._rework_refusal({"name": "x", "nodes": _nodes({"to": "build"})})
        self.assertIsNotNone(out)
        self.assertEqual(out["error_type"], "engine_loop_not_wired")
        self.assertEqual(out["nodes"], ["verdict"])
        self.assertIn("zero writes", out["error"])
        self.assertIn("#459", out["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
