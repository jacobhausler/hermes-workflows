#!/usr/bin/env python3
"""est-t7yod (the #583 peer-review residual): the machine-readable spent-cap
refusal stamp must ride the READ MODEL, not only the committed record.

#583 (est-mqp1f) stamped `refusal: lifetime_cap_spent` on the `_window_spent_
record` output (wf.py `_window_spent_record`) so every later seam reads the
class of verdict without grepping the message — but the stamp stopped at the
record: `wfcommon.FACT_KEYS` (the ONE node-truth read's closed key set, shared
by the dashboard `_view` and the door's A2 facts) did not carry `refusal`, and
the door's node_facts passthrough whitelist did not either. Result: a spent-cap
boot surfaced its error_class and the 'spawn refused' prose on `workflow
status` but not the stamp itself.

Fix law (both surfaces, unknown-law preserved):
  1. `refusal` joins FACT_KEYS — present records ride verbatim, absent records
     read `unknown`, never fabricated (AGENTS.md rule 8, same treatment
     `error_class` gets).
  2. The door's failed/partial node_facts whitelist passes `refusal` through
     like the other final-record facts, so the desktop/tool door shows
     refusal=lifetime_cap_spent on a spent-cap boot.

S1: refusal is a FACT_KEYS row (existing rows preserved — pinned in S4).
S2: wfcommon.node_facts surfaces refusal verbatim on a refusal-stamped record.
S3: the door's act_status node_facts shows refusal=lifetime_cap_spent for the
    failed node (the acceptance: 'node_facts shows refusal=lifetime_cap_spent
    on a spent-cap boot').
S4: unknown law + no-regression — a done record without a refusal reads
    refusal='unknown' (never fabricated), every pre-existing FACT_KEYS row is
    still there, and the door's other passthrough facts (error_class, attempts,
    attempts_log, final) ride unchanged beside refusal on the stamped node.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

checks = 0
failures = 0


def check(label, cond, detail=""):
    global checks, failures
    checks += 1
    if cond:
        print(f"PASS {label}")
    else:
        failures += 1
        print(f"FAIL {label}: {detail}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


import importlib.util  # noqa: E402  (load() above needs it at call time)

with tempfile.TemporaryDirectory(prefix="refusalt7yod-", dir=HERE,
                                 ignore_cleanup_errors=True) as td:
    home = Path(td) / "home"
    runs = home / "workflows"
    runs.mkdir(parents=True)
    os.environ["HERMES_HOME"] = str(home)
    os.environ["WF_RUNS_ROOT"] = str(runs)  # #71 env pin
    wfcommon = load("t7_wfcommon", ROOT / "wfcommon.py")
    door = load("t7_door", ROOT / "__init__.py")
    import wf_test_isolation as _iso71_t7
    _iso71_t7.install(door)  # #71: pin settings.runs_root too

    NODES = [{"id": "a", "type": "agent", "goal": "x"},
             {"id": "b", "type": "agent", "goal": "y", "after": ["a"]}]
    byid = {n["id"]: n for n in NODES}

    def scene(run_id, records):
        r = runs / run_id
        (r / "nodes").mkdir(parents=True)
        (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": NODES}))
        (r / "run.json").write_text("{}")
        for nid, rec in records.items():
            rec = dict(rec)
            rec.setdefault("efp", wfcommon.efp(byid, byid[nid]))
            (r / "nodes" / f"{nid}.json").write_text(json.dumps(rec))
        return r

    # The record verbatim as wf.py's _window_spent_record commits it (est-mqp1f):
    # a refused spawn, lifetime grant ledger of 2 persisted attempts, cap 3.
    REFUSAL_REC = {
        "status": "failed",
        "error": ("transient-retry lifetime bound spent before this boot: "
                  "2 persisted re-spawn grant(s) against the node transient "
                  "cap (3) — spawn refused"),
        "error_class": "transport_exhausted",
        "ms": 0,
        "attempts": 3,
        "spawn": 2,
        "refusal": "lifetime_cap_spent",
        "attempts_log": [
            {"attempt": 0, "error_class": "transport"},
            {"attempt": 1, "error_class": "transport"},
            {"attempt": 2, "error_class": "transport_exhausted"},
        ],
        "final": "",
    }

    r = scene("t7-refusal", {"a": {"status": "done", "output": {"result": "ok"}},
                             "b": REFUSAL_REC})

    # ---- S1: refusal is a row of the ONE node-truth read's closed key set ----
    check("S1: 'refusal' is in wfcommon.FACT_KEYS",
          "refusal" in wfcommon.FACT_KEYS,
          json.dumps(list(wfcommon.FACT_KEYS)))

    # ---- S2: node_facts surfaces the stamp verbatim ----
    nf = wfcommon.node_facts(r, "b") or {}
    check("S2: node_facts(b).refusal == 'lifetime_cap_spent' (verbatim from record)",
          nf.get("refusal") == "lifetime_cap_spent",
          json.dumps(nf.get("refusal")))

    # ---- S3: the door's status output shows it on the failed node ----
    out = door.act_status({"run_id": "t7-refusal"})
    nf3 = (out.get("nodes") or {}).get("b", {}).get("node_facts") or {}
    check("S3: door act_status node_facts(b).refusal == 'lifetime_cap_spent'",
          nf3.get("refusal") == "lifetime_cap_spent",
          json.dumps(nf3))

    # ---- S4: unknown law, FACT_KEYS rows preserved, door facts unchanged ----
    for k in ("status", "error_class", "error", "attempts", "attempts_log",
              "final", "harvest", "output", "ms", "started", "log_path",
              "prompt_path", "efp", "skey"):
        check(f"S4: pre-existing FACT_KEYS row preserved: {k}",
              k in wfcommon.FACT_KEYS, str(wfcommon.FACT_KEYS))
    nfa = wfcommon.node_facts(r, "a") or {}
    check("S4: a done record WITHOUT a refusal reads 'unknown', never fabricated",
          nfa.get("refusal") == "unknown",
          json.dumps(nfa.get("refusal")))
    check("S4: door passthrough facts ride unchanged beside refusal on the stamped node",
          nf3.get("error_class") == "transport_exhausted"
          and nf3.get("attempts") == 3
          and nf3.get("attempts_log") == REFUSAL_REC["attempts_log"],
          json.dumps(nf3))

    print(f"\n{checks - failures}/{checks} checks passed")
    sys.exit(1 if failures else 0)
