#!/usr/bin/env python3
"""est-25t / E21 — quota_exhausted vs rate_limited_transient, honestly split.

The corpus: an account-level 429 WITHOUT a reset horizon, classed transient,
legally burned the full 8-attempt cap and 60 minutes of lane on one
deterministic condition. Pinned here:
  (1) a horizon-less account-state 429 classifies quota_exhausted (NOT
      transport, NOT ratelimit); the credential-window banner keeps its own
      transient park class — the split is by FACT, not by status code;
  (2) end-to-end, the horizon-less death emits quota_exhausted{identity,
      reset: null} at attempt 1, the node parks pending on the verdict, and
      the transient ladder draws ZERO respawns (one spawn, zero node.retrying
      events, no transport_exhausted anywhere);
  (3) the #24 law holds for the horizon twin: named horizon rides the record
      verbatim-parsed, still ONE attempt.

Run: cd tests && python3 test_quota_horizonless_25t.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-qh25t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# ---------- (1) the split, at the classifier ----------
HORIZONLESS = ("Warning: install out of sync\n"
               "hermes -z: agent failed: Error code: 429 - {\"error\": {\"message\": "
               "\"Account usage cap reached for this billing period\"}}\n")
ec, marker = wf._classify_rc_output(HORIZONLESS)
check("horizon-less account 429 -> quota_exhausted (not transport)",
      ec == "quota_exhausted", f"{ec}/{marker}")

BANNER = ("hermes -z: agent failed: Anthropic credentials are rate-limited for "
          "example-model-1; other Anthropic models remain available (see `hermes auth list`).\n")
ec2, _ = wf._classify_rc_output(BANNER)
check("credential-window 429 stays the transient banner class (ratelimit)",
      ec2 == "ratelimit", ec2)

HORIZON = ('Provider said: HTTP 429: {"error": {"message": "Subscription usage '
           'limit reached, resets in ~109 hours"}}')
ec3, _ = wf._classify_rc_output(HORIZON)
check("#24 twin: quota phrase + named horizon -> quota_exhausted",
      ec3 == "quota_exhausted", ec3)

PLAIN = "hermes -z: agent failed: Error code: 429 - {'error': 'slow down'}"
ec4, _ = wf._classify_rc_output(PLAIN)
check("a bare throttle 429 names no account state and stays transport (pin)",
      ec4 == "transport", ec4)

check("quota_exhausted is in the closed set", "quota_exhausted" in wf.ERROR_CLASSES)
check("quota_exhausted rides neither ladder",
      "quota_exhausted" not in wf._RETRYABLE_CLASSES
      and "quota_exhausted" not in wf._BOUNDED_RETRY_CLASSES)

# ---------- (2) end-to-end: attempt 1, parked, zero transient draws ----------
if HOME.exists():
    shutil.rmtree(HOME)
(HOME / "workflows").mkdir(parents=True)
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30, "retry_budget": 8}
    m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def drive(run_id, mode):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / "fake.log"), FAKE_MODE=mode,
               WF_QUOTA_CACHE=str(HOME / "quota-cache.json"))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=120).stdout.strip()

(HOME / "fake.log").write_text("")
r = mk("qh25t", [{"id": "a", "type": "agent", "goal": "GO qh25t", "model": "gpt-x"}])
out = drive("qh25t", "quota_horizonless")
rec = json.loads((r / "nodes" / "a.json").read_text())
events = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines() if l.strip()]
nspawns = (HOME / "fake.log").read_text().count("qh25t")
check("recorded at attempt 1 as quota_exhausted",
      rec.get("status") == "failed" and rec.get("error_class") == "quota_exhausted"
      and rec.get("attempts", 1) == 1, json.dumps(rec)[:200])
check("the record carries quota_exhausted{identity, reset: null}",
      rec.get("quota", {}).get("identity") == "gpt-x"
      and rec["quota"].get("reset") is None, str(rec.get("quota")))
check("the error says reset: none and names the parking",
      "reset: none" in (rec.get("error") or "")
      and "parked" in (rec.get("error") or "").lower(), str(rec.get("error"))[:200])
check("ONE spawn — zero transient retries consumed", nspawns == 1, f"spawns={nspawns}")
check("zero node.retrying events; no transport_exhausted anywhere",
      not [e for e in events if e.get("event") == "node.retrying"]
      and not any(e.get("error_class") == "transport_exhausted" for e in events),
      json.dumps([e.get("event") for e in events]))
check("the run blocks on the parked node", "WORKFLOW_FAILED" in out, out[:80])

# ---------- (3) the named-horizon twin keeps the #24 law, reset now typed ----------
(HOME / "fake.log").write_text("")
r2 = mk("qwh25t", [{"id": "a", "type": "agent", "goal": "GO qwh25t", "model": "m-hz"}])
drive("qwh25t", "quota")
rec2 = json.loads((r2 / "nodes" / "a.json").read_text())
check("named horizon: quota_exhausted{identity, reset='109 hour'} at one attempt",
      rec2.get("error_class") == "quota_exhausted"
      and (rec2.get("quota") or {}).get("reset") == "109 hour"
      and (rec2.get("quota") or {}).get("identity") == "m-hz",
      json.dumps(rec2)[:220])
check("named horizon: still exactly one spawn",
      (HOME / "fake.log").read_text().count("qwh25t") == 1)

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
