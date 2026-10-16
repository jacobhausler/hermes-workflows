#!/usr/bin/env python3
"""est-mg5o2 x est-2ek.1.856/857 — the pool-recorded cap composed with FIFO
admission and the validated operator knobs (the merge pins).

test_pool_seat_cap_mg5o2.py proves the pool arbiter on its own; the 856 suite
proves FIFO + the typed seat_cap on its own. This file pins the three places
the two laws MEET after the merge, each one a place a wrong graft would pass
both parent suites and still be wrong:

  P1  FIFO inside the pool cap: admission is `live < POOL cap` AND no
      strictly-older live queue marker. Caller cap 1 (stale) over a recorded
      pool cap of 2: two freed seats go to the two OLDEST waiters, in arrival
      order, and a late arrival never jumps them.
  P2  seed law: the pool seed rides wfcommon.seat_max_seats. An invalid
      operator knob is NEVER recorded as the pool's global cap — even when an
      explicit run.json max_seats lets `_max_seats` pass — it fails the node
      closed as error_class=seat_cap before any ticket, marker or .cap exists.
  P3  seat_wait prints the POOL truth (recorded cap, not the process's own
      resolution) through the typed re-resolve catch (deep review D1).

Run: cd tests && python3 test_pool_seat_cap_fifo_mg5o2.py
"""
import importlib.util, json, os, shutil, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "home-mg5o2-fifo"
shutil.rmtree(BUILD, ignore_errors=True)
BUILD.mkdir(parents=True)
os.environ["HERMES_HOME"] = str(BUILD / "home")
(BUILD / "home").mkdir()
(BUILD / "home" / "config.yaml").write_text("model:\n  default: mg5o2fifo\n")
# est-2ek.1.762: never inherit the lane's runs root — pin it to this test's scratch
os.environ["WF_RUNS_ROOT"] = str(BUILD / "runs")
for k in ("WORKFLOW_MAX_SEATS", "HERMES_PROFILE", "WF_SEATS_DIR"):
    os.environ.pop(k, None)

_spec = importlib.util.spec_from_file_location("hw_mg5o2_fifo", ROOT / "wf.py")
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

def seed_cap(seats, v):
    Path(seats).mkdir(parents=True, exist_ok=True)
    Path(seats, ".cap").write_text(str(v))

# ============ P1: FIFO inside the pool cap ====================================
seats = BUILD / "seats-fifo"
seed_cap(seats, 2)
h1 = wf._seat_acquire(seats, "H1", 1, 5.0, pool_seed=99)     # caller cap 1 is stale
h2 = wf._seat_acquire(seats, "H2", 1, 5.0, pool_seed=99)
check("P1 setup: stale caller cap=1 does not cap — the pool's recorded 2 admits both holders",
      isinstance(h1, Path) and isinstance(h2, Path) and h1.exists() and h2.exists(),
      f"h1={h1} h2={h2}")

order, order_lock, admitted = [], threading.Lock(), []
def _waiter(nm):
    t = wf._seat_acquire(seats, nm, 1, 20.0, pool_seed=99)
    with order_lock:
        order.append(nm)
        admitted.append(t)
names = ["W-early", "W-mid", "W-late"]
ths = []
for nm in names:
    th = threading.Thread(target=_waiter, args=(nm,), daemon=True)
    th.start(); ths.append(th)
    time.sleep(0.35)                         # staggered, strictly ordered arrival
time.sleep(0.6)                              # everyone registered and waiting
qd = seats / "queue"
markers_before = len(list(qd.glob("*.json"))) if qd.exists() else 0
check("P1: all three waiters hold a queue marker while the pool is full",
      markers_before == 3, f"markers={markers_before}")
wf._seat_release(h1)
t_end = time.time() + 10
while time.time() < t_end:
    with order_lock:
        if len(order) >= 1:
            break
    time.sleep(0.05)
time.sleep(0.8)                              # a second admission would have landed by now
with order_lock:
    first = list(order)
check("P1: ONE freed seat admits exactly the OLDEST waiter (live<pool cap AND no older marker)",
      first == ["W-early"], f"admitted={first}")
wf._seat_release(h2)
t_end = time.time() + 10
while time.time() < t_end:
    with order_lock:
        if len(order) >= 2:
            break
    time.sleep(0.05)
time.sleep(0.8)
with order_lock:
    second = list(order)
check("P1: the second freed seat admits the next-oldest — arrival order, no late jump",
      second == ["W-early", "W-mid"], f"admitted={second}")
for t in list(admitted):
    if isinstance(t, Path):
        wf._seat_release(t)
t_end = time.time() + 10
while time.time() < t_end:
    with order_lock:
        if len(order) >= 3:
            break
    time.sleep(0.05)
for th in ths:
    th.join(10)
with order_lock:
    final = list(order)
    for t in admitted:
        if isinstance(t, Path):
            wf._seat_release(t)
check("P1: full arrival order held and every waiter was admitted",
      final == names, f"admitted={final}")
check("P1: pool cap survived the whole churn (still the recorded 2) and no marker outlived its waiter",
      (seats / ".cap").read_text() == "2"
      and (not qd.exists() or not list(qd.glob("*.json"))),
      f"cap={(seats / '.cap').read_text()} markers={[m.name for m in qd.glob('*.json')] if qd.exists() else '-'}")

# ============ P2: the pool seed rides the validator, fail-closed ==============
os.environ["WORKFLOW_MAX_SEATS"] = "2"       # below the landed floor of 4
try:
    wf._seat_pool_seed()
    seed_err = None
except wf.SeatCapError as e:
    seed_err = e
check("P2: _seat_pool_seed raises SeatCapError for a sub-floor operator cap (no honest-degradation inline resolve)",
      seed_err is not None and "WORKFLOW_MAX_SEATS" in str(seed_err), f"{seed_err!r}")
os.environ["WORKFLOW_MAX_SEATS"] = "6"
check("P2: a valid operator cap seeds through the same validator (env 6 -> 6)",
      wf._seat_pool_seed() == 6)
os.environ["WORKFLOW_MAX_SEATS"] = "0"
check("P2: the explicit 0 sentinel stays a local disable (seed 0 records nothing)",
      wf._seat_pool_seed() == 0)
os.environ.pop("WORKFLOW_MAX_SEATS", None)

def make_meta(tag, **extra):
    run = BUILD / "workflows" / tag
    (run / "nodes").mkdir(parents=True)
    node = {"id": "n", "type": "agent", "goal": "ok"}
    (run / "graph.json").write_text(json.dumps({"name": tag, "nodes": [node]}))
    meta = {"_run": run, "hermes_bin": str(HERE / "nonexistent-hermes-must-never-run"),
            "_spawn_n": {}, "_procs_lock": threading.Lock(), "_procs": {},
            "_stop": threading.Event(), "node_timeout": 2}
    meta.update(extra)
    return meta, node, tag

# explicit run.json max_seats lets _max_seats PASS (meta wins) while the env
# seed is garbage: the seed path itself must still fail closed — nothing recorded.
seats_p2 = BUILD / "seats-p2"
os.environ["WF_SEATS_DIR"] = str(seats_p2)
os.environ["WORKFLOW_MAX_SEATS"] = "banana"
meta, node, tag = make_meta("r-seed", max_seats=8)
res = wf.run_child(meta, node, {"n": node}, "ok", "", None, skey=f"wf:{tag}:n")
check("P2: explicit meta max_seats + invalid env seed fails the NODE closed as seat_cap, naming the knob",
      isinstance(res, dict) and res.get("status") == "failed"
      and res.get("error_class") == "seat_cap" and "banana" in str(res.get("error", "")),
      json.dumps(res, default=str)[:300])
check("P2: nothing was recorded or admitted — no .cap, no ticket, no queue marker",
      not (seats_p2 / ".cap").exists()
      and not (seats_p2.exists() and list(seats_p2.rglob("*.json"))),
      f"left={[p.name for p in seats_p2.rglob('*')] if seats_p2.exists() else '-'}")
os.environ.pop("WORKFLOW_MAX_SEATS", None)
os.environ.pop("WF_SEATS_DIR", None)

# ============ P3: seat_wait prints the POOL truth through the typed catch =====
seats_p3 = BUILD / "seats-p3"
seed_cap(seats_p3, 5)                         # pool truth 5; this process's env says 4
os.environ["WF_SEATS_DIR"] = str(seats_p3)
os.environ["WORKFLOW_MAX_SEATS"] = "4"
held = [wf._seat_acquire(seats_p3, f"P3-{i}", 4, 5.0, pool_seed=4) for i in range(5)]
check("P3 setup: five holders fill the 5-seat pool (env 4 does not cap them)",
      all(isinstance(t, Path) and t.exists() for t in held), f"{[str(t) for t in held]}")
meta, node, tag = make_meta("r-wait")
try:
    res = wf.run_child(meta, node, {"n": node}, "ok", "", None, skey=f"wf:{tag}:n")
    escaped = None
except wf.SeatCapError as e:
    res, escaped = None, e
check("P3: a full pool ends the node typed seat_wait (never a swallowed crash)",
      escaped is None and isinstance(res, dict) and res.get("error_class") == "seat_wait",
      f"escaped={escaped!r} res={json.dumps(res, default=str)[:300]}")
check("P3: the seat_wait row reports the POOL's recorded cap (5), not this process's env (4)",
      isinstance(res, dict) and "cap=5" in str(res.get("error", "")),
      json.dumps(res, default=str)[:300])
for t in held:
    if isinstance(t, Path):
        wf._seat_release(t)
os.environ.pop("WORKFLOW_MAX_SEATS", None)
os.environ.pop("WF_SEATS_DIR", None)

shutil.rmtree(BUILD, ignore_errors=True)
print(("" if ok else "FAILURES PRESENT ") + "DONE")
sys.exit(0 if ok else 1)
