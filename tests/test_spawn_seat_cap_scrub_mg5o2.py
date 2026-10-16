#!/usr/bin/env python3
"""est-mg5o2 (spawn half) — the seat cap is AUTHORITATIVE AT SPAWN: a stale
inherited WORKFLOW_MAX_SEATS must lose to the fresh .env read in the child.

Measured defect (2026-10-11 owner squad launch): the estate pool
.seats held 6/12 at an 8-squad launch despite WORKFLOW_MAX_SEATS=12 in .env.
Mechanism: wf._seat_cap_from_env_files (est-gxjh6) re-reads .env fresh, BUT
the runner spawns child hermes CLI processes with dict(os.environ, ...), so a
gateway that booted before the key existed passes a stale inherited value to
every nested child — and seat_max_seats precedence (env > .env) makes the
child arbitrate against the STALE inheritance instead of the fresh file.
Fix contract (wf.py spawn seam): an env-file value OVERWRITES the inherited
key; with no env-file value the key is STRIPPED so the child resolves fresh
(config workflows.max_seats / SEATS_DEFAULT); the local-disable sentinel "0"
keeps riding (est-2ek.1.856: a local disable, never an arbiter).

Process-local precedence is deliberately UNCHANGED (gxjh6 law, locked by
test_seat_cap_dotenv_gxjh6 (4): an exported env beats .env for the process
that exported it). This regression locks only what rides the spawn hop.

Every case drives the real runner (wf.py run) against a stub hermes bin that
records its OWN WORKFLOW_MAX_SEATS at entry — the exact inheritance channel
the row measured, not an in-process call.

Run: cd tests && python3 test_spawn_seat_cap_scrub_mg5o2.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(os.environ.get('WF_TEST_BUILD') or Path(__file__).resolve().parents[1])

STUB = r'''
import os, sys
args = sys.argv[1:]
if "--query-file" in args:
    open(r"__PROBE__", "w").write(os.environ.get("WORKFLOW_MAX_SEATS", "<absent>"))
    print("```json\n{\"result\":\"ok\"}\n```", flush=True)
sys.exit(0)
'''

ABSENT = "<absent>"


class SpawnSeatCapScrub(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wf-mg5o2-scrub-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.home = self.tmp / "home"
        self.runs = self.tmp / "runs"
        self.home.mkdir()
        self.probe = self.tmp / "child-env.txt"
        self.stub = self.tmp / "stub.py"
        self.stub.write_text("#!" + sys.executable + "\n" + STUB.replace("__PROBE__", str(self.probe)))
        self.stub.chmod(0o755)

    def base_env(self, inherited=None, profile=None):
        # Same channel hygiene as test_on_exit_129, plus a guaranteed-clean seat
        # key so each case decides the inheritance itself.
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("HERMES_WF_", "HERMES_SESSION_", "HERMES_UI_SESSION_"))
               and k not in ("WF_TEST_BUILD", "WORKFLOW_MAX_SEATS", "HERMES_PROFILE")}
        env.update(HERMES_HOME=str(self.home), WF_RUNS_ROOT=str(self.runs),
                   HERMES_WF_HERMES_BIN=str(self.stub))
        if profile:
            env["HERMES_PROFILE"] = profile
        if inherited is not None:
            env["WORKFLOW_MAX_SEATS"] = inherited
        return env

    def drive(self, env, rid="scrub"):
        r = self.runs / rid
        (r / "nodes").mkdir(parents=True)
        (r / "gates").mkdir()
        (r / "graph.json").write_text(json.dumps(
            {"name": rid, "nodes": [{"id": "work", "type": "agent",
                                     "goal": "SCRUB", "timeout": 15}]}))
        (r / "run.json").write_text(json.dumps(
            {"hermes_bin": str(self.stub), "concurrency": 1,
             "node_timeout": 15, "retry_backoff": [0], "retry_budget": 0}))
        if self.probe.exists():
            self.probe.unlink()
        p = subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", rid],
                           env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)  # never crash closed
        rec = json.loads((r / "nodes" / "work.json").read_text())
        self.assertEqual(rec.get("status"), "done", rec)       # node actually ran
        self.assertTrue(self.probe.exists(), "stub never spawned")
        return self.probe.read_text()

    # ---- (1) the named regression: stale inherited value LOSES to the .env read.
    def test_stale_inherited_loses_to_env_file(self):
        (self.home / ".env").write_text("WORKFLOW_MAX_SEATS=12\n")
        got = self.drive(self.base_env(inherited="6"))   # pre-.env boot shape
        self.assertEqual(got, "12", f"child saw {got!r}, expected the .env truth")

    # ---- (2) no env-file value: the inherited key is STRIPPED, so inheritance
    # ----      can never shadow the child's own fresh resolution.
    def test_no_env_file_strips_inheritance(self):
        got = self.drive(self.base_env(inherited="6"))
        self.assertEqual(got, ABSENT, f"child saw {got!r}, expected stripped")

    # ---- (3) the local-disable sentinel "0" KEEPS RIDING (never silently
    # ----      flipped from disabled to capped).
    def test_sentinel_zero_keeps_riding(self):
        got = self.drive(self.base_env(inherited="0"))
        self.assertEqual(got, "0", f"child saw {got!r}, expected sentinel")

    # ---- (4) key nowhere: child sees nothing (no-op scrub).
    def test_no_knob_anywhere(self):
        got = self.drive(self.base_env())
        self.assertEqual(got, ABSENT, f"child saw {got!r}, expected absent")

    # ---- (5) fresh knob lands through the spawn hop with nothing inherited.
    def test_env_file_lands_when_uninherited(self):
        (self.home / ".env").write_text("WORKFLOW_MAX_SEATS=9\n")
        got = self.drive(self.base_env())
        self.assertEqual(got, "9", f"child saw {got!r}, expected 9")

    # ---- (6) profile .env beats root .env across the hop (reader law preserved).
    def test_profile_env_wins_over_root_env(self):
        prof = self.home / "profiles" / "pro1"
        prof.mkdir(parents=True)
        (prof / ".env").write_text("WORKFLOW_MAX_SEATS=7\n")
        (self.home / ".env").write_text("WORKFLOW_MAX_SEATS=12\n")
        got = self.drive(self.base_env(inherited="6", profile="pro1"))
        self.assertEqual(got, "7", f"child saw {got!r}, expected profile 7")

    # ---- (7) parse shapes survive the hop: export prefix + inline comment.
    def test_export_prefix_parses_through_the_hop(self):
        (self.home / ".env").write_text("export WORKFLOW_MAX_SEATS=8 # fleet knob\n")
        got = self.drive(self.base_env(inherited="4"))
        self.assertEqual(got, "8", f"child saw {got!r}, expected 8")


if __name__ == "__main__":
    unittest.main(verbosity=2)
