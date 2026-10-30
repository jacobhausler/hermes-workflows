#!/usr/bin/env python3
"""Suite per-file cap headroom (est-jggzt): the suite's per-file timeout is a
hang guard, not a speed budget, and must exceed the deadlines it wraps.

Background: #581 raised the two 11-integration hook walls to 120 s while the
enclosing scripts/suite.py per-file cap stayed 90 s, so crash-resume,
lane-supervisor (and, by measured wall, concurrency_retry_knobs_24 and
suite_runs_root_762) died exit 124 in the v1.4.5 full-serial qualification
despite passing standalone. This test pins the split-brain shut: the cap is a
named constant, the run loop uses it, and it carries headroom over (a) the max
subprocess wall the wrapped hook tests enforce and (b) the worst measured
standalone wall (110.68 s) at #581's own ~32 % margin.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


suite_src = (ROOT / "scripts" / "suite.py").read_text()
m = re.search(r"^PER_FILE_TIMEOUT_S\s*=\s*(\d+)", suite_src, re.M)
check("suite.py declares PER_FILE_TIMEOUT_S", m is not None)
cap = int(m.group(1)) if m else 0
check("run loop enforces the constant (no bare timeout=90 left)",
      "timeout=90" not in suite_src and "timeout=PER_FILE_TIMEOUT_S" in suite_src)

WRAPPED = ["tests/test_11_integration_crash_resume.py",
           "tests/test_11_integration_lane_supervisor.py"]
inner_walls = []
for rel in WRAPPED:
    txt = (ROOT / rel).read_text()
    inner_walls += [int(x) for x in re.findall(r"timeout\s*=\s*(\d+)", txt)]
check("wrapped hook tests still declare their walls", bool(inner_walls),
      "found none")
max_inner = max(inner_walls) if inner_walls else 0
check(f"cap {cap}s >= max wrapped wall {max_inner}s + 30s slack",
      cap >= max_inner + 30)

MEASURED_MAX_S = 110.68  # suite_runs_root_762, v1.4.5 serial qualification
check(f"cap {cap}s >= measured worst wall {MEASURED_MAX_S}s x 1.35 (#581 formula)",
      cap >= MEASURED_MAX_S * 1.35)

print(("FAIL " if FAILS else "PASS ") +
      f"suite cap headroom: cap={cap} wrapped={max_inner} measured={MEASURED_MAX_S}")
sys.exit(1 if FAILS else 0)
