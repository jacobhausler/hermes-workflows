#!/usr/bin/env python3
"""ship2.0 / s20-wake-fixture — the owning-session notice fixture.

This is the reusable fixture (the nyf order's E13/E10 evidence bridge as an
executable) for what a REAL owner session must be able to tell apart when the
runner wakes it: a fresh owner stamp, a held gate ASK carrying its payload,
failed-set DELTAS, and cascade folds — all through the real durable notice
writer (notify / _notify_node_failure) on synthetic private run roots.

The owner endpoint is a process-local one-shot sink (WF_WAKE_SINK_PORT, the
test/sidecar-only hook): no real session, gateway or scheduler is contacted,
and every owner stamp is a synthetic session id minted by this file. Pinned
observable outcomes (stdlib-parsable, never substring-hunting the text):

  A. FRESH OWNER — every run carries its own owner {session_id: synth-*}; the
     sink's X-Hermes-Session-Id header can only ever equal a minted id, and an
     owner-null run writes NOTHING (no wake manufactured on an owner-null seed);
  B. HELD-GATE ASK — the notice carries gate_id, the diff-first gate_hold_diff
     verdict, the dwell age from the committed hold marker, the question,
     options, context and the declared timeout (all from the COMMITTED
     graph.json), the template body stays verbatim after the separator, and
     the row carries the gate subject for machine readers (gate, gate_fields
     per-field digests); a re-fire of an amended question adjudicates
     changed/unchanged/unchanged and a bearer shape inside graph prose is
     redacted; a redrive of one SETTLED decision costs zero new POSTs;
  C. FAILED_DELTA DELIVERY — the first run.failed renders the newly-failed ids
     (failed_delta/failed_set); key-variant re-notices over the UNCHANGED
     committed failed-set cost zero owner turns and one
     `suppressed: failed_set_unchanged` audit row each; a real change emits
     exactly one notice naming only the new delta;
  D. CASCADE — a committed root failure notifies IMMEDIATELY naming
     cascade_root/cascade_members; causally-dependent member failures fold to
     `cascade_of=<root>` audit rows and the notices/cascade.json member list;
     wave-top redrives of accounted commits are silent;
  E. DND/SUPPRESSION DISTINGUISHES DELIVERIES FROM ASKS — a node-level
     wake_tier:"silent" suppresses that gate's ASK into exactly ONE recorded
     row (delivered=False, payload text intact, never retried for that
     instance, every earlier row still on disk — a suppression is a decision,
     not an eraser); a new hold decision records its OWN row; run-terminal
     deliveries are NOT tier-governable and still fire; a [SILENT] declared
     verdict quiets run.done via `silent_marker` only, never run.failed; and
     the row-shape classification (ask rows carry `gate`, delivery rows carry
     delta/cascade pointers, suppression rows carry `suppressed`) is disjoint
     and count-exact over the whole ledger;
  F. EVENT SOURCE — every persisted row is wake-observe/v2 with the first-class
     trio (skey/rev/attempts), its run_id and event, the inert run_id/event
     fields ride before the separator, every delivered row's Idempotency-Key
     equals its row id, and the rendered body is redacted at the seam;
  G. NO DEFAULT EDITS — the wake defaults and registries this fixture leans on
     are pinned at their shipped values (full tier, tier-governed set,
     coalesce set, template<->registry closure, cascade window): the fixture
     observes the scheduler, it does not move it.

Run: cd tests && python3 ship20-wake-owner-fixture.py
"""
import http.server
import json
import os
import shutil
import sys
import threading
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-ship20-wake"
os.environ["HERMES_HOME"] = str(HOME)          # fake home: gateway discovery is absent
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")   # hermetic pin: own runs root, ever
os.environ.pop("WF_WAKE_SINK_PORT", None)
os.environ.pop("API_SERVER_KEY", None)
os.environ.pop("API_SERVER_HOST", None)
os.environ.pop("API_SERVER_PORT", None)
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
RUNS = HOME / "workflows"
RUNS.mkdir(parents=True)

POSTS = []
MODE = {"status": 202}

class Sink(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        POSTS.append({"idem": self.headers.get("Idempotency-Key"),
                      "sid": self.headers.get("X-Hermes-Session-Id"),
                      "content": body["messages"][0]["content"],
                      "status": MODE["status"]})
        self.send_response(MODE["status"])
        self.end_headers()
        self.wfile.write(b"{}")
    def log_message(self, *a):
        pass

SRV = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Sink)
threading.Thread(target=SRV.serve_forever, daemon=True).start()
os.environ["WF_WAKE_SINK_PORT"] = str(SRV.server_address[1])

OWNER_SIDS = set()
def fresh_owner():
    sid = "synth-" + uuid.uuid4().hex[:10]
    OWNER_SIDS.add(sid)
    return sid

def mk_run(name, graph_doc):
    """A synthetic private run root with a FRESH owner stamp."""
    r = RUNS / name
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps(graph_doc))
    (r / "run.json").write_text(json.dumps({"owner": {"session_id": fresh_owner()}}))
    (r / "wake_protocol").write_text("runner-authored/v1")
    return r

def owner_sid(r):
    return json.loads((r / "run.json").read_text())["owner"]["session_id"]

def commit_node(r, byid, nid, status, attempts=1, error_class="transport",
                output=None):
    rec = {"status": status, "attempts": attempts,
           "skey": f"wf:{r.name}:{nid}:abcdef01.{attempts:06d}",
           "log_path": str(r / "logs" / f"{nid}.a{attempts}.log")}
    if status == "failed":
        rec["error"] = "boom"
        rec["error_class"] = error_class
    if output is not None:
        rec["output"] = output
    rec["efp"] = wfcommon.efp(byid, byid[nid])
    rec["fp_rule_version"] = wfcommon.FP_RULE_VERSION
    (r / "nodes" / f"{nid}.json").write_text(json.dumps(rec))
    return rec

def rows(r):
    p = r / "wake.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []

def owner_notices(r):
    return [x for x in rows(r) if not x.get("suppressed")]

def audits(r, reason):
    return [x for x in rows(r) if x.get("suppressed") == reason]

def field(t, name):
    seg = t.split(" \u2014 ", 1)[0]
    key = name + "="
    i = seg.find(" " + key)
    if i < 0:
        return None
    return json.JSONDecoder().raw_decode(seg[i + 1 + len(key):])[0]

GATE = {"id": "g1", "type": "gate", "question": "Ship the change?",
        "options": ["approve", "veto"], "context": "tests green",
        "hold_timeout": 600}
AGENT = {"id": "n1", "type": "agent", "goal": "g"}

try:
    # ============ B/F: the held-gate ASK rides its payload, source-stamped ============
    NODES = [GATE, AGENT]
    r = mk_run("s20-ask", {"name": "s20-ask", "nodes": NODES})
    (r / "gates" / "g1.held.json").write_text(json.dumps({"since": time.time() - 123}))
    b = len(POSTS)
    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    row = rows(r)[-1]
    t = row["text"]
    check("the ASK delivers one owner turn to the fresh owner",
          v == "delivered" and len(owner_notices(r)) == 1 and len(POSTS) - b == 1, f"{v}")
    check("the ASK POST rides the run's OWN fresh owner stamp",
          POSTS[-1]["sid"] == owner_sid(r) and POSTS[-1]["sid"].startswith("synth-"),
          POSTS[-1]["sid"])
    check("the ASK carries the gate id", field(t, "gate_id") == "g1", t[:200])
    check("diff-first: gate_hold_diff precedes the question fields",
          t.index("gate_hold_diff") < t.index("gate_question")
          and field(t, "gate_hold_diff") == {"question": "new_hold", "options": "new_hold",
                                              "context": "new_hold"}, t[:240])
    check("dwell age renders from the committed hold marker",
          abs((field(t, "gate_hold_dwell_s") or 0) - 123) <= 2, str(field(t, "gate_hold_dwell_s")))
    check("the question/options/context ride from the COMMITTED graph",
          field(t, "gate_question") == "Ship the change?"
          and field(t, "gate_options") == ["approve", "veto"]
          and field(t, "gate_context") == "tests green", t[:240])
    check("the declared hold timeout rides", field(t, "gate_hold_timeout_s") == 600, t[:240])
    check("the template body after the separator stays verbatim",
          t.split(" \u2014 ", 1)[1] == wf._WAKE_TEMPLATES["gate.held"], t[:240])
    check("the row carries the gate subject for machine readers",
          row.get("gate") == "g1" and len(row["gate_fields"]["question"]) == 12,
          str(row.get("gate_fields")))
    check("event source: every delivered row is wake-observe/v2 with the trio",
          row.get("schema") == "wake-observe/v2"
          and set(("skey", "rev", "attempts")) <= set(row)
          and row.get("run_id") == r.name and row.get("event") == "gate.held"
          and field(t, "run_id") == r.name and field(t, "event") == "gate.held"
          and POSTS[-1]["idem"] == row["id"], str(sorted(row))[:240])

    # re-fire: an amended ASK adjudicates; a settled redrive costs zero turns
    amended = dict(GATE, question="Ship the change? v2 (Bearer SYNTHGATE says hi)")
    (r / "graph.json").write_text(json.dumps({"name": "s20-ask", "nodes": [amended, AGENT]}))
    v = wf.notify(r, "gate.held", key="g1:hdefB", node="g1")
    t2 = rows(r)[-1]["text"]
    check("re-fire: the diff verdict names exactly the moved field",
          field(t2, "gate_hold_diff") == {"question": "changed", "options": "unchanged",
                                          "context": "unchanged"}, str(field(t2, "gate_hold_diff")))
    check("re-fire: dwell grows from the same hold marker",
          (field(t2, "gate_hold_dwell_s") or 0) >= 123, str(field(t2, "gate_hold_dwell_s")))
    check("re-fire: the bearer shape inside graph prose is redacted, the ask still rides",
          "SYNTHGATE" not in t2 and "[redacted]" in t2 and "v2" in str(field(t2, "gate_question")),
          t2[:300])
    b = len(POSTS)
    v = wf.notify(r, "gate.held", key="g1:hdefB", node="g1")   # same settled decision, redrive
    check("a redrive of one SETTLED decision costs zero new owner turns",
          v == "delivered" and len(POSTS) - b == 0 and len(rows(r)) == 2, f"{v}")

    # ============ A: owner-null writes nothing (no manufactured wake) ============
    r = mk_run("s20-null", {"name": "s20-null", "nodes": NODES})
    (r / "run.json").write_text(json.dumps({"owner": None}))
    b = len(POSTS)
    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    check("owner-null degrades silently: zero rows, zero POSTs",
          v == "skipped" and not (r / "wake.jsonl").exists() and len(POSTS) - b == 0, str(v))

    # ============ C: run.failed renders the failed-set DELTA ============
    NODES = [{"id": "n1", "type": "agent", "goal": "g"},
             {"id": "n2", "type": "agent", "goal": "g"}]
    r = mk_run("s20-delta", {"name": "s20-delta", "nodes": NODES})
    byid = {n["id"]: n for n in NODES}
    commit_node(r, byid, "n1", "failed")
    b = len(POSTS)
    v = wf.notify(r, "run.failed", key="aborted by n1")
    w = owner_notices(r)
    check("first run.failed delivers one DELIVERY notice",
          v == "delivered" and len(w) == 1 and len(POSTS) - b == 1, f"{v}")
    check("the delivery renders the newly-failed ids (failed_delta/failed_set)",
          field(w[0]["text"], "failed_delta") == ["n1"]
          and field(w[0]["text"], "failed_set") == ["n1"], w[0]["text"][:240])
    b = len(POSTS)
    outs = [wf.notify(r, "run.failed", key=k) for k in
            ("dead end", "graph stuck", "stalled lane")]
    check("3 key-variant re-notices over the UNCHANGED failed-set cost zero owner turns",
          all(o == "skipped" for o in outs) and len(owner_notices(r)) == 1
          and len(POSTS) - b == 0, f"{outs}")
    check("each costs exactly one failed_set_unchanged audit row (history, not a hole)",
          len(audits(r, "failed_set_unchanged")) == 3
          and all(x["delivered"] is False and "id" not in x and x.get("funnel") == "suppressed"
                  for x in audits(r, "failed_set_unchanged")))
    commit_node(r, byid, "n2", "failed")
    v = wf.notify(r, "run.failed", key="graph stuck")
    w = owner_notices(r)
    check("a failed-set change emits exactly ONE notice naming only the new delta",
          v == "delivered" and len(w) == 2
          and field(w[-1]["text"], "failed_delta") == ["n2"]
          and field(w[-1]["text"], "failed_set") == ["n1", "n2"], w[-1]["text"][:240])

    # ============ D: the cascade folds members under the root's notice ============
    NODES = [{"id": "root", "type": "agent", "goal": "g"}] + \
            [{"id": f"m{i}", "type": "agent", "goal": "g", "after": ["root"]} for i in range(1, 5)]
    r = mk_run("s20-cascade", {"name": "s20-cascade", "nodes": NODES})
    byid = {n["id"]: n for n in NODES}
    for nid in byid:
        commit_node(r, byid, nid, "failed")
    b = len(POSTS)
    wf._notify_node_failure(r, "root")
    for i in range(1, 5):
        wf._notify_node_failure(r, f"m{i}")
    lead = [x for x in owner_notices(r) if x.get("event") == "node.action_required"]
    check("a root failure fans into ONE owner notice (5-node causal fan)",
          len(lead) == 1 and len(POSTS) - b == 1, f"rows={len(lead)} posts={len(POSTS)-b}")
    check("the leading notice names the cascade root and its member count",
          field(lead[0]["text"], "cascade_root") == "root"
          and type(field(lead[0]["text"], "cascade_members")) is int, lead[0]["text"][:240])
    check("the leading notice carries the trio from the observer's key payload",
          isinstance(lead[0].get("skey"), str) and type(lead[0].get("attempts")) is int
          and type(lead[0].get("rev")) is int, str(lead[0])[:240])
    check("each member commit costs exactly one cascade_of=root audit row",
          len(audits(r, "cascade_of=root")) == 4, str(len(audits(r, "cascade_of=root"))))
    cad = json.loads((r / "notices" / "cascade.json").read_text())
    check("the cascade record names root and all 4 folded members",
          cad["root"]["root"] == "root" and len(cad["root"]["members"]) == 4, str(cad)[:240])
    n_rows, n_posts = len(rows(r)), len(POSTS)
    for _tick in range(3):
        for nid in byid:
            wf._notify_node_failure(r, nid)
    check("wave-top redrives of accounted commits stay silent (ops-idempotent)",
          len(rows(r)) == n_rows and len(POSTS) == n_posts, f"rows={len(rows(r))}")

    # ============ E: DND distinguishes the ASK from the DELIVERY ============
    NODES = [dict(GATE, wake_tier="silent"), AGENT]
    r = mk_run("s20-dnd", {"name": "s20-dnd", "nodes": NODES})
    byid = {n["id"]: n for n in NODES}
    (r / "gates" / "g1.held.json").write_text(json.dumps({"since": time.time() - 60}))
    commit_node(r, byid, "n1", "failed")
    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    sup = [x for x in rows(r) if x.get("suppressed") == "wake_tier:silent"]
    check("the DND'd ASK costs zero owner turns and records exactly ONE row",
          v == "skipped" and len(sup) == 1 and sup[0]["delivered"] is False, f"{v} {rows(r)}")
    check("the suppression row keeps the payload (a decision, not an eraser)",
          field(sup[0]["text"], "gate_id") == "g1"
          and field(sup[0]["text"], "gate_hold_dwell_s") is not None
          and sup[0]["id"], str(sup[0])[:240])
    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    check("the same suppressed instance never re-arms (recorded once)",
          v == "skipped" and len(rows(r)) == 1, f"{v}")
    v = wf.notify(r, "gate.held", key="g1:hdefB", node="g1")
    check("a NEW hold decision records its OWN suppression row (history accumulates)",
          v == "skipped" and len(rows(r)) == 2, f"{v}")
    b = len(POSTS)
    v = wf.notify(r, "run.failed", key="aborted by n1")
    check("run-terminal deliveries are NOT tier-governable: the DELIVERY still fires",
          v == "delivered" and len(POSTS) - b == 1
          and field(owner_notices(r)[-1]["text"], "failed_delta") == ["n1"]
          and (r / "gates" / "g1.held.json").exists(), f"{v}")

    # [SILENT] verdict: the author's own quieting — run.done only, never run.failed
    NODES = [{"id": "verdict", "type": "agent", "goal": "g"}, AGENT]
    r = mk_run("s20-quiet", {"name": "s20-quiet", "result": "verdict", "nodes": NODES})
    byid = {n["id"]: n for n in NODES}
    commit_node(r, byid, "verdict", "done", output="all quiet on this lane [SILENT]")
    v = wf.notify(r, "run.done")
    check("a [SILENT] declared verdict quiets run.done (silent_marker, recorded once)",
          v == "skipped" and len(audits(r, "silent_marker")) == 1, f"{v}")
    v = wf.notify(r, "run.failed", key="later crash")
    check("the same run's run.failed never consults the marker: it still delivers",
          v == "delivered" and len(owner_notices(r)) == 1, f"{v}")
    check("the marker suppression did not erase the ledger: both rows readable",
          len(rows(r)) == 2, str(rows(r))[:240])

    # ============ E: the ledger classification is disjoint and count-exact ============
    r = mk_run("s20-shapes", {"name": "s20-shapes", "nodes": [GATE,
                                                              {"id": "x1", "type": "agent", "goal": "g"},
                                                              {"id": "x2", "type": "agent", "goal": "g",
                                                               "after": ["x1"]}]})
    byid = {n["id"]: n for n in json.loads((r / "graph.json").read_text())["nodes"]}
    (r / "gates" / "g1.held.json").write_text(json.dumps({"since": time.time()}))
    commit_node(r, byid, "x1", "failed")
    commit_node(r, byid, "x2", "failed")
    wf.notify(r, "gate.held", key="g1:hdefA", node="g1")          # delivered ASK
    wf._notify_node_failure(r, "x1")                              # leading DELIVERY
    wf._notify_node_failure(r, "x2")                              # folded member
    wf.notify(r, "run.failed", key="aborted by x1")               # delta DELIVERY
    all_rows = rows(r)
    asks = [x for x in all_rows if not x.get("suppressed") and x.get("gate")]
    deliveries = [x for x in all_rows if not x.get("suppressed") and not x.get("gate")
                  and ("failed_delta" in (x.get("text") or "")
                       or "cascade_root" in (x.get("text") or ""))]
    suppressed = [x for x in all_rows if x.get("suppressed")]
    check("ASK rows carry the gate subject; DELIVERY rows carry delta/cascade pointers",
          len(asks) == 1 and len(deliveries) == 2
          and not ({json.dumps(x, sort_keys=True) for x in asks}
                   & {json.dumps(x, sort_keys=True) for x in deliveries}),
          f"asks={len(asks)} deliveries={len(deliveries)}")
    check("every suppression (DND or fold) is a recorded row with delivered=False",
          all(x["delivered"] is False for x in suppressed)
          and {x["suppressed"] for x in suppressed} == {"cascade_of=x1"},
          str([x.get("suppressed") for x in suppressed]))
    check("one owner-turn budget per ask/delivery: POSTs == non-suppressed rows with text",
          len([p for p in POSTS if p["sid"] == owner_sid(r)])
          == len([x for x in all_rows if not x.get("suppressed") and x.get("delivered")]),
          f"posts={len(POSTS)}")

    # ============ G: no wake-default or scheduler-code edits ============
    check("wake defaults and registries stand at their shipped values",
          wf.WAKE_TIER_DEFAULT == "full"
          and wf._TIERED_WAKE_EVENTS == frozenset({"gate.held", "fanout.stragglers"})
          and wf._WAKE_COALESCE == frozenset({"fanout.stragglers"})
          and set(wf._WAKE_TEMPLATES) == set(wf._WAKE_EVENTS)
          and wf.CASCADE_COALESCE_S == 120.0
          and wf.SILENT_MARKER == "[SILENT]")

    # ============ A closer: no POST ever carried a non-synthetic owner ============
    check("the fixture never contacted a real owner session",
          len(POSTS) > 0 and all(p["sid"] in OWNER_SIDS for p in POSTS),
          f"owners={len(OWNER_SIDS)} posts={len(POSTS)}")
finally:
    SRV.shutdown()
    shutil.rmtree(HOME, ignore_errors=True)

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
