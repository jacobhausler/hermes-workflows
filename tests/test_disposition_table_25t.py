#!/usr/bin/env python3
"""est-25t / E15 — the ONE total state->disposition mapping is legible.

The corpus failure this pins: operator docs listed SUCCEEDED/FAILED/CANCELLED/
SKIPPED while the shipped records carry lowercase `done`/`failed` — every
disposition check in the hostile-family battery scored zero because the seat
had to guess a state table that was nowhere total. Pinned here:
  (1) the table is TOTAL over every record-status value the engine writes and
      maps each to a named terminal disposition (unknown is a VALUE, not an
      absence);
  (2) the read model (run_state's per-node view) carries `disposition` for
      every node — one field read, zero substring parsing;
  (3) a torn record (running + matching interruption claim, dead pid) reads
      back with an explicit disposition=unknown — never upgraded to terminal.

Run: cd tests && python3 test_disposition_table_25t.py
"""
import json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
os.environ.setdefault("WF_TEST_DISPO_HOME", str(HERE / "home-dispo25t"))
HOME = Path(os.environ["WF_TEST_DISPO_HOME"])
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

DISPOSITIONS = {"SUCCEEDED", "PARTIAL", "FAILED", "CANCELLED", "SKIPPED", "UNKNOWN"}

# ---------- (1) totality + the mapping itself ----------
check("table is total over the documented domain",
      set(wfcommon.DISPOSITION_BY_STATUS) == {"done", "partial", "failed",
                                              "skipped", "running", "interrupted",
                                              "registered"},
      str(sorted(wfcommon.DISPOSITION_BY_STATUS)))
check("every table value is a named disposition",
      set(wfcommon.DISPOSITION_BY_STATUS.values()) <= DISPOSITIONS)
check("done -> SUCCEEDED", wfcommon.disposition_of("done") == "SUCCEEDED")
check("partial -> PARTIAL (committed, incomplete)",
      wfcommon.disposition_of("partial") == "PARTIAL")
check("failed -> FAILED", wfcommon.disposition_of("failed") == "FAILED")
check("failed+cancelled -> CANCELLED (stop is not failure)",
      wfcommon.disposition_of("failed", "cancelled") == "CANCELLED")
check("skipped -> SKIPPED", wfcommon.disposition_of("skipped") == "SKIPPED")
check("running -> UNKNOWN (torn half is a value, not an absence)",
      wfcommon.disposition_of("running") == "UNKNOWN")
check("interrupted -> UNKNOWN", wfcommon.disposition_of("interrupted") == "UNKNOWN")
check("garbage status -> UNKNOWN, never an exception",
      wfcommon.disposition_of("SUCCEEDED") == "UNKNOWN"
      and wfcommon.disposition_of(None) == "UNKNOWN"
      and wfcommon.disposition_of("") == "UNKNOWN")

# ---------- (2)/(3) read model on a staged run ----------
if HOME.exists():
    shutil.rmtree(HOME)
(HOME / "workflows").mkdir(parents=True)
RUN = HOME / "workflows" / "20261119-dispo25t"
(RUN / "nodes").mkdir(parents=True)

NODES = [{"id": "win", "type": "agent", "goal": "g"},
         {"id": "broke", "type": "agent", "goal": "g"},
         {"id": "torn", "type": "agent", "goal": "g"},
         {"id": "notstarted", "type": "agent", "goal": "g"}]
BYID = {n["id"]: n for n in NODES}
(RUN / "graph.json").write_text(json.dumps({"name": "dispo25t", "nodes": NODES}))
(RUN / "run.json").write_text(json.dumps({"concurrency": 4}))

def stamp(nid, rec):
    n = BYID[nid]
    rec = dict(rec, efp=wfcommon.efp(BYID, n), fp_rule_version=wfcommon.FP_RULE_VERSION)
    (RUN / "nodes" / f"{nid}.json").write_text(json.dumps(rec))

stamp("win", {"status": "done", "output": {"result": "ok"}})
stamp("broke", {"status": "failed", "error": "boom", "error_class": "timeout"})
stamp("torn", {"status": "running", "pid": 999999, "skey": "wf:dispo25t:torn:abcdef.012345",
               "attempt": 0, "spawn": 1, "started": "2026-11-19T00:00:00+00:00",
               "log_path": str(RUN / "logs" / "torn.a0.log")})
(RUN / "interruptions").mkdir()
trec = json.loads((RUN / "nodes" / "torn.json").read_text())
(RUN / "interruptions" / "torn.json").write_text(json.dumps(
    {"claim": {k: trec.get(k) for k in ("pid", "skey", "attempt", "efp", "fp_rule_version")},
     "at": "2026-11-19T00:01:00+00:00", "why": "runner died"}))

st = wfcommon.run_state(RUN, telemetry=False, lock_state=("stale", "no lock"))
views = st["nodes"]
check("every node view carries a disposition (total, no holes)",
      all("disposition" in v for v in views.values()),
      json.dumps({k: sorted(v) for k, v in views.items()}))
check("committed done reads SUCCEEDED", views["win"]["disposition"] == "SUCCEEDED")
check("committed failed reads FAILED", views["broke"]["disposition"] == "FAILED")
check("torn running reads UNKNOWN (never upgraded)",
      views["torn"]["disposition"] == "UNKNOWN", views["torn"]["status"])
check("never-started node is UNKNOWN at the view",
      views["notstarted"]["disposition"] == "UNKNOWN")
check("node_rec surfaces the interruption as an explicit record-level unknown",
      (wfcommon.node_rec(RUN, BYID["torn"], BYID)[1] or {}).get("disposition") == "UNKNOWN")

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
