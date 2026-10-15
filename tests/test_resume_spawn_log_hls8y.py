#!/usr/bin/env python3
"""est-hls8y — a resumed runner must never reuse a spawn number that already
owns a log, so a timed-out attempt's logs/<node>.a<N>.log survives verbatim.

Root cause (wf.py @ main): meta["_spawn_n"] is reset to {} at every runner
start (per process), and _next_spawn_no() returned 0 again on resume. The
resumed spawn then opened logs/<node>.a0.log with "w", truncating attempt 0's
stdout capture.

  R1  fresh run, no logs: first spawn number is 0 (healthy-run byte identity).
  R2  resume: prior logs fix.a0.log + fix.a1.log exist -> next spawn is a2, and
      the prior log bytes are untouched by allocation.
  R3  index-scoped: fan-out item 1 logs do not shift node "fix" (index None), and
      the item-1 counter continues from its own highest a<N>.
  R4  monotone within one process.
  R5  no _run in meta (unit contexts) -> legacy 0.

Run: python3 tests/test_resume_spawn_log_hls8y.py
"""
import os, sys, tempfile, threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok, checks = True, []
def check(label, cond, detail=""):
    global ok
    ok = ok and bool(cond)
    checks.append((label, bool(cond), detail))

def fresh_meta(run):
    return {"_spawn_n": {}, "_procs_lock": threading.Lock(), "_run": run}

def make_log(run, node, index, n, body):
    lp = wf.spawn_log_path(run, node, index, n)
    lp.write_text(body, encoding="utf-8")
    return lp

with tempfile.TemporaryDirectory() as td:
    node = {"id": "fix"}

    run1 = Path(td) / "run1"; run1.mkdir()
    check("R1 fresh run first spawn is 0",
          wf._next_spawn_no(fresh_meta(run1), node, None) == 0)

    run2 = Path(td) / "run2"; run2.mkdir()
    a0 = make_log(run2, node, None, 0, "ATTEMPT-0 stdout\n" * 40)
    a1 = make_log(run2, node, None, 1, "ATTEMPT-1 stdout\n" * 10)
    before = (a0.read_bytes(), a1.read_bytes())
    n = wf._next_spawn_no(fresh_meta(run2), node, None)
    check("R2 resume allocates a2 (not a0)", n == 2, f"got {n}")
    check("R2 prior a0 log bytes intact", a0.read_bytes() == before[0])
    check("R2 prior a1 log bytes intact", a1.read_bytes() == before[1])

    make_log(run2, node, 1, 5, "item-1 attempt 5\n")
    m3 = fresh_meta(run2)
    check("R3 node-level counter ignores item-1 logs",
          wf._next_spawn_no(m3, node, None) == 2)
    check("R3 item-1 counter continues after its own a5",
          wf._next_spawn_no(m3, node, 1) == 6)

    m4 = fresh_meta(run2)
    seq = [wf._next_spawn_no(m4, node, None) for _ in range(3)]
    check("R4 sequence 2,3,4 within a process", seq == [2, 3, 4], f"got {seq}")

    check("R5 no _run -> 0",
          wf._next_spawn_no({"_spawn_n": {}, "_procs_lock": threading.Lock()}, node, None) == 0)

for label, passed, detail in checks:
    print(("PASS " if passed else "FAIL ") + label + (f"  [{detail}]" if detail and not passed else ""))
print("ALL PASS" if ok else "FAILED")
sys.exit(0 if ok else 1)
