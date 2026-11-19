#!/usr/bin/env python3
"""bd_2026-11-13-az9 — the reconcile-pass stamp law, behavior-first.

The evidence: a 4,343-row quorum storm and 16 provably zero-info owner
re-notices, all traced to reconcile passes (respawn boot scans, settled-failed
re-entries, straggler watchdog re-evals) re-firing on SETTLED states. The law
this pins (module section at wf.RECONCILE_STAMP_FILE):

  T1 seed    — a pass with no stamp SEEDS it: 0 notices.
  T2 (AC-A)  — a pass over an unchanged settled run writes ONLY the touched
               stamp: 0 notices, exactly one run.reconcile audit row.
  T3          idempotent: two consecutive passes converge (same ident, still
               0 notices; the stamp's vector/rev fields byte-stable).
  T4 (AC-B)  — the first pass after a NODE TRANSITION writes exactly ONE
               run.reconciled notice naming the move (old->new per node).
  T5 (AC-B)  — the first pass after an AMENDMENT (rev steps) writes exactly
               ONE naming notice.
  T6          the explicit-unknown law: a crash re-paint (a DIFFERENT node
               torn, both views UNKNOWN) moves no disposition cell — the pass
               finds explicit-unknowns and only updates the stamp.
  T7 (AC-C)  — the s34 storm fixture (s-family re-run): a quorum storm of
               stragglers with retry re-stamps emits <= 2 owner notices for
               the storm, and a settled re-drive of the same fixture adds
               ZERO notices (one audit row only).

Run: python3 tests/test_reconcile_pass_az9.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HOME = HERE / "home-az9"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " ) + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

if HOME.exists():
    shutil.rmtree(HOME)
RUNS = HOME / "workflows"
RUNS.mkdir(parents=True)

NODES = [{"id": "a", "type": "agent", "goal": "ga"},
         {"id": "b", "type": "agent", "goal": "gb"}]
BYID = {n["id"]: n for n in NODES}


def mkrun(name, records):
    """A settled run dir: committed graph, owner stamp, the named node records."""
    run = RUNS / name
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    (run / "graph.json").write_text(json.dumps({"name": name, "nodes": NODES}))
    (run / "run.json").write_text(json.dumps({"owner": {"session_id": "az9-session"}}))
    (run / "wake_protocol").write_text("runner-authored/v1")
    for nid, rec in records.items():
        rec = dict(rec)
        rec["efp"] = wfcommon.efp(BYID, BYID[nid])
        rec["fp_rule_version"] = wfcommon.FP_RULE_VERSION
        (run / "nodes" / f"{nid}.json").write_text(json.dumps(rec))
    return run


def events(run, ev):
    p = run / "events.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if isinstance(e, dict) and e.get("event") == ev:
            out.append(e)
    return out


def wakes(run, ev=None):
    p = run / "wake.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if isinstance(e, dict) and (ev is None or e.get("event") == ev):
            out.append(e)
    return out


SETTLED = {"a": {"status": "failed", "error": "boom", "error_class": "timeout"},
           "b": {"status": "done", "output": {"result": "ok"}}}

# ---- T1/T2/T3: seed, unchanged settled pass, convergence --------------------------
r1 = mkrun("az9-settled", json.loads(json.dumps(SETTLED)))
v1 = wf.reconcile_pass(r1)
check("T1 first pass seeds: changed=False first=True noticed=False",
      v1["first"] and not v1["changed"] and not v1["noticed"], json.dumps(v1))
check("T1 seed: ZERO notices", len(wakes(r1)) == 0, str(wakes(r1)))
check("T1/T2 seed pass writes exactly one run.reconcile audit row",
      len(events(r1, "run.reconcile")) == 1, str(events(r1, "run.reconcile")))
stamp1 = json.loads((r1 / "reconcile.stamp.json").read_text())
check("T2 stamp total: every declared node has an explicit row",
      set(stamp1["vector"]) == {"a", "b"}, json.dumps(stamp1))
check("T2 stamp shape keys", {"ident", "rev", "vector", "touched_ts", "notified_ts"}
      <= set(stamp1), json.dumps(sorted(stamp1)))
check("T2 notified_ts null before any change-notice", stamp1["notified_ts"] is None)
time.sleep(0.01)
v2 = wf.reconcile_pass(r1)
check("T2 unchanged settled pass: changed=False, no notice",
      not v2["changed"] and not v2["first"] and not v2["noticed"], json.dumps(v2))
check("T2 unchanged settled pass: still ZERO notices",
      len(wakes(r1)) == 0, str(wakes(r1)))
check("T2 unchanged settled pass: exactly ONE audit row appended (two total)",
      len(events(r1, "run.reconcile")) == 2, str(len(events(r1, "run.reconcile"))))
stamp2 = json.loads((r1 / "reconcile.stamp.json").read_text())
check("T3 convergence: ident and vector byte-stable across the two passes",
      stamp2["ident"] == stamp1["ident"] and stamp2["vector"] == stamp1["vector"],
      json.dumps(stamp2))
check("T3 convergence: only the touched stamp moved",
      stamp2["touched_ts"] >= stamp1["touched_ts"], json.dumps(stamp2))

# ---- T4: node transition -> exactly one naming notice ------------------------------
rec_b = json.loads((r1 / "nodes" / "b.json").read_text())
rec_b.update({"status": "failed", "error": "boom2", "error_class": "timeout"})
rec_b.pop("output", None)
(r1 / "nodes" / "b.json").write_text(json.dumps(rec_b))
v3 = wf.reconcile_pass(r1)
check("T4 first pass after a node transition reports changed=True",
      v3["changed"] and not v3["first"], json.dumps(v3))
check("T4 transition row names the node and the exact move",
      {"node": "b", "from": "SUCCEEDED", "to": "FAILED"} in v3["diff"], json.dumps(v3["diff"]))
w = wakes(r1, "run.reconciled")
check("T4 EXACTLY ONE run.reconciled notice", len(w) == 1, str(w))
if w:
    t = (w[0].get("text") or "").replace('\\"', '"')
    check("T4 the notice names what changed (diff rides the identity key, inert-quoted)",
          '"node":"b"' in t and '"from":"SUCCEEDED"' in t and '"to":"FAILED"' in t,
          w[0].get("text", "")[:300])
check("T4 the audit row carries the diff", events(r1, "run.reconcile")[-1]["changed"]
      and events(r1, "run.reconcile")[-1]["diff_count"] == 1,
      str(events(r1, "run.reconcile")[-1]))
v4 = wf.reconcile_pass(r1)
check("T3 second pass over the moved state converges quiet",
      not v4["changed"] and not v4["noticed"] and len(wakes(r1, "run.reconciled")) == 1,
      json.dumps(v4))

# ---- T5: amendment (rev steps) -> exactly one naming notice -----------------------
with open(r1 / "events.jsonl", "a") as f:
    f.write(json.dumps({"event": "graph.amended", "at": "2026-11-19T00:00:00+00:00"}) + "\n")
v5 = wf.reconcile_pass(r1)
check("T5 first pass after an amendment reports changed=True",
      v5["changed"] and not v5["first"], json.dumps(v5))
check("T5 the diff names the amendment step",
      any("rev" in row for row in v5["diff"]), json.dumps(v5["diff"]))
check("T5 EXACTLY ONE additional notice (two total)",
      len(wakes(r1, "run.reconciled")) == 2, str(len(wakes(r1, "run.reconciled"))))
check("T5 settled notice stamps notified_ts", json.loads((r1 / "reconcile.stamp.json")
      .read_text())["notified_ts"] is not None)

# ---- T6: explicit-unknown crash re-paint moves nothing -----------------------------
# The storm's class: the crash scene re-paints between passes — a torn record
# disappears, another stays torn — while EVERY cell remains the same EXPLICIT
# UNKNOWN. No disposition cell moved, so the pass updates the stamp and says
# nothing: the re-paint a naive reader calls "state changed" is disposition-
# invariant, and the law reads the table, not the files.
r2 = mkrun("az9-torn", {"a": {"status": "running"}, "b": {"status": "running"}})
v6a = wf.reconcile_pass(r2)                       # seed: both cells UNKNOWN
check("T6 seed over an all-UNKNOWN vector stays quiet",
      not v6a["noticed"] and len(wakes(r2, "run.reconciled")) == 0, json.dumps(v6a))
(r2 / "nodes" / "a.json").unlink()                # a's corpse vanishes (pending=UNKNOWN)
v6 = wf.reconcile_pass(r2)
check("T6 crash re-paint (UNKNOWN cells, same vector) is stamp-only",
      not v6["changed"] and not v6["noticed"] and len(wakes(r2, "run.reconciled")) == 0,
      json.dumps(v6))
check("T6 the stamp vector keeps UNKNOWN explicit for BOTH shapes",
      json.loads((r2 / "reconcile.stamp.json").read_text())["vector"]
      == {"a": "UNKNOWN", "b": "UNKNOWN"},
      "vector stayed inside the total table")

# ---- T7: the s34 storm fixture — s-family re-run -----------------------------------
# Geometry from the incident: a fan-out fat tail where the stragglers RETRY (their
# launch stamps get overwritten while the open pair holds — the re-stamp class that
# re-armed the old latch into the 4,343-row / 16-re-notice storm). Under the new
# law the re-stamp class writes AUDIT rows only; the storm costs <= 2 owner
# notices, and re-driving the settled fixture adds none.
FAKE = str(HERE / "fake")
storm = RUNS / "az9-s34-storm"
(storm / "nodes").mkdir(parents=True)
(storm / "gates").mkdir()
items = [{"goal": "reply ok"}] * 4 + [{"goal": "QSLEEP 6 FAILME reply ok"}] * 2
(storm / "graph.json").write_text(json.dumps({"name": storm.name, "nodes": [
    {"id": "fan", "type": "agent", "timeout": 120,
     "fanout": {"items": items,
                "schema": {"type": "object", "properties": {"result": {"type": "string"}},
                           "required": ["result"]}}},
    # the storm run's tail: a join that dies, so the fixture lands the run in
    # the settled-failed state the boundary-pass law owns (the re-run below
    # re-enters exactly that branch).
    {"id": "join", "type": "agent", "after": ["fan"], "goal": "FAILME join"}]}))
(storm / "run.json").write_text(json.dumps({
    "hermes_bin": FAKE, "item_concurrency": 6, "max_seats": 0,
    "owner": {"session_id": "az9-storm-session"},
    "straggler_grace_s": 2, "straggler_poll_s": 0.5}))
env = dict(os.environ, WF_SEATS_DIR=str(HOME / "seats"), FAKE_LOG=str(HOME / "fake.log"))
cp = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", storm.name],
                    env=env, capture_output=True, text=True, timeout=300)
storm_events = [json.loads(l) for l in
                (storm / "events.jsonl").read_text().splitlines() if l.strip()]
storm_lines = [e for e in storm_events if e.get("event") == "fanout.stragglers"]
straggler_spawns = sum(1 for l in (HOME / "fake.log").read_text().splitlines()
                       if "QSLEEP" in l)
check("T7 non-vacual: the storm shape ran (4 straggler spawns = 2 items x 1 retry) "
      "and the cohort tripped", straggler_spawns >= 4 and len(storm_lines) >= 1,
      f"spawns={straggler_spawns} lines={len(storm_lines)} out={cp.stdout[:200]}")
owner_wakes = wakes(storm)
storm_notices = [w0 for w0 in owner_wakes
                 if w0.get("event") in ("fanout.stragglers", "run.reconciled")]
check("T7 s34 storm: <= 2 owner notices for the storm (straggler-class + reconcile)",
      len(storm_notices) <= 2,
      json.dumps([(w0.get("event"), str(w0.get("text"))[:60]) for w0 in owner_wakes]))
check("T7 the straggler cohort is noticed EXACTLY once (storm's single alarm)",
      len(wakes(storm, "fanout.stragglers")) == 1,
      str(len(wakes(storm, "fanout.stragglers"))))
check("T7 no reconcile-notice rode the storm itself (commit edges owned it)",
      len(wakes(storm, "run.reconciled")) == 0,
      str(wakes(storm, "run.reconciled")))
if len(storm_lines) >= 2:
    check("T7 the retry re-stamp class writes audit-only rows (noticed:false) "
          "— the 4,343-row storm re-run silent on the wake channel",
          storm_lines[0].get("noticed") is True
          and all(e.get("noticed") is False for e in storm_lines[1:]),
          json.dumps([(e.get("done"), e.get("open"), e.get("noticed"))
                      for e in storm_lines]))
check("T7 audit rows keep the full cohort record (rows were NOT cut, wakes were)",
      all("noticed" in e for e in storm_lines), json.dumps(storm_lines[:1]))
# s-family RE-RUN: re-drive the settled fixture — reconcile passes over unchanged
# settled state: zero new notices, one audit row PER PASS (engine-level AC-A: the
# respawn runs the boot pass and the settled-failed boundary pass = two passes).
before_wakes = len(wakes(storm))
before_audits = len(events(storm, "run.reconcile"))
blocked_before = len(events(storm, "run.blocked"))
cp2 = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", storm.name],
                     env=env, capture_output=True, text=True, timeout=120)
after_wakes = wakes(storm)
check("T7 re-run of the settled fixture: ZERO new notices",
      len(after_wakes) == before_wakes,
      f"before={before_wakes} after={len(after_wakes)} out={cp2.stdout[:200]}")
check("T7 re-run added pass audit rows and nothing louder — the boundary pass "
      "re-checked and stayed quiet (NO second run.blocked, NO re-notice; the "
      "boot pass rides the respawn record and is order-robust, so the audit "
      "delta is pinned >=1 with the LAST row provably quiet)",
      len(events(storm, "run.reconcile")) >= before_audits + 1
      and len(events(storm, "run.blocked")) == blocked_before
      and events(storm, "run.reconcile")[-1].get("first") is False
      and events(storm, "run.reconcile")[-1].get("changed") is False,
      f"before={before_audits} after={len(events(storm, 'run.reconcile'))} "
      f"blocked={blocked_before}->{len(events(storm, 'run.blocked'))}")
check("T7 re-run still re-EMITS the lifecycle line (spawner contract untouched)",
      "WORKFLOW_FAILED" in cp2.stdout, cp2.stdout[:200] + cp2.stderr[:200])

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
