"""hw-sl0: a legacy `from:<name>` string in the graph slot must name its remedy.

The retired library pin `graph="from:<name>"` used to fall into json.loads and
get refused as "graph is not valid JSON: Expecting value...", which names the
wrong offender and no remedy. The door must instead say the replay lives on the
`from` argument and quote the pinned name back.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
HOME = tempfile.TemporaryDirectory(prefix="hw-sl0-home-", dir=ROOT)
os.environ["HERMES_HOME"] = HOME.name
os.environ["WF_RUNS_ROOT"] = str(Path(HOME.name) / "workflows")

import wf_test_isolation

spec = importlib.util.spec_from_file_location("hw_sl0_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
wf_test_isolation.install(door)


class LegacyFromPin(unittest.TestCase):
    def test_run_with_from_pin_names_the_from_argument_not_json(self):
        result = json.loads(door.handle({"action": "run", "graph": "from:my-graph"}))
        self.assertIn("error", result)
        self.assertNotIn("valid JSON", result["error"])
        self.assertIn("from", result["error"])
        self.assertIn('from="my-graph"', result.get("hint", ""))

    def test_garbage_string_still_refused_as_json(self):
        graph, bad = door._coerce_graph("{not json")
        self.assertIsNone(graph)
        self.assertIn("graph is not valid JSON", bad["error"])


if __name__ == "__main__":
    unittest.main()
