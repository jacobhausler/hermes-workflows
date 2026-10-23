#!/usr/bin/env python3
"""WF-GRAFT-4 (est-f1w4u): exhaustive fail-closed resolution.

Two failure classes the runner must never swallow into a silent idle:

  1. DEAD END — a settled fork (done/partial with >=2 direct consumers) whose
     EVERY direct consumer is terminal-skipped on an UNTAKEN edge (when-false,
     prune cascade, gate skip) forces run-failed naming the fork
     (run.blocked error_class=dead_end + WORKFLOW_FAILED), NEVER finalize done.
     Discriminator: a consumer whose record says {skipped:"on_fail"} means the
     edge WAS taken (flow reached it, the death was caught, the author
     tolerated it) — that arm never counts toward a dead end. A single
     complementary arm taken closes the run done.

  2. ABORT PRECEDENCE — a persisted run-dir abort.json {node, source, reason,
     at} (atomic; survives a runner restart) forces run-failed and outranks
     every other branch: sources are the on_fail:"abort" target (the failed
     status STANDS — never converted to skipped) and a zero-item fanout with no
     else-arm fallback (fanout_empty + flag). The flag is checked before the
     on_fail-catch opportunity and before finalize-done; once flagged the
     scheduler refuses NEW spawns (live in-flight waves drain, never killed).
     A fanout-empty WITH an on_fail:"<agent-id>" else-arm keeps the existing
     catch path untouched and sets NO flag (regression guard).

Run: python3 tests/test_fail_closed_f1w4u.py   (exit code is the verdict)
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(PLUGIN))
import wfcommon  # noqa: E402

HOME = Path(tempfile.mkdtemp(prefix="wf-f1w4u-"))
RUNS = HOME / "workflows"
RUNS.mkdir()
FAKE = HERE / "fake"
ENV = {**os.environ, "HERMES_HOME": str(HOME), "WF_RUNS_ROOT": str(RUNS),
       "WF_HERMES_BIN": str(FAKE),
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
                                            "started": "2026-10-23T00:00:00+00:00",
                                            "owner": "test"}))
    return r

def seed_abort(r, node="pre-seeded"):
    (r / "abort.json").write_text(json.dumps(
        {"node": node, "source": "test-persistence", "reason": "flagged before launch",
         "at": "2026-10-23T00:00:00+00:00"}))

def run_runner(r, timeout=120):
    return subprocess.run([PY, str(PLUGIN / "wf.py"), "run", r.name], env=ENV,
                          capture_output=True, text=True, timeout=timeout).stdout.strip()

def agent(id, after=(), goal=None, **kw):
    n = {"id": id, "type": "agent", "after": list(after), "timeout": 30,
         "goal": goal if goal is not None else f'JSON:{json.dumps({"ok": True})}'}
    n.update(kw)
    return n

def echo(id, output, after=()):
    return {"id": id, "type": "echo", "after": list(after), "output": output}

def events(r):
    return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines() if l.strip()]

def rec(r, nid):
    p = r / "nodes" / f"{nid}.json"
    return json.loads(p.read_text()) if p.exists() else None

def status(r):
    return wfcommon.run_state(r, telemetry=False)["status"]

V = wfcommon.validate_graph

# ---- 0. grammar: on_fail gains the abort keyword ----
check("on_fail:'abort' accepted on agent", V([agent("a", on_fail="abort")]) is None,
      str(V([agent("a", on_fail="abort")])))
check("on_fail unknown target still rejected with the locked message",
      "must be 'skip' or an existing node id"
      in (V([agent("a", on_fail="ghost")]) or ""))

# ---- 1. DEAD END: echo producer, two when-false arms => run FAILED naming the fork ----
r = fresh("de-fork", [
    echo("prod", {"v": 1}),
    agent("arm_a", ["prod"], when="out.prod.v == 2"),
    agent("arm_b", ["prod"], when="out.prod.v == 3"),
])
out = run_runner(r)
check("dead end: run FAILS, never a silent idle", out.startswith("WORKFLOW_FAILED de-fork"), out[:120])
check("dead end: the failure names the fork", "prod" in out, out[:160])
evs = events(r)
blocked = [e for e in evs if e.get("event") == "run.blocked" and e.get("error_class") == "dead_end"]
check("dead end: run.blocked error_class=dead_end names the fork",
      bool(blocked) and "prod" in json.dumps(blocked[0]), json.dumps(blocked[:1])[:300])
check("dead end: the run NEVER finalizes done", not (r / "summary.md").exists()
      and not any(e.get("event") == "run.done" for e in evs))
check("dead end: the read model reads failed", status(r) == "failed", status(r))
check("dead end: both arms committed skipped (when-false, zero spawns)",
      (rec(r, "arm_a") or {}).get("status") == "skipped"
      and (rec(r, "arm_b") or {}).get("status") == "skipped")

# ---- 2. control: one complementary arm taken => DONE (no regression) ----
r = fresh("de-ctrl", [
    echo("prod", {"v": 1}),
    agent("arm_a", ["prod"], when="out.prod.v == 1"),   # taken: fake child answers
    agent("arm_b", ["prod"], when="out.prod.v == 2"),   # untaken
])
out = run_runner(r)
check("control: one arm taken closes DONE", out.startswith("WORKFLOW_DONE de-ctrl"), out[:120])
check("control: the read model reads done", status(r) == "done", status(r))

# ---- 3. discriminator: an on_fail-caught arm is a TAKEN edge => not a dead end ----
r = fresh("de-caught", [
    agent("prod", goal='JSON:{"v": 1}'),
    agent("arm_dead", ["prod"], goal="FAILME de-caught", on_fail="skip"),
    agent("arm_when", ["prod"], when="out.prod.v == 2"),
])
out = run_runner(r)
check("discriminator: caught-death arm counts as taken — run closes DONE",
      out.startswith("WORKFLOW_DONE de-caught"), out[:120])
check("discriminator: the caught arm reads skipped",
      (rec(r, "arm_dead") or {}).get("status") == "skipped"
      and (rec(r, "arm_dead") or {}).get("output", {}).get("skipped") == "on_fail")

# ---- 4. ABORT: on_fail:"abort" death => failed, flag persisted, failed STANDS ----
r = fresh("ab-target", [
    agent("live", goal='JSON:{"ok": true}'),
    agent("dead", goal="FAILME ab-target", on_fail="abort"),
])
out = run_runner(r)
check("abort target: run FAILS", out.startswith("WORKFLOW_FAILED ab-target"), out[:120])
ab = json.loads((r / "abort.json").read_text()) if (r / "abort.json").exists() else {}
check("abort target: abort.json persisted naming the node",
      ab.get("node") == "dead" and ab.get("source") and ab.get("at"), json.dumps(ab)[:200])
check("abort target: the failed status STANDS (never converted to skipped)",
      (rec(r, "dead") or {}).get("status") == "failed")
evs = events(r)
check("abort target: node.on_fail event mirrors the caught error class",
      any(e.get("event") == "node.on_fail" and e.get("node") == "dead"
          and e.get("on_fail") == "abort" and e.get("caught_error_class")
          for e in evs))
check("abort target: run.blocked carries the abort verdict",
      any(e.get("event") == "run.blocked" and e.get("error_class") == "aborted"
          for e in evs))
check("abort target: the read model reads failed", status(r) == "failed", status(r))

# ---- 5. fanout items:[] (items_from resolving empty) with NO else-arm => flag + failed ----
r = fresh("ab-fo-empty", [
    echo("seed", {"items": []}),
    {**agent("fan", ["seed"]), "fanout": {"items_from": "seed.items", "goal": "do {item}"}},
])
out = run_runner(r)
check("fanout-empty: run FAILS", out.startswith("WORKFLOW_FAILED ab-fo-empty"), out[:120])
check("fanout-empty: the node keeps fanout_empty failed",
      (rec(r, "fan") or {}).get("status") == "failed"
      and (rec(r, "fan") or {}).get("error_class") == "fanout_empty")
check("fanout-empty: abort flag set in addition to node.failed",
      (r / "abort.json").exists()
      and json.loads((r / "abort.json").read_text()).get("node") == "fan")

# ---- 6. fanout items:[] WITH an on_fail:"<agent>" else-arm => fallback runs, NO flag ----
r = fresh("ab-fo-else", [
    echo("seed", {"items": []}),
    {**agent("fan", ["seed"], on_fail="fb"),
     "fanout": {"items_from": "seed.items", "goal": "do {item}"}},
    agent("fb", ["fan"], goal='JSON:{"fallback": true}'),
])
out = run_runner(r)
check("fanout else-arm: the fallback runs and the run closes DONE",
      out.startswith("WORKFLOW_DONE ab-fo-else")
      and (rec(r, "fb") or {}).get("status") == "done", out[:120])
check("fanout else-arm: NO abort flag (the catch path is untouched)",
      not (r / "abort.json").exists())

# ---- 7. fanout-empty with on_fail:"skip": flag is STILL set, catch never gets its turn ----
r = fresh("ab-fo-skip", [
    echo("seed", {"items": []}),
    {**agent("fan", ["seed"], on_fail="skip"),
     "fanout": {"items_from": "seed.items", "goal": "do {item}"}},
])
out = run_runner(r)
check("fanout-empty + on_fail:skip: the flag outranks the catch — run FAILS",
      out.startswith("WORKFLOW_FAILED ab-fo-skip"), out[:120])
check("fanout-empty + on_fail:skip: the node stays FAILED (never laundered to skipped)",
      (rec(r, "fan") or {}).get("status") == "failed")

# ---- 8. flag persisted on disk + all-else-done => FAILED (outranks done) ----
r = fresh("ab-flagdone", [echo("one", {"ok": True})])
seed_abort(r)
out = run_runner(r)
check("persisted flag: a run whose every node lands done still FAILS",
      out.startswith("WORKFLOW_FAILED ab-flagdone") and "WORKFLOW_DONE" not in out, out[:120])
check("persisted flag: NEVER finalize done", not (r / "summary.md").exists())
check("persisted flag: the read model reads failed", status(r) == "failed", status(r))

# ---- 9. flag present => the scheduler refuses NEW spawns ----
r = fresh("ab-nospawn", [agent("n1", goal='JSON:{"ok": true}')])
seed_abort(r)
out = run_runner(r)
check("refused spawn: run FAILS with the abort verdict",
      out.startswith("WORKFLOW_FAILED ab-nospawn"), out[:120])
check("refused spawn: the pending node never spawned or committed",
      rec(r, "n1") is None)
check("refused spawn: the refusal is logged",
      any(e.get("event") == "run.spawn_refused" and "n1" in json.dumps(e)
          for e in events(r)))

shutil.rmtree(HOME, ignore_errors=True)
print("FAILS:", FAILS if FAILS else "none")
sys.exit(1 if FAILS else 0)
