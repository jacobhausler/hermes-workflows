"""Response truth at the release/stop terminal handoff (est-gexk5 — the sibling
sweep of PR #518's amend fix, found on the #518 R8 adversary review): an applied
act_release / act_stop must never promise a live-runner commit/consume that no
runner demonstrably performed. The measured lie shape (row est-3acn branch of
_resume_after_action, __init__.py "return \"consumed\"" for terminal runs): the
run closed terminal — a RunBudget partial keeps held gates uncommitted — so the
handoff answers "consumed" though NOTHING was consumed, and the response promised
"the live runner commits/consumes it at its boundary". The row's second clause is
honored here: the re-drive-on-interrupted advice is UNSATISFIABLE for a terminal
false-consume (a terminal run never reads interrupted; act_wait respawns only
running/pending/interrupted), so the terminal copy names inertness instead — and
the re-drive is offered ONLY where it is satisfiable (mode "live": the dying
runner lands interrupted and a re-submit is admitted then).

Ten legs, two verbs:
  R1 release, held gate + dead runner   -> respawn bridge (regression pin; green at base)
  R2 release, RunBudget partial + held gate, dead runner (the est-3acn false
     consume) -> terminal copy. RED at base: the hint promised the live-runner
     boundary commit for a run with no runner and no re-drive.
  R3 release, runner commits the gate at its boundary (observed, then dies)
     -> confident past-tense copy, zero hedge. RED at base wording (the base
     copy promises a FUTURE commit even for an observed one).
  R4 release, dying runner (liveness reads True across the whole window)
     -> expected-not-observed copy naming verify + re-drive. RED at base.
  R5 release, stop pending -> refused, zero writes (pin; green at base)
  S1 stop, interrupted + dead runner    -> respawn note (regression pin; green at base)
  S2 stop, runner closes partial INSIDE the grace window -> terminal copy, no
     live-runner claim, no re-drive promise. RED at base.
  S3 stop, marker observed consumed at runner death -> observed copy, no hedge.
     RED at base wording.
  S4 stop, dying runner -> expected-not-observed + satisfiable re-drive. RED at base.
  S5 stop, done run -> terminal guard {"already": "done"}, zero writes (pin; green at base)

Pure door test: liveness faked by call sequence (the r18 S4a / test_amend_handoff_truth_83v
pattern), respawn captured, no network (liveness ping stubbed). Stdlib only.
"""
import importlib, json, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
sys.path.insert(0, str(BUILD))

_tmp = tempfile.TemporaryDirectory(prefix=".tmphandoffgexk5-", dir=HERE)
HOME = Path(_tmp.name)
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
(HOME / "config.yaml").write_text(
    "model:\n  default: qwen38-next\n  aliases:\n"
    "    fable: anthropic/claude-fable-5.1\n    opus: anthropic/claude-opus-5-5\n")

door = importlib.import_module("__init__")
import wf_test_isolation as _iso71; _iso71.install(door)  # #71 r5: pin settings.runs_root
from wfcommon import efp

door._CTX = type("Ctx", (), {"get_config": lambda self, k, d=None:
    {"worker": "qwen38-next", "manager": "fable", "frontier": "opus"} if k == "models" else d})()
door._ping_route_once = lambda p, m: {"liveness": "unknown"}   # no network

RUNS = Path(os.environ["WF_RUNS_ROOT"])
FAILS = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)

RESPAWN = []
door._respawn_runner = lambda r: RESPAWN.append(Path(r).name)

def fake_alive(seq, hook=None):
    """Door-global liveness fake: seq = per-call booleans (last sticks),
    hook(i) runs before each answer (i is 0-based)."""
    state = {"i": 0}
    def f(_r):
        i = state["i"]; state["i"] += 1
        if hook: hook(i)
        return seq[i] if i < len(seq) else seq[-1]
    return f

def gate_graph():
    author = {"name": "probe", "nodes": [
        {"id": "a", "type": "agent", "goal": "g", "model": "manager"},
        {"id": "g", "type": "gate", "after": ["a"], "question": "?", "options": ["go", "no"]}]}
    g = door._common.apply_graph_defaults(author)
    err, _, _ = door._resolve_models(g["nodes"])
    assert err is None, err
    return g

def linear_graph():
    author = {"name": "probe2", "nodes": [
        {"id": "a", "type": "agent", "goal": "g", "model": "manager"},
        {"id": "b", "type": "agent", "goal": "h", "model": "manager", "after": ["a"]}]}
    g = door._common.apply_graph_defaults(author)
    err, _, _ = door._resolve_models(g["nodes"])
    assert err is None, err
    return g

def write_run(rid, g):
    r = RUNS / rid
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps(g))
    (r / "run.json").write_text(json.dumps({"name": Path(rid).name}))
    (r / "runner.lock").touch()   # present, unheld -> not alive
    byid = {n["id"]: n for n in g["nodes"]}
    (r / "nodes" / "a.json").write_text(json.dumps(
        {"status": "done", "efp": efp(byid, byid["a"]),
         "fp_rule_version": door._common.FP_RULE_VERSION}))
    return r

def events(r, *evts):
    (r / "events.jsonl").write_text("".join(
        json.dumps({"ts": "2026-10-25T00:00:00+00:00", "event": e}) + "\n" for e in evts))

def exit_rec(r, g, reason):
    (r / "runner_exit.json").write_text(json.dumps(
        {"reason": reason, "at": "2026-10-25T00:00:02+00:00",
         "graph_fingerprint": door._common.graph_fingerprint(g),
         "fp_rule_version": door._common.FP_RULE_VERSION}))

def make_held(rid):
    """Agent done + gate unanswered; dead runner; last event run.started -> held."""
    g = gate_graph()
    r = write_run(rid, g)
    events(r, "run.started")
    assert door.run_state(r)["status"] == "held", door.run_state(r)["status"]
    return r, g

def make_partial(rid):
    """The est-3acn shape: RunBudget-capped graceful partial, gate g never committed."""
    g = gate_graph()
    r = write_run(rid, g)
    events(r, "run.started", "dispatch.refused", "run.partial")
    exit_rec(r, g, "budget_exhausted")
    assert door.run_state(r)["status"] == "partial", door.run_state(r)["status"]
    return r, g

def commit_gate(r, g):
    """What the runner's boundary would write: the gate record committed done."""
    byid = {n["id"]: n for n in g["nodes"]}
    (r / "nodes" / "g.json").write_text(json.dumps(
        {"status": "done", "efp": efp(byid, byid["g"]),
         "fp_rule_version": door._common.FP_RULE_VERSION}))

_real_alive = door.runner_alive

def with_alive(seq, hook=None):
    setattr(door, "runner_alive", fake_alive(tuple(seq), hook=hook))

def restore_alive():
    setattr(door, "runner_alive", _real_alive)


# ---- R1: held + dead runner -> the respawn bridge (regression pin)
r, g = make_held("r1-held-dead")
RESPAWN.clear()
out = door.act_release({"run_id": "r1-held-dead", "gate_id": "g", "answer": "go"})
check("R1 dead-runner release routes through the respawn bridge", RESPAWN == ["r1-held-dead"], RESPAWN)
check("R1 respawned copy + auto_resumed", out.get("auto_resumed") is True and "respawned" in out.get("hint", ""), out)
check("R1 answer durable", (r / "gates" / "g.json").exists())

# ---- R2: est-3acn terminal false-consume — the RED proof at base
r, g = make_partial("r2-partial-held")
RESPAWN.clear()
out = door.act_release({"run_id": "r2-partial-held", "gate_id": "g", "answer": "go"})
dump = json.dumps(out).lower()
check("R2 terminal copy states the inertness (RED at base)", "terminal" in dump and "nothing will" in dump, dump[:400])
check("R2 no live-runner commit promise (RED at base)", "live runner" not in dump, dump[:400])
check("R2 no unsatisfiable re-drive-on-interrupted advice", "once the run reads interrupted" not in dump, dump[:400])
check("R2 answer still durable (ok:true with real side effect)", out.get("ok") and (r / "gates" / "g.json").exists())
check("R2 no respawn for a terminal run", RESPAWN == [] and "auto_resumed" not in out, out)

# ---- R3: observed boundary commit -> confident past-tense copy, no hedge
r, g = make_held("r3-committed")
RESPAWN.clear()
with_alive((True, False, False, False), hook=lambda i: i == 1 and commit_gate(r, g))
try:
    out = door.act_release({"run_id": "r3-committed", "gate_id": "g", "answer": "go"})
finally:
    restore_alive()
dump = json.dumps(out).lower()
check("R3 observed commit reports consumption in the past tense (RED at base wording)",
      "runner committed" in dump, dump[:400])
check("R3 consumed shape carries no hedge", "not observed" not in dump and "no re-drive" not in dump, dump[:200])
check("R3 no respawn for a consumed release", RESPAWN == [], RESPAWN)

# ---- R4: dying runner (grace window all-alive) -> expected-not-observed + re-drive
r, g = make_held("r4-dying")
RESPAWN.clear()
with_alive((True,))
try:
    out = door.act_release({"run_id": "r4-dying", "gate_id": "g", "answer": "go"})
finally:
    restore_alive()
dump = json.dumps(out).lower()
check("R4 unobserved copy names the not-yet-observed truth (RED at base)", "not observed" in dump, dump[:400])
check("R4 unobserved copy names the satisfiable re-drive",
      "once the run reads interrupted" in dump, dump[:400])
check("R4 no respawn was attempted; durable answer written", RESPAWN == [] and (r / "gates" / "g.json").exists())

# ---- R5: stop-pending refused, zero writes (pin; green at base)
r, g = make_held("r5-stop-pending")
(r / "stop.request").write_text("2026-10-25T00:00:00+00:00")
out = door.act_release({"run_id": "r5-stop-pending", "gate_id": "g", "answer": "go"})
check("R5 stop-pending release refused with nothing written",
      "refused" in json.dumps(out).lower() and not (r / "gates" / "g.json").exists(), out)


# ---- S1: interrupted + dead runner -> respawn note (regression pin)
g = linear_graph(); r = write_run("s1-interrupted-dead", g)
events(r, "run.started")
assert door.run_state(r)["status"] == "interrupted", door.run_state(r)["status"]
RESPAWN.clear()
out = door.act_stop({"run_id": "s1-interrupted-dead"})
check("S1 dead-runner stop respawns to consume the marker", RESPAWN == ["s1-interrupted-dead"], RESPAWN)
check("S1 respawn copy unchanged", "runner spawned to consume the stop marker" in out.get("note", ""), out)
check("S1 marker durable", (r / "stop.request").exists())

# ---- S2: runner closes partial INSIDE the grace window — the RED proof at base
g = linear_graph(); r = write_run("s2-dying-partial", g)
events(r, "run.started")
RESPAWN.clear()
def _close_partial(i):
    if i == 1:   # grace poll 1: the runner finalizes the capped run mid-window
        events(r, "run.started", "dispatch.refused", "run.partial")
        exit_rec(r, g, "budget_exhausted")
with_alive((True, False, False), hook=_close_partial)
try:
    out = door.act_stop({"run_id": "s2-dying-partial"})
finally:
    restore_alive()
dump = json.dumps(out).lower()
check("S2 terminal copy states the inertness (RED at base)", "terminal" in dump and "nothing will" in dump, dump[:400])
check("S2 no live-runner consume promise (RED at base)", "live runner" not in dump, dump[:400])
check("S2 no unsatisfiable re-drive-on-interrupted advice", "once the run reads interrupted" not in dump, dump[:400])
check("S2 marker stays (residue), no respawn", (r / "stop.request").exists() and RESPAWN == [])

# ---- S3: marker observed consumed at runner death -> observed copy
g = linear_graph(); r = write_run("s3-consumed", g)
events(r, "run.started")
RESPAWN.clear()
def _consume(i):
    if i == 1:
        (r / "stop.request").unlink(missing_ok=True)
with_alive((True, False, False, False), hook=_consume)
try:
    out = door.act_stop({"run_id": "s3-consumed"})
finally:
    restore_alive()
dump = json.dumps(out).lower()
check("S3 observed consume reports in the past tense (RED at base wording)", "stop committed" in dump, dump[:400])
check("S3 observed consume carries no future promise", "next boundary" not in dump and "not observed" not in dump, dump[:200])
check("S3 no respawn for a consumed stop", RESPAWN == [], RESPAWN)

# ---- S4: dying runner stop -> expected-not-observed + satisfiable re-drive
g = linear_graph(); r = write_run("s4-dying", g)
events(r, "run.started")
RESPAWN.clear()
with_alive((True,))
try:
    out = door.act_stop({"run_id": "s4-dying"})
finally:
    restore_alive()
dump = json.dumps(out).lower()
check("S4 unobserved copy names the not-yet-observed truth (RED at base)", "not observed" in dump, dump[:400])
check("S4 unobserved copy names the satisfiable re-drive", "once the run reads interrupted" in dump, dump[:400])
check("S4 no respawn attempted", RESPAWN == [])

# ---- S5: terminal early guard untouched (pin; green at base)
g = linear_graph(); r = write_run("s5-done", g)
(r / "nodes" / "b.json").write_text(json.dumps(
    {"status": "done", "efp": efp({n["id"]: n for n in g["nodes"]},
                                  [n for n in g["nodes"] if n["id"] == "b"][0]),
     "fp_rule_version": door._common.FP_RULE_VERSION}))
events(r, "run.started", "run.done")
exit_rec(r, g, "done")
RESPAWN.clear()
out = door.act_stop({"run_id": "s5-done"})
check("S5 done run keeps the already guard", out.get("already") == "done", out)
check("S5 zero writes, zero respawn", not (r / "stop.request").exists() and RESPAWN == [])

print(f"\n{'ALL PASS' if not FAILS else 'FAILURES: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
