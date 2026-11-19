#!/usr/bin/env python3
"""E18 (bd_2026-11-13-4hc) — amendment application evidence ships.

The doc map (runtime 01-quickstart + 03-incidents) promised
runs/<run>/nodes/<name>/amendment-applied.json + logs/boundary.log; plugin
1.4.10 wrote none of that. The runner now writes BOTH at application time.

  (1) unit: _evidence_amendments over a seeded amends.jsonl (changed node,
      torn line, added+removed nodes) -> boundary rows named per revision,
      per-node amendment-applied.json carrying the efp movement;
  (2) idempotent: re-running the evidence pass writes nothing new;
  (3) integration: a LIVE runner consumes restart.request at the wave
      boundary and lands the evidence with trigger=wave-boundary alongside
      the graph.amended(ordinal)/graph.reloaded event pair.

Standalone, stdlib-only: PYTHONPATH=<clone> python3 tests/test_amendment_evidence_e18.py
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
sys.path.insert(0, str(BUILD))
import wf

HOME = HERE / "home-amend18"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}

# ------------------------------------------------------------------ (1)+(2)
shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
run = RUNS / "e18-seeded"
(run / "nodes").mkdir(parents=True)
g1 = {"nodes": [
    {"id": "a", "type": "agent", "goal": "ga", "schema": SCHEMA},
    {"id": "b", "type": "agent", "goal": "gb", "after": ["a"], "schema": SCHEMA},
    {"id": "c", "type": "agent", "goal": "gc", "after": ["b"], "schema": SCHEMA},
]}
g2 = json.loads(json.dumps(g1)); g2["nodes"][1]["goal"] = "gb AMENDED"          # rev 1: b changed
g3 = json.loads(json.dumps(g2)); g3["nodes"].remove(g3["nodes"][2])             # rev 3: c removed
g3["nodes"].append({"id": "d", "type": "agent", "goal": "gd", "after": ["b"], "schema": SCHEMA})  # + d added
amends = [json.dumps({"at": "t", "old": g1, "new": g2, "base_revision": "0:x", "cas": False}),
          "{torn amends row without a closing brace",
          json.dumps({"at": "t2", "old": g2, "new": g3, "base_revision": "1:x", "cas": False})]
(run / "amends.jsonl").write_text("\n".join(amends) + "\n")
(run / "graph.json").write_text(json.dumps(g3))
(run / "events.jsonl").write_text(json.dumps({"ts": "t", "event": "run.started"}) + "\n")

wf._evidence_amendments(run, "boot")
bl = run / "logs" / "boundary.log"
check("1 boundary.log written at the promised path", bl.exists())
rows = [json.loads(l) for l in bl.read_text().splitlines()] if bl.exists() else []
check("1 one boundary row per revision, torn line named, in order",
      [(r.get("event"), r.get("rev")) for r in rows]
      == [("amendment.applied", 1), ("amendment.row_torn", 2), ("amendment.applied", 3)],
      json.dumps(rows))
r1 = next((r for r in rows if r.get("rev") == 1), {})
r3 = next((r for r in rows if r.get("rev") == 3), {})
check("1 rev1 names the moved nodes with their efp movement (b changed; c is downstream — efp law)",
      r1.get("trigger") == "boot"
      and [c["id"] for c in r1.get("changed", [])] == ["b", "c"]
      and all(c["from_efp"] != c["to_efp"] for c in r1["changed"])
      and r1.get("unchanged") == ["a"], json.dumps(r1))
check("1 rev3 names added d and removed c",
      r3.get("added") == ["d"] and r3.get("removed") == ["c"], json.dumps(r3))
doc_b = json.loads((run / "nodes" / "b" / "amendment-applied.json").read_text())
check("1 nodes/b/amendment-applied.json carries from/to efp + rev 1",
      doc_b["node"] == "b" and doc_b["amendment_rev"] == 1
      and doc_b["from_efp"] != doc_b["to_efp"] and doc_b["from_efp"] is not None,
      json.dumps(doc_b))
doc_d = json.loads((run / "nodes" / "d" / "amendment-applied.json").read_text())
check("1 added node d evidence has from_efp null (honest add)",
      doc_d["from_efp"] is None and doc_d["to_efp"] and doc_d["amendment_rev"] == 3,
      json.dumps(doc_d))

before = bl.read_text()
wf._evidence_amendments(run, "boot")
check("2 re-run is a no-op (revision already evidenced)", bl.read_text() == before)

# ------------------------------------------------------------------- (3) live
RUN_ID = "e18-live"
run2 = RUNS / RUN_ID
(run2 / "nodes").mkdir(parents=True); (run2 / "gates").mkdir()
gl = {"name": RUN_ID, "nodes": [
    {"id": "slow", "type": "agent", "goal": "QSLEEP 4", "schema": SCHEMA},
    {"id": "late", "type": "agent", "goal": "first", "after": ["slow"], "schema": SCHEMA},
]}
(run2 / "graph.json").write_text(json.dumps(gl))
(run2 / "run.json").write_text(json.dumps(
    {"hermes_bin": FAKE, "concurrency": 2, "node_timeout": 60}))
env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
           FAKE_LOG=str(HOME / "fake.log"))
p = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", RUN_ID],
                     env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def wait_for(pred, timeout=60, tick=0.1):
    end = time.time() + timeout
    while time.time() < end:
        if pred():
            return True
        time.sleep(tick)
    return False
check("3 runner booted over the clean graph (no evidence owed yet)",
      wait_for(lambda: (run2 / "events.jsonl").exists()))
g_new = json.loads(json.dumps(gl)); g_new["nodes"][1]["goal"] = "AMENDED-SECOND"
with open(run2 / "amends.jsonl", "a") as f:
    f.write(json.dumps({"at": "t", "old": gl, "new": g_new,
                        "base_revision": "0:x", "cas": False}) + "\n")
tmp = run2 / "graph.json.tmp"; tmp.write_text(json.dumps(g_new)); os.replace(tmp, run2 / "graph.json")
(run2 / "restart.request").touch()                                    # the door's marker
p.communicate(timeout=90)
bl2 = run2 / "logs" / "boundary.log"
check("3 live-boundary amend landed boundary.log with trigger wave-boundary",
      bl2.exists() and any(
          (rec := json.loads(l)).get("rev") == 1 and rec.get("trigger") == "wave-boundary"
          and [c["id"] for c in rec.get("changed", [])] == ["late"]
          for l in bl2.read_text().splitlines() if l.strip()),
      bl2.read_text() if bl2.exists() else "no boundary.log")
evs = [json.loads(l) for l in (run2 / "events.jsonl").read_text().splitlines() if l.strip()]
check("3 the graph.amended ordinal + graph.reloaded pair is the proof trail",
      any(e.get("event") == "graph.reloaded" for e in evs))
doc_late = run2 / "nodes" / "late" / "amendment-applied.json"
check("3 nodes/late/amendment-applied.json exists (promised path, per-node)",
      doc_late.exists() and json.loads(doc_late.read_text())["amendment_rev"] == 1)
late_rec = json.loads((run2 / "nodes" / "late.json").read_text())
new_byid = {n["id"]: n for n in g_new["nodes"]}
check("3 the amended def actually landed (committed record is efp-current under the NEW graph)",
      late_rec.get("status") == "done"
      and late_rec.get("efp") == wf.efp(new_byid, new_byid["late"]),
      json.dumps(late_rec)[:200])

shutil.rmtree(HOME, ignore_errors=True)
print("RESULT " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
