#!/usr/bin/env python3
"""Graph-case fixture materializer for the ui2-proof driver (bd_2026-11-13-33h).

Three honest seeds, printed as one JSON line:

  council  — HISTORICAL SNAPSHOT: the frozen wave6 shelf fixture
             (ui2/synthesis/fixtures-real/20261122-121032-wave6-council.json,
             sha256-pinned, refuses on mismatch) materialized read-only into
             the isolated runs root. The fixture FILE is never touched; the
             run is never relaunched.

  mf1      — CLEARLY SYNTHETIC regression rows for the MF1 law: a done fan-out
             parent whose item records hold raw `partial` (cap_exhausted) and
             raw `failed/cancelled` side by side — a census no live launch of
             this graph produced. Node records carry the REAL `efp` computed
             by the repo's own read model (wfcommon.efp), so run_state reads
             the trio as `done` for the right reason (valid, complete), not
             as a painted costume. SYNTHETIC.txt in the run dir says so.

  thr      — TERMINAL WAIT for the engine seed the driver launched separately:
             polls wfcommon.run_state (the same read model the dashboard
             route uses) until the run is terminal. The strip must render an
             exact ENDED census, never a mid-flight count.

Run: python3 seed_graph.py --repo R --runs-root DIR --fixture F --fixture-sha256 S [--wait-run ID]
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--runs-root", required=True)
ap.add_argument("--fixture", required=True, help="council snapshot fixture json (read-only)")
ap.add_argument("--fixture-sha256", required=True)
ap.add_argument("--wait-run", default=None, help="run id to wait for, terminal via run_state")
ap.add_argument("--wait-s", type=float, default=90.0)
a = ap.parse_args()

root = Path(a.runs_root)
root.mkdir(parents=True, exist_ok=True)

raw = Path(a.fixture).read_bytes()
got = hashlib.sha256(raw).hexdigest()
if got != a.fixture_sha256:
    print(f"REFUSED: fixture sha {got} != pinned {a.fixture_sha256}", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, a.repo)
import wfcommon  # repo read model — the same efp the door would have stamped

d = json.loads(raw.decode())
rid = d["run_id"]
c = root / rid
(c / "nodes").mkdir(parents=True, exist_ok=True)
(c / "graph.json").write_text(json.dumps(d["graph"]))
run = dict(d.get("run") or {})
run.setdefault("run_id", rid)
(c / "run.json").write_text(json.dumps(run))
for nid, rec in (d.get("nodes") or {}).items():
    (c / "nodes" / f"{nid}.json").write_text(json.dumps(rec))
ev = d.get("events") or []
(c / "events.jsonl").write_text("\n".join(json.dumps(e) for e in ev) + ("\n" if ev else ""))
out = {"council_run_id": rid, "council_fixture_sha256": got}

# -- MF1 synthetic trio ---------------------------------------------------
mf1_id = "20990101-000000-mf1-33h"
m = root / mf1_id
(m / "nodes").mkdir(parents=True, exist_ok=True)
ts = 4102444800.0  # 2099-11-19: sorted first among names; never claims recency
graph = {"grammar": "wf/1", "name": "mf1-33h", "nodes": [
    {"id": "seed", "type": "echo", "output": {"msg": "synthetic"}},
    {"id": "fan", "type": "agent", "after": ["seed"],
     "fanout": {"goal": "mf1 probe {index}",
                "items": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}},
    {"id": "tail", "type": "echo", "after": ["fan"], "output": {"msg": "synthetic"}}]}
byid = {n["id"]: n for n in graph["nodes"]}
(m / "graph.json").write_text(json.dumps(graph))
(m / "run.json").write_text(json.dumps({
    "run_id": mf1_id, "name": "mf1-33h", "started": ts, "owner": "ui2-proof"}))
ar = [
    {"index": 0, "id": "a", "status": "done", "output": {"r": 1}, "ms": 31000, "item": {"id": "a"}},
    {"index": 1, "id": "b", "status": "partial", "output": {"r": 2}, "error_class": "cap_exhausted",
     "error": "turn cap spent; harvest readable (synthetic row)", "ms": 44000, "item": {"id": "b"}},
    {"index": 2, "id": "c", "status": "failed", "error_class": "cancelled",
     "error": "cancelled: stop (synthetic row)", "ms": 9000, "item": {"id": "c"}}]


def rec(nid, **kw):
    return {"efp": wfcommon.efp(byid, byid[nid]), "fp_rule_version": wfcommon.FP_RULE_VERSION, **kw}


(m / "nodes" / "seed.json").write_text(json.dumps(rec("seed", status="done", output={"msg": "synthetic"})))
(m / "nodes" / "fan.json").write_text(json.dumps(rec(
    "fan", status="done", attempts=1, attempts_log=[],
    output={"all_results": ar, "items": [r["output"]["r"] for r in ar[:2]]})))
(m / "nodes" / "tail.json").write_text(json.dumps(rec("tail", status="done", output={"msg": "synthetic"})))
(m / "events.jsonl").write_text("\n".join(json.dumps(
    {"ts": ts + i, "event": "node.started", "node": "fan"}) for i in range(3)) + "\n")
(m / "SYNTHETIC.txt").write_text(
    "CLEARLY SYNTHETIC (bd_2026-11-13-33h): MF1 regression rows — done parent, raw partial\n"
    "child (cap_exhausted) and raw cancelled child side by side. No live launch of this graph\n"
    "produced these rows; the frozen shelf fixture is preserved byte-for-byte elsewhere.\n"
    "Node efp stamps are REAL (wfcommon.efp at materialization) so run_state reads `done`\n"
    "for the right reason: valid, complete, terminal.\n")
out["mf1_run_id"] = mf1_id
out["mf1_kind"] = "synthetic_hand_seeded"

# -- terminal wait for the engine seed (read model, not a file guess) -----
if a.wait_run:
    deadline = time.monotonic() + a.wait_s
    last = None
    while time.monotonic() < deadline:
        st = wfcommon.run_state(Path(root / a.wait_run), telemetry=False)
        last = st.get("status")
        if last in ("done", "failed", "stopped"):
            break
        time.sleep(0.4)
    if last not in ("done", "failed", "stopped"):
        print(f"NOT_TERMINAL: {a.wait_run} status={last}", file=sys.stderr)
        sys.exit(1)
    out["thr_final_status"] = last

print(json.dumps(out))
