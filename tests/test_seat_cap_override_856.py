#!/usr/bin/env python3
"""est-2ek.1.856 — the seat cap is an operator knob, validated where it can still refuse.

Failure (field report 2026-10-08, w54 spool): the cap was resolved at
import time into a baked default and the operator knobs were half-read —
`_max_seats` swallowed an unparseable WORKFLOW_MAX_SEATS into SEATS_DEFAULT
(`int(os.environ.get(...))` wrapped in `except ValueError: return 4`), config
`workflows.max_seats` was never read at all, and an 8/8-lane incident shipped
with the cap silently wrong. A typo'd cap is an operator INPUT error: it must
name itself and REFUSE, never ride a silent default (same law as
seat_forbidden_models / config_input).

Fix contract:
  wfcommon.seat_max_seats(meta_cap): precedence run.json meta max_seats >
    WORKFLOW_MAX_SEATS env > config workflows.max_seats (core-first
    load_config_readonly, stdlib lite-scan on bare hosts) > SEATS_DEFAULT.
    An operator-named cap must be an integer in [SEAT_CAP_FLOOR=4,
    SEAT_CAP_CEILING=16] or the explicit 0 off-sentinel (the documented
    est-g255 WORKFLOW_MAX_SEATS=0 guidance); anything else raises
    SeatCapError naming the knob. bool is a typo shape, not a cap.
  __init__.py act_run: the DOOR resolves the cap and refuses the whole launch
    (error, typed guidance) BEFORE any run-dir write or spawn.
  wf.py run_child: a runner that launched while the knob was valid and finds
    it invalid at the acquire instant fails the NODE closed with
    error_class="seat_cap" — never a silent default, never a blind spawn.

And the fairness ask folded in (est-2ek.1.856 sibling, the starve shape):
with cap 1, ONE long-waiting node plus eight freshly-launched short-run
waiters, admission order must equal arrival order (monotonic enqueued key).
Base's blind flock poll is first-poller-wins: the fresh arrivals re-took every
freed seat and the early waiter starved — at base the recorded admission order
is a race permutation, never the arrival order: RED. Head serializes on the
queue markers: exact arrival order: GREEN.

Run: cd tests && PYTHONPATH=/opt/hermes:.. WF_RUNS_ROOT=$(mktemp -d) python3 test_seat_cap_override_856.py
"""
import importlib.util, json, os, shutil, sys, threading, time
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

_spec_c = importlib.util.spec_from_file_location("hw_856_common", ROOT / "wfcommon.py")
wfc = importlib.util.module_from_spec(_spec_c)
_spec_c.loader.exec_module(wfc)

_spec = importlib.util.spec_from_file_location("hw_856_cap", ROOT / "wf.py")
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)

ME = os.getpid()

# ---------- C1: pure resolution — floor/ceiling/precedence/off-sentinel --------
def env_cap(val, meta=None, home=None):
    """Resolve through seat_max_seats with ONLY WORKFLOW_MAX_SEATS set (config
    unreachable: empty home, both core channels blocked)."""
    env = {} if val is None else {"WORKFLOW_MAX_SEATS": str(val)}
    with patch.dict(os.environ, env, clear=False), \
         patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
         patch.dict(os.environ, {"HERMES_HOME": str(home)}, clear=False):
        if val is None:
            os.environ.pop("WORKFLOW_MAX_SEATS", None)
        try:
            return wfc.seat_max_seats(meta), None
        except wfc.SeatCapError as e:
            return None, str(e)

import tempfile
_tmp = Path(tempfile.mkdtemp(prefix="seatcap-856-"))

got, err = env_cap(6, home=_tmp)
check("C1a: WORKFLOW_MAX_SEATS=6 overrides SEATS_DEFAULT", got == 6, f"got={got} err={err}")
got, err = env_cap(None, home=_tmp)
check("C1b: unset knobs -> SEATS_DEFAULT (4)", got == wfc.SEATS_DEFAULT == 4, f"got={got}")
got, err = env_cap(0, home=_tmp)
check("C1c: explicit 0 is the documented semaphore-off sentinel (est-g255), not a refusal",
      got == 0, f"got={got} err={err}")
got, err = env_cap(3, home=_tmp)
check("C1d: cap below the floor (3) raises SeatCapError naming the knob — never a silent default",
      got is None and err and "WORKFLOW_MAX_SEATS" in err and "3" in err, f"got={got} err={err}")
got, err = env_cap(17, home=_tmp)
check("C1e: cap above the ceiling (17) raises SeatCapError", got is None and err and "17" in err,
      f"got={got} err={err}")
got, err = env_cap("banana", home=_tmp)
check("C1f: unparseable cap raises with 'not an integer'",
      got is None and err and "not an integer" in err, f"got={got} err={err}")
got, err = env_cap(True, home=_tmp)
check("C1g: bool True is a typo shape, not a cap of 1 — raises", got is None and bool(err),
      f"got={got} err={err}")
got, err = env_cap(8, meta=2, home=_tmp)
check("C1h: the per-run meta max_seats outranks the env knob (door's existing knob untouched)",
      got == 2, f"got={got} err={err}")
got, err = env_cap(8, meta=0, home=_tmp)
check("C1i: per-run meta 0 still opts out of the semaphore entirely", got == 0, f"got={got}")
got, err = env_cap(999, meta=2, home=_tmp)
check("C1j: an invalid env value never reaches resolution when meta wins (meta is the escape hatch)",
      got == 2, f"got={got} err={err}")

# config workflows.max_seats (stdlib lite-scan half: core channels blocked)
_cfg_home = _tmp / "cfghome"
_cfg_home.mkdir()
(_cfg_home / "config.yaml").write_text("model:\n  default: x\n\nworkflows:\n  max_seats: 6\n")
with patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
     patch.dict(os.environ, {"HERMES_HOME": str(_cfg_home)}), \
     patch.dict(os.environ, {}, clear=False):
    os.environ.pop("WORKFLOW_MAX_SEATS", None)
    got = None; err = None
    try:
        got = wfc.seat_max_seats()
    except wfc.SeatCapError as e:
        err = str(e)
check("C2a: config workflows.max_seats is read on bare hosts (stdlib lite-scan)", got == 6,
      f"got={got} err={err}")
(_cfg_home / "config.yaml").write_text("model:\n  default: x\n\nworkflows:\n  max_seats: 99\n")
with patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
     patch.dict(os.environ, {"HERMES_HOME": str(_cfg_home)}):
    os.environ.pop("WORKFLOW_MAX_SEATS", None)
    got = None; err = None
    try:
        got = wfc.seat_max_seats()
    except wfc.SeatCapError as e:
        err = str(e)
check("C2b: config cap outside [4,16] raises naming config workflows.max_seats",
      got is None and err and "config workflows.max_seats" in err and "99" in err,
      f"got={got} err={err}")
(_cfg_home / "config.yaml").write_text("model:\n  default: x\n\nworkflows:\n  max_seats: 6\n")
with patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
     patch.dict(os.environ, {"HERMES_HOME": str(_cfg_home), "WORKFLOW_MAX_SEATS": "8"}):
    got = wfc.seat_max_seats()
check("C2c: env outranks config (env 8 over config 6)", got == 8, f"got={got}")

# ---------- C3: the door refuses an invalid cap BEFORE any write or spawn ------
_spec_d = importlib.util.spec_from_file_location("hw_856_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(_spec_d)
_spec_d.loader.exec_module(door)
import wf_test_isolation as _iso856; _iso856.install(door)
FAKE = str(ROOT / "tests" / "fake")

def mini_graph():
    return {"name": "cap-856", "nodes": [
        {"id": "worker", "type": "agent", "goal": "OK"},
        {"id": "next", "type": "echo", "after": ["worker"], "output": {"reached": True}}]}

with tempfile.TemporaryDirectory(prefix="cap856-door-") as td:
    home = Path(td)
    (home / "config.yaml").write_text("model:\n  default: safe\n")
    with patch.dict(os.environ, HERMES_HOME=td, WF_RUNS_ROOT=str(home / "workflows"),
                    WORKFLOW_MAX_SEATS="banana"), \
         patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
         patch.object(door, "_spawn_runner"):
        refused = door.act_run({"graph": mini_graph(), "hermes_bin": FAKE})
    check("C3a: the door refuses an unparseable WORKFLOW_MAX_SEATS at submit",
          isinstance(refused, dict) and "invalid seat cap" in str(refused.get("error", "")),
          json.dumps(refused)[:300])
    check("C3b: the refusal names both knobs and the valid range",
          "WORKFLOW_MAX_SEATS" in str(refused.get("error", ""))
          and "workflows.max_seats" in str(refused.get("error", ""))
          and str(wfc.SEAT_CAP_FLOOR) in str(refused.get("error", ""))
          and str(wfc.SEAT_CAP_CEILING) in str(refused.get("error", "")),
          json.dumps(refused)[:300])
    check("C3c: refusal happened BEFORE any run-dir write (runs root never created)",
          not (home / "workflows").exists(),
          f"runs root contents: {list((home / 'workflows').iterdir()) if (home / 'workflows').exists() else '-'}")
    with patch.dict(os.environ, HERMES_HOME=td, WF_RUNS_ROOT=str(home / "workflows"),
                    WORKFLOW_MAX_SEATS="3"), \
         patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
         patch.object(door, "_spawn_runner"):
        refused_low = door.act_run({"graph": mini_graph(), "hermes_bin": FAKE})
    check("C3d: the door refuses a cap below the floor (3)",
          "invalid seat cap" in str(refused_low.get("error", "")), json.dumps(refused_low)[:200])
    with patch.dict(os.environ, HERMES_HOME=td, WF_RUNS_ROOT=str(home / "workflows"),
                    WORKFLOW_MAX_SEATS="6"), \
         patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
         patch.object(door, "_spawn_runner"):
        accepted = door.act_run({"graph": mini_graph(), "hermes_bin": FAKE})
    check("C3e: a valid override (6) launches normally", bool(accepted.get("run_id")),
          json.dumps(accepted)[:200])
    with patch.dict(os.environ, HERMES_HOME=td, WF_RUNS_ROOT=str(home / "workflows"),
                    WORKFLOW_MAX_SEATS="0"), \
         patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
         patch.object(door, "_spawn_runner"):
        off = door.act_run({"graph": mini_graph(), "hermes_bin": FAKE})
    check("C3f: WORKFLOW_MAX_SEATS=0 (documented opt-out) still launches — the door must not turn the escape hatch into a refusal",
          bool(off.get("run_id")), json.dumps(off)[:200])

# ---------- C4: the runner fails the node typed seat_cap, never a blind spawn --
HOME_R = HERE / "home-856-cap-runner"
shutil.rmtree(HOME_R, ignore_errors=True)
HOME_R.mkdir()
(HOME_R / "config.yaml").write_text("model:\n  default: cap856\n")
os.environ["HERMES_HOME"] = str(HOME_R)
os.environ["WF_RUNS_ROOT"] = str(HOME_R / "workflows")
seats_r = HOME_R / "seats"
os.environ["WF_SEATS_DIR"] = str(seats_r)
os.environ["WORKFLOW_MAX_SEATS"] = "banana"
run = HOME_R / "workflows" / "r-cap"
(run / "nodes").mkdir(parents=True)
node = {"id": "capn", "type": "agent", "goal": "ok"}
(run / "graph.json").write_text(json.dumps({"name": "r", "nodes": [node]}))
meta = {"_run": run, "hermes_bin": str(HERE / "nonexistent-hermes-must-never-run"),
        "_spawn_n": {}, "_procs_lock": threading.Lock(), "_procs": {},
        "_stop": threading.Event(), "node_timeout": 30}
res = wf.run_child(meta, node, {"capn": node}, "ok", "", None, skey="wf:r-cap:capn")
check("C4a: an invalid cap at the acquire instant fails the NODE with error_class=seat_cap",
      isinstance(res, dict) and res.get("status") == "failed"
      and res.get("error_class") == "seat_cap",
      json.dumps(res)[:300])
check("C4b: the typed error names the knobs and the range (no silent SEATS_DEFAULT)",
      "WORKFLOW_MAX_SEATS" in str(res.get("error", "")) and "banana" in str(res.get("error", "")),
      json.dumps(res)[:300])
check("C4c: zero spawns — the seat was never acquired and nothing was admitted",
      not seats_r.exists() or not list(seats_r.glob("*.json")),
      f"tickets: {[p.name for p in seats_r.glob('*.json')] if seats_r.exists() else '-'}")
check("C4d: 'seat_cap' is in the closed ERROR_CLASSES set", "seat_cap" in wf.ERROR_CLASSES)
os.environ.pop("WORKFLOW_MAX_SEATS", None)
shutil.rmtree(HOME_R, ignore_errors=True)

# ---------- C5: FIFO starvation — 9 concurrent waiters, arrival order wins ------
HOME_F = HERE / "home-856-starve"
shutil.rmtree(HOME_F, ignore_errors=True)
HOME_F.mkdir()
os.environ["HERMES_HOME"] = str(HOME_F)
os.environ["WF_RUNS_ROOT"] = str(HOME_F / "workflows")
seats_f = HOME_F / "seats"
os.environ["WF_SEATS_DIR"] = str(seats_f)

holder = wf._seat_acquire(seats_f, "S-holder", 1, 20.0)
check("C5 setup: holder holds the only seat", isinstance(holder, Path) and holder.exists(),
      f"got={holder}")

order = []
order_lock = threading.Lock()
admitted = []          # (name, ticket|None) — released by the waiter itself
names = ["W-early"] + [f"S{i}" for i in range(1, 9)]   # 1 long waiter + 8 fresh short runs
def _waiter(nm):
    t = wf._seat_acquire(seats_f, nm, 1, 30.0)
    with order_lock:
        order.append(nm)
        admitted.append(t)
    time.sleep(0.25)                                    # simulated short run on the seat
    if isinstance(t, Path):
        try: wf._seat_release(t)
        except OSError: pass

threads = []
for nm in names:
    th = threading.Thread(target=_waiter, args=(nm,), daemon=True)
    th.start()
    threads.append(th)
    time.sleep(0.4 if nm == names[0] else 0.15)         # staggered arrival
time.sleep(0.6)                                          # everyone is registered and waiting
wf._seat_release(holder)
deadline = time.time() + 30
while time.time() < deadline:
    with order_lock:
        n = len(order)
    if n == len(names):
        break
    time.sleep(0.05)
for th in threads:
    th.join(10)
with order_lock:
    final_order = list(order)
    tix = list(admitted)
check("C5a: every waiter was admitted (bounded wait holds)", len(final_order) == len(names),
      f"admitted={final_order}")
check("C5b: admission order == arrival order — the long waiter never starves behind "
      "short-run churn (base's first-poller-wins yields a race permutation)",
      final_order == names, f"arrival={names} admitted={final_order}")
q = seats_f / "queue"
check("C5c: no queue marker outlived its waiter",
      not q.exists() or not list(q.glob("*.json")),
      f"{[m.name for m in q.glob('*.json')] if q.exists() else '-'}")
for t in tix:
    if isinstance(t, Path):
        try: wf._seat_release(t)
        except OSError: pass
shutil.rmtree(HOME_F, ignore_errors=True)
shutil.rmtree(_tmp, ignore_errors=True)

print(("" if ok else "FAILURES PRESENT ") + "DONE")
sys.exit(0 if ok else 1)
