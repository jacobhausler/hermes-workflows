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

# ---------- C6 (deep review D1): the seat_wait error string must never        --
# re-raise SeatCapError out of run_child. The seat_wait branch re-resolves
# _max_seats(meta) inline to print the cap. Shape: the knob is VALID when the
# node resolves it at the acquire instant (4658) and the operator breaks it
# WHILE the node sits on the seat wait; the inline call at 4694 then raises
# SeatCapError out of run_child and the caller's harvest swallows it as
# `crashed` — the typed seat_cap law (C4) leaks as an untyped death.
# Contract: the seat_wait branch must fail the node TYPED seat_cap (same
# handling as the primary acquire site), never let the exception escape.
HOME_W = HERE / "home-856-waitflip"
shutil.rmtree(HOME_W, ignore_errors=True)
HOME_W.mkdir()
(HOME_W / "config.yaml").write_text("model:\n  default: cap856\n")
os.environ["HERMES_HOME"] = str(HOME_W)
os.environ["WF_RUNS_ROOT"] = str(HOME_W / "workflows")
seats_w = HOME_W / "seats"
os.environ["WF_SEATS_DIR"] = str(seats_w)
os.environ["WORKFLOW_MAX_SEATS"] = "4"          # valid at the acquire instant
run_w = HOME_W / "workflows" / "r-wait"
(run_w / "nodes").mkdir(parents=True)
node_w = {"id": "waitn", "type": "agent", "goal": "ok"}
(run_w / "graph.json").write_text(json.dumps({"name": "r-wait", "nodes": [node_w]}))

# hold ALL 4 seats (cap 4 via env, no meta knob) so the child's acquire times
# out into the seat_wait branch; flip the knob to invalid mid-wait.
holder_w = [wf._seat_acquire(seats_w, f"C6-holder-{i}", 4, 20.0) for i in range(4)]
check("C6 setup: holder holds all 4 seats (cap 4 via env)",
      all(isinstance(t, Path) and t.exists() for t in holder_w),
      f"got={[str(t) for t in holder_w]}")
meta_w = {"_run": run_w, "hermes_bin": str(HERE / "nonexistent-hermes-must-never-run"),
          "_spawn_n": {}, "_procs_lock": threading.Lock(), "_procs": {},
          "_stop": threading.Event(), "node_timeout": 2}
_flip = threading.Timer(0.3, lambda: os.environ.__setitem__("WORKFLOW_MAX_SEATS", "banana"))
_flip.start()
try:
    res_w = wf.run_child(meta_w, node_w, {"waitn": node_w}, "ok", "", None,
                         skey="wf:r-wait:waitn")
    escaped = None
except wf.SeatCapError as e:         # D1 shape: the inline re-resolve escaping
    escaped, res_w = e, None
finally:
    _flip.cancel()
    os.environ.pop("WORKFLOW_MAX_SEATS", None)
    for t in holder_w:
        if isinstance(t, Path):
            try: wf._seat_release(t)
            except OSError: pass
check("C6a: a knob that breaks mid seat-wait never raises SeatCapError out of "
      "run_child — the node fails typed, never a swallowed `crashed`",
      escaped is None and isinstance(res_w, dict),
      f"escaped={escaped!r} res={str(res_w)[:200]}")
check("C6b: the typed verdict is seat_cap naming the broken knob (same handling as "
      "the primary acquire path) — never a swallowed unknown/crashed death",
      isinstance(res_w, dict) and res_w.get("status") == "failed"
      and res_w.get("error_class") == "seat_cap"
      and "banana" in str(res_w.get("error", "")),
      json.dumps(res_w, default=str)[:300])
check("C6c: zero spawns and no ticket/queue marker left behind by the broken-knob death",
      not seats_w.exists() or not [p for p in seats_w.rglob("*.json")
                                   if p not in holder_w],
      f"left: {[p.name for p in seats_w.rglob('*.json') if p not in holder_w] if seats_w.exists() else '-'}")
shutil.rmtree(HOME_W, ignore_errors=True)

# ---------- C7 (deep review D2): the advertised per-run opt-out is the truth. --
# Three error strings advertise "the per-run opt-out is graph/run.json max_seats
# : 0" (door submit refusal, runner seat_cap, runner seat_wait). An advertised
# contract must be TRUE: the graph key is accepted by the structural validator
# (integer in [4,16] or 0), act_run bakes it into run.json, and the runner's
# _max_seats honours it (C1 already proves meta wins and 0 disables). A plain
# run NEVER grows the key (solo golden key-set law).
with tempfile.TemporaryDirectory(prefix="cap856-d2-") as td:
    home = Path(td)
    (home / "config.yaml").write_text("model:\n  default: safe\n")
    base_env = {"HERMES_HOME": td, "WF_RUNS_ROOT": str(home / "workflows")}

    def _door_run(g, extra_env=None):
        env = dict(base_env)
        env.pop("WORKFLOW_MAX_SEATS", None)
        if extra_env:
            env.update(extra_env)
        with patch.dict(os.environ, env, clear=False), \
             patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
             patch.object(door, "_spawn_runner"):
            os.environ.pop("WORKFLOW_MAX_SEATS", None)
            return door.act_run({"graph": g, "hermes_bin": FAKE})

    def _run_json(res):
        # the run.json of THIS launch only — matched by its run_id, never rglob
        rid = res.get("run_id") if isinstance(res, dict) else None
        if not rid:
            return None
        for p in (home / "workflows").rglob("run.json"):
            if rid in str(p.parent):
                return json.loads(p.read_text())
        return None

    off = _door_run(dict(mini_graph(), max_seats=0))
    rj = _run_json(off)
    check("C7a: the door ACCEPTS the advertised graph max_seats: 0 (not 'unknown graph key') "
          "and run.json records it — the advertised opt-out is a real contract",
          bool(off.get("run_id")) and isinstance(rj, dict) and rj.get("max_seats") == 0,
          json.dumps(off)[:200] + f" run.json={str(rj)[:200]}")
    cap8 = _door_run(dict(mini_graph(), max_seats=8))
    rj8 = _run_json(cap8)
    check("C7b: a valid graph cap (8) launches and lands in run.json for the runner",
          bool(cap8.get("run_id")) and isinstance(rj8, dict) and rj8.get("max_seats") == 8,
          json.dumps(cap8)[:200] + f" run.json={str(rj8)[:200]}")
    bad_ms = _door_run(dict(mini_graph(), max_seats="banana"))
    check("C7c: an invalid graph max_seats refuses at submit naming the key and the "
          "shape (value error, not 'unknown graph key'), before any write",
          isinstance(bad_ms, dict) and "max_seats" in str(bad_ms.get("error", ""))
          and "unknown graph key" not in str(bad_ms.get("error", ""))
          and "integer" in str(bad_ms.get("error", "")),
          json.dumps(bad_ms)[:300])
    bad_lo = _door_run(dict(mini_graph(), max_seats=3))
    check("C7d: graph max_seats below the floor (3) refuses with the range",
          isinstance(bad_lo, dict) and "max_seats" in str(bad_lo.get("error", ""))
          and str(wfc.SEAT_CAP_FLOOR) in str(bad_lo.get("error", "")),
          json.dumps(bad_lo)[:300])
    bad_bool = _door_run(dict(mini_graph(), max_seats=True))
    check("C7e: bool graph max_seats is the typo shape, refused (same law as env/config)",
          isinstance(bad_bool, dict) and "max_seats" in str(bad_bool.get("error", "")),
          json.dumps(bad_bool)[:300])
    plain = _door_run(mini_graph())
    rjp = _run_json(plain)
    check("C7f: a plain run (no max_seats declared) never grows the key — the solo "
          "golden key-set law is untouched",
          bool(plain.get("run_id")) and "max_seats" not in (rjp or {}),
          json.dumps(plain)[:150] + f" keys={sorted((rjp or {}).keys())}")

# ---------- C8 (deep review D2, amend half): run.json's max_seats is the        --
# CURRENT graph's truth. An amend that declares the key bakes it; an amend whose
# replacement graph DROPS the key must drop it too — a stale opt-out surviving a
# graph swap would leave the runner honouring a cap its own graph no longer
# declares (the same set-or-remove law the include notes follow).
with tempfile.TemporaryDirectory(prefix="cap856-d2-amend-") as td:
    home = Path(td)
    (home / "config.yaml").write_text("model:\n  default: safe\n")

    def _amend_env(fn, *a, **k):
        with patch.dict(os.environ, {"HERMES_HOME": td,
                                     "WF_RUNS_ROOT": str(home / "workflows")}, clear=False), \
             patch.dict(sys.modules, {"hermes_cli.config": None, "hermes_constants": None}), \
             patch.object(door, "_spawn_runner"), \
             patch.object(door, "_ping_route_once",
                          lambda p, m: {"liveness": "unknown"}), \
             patch.object(door, "_resume_after_action", lambda *x, **y: "no-runner"):
            os.environ.pop("WORKFLOW_MAX_SEATS", None)
            return fn(*a, **k)

    made = _amend_env(door.act_run, {"graph": mini_graph(), "hermes_bin": FAKE})
    rid = made.get("run_id")
    rdir = home / "workflows" / rid if rid else None
    rjam = json.loads((rdir / "run.json").read_text()) if rdir else {}
    check("C8 setup: plain run armed, run.json carries no max_seats",
          bool(rid) and "max_seats" not in rjam, json.dumps(made)[:200])
    am1 = _amend_env(door.act_amend, {"run_id": rid, "graph": dict(mini_graph(), max_seats=0)})
    rjam1 = json.loads((rdir / "run.json").read_text()) if rdir else {}
    check("C8a: an amend declaring graph max_seats bakes it into run.json "
          "(the advertised per-run contract survives a graph swap)",
          not (isinstance(am1, dict) and am1.get("error")) and rjam1.get("max_seats") == 0,
          json.dumps(am1, default=str)[:200] + f" run.json={str(rjam1)[:200]}")
    am2 = _amend_env(door.act_amend, {"run_id": rid, "graph": mini_graph()})
    rjam2 = json.loads((rdir / "run.json").read_text()) if rdir else {}
    check("C8b: an amend whose graph DROPS max_seats removes it from run.json — "
          "no stale opt-out may outlive the graph that declared it",
          not (isinstance(am2, dict) and am2.get("error")) and "max_seats" not in rjam2,
          json.dumps(am2, default=str)[:200] + f" run.json={str(rjam2)[:200]}")
    am3 = _amend_env(door.act_amend, {"run_id": rid, "graph": dict(mini_graph(), max_seats=True)})
    check("C8c: amend measures the key with the SAME law as run (bool refused, "
          "before graph.json is swapped)",
          isinstance(am3, dict) and "max_seats" in str(am3.get("error", "")),
          json.dumps(am3, default=str)[:300])

print(("" if ok else "FAILURES PRESENT ") + "DONE")
sys.exit(0 if ok else 1)
