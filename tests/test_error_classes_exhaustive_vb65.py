#!/usr/bin/env python3
"""Closed-set contract for node.failed records and events (AGENTS.md 3d).

Exercise producer paths, not source spelling: launcher failure, forbidden
served model, unmet prerequisites, missing inputs, empty fan-out, and capture
classification. Other producer paths have their own behavioral suites; this
is not a static census of every error_class write. Wake delivery failures
belong to wake.jsonl, not the node.failed namespace.
"""
import json
import os
import re
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wf


def assert_member(label, value):
    assert value in wf.ERROR_CLASSES, f"{label}: {value!r} missing from ERROR_CLASSES"
    print(f"PASS {label}: {value}", flush=True)


def assert_failure(run, node, expected):
    rec = json.loads((run / "nodes" / (node["id"] + ".json")).read_text())
    events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
    failures = [e for e in events if e["event"] == "node.failed"]
    assert rec["status"] == "failed" and rec.get("error_class") == expected, rec
    assert len(failures) == 1 and failures[0].get("error_class") == expected, failures
    assert_member("committed record " + node["id"], rec["error_class"])
    assert_member("committed event " + node["id"], failures[0]["error_class"])
    return rec


def fresh(home, name, **fields):
    run = home / "workflows" / name
    (run / "nodes").mkdir(parents=True)
    node = {"id": name, "type": "agent", "goal": "ok", **fields}
    (run / "graph.json").write_text(json.dumps({"name": name, "nodes": [node]}))
    meta = {"_run": run, "hermes_bin": str(home / "absent-hermes"),
            "_spawn_n": {}, "_procs_lock": threading.Lock(), "_procs": {},
            "_stop": threading.Event(), "_retries_left": 0,
            "max_seats": 0, "node_timeout": 1}
    return run, node, {name: node}, meta


def test_error_class_contract():
    assert isinstance(wf.ERROR_CLASSES, frozenset)
    assert all(isinstance(t, str) and re.fullmatch(r"[a-z0-9_]+", t) for t in wf.ERROR_CLASSES)
    captures = [
        ("unresolved_model", "Provider said: unknown model"),
        ("provider_400", "Provider said: Error code: 400"),
        ("fatal_quota", "Provider said: Error code: 429 quota resets in 3 days"),
        ("cap_exhausted", "Provider said: turn limit reached"),
        ("transport", "Provider said: Error code: 503"),
        ("unknown", "ordinary child prose"),
    ]
    for expected, text in captures:
        actual, marker = wf._classify_rc_output(text)
        assert actual == expected, (expected, actual, marker)
        assert_member("capture classification", actual)

    with tempfile.TemporaryDirectory(prefix="wf-class-contract-") as tmp:
        home = Path(tmp)
        with patch.dict(os.environ, {"HERMES_HOME": str(home),
                                     "WF_RUNS_ROOT": str(home / "workflows"),
                                     "WF_SEATS_DIR": str(home / "seats")}):
            with patch.object(wf, "hermes_home", return_value=home), \
                 patch.object(wf, "seat_forbidden_models", return_value=[]):
                # Real Popen on a guaranteed-absent executable: no agent, model,
                # network, or shared semaphore is touched. Check both consumers.
                run, node, byid, meta = fresh(home, "spawn")
                wf.run_agent_node(run, meta, byid, node, {}, [])
                rec = assert_failure(run, node, "spawn")
                assert "launcher spawn failed" in rec["error"] and rec["attempts"] == 1, rec
                assert not meta["_procs"], meta["_procs"]
                assert not list((home / "seats").glob("*.json"))

                run, node, byid, meta = fresh(home, "precondition")
                wf._fail_precondition(run, node, byid, ["missing.output"])
                assert_failure(run, node, "precondition")

                for expected, fields in [
                    ("inputs", {"inputs": ["absent.output"]}),
                    ("fanout_empty", {"fanout": {"items": []}}),
                ]:
                    run, node, byid, meta = fresh(home, expected, **fields)
                    wf.run_agent_node(run, meta, byid, node, {}, [])
                    assert_failure(run, node, expected)

                # Substitute only the child/metrics boundaries; the served-model
                # policy, commit, and node.failed event producers run unchanged.
                run, node, byid, meta = fresh(home, "forbidden_model")
                with patch.object(wf, "run_child", return_value={"status": "done", "skey": "child"}), \
                     patch.object(wf, "child_metrics", return_value={"child": {"model": "blocked"}}), \
                     patch.object(wf, "seat_forbidden_models", return_value=["blocked"]):
                    wf.run_agent_node(run, meta, byid, node, {}, [])
                assert_failure(run, node, "forbidden_model")

                # Exercise the separate wake-ledger producers without delivery.
                for expected in ("missing_endpoint", "notify_prep"):
                    run, node, byid, meta = fresh(home, expected)
                    (run / "run.json").write_text(json.dumps({"owner": {"session_id": "fixture"}}))
                    with patch.object(wf, "_wake_identity", return_value="fixture"), \
                         patch.object(wf, "_wake_endpoint", return_value=None):
                        if expected == "notify_prep":
                            with patch.object(wf, "_wake_owner_text", side_effect=ValueError("fixture")):
                                wf.notify(run, "run.failed")
                        else:
                            wf.notify(run, "run.failed")
                    rows = [json.loads(line) for line in (run / "wake.jsonl").read_text().splitlines()]
                    assert len(rows) == 1 and rows[0]["error_class"] == expected, rows
                    # est-7rudf: a nowhere-ever row is tri-state null (settles);
                    # a notify_prep row stays false (try-later, retry path open).
                    assert rows[0]["delivered"] is (None if expected == "missing_endpoint" else False)
                    assert expected not in wf.ERROR_CLASSES, expected
                    assert not (run / "events.jsonl").exists()
                    assert not list((run / "nodes").glob("*.json"))
                    print(f"PASS wake-ledger namespace: {expected}", flush=True)
    print("ALL PASS node.failed producer/contract coverage", flush=True)


if __name__ == "__main__":
    test_error_class_contract()
