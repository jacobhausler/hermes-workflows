#!/usr/bin/env python3
"""est-yq2xq: marker-gated creation-override flag strip on the child spawn argv.

The gateway's frozen-route resume policy refuses creation overrides under
`--continue <skey> --create-if-missing` (every child dies rc=2 — est-yq2xq
class). The runner strips the frozen-route flag PAIRS (--max-turns,
--run-budget, --reasoning, -t, -m, --provider) while the feature is active:
env WF_OMIT_POLICY_FLAGS=1 OR the marker file
<hermes_home>/workflows/omit-policy-flags.on. Two proofs here:

  (1) the factored helper _omit_policy_flags_if_enabled: byte-identical argv
      when disabled, exact pair-strip when enabled (marker OR env; each flag
      consumes its own value token);
  (2) the wiring end-to-end through run_child with a fake hermes bin: the
      CAPTURED child argv carries the flags off a stock spawn and never
      carries them while WF_OMIT_POLICY_FLAGS=1, with the deterministic
      skey join (--continue/--create-if-missing) surviving in both.

Harness shape mirrors tests/test_11_runner_profile.py.
"""
import importlib.util
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("runner_yq2x", ROOT / "wf.py")
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)

# One of every frozen-route pair, in builder order, plus the tokens that must
# ALWAYS survive (route, join, I/O contract).
ARGV = ["hermes", "-p", "launcher", "chat", "--query-file", "/tmp/p.md",
        "--oneshot", "-Q", "--source", "workflow",
        "--continue", "wf:r1:child#a0", "--create-if-missing",
        "-m", "test-model", "--provider", "test-provider", "--reasoning", "high",
        "-t", "terminal,-file", "--max-turns", "65", "--run-budget", "300"]
STRIPPED = ["hermes", "-p", "launcher", "chat", "--query-file", "/tmp/p.md",
            "--oneshot", "-Q", "--source", "workflow",
            "--continue", "wf:r1:child#a0", "--create-if-missing"]


class HelperStrip(unittest.TestCase):
    def test_disabled_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)  # marker absent
            for env in ({}, {"WF_OMIT_POLICY_FLAGS": "0"},
                        {"WF_OMIT_POLICY_FLAGS": "true"}):
                self.assertEqual(wf._omit_policy_flags_if_enabled(ARGV, home=home, env=env),
                                 ARGV, f"env={env} must be byte-identical")

    def test_marker_strips_pairs(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            (home / "workflows").mkdir()
            (home / "workflows" / "omit-policy-flags.on").write_text("")
            self.assertEqual(wf._omit_policy_flags_if_enabled(ARGV, home=home, env={}),
                             STRIPPED)

    def test_env_enables_without_marker(self):
        with tempfile.TemporaryDirectory() as td:
            got = wf._omit_policy_flags_if_enabled(
                ARGV, home=Path(td), env={"WF_OMIT_POLICY_FLAGS": "1"})
            self.assertEqual(got, STRIPPED)

    def test_empty_argv_enabled_is_stable(self):
        # a spawn with zero policy flags loses nothing when the strip is on
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                wf._omit_policy_flags_if_enabled(STRIPPED, home=Path(td),
                                                 env={"WF_OMIT_POLICY_FLAGS": "1"}),
                STRIPPED)


class SpawnWiring(unittest.TestCase):
    """run_child captures its final argv through a fake hermes bin."""

    def _capture(self, run_root, extra_env):
        home = run_root / "profiles" / "launcher"
        home.mkdir(parents=True)
        run = run_root / "runs" / "r1"
        (run / "nodes").mkdir(parents=True)
        # #483: under an ARMED strip a node with an effective require_route now
        # refuses before the child starts (route_inexpressible) — the lane that
        # still launches through the strip is an author opted into the seat
        # default. The refusal itself is pinned by tests/test_spawn_expressibility_483.py E1.
        node = {"id": "child", "type": "agent", "goal": "ok", "model": "test-model",
                "provider": "test-provider", "require_route": False,
                "max_turns": 65, "run_budget": 300}
        (run / "graph.json").write_text(json.dumps({"nodes": [node]}))
        binpath = run_root / "hermes"
        binpath.write_text("#!/usr/bin/python3\n"
                           "import json,os,sys\nfrom pathlib import Path\n"
                           "a=sys.argv[1:]\n"
                           "Path(os.environ['HERMES_WF_RUN_DIR'],'capture.json')"
                           ".write_text(json.dumps({'argv':a,'env':dict(os.environ)}))\n"
                           "print('```json\\n{}\\n```')\n")
        binpath.chmod(0o755)
        meta = {"_run": run, "hermes_bin": str(binpath), "_spawn_n": {},
                "_procs_lock": threading.Lock(), "_procs": {},
                "_stop": threading.Event(), "node_timeout": 10}
        with patch.dict(os.environ, dict({"HERMES_HOME": str(home),
                                         "WF_RUNS_ROOT": str(run_root / "runs"),
                                         "HERMES_WRITE_SAFE_ROOT": str(run_root / "safe")},
                                        **extra_env), clear=False):
            if "WF_OMIT_POLICY_FLAGS" not in extra_env:
                os.environ.pop("WF_OMIT_POLICY_FLAGS", None)  # ambient-proof the stock case
            r = wf.run_child(meta, node, {"child": node}, "ok", "", None,
                             skey="wf:r1:child", attempt=0)
        self.assertEqual(r["status"], "done", r)
        return json.loads((run / "capture.json").read_text())["argv"]

    def test_stock_spawn_keeps_flags(self):
        with tempfile.TemporaryDirectory() as td:
            argv = self._capture(Path(td), {})
            for flag in ("-m", "--provider", "--max-turns", "--run-budget"):
                self.assertIn(flag, argv)
            self.assertIn("--continue", argv)
            self.assertIn("--create-if-missing", argv)

    def test_enabled_spawn_never_carries_frozen_route_flags(self):
        with tempfile.TemporaryDirectory() as td:
            argv = self._capture(Path(td), {"WF_OMIT_POLICY_FLAGS": "1"})
            for flag in ("-m", "--provider", "--reasoning", "-t",
                         "--max-turns", "--run-budget"):
                self.assertNotIn(flag, argv)
            self.assertIn("--continue", argv)   # the join survives
            self.assertIn("--create-if-missing", argv)


if __name__ == "__main__":
    unittest.main(verbosity=2)
