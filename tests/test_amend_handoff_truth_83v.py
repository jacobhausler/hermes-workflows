"""Response truth at the dead/dying-runner amend handoff (the silent-heal shape):
an applied act_amend must never promise hot-reload or automatic continuation that
no runner demonstrably performed. The measured shape: runner exiting, its liveness
still reading True through the door's grace window (the sub-second flock HELD
window the wait path already knows about); the door returned ok:true + will_rerun
with a success claim, the process died without consuming restart.request, and the
heal lane never launched — the SECOND identical call applied for real.

Four shapes:
  T1 APPLIED (runner already dead at submit) -> respawn path claimed AND attempted.
  T2 UNOBSERVED (liveness true across the whole window, nothing consumed) -> the
     response must name the re-drive; claiming respawn is illegal, and the durable
     writes must still be there (ok:true never rides on zero side effect).
     T2 is the RED proof: at the pre-fix base the response carries no re-drive
     name and answers "continuation is automatic".
  T3 CONSUMED (marker observed gone at runner death) -> the confident consumed copy
     stays, with no re-drive nagging (the fix must not overcorrect into always hedging).
  T4 NO-OP (terminal run, byte-identical resubmit) -> the terminal-verdict fallback
     must NOT claim consumption: durable, nothing scheduled to re-run.

Pure door test: liveness faked by call sequence (r18 S4a pattern), respawn captured,
no network (liveness ping stubbed). Stdlib only.
"""
import importlib, json, os, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
sys.path.insert(0, str(BUILD))

_tmp = tempfile.TemporaryDirectory(prefix=".tmp-handoff83v-", dir=HERE)
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

RESPAWN_CALLS = []
door._respawn_runner = lambda r: RESPAWN_CALLS.append(Path(r).name)

def done_run(rid, extra=None):
    """A committed-done run: one agent node done at its efp, runner exited reason=done."""
    author = {"name": "probe", "nodes": [
        {"id": "a", "type": "agent", "goal": "g", "model": "manager"}]}
    g = door._common.apply_graph_defaults(author)
    err, _, _ = door._resolve_models(g["nodes"])
    assert err is None, err
    r = RUNS / rid
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps(g))
    (r / "run.json").write_text(json.dumps({"name": "probe"}))
    byid = {n["id"]: n for n in g["nodes"]}
    (r / "nodes" / "a.json").write_text(json.dumps(
        {"status": "done", "efp": efp(byid, g["nodes"][0]),
         "fp_rule_version": door._common.FP_RULE_VERSION}))
    (r / "runner_exit.json").write_text(json.dumps(
        {"reason": "done", "at": "2026-10-20T00:00:00+00:00",
         "graph_fingerprint": door._common.graph_fingerprint(g),
         "fp_rule_version": door._common.FP_RULE_VERSION}))
    (r / "events.jsonl").write_text(
        '{"ts":"2026-10-20T00:00:00+00:00","event":"run.started"}\n'
        '{"ts":"2026-10-20T00:00:01+00:00","event":"run.done"}\n')
    (r / "runner.lock").touch()   # present, unheld -> runner_lock_held False
    assert door.run_state(r)["status"] == "done"
    return r, g

def heal_graph(g):
    """The heal lane: append node b after the committed a."""
    ng = json.loads(json.dumps(g))
    ng["nodes"].append({"id": "b", "type": "agent", "goal": "heal",
                        "model": "manager", "after": ["a"]})
    return ng

def fake_alive(seq, hook=None):
    """Door-global liveness fake: seq = per-call booleans (last one sticks),
    hook(i) runs before each answer."""
    state = {"i": 0}
    def f(_r):
        i = state["i"]; state["i"] += 1
        if hook: hook(i)
        return seq[i] if i < len(seq) else seq[-1]
    return f

# ---- T1: APPLIED shape — runner dead at submit -> respawn claimed AND attempted
r, g = done_run("run-applied")
RESPAWN_CALLS.clear()
out = door.act_amend({"run_id": "run-applied", "graph": heal_graph(g)})
check("T1 dead-runner amend routes through the respawn bridge", RESPAWN_CALLS == ["run-applied"], RESPAWN_CALLS)
check("T1 applies truthfully claims the respawn", out.get("ok") and "respawned" in out.get("applies", ""), out)
check("T1 durable write applied", "b" in (r / "graph.json").read_text()
      and (r / "amends.jsonl").exists(), str(r))
check("T1 preview scheduled the heal node", out.get("will_rerun") == ["b"], out.get("will_rerun"))

# ---- T2: UNOBSERVED shape — the RED proof (dying runner, grace window all-alive)
r, g = done_run("run-dying")
RESPAWN_CALLS.clear()
_real_alive = door.runner_alive
setattr(door, "runner_alive", fake_alive((True,)))   # flock HELD window across the whole call
try:
    t0 = time.monotonic()
    out2 = door.act_amend({"run_id": "run-dying", "graph": heal_graph(g)})
finally:
    setattr(door, "runner_alive", _real_alive)
dump2 = json.dumps(out2).lower()
check("T2 response names the required re-drive (RED proof at base)", "re-drive" in dump2, dump2[:400])
check("T2 response does not claim a respawn that never happened",
      "respawned" not in dump2 and "respawn:" not in dump2, dump2[:200])
check("T2 no respawn was attempted", RESPAWN_CALLS == [], RESPAWN_CALLS)
check("T2 durable writes still happened (ok:true with real side effect)",
      out2.get("ok") is True and (r / "restart.request").exists()
      and (r / "amends.jsonl").exists() and "b" in (r / "graph.json").read_text(), str(r))

# ---- T3: CONSUMED shape — marker observed gone at runner death -> confident copy
r, g = done_run("run-consumed")
RESPAWN_CALLS.clear()
def _consume(i):
    if i == 1:   # first grace poll: the runner's post-notify boundary consumes it
        (r / "restart.request").unlink(missing_ok=True)
_real_alive = door.runner_alive
setattr(door, "runner_alive", fake_alive((True, True, True, False, False), hook=_consume))
try:
    out3 = door.act_amend({"run_id": "run-consumed", "graph": heal_graph(g)})
finally:
    setattr(door, "runner_alive", _real_alive)
dump3 = json.dumps(out3).lower()
check("T3 consumed shape reports consumption", "consumed" in out3.get("applies", ""), dump3[:400])
check("T3 consumed shape carries no re-drive hedge", "re-drive" not in dump3, dump3[:200])
check("T3 no respawn attempted for a consumed amend", RESPAWN_CALLS == [], RESPAWN_CALLS)

# ---- T4: NO-OP shape — terminal run, byte-identical resubmit (terminal fallback)
r, g = done_run("run-identical")
RESPAWN_CALLS.clear()
out4 = door.act_amend({"run_id": "run-identical", "graph": json.loads(json.dumps(g))})
dump4 = json.dumps(out4).lower()
check("T4 terminal fallback does not claim consumption", "consumed" not in out4.get("applies", ""), dump4[:400])
check("T4 terminal fallback states nothing is scheduled", "nothing scheduled" in dump4, dump4[:400])
check("T4 no respawn attempted", RESPAWN_CALLS == [], RESPAWN_CALLS)

print(f"\n{'ALL PASS' if not FAILS else 'FAILURES: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
