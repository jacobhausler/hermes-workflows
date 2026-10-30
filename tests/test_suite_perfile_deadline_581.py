#!/usr/bin/env python3
"""est-jggzt (#592) — the suite's per-file wall is a hang backstop with a
measured floor, not a truncatable performance budget.

Failure mode pinned: the nightly serial qualification at release head 7faed79
recorded FOUR deterministic exit-124 rows (crash-resume, lane-supervisor,
concurrency_retry_knobs_24, suite_runs_root_762) while scoped serial rechecks
of the same files passed OUTSIDE the suite at 91.14 / 92.40 / 94.39 / 110.68 s.
The inline 90s cap sat below the estate-host floor; #581 had already raised the
hook-internal deadlines to 120s but not the enclosing suite cap, so the same
mismatch class survived one cure. The cap is now DEFAULT_PER_FILE_TIMEOUT_S=180
(1.6x the observed worst) and flag-overridable via --per-file-timeout.

Legs:
  (A) BEHAVIOURAL timeout — a fixture that sleeps past --per-file-timeout 1 is
      recorded exit 124 (the mechanism survives parameterization) and the suite
      exits 1.
  (B) DEFAULT admission + anti-truncation — the same fixture set passes under
      the default, and the startup banner's default is pinned >= 150 and > 120:
      measured floor 110.68s plus margin, and the 120s hook-internal deadline
      (#581) must stay the FIRST responder, never backstopped from above.
  (C) REFUSAL before side effects — a missing, non-integer, or <1 value exits 2
      and writes no ledger/admission in the out-dir.
  (D) FLAG x SHARD coexistence — --shard 0/2 --per-file-timeout 30 runs only
      the first sorted position and exits 0 (the new flag cannot reorder mode
      parsing).
  (E) RETIME tripwire — the machine-watch budgets widened in this same fix must
      be present at their new values and absent at the old ones.

usage: python3 tests/test_suite_perfile_deadline_581.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "scripts" / "suite.py"

failures = 0
def check(label, ok, detail: object = ""):
    global failures
    print(("PASS " if ok else "FAIL ") + label + ((" " + str(detail)) if not ok else ""))
    failures += not ok

FAST = "import sys; sys.exit(0)\n"
SLOW = "import sys, time\n\ntime.sleep(5)\nsys.exit(0)\n"


def suite_run(fix_root, out_dir, extra):
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, str(SUITE), str(fix_root), str(out_dir)] + extra,
                       capture_output=True, text=True, timeout=180,
                       env={k: v for k, v in os.environ.items() if k != "WF_RUNS_ROOT"})
    return p, time.monotonic() - t0


with tempfile.TemporaryDirectory(prefix="wf-pfd-") as t:
    T = Path(t)
    fix = T / "fixroot"
    (fix / "tests").mkdir(parents=True)
    (fix / "tests" / "test_a_fast.py").write_text(FAST)
    (fix / "tests" / "test_z_slow.py").write_text(SLOW)

    # (A) timeout mechanism survives parameterization: 1s cap, 5s sleeper.
    outA = T / "outA"
    p, _ = suite_run(fix, outA, ["--per-file-timeout", "1"])
    rowsA = {r["test"]: r["exit"] for r in json.loads((outA / "exits.json").read_text())}
    check("A: suite exits 1 with a red row", p.returncode == 1, p.returncode)
    check("A: slow case recorded 124", rowsA.get("test_z_slow.py") == 124, rowsA)
    check("A: fast case recorded 0", rowsA.get("test_a_fast.py") == 0, rowsA)

    # (B) default admits the fixture AND is pinned above the measured floor.
    outB = T / "outB"
    p, wall = suite_run(fix, outB, [])
    rowsB = {r["test"]: r["exit"] for r in json.loads((outB / "exits.json").read_text())}
    check("B: suite exits 0 under the default", p.returncode == 0, (p.returncode, p.stdout[-200:]))
    banner = [line for line in p.stdout.splitlines() if line.startswith("suite: per-file-timeout=")]
    check("B: banner names the effective per-file timeout", len(banner) == 1, banner)
    default_s = int(banner[0].split("=", 1)[1].rstrip("s")) if banner else 0
    check("B: default >= 150 (measured floor 110.68s + margin)", default_s >= 150, default_s)
    check("B: default > 120 so the #581 hook deadline stays first responder",
          default_s > 120, default_s)
    check("B: 5s sleeper admitted", wall > 4 and rowsB.get("test_z_slow.py") == 0, (wall, rowsB))

    # (C) refusal before any out-dir side effects.
    for bad in ([], ["x"], ["0"], ["-5"]):
        outC = T / ("outC" + (bad[0] if bad else "missing"))
        p, _ = suite_run(fix, outC, ["--per-file-timeout"] + bad)
        ledgered = (outC / "exits.json").exists() or (outC / "admission.json").exists()
        check(f"C: refusal exits 2 for {bad!r}", p.returncode == 2 and not ledgered,
              (p.returncode, ledgered))

    # (D) flag x shard coexistence: shard 0/2 of [fast, slow] is [fast] only.
    outD = T / "outD"
    p, _ = suite_run(fix, outD, ["--shard", "0/2", "--per-file-timeout", "30"])
    rowsD = json.loads((outD / "exits.json").read_text())
    check("D: shard+flag runs one position, green",
          p.returncode == 0 and [r["test"] for r in rowsD] == ["test_a_fast.py"],
          (p.returncode, rowsD))

    # (E) the machine-watch retime landed: the stale micro-budgets must be gone
    # and the widened ones present (string tripwire; the functional contract is
    # the test file itself, which CI re-runs anyway).
    mw_src = (ROOT / "tests" / "test_machine_watch_94.py").read_text(encoding="utf-8")
    missing = [n for n in ("every_s=1.0", "timeout_s=30", "wait(timeout=90",
                           "monotonic() + 75")
               if n not in mw_src]
    stale = [g for g in ("every_s=.15, timeout_s=1.5", "wait(timeout=12",
                         "wait(timeout=30)", "monotonic() + 6",
                         "monotonic() + 25") if g in mw_src]
    check("E: machine-watch retime landed", not missing and not stale,
          {"missing": missing, "stale": stale})

print(f"FAILURES PRESENT: {failures}" if failures else "ALL PASS")
raise SystemExit(1 if failures else 0)
