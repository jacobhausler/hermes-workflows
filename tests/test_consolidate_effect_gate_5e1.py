#!/usr/bin/env python3
"""The fan+consolidate partner's boundary `done` must pass the effect gate.

The incident class (ledger audits): a run's terminal WORKFLOW_DONE fired over a
write-gated lane that wrote nothing — the lane declared `effects` postconditions
and the record carried no proof. The commit-edge gate (#56) covers the agent
solo, fan-out aggregate and echo paths; the consolidate partner's wave-boundary
tally commit was the fourth done path and it bypassed the gate: a partner
declaring `effects` committed done with zero measured rows, and the run closed
run.done over the empty lane.

The contract is the #56 law, unchanged: a done whose declared file row the
runner cannot prove from bytes under the run dir DEMOTES to failed
(error_class 'effect_receipt', 'effect_receipt_unproven: ...'), the measured
facts ride on the failed record, and run.done never fires. A proven row commits
done with the measured facts on the record. No `effects` key = byte-identical
(the fanout-cell suite pins that shape).

RED proof (run before the fix): case (a) FAILS — the partner commits done with
no effect_receipts and the run closes WORKFLOW_DONE over the never-written row.

Run: env -u WF_RUNS_ROOT -u HERMES_HOME python3 tests/test_consolidate_effect_gate_5e1.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAKE = str(ROOT / "tests" / "fake")
SCRATCH = Path(tempfile.mkdtemp(prefix="wfcge-"))
ENV = {k: v for k, v in os.environ.items()
       if not k.startswith(("WF_", "FAKE_", "HERMES_WF_")) and k != "HERMES_HOME"}
ENV.update(HERMES_HOME=str(SCRATCH / "home"), WF_RUNS_ROOT=str(SCRATCH / "runs"),
           FAKE_LOG=str(SCRATCH / "fake.log"))
Path(ENV["HERMES_HOME"]).mkdir(parents=True)
SCHEMA = {"type": "object", "required": ["result"],
          "properties": {"result": {"type": "string"}}}

fails = total = 0
def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL " + name) + (f" :: {str(detail)[:280]}" if detail and not ok else ""), flush=True)
    if not ok:
        fails += 1

def mk(run_id, nodes):
    r = Path(ENV["WF_RUNS_ROOT"]) / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps(
        {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 60}))
    return r

def cell(run_id, fan_goal, partner_extra):
    return mk(run_id, [
        {"id": "fan", "type": "agent", "timeout": 120, "goal": fan_goal,
         "fanout": {"items": ["g1"], "schema": SCHEMA}},
        {"id": "merge", "type": "agent", "after": ["fan"], "timeout": 120,
         "goal": "merge", "consolidate": {"from": "fan", "batch": 1},
         **partner_extra},
    ])

def wf(run_id):
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                          env=ENV, capture_output=True, text=True,
                          timeout=240, cwd=str(ROOT)).stdout

def rec(r, nid):
    p = r / "nodes" / f"{nid}.json"
    return json.loads(p.read_text()) if p.exists() else {}

# ---- (a) the incident: partner declares an effects row nobody wrote.
#         The boundary done must DEMOTE to typed failed; run.done never fires.
ra = cell("cge-a", "ITEM {index} {item}",
          {"effects": [{"file": "work/merge/never.json"}]})
out_a = wf("cge-a")
rec_a = rec(ra, "merge")
check("a1 unproven partner row demotes the boundary commit to failed",
      rec_a.get("status") == "failed" and rec_a.get("error_class") == "effect_receipt",
      f"status={rec_a.get('status')} class={rec_a.get('error_class')}")
check("a2 the refusal names the unprovable row",
      "effect_receipt_unproven" in (rec_a.get("error") or "")
      and "work/merge/never.json" in (rec_a.get("error") or ""), rec_a.get("error"))
check("a3 the measured facts ride on the FAILED record",
      isinstance(rec_a.get("effect_receipts"), list)
      and rec_a["effect_receipts"][0]["ok"] is False, rec_a.get("effect_receipts"))
check("a4 WORKFLOW_DONE never fires over the empty write-gated lane",
      "WORKFLOW_DONE" not in out_a, out_a.strip()[:200])
check("a5 run.done never enters the ledger",
      "run.done" not in (ra / "events.jsonl").read_text()
      if (ra / "events.jsonl").exists() else False, "no events")

# ---- (b) the proven twin: the batch child publishes the artifact; the partner
#         commits done WITH the measured rows, run.done fires.
rb = cell("cge-b", "EFFECT-EMIT out/x.json BYTES=64 ITEM {index} {item}",
          {"effects": [{"file": "work/fan.0/out/x.json"}]})
out_b = wf("cge-b")
rec_b = rec(rb, "merge")
check("b1 proven partner row commits done", rec_b.get("status") == "done", rec_b)
check("b2 the record carries the runner-measured row",
      isinstance(rec_b.get("effect_receipts"), list)
      and all(x["ok"] for x in rec_b["effect_receipts"]), rec_b.get("effect_receipts"))
check("b3 WORKFLOW_DONE fires over the proven lane", "WORKFLOW_DONE" in out_b, out_b.strip()[:200])

# ---- (c) the fourth-path gap (ra-pr R8): a partner DECLARING bead_close is a
#          commit edge too — with no readable store the close claim cannot be
#          proven, so the boundary done must DEMOTE, class bead_close.
rc_cell = cell("cge-c", "ITEM {index} {item}",
               {"bead_close": {"store": str(SCRATCH / "no-store"), "id": "nope-1"}})
out_c = wf("cge-c")
rec_c = rec(rc_cell, "merge")
check("c1 declared bead_close on the partner is read back and demotes unproven",
      rec_c.get("status") == "failed" and rec_c.get("error_class") == "bead_close",
      f"status={rec_c.get('status')} class={rec_c.get('error_class')}")
check("c2 the refusal names the unproven bead",
      "bead_close_unproven" in (rec_c.get("error") or "") and "nope-1" in (rec_c.get("error") or ""),
      rec_c.get("error") or "")
check("c3 run.done never fires over an unproven partner close",
      "WORKFLOW_DONE" not in out_c, out_c.strip()[:200])

print(f"{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
