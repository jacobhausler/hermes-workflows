#!/usr/bin/env python3
"""Sprint-101 lane D-surface, item #15: the inline card is machinery, not a choice.

Proves, with the door module and the fake session env:
 1. act_run's response carries no `card_rule` paste-prose anywhere (source + payload).
 2. act_wait/act_status register the run's card for the WATCHING session — a
    session that never launched the run still gets the card once.
 3. Repeat waits in one turn register the same rid once (exactly-once emission).
 4. Hook-miss reproduction (core contract, agent/turn_finalizer.py: the hook is
    gated on `final_response and not interrupted`): an interrupted/blank turn
    never fires transform_llm_output — the card is NOT emitted that turn, and
    the on_session_end hold replays it at the next transform exactly once.
 5. A held launch older than _HELD_TTL_SECONDS expires instead of leaking a
    stale card into a much-later turn.

Run: /opt/hermes/.venv/bin/python3 tests/test_sprint101_D-surface.py
"""
import importlib.util, json, os, shutil, sys, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
ROOT = BUILD.parent
HOME = ROOT / "home-s101d"
os.environ["HERMES_HOME"] = str(HOME)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/opt/hermes")

spec = importlib.util.spec_from_file_location("wf_door_s101d", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)

# Share ONE ContextVar-backed session_context module (same dance as
# test_card_delivery_0924): door._session_env must read the env we bind.
import gateway  # noqa: E402
if "gateway.session_context" not in sys.modules:
    from importlib.util import spec_from_file_location
    p = Path(gateway.__file__).with_name("session_context.py")
    _ctx_spec = spec_from_file_location("gateway.session_context", p)
    _ctx = importlib.util.module_from_spec(_ctx_spec)
    sys.modules["gateway.session_context"] = _ctx
    _ctx_spec.loader.exec_module(_ctx)
sc = sys.modules["gateway.session_context"]

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

def reset(sid=None):
    with door._LAUNCH_LOCK:
        door._LAUNCHED.clear()
        door._HELD.clear()
    return sid

def bind(sid):
    # The session env layer binds ContextVars; emulate a turn of session `sid`.
    return sc.bind_session_vars({"HERMES_SESSION_ID": sid}) if hasattr(sc, "bind_session_vars") \
        else os.environ.update({"HERMES_SESSION_ID": sid})

GRAPH = {"name": "s101d", "nodes": [{"id": "one", "type": "agent", "goal": "offline"}]}

def mk_run(rid, owner="other-session"):
    """Hand-built committed run dir so act_wait/act_status need NO runner spawn."""
    r = HOME / "workflows" / rid
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps(GRAPH))
    (r / "run.json").write_text(json.dumps({"hermes_bin": "/bin/false", "name": "s101d",
                                            "owner": {"session_id": owner}}))
    node = GRAPH["nodes"][0]
    (r / "nodes" / "one.json").write_text(json.dumps(
        {"status": "done", "output": {"ok": True}, "ms": 1,
         "efp": door._common.efp({node["id"]: node}, node)}))
    (r / "runner_exit.json").write_text(json.dumps({"reason": "done", "exit": 0}))
    return r

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)
class _NoSpawn:
    def __enter__(self): return self
    def __exit__(self, *a): return False
_orig_spawn = door._spawn_runner
door._spawn_runner = lambda r: None

CARD = lambda rid: f'::workflow{{id="{rid}"}}'

try:
    # ---- 1: no card_rule anywhere (payload + source of truth) ----------------
    os.environ["HERMES_SESSION_ID"] = "session-a"
    reset()
    out = door.act_run({"graph": dict(GRAPH)})
    rid = out.get("run_id", "")
    check("act_run returns a run_id + card", bool(rid) and out.get("card") == CARD(rid), json.dumps(out)[:200])
    check("act_run response carries NO card_rule", "card_rule" not in out, json.dumps(out)[:200])
    src = (ROOT / "__init__.py").read_text(encoding="utf-8")
    check("no card_rule key remains in __init__.py", '"card_rule"' not in src)

    # ---- 2/3: wait/status register the card for the WATCHING session ---------
    os.environ["HERMES_SESSION_ID"] = "watcher"
    reset()
    rid2 = "s101d-watch-1"
    mk_run(rid2, owner="launcher-elsewhere")
    w = door.act_wait({"run_id": rid2, "timeout": 0})
    check("setup: act_wait on a committed run returns status", w.get("status") == "done", json.dumps(w)[:160])
    with door._LAUNCH_LOCK:
        registered = list(door._LAUNCHED.get("watcher", []))
    check("act_wait registered the card for the watching session", registered == [rid2], json.dumps(registered))
    # repeat waits in the same turn register once
    door.act_wait({"run_id": rid2, "timeout": 0})
    door.act_status({"run_id": rid2})
    with door._LAUNCH_LOCK:
        registered = list(door._LAUNCHED.get("watcher", []))
    check("repeat wait/status register the SAME rid once", registered == [rid2], json.dumps(registered))
    res = door._auto_card(response_text="all done", session_id="watcher")
    check("watcher's turn emits the card exactly once",
          res is not None and res.count(CARD(rid2)) == 1, repr(res)[:200])
    check("second transform of the same turn emits nothing",
          door._auto_card(response_text="more", session_id="watcher") is None)

    # ---- 4: hook-miss reproduction (interrupted turn never transforms) -------
    os.environ["HERMES_SESSION_ID"] = "session-b"
    reset()
    out_b = door.act_run({"graph": dict(GRAPH)})
    ridb = out_b["run_id"]
    # Core contract: an interrupted/blank turn never fires transform_llm_output.
    # The session-end hook moves the launch to the hold instead of dropping it.
    door._clear_launch(session_id="session-b")
    with door._LAUNCH_LOCK:
        held = [x[1] for x in door._HELD.get("session-b", [])]
    check("interrupted turn holds the launch (hook could not fire)", held == [ridb], json.dumps(held))
    replay = door._auto_card(response_text="continuing", session_id="session-b")
    check("next transform replays the card exactly once",
          replay is not None and replay.count(CARD(ridb)) == 1, repr(replay)[:200])
    check("replay happens once, not twice",
          door._auto_card(response_text="again", session_id="session-b") is None)

    # ---- 5: held launch expires past the TTL ---------------------------------
    reset()
    door._note_launch(ridc := "s101d-held-expired")
    door._clear_launch(session_id="session-b")
    with door._LAUNCH_LOCK:
        rows = door._HELD.get("session-b", [])
        door._HELD["session-b"] = [(t - door._HELD_TTL_SECONDS - 1, r) for (t, r) in rows]
    check("expired hold never replays", door._auto_card(response_text="late", session_id="session-b") is None)
finally:
    door._spawn_runner = _orig_spawn
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
