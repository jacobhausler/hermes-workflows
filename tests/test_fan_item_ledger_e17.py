#!/usr/bin/env python3
"""E17 (bd_2026-11-13-4hc) — the fan item-level ledger.

T20 deferred item addressing on 'zero attempts in window'; the wave engineers
the state and hostile families miss item-level checks at 100%. The ledger now
ships (layout named at the wf.py E17 block — docs signature == shipped):

  (1) a quarantine row lands at <run>/quarantine/<node>.<i>.jsonl through the
      REAL #61 quarantine call site (mocked /proc observation, real writer);
  (2) every finalized item record carries disposition (disposition_of's total
      table) and, when a quarantine happened, quarantine={rows_path, rows}
      with a path that EXISTS;
  (3) certification stamps receipt_vs_parent {claim_status, output_matches,
      problem, at} onto the item's own record — match, divergence, and
      never-finalized-spawn all leave a durable line.

Standalone, stdlib-only: PYTHONPATH=<clone> python3 tests/test_fan_item_ledger_e17.py
"""
import json, os, shutil, sys
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
sys.path.insert(0, str(BUILD))
import wf

HOME = HERE / "home-fanledger17"
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

shutil.rmtree(HOME, ignore_errors=True)
run = HOME / "run"
(run / "nodes").mkdir(parents=True)
SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}
node = {"id": "wide", "type": "agent", "goal": "fan {item}", "schema": SCHEMA,
        "fanout": {"items_from": "list"}}
byid = {"wide": node}
efp_wide = wf.efp(byid, node)

# ------------------------------------------------ (1) the real call site
meta = {"_run": run}
r = {"pid": 4242, "spawn": 1, "tree_pids": [4243]}
state = {"killed": False}
def alive(pid):
    return not state["killed"]           # live at the walk, dead after the quiesce
def quiesce(*a):
    state["killed"] = True
    return ("dead", [])
with patch.object(wf, "_proc_pids_by_pgid", side_effect=lambda pid: [4242, 4243]), \
     patch.object(wf, "_proc_alive", side_effect=alive), \
     patch.object(wf, "_proctree_tracked", side_effect=lambda m: {}), \
     patch.object(wf, "_spawn_tokens", side_effect=lambda m, n, i: iter([])), \
     patch.object(wf, "_survivors", side_effect=lambda m, t: set()), \
     patch.object(wf, "_proctree_hold_s", side_effect=lambda m: 0), \
     patch.object(wf, "_proctree_kill_proof_s", side_effect=lambda m: 0), \
     patch.object(wf, "_tree_quiesce", side_effect=quiesce), \
     patch.object(wf, "_reap_zombie", side_effect=lambda *a, **k: None):
    verdict = wf._isolate_prior(meta, r, "node", {"node": "wide", "index": 0})
qf = run / "quarantine" / "wide.0.jsonl"
check("1 quarantine row file exists at the documented path", qf.exists(), str(qf))
rows = [json.loads(l) for l in qf.read_text().splitlines()] if qf.exists() else []
stages = [x["stage"] for x in rows]
check("1 call site wrote tree_kill + respawn_reap rows with pids+proof",
      stages == ["node.tree_kill", "node.respawn_reap"]
      and all(x["pids"] == [4242, 4243] for x in rows)
      and rows[1]["proof"] == "dead", json.dumps(rows))
check("1 the reaped prior record got the tree proof stamp",
      r.get("tree_proof") == "dead" and verdict is None, json.dumps(r))

# ------------------------------- (2) commit_item_record disposition + target
wf.commit_item_record(run, node, byid, 0, {"status": "done", "output": {"result": "a"}})
rec0 = json.loads((run / "nodes" / "wide.0.json").read_text())
check("2 finalized item carries disposition SUCCEEDED from the total table",
      rec0.get("disposition") == "SUCCEEDED", json.dumps(rec0)[:200])
check("2 item with a quarantine history names the target that EXISTS",
      rec0.get("quarantine", {}).get("rows_path") == "quarantine/wide.0.jsonl"
      and (run / rec0["quarantine"]["rows_path"]).exists()
      and rec0["quarantine"]["rows"] == 2, json.dumps(rec0.get("quarantine")))
wf.commit_item_record(run, node, byid, 1, {"status": "done", "output": {"result": "b"}})
rec1 = json.loads((run / "nodes" / "wide.1.json").read_text())
check("2 clean item omits quarantine (no phantom target)",
      "quarantine" not in rec1 and rec1.get("disposition") == "SUCCEEDED")
wf.commit_item_record(run, node, byid, 2, {"status": "failed", "error_class": "cancelled",
                                           "error": "stop"})
rec2 = json.loads((run / "nodes" / "wide.2.json").read_text())
check("2 cancelled straggler reads CANCELLED, never FAILED",
      rec2.get("disposition") == "CANCELLED", json.dumps(rec2)[:200])

# ------------------------------------- (3) receipt-vs-parent reconciliation
(run / "nodes" / "wide.3.json").write_text(json.dumps(          # never-finalized spawn record
    {"status": "running", "pid": 9999, "efp": efp_wide, "fp_rule_version": wf.FP_RULE_VERSION}))
results = [{"status": "done", "output": {"result": "a"}},
           {"status": "done", "output": {"result": "DIVERGED"}},
           {"status": "failed", "error_class": "cancelled"},
           {"status": "done", "output": {"result": "z"}}]
good, problems = wf.item_records_certified(run, node, byid, results)
check("3 certification refuses: index1 diverged output, index3 never finalized",
      good is False and sorted(p["index"] for p in problems) == [1, 3],
      json.dumps(problems))
rec0 = json.loads((run / "nodes" / "wide.0.json").read_text())
rec1 = json.loads((run / "nodes" / "wide.1.json").read_text())
check("3 matching item stamped output_matches=True problem=None",
      rec0.get("receipt_vs_parent", {}).get("output_matches") is True
      and rec0["receipt_vs_parent"]["problem"] is None
      and rec0["receipt_vs_parent"]["claim_status"] == "done",
      json.dumps(rec0.get("receipt_vs_parent")))
check("3 diverging item stamped output_matches=False with the problem line",
      rec1.get("receipt_vs_parent", {}).get("output_matches") is False
      and "diverges" in (rec1["receipt_vs_parent"]["problem"] or ""),
      json.dumps(rec1.get("receipt_vs_parent")))
rec4 = json.loads((run / "nodes" / "wide.3.json").read_text())
check("3 never-finalized claim leaves an unfinalized reconciliation line",
      "not a committed fact" in (rec4.get("receipt_vs_parent", {}).get("problem") or ""),
      json.dumps(rec4.get("receipt_vs_parent")))
wf.commit_item_record(run, node, byid, 2, {"status": "failed", "error_class": "cancelled",
                                           "error": "stop"})
wf.commit_item_record(run, node, byid, 3, {"status": "done", "output": {"result": "z"}})
results[1]["output"]["result"] = "b"          # the honest aggregate now claims the committed bytes
good, problems = wf.item_records_certified(run, node, byid, results)
check("3 after finalize + honest claim, certification passes",
      good is True and problems == [], json.dumps(problems))
rec2 = json.loads((run / "nodes" / "wide.2.json").read_text())
check("3 failed claim still leaves its reconciliation line (silent, adjudicated)",
      rec2.get("receipt_vs_parent", {}).get("problem") is None
      and rec2["receipt_vs_parent"]["claim_status"] == "failed",
      json.dumps(rec2.get("receipt_vs_parent")))

# re-certify is a re-stamp, never a refusal
good2, _ = wf.item_records_certified(run, node, byid, results)
check("3 re-certification idempotent", good2 is True)

shutil.rmtree(HOME, ignore_errors=True)
print("RESULT " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
