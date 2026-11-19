#!/usr/bin/env python3
"""#692 slice 1 — the engine lifecycle REDRIVE verb (act_redrive + wf.py redrive).

The wake-consumer law (issue #692, binding): redrive takes an explicit
mode in {same-fingerprint-resume, new-fingerprint-rerun} with NO silent
default, and its response enumerates which nodes re-drive and which
completed-work receipts the resume preserves. The two failure modes it
replaces (hand-run setsid + node-record deletion): a silent re-run of
completed nodes, and an opaque refusal under creation-override drift.

Laws pinned here:
  M  mode law: missing mode and unknown mode both refuse, naming the flag and
     the closed set; the refusal is typed (redrive_mode_required). A done run
     and an unknown run_id refuse honestly.
  R  resume law: over a genuinely failed run (one failed lane, upstream
     receipts efp-valid), same-fingerprint-resume re-drives ONLY the failed
     lane — the completed node's record bytes stay byte-identical and its
     child is NEVER re-spawned — and the run reaches done. The response
     enumerates re_drive=[failed] and the preserved receipts.
  D  drift law: when a committed completed receipt sits under an effective
     fingerprint the current graph no longer produces, resume-mode refuses
     (error_type redrive_fingerprint_drift, names the nodes, NOTHING written:
     the failed record and the runner verdict stay, no run.redriven event) and
     rerun-mode accepts it: the drifted receipts join re_drive under the efp
     override rule and the run re-runs them to done.
  S  scheduler law: a pending watchdog redrive.request is CONSUMED by the
     verb (file gone, watchdog.redrive_consumed on the event record, response
     says consumed) and the P40 grant ledger is zeroed at the boundary
     (grant_ledger_reset in the response) — the verb consumes the tick's
     mechanism and forks no second scheduler.
  C  CLI law: `wf.py redrive <id>` with no --mode exits 1 on the door's OWN
     typed refusal (the CLI never invents a default); an unknown extra
     argument is a usage fault (exit 2).

Style: PASS/FAIL lines + exit code (test_failures_0923 house style). The stub
hermes fails a FAILME-marked goal until $STUB_OK_FILE exists, so a lane goes
failed on run 1 and succeeds on the re-drive with zero product-code branches.
"""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
os.environ["WF_TEST_BUILD"] = str(BUILD)
HOME = HERE / "home692"
RUNS = HOME / "workflows"
shutil.rmtree(HOME, ignore_errors=True); HOME.mkdir(); RUNS.mkdir()
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)     # #71 law: env pin, not home alone
os.environ["FAKE_LOG"] = str(HOME / "fake.log")
sys.path.insert(0, str(BUILD))

STUB = HOME / "hermes"
STUB.write_text("#!/usr/bin/env python3\n"
    "import json, os, sys\n"
    "args = sys.argv[1:]\n"
    "q = open(args[args.index('--query-file') + 1]).read() if '--query-file' in args else ''\n"
    "log = os.environ.get('FAKE_LOG', '')\n"
    "if log:\n"
    "    open(log, 'a').write((q.splitlines() or [''])[0] + '\\n')\n"
    "ok_file = os.environ.get('STUB_OK_FILE', '')\n"
    "if 'FAILME' in q and (not ok_file or not os.path.exists(ok_file)):\n"
    "    sys.exit(0)\n"
    "print('```json\\n' + json.dumps({'result': 'ok'}) + '\\n```')\n")
STUB.chmod(0o755)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

def nodes(goal_suffix=""):
    return [{"id": "prep", "type": "agent", "goal": "GOAL-PREP build the base" + goal_suffix},
            {"id": "worka", "type": "agent", "after": ["prep"],
             "goal": "GOAL-WORKA downstream work" + goal_suffix},
            {"id": "bad", "type": "agent", "goal": "FAILME bad lane" + goal_suffix}]

def mk(rid, graph_nodes=None):
    r = RUNS / rid
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": rid, "nodes": graph_nodes or nodes()}))
    (r / "run.json").write_text(json.dumps(
        {"hermes_bin": str(STUB), "concurrency": 1, "node_timeout": 30,
         "retry_backoff": [0.05, 0.05]}))
    return r

def boot(rid, timeout=180):
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", rid],
                          env=dict(os.environ, HERMES_HOME=str(HOME)),
                          capture_output=True, text=True, timeout=timeout).stdout.strip()

def events(r):
    try:
        return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
    except FileNotFoundError:
        return []

def log_lines():
    try:
        return Path(os.environ["FAKE_LOG"]).read_text().splitlines()
    except FileNotFoundError:
        return []

def rec_bytes(r, nid):
    return (r / "nodes" / f"{nid}.json").read_bytes()

specd = importlib.util.spec_from_file_location("hw692_door", BUILD / "__init__.py")
door = importlib.util.module_from_spec(specd); specd.loader.exec_module(door)
try:
    import wf_test_isolation as _iso71; _iso71.install(door)   # #71 writer pin
except Exception:
    pass
def call(**a):
    return json.loads(door.handle(a))

# ================= M: the mode law (no silent default) =================
out = call(action="redrive", run_id="nope", mode="same-fingerprint-resume")
check("M0 unknown run_id refuses honestly", out.get("error") == "unknown run_id", out)

# ================= R: the real failed run (fresh runner, stub-driven) =================
OKF = HOME / "b-ok"          # stub flips to success once this exists
os.environ.pop("STUB_OK_FILE", None)
os.environ["STUB_OK_FILE"] = str(OKF)     # the stub READS the path; the file's ABSENCE fails FAILME
r1 = mk("rd692-resume")
booted = boot("rd692-resume")
check("R0 the first boot ends on a failed verdict (bad lane, stub prose)",
      "WORKFLOW_FAILED" in booted
      and json.loads((r1 / "runner_exit.json").read_text())["reason"].startswith(("blocked by failed", "aborted by")),
      booted[-200:])
prep_before = rec_bytes(r1, "prep")
bad_rec = json.loads((r1 / "nodes" / "bad.json").read_text())
check("R0b prep/worka committed done, bad committed failed",
      json.loads((r1 / "nodes" / "prep.json").read_text())["status"] == "done"
      and bad_rec["status"] == "failed", json.dumps(bad_rec)[:160])
prep_spawns_before = sum("GOAL-PREP" in l for l in log_lines())
fail_spawns_before = sum("FAILME" in l for l in log_lines())

# no mode / bogus mode refuse BEFORE anything else is touched
out = call(action="redrive", run_id="rd692-resume")
check("M1 missing mode: typed refusal naming the flag and the closed set",
      out.get("ok") is False and out.get("error_type") == "redrive_mode_required"
      and "mode" in out.get("error", "") and "same-fingerprint-resume" in out.get("error", "")
      and "new-fingerprint-rerun" in out.get("error", ""), json.dumps(out)[:220])
out = call(action="redrive", run_id="rd692-resume", mode="redo")
check("M2 unknown mode refuses with the same typed shape",
      out.get("ok") is False and out.get("error_type") == "redrive_mode_required", json.dumps(out)[:160])
check("M3 the refusal wrote nothing (verdict and failed record intact)",
      (r1 / "runner_exit.json").exists() and (r1 / "nodes" / "bad.json").exists()
      and rec_bytes(r1, "prep") == prep_before)

# the scheduled continuation + a spendy grant ledger ride along (S law); the
# stub flips FAILME lanes to success only once its OK file exists on disk
OKF.write_text("go")
(r1 / "redrive.request").write_text(json.dumps(
    {"at": time.time(), "expires_at": time.time() + 3600, "reason": "wedged runner lock: heal refused", "tries": 2}))
(r1 / "retry-window.json").write_text(json.dumps(
    {"bad:0": {"deadline": time.time() - 1, "attempts": 2, "log": [{"n": 1, "rc": 1}]}}))

out = call(action="redrive", run_id="rd692-resume", mode="same-fingerprint-resume")
check("R1 resume-mode redrive answers ok and enumerates exactly the failed lane",
      out.get("ok") is True and out.get("re_drive") == ["bad"], json.dumps(out)[:260])
check("R2 the response enumerates the preserved completed receipts",
      {p["node"] for p in out.get("preserved", [])} == {"prep", "worka"}
      and all(p["status"] == "done" and p.get("efp") for p in out.get("preserved", [])),
      json.dumps(out.get("preserved"))[:220])
check("S1 the scheduled redrive.request was CONSUMED (file gone, response says so)",
      out.get("scheduled_redrive") == "consumed" and not (r1 / "redrive.request").exists())
check("S2 the P40 grant ledger zeroed at the generation boundary",
      out.get("grant_ledger_reset") == {"bad:0": 2}, json.dumps(out.get("grant_ledger_reset")))

deadline = time.monotonic() + 90
st = {}
while time.monotonic() < deadline:
    st = call(action="status", run_id="rd692-resume")
    if st.get("status") in ("done", "failed"):
        break
    time.sleep(0.3)
check("R3 the resumed run reaches done (bad lane re-driven, stub now answers)",
      st.get("status") == "done", json.dumps(st.get("status")))
prep_spawns_after = sum("GOAL-PREP" in l for l in log_lines())
fail_spawns_after = sum("FAILME" in l for l in log_lines())
check("R4 completed work was NEVER re-run: the prep record is byte-identical and no new prep spawn",
      rec_bytes(r1, "prep") == prep_before and prep_spawns_after == prep_spawns_before,
      f"spawns {prep_spawns_before}->{prep_spawns_after}")
check("R5 the failed lane WAS re-driven (exactly one more stub spawn than its failed budget)",
      fail_spawns_after - fail_spawns_before in (1, 2),
      f"spawns {fail_spawns_before}->{fail_spawns_after}")
evs = events(r1)
check("R6 the transaction is on the event record (run.redriven + watchdog receipts)",
      any(e.get("event") == "run.redriven" and e.get("mode") == "same-fingerprint-resume"
          and e.get("re_drive") == ["bad"] for e in evs)
      and any(e.get("event") == "watchdog.redrive_consumed" for e in evs)
      and any(e.get("event") == "watchdog.grant_ledger_reset" for e in evs),
      json.dumps([e.get("event") for e in evs])[-260:])
out = call(action="redrive", run_id="rd692-resume", mode="same-fingerprint-resume")
check("M4 a done run refuses redrive naming the status (nothing re-runs)",
      out.get("ok") is False and "done" in out.get("error", ""), json.dumps(out)[:160])

# ================= D: the drift law (creation overrides moved) =================
os.environ.pop("STUB_OK_FILE", None)     # bad fails again
r2 = mk("rd692-drift")
boot("rd692-drift")
prep_before2 = rec_bytes(r2, "prep")
g2 = json.loads((r2 / "graph.json").read_text())
g2["nodes"][0]["goal"] = "GOAL-PREP build the base — AMENDED"      # an override drifted the graph
(r2 / "graph.json").write_text(json.dumps(g2))
(r2 / "retry-window.json").unlink(missing_ok=True)
os.environ["STUB_OK_FILE"] = str(OKF)
out = call(action="redrive", run_id="rd692-drift", mode="same-fingerprint-resume")
check("D1 drift makes resume-mode REFUSE, naming the drifted receipts",
      out.get("ok") is False and out.get("error_type") == "redrive_fingerprint_drift"
      and set(out.get("drifted", [])) >= {"prep", "worka"} and out.get("re_drive") == ["bad"],
      json.dumps(out)[:260])
check("D2 the refusal wrote NOTHING (failed record, verdict, receipt bytes intact)",
      (r2 / "runner_exit.json").exists() and (r2 / "nodes" / "bad.json").exists()
      and rec_bytes(r2, "prep") == prep_before2
      and not any(e.get("event") == "run.redriven" for e in events(r2)))
out = call(action="redrive", run_id="rd692-drift", mode="new-fingerprint-rerun")
check("D3 rerun-mode accepts the drift: drifted receipts join re_drive under the efp law",
      out.get("ok") is True and set(out.get("re_drive")) == {"bad", "prep", "worka"}
      and out.get("preserved") == [], json.dumps(out)[:260])
deadline = time.monotonic() + 90
st = {}
while time.monotonic() < deadline:
    st = call(action="status", run_id="rd692-drift")
    if st.get("status") in ("done", "failed"):
        break
    time.sleep(0.3)
check("D4 the rerun reaches done and the drifted receipt was actually re-run",
      st.get("status") == "done" and rec_bytes(r2, "prep") != prep_before2,
      json.dumps(st.get("status")))

# ================= C: the CLI rides the door's own mode law =================
r3 = mk("rd692-cli")
boot("rd692-cli")
cli = subprocess.run([sys.executable, str(BUILD / "wf.py"), "redrive", "rd692-cli"],
                     env=dict(os.environ, HERMES_HOME=str(HOME)),
                     capture_output=True, text=True, timeout=120)
check("C1 CLI without --mode exits 1 on the door's typed refusal (no default invented)",
      cli.returncode == 1 and "REFUSED" in cli.stdout and "redrive_mode_required" in cli.stdout,
      cli.stdout[-200:] + cli.stderr[-200:])
cli = subprocess.run([sys.executable, str(BUILD / "wf.py"), "redrive", "rd692-cli", "--mode=again"],
                     env=dict(os.environ, HERMES_HOME=str(HOME)),
                     capture_output=True, text=True, timeout=120)
check("C2 CLI --mode=<bogus> exits 1 with the closed-set refusal",
      cli.returncode == 1 and "same-fingerprint-resume" in cli.stdout, cli.stdout[-200:])
cli = subprocess.run([sys.executable, str(BUILD / "wf.py"), "redrive", "rd692-cli", "--force"],
                     env=dict(os.environ, HERMES_HOME=str(HOME)),
                     capture_output=True, text=True, timeout=120)
check("C3 CLI usage fault (unknown argument) exits 2 without touching the run",
      cli.returncode == 2 and "unknown argument" in cli.stdout and (r3 / "runner_exit.json").exists(),
      cli.stdout[-160:])

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
