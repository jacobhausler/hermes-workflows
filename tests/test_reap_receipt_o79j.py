#!/usr/bin/env python3
"""Silent deaths have a durable typed verdict, not a false-running read model."""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon


def test_reap_receipt():
    with tempfile.TemporaryDirectory(prefix="reap-receipt-") as td:
        r = Path(td)
        os.environ["HERMES_HOME"] = str(r / "home")
        (r / "nodes").mkdir()
        n = {"id": "work", "type": "agent", "goal": "g"}
        graph = {"name": "reap", "nodes": [n]}
        byid = {"work": n}
        (r / "graph.json").write_text(json.dumps(graph))
        (r / "wf.pid").write_text("99999998")
        rec = {"status": "running", "pid": 99999999, "skey": "wf:reap:work:x#a0",
               "attempt": 0, "efp": wfcommon.efp(byid, n),
               "fp_rule_version": wfcommon.FP_RULE_VERSION}
        (r / "nodes/work.json").write_text(json.dumps(rec))
        spec = importlib.util.spec_from_file_location("receipt_door", ROOT / "__init__.py")
        door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(door)
        door._reap_silent_death(r)
        rx = json.loads((r / "runner_exit.json").read_text())
        assert rx["reason"].startswith("interrupted: silent runner death")
        assert rx["error_class"] == "crashed"
        assert rx["prev_pid"] == 99999998
        assert wfcommon.runner_exit_read(r)["reason"] == rx["reason"]
        st, current = wfcommon.node_rec(r, n, byid)
        assert st == "pending"  # interrupted work remains resumable, not a failure
        assert current["status"] == "interrupted"
        assert current["error_class"] == "crashed"
        before = (r / "events.jsonl").read_bytes()
        door._reap_silent_death(r)
        assert (r / "events.jsonl").read_bytes() == before
        assert json.loads((r / "runner_exit.json").read_text()) == rx
        # A new spawn must not inherit the old interruption.
        rec["pid"] = 99999997
        (r / "nodes/work.json").write_text(json.dumps(rec))
        assert wfcommon.node_rec(r, n, byid)[1]["status"] == "running"
        # A committed answer is never overwritten by historical death evidence.
        rec.update(status="done", output={"ok": True})
        (r / "nodes/work.json").write_text(json.dumps(rec))
        assert wfcommon.node_rec(r, n, byid)[0] == "done"


if __name__ == "__main__":
    test_reap_receipt()
    print("PASS durable silent-death receipt and current node projection")
