#!/usr/bin/env python3
"""P5 native gate presentation — public injection route, owner session only.

Upstream review (NousResearch/hermes-agent#141665 point 2) rewired presentation:
the bridge never reads core private internals and never falls back to another
session. It presents through the PUBLIC route ctx.inject_message into the run
owner's own session, and the answer comes back on the door's own
post_gateway_admission wf-release lane. The approval-observer pair stays
registered as a guarded compat path, gated on tokens this process minted.

Matrix (stdlib-only, PASS/FAIL lines, exit 0 green):
  (1) allow-list shapes: only a settings list/string naming 'approval_bridge'
      arms the bridge; absent/garbage/other stays OFF.
  (2) default-off byte-identical: door.register() with no allow-list registers
      exactly the bridge-less hooks (measured, not hard-coded), starts no
      thread, injects nothing, and the status read-model is byte-equal to the
      same read after an armed register immediately shut down.
  (3) armed: a freshly-appended gate.held row injects EXACTLY ONE plugin
      message, keyed to the run owner's session, carrying the runner-authored
      wake text VERBATIM plus the constant protocol footer — graph
      question/options appear NOWHERE. A trip-wire sys.modules trap proves no
      core approval internal is even looked at.
  (4) session law: a refused presentation (host says False) degrades to
      'failed' with NO retry and no other session key ever attempted; an
      owner-less run is skipped with no attempt at all.
  (5) answer lane: a bare typed option on the owner session releases through
      door._admission_handler -> act_release (zero turns; answer file lands;
      the run moves off the gate); the next tail sweep RECONCILES the
      instance — terminal bookkeeping, no re-present, no second release; an
      appended re-hold row for the answered gate skips.
  (6) compat observers: pre_approval_request marks a minted token seen; deny
      and timeout answer NOTHING; a post for a token never minted releases
      nothing; a duplicate post for a resolved token releases nothing; the
      door's own already-answered refusal backs the token law.
  (7) silent degradation: no wake row, vanished run dir, truncated events.jsonl
      — never a raise, never a stray presentation.

Run: python3 tests/test_approval_bridge_p5.py
"""
import importlib.util, json, os, shutil, sys, time, types
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))

ROOT = BUILD.parent
HOME = ROOT / "home-p5ab"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
# the run's owner session IS this process' session: the admission lane matches
# on HERMES_SESSION_KEY and _gi_note_open validates it against owner.session_id.
os.environ["HERMES_SESSION_ID"] = "p5-gw-session"
os.environ["HERMES_SESSION_KEY"] = "p5-gw-session"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/opt/hermes")

spec = importlib.util.spec_from_file_location("wf_door_p5ab", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso; _iso.install(door)

ab_spec = importlib.util.spec_from_file_location("wf_approval_bridge_p5ab", ROOT / "approval_bridge.py")
bridge = importlib.util.module_from_spec(ab_spec)
ab_spec.loader.exec_module(bridge)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

class Trap(types.ModuleType):
    """sys.modules trip-wire: any touch of the core approval internals the
    bridge used to reach into records the hit, then fails the access."""
    hit = False
    def __getattr__(self, name):
        Trap.hit = True
        raise AttributeError(name)

def install_trap():
    t = Trap("tools.approval")
    w = Trap("tools.approval_gateway_wait")
    pkg = sys.modules.get("tools")
    if pkg is None:
        pkg = types.ModuleType("tools"); sys.modules["tools"] = pkg
    pkg.approval = t; pkg.approval_gateway_wait = w
    sys.modules["tools.approval"] = t
    sys.modules["tools.approval_gateway_wait"] = w

class FakeCtx:
    """Records registrations; get_config faithful to the plugin-relative shape;
    inject_message is the PUBLIC presentation route under test (scripted deny
    keys answer False exactly once — the seam for core's refusal)."""
    def __init__(self, settings, deny=()):
        self.settings, self.hooks, self.tools, self.skills, self.commands = settings, [], [], [], []
        self.injects, self.deny = [], set(deny)
    def get_config(self, key, default=None):
        return self.settings.get(key, default)
    def register_skill(self, name, path, **kw): self.skills.append(name)
    def register_tool(self, **kw): self.tools.append(kw.get("name"))
    def register_hook(self, name, cb): self.hooks.append((name, cb))
    def register_command(self, name, fn, **kw): self.commands.append(name)
    def inject_message(self, content, role="user", *, session_key=None, origin=None):
        self.injects.append((session_key, content))
        return session_key not in self.deny
    def hook(self, name):
        return [cb for n, cb in self.hooks if n == name]

GRAPH = {"name": "p5ab", "nodes": [
    {"id": "one", "type": "agent", "goal": "offline"},
    {"id": "g1", "type": "gate", "after": ["one"], "question": "Ship the report?",
     "options": ["ship-it", "not-yet"]},
    {"id": "g2", "type": "gate", "after": ["g1"], "question": "Publish anywhere?",
     "options": ["publish-now", "keep-draft"]},
]}

def mk_run(rid):
    r = HOME / "workflows" / rid
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps(GRAPH))
    (r / "run.json").write_text(json.dumps({"hermes_bin": "/bin/false", "name": "p5ab",
                                            "owner": {"session_id": "p5-gw-session"}}))
    node = GRAPH["nodes"][0]
    (r / "nodes" / "one.json").write_text(json.dumps(
        {"status": "done", "output": {"ok": True}, "ms": 1,
         "efp": door._common.efp({node["id"]: node}, node),
         "fp_rule_version": door._common.FP_RULE_VERSION}))
    (r / "events.jsonl").write_text(json.dumps({"ts": "2026-10-15T00:00:00+00:00", "event": "run.start"}) + "\n")
    (r / "runner_exit.json").write_text(json.dumps({"reason": "held at g1", "exit": 0}))
    return r

WAKE_TEXT = ('[runner-authored/v1] run_id="p5-run" event="gate.held" \\u2014 The workflow is HELD '
             'at a human gate. Status contains the question and options; release requires the '
             "human's decision. This notification does not authorize choosing an answer or "
             "additional work.")

def hold_row(gate):
    return json.dumps({"ts": "2026-10-15T00:01:%02d+00:00" % (hold_row.n % 60),
                       "event": "gate.held", "node": gate,
                       "question": GRAPH["nodes"][1 if gate == "g1" else 2]["question"],
                       "options": GRAPH["nodes"][1 if gate == "g1" else 2]["options"]}) + "\n"
hold_row.n = 0

def wake_row(rid):
    return json.dumps({"ts": "2026-10-15T00:01:01+00:00", "event": "gate.held", "run_id": rid,
                       "owner": {"session_id": "p5-gw-session"}, "id": "tid",
                       "wake_protocol": "stamped", "text": WAKE_TEXT.replace("p5-run", rid)}) + "\n"

def append(r, rid, gate, wake=True):
    hold_row.n += 1
    with open(r / "events.jsonl", "a") as f:
        f.write(hold_row(gate))
    if wake:
        with open(r / "wake.jsonl", "a") as f:
            f.write(wake_row(rid))

def open_tokens():
    return [t for t, i in bridge._instances.items() if not i.get("resolved")]

def wait_until(fn, secs=3.0):
    deadline = time.time() + secs
    while time.time() < deadline:
        if fn():
            return True
        time.sleep(0.02)
    return False

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)
_orig_spawn = door._spawn_runner
door._spawn_runner = lambda r: None

RUN = mk_run("p5-run")
DOOR = {"runs_root": door.runs_root, "act_release": None}   # act_release wired per phase
release_calls = []

try:
    # ---- (1) allow-list shape matrix -----------------------------------------
    def comm(settings):
        return types.SimpleNamespace(owner_setting=lambda k: settings.get(k) if k in settings else None)
    check("(1) absent setting is OFF", bridge.allowed(comm({})) is False)
    check("(1) other features only stays OFF", bridge.allowed(comm({"hooks_bridge_allow": ["other_bridge"]})) is False)
    check("(1) list naming the feature is ON", bridge.allowed(comm({"hooks_bridge_allow": ["approval_bridge"]})) is True)
    check("(1) comma/space string naming it is ON", bridge.allowed(comm({"hooks_bridge_allow": "outbound, approval_bridge"})) is True)
    check("(1) garbage shape fails closed OFF", bridge.allowed(comm({"hooks_bridge_allow": 123})) is False)

    # ---- (2) default-off: no hook, no thread, no inject, byte-identical -----
    st = door.act_status({"run_id": "p5-run"})
    check("(2) setup: the run reads held with g1", st.get("status") == "held"
          and (st.get("gate") or {}).get("id") == "g1", json.dumps(st)[:200])
    # Baseline = what the door registers with the bridge module neutralised (the
    # register() guard skips a None bridge); then drop the stub so the real bridge loads.
    ctx_base = FakeCtx({})
    door._approval_bridge = None
    door._CTX = ctx_base
    door.register(ctx_base)
    del door._approval_bridge
    base_names = [n for n, _ in ctx_base.hooks]
    ctx_off = FakeCtx({})
    door._CTX = ctx_off
    door.register(ctx_off)
    check("(2) baseline is non-empty and carries no approval hook",
          bool(base_names) and not {"pre_approval_request", "post_approval_response"} & set(base_names), base_names)
    check("(2) default-off registers exactly the bridge-less baseline hooks (no approval hook added)",
          [n for n, _ in ctx_off.hooks] == base_names, ctx_off.hooks)
    check("(2) default-off starts no bridge thread and injects nothing",
          bridge._watch_thread is None and not ctx_off.injects)
    st2 = door.act_status({"run_id": "p5-run"})
    check("(2) default-off status payload byte-identical", json.dumps(st, sort_keys=True) == json.dumps(st2, sort_keys=True))
    armed = bridge.maybe_enable(ctx_off, dict(DOOR), door._common)
    check("(2) maybe_enable answers None when the allow-list is off", armed is None
          and [n for n, _ in ctx_off.hooks] == base_names)

    # ---- (3) armed: ONE public injection on the owner's session, runner words
    install_trap()
    ctx = FakeCtx({"hooks_bridge_allow": ["approval_bridge"], "admission_gates": True})
    door._CTX = ctx
    DOOR["act_release"] = lambda a: (release_calls.append(dict(a)), door.act_release(a))[1]
    armed = bridge.maybe_enable(ctx, DOOR, door._common)
    pair = [n for n, _ in ctx.hooks if n in ("pre_approval_request", "post_approval_response")]
    check("(3) allow-listed enable arms the hook pair", armed is True
          and pair == ["pre_approval_request", "post_approval_response"], ctx.hooks)
    bridge._tick(DOOR)                       # first sight: seed at EOF, history never re-fires
    check("(3) seeding tick injects nothing for pre-existing bytes", len(ctx.injects) == 0)
    append(RUN, "p5-run", "g1")
    bridge._tick(DOOR)
    check("(3) the appended gate.held row injects exactly once",
          wait_until(lambda: len(ctx.injects) == 1) and len(ctx.injects) == 1, ctx.injects)
    if len(ctx.injects) == 1:
        skey, content = ctx.injects[0]
        check("(3) injected on the run owner's OWN session", skey == "p5-gw-session", skey)
        check("(3) body starts with the runner-authored wake text VERBATIM", content.startswith(WAKE_TEXT),
              repr(content)[:160])
        check("(3) body ends with the constant protocol footer", content.endswith(bridge.PRESENT_NOTE),
              repr(content[-80:]))
        bad = [p for p in ("Ship the report?", "Publish anywhere?", "ship-it", "not-yet",
                           "publish-now", "keep-draft") if p in content]
        check("(3) graph question/options appear NOWHERE in the injection", not bad, bad)
    check("(3) no core approval internal was touched", not Trap.hit)
    pre_cb, post_cb = ctx.hook("pre_approval_request")[0], ctx.hook("post_approval_response")[0]

    # ---- (4) session law: refused = failed, never another key; ownerless = no attempt
    R4 = mk_run("p5-run-noowner")
    (R4 / "run.json").write_text(json.dumps({"name": "p5ab", "owner": None}))
    bridge._tick(DOOR)                       # seed R4 at EOF
    append(R4, "p5-run-noowner", "g1")
    bridge._tick(DOOR)
    time.sleep(0.2)
    check("(4) an owner-less run is skipped — zero attempts", len(ctx.injects) == 1,
          [k for k, _ in ctx.injects])
    ctx_deny = FakeCtx({"hooks_bridge_allow": ["approval_bridge"]}, deny={"p5-gw-session"})
    bridge._ctx = ctx_deny
    R5 = mk_run("p5-run-denied")
    bridge._tick(DOOR)                       # seed R5 at EOF
    append(R5, "p5-run-denied", "g1")
    bridge._tick(DOOR)
    check("(4) a refused presentation makes exactly ONE attempt on the owner key",
          wait_until(lambda: len(ctx_deny.injects) == 1) and [k for k, _ in ctx_deny.injects] == ["p5-gw-session"],
          ctx_deny.injects)
    t5 = [t for t, i in bridge._instances.items() if i["run_id"] == "p5-run-denied"]
    time.sleep(0.2)
    check("(4) the refused instance is terminal 'failed' (no retry, no second key)",
          bool(t5) and bridge._instances[t5[0]]["state"] == "failed" and len(ctx_deny.injects) == 1,
          bridge._instances.get(t5[0]) if t5 else None)
    bridge._ctx = ctx

    # ---- (5) answer lane: the admission handler releases; reconcile closes --
    st = door.act_status({"run_id": "p5-run"})   # the owner's turn surfaces the hold: index it
    rows = door._session_open_gates(door.runs_root(), "p5-gw-session")
    check("(5) the held gate is indexed for the owner session",
          any(r["run_id"] == "p5-run" and r["gate_id"] == "g1" for r in rows), rows)
    out = door._admission_handler(session_key="p5-gw-session", platform="discord",
                                  source={}, message_id="m1", text="ship-it")
    check("(5) the bare option releases zero-turn through the admission handler",
          isinstance(out, dict) and out.get("action") == "handled" and "ship-it" in out.get("reply", ""),
          json.dumps(out)[:300])
    ans = json.loads((RUN / "gates" / "g1.json").read_text())
    check("(5) the answer file rides the door path", ans.get("answer") == "ship-it", ans)
    st = door.act_status({"run_id": "p5-run"})
    check("(5) the run moves off g1", (st.get("gate") or {}).get("id") != "g1", json.dumps(st.get("gate")))
    bridge._tick(DOOR)                       # reconcile sweep
    g1tok = [t for t, i in bridge._instances.items()
             if i["run_id"] == "p5-run" and i["gate_id"] == "g1"]
    check("(5) the answered instance is reconciled (resolved, terminal)",
          bool(g1tok) and all(bridge._instances[t].get("resolved") for t in g1tok),
          [bridge._instances.get(t) for t in g1tok])
    append(RUN, "p5-run", "g1")              # re-hold line for the ALREADY-ANSWERED gate
    bridge._tick(DOOR)
    time.sleep(0.25)
    states = [i["state"] for i in bridge._instances.values()]
    check("(5) a hold line for an answered gate skips — no re-present",
          len(ctx.injects) == 1 and "skipped" in states, (len(ctx.injects), states))

    # ---- (6) compat observers: minted-token law on the answer side ----------
    append(RUN, "p5-run", "g2")
    bridge._tick(DOOR)
    check("(6) the next hold injects on the same owner session",
          wait_until(lambda: len(ctx.injects) == 2) and ctx.injects[-1][0] == "p5-gw-session")
    tok2 = [t for t in open_tokens() if bridge._instances[t]["gate_id"] == "g2"]
    check("(6) the instance carries the 16-hex minted token", bool(tok2), open_tokens())
    if tok2:
        t2 = tok2[0]
        payload = {"pattern_key": bridge.TOKEN_PREFIX + t2, "pattern_keys": [bridge.TOKEN_PREFIX + t2],
                   "command": WAKE_TEXT, "description": "x", "session_key": "p5-gw-session", "surface": "gateway"}
        pre_cb(**payload)
        check("(6) pre_approval_request marks the minted token seen",
              bridge._instances[t2]["state"] == "seen")
        nrel = len(release_calls)
        forged = dict(payload)
        forged["pattern_key"] = bridge.TOKEN_PREFIX + "f" * 16
        forged["pattern_keys"] = [bridge.TOKEN_PREFIX + "f" * 16]
        post_cb(**forged, choice="once")
        dup = dict(payload)
        dup["pattern_key"] = bridge.TOKEN_PREFIX + g1tok[0]
        dup["pattern_keys"] = [bridge.TOKEN_PREFIX + g1tok[0]]
        post_cb(**dup, choice="once")        # duplicate: g1's token is already resolved
        time.sleep(0.1)
        check("(6) forged (unminted) and duplicate (resolved) posts release nothing",
              len(release_calls) == nrel, json.dumps(release_calls))
        post_cb(**payload, choice="deny")    # deny: hard halt, answers NOTHING
        time.sleep(0.1)
        check("(6) deny answers nothing (hold stands, no release)", len(release_calls) == nrel
              and not (RUN / "gates" / "g2.json").exists())
        append(RUN, "p5-run", "g2")          # re-hold g2 after the deny: fresh instance
        bridge._tick(DOOR)
        wait_until(lambda: len(ctx.injects) == 3)
        t3 = [t for t in open_tokens() if bridge._instances[t]["gate_id"] == "g2"]
        check("(6) a deny leaves the gate holdable: fresh inject", bool(t3) and len(ctx.injects) == 3, open_tokens())
        if t3:
            p3 = dict(payload)
            p3["pattern_key"] = bridge.TOKEN_PREFIX + t3[0]
            p3["pattern_keys"] = [bridge.TOKEN_PREFIX + t3[0]]
            post_cb(**p3, choice="timeout")
            time.sleep(0.1)
            check("(6) timeout answers NOTHING", len(release_calls) == nrel)
    r2 = door.act_release({"run_id": "p5-run", "gate_id": "g1", "answer": "approve"})
    check("(6) the door's own already-answered refusal backs the token law",
          r2.get("ok") is False and "already answered" in str(r2.get("error")), r2)
    check("(6) no core approval internal was touched (whole run)", not Trap.hit)

    # ---- (7) silent degradation ----------------------------------------------
    R3 = mk_run("p5-run-nowake")
    bridge._tick(DOOR)                             # seed R3 at EOF
    append(R3, "p5-run-nowake", "g1", wake=False)  # hold row WITHOUT a wake row
    bridge._tick(DOOR)
    time.sleep(0.25)
    check("(7) no runner-authored wake row injects nothing (silent)",
          all(i["run_id"] != "p5-run-nowake" or i["state"] == "skipped" for i in bridge._instances.values()))
    R6 = mk_run("p5-run-gone")
    bridge._tick(DOOR)                             # seed R6 at EOF
    append(R6, "p5-run-gone", "g1")
    bridge._tick(DOOR)
    check("(7) presented instance for the live run",
          wait_until(lambda: any(i["run_id"] == "p5-run-gone" and i["state"] == "issued"
                                 for i in bridge._instances.values())))
    shutil.rmtree(R6)
    bridge._tick(DOOR)                       # run dir gone: reconcile, terminal
    check("(7) a vanished run dir reconciles terminal, no raise",
          all(not (i["run_id"] == "p5-run-gone" and not i.get("resolved")) for i in bridge._instances.values()))
    (R4 / "events.jsonl").write_text("")
    bridge._tick(DOOR)
    check("(7) a truncated events.jsonl reseeds honestly, no raise", True)
finally:
    bridge.shutdown()
    door._spawn_runner = _orig_spawn
    for k in ("tools.approval", "tools.approval_gateway_wait", "tools"):
        sys.modules.pop(k, None)
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
