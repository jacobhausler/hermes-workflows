#!/usr/bin/env python3
"""Fake `bd` for the bead-close read-back gate (est-13z1).

Spawned as the runner's estate-store probe with the fixed argv of a real
read-back:  bd -C <store> show <id> --json

Ground truth is the JSON map at $FAKE_BD_STORE: {bead_id: {"status": ...,
"assignee": ...}}. A bead that is closed reports closed; every OTHER bead is
the incident shape — an OPEN bead (in_progress) that a node's prose may falsely
claim closed. Invocation argv is appended to $FAKE_BD_LOG so tests can prove
the exact argv the gate ran.

Unknown bead id => exit 1 with bd's own 'not found' wording (read-back proves
non-existence, never launders a close).
"""
import json
import os
import sys

args = sys.argv[1:]
log = os.environ.get("FAKE_BD_LOG")
if log:
    with open(log, "a") as f:
        f.write(" ".join(args) + "\n")

# fixed-argv contract: -C <store> show <id> --json
if len(args) != 5 or args[0] != "-C" or args[2] != "show" or args[4] != "--json":
    print(json.dumps({"error": "fake bd: unexpected argv", "argv": args}))
    sys.exit(2)
store_dir, bid = args[1], args[3]

store_path = os.environ.get("FAKE_BD_STORE", "")
try:
    with open(store_path) as f:
        store = json.load(f)
except Exception:
    print("fake bd: store unreadable", file=sys.stderr)
    sys.exit(3)

row = store.get(bid)
if row is None:
    print(f"Issue {bid} not found")
    print(json.dumps({"error": "no issues found matching the provided IDs",
                      "schema_version": 1}))
    sys.exit(1)

print(json.dumps([{"id": bid, "title": "fake", "status": row["status"],
                   "issue_type": "task", "assignee": row.get("assignee", "nobody")}]))
sys.exit(0)
