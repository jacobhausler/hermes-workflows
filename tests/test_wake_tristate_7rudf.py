#!/usr/bin/env python3
"""Tri-state wake delivery + at-most-once markers (est-7rudf, peer atbrace:hw-0e2).

The flattened-bool failure mode: the wake sender recorded "no endpoint at all"
with the SAME `delivered: false` as "endpoint answered 500". One bool cannot tell
a retryable miss from a permanent nowhere, so every respawn of a decided
transition re-POSTed a delivery that could never land, and the ledger grew a
row per attempt forever. The peer audit's convergence (iw-recon
notify_sender.py:29-43,69-93 + engine.py:871-967, SYNTHESIS.md #10): the sender
returns True/False/None = delivered / try-later / nowhere-ever, and the
once-per-transition marker persists only on True-or-None. A headless no-op
never stamps delivered; a nowhere-ever transition settles instead of
re-driving.

Laws this pins (RED at the pre-fix head):
  * TRI-STATE SENDER: wf._wake_deliver returns True on a 2xx, False on a
    transient failure (HTTP status, redirect, timeout, transport error), None
    when the host configures no reachable API server at all.
  * TRI-STATE ROW: the wake.jsonl row mirrors it - delivered true/false/null -
    and a null row is never a delivered stamp; error_class stays the typed
    missing_endpoint.
  * AT-MOST-ONCE ON True-or-None: a re-drive (the respawn shape: a fresh
    process re-calling notify() over the SAME ledger) writes zero rows and
    fires zero POSTs for a delivered instance AND for a nowhere-ever instance.
  * TRY-LATER KEEPS ITS PATH: a false row does not settle the instance; the
    next re-drive POSTs again and the row converges to true.
  * MARKER RULE IS HERMETIC: rows without an id or without the delivered key
    never settle anything (the ledger parse stays fail-open on legacy shapes).

Direct notify()/_wake_deliver calls against real run dirs + the loopback sink
the sibling wake suites use (WF_WAKE_SINK_PORT). No provider, synthetic ids.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
for _k in ("WF_WAKE_SINK_PORT", "API_SERVER_KEY", "API_SERVER_HOST", "API_SERVER_PORT",
           "WF_RUNS_ROOT"):
    os.environ.pop(_k, None)  # hermetic: no inherited endpoint may steal the wake
EMPTY_HOME = Path(tempfile.mkdtemp(prefix="wf-7rudf-home-"))  # no config.yaml -> no endpoint
os.environ["HERMES_HOME"] = str(EMPTY_HOME)
import wf  # noqa: E402

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


posts = []
MODE = {"code": 202}


class _Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(n)
        posts.append({"idem": self.headers.get("Idempotency-Key", ""),
                      "session": self.headers.get("X-Hermes-Session-Id", ""),
                      "body": json.loads(body.decode() or "{}")})
        self.send_response(MODE["code"])
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
threading.Thread(target=srv.serve_forever, daemon=True).start()
SINK_PORT = srv.server_address[1]

tmp = Path(tempfile.mkdtemp(prefix="wf-tristate-"))
OWNER = {"session_id": "7rudf-session", "ui_session_id": "7rudf-ui", "platform": "api_server"}


def mk_run(run_id):
    r = tmp / run_id
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "run.json").write_text(json.dumps({"concurrency": 1, "node_timeout": 60,
                                            "owner": OWNER}))
    return r


def ledger(r):
    p = r / "wake.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def use_sink():
    os.environ["WF_WAKE_SINK_PORT"] = str(SINK_PORT)


def kill_endpoint():
    os.environ.pop("WF_WAKE_SINK_PORT", None)


try:
    # ---- 1. TRI-STATE SENDER: the return value itself is the contract -------
    use_sink()
    MODE["code"] = 202
    deliver = getattr(wf, "_wake_deliver", None)
    check("sender seam exists (wf._wake_deliver)", callable(deliver), repr(deliver))
    if callable(deliver):
        r1 = mk_run("ts-1")
        ok = deliver({}, "s", "t", "tid-2xx")
        MODE["code"] = 503
        late = deliver({}, "s", "t", "tid-5xx")
        kill_endpoint()
        nowhere = deliver({}, "s", "t", "tid-none")
        check("sender: 2xx -> True (delivered)", ok is True, repr(ok))
        check("sender: 503 -> False (try-later)", late is False, repr(late))
        check("sender: no endpoint -> None (nowhere-ever)", nowhere is None, repr(nowhere))
    MODE["code"] = 202

    # ---- 2. TRI-STATE ROW: the ledger mirrors the outcome, null != delivered -
    r2 = mk_run("ts-2")
    use_sink()
    MODE["code"] = 503
    before2 = len(posts)
    wf.notify(r2, "gate.held", key="g1")
    rows = ledger(r2)
    check("row: transient attempt is delivered=false + error",
          len(rows) == 1 and rows[0].get("delivered") is False
          and rows[0].get("error"), str(rows))
    MODE["code"] = 202
    wf.notify(r2, "gate.held", key="g1")          # redrive: the retry path exists
    rows = ledger(r2)
    check("row: redrive after transient converges to delivered=true",
          len(rows) == 2 and rows[1].get("delivered") is True
          and len(posts) == before2 + 2, str(rows))

    r3 = mk_run("ts-3")
    kill_endpoint()
    before3 = len(posts)
    wf.notify(r3, "gate.held", key="g1")
    rows = ledger(r3)
    check("row: nowhere attempt is delivered=null, never a true stamp",
          len(rows) == 1 and rows[0].get("delivered") is None
          and all(x.get("delivered") is not True for x in rows), str(rows))
    check("row: nowhere attempt keeps the typed error_class + zero wire traffic",
          rows[0].get("error_class") == "missing_endpoint" and len(posts) == before3,
          str(rows))

    # ---- 3. AT-MOST-ONCE: restart redrive does not double-notice -------------
    r4 = mk_run("ts-4-nowhere")
    kill_endpoint()
    before4 = len(posts)
    wf.notify(r4, "gate.held", key="g1")
    wf.notify(r4, "gate.held", key="g1")           # respawn re-drive, same decision
    rows = ledger(r4)
    check("nowhere marker persists: restart redrive writes no second row",
          len(rows) == 1, str(rows))
    check("nowhere marker persists: restart redrive fires zero POSTs",
          len(posts) == before4, str(posts))

    r5 = mk_run("ts-5-delivered")
    (r5 / "graph.json").write_text(json.dumps(
        {"name": "ts-5-delivered", "nodes": [{"id": "a", "type": "echo", "output": "x"}]}))
    use_sink()
    MODE["code"] = 202
    before5 = len(posts)
    wf.notify(r5, "run.done")
    rows = ledger(r5)
    check("delivered row recorded",
          len(rows) == 1 and rows[0].get("delivered") is True, str(rows))
    wf.notify(r5, "run.done")                      # respawn re-drive, same decision
    rows = ledger(r5)
    check("delivered marker persists: restart redrive not double-noticing",
          len(rows) == 1 and len(posts) == before5 + 1, f"rows={rows} posts={len(posts)}")

    # ---- 4. MARKER RULE HERMETIC: only explicit true/null rows settle --------
    r6 = mk_run("ts-6")
    (r6 / "wake.jsonl").write_text(
        json.dumps({"id": "legacy-no-delivered-key", "event": "gate.held"}) + "\n"
        + json.dumps({"delivered": None}) + "\n"          # null row without an id
        + "not json\n")
    _rows, settled6 = wf._wake_ledger_read(r6)
    check("marker rule: legacy no-key row and id-less null row settle nothing",
          settled6 == set(), str(settled6))
    (r6 / "wake.jsonl").write_text(
        json.dumps({"id": "n1", "delivered": None}) + "\n"
        + json.dumps({"id": "n2", "delivered": False}) + "\n"
        + json.dumps({"id": "n3", "delivered": True}) + "\n")
    _rows, settled6b = wf._wake_ledger_read(r6)
    check("marker rule: settles on True-or-None only",
          settled6b == {"n1", "n3"}, str(settled6b))

    print(f"\n{checks} checks, {failures} failures")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(EMPTY_HOME, ignore_errors=True)

sys.exit(1 if failures else 0)
