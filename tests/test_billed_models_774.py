#!/usr/bin/env python3
"""est-2ek.1.774 — the node record names every model the child actually billed.

A pinned node whose session ends on the pinned model can still have billed another
model mid-session (core's session_model_usage keeps every main-loop model). The
commit-time route hold fails such a node route_unavailable, but the record showed
only the final served_model, so the error cited a model the record never listed.
The record now carries `billed_models` (every main-loop model, auxiliary tasks
excluded) and the error says which one was the final served model and which one
was billed mid-session. The guard itself is unchanged.
"""
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

failures = 0
def check(label, ok, detail=""):
    global failures
    print(("PASS " if ok else "FAIL ") + label + (" " + str(detail)[:400] if not ok else ""))
    failures += not ok

PIN = "m-pin-1"
OTHER = "m-fallback-2"
NODE = {"id": "a", "type": "agent", "goal": "x", "model": PIN, "provider": "openai-codex",
        "route_verified": f"openai-codex/{PIN}"}

def seed(home, run_name, usage, final=PIN):
    title = f"wf:{run_name}:a:abc12345#a1"
    db = sqlite3.connect(home / "state.db")
    db.execute("create table sessions (id text, title text, model text, billing_provider text, "
               "input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, "
               "api_call_count int, tool_call_count int, estimated_cost_usd real, "
               "last_activity_at real, last_activity_description text, ended_at real, started_at real)")
    db.execute("insert into sessions (id,title,model,billing_provider,api_call_count,started_at) "
               "values (?,?,?,?,?,?)", ("child1", title, final, "openai-codex", 2, 1.0))
    db.execute("create table session_model_usage (session_id text, model text, "
               "billing_provider text, task text, api_call_count int)")
    db.executemany("insert into session_model_usage values (?,?,?,?,?)",
                   [("child1", m, "p", task, 1) for m, task in usage])
    db.commit(); db.close()
    return title.split("#a", 1)[0]

with tempfile.TemporaryDirectory(prefix="wf-billed-") as scratch:
    base = Path(scratch)
    os.environ["WF_RUNS_ROOT"] = str(base / "runs")
    import wf
    wf.seat_forbidden_models = lambda: []

    def lane(name):
        home = base / name
        home.mkdir()
        os.environ["HERMES_HOME"] = str(home)
        run = home / "runs" / name
        (run / "nodes").mkdir(parents=True)
        return home, run

    # MIXED: final session model is the pin, but a mid-session call billed OTHER.
    home, run = lane("mixed")
    skey = seed(home, "mixed", [(PIN, ""), (OTHER, ""), ("aux-model", "compression")])
    r = wf._stamp_served({"_run": run}, {"skey": skey, "status": "done", "profile_home": str(home)}, NODE)
    check("MIXED fails route_unavailable (guard unchanged)",
          r.get("status") == "failed" and r.get("error_class") == "route_unavailable", r)
    check("MIXED billed_models lists both main-loop models, not the aux task",
          sorted(r.get("billed_models") or []) == sorted([PIN, OTHER]), r.get("billed_models"))
    check("MIXED served_model stays the final session model", r.get("served_model") == PIN, r)
    check("MIXED error names the final served model and the mid-session model",
          f"final served_model '{PIN}'" in r.get("error", "")
          and f"mid-session call billed '{OTHER}'" in r.get("error", ""), r.get("error"))
    wf.save_node(run, NODE, {"a": NODE}, r)
    rec = json.loads((run / "nodes" / "a.json").read_text())
    check("MIXED committed node record carries billed_models",
          sorted(rec.get("billed_models") or []) == sorted([PIN, OTHER]), rec)
    item = wf.commit_item_record(run, dict(NODE, id="b"), {"b": NODE}, 0, r)
    rec_i = json.loads((run / "nodes" / "b.0.json").read_text()) if (run / "nodes" / "b.0.json").exists() else {}
    check("MIXED fan-out item record carries billed_models too",
          sorted(rec_i.get("billed_models") or []) == sorted([PIN, OTHER]), rec_i)

    # SINGLE: one model billed, equals the pin -> one-item list, still passes.
    home, run = lane("single")
    skey = seed(home, "single", [(PIN, "")])
    r = wf._stamp_served({"_run": run}, {"skey": skey, "status": "done", "profile_home": str(home)}, NODE)
    check("SINGLE still passes", r.get("status") == "done" and not r.get("error_class"), r)
    check("SINGLE billed_models is a one-item list", r.get("billed_models") == [PIN], r.get("billed_models"))

    # LEGACY: no route_verified proof -> no hold, and the runner invents no billed list.
    home, run = lane("legacy")
    skey = seed(home, "legacy", [(PIN, ""), (OTHER, "")])
    legacy = {k: v for k, v in NODE.items() if k != "route_verified"}
    r = wf._stamp_served({"_run": run}, {"skey": skey, "status": "done", "profile_home": str(home)}, legacy)
    check("LEGACY unproved route stays done with no billed_models",
          r.get("status") == "done" and "billed_models" not in r, r)

print("ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(bool(failures))
