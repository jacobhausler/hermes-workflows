#!/usr/bin/env python3
"""Inspection-case fixture materializer for the ui2-proof driver (bd_2026-11-13-jtf).

Isolated ZERO-TOKEN fixtures for the NodePanel/Timeline acceptance, written
straight through the repo's OWN read model (real wfcommon.efp stamps, real
per-item child record files, real log/prompt bytes) into the bench's isolated
runs root — the dashboard route, not a mocked payload, serves every frame:

  insp-fan      — fan-out census with the cancelled-vs-failed grammar side by
                  side (workers.1 provider_400 RED, workers.2 cancelled NEUTRAL
                  with its last words kept), a node.failed(cancelled) spine row,
                  a node.cancelled spine row, a released amber gate span, a RED
                  failed node (sole), a run.lock_healed journal row, a retry
                  history (attempts_log #1 transport / #2 timeout) and a
                  >16 KiB spawn log whose HEAD-MARKER must age out of the ONE
                  tail window while the TAIL-MARKER rides.
  insp-zero     — the red zero-spawn record: error verbatim, `attempts` 0,
                  no log fact at all (Log tab reads the honest `log: unknown`).
  insp-refusal  — the refusal stamp `window_spent` read verbatim beside the
                  death facts (est-zmpx8 / #584 law).
  insp-mid      — an unfinished record with no live runner: the row reads
                  `interrupted` (never done, never a costume).

Synthetic, isolated, disclosed: SYNTHETIC.txt inside every fixture dir says so.
The historical lookbook records are NOT rewritten by anything here.

Run: python3 seed_inspect.py --repo R --runs-root DIR
Prints one JSON line: {"ids": {...}, "names": {...}} keyed by short role.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--runs-root", required=True)
a = ap.parse_args()

sys.path.insert(0, a.repo)
os.environ.setdefault("HERMES_HOME", str(Path(a.runs_root).parent / "home"))
import wfcommon

root = Path(a.runs_root)
root.mkdir(parents=True, exist_ok=True)
T0 = datetime(2099, 11, 19, 0, 0, 0, tzinfo=timezone.utc)
def ts(s):
    return (T0 + timedelta(seconds=s)).isoformat()

ids, names = {}, {}

def write_run(rid, name, graph, records, events, extra_files=None, synth_note=""):
    r = root / rid
    (r / "nodes").mkdir(parents=True, exist_ok=True)
    (r / "graph.json").write_text(json.dumps({"name": name, "nodes": graph}))
    (r / "run.json").write_text(json.dumps({"run_id": rid, "name": name, "started": ts(0),
                                           "owner": {"session_id": "ui2-inspect"}}))
    byid = {n["id"]: n for n in graph}
    for nid, rec in records.items():
        rec.setdefault("efp", wfcommon.efp(byid, byid[nid]))
        rec.setdefault("fp_rule_version", wfcommon.FP_RULE_VERSION)
        (r / "nodes" / f"{nid}.json").write_text(json.dumps(rec))
    (r / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    for rel, body in (extra_files or {}).items():
        p = r / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    (r / "SYNTHETIC.txt").write_text(
        "ISOLATED BENCH FIXTURE (bd_2026-11-13-jtf, ui2 proof `inspection` case).\n"
        + (synth_note or "") +
        "eFP stamps are REAL (wfcommon.efp at materialization); bytes are served\n"
        "by the actual dashboard routes. Historical lookbook records are untouched.\n")
    ids[name] = rid
    names[name] = name
    return r, byid

# ---------------------------------------------------------------- insp-fan --
fan_items = [{"label": "alpha-item", "id": "a"}, {"label": "beta-item", "id": "b"},
             {"label": "gamma-item", "id": "c"}]
fan_graph = [
    {"id": "prep", "type": "echo", "output": {"msg": "inspect fixture"}},
    {"id": "workers", "type": "agent", "after": ["prep"],
     "profile": "crew", "provider": "fake", "model": "fake/opus-test", "reasoning": "medium",
     "fanout": {"goal": "inspect {item}", "items": fan_items}},
    {"id": "watchdog", "type": "agent", "after": ["prep"], "goal": "straggler that was cancelled"},
    {"id": "sole", "type": "agent", "after": ["prep"], "optional": True,
     "goal": "single child that really failed"},
    {"id": "hold", "type": "gate", "after": ["workers"], "question": "inspect: release?",
     "options": ["release", "stop"]},
    {"id": "tail", "type": "echo", "after": ["hold"], "optional": True, "output": {"msg": "skippable"}},
]
fan, fby = write_run(
    "20991119-000400-inspect-fan", "insp-fan", fan_graph,
    {
        "prep": {"status": "done", "output": {"msg": "inspect fixture"}},
        "workers": {"status": "done", "attempts": 1,
                    "attempts_log": [{"attempt": 1, "error_class": "transport"},
                                     {"attempt": 2, "error_class": "timeout"}],
                    "started": ts(10), "ms": 30000,
                    "output": {"all_results": [
                        {"index": 0, "item": fan_items[0], "status": "done",
                         "output": {"note": "alpha-item committed output"}, "ms": 21000},
                        {"index": 1, "item": fan_items[1], "status": "failed",
                         "error_class": "provider_400", "error": "provider said no (isolated fixture)", "ms": 4000},
                        {"index": 2, "item": fan_items[2], "status": "failed",
                         "error_class": "cancelled", "error": "stopped: owner cancel (isolated fixture)", "ms": 9000},
                    ]}},
        "watchdog": {"status": "stopped", "error_class": "cancelled",
                     "error": "cancelled: straggler folded by the stop (isolated fixture)",
                     "final": "folded cleanly", "started": ts(12), "ms": 23000},
        "sole": {"status": "failed", "error_class": "provider_400",
                 "error": "provider rejected the payload (isolated fixture)",
                 "started": ts(14), "ms": 6000},
        "hold": {"status": "done", "output": {"answer": "release"}, "started": ts(50), "ms": 5000},
        "tail": {"status": "done", "output": {"msg": "skippable"}},
    },
    [
        {"ts": ts(0), "event": "run.started"},
        {"ts": ts(1), "event": "node.started", "node": "prep"},
        {"ts": ts(2), "event": "node.finished", "node": "prep"},
        {"ts": ts(10), "event": "node.started", "node": "workers"},
        {"ts": ts(40), "event": "node.finished", "node": "workers"},
        {"ts": ts(12), "event": "node.started", "node": "watchdog"},
        {"ts": ts(35), "event": "node.cancelled", "node": "watchdog"},
        {"ts": ts(14), "event": "node.started", "node": "sole"},
        {"ts": ts(20), "event": "node.failed", "node": "sole",
         "error_class": "provider_400", "error": "provider rejected the payload (isolated fixture)"},
        {"ts": ts(50), "event": "gate.held", "node": "hold"},
        {"ts": ts(55), "event": "gate.released", "node": "hold", "by": "proof"},
        {"ts": ts(56), "event": "run.lock_healed", "stranded": "run.lock.healed-1"},
        {"ts": ts(57), "event": "run.finished", "status": "failed"},
    ],
    extra_files={
        "nodes/workers.0.json": json.dumps({
            "status": "done", "output": {"note": "alpha-item committed output"}, "ms": 21000,
            "attempts": 2, "started": ts(10),
            "log_path": None, "prompt_path": None, "efp": None, "fp_rule_version": None}),
        "nodes/workers.1.json": json.dumps({
            "status": "failed", "error_class": "provider_400",
            "error": "provider said no (isolated fixture)", "attempts": 1, "ms": 4000,
            "log_path": None, "prompt_path": None, "efp": None, "fp_rule_version": None}),
        "nodes/workers.2.json": json.dumps({
            "status": "failed", "error_class": "cancelled",
            "error": "stopped: owner cancel (isolated fixture)", "final": "cleaned up halfway",
            "attempts": 1, "ms": 9000,
            "log_path": None, "prompt_path": None, "efp": None, "fp_rule_version": None}),
    },
    synth_note="Fan-out census, cancelled-vs-failed spine rows, retry history and the\n"
               ">16 KiB spawn log are isolated fixtures; no live launch produced them.\n"
               "The opt badge key rides the sole def: the engine closed key set does not\n"
               "carry optional, so this is the ONLY honest carrier for the UI branch.\n")

# Re-stamp the item files with real efp + absolute record paths (the route's
# ONLY path source) — written through the same helpers the runner uses shape-wise.
def stamp_item(rid, stem, **kw):
    p = root / rid / "nodes" / f"{stem}.json"
    rec = json.loads(p.read_text())
    rec.update({"efp": wfcommon.efp(fby, fby["workers"]),
                "fp_rule_version": wfcommon.FP_RULE_VERSION})
    for k, v in kw.items():
        if v is not None:
            rec[k] = v
    p.write_text(json.dumps(rec))

LOGS = fan / "logs"
LOGS.mkdir(exist_ok=True)
(LOGS / "workers.0.a2.log").write_text(
    "HEAD-MARKER-INSPECT-AGED-OUT\n" + ("x" * (20 * 1024)) + "\nTAIL-MARKER-INSPECT-BOUNDED-WINDOW\n")
LOGS.joinpath("workers.0.a1.log").write_text("ALPHA-ATTEMPT-1-RETRY\n")
LOGS.joinpath("workers.0.a2.prompt.md").write_text("PROMPT-BODY-INSPECT (isolated fixture)\n")
LOGS.joinpath("workers.1.a1.log").write_text("BETA-400-CAPTURE (isolated fixture)\n")
LOGS.joinpath("workers.2.a1.log").write_text("GAMMA-CANCELLED-CAPTURE (isolated fixture)\n")
stamp_item(ids["insp-fan"], "workers.0",
           log_path=str(LOGS / "workers.0.a2.log"), prompt_path=str(LOGS / "workers.0.a2.prompt.md"))
stamp_item(ids["insp-fan"], "workers.1", log_path=str(LOGS / "workers.1.a1.log"))
stamp_item(ids["insp-fan"], "workers.2", log_path=str(LOGS / "workers.2.a1.log"))

# --------------------------------------------------------------- insp-zero --
write_run(
    "20991119-000401-inspect-zero", "insp-zero",
    [{"id": "spawner", "type": "agent", "goal": "die at spawn",
      "model": "fake/luna-test", "provider": "fake"}],
    {"spawner": {"status": "failed", "error_class": "spawn",
                 "error": "exec failed: the child binary refused to spawn (isolated fixture)",
                 "attempts": 0, "started": ts(3), "ms": 40}},
    [{"ts": ts(0), "event": "run.started"},
     {"ts": ts(3), "event": "node.failed", "node": "spawner", "error_class": "spawn",
      "error": "exec failed: the child binary refused to spawn (isolated fixture)", "attempts": 0},
     {"ts": ts(4), "event": "run.finished", "status": "failed"}],
    synth_note="Red zero-spawn record: attempts 0, no log fact, no fabricated tail.\n")

# ------------------------------------------------------------- insp-refusal --
ref, _rby = write_run(
    "20991119-000402-inspect-refusal", "insp-refusal",
    [{"id": "asker", "type": "agent", "goal": "refuse honestly"}],
    {"asker": {"status": "failed", "error_class": "cap_exhausted", "refusal": "window_spent",
               "error": "attempt cap spent with the window gone (isolated fixture)",
               "attempts": 1, "started": ts(3), "ms": 1200}},
    [{"ts": ts(0), "event": "run.started"},
     {"ts": ts(3), "event": "node.failed", "node": "asker", "error_class": "cap_exhausted",
      "refusal": "window_spent",
      "error": "attempt cap spent with the window gone (isolated fixture)"},
     {"ts": ts(4), "event": "run.finished", "status": "failed"}],
    extra_files={"logs/asker.a1.log": "REFUSAL-CAPTURE (isolated fixture)\n"},
    synth_note="Refusal stamp `window_spent` (the #584 class) renders verbatim, never rewritten.\n")
json_ = json.loads((ref / "nodes" / "asker.json").read_text())
json_["log_path"] = str(ref / "logs" / "asker.a1.log")
(ref / "nodes" / "asker.json").write_text(json.dumps(json_))

# ---------------------------------------------------------------- insp-mid --
write_run(
    "20991119-000403-inspect-mid", "insp-mid",
    [{"id": "slow", "type": "agent", "goal": "never finished"},
     {"id": "next", "type": "agent", "after": ["slow"], "goal": "queued behind"}],
    {"slow": {"status": "running", "started": ts(3), "attempts": 1,
              "log_path": str(root / "20991119-000403-inspect-mid" / "logs" / "slow.a1.log")},
     "next": {"status": "pending"}},
    [{"ts": ts(0), "event": "run.started"},
     {"ts": ts(3), "event": "node.started", "node": "slow"}],
    extra_files={"logs/slow.a1.log": "MID-FLIGHT-CAPTURE (isolated fixture, runner died)\n"},
    synth_note="Running record, no live runner: run_state reads `interrupted` — never done.\n")

print(json.dumps({"ids": ids, "names": names}))
