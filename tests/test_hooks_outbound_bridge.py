#!/usr/bin/env python3
"""P1 outbound bridge — the webhook mirror of typed lifecycle transitions.
Laws pinned (spec P1):
 1. ENABLED-OFF byte-identical: with the setting absent (and no carrier), notify()
    touches exactly the files it always touched — no outbound.jsonl, no
    events.jsonl delta, wake.jsonl unchanged.
 2. IDENTITY REUSE: the outbound Idempotency-Key IS wake.jsonl's own instance id
    for the same transition (one identity, sha256(run|event|discriminant)); the
    bridge never mints a second one.
 3. DEDUPE ON RETRY: a delivered instance re-notified POSTs nothing, rows nothing.
 4. FAIL-OPEN ON ENDPOINT DEATH: an undelivered attempt raises NOTHING into the
    caller, records a typed outbound.failed line in events.jsonl + an undelivered
    probe row, and the retry re-drives under the SAME Idempotency-Key once the
    endpoint returns (redaction: the bearer never reaches disk).
 5. FAIL-CLOSED CONFIG: a refused url POSTs nothing and records typed config
    rows; operator `enabled: false` is a floor no per-run carrier can re-arm;
    carriers (run.json / graph meta) may opt in against an operator url.
 6. EVENT FILTER: a present filter skips non-matching transitions without any
    row or attempt.
 7. DURABLE CACHE + OWNER-NULL: the delivered set lives in outbound.jsonl, NOT in
    process memory — a fresh interpreter re-notifying a DELIVERED instance POSTs
    nothing and still ships a genuinely new instance; an owner-null run mirrors
    too (the endpoint is the operator's, not the session's).
Run: python3 tests/test_hooks_outbound_bridge.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT / "home-ho-p1"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
os.environ.pop("WF_WAKE_SINK_PORT", None)   # wake must stay endpoint-less here
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("wf_ho_p1", ROOT / "wf.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

# The sanctioned owner-settings seam (same one the door installs): this rig
# answers outbound_bridge directly and NO_READER for everything else, so the
# raw config.yaml fallback stays wfcommon's own untouched path.
_CFG: dict = {"outbound_bridge": None}

def _reader(key):
    if key == "outbound_bridge":
        v = _CFG["outbound_bridge"]
        return wf.wfcommon.NO_READER if v is None else v
    return wf.wfcommon.NO_READER

wf.wfcommon.set_owner_setting_reader(_reader)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

GRAPH = {"name": "ho-p1", "nodes": [{"id": "one", "type": "agent", "goal": "offline"}]}
BEARER = "tok-ho-1"

def mk_run(rid, owner="ho-session", run_extra=None, graph=None):
    r = HOME / "workflows" / rid
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps(graph if graph is not None else GRAPH))
    meta = {"hermes_bin": "/bin/false", "name": "ho-p1"}
    if owner is not None:
        meta["owner"] = {"session_id": owner}
    if run_extra:
        meta.update(run_extra)
    (r / "run.json").write_text(json.dumps(meta))
    return r

def jl(path):
    try:
        return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    except FileNotFoundError:
        return []

# ---------- the sink (the ONLY network the bridge is allowed to see) ----------
class _Sink(BaseHTTPRequestHandler):
    mode = "ok"
    hits = []

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        _Sink.hits.append({"headers": dict(self.headers), "body": body})
        if _Sink.mode == "err500":
            self.send_response(500)
        elif _Sink.mode == "redirect":
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.1:1/away")
        else:
            self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass

_srv = [None]

def sink_start():
    _srv[0] = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
    threading.Thread(target=_srv[0].serve_forever, daemon=True).start()
    return _srv[0].server_address[1]

def sink_stop():
    _srv[0].shutdown()
    _srv[0].server_close()

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)

try:
    # ---- 1: enabled-OFF is byte-identical ----------------------------------
    r = mk_run("ho-off", owner=None)
    wf.notify(r, "run.done", graph=GRAPH)
    check("off+owner-null: wake silent AND no outbound artifacts",
          not (r / "wake.jsonl").exists() and not (r / "outbound.jsonl").exists()
          and not (r / "events.jsonl").exists())
    wf.notify(r, "run.failed", key="k1", graph=GRAPH)
    r2 = mk_run("ho-off-2")
    wf.notify(r2, "run.failed", key="k1", graph=GRAPH)
    wf.notify(r2, "run.failed", key="k1", graph=GRAPH)
    check("off+owner: wake ledger at-most-once (missing_endpoint settles: one row, no re-drive)",
          len(jl(r2 / "wake.jsonl")) == 1
          and jl(r2 / "wake.jsonl")[0].get("error_class") == "missing_endpoint")
    check("off: zero outbound rows, zero events lines, no outbound file at all",
          not (r2 / "outbound.jsonl").exists() and not (r2 / "events.jsonl").exists())

    # ---- 2: ON — delivery, identity reuse, delivered-cache dedupe -----------
    port = sink_start()
    _CFG["outbound_bridge"] = {"enabled": True, "bearer": BEARER,
                               "url": f"http://127.0.0.1:{port}/hook", "timeout_s": 5}
    r3 = mk_run("ho-on")
    wf.notify(r3, "run.done", graph=GRAPH)
    rows = jl(r3 / "outbound.jsonl")
    wake = jl(r3 / "wake.jsonl")
    check("on: exactly one POST, one probe row delivered",
          len(_Sink.hits) == 1 and len(rows) == 1 and rows[0].get("delivered") is True,
          json.dumps(rows)[:200])
    check("identity reuse: Idempotency-Key == wake's own instance id (ONE identity)",
          _Sink.hits and wake and rows
          and _Sink.hits[0]["headers"].get("Idempotency-Key") == wake[-1]["id"] == rows[0]["id"])
    body = json.loads(_Sink.hits[0]["body"]) if _Sink.hits else {}
    check("wire envelope: schema/run/event/instance ride; bearer header present",
          body.get("schema") == "wf-outbound/v1" and body.get("event") == "run.done"
          and body.get("run_id") == r3.name and body.get("instance") == rows[0].get("id")
          and _Sink.hits[0]["headers"].get("Authorization") == f"Bearer {BEARER}")
    wf.notify(r3, "run.done", graph=GRAPH)
    check("dedupe: retry of a DELIVERED instance POSTs nothing, rows nothing",
          len(_Sink.hits) == 1 and len(jl(r3 / "outbound.jsonl")) == 1)
    wf.notify(r3, "gate.held", key="gA:def1", graph=GRAPH)
    check("a genuinely new instance (gate.held) mints a fresh id and ships",
          len(_Sink.hits) == 2
          and _Sink.hits[1]["headers"].get("Idempotency-Key")
          != _Sink.hits[0]["headers"].get("Idempotency-Key"))

    # ---- 4: fail-open — endpoint answers 500, then dies, then revives -------
    _Sink.mode = "err500"
    r4 = mk_run("ho-500")
    before = len(_Sink.hits)
    try:
        wf.notify(r4, "run.failed", key="boom", graph=GRAPH)
        no_raise = True
    except Exception as e:
        no_raise = False
    check("fail-open: a 500 never raises into the caller", no_raise)
    fails = [x for x in jl(r4 / "events.jsonl") if x.get("event") == "outbound.failed"]
    check("failure records a typed outbound.failed line in events.jsonl",
          len(_Sink.hits) == before + 1 and len(fails) == 1
          and fails[0].get("error_class") == "http_status"
          and fails[0].get("out_event") == "run.failed", json.dumps(fails)[:200])
    check("undelivered attempt rides the probe ledger too",
          jl(r4 / "outbound.jsonl")[-1].get("delivered") is False)
    _Sink.mode = "ok"
    sink_stop()
    r5 = mk_run("ho-dead")
    try:
        wf.notify(r5, "run.failed", key="dead", graph=GRAPH)
        no_raise = True
    except Exception:
        no_raise = False
    dead_rows = [x for x in jl(r5 / "events.jsonl") if x.get("event") == "outbound.failed"]
    check("endpoint death: refused connection is typed transport, fail-open, no POST seen",
          no_raise and len(dead_rows) == 1 and dead_rows[0].get("error_class") == "transport")
    disk = (r5 / "events.jsonl").read_text() + (r5 / "outbound.jsonl").read_text()
    check("bearer NEVER reaches disk (redaction net)", BEARER not in disk)
    port2 = sink_start()   # same-port rebind is NOT guaranteed — re-point the setting
    _CFG["outbound_bridge"]["url"] = f"http://127.0.0.1:{port2}/hook"
    hits_before = len(_Sink.hits)
    wf.notify(r5, "run.failed", key="dead", graph=GRAPH)
    after = jl(r5 / "outbound.jsonl")
    check("revival: retry re-drives the UNDELIVERED instance under the SAME id, now delivered",
          len(_Sink.hits) == hits_before + 1 and len(after) == 2
          and after[0]["id"] == after[1]["id"] and after[1].get("delivered") is True
          and _Sink.hits[-1]["headers"].get("Idempotency-Key") == after[1]["id"])
    _Sink.mode = "redirect"
    r6 = mk_run("ho-redirect")
    wf.notify(r6, "gate.held", key="gR:d", graph=GRAPH)
    red = jl(r6 / "outbound.jsonl")[-1]
    check("redirect law: 30x is NOT a delivery, never followed, typed undelivered",
          red.get("delivered") is False and red.get("error_class") == "redirect")
    _Sink.mode = "ok"

    # ---- 5: fail-closed config ----------------------------------------------
    _CFG["outbound_bridge"] = {"enabled": True, "url": "http://203.0.113.9/hook"}
    hits_before = len(_Sink.hits)
    r7 = mk_run("ho-refuse")
    wf.notify(r7, "run.done", graph=GRAPH)
    cfg_rows = [x for x in jl(r7 / "events.jsonl") if x.get("event") == "outbound.failed"]
    check("plaintext non-loopback url: refused, typed config row, zero POSTs",
          len(_Sink.hits) == hits_before and len(cfg_rows) == 1
          and cfg_rows[0].get("error_class") == "config")
    _CFG["outbound_bridge"] = False            # operator floor
    r8 = mk_run("ho-floor", run_extra={"outbound_bridge": {"enabled": True}})
    hits_before = len(_Sink.hits)
    wf.notify(r8, "run.done", graph=GRAPH)
    check("operator false is a carrier-proof floor: no rows, no lines, no POSTs",
          len(_Sink.hits) == hits_before and not (r8 / "outbound.jsonl").exists()
          and not (r8 / "events.jsonl").exists())
    _CFG["outbound_bridge"] = None             # settings absent, carrier opts in, no url
    r9 = mk_run("ho-carrier-nourl", run_extra={"outbound_bridge": {"enabled": True}})
    wf.notify(r9, "run.done", graph=GRAPH)
    nourl = [x for x in jl(r9 / "events.jsonl") if x.get("event") == "outbound.failed"]
    check("carrier opt-in with NO operator url: typed config refusal, never silence",
          len(nourl) == 1 and nourl[0].get("error_class") == "config")
    _CFG["outbound_bridge"] = {"url": f"http://127.0.0.1:{port2}/hook", "bearer": BEARER}
    gmeta = dict(GRAPH, meta={"outbound_bridge": {"enabled": True}})
    r10 = mk_run("ho-gmeta", graph=gmeta)
    hits_before = len(_Sink.hits)
    wf.notify(r10, "run.done", graph=GRAPH)
    check("graph meta.outbound_bridge opts the run in against the operator url",
          len(_Sink.hits) == hits_before + 1
          and jl(r10 / "outbound.jsonl")[-1].get("delivered") is True)

    # ---- 4b: redaction seam — a stdlib error carrying the bearer ------------
    _CFG["outbound_bridge"] = {"enabled": True, "url": f"http://127.0.0.1:{port2}/hook",
                               "bearer": BEARER}
    ho = wf._outbound_bridge()
    real_post = ho._post
    def _boom(url, body, headers, timeout):
        raise ValueError("Invalid header value b'Bearer " + BEARER + "'")
    ho._post = _boom
    try:
        r11 = mk_run("ho-redact")
        wf.notify(r11, "gate.held", key="gX:d", graph=GRAPH)
        rows = jl(r11 / "outbound.jsonl") + jl(r11 / "events.jsonl")
        blob = json.dumps(rows)
        check("generic stdlib death is typed transport and the bearer is [redacted] on disk",
              rows and all(x.get("error_class") == "transport" for x in rows)
              and "[redacted]" in blob and BEARER not in blob, blob[:200])
    finally:
        ho._post = real_post

    # ---- 6: event filter ------------------------------------------------------
    _CFG["outbound_bridge"] = {"enabled": True, "url": f"http://127.0.0.1:{port2}/hook",
                               "events": ["gate.*"]}
    r12 = mk_run("ho-filter")
    hits_before = len(_Sink.hits)
    wf.notify(r12, "run.done", graph=GRAPH)
    check("filter: a non-matching transition is skipped — no POST, no row, no line",
          len(_Sink.hits) == hits_before and not (r12 / "outbound.jsonl").exists()
          and not (r12 / "events.jsonl").exists())
    wf.notify(r12, "gate.held", key="gF:d", graph=GRAPH)
    check("filter: a matching transition ships", len(_Sink.hits) == hits_before + 1)

    # ---- 7: the cache is DISK, not memory + owner-null mirrors -----------------
    _CFG["outbound_bridge"] = {"enabled": True, "url": f"http://127.0.0.1:{port2}/hook",
                               "bearer": BEARER, "timeout_s": 5}
    child = HOME / "child_mirror.py"          # a stand-in for a respawned runner
    child.write_text(
        "import importlib.util, json, os, pathlib\n"
        "root = pathlib.Path(os.environ['HO_ROOT'])\n"
        "sp = importlib.util.spec_from_file_location('wf_ho_child', root / 'wf.py')\n"
        "wf = importlib.util.module_from_spec(sp); sp.loader.exec_module(wf)\n"
        "cfg = {'enabled': True, 'url': os.environ['HO_URL'], 'bearer': os.environ['HO_BEARER'],\n"
        "       'timeout_s': 5}\n"
        "wf.wfcommon.set_owner_setting_reader(\n"
        "    lambda k: cfg if k == 'outbound_bridge' else wf.wfcommon.NO_READER)\n"
        "run = pathlib.Path(os.environ['HO_RUN'])\n"
        "wf.notify(run, 'gate.held', key=os.environ['HO_KEY'],\n"
        "          graph=json.loads((run / 'graph.json').read_text()))\n")
    r13 = mk_run("ho-xproc", owner=None)      # owner-null: no session to wake
    hits_before = len(_Sink.hits)
    wf.notify(r13, "gate.held", key="gP:d", graph=GRAPH)
    check("owner-null run still mirrors: the endpoint is the operator's, not the session's",
          len(_Sink.hits) == hits_before + 1
          and jl(r13 / "outbound.jsonl")[-1].get("delivered") is True)
    cenv = dict(os.environ, HO_ROOT=str(ROOT), HO_URL=f"http://127.0.0.1:{port2}/hook",
                HO_BEARER=BEARER, HO_RUN=str(r13), HO_KEY="gP:d")
    cp = subprocess.run([sys.executable, str(child)], env=cenv, capture_output=True, timeout=90)
    check("dedupe survives respawn: a zero-memory process re-notifying a DELIVERED "
          "instance POSTs nothing, rows nothing (cache = outbound.jsonl)",
          cp.returncode == 0 and len(_Sink.hits) == hits_before + 1
          and len(jl(r13 / "outbound.jsonl")) == 1,
          (cp.stderr.decode()[:200] if cp.returncode else ""))
    cp2 = subprocess.run([sys.executable, str(child)],
                         env=dict(cenv, HO_KEY="gQ:d"), capture_output=True, timeout=90)
    rows13 = jl(r13 / "outbound.jsonl")
    check("the cache never blocks a live transition: a new instance from a fresh "
          "process ships and lands a second row",
          cp2.returncode == 0 and len(_Sink.hits) == hits_before + 2 and len(rows13) == 2
          and rows13[0]["id"] != rows13[1]["id"] and rows13[1].get("delivered") is True,
          (cp2.stderr.decode()[:200] if cp2.returncode else ""))

finally:
    if _srv[0] is not None:
        try:
            sink_stop()
        except Exception:
            pass
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
