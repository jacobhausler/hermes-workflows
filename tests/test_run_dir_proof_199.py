#!/usr/bin/env python3
"""est-2ek.1.199 — durable run-dir proof in act_run + plugin-level orphaned-run status.

Postmortem (fb-fix run 20260927-082306-fb-fix-cef3acf6): a door launched via an
importlib import with a stub _CTX returned a run_id whose dir never landed under
the durable root (/home/hermes/.hermes/workflows) — neighbours intact, cause
unknown, the ledger loop slept 6h because the census only saw 'in_progress'.

Two plugin-level gates pin this run:

1. act_run durability proof: after the writes and the runner spawn, the door
   fsyncs what it wrote (files + the run dir + the runs root) and VERIFIES the
   run dir still exists under the resolved durable root BEFORE returning the
   run_id. Verification failure must RAISE, naming the attempted path — a
   phantom run_id is never handed back. (handle() turns the raise into the
   tool's loud error payload; act_run itself must not swallow it.)

2. orphaned-run status: a lane-ledger entry whose run dir does NOT exist on
   disk — the ledger's in-progress claim that the census could not see
   through — surfaces as state 'orphaned' from act_status(lane_key=...) and
   from the act_run dedupe row, instead of a forever-'pending' ghost.

RED on origin/main: (1) act_run returns a phantom run_id after the launch
path deletes the dir, and no fsync ever runs; (2) the missing-dir lane entry
reports state 'pending', never 'orphaned'. Stdlib only; no network; the spawn
is stubbed so nothing ever launches.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = {"name": "proof199", "nodes": [{"id": "x", "type": "echo", "output": {"ok": True}}]}


class RunDirProof199(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.root),
                                      "HERMES_HOME": str(self.root / "home")})
        env.start()
        self.addCleanup(env.stop)
        self.door = load("door199_" + self.id(), ROOT / "__init__.py")
        import wf_test_isolation as _iso71
        _iso71.install(self.door)
        self.spawns = []
        patch.object(self.door, "_spawn_runner",
                     side_effect=lambda r: self.spawns.append(r)).start()
        self.addCleanup(patch.stopall)

    # ---- 1. durability proof -------------------------------------------------
    def test_phantom_run_id_raises(self):
        # The phantom shape: the launch path leaves NO run dir (simulated by a
        # spawn that rmtree's it, standing for "wrote to a non-durable root /
        # the dir vanished"). act_run must raise with the attempted path, never
        # hand back a run_id.
        def killer(r):
            shutil.rmtree(r, ignore_errors=True)
            self.spawns.append(r)
        with patch.object(self.door, "_spawn_runner", side_effect=killer):
            with self.assertRaises(RuntimeError) as cm:
                self.door.act_run({"graph": G})
        msg = str(cm.exception)
        self.assertIn("run dir", msg.lower())
        # the attempted path is named loudly
        attempted = [x for x in msg.split() if "proof199" in x]
        self.assertTrue(attempted, msg)
        self.assertTrue(any(str(self.root) in x for x in attempted), msg)

    def test_happy_launch_fsyncs_and_proves(self):
        # A normal launch still returns its run_id (golden keys unchanged) AND
        # the durability proof really fsyncs: files, run dir, and the runs root.
        real_fsync = os.fsync
        fsynced = []
        def spy(fd):
            fsynced.append(os.fstat(fd))
            return real_fsync(fd)
        with patch.object(os, "fsync", side_effect=spy):
            out = self.door.act_run({"graph": G})
        rid = out["run_id"]
        r = self.root / rid
        self.assertEqual(
            {"run_id", "models", "routes", "hint", "card", "lifecycle_notice"},
            set(out))
        self.assertTrue((r / "graph.json").exists() and (r / "run.json").exists())
        self.assertTrue(fsynced, "no fsync calls — the durability proof is a no-op")
        # every fsynced inode must resolve to the run dir, one of its durable
        # files, or the runs root itself
        targets = []
        for st in fsynced:
            for cand in (self.root, r, r / "graph.json", r / "run.json",
                         r / "wake_protocol"):
                try:
                    cst = cand.stat()
                except OSError:
                    continue
                if cst.st_ino == st.st_ino and cst.st_dev == st.st_dev:
                    targets.append(cand)
                    break
        self.assertTrue(any(str(t) == str(self.root) for t in targets),
                        "runs root never fsynced")
        self.assertTrue(any(str(t).startswith(str(r)) for t in targets),
                        "run dir/files never fsynced")

    # ---- 2. orphaned-run status ----------------------------------------------
    def test_missing_run_dir_reports_orphaned(self):
        key = "lane199/orphan"
        a = self.door.act_run({"graph": G, "lane_key": key})
        rid = a["run_id"]
        # The ledger entry CLAIMS the run; the dir is gone (the census-blind state).
        shutil.rmtree(self.root / rid)
        row = self.door.act_status({"lane_key": key})
        self.assertEqual(row["run_id"], rid)
        self.assertEqual(row["state"], "orphaned", row)
        # dedupe row on a re-submit says the same thing, loudly
        again = self.door.act_run({"graph": G, "lane_key": key})
        self.assertTrue(again.get("deduped"), again)
        self.assertEqual(again.get("state"), "orphaned", again)

    def test_live_and_normal_lane_states_unchanged(self):
        # Byte-compat: a normal (non-orphan) lane row keeps the exact key set
        # and its 'pending'/'running' read-model values.
        key = "lane199/normal"
        a = self.door.act_run({"graph": G, "lane_key": key})
        row = self.door.act_status({"lane_key": key})
        self.assertEqual({"lane_key", "run_id", "state", "runner_live",
                          "unfinished", "needs_resume", "last_event_ts"}, set(row))
        self.assertNotEqual(row["state"], "orphaned")
        self.assertEqual(row["run_id"], a["run_id"])

    def test_stub_ctx_poisoned_root_is_a_named_refusal_not_a_phantom(self):
        # The suspect launch shape from the postmortem: a truthy stub _CTX whose
        # get_config can redirect settings.runs_root. If the configured durable
        # root cannot hold/keep the run dir, the door must refuse LOUDLY with
        # the attempted path — never return a run_id the estate census can't see.
        bogus = self.root / "gone-root"
        bogus.mkdir()
        class StubCtx:
            def get_config(self, key, default=None):
                if key == "runs_root":
                    return str(bogus)
                return default
        self.door._CTX = StubCtx()
        def killer(r):
            shutil.rmtree(r, ignore_errors=True)   # dir "never lands"
        with patch.object(self.door, "_spawn_runner", side_effect=killer):
            with self.assertRaises(RuntimeError) as cm:
                self.door.act_run({"graph": G})
        self.assertIn(str(bogus), str(cm.exception))
        self.door._CTX = None


if __name__ == "__main__":
    unittest.main(verbosity=2)
