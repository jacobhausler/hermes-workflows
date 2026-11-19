#!/usr/bin/env python3
"""E24 (bd_2026-11-13-42t): the declared timeout is honored or clamped LOUDLY.

  * an effective wall below the author's number emits node.timeout_clamped at
    the BAKE (declared_s, effective_s, reasons) — the park clamp is never a
    silent min();
  * a death on the wall names declared-vs-effective and EVERY extension grant
    that moved it, in the failure text AND as the structured wall_account:
        {"declared_s", "baked_s", "clamp_reasons",
         "grants": [{"extra_s", "basis"}], "effective_s"}
    (the wave-3 shape: a 2250 s death on a node whose author wrote 1500 — the
    wall the owner sees must name the +50% grant that produced it);
  * every extension grant is already an event (node.extended; log/session/
    adopted bases) — this file pins that the death TEXT keeps the same ledger.

Run (stdlib only): python3 tests/test_wall_truth_42t.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))
ROOT = BUILD.parent
HOME = BUILD / f"home-e24.{os.getpid()}"
RUNS = HOME / "workflows"
FAKE = str(BUILD / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)  # est-2ek.1.762 pin: HERMES_HOME alone is not a sandbox
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402
import atexit
atexit.register(shutil.rmtree, HOME, ignore_errors=True)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

HOME.mkdir(parents=True); RUNS.mkdir()

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}
    m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def runx(run_id, extra_env=None, timeout=120):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / "fake.log"), **(extra_env or {}))
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def events(r):
    p = r / "events.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def rec_of(r, nid="a"):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())

# ------------------------------------------------------------------ W1: E24
# A node that EXTENDS and still dies: timeout 4 => one +50% (2 s) session-basis
# grant; the pulse outlives the extended 6 s wall => the death names declared
# 4 vs effective 6 and the grant that moved it. Honored wall => no clamp event.
(HOME / "fake.log").write_text("")
r = mk("t42t-extend", [{"id": "a", "type": "agent", "goal": "SLOW", "timeout": 4}])
runx("t42t-extend", {"FAKE_MODE": "session_pulse", "FAKE_SESSION_SEC": "9"})
rec = rec_of(r)
ext = [e for e in events(r) if e.get("event") == "node.extended"]
check("W1 one node.extended grant moved the wall (the event already existed; kept)",
      len(ext) == 1 and ext[0].get("extra_s") == 2, json.dumps(ext))
check("W1 died on the wall, class timeout",
      rec.get("status") == "failed" and rec.get("error_class") == "timeout",
      json.dumps({k: rec.get(k) for k in ("status", "error_class", "error")})[:250])
err = rec.get("error", "")
check("W1 failure text names declared-vs-effective",
      "declared 4s" in err and "effective 6s" in err, err)
check("W1 failure text names the extension grant that moved it",
      "+2s extension grant" in err, err)
acct = rec.get("wall_account")
check("W1 structured wall_account present and exact",
      isinstance(acct, dict) and acct.get("declared_s") == 4 and acct.get("effective_s") == 6
      and len(acct.get("grants") or []) == 1 and acct["grants"][0]["extra_s"] == 2
      and acct["grants"][0]["basis"] == "session", json.dumps(acct))
check("W1 honored wall => no clamp event (honest absence)",
      not any(e.get("event") == "node.timeout_clamped" for e in events(r)),
      json.dumps([e["event"] for e in events(r)])[:200])

# ------------------------------------------------------------------ W2: E24
# The park clamp moves the respawn's wall BELOW the declared number: LOUD at
# the bake, and the clamped spawn still answers.
(HOME / "fake.log").write_text("")
att = HOME / "att-w2"; shutil.rmtree(att, ignore_errors=True)
r = mk("t42t-park", [{"id": "a", "type": "agent", "goal": "GO park-clamp", "timeout": 30}],
       ratelimit_interval=1.5, ratelimit_jitter=0.0, retry_budget=6)
runx("t42t-park", {"FAKE_MODE": "ratelimit", "FAKE_RL_FAILS": "1", "FAKE_ATTEMPT_DIR": str(att)})
cl = [e for e in events(r) if e.get("event") == "node.timeout_clamped"]
check("W2 the parked respawn's clamp is an event fact at the bake",
      len(cl) == 1 and cl[0].get("declared_s") == 30
      and isinstance(cl[0].get("effective_s"), (int, float))
      and 0 < cl[0]["effective_s"] < 30 and cl[0].get("reasons") == ["park_cap"],
      json.dumps(cl))
check("W2 the clamped spawn still delivered the node done",
      rec_of(r).get("status") == "done", json.dumps(rec_of(r))[:200])

# ------------------------------------------------------------------ W3: E24
# Phrase builder, the 2250-s shape from the evidence: declared 1500, ONE
# +50% (750 s) grant — the failure text an owner sees names both numbers.
phrase = wf._wall_truth_phrase({"declared_s": 1500, "baked_s": 1500, "clamp_reasons": [],
                                "grants": [{"extra_s": 750, "basis": "log"}],
                                "effective_s": 2250})
check("W3 the evidence shape renders declared + grant + effective",
      "declared 1500s" in phrase and "+750s extension grant (basis log)" in phrase
      and "died at effective 2250s" in phrase, phrase)
phrase2 = wf._wall_truth_phrase({"declared_s": 600, "baked_s": 337.5,
                                 "clamp_reasons": ["park_cap"], "grants": [],
                                 "effective_s": 337.5})
check("W3 a clamp with no grant names the clamp, no phantom grant line",
      "declared 600s" in phrase2 and "clamped at bake to 337.5s (park_cap)" in phrase2
      and "grant" not in phrase2, phrase2)

print(("\nALL PASS" if ok else "\nFAILURES PRESENT") + " test_wall_truth_42t")
sys.exit(0 if ok else 1)
