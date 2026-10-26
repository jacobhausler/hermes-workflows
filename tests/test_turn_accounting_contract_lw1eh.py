#!/usr/bin/env python3
"""est-lw1eh (#387 option-b ruling): the turn/accounting contract pin.

The documented contract (references/budgets.md "Turn accounting"):
`max_turns` is billed per API call — `api_calls == turns` is ONE counter, and a
lane that hits the cap must be machine-distinguishable from a lane that
finished cleanly. This test pins the whole chain deterministically with the
fake hermes (FAKE_MODE=budget_lane burns exactly one api_call per turn through
the state.db row the read model already joins):

  (1) spawn contract: the author's cap rides the child CLI as `--max-turns <cap>`
      (FAKE_ARGV_LOG line per spawn), and the child's consumed api_calls reach
      that cap before anything else kills it (wall untouched, generous timeout);
  (2) typed death: node record failed + error_class cap_exhausted + the error
      names the turn budget and the cap; door stop_reason.class carries it; the
      run clock says phase=expired / exhaustion_reason=turn_cap;
  (3) re-drivable: exactly one bounded re-drive (retry.bounded default 1 ->
      two spawns, record attempts == 2), logged as node.retry error_class=cap_exhausted;
  (4) distinguishable: the twin lane answers BELOW the cap (FAKE_BUDGET_STOP_AT)
      -> done, metrics.api_calls == the stop-at count, no cap evidence anywhere.

Harness mirrors tests/test_budget_cue_bbfy.py (mk/wf/load_door).
"""
import importlib.util
import json, os, shutil, subprocess, sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))

ROOT = BUILD.parent
sys.path.insert(0, str(ROOT))
HOME = BUILD / "home_lw1eh"
os.environ["HERMES_HOME"] = str(HOME)  # door's run_dir()/act_status() resolve home in-process
os.environ["WF_RUNS_ROOT"] = str(Path(os.environ["HERMES_HOME"]) / "workflows")  # est-2ek.1.762 pin
RUNS = HOME / "workflows"
env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS))
FAKE = str(BUILD / "fake")

CAP = 10
TICK = "0.2"

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1

def mk(run_id, nodes):
    r = RUNS / run_id
    if r.exists(): shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 120}))
    return r

def wf(run_id, argv_log, log_path, extra_env=None):
    for p in (argv_log, log_path):
        if p.exists(): p.unlink()
    e = dict(env, FAKE_LOG=str(log_path), FAKE_ARGV_LOG=str(argv_log))
    for k in ("FAKE_API_CALLS", "FAKE_ATTEMPT_DIR", "FAKE_BUDGET_STOP_AT"):
        e.pop(k, None)
    e.update(extra_env or {})
    p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                       env=e, capture_output=True, text=True, timeout=240)
    return p.stdout.strip()

def load_door():
    spec = importlib.util.spec_from_file_location("turn_contract_door", ROOT / "__init__.py")
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    return door

def events(r):
    p = r / "events.jsonl"
    out = []
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(l))
            except Exception:
                pass
    return out

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()

door = load_door()
import wfcommon as _c

# ---- the capped lane: burns api_calls one per turn until the cap trips it ----
r = mk("lw1eh-cap", [{"id": "a", "type": "agent", "goal": "lw1eh cap trip", "max_turns": CAP}])
wf("lw1eh-cap", BUILD / "argv_lw1eh_cap.log", BUILD / "fake_lw1eh_cap.log",
   {"FAKE_MODE": "budget_lane", "FAKE_BUDGET_TICK": TICK})

# ---- (1) the spawn contract: author cap == the CLI turn cap the child ran under ----
argv_lines = [l for l in (BUILD / "argv_lw1eh_cap.log").read_text().splitlines() if l.strip()]
check("(1) the capped lane really ran twice (one bounded re-drive, no more)",
      len(argv_lines) == 2, f"{len(argv_lines)} spawn lines")
check("(1) every spawn carried the author cap as --max-turns <cap>",
      all(f"--max-turns {CAP}" in l for l in argv_lines), json.dumps(argv_lines)[:300])

rec = json.loads((r / "nodes" / "a.json").read_text())
# ---- (2) the death is typed, and the counter that tripped it is api_calls ----
check("(2) the capped lane died typed cap_exhausted (failed, not a clean finish)",
      rec.get("status") == "failed" and rec.get("error_class") == "cap_exhausted",
      json.dumps({k: rec.get(k) for k in ("status", "error_class")}))
check("(2) the error names the turn budget and the cap it hit",
      "turn budget" in (rec.get("error") or "") and f"max_turns={CAP}" in (rec.get("error") or ""),
      (rec.get("error") or "")[:200])
check("(2) the attempt ledger says two attempts (bounded ladder default 1)",
      rec.get("attempts") == 2, str(rec.get("attempts")))
st = door.act_status({"run_id": "lw1eh-cap"})
nm = (st.get("nodes") or {}).get("a", {}).get("metrics") or {}
check("(2) the read model's api_calls reached the cap (the counter that kills)",
      isinstance(nm.get("api_calls"), int) and nm["api_calls"] >= CAP,
      json.dumps(nm))
sr = st.get("stop_reason")
check("(2) door stop_reason.class is cap_exhausted",
      isinstance(sr, dict) and sr.get("class") == "cap_exhausted", json.dumps(st)[:240])
if (r / "budget_cue" / "a").exists():
    check("(2) cue-then-cap death stamps stop_reason.kind=budget",
          isinstance(sr, dict) and sr.get("kind") == "budget", json.dumps(sr))
from unittest.mock import patch
with patch.object(_c, "runner_alive", return_value=False):
    clock = _c.run_state(r)["nodes"]["a"].get("clocks") or {}
check("(2) run clock: phase expired with exhaustion_reason turn_cap",
      clock.get("phase") == "expired" and clock.get("exhaustion_reason") == "turn_cap",
      json.dumps(clock))

# ---- (3) the death rode the bounded ladder: node.retry names the class ----
evs = [e for e in events(r) if e.get("event") == "node.retry"
       and e.get("node") == "a" and e.get("error_class") == "cap_exhausted"]
check("(3) events carry node.retry error_class=cap_exhausted (re-drivable, not final)",
      len(evs) == 1, json.dumps([e.get("event") for e in events(r)])[:300])
retries = [e for e in events(r) if str(e.get("event", "")).endswith(".retry")
           and e.get("error_class") == "cap_exhausted"]
check("(3) exactly one bounded re-drive event (no silent extra replays)",
      len(retries) == 1, f"{len(retries)} retry events")

# ---- (4) the twin: answers BELOW the cap -> done, and legibly not a cap death ----
r2 = mk("lw1eh-clean", [{"id": "b", "type": "agent", "goal": "lw1eh clean finish", "max_turns": CAP}])
STOP_AT = 4   # below the budget-cue soft-cap (CAP - default margin 5): no cue, no cap
wf("lw1eh-clean", BUILD / "argv_lw1eh_clean.log", BUILD / "fake_lw1eh_clean.log",
   {"FAKE_MODE": "budget_lane", "FAKE_BUDGET_TICK": TICK, "FAKE_BUDGET_STOP_AT": str(STOP_AT)})
rec2 = json.loads((r2 / "nodes" / "b.json").read_text())
check("(4) the below-cap lane finished done", rec2.get("status") == "done", str(rec2.get("status")))
st2 = door.act_status({"run_id": "lw1eh-clean"})
nm2 = (st2.get("nodes") or {}).get("b", {}).get("metrics") or {}
check("(4) its api_calls stopped at the answer point, under the cap",
      nm2.get("api_calls") == STOP_AT, json.dumps(nm2))
blob = json.dumps(st2) + json.dumps(rec2)
check("(4) no cap evidence anywhere on the clean finish",
      "cap_exhausted" not in blob and "turn_cap" not in blob and "stop_reason" not in st2,
      blob[:260])
lines2 = [l for l in (BUILD / "argv_lw1eh_clean.log").read_text().splitlines() if l.strip()]
check("(4) the clean lane spawned exactly once", len(lines2) == 1, str(len(lines2)))

print(("PASS" if fails == 0 else "FAIL") + f" test_turn_accounting_contract_lw1eh ({fails} failing checks)")
sys.exit(0 if fails == 0 else 1)
