#!/usr/bin/env python3
"""est-imp1z (WF-GRAFT-2) — the settle-boundary wiring: a CLI-backed child that
exits 0 on an exhausted-provider-retry line must NOT settle `done`, kind=transient
may ONLY feed the bounded transient ladder, and a token-declared failure is
terminal in both ladders.

Shapes driven through the real runner + fake CLI (same harness as
test_config_input_tmuu.py):
  (a) exit0lie, api_calls=1 — the lie is typed `transport` with the sentinel on the
      record, ONE spawn (the Q4 ladder's positive-api_calls gate refuses re-drive);
  (b) exit0lie, api_calls=0 — kind=transient feeds the Q4 ladder: retry events,
      capped respawns, terminal `transport_exhausted`;
  (c) declared (token failure on a clean exit 0 with a valid fence) — terminal
      `declared_failure`, ONE spawn, NO retry event (deterministic never re-driven);
  (d) tokenok (sentinel line + valid fence + success tail token) — the token
      outranks the sentinel: `done` commits the real answer;
  (e) exit1lie — the sentinel on a dying exit types `transport` (not `unknown`) and
      the retry event carries the typed class.

Run: python3 tests/test_exit0_is_not_success_imp1z.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-imp1z"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ.pop("WF_RUNS_ROOT", None)   # hermetic: runs land under HOME/workflows
sys.path.insert(0, str(BUILD))

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}; m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def wf_run(run_id, extra_env=None, timeout=120):
    base = {k: v for k, v in os.environ.items() if k != "WF_RUNS_ROOT"}
    env = dict(base, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / "fake.log"), **(extra_env or {}))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def rec_of(r, nid):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())

def events(r):
    return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines() if l.strip()]

def n_spawns(token):
    return (HOME / "fake.log").read_text().count(token)

LIE = "API call failed after 3 retries: HTTP 429 Too Many Requests"

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
(HOME / "fake.log").write_text("")
(HOME / "prompts.log").write_text("")

# ---------- (a) the exit-0 lie is typed, never `done`, never re-driven on live calls ----------
r = mk("imp1z-lie-hot", [{"id": "a", "type": "agent", "goal": "LIE-A report findings",
                          "schema": SCHEMA}], retry_backoff=[0.05, 0.1])
out = wf_run("imp1z-lie-hot", {"FAKE_MODE": "exit0lie", "FAKE_API_CALLS": "1"})
rec = rec_of(r, "a")
check("(a) the exit-0 lie never commits done: run lands failed",
      rec.get("status") == "failed" and "WORKFLOW_FAILED imp1z-lie-hot" in out,
      json.dumps(rec)[:200] + " | " + out[:80])
check("(a) the lie is typed transport (kind=transient hand-off class), not unknown",
      rec.get("error_class") == "transport", json.dumps(rec.get("error_class")))
check("(a) the verbatim sentinel line rides the record",
      LIE in str(rec.get("sentinel") or "") and LIE in rec.get("error", ""),
      str(rec.get("sentinel"))[:80])
check("(a) the error names the exit-0-is-not-success law",
      "rc=0" in rec.get("error", ""), rec.get("error", "")[:160])
check("(a) ONE spawn only: positive api_calls refuses the transient re-drive",
      n_spawns("LIE-A") == 1, f"spawns={n_spawns('LIE-A')}")
check("(a) no retry ladder ran (no node.retrying event)",
      not any(e.get("event") == "node.retrying" for e in events(r)))

# ---------- (b) kind=transient feeds the BOUNDED transient ladder ----------
r = mk("imp1z-lie-cold", [{"id": "a", "type": "agent", "goal": "LIE-B report findings",
                           "schema": SCHEMA}], retry_backoff=[0.05, 0.1])
out = wf_run("imp1z-lie-cold", {"FAKE_MODE": "exit0lie", "FAKE_API_CALLS": "0"})
rec = rec_of(r, "a")
evs = events(r)
check("(b) transient re-drive follows: retry events carry error_class=transport",
      any(e.get("event") == "node.retrying" and e.get("error_class") == "transport"
          for e in evs), json.dumps(evs[-1])[:200] if evs else "no events")
check("(b) the ladder is BOUNDED: 1 spawn + the default transient cap (2) respawns",
      n_spawns("LIE-B") == 3, f"spawns={n_spawns('LIE-B')}")
check("(b) spent ladder lands transport_exhausted (never done)",
      rec.get("error_class") == "transport_exhausted" and rec.get("status") == "failed",
      json.dumps(rec.get("error_class")))

# ---------- (c) token-declared failure on a clean exit 0 is TERMINAL ----------
r = mk("imp1z-declared", [{"id": "a", "type": "agent", "goal": "DECL-C report findings",
                           "schema": SCHEMA}], retry_backoff=[0.05, 0.1])
out = wf_run("imp1z-declared", {"FAKE_MODE": "declared", "FAKE_API_CALLS": "0"})
rec = rec_of(r, "a")
check("(c) the node's own failure declaration outranks exit 0 AND the valid fence",
      rec.get("status") == "failed" and rec.get("error_class") == "declared_failure",
      json.dumps(rec)[:200])
check("(c) deterministic: ONE spawn, no ladder event (never re-driven)",
      n_spawns("DECL-C") == 1
      and not any(e.get("event") == "node.retrying" for e in events(r)),
      f"spawns={n_spawns('DECL-C')}")

# ---------- (d) the success token outranks the transient sentinel ----------
r = mk("imp1z-tokenok", [{"id": "a", "type": "agent", "goal": "TOKEN-D report findings",
                          "schema": SCHEMA}], retry_backoff=[0.05, 0.1])
out = wf_run("imp1z-tokenok", {"FAKE_MODE": "tokenok", "FAKE_API_CALLS": "1",
                               "FAKE_PROMPT_LOG": str(HOME / "prompts-bare.log")})
rec = rec_of(r, "a")
check("(d) declared success protects finished work from the sentinel: done commits",
      rec.get("status") == "done" and rec.get("output", {}).get("result") == "recovered",
      json.dumps(rec)[:200])
check("(d) an undeclared shape pays ZERO token-contract prompt bytes (golden prompt law)",
      "node_outcome" not in (HOME / "prompts-bare.log").read_text())

# ---------- (e) the prompt contract: build-shape spawns are told the token grammar ----------
r = mk("imp1z-prompt", [{"id": "a", "type": "agent", "shape": "build",
                         "goal": "PROMPT-E report findings", "schema": SCHEMA}],
       retry_backoff=[0.05, 0.1])
out = wf_run("imp1z-prompt", {"FAKE_MODE": "tokenok", "FAKE_API_CALLS": "1",
                              "FAKE_PROMPT_LOG": str(HOME / "prompts.log")})
prompts = (HOME / "prompts.log").read_text()
check("(e) the build-shape spawn carries the node-outcome preamble with the EXACT grammar",
      "## Node-outcome token" in prompts
      and '{"node_outcome": "success"}' in prompts and '{"node_outcome": "failure"}' in prompts,
      "grammar absent from prompts.log")

# ---------- (f) the sentinel on a dying exit types transport, not unknown ----------
r = mk("imp1z-exit1", [{"id": "a", "type": "agent", "goal": "LIE-F report findings",
                        "schema": SCHEMA}], retry_backoff=[0.05, 0.1])
out = wf_run("imp1z-exit1", {"FAKE_MODE": "exit1lie", "FAKE_API_CALLS": "0"})
rec = rec_of(r, "a")
evs = events(r)
check("(f) sentinel-on-dying-exit feeds the same ladder typed transport (not unknown)",
      any(e.get("event") == "node.retrying" and e.get("error_class") == "transport"
          for e in evs), json.dumps(evs[-2:])[:260] if evs else "no events")

print("OVERALL", "GREEN" if ok else "RED")
raise SystemExit(0 if ok else 1)
