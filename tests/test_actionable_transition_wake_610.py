#!/usr/bin/env python3
"""Committed failures wake before sibling drain; steering and amend stay cooperative."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
FAILS = []


def check(label, condition, detail=""):
    print(("PASS " if condition else "FAIL ") + label + (f" {detail}" if not condition else ""), flush=True)
    if not condition:
        FAILS.append(label)


def read(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def rows(path):
    try:
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    except (OSError, ValueError):
        return []


def until(fn, timeout=30):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(0.02)
    raise AssertionError("observation deadline expired")


wake = threading.Event()
posts = []


class Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        posts.append((self.headers.get("Idempotency-Key"), body))
        if 'event="node.action_required"' in json.dumps(body).replace('\\"', '"'):
            wake.set()
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args):
        pass


with tempfile.TemporaryDirectory(prefix="wf-transition-") as tmp:
    home = Path(tmp)
    runs = home / "workflows"
    env = dict(os.environ)
    for key in ("API_SERVER_KEY", "API_SERVER_HOST", "API_SERVER_PORT", "HERMES_WF_STEER_FILE", "HERMES_WF_STEER_CURSOR"):
        env.pop(key, None)
        os.environ.pop(key, None)
    os.environ.update(HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs))
    (home / "config.yaml").write_text("model:\n  default: test-model\n")
    door = importlib.import_module("__init__")
    import wf_test_isolation
    wf_test_isolation.install(door)
    door._ping_route_once = lambda p, m: {"liveness": "unknown"}
    server = ThreadingHTTPServer(("127.0.0.1", 0), Sink)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env.update(HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
               WF_WAKE_SINK_PORT=str(server.server_port), FAKE_MODE="transition_latch",
               FAKE_LOG=str(home / "fake.log"), WORKFLOW_MAX_SEATS="0")
    run = runs / "two-branches"
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    graph = {"name": "two-branches", "nodes": [
        {"id": "failure", "type": "agent", "goal": "LATCH-FAIL"},
        {"id": "sibling", "type": "agent", "goal": "LATCH-SIBLING"},
        {"id": "next", "type": "agent", "goal": "LATCH-NEXT", "after": ["sibling"]}]}
    (run / "graph.json").write_text(json.dumps(graph))
    fake = home / "fake"
    fake.write_text(f'#!{sys.executable}\nimport os, sys\nos.execv(sys.executable, [sys.executable, {str(ROOT / "tests" / "fake_hermes.py")!r}] + sys.argv[1:])\n')
    fake.chmod(0o755)
    (run / "run.json").write_text(json.dumps({"hermes_bin": str(fake),
        "concurrency": 2, "node_timeout": 90, "owner": {"session_id": "transition-owner"}}))
    (run / "inbox.jsonl").write_text(json.dumps({"node": "sibling", "text": "baked-before-spawn"}) + "\n")
    fds = {}
    for role in ("failure", "sibling"):
        path = run / f"{role}.fifo"
        os.mkfifo(path)
        fds[role] = os.open(path, os.O_RDWR | os.O_NONBLOCK)
    with open(home / "runner.log", "w") as log:
        proc = subprocess.Popen([sys.executable, str(ROOT / "wf.py"), "run", run.name],
                                env=env, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
        try:
            pid = int(until(lambda: (run / "sibling.started").read_text() if (run / "sibling.started").exists() else None))
            os.write(fds["failure"], b"fail\n")
            failed = until(lambda: read(run / "nodes" / "failure.json", {}).get("status") == "failed")
            check("failure committed only after sibling started", failed and proc.poll() is None)
            check("node wake delivered while sibling remains latched", wake.wait(4))
            check("no final run failure claimed before sibling drain",
                  not any(x.get("event") == "run.failed" for x in rows(run / "wake.jsonl")))
            os.kill(pid, 0)
            sibling_steer = door.act_steer({"run_id": run.name, "node": "sibling", "text": "late-for-original-spawn"})
            next_steer = door.act_steer({"run_id": run.name, "node": "next", "text": "consume-after-drain"})
            check("public steering admitted with live sibling despite failed branch",
                  sibling_steer.get("ok") and next_steer.get("ok"), [sibling_steer, next_steer])
            os.write(fds["sibling"], b"pull\n")
            pulled = until(lambda: read(run / "sibling.pulled"))
            check("original live PID consumes baked steering, not post-spawn steering",
                  pulled.get("steering") == ["baked-before-spawn"] and pulled.get("pulled") == 1, pulled)
            check("consumption is recorded before latch release",
                  any(x.get("event") == "steer.consumed" for x in rows(run / "events.jsonl")))
            graph["nodes"][0]["goal"] = "LATCH-OK"
            start = time.monotonic()
            amended = door.act_amend({"run_id": run.name, "graph": graph})
            print("AMEND_RECEIPT " + json.dumps({"elapsed_s": time.monotonic() - start, "response": amended}), flush=True)
            check("public amend durably accepted during live sibling", amended.get("ok"), amended)
            check("amend admitted but not applied before sibling drain",
                  (run / "restart.request").exists() and not any(x.get("event") == "graph.reloaded" for x in rows(run / "events.jsonl")))
            os.kill(pid, 0)
            check("unaffected sibling has exactly its original spawn before drain",
                  [x["pid"] for x in rows(run / "latch-spawns.jsonl") if x["role"] == "sibling"] == [pid])
            os.write(fds["sibling"], b"release\n")
            proc.wait(timeout=60)
            check("amend consumed at later wave boundary",
                  not (run / "restart.request").exists() and any(x.get("event") == "graph.reloaded" for x in rows(run / "events.jsonl")))
            next_rec = read(run / "nodes" / "next.json", {})
            check("queued downstream steer actually consumed after drain",
                  next_rec.get("output", {}).get("inbox", {}).get("steering") == ["consume-after-drain"], next_rec)
            check("unaffected sibling completed with one original spawn",
                  read(run / "nodes" / "sibling.json", {}).get("status") == "done"
                  and [x["pid"] for x in rows(run / "latch-spawns.jsonl") if x["role"] == "sibling"] == [pid])
            check("final run notification preserved", any(x.get("event") == "run.done" for x in rows(run / "wake.jsonl")))
        finally:
            if proc.poll() is None:
                os.write(fds["failure"], b"fail\n")
                os.write(fds["sibling"], b"release\n")
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            for fd in fds.values():
                os.close(fd)
            server.shutdown()
    if FAILS:
        print((home / "runner.log").read_text())
print("FAILURES " + json.dumps(FAILS) if FAILS else "ALL PASS")
sys.exit(bool(FAILS))
