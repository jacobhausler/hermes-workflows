#!/usr/bin/env python3
"""est-mnd / E10 — the notice funnel: state-identity dedupe, same-root cascade
coalescing, run.failed DELTA rendering.

The ha-lighting bill: 33 delivered re-notices (16 provably zero-info), 7 real
failures rendered as one indistinguishable sentence, one root failure fanned
into 9 'Inspect status once' owner notices in 74 s. This file replays that
shape through the new notifier and asserts OBSERVABLE outcomes only:

  A. delta law — 7 re-notices of run.failed over an UNCHANGED committed
     failed-set (distinct call-site keys, hence distinct instance ids) emit
     ZERO owner notices and one `suppressed: failed_set_unchanged` wake.jsonl
     audit row EACH; a failed-set change emits EXACTLY ONE notice whose text
     renders the newly-failed node ids (failed_delta) — and only those;
  B. state-identity law — the same node-subject state (skey+efp+attempts-set)
     reached over a NEW instance id (bumped graph fingerprint) is suppressed
     with a `state_identity_delivered` audit row, while a genuinely new
     attempt-set still delivers;
  C. cascade law — a committed root failure notifies IMMEDIATELY (the 610
     actionable-transition law) naming its cascade record; the 8 causally
     dependent member failures that follow emit ZERO additional owner notices
     and one `cascade_of=<root>` audit row each, folded into the record with
     the member list;
  D. idempotent redrive — the wave-top observation loop re-noticing every
     failed node every tick writes zero new rows and fires zero POSTs;
  E. a try-later delivery (500) leaves the baselines STALE (the retry must
     re-notice); the eventual success moves them.

Run: cd tests && python3 test_notice_funnel_mnd.py
"""
import http.server
import json
import os
import shutil
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-mnd-funnel"
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
RUNS = HOME / "workflows"
RUNS.mkdir(parents=True)

POSTS = []
MODE = {"status": 202}

class Sink(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        POSTS.append({"idem": self.headers.get("Idempotency-Key"),
                      "content": body["messages"][0]["content"], "status": MODE["status"]})
        self.send_response(MODE["status"])
        self.end_headers()
        self.wfile.write(b"{}")
    def log_message(self, *a):
        pass

SRV = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Sink)
threading.Thread(target=SRV.serve_forever, daemon=True).start()
os.environ["WF_WAKE_SINK_PORT"] = str(SRV.server_address[1])

def field(t, name):
    seg = t.split(" \u2014 ", 1)[0]
    key = name + "="
    i = seg.find(" " + key)
    if i < 0:
        return None
    return json.JSONDecoder().raw_decode(seg[i + 1 + len(key):])[0]

def mk_run(name, nodes):
    r = RUNS / name
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": name, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"owner": {"session_id": "funnel-mnd"}}))
    (r / "wake_protocol").write_text("runner-authored/v1")
    return r

def fail_node(r, byid, nid, attempts=1, error_class="transport", skey=None):
    rec = {"status": "failed", "error": "boom", "error_class": error_class,
           "attempts": attempts, "skey": skey or f"wf:{r.name}:{nid}:abcdef01.{attempts:06d}",
           "log_path": str(r / "logs" / f"{nid}.a{attempts}.log")}
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

try:
    # ---------------- A. failed-set DELTA over key-variant re-notices ----------------
    NODES = [{"id": "n1", "type": "agent", "goal": "g"},
             {"id": "n2", "type": "agent", "goal": "g"}]
    r = mk_run("mnd-delta", NODES)
    byid = {n["id"]: n for n in NODES}
    fail_node(r, byid, "n1")
    b = len(POSTS)
    v = wf.notify(r, "run.failed", key="aborted by n1")
    w = owner_notices(r)
    check("first run.failed delivers one owner notice",
          v == "delivered" and len(w) == 1 and len(POSTS) - b == 1, f"{v} {w}")
    check("first notice renders the newly-failed ids",
          field(w[0]["text"], "failed_delta") == ["n1"], w[0]["text"][:200])
    b = len(POSTS)
    outs = [wf.notify(r, "run.failed", key=k) for k in
            ("dead end", "effect receipt", "graph stuck", "stalled lane",
             "aborted by n1 (again)", "pre-start: lane wreckage", "graph stuck v2")]
    check("7 re-notices over an unchanged failed-set emit 0 owner notices",
          all(o == "skipped" for o in outs) and len(owner_notices(r)) == 1
          and len(POSTS) - b == 0, f"{outs} posts={len(POSTS)-b}")
    check("each re-notice carries a 'suppressed: failed_set_unchanged' audit row",
          len(audits(r, "failed_set_unchanged")) == 7, str(len(audits(r, "failed_set_unchanged"))))
    check("audit rows are delivered=False and settle nothing",
          all(x["delivered"] is False and "id" not in x for x in audits(r, "failed_set_unchanged")))
    fail_node(r, byid, "n2")
    b = len(POSTS)
    v = wf.notify(r, "run.failed", key="graph stuck")
    w = owner_notices(r)
    check("a failed-set change emits exactly one notice",
          v == "delivered" and len(w) == 2 and len(POSTS) - b == 1, f"{v}")
    check("the delta notice renders ONLY the newly-failed node id",
          field(w[-1]["text"], "failed_delta") == ["n2"]
          and field(w[-1]["text"], "failed_set") == ["n1", "n2"], w[-1]["text"][:200])
    # the #610/B3 amendment law stays whole under the delta law: a genuine
    # amendment re-arms the delta (one notice, nothing newly-failed); with no
    # amendment, the same set over any other reason string stays suppressed.
    wf.log(r, "graph.amended")
    b = len(POSTS)
    v = wf.notify(r, "run.failed", key="post-amend re-observe")
    w = owner_notices(r)
    check("a genuine amendment re-arms run.failed (one notice, empty delta)",
          v == "delivered" and len(w) == 3 and len(POSTS) - b == 1
          and field(w[-1]["text"], "failed_delta") == [], f"{v}")
    v = wf.notify(r, "run.failed", key="same gen, another reason")
    check("the re-armed set stays unchanged at the new rev: zero further notices",
          v == "skipped" and len(owner_notices(r)) == 3
          and len(audits(r, "failed_set_unchanged")) == 8, f"{v}")

    # ---------------- B. state-identity dedupe over a new instance ----------------
    NODES = [{"id": "n3", "type": "agent", "goal": "g"}]
    r = mk_run("mnd-ident", NODES)
    byid = {n["id"]: n for n in NODES}
    rec = fail_node(r, byid, "n3", attempts=2)
    key = json.dumps({"node": "n3", "efp": rec["efp"], "skey": rec["skey"],
                      "attempts": 2, "graph": "0" * 16, "rev": 0},
                     sort_keys=True, separators=(",", ":"))
    b = len(POSTS)
    v = wf.notify(r, "node.action_required", key=key, node="n3", graph={"nodes": NODES})
    check("a fresh node state delivers",
          v == "delivered" and len(owner_notices(r)) == 1, str(v))
    key2 = json.dumps({"node": "n3", "efp": rec["efp"], "skey": rec["skey"],
                       "attempts": 2, "graph": "f" * 16, "rev": 0},
                      sort_keys=True, separators=(",", ":"))
    v2 = wf.notify(r, "node.action_required", key=key2, node="n3", graph={"nodes": NODES})
    check("the SAME state over a new instance id is suppressed (state_identity_delivered)",
          v2 == "skipped" and len(audits(r, "state_identity_delivered")) == 1
          and len(owner_notices(r)) == 1, f"{v2} {rows(r)}")
    rec3 = fail_node(r, byid, "n3", attempts=3)   # new attempt-set = new state
    key3 = json.dumps({"node": "n3", "efp": rec3["efp"], "skey": rec3["skey"],
                       "attempts": 3, "graph": "0" * 16, "rev": 0},
                      sort_keys=True, separators=(",", ":"))
    v3 = wf.notify(r, "node.action_required", key=key3, node="n3", graph={"nodes": NODES})
    check("a later attempt-set is new state and delivers", v3 == "delivered", str(v3))

    # ---------------- C. same-root cascade fan (ha-lighting shape) ----------------
    NODES = [{"id": "root", "type": "agent", "goal": "g"}] + \
            [{"id": f"m{i}", "type": "agent", "goal": "g", "after": ["root"]} for i in range(1, 9)]
    r = mk_run("mnd-fan", NODES)
    byid = {n["id"]: n for n in NODES}
    recs = {nid: fail_node(r, byid, nid) for nid in byid}
    b = len(POSTS)
    wf._notify_node_failure(r, "root")
    for i in range(1, 9):
        wf._notify_node_failure(r, f"m{i}")
    fan_posts = POSTS[b:]
    node_rows = [x for x in owner_notices(r) if x.get("event") == "node.action_required"]
    check("one root failure fans into ONE owner notice (9-node fan)",
          len(node_rows) == 1 and len(fan_posts) == 1,
          f"rows={len(node_rows)} posts={len(fan_posts)}")
    check("the notice names the root and its cascade member count",
          field(node_rows[0]["text"], "cascade_root") == "root"
          and type(field(node_rows[0]["text"], "cascade_members")) is int,
          node_rows[0]["text"][:240])
    check("each member commit carries a 'cascade_of=root' audit row",
          len(audits(r, "cascade_of=root")) == 8, str(len(audits(r, "cascade_of=root"))))
    cad = json.loads((r / "notices" / "cascade.json").read_text())
    check("the cascade record names root and ALL 8 members",
          cad["root"]["root"] == "root" and len(cad["root"]["members"]) == 8, str(cad))
    # D. idempotent redrive: the wave-top observation loop again, everything
    for _tick in range(3):
        for nid in byid:
            wf._notify_node_failure(r, nid)
    check("redrives of accounted commits are silent (no rows, no POSTs, ops-idempotent)",
          len(rows(r)) == 9 and len(POSTS) == b + 1, f"rows={len(rows(r))}")

    # ---------------- E. try-later keeps the retry line open ----------------
    MODE["status"] = 500
    NODES = [{"id": "x1", "type": "agent", "goal": "g"}]
    r = mk_run("mnd-retry", NODES)
    byid = {n["id"]: n for n in NODES}
    fail_node(r, byid, "x1")
    v = wf.notify(r, "run.failed", key="graph stuck")
    check("a 500 attempt records undelivered and leaves the baseline stale",
          v == "undelivered" and rows(r)[-1]["delivered"] is False, str(rows(r)))
    MODE["status"] = 202
    v = wf.notify(r, "run.failed", key="graph stuck")
    check("the retry delivers (same instance, unsettled row)", v == "delivered", str(v))
    v = wf.notify(r, "run.failed", key="graph stuck v2")
    check("after the settled retry the unchanged set suppresses",
          v == "skipped" and len(audits(r, "failed_set_unchanged")) == 1, str(rows(r)))
finally:
    SRV.shutdown()

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
