#!/usr/bin/env python3
"""est-zmpx8: the ONE capture the desktop render test feeds the panel.

Prints, as JSON, the READ-MODEL facts (wfcommon.node_facts — the same call the
dashboard `_view` merges onto nodes[id], which is what NodePanel reads) for a
two-node run whose second node carries the spent-cap refusal record verbatim as
wf.py `_window_spent_record` commits it (est-9qhpf / est-mqp1f / est-t7yod).

The record is written here, not imported from the runner, so the capture stays a
pure read-model fixture with no runner state; the shape is the one
tests/test_refusal_facts_t7yod.py asserts the stamp rides on.

Usage: python3 refusal_capture.py <repo_root>   -> {"a": {...}, "b": {...}}
"""
import json
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
import wfcommon  # noqa: E402

# wf.py `_window_spent_record` output, verbatim (seed 2 persisted grants vs cap 3).
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
DONE_REC = {"status": "done", "output": {"result": "ok"}, "ms": 10}

NODES = [{"id": "a", "type": "agent", "goal": "x"},
         {"id": "b", "type": "agent", "goal": "y", "after": ["a"]}]

with tempfile.TemporaryDirectory(prefix="zmpx8-capture-") as td:
    r = Path(td) / "zmpx8-refusal"
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": "zmpx8-refusal", "nodes": NODES}))
    (r / "run.json").write_text("{}")
    (r / "nodes" / "a.json").write_text(json.dumps(DONE_REC))
    (r / "nodes" / "b.json").write_text(json.dumps(REFUSAL_REC))
    out = {nid: (wfcommon.node_facts(r, nid) or {}) for nid in ("a", "b")}

print(json.dumps(out))
