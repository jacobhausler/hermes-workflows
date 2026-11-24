#!/usr/bin/env python3
"""State-matrix fixture materializer for the CHAT proof case (bd_2026-11-13-1bm).

Materializes the in-chat card's state rows THROUGH the repo's own read model
(the same run-dir grammar seed_fixture.py/seed_graph.py use, real wfcommon.efp
hashes, so run_state derives each word for the right reason — never a painted
costume). Engine seeds cover `held` and `Finished` as REAL door runs; this file
supplies the states no zero-token bench launch can stage deterministically:

  running      — done seed + pending tail; runner.lock left OPEN (absent flock
                 at seed time, honest 'interrupted' until the driver spawns its
                 flock keeper, then run_state reads `running` for the right
                 reason: a live process holds the admission lock). No work is
                 dispatched and no fake activity stamp is painted — the card
                 says exactly what it sees ('Running · activity unknown' at
                 worst). SYNTHETIC-LIVE.txt says so.
  failed       — one agent record failed with error_class provider_error.
  partial      — all-committed run closed on a run.partial event (est-3acn
                 vocabulary: the event is the fact).
  interrupted  — the covr shape: an unstamped (efp "") record fails replay
                 validity (#134); unfinished work, no live runner.
  cancelled    — one record failed with error_class cancelled (node_rec
                 re-reads it pending, re-drivable, #7) over a run.stopped
                 event: stop is history, not failure, and the card census
                 must say `cancelled`, never `failed`.

Every fixture dir carries SYNTHETIC.txt (mf1 precedent). A pinned future ts
(2099) keeps the bench's first-page census stable. Prints one JSON line with
the fixture ids plus the running row's lock path (the driver's keeper target).

Run: python3 seed_chat.py --repo R --runs-root DIR [--wait-run ID --wait-s S]
"""
import argparse
import json
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--runs-root", required=True)
ap.add_argument("--wait-run", default=None, help="engine run to wait for, terminal via run_state")
ap.add_argument("--wait-s", type=float, default=90.0)
a = ap.parse_args()

root = Path(a.runs_root)
root.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, a.repo)
import wfcommon  # the repo read model — the SAME efp the door would have stamped

TS = "2099-11-19T00:00:00+00:00"  # 2099 anchor (mf1 precedent): sorts first, never claims recency
out = {}

def mkg(id_slug, name, graph, run_started=TS):
    rid = "20990101-000000-%s-1bm" % id_slug
    r = root / rid
    (r / "nodes").mkdir(parents=True, exist_ok=True)
    (r / "graph.json").write_text(json.dumps({"grammar": "wf/1", "name": name, "nodes": graph}))
    (r / "run.json").write_text(json.dumps({"run_id": rid, "name": name,
                                           "started": run_started, "owner": "ui2-proof"}))
    return r, rid, {n["id"]: n for n in graph}

def ev(r, *rows):
    (r / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in rows))

def node(r, byid, nid, **kw):
    rec = {"efp": wfcommon.efp(byid, byid[nid]), "fp_rule_version": wfcommon.FP_RULE_VERSION, **kw}
    (r / "nodes" / f"{nid}.json").write_text(json.dumps(rec))

# -- running: live lock, no dispatched work --------------------------------------
r, out["running"], byid = mkg("run", "chat-running-1bm", [
    {"id": "seed", "type": "echo", "output": {"msg": "synthetic"}},
    {"id": "tail", "type": "echo", "after": ["seed"], "output": {"msg": "synthetic"}}])
node(r, byid, "seed", status="done", output={"msg": "synthetic"})
ev(r, {"ts": TS, "event": "run.started"})
(r / "runner.lock").write_text("")  # the keeper file: the driver flocks it
(r / "SYNTHETIC-LIVE.txt").write_text(
    "Synthetic live row: a driver-spawned flock keeper holds runner.lock (a genuinely "
    "live process, per the #128/#44 liveness law), but no child was ever dispatched — "
    "the card reports the honest activity-unknown word, never an invented stamp.\n")
out["running_lock"] = str(r / "runner.lock")

# -- failed ----------------------------------------------------------------------
r, out["failed"], byid = mkg("fail", "chat-failed-1bm", [{"id": "a", "type": "agent", "goal": "probe"}])
node(r, byid, "a", status="failed", error_class="provider_error", error="400 synthetic provider refusal")
ev(r, {"ts": TS, "event": "run.started"}, {"ts": TS, "event": "node.failed", "node": "a"})
(r / "SYNTHETIC.txt").write_text("synthetic state row (chat case, bd_2026-11-13-1bm)\n")

# -- partial: committed outputs, closed on the cap event --------------------------
r, out["partial"], byid = mkg("part", "chat-partial-1bm", [
    {"id": "a", "type": "echo", "output": {"msg": "synthetic"}},
    {"id": "b", "type": "agent", "after": ["a"], "goal": "never launched"}])
node(r, byid, "a", status="done", output={"msg": "synthetic"})
ev(r, {"ts": TS, "event": "run.started"}, {"ts": TS, "event": "run.partial"})
(r / "SYNTHETIC.txt").write_text("synthetic state row (chat case, bd_2026-11-13-1bm)\n")

# -- interrupted: the covr shape — an unstamped record fails replay validity -------
r, out["interrupted"], byid = mkg("int", "chat-interrupted-1bm", [{"id": "a", "type": "agent", "goal": "probe"}])
(r / "nodes" / "a.json").write_text(json.dumps(
    {"status": "done", "output": {"answer": "ok"}, "efp": "",
     "fp_rule_version": wfcommon.FP_RULE_VERSION}))
ev(r, {"ts": TS, "event": "run.started"})
(r / "SYNTHETIC.txt").write_text("synthetic state row (chat case, bd_2026-11-13-1bm)\n")

# -- cancelled: stop is history, not failure (#7 / WF-02) -------------------------
r, out["cancelled"], byid = mkg("cxl", "chat-cancelled-1bm", [{"id": "a", "type": "agent", "goal": "probe"}])
node(r, byid, "a", status="failed", error_class="cancelled", error="cancelled: stop (synthetic row)")
ev(r, {"ts": TS, "event": "run.started"}, {"ts": TS, "event": "run.stopped"})
(r / "SYNTHETIC.txt").write_text("synthetic state row (chat case, bd_2026-11-13-1bm)\n")

# -- terminal wait for the engine-run sibling (finished frame) --------------------
if a.wait_run:
    rid = Path(a.wait_run).name
    deadline = time.monotonic() + a.wait_s
    while time.monotonic() < deadline:
        st = wfcommon.run_state(root / rid) if (root / rid).is_dir() else None
        if st and st["status"] in ("done", "failed", "stopped", "partial"):
            break
        time.sleep(0.4)
    else:
        print(f"REFUSED: wait-run {a.wait_run} never terminated", file=sys.stderr)
        sys.exit(1)
    out["waited_terminal"] = {"run_id": a.wait_run, "status": st["status"]}

print(json.dumps(out))
