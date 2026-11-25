#!/usr/bin/env python3
"""Exercise the authored wait-all mode through validation and the real runner."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wfcommon


def plan(policy):
    return {"name": "quorum-policy", "nodes": [{
        "id": "review", "type": "agent",
        "fanout": {"items": ["first", "second", "dissent"],
                   "goal": "Review {item} independently", **policy},
    }]}


def run_wave(home, policy, expected_goals):
    home.mkdir()
    run = home / "workflows" / "quorum-policy"
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    graph = plan(policy)
    (run / "graph.json").write_text(json.dumps(graph))
    (run / "run.json").write_text(json.dumps({
        "hermes_bin": str(HERE / "fake"), "concurrency": 1,
        "item_concurrency": 1, "node_timeout": 10, "max_seats": 0,
    }))
    # Serial admission makes the third item queued at majority, not a sleep race.
    log = home / "fake.log"
    env = dict(os.environ, HERMES_HOME=str(home), WF_RUNS_ROOT=str(run.parent),
               WORKFLOW_MAX_SEATS="0", FAKE_LOG=str(log))
    env.pop("HERMES_WF_RUN_DIR", None)
    p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run.name],
                       env=env, capture_output=True, text=True, timeout=25)
    assert p.returncode == 0 and (run / "nodes/review.json").is_file(), p.stdout + p.stderr
    rec = json.loads((run / "nodes/review.json").read_text())
    assert rec["status"] == "done", rec
    rows = rec["output"]["all_results"]
    assert [row["item"] for row in rows if row["status"] == "done"] == expected_goals, rows
    assert [row["item"] for row in rows if row.get("error_class") == "cancelled"] == (
        [] if len(expected_goals) == 3 else ["dissent"]), rows
    assert len(log.read_text().splitlines()) == len(expected_goals)
    assert json.loads((run / "graph.json").read_text())["nodes"][0]["fanout"] == graph["nodes"][0]["fanout"]
    print(f"PASS runner {policy!r} commits {expected_goals!r}")


with tempfile.TemporaryDirectory(prefix="wf-eh1-") as tmp:
    home = Path(tmp)
    run_wave(home / "authored", {"quorum_mode": "all"}, ["first", "second", "dissent"])
    run_wave(home / "default", {}, ["first", "second", "dissent"])
    run_wave(home / "numeric", {"quorum": 2}, ["first", "second"])


def errors(policy):
    return wfcommon.validate_graph_errors(plan(policy)["nodes"], admission=True)


assert not errors({"quorum_mode": "all"})
for value in ("majority", "ALL", "", None, True, ["all"]):
    errs = errors({"quorum_mode": value})
    assert any(e["field"] == "fanout.quorum_mode" and "must be" in e["msg"] for e in errs), errs
assert any(e["field"] == "fanout.quorum_mode" and "cannot" in e["msg"]
           for e in errors({"quorum_mode": "all", "quorum": 2}))
assert any(e["field"] == "fanout.quorum_drain_s"
           for e in errors({"quorum_mode": "all", "quorum_drain_s": 1}))
print("PASS admission rejects invalid modes, conflicting quorum, and drain without quorum")
