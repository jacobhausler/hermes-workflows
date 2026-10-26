#!/usr/bin/env python3
"""hw-bgb: grammar.md must name the fan-out/seat-cap trap AND state the ceiling
law with the engine's direction.

Measured defect (hw-bead-upstream wave1): fan-out width 8 against the resolved
seat cap 4, first-wave lanes overran their walls, and the four queued items
expired typed seat_wait (read model: queue_timeout) without ever spawning.

Review round (daa0aba, verdict=changes) proved the first remedy sentence pinned
the law BACKWARDS: the graph `max_seats` key is a per-run CEILING — wf.py
_seat_pool_cap admits it only as `0 < ceiling < cap_v` (lowers never raises; a
value above the pool truth is inert) and _seat_pool_seed deliberately excludes
the per-run value. The knob that raises is the host one: WORKFLOW_MAX_SEATS env
> .env > config workflows.max_seats. This test therefore bites on DIRECTION,
not words, and ships its own mutation probe (the backwards sentence) so the
claim law itself is proven to bite. Range bounds ride the live engine
attributes, not source-text regex (R6; precedent test_error_class_doc_sync.py).

Run: python3 tests/test_grammar_hw-bgb.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from wfcommon import SEAT_CAP_CEILING, SEAT_CAP_FLOOR  # live engine truth

grammar = (root / "references" / "grammar.md").read_text(encoding="utf-8")

ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and cond


# Slice the concurrency section (heading to next heading) — the section the
# fan-out author actually reads.
m = re.search(r"^## Per-run concurrency.*?(?=^## )", grammar, re.M | re.S)
check("concurrency section exists", m is not None)
section = m.group(0) if m else ""

check("names graph key max_seats", "max_seats" in section)
check("names the typed death seat_wait", "seat_wait" in section)
check("names the read-model symptom queue_timeout", "queue_timeout" in section)
check("states the bake law (baked at submit)",
      "submit" in section.lower() and "baked" in section.lower())
check(f"doc range matches engine [{SEAT_CAP_FLOOR},{SEAT_CAP_CEILING}]",
      re.search(rf"\[\s*{SEAT_CAP_FLOOR}\s*,\s*{SEAT_CAP_CEILING}\s*\]", section) is not None)

# Direction law: names the host knob that actually raises, states the ceiling
# semantics, and no sentence inside the section presents max_seats as a raise.
check("names the host knob that raises", "WORKFLOW_MAX_SEATS" in section,
      "env/.env/config must be named as the raise source")
check("states ceiling direction",
      re.search(r"CEILING|rides under|only lower", section) is not None,
      "section must state the per-run key is a ceiling under the pool truth")
RAISE_CLAIM = re.compile(
    r"rais\w+[^.]{0,200}?(?<!workflows\.)(?<!WORKFLOW_)(?<!_)max_seats(?![^.]{"
    r"0,40}inert)", re.I)
bad = [s for s in re.split(r"(?<=\.)\s", section) if RAISE_CLAIM.search(s)]
check("no sentence presents max_seats as a raise", not bad, (bad[0][:200] if bad else ""))

# Mutation probe (replaces the old tautological bite-check): the direction regex
# must reject the backwards sentence as authored at daa0aba.
MUTATION = ("So size a wave to the resolved seat cap, or raise it for the run with "
            "the top-level graph key `max_seats`: an integer in [4,16].")
check("direction law bites (mutation probe)", bool(RAISE_CLAIM.search(MUTATION)))

print("ALL PASS: grammar states the seat-cap trap with the engine's direction" if ok else "FAILURES")
sys.exit(0 if ok else 1)
