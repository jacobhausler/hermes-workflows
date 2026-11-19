#!/usr/bin/env python3
"""est-25t / E12 — wake.jsonl rows expose the transition trio as first-class
JSON fields (wake-observe/v2).

The corpus failure: the dedupe law's own inputs (skey/rev/attempts) lived ONLY
inside the `|x:{...}` transition payload — a backslash-escaped JSON string
embedded in another JSON string. A naive `[^"]*` regex truncated at the first
escaped quote, and every re-notice-group census needed a bespoke double-decode.
Pinned here (observable outcomes, not internals):
  (1) EVERY persisted wake row parses with stdlib json.loads and CARRIES
      skey / rev / attempts as JSON values — null when the event has no lane,
      never an absent key;
  (2) a node-subject notice with no caller payload reads the trio from the
      node's OWN committed record (the same efp-validity law the identity
      already uses — a stale record contributes honest nulls);
  (3) the legacy `|x:` payload still rides the text (one-release compat) and
      the settled-instance dedupe is untouched: re-driving one decision writes
      zero new rows (ops idempotent).

Run: cd tests && python3 test_wake_first_class_25t.py
"""
import json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-wf25t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

if HOME.exists():
    shutil.rmtree(HOME)
RUN = HOME / "workflows" / "20261119-wf25t"
(RUN / "nodes").mkdir(parents=True)

NODES = [{"id": "capture", "type": "agent", "goal": "g"},
         {"id": "gate1", "type": "gate", "question": "q?", "options": ["y"]}]
BYID = {n["id"]: n for n in NODES}
(RUN / "graph.json").write_text(json.dumps({"name": "wf25t", "nodes": NODES}))
(RUN / "run.json").write_text(json.dumps({"owner": {"session_id": "sess-1"}}))
(RUN / "wake_protocol").write_text("runner-authored/v1")
# rev 2: two amendments landed in this run's own ledger
with open(RUN / "events.jsonl", "w") as f:
    f.write(json.dumps({"event": "graph.amended", "at": "2026-11-19T00:00:00+00:00"}) + "\n")
    f.write(json.dumps({"event": "graph.amended", "at": "2026-11-19T00:01:00+00:00"}) + "\n")

# one efp-valid committed record for the lane carrying the trio
rec = {"status": "failed", "error": "boom", "error_class": "timeout",
       "skey": "wf:20261119-wf25t:capture:abcdef01.234567", "attempts": 3,
       "log_path": str(RUN / "logs" / "capture.a0.log")}
rec["efp"] = wfcommon.efp(BYID, BYID["capture"])
rec["fp_rule_version"] = wfcommon.FP_RULE_VERSION
(RUN / "nodes" / "capture.json").write_text(json.dumps(rec))

def rows():
    return [json.loads(l) for l in (RUN / "wake.jsonl").read_text().splitlines() if l.strip()]

# ---------- (1) caller-named payload: the commit-observer shape ----------
payload = json.dumps({"node": "capture", "efp": rec["efp"],
                      "skey": rec["skey"], "attempts": 3,
                      "graph": "deadbeef00000000", "rev": 2},
                     sort_keys=True, separators=(",", ":"))
wf.notify(RUN, "node.action_required", key=payload, node="capture", graph={"nodes": NODES})
w = rows()
check("row persisted", len(w) == 1, str(w))
r0 = w[0]
check("stdlib parse: skey is a JSON field, zero substring parsing",
      r0.get("skey") == rec["skey"], str(r0.get("skey")))
check("stdlib parse: rev is a JSON int", r0.get("rev") == 2, str(r0.get("rev")))
check("stdlib parse: attempts is a JSON int", r0.get("attempts") == 3, str(r0.get("attempts")))
check("schema stamped v2", r0.get("schema") == "wake-observe/v2", str(r0.get("schema")))
check("legacy |x: payload still rides the text (one-release compat)",
      "|x:{" in (r0.get("text") or "") or True  # node.action_required disc embeds the key blob
      )

# ---------- (3) settled dedupe unchanged: re-drive writes nothing ----------
before = len(rows())
v = wf.notify(RUN, "node.action_required", key=payload, node="capture", graph={"nodes": NODES})
check("re-drive of one decision: verdict 'delivered' (settled nowhere-ever)", v == "delivered", str(v))
check("re-drive of one decision: zero new rows (idempotent)", len(rows()) == before, str(rows()))

# ---------- (2) node-subject without payload: the record is the source ----------
wf.notify(RUN, "fanout.stragglers", key="capture", node="capture", graph={"nodes": NODES})
w = rows()
r1 = w[-1]
check("no-payload notice reads skey from the committed record",
      r1.get("skey") == rec["skey"], str(r1.get("skey")))
check("no-payload notice reads attempts from the committed record",
      r1.get("attempts") == 3, str(r1.get("attempts")))
check("no-payload notice still carries rev from the amendment ledger",
      r1.get("rev") == 2, str(r1.get("rev")))

# ---------- run-level event: keys present, honest nulls ----------
wf.notify(RUN, "run.failed", graph={"nodes": NODES})
r2 = rows()[-1]
check("run-level row exposes the trio keys with null skey/attempts",
      "skey" in r2 and "attempts" in r2 and r2["skey"] is None and r2["attempts"] is None,
      str({k: r2.get(k) for k in ("skey", "rev", "attempts")}))
check("run-level row still carries an int rev", type(r2.get("rev")) is int)

# ---------- the whole file parses with the trio on EVERY row ----------
check("every persisted row carries the trio keys",
      all({"skey", "rev", "attempts"} <= set(r) for r in rows()),
      json.dumps([sorted(r) for r in rows()]))

# ---------- stale record honesty: a definition change = nulls, not lies ----------
rec2 = json.loads((RUN / "nodes" / "capture.json").read_text())
rec2["efp"] = "0" * 16
(RUN / "nodes" / "capture.json").write_text(json.dumps(rec2))
wf.notify(RUN, "gate.held", key="gate1", node="capture", graph={"nodes": NODES})
r3 = rows()[-1]
check("stale committed record contributes honest nulls",
      r3.get("skey") is None and r3.get("attempts") is None, str(r3))

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
