#!/usr/bin/env python3
"""Committee wf159c fix-response (PR #159) — three blocking findings, pinned.

The #54 park shipped with three boundary defects the committee reproduced on
6b6b34d1a9; each is pinned here against its exact repro BEFORE the fix:

  W1 (finding 1, wall bound): the fit-check used the UNJITTERED interval and
      never rechecked the deadline before respawn — a park at timeout=2,
      interval=1.95, jitter=0 bought a SECOND spawn with a fresh full timeout
      that committed done at wall 2.65s > the 2s budget. Law now: a park may
      only fire when worst-case wait AND a non-empty respawn window fit inside
      the wall, the deadline is rechecked after the wait, and the respawn it
      triggers is CLAMPED to the remaining budget (a park can never buy a
      fresh full timeout).

  W2 (finding 1, clamp): slow-success second spawn must die at the wall, not
      commit done past it.

  W3 (finding 1, jitter): with jitter=0.9 the actual wait must never push the
      node past its wall (backoff_max = interval*(1+jitter) is what the fit
      check may consume).

  B2 (finding 2): a ratelimit death discovered AFTER the first respawn (the
      transport-ladder shape: transport death -> respawn -> banner death)
      must get the SAME dispatcher contract — parks while the wall allows,
      then the verbatim banner + ratelimit_gave_up. Zero parks with budget
      and wall room was a contract break.

  B3 (finding 3): the park must observe the fan-out quorum cancel
      (fo_cancel): a satisfied quorum must not wait out a parked straggler.
      At the default 300s interval that was ~5 dead minutes per straggler.

Run: env -u WF_RUNS_ROOT -u HERMES_HOME PYTHONPATH=/opt/hermes /opt/hermes/.venv/bin/python tests/test_ratelimit_park_walls_159c.py
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-159c"
RUNS = HOME / "workflows"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(Path(os.environ["HERMES_HOME"]) / "workflows")  # est-2ek.1.762 pin: HERMES_HOME alone is not a sandbox
os.environ.pop("WF_RUNS_ROOT", None)
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

if HOME.exists(): shutil.rmtree(HOME)
HOME.mkdir(parents=True); RUNS.mkdir()
FAKE = str(HERE / "fake")

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30}; m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def runx(run_id, extra_env=None, timeout=120):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS), FAKE_LOG=str(HOME / "fake.log"))
    env.update(extra_env or {})
    env.pop("WF_RUNS_ROOT", None)
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def events(r):
    return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines() if l.strip()]
def rec_of(r, nid="a"):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())
def spawns(tag):
    return (HOME / "fake.log").read_text().count(tag)

BANNER_GIVEUP = "credential rate-limited for claude-fable-5-1"

# ---------- W1: exact committee repro — interval that fits only by ignoring the
# ---------- respawn window must fire ZERO parks; done must never land past wall ----------
(HOME / "fake.log").write_text("")
att = HOME / "att-w1"; shutil.rmtree(att, ignore_errors=True)
r = mk("w1-fit", [{"id": "a", "type": "agent", "goal": "GO w1-fit", "timeout": 2}],
       ratelimit_interval=1.95, ratelimit_jitter=0.0, retry_budget=6, node_timeout=2)
env = {"FAKE_MODE": "ratelimit", "FAKE_RL_FAILS": "1", "FAKE_ATTEMPT_DIR": str(att)}
t0 = time.time(); out = runx("w1-fit", env); dt = time.time() - t0
rec = rec_of(r)
rl_ev = [e for e in events(r) if e.get("event") == "item.retrying" or
         (e.get("event") == "node.retrying" and e.get("error_class") == "ratelimit")]
check("W1: a park that cannot leave a respawn window fires ZERO parks (1 spawn)",
      spawns("GO w1-fit") == 1 and not rl_ev,
      f"spawns={spawns('GO w1-fit')} parks={len(rl_ev)}")
check("W1: honest give-up with the verbatim banner + ratelimit_gave_up",
      rec.get("status") == "failed" and rec.get("error_class") == "ratelimit"
      and rec.get("error") == BANNER_GIVEUP and rec.get("ratelimit_gave_up") is True,
      json.dumps({k: rec.get(k) for k in ("status", "error_class", "error", "ratelimit_gave_up")}))
check("W1: wall honored — run finished far below the 2s budget it refused to overshoot",
      dt < 1.5, f"wall={dt:.2f}s")
check("W1: WORKFLOW_FAILED", "WORKFLOW_FAILED" in out, out[:60])

# ---------- W-FIT (unit): the park's fit law is worst-case-jitter bounded and ----------
# ---------- must leave a real respawn window (>=15% wall, floor 0.25 s). ----------
# ---------- Deterministic: no subprocess, no fake — stub respawn, fake meta. ----------
import tempfile, threading
def unit_meta(interval=1.5, jitter=0.0):
    # the park reads interval/jitter ONLY from run meta (the door's channel) —
    # omit them here and the 300 s default silently refuses every park.
    d = Path(tempfile.mkdtemp(prefix="rlfit-"))
    return {"_run": d, "_stop": threading.Event(), "_procs_lock": threading.Lock(),
            "_retries_left": 99, "ratelimit_interval": interval,
            "ratelimit_jitter": jitter}, d

def stub_r(pid=4294967):   # a pid that cannot exist: quarantine sees dead-or-empty
    # raw carries the VERBATIM banner: the give-up text names the model the
    # banner declared (never a node/seat guess when the banner speaks).
    return {"status": "failed", "error_class": "ratelimit", "error": "boom",
            "raw": ("hermes -z: agent failed: Anthropic credentials are rate-limited "
                    "for claude-fable-5-1; other Claude models remain available "
                    "(see `hermes auth list`)."),
            "pid": pid, "ms": 1, "attempts": 0}

import random as _rnd
fixed = _rnd.Random(0.5)   # jitter draws at the exact midpoint: backoff == interval
_saved = _rnd.random
import wf as _wfmod
_wfmod.random = fixed      # module-level determinism for the park's jitter draw
try:
    m, d = unit_meta(1.95, 0.0)
    calls = []
    def respawn_fail():
        calls.append(1); return stub_r()
    r = _wfmod._ratelimit_park(m, stub_r(), respawn_fail, "node", {"node": "x"},
                               node={"timeout": 2})
    check("FIT unit: committee repro wall=2 interval=1.95 jitter=0 -> ZERO parks (no respawn window left)",
          not calls and r.get("ratelimit_gave_up") is True
          and r.get("error") == BANNER_GIVEUP,
          f"respawns={len(calls)}")
    m, d = unit_meta(1.5, 0.9); calls = []
    r = _wfmod._ratelimit_park(m, stub_r(), respawn_fail, "node", {"node": "x"},
                               node={"timeout": 3})
    # jitter midpoint: backoff=1.5; fit needs 1.5*1.9=2.85 <= 3-0.45=2.55 -> false
    check("FIT unit: jitter=0.9 interval=1.5 wall=3 -> refuse (worst-case fit), no overshoot done",
          not calls and r.get("ratelimit_gave_up") is True, f"respawns={len(calls)}")
    m, d = unit_meta(1.5, 0.0); calls = []
    def respawn_ok():
        calls.append(1)
        return {"status": "done", "output": {"result": "ok"}, "pid": 4294967, "ms": 1}
    r = _wfmod._ratelimit_park(m, stub_r(), respawn_ok, "node", {"node": "x"},
                               node={"timeout": 5})
    check("FIT unit: interval=1.5 wall=5 fits (worst case + window) -> exactly ONE park then respawn",
          len(calls) == 1 and r.get("status") == "done"
          and [a.get("error_class") for a in (r.get("attempts_log") or [])] == ["ratelimit"],
          f"respawns={len(calls)} status={r.get('status')}")
    _saved_calls = _wfmod._attempt_api_calls
    _wfmod._attempt_api_calls = lambda *a, **k: 0   # replay-safe evidence, FAKE_API_CALLS=0 shape
    try:
        m, d = unit_meta(1.0, 0.0); calls = []
        class Late:
            n = 0
            def spawn(self):
                self.n += 1
                if self.n == 1:
                    return {"status": "failed", "error_class": "transport", "error": "conn",
                            "raw": "conn", "pid": 4294967, "ms": 1}
                return stub_r()
        L = Late()
        def respawn_late():
            calls.append(1); return L.spawn()
        m2 = dict(m); m2["_retries_left"] = 3
        r = _wfmod._transient_retry(m2, L.spawn(), respawn_late, "node", {"node": "x"},
                                    node={"timeout": 30})
        check("B2 unit: transport->respawn->banner parks under the SAME budget; the park owns "
              "the terminal word, banner truth survives (no zero-park transport terminal)",
              r.get("error_class") == "ratelimit"
              and r.get("error") == BANNER_GIVEUP
              and [a.get("error_class") for a in (r.get("attempts_log") or [])][:2]
              == ["transport", "ratelimit"],
              f"ec={r.get('error_class')} err={str(r.get('error'))[:60]} "
              f"log={[a.get('error_class') for a in (r.get('attempts_log') or [])]}")
    finally:
        _wfmod._attempt_api_calls = _saved_calls
finally:
    _wfmod.random = _saved

# ---------- B2: banner death discovered AFTER a transport respawn gets the park ----------
# ---------- shape a: two banner deaths then recovery — parks must fire after the ----------
# ---------- transport respawn (old: transport->respawn->banner TERMINATED at 2 ----------
# ---------- spawns, zero parks, rc=1 prose error, no ratelimit_gave_up). ----------
(HOME / "fake.log").write_text("")
att = HOME / "att-b2a"; shutil.rmtree(att, ignore_errors=True)
r = mk("b2a-late", [{"id": "a", "type": "agent", "goal": "GO b2a-late"}],
       ratelimit_interval=0.3, ratelimit_jitter=0.0, retry_backoff=[0.05, 0.05],
       retry_budget=6)
env = {"FAKE_MODE": "ratelimit_after_transport", "FAKE_ATTEMPT_DIR": str(att),
       "FAKE_RL_FAILS": "2", "FAKE_API_CALLS": "0"}
out = runx("b2a-late", env)
rec = rec_of(r)
rl_ev = [e for e in events(r) if e.get("error_class") == "ratelimit"
         and str(e.get("event", "")).endswith(".retrying")]
check("B2a: transport->respawn->banner gets PARKS and recovers (4 spawns: t,b,b,ok)",
      spawns("GO b2a-late") == 4 and len(rl_ev) == 2 and rec["status"] == "done",
      f"spawns={spawns('GO b2a-late')} rl_parks={len(rl_ev)} status={rec.get('status')} "
      f"(old: 2 spawns, 0 parks, terminal failed)")
check("B2a: attempts_log preserves the transport attempt AND the parked banner attempts",
      [a.get("error_class") for a in (rec.get("attempts_log") or [])]
      == ["transport", "ratelimit", "ratelimit"],
      json.dumps([a.get("error_class") for a in (rec.get("attempts_log") or [])]))
check("B2a: never laundered to transport_exhausted while banner truth exists",
      rec.get("error_class") != "transport_exhausted", str(rec.get("error_class")))

# ---------- shape b: always-banner after the transport death, budget 2 -> the ----------
# ---------- dispatcher contract on give-up: verbatim banner + ratelimit_gave_up. ----------
(HOME / "fake.log").write_text("")
att = HOME / "att-b2b"; shutil.rmtree(att, ignore_errors=True)
r = mk("b2b-giveup", [{"id": "a", "type": "agent", "goal": "GO b2b-giveup"}],
       ratelimit_interval=0.3, ratelimit_jitter=0.0, retry_backoff=[0.05, 0.05],
       retry_budget=2)
env = {"FAKE_MODE": "ratelimit_after_transport", "FAKE_ATTEMPT_DIR": str(att),
       "FAKE_RL_FAILS": "9999", "FAKE_API_CALLS": "0"}
out = runx("b2b-giveup", env)
rec = rec_of(r)
check("B2b: give-up after a late banner: verbatim banner + ratelimit_gave_up, class ratelimit",
      rec.get("status") == "failed" and rec.get("error_class") == "ratelimit"
      and rec.get("error") == BANNER_GIVEUP and rec.get("ratelimit_gave_up") is True,
      json.dumps({k: rec.get(k) for k in ("status", "error_class", "error", "ratelimit_gave_up")}))
check("B2b: WORKFLOW_FAILED", "WORKFLOW_FAILED" in out, out[:60])

# ---------- B3: the park observes the fan-out quorum cancel (committee repro: ----------
# ---------- interval 3, quorum 1 — old code held the node 3.38s for the park). ----------
(HOME / "fake.log").write_text("")
r = mk("b3-quorum", [{"id": "f", "type": "agent",
                      "fanout": {"items": ["b3-winner", "b3-late"], "goal": "GO {item}",
                                 "quorum": 1},
                      "schema": {"type": "object", "required": ["result"]}}],
       ratelimit_interval=3.0, ratelimit_jitter=0.0)
env = {"FAKE_MODE": "ratelimit_straggler"}
t0 = time.time(); out = runx("b3-quorum", env, timeout=90); dt = time.time() - t0
rec = rec_of(r, "f")
check("B3: satisfied quorum commits WITHOUT waiting out the parked straggler",
      rec.get("status") in ("done", "partial") and dt < 1.8,
      f"status={rec.get('status')} wall={dt:.2f}s (old: 3.38s — full 3s park)")
check("B3: the parked straggler is recorded cancelled, not as a ratelimit failure",
      not any(e.get("error_class") == "ratelimit" and str(e.get("event", "")).endswith(".failed")
              for e in events(r)), json.dumps([e.get("event") for e in events(r)])[-200:])
check("B3: WORKFLOW_DONE", "WORKFLOW_DONE" in out, out[:60])

print(("" if ok else "FAILURES PRESENT"), "DONE test_ratelimit_park_walls_159c" if ok else "DONE with FAILURES")
sys.exit(0 if ok else 1)
