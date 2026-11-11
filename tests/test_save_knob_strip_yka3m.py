#!/usr/bin/env python3
"""est-yka3m (PR#500 shelf-leak residual): save(run_id) must not shelf
arg-channel concurrency widths.

#498 merged launch-time concurrency args into the graph channel BEFORE the
run-dir write, so the run-dir graph.json carries them raw and a re-shelve
(the documented normal flow, #70) silently gained widths the author never
wrote: the shelf row poisoned every `from=<entry>` replay (silent inherit)
and later `from=` + concurrency launches refused as co-declaration naming a
forged key. The door now stamps the arg-channel keys into run.json
(`knob_arg_keys`) and save(run_id) strips exactly those keys — shelf bytes
ride the author graph (launch-only law #580 B1: per-run widths live at the
launch, never on the shelf). Author-written graph-key widths are untouched;
pre-stamp run dirs keep their bytes verbatim (no retroactive strip); an
amend drops the stamp because it replaces the bytes the stamp described.

Run: env -u WF_RUNS_ROOT -u HERMES_HOME PYTHONPATH=/opt/hermes
     /opt/hermes/.venv/bin/python tests/test_save_knob_strip_yka3m.py
"""
import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_yka3m", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)

BASE = {"name": "yka3m", "nodes": [{"id": "a", "type": "echo", "output": 1}]}


class Owner:
    def __init__(self):
        self.settings = {}

    def get_config(self, key, default=None):
        return self.settings.get(key, default)


class SaveKnobStripYka3m(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="wf-yka3m-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "home").mkdir()
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root / "runs"),
                                      "HERMES_HOME": str(self.root / "home")})
        env.start()
        self.addCleanup(env.stop)
        wf_test_isolation.install(door)
        ctx = patch.object(door, "_CTX", Owner())
        ctx.start()
        self.addCleanup(ctx.stop)
        spawn = patch.object(door, "_spawn_runner")
        spawn.start()
        self.addCleanup(spawn.stop)
        resume = patch.object(door, "_resume_after_action",
                              lambda r, consumed=None: "live")
        resume.start()
        self.addCleanup(resume.stop)

    # -- helpers ----------------------------------------------------------
    def launch(self, **kwargs):
        out = door.act_run({"graph": copy.deepcopy(BASE), **kwargs})
        self.assertIn("run_id", out, out)
        return out["run_id"]

    def run_dir(self, rid):
        return self.root / "runs" / rid

    def meta(self, rid):
        return json.loads((self.run_dir(rid) / "run.json").read_text())

    def graph_json(self, rid):
        return json.loads((self.run_dir(rid) / "graph.json").read_text())

    def shelf(self, name):
        row = json.loads((self.root / "runs" / "library" / f"{name}.json").read_text())
        return row.get("graph", row)   # envelope or bare — the graph either way

    def strip_author_meta(self, rid):
        """Simulate a pre-fix (unstamped) run dir: drop the stamp from a
        launch that carried arg-channel widths."""
        m = self.meta(rid)
        m.pop("knob_arg_keys", None)
        (self.run_dir(rid) / "run.json").write_text(json.dumps(m))

    # -- T1: the leak leg — arg-channel run, stamped, stripped on re-shelve
    def test_T1_arg_channel_widths_stripped_shelf_equals_author_bytes(self):
        rid = self.launch(concurrency=6, item_concurrency=10)
        # launch legs (the #498 contract, unchanged): raw rides graph.json,
        # clamped truth rides run.json (owner caps unset -> defaults 4/8).
        self.assertEqual(self.graph_json(rid).get("concurrency"), 6)
        self.assertEqual(self.graph_json(rid).get("item_concurrency"), 10)
        meta = self.meta(rid)
        self.assertEqual((meta["concurrency"], meta["item_concurrency"]), (4, 8))
        self.assertEqual(meta["knob_arg_keys"], ["concurrency", "item_concurrency"])
        out = door.act_save({"run_id": rid, "name": "yka3m-arg"})
        self.assertNotIn("error", out, out)
        self.assertEqual(out.get("knobs_stripped"), ["concurrency", "item_concurrency"])
        shelf_g = self.shelf("yka3m-arg")
        expected = {k: v for k, v in self.graph_json(rid).items()
                    if k not in ("concurrency", "item_concurrency")}
        expected["name"] = "yka3m-arg"   # act_save forces the entry stem, by design
        shelf_g = {k: v for k, v in shelf_g.items() if k != "provenance"}
        self.assertEqual(shelf_g, expected)   # shelf bytes == author bytes
        self.assertNotIn("concurrency", shelf_g)

    # -- T2: author-written graph-key width is author bytes, never stripped
    def test_T2_author_key_width_rides_the_shelf(self):
        rid = self.launch(graph={**copy.deepcopy(BASE), "concurrency": 2})
        meta = self.meta(rid)
        self.assertEqual(meta["concurrency"], 2)
        self.assertNotIn("knob_arg_keys", meta)   # no args -> legacy bytes
        out = door.act_save({"run_id": rid, "name": "yka3m-author"})
        self.assertNotIn("error", out, out)
        self.assertNotIn("knobs_stripped", out)   # clean save: response bytes unchanged
        self.assertEqual(self.shelf("yka3m-author").get("concurrency"), 2)

    # -- T3: pre-fix (unstamped) run dirs keep bytes verbatim
    def test_T3_legacy_unstamped_run_dir_untouched(self):
        rid = self.launch(concurrency=6)
        self.strip_author_meta(rid)
        out = door.act_save({"run_id": rid, "name": "yka3m-legacy"})
        self.assertNotIn("error", out, out)
        self.assertNotIn("knobs_stripped", out)
        self.assertEqual(self.shelf("yka3m-legacy").get("concurrency"), 6)

    # -- T4: acceptance leg — re-shelved entry + width arg launches clean
    def test_T4_reshelve_unblocks_from_plus_width_arg(self):
        rid = self.launch(concurrency=6)
        door.act_save({"run_id": rid, "name": "yka3m-arg"})
        out = door.act_run({"from": "yka3m-arg", "concurrency": 3})
        self.assertNotIn("error", out, out)   # pre-fix: co-declaration refusal
        self.assertIn("run_id", out, out)
        self.assertEqual(self.meta(out["run_id"])["concurrency"], 3)

    # -- T5: an amend replaces the stamped bytes -> the stamp dies with them
    def test_T5_amend_drops_stamp_amended_width_is_author_truth(self):
        rid = self.launch(concurrency=6)
        out = door.act_amend({"run_id": rid,
                              "graph": {**copy.deepcopy(BASE), "concurrency": 3}})
        self.assertNotIn("error", out, out)
        self.assertNotIn("knob_arg_keys", self.meta(rid))   # set-or-remove
        self.assertEqual(self.graph_json(rid).get("concurrency"), 3)
        out = door.act_save({"run_id": rid, "name": "yka3m-amended"})
        self.assertNotIn("error", out, out)
        self.assertNotIn("knobs_stripped", out)
        self.assertEqual(self.shelf("yka3m-amended").get("concurrency"), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
