#!/usr/bin/env python3
"""Signal death needs this spawn's quorum-kill intent, not a negative rc.

Standalone stdlib regression: python3 tests/test_quorum_cause_guard_6226.py.
External SIGTERM/SIGKILL, an event set after death, and harvest preservation
exercise run_child with real processes. A real fan-out exercises the production
cancel setter. Banner bytes and work files never establish agent-visible output;
unstructured captures remain explicitly unknown, not confirmed output.
"""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("quorum_guard_runner", ROOT / "wf.py")
assert spec is not None and spec.loader is not None
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

BANNER = "Hermes Agent\nModel: fixture\nTools: terminal\nSession: starting\n"
STUB = '''import json, os, signal, sys, time
from pathlib import Path
q = Path(sys.argv[sys.argv.index('--query-file') + 1]).read_text().splitlines()[0]
if q == 'winner':
    time.sleep(0.8)
    print('```json\\n{"result":"winner"}\\n```', flush=True)
    sys.exit(0)
if q != 'empty':
    print(%r, end='', flush=True)
    for i in range(4):
        Path('startup-%%s.txt' %% i).write_text('fixture scaffolding')
if q.startswith('partial') or q == 'fenced':
    print('```json\\n{"result":"banked"}\\n```', flush=True)
if q == 'empty' or q == 'banner' or q == 'fenced':
    time.sleep(20)
else:
    os.kill(os.getpid(), signal.SIGKILL if 'kill' in q else signal.SIGTERM)
''' % BANNER


class QuorumCauseGuard(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".tmp-quorum6226-", dir=ROOT / "tests")
        self.home = Path(self.temp.name)
        self.bin = self.home / "fake"
        self.bin.write_text("#!" + sys.executable + "\n" + STUB)
        self.bin.chmod(0o755)
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("HERMES_WF_", "HERMES_SESSION_", "HERMES_UI_SESSION_"))}
        env.update(HERMES_HOME=str(self.home), WF_RUNS_ROOT=str(self.home / "runs"),
                   HERMES_WF_HERMES_BIN=str(self.bin), PYTHONDONTWRITEBYTECODE="1")
        self.env = patch.dict(os.environ, env, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.temp.cleanup)

    def make_run(self, name):
        r = self.home / "runs" / name
        for d in ("nodes", "gates", "logs", "work"):
            (r / d).mkdir(parents=True, exist_ok=True)
        return r

    def child(self, goal, late_event=False):
        r = self.make_run("child")
        n = {"id": "work", "type": "agent", "goal": goal, "timeout": 10}
        meta = {"_run": r, "_procs": {}, "_procs_lock": threading.RLock(),
                "_stop": threading.Event(), "hermes_bin": str(self.bin), "max_seats": 0}
        event = threading.Event()
        release = wf._seat_release
        def release_then_event(seat):
            release(seat)
            if late_event:
                event.set()  # genuine event, but no cancellation of THIS spawn
        with patch.object(wf, "_seat_release", side_effect=release_then_event):
            rec = wf.run_child(meta, n, {"work": n}, goal, "", None, seat_cancel=event)
        self.assertEqual(meta["_procs"], {})
        self.assertFalse(wf._proc_alive(rec["pid"]))
        return rec

    def assert_external(self, rec, sig):
        self.assertNotEqual(rec.get("error_class"), "cancelled", rec)
        self.assertEqual(rec.get("death_class"), "external_kill", rec)
        self.assertEqual(rec.get("signal"), sig.name, rec)
        self.assertEqual(rec.get("signal_number"), int(sig), rec)
        self.assertEqual(rec.get("returncode"), -int(sig), rec)
        self.assertIn("source unknown", rec.get("error", ""))
        self.assertNotIn("quorum", rec.get("error", ""))
        self.assertNotIn("cancel_evidence", rec)
        self.assertIn(rec.get("error_class"), wf.ERROR_CLASSES)

    def test_external_sigterm_banner_and_scaffolding(self):
        rec = self.child("term")
        self.assert_external(rec, signal.SIGTERM)
        self.assertEqual(rec["status"], "failed")
        self.assertIn(BANNER, rec["raw"])

    def test_external_sigkill_no_quorum(self):
        self.assert_external(self.child("kill"), signal.SIGKILL)

    def test_late_quorum_event_is_not_this_spawns_kill_cause(self):
        self.assert_external(self.child("kill", late_event=True), signal.SIGKILL)

    def test_external_death_retains_fenced_harvest(self):
        rec = self.child("partial-term")
        self.assert_external(rec, signal.SIGTERM)
        self.assertEqual(rec["status"], "partial")
        self.assertEqual(rec["output"], {"result": "banked"})

    def test_output_evidence_requires_agent_answer_not_bytes_or_files(self):
        r = self.make_run("evidence")
        lp = r / "logs" / "work.a0.log"
        wd = wf.child_work_dir(r, {"id": "work"}, None)
        (wd / "setup.txt").write_text("scaffolding")
        lp.write_text(BANNER)
        suffix, snap = wf._cancel_evidence(r, "work", None, lp)
        self.assertIsNot(snap.get("agent_visible_output"), True, snap)
        self.assertIn("no confirmed agent-visible output", suffix)
        self.assertEqual(snap["log_bytes"], len(BANNER.encode()))
        self.assertEqual(snap["work_files"], 1)
        lp.write_text('```json\n{"result":"answer"}\n```')
        suffix, snap = wf._cancel_evidence(r, "work", None, lp)
        self.assertIs(snap.get("agent_visible_output"), True)
        self.assertIn("had output at quorum moment", suffix)

    def test_real_quorum_cancels_only_stragglers_and_keeps_harvest(self):
        r = self.make_run("quorum")
        node = {"id": "fan", "type": "agent", "timeout": 10,
                "fanout": {"goal": "{item}", "quorum": 1,
                           "items": ["winner", "banner", "fenced"]}}
        (r / "graph.json").write_text(json.dumps({"name": r.name, "nodes": [node]}))
        (r / "run.json").write_text(json.dumps({"hermes_bin": str(self.bin),
             "concurrency": 1, "item_concurrency": 3, "max_seats": 0, "node_timeout": 10}))
        p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", str(r)],
                           capture_output=True, text=True, timeout=25)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        rec = json.loads((r / "nodes" / "fan.json").read_text())
        self.assertEqual(rec["status"], "done", rec)
        rows = {row["item"]: row for row in rec["output"]["all_results"]}
        self.assertEqual(rec["output"]["failed_items"], 0)
        self.assertEqual(rec["output"]["cancelled_items"], 2)
        for item in ("banner", "fenced"):
            row = rows[item]
            self.assertEqual(row["error_class"], "cancelled", row)
            self.assertIn("quorum", row["error"])
            self.assertFalse(wf._proc_alive(row["pid"]))
        self.assertIsNot(rows["banner"]["cancel_evidence"].get("agent_visible_output"), True)
        self.assertIn("no confirmed agent-visible output", rows["banner"]["error"])
        self.assertEqual(rows["fenced"]["output"], {"result": "banked"})
        self.assertIs(rows["fenced"]["cancel_evidence"].get("agent_visible_output"), True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
