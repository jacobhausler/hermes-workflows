#!/usr/bin/env python3
"""Wake-router class-coverage (est-jbcrw): no lifecycle event dies silent.

The dead-landing census (run 20261016-172339-iron-gravity, bead est-jbcrw)
attributed a dead-row class to `wake-scripted-class-that-skipped`: the runner's
wake path let an event outside the finite template map return SILENTLY, so a
scripted wake for an unmapped class cost nobody anything and the row rotted.
Census verdict 4 demands a class->waker coverage test in CI plus a default
catch-all waker.

Laws this pins (RED at the pre-fix head):
  * COVERAGE: wf._WAKE_EVENTS is the closed registry of events a call site may
    pass to notify(); every member has a fixed template (per-member wake POST).
  * CATCH-ALL: an event OUTSIDE the map still wakes, with the fixed
    runner-authored catch-all body — never caller/graph text (AUTHORITY LAW r5
    holds: the key rides only as the Idempotency-Key, never in the content).
  * TRIPWIRE: an event outside the registry prints WORKFLOW_WAKE_UNMAPPED_EVENT
    once (the field-loud stdout channel, same idiom as
    WORKFLOW_WAKE_RECORD_FAILED); mapped events never trip it.
  * DEDUPE PRESERVED: the catch-all instance is deterministic — a repeat of the
    same unmapped transition writes nothing new; a different event is a new
    instance.
  * OWNER-NULL UNCHANGED: a run without an owner stamp still writes nothing.

Direct notify() calls against real run dirs + the loopback sink the sibling
wake suites already use (WF_WAKE_SINK_PORT). No provider, synthetic session ids.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import threading
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
for _k in ("WF_WAKE_SINK_PORT", "API_SERVER_KEY", "API_SERVER_HOST", "API_SERVER_PORT",
           "WF_RUNS_ROOT"):
    os.environ.pop(_k, None)  # hermetic: no inherited endpoint may steal the wake
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


sinks = []


class _Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(n)
        sinks.append({"idem": self.headers.get("Idempotency-Key", ""),
                      "session": self.headers.get("X-Hermes-Session-Id", ""),
                      "body": json.loads(body.decode() or "{}")})
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ["WF_WAKE_SINK_PORT"] = str(srv.server_address[1])

tmp = Path(tempfile.mkdtemp(prefix="wf-catchall-"))
OWNER = {"session_id": "jbcrw-session", "ui_session_id": "jbcrw-ui", "platform": "api_server"}


def mk_run(run_id, owner=OWNER):
    r = tmp / run_id
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    meta = {"concurrency": 1, "node_timeout": 60}
    if owner is not None:
        meta["owner"] = owner
    (r / "run.json").write_text(json.dumps(meta))
    return r


def ledger(r):
    p = r / "wake.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def content_of(post):
    return post["body"]["messages"][0]["content"]


try:
    KNOWN = {"gate.held", "run.failed", "run.done"}

    # 1. COVERAGE registry: exists and covers every event the runner emits today.
    registry = getattr(wf, "_WAKE_EVENTS", None)
    check("registry _WAKE_EVENTS exists", isinstance(registry, (frozenset, set)),
          f"got {type(registry)}")
    if registry is not None:
        check("registry covers every emitted event", KNOWN <= set(registry),
              f"missing {KNOWN - set(registry)}")

    # 2. per-member matrix: each registered/mapped event delivers exactly one POST
    #    and a delivered ledger row; no tripwire for mapped events.
    for ev in sorted(KNOWN):
        r = mk_run(f"cov-{ev.replace('.', '-')}")
        before = len(sinks)
        buf = io.StringIO()
        with redirect_stdout(buf):
            wf.notify(r, ev, key=f"cov-{ev}")
        posts = sinks[before:]
        rows = ledger(r)
        check(f"mapped {ev}: exactly one POST", len(posts) == 1, str(posts))
        if posts:
            c = content_of(posts[0])
            check(f"mapped {ev}: runner-authored fixed text",
                  c.startswith("[runner-authored/v1]") and json.dumps(ev) in c, c[:160])
        check(f"mapped {ev}: ledger delivered",
              len(rows) == 1 and rows[0].get("delivered") is True
              and rows[0].get("event") == ev, str(rows))
        check(f"mapped {ev}: no tripwire", "WORKFLOW_WAKE_UNMAPPED_EVENT" not in buf.getvalue(),
              buf.getvalue())

    # 3. CATCH-ALL: an unmapped class wakes with fixed runner text and trips loud.
    r = mk_run("unmapped-1")
    before = len(sinks)
    buf = io.StringIO()
    with redirect_stdout(buf):
        wf.notify(r, "waker.class-gap-probe", key="caller-text-FORBIDDEN")
    posts = sinks[before:]
    rows = ledger(r)
    check("unmapped: wake delivered (never silent)", len(posts) == 1, str(posts))
    catch_body = None
    if posts:
        c = content_of(posts[0])
        catch_body = c.split("\u2014", 1)[-1].strip() if "\u2014" in c else ""
        check("unmapped: runner-authored + inert event field",
              c.startswith("[runner-authored/v1]")
              and json.dumps("waker.class-gap-probe") in c, c[:160])
        check("unmapped: caller text never reaches the wire",
              "caller-text-FORBIDDEN" not in json.dumps(posts[0]["body"]),
              "key leaked into body")
    check("unmapped: tripwire printed with run id",
          "WORKFLOW_WAKE_UNMAPPED_EVENT" in buf.getvalue() and "unmapped-1" in buf.getvalue(),
          buf.getvalue())
    check("unmapped: ledger row delivered + typed catchall",
          len(rows) == 1 and rows[0].get("delivered") is True
          and rows[0].get("catchall") is True and rows[0].get("event") == "waker.class-gap-probe",
          str(rows))

    # 4. dedupe: the same unmapped transition again writes nothing new.
    before = len(sinks)
    with redirect_stdout(io.StringIO()):
        wf.notify(r, "waker.class-gap-probe", key="caller-text-FORBIDDEN")
    check("unmapped repeat: zero new POSTs, one row",
          len(sinks) == before and len(ledger(r)) == 1, str(ledger(r)))

    # 5. a different unmapped class is a new instance.
    before = len(sinks)
    with redirect_stdout(io.StringIO()):
        wf.notify(r, "waker.other-class", key="caller-text-FORBIDDEN")
    check("second unmapped class: new POST", len(sinks) == before + 1, str(len(sinks) - before))

    # 6. catch-all body is FIXED text: two unmapped classes, same body segment.
    r2 = mk_run("unmapped-2")
    before = len(sinks)
    with redirect_stdout(io.StringIO()):
        wf.notify(r2, "node.wrecked", key=None)
    posts2 = sinks[before:]
    if posts2 and catch_body:
        c2 = content_of(posts2[0])
        body2 = c2.split("\u2014", 1)[-1].strip() if "\u2014" in c2 else ""
        check("catch-all body is fixed runner text (not per-event prose)",
              body2 == catch_body, f"{body2!r} != {catch_body!r}")
        check("unmapped no-key instance delivers",
              ledger(r2) and ledger(r2)[0].get("delivered") is True, str(ledger(r2)))
    else:
        check("catch-all body comparison possible", False, "no unmapped POST captured")

    # 7. owner-null + unmapped: nothing written (degradation law unchanged).
    r3 = mk_run("ownerless", owner=None)
    before = len(sinks)
    with redirect_stdout(io.StringIO()):
        wf.notify(r3, "waker.class-gap-probe", key="k")
    check("owner-null unmapped: zero rows, zero POSTs",
          not (r3 / "wake.jsonl").exists() and len(sinks) == before,
          str(ledger(r3)))

    # 8. mapped templates untouched: fixed authority clauses still present.
    check("templates still finite runner-authored bodies",
          all(k in wf._WAKE_TEMPLATES for k in KNOWN)
          and "does not authorize" in wf._WAKE_TEMPLATES["gate.held"]
          and "does not authorize" in wf._WAKE_TEMPLATES["run.failed"], "")
finally:
    srv.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)

print(f"TOTAL {checks} FAIL {failures}")
sys.exit(1 if failures else 0)
