#!/usr/bin/env python3
"""P5 native approval surface for human gates — config-gated, default OFF.

Matrix (stdlib-only, PASS/FAIL lines, exit 0 green):
  (1) allow-list shapes: only a settings list/string naming 'approval_bridge'
      arms the bridge; absent/garbage/other stays OFF.
  (2) default-off byte-identical: door.register() with no allow-list registers
      exactly the hooks the door registers WITHOUT the bridge (measured, not
      hard-coded, so later hook lanes never re-break this law), adds neither
      approval hook, starts no bridge thread, and the
      status read-model of a held run is byte-equal to the same read after an
      armed register immediately shut down (the bridge changes no payload).
  (3) armed: a freshly-appended gate.held row (tail-seeded, history never
      re-fires) is presented on the approval channel carrying the run's
      runner-authored wake text VERBATIM, a wf-gate:<16hex> correlation key,
      and the constant description — graph question/options appear NOWHERE in
      what is presented.
  (4) answer mapping: an approve-shape choice (once) resolves through the
      door's OWN act_release with answer 'approve' (exactly one call, answer
      file stamped); deny answers NOTHING (hold stands, no answer file);
      timeout answers nothing.
  (5) idempotency/forgery: a second gate.held line for an ALREADY-ANSWERED
      gate is skipped (no presentation); a post response with a token that was
      never minted releases nothing; a duplicate post for a resolved token
      releases nothing; the door's own already-answered refusal backs both.
  (6) silent degradation: no wake row and no answerable session present nothing.

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
os.environ["HERMES_SESSION_ID"] = "p5-owner"
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

class FakeCtx:
    """Records registrations; get_config faithful to the plugin-relative shape."""
    def __init__(self, settings):
        self.settings, self.hooks, self.tools, self.skills, self.commands = settings, [], [], [], []
    def get_config(self, key, default=None):
        return self.settings.get(key, default)
    def register_skill(self, name, path, **kw): self.skills.append(name)
    def register_tool(self, **kw): self.tools.append(kw.get("name"))
    def register_hook(self, name, cb): self.hooks.append((name, cb))
    def register_command(self, name, fn, **kw): self.commands.append(name)
    def hook(self, name):
        return [cb for n, cb in self.hooks if n == name]

GRAPH = {"name": "p5ab", "nodes": [
    {"id": "one", "type": "agent", "goal": "offline"},
    {"id": "g1", "type": "gate", "after": ["one"], "question": "Ship the report?",
     "options": ["ship", "hold"]},
    {"id": "g2", "type": "gate", "after": ["g1"], "question": "Publish anywhere?",
     "options": ["yes", "no"]},
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

def hold_row(rid, gate):
    return json.dumps({"ts": "2026-10-15T00:01:0%d+00:00" % (hold_row.n % 10),
                       "event": "gate.held", "node": gate,
                       "question": "Ship the report?", "options": ["ship", "hold"]}) + "\n"
hold_row.n = 0

def wake_row(rid):
    return json.dumps({"ts": "2026-10-15T00:01:01+00:00", "event": "gate.held", "run_id": rid,
                       "owner": {"session_id": "p5-gw-session"}, "id": "tid",
                       "wake_protocol": "stamped", "text": WAKE_TEXT}) + "\n"

def append(r, text, wake=True):
    hold_row.n += 1
    with open(r / "events.jsonl", "a") as f:
        f.write(hold_row("p5-run", append.gate))
    if wake:
        with open(r / "wake.jsonl", "a") as f:
            f.write(wake_row("p5-run"))
append.gate = "g1"

class Present:
    """Test seam standing in for the native approval channel: records what is
    presented, replays core's observer dispatch (pre, then post with the
    scripted choice) synchronously, and returns the channel decision."""
    script = []
    def __init__(self, pre_cb, post_cb):
        self.pre, self.post, self.calls = pre_cb, post_cb, []
    def __call__(self, session_key, data):
        self.calls.append((session_key, dict(data)))
        payload = {k: data[k] for k in ("command", "description", "pattern_key", "pattern_keys")}
        payload["session_key"] = session_key
        payload["surface"] = "gateway"
        self.pre(**payload)
        self.choice = Present.script.pop(0) if Present.script else "once"
        self.post(**payload, choice=self.choice)
        return {"resolved": self.choice not in ("timeout",), "choice": None if self.choice == "timeout" else self.choice}

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

# fake core approval module: exactly one gateway notify session registered.
fake_tools = types.ModuleType("tools")
fake_approval = types.ModuleType("tools.approval")
fake_approval._gateway_notify_cbs = {"p5-gw-session": (lambda d: None)}
fake_tools.approval = fake_approval
sys.modules.setdefault("tools", fake_tools)
sys.modules["tools.approval"] = fake_approval

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

    # ---- (2) default-off: one hook, no thread, byte-identical read-model ----
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
    check("(2) default-off starts no bridge thread",
          bridge._watch_thread is None)
    st2 = door.act_status({"run_id": "p5-run"})
    check("(2) default-off status payload byte-identical", json.dumps(st, sort_keys=True) == json.dumps(st2, sort_keys=True))
    armed = bridge.maybe_enable(ctx_off, dict(DOOR), door._common)
    check("(2) maybe_enable answers None when the allow-list is off", armed is None
          and [n for n, _ in ctx_off.hooks] == base_names)

    # ---- (3) armed: the hold presents the runner's words, not the graph's ----
    ctx = FakeCtx({"hooks_bridge_allow": ["approval_bridge"]})
    door._CTX = ctx
    DOOR["act_release"] = lambda a: (release_calls.append(dict(a)), door.act_release(a))[1]
    armed = bridge.maybe_enable(ctx, DOOR, door._common)
    check("(3) allow-listed register arms the hook pair", armed is True
          and [n for n, _ in ctx.hooks] == ["pre_approval_request", "post_approval_response"], ctx.hooks)
    pre_cb, post_cb = ctx.hook("pre_approval_request")[0], ctx.hook("post_approval_response")[0]
    pres = Present(pre_cb, post_cb)
    bridge._native_present = pres

    bridge._tick(DOOR)                       # first sight: seed at EOF, history never re-fires
    check("(3) seeding tick presents nothing for pre-existing bytes", len(pres.calls) == 0)
    append(RUN, "p5-run", wake=True)
    append.gate = "g1"
    bridge._tick(DOOR)
    check("(3) the appended gate.held row is presented once",
          wait_until(lambda: len(pres.calls) == 1))
    if len(pres.calls) == 1:
        skey, data = pres.calls[0]
        check("(3) presented on the run owner's approval session", skey == "p5-gw-session", skey)
        check("(3) command is the runner-authored wake text VERBATIM", data["command"] == WAKE_TEXT,
              repr(data["command"])[:120])
        bad = [p for p in ("Ship the report?", "ship", "Publish anywhere") if p in json.dumps(data)]
        check("(3) graph question/options appear NOWHERE in the presentation", not bad, bad)
        pk = data["pattern_key"]
        check("(3) correlation key is wf-gate:<16hex> and single-valued",
              pk.startswith("wf-gate:") and len(pk[8:]) == 16 and data["pattern_keys"] == [pk], pk)
        check("(3) presentation is one-use (no permanent/session scope)",
              data["allow_permanent"] is False and data["allow_session"] is False)
    # ---- (4) answer mapping --------------------------------------------------
    check("(4) approve-shape answer released through the door's OWN act_release",
          wait_until(lambda: len(release_calls) == 1) and release_calls[0]["answer"] == "approve"
          and release_calls[0]["gate_id"] == "g1", json.dumps(release_calls))
    # the release runs on the bridge's thread: the call is recorded BEFORE act_release returns,
    # so wait for the atomic answer-file landing instead of racing it.
    check("(4) the answer file lands via the door path", wait_until((lambda: (RUN / "gates" / "g1.json").exists()), 10.0))
    ans = json.loads((RUN / "gates" / "g1.json").read_text())
    check("(4) the answer file carries the approve token via the door path", ans.get("answer") == "approve", ans)
    st = door.act_status({"run_id": "p5-run"})
    check("(4) the run moves off g1", (st.get("gate") or {}).get("id") != "g1", json.dumps(st.get("gate")))
    append.gate = "g2"
    append(RUN, "p5-run")                    # second hold, scripted deny
    Present.script = ["deny"]
    bridge._tick(DOOR)
    wait_until(lambda: len(pres.calls) == 2)
    time.sleep(0.15)
    check("(4) deny presents but answers NOTHING (no release call)", len(release_calls) == 1
          and not (RUN / "gates" / "g2.json").exists(), json.dumps(release_calls))
    append(RUN, "p5-run")                    # third hold on g2, scripted timeout
    Present.script = ["timeout"]
    bridge._tick(DOOR)
    wait_until(lambda: len(pres.calls) == 3)
    time.sleep(0.15)
    check("(4) timeout answers NOTHING", len(release_calls) == 1
          and not (RUN / "gates" / "g2.json").exists())

    # ---- (5) idempotency and forgery ----------------------------------------
    append.gate = "g1"
    append(RUN, "p5-run")                    # re-hold line for the ALREADY-ANSWERED gate
    bridge._tick(DOOR)
    wait_until(lambda: len(pres.calls) == 4)
    time.sleep(0.15)
    states = [i["state"] for i in bridge._instances.values()]
    check("(5) a hold line for an answered gate is skipped, never presented",
          len(pres.calls) == 3 and "skipped" in states, (len(pres.calls), states))
    forged = dict(pattern_key="wf-gate:" + "f" * 16, command="x", description="x",
                  pattern_keys=["wf-gate:" + "f" * 16], session_key="p5-gw-session", surface="gateway")
    post_cb(**forged, choice="once")         # forged: token never minted here
    time.sleep(0.1)
    check("(5) a forged post response with an unminted token releases nothing", len(release_calls) == 1)
    dup = dict(pres.calls[0][1]); dup["session_key"] = "p5-gw-session"; dup["surface"] = "gateway"
    post_cb(**dup, choice="once")            # duplicate: token already resolved
    time.sleep(0.1)
    check("(5) a duplicate post response for a resolved token releases nothing", len(release_calls) == 1)
    r2 = door.act_release({"run_id": "p5-run", "gate_id": "g1", "answer": "approve"})
    check("(5) the door's own already-answered refusal backs the token law",
          r2.get("ok") is False and "already answered" in str(r2.get("error")), r2)

    # ---- (6) silent degradation ----------------------------------------------
    R3 = mk_run("p5-run-nowake")
    append.gate = "g1"
    append(R3, "p5-run-nowake", wake=False)  # hold row WITHOUT a wake row
    bridge._tick(DOOR)
    time.sleep(0.25)
    check("(6) no runner-authored wake row presents nothing (silent)", len(pres.calls) == 3)
    R4 = mk_run("p5-run-noowner")
    (R4 / "run.json").write_text(json.dumps({"name": "p5ab", "owner": None}))
    append(R4, "p5-run-noowner")
    bridge._tick(DOOR)
    time.sleep(0.2)
    check("(6) an owner-less run presents nothing (silent)", len(pres.calls) == 3)
    # truncation resilience: an events file that shrank must not raise, must reseed
    (R4 / "events.jsonl").write_text("")
    bridge._tick(DOOR)
    check("(6) a truncated events.jsonl reseeds honestly, no raise", True)
finally:
    bridge.shutdown()
    door._spawn_runner = _orig_spawn
    sys.modules.pop("tools.approval", None)
    sys.modules.pop("tools", None)
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
