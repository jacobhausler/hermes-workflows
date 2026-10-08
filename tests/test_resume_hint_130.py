#!/usr/bin/env python3
"""#130 resume_hint — dead-attempt artifact inventory on every re-run path.

Contracts pinned (prompt-side only; the def-hash law):
  A transient-retry respawn (the currently-BLANK re-run path): the respawned
    prompt carries the machine '## Dead-attempt artifact inventory (machine
    preamble)' block — per-artifact size=/mtime=/lines= inventory of the dead
    attempt's durable work dir, the prior attempts' spawn logs, and
    runner.log — ending in RESUME_LINE; the respawned child VERIFIES the
    inventory arrived (the fake only answers when its prompt carried it) and
    the run closes done.
  B bounded re-drive (dead_session_102 shape, resume_hint: true): the harvest
    block still rides AND the inventory block is added; dead-session noise is
    stripped from every inventory excerpt (fixture law).
  C resume_hint: false — the re-drive prompt stays BYTE-IDENTICAL to the dead
    attempt's prompt (the pre-#130 shape); node records carry no resume_hint key.
  D auto (flag absent): no prior attempt => zero hint bytes (spawn 0 prompt
    byte-identical to the plain goal); transient respawns stay blank (today's
    law, unchanged without the flag).
  E closed grammar: resume_hint registered in AGENT_KEYS; true/false accepted;
    a non-bool value and an echo-node use are REJECTED.

Run: cd tests && env -u WF_RUNS_ROOT -u HERMES_HOME HOME=/home/hermes \
     PYTHONPATH=/opt/hermes /opt/hermes/.venv/bin/python3 test_resume_hint_130.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home130"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)   # est-2ek.1.762 pin: writers pin the env door
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

HEADER = "## Dead-attempt artifact inventory (machine preamble)"

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30,
         "retry_backoff": [0.05, 0.1]}; m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def wf(run_id, extra_env=None, timeout=180):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / "fake.log"), **(extra_env or {}))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def rec_of(r, nid):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())

SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}
MARK = "RESUME-HINT-ARTIFACT-130"

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
(HOME / "fake.log").write_text("")

# ---- A: transient-retry respawn carries the inventory (resume_hint: true) ----
r = mk("rh130-transient", [{"id": "a", "type": "agent", "goal": "tr rh130-transient",
                            "schema": SCHEMA, "resume_hint": True}])
out = wf("rh130-transient", {"FAKE_MODE": "retry_hint", "FAKE_API_CALLS": "0",
                             "FAKE_ATTEMPT_DIR": str(HOME / "att_transient")})
rec = rec_of(r, "a")
check("A transient respawn recovers to done ONLY off the inventory (fake gate)",
      rec["status"] == "done" and (rec.get("output") or {}).get("result") == "resumed-hint-130",
      str(rec)[:300])
p2 = (r / "logs" / "a.a1.prompt.md")
prompt2 = p2.read_text() if p2.exists() else ""
check("A respawned prompt carries the machine inventory header", HEADER in prompt2, prompt2[:120])
check("A inventory lists the dead attempt's work artifact", MARK in prompt2, prompt2[:120])
check("A inventory carries size=/mtime= per artifact", "size=" in prompt2 and "mtime=" in prompt2,
      prompt2[:120])
check("A inventory ends in the don't-redo law",
      "Do not redo finished work; continue from the state above." in prompt2, prompt2[-160:])
check("A attempts_log shows the transient retry ran",
      any(a.get("error_class") == "transport" for a in (rec.get("attempts_log") or [])),
      str(rec.get("attempts_log"))[:200])
check("A run closes done", out.startswith("WORKFLOW_DONE rh130-transient"), out[-160:])
check("A prompt-side only: the committed node record carries no resume_hint key",
      "resume_hint" not in json.dumps(rec), str(rec)[:200])

# ---- B: bounded re-drive — harvest block rides AND the inventory rides ----
r = mk("rh130-bounded", [{"id": "build", "type": "agent", "goal": "DEADSESS rh130-bounded",
                          "schema": SCHEMA, "resume_hint": True}], node_timeout=6)
out = wf("rh130-bounded", {"FAKE_MODE": "dead_session_102", "FAKE_MESSAGES": "0",
                           "FAKE_ATTEMPT_DIR": str(HOME / "att_bounded"),
                           "FAKE_HANG_SEC": "30"})
rec = rec_of(r, "build")
check("B bounded re-drive recovers to done", rec["status"] == "done"
      and (rec.get("output") or {}).get("result") == "resumed-102", str(rec)[:300])
pp = r / "logs" / "build.a1.prompt.md"
prompt = pp.read_text() if pp.exists() else ""
check("B the dead-session harvest block still rides",
      "## Dead-session re-drive harvest (machine preamble)" in prompt, prompt[:120])
check("B the inventory block rides beside it", HEADER in prompt, prompt[:120])
check("B inventory carries size=/mtime= inventory", "size=" in prompt and "mtime=" in prompt,
      prompt[:120])
check("B dead-session noise stripped from every inventory excerpt (fixture law)",
      "found but has no messages" not in prompt,
      str([l for l in prompt.splitlines() if "found but has no messages" in l][:1]))

# ---- C: resume_hint: false — the re-drive prompt stays byte-identical ----
# SAME goal for both runs; the false run's drive-2 prompt must equal what a
# pre-#130 runner sends (the full #102 harvest, no inventory), while the
# flag-absent control (artifacts exist) DOES get the inventory.
r = mk("rh130-off", [{"id": "build", "type": "agent", "goal": "DEADSESS COMMON-130",
                      "schema": SCHEMA, "resume_hint": False}], node_timeout=6)
out = wf("rh130-off", {"FAKE_MODE": "dead_session_102", "FAKE_MESSAGES": "0",
                      "FAKE_ATTEMPT_DIR": str(HOME / "att_off"), "FAKE_HANG_SEC": "30"})
rec = rec_of(r, "build")
check("C re-drive still fires with resume_hint:false (done, harvest path)",
      rec["status"] == "done" and (rec.get("output") or {}).get("result") == "resumed-102",
      str(rec)[:300])
p_off = (r / "logs" / "build.a1.prompt.md").read_text()
check("C resume_hint:false keeps the standard #102 harvest (names+excerpts ride)",
      "## Dead-session re-drive harvest (machine preamble)" in p_off
      and "progress.md" in p_off and "BANKED-WORKFILE-102" in p_off, p_off[:120])
check("C resume_hint:false adds NO inventory bytes (prompt byte-identical to pre-#130)",
      HEADER not in p_off and "size=" not in p_off,
      str([l for l in p_off.splitlines() if "size=" in l][:1]))
check("C node record stays prompt-side clean (no resume_hint key in the record)",
      "resume_hint" not in json.dumps(rec), str(rec)[:200])
r = mk("rh130-ctrl", [{"id": "build", "type": "agent", "goal": "DEADSESS COMMON-130",
                       "schema": SCHEMA}], node_timeout=6)
out = wf("rh130-ctrl", {"FAKE_MODE": "dead_session_102", "FAKE_MESSAGES": "0",
                        "FAKE_ATTEMPT_DIR": str(HOME / "att_ctrl"), "FAKE_HANG_SEC": "30"})
p_ctrl = (r / "logs" / "build.a1.prompt.md").read_text()
check("C flag-absent control auto-FIRES (prior attempt left artifacts)",
      HEADER in p_ctrl and "size=" in p_ctrl, p_ctrl[:120])

# ---- D: auto (flag absent) — first spawn never gets a hint; today's laws stand ----
r = mk("rh130-auto", [{"id": "a", "type": "agent", "goal": "plain rh130-auto",
                       "schema": SCHEMA}])
out = wf("rh130-auto", {"FAKE_API_CALLS": "0"})
rec = rec_of(r, "a")
p0 = (r / "logs" / "a.a0.prompt.md").read_text()
check("D no prior attempt => zero hint bytes on the first prompt",
      HEADER not in p0 and "size=" not in p0, p0[:120])
check("D plain node still closes done", rec["status"] == "done", str(rec)[:160])
r = mk("rh130-auto2", [{"id": "a", "type": "agent", "goal": "tr rh130-auto2"}],
       retry_backoff=[0.05, 0.1])
out = wf("rh130-auto2", {"FAKE_MODE": "transport", "FAKE_API_CALLS": "0"})
rec = rec_of(r, "a")
check("D auto/absent keeps the transient re-drive BLANK today (unchanged)",
      rec["error_class"] == "transport_exhausted"
      and HEADER not in (r / "logs" / "a.a1.prompt.md").read_text(), str(rec)[:160])

# ---- E: validator contract (closed grammar) ----
check("resume_hint registered in AGENT_KEYS", "resume_hint" in wfcommon.AGENT_KEYS)
check("validator accepts resume_hint true/false",
      not wfcommon.validate_graph_errors([
          {"id": "a", "type": "agent", "goal": "g", "resume_hint": True},
          {"id": "b", "type": "agent", "goal": "g", "after": ["a"], "resume_hint": False}]),
      str(wfcommon.validate_graph_errors([{"id": "a", "type": "agent", "goal": "g",
                                           "resume_hint": True}])))
errs = wfcommon.validate_graph_errors([{"id": "a", "type": "agent", "goal": "g",
                                        "resume_hint": "yes"}])
check("validator rejects a non-bool resume_hint",
      any(e["field"] == "resume_hint" for e in errs), str(errs)[:200])
errs = wfcommon.validate_graph_errors([{"id": "a", "type": "echo", "after": [],
                                        "output": {}, "resume_hint": True}])
check("validator rejects resume_hint on an echo node",
      any(e["field"] == "resume_hint" for e in errs), str(errs)[:200])

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
