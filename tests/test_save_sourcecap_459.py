#!/usr/bin/env python3
"""#459 G1 (est-rza3t): save `source` cap 200 -> 512.

The factory attribution law (repo URL + commit sha + source path) cannot ride
a 200-char line — the pstack conversion demonstrated pack graphs needing 248
and 261 chars. The cap exists to bound the annotation, not to strangle it;
512 keeps the bound visible. Contracts pinned here:
  (1) 512-char source SAVES and rides verbatim into provenance.source;
  (2) 513-char source is REFUSED with the error naming 512;
  (3) the model-reachable schema description says <=512 (docs and door agree).

Standalone script (no pytest):
  python3 tests/test_save_sourcecap_459.py
"""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_459", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso; _iso.install(door)

G = {"name": "cap459", "nodes": [{"id": "x", "type": "echo", "output": {"ok": True}}]}


class SourceCap459(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root)})
        env.start()
        self.addCleanup(env.stop)

    def _save(self, source):
        return door.act_save({"name": "cap459", "source": source,
                              "graph": json.loads(json.dumps(G))})

    def test_512_rides_verbatim(self):
        src = "u" * 512
        out = self._save(src)
        self.assertNotIn("error", out, out)
        row = json.loads((self.root / "library" / "cap459.json").read_text())
        prov = row.get("provenance") or (row.get("graph") or {}).get("provenance") or {}
        self.assertEqual(prov.get("source"), src)

    def test_513_refused_naming_512(self):
        out = self._save("u" * 513)
        self.assertIn("error", out)
        self.assertIn("512", out["error"])
        self.assertFalse((self.root / "library" / "cap459.json").exists())

    def test_schema_description_agrees(self):
        schema = door.WORKFLOW_SCHEMA["parameters"]["properties"]["source"]["description"]
        self.assertIn("<=512 chars", schema)
        self.assertNotIn("<=200 chars", schema)


if __name__ == "__main__":
    unittest.main(verbosity=2)
