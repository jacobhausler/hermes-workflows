#!/usr/bin/env python3
"""Continuous zombie hygiene for the subreaper pool (field receipt 2026-10-07:
8.8k adopted zombies — 7.6k of them `git` — load average 39 on 20 cores; every
healthy runner burned ~0.65 cores because the poll walks that grow with the
zombie pool run on a 0.25 s cadence).

The law this test locks:
  * VERDICT INTEGRITY: the reaper never waitpid()s a child the runner itself
    owns — a seat Popen in meta['_procs'] or an aux probe in _aux_pids.
    Stealing it makes subprocess report returncode 0: a FALSE GREEN.
      T1  a tracked seat that is ALREADY a zombie keeps its exit code (7).
      T2  #283 review B1(a): a seat registered AFTER the reaper's scan (the
          stale-snapshot recheck) keeps its exit code (7).
      T3  #283 review B1(b): an aux pid that is a zombie is never reaped.
      T4  #283 review B1(b).3: _aux_run spawn+registration is atomic — a
          reaper pass racing the Popen->register gap never steals its rc (3).
  * T5  #283 review B2: no subreaper (prctl refused) -> no reaper thread; it
        could only ever reap DIRECT children, i.e. only do harm.
  * T6  the reaper drains adopted zombies for real (a double-forked grandchild
        that exits is adopted while the subreaper is set; the pool empties),
        and the stop event ends the thread.
"""
import os, sys, threading, time, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import wf  # noqa: E402

fails = []


def _state(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def _wait_zombie(pid, budget=5.0):
    end = time.time() + budget
    while time.time() < end:
        if _state(pid) == "Z":
            return True
        time.sleep(0.02)
    return False


def _meta(subreaper=True):
    return {"_stop": threading.Event(), "_procs_lock": threading.Lock(),
            "_procs": {}, "_subreaper": subreaper}


def _reapers():
    return [t for t in threading.enumerate() if t.name == "zombie-reaper" and t.is_alive()]


def _run_reaper(meta, secs=2.5):
    wf._start_reaper(meta)
    time.sleep(secs)
    meta["_stop"].set()
    end = time.time() + 3
    while _reapers() and time.time() < end:
        time.sleep(0.05)


def t5_no_subreaper_no_reaper():
    before = len(_reapers())
    meta = _meta(subreaper=False)
    wf._start_reaper(meta)
    time.sleep(0.2)
    if len(_reapers()) != before:
        fails.append("T5/B2: reaper thread started although _subreaper is False")
    meta["_stop"].set()
    time.sleep(1.5)


def t1_tracked_zombie_keeps_rc():
    meta = _meta()
    p = subprocess.Popen(["sh", "-c", "exit 7"], start_new_session=True)
    with meta["_procs_lock"]:
        meta["_procs"]["seat:t1"] = p
    if not _wait_zombie(p.pid):
        fails.append("T1 fixture: tracked child never became a zombie")
    if p.pid in wf._adopted_zombie_pids(meta):
        fails.append("T1/C2: tracked zombie pid returned by _adopted_zombie_pids")
    _run_reaper(meta)
    rc = p.poll()
    if rc != 7:
        fails.append(f"T1: tracked seat zombie lost its exit status: rc={rc} (want 7)")


def t2_late_registration_keeps_rc():
    meta = _meta()
    p = subprocess.Popen(["sh", "-c", "exit 7"], start_new_session=True)
    if not _wait_zombie(p.pid):
        fails.append("T2 fixture: child never became a zombie")
    orig = wf._adopted_zombie_pids
    done = []

    def scan_then_register(*a, **kw):
        res = orig(*a, **kw)
        if not done and p.pid in res:
            # the seat is Popen'd+registered under _procs_lock AFTER the scan
            with meta["_procs_lock"]:
                meta["_procs"]["seat:t2"] = p
            done.append(1)
        return res

    wf._adopted_zombie_pids = scan_then_register
    try:
        _run_reaper(meta)
    finally:
        wf._adopted_zombie_pids = orig
    if not done:
        fails.append("T2 fixture: the scan never saw the unregistered zombie")
    rc = p.poll()
    if rc != 7:
        fails.append(f"T2/B1a: seat registered after the scan lost its exit status: rc={rc} (want 7)")


def t3_aux_zombie_not_reaped():
    meta = _meta()
    pid = os.fork()
    if pid == 0:
        os._exit(5)
    with wf._aux_lock:
        wf._aux_pids.add(pid)
    try:
        if not _wait_zombie(pid):
            fails.append("T3 fixture: aux child never became a zombie")
        if pid in wf._adopted_zombie_pids(meta):
            fails.append("T3/B1b: aux zombie pid returned by _adopted_zombie_pids")
        _run_reaper(meta)
        try:
            _, st = os.waitpid(pid, 0)
            if not os.WIFEXITED(st) or os.WEXITSTATUS(st) != 5:
                fails.append(f"T3/B1b: aux child status corrupted: {st}")
        except ChildProcessError:
            fails.append("T3/B1b: reaper stole the aux child's exit status (ECHILD)")
    finally:
        with wf._aux_lock:
            wf._aux_pids.discard(pid)


def t4_aux_spawn_registration_atomic():
    meta = _meta()
    real = subprocess.Popen
    raced = []

    def popen_then_race(*a, **kw):
        p = real(*a, **kw)
        _wait_zombie(p.pid, 3.0)
        # a reaper pass lands in the gap between Popen() returning and the
        # pid being registered in _aux_pids
        t = threading.Thread(target=lambda: raced.append(wf._reap_adopted_zombies(meta)),
                             daemon=True)
        t.start()
        t.join(1.0)
        return p

    wf.subprocess.Popen = popen_then_race
    try:
        r = wf._aux_run(["sh", "-c", "exit 3"], timeout=30)
    finally:
        wf.subprocess.Popen = real
    if r.returncode != 3:
        fails.append(f"T4/B1b.3: _aux_run rc stolen in the Popen->register gap: rc={r.returncode} (want 3)")
    end = time.time() + 3
    while not raced and time.time() < end:
        time.sleep(0.05)


def t6_drain_and_stop():
    if not wf._set_subreaper():
        print("SKIP T6: PR_SET_CHILD_SUBREAPER unavailable on this platform")
        return
    pid = os.fork()
    if pid == 0:
        try:
            g = os.fork()
            if g == 0:
                os._exit(0)               # grandchild: adopted by us, then dead
            os._exit(0)                   # intermediate dies too
        except Exception:
            os._exit(1)
    meta = _meta()
    time.sleep(1.0)
    if not wf._adopted_zombie_pids(meta):
        fails.append("T6 fixture: no adopted zombie observed after double-fork exit")
    wf._start_reaper(meta)
    if not _reapers():
        fails.append("T6: reaper thread not started")
    deadline = time.time() + 10
    while time.time() < deadline and wf._adopted_zombie_pids(meta):
        time.sleep(0.5)
    if wf._adopted_zombie_pids(meta):
        fails.append("T6: reaper did not drain the adopted zombie pool within 10s")
    meta["_stop"].set()
    time.sleep(1.5)
    if _reapers():
        fails.append("T6: reaper thread survived the stop event")


def main() -> int:
    if not Path("/proc/self/stat").exists():
        print("SKIP: no procfs on this platform")
        return 0
    for t in (t5_no_subreaper_no_reaper, t1_tracked_zombie_keeps_rc,
              t2_late_registration_keeps_rc, t3_aux_zombie_not_reaped,
              t4_aux_spawn_registration_atomic, t6_drain_and_stop):
        try:
            t()
        except Exception as e:  # a crash is a failure, never a skip
            fails.append(f"{t.__name__}: {type(e).__name__}: {e}")
    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print("zombie-reaper: owned seat/aux children keep their exit status (tracked, "
          "late-registered, aux, aux spawn gap); no reaper without subreaper; the "
          "daemon drains the adopted pool; stop event ends the thread")
    return 0


if __name__ == "__main__":
    sys.exit(main())
