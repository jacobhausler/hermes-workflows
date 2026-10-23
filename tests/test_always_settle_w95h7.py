#!/usr/bin/env python3
"""est-w95h7 (atbrace:hw-i6e, SYNTHESIS #21): the always-settle law over the
spawn seam of the spawn-backed child path (wf.py run_child).

Three fault injections:
  A. SIGKILL at the started-marker instant (test hook fires between the marker
     write and the exec). The marker is the started record: status=running,
     pid=None (an unproven spawn is never adoptable), capture path named and
     already open as a file under the run dir. The door reaper settles the
     crash with a claim-bound interruption receipt derived from the record's
     own file name; a respawn re-drives to done. The lane is never stranded
     started-but-unsettled, and across the crash the child executed exactly
     once.
  B. Missing child binary. The typed spawn refusal commits a settled failure
     record over the marker: error_class=spawn, attempts=1, no retry over an
     ENOENT launcher death.
  C. Capture failure. The spawn log open fails (test-only deterministic fault
     hook, same discipline as WF_TEST_KILL_ITEM_AT_FINALIZE). The failure
     lands as a typed spawn record naming the capture path, never an untyped
     crash stranding.

Group-kill on timeout is the pre-existing #61/#80 law (start_new_session at
spawn, killpg on every death); its proofs live in the established tree-death
tests (test_zombie_settle_448, the #80 aux deadline law), not here.

Standalone, stdlib-only:
  python3 tests/test_always_settle_w95h7.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "__init__.py").exists():
    raise SystemExit("WF_TEST_BUILD names a plugin BUILD root (this test loads its __init__.py); got " + str(BUILD))

HOME = HERE / "home-alwayssettle-w95h7"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)
sys.path.insert(0, str(BUILD))
import wfcommon

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

def jload(p):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None

def spawn_wf(run_id, extra_env=None):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / ("fake_" + run_id + ".log")),
               **(extra_env or {}))
    return subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)

def events(r):
    try:
        return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
    except (FileNotFoundError, ValueError):
        return []

def wait_for(pred, timeout=60, tick=0.1):
    end = time.time() + timeout
    while time.time() < end:
        if pred():
            return True
        time.sleep(tick)
    return False

SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}
NODE = {"id": "seed", "type": "agent", "goal": "always-settle work", "schema": SCHEMA}

def seed_run(name, hermes_bin):
    run = RUNS / name
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    (run / "graph.json").write_text(json.dumps({"name": name, "nodes": [NODE]}))
    (run / "run.json").write_text(json.dumps(
        {"hermes_bin": str(hermes_bin), "concurrency": 4, "node_timeout": 30}))
    return run

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()

byid = {"seed": NODE}

# ---------------------------------------------------------------- A. SIGKILL at the started marker
run = seed_run("w95h7-crash", FAKE)
p1 = spawn_wf("w95h7-crash", {"WF_TEST_KILL_AT_SPAWN_MARKER": "1"})
reached = wait_for(lambda: (run / "nodes" / "seed.json").exists())
rc1 = p1.wait(60) if reached else p1.wait(60)
check("A1 runner SIGKILLed at the started-marker instant",
      reached and rc1 == -9, f"reached={reached} rc={rc1}")
rec = jload(run / "nodes" / "seed.json") or {}
check("A1 the started marker precedes the exec (running, pid unproven)",
      rec.get("status") == "running" and "pid" in rec and rec.get("pid") is None,
      json.dumps({k: rec.get(k) for k in ("status", "pid")}))
check("A1 the marker carries spawn identity and efp",
      rec.get("skey") and rec.get("attempt") == 0
      and rec.get("efp") == wfcommon.efp(byid, NODE)
      and rec.get("fp_rule_version") == wfcommon.FP_RULE_VERSION,
      json.dumps({k: rec.get(k) for k in ("skey", "attempt", "efp", "fp_rule_version")}))
lp = Path(str(rec.get("log_path", "")))
check("A1 capture is a run-dir file, never a pipe",
      bool(str(lp)) and lp.is_file() and run in lp.parents
      and str(rec.get("prompt_path", "")).endswith(".prompt.md")
      and Path(str(rec.get("prompt_path"))).is_file(), str(lp))

# door reaper: the crash settles as claim-bound typed truth, derived from the
# record's own file name (the interruption receipt sits beside it by name).
spec = importlib.util.spec_from_file_location("settle_door", BUILD / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
door._reap_silent_death(run)
st, cur = wfcommon.node_rec(run, NODE, byid)
check("A2 the unproven spawn reads interrupted, never a live claim",
      st == "pending" and cur.get("status") == "interrupted"
      and cur.get("error_class") == "crashed",
      f"{st} {json.dumps(cur if isinstance(cur, dict) else {})}")
ir = jload(run / "interruptions" / "seed.json") or {}
check("A2 interruption receipt is claim-bound to the marker",
      ir.get("claim", {}).get("skey") == rec.get("skey")
      and ir.get("claim", {}).get("attempt") == rec.get("attempt")
      and ir.get("claim", {}).get("pid") is None, json.dumps(ir))
check("A2 the reap is loud",
      any(e.get("event") == "node.interrupted" and e.get("node") == "seed"
          for e in events(run)))

p2 = spawn_wf("w95h7-crash")
check("A3 the re-drive commits a settled done record",
      wait_for(lambda: (jload(run / "nodes" / "seed.json") or {}).get("status") == "done")
      and p2.wait(60) == 0)
fake_lines = (HOME / "fake_w95h7-crash.log").read_text().splitlines() \
    if (HOME / "fake_w95h7-crash.log").exists() else []
check("A3 the child executed exactly once across the crash",
      len(fake_lines) == 1, f"{len(fake_lines)} execs")

# ---------------------------------------------------------------- B. missing child binary
# The runner re-resolves a missing ABSOLUTE pin through PATH (documented boot
# law); the sandboxed PATH makes the bare fallback unresolvable too, so the
# death lands at the exec as ENOENT, exactly as the field shape demands.
(HOME / "emptybin").mkdir()
run_b = seed_run("w95h7-nobin", HOME / "no-such-hermes-bin")
p3 = spawn_wf("w95h7-nobin", {"PATH": str(HOME / "emptybin")})
check("B the missing-binary death commits a settled typed record",
      wait_for(lambda: (jload(run_b / "nodes" / "seed.json") or {}).get("status") == "failed")
      and (jload(run_b / "nodes" / "seed.json") or {}).get("error_class") == "spawn"
      and (jload(run_b / "nodes" / "seed.json") or {}).get("attempts") == 1,
      json.dumps(jload(run_b / "nodes" / "seed.json") or {}))

# ---------------------------------------------------------------- C. capture failure
# The capture write fails at the open (test-only deterministic fault hook,
# same discipline as WF_TEST_KILL_ITEM_AT_FINALIZE: a real ENOSPC race is
# undeterministic, the seam under test is the typed settlement).
run_c = seed_run("w95h7-capture", FAKE)
p4 = spawn_wf("w95h7-capture", {"WF_TEST_FAIL_SPAWN_LOG_OPEN": "1"})
settled_c = wait_for(lambda: (jload(run_c / "nodes" / "seed.json") or {}).get("status")
                     in ("done", "partial", "failed"), timeout=30)
rec_c = jload(run_c / "nodes" / "seed.json") or {}
check("C capture failure settles typed, never an untyped stranding",
      settled_c and rec_c.get("status") == "failed"
      and rec_c.get("error_class") == "spawn"
      and "capture" in str(rec_c.get("error", "")).lower(),
      json.dumps({k: rec_c.get(k) for k in ("status", "error_class", "error")}))

print("RESULT PASS" if ok else "RESULT FAIL")
sys.exit(0 if ok else 1)
