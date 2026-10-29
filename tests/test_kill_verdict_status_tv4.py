#!/usr/bin/env python3
"""A killed run must never book done. The runner's signal handler records a
kill verdict ("terminated: SIGTERM ...") whenever SIGTERM lands before the
runner wrote its own exit verdict — including the post-run.done window where
cleanup keeps the runner alive for minutes after the graph finalized. The
verdict ladder in run_state() only outranked done/stopped/budget/blocked/
crashed verdicts, so a kill verdict fell through and a run with every node
committed read status "done" — the finish-rate consumers downstream then
book a SIGTERM'd run as a success.

Fix law — terminal-record-or-completed: a present, graph-valid terminal
record IS the completion truth; the killed verdict outranks node-commit
done-ness and reads "interrupted" (resumable, respawn-eligible per the
external-kill law), never "done". Honest absence (no exit record) keeps the
node/event fallback.

S1: all nodes committed + run.done + external-kill verdict -> status is not
    done; it is interrupted; the kill reason survives in the read view; the
    derived `completed` KPI field reads False (not merely absent).
S2: the bare (untagged) kill verdict shape behaves the same.
S3: kill verdict with unfinished nodes keeps interrupted (no over-fix).
S4: a clean done verdict still books done (no-regression pin).
S5: honest absence — all committed, run.done, NO exit record -> still done.

Run: python3 tests/test_kill_verdict_status_tv4.py
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

checks = 0
failures = 0


def check(label, cond, detail=""):
    global checks, failures
    checks += 1
    if cond:
        print(f"PASS {label}")
    else:
        failures += 1
        print(f"FAIL {label}: {detail}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


with tempfile.TemporaryDirectory(prefix="killverdict-", dir=HERE,
                                 ignore_cleanup_errors=True) as td:
    home = Path(td) / "home"
    runs = home / "workflows"
    runs.mkdir(parents=True)
    os.environ["HERMES_HOME"] = str(home)
    os.environ["WF_RUNS_ROOT"] = str(runs)
    wfcommon = load("kv_wfcommon", ROOT / "wfcommon.py")
    door = load("kv_door", ROOT / "__init__.py")
    import wf_test_isolation as _iso_kv
    _iso_kv.install(door)

    NODES = [{"id": "a", "type": "agent", "goal": "x"},
             {"id": "b", "type": "agent", "goal": "y", "after": ["a"]}]
    DONE_REC = {"status": "done", "output": {"result": "ok"}}

    def scene(run_id, records, events=None, exit_reason=None):
        r = runs / run_id
        (r / "nodes").mkdir(parents=True)
        graph = {"name": run_id, "nodes": NODES}
        (r / "graph.json").write_text(json.dumps(graph))
        (r / "run.json").write_text("{}")
        byid = {n["id"]: n for n in NODES}
        for nid, rec in records.items():
            rec = dict(rec)
            rec.setdefault("efp", wfcommon.efp(byid, byid[nid]))
            (r / "nodes" / f"{nid}.json").write_text(json.dumps(rec))
        if events:
            (r / "events.jsonl").write_text(
                "".join(json.dumps(e) + "\n" for e in events))
        if exit_reason:
            (r / "runner_exit.json").write_text(json.dumps({
                "reason": exit_reason, "at": "2026-10-11T21:38:24+00:00",
                "graph_fingerprint": wfcommon.graph_fingerprint(
                    graph, rule=wfcommon.FP_RULE_VERSION),
                "fp_rule_version": wfcommon.FP_RULE_VERSION}))
        return r

    ALL_DONE = {"a": DONE_REC, "b": DONE_REC}
    RUN_DONE = [{"event": "run.done"}]
    KILL = "terminated: SIGTERM (external: source unknown)"

    # ---- S1: witnessed shape — committed graph, run.done, kill verdict ----
    r1 = scene("kv-kill", ALL_DONE, events=RUN_DONE, exit_reason=KILL)
    st1 = wfcommon.run_state(r1)
    check("S1: killed run does not book done", st1["status"] != "done",
          st1["status"])
    check("S1: killed run reads interrupted (resumable)",
          st1["status"] == "interrupted", st1["status"])
    check("S1: kill reason preserved in the read view",
          (st1.get("runner_exit") or {}).get("reason") == KILL,
          json.dumps(st1.get("runner_exit")))
    out1 = door.act_status({"run_id": "kv-kill"})
    check("S1: door status preserves the kill reason",
          (out1.get("runner_exit") or {}).get("reason", "").startswith(
              "terminated: SIGTERM"), json.dumps(out1.get("runner_exit")))
    check("S1: completed KPI field is False under a kill verdict",
          st1.get("completed") is False, json.dumps(st1.get("completed")))

    # ---- S2: the bare (untagged) verdict shape behaves the same ----
    r2 = scene("kv-kill-bare", ALL_DONE, events=RUN_DONE,
               exit_reason="terminated: SIGTERM")
    st2 = wfcommon.run_state(r2)
    check("S2: bare kill verdict does not book done",
          st2["status"] == "interrupted", st2["status"])

    # ---- S3: unfinished nodes under a kill verdict stay interrupted ----
    r3 = scene("kv-kill-open", {"a": DONE_REC},
               events=[{"event": "node.started", "node": "a"}],
               exit_reason=KILL)
    st3 = wfcommon.run_state(r3)
    check("S3: kill verdict with pending nodes keeps interrupted",
          st3["status"] == "interrupted", st3["status"])

    # ---- S4: a clean done verdict still books done ----
    r4 = scene("kv-done", ALL_DONE, events=RUN_DONE, exit_reason="done")
    st4 = wfcommon.run_state(r4)
    check("S4: done verdict keeps done", st4["status"] == "done",
          st4["status"])

    # ---- S5: honest absence (no exit record) keeps the fallback ----
    r5 = scene("kv-norec", ALL_DONE, events=RUN_DONE)
    st5 = wfcommon.run_state(r5)
    check("S5: committed run with no exit record still books done",
          st5["status"] == "done", st5["status"])

print(f"\n{checks} checks, {failures} failures")
sys.exit(1 if failures else 0)
