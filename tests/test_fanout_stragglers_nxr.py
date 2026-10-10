#!/usr/bin/env python3
"""est-fanout-stragglers (sys-nxrhxo) — the fanout.stragglers wake fires exactly
once on a fat-tail cohort and never on a healthy one, through the REAL engine.

Design both offices ratified (threads 1558442494/1558443003, owner directive
1558443586): t0 is the COHORT MEDIAN finish, floor = max(grace, cohort p50 ms);
>=2 items must still be open (a majority already committed needs no smoke — the
quorum law); one wake per driven wave, RE-ARMED by a launch-stamp change (retry
is the straggler's second home). The grace constant is an ENGINE value
(wfcommon.STRAGGLER_GRACE_S=180, census-earned by two independent offices:
36-cohort tail median 153s / p90 5,693s; 34-cohort p90 max/median 4.0).
`run.json straggler_grace_s`/`straggler_poll_s` are LAUNCHER seams for this
test only — FANOUT_KEYS deliberately omits them, so a graph that tries to tune
its own clock fails validation with "unknown key" (peer ruling: a threshold the
timed party can tune is culture, not a sign).

Test geometry (the RED-on-base pair both seats demanded — "didn't look" vs
"nothing to see" must never collapse into one green):
  A healthy cohort (6 fast items)         -> ZERO fanout.stragglers lines,
                                             ZERO straggler wakes.
  B fat tail (4 fast + 2 long QSLEEP)     -> EXACTLY ONE fanout.stragglers
                                             events line (open=[4,5], items=6)
                                             AND exactly ONE wake.jsonl probe
                                             row for the event (owner stamped;
                                             endpoint absent records the typed
                                             missing_endpoint degradation — the
                                             transition-instance identity, not
                                             delivery, is what's pinned).
RED at the pre-PR head: the event name does not exist, so case B fails on the
zero-count line (the healthy case passes on base too — that asymmetry is the
proof that case A's silence is earned, not vacuous).

Runner-authored wake law (PR#97 r5): the wake text is fixed template prose; the
named facts (indices, counts, ages) ride events.jsonl only. This test asserts
the wake.jsonl row carries NO caller text — no item payload leaks into it.
"""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

FAKE = str(HERE / "fake")
fails = total = 0
def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not ok else ""), flush=True)
    if not ok:
        fails += 1

_scratch = Path(tempfile.mkdtemp(prefix="wfnxr-"))
BASE_ENV = {k: v for k, v in os.environ.items()
            if not k.startswith(("WF_", "FAKE_", "HERMES_WF_")) and k != "HERMES_HOME"}
BASE_ENV["HERMES_HOME"] = str(_scratch / "home")
BASE_ENV["WF_RUNS_ROOT"] = str(_scratch / "runs")
BASE_ENV["FAKE_LOG"] = str(_scratch / "fake.log")
Path(BASE_ENV["HERMES_HOME"]).mkdir(parents=True, exist_ok=True)

SCHEMA = {"type": "object", "required": ["result"], "properties": {"result": {"type": "string"}}}

# ---- 0. pure cohort math (stdlib, deterministic ledger replay — the two
# shapes the census named, plus the boundary and fairness laws) ----
# getattr-gated so a pre-fix base prints legible FAIL lines instead of an
# AttributeError crash (the RED pair must show WHICH law is missing).
import wfcommon
_sv = getattr(wfcommon, "straggler_verdict", None)
def _v(fires, *a, **k):
    # fires=True  -> expect a verdict; False -> expect silence AND the function
    #                to exist at all (silence from a missing module is not a law).
    if _sv is None:
        return False
    v = _sv(*a, **k)
    return (v is not None) if fires else (v is None)
T = 1_000_000.0
check("math fat tail fires (4 done, 2 open, age 400s > floor 180)",
      _v(True, T + 400, [T, T + 1, T + 2, T + 3],
         {4: T, 5: T + 0.5}, [60, 61, 59, 60], [4, 5]))
check("math single straggler stays silent (>=2 open is the quorum law)",
      _v(False, T + 9999, [T, T + 1, T + 2, T + 3], {}, [60] * 4, [4]))
check("math queued-never-launched items are scheduling, not squirreling",
      _v(False, T + 99999, [T], {}, [], [1, 2]))
check("math legit-slow cohort raises its own floor (p50 ms 600s > age 400s)",
      _v(False, T + 400, [T], {1: T, 2: T}, [600.0], [1, 2]))
check("math late-launched item is young (aged from launch, never from t0)",
      _v(False, T + 50, [T - 100], {1: T + 45, 2: T + 46}, [10.0], [1, 2]))
check("math boundary is strict (age == grace stays silent)",
      _v(False, T + 180, [T], {1: T, 2: T}, [10.0], [1, 2]))
# Door law (peer ruling): the author cannot tune the clock they're timed by.
_bad = {"name": "x", "nodes": [{"id": "f", "type": "agent",
        "fanout": {"items": [{"goal": "g"}], "straggler_grace_s": 1}}]}
_errs = wfcommon.validate_graph_errors(
    [{"id": "f", "type": "agent",
      "fanout": {"items": [{"goal": "g"}], "straggler_grace_s": 1}}])
check("door refuses fanout.straggler_grace_s as an unknown graph key "
      "(grace lives in run.json meta = launcher seam, never the graph)",
      any("straggler_grace_s" in e["field"] for e in _errs), str(_errs[:2]))

def mk(run_id, goals, grace_s=2, poll_s=0.5):
    r = Path(BASE_ENV["WF_RUNS_ROOT"]) / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    items = [{"goal": g} for g in goals]
    graph = {"name": run_id, "nodes": [
        {"id": "fan", "type": "agent", "timeout": 120,
         "fanout": {"items": items, "schema": SCHEMA}}]}
    (r / "graph.json").write_text(json.dumps(graph))
    # owner stamped as the door's dict shape: notify() writes its probe ledger
    # against it; with no reachable api_server the row records the typed
    # missing_endpoint degradation (the transition instance is what's pinned).
    (r / "run.json").write_text(json.dumps({
        "hermes_bin": FAKE, "item_concurrency": len(goals),
        "owner": {"session_id": "nxr-test-session"},
        "straggler_grace_s": grace_s, "straggler_poll_s": poll_s}))
    return r

def run_wf(r, timeout=120):
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", r.name],
                          env=BASE_ENV, capture_output=True, text=True, timeout=timeout)

def strag_lines(r):
    p = r / "events.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("event") == "fanout.stragglers":
            out.append(e)
    return out

def strag_wakes(r):
    p = r / "wake.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("event") == "fanout.stragglers":
            out.append(e)
    return out

# ---- A. healthy cohort: six fast items, everything lands well inside the floor
ra = mk("nxr-healthy", ["reply ok"] * 6, grace_s=2, poll_s=0.5)
ta = time.time()
run_wf(ra)
la = strag_lines(ra)
check("A healthy cohort: ZERO fanout.stragglers event lines", len(la) == 0,
      f"lines={json.dumps(la)[:200]}")
check("A healthy cohort: ZERO straggler wakes", len(strag_wakes(ra)) == 0)
check("A healthy cohort still completes (not a vacuous green)",
      json.loads((ra / "nodes" / "fan.json").read_text())["status"] == "done")

# ---- B. fat tail: 4 fast + 2 that squirrel 12s (cohort median ~1s, grace 2s)
rb = mk("nxr-fattail", ["reply ok"] * 4 + ["QSLEEP 12 reply ok"] * 2,
        grace_s=2, poll_s=0.5)
tb = time.time()
run_wf(rb)
lb = strag_lines(rb)
check("B fat tail: EXACTLY ONE fanout.stragglers event line", len(lb) == 1,
      f"lines={json.dumps(lb)[:300]}")
if lb:
    e = lb[0]
    check("B names the open pair and the cohort counts",
          e.get("open") == [4, 5] and e.get("done") == 4 and e.get("items") == 6,
          json.dumps({k: e.get(k) for k in ("open", "done", "items")}))
    check("B fires EARLY (age past floor, before the sleepers land): "
          "wake ts precedes run end by >2s of squirrel time",
          e.get("oldest_open_age_s", 0) > 2, str(e.get("oldest_open_age_s")))
    check("B silent-classification field present (budget_cue-derived)",
          isinstance(e.get("silent"), list), str(e.get("silent")))
wb = strag_wakes(rb)
check("B fat tail: EXACTLY ONE straggler wake probe row", len(wb) == 1,
      f"rows={json.dumps(wb)[:300]}")
if wb:
    row = wb[0]
    txt = row.get("text") or ""
    check("B wake row is runner-authored template text (no caller payload)",
          "FAN-OUT STRAGGLERS" in txt and "QSLEEP" not in txt
          and "reply ok" not in txt and "nxr-test-session" not in txt,
          txt[:200])
    check("B run still completes after the smoke (observation, not interference)",
          json.loads((rb / "nodes" / "fan.json").read_text())["status"] == "done")

print("DONE fanout_stragglers_nxr", "OK" if fails == 0 else "FAIL")
sys.exit(0 if fails == 0 else 1)
