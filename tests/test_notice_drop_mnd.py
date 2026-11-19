#!/usr/bin/env python3
"""est-mnd / E11 — notice delivery misses are LOUD.

The measured failure: 'delivered=None, error no reachable api_server … the
owner had to poll for completion; the run looked silently orphaned from
outside.' Pinned here (observable outcomes):

  * accept: an admitted run whose owner stamp has no reachable route stamps
    notice_route.json {reachable:false, error_class:"missing_endpoint"},
    logs a typed notice.route events line, and prints a WORKFLOW_NOTICE_ROUTE
    line naming the drop risk BEFORE anything spawns;
  * miss: a later failed delivery appends a typed row (event, class, at, tid)
    to notice_drop.json in the run dir — visible to status — and prints
    WORKFLOW_NOTICE_DROP;
  * the terminal lifecycle line carries the miss next to the verdict:
    'WORKFLOW_DONE <run> notice_drop=missing_endpoint';
  * every miss class is typed (s47 delivery_miss_classified): missing
    endpoint -> missing_endpoint, HTTP 500 -> http_status;
  * ops-idempotent: a settled miss redrives to zero rows, zero markers,
    zero POSTs.

Run: cd tests && python3 test_notice_drop_mnd.py
"""
import http.server
import io
import json
import os
import shutil
import sys
import threading
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-mnd-drop"
os.environ["HERMES_HOME"] = str(HOME)          # no config.yaml: no reachable route
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
os.environ.pop("WF_WAKE_SINK_PORT", None)
os.environ.pop("API_SERVER_KEY", None)
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

def mk_run(name, nodes):
    r = RUNS / name
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": name, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"owner": {"session_id": "drop-mnd"}}))
    (r / "wake_protocol").write_text("runner-authored/v1")
    return r

NODES = [{"id": "g1", "type": "gate", "question": "q?", "options": ["y"]},
         {"id": "e", "type": "echo", "output": "x"}]

# ---------------- 1. accept: the route truth is stated at admission ----------------
r = mk_run("mnd-route", NODES)
buf = io.StringIO()
with redirect_stdout(buf):
    wf._notice_route_check(r)
out = buf.getvalue()
stamp = json.loads((r / "notice_route.json").read_text())
check("accepted run stamps its notice-route truth",
      stamp.get("reachable") is False and stamp.get("error_class") == "missing_endpoint",
      str(stamp))
check("the accepted-run stdout names the drop risk",
      "WORKFLOW_NOTICE_ROUTE" in out and "drop_risk=missing_endpoint" in out, out[:200])
evs = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
check("the route verdict is a typed events.jsonl line",
      any(e.get("event") == "notice.route" and e.get("error_class") == "missing_endpoint"
          for e in evs), str(evs))

# ---------------- 2. a later miss writes the run-dir marker ----------------
r = mk_run("mnd-miss", NODES)
buf = io.StringIO()
with redirect_stdout(buf):
    v = wf.notify(r, "gate.held", key="g1:abc", node="g1")
out = buf.getvalue()
w = [json.loads(l) for l in (r / "wake.jsonl").read_text().splitlines()]
check("nowhere-ever miss: the row is typed missing_endpoint",
      v is None and w[-1].get("delivered") is None
      and w[-1].get("error_class") == "missing_endpoint", f"{v} {w[-1]}")
drop = json.loads((r / "notice_drop.json").read_text())
check("the miss appends a typed marker row visible in status",
      drop["rows"][-1]["event"] == "gate.held"
      and drop["rows"][-1]["class"] == "missing_endpoint"
      and drop["rows"][-1].get("tid"), str(drop))
check("the miss is loud on the lifecycle channel",
      "WORKFLOW_NOTICE_DROP" in out and "missing_endpoint" in out, out[:200])
before = (r / "notice_drop.json").read_text()
v2 = wf.notify(r, "gate.held", key="g1:abc", node="g1")
check("ops-idempotent: a settled miss redrives with zero new rows or markers",
      v2 == "delivered" and (r / "notice_drop.json").read_text() == before
      and len(w) == len([json.loads(l) for l in (r / "wake.jsonl").read_text().splitlines()]),
      f"{v2}")

# ---------------- 3. the terminal line carries the miss next to the verdict --------
buf = io.StringIO()
with redirect_stdout(buf):
    wf.finalize(r, {"name": r.name, "nodes": NODES}, "done")
out = buf.getvalue()
check("WORKFLOW_DONE renders notice_drop=<class> next to the verdict",
      any(l.startswith("WORKFLOW_DONE ") and " notice_drop=missing_endpoint" in l
          for l in out.splitlines()), out[:400])

# ---------------- 4. a 500 answer classifies as http_status ----------------
POSTS = []
class Sink500(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        self.rfile.read(n)
        POSTS.append(1)
        self.send_response(500)
        self.end_headers()
        self.wfile.write(b"{}")
    def log_message(self, *a):
        pass

SRV = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Sink500)
threading.Thread(target=SRV.serve_forever, daemon=True).start()
os.environ["WF_WAKE_SINK_PORT"] = str(SRV.server_address[1])
try:
    r = mk_run("mnd-500", NODES)
    with redirect_stdout(io.StringIO()):
        v = wf.notify(r, "run.done", graph={"nodes": NODES})
    w = [json.loads(l) for l in (r / "wake.jsonl").read_text().splitlines()]
    drop = json.loads((r / "notice_drop.json").read_text())
    check("a 500 answer: undelivered with a typed http_status class on the row AND the marker",
          v == "undelivered" and w[-1].get("delivered") is False
          and w[-1].get("error_class") == "http_status"
          and drop["rows"][-1]["class"] == "http_status", f"{v} {drop}")
finally:
    del os.environ["WF_WAKE_SINK_PORT"]
    SRV.shutdown()

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
