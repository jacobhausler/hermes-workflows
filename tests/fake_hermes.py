#!/usr/bin/env python3
"""Fake hermes chat for wf.py engine tests.
Usage: fake_hermes.py chat --query-file PATH --oneshot -Q ...
Behavior markers inside the prompt:
  'STEER-<word>'  -> returns {"steered": "<word>"}
  'FAILME'        -> returns unparseable prose (forces retry then failure)
  otherwise       -> returns {"result": "ok", "goal": <first line>}
Every invocation appends one line to $FAKE_LOG so tests can count spawns.
"""
import sys, os, json, time

args = sys.argv[1:]
_FAKE_HOME = os.environ.get("HERMES_HOME") or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tmp-fake-home")
os.makedirs(_FAKE_HOME, exist_ok=True)
if "--query-file" in args:
    q = open(args[args.index("--query-file") + 1]).read()
else:
    q = sys.stdin.read()
with open(os.environ.get("FAKE_LOG", os.path.join(_FAKE_HOME, "fake.log")), "a") as f:
    f.write(q.splitlines()[0] + "\n")
if os.environ.get("FAKE_ARGV_LOG"):          # spawn-contract tests: full argv, one line per child
    with open(os.environ["FAKE_ARGV_LOG"], "a") as f:
        f.write(" ".join(args) + "\n")
if os.environ.get("FAKE_PID_LOG"):            # spawn-record tests: child pid, one per spawn
    with open(os.environ["FAKE_PID_LOG"], "a") as f:
        f.write(str(os.getpid()) + "\n")
if os.environ.get("FAKE_PROMPT_LOG"):         # prompt-content tests: FULL prompt per child,
    with open(os.environ["FAKE_PROMPT_LOG"], "a") as f:   # delimited (first line + full text)
        f.write("\n=====PROMPT=====\n" + q + "\n")
time.sleep(0.15)
if "CRASHME" in q:
    print("segfault-ish diagnostic prose, NO json")
    sys.exit(2)
import time as _t
if "SLEEP" in q:
    try: _t.sleep(float(q.split("SLEEP")[1].split()[0]))
    except Exception: pass
# ---- test_failures_0923 env-gated modes (Lane A; no behavior change without the env) ----
def _fake_state_row(n):
    """Register this child's --continue session title in state.db with n api
    calls — the runner's Q4 retry gate reads api_calls via wfcommon.child_metrics."""
    if "--continue" not in args:
        return
    import sqlite3
    title = args[args.index("--continue") + 1]
    c = sqlite3.connect(os.path.join(_FAKE_HOME, "state.db"))
    c.execute("create table if not exists sessions (id text primary key, title text, model text, input_tokens int, output_tokens int, "
              "cache_read_tokens int, reasoning_tokens int, api_call_count int, tool_call_count int, estimated_cost_usd real, "
              "last_activity_at real, last_activity_description text, ended_at real, started_at real)")
    t = time.time()
    c.execute("insert or replace into sessions values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              ("f-" + title, title, "fake", 0, 0, 0, 0, int(n), 0, 0.0, t, "", t, t))
    c.commit(); c.close()
if os.environ.get("FAKE_API_CALLS"):
    _fake_state_row(os.environ["FAKE_API_CALLS"])
_FAKE_MODE = os.environ.get("FAKE_MODE")
if _FAKE_MODE == "transport":      # stable marker oneline the runner can pin (oneshot escalation shape)
    print("Warning: Unknown toolsets: bogus")
    print("hermes -z: agent failed: openai.APIConnectionError. Connection error.")
    sys.exit(2)
if _FAKE_MODE == "provider400":    # 400 with inherited CLI advice lines that must be stripped
    print("Try re-running with a different model via /new or /model")
    print("hermes -z: agent failed: Error code: 400 - {'error': 'bad request'}")
    sys.exit(2)
if _FAKE_MODE == "unknown":        # dies with prose only — no machine-readable marker
    print("some daemon died unexpectedly, see your provider dashboard")
    sys.exit(7)
if _FAKE_MODE == "maxturns":       # prose mentions the cap — runner must NOT grep it (stays unknown)
    print("Agent reached its max turns budget and stopped.")
    sys.exit(2)
if _FAKE_MODE == "typed_maxturns": # core -Q turn report carries the loop's typed stamp
    _rp = os.environ.get("HERMES_QUIET_TURN_REPORT_FILE")
    if _rp:
        with open(_rp, "w") as f:
            json.dump({"pid": os.getpid(), "exit_code": 2, "error": "budget",
                       "reply": "partial answer before the cap",
                       "turn_exit_reason": "max_iterations_reached(61/60)"}, f)
    print("partial answer before the cap")
    sys.exit(2)
if _FAKE_MODE == "typed_empty_report":  # report exists WITHOUT a typed reason: must stay unknown
    _rp = os.environ.get("HERMES_QUIET_TURN_REPORT_FILE")
    if _rp:
        with open(_rp, "w") as f:
            json.dump({"pid": os.getpid(), "exit_code": 2, "error": "", "reply": "", "turn_exit_reason": ""}, f)
    print("prose death"); sys.exit(2)
if _FAKE_MODE == "untyped_report":   # tier self-report (0924): report exists but the
    _rp = os.environ.get("HERMES_QUIET_TURN_REPORT_FILE")   # typed key is ABSENT -> untyped
    if _rp:
        with open(_rp, "w") as f:
            json.dump({"pid": os.getpid(), "exit_code": 2, "error": "boom", "reply": ""}, f)
    print("prose death without the typed key"); sys.exit(2)
from pathlib import Path
if _FAKE_MODE == "poll_steer":     # B1: child pulls baked steering through the real door
    # and prints what it got — proves the file protocol + cursor, not model compliance.
    ROOT40 = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(ROOT40))
    import importlib.util as _il
    _spec = _il.spec_from_file_location("hw_door_fake", ROOT40 / "__init__.py")
    _door = _il.module_from_spec(_spec); _spec.loader.exec_module(_door)
    _res = _door.act_inbox({})
    _g = _FAKE_POLL_SECS = float(os.environ.get("FAKE_POLL_SLEEP", "0"))
    if _g:
        _t.sleep(_g)
    print("PULLED:" + json.dumps(_res.get("steering", [])))
    # second pull must be empty: the cursor advances exactly-once per spawn
    _res2 = _door.act_inbox({})
    print("REPULL:" + json.dumps(_res2.get("steering", [])))
    print("```json\n" + json.dumps({"pulled": _res.get("steering", []), "repull": _res2.get("steering", [])}) + "\n```")
    sys.exit(0)
if _FAKE_MODE == "hang":
    _t.sleep(float(os.environ.get("FAKE_HANG_SEC", "60")))
    sys.exit(0)
if _FAKE_MODE == "early":          # writes stdout, then keeps cooking (mid-run log growth)
    print("partial progress line, flushed early", flush=True)
    _t.sleep(float(os.environ.get("FAKE_EARLY_SLEEP", "3")))
if _FAKE_MODE == "bad_schema":     # valid json fence that fails the node's schema
    print("```json\n" + json.dumps({"wrong": True}) + "\n```")
    sys.exit(0)
if "FAILME" in q:
    print("", end="")  # simulate a crashed/empty child
    sys.exit(0)
if "STEER-" in q:
    import re
    m = re.search(r"STEER-(\w+)", q)
    print("```json\n" + json.dumps({"steered": m.group(1)}) + "\n```")
    sys.exit(0)
if "LIST:" in q:
    print("```json\n" + json.dumps({"result": ["a", "b", "c"]}) + "\n```")
    sys.exit(0)
if "JSON:" in q:   # 'JSON:{...}' on the goal line -> echo that exact object (branch/prune tests)
    line = next(l for l in q.splitlines() if "JSON:" in l)
    print("```json\n" + line.split("JSON:", 1)[1].strip() + "\n```")
    sys.exit(0)
print("```json\n" + json.dumps({"result": "ok", "goal": q.splitlines()[0][:80]}) + "\n```")
