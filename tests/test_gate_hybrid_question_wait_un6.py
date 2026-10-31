#!/usr/bin/env python3
"""hw-un6 — hybrid gate rejection: a gate carrying BOTH `question` (human) and
`wait` (machine) must be refused at submit, mirroring the sibling rule that
already rejects `default_option` on wait-gates. Validator-only: the engine is
the shared surface, so the door never accepts the hybrid shape.

Law: `question` and `wait` are mutually exclusive on a gate. `options` stays
legal on a wait-gate (answer DATA, spec pins only question+wait).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import wfcommon  # noqa: E402

V = wfcommon.validate_graph_errors

ok = 0
def check(cond, name):
    global ok
    print(("PASS" if cond else "FAIL"), "-", name)
    ok += 1 if cond else 0
    if not cond:
        raise SystemExit(1)


def fields(errs, nid):
    return sorted({e["field"] for e in errs if e["node"] == nid})


# --- the exact repro: hybrid human-question + machine-wait gate ----------------
hybrid = [{"id": "g", "type": "gate", "question": "ship it?", "wait": {"wait_s": 60}}]
errs = V(hybrid)
check(any(e["node"] == "g" and e["field"] == "question"
         and "wait-gates" in e["msg"] for e in errs),
      "issue repro: gate question+wait rejected at submit naming node+field")

# explicit hybrid with options still lands exactly one hybrid error on `question`
hybrid_opts = [{"id": "g", "type": "gate", "question": "q", "options": ["a", "b"],
                "wait": {"until_argv": ["/bin/true"], "every_s": 60}}]
check(fields(V(hybrid_opts), "g") == ["question"],
      "hybrid with options names only the question field")

# --- untouched neighbours -------------------------------------------------------
check(V([{"id": "g", "type": "gate", "question": "q"}]) == [],
      "human gate (question only) still accepted")
check(V([{"id": "g", "type": "gate", "wait": {"wait_s": 60}}]) == [],
      "machine gate (wait only) still accepted")
check(V([{"id": "g", "type": "gate", "options": ["a", "b"],
          "wait": {"wait_s": 60}}]) == [],
      "wait-gate with options (no question) stays legal")

# sibling rule unchanged (pinned wording, exact message)
sib = [{"id": "g", "type": "gate", "options": ["a", "b"], "default_option": "a",
        "wait": {"wait_s": 60}}]
check(V(sib) == [{"node": "g", "field": "default_option",
                  "msg": "default_option applies to human gates, not machine wait-gates"}],
      "sibling default_option+wait rule byte-unchanged")

# malformed wait on a hybrid: hybrid error lands, wait errors are independent
bad = [{"id": "g", "type": "gate", "question": "q", "wait": {}}]
check(fields(V(bad), "g") == ["question", "wait"],
      "hybrid error is independent of wait-shape errors")

print(f"ALL {ok} CHECKS PASS")
