#!/usr/bin/env python3
"""est-2ek.1.699 — route IDENTITY: dotted vs hyphenated model aliases.

Field evidence run 20261005-030530-zap-banked-findings-squa: nodes pinned
claude-fable-5.1; the door's submit ping PROVED anthropic/claude-fable-5.1 alive
(route_verified baked, liveness alive) and the items completed — yet the commit
hold marked them route_unavailable because core normalizes/bills the model id as
claude-fable-5-1. The door's proof and the runner's identity law compared RAW
strings, so the same route under two spellings billed as a different one.

The fix is ONE provider normalization contract (wfcommon.canonical_model_id)
used by BOTH the submit-proof comparison (door ping same-route law) and the
actual-child identity comparisons (runner commit hold + post-admission receipt
hold). Acceptance pinned here:
  * alias pair 5.1 vs 5-1 -> proven-and-run items are NOT route_unavailable
  * a genuinely different model stays blocked (require_route NOT weakened —
    no fallback enabled, the gate itself unchanged)
  * a dead pin is still refused at submit; legacy runs (no route_verified) are
    byte-identical.
Stdlib only; the seat stub is a recording fake; no network.
"""
import importlib, json, os, sys, tempfile, types
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-routeid699-", dir=HERE / "tests")
import atexit
atexit.register(tmp_dir.cleanup)
os.environ["HERMES_HOME"] = tmp_dir.name
os.environ["WF_RUNS_ROOT"] = str(Path(tmp_dir.name) / "workflows")
os.environ["HERMES_WF_HERMES_BIN"] = "offline"

_fake_agent = types.ModuleType("agent"); _fake_agent.__path__ = []
_fake_ru = types.ModuleType("agent.retry_utils")
_fake_ru.parse_retry_after_seconds = lambda x: None
sys.modules["agent"] = _fake_agent
sys.modules["agent.retry_utils"] = _fake_ru

import wfcommon as wc
import wf as wfmod

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

DOT, HY = "claude-fable-5.1", "claude-fable-5-1"
OTHER = "claude-opus-5-5"

# ---- 0. the ONE canonical normalizer exists and is the shared contract ---------
check("canonical_model_id exported by wfcommon (the shared contract)",
      callable(getattr(wc, "canonical_model_id", None)))
if callable(getattr(wc, "canonical_model_id", None)):
    cm = wc.canonical_model_id
    check("alias pair 5.1 vs 5-1 canonicalize EQUAL",
          cm(DOT) == cm(HY), f"{cm(DOT)!r} vs {cm(HY)!r}")
    check("provider-qualified strips to the same model identity",
          cm("anthropic/" + DOT) == cm(HY) == cm("anthropic/" + HY),
          f"{cm('anthropic/' + DOT)!r} vs {cm(HY)!r}")
    check("different models stay DIFFERENT (no fuzzy equality)",
          cm(OTHER) != cm(DOT) and cm("qwen38-next") != cm(DOT))
    check("core's labeled route shape 'name(provider)' normalizes",
          cm(f"main-agent({DOT})".replace("main-agent", DOT)) == cm(HY) or
          cm(DOT + "(anthropic)") == cm(HY), cm(DOT + "(anthropic)"))
    check("case/whitespace insensitive",
          cm("  Anthropic/" + DOT.upper() + " ") == cm(HY))

# ---- 1. runner commit hold: dotted proof vs hyphenated billed -> NO hold --------
# Exact field shape: door proved anthropic/claude-fable-5.1, the row billed
# claude-fable-5-1 for a node that completed.
meta = {"_run": Path(tmp_dir.name)}
PROOF = {"model": DOT, "provider": "anthropic", "route_verified": f"anthropic/{DOT}"}
out = wfmod._route_hold(meta, {"status": "done", "served_model": HY}, PROOF)
check("commit hold: proven-and-run alias pair (5.1 proved, 5-1 billed) -> NOT route_unavailable",
      out.get("status") == "done", out)
# reverse spelling: proved hyphenated, billed dotted
out = wfmod._route_hold(meta, {"status": "done", "served_model": DOT},
                        {"model": HY, "provider": "anthropic",
                         "route_verified": f"anthropic/{HY}"})
check("commit hold: reverse spelling (5-1 proved, 5.1 billed) -> NOT route_unavailable",
      out.get("status") == "done", out)
# provider-qualified served row
out = wfmod._route_hold(meta, {"status": "done", "served_model": f"anthropic/{HY}"}, PROOF)
check("commit hold: provider-qualified billed alias passes", out.get("status") == "done", out)
# require_route NOT weakened: a genuinely different billed model still fails
out = wfmod._route_hold(meta, {"status": "done", "served_model": OTHER}, PROOF)
check("commit hold: different model billed despite alive proof -> still route_unavailable",
      out.get("status") == "failed" and out.get("error_class") == "route_unavailable", out)
out = wfmod._route_hold(meta, {"status": "done", "served_model": "qwen38-next"}, PROOF)
check("commit hold: seat fallback still route_unavailable", out.get("status") == "failed", out)
# unknown served / no proof: legacy laws byte-identical
check("commit hold: unknown served passes (never invents known)",
      wfmod._route_hold(meta, {"status": "done", "served_model": None}, PROOF)["status"] == "done")
check("commit hold: no route_verified -> no hold (legacy identity)",
      wfmod._route_hold(meta, {"status": "done", "served_model": "whatever"},
                        {"model": DOT})["status"] == "done")
# seat alias map still honored under the normalizer
seat = Path(tmp_dir.name) / "seat699"; seat.mkdir(exist_ok=True)
(seat / "config.yaml").write_text(f"model:\n  aliases:\n    {HY.replace('.', '-')}: anthropic/{DOT}\n")
class FRResult(dict):
    def get(self, k, d=None):
        return str(seat) if k == "profile_home" else dict.get(self, k, d)
out = wfmod._route_hold(meta, FRResult({"status": "done", "served_model": HY}),
                        {"model": HY, "route_verified": f"anthropic/{HY}"})
check("commit hold: seat alias spelling passes", out.get("status") == "done", out)

# ---- 2. post-admission receipt hold: same ONE contract --------------------------
# The lane has a proved-alive receipt for dotted; a re-spawn that asks the hyphenated
# spelling of the SAME route must NOT be a substitution (no self-certification
# widening: a different model stays denied).
node_dot = {"id": "plans", "type": "agent", "goal": "g",
            "provider": "anthropic", "model": DOT, "route_verified": f"anthropic/{DOT}"}
lane699 = Path(tmp_dir.name) / "lane699"; (lane699 / "nodes").mkdir(parents=True)
(lane699 / "route_receipts.json").write_text(json.dumps({"plans": f"anthropic/{DOT}"}))
r = wfmod._route_substitution_refusal({"_run": lane699},
                                      dict(node_dot, model=HY), spawn_no=2)
check("receipt hold: hyphenated re-spawn under dotted receipt is NOT a substitution",
      r is None, r)
r = wfmod._route_substitution_refusal({"_run": lane699},
                                      dict(node_dot, model=OTHER), spawn_no=2)
check("receipt hold: different model under the receipt is STILL denied",
      isinstance(r, dict) and r.get("error_class") == "route_substitution_denied", r)
# receipt file shape (the durable lane receipt) held to the same contract
run699 = Path(tmp_dir.name) / "run699"; (run699 / "nodes").mkdir(parents=True)
(run699 / "route_receipts.json").write_text(json.dumps({"plans": f"anthropic/{DOT}"}))
r = wfmod._route_substitution_refusal({"_run": run699},
                                      {"id": "plans", "type": "agent",
                                       "provider": "anthropic", "model": HY}, 3)
check("receipt hold (durable file): alias spelling re-spawn passes the receipt",
      r is None, r)
r = wfmod._route_substitution_refusal({"_run": run699},
                                      {"id": "plans", "type": "agent",
                                       "provider": "x", "model": OTHER}, 3)
check("receipt hold (durable file): different model still refused BEFORE submit",
      isinstance(r, dict) and r.get("error_class") == "route_substitution_denied", r)
check("receipt hold: absent receipt never fires",
      wfmod._route_substitution_refusal({"_run": Path(tmp_dir.name) / "nope"},
                                        {"id": "x", "provider": "a", "model": "m"}, 1) is None)

# ---- 3. door side: the submit-ping same-route law uses the SAME normalizer ------
door = importlib.import_module("__init__")
import wf_test_isolation as _iso71; _iso71.install(door)
door._CTX = None
door._seat_model_cfg = lambda: {"default": "seat-default", "aliases": {}}
door._seat_aliases = lambda: []
door._seat_default = lambda: "seat-default"
_spawned = []
door._spawn_runner = lambda r: _spawned.append(r.name)

# core records the ping route with ITS normalized (hyphenated) spelling; the
# pinned node is dotted. Under one contract the recorded route IS the pinned route.
check("door same-route law: hyphenated recorded route matches dotted pin",
      door._same_ping_route({"provider": "anthropic", "model": HY}, "anthropic", DOT))
check("door same-route law: dotted recorded route matches hyphenated pin",
      door._same_ping_route({"provider": "anthropic", "model": DOT}, "anthropic", HY))
check("door same-route law: different model on the pin is NOT same-route",
      not door._same_ping_route({"provider": "anthropic", "model": OTHER}, "anthropic", DOT))
check("door same-route law: provider mismatch is NOT same-route (gate intact)",
      not door._same_ping_route({"provider": "other", "model": DOT}, "anthropic", DOT))
check("door same-route law: labeled 'model(anthropic)' shape still normalizes",
      door._same_ping_route({"provider": "anthropic", "model": f"{HY}(anthropic)"},
                            "anthropic", DOT))

def set_ping(behavior):
    if behavior is None:
        door._import_call_llm = lambda: (_ for _ in ()).throw(ImportError("No module named 'agent'"))
        return
    def call_llm(task=None, provider=None, model=None, messages=None, max_tokens=None,
                 timeout=None, route_info=None, **kw):
        if route_info is not None:
            route_info.update(behavior.get("record",
                                {"provider": str(provider or ""), "model": str(model or "")}))
        exc = behavior.get("raise_")
        if exc is not None:
            raise exc
        return "pong"
    door._import_call_llm = lambda: call_llm

class HTTP429(Exception): pass

def pinned_graph(**extra):
    n = {"id": "plans", "type": "agent", "goal": "x",
         "provider": "anthropic", "model": DOT}
    n.update(extra)
    return {"name": "p699", "nodes": [n]}

# alive pin under the dotted name bakes route_verified and launches
set_ping({"record": {"provider": "anthropic", "model": HY}})   # core answers normalized
out = door.act_run({"graph": pinned_graph()})
check("door: normalized ping answer on the pinned route counts ALIVE (launches, no refusal)",
      bool(out.get("run_id")), out)
if out.get("run_id"):
    gj = json.loads((Path(os.environ["WF_RUNS_ROOT"]) / out["run_id"] / "graph.json").read_text())
    check("door: alive pin bakes route_verified (require_route machinery intact)",
          gj["nodes"][0].get("route_verified") == f"anthropic/{DOT}", gj["nodes"][0])

# dead pin STILL refused — the gate is NOT softened
set_ping({"raise_": HTTP429("Error code: 429 - rate limited"),
          "record": {"provider": "anthropic", "model": HY}})
out = door.act_run({"graph": pinned_graph()})
check("dead pin still REFUSED at submit (gate not softened, no fallback enabled)",
      "error" in out and "route_unavailable at submit" in out.get("error", "")
      and DOT in out.get("error", ""), out)

# fallback-ladder surprise (different model recorded) STILL refused
set_ping({"record": {"provider": "openai", "model": "gpt-6-sol-900k"}})
out = door.act_run({"graph": pinned_graph()})
check("fallback-ladder surprise still REFUSED (wrong_route law intact)",
      "error" in out and "FALLBACK LADDER" in out.get("error", "").upper(), out)

# infra-absence stays unknown = launches
set_ping(None)
out = door.act_run({"graph": pinned_graph()})
check("core-absence never blocks (fail-open on absence unchanged)",
      bool(out.get("run_id")), out)

sys.exit(1 if fails else 0)
