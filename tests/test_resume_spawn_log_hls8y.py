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
import json, os, sys, tempfile, threading
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

    # R6 fake-timeout corpus survival: _bank_the_corpse is EXACTLY what the wall
    # timeout calls (both wait paths). Bank attempt 0, mutate the work dir as
    # attempt 1 would, bank attempt 1: attempt 0's banked corpus must survive
    # verbatim (bytes > 0, byte-identical) at its own per-attempt slot, and the
    # canonical pointer must carry the latest.
    run6 = Path(td) / "run6"
    wd6 = wf.child_work_dir(run6, node, None)          # creates run6/work/fix
    (wd6 / "notes.md").write_text("ATTEMPT-0 WORK\n" * 10, encoding="utf-8")
    p0 = wf._bank_the_corpse(run6, node, None, 0, "ATTEMPT-0 tail\n" * 50)
    slot0 = Path(str(p0) + ".a0") if p0 else None
    a0_manifest = slot0.joinpath("manifest.json") if slot0 else Path(td) / "absent.json"
    a0_notes = slot0.joinpath("work/notes.md") if slot0 else Path(td) / "absent.md"
    m0_bytes = a0_manifest.read_bytes() if a0_manifest.exists() else b""
    n0_bytes = a0_notes.read_bytes() if a0_notes.exists() else b""
    check("R6 attempt-0 bank returns a corpus pointer", bool(p0))
    check("R6 attempt-0 per-attempt slot exists", slot0 is not None and slot0.is_dir())
    check("R6 attempt-0 corpus bytes > 0", len(n0_bytes) > 0, "banked work empty")
    # attempt 1: child edits its work dir, then the wall fires again
    (wd6 / "notes.md").write_text("ATTEMPT-1 REWRITE\n" * 4, encoding="utf-8")
    (wd6 / "found.md").write_text("ATTEMPT-1 FINDING\n", encoding="utf-8")
    p1 = wf._bank_the_corpse(run6, node, None, 1, "ATTEMPT-1 tail\n" * 50)
    check("R6 prior attempt-0 slot survives verbatim after attempt-1 bank",
          a0_notes.exists() and a0_notes.read_bytes() == n0_bytes
          and a0_manifest.read_bytes() == m0_bytes)
    slot1 = Path(str(p1) + ".a1") if p1 else None
    check("R6 attempt-1 slot carries the new work",
          slot1 is not None and (slot1 / "work/found.md").is_file())
    check("R6 canonical corpus stays latest (spawn=1 in manifest)",
          bool(p1) and json.loads((Path(p1) / "manifest.json").read_text()).get("spawn") == 1)

    # R7 log reopen at the real call site: run_child opens its spawn log through
    # wf._open_spawn_log — the one place mode is decided. A prior attempt's log
    # bytes must survive verbatim as a prefix (append, never truncate).
    run7 = Path(td) / "run7"; (run7 / "logs").mkdir(parents=True)
    lp7 = wf.spawn_log_path(run7, node, None, 3)
    lp7.write_bytes(b"PRIOR ATTEMPT LOG\n" * 8)
    before7 = lp7.read_bytes()
    helper = getattr(wf, "_open_spawn_log", None)
    check("R7 wf._open_spawn_log exists (single call-site opener)", callable(helper))
    if callable(helper):
        _f = helper(lp7)
        _f.write("RESUMED SPAWN BANNER\n")
        _f.close()
        after7 = lp7.read_bytes()
        check("R7 prior log intact + banner appended",
              after7.startswith(before7) and b"RESUMED SPAWN BANNER" in after7)
    src = (BUILD / "wf.py").read_text(encoding="utf-8")
    check("R7 no truncate-mode open of a spawn log remains in wf.py",
          'open(lp, "w"' not in src and src.count("_open_spawn_log(") >= 2)

for label, passed, detail in checks:
    print(("PASS " if passed else "FAIL ") + label + (f"  [{detail}]" if detail and not passed else ""))
print("ALL PASS" if ok else "FAILED")
sys.exit(0 if ok else 1)
