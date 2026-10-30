#!/usr/bin/env python3
"""Native admission and legacy wake transport compatibility."""
import asyncio
import contextlib
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
    os.environ.pop(_k, None)  # hermetic: no inherited endpoint may steer the wake
FAKE_HOME = Path(tempfile.mkdtemp(prefix="wf-native-home-"))  # no config.yaml
os.environ["HERMES_HOME"] = str(FAKE_HOME)
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

tmp = Path(tempfile.mkdtemp(prefix="wf-native-"))


def mk_run(run_id, platform):
    r = tmp / run_id
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "run.json").write_text(json.dumps(
        {"concurrency": 1, "node_timeout": 60,
         "owner": {"session_id": STORED_SID if platform == "local" else f"{platform}-sid",
                   "ui_session_id": None, "platform": platform}}))
    return r


def ledger(r):
    p = r / "wake.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


STORED_SID = "local-native-wake-session"
ALLOWED_VERBS = {"session.resume", "prompt.submit", "prompt.receipt"}


class FakeRPCError(Exception):
    """Duck of gateway_client.GatewayRPCError: str() is the bounded reason code."""


class FakeClient:
    """Scripted native transport: method -> dict result, Exception, or fn(method,
    params) -> result (may raise). Records every call EXCEPT the never-wire
    _timeout knob, exactly like the real client."""

    def __init__(self, script):
        self.script = script
        self.calls = []

    async def rpc(self, method, **params):
        params.pop("_timeout", None)
        self.calls.append((method, dict(params)))
        action = self.script.get(method, {})
        if isinstance(action, BaseException):
            raise action
        if callable(action):
            return action(method, params)
        return action


def fake_connect(client, endpoints, tripwire=False):
    @contextlib.asynccontextmanager
    async def _ctx(endpoint):
        if tripwire:
            raise AssertionError("connect seam reached: absence must never attach/start")
        endpoints.append(endpoint)
        yield client
    return _ctx


def exact_sid_resume(store):
    def _resume(method, params):
        if params.get("session_id") != store:
            raise FakeRPCError("not_found")
        return {"session_id": store, "stored_session_id": store, "subscription_id": "sub-1", "pending": []}
    return _resume


def use_sink():
    os.environ["WF_WAKE_SINK_PORT"] = str(SINK_PORT)


def kill_sink():
    os.environ.pop("WF_WAKE_SINK_PORT", None)


try:
    nw = getattr(wf, "_native_wake", lambda: None)()   # graceful at the pre-fix head
    check("adapter seam: wf._native_wake() loads wake_native.py", nw is not None,
          repr(nw))
    if nw is None:
        print(f"\n{checks} checks, {failures} failures (adapter missing at baseline)")
        sys.exit(1)
    for attr in ("discover", "deliver", "_connect", "_admit"):
        check(f"adapter surface: wake_native.{attr}", callable(getattr(nw, attr, None)),
              repr(getattr(nw, attr, None)))

    _real_discover, _real_connect = nw.discover, nw._connect

    use_sink()
    eps = []
    client = FakeClient({
        "session.resume": exact_sid_resume(STORED_SID),
        "prompt.submit": {"admission_id": "adm-1", "status": "queued"},
        "prompt.receipt": {"admission_id": "adm-1", "status": "queued", "ref": {"session_id": STORED_SID}},
    })
    nw.discover = lambda home: "EP-SENTINEL"
    nw._connect = fake_connect(client, eps)
    r1 = mk_run("nv-1", "local")
    out = wf.notify(r1, "gate.held", key="g1")
    rows = ledger(r1)
    check("notify: native admission reports delivered", out == "delivered", repr(out))
    check("row: delivered=true with native protocol fields",
          len(rows) == 1 and rows[0].get("delivered") is True
          and rows[0].get("protocol") == "wake-native-admission/v1"
          and rows[0].get("admission_id") == "adm-1"
          and rows[0].get("native_status") == "queued", str(rows))
    check("legacy sink untouched by a native admission", len(posts) == 0, str(posts))
    check("discover-only: connect dialed the DISCOVERED endpoint (never None)",
          eps == ["EP-SENTINEL"], str(eps))
    methods = [m for m, _ in client.calls]
    check("protocol order: resume -> submit -> receipt",
          methods == ["session.resume", "prompt.submit", "prompt.receipt"], str(methods))
    submit = dict(client.calls[1][1])
    check("prompt.submit carries exact owner SID + the stable input_id (=tid)",
          submit.get("session_id") == STORED_SID and submit.get("input_id") == rows[0].get("id"),
          str(submit))
    check("prompt.submit is queued=True unattended=False (no bypass flags)",
          submit.get("queued") is True and submit.get("unattended") is False, str(submit))
    check("receipt readback asked for the returned admission_id",
          client.calls[2][1].get("admission_id") == "adm-1", str(client.calls[2]))
    check("ONLY the three wake verbs were ever dialed (no respond/resolve/bypass)",
          set(methods) <= ALLOWED_VERBS, str(methods))
    before1 = len(client.calls)
    wf.notify(r1, "gate.held", key="g1")                 # respawn re-drive
    check("settled native row: re-drive costs zero verbs, zero rows",
          len(client.calls) == before1 and len(ledger(r1)) == 1,
          f"calls={len(client.calls)} rows={ledger(r1)}")

    eps2 = []
    client2 = FakeClient({"session.resume": exact_sid_resume("some-OTHER-session")})
    nw._connect = fake_connect(client2, eps2)
    r2 = mk_run("nv-2", "local")                          # stamp carries STORED_SID
    out = wf.notify(r2, "gate.held", key="g1")
    rows = ledger(r2)
    check("wrong owner SID: not delivered, typed native_refused",
          out == "undelivered" and len(rows) == 1 and rows[0].get("delivered") is False
          and rows[0].get("error_class") == "native_refused", str(rows))
    check("refused wake FAILS CLOSED: the live sink got zero bypass POSTs",
          len(posts) == 0, str(posts))
    check("refusal never reached prompt.submit (resume gate held)",
          [m for m, _ in client2.calls] == ["session.resume"], str(client2.calls))

    client3 = FakeClient({"session.resume": FakeRPCError("permission_denied")})
    nw._connect = fake_connect(client3, [])
    r3 = mk_run("nv-3", "local")
    out = wf.notify(r3, "gate.held", key="g1")
    rows = ledger(r3)
    check("permission_denied: delivered=false + native_refused, sink untouched",
          out == "undelivered" and rows[0].get("delivered") is False
          and rows[0].get("error_class") == "native_refused" and len(posts) == 0,
          str(rows))

    attempts = {"n": 0}

    def flaky_submit(method, params):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise FakeRPCError("connection failed; turn outcome is unknown")
        return {"admission_id": "adm-4", "status": "queued"}
    client4 = FakeClient({
        "session.resume": exact_sid_resume(STORED_SID),
        "prompt.submit": flaky_submit,
        "prompt.receipt": {"admission_id": "adm-4", "status": "queued", "ref": {"session_id": STORED_SID}},
    })
    nw._connect = fake_connect(client4, [])
    r4 = mk_run("nv-4", "local")
    out = wf.notify(r4, "gate.held", key="g1")
    rows = ledger(r4)
    check("ambiguous transport failure is try-later (false, native_retry)",
          out == "undelivered" and rows[0].get("delivered") is False
          and rows[0].get("error_class") == "native_retry", str(rows))
    out = wf.notify(r4, "gate.held", key="g1")
    rows = ledger(r4)
    submits = [p for m, p in client4.calls if m == "prompt.submit"]
    check("re-drive converges to delivered", out == "delivered"
          and rows[-1].get("delivered") is True, str(rows))
    check("retry reused the STABLE input_id (both submits, equal to the row id)",
          len(submits) == 2 and submits[0].get("input_id") == submits[1].get("input_id")
          == rows[-1].get("id"), str(submits))

    client5 = FakeClient({
        "session.resume": exact_sid_resume(STORED_SID),
        "prompt.submit": {"admission_id": "adm-5", "status": "queued"},
        "prompt.receipt": {"admission_id": "adm-5", "status": "unknown", "ref": {"session_id": STORED_SID}},
    })
    nw._connect = fake_connect(client5, [])
    r5 = mk_run("nv-5", "local")
    out = wf.notify(r5, "gate.held", key="g1")
    rows = ledger(r5)
    check("submit queued but readback unknown: try-later, no delivered stamp",
          out == "undelivered" and rows[0].get("delivered") is False
          and rows[0].get("error_class") == "native_retry", str(rows))

    client6 = FakeClient({
        "session.resume": exact_sid_resume(STORED_SID),
        "prompt.submit": {"admission_id": "adm-6", "status": "started"},
        "prompt.receipt": {"admission_id": "adm-6", "status": "started", "ref": {"session_id": STORED_SID}},
    })
    nw._connect = fake_connect(client6, [])
    r6 = mk_run("nv-6", "local")
    out = wf.notify(r6, "gate.held", key="g1")
    rows = ledger(r6)
    check("started receipt readback = acceptance (not terminal completion)",
          out == "delivered" and rows[0].get("native_status") == "started", str(rows))

    client7 = FakeClient({
        "session.resume": lambda m, p: {"session_id": STORED_SID, "stored_session_id": STORED_SID, "subscription_id": "s",
                                        "pending": [{"prompt_id": "ap-1"}]},
        "prompt.submit": FakeRPCError("session_busy"),
    })
    nw._connect = fake_connect(client7, [])
    r7 = mk_run("nv-7", "local")
    out = wf.notify(r7, "gate.held", key="g1")
    rows = ledger(r7)
    verbs = {m for m, _ in client7.calls}
    check("approval-pending session: wake stays try-later",
          out == "undelivered" and rows[0].get("delivered") is False
          and rows[0].get("error_class") == "native_retry", str(rows))
    check("no approval-response/resolve verb was ever dialed (not bypassed)",
          all(v in ALLOWED_VERBS for v in verbs) and "session.respond" not in verbs,
          str(sorted(verbs)))

    nw.discover = lambda home: None
    trip = fake_connect(FakeClient({}), [], tripwire=True)   # absence must not connect
    nw._connect = trip
    r8 = mk_run("nv-8-sink", "local")
    before8 = len(posts)
    out = wf.notify(r8, "gate.held", key="g1")
    rows = ledger(r8)
    check("no ready gateway + sink: legacy POST delivers (unchanged)",
          out == "delivered" and rows[0].get("delivered") is True
          and len(posts) == before8 + 1 and "protocol" not in rows[0], str(rows))
    check("absent gateway: zero connect attempts — nothing was started",
          posts[-1]["session"] == STORED_SID, str(posts[-1]))
    kill_sink()
    r9 = mk_run("nv-9-nowhere", "local")
    out = wf.notify(r9, "gate.held", key="g1")
    rows = ledger(r9)
    check("no gateway + no sink: nowhere-ever missing_endpoint (unchanged)",
          out is None and rows[0].get("delivered") is None
          and rows[0].get("error_class") == "missing_endpoint", str(rows))
    use_sink()

    nw.discover = lambda home: (_ for _ in ()).throw(
        AssertionError("native discover reached for an api_server owner"))
    r10 = mk_run("nv-10-apiserver", "api_server")
    before10 = len(posts)
    out = wf.notify(r10, "gate.held", key="g1")
    rows = ledger(r10)
    check("api_server owner: legacy route intact, native seam never consulted",
          out == "delivered" and rows[0].get("delivered") is True
          and len(posts) == before10 + 1, str(rows))

    use_sink()
    before_broken = len(posts)
    wf._WAKE_NATIVE = None
    wf._WAKE_NATIVE_TRIED = True
    broken = mk_run("nv-broken-module", "local")
    broken_result = wf.notify(broken, "gate.held", key="g1")
    broken_rows = ledger(broken)
    check("unloadable native adapter cannot bypass through legacy HTTP",
          broken_result == "undelivered" and len(posts) == before_broken
          and broken_rows[0].get("error_class") == "native_retry", str(broken_rows))
    wf._WAKE_NATIVE = nw

finally:
    with contextlib.suppress(Exception):
        nw.discover, nw._connect = _real_discover, _real_connect
    srv.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(FAKE_HOME, ignore_errors=True)

print(f"\n{checks} checks, {failures} failures")
sys.exit(1 if failures else 0)
