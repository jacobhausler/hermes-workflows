#!/usr/bin/env python3
"""bd_2026-11-13-9i1 — the `start` verb, tested as BEHAVIOR at the tool seam.

Every check goes through door.handle(...) (the registered action surface), not
into the synthesizer's internals: what the caller sees is the contract.

  T1 happy path: one plain-language goal string -> one dispatch, a run dir
     whose graph.json carries ONE baked agent node (shape census baked in:
     review-phrased goal -> max_turns/timeout from SHAPE_PRESETS["review"],
     no model/provider key = the seat's own route), and a response carrying
     run_id + the one watch command.
  T2 misuse (no input): refusal payload carries the accepting example.
  T3 misuse (mapping without goal/nodes): same refusal.
  T4 fixed fan-out from a json path: the five-line spec's items_from reaches
     the door as fanout.items_from and the launch passes the full door.
  T5 idempotence: a second start of the same goal while the first run is
     unfinished DEDUPES on the derived lane key (no second spawn) and the
     team form yields <team>/start-<slug>.
  T6 the teach example parses (it is an accepting input by construction).
"""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_start", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso71_start; _iso71_start.install(door)  # pin settings.runs_root like every writer test


class StartVerb(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root),
                                      "HERMES_HOME": str(self.root / "home")})
        env.start()
        self.addCleanup(env.stop)
        self.spawns = []
        for target, val in (("_spawn_runner", lambda r: self.spawns.append(r)),
                            ("_route_liveness_ping", lambda routes: []),
                            ("_quota_refusal", lambda graph, routes: None)):
            p = patch.object(door, target, side_effect=val)
            p.start()
            self.addCleanup(p.stop)

    def handle(self, args):
        return json.loads(door.handle(args))

    def run_graph(self, rid):
        return json.loads((self.root / rid / "graph.json").read_text())

    # ---- T1 happy path: single node ------------------------------------------
    def test_t1_plain_goal_dispatches_one_node(self):
        res = self.handle({"action": "start",
                           "goal": "audit the requirements file and report every gap"})
        self.assertNotIn("error", res, res)
        rid = res["run_id"]
        self.assertEqual(res["watch"], f'workflow{{action:"status",run_id:{rid}}}')
        self.assertEqual(len(self.spawns), 1)
        g = self.run_graph(rid)
        self.assertEqual(g["name"], "audit-the-requirements-file-and-report-e")  # 40-char slug cap, measured
        self.assertEqual(len(g["nodes"]), 1)
        node = g["nodes"][0]
        self.assertEqual(node["id"], "work")
        self.assertEqual(node["type"], "agent")
        self.assertEqual(node["goal"], "audit the requirements file and report every gap")
        # shape census baked by the door: goal says "audit" -> review p95
        self.assertEqual(node["shape"], "review")
        import wfcommon
        self.assertEqual(node["max_turns"], wfcommon.SHAPE_PRESETS["review"]["max_turns"])
        self.assertEqual(node["timeout"], wfcommon.SHAPE_PRESETS["review"]["timeout"])
        # provider = the seat's own route: NO model/provider baked into the node
        self.assertNotIn("model", node)
        self.assertNotIn("provider", node)
        # the one status command really reads the run
        st = self.handle({"action": "status", "run_id": rid})
        self.assertEqual(st["run_id"], rid)
        # derived lane key (no team): start-<slug>
        entry, collision = door._lane_entry("start-audit-the-requirements-file-and-report-e")
        self.assertIsNone(collision)
        self.assertEqual(entry["run_id"], rid)

    # ---- T2 misuse: empty input ----------------------------------------------
    def test_t2_empty_input_prints_the_example(self):
        res = self.handle({"action": "start"})
        self.assertIn("error", res)
        self.assertIn("example", res)
        self.assertIn("goal:", res["example"])
        self.assertEqual(self.spawns, [])

    # ---- T3 misuse: a mapping without goal/nodes -----------------------------
    def test_t3_spec_without_content_prints_the_example(self):
        res = self.handle({"action": "start",
                           "goal": "name: weekly-digest\ndescription: tidies things\n"})
        self.assertIn("error", res)
        self.assertIn("example", res)
        self.assertEqual(self.spawns, [])

    # ---- T4 fixed fan-out from a json path ------------------------------------
    def test_t4_items_from_launches_through_the_door(self):
        y = ("name: charter-review\n"
             "nodes:\n"
             "  - {id: load, goal: 'Read charter.json; answer exactly {\"items\": [...]}'}\n"
             "  - {id: review, goal: 'Review this item', items_from: load.items, after: [load]}\n")
        res = self.handle({"action": "start", "goal": y, "team": "crew"})
        self.assertNotIn("error", res, res)
        g = self.run_graph(res["run_id"])
        byid = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(byid["review"]["fanout"], {"items_from": "load.items"})
        self.assertEqual(byid["review"]["after"], ["load"])
        self.assertEqual(len(self.spawns), 1)
        # team form: lane key <team>/start-<slug>, and the team stamp rides run.json
        entry, collision = door._lane_entry("crew/start-charter-review")
        self.assertIsNone(collision)
        self.assertEqual(entry["run_id"], res["run_id"])
        meta = json.loads((self.root / res["run_id"] / "run.json").read_text())
        self.assertEqual(meta.get("team"), "crew")

    # ---- T5 idempotence: double start dedupes on the derived key --------------
    def test_t5_double_start_dedupes(self):
        a = self.handle({"action": "start", "goal": "audit the lock file"})
        b = self.handle({"action": "start", "goal": "audit the lock file"})
        self.assertEqual(b["run_id"], a["run_id"])
        self.assertTrue(b.get("deduped"))
        self.assertEqual(len(self.spawns), 1)

    # ---- T6 the teach example is an accepting input ---------------------------
    def test_t6_example_round_trips(self):
        res = self.handle({"action": "start", "goal": door._wfstart.START_EXAMPLE})
        self.assertNotIn("error", res, res)
        g = self.run_graph(res["run_id"])
        self.assertEqual({n["id"] for n in g["nodes"]}, {"load", "review"})

    # ---- dry_run rides the door's own dry-run gates ----------------------------
    def test_dry_run_writes_nothing(self):
        res = self.handle({"action": "start", "goal": "audit the lock file",
                           "dry_run": True})
        self.assertTrue(res.get("ok") and res.get("dry_run"))
        self.assertNotIn("run_id", res)
        self.assertEqual(self.spawns, [])
        self.assertEqual(list(self.root.glob("audit-the-lock-file*")), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
