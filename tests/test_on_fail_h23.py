#!/usr/bin/env python3
"""jam-h23 on_fail: per-agent failure catch -> join-tolerant `skipped` (or fallback run).

Validator grammar (agent-only key, value checks) + real-runner cases with
tests/fake:
  1. dead node FAILME on_fail:'skip' commits `skipped`; the downstream join with
     one live dep runs; the run closes `done` (WORKFLOW_DONE), death readable via
     caught_error/caught_error_class, event node.on_fail.
  2. on_fail:'<fallback-id>' additionally lets the named agent run.
  3. negative control: the same failing node WITHOUT on_fail blocks the run
     (WORKFLOW_FAILED, run.blocked) — the catch is opt-in, nothing changed for
     graphs that never name it.
  4. #473: a downstream node that NAMES the skipped head in `inputs:` spawns with a
     labelled skip-sentinel block (the death as data), never `error_class:inputs`.
  5. control for #473: a `done` head missing the dotted path keeps the exact hard
     failure — the sentinel never launders an authoring typo into a sanctioned skip.

Run: cd tests && python3 test_on_fail_h23.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(PLUGIN))
import wfcommon  # noqa: E402

HOME = HERE / "home14"
RUNS = HOME / "workflows"
FAKE = HERE / "fake"
ENV = {**os.environ, "HERMES_HOME": str(HOME), "WF_RUNS_ROOT": str(RUNS), "WF_HERMES_BIN": str(FAKE),
       "PATH": f"{FAKE.parent}:{os.environ.get('PATH', '')}"}
PY = sys.executable
FAILS = []

def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)

def fresh(run_id, nodes):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    for d in ("nodes", "gates", "logs"):
        (r / d).mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": "t", "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"name": "t", "hermes_bin": str(FAKE),
                                            "concurrency": 4, "node_timeout": 30,
                                            "retry_backoff": [0.05, 0.05],
                                            "started": "2026-09-29T00:00:00+00:00",
                                            "owner": "test"}))
    return r

def run_runner(r, timeout=120):
    return subprocess.run([PY, str(PLUGIN / "wf.py"), "run", r.name], env=ENV,
                          capture_output=True, text=True, timeout=timeout).stdout.strip()

def agent(id, after=(), goal=None, **kw):
    n = {"id": id, "type": "agent", "after": list(after), "timeout": 30,
         "goal": goal if goal is not None else f'JSON:{json.dumps({"ok": True})}'}
    n.update(kw)
    return n

# ---- 1. validator grammar ----
V = wfcommon.validate_graph
check("on_fail:'skip' accepted on agent", V([agent("a", on_fail="skip")]) is None)
check("on_fail on gate rejected (closed key set)",
      "unknown key" in (V([agent("a"), {"id": "g", "type": "gate", "after": ["a"],
                                        "question": "?", "on_fail": "skip"}]) or ""))
check("on_fail on echo rejected",
      "unknown key" in (V([agent("a"), {"id": "e", "type": "echo", "after": ["a"],
                                        "output": {}, "on_fail": "skip"}]) or ""))
check("on_fail unknown target rejected",
      "must be 'skip' or an existing node id"
      in (V([agent("a", on_fail="ghost")]) or ""))
check("on_fail gate target rejected",
      "must be an agent node"
      in (V([agent("a", on_fail="g"), {"id": "g", "type": "gate", "after": [],
                                       "question": "?"}]) or ""))
check("on_fail ancestor target rejected",
      "must not be an ancestor"
      in (V([agent("up"), agent("mid", ["up"]), agent("dn", ["mid"], on_fail="up")]) or ""))
check("on_fail descendant target accepted (fallback runs after the death)",
      V([agent("seed"), agent("dead", ["seed"], on_fail="fb"),
         agent("fb", ["dead"]), agent("join", ["dead", "fb"])]) is None)
check("on_fail self rejected",
      "must not be an ancestor" in (V([agent("a", on_fail="a")]) or ""))

# ---- 2. run: on_fail:'skip' lets the join arm complete ----
shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
r = fresh("of-skip", [
    agent("live", goal='JSON:{"ok": true}'),
    agent("dead", goal="FAILME of-skip", on_fail="skip"),
    agent("join", ["dead", "live"], goal='JSON:{"joined": true}'),
])
out = run_runner(r)
check("on_fail:'skip' run closes DONE", out.startswith("WORKFLOW_DONE of-skip"), out[:90])
rec = json.loads((r / "nodes" / "dead.json").read_text())
check("failed node committed as skipped (not failed)", rec["status"] == "skipped", json.dumps(rec)[:160])
check("death stays readable on the skipped record",
      rec.get("caught_error_class") == "schema"
      and rec["output"]["skipped"] == "on_fail", json.dumps(rec)[:160])
check("join ran (one live dep satisfies)",
      json.loads((r / "nodes" / "join.json").read_text())["status"] == "done")
evs = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
check("node.on_fail event logged",
      any(e.get("event") == "node.on_fail" and e.get("node") == "dead"
          and e.get("on_fail") == "skip" for e in evs))
check("run.blocked NOT logged", not any(e.get("event") == "run.blocked" for e in evs))

# ---- 3. run: on_fail:'<fallback-id>' runs the named agent ----
r = fresh("of-fb", [
    agent("seed", goal='JSON:{"ok": true}'),
    agent("dead", ["seed"], goal="FAILME of-fb", on_fail="fb"),
    agent("fb", ["dead"], goal='JSON:{"fallback": true}'),
    agent("join", ["dead", "fb"], goal='JSON:{"joined": true}'),
])
out = run_runner(r)
check("on_fail:'<fb>' run closes DONE", out.startswith("WORKFLOW_DONE of-fb"), out[:90])
check("failed node committed as skipped",
      json.loads((r / "nodes" / "dead.json").read_text())["status"] == "skipped")
check("fallback agent ran",
      json.loads((r / "nodes" / "fb.json").read_text())["status"] == "done")
check("join ran", json.loads((r / "nodes" / "join.json").read_text())["status"] == "done")
evs = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
check("node.on_fail event names the fallback",
      any(e.get("event") == "node.on_fail" and e.get("node") == "dead"
          and e.get("on_fail") == "fb" for e in evs))

# ---- 4. negative control: no on_fail => the same shape blocks ----
r = fresh("of-none", [
    agent("live", goal='JSON:{"ok": true}'),
    agent("dead", goal="FAILME of-none"),
    agent("join", ["dead", "live"], goal='JSON:{"joined": true}'),
])
out = run_runner(r)
check("without on_fail the failure still blocks the run",
      out.startswith("WORKFLOW_FAILED of-none"), out[:90])
check("negative control: node stays failed",
      json.loads((r / "nodes" / "dead.json").read_text())["status"] == "failed")

# ---- 5. #473: an explicit inputs ref to the SKIPPED head is a sentinel, not a crash ----
plog = HOME / "of-sentinel.prompts.log"
if plog.exists():
    plog.unlink()
r = fresh("of-sentinel", [
    agent("live", goal='JSON:{"ok": true}'),
    agent("dead", goal="FAILME of-sentinel", on_fail="skip"),
    agent("census", ["dead", "live"], goal='JSON:{"joined": true}', inputs=["dead"]),
])
cp = subprocess.run([PY, str(PLUGIN / "wf.py"), "run", r.name],
                    env={**ENV, "FAKE_PROMPT_LOG": str(plog)},
                    capture_output=True, text=True, timeout=120)
out = cp.stdout.strip()
prompts = plog.read_text().split("\n=====PROMPT=====\n")[1:] if plog.exists() else []
sentinel = next((p for p in prompts if "(skipped: on_fail)" in p), None)
check("#473: the consumer of a skipped head SPAWNS (no error_class=inputs death)",
      json.loads((r / "nodes" / "census.json").read_text())["status"] == "done",
      json.dumps(json.loads((r / "nodes" / "census.json").read_text()))[:200])
check("#473: the dropout arm reaches `## Inputs` as a labelled skip-sentinel block",
      sentinel is not None, str([p.splitlines()[0][:60] for p in prompts]))
check("#473: the sentinel stays fail-closed — the death is readable in the payload",
      sentinel is not None and "caught_error_class" in sentinel)
check("#473: the run closes DONE with the census answered",
      out.startswith("WORKFLOW_DONE of-sentinel"), out[:90])
check("#473: the sentinel never pretends to be data (no fabricated roster key)",
      sentinel is not None and '"all_results"' not in sentinel)

# ---- 6. control: the sentinel is `skipped`-only; a missing path on a DONE head still fails ----
r = fresh("of-hardfail", [
    agent("live", goal='JSON:{"ok": true}'),
    agent("census", ["live"], goal='JSON:{"joined": true}', inputs=["live.nope"]),
])
out = run_runner(r)
check("#473 control: a `done` head without the path keeps the hard failure",
      out.startswith("WORKFLOW_FAILED of-hardfail"), out[:90])
check("#473 control: the exact error string is untouched",
      json.loads((r / "nodes" / "census.json").read_text()).get("error")
      == "inputs: live.nope not resolvable",
      json.dumps(json.loads((r / "nodes" / "census.json").read_text()))[:200])

print("FAILS:", FAILS if FAILS else "none")
sys.exit(1 if FAILS else 0)
