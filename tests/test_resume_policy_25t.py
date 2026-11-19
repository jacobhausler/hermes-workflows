#!/usr/bin/env python3
"""est-25t / E19 — the update-wall misattribution is dead.

The corpus: 34 attempt logs carry the resume-policy refusal and 661/662 of
them open with the banner "restart the gateway"; wave-3 cold seats
independently reproduced the misreading, and rc=2 argv deaths landed
`transport_exhausted` after the transient ladder legally burned the node's
whole cap on a deterministic condition. Pinned here:
  (1) the classifier takes the child's LAST Error: line: the update-wall
      capture types `resume_policy`, and the marker IS that line;
  (2) resume_policy is in the closed error-class set and rides NEITHER
      ladder — it is outside the retry gate by construction;
  (3) end-to-end: the rc=2 resume death commits error_class=resume_policy,
      renders the real refusal (never the banner) as the error text, spawned
      EXACTLY once, and emitted zero node.retrying events (zero transient
      draws) — the run blocks on the node, not on a spent cap.

Run: cd tests && python3 test_resume_policy_25t.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-rp25t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

REFUSAL = "Error: Resume retains gateway session policy; creation overrides are unsupported on resume."
UPDATE_WALL = ("Warning: A previous `hermes update` pulled new code; restart the gateway to load it.\n"
               "Switching to the seat default model for this session.\n"
               + REFUSAL + "\n")

# ---------- (1) classification from the LAST Error: line ----------
ec, marker = wf._classify_rc_output(UPDATE_WALL)
check("update-wall capture -> resume_policy", ec == "resume_policy", ec)
check("the marker IS the refusal line (last Error:, not the banner head)",
      marker == REFUSAL, str(marker))

ESCALATED = ("Warning: A previous `hermes update` pulled new code; restart the gateway to load it.\n"
             "hermes -z: agent failed: " + REFUSAL + "\n")
ec2, marker2 = wf._classify_rc_output(ESCALATED)
check("the oneshot-escalated twin types the same", ec2 == "resume_policy", ec2)

BANNER_ONLY = "Warning: A previous `hermes update` pulled new code; restart the gateway to load it.\n"
ec3, marker3 = wf._classify_rc_output(BANNER_ONLY)
check("a banner with no Error: line stays unknown, no marker (pin unchanged)",
      ec3 == "unknown" and marker3 is None, f"{ec3}/{marker3}")

PROSE_AND_ERROR = ("some daemon chatter\n"
                   "Error: first refusal, stale\n"
                   "more chatter\n"
                   "Error: the final argv refusal wins\n")
ec4, marker4 = wf._classify_rc_output(PROSE_AND_ERROR)
check("LAST Error: line is the one surfaced",
      ec4 == "unknown" and marker4 == "Error: the final argv refusal wins", str(marker4))

check("resume_policy is in the closed set", "resume_policy" in wf.ERROR_CLASSES)
check("resume_policy rides neither ladder",
      "resume_policy" not in wf._RETRYABLE_CLASSES and "resume_policy" not in wf._BOUNDED_RETRY_CLASSES)

# ---------- (3) end-to-end: one spawn, zero transient draws ----------
if HOME.exists():
    shutil.rmtree(HOME)
(HOME / "workflows").mkdir(parents=True)
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")

run = RUNS / "rp25t"
(run / "nodes").mkdir(parents=True)
(run / "gates").mkdir()
(run / "graph.json").write_text(json.dumps(
    {"name": "rp25t", "nodes": [{"id": "boom", "type": "agent", "goal": "GO rp25t"}]}))
(run / "run.json").write_text(json.dumps(
    {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30, "retry_budget": 6,
     "retry": {"transient": 2, "bounded": 1}}))
(HOME / "fake.log").write_text("")

env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
           FAKE_LOG=str(HOME / "fake.log"), FAKE_MODE="resume_policy")
env.pop("WF_WAKE_SINK_PORT", None)
out = subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", "rp25t"],
                     env=env, capture_output=True, text=True, timeout=120).stdout.strip()

rec = json.loads((run / "nodes" / "boom.json").read_text())
events = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines() if l.strip()]
nspawns = (HOME / "fake.log").read_text().count("rp25t")
check("node committed failed with error_class=resume_policy",
      rec["status"] == "failed" and rec.get("error_class") == "resume_policy",
      json.dumps(rec)[:200])
check("the record renders the child's real refusal",
      "creation overrides are unsupported on resume" in (rec.get("error") or ""),
      str(rec.get("error"))[:200])
check("the record does NOT launder the banner as the cause",
      "restart the gateway" not in (rec.get("error") or ""), str(rec.get("error"))[:200])
check("exactly ONE spawn (deterministic: zero transient-cap consumption)",
      nspawns == 1, f"spawns={nspawns}")
check("zero node.retrying events (the ladder never touched it)",
      not [e for e in events if e.get("event") == "node.retrying"],
      json.dumps([e.get("event") for e in events]))
check("node.failed event carries the class",
      any(e.get("event") == "node.failed" and e.get("error_class") == "resume_policy"
          for e in events))
check("the run blocks on the death, not on a spent transport cap",
      "WORKFLOW_FAILED" in out
      and not any(e.get("error_class") == "transport_exhausted" for e in events),
      out[:80])

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
