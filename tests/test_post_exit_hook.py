"""Regression for runner-owned roll-last post-exit handoff (est-w4qa)."""
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import post_exit_hook as hook

# All fixture writes stay on durable work ground, never the platform scratch dir.
FIXTURES = Path(os.environ.get("WF_HOOK_TEST_ROOT",
                               str(Path.home() / ".hermes" / "work" / "post-exit-hook-fixtures")))


class PostExitHookTest(unittest.TestCase):
    def setUp(self):
        FIXTURES.mkdir(parents=True, exist_ok=True)
        self.temp = TemporaryDirectory(dir=FIXTURES)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_dir = self.root / "workflows" / "roll-last-test"
        self.run_dir.mkdir(parents=True)
        self.outside = self.root / "work" / "hermes-nightly" / "roll-last-fixture"
        self.outside.mkdir(parents=True)
        self.script = self.outside / "roll_last.sh"
        self.script.write_text('#!/bin/bash\n'
                               f'echo $$ > "{self.outside}/tail.pid"\n'
                               f'echo all_done > "{self.outside}/state"\n')

    def test_registration_refuses_script_inside_runner_tree_and_conflicting_order(self):
        inside = self.run_dir / "nested.sh"
        inside.write_text("#!/bin/bash\n")
        with self.assertRaises(ValueError):
            hook.register(self.run_dir, inside)
        hook.register(self.run_dir, self.script, "0")
        self.assertEqual(hook.register(self.run_dir, self.script, "0")["run_id"], self.run_dir.name)
        with self.assertRaises(ValueError):
            hook.register(self.run_dir, self.script, "1")

    def test_failed_runner_never_installs(self):
        hook.register(self.run_dir, self.script, "0")
        rec = hook.dispatch(self.run_dir, "blocked by failed close")
        self.assertEqual(rec["state"], "held")
        self.assertEqual(rec["attempts"], [])
        self.assertFalse((self.outside / "state").exists())

    def test_launchctl_chain_and_detached_fallback_receipt(self):
        hook.register(self.run_dir, self.script, "0")
        class Failure:
            def __init__(self, rc):
                self.returncode, self.stderr, self.stdout = rc, "guarded", ""
        calls = []
        def launch(argv, **kwargs):
            calls.append(argv[1])
            return Failure({"submit": 134, "bootstrap": 125, "load": 134}[argv[1]])
        with patch.object(hook.subprocess, "run", side_effect=launch):
            rec = hook.dispatch(self.run_dir, "done", launchctl="/bin/launchctl")
        self.assertEqual(calls, ["submit", "bootstrap", "load"])
        self.assertEqual([a["rc"] for a in rec["attempts"]], [134, 125, 134])
        self.assertEqual((rec["state"], rec["method"]), ("dispatched", "double_fork"))
        self.assertEqual(rec["author"], "workflow_runner")
        self.assertEqual((self.outside / "state").read_text().strip(), "all_done")
        self.assertEqual(json.loads((self.run_dir / hook.RECEIPT).read_text()), rec)
        with patch.object(hook.subprocess, "run") as no_relaunch:
            self.assertEqual(hook.dispatch(self.run_dir, "done"), rec)
            no_relaunch.assert_not_called()

    def test_actual_runner_writes_receipt_after_exit(self):
        # Real wf.py process; echo needs no model and makes a terminal run.
        (self.run_dir / "graph.json").write_text(json.dumps({"name": "roll-last-test", "nodes": [
            {"id": "done", "type": "echo", "output": {"status": "ok"}}]}))
        (self.run_dir / "run.json").write_text(json.dumps({"hermes_bin": "offline"}))
        hook.register(self.run_dir, self.script, "0")
        env = dict(os.environ, HERMES_HOME=str(self.root), WF_RUNS_ROOT=str(self.root / "workflows"))
        p = subprocess.run([sys.executable, str(REPO / "wf.py"), "run", self.run_dir.name],
                           env=env, capture_output=True, text=True, timeout=50)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("WORKFLOW_DONE", p.stdout)
        rec = json.loads((self.run_dir / hook.RECEIPT).read_text())
        self.assertGreater(rec["runner_pid"], 0)
        self.assertEqual(rec["state"], "dispatched", rec)
        self.assertEqual(rec["author"], "workflow_runner")
        deadline = time.monotonic() + 4
        final = ""
        while time.monotonic() < deadline:
            try:
                final = (self.outside / "state").read_text().strip()
            except OSError:
                final = ""
            if final == "all_done":
                break
            time.sleep(0.1)
        self.assertEqual(final, "all_done", "state marker never reached all_done")
        self.assertEqual(json.loads((self.run_dir / "runner_exit.json").read_text())["reason"], "done")


if __name__ == "__main__":
    unittest.main(verbosity=2)
