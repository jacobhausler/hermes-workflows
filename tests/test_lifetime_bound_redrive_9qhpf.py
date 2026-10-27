#!/usr/bin/env python3
"""est-9qhpf (B1 of the PR#539 deep re-review): the persisted LIFETIME attempt
count must gate EVERY spawn — including the first spawn of a re-drive boot.

Defect at main tip 31dbf6a: _honor_retry_window only waits the deadline out;
the persisted-attempt seed lives inside _transient_retry, which runs AFTER a
spawn has already died. A runner SIGKILLed while the lifetime-3rd spawn (the
grant that spent the cap) is in flight resumes to a 4th child against a
lifetime bound of 3, and the settled death commits the mislabeled
error_class=transport attempts=1 attempts_log=[] (the boot-local log is empty
and the seeded-cap demotion never fires on that exit — est-ja41 record-vs-
ledger agreement broken across the restart seam). Repro shape:
probe_bound2.py from the review lane (RED at main tip: TOTAL_SPAWNS=4).

Pinned law:
  * a boot finding persisted attempts >= the node's transient cap refuses the
    spawn at the gate and commits the exhausted verdict with the SEEDED count
    (error_class=transport_exhausted, attempts=seed+1, attempts_log=persisted);
  * the refusal fires once per boot per window key (the first spawn of the
    node/item); in-boot ladders stay governed by their seeded loop, so a
    single fresh boot still runs the full ladder (1 + cap spawns) untouched;
  * the pre-sleep window save persists the attempts_log entries alongside
    {deadline, attempts}, so the refusal can commit the true history;
  * the integration case SIGKILLs exactly at the kill-during-third-spawn seam
    (solo node, FAKE_MODE=transport FAKE_API_CALLS=0, retry_backoff=[3,3],
    default cap 2 -> lifetime bound 3) and pins: the re-drive spawns NO 4th
    child, the committed record reads transport_exhausted with attempts 3 and
    the 2-entry persisted attempts_log, and the spent cap stays persisted.

Plain script, no pytest: exits non-zero on the first red.
"""
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
sys.path.insert(0, str(BUILD))

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


os.environ["HERMES_HOME"] = str(HERE / "home9k")
os.environ["WF_RUNS_ROOT"] = str(HERE / "home9k" / "workflows")
shutil.rmtree(HERE / "home9k", ignore_errors=True)
wf = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("wf_under_test", BUILD / "wf.py"))
importlib.util.spec_from_file_location("wf_under_test", BUILD / "wf.py").loader.exec_module(wf)


def fresh_run(name):
    r = Path(os.environ["WF_RUNS_ROOT"]) / name
    r.mkdir(parents=True, exist_ok=True)
    return r


def unit_meta(r, **over):
    m = {"_run": r, "_stop": threading.Event(), "_procs_lock": threading.Lock(),
         "_retries_left": 6, "_procs": {}, "_spawn_n": {}}
    m.update(over)
    return m


# ---------- unit half: the gate, the record, the persisted ledger ----------

# U1 a spent cap refuses the first spawn of the boot WITHOUT waiting the
#    (still-future) deadline: a refusal buys no information worth a sleep
run1 = fresh_run("u1")
(run1 / "retry-window.json").write_text(json.dumps(
    {"n": {"deadline": time.time() + 5.0, "attempts": 2, "log": []}}))
t0 = time.time()
spent = wf._honor_retry_window(unit_meta(run1), "n", node={"id": "n"})
el = time.time() - t0
check("U1 spent cap returns a refusal at the gate (no wait, no spawn)",
      isinstance(spent, dict) and spent.get("attempts") == 2 and el < 0.3,
      f"returned {spent!r} after {el:.2f}s")

# U2 an unspent cap seeds but never refuses; a past deadline is no wait either
run2 = fresh_run("u2")
(run2 / "retry-window.json").write_text(json.dumps(
    {"n": {"deadline": time.time() - 5.0, "attempts": 1, "log": []}}))
check("U2 attempts=1 < cap=2 passes the gate",
      wf._honor_retry_window(unit_meta(run2), "n", node={"id": "n"}) is None)
check("U2b a node-less caller (no cap to consult) still passes",
      wf._honor_retry_window(unit_meta(run2), "n") is None)

# U3 once-per-boot: the refusal guards the FIRST spawn of the key; a later
#    call for the same key in the same boot is the in-boot ladder seam and
#    must NOT refuse (run 1's own third spawn rides a persisted attempts==cap
#    save written right before its sleep — refusing there would under-grant).
m3 = unit_meta(run1)
first = wf._honor_retry_window(m3, "n", node={"id": "n"})
second = wf._honor_retry_window(m3, "n", node={"id": "n"})
check("U3 refusal is once-per-boot-per-key (in-boot respawns unaffected)",
      isinstance(first, dict) and second is None, f"{first!r} / {second!r}")

# U4 the exhausted verdict carries the seeded lifetime count and the persisted
#    log; a legacy window (no log key) still carries the count and class
rec4 = wf._window_spent_record(unit_meta(fresh_run("u4")), "n", None,
                               {"attempts": 2, "log": [{"attempt": 0, "error_class": "transport"},
                                                       {"attempt": 1, "error_class": "transport"}]})
check("U4 refusal record: transport_exhausted, attempts=seed+1, log carried",
      rec4["status"] == "failed" and rec4["error_class"] == "transport_exhausted"
      and rec4["attempts"] == 3 and rec4.get("spawn") == 2
      and len(rec4["attempts_log"]) == 2, json.dumps(rec4))
rec4b = wf._window_spent_record(unit_meta(fresh_run("u4b")), "n", None, {"attempts": 2})
check("U4b legacy window (no persisted log): count and class still right",
      rec4b["attempts"] == 3 and rec4b["error_class"] == "transport_exhausted"
      and rec4b["attempts_log"] == [], json.dumps(rec4b))

# U5 record-vs-ledger through the ladder: feeding the refusal record through
#    _transient_retry must NEVER respawn and must keep the verdict + counts
run5 = fresh_run("u5")
(run5 / "retry-window.json").write_text(json.dumps(
    {"n": {"deadline": time.time() - 1.0, "attempts": 2,
           "log": [{"attempt": 0, "error_class": "transport"},
                   {"attempt": 1, "error_class": "transport"}]}}))
calls5 = []
rec5 = wf._transient_retry(unit_meta(run5, retry_backoff=[0.05, 0.05]), rec4,
                           lambda **kw: calls5.append(1) or {"status": "done"},
                           "node", {"node": "n"}, node={"id": "n"})
kept5 = json.loads((run5 / "retry-window.json").read_text())
check("U5 seeded-cap settle: zero respawns, transport_exhausted, attempts=3, log=2",
      rec5["status"] == "failed" and rec5["error_class"] == "transport_exhausted"
      and rec5["attempts"] == 3 and len(rec5["attempts_log"]) == 2 and not calls5,
      json.dumps({k: rec5.get(k) for k in ("error_class", "attempts")}))
check("U5b the spent cap stays persisted across the settle",
      kept5["n"]["attempts"] == 2 and len(kept5["n"]["log"]) == 2, json.dumps(kept5))

# U6 the pre-sleep save persists the attempts_log alongside {deadline, attempts}
run6 = fresh_run("u6")
_orig_calls = wf._attempt_api_calls
wf._attempt_api_calls = lambda *a, **k: 0
snap = {}
try:
    def respawn6(**kw):
        if (run6 / "retry-window.json").exists():
            snap["window"] = json.loads((run6 / "retry-window.json").read_text())
        return {"status": "failed", "error_class": "transport", "error": "boom",
                "ms": 1, "attempts": 1, "spawn": 1}
    wf._transient_retry(unit_meta(run6, retry_backoff=[0.05, 0.05]),
                        {"status": "failed", "error_class": "transport",
                         "error": "boom", "ms": 1},
                        respawn6, "node", {"node": "n"}, node={"id": "n"})
finally:
    wf._attempt_api_calls = _orig_calls
w6 = snap.get("window", {}).get("n", {})
check("U6 the window save carries the attempt ledger (log entries)",
      isinstance(w6.get("log"), list) and len(w6["log"]) >= 1
      and w6["log"][0].get("error_class") == "transport", json.dumps(snap))

# ---------- integration half: SIGKILL at the kill-during-third-spawn seam ----------

HOME = HERE / "home9q"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
shutil.rmtree(HOME, ignore_errors=True)


def runner_env():
    return dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
                FAKE_LOG=str(HOME / "fake.log"), FAKE_MODE="transport",
                FAKE_API_CALLS="0")   # zero-call evidence: the Q4 retry gate's precondition


r = RUNS / "est9q-seam"
(r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
(r / "graph.json").write_text(json.dumps({"name": "est9q-seam", "nodes": [
    {"id": "a", "type": "agent", "goal": "G"}]}))
(r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "concurrency": 4,
                                        "node_timeout": 30,
                                        "retry_backoff": [3.0, 3.0]}))
(HOME / "fake.log").unlink(missing_ok=True)

proc = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", "est9q-seam"],
                        env=runner_env(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
seam = False
t_end = time.time() + 40
while time.time() < t_end:
    try:
        w = json.loads((r / "retry-window.json").read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        time.sleep(0.02); continue
    d = w.get("a") or {}
    logs = sorted((r / "logs").glob("*.log"))
    if (isinstance(d, dict) and d.get("attempts") == 2
            and d.get("deadline", 9e18) <= time.time() and len(logs) >= 3):
        # the lifetime-3rd spawn is in flight (or just died): SIGKILL the runner
        try:
            os.kill(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
        seam = True
        break
    time.sleep(0.02)
check("I0 the seam was reached (attempts==2, deadline past, 3rd spawn in flight)", seam)

t_restart = time.time()
subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", "est9q-seam"],
               env=runner_env(), capture_output=True, text=True, timeout=180)
logs = sorted((r / "logs").glob("*.log"))
rec = json.loads((r / "nodes" / "a.json").read_text())
check("I1 the re-drive spawned NO 4th child (lifetime bound 3 holds across the seam)",
      len(logs) == 3, f"spawn logs: {[l.name for l in logs]}")
check("I2 the committed record is transport_exhausted with the lifetime count 3 "
      "and the persisted attempts_log (never attempts=1 with attempts_log=[])",
      rec.get("error_class") == "transport_exhausted" and rec.get("attempts") == 3
      and len(rec.get("attempts_log") or []) == 2,
      json.dumps({k: rec.get(k) for k in ("error_class", "attempts")}
                 | {"log_len": len(rec.get("attempts_log") or [])}))
check("I2b the record was (re)written by the re-drive boot",
      (r / "nodes" / "a.json").stat().st_mtime >= t_restart - 0.5)
win = (r / "retry-window.json")
kept = json.loads(win.read_text()) if win.exists() else {}
check("I3 the spent cap and its ledger stay persisted after the settle",
      kept.get("a", {}).get("attempts") == 2
      and len(kept.get("a", {}).get("log") or []) == 2, json.dumps(kept))
# I4: settle is idempotent — a second re-drive refuses again, still 3 spawns,
#     same verdict (a spent cap never re-grants, boot after boot).
subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", "est9q-seam"],
               env=runner_env(), capture_output=True, text=True, timeout=180)
logs2 = sorted((r / "logs").glob("*.log"))
rec2 = json.loads((r / "nodes" / "a.json").read_text())
check("I4 a further re-drive still never spawns (TOTAL_SPAWNS stays 3)",
      len(logs2) == 3 and rec2.get("error_class") == "transport_exhausted"
      and rec2.get("attempts") == 3,
      f"spawn logs: {[l.name for l in logs2]}, {rec2.get('error_class')}@{rec2.get('attempts')}")

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
