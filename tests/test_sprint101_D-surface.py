#!/usr/bin/env python3
"""Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is
agent-authored — the auto-card hook machine is DELETED (wf-11 O1), so the
hook-registration, watching-session registration, interrupted-turn hold and
TTL-expiry assertions that referenced _LAUNCHED/_HELD/_auto_card are gone
with it. What remains:
 1. act_run's response carries no `card_rule` paste-prose anywhere (source + payload).
 2. act_run's payload carries the exact card, and the hint is the copy-exact
    paste line (papercut #70).
 3. status/wait payloads carry the same card for any reading session (the
    watching session gets the line in the payload; emitting it is the agent's
    job, not the backend's).
 4. The hook machine's symbols are gone from the shipped door module.
 5. STRUCTURAL LAW (P1): ALL hook registrations flow through the plugin's
    register(), gated by the config allow-list (settings.enabled_hooks); the
    expected count comes FROM CONFIG (door._hook_allowlist()), never a hardcoded
    1 — the shipped default surface (unset config) is #157's card-enforcement
    hook, and narrowing/failing the allow-list moves the registered count.

Run: /opt/hermes/.venv/bin/python3 tests/test_sprint101_D-surface.py
"""
# Ledger 95d7010295d70102: stamped fixtures verify under their own rule; ambiguous unstamped records fail closed.
import importlib.util, json, os, shutil, sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
ROOT = BUILD.parent
HOME = ROOT / "home-s101d"
# #71: HERMES_HOME alone does NOT sandbox the shelf — the context-local home
# override outranks the env in lane processes; WF_RUNS_ROOT is checked first and
# pins runs/library wherever the door resolves. Without it, saves pollute prod.
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/opt/hermes")

spec = importlib.util.spec_from_file_location("wf_door_s101d", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso71; _iso71.install(door)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

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
         "efp": door._common.efp({node["id"]: node}, node), "fp_rule_version": door._common.FP_RULE_VERSION}))
    (r / "runner_exit.json").write_text(json.dumps({"reason": "done", "exit": 0}))
    return r

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)
_orig_spawn = door._spawn_runner
door._spawn_runner = lambda r: None

CARD = lambda rid: f'::workflow{{id="{rid}"}}'

try:
    # ---- 1: no card_rule anywhere (payload + source of truth) ----------------
    os.environ["HERMES_SESSION_ID"] = "session-a"
    out = door.act_run({"graph": dict(GRAPH)})
    rid = out.get("run_id", "")
    check("act_run returns a run_id + card", bool(rid) and out.get("card") == CARD(rid), json.dumps(out)[:200])
    check("act_run response carries NO card_rule", "card_rule" not in out, json.dumps(out)[:200])
    src = (ROOT / "__init__.py").read_text(encoding="utf-8")
    check("no card_rule key remains in __init__.py", '"card_rule"' not in src)
    # O1 copy-exact hint (papercut #70): the hint names the paste line verbatim.
    check("hint makes cards optional",
          "desktop cards are optional" in out.get("hint", "")
          and CARD(rid) in out.get("lifecycle_notice", ""), repr(out.get("hint"))[:200])

    # ---- 2: any reading session gets the card in the payload -----------------
    os.environ["HERMES_SESSION_ID"] = "watcher"
    rid2 = "s101d-watch-1"
    mk_run(rid2, owner="launcher-elsewhere")
    w = door.act_wait({"run_id": rid2, "timeout": 0})
    check("setup: act_wait on a committed run returns status", w.get("status") == "done", json.dumps(w)[:160])
    check("act_wait payload carries the card for the watching session",
          w.get("card") == CARD(rid2), json.dumps(w)[:200])
    s = door.act_status({"run_id": rid2})
    check("act_status payload carries the card", s.get("card") == CARD(rid2), json.dumps(s)[:200])

    # ---- 4: the hook machine is gone from the shipped module -----------------
    for sym in ("_auto_card", "_note_launch", "_clear_launch", "_take_held",
                "_visible_cards", "_LAUNCHED", "_HELD", "_HELD_TTL_SECONDS",
                "_LAUNCH_LOCK", "_VISIBLE_CARD_RE", "_CARD_ATTR_RE"):
        check(f"symbol {sym} no longer exists on the door", not hasattr(door, sym))
    # ---- 5: STRUCTURAL LAW (P1): hook registrations flow through register()
    # gated by the config allow-list; the count comes FROM CONFIG, never a
    # hardcoded number. The card ledger's three hooks (post_tool_call records
    # launches, pre_llm_call reminds, transform_llm_output ships) are the literal
    # sites; PR-3's flag-gated admission/witness pair and PR-4's default-on orphan-held
    # observers (orphan_watch.HOOKS) ride the ONE variable-named loop over the surface.
    import re as _re
    _reg_src = src[src.index("def register(ctx):"):]
    _sites = _re.findall(r'ctx\.register_hook\(\s*["\']([A-Za-z0-9_]+)["\']', _reg_src)
    _surface = dict(door._hook_surface())
    _GATED_ADDITIONS = {"subagent_stop"}  # P3 config-gated lane: a literal site of its own, gated by its own allow-list, pinned by tests/test_subagent_accounting_p3.py
    check("every ctx.register_hook site lives in register() and names a surface or gated-addition hook",
          len(_sites) >= 1 and all(n in _surface or n in _GATED_ADDITIONS for n in _sites), str(_sites))
    check("the literal sites are the card ledger's three hooks (plus sanctioned config-gated additions)",
          sorted(n for n in _sites if n not in _GATED_ADDITIONS)
          == sorted(door._CARD_HOOKS) == sorted(["post_tool_call", "pre_llm_call", "transform_llm_output"]),
          str(_sites))
    check("the gate is one allow-list read and every site is membership-gated",
          "_hooks = _hook_allowlist()" in _reg_src
          and all(_re.search(rf'if "{n}" in _hooks:\s*\n\s*ctx\.register_hook\("{n}"', _reg_src)
                  for n in _sites if n not in _GATED_ADDITIONS))
    _loops = _re.findall(r'if _hook in _hooks:\s*\n\s*try:\s*\n\s*ctx\.register_hook\(_hook, _fn\)', _reg_src)
    check("the PR-3 + PR-4 variable-named loop site is membership-gated too, and no other site exists",
          len(_loops) == 1
          and _reg_src.count("ctx.register_hook(") == len(_sites) + _reg_src.count("ctx.register_hook(_hook, _fn)"),
          f"literal={_sites} loop={len(_loops)}")
    _orphan_names = list(door._orphan_watch.HOOKS)
    check("PR-4 orphan observers are on the surface (default-on, byte-identical when the allow-list is unset) and reach register() only via the gated loop",
          len(_orphan_names) >= 1 and all(n in _surface for n in _orphan_names)
          and all(_surface[n] is door._orphan_watch.HOOKS[n] for n in _orphan_names)
          and "_orphan_watch.HOOKS" not in _reg_src and "ctx.register_hook(_hn" not in _reg_src,
          str(_orphan_names))

    class _StubCtx:
        def __init__(self):
            self.hooks = []
        def register_skill(self, *a, **k):
            pass
        def register_tool(self, *a, **k):
            pass
        def register_command(self, *a, **k):
            pass
        def register_hook(self, name, fn):
            self.hooks.append(name)

    _prev_ctx = door._CTX
    _prev_reader = door._common._OWNER_SETTING_READER
    try:
        _c1 = _StubCtx(); door.register(_c1)
        check("registered set == the config allow-list (count from config, unset -> shipped surface)",
              _c1.hooks == door._hook_allowlist() == [h for h, _f in door._hook_surface()])
        door._common.set_owner_setting_reader(
            lambda k: [] if k == "enabled_hooks" else _prev_reader(k))
        _c2 = _StubCtx(); door.register(_c2)
        check("allow-list [] registers zero hooks — the count FOLLOWED config", _c2.hooks == [])
        door._common.set_owner_setting_reader(
            lambda k: ["no_such_hook"] if k == "enabled_hooks" else _prev_reader(k))
        _c3 = _StubCtx(); door.register(_c3)
        check("allow-list of a non-surface name registers zero hooks (intersect, no widening)",
              _c3.hooks == [] and door._hook_allowlist() == [])
        door._common.set_owner_setting_reader(
            lambda k: ["post_tool_call", "pre_gateway_dispatch", "on_session_end", "no_such_hook"]
            if k == "enabled_hooks" else _prev_reader(k))
        _c4 = _StubCtx(); door.register(_c4)
        check("allow-list subset registers exactly the intersection (literal site + loop sites, PR-3 and PR-4 names)",
              sorted(_c4.hooks) == ["on_session_end", "post_tool_call", "pre_gateway_dispatch"])
        door._common.set_owner_setting_reader(
            lambda k: "not-a-list" if k == "enabled_hooks" else _prev_reader(k))
        check("malformed allow-list fails CLOSED (zero hooks)", door._hook_allowlist() == [])
    finally:
        door._common.set_owner_setting_reader(_prev_reader)
        door._CTX = _prev_ctx
finally:
    door._spawn_runner = _orig_spawn
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
