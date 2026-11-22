#!/usr/bin/env python3
"""est-vy6j8 — pin the wf.side_effect_rows reader contract (sweep-c test gain).

Unpinned semantics the reconcile fail-open rests on: a torn line (writer died
mid-append) is never a committed fact; a journal that cannot be READ degrades
to [] (admission is never blocked by a missing inventory); rows are filtered
to dicts carrying a `node` key; surviving rows keep file order.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf


def rows_for(content: str) -> list:
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "side_effects.jsonl").write_text(content)
        return wf.side_effect_rows(Path(td))


def check(value, label):
    assert value, label
    print("PASS", label)


g1 = json.dumps({"node": "build", "event": "commit"})
g2 = json.dumps({"node": "publish", "event": "tag"})

check([r["node"] for r in rows_for(g1 + "\n\n" + g2 + "\n")] == ["build", "publish"],
      "well-formed rows kept in file order; blank lines skipped")

check([r["node"] for r in rows_for(g1 + '\n{"node": "par' + "\n" + g2 + "\n")] == ["build", "publish"],
      "torn line never a fact, neighbours survive")

check([r["node"] for r in rows_for('[1, 2]\n{"event": "no-node"}\n7\n' + g1 + "\n")] == ["build"],
      "non-dict rows and node-less dicts filtered")

with tempfile.TemporaryDirectory() as td:
    check(wf.side_effect_rows(Path(td)) == [], "missing journal fails open to []")

with tempfile.TemporaryDirectory() as td:
    (Path(td) / "side_effects.jsonl").mkdir()  # unreadable: IsADirectoryError on read
    check(wf.side_effect_rows(Path(td)) == [], "unreadable journal fails open to []")

print("OK")
