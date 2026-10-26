#!/usr/bin/env python3
"""#51 (issue #51): the curated public `library/general/` starter set and the
door's packaged fallback.

Contracts pinned here:
  (1) PACKAGED SET WELL-FORMED: every packaged general/ entry is an envelope
      {meta:{description,tags[,params]}, graph}, loads through the shared
      normalizer, validates through the door's own validator, routes EVERY
      agent via a tier key (worker|manager) — no literal model ids — and its
      declared meta.params exactly cover its live {run.KEY} refs.
  (2) EXEMPLARS: one graph carries the seed contract in its description
      (issue-triage), one parks on a machine wait gate whose until_argv is
      fixed argv containing no {run.*} placeholder (report-and-verify), one
      encodes the 8 KB per-parent input cap as file paths with the schema
      pinning the path key on both sides (fan-out-audit-census).
  (3) RESOLUTION ORDER for `general/<name>`: runs_root library FIRST (a
      shelved shadow wins on both resolve and launch), packaged fallback when
      every private root misses (launch works from a cold shelf), unknown
      names keep the typed nudge. The packaged directory is read-only: save
      never writes there and a shadow still wins.

Standalone script (no pytest): PYTHONPATH=<repo> python3 tests/test_door_general_51.py
"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_51", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso51; _iso51.install(door)

PACKAGED = ["pr-review-light", "issue-triage", "test-first-feature-slice",
            "fan-out-audit-census", "report-and-verify", "queue-executor"]
TIERS = {"worker": "test-fast-model", "manager": "test-strong-model"}

SEED = {"work_queue": "a test queue", "decision_rule": "urgent when the pager rings",
        "owner_notify": "reply in channel"}


class Ctx:
    def __init__(self, tiers): self.t = tiers
    def get_config(self, k, d=None): return self.t if k == "models" else d


def entry(name):
    p = door._packaged_general_root() / f"{name}.json"
    return door._common.library_entry(json.loads(p.read_text(encoding="utf-8")))


class DoorGeneral51(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root),
                                      "HERMES_HOME": str(self.root / "home")})
        env.start()
        self.addCleanup(env.stop)
        for k in ("HERMES_WF_STEER_FILE", "HERMES_WF_STEER_CURSOR", "HERMES_WF_STEER_HWM",
                  "HERMES_WF_STEER_NODE", "HERMES_WF_STEER_SPAWN", "HERMES_WF_RUN_DIR",
                  "HERMES_WF_RUN_ID"):
            os.environ.pop(k, None)
        self.ctx = patch.object(door, "_CTX", Ctx(dict(TIERS)))
        self.ctx.start()
        self.addCleanup(self.ctx.stop)
        self.spawns = []
        spawn = patch.object(door, "_spawn_runner", side_effect=lambda r: self.spawns.append(r))
        spawn.start()
        self.addCleanup(spawn.stop)

    # ---------------- (1) the packaged set is well-formed ----------------

    def test_packaged_dir_exists_with_at_least_five_entries(self):
        files = sorted(p.stem for p in door._packaged_general_root().glob("*.json"))
        self.assertGreaterEqual(len(files), 5)
        self.assertEqual(sorted(PACKAGED), sorted(files))

    def test_every_entry_envelope_tags_and_validation(self):
        for name in PACKAGED:
            e = entry(name)
            self.assertIn("graph", e, f"{name}: {e.get('invalid')}")
            self.assertTrue(e["envelope"], f"{name}: starter entries ship the envelope")
            self.assertIsInstance(e["description"], str)
            self.assertTrue(e["description"].strip())
            self.assertLessEqual(len(e["description"]), door.DESC_MAX)
            norm, err = door._norm_tags(e["tags"])
            self.assertIsNone(err, f"{name}: {err}")
            self.assertGreaterEqual(len(norm), 1)
            graph = door._common.apply_graph_defaults(dict(e["graph"]))
            bad = door._validation_error(graph)
            self.assertIsNone(bad, f"{name}: {bad}")

    def test_models_route_via_tiers_only(self):
        for name in PACKAGED:
            for n in entry(name)["graph"]["nodes"]:
                if n.get("type") == "agent":
                    self.assertIn(n.get("model"), ("worker", "manager"),
                                  f"{name}/{n['id']}: every agent names a TIER key as its model —"
                                  " never a vendor id, never a bare unset")
                    self.assertNotIn("provider", n)
                    self.assertNotIn("tier", n)         # the resolver's stamp, not author-written

    def test_declared_params_cover_the_live_refs(self):
        for name in PACKAGED:
            e = entry(name)
            contract = door._common.run_context_contract(e["graph"], e["meta"].get("params"))
            self.assertEqual([], contract["missing"], f"{name}: refs without a declaration")
            self.assertEqual([], contract["dead"], f"{name}: declarations for dead refs")

    # ---------------- (2) the three exemplars ----------------

    def test_seed_contract_exemplar(self):
        e = entry("issue-triage")
        desc = e["graph"]["description"]
        text = json.dumps(e["graph"])
        for key in ("work_queue", "decision_rule", "owner_notify"):
            self.assertIn(key, desc)                          # the key contract is IN the description
            self.assertIn(f"{{run.{key}}}", text)             # and rides as a live ref
        self.assertIn("SEED CONTRACT", desc)
        self.assertEqual(["decision_rule", "owner_notify", "work_queue"],
                         door._common.run_context_contract(e["graph"], e["meta"]["params"])["refs"])

    def test_machine_wait_gate_exemplar(self):
        gates = [n for n in entry("report-and-verify")["graph"]["nodes"] if n.get("wait")]
        self.assertEqual(1, len(gates))
        w = gates[0]["wait"]
        argv = w["until_argv"]
        self.assertIsInstance(argv, list) and self.assertTrue(argv)
        self.assertTrue(all(isinstance(a, str) for a in argv))
        self.assertTrue(argv[0].startswith("/"), "fixed argv: absolute program, never a shell")
        for a in argv:
            self.assertNotIn("{run.", a)          # argv is never rendered — exemplar law
        self.assertIsInstance(w["every_s"], int) and self.assertGreater(w["every_s"], 0)
        self.assertIsInstance(w["timeout_s"], int) and self.assertGreater(w["timeout_s"], 0)
        self.assertIn("failure not approval", entry("report-and-verify")["graph"]["description"].lower())

    def test_eight_k_cap_exemplar(self):
        g = entry("fan-out-audit-census")["graph"]
        self.assertIn("8 KB", g["description"])
        roster = next(n for n in g["nodes"] if n["id"] == "census")
        items = roster["schema"]["properties"]["items"]["items"]
        self.assertIn("path", items["required"])           # roster schema pins the path key
        self.assertNotIn("content", items["properties"])   # nothing to overflow the cap
        lane = next(n for n in g["nodes"] if n.get("fanout"))
        self.assertIn("{item.path}", lane["fanout"]["goal"])
        self.assertEqual(["path", "finding", "pass"], lane["fanout"]["schema"]["required"])

    # ---------------- (3) resolution order + packaged fallback ----------------

    def test_packaged_fallback_launches_from_a_cold_shelf(self):
        p = door._lib_read("general/report-and-verify")
        self.assertEqual(door._packaged_general_root() / "report-and-verify.json", p)
        started = door.act_run({"from": "general/report-and-verify"})
        self.assertIn("run_id", started), started
        baked = json.loads((door.run_dir(started["run_id"]) / "graph.json").read_text())
        self.assertEqual(["prepare", "await-report", "verify"], [n["id"] for n in baked["nodes"]])
        self.assertEqual("test-fast-model", baked["nodes"][0]["model"])   # tier baked at the door
        self.assertEqual("worker", baked["nodes"][0]["tier"])

    def test_runs_root_library_wins_over_packaged(self):
        shadow = door.library_root() / "general" / "report-and-verify.json"
        shadow.parent.mkdir(parents=True)
        shadow.write_text(json.dumps({"name": "report-and-verify",
                                      "nodes": [{"id": "sentinel", "type": "echo", "output": 1}]}))
        p = door._lib_read("general/report-and-verify")
        self.assertEqual(shadow, p)
        started = door.act_run({"from": "general/report-and-verify"})
        baked = json.loads((door.run_dir(started["run_id"]) / "graph.json").read_text())
        self.assertEqual(["sentinel"], [n["id"] for n in baked["nodes"]])

    def test_packaged_name_replays_with_its_prefix(self):
        p = door._lib_read("general/issue-triage")
        self.assertEqual("general/issue-triage", door._lib_rel_name(p))

    def test_seed_contract_enforced_through_the_door(self):
        refused = door.act_run({"from": "general/issue-triage"})
        self.assertIn("error", refused)                      # unbound refs refuse before write
        self.assertEqual([], self.spawns)
        started = door.act_run({"from": "general/issue-triage", "run_context": dict(SEED)})
        self.assertIn("run_id", started)
        baked = json.loads((door.run_dir(started["run_id"]) / "graph.json").read_text())
        texts = json.dumps([door._common._include_texts(n) for n in baked["nodes"]])
        self.assertNotIn("{run.", texts)                     # every node-surface ref rendered
        for v in SEED.values():
            self.assertIn(v, texts)                          # seeds landed in prompts

    def test_unknown_general_name_keeps_the_typed_nudge(self):
        r = door.act_run({"from": "general/report-and-verifed"})
        self.assertEqual("library_not_found", r.get("error_class"))
        self.assertIn("no library graph", r.get("error", ""))

    def test_save_never_writes_the_packaged_dir(self):
        before = sorted(os.listdir(door._packaged_general_root()))
        g = {"name": "starter", "nodes": [{"id": "x", "type": "echo", "output": 1}]}
        r = door.act_save({"graph": g, "name": "general/report-and-verify"})
        self.assertEqual("general/report-and-verify", r.get("saved"))
        self.assertEqual(before, sorted(os.listdir(door._packaged_general_root())))
        self.assertEqual(door.library_root() / "general" / "report-and-verify.json",
                         door._lib_read("general/report-and-verify"))   # the shadow wins


if __name__ == "__main__":
    unittest.main(verbosity=2)
