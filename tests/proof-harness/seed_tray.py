#!/usr/bin/env python3
"""Collection-fold fixture materializer for the tray case (bd_2026-11-13-3gh).

Materializes the clean-finished/attention boundary specimens DIRECTLY as
read-model bytes (no door launch, no tokens, no mocks): each row is the
valid-run trio (graph.json + run.json + nodes/*.json + events.jsonl) with
REAL `efp` stamps computed by the repo's own read model (wfcommon.efp), so
run_state reads every verdict for the right reason:

  done    — the single echo node committed done with a valid efp; the
            ledger's last line is run.finished. The ONLY status the
            'N finished' fold label speaks.
  failed  — the node committed failed (error_class=crashed): attention,
            NEVER counted into the finished label.
  stopped — the last event line is run.stopped: attention, likewise.

`updated` on the row is the events.jsonl mtime (dashboard/_view), so this
script sets a distinct, ordered mtime per row: the fold's updated-DESC
order is deterministic, and the tie law (equal keeps input order) is not
needed for the specimen order.

Every row carries owner.session_id = --owner-sid, so the composer strip
(ownedRuns law) renders THIS ledger for the focused chat. ids are unique
with the --prefix so repeated invocations (6, then +1, then +10) append
without collision.

Prints one JSON line: {"ids": [...], "names": [...], "by_status": {...}}.

Run: python3 seed_tray.py --repo R --runs-root DIR --owner-sid SID \
        --done N [--failed K] [--stopped L] [--prefix P] [--start S]
"""
import argparse
import json
import os
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--runs-root", required=True)
ap.add_argument("--owner-sid", required=True,
                help="owner.session_id to stamp (the focused chat's runtime id)")
ap.add_argument("--done", type=int, default=0)
ap.add_argument("--failed", type=int, default=0)
ap.add_argument("--stopped", type=int, default=0)
ap.add_argument("--prefix", default="trf")
ap.add_argument("--start", type=int, default=0, help="index offset for unique ids")
a = ap.parse_args()

sys.path.insert(0, a.repo)
import wfcommon

root = Path(a.runs_root)
root.mkdir(parents=True, exist_ok=True)

# 2099 clock: the fixtures never claim recency against real runs, and the
# ordering is fully deterministic; events.jsonl mtimes carry `updated`.
BASE_TS = 4102444800  # 2099-11-19T00:00:00Z
iso = lambda t: "2099-11-19T00:%02d:%02d+00:00" % ((t // 60) % 60, t % 60)

graph = {"grammar": "wf/1", "nodes": [{"id": "say", "type": "echo",
                                       "output": {"msg": "fixture"}}]}
byid = {"say": graph["nodes"][0]}

ids, names = [], []
by_status = {"done": [], "failed": [], "stopped": []}
specs = ([("done", i) for i in range(a.done)]
         + [("failed", i) for i in range(a.failed)]
         + [("stopped", i) for i in range(a.stopped)])
for n_i, (status, k) in enumerate(specs):
    idx = a.start + n_i
    rid = "20990101-%06d-%s" % (200000 + idx, a.prefix)
    name = "%s-%s-%03d" % (a.prefix, status, idx)
    r = root / rid
    (r / "nodes").mkdir(parents=True, exist_ok=True)
    (r / "graph.json").write_text(json.dumps(graph))
    ts = BASE_TS + idx * 60
    (r / "run.json").write_text(json.dumps({
        "run_id": rid, "name": name, "started": iso(ts),
        "owner": {"session_id": a.owner_sid, "platform": "ui2-proof"}}))
    rec = {"efp": wfcommon.efp(byid, byid["say"]),
           "fp_rule_version": wfcommon.FP_RULE_VERSION}
    if status == "done":
        rec.update(status="done", output={"msg": "fixture"})
        events = [{"ts": iso(ts), "event": "run.started"},
                  {"ts": iso(ts + 30), "event": "node.committed", "node": "say"},
                  {"ts": iso(ts + 40), "event": "run.finished"}]
    elif status == "failed":
        rec.update(status="failed", error_class="crashed",
                   error="fixture ledger row (ui2-proof tray case)")
        events = [{"ts": iso(ts), "event": "run.started"},
                  {"ts": iso(ts + 30), "event": "node.failed", "node": "say"},
                  {"ts": iso(ts + 40), "event": "run.finished"}]
    else:
        rec.update(status="skipped")
        events = [{"ts": iso(ts), "event": "run.started"},
                  {"ts": iso(ts + 30), "event": "run.stopped"}]
    (r / "nodes" / "say.json").write_text(json.dumps(rec))
    ev = r / "events.jsonl"
    ev.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    os.utime(ev, (ts + 40, ts + 40))       # deterministic `updated` order
    ids.append(rid)
    names.append(name)
    by_status[status].append(rid)

print(json.dumps({"ids": ids, "names": names, "by_status": by_status,
                  "owner_sid": a.owner_sid}))
