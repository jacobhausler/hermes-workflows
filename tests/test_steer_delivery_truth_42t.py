#!/usr/bin/env python3
"""E14 (bd_2026-11-13-42t): steer delivery truth.

Steering is ONE mechanism per node and the receipt says so:
  * the guaranteed channel is BAKE-AT-SPAWN — every steer.baked receipt carries
    mechanism=bake-at-spawn and drained_cues (the budget cues it refused to
    re-bake for this spawn);
  * a budget cue is the DYING generation's fact: the claim stamps its spawn and
    every LATER generation DRAINS the line — never re-baked into the steer
    file, never re-fed into the runner's prompt injection (drain_inbox skips it
    with a budget_cue.drained event). 'budget left: N' can never lie to a fresh
    budget;
  * the live pull is an OPT-IN seam whose only evidence is steer.consumed + the
    cursor advance. The seam runs on the RUNNER's interpreter
    (HERMES_WF_PYTHON stamped at the spawn seam, honoured by tests/fake): a
    seat-local /usr/bin/python3 too old for the door's syntax must not silently
    kill the pull (the E14 evidence: every .cursor 0, zero steer.consumed).

Run (stdlib only): python3 tests/test_steer_delivery_truth_42t.py
"""
import importlib.util
import json, os, shutil, subprocess, sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))
ROOT = BUILD.parent
HOME = BUILD / f"home-e14.{os.getpid()}"
RUNS = HOME / "workflows"
FAKE = str(BUILD / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)  # est-2ek.1.762 pin: HERMES_HOME alone is not a sandbox
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402
import atexit
atexit.register(shutil.rmtree, HOME, ignore_errors=True)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

HOME.mkdir(parents=True); RUNS.mkdir()

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}
    m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def runx(run_id, extra_env=None, timeout=120):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / "fake.log"), **(extra_env or {}))
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def events(r):
    p = r / "events.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

def rec_of(r, nid="w"):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())

# ------------------------------------------------------------------ S1: E14
# Bake seam unit: a cue stamped to generation 0 is DRAINED from generation 1's
# bake (plain steer lines still ride); the same-generation claim still bakes
# its own cue; drain_inbox never re-feeds the stale cue into a prompt.
u = RUNS / "t42t-e14-unit"
(u / "steer").mkdir(parents=True)
(u / "budget_cue").mkdir()
(u / "budget_cue" / "u").write_text(json.dumps(
    {"node": "u", "index": None, "consumed": 27, "turns_left": 3,
     "max_turns": 30, "spawn": 0, "at": "now"}))
(u / "inbox.jsonl").write_text(
    json.dumps({"node": "u", "text": "fresh steer"}) + "\n"
    + json.dumps({"node": "u", "budget_cue": True,
                  "text": "turn budget: 3 turns left — persist your work now"}) + "\n")
node = {"id": "u", "type": "agent", "goal": "u"}
p1, c1, hwm1 = wf._steer_bake(u, node, None, 1)
bake1 = Path(p1).read_text()
check("S1 respawn bake carries the plain steer line", "fresh steer" in bake1, bake1)
check("S1 respawn bake DRAINS the stale budget cue (no lie about a fresh budget)",
      "turn budget" not in bake1, bake1)
baked1 = [e for e in events(u) if e.get("event") == "steer.baked"]
check("S1 steer.baked receipt names the mechanism and counts the drain",
      len(baked1) == 1 and baked1[0].get("mechanism") == "bake-at-spawn"
      and baked1[0].get("drained_cues") == 1, json.dumps(baked1))
p0, c0, hwm0 = wf._steer_bake(u, node, None, 0)
check("S1 same-generation claim still bakes its own cue (no retro-drain)",
      "turn budget" in Path(p0).read_text(), Path(p0).read_text())
consumed = set()
steering = wf.drain_inbox(u, consumed)
check("S1 drain_inbox delivers the plain line to the prompt channel",
      steering.get("u") == ["fresh steer"], json.dumps(steering))
check("S1 the stale cue never enters the respawn prompt and the drain is an event",
      "turn budget" not in json.dumps(steering)
      and any(e.get("event") == "budget_cue.drained" for e in events(u)),
      json.dumps(steering))
check("S1 the cue line is consumed exactly once (idempotent re-drain)",
      len(consumed) == 2 and wf.drain_inbox(u, consumed) == {}, json.dumps(sorted(consumed)))

# ------------------------------------------------------------------ S2: E14
# The live-pull seam on an engine run: steer accepted pre-spawn, baked into the
# spawn, PULLED by the child (steer.consumed pulled=1 + cursor 1), receipt
# honest on a clean run (drained_cues=0).
(HOME / "fake.log").write_text("")
r = mk("t42t-pull", [{"id": "w", "type": "agent", "goal": "pull me"}])
spec = importlib.util.spec_from_file_location("door42t", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
ans = door.act_steer({"run_id": r.name, "node": "w", "text": "nudge 42t"})
check("S2 steer accepted pre-spawn", ans.get("ok") is True, json.dumps(ans))
runx("t42t-pull", {"FAKE_MODE": "poll_steer"})
rec = rec_of(r)
cons = [e for e in events(r) if e.get("event") == "steer.consumed"]
check("S2 the live child PULLED: steer.consumed with pulled=1",
      len(cons) == 1 and cons[0].get("pulled") == 1, json.dumps(cons))
check("S2 the pull landed: the child echoed the line",
      (rec.get("output") or {}).get("pulled") == ["nudge 42t"], json.dumps(rec)[:200])
baked = [e for e in events(r) if e.get("event") == "steer.baked" and e.get("node") == "w"]
check("S2 bake receipt names the mechanism on a clean run (drained_cues=0)",
      len(baked) == 1 and baked[0].get("n_lines") == 1
      and baked[0].get("mechanism") == "bake-at-spawn" and baked[0].get("drained_cues") == 0,
      json.dumps(baked))
check("S2 cursor advanced (observable, exactly once per spawn)",
      (r / "steer" / "w.a0.cursor").read_text().strip() == "1",
      (r / "steer" / "w.a0.cursor").read_text())
check("S2 spawn env stamps HERMES_WF_PYTHON (the fake seat runs the runner's interpreter)",
      "HERMES_WF_PYTHON=sys.executable" in (ROOT / "wf.py").read_text()
      and 'HERMES_WF_PYTHON:-' in (BUILD / "fake").read_text(), "")

print(("\nALL PASS" if ok else "\nFAILURES PRESENT") + " test_steer_delivery_truth_42t")
sys.exit(0 if ok else 1)
