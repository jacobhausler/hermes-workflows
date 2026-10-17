#!/usr/bin/env python3
"""est-2ek.1.818: status must not call a live runner's running child `pending` just
because the child's pid lives in another container's pid namespace.

Runner liveness already crosses namespaces (flock on runner.lock, 91b9a3de), but
child verification (`_verify_spawn_rec`: os.kill + /proc argv) is blind there, so a
node whose record says status=running and whose runner holds the lock read
`pending` with no active_spawn / idle_s — a false stall for the babysitting parent.

Law under test (display path only; adoption + reaper keep the strict law):
  - visible, identity-verified child        -> running, active_spawn WITHOUT `verified`
  - pid invisible here + runner lock HELD + efp-valid status=running record +
    spawn-ledger `child` row after the last `runner` row and no later `child_end`
                                            -> running, active_spawn verified=False
  - any of those missing                    -> pending (never fabricated)
  - a VISIBLE pid failing identity (PID reuse) is never relaxed

RED on origin/main: case B reads `pending`.
Hand-built run dirs, stdlib-only (flock held by a helper process, like a runner).
"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon

HOME = Path(tempfile.mkdtemp(prefix="home-foreign-ns-818-", dir=str(ROOT)))
os.environ["HERMES_HOME"] = str(HOME)

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}" if detail else msg
    ok += 1; print("PASS", msg)

NODE = {"id": "carry", "type": "agent", "goal": "work"}
BYID = {"carry": NODE}
SKEY = "wf:t-foreign-ns-818:carry:a1dc2ad4.9e26b6"
procs = []

def dead_pid():
    p = subprocess.Popen(["true"]); p.wait()
    assert not Path(f"/proc/{p.pid}").exists()
    return p.pid   # reaped: absent from /proc exactly like a pid in another namespace

def mk(rid, pid, *, ledger, holder=True, efp_ok=True):
    r = HOME / "workflows" / rid
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": rid, "nodes": [NODE]}))
    (r / "run.json").write_text(json.dumps({"name": rid, "hermes_bin": "/bin/true"}))
    rec = {"status": "running", "pid": pid, "skey": SKEY, "attempt": 0,
           "started": "2026-10-08T01:28:21+00:00", "log_path": str(r / "logs" / "carry.a0.log"),
           "efp": wfcommon.efp(BYID, NODE) if efp_ok else "0" * 16,
           "fp_rule_version": wfcommon.FP_RULE_VERSION}
    (r / "nodes" / "carry.json").write_text(json.dumps(rec))
    if ledger is not None:
        (r / "spawn-ledger.jsonl").write_text("".join(json.dumps(x) + "\n" for x in ledger))
    (r / "runner.lock").write_text("")
    if holder:   # the runner's flock, held from "another container"
        procs.append(subprocess.Popen(["flock", str(r / "runner.lock"), "sleep", "120"]))
        time.sleep(0.4)
    return r

def row(role, pid=0, skey=None):
    return {"ts": "2026-10-08T01:28:21+00:00", "pid": pid, "role": role, "node": None if role == "runner" else "carry",
            "index": None, "skey": skey, "purpose": "workflow-runner"}

def carry(r):
    st = wfcommon.run_state(r)
    return st["runner_live"], st["nodes"]["carry"]

try:
    # A: visible, identity-verified child -> strict path, unchanged shape
    title = SKEY + "#a0"
    live = subprocess.Popen(["/bin/sh", "-c", "sleep 120", title]); procs.append(live)
    time.sleep(0.3)
    rA = mk("t-a", live.pid, ledger=[row("runner", 1), row("child", live.pid, SKEY)])
    lv, n = carry(rA)
    check(lv and n["status"] == "running" and "verified" not in n["active_spawn"],
          "A: visible verified child reads running with the strict (unmarked) identity", json.dumps(n))

    # B: pid invisible + lock held + ledger child after runner, not ended -> running, marked unverified
    pid = dead_pid()
    rB = mk("t-b", pid, ledger=[row("runner", 1), row("child", pid, SKEY)])
    lv, n = carry(rB)
    check(lv and n["status"] == "running", "B: foreign-namespace child of the live runner reads running", json.dumps(n))
    sp = n.get("active_spawn") or {}
    check(sp.get("verified") is False and sp.get("pid") == pid and sp.get("skey") == title and sp.get("unverified_because"),
          "B: identity is explicitly verified=False with the exact #aN session title", json.dumps(sp))
    cur = wfcommon.current_attempt({}, n["active_spawns"])
    check(cur["live"] == 1, "B: current_attempt counts the spawn live (idle_s joins by session title)", json.dumps(cur))

    # C: child_end after the child row -> ended, pending
    pid = dead_pid()
    rC = mk("t-c", pid, ledger=[row("runner", 1), row("child", pid, SKEY), row("child_end", pid, SKEY)])
    check(carry(rC)[1]["status"] == "pending", "C: ended child (child_end row) stays pending")

    # D: child row precedes the latest runner row -> predecessor's child, pending
    pid = dead_pid()
    rD = mk("t-d", pid, ledger=[row("runner", 1), row("child", pid, SKEY), row("runner", 2)])
    check(carry(rD)[1]["status"] == "pending", "D: crashed predecessor's child (older runner generation) stays pending")

    # E: no ledger -> pending
    pid = dead_pid()
    rE = mk("t-e", pid, ledger=None)
    check(carry(rE)[1]["status"] == "pending", "E: no spawn-ledger -> no proof -> pending")

    # F: runner lock not held (and no pid file) -> no live runner, no relaxation
    pid = dead_pid()
    rF = mk("t-f", pid, ledger=[row("runner", 1), row("child", pid, SKEY)], holder=False)
    lv, n = carry(rF)
    check((not lv) and n["status"] == "pending" and "active_spawn" not in n,
          "F: runner lock free -> not live, node pending, no active_spawn", json.dumps(n))

    # G: stale efp -> pending
    pid = dead_pid()
    rG = mk("t-g", pid, ledger=[row("runner", 1), row("child", pid, SKEY)], efp_ok=False)
    check(carry(rG)[1]["status"] == "pending", "G: efp-stale record stays pending")

    # H: pid VISIBLE but not our child (PID reuse: skey absent from argv) -> never relaxed
    other = subprocess.Popen(["/bin/sh", "-c", "sleep 120", "unrelated-title"]); procs.append(other)
    time.sleep(0.3)
    rH = mk("t-h", other.pid, ledger=[row("runner", 1), row("child", other.pid, SKEY)])
    check(carry(rH)[1]["status"] == "pending", "H: visible pid failing identity (PID reuse) is not relaxed")

    # I: the strict law itself is untouched (adoption/reaper share it)
    rec = wfcommon.jload(rB / "nodes" / "carry.json")
    check(wfcommon._verify_spawn_rec(rB, NODE, BYID, rec) is None,
          "I: _verify_spawn_rec still refuses the unverifiable pid (adoption stays strict)")
    check(wfcommon.active_child(rB, NODE, BYID) is None, "I: active_child (runner adoption) still None")
finally:
    for p in procs:
        try: p.kill()
        except Exception: pass
    import shutil; shutil.rmtree(HOME, ignore_errors=True)

print(f"ALL PASS ({ok})")
