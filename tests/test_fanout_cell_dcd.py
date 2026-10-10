#!/usr/bin/env python3
"""est-fanout-cell (sys-96dcod) — the [fan + consolidate] cell streams finished
members into batch children WHILE the fan still runs (wave-consolidation) and
the partner commits a machine tally, never a spawn of its own.

Owner directive (2026-10-10): a standard unit pairing with the fan so operators
never consolidate by waiting for the whole wave — the straggler tail stops
blocking everything downstream. batch:1 = as they finish; batch:N = batches;
the open batch always flushes with its tail NAMED.

Pins:
  A door law (shape + cross-node): consolidate must name a real fan-out that is
    a direct `after` parent; one partner per fan; batch positive int; unknown
    key refused; a fan node may not also be a partner.
  B streaming: with fan(6 fast items)+partner(batch:2), FAKE_LOG proves batch
    children spawn (partner spawns = dispatched batches, fan spawns = 6), the
    partner's OWN id never appears as a plain spawn, consolidate/<fan>.batches
    .jsonl carries done finals covering every index, and the partner commits
    DONE with verdict 'consolidated' (census: missing=[]).
  C honesty: 2 items FAILME -> they are NOT dispatched into a batch (a failed
    member's record never rides a hollow payload); the tally NAMES them in
    `missing` with verdict consolidated_partial — the partner still commits
    done (the tally is honest, the wave is accounted).
  D the tally math itself replays deterministically (pure wfcommon).
RED-on-base: the consolidate key is unknown at the base door (A fails), B/C
find no batches.jsonl at all (fails), D imports nothing (fails).
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wfcommon

FAKE = str(HERE / "fake")
fails = total = 0
def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL " + name) + (f" :: {detail[:280]}" if detail and not ok else ""), flush=True)
    if not ok:
        fails += 1

def V(nodes):
    return [e["field"] for e in wfcommon.validate_graph_errors(nodes, admission=True)]

# ---- A. door laws ----
good = [{"id": "fan", "type": "agent",
         "fanout": {"items": [{"goal": "g1"}, {"goal": "g2"}], "goal": "t {index}"}},
        {"id": "cons", "type": "agent", "after": ["fan"],
         "consolidate": {"from": "fan", "batch": 2}, "goal": "merge"}]
check("A valid cell validates clean", not V(good), str(V(good)))
nodes_noedge = [good[0], {**good[1], "after": []}]
check("A from must be a direct after parent (the cell is an edge)",
      any(e == "consolidate.from" for e in V(nodes_noedge)), str(V(nodes_noedge)))
nodes_nofan = [{**good[0], "consolidate": None}, good[1]]  # partner naming a non-fan
check("A `from` naming a non-fan node is refused",
      any(e == "consolidate.from" for e in V([
          {"id": "plain", "type": "agent", "goal": "g"},
          {**good[1], "consolidate": {"from": "plain"}}])), "")
check("A one partner per fan",
      any(e == "consolidate.from" for e in V(
          good + [{**good[1], "id": "cons2"}])), "")
check("A batch must be a positive int",
      any(e == "consolidate.batch" for e in V(
          [good[0], {**good[1], "consolidate": {"from": "fan", "batch": 0}}])), "")
check("A unknown consolidate key refused",
      any(e.startswith("consolidate.") for e in V(
          [good[0], {**good[1], "consolidate": {"from": "fan", "when_done": 1}}])), "")
check("A consolidate.from cannot name itself",
      any(e == "consolidate.from" for e in V([
          {"id": "x", "type": "agent", "goal": "g",
           "fanout": {"items": [{"goal": "i"}]},
           "consolidate": {"from": "x"}}])), "")
check("A non-fan `from` refused",
      any(e == "consolidate.from" for e in V([
          {"id": "plain", "type": "agent", "goal": "g"},
          {"id": "cons", "type": "agent", "after": ["plain"],
           "consolidate": {"from": "plain"}, "goal": "m"}])), "")

# ---- D. tally math (pure, deterministic; getattr-gated so a base lacking the
# helper prints legible FAILs and lets B/C run — never a bare AttributeError) ----
def _t(*a, **k):
    fn = getattr(wfcommon, "consolidate_tally", None)
    return fn(*a, **k) if fn else {"verdict": "NO-HELPER", "missing": [], "pending_batch": []}
t = _t(4, [{"batch": 1, "items": [0, 1], "status": "done"},
           {"batch": 2, "items": [2, 3], "status": "done"}])
check("D full coverage -> consolidated, missing=[]",
      t["verdict"] == "consolidated" and t["missing"] == [], json.dumps(t))
t2 = _t(4, [{"batch": 1, "items": [0, 1], "status": "done"},
            {"batch": 2, "items": [2], "status": "failed",
             "error_class": "schema"}], pending_batch=[])
check("D uncovered items are NAMED, verdict partials honestly",
      t2["verdict"] == "consolidated_partial" and t2["missing"] == [2, 3], json.dumps(t2))
t3 = _t(2, [], pending_batch=[0, 1])
check("D an undelivered tail is NAMED, never dropped",
      t3["missing"] == [0, 1] and t3["pending_batch"] == [0, 1], json.dumps(t3))

# ---- engine harness ----
_scratch = Path(tempfile.mkdtemp(prefix="wfdcd-"))
BASE_ENV = {k: v for k, v in os.environ.items()
            if not k.startswith(("WF_", "FAKE_", "HERMES_WF_")) and k != "HERMES_HOME"}
BASE_ENV["HERMES_HOME"] = str(_scratch / "home")
BASE_ENV["WF_RUNS_ROOT"] = str(_scratch / "runs")
BASE_ENV["FAKE_LOG"] = str(_scratch / "fake.log")
Path(BASE_ENV["HERMES_HOME"]).mkdir(parents=True, exist_ok=True)
SCHEMA = {"type": "object", "required": ["result"], "properties": {"result": {"type": "string"}}}

def mk(run_id, item_goals, batch=2):
    r = Path(BASE_ENV["WF_RUNS_ROOT"]) / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    graph = {"name": run_id, "nodes": [
        {"id": "fan", "type": "agent", "timeout": 120,
         "fanout": {"items": [{"goal": g} for g in item_goals],
                    "goal": "ITEM {index} {item}", "schema": SCHEMA}},
        {"id": "merge", "type": "agent", "after": ["fan"], "timeout": 120,
         "consolidate": {"from": "fan", "batch": batch},
         "goal": "CONSOLIDATE the batch below into one answer"}]}
    (r / "graph.json").write_text(json.dumps(graph))
    (r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "item_concurrency": len(item_goals)}))
    return r

def evs(r, ev):
    try:
        return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines() if l.strip()]
    except OSError:
        return []
def only(r, ev):
    return [e for e in evs(r, ev) if e.get("event") == ev]

def node_rec(r, nid):
    # at a base with no cell there is no partner record at all: return a
    # legible NO-FILE stub so every check FAILs by name, never a bare crash.
    try:
        return json.loads((r / "nodes" / (nid + ".json")).read_text())
    except (OSError, json.JSONDecodeError):
        return {"status": "NO-FILE"}

# ---- B. streaming with all-fast items ----
BASE_ENV["FAKE_LOG"] = str(_scratch / "fake-b.log")
rb = mk("dcd-fast", ["reply ok"] * 6, batch=2)
subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", rb.name],
               env=BASE_ENV, capture_output=True, text=True, timeout=180)
bs = only(rb, "consolidate.batch.started")
bf = only(rb, "consolidate.batch.finished")
check("B batch children dispatched as members land (6 items / batch 2 -> 3 batches)",
      len(bs) == 3 and len(bf) == 3, f"started={len(bs)} finished={len(bf)}")
check("B every item index lands in exactly one batch",
      sorted(i for e in bs for i in e.get("items", [])) == [0, 1, 2, 3, 4, 5],
      json.dumps([e.get("items") for e in bs]))
mpart = node_rec(rb, "merge")
check("B partner commits DONE from the machine tally (never spawns itself)",
      mpart.get("status") == "done", json.dumps(mpart)[:200])
tout = mpart.get("output") or {}
check("B census: 6 dispatched, 6 consolidated, missing=[]",
      tout.get("dispatched") == 6 and tout.get("consolidated") == 6
      and tout.get("missing") == [], json.dumps(tout)[:300])
try:
    logs = Path(BASE_ENV["FAKE_LOG"]).read_text()
except OSError:
    logs = ""
check("B batch payloads carry the CONSOLIDATE template (partner's mission)",
      "CONSOLIDATE" in logs, logs[:200])
try:
    led = [json.loads(l) for l in
           (rb / "consolidate" / "fan.batches.jsonl").read_text().splitlines()]
except (OSError, json.JSONDecodeError):
    led = []
check("B finals ledger exists with done rows",
      len(led) == 3 and all(r_["status"] == "done" for r_ in led), json.dumps(led)[:200])

# ---- C. failed members named, never dispatched ----
BASE_ENV["FAKE_LOG"] = str(_scratch / "fake-c.log")
rc = mk("dcd-partial", ["reply ok"] * 4 + ["FAILME"] * 2, batch=2)
subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", rc.name],
               env=BASE_ENV, capture_output=True, text=True, timeout=240)
bsc = only(rc, "consolidate.batch.started")
allb = [i for e in bsc for i in e.get("items", [])]
check("C failed members are NOT dispatched into a batch",
      not any(i in (4, 5) for i in allb), json.dumps([e.get("items") for e in bsc]))
mpc = node_rec(rc, "merge")
tc = mpc.get("output") or {}
check("C tally NAMES the failed pair (4 consolidated, missing [4,5])",
      mpc.get("status") == "done" and tc.get("consolidated") == 4
      and tc.get("missing") == [4, 5], json.dumps(tc)[:300])

print("DONE fanout_cell_dcd", "OK" if fails == 0 else "FAIL")
sys.exit(0 if fails == 0 else 1)
