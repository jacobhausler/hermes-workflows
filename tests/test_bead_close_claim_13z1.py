#!/usr/bin/env python3
"""est-13z1 — bead-close claims are checked against the store at the commit edge.

The incident (run 20261008-013428-ra-pr-deep-283, node reconcile): the child's
fenced answer carried note "est-o90l closed" and the prose line "bead est-o90l
is closed"; the node committed DONE and the run reached run.done. The bd
read-back right after run.done said est-o90l was still in_progress, assignee
gh-dispatch. Prompt law ("close the bead and check it closed") cannot be
trusted — the assignee guard ('cannot close: assignee is gh-dispatch, actor is
<other>') makes an honest-looking false claim easy to emit. So the RUNNER owns
the check, the same law #56 owns for effect receipts and 64c6772b owns for
lanes: a claimed external state change is only believed when the runner reads
the state itself.

The contract implemented:
  * a node declares `bead_close: {"store", "id", "actor"?}` (closed keys);
  * at the commit edge — after the effect gate, before the record lands, on the
    agent, fan-out aggregate, and echo paths — the runner runs
    `bd -C <store> show <id> --json` ITSELF and records the measured row on the
    node record as `bead_close_receipt`;
  * anything but an observed `status == "closed"` DEMOTES the commit to
    `failed` `error_class:"bead_close"`, error `bead_close_unproven: <id>:
    <reason>` — a proven-fail, never retried by either ladder, run.done never
    fires over it;
  * honest degradation: no `bead_close` key = today's behavior byte-identical;
  * the child-side law: a lane that cannot close (assignee differs) returns
    `close-pending: <reason>` and NEVER claims closure — the fake-hermes
    CLOSE-CLAIM prompt below proves the false-claim shape is what dies.

RED proof (run before the fix): (a) the `bead_close` key is refused as an
unknown key at the door and nothing checks the store, so the false close
commits done; (b-e) fail because no check exists at the commit edge.

Run: env -u WF_RUNS_ROOT -u HERMES_HOME \
     PYTHONPATH=/opt/hermes /opt/hermes/.venv/bin/python tests/test_bead_close_claim_13z1.py
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
import wf  # noqa: E402

FAKE = str(ROOT / "tests" / "fake")
BD_PY = str(ROOT / "tests" / "fake_bd_close_13z1.py")


class BeadCloseClaim(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="13z1-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.runs = self.home / "workflows"
        self.runs.mkdir()
        (self.home / "fake.log").write_text("")
        self.store = self.home / "bd-store.json"
        self.bdlog = self.home / "bd.log"
        (self.home / "bin").mkdir()
        bdp = self.home / "bin" / "bd"
        bdp.write_text("#!/bin/sh\nexec /usr/bin/python3 %s \"$@\"\n" % BD_PY)
        bdp.chmod(0o755)
        os.environ["PATH"] = str(self.home / "bin") + os.pathsep + os.environ["PATH"]

    def set_store(self, **beads):
        self.store.write_text(json.dumps(beads))

    def mk(self, run_id, nodes, **meta):
        r = self.runs / run_id
        (r / "nodes").mkdir(parents=True)
        (r / "gates").mkdir()
        (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
        m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}
        m.update(meta)
        (r / "run.json").write_text(json.dumps(m))
        return r

    def wf(self, run_id, timeout=120):
        env = dict(os.environ, HERMES_HOME=str(self.home),
                   WF_RUNS_ROOT=str(self.runs),
                   FAKE_LOG=str(self.home / "fake.log"),
                   FAKE_BD_STORE=str(self.store),
                   FAKE_BD_LOG=str(self.bdlog))
        return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                              env=env, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()

    def rec(self, r, nid):
        p = r / "nodes" / f"{nid}.json"
        return json.loads(p.read_text()) if p.exists() else {}

    def decl(self, **over):
        d = {"store": str(self.home / "estate"), "id": "est-closed1"}
        d.update(over)
        return d

    # ---- (a) THE INCIDENT REGRESSION: a fake child output claims the bead was
    #         closed; the store says in_progress => the check catches it.
    def test_a_false_close_claim_caught(self):
        self.set_store(**{"est-closed1": {"status": "in_progress", "assignee": "gh-dispatch"}})
        r = self.mk("bc-a", [{
            "id": "rec", "type": "agent",
            "goal": 'CLOSE-CLAIM {"result":"done","note":"est-closed1 closed"} post the verdict',
            "bead_close": self.decl()}])
        out = self.wf("bc-a")
        self.assertNotIn("WORKFLOW_DONE", out)
        rec = self.rec(r, "rec")
        self.assertEqual(rec.get("status"), "failed",
                         f"false close claim committed {rec.get('status')}: {rec}")
        self.assertEqual(rec.get("error_class"), "bead_close")
        self.assertIn("bead_close_unproven", rec.get("error", ""))
        self.assertIn("est-closed1", rec.get("error", ""))
        row = rec.get("bead_close_receipt")
        self.assertIsInstance(row, dict, "measured read-back must ride the FAILED record")
        self.assertEqual(row.get("observed_status"), "in_progress")
        self.assertEqual(row.get("assignee"), "gh-dispatch")
        self.assertTrue(row.get("ok") is False)
        # the runner ran the store read ITSELF, with bd's own argv shape
        argvs = self.bdlog.read_text().splitlines() if self.bdlog.exists() else []
        self.assertTrue(any(a.startswith("-C ") and a.endswith("show est-closed1 --json")
                            for a in argvs), f"no store read-back argv recorded: {argvs}")

    # ---- (b) the store really says closed => done stands, receipt recorded,
    #         run.done fires.
    def test_b_true_close_commits_done(self):
        self.set_store(**{"est-closed1": {"status": "closed", "assignee": "hermes"}})
        r = self.mk("bc-b", [{
            "id": "rec", "type": "agent",
            "goal": 'CLOSE-CLAIM {"result":"done","note":"est-closed1 closed"} post the verdict',
            "bead_close": self.decl()}])
        self.wf("bc-b")
        rec = self.rec(r, "rec")
        self.assertEqual(rec.get("status"), "done",
                         f"true close refused: {rec}")
        row = rec.get("bead_close_receipt")
        self.assertTrue(row.get("ok") and row.get("observed_status") == "closed")
        self.assertIn("run.done", (r / "events.jsonl").read_text())

    # ---- (c) honest non-claim: child returns close-pending (no claimed=) =>
    #         no store read, node commits done untouched.
    def test_c_close_pending_never_checked(self):
        self.set_store(**{"est-closed1": {"status": "in_progress", "assignee": "gh-dispatch"}})
        r = self.mk("bc-c", [{
            "id": "rec", "type": "agent",
            "goal": 'CLOSE-CLAIM {"result":"in_progress","close-pending":"cannot close: '
                    'assignee is gh-dispatch, actor is hermes","note":"left open honestly"}',
            "bead_close": self.decl()}])
        out = self.wf("bc-c")
        self.assertIn("WORKFLOW_DONE", out)
        rec = self.rec(r, "rec")
        self.assertEqual(rec.get("status"), "done", f"honest close-pending died: {rec}")
        self.assertNotIn("bead_close_receipt", rec)
        self.assertFalse(self.bdlog.exists() and self.bdlog.read_text().strip(),
                         "runner read the store for a child that never claimed closure")

    # ---- (d) closed-without-claim: the child says nothing about closing but
    #         the declaration stands => runner verifies anyway and PASSES
    #         (proves the check anchors to the store, not to the prose).
    def test_d_closed_without_claim_passes(self):
        self.set_store(**{"est-closed1": {"status": "closed", "assignee": "hermes"}})
        r = self.mk("bc-d", [{
            "id": "rec", "type": "agent",
            "goal": "CLOSE-CLAIM {\"result\":\"done\",\"note\":\"quiet about the bead\"}",
            "bead_close": self.decl()}])
        self.wf("bc-d")
        rec = self.rec(r, "rec")
        self.assertEqual(rec.get("status"), "done", f"true close refused: {rec}")
        self.assertTrue(rec.get("bead_close_receipt", {}).get("ok"))

    # ---- (e) a bead unknown to the store can never launder a close.
    def test_e_unknown_bead_fails(self):
        self.set_store(**{"other": {"status": "closed", "assignee": "hermes"}})
        r = self.mk("bc-e", [{
            "id": "rec", "type": "agent",
            "goal": 'CLOSE-CLAIM {"result":"done","note":"est-ghost1 closed"} post',
            "bead_close": self.decl(id="est-ghost1")}])
        out = self.wf("bc-e")
        self.assertNotIn("WORKFLOW_DONE", out)
        rec = self.rec(r, "rec")
        self.assertEqual(rec.get("status"), "failed")
        self.assertEqual(rec.get("error_class"), "bead_close")
        self.assertEqual(rec.get("bead_close_receipt", {}).get("observed_status"), None)
        self.assertEqual(rec.get("bead_close_receipt", {}).get("probe_rc"), 1)

    # ---- (f) the check is a proven-fail: outside BOTH retry ladders, so the
    #         false-close child spawns exactly once.
    def test_f_proven_fail_never_retried(self):
        self.set_store(**{"est-closed1": {"status": "in_progress", "assignee": "gh-dispatch"}})
        self.assertNotIn("bead_close", wf._RETRYABLE_CLASSES + wf._BOUNDED_RETRY_CLASSES)
        (self.home / "fake.log").write_text("")
        r = self.mk("bc-f", [{
            "id": "rec", "type": "agent",
            "goal": 'CLOSE-CLAIM {"result":"done","note":"est-closed1 closed"} post',
            "bead_close": self.decl()}])
        self.wf("bc-f")
        lines = [l for l in (self.home / "fake.log").read_text().splitlines() if "CLOSE-CLAIM" in l]
        self.assertEqual(len(lines), 1, f"proven-fail was retried: {len(lines)} spawns")

    # ---- (g) honest degradation: a node WITHOUT the declaration is byte-
    #         identical today's behavior, even if its prose claims a close.
    def test_g_undeclared_untouched(self):
        self.set_store(**{"est-closed1": {"status": "in_progress", "assignee": "x"}})
        r = self.mk("bc-g", [{
            "id": "rec", "type": "agent",
            "goal": 'CLOSE-CLAIM {"result":"done","note":"est-closed1 closed"} plain node'}])
        out = self.wf("bc-g")
        self.assertIn("WORKFLOW_DONE", out)
        rec = self.rec(r, "rec")
        self.assertEqual(rec.get("status"), "done")
        self.assertNotIn("bead_close_receipt", rec)
        self.assertFalse(self.bdlog.exists() and self.bdlog.read_text().strip(),
                         "undeclared graph triggered a store read (scan-free law)")

    # ---- (h) door: closed grammar, fail-closed.
    def _bc_errs(self, nodes):
        return [e for e in wfcommon.validate_graph_errors(nodes)
                if "bead_close" in json.dumps(e)]

    def test_h_door_rejects_malformed(self):
        base = [{"id": "a", "type": "agent", "bead_close":
                 {"store": "/srv/beads", "id": "est-x", "actor": "hermes"}}]
        self.assertEqual(self._bc_errs(base), [], "well-formed declaration must pass")
        for nodes, label in (
            ([{"id": "a", "type": "agent", "bead_close": "est-x"}], "bare string"),
            ([{"id": "a", "type": "agent", "bead_close": {}}], "empty object"),
            ([{"id": "a", "type": "agent", "bead_close": {"store": "/s"}}], "missing id"),
            ([{"id": "a", "type": "agent", "bead_close": {"id": "est-x"}}], "missing store"),
            ([{"id": "a", "type": "agent", "bead_close":
               {"store": "/s", "id": "est-x", "argv": ["x"]}}], "stray key"),
            ([{"id": "a", "type": "agent", "bead_close":
               {"store": "", "id": "est-x"}}], "blank store"),
            ([{"id": "a", "type": "agent", "bead_close":
               {"store": "/s", "id": ""}}], "blank id"),
            ([{"id": "a", "type": "agent", "bead_close":
               {"store": "/s", "id": "est-x", "actor": ""}}], "blank actor"),
            ([{"id": "a", "type": "gate", "after": [], "bead_close":
               {"store": "/s", "id": "est-x"}}], "gate rejects it"),
            ([{"id": "a", "type": "agent", "bead_close":
               {"store": "/s", "id": "est x"}}], "id with space"),
        ):
            with self.subTest(label):
                self.assertTrue(self._bc_errs(nodes), f"door accepted {label}")

    # ---- (i) docs + closed-set pins carry the new class/key.
    def test_i_doc_pins(self):
        self.assertIn("bead_close", wf.ERROR_CLASSES)
        doc = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("bead_close", doc, "AGENTS.md §3d pipe-list must carry the class")
        self.assertIn("bead_close", wfcommon.AGENT_KEYS)
        self.assertNotIn("bead_close", wfcommon.GATE_KEYS)
        self.assertIn("bead_close", wfcommon.ECHO_KEYS)
        gram = (ROOT / "references" / "grammar.md").read_text(encoding="utf-8")
        self.assertIn("bead_close", gram,
                      "grammar.md must document the bead_close declaration")
        # the gate must be opt-in by DECLARATION only — never inferred from prose
        src = (ROOT / "wf.py").read_text(encoding="utf-8")
        gate_src = src[src.index("def _bead_close_gate"):src.index("def _bead_close_gate") + 6000]
        self.assertIn('node.get("bead_close")', gate_src,
                      "gate keys off the declaration, not output prose")

    # ---- (j) echo commit path carries the gate too.
    def test_j_echo_commit_path_gated(self):
        self.set_store(**{"est-closed1": {"status": "in_progress", "assignee": "x"}})
        r = self.mk("bc-j", [{
            "id": "say", "type": "echo", "output": {"result": "done", "note": "est-closed1 closed"},
            "bead_close": self.decl()}])
        out = self.wf("bc-j")
        self.assertNotIn("WORKFLOW_DONE", out)
        rec = self.rec(r, "say")
        self.assertEqual(rec.get("status"), "failed")
        self.assertEqual(rec.get("error_class"), "bead_close")
        self.assertNotIn("run.done", (r / "events.jsonl").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
