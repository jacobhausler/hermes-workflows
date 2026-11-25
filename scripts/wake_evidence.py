#!/usr/bin/env python3
"""bd_2026-11-13-nyf — wake-evidence validator for the owner-bound receipt seeds.

WHAT THIS IS. The FINAL/COVERAGE audit (ui2/synthesis/FINAL.md:271) caught that the
isolated lookbook seed carried NO owner stamp, so it produced NO wake.jsonl owner-wake
evidence — and manufacturing a wake on an owner-null seed would launder a hole into a
"proof". This validator closes that gap from the production side, on NATIVE isolated
gateway/runner fixtures (never the desktop, never a live personal chat):

  seeds/            minimal, reproducible owner-bound receipt inputs for the three
                    receipt classes the lookbook was missing:
    held/           gate.held — question/options/context/hold_timeout + a DND
                    (wake_tier silent) twin gate + an amended re-fire,
    failed_delta/   run.failed — a committed efp-valid failed record + a pinned
                    FailedSetBaseline, so the notice must render the NEWLY-FAILED set,
    cascade/        node.action_required — root commit leads, causal-folded child,
                    so ONE notice names root + members and the fold is an audit row.
  seeds-owner-null/ the rejection twin: owner null. The validator refuses it BEFORE
                    touching transport, and notify() on it writes NOTHING — the
                    owner-null degradation stays evidence-free by construction.

LAW CHECKED (observable outcomes, stdlib-parsed — no substring-only acceptance):
  * every receipt row links its pointers to the source event: gate rows carry the
    subject (gate + per-field 12-hex digests) AND the diff-first text fields; the
    run.failed row carries failed_delta/failed_set/run_dir/failed_node_logs; the
    cascade row carries the trio (skey/rev/attempts) + cascade_root/members/ids;
  * delivery state is TRI-STATE and distinct from any unresolved action:
    delivered true/false/null, a typed error_class or `suppressed` reason on every
    non-delivered row — never an untyped void;
  * DND suppression never erases ledger history: the silent-tier row stays in
    wake.jsonl forever, and a re-drive of the same suppressed instance adds zero rows;
  * a settled miss (nowhere-ever) is recorded LOUD (notice_drop.json) and settles.

Run: python3 scripts/wake_evidence.py validate \
        --seeds tests/wake-evidence-nyf/seeds --out <PROOF_DIR> \
        [--head <sha>] [--owner-null-seed tests/wake-evidence-nyf/seeds-owner-null/held]
Exit 0 = every class green; exit 1 = any FAIL line (printed, one per checked law).
"""
import argparse
import json
import os
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

ARGS = None
SINK_POSTS = []          # every POST the isolated sink received, in order
SEP = " \u2014 "


class _Sink(BaseHTTPRequestHandler):
    def do_POST(self):                                    # noqa: N802
        body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
        SINK_POSTS.append({"path": self.path,
                           "session": self.headers.get("X-Hermes-Session-Id"),
                           "idempotency": self.headers.get("Idempotency-Key"),
                           "content": body.decode("utf-8", "replace")})
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):                            # stay silent: stdout is the ledger
        pass


ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


def field(t, name):
    """Parse one inert JSON-quoted pointer field out of the pre-separator segment
    (the same reader shape tests/test_gate_hold_payload_mnd.py pins)."""
    seg = t.split(SEP, 1)[0]
    key = name + "="
    i = seg.find(" " + key)
    if i < 0:
        return None
    return json.JSONDecoder().raw_decode(seg[i + 1 + len(key):])[0]


def jw(p, doc):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False))


def wake_rows(run):
    p = Path(run) / "wake.jsonl"
    if not p.is_file():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def owner_bound(run_json):
    o = (run_json.get("owner") if isinstance(run_json, dict) else None)
    return (isinstance(o, dict) and isinstance(o.get("session_id"), str)
            and o.get("session_id").strip() != "")


def stamp_failed_record(wfcommon, run, byid, nid, body, skey):
    """Materialize an efp-valid committed-failure record from the seed body:
    efp is RECOMPUTED from the live graph def, so the validity law holds by
    construction and no digest is hand-pinned."""
    node = byid[nid]
    rec = {"status": "failed", "node": nid, "skey": skey,
           "efp": wfcommon.efp(byid, node), "fp_rule_version": wfcommon.FP_RULE_VERSION,
           "finished_at": "2026-11-24T00:00:00+00:00"}
    rec.update({k: v for k, v in body.items() if k != "note"})
    jw(Path(run) / "nodes" / f"{nid}.json", rec)
    return rec


def materialize(wf, seeds, cls, run):
    """Copy the class seed into a fresh run dir: owner stamp, committed graph,
    the door's wake-protocol marker, and the class's pinned ledger facts."""
    s = Path(seeds) / cls
    r = Path(run) / cls
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    (r / "notices").mkdir()
    jw(r / "run.json", json.loads((s / "run.json").read_text()))
    jw(r / "graph.json", json.loads((s / "graph.json").read_text()))
    (r / "wake_protocol").write_text("runner-authored/v1")
    return s, r


def run_held(wf, wfcommon, seeds, run):
    s, r = materialize(wf, seeds, "held", run)
    hold = json.loads((s / "hold.json").read_text())
    since = time.time() - float(hold["since_offset_s"])
    jw(r / "gates" / "g1.held.json", {"since": since})
    graph = json.loads((r / "graph.json").read_text())
    sid = json.loads((r / "run.json").read_text())["owner"]["session_id"]
    n0 = len(SINK_POSTS)

    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    check("held: first fire DELIVERS on the isolated sink", v == "delivered", str(v))
    rows = wake_rows(r)
    a = next((x for x in rows if x.get("event") == "gate.held" and x.get("gate") == "g1"
              and not x.get("suppressed")), None)
    check("held: exactly one attempt row so far", a is not None and len(rows) == 1, str(len(rows)))
    t = a["text"]
    check("held: gate_id links the source gate", field(t, "gate_id") == "g1", t[:160])
    check("held: diff-first verdict is new_hold across all fields",
          field(t, "gate_hold_diff") == {"question": "new_hold", "options": "new_hold",
                                          "context": "new_hold"}, t[:220])
    d = field(t, "gate_hold_dwell_s")
    check("held: dwell renders the hold marker's clock (~90s seed)",
          isinstance(d, int) and 85 <= d <= 96, str(d))
    gdef = graph["nodes"][0]
    check("held: the rendered question/options/context ride from the committed graph",
          field(t, "gate_question") == gdef["question"]
          and field(t, "gate_options") == gdef["options"]
          and field(t, "gate_context") == gdef["context"], t[:260])
    check("held: declared hold_timeout rides", field(t, "gate_hold_timeout_s") == 900, t[:260])
    check("held: the row links per-field source digests (12-hex each)",
          a.get("gate") == "g1" and all(isinstance(v_, str) and len(v_) == 12
                                         for v_ in a["gate_fields"].values()),
          json.dumps(a.get("gate_fields")))
    check("held: the row is wake-observe/v2 + runner-authored protocol + tri-state delivered",
          a.get("schema") == "wake-observe/v2"
          and a.get("wake_protocol") == "runner-authored/v1"
          and a.get("delivered") is True, json.dumps({k: a.get(k) for k in
                                                      ("schema", "wake_protocol", "delivered")}))
    check("held: the transition trio rides as first-class fields",
          all(k in a for k in ("skey", "rev", "attempts")) and a.get("rev") == 0,
          json.dumps({k: a.get(k) for k in ("skey", "rev", "attempts")}))
    p = SINK_POSTS[n0]
    env = json.loads(p["content"])
    msg = (env.get("messages") or [{}])[0]
    check("held: the sink POST carries the owner session, a non-empty Idempotency-Key, "
          "and the runner-authored role:user turn",
          p["session"] == sid and bool(p["idempotency"])
          and msg.get("role") == "user"
          and str(msg.get("content", "")).startswith("[runner-authored/v1] run_id="),
          json.dumps(p)[:200])

    n1 = len(SINK_POSTS)
    v = wf.notify(r, "gate.held", key="g2:hdefS", node="g2")
    rows = wake_rows(r)
    b = next((x for x in rows if x.get("gate") is None and x.get("suppressed")), None)
    check("held: a silent-tier (DND) hold SUPPRESSES the owner turn", v == "skipped", str(v))
    check("held: the suppression is a recorded row, delivered False",
          b is not None and b.get("suppressed") == "wake_tier:silent"
          and b.get("delivered") is False, json.dumps(b)[:200])
    n_before = len(rows)
    v = wf.notify(r, "gate.held", key="g2:hdefS", node="g2")   # re-drive the SAME suppressed instance
    check("held: a re-drive of the suppressed instance writes ZERO rows (recorded once, never retried)",
          v == "skipped" and len(wake_rows(r)) == n_before, str(len(wake_rows(r))))

    # amend g1's question only, journal the amendment, re-fire under a fresh instance
    amended = json.loads(json.dumps(graph))
    amended["nodes"][0]["question"] = hold["refire_question"]
    jw(r / "graph.json", amended)
    with open(r / "events.jsonl", "a") as f:
        f.write(json.dumps({"ts": "2026-11-24T00:00:00+00:00", "event": "graph.amended",
                            "node": "g1"}) + "\n")
    v = wf.notify(r, "gate.held", key="g1:hdefB", node="g1")
    c = wake_rows(r)[-1]
    check("held: re-fire after amend delivers at a new rev", v == "delivered" and c.get("rev") == 1,
          f"{v} rev={c.get('rev')}")
    check("held: re-fire adjudicates changed/unchanged/unchanged",
          field(c["text"], "gate_hold_diff") == {"question": "changed", "options": "unchanged",
                                                  "context": "unchanged"},
          str(field(c["text"], "gate_hold_diff")))
    d2 = field(c["text"], "gate_hold_dwell_s")
    check("held: dwell grew from the same hold marker", isinstance(d2, int) and d2 >= d, str(d2))

    b_row = next((x for x in wake_rows(r) if x.get("suppressed") == "wake_tier:silent"), None)
    check("held: DND suppression never erases ledger history (row still present)",
          b_row is not None, "suppressed row vanished")
    check("held: exactly two owner POSTs for the whole held class",
          len(SINK_POSTS) - n0 == 2, str(len(SINK_POSTS) - n0))
    return r


def run_failed_delta(wf, wfcommon, seeds, run):
    s, r = materialize(wf, seeds, "failed_delta", run)
    graph = json.loads((r / "graph.json").read_text())
    byid = {n["id"]: n for n in graph["nodes"]}
    body = json.loads((s / "record.json").read_text())["root"]
    rec = stamp_failed_record(wfcommon, r, byid, "root", body, "wake-nyf-skey-nyfF")
    base = json.loads((s / "baseline.json").read_text())
    jw(r / "notices" / "failed_set.json", {k: base[k] for k in ("state", "at")})
    n0 = len(SINK_POSTS)

    # identity resolution for an UNKEYED run.failed reads the caller's graph —
    # the real runner passes the run_state projection; the fixture hands over the
    # committed graph.json, the same on-disk fact.
    v = wf.notify(r, "run.failed", graph=graph)
    row = wake_rows(r)[-1]
    t = row["text"]
    check("failed_delta: run.failed DELIVERS on the isolated sink", v == "delivered", str(v))
    check("failed_delta: the notice renders the NEWLY-FAILED set against the seeded baseline",
          field(t, "failed_delta") == ["root"] and field(t, "failed_set") == ["root"],
          f"{field(t, 'failed_delta')} / {field(t, 'failed_set')}")
    check("failed_delta: run_dir + failed_node_logs point at the source evidence",
          field(t, "run_dir") == str(r) and field(t, "failed_node_logs") == [rec["log_path"]],
          f"{field(t, 'run_dir')} / {field(t, 'failed_node_logs')}")
    check("failed_delta: the settled delivery moved the FailedSetBaseline",
          (json.loads((r / "notices" / "failed_set.json").read_text()).get("state") or {})
          .get("ids") == ["root"], "baseline did not advance")

    # a DIFFERENT instance (new reason key) over the SAME settled state: the funnel's
    # delta law cuts it to one audit row — zero owner turns, zero sink POSTs.
    v = wf.notify(r, "run.failed", key="second-reason-string")
    rows = wake_rows(r)
    sup = next((x for x in rows if x.get("funnel") == "suppressed"), None)
    check("failed_delta: an unchanged-set re-notice is funnel-suppressed",
          v == "skipped" and sup is not None
          and sup.get("suppressed") == "failed_set_unchanged"
          and sup.get("delivered") is False, json.dumps(sup)[:200])
    check("failed_delta: the suppression cost ZERO sink POSTs", len(SINK_POSTS) == n0 + 1,
          str(len(SINK_POSTS)))
    return r


def run_cascade(wf, wfcommon, seeds, run):
    s, r = materialize(wf, seeds, "cascade", run)
    graph = json.loads((r / "graph.json").read_text())
    byid = {n["id"]: n for n in graph["nodes"]}
    bodies = {k: v for k, v in json.loads((s / "record.json").read_text()).items() if k != "note"}
    rec_root = stamp_failed_record(wfcommon, r, byid, "root", bodies["root"], "wake-nyf-skey-nyfC")
    rec_child = stamp_failed_record(wfcommon, r, byid, "child", bodies["child"], "wake-nyf-skey-nyfC2")
    key_root = json.dumps({"node": "root", "efp": rec_root["efp"],
                           "skey": "wake-nyf-skey-nyfC", "attempts": 1, "rev": 0})
    key_child = json.dumps({"node": "child", "efp": rec_child["efp"],
                            "skey": "wake-nyf-skey-nyfC2", "attempts": 1, "rev": 0})
    n0 = len(SINK_POSTS)

    leads = wf._notice_cascade(r, "root", rec_root, byid, key_root)
    folded = wf._notice_cascade(r, "child", rec_child, byid, key_child)
    check("cascade: root LEADS its cascade, child FOLDS under it",
          leads is False and folded is True, f"{leads} / {folded}")
    fold_row = next((x for x in wake_rows(r) if x.get("funnel") == "suppressed"), None)
    check("cascade: the fold is an audit row naming the root (not a silent hole)",
          fold_row is not None and fold_row.get("suppressed") == "cascade_of=root"
          and fold_row.get("delivered") is False, json.dumps(fold_row)[:200])

    state = wf._notice_cascade_state(r, "root")
    v = wf.notify(r, "node.action_required", key=key_root, node="root", cascade=state)
    row = wake_rows(r)[-1]
    t = row["text"]
    check("cascade: the leading notice DELIVERS once", v == "delivered"
          and len(SINK_POSTS) == n0 + 1, f"{v} posts={len(SINK_POSTS)}")
    check("cascade: the trio names root, the folded count, and the member ids",
          field(t, "cascade_root") == "root" and field(t, "cascade_members") == 1
          and field(t, "cascade_member_ids") == ["child"],
          f"{field(t, 'cascade_root')}/{field(t, 'cascade_members')}/{field(t, 'cascade_member_ids')}")
    check("cascade: the transition identity rides the notice", " transition=" in t.split(SEP, 1)[0],
          t[:200])
    check("cascade: the row carries the payload trio as first-class fields",
          row.get("skey") == "wake-nyf-skey-nyfC" and row.get("attempts") == 1
          and row.get("rev") == 0, json.dumps({k: row.get(k) for k in ("skey", "attempts", "rev")}))
    check("cascade: exactly ONE owner notice for the two committed failures",
          len([x for x in wake_rows(r) if x.get("event") == "node.action_required"
               and x.get("delivered") is True]) == 1,
          str(len([x for x in wake_rows(r) if x.get("event") == "node.action_required"
                   and x.get("delivered") is True])))
    seen = (json.loads((r / "notices" / "state_seen.json").read_text()).get("ids") or [])
    check("cascade: the state identity settled into the delivered ledger", len(seen) == 1, str(seen))
    return r


def run_nowhere_ever(wf, wfcommon, seeds, run):
    """No endpoint at all (sink torn down, isolated home has no config): the attempt
    records a NOWHERE-EVER miss — delivered None, typed error_class, loud drop row —
    and the settled-miss law stops the retry."""
    s, r = materialize(wf, seeds, "held", run)
    jw(r / "gates" / "g1.held.json", {"since": time.time() - 5})
    os.environ.pop("WF_WAKE_SINK_PORT", None)
    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    rows = wake_rows(r)
    a = next((x for x in rows if x.get("gate") == "g1"), None)
    check("nowhere_ever: a no-endpoint attempt records delivered=None, NOT a silent skip",
          v is None and a is not None and a.get("delivered") is None
          and a.get("error_class") == "missing_endpoint",
          f"{v} {json.dumps({k: a.get(k) for k in ('delivered', 'error_class')}) if a else 'no row'}")
    drop = json.loads((r / "notice_drop.json").read_text())
    check("nowhere_ever: the miss is loud in notice_drop.json (E11)",
          isinstance(drop.get("rows"), list) and len(drop["rows"]) == 1
          and drop["rows"][0].get("class") == "missing_endpoint", json.dumps(drop)[:200])
    v = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
    check("nowhere_ever: a settled miss re-drives to ZERO new rows",
          v == "delivered" and len(wake_rows(r)) == len(rows), f"{v} {len(wake_rows(r))}")
    return r


def main():
    ap = argparse.ArgumentParser(prog="wake_evidence.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--seeds", required=True)
    v.add_argument("--out", required=True)
    v.add_argument("--head", default="")
    v.add_argument("--owner-null-seed", default="")
    a = ap.parse_args()

    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.environ["HERMES_HOME"] = str(out / "home")
    os.environ["WF_RUNS_ROOT"] = str(out / "runs")
    os.environ.pop("API_SERVER_KEY", None)
    sys.path.insert(0, str(ROOT))
    import wf                                   # noqa: E402
    import wfcommon                             # noqa: E402

    # 1) THE owner-bound gate runs BEFORE any transport: an owner-null seed can
    #    never be a wake-evidence source (the FINAL.md:271 manufacturing trap).
    for cls in ("held", "failed_delta", "cascade"):
        sj = json.loads((Path(a.seeds) / cls / "run.json").read_text())
        check(f"seed:{cls}: owner-bound (dict stamp with a non-empty session_id)",
              owner_bound(sj), json.dumps(sj.get("owner")))
        if not owner_bound(sj):
            print("EXIT 1 (owner-null seed cannot carry wake evidence)")
            return 1
    if a.owner_null_seed:
        twin = Path(a.owner_null_seed)
        sj = json.loads((twin / "run.json").read_text())
        check("owner-null twin: validator REJECTS it as a wake-evidence source",
              not owner_bound(sj), json.dumps(sj.get("owner")))
        r = out / "runs" / "owner-null"
        shutil.rmtree(r, ignore_errors=True)
        (r / "nodes").mkdir(parents=True)
        jw(r / "run.json", sj)
        shutil.copy(twin / "graph.json", r / "graph.json")
        (r / "wake_protocol").write_text("runner-authored/v1")
        jw(r / "gates" / "g1.held.json", {"since": time.time() - 10})
        verdict = wf.notify(r, "gate.held", key="g1:hdefA", node="g1")
        check("owner-null twin: notify() writes NOTHING (no wake manufactured)",
              verdict == "skipped" and not (r / "wake.jsonl").exists(), str(verdict))

    # 2) the isolated sink stands in for the owner transport (test-sidecar hook)
    sink = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
    threading.Thread(target=sink.serve_forever, daemon=True).start()
    os.environ["WF_WAKE_SINK_PORT"] = str(sink.server_address[1])
    run = out / "runs"
    run_held(wf, wfcommon, a.seeds, run)
    run_failed_delta(wf, wfcommon, a.seeds, run)
    run_cascade(wf, wfcommon, a.seeds, run)
    sink.shutdown()
    run_nowhere_ever(wf, wfcommon, a.seeds, out / "runs-nowhere")
    sink_port = sink.server_address[1]

    # 3) harvest: receipts + manifest, so a cold reader re-derives every claim
    rec = out / "receipts"
    rec.mkdir(exist_ok=True)
    for cls in ("held", "failed_delta", "cascade"):
        shutil.copy(run / cls / "wake.jsonl", rec / f"{cls}.wake.jsonl")
    shutil.copy(out / "runs-nowhere" / "held" / "wake.jsonl", rec / "nowhere_ever.wake.jsonl")
    (rec / "sink.jsonl").write_text("".join(json.dumps(p) + "\n" for p in SINK_POSTS))
    jw(out / "manifest.json", {"head": a.head, "seeds": str(Path(a.seeds).resolve()),
                               "sink_port": sink_port, "sink_posts": len(SINK_POSTS),
                               "python": sys.version.split()[0],
                               "classes": ["held", "failed_delta", "cascade", "nowhere_ever"]})
    print("EXIT " + ("0" if ok else "1"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
