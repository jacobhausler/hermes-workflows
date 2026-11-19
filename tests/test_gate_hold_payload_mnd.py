#!/usr/bin/env python3
"""est-mnd / E13 — gate holds carry their payload.

The measured failure: 'the hold notices carry no question content, so the
operator polls to find what is asked' — reproduced on cold seats: 28/28 miss
question_found; seats re-derived _def from full node definitions. Pinned here
(observable outcomes):

  * EVERY gate.held notice carries: the gate id, the rendered question (and
    options/context), a DIFF-FIRST verdict (gate_hold_diff before the
    question fields), and the dwell age (gate_hold_dwell_s) from the run's
    committed hold marker;
  * the row itself carries the subject for machine readers: gate,
    gate_fields (per-field digests) — s42 question_found has a stdlib-parsable
    home;
  * a RE-FIRE adjudicates: fields compared against the last notified hold for
    the same gate (changed/unchanged/added/removed), s42 refire_adjudicated;
  * AUTHORITY stays whole: the values are read by the RUNNER from the
    committed graph.json at the notify point (no call-site text), they ride
    as JSON-quoted inert fields BEFORE the separator, the template body
    after the separator stays verbatim, and a bearer shape inside a graph
    string is redacted like every persisted field;
  * an unresolved gate (bogus key) degrades to honest absence: gate_id +
    new_hold verdict, no fabricated question.

Run: cd tests && python3 test_gate_hold_payload_mnd.py
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-mnd-hold"
os.environ["HERMES_HOME"] = str(HOME)          # no config: nowhere-ever settles, no sink needed
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
os.environ.pop("WF_WAKE_SINK_PORT", None)
os.environ.pop("API_SERVER_KEY", None)
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

if HOME.exists():
    shutil.rmtree(HOME)
RUNS = HOME / "workflows"
RUNS.mkdir(parents=True)

def field(t, name):
    seg = t.split(" \u2014 ", 1)[0]
    key = name + "="
    i = seg.find(" " + key)
    if i < 0:
        return None
    return json.JSONDecoder().raw_decode(seg[i + 1 + len(key):])[0]

GATE = {"id": "g1", "type": "gate", "question": "Ship the change?",
        "options": ["yes", "no"], "context": "tests are green", "hold_timeout": 600}
NODES = [GATE]

r = RUNS / "mnd-hold"
(r / "nodes").mkdir(parents=True)
(r / "gates").mkdir()
(r / "graph.json").write_text(json.dumps({"name": "mnd-hold", "nodes": NODES}))
(r / "run.json").write_text(json.dumps({"owner": {"session_id": "hold-mnd"}}))
(r / "wake_protocol").write_text("runner-authored/v1")
(r / "gates" / "g1.held.json").write_text(json.dumps({"since": time.time() - 123}))

def rows():
    return [json.loads(l) for l in (r / "wake.jsonl").read_text().splitlines()]

# ---- first fire: the payload rides; the body stays template-verbatim ----
wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
row = rows()[-1]
t = row["text"]
check("question_found: the hold notice carries the gate id",
      field(t, "gate_id") == "g1", t[:200])
check("question_found: the rendered question rides the notice",
      field(t, "gate_question") == "Ship the change?", t[:240])
check("the options ride too",
      field(t, "gate_options") == ["yes", "no"], t[:240])
check("the context rides too",
      field(t, "gate_context") == "tests are green", t[:240])
check("diff-first: gate_hold_diff precedes the question field",
      t.index("gate_hold_diff") < t.index("gate_question")
      and field(t, "gate_hold_diff") == {"question": "new_hold", "options": "new_hold",
                                          "context": "new_hold"}, t[:240])
check("the hold marker's clock renders as dwell age",
      abs((field(t, "gate_hold_dwell_s") or 0) - 123) <= 2, str(field(t, "gate_hold_dwell_s")))
check("the declared hold timeout rides", field(t, "gate_hold_timeout_s") == 600, t[:240])
check("template body after the separator stays verbatim",
      t.split(" \u2014 ", 1)[1] == wf._WAKE_TEMPLATES["gate.held"], t[:240])
check("machine-readable subject on the row (stdlib parse, no substring hunting)",
      row.get("gate") == "g1" and len(row["gate_fields"]["question"]) == 12, str(row.get("gate_fields")))

# ---- re-fire: an amended question adjudicates against the last hold ----
amended = dict(GATE, question="Ship the change? v2 (Bearer SYNTHHOLD says hi)")
(r / "graph.json").write_text(json.dumps({"name": "mnd-hold", "nodes": [amended]}))
wf.notify(r, "gate.held", key="g1:hdefB", node="g1")
row2 = rows()[-1]
t2 = row2["text"]
check("refire: the compared-field verdict names the moved field",
      field(t2, "gate_hold_diff") == {"question": "changed", "options": "unchanged",
                                       "context": "unchanged"}, str(field(t2, "gate_hold_diff")))
check("refire: dwell age grew from the same hold marker",
      (field(t2, "gate_hold_dwell_s") or 0) >= 123, str(field(t2, "gate_hold_dwell_s")))
check("refire: a bearer shape inside graph prose is redacted in the persisted row",
      "SYNTHHOLD" not in row2["text"] and "[redacted]" in row2["text"], row2["text"][:300])
check("refire: the NEW question still rides (never suppressed for containing prose)",
      "v2" in str(field(t2, "gate_question")), t2[:300])

# ---- honest degradation: unresolvable gate def -> id + new_hold, no lie ----
wf.notify(r, "gate.held", key="ghostdef", node="ghostdef")
row3 = rows()[-1]
check("unresolvable gate: id rides, question omitted (absent, never fabricated)",
      field(row3["text"], "gate_id") == "ghostdef"
      and field(row3["text"], "gate_question") is None
      and field(row3["text"], "gate_hold_diff")["question"] == "new_hold",
      row3["text"][:240])

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
