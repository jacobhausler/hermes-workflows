#!/usr/bin/env python3
"""est-mg5o2 — POOL-level seat admission: the cap is the .seats pool's recorded
truth, not each inheriting process's environment.

Measured defect (2026-10-11 owner squad launch): estate pool .seats held 6/12
at an 8-squad launch under WORKFLOW_MAX_SEATS=12 — child CLI processes inherit
the PARENT runner's env, so each runner's admission re-resolved the cap per
process (meta > env > .env > default) and nested fan-outs starved to ~1 slot
despite a 12-seat fleet.

Fix contract (wf.py): the first admission records its resolved cap in
<seats>/.cap (first writer wins, serialized by the pool's .lock flock); every
admission after it — from any process, nested children included — arbitrates
against the RECORDED value, never the inheriting process's env. Env/.env stay
the SEED for the first acquirer only; run.json max_seats is a per-run CEILING
under the pool cap; WORKFLOW_MAX_SEATS=0 stays a local disable that never
touches pool state.

Acceptance per row: the arbiter honors the pool-recorded cap AND a two-runner
test — two independent runner processes against ONE .seats dir, combined live
tickets <= the pool cap, while each process's own env (stale-small here) does
NOT cap it (the measured starvation shape).

Run: cd tests && python3 test_pool_seat_cap_mg5o2.py
"""
import importlib.util, json, os, shutil, subprocess, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "home-mg5o2"
shutil.rmtree(BUILD, ignore_errors=True)
(BUILD / "home").mkdir(parents=True)
(BUILD / "emptyhome").mkdir(parents=True)
os.environ["HERMES_HOME"] = str(BUILD / "home")
for k in ("WORKFLOW_MAX_SEATS", "HERMES_PROFILE", "WF_SEATS_DIR"):
    os.environ.pop(k, None)

_spec = importlib.util.spec_from_file_location("hw_mg5o2", ROOT / "wf.py")
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " ) + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# ---------- the child runner fixture (written at run time): drives the SAME
# argument shape the production spawn seam passes _seat_acquire (caller cap
# from _max_seats, seed from _seat_pool_seed, ceiling from _seat_pool_ceiling
# against an empty run meta) as an INDEPENDENT process.
CHILD = BUILD / "child_runner.py"
CHILD.write_text(r'''
import importlib.util, json, os, sys, threading, time
from pathlib import Path
wf_path, seats_s, name, mode, rep_s, n_s, hold_s, bounded_s = sys.argv[1:9]
gate = sys.argv[9] if len(sys.argv) > 9 and sys.argv[9] != "-" else ""
seats = Path(seats_s); rep = Path(rep_s)
spec = importlib.util.spec_from_file_location("hw_child", wf_path)
wf = importlib.util.module_from_spec(spec); spec.loader.exec_module(wf)
n = int(n_s); hold = float(hold_s); bounded = float(bounded_s)
def emit(row):
    with open(rep, "a") as f: f.write(json.dumps(row) + "\n")
if gate:
    g = Path(gate)
    while not g.exists(): time.sleep(0.01)

def acquire():
    return wf._seat_acquire(seats, name, wf._max_seats({}), bounded,
                            pool_seed=wf._seat_pool_seed(),
                            pool_ceiling=wf._seat_pool_ceiling({}))

if mode == "holdN":
    held = []
    try:
        for i in range(n):
            t = acquire()
            if t is None or t is wf._SEAT_UNSUPPORTED:
                emit({"evt": "stall", "k": len(held)}); break
            held.append(t)
            emit({"evt": "hold", "k": len(held)})
        time.sleep(hold)
    finally:
        for t in held: wf._seat_release(t)
    emit({"evt": "done", "k": len(held)})
elif mode == "eff":
    t = acquire()
    eff = wf._seat_pool_cap(seats)   # read-only: the pool's recorded truth
    emit({"evt": "eff", "eff": eff, "env": os.environ.get("WORKFLOW_MAX_SEATS", "")})
    if t is not None: time.sleep(1.0); wf._seat_release(t)
    emit({"evt": "done"})
elif mode == "hammer":
    stop = time.time() + hold        # reuse hold as the duration
    counts = {"acq": 0, "miss": 0}
    lock = threading.Lock()
    def worker():
        while time.time() < stop:
            t = acquire()
            if t is None or t is wf._SEAT_UNSUPPORTED:
                with lock: counts["miss"] += 1
                continue
            with lock: counts["acq"] += 1
            time.sleep(0.25)
            wf._seat_release(t)
    ts = [threading.Thread(target=worker) for _ in range(n)]
    [t.start() for t in ts]; [t.join() for t in ts]
    emit({"evt": "done", "acq": counts["acq"], "miss": counts["miss"]})
''')

def run_child(seats, name, mode, n, hold, bounded, rep, env_extra=None, gate=""):
    env = dict(os.environ)
    env["WF_RUNS_ROOT"] = str(BUILD / "runs")  # est-2ek.1.762: pin child runs root to this test's scratch — never inherit the lane root
    if env_extra is not None:
        env.update(env_extra)
    for k in ("WORKFLOW_MAX_SEATS",):
        if env_extra is not None and k not in env_extra:
            env.pop(k, None)
    return subprocess.Popen([sys.executable, str(CHILD), str(ROOT / "wf.py"),
                             str(seats), name, mode, str(rep), str(n), str(hold),
                             str(bounded), gate or "-"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env)

def read_rows(p):
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try: out.append(json.loads(line))
        except ValueError: pass
    return out

def peak_k(rows):
    ks = [r["k"] for r in rows if r.get("evt") in ("hold", "stall")]
    return max(ks) if ks else 0

def observer(seats, until, samples):
    def _o():
        while not until.is_set():
            samples.append(len(list(Path(seats).glob("*.json"))))
            time.sleep(0.015)
    t = threading.Thread(target=_o, daemon=True)
    t.start()
    return t

def seed_cap(seats, v):
    Path(seats).mkdir(parents=True, exist_ok=True)
    Path(seats, ".cap").write_text(str(v))

# ============ (1) unit: the recorder = first writer wins, ceiling under, =
#                corrupt re-seeds, read-only never writes.
d = BUILD / "unit-cap"; d.mkdir()
check("read-only on an unrecorded pool returns None and writes nothing",
      wf._seat_pool_cap(d) is None and not (d / ".cap").exists())
check("first seed records (12)", wf._seat_pool_cap(d, seed=12) == 12
      and (d / ".cap").read_text() == "12")
check("a later divergent seed does NOT overwrite (first writer wins)",
      wf._seat_pool_cap(d, seed=3) == 12 and (d / ".cap").read_text() == "12")
check("per-run ceiling rides UNDER the pool cap (2 < 12)", wf._seat_pool_cap(d, ceiling=2) == 2)
check("ceiling above the pool cap never raises it", wf._seat_pool_cap(d, ceiling=99) == 12)
(d / ".cap").write_text("banana")
check("corrupt .cap is re-seeded, never trusted, never fatal",
      wf._seat_pool_cap(d, seed=7) == 7 and (d / ".cap").read_text() == "7")

# ============ (2) unit: WORKFLOW_MAX_SEATS=0 stays a LOCAL disable, never
#                touches pool state; a fresh pool seeds from the caller.
d2 = BUILD / "unit-zero"; d2.mkdir()
got0 = wf._seat_acquire(d2, "Z", 0, 0.1, pool_seed=9)
check("cap<=0 returns the uncapped sentinel", isinstance(got0, Path) and got0.name == ".uncapped")
check("local disable never records a pool cap", not (d2 / ".cap").exists())
d5 = BUILD / "unit-seed"
g5 = wf._seat_acquire(d5, "S", 3, 1.0, pool_seed=3)
check("first admission into an empty pool records its seed", g5 is not None
      and (d5 / ".cap").exists() and (d5 / ".cap").read_text() == "3")
wf._seat_release(g5)

# ============ (3) unit: admission honors the POOL cap, not the caller cap;
#                run.json ceiling caps the run under the pool truth.
d3 = BUILD / "unit-admit"; seed_cap(d3, 4)
held = []
for i in range(5):
    t = wf._seat_acquire(d3, f"X{i}", 1, 0.3, pool_seed=99, pool_ceiling=None)  # caller cap 1!
    if t is None: break
    held.append(t)
check("stale caller cap=1 does NOT cap admission — pool .cap=4 admits 4, refuses the 5th",
      len(held) == 4 and len(list(d3.glob("*.json"))) == 4, f"held={len(held)}")
check("pool cap survived the divergent seed (99 ignored once recorded)",
      (d3 / ".cap").read_text() == "4")
for t in held: wf._seat_release(t)
d4 = BUILD / "unit-ceiling"; seed_cap(d4, 4)
held4 = []
for i in range(3):
    t = wf._seat_acquire(d4, f"C{i}", 9, 0.3, pool_seed=99, pool_ceiling=2)     # run wants 9
    if t is None: break
    held4.append(t)
check("per-run max_seats=2 admits 2 of the 4-seat pool and no more", len(held4) == 2,
      f"held={len(held4)}")
for t in held4: wf._seat_release(t)

# ============ (4) TWO-RUNNER acceptance: two independent processes, ONE
#                .seats dir, pool-recorded cap 4; A's env says 2, B's env says
#                1 (the inherited-stale-env starvation shape). Old code: A max
#                2, B max 1 (near one request at a time). New code: the pool
#                arbitrates — both hold up to the ceiling the pool allows and
#                the combined live count never crosses 4.
seats = BUILD / "seats-2r"; seed_cap(seats, 4)
repA, repB = BUILD / "2r-A.jsonl", BUILD / "2r-B.jsonl"
gate = str(BUILD / "gate1")
pA = run_child(seats, "A2R", "holdN", 3, 2.0, 10, repA,
               env_extra={"WORKFLOW_MAX_SEATS": "2"}, gate=gate)
pB = run_child(seats, "B2R", "holdN", 2, 1.5, 10, repB,
               env_extra={"WORKFLOW_MAX_SEATS": "1"}, gate=gate)
until = threading.Event(); samples = []
obs = observer(seats, until, samples)
time.sleep(0.05); Path(gate).write_text("go")
rcA, rcB = pA.wait(60), pB.wait(60)
until.set(); obs.join(5)
a_rows, b_rows = read_rows(repA), read_rows(repB)
a_peak, b_peak = peak_k(a_rows), peak_k(b_rows)
check("runner A (env=2) reached 3 live tickets — the inherited env no longer caps admission",
      a_peak >= 3, f"peak={a_peak} rows={a_rows}")
check("runner B (env=1, nested-stale shape) reached 2 live tickets",
      b_peak >= 2, f"peak={b_peak} rows={b_rows}")
check("TWO-RUNNER combined live tickets never crossed the pool cap of 4",
      max(samples) <= 4, f"observed max live={max(samples)}")
check("clean hand-back — no stray tickets after both runners exited",
      len(list(seats.glob("*.json"))) == 0)

# ============ (5) TWO-RUNNER COMBINED CAP under pressure: both processes
#                fan 4 hammer threads with env=8 (above the pool cap of 4).
#                Old code admitted 8+8 per-process; the pool holds combined
#                live <= 4 while BOTH runners still get work (not serialized
#                to one).
seats2 = BUILD / "seats-hammer"; seed_cap(seats2, 4)
repH1, repH2 = BUILD / "h1.jsonl", BUILD / "h2.jsonl"
gate2 = str(BUILD / "gate2")
h1 = run_child(seats2, "H1", "hammer", 4, 3.0, 5, repH1,
               env_extra={"WORKFLOW_MAX_SEATS": "8"}, gate=gate2)
h2 = run_child(seats2, "H2", "hammer", 4, 3.0, 5, repH2,
               env_extra={"WORKFLOW_MAX_SEATS": "8"}, gate=gate2)
until2 = threading.Event(); samples2 = []
obs2 = observer(seats2, until2, samples2)
time.sleep(0.05); Path(gate2).write_text("go")
rc1, rc2 = h1.wait(90), h2.wait(90)
until2.set(); obs2.join(5)
r1, r2 = read_rows(repH1), read_rows(repH2)
acq1 = sum(r.get("acq", 0) for r in r1); acq2 = sum(r.get("acq", 0) for r in r2)
check("combined live tickets across BOTH runners stayed <= the pool cap (4)",
      max(samples2) <= 4, f"observed max live={max(samples2)}")
check("pool pressure reached the cap (observed live hit >=3 at least once)",
      max(samples2) >= 3, f"observed max live={max(samples2)}")
check("both runners did real work through the shared pool (not serialized to one)",
      acq1 >= 2 and acq2 >= 2, f"acq1={acq1} acq2={acq2}")

# ============ (6) the nested-child shape: a runner with NO env at all (no
#                WORKFLOW_MAX_SEATS, empty HERMES_HOME => SEATS_DEFAULT 4)
#                arbitrates against the pool's recorded 2 — the recorded
#                truth beats BOTH the env and the default.
seats3 = BUILD / "seats-blank"; seed_cap(seats3, 2)
rep3 = BUILD / "blank.jsonl"
c3 = run_child(seats3, "BLANK", "holdN", 4, 0.2, 0.5, rep3,
               env_extra={"HERMES_HOME": str(BUILD / "emptyhome")})
rc3 = c3.wait(60)
rows3 = read_rows(rep3)
check("env-less runner (default would be 4) admitted exactly the pool's 2 and stalled on the 3rd",
      peak_k(rows3) == 2 and any(r.get("evt") == "stall" for r in rows3),
      f"rows={rows3}")

# ============ (7) first-writer race ACROSS processes: two runners (env 6 and
#                env 12) start against an UNRECORDED pool at one gate — the
#                flock serializes the record, so both see the SAME effective
#                cap and the file holds exactly one of the two seeds.
seats4 = BUILD / "seats-race"
repW1, repW2 = BUILD / "w1.jsonl", BUILD / "w2.jsonl"
gate3 = str(BUILD / "gate3")
w1 = run_child(seats4, "W1", "eff", 1, 0, 5, repW1, env_extra={"WORKFLOW_MAX_SEATS": "6"}, gate=gate3)
w2 = run_child(seats4, "W2", "eff", 1, 0, 5, repW2, env_extra={"WORKFLOW_MAX_SEATS": "12"}, gate=gate3)
time.sleep(0.05); Path(gate3).write_text("go")
w1.wait(60); w2.wait(60)
e1 = [r for r in read_rows(repW1) if r.get("evt") == "eff"]
e2 = [r for r in read_rows(repW2) if r.get("evt") == "eff"]
final = int((seats4 / ".cap").read_text()) if (seats4 / ".cap").exists() else None
check("first-writer race: both runners resolved the SAME pool-recorded cap",
      len(e1) == 1 and len(e2) == 1 and e1[0]["eff"] == e2[0]["eff"] == final,
      f"e1={e1} e2={e2} final={final}")
check("the recorded cap is one of the contending seeds", final in (6, 12), f"final={final}")

shutil.rmtree(BUILD, ignore_errors=True)
print(("" if ok else "FAILURES PRESENT ") + "DONE")
sys.exit(0 if ok else 1)
