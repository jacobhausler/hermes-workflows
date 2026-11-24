#!/usr/bin/env python3
"""Materialize the coverage-case fixture census (bd_2026-11-13-yjp).

Writes the valid-run trio (graph.json + run.json + nodes/a.json + events.jsonl)
straight from the repo's OWN read model (fp_rule_version and all), so the
dashboard route — not a mocked payload — counts these rows. This mirrors the
seeding shape already pinned by tests/test_runs_offloop_ey31s.py; it launches
no door, no runner, no tokens.

Status truth, stated not painted: with an empty efp the record does not pass
the replay-skip validity (#134), so run_state reads every fixture row as
`interrupted` (unfinished work, no live runner) — never `done`. That is the
contract this case relies on: `interrupted` is NOT in the plugin's TERMINAL
set, so the pane keeps its real 4 s poll loop and the error/recovery frames
are driven by that actual loop, not by a timer fiction. The fixture never
fabricates a verdict it did not earn.

ids sort name-DESC at the route (iter_run_dirs), so --start 0's row
(covr-000) sits at the DEEPEST census position — beyond the first page.

Prints one JSON line: {"ids": [...], "names": [...]}.

Run: python3 seed_fixture.py --repo <plugin-repo> --runs-root <dir> --count N [--start S]
"""
import argparse, json, os, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--runs-root", required=True)
ap.add_argument("--count", type=int, default=1)
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--prefix", default="covr")
a = ap.parse_args()
sys.path.insert(0, a.repo)
os.environ.setdefault("HERMES_HOME", str(Path(a.runs_root).parent / "home"))
import wfcommon

root = Path(a.runs_root)
root.mkdir(parents=True, exist_ok=True)
ids, names = [], []
for i in range(a.start, a.start + a.count):
    rid = "20990101-%06d-%s" % (100000 + i, a.prefix)
    name = "%s-%03d" % (a.prefix, i)
    r = root / rid
    (r / "nodes").mkdir(parents=True, exist_ok=True)
    (r / "graph.json").write_text(json.dumps({"name": name, "nodes": [
        {"id": "a", "type": "agent", "goal": "fixture census row"}]}))
    (r / "run.json").write_text(json.dumps({"run_id": rid, "name": name,
                                            "started": "2099-01-01T00:00:00+00:00"}))
    (r / "nodes" / "a.json").write_text(json.dumps(
        {"status": "done", "output": {"answer": "ok"}, "efp": "",
         "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    (r / "events.jsonl").write_text(json.dumps(
        {"ts": "2099-01-01T00:00:00+00:00", "event": "run.started"}) + "\n")
    ids.append(rid)
    names.append(name)
print(json.dumps({"ids": ids, "names": names}))
