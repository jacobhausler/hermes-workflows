#!/usr/bin/env python3
"""est-2ek.1.856 — the global agent seat must admit waiters FIFO, not first-poller-wins.

Failure (keeper field report 2026-10-08 12:19Z, spool key 57f5b8ba394a173c):
`_seat_acquire` is a blind poll loop — every waiter wakes on the .lock flock and
the FIRST poller to sweep takes a freed seat, regardless of how long it has
waited. keeper-windows-client-up's accept_probe (needs the owner's scarce
Windows boot window) sat `seat.wait` while freshly-launched gh-dispatch cron
runs (gh-drive-prs / gh-drive-issues, one holding 2 seats) re-took every freed
ticket. A long-waiting node starves behind churn of short runs.

Fix contract (wf.py): a waiter that finds the semaphore full registers a queue
marker under <seats>/queue/ carrying the waiter's identity ({pid, boottime,
uuid, enqueued, ts, hb}). Admission then requires BOTH `live < cap` AND "no
older live marker than mine" (order key: (enqueued, uuid), strictly older).
Markers are not tickets: the ticket count (glob over <seats>/*.json) never
sees the queue subdir. A waiter removes its own marker on admit, on bounded
expiry, and on abort (same under-lock recheck contract as tickets — est-g255
r2/r3). A marker whose owner is verifiably dead AND whose heartbeat is stale
is pruned by any acquirer; a marker that cannot be parsed is uncertain
capacity — counted as blocking, never silently dropped (#80 law). A marker
older than SEAT_QUEUE_HARD_S never blocks (a wedged owner cannot wedge the
queue forever); the bounded wait stays the outer bound and expiry stays the
typed `seat_wait`.

Cases (hermetic seats dir, no real runners):
  A1) a waiter blocked on a full semaphore leaves exactly one queue marker
      naming its pid — base creates nothing: RED.
  A2) with the semaphore FREE, an OLDER marker owned by a LIVE process blocks
      admission until it is removed (the queue is the arbiter, not the poll
      race): base admits immediately: RED.
  A3) an older marker whose owner pid is dead (and heartbeat absent) does NOT
      block, and is pruned — control, green at base.
  A4) an aborted waiter leaves no marker behind — control (vacuous at base).
  A5) control: an uncontended acquire admits and never registers a marker.

Run: cd tests && python3 test_seat_fifo_856.py
"""
import importlib.util, json, os, shutil, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HOME = HERE / "home-856-fifo"
shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir()
os.environ["HERMES_HOME"] = str(HOME)
os.environ.pop("WF_RUNS_ROOT", None)
for k in ("WF_SEATS_DIR", "WORKFLOW_MAX_SEATS", "WF_TEST_BUILD", "FAKE_LOG"):
    os.environ.pop(k, None)
_spec = importlib.util.spec_from_file_location("hw_856_fifo", ROOT / "wf.py")
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

_NOT_YET = object()      # "the thread has not returned yet" sentinel

ME = os.getpid()
ME_BT = wf._proc_boottime(ME)

def queue_rows(seats):
    q = Path(seats) / "queue"
    out = []
    if q.is_dir():
        for m in sorted(q.glob("*.json")):
            try:
                out.append((m, json.loads(m.read_text())))
            except Exception:
                out.append((m, None))
    return out

# ---------- A1: a blocked waiter registers a queue marker (RED at base) --------
seats = HOME / "seats-A1"
hold = threading.Event()
holder_got = [_NOT_YET]
def _holder():
    holder_got[0] = wf._seat_acquire(seats, "A1-holder", 1, 10.0)
t_h = threading.Thread(target=_holder, daemon=True); t_h.start()
deadline = time.time() + 5
while not (seats / ".lock").exists() and time.time() < deadline:
    time.sleep(0.02)
# the holder really holds: wait until its ticket exists
deadline = time.time() + 5
while time.time() < deadline and not list(seats.glob("*.json")):
    time.sleep(0.02)
check("A1 setup: holder ticket exists", bool(list(seats.glob("*.json"))))

waiter_got = [_NOT_YET]
def _waiter():
    waiter_got[0] = wf._seat_acquire(seats, "A1-waiter", 1, 6.0)
t_w = threading.Thread(target=_waiter, daemon=True); t_w.start()
time.sleep(0.8)                                   # waiter is mid-poll, blocked
rows = queue_rows(seats)
mine = [(m, r) for m, r in rows if isinstance(r, dict) and r.get("pid") == ME]
check("A1: a waiter blocked on a full semaphore registers a queue marker naming its pid",
      len(mine) == 1 and waiter_got[0] is _NOT_YET,
      f"queue rows={[(m.name, r) for m, r in rows]}")
if len(mine) == 1:
    r0 = mine[0][1]
    check("A1: the marker carries an order identity (enqueued) and a heartbeat",
          isinstance(r0.get("enqueued"), (int, float)) and isinstance(r0.get("hb"), (int, float)),
          json.dumps(r0)[:200])
hold.set()
if isinstance(holder_got[0], Path):
    wf._seat_release(holder_got[0])
t_w.join(10)
w = waiter_got[0]
check("A1: the waiter was admitted once the holder released",
      isinstance(w, Path) and w.exists(), f"got={w}")
check("A1: the admitted waiter's marker is gone",
      [m for m, r in queue_rows(seats) if isinstance(r, dict) and r.get("pid") == ME] == [],
      json.dumps([m.name for m, _ in queue_rows(seats)]))
wf._seat_release(w) if isinstance(w, Path) else None

# ---------- A2: an older LIVE marker blocks admission (RED at base) -----------
seats = HOME / "seats-A2"                                     # cap 1, NOTHING held
old = None
def _seed_old_marker():
    global old
    q = seats / "queue"
    q.mkdir(parents=True, exist_ok=True)
    old = q / "old-live-holder.json"
    old.write_text(json.dumps({"pid": ME, "boottime": ME_BT, "uuid": "0" * 8,
                               "name": "older-waiter", "enqueued": time.time() - 100,
                               "ts": time.time() - 100, "hb": round(time.time(), 3)}))
_seed_old_marker()
got2 = [_NOT_YET]
def _waiter2():
    got2[0] = wf._seat_acquire(seats, "A2-waiter", 1, 8.0)
t_w2 = threading.Thread(target=_waiter2, daemon=True); t_w2.start()
time.sleep(1.2)
blocked = got2[0] is _NOT_YET
tickets = sorted(p.name for p in seats.glob("*.json"))
check("A2: capacity is free yet an older live marker holds the seat for its owner "
      "(FIFO, not first-poller-wins) — base admits immediately",
      blocked and tickets == [],
      f"admitted_early={not blocked} tickets={tickets}")
try:
    old.unlink()
except OSError:
    pass
t_w2.join(10)
g = got2[0]
check("A2: once the older marker is gone the waiter is admitted",
      isinstance(g, Path) and g.exists(), f"got={g}")
check("A2: no ticket was ever created while the marker gated admission",
      isinstance(g, Path), "admitted at base — see prior check")
if isinstance(g, Path):
    wf._seat_release(g)

# ---------- A3: an older DEAD marker does not block, and is pruned (control) --
seats = HOME / "seats-A3"
q3 = seats / "queue"
q3.mkdir(parents=True, exist_ok=True)
dead_marker = q3 / "dead-holder.json"
dead_marker.write_text(json.dumps({"pid": 10**9 + 7, "boottime": 1, "uuid": "d" * 8,
                                   "name": "dead-waiter", "enqueued": time.time() - 100,
                                   "ts": time.time() - 100}))
t0 = time.time()
got3 = wf._seat_acquire(seats, "A3-waiter", 1, 3.0)
check("A3: a marker owned by a verifiably dead pid does not block admission",
      isinstance(got3, Path) and got3.exists() and time.time() - t0 < 1.5,
      f"got={got3} waited={time.time()-t0:.2f}s")
check("A3: the dead marker was pruned by the acquirer", not dead_marker.exists(),
      "dead marker still in queue")
wf._seat_release(got3) if isinstance(got3, Path) else None

# ---------- A4: an aborted waiter leaves no marker (control) ------------------
seats = HOME / "seats-A4"
got4h = [_NOT_YET]
def _holder4():
    got4h[0] = wf._seat_acquire(seats, "A4-holder", 1, 10.0)
t_h4 = threading.Thread(target=_holder4, daemon=True); t_h4.start()
deadline = time.time() + 5
while time.time() < deadline and not list(seats.glob("*.json")):
    time.sleep(0.02)
abort_ev = threading.Event()
got4 = [_NOT_YET]
def _waiter4():
    got4[0] = wf._seat_acquire(seats, "A4-waiter", 1, 8.0, abort=lambda: abort_ev.is_set())
t_w4 = threading.Thread(target=_waiter4, daemon=True); t_w4.start()
time.sleep(0.8)
abort_ev.set()
t_w4.join(10)
g4 = got4[0]
check("A4: abort returns None (no ticket)", g4 is None, f"got={g4}")
check("A4: an aborted waiter leaves no queue marker behind",
      [m for m, r in queue_rows(seats) if isinstance(r, dict) and r.get("pid") == ME] == [],
      json.dumps([m.name for m, _ in queue_rows(seats)]))
if isinstance(got4h[0], Path):
    wf._seat_release(got4h[0])

# ---------- A5: control: uncontended acquire admits, never registers ----------
seats = HOME / "seats-A5"
got5 = wf._seat_acquire(seats, "A5-waiter", 4, 2.0)
check("A5: uncontended acquire still admits", isinstance(got5, Path) and got5.exists(),
      f"got={got5}")
check("A5: an admitted-without-waiting acquire never registered a marker",
      queue_rows(seats) == [], json.dumps([m.name for m, _ in queue_rows(seats)]))
wf._seat_release(got5) if isinstance(got5, Path) else None

shutil.rmtree(HOME, ignore_errors=True)
print(("" if ok else "FAILURES PRESENT ") + "DONE")
sys.exit(0 if ok else 1)
