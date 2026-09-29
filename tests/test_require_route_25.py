#!/usr/bin/env python3
"""#25 (haus-fixer) — fail-closed pinned routes, default ON.

fb-fix-9c575645: nodes pinned openai-codex/gpt-6-sol-900k while the submit ping had
ALREADY reported "ping answered by a different route (fallback ladder)" — and the
door spawned anyway; three whole nodes silently billed the seat's fallback.
The 1.0.14 served-model stamp caught it post-hoc; this test pins the GATE:
  * dead pin + require_route true (default on pinned nodes) -> launch REFUSED
  * fallback-ladder surprise on a pin                  -> launch REFUSED
  * require_route:false                                 -> the OLD warn-and-surface
    contract (annotated, launched) — the opt-out is byte-the-old-behavior
  * unknown from INFRA absence (core not importable)    -> launches (no false block)
  * alive pin                                           -> launches + bakes
    route_verified, and the runner's commit hold fails a mismatched served_model
    (route_unavailable) while a matching / unknown served_model passes.
Stdlib only; the core seam is stubbed; no network.
"""
import importlib, atexit, json, os, sys, tempfile, types
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-reqroute25-", dir=HERE / "tests")
atexit.register(tmp_dir.cleanup)
os.environ["HERMES_HOME"] = tmp_dir.name
os.environ["HERMES_WF_HERMES_BIN"] = "offline"

_fake_agent = types.ModuleType("agent"); _fake_agent.__path__ = []
_fake_ru = types.ModuleType("agent.retry_utils")
_fake_ru.parse_retry_after_seconds = lambda x: None
sys.modules["agent"] = _fake_agent
sys.modules["agent.retry_utils"] = _fake_ru

door = importlib.import_module("__init__")
door._CTX = None
door._seat_model_cfg = lambda: {"default": "seat-default", "aliases": {}}
door._seat_aliases = lambda: []
door._seat_default = lambda: "seat-default"
_spawned = []
door._spawn_runner = lambda r: _spawned.append(r.name)

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

def set_ping(behavior):
    if behavior is None:
        door._import_call_llm = lambda: (_ for _ in ()).throw(ImportError("No module named 'agent'"))
        return
    def call_llm(task=None, provider=None, model=None, messages=None, max_tokens=None,
                 timeout=None, route_info=None, **kw):
        if route_info is not None:
            route_info.update(behavior.get("record", {"provider": str(provider or ""), "model": str(model or "")}))
        exc = behavior.get("raise_")
        if exc is not None:
            raise exc
        return "pong"
    door._import_call_llm = lambda: call_llm

class HTTP429(Exception): pass

def pinned_graph(**extra):
    n = {"id": "a", "type": "agent", "goal": "x", "provider": "openai", "model": "m-1"}
    n.update(extra)
    return {"name": "p25", "nodes": [n]}

# ---- 1. DEAD pin, default (no require_route key at all) -> REFUSE -------------------
set_ping({"raise_": HTTP429("Error code: 429 - rate limited")})
out = door.act_run({"graph": pinned_graph()})
check("dead pin: launch refused, error names the node and the route",
      "error" in out and "'a'" in out.get("error", "") and "openai/m-1" in out.get("error", "")
      and "route_unavailable at submit" in out.get("error", ""), out)
check("dead pin: NOTHING spawned", len(_spawned) == 0, _spawned)

# ---- 2. fallback-ladder surprise on a pin -> REFUSE (the fb-fix-9c575645 shape) ----
set_ping({"record": {"provider": "fallback_chain[0](other)", "model": "qwen-fallback"}})
out = door.act_run({"graph": pinned_graph()})
check("fallback-ladder surprise: launch refused",
      "error" in out and "FALLBACK LADDER" in out.get("error", ""), out)
check("surprise: nothing spawned", len(_spawned) == 0, _spawned)

# ---- 3. opt-out: the OLD warn-and-surface contract, verbatim ------------------------
set_ping({"raise_": HTTP429("Error code: 429 - rate limited")})
n_before = len(_spawned)
out = door.act_run({"graph": pinned_graph(require_route=False)})
check("require_route:false + dead: launches, annotated dead, hint rides",
      out.get("run_id") and out["routes"]["a"]["liveness"] == "dead"
      and len(_spawned) == n_before + 1, out)
n_before = len(_spawned)
set_ping({"record": {"provider": "fallback_chain[0](other)", "model": "qwen-fallback"}})
out = door.act_run({"graph": pinned_graph(require_route=False)})
check("require_route:false + surprise: launches, unknown+not-counted",
      out.get("run_id") and out["routes"]["a"]["liveness"] == "unknown"
      and "not counted as alive" in out["routes"]["a"].get("note", ""), out)

# ---- 4. INFRA absence never false-blocks: core not importable -> unknown -> LAUNCH -
set_ping(None)
n_before = len(_spawned)
out = door.act_run({"graph": pinned_graph()})
check("core not importable: unknown -> launches anyway (no false block)",
      out.get("run_id") and out["routes"]["a"]["liveness"] == "unknown"
      and len(_spawned) == n_before + 1, out)

# ---- 5. unpinned node: nothing to hold, ever ---------------------------------------
set_ping({"raise_": HTTP429("Error code: 429 - nope")})
out = door.act_run({"graph": {"name": "u", "nodes": [{"id": "a", "type": "agent", "goal": "x"}]}})
check("unpinned node: launches (no pin, no hold)", bool(out.get("run_id")), out)

# ---- 6. graph defaults.require_route:false opts the whole graph in to the ladder ---
_g = pinned_graph()
_g["defaults"] = {"require_route": False}
out = door.act_run({"graph": _g})
check("defaults.require_route:false respected", bool(out.get("run_id")), out)

# ---- 7. boolean-only validation ------------------------------------------------------
out = door.act_run({"graph": pinned_graph(require_route="yes-please")})
check("require_route must be boolean (rejected pre-write)",
      "error" in out and "boolean" in json.dumps(out), out)
out = door.act_run({"graph": dict(pinned_graph(), defaults={"require_route": "sure"})})
check("defaults.require_route must be boolean",
      "error" in out and "boolean" in json.dumps(out), out)

# ---- 8. alive pin: launches + bakes route_verified into graph.json -------------------
set_ping({})
out = door.act_run({"graph": pinned_graph()})
rid = out.get("run_id")
check("alive pin launches", bool(rid), out)
if rid:
    gj = json.loads((Path(os.environ["HERMES_HOME"]) / "workflows" / rid / "graph.json").read_text())
    check("alive proof baked: route_verified=openai/m-1",
          gj["nodes"][0].get("route_verified") == "openai/m-1", gj["nodes"][0])

# ---- 9. the runner commit hold: served mismatch fails, match/unknown pass -----------
import wf as wfmod
class Meta(dict): pass
meta = Meta({"_run": Path(tmp_dir.name)})
PROOF = {"model": "gpt-6-sol-900k", "provider": "openai-codex",
         "route_verified": "openai-codex/gpt-6-sol-900k"}
# mismatch: door proved openai/m-1, row says the fallback served it
r = {"status": "done", "served_model": "qwen38-next"}
out2 = wfmod._route_hold(meta, dict(r), PROOF)
check("commit hold: fallback served despite alive-proof -> route_unavailable",
      out2.get("status") == "failed" and out2.get("error_class") == "route_unavailable", out2)
check("commit hold: the record NEVER carries node_def (golden-solo leak guard)",
      "node_def" not in out2, out2)
# match (literal)
check("commit hold: matching served_model passes",
      wfmod._route_hold(meta, {"status": "done", "served_model": "gpt-6-sol-900k"}, PROOF)["status"] == "done")
# match (provider/model form recorded by core)
check("commit hold: provider-qualified served matches",
      wfmod._route_hold(meta, {"status": "done", "served_model": "openai-codex/gpt-6-sol-900k"}, PROOF)["status"] == "done")
# unknown served (no row): never counted
check("commit hold: unknown served passes (never invents known)",
      wfmod._route_hold(meta, {"status": "done", "served_model": None}, PROOF)["status"] == "done")
# no proof key: legacy runs byte-behave (no hold)
check("commit hold: no route_verified -> no hold (legacy identity)",
      wfmod._route_hold(meta, {"status": "done", "served_model": "whatever"},
                        {"model": "m-1"})["status"] == "done")
# alias match via seat config
seat = Path(tmp_dir.name) / "seatA"; seat.mkdir(exist_ok=True)
(seat / "config.yaml").write_text("model:\n  aliases:\n    sol: openai-codex/gpt-6-sol-900k\n")
class FRResult(dict):
    def get(self, k, d=None):
        return str(seat) if k == "profile_home" else dict.get(self, k, d)
out5 = wfmod._route_hold(meta, FRResult({"status": "done", "served_model": "sol"}),
                         {"model": "sol", "route_verified": "openai-codex/gpt-6-sol-900k"})
check("commit hold: alias that resolves to the verified route passes",
      out5.get("status") == "done", out5)

# ---- 10. gate/echo nodes are never gated --------------------------------------------
set_ping({"raise_": HTTP429("Error code: 429 - nope")})
out = door.act_run({"graph": {"name": "g", "nodes": [
    {"id": "a", "type": "agent", "goal": "x"},
    {"id": "g1", "type": "gate", "after": ["a"], "question": "?", "options": ["y"]},
    {"id": "e1", "type": "echo", "after": ["g1"], "output": {}}]}})
check("gate/echo never route-gated", bool(out.get("run_id")), out)

print("ALL PASS" if fails == 0 else f"FAILURES: {fails}")
sys.exit(0 if fails == 0 else 1)
