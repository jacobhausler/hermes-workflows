#!/usr/bin/env python3
"""hw-sq1 — the joint peer-estate ruling (re-hashed at d9a53dc), two fixes to
the partial/precondition law:

  1. PRECONDITION RECORDS CARRY attempts:0 (ruling 3): a never-spawned,
     precondition-blocked victim is NOT a dead child. The record dict in
     _fail_precondition must carry attempts=0 so _dead_letter's
     rec.get("attempts") splits root cause from collateral (blocked victims:
     attempts=0, real deaths: attempts>0). status STAYS failed — the read-model
     fix, not a rename.
  2. PRODUCER-DECLARES RELEASE (ruling 2): a partial releases plain after-edges
     ONLY when its node declares answer-only work (shape recon/review, no
     repo:, no publishes:) AND its harvest committed an empty `remaining` tail
     with no blocking declared_status. Undeclared shape, a non-empty tail or a
     blocking declared status keep the plain edge BLOCKED — fb-fix-2dd8de73
     stands (test_partial_block_87.py must stay green; this test never weakens
     the block, it only opens the declared-and-complete gate).

Run: python3 tests/test_partial_release_hw-sq1.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

FAKE = str(ROOT / "tests" / "fake")
SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}},
          "required": ["result"]}


class SQ1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sq1-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.runs = self.home / "workflows"
        self.runs.mkdir()
        (self.home / "fake.log").write_text("")

    def mk(self, run_id, nodes, **meta):
        r = self.runs / run_id
        (r / "nodes").mkdir(parents=True)
        (r / "gates").mkdir()
        (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
        m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}
        m.update(meta)
        (r / "run.json").write_text(json.dumps(m))
        return r

    def wf(self, run_id, extra_env=None, timeout=120):
        env = dict(os.environ, HERMES_HOME=str(self.home),
                   WF_RUNS_ROOT=str(self.runs),
                   FAKE_LOG=str(self.home / "fake.log"),
                   **(extra_env or {}))
        return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                              env=env, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()

    def rec(self, r, nid):
        return json.loads((r / "nodes" / f"{nid}.json").read_text())

    def spawns_of(self, run_id):
        return len(list((self.runs / run_id / "logs").glob("*.log")))

    # ---- R1: declared answer-only partial + empty tail releases the plain edge
    def test_R1_declared_partial_releases_plain_edge(self):
        r = self.mk("sq1-r1", [
            {"id": "scan", "type": "agent", "goal": "DIETEST r1", "schema": SCHEMA,
             "shape": "recon"},
            {"id": "use", "type": "agent", "after": ["scan"], "goal": "USE r1",
             "schema": SCHEMA}])
        out = self.wf("sq1-r1", {"FAKE_MODE": "die_after_json"})
        scan, use = self.rec(r, "scan"), self.rec(r, "use")
        self.assertEqual(scan["status"], "partial")           # status stays partial (law: release, not rename)
        self.assertEqual(use["status"], "done", str(use))     # released, spawned off the harvest
        self.assertEqual(self.spawns_of("sq1-r1"), 2)
        prompt = next((r / "logs").glob("use.a*.prompt.md")).read_text()
        self.assertIn("harvested", prompt)                    # the harvest rode ## Inputs
        self.assertTrue(out.startswith("WORKFLOW_DONE"), out)
        st = wfcommon.run_state(r)                            # read model agrees with the runner
        self.assertEqual(st["status"], "done")

    # ---- R2: undeclared shape keeps blocking + the blocked record says attempts:0
    def test_R2_undeclared_blocks_and_record_carries_attempts_zero(self):
        r = self.mk("sq1-r2", [
            {"id": "scan", "type": "agent", "goal": "DIETEST r2", "schema": SCHEMA},
            {"id": "use", "type": "agent", "after": ["scan"], "goal": "USE r2",
             "schema": SCHEMA}])
        out = self.wf("sq1-r2", {"FAKE_MODE": "die_after_json"})
        use = self.rec(r, "use")
        self.assertEqual(use["status"], "failed")
        self.assertEqual(use["error_class"], "precondition")
        self.assertEqual(use["error"], "blocked_by_partial_ancestor: scan")
        self.assertEqual(self.spawns_of("sq1-r2"), 1, "use must NEVER spawn")
        self.assertTrue(out.startswith("WORKFLOW_FAILED"), out)
        # ruling 3: blocked victim reads attempts=0, the real death reads attempts>0
        self.assertEqual(use.get("attempts"), 0, str(use))
        self.assertGreater(self.rec(r, "scan").get("attempts") or 0, 0)

    # ---- R3: declared shape but NON-EMPTY remaining tail -> still blocked
    def test_R3_nonempty_tail_still_blocks(self):
        r = self.mk("sq1-r3", [
            {"id": "scan", "type": "agent", "goal": "DIETEST r3", "schema": SCHEMA,
             "shape": "recon"},
            {"id": "use", "type": "agent", "after": ["scan"], "goal": "USE r3",
             "schema": SCHEMA}])
        out = self.wf("sq1-r3", {"FAKE_MODE": "partial_remaining"})
        self.assertEqual(self.rec(r, "scan")["status"], "partial")
        self.assertEqual(self.rec(r, "use")["status"], "failed")
        self.assertEqual(self.rec(r, "use")["error"], "blocked_by_partial_ancestor: scan")
        self.assertEqual(self.spawns_of("sq1-r3"), 1)
        self.assertTrue(out.startswith("WORKFLOW_FAILED"), out)

    # ---- R4: empty tail but declared terminal status BLOCKED -> still blocked
    def test_R4_declared_blocked_status_still_blocks(self):
        r = self.mk("sq1-r4", [
            {"id": "scan", "type": "agent", "goal": "DIETEST r4", "schema": SCHEMA,
             "shape": "review"},
            {"id": "use", "type": "agent", "after": ["scan"], "goal": "USE r4",
             "schema": SCHEMA}])
        out = self.wf("sq1-r4", {"FAKE_MODE": "die_after_json_blocked"})
        self.assertEqual(self.rec(r, "scan")["status"], "partial")
        self.assertEqual(self.rec(r, "use")["status"], "failed")
        self.assertEqual(self.rec(r, "use")["error"], "blocked_by_partial_ancestor: scan")
        self.assertEqual(self.spawns_of("sq1-r4"), 1)
        self.assertTrue(out.startswith("WORKFLOW_FAILED"), out)

    # ---- R5: the predicate itself — repo:/publishes:/shape/tail fail-closed
    def test_R5_predicate_grammar(self):
        def node(**over):
            n = {"id": "scan", "type": "agent", "goal": "g", "shape": "recon"}
            n.update(over)
            return n
        states = {"scan": "partial", "use": "pending"}
        rec_ok = {"status": "partial", "remaining": [], "harvest": {"declared_status": None}}
        ok = wfcommon.released_partials([node()], states, {"scan": rec_ok})
        self.assertEqual(ok, {"scan"})
        self.assertEqual(wfcommon.released_partials([node(shape="review")], states,
                                                    {"scan": rec_ok}), {"scan"})
        for over in ({"shape": "build"}, {"shape": None}, {"repo": "/tmp/lane"},
                     {"publishes": True}):
            n = node(**over)
            if over.get("shape") is None:
                n.pop("shape")
            self.assertEqual(wfcommon.released_partials([n], states, {"scan": rec_ok}),
                             set(), f"must not release: {over}")
        self.assertEqual(wfcommon.released_partials([node()], states,
                         {"scan": dict(rec_ok, remaining=["x"])}), set(), "tail not empty")
        self.assertEqual(wfcommon.released_partials([node()], states,
                         {"scan": dict(rec_ok, error_class="left_live_descendants")}),
                         set(), "#61: work outlived the answer — never release over a live tree")
        self.assertEqual(wfcommon.released_partials([node()], states,
                         {"scan": {k: v for k, v in rec_ok.items() if k != "remaining"}}),
                         set(), "missing tail reads blocking (fail-closed)")
        self.assertEqual(wfcommon.released_partials([node()], states,
                         {"scan": dict(rec_ok, harvest={"declared_status": "BLOCKED"})}),
                         set(), "blocking declared status")
        self.assertEqual(wfcommon.released_partials([node()], states,
                         {"scan": dict(rec_ok, harvest={"declared_status": "done"})}),
                         {"scan"}, "non-blocking declared status")
        self.assertEqual(wfcommon.released_partials([node()], states, {}), set(),
                         "no record = no release")
        # a done ancestor is not a partial — nothing to release
        self.assertEqual(wfcommon.released_partials([node()], {"scan": "done", "use": "pending"},
                                                    {"scan": rec_ok}), set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
