#!/usr/bin/env python3
"""45b038: cron's core-less interpreter must still bake a proved pinned route.

The fake launcher owns a sibling Python interpreter, as a venv's bin/ directory
does. Its isolated auxiliary client records the single explicit-route call. No
network or live seat is used. The runner spawn spy reads the committed graph,
proving the bake is on disk before any child could start.
"""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import wf_test_isolation

failures = 0
def check(label, ok, detail=""):
    global failures
    print(("PASS " if ok else "FAIL ") + label + (" " + str(detail) if not ok else ""))
    failures += not ok

with tempfile.TemporaryDirectory(prefix="wf-route-cron-") as scratch:
    home = Path(scratch)
    os.environ["HERMES_HOME"] = str(home)
    os.environ["WF_RUNS_ROOT"] = str(home / "runs")
    bindir = home / "venv" / "bin"
    bindir.mkdir(parents=True)
    (bindir / "python").symlink_to(sys.executable)
    launcher = bindir / "hermes"
    launcher.write_text("#!/bin/sh\nexit 0\n")
    launcher.chmod(0o755)
    os.environ["HERMES_WF_HERMES_BIN"] = str(launcher)
    package = home / "fake-core" / "agent"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "auxiliary_client.py").write_text('''import json, os

def call_llm(*, task, provider, model, messages, max_tokens, timeout, route_info):
    with open(os.environ["WF_FAKE_PING_LOG"], "a") as f:
        f.write(json.dumps(dict(task=task, provider=provider, model=model,
                                messages=messages, max_tokens=max_tokens,
                                timeout=timeout)) + "\\n")
    route_info.update(json.loads(os.environ.get("WF_FAKE_ROUTE") or
                                 json.dumps(dict(provider=provider, model=model))))
    return "pong"
''')
    os.environ["PYTHONPATH"] = str(home / "fake-core") + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["WF_FAKE_PING_LOG"] = str(home / "ping.log")
    door = importlib.import_module("__init__")
    wf_test_isolation.install(door)
    door._CTX = None
    door._seat_model_cfg = lambda: {"default": "seat-default", "aliases": {}}
    door._seat_aliases = lambda: []
    door._seat_default = lambda: "seat-default"
    door._import_call_llm = lambda: (_ for _ in ()).throw(ModuleNotFoundError("agent"))
    observed = []
    def spawn(run):
        observed.append(json.loads((run / "graph.json").read_text()))
    door._spawn_runner = spawn
    graph = {"name": "cron-probe", "nodes": [{"id": "a", "type": "agent",
        "goal": "x", "provider": "openai", "model": "m-1"}]}
    answer = door.act_run({"graph": graph})
    check("cron submit launches", bool(answer.get("run_id")), answer)
    check("subprocess proves route alive", answer.get("routes", {}).get("a", {}).get("liveness") == "alive", answer)
    committed = observed[0] if observed else {}
    check("atomic pre-spawn graph bake", committed.get("nodes", [{}])[0].get("route_verified") == "openai/m-1", committed)
    lines = (home / "ping.log").read_text().splitlines() if (home / "ping.log").exists() else []
    calls = [json.loads(line) for line in lines]
    check("one explicit provider+model call", len(calls) == 1 and calls[0]["provider"] == "openai"
          and calls[0]["model"] == "m-1" and calls[0]["max_tokens"] == 1, calls)
    os.environ["WF_FAKE_ROUTE"] = json.dumps({"provider": "other", "model": "fallback"})
    wrong = door.act_run({"graph": graph})
    check("different recorded route refused", "FALLBACK LADDER" in wrong.get("error", ""), wrong)
    os.environ["HERMES_WF_HERMES_BIN"] = str(home / "missing-hermes")
    offline = door.act_run({"graph": graph})
    check("missing launcher stays unknown and fail-open", bool(offline.get("run_id"))
          and offline["routes"]["a"]["liveness"] == "unknown", offline)
    unpinned = {"name": "solo", "nodes": [{"id": "a", "type": "agent", "goal": "x"}]}
    original = dict(unpinned)
    solo = door.act_run({"graph": unpinned})
    saved = json.loads((home / "runs" / solo["run_id"] / "graph.json").read_text()) if solo.get("run_id") else {}
    check("unpinned never proves/holds/refuses", bool(solo.get("run_id"))
          and "route_verified" not in saved.get("nodes", [{}])[0]
          and "route_verified" not in original["nodes"][0], solo)
print("ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(bool(failures))
