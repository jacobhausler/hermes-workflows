#!/usr/bin/env python3
"""WF-GRAFT-9: the park watchdog (peer row atbrace:hw-36y, SYNTHESIS #23/#25).

Work parked on external events (machine-gate probes, human-gate holds) gets a
persisted blocked-since clock. N consecutive dispatcher-failure strikes or the
time-box (default 6 h) settle the park failed loudly, with a one-shot notice.
The clock lives in the gate's own persisted mirror, so it survives a runner
restart and a clean wake starts a fresh window.

Checks: kernel strike accumulation, kernel time-box expiry, kernel clean-wake
reset, park_gate wiring (persisted clock, restart replay, probe-dispatch
strikes, release clears), human-hold wiring (time-box settle, strike settle,
one-shot across re-drives, disabled escape).
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

TMP = Path(tempfile.mkdtemp(prefix="pw-", dir=str(ROOT)))
os.environ["HERMES_HOME"] = str(TMP / "home")
os.environ["WF_RUNS_ROOT"] = str(TMP / "workflows")
os.environ["HERMES_WF_HERMES_BIN"] = "offline"
os.environ.pop("HERMES_SESSION_ID", None)
RUNS = Path(os.environ["WF_RUNS_ROOT"])
RUNS.mkdir(parents=True)

def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, ROOT / fname)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

pw = _load("park_watch", "park_watch.py")          # RED first: the module is the graft
wf = _load("pw_wf", "wf.py")
c = wf.wfcommon

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}" if detail else msg
    ok += 1
    print("PASS", msg)

def evs(rdir):
    out = []
    p = Path(rdir) / "events.jsonl"
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out

def watchdog_evs(rdir):
    return [e for e in evs(rdir) if e.get("event") == "gate.watchdog_settled"]

_UNSET = object()

def mk(rid, graph, owner=_UNSET) -> Path:
    r = RUNS / rid
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps(graph))
    meta = {"name": rid, "hermes_bin": "/bin/true"}
    if owner is not _UNSET:
        meta["owner"] = owner
    (r / "run.json").write_text(json.dumps(meta))
    return r

def gate_graph(nid, wait=None, **extra):
    n = {"id": nid, "type": "gate", "question": "ship?", "options": ["yes", "no"]}
    if wait is not None:
        n["wait"] = wait
    n.update(extra)
    return {"name": "pw-" + nid, "nodes": [n]}, n

def park_gate_run(rid, gate):
    r = mk(rid, {"name": rid, "nodes": [gate]})
    return r

PROBE_FAIL = ["/bin/false"]              # a probe that RUNS and reports not-ready
# est-7ncu0 (merged #570) refuses nonresident until_argv before dispatch, so a
# dispatcher-failure probe must be resident yet still fail to exec: an executable
# with a missing interpreter yields ENOENT at spawn — the always-settle field shape.
_STABLE = TMP / "stable-root"; _STABLE.mkdir(exist_ok=True)
PROBE_SH = _STABLE / "probe"; PROBE_SH.write_text("#!/nonexistent-interpreter\n")
PROBE_SH.chmod(0o755)
os.environ["WF_ARGV_STABLE_ROOTS"] = str(_STABLE)
PROBE_GONE = [str(PROBE_SH)]

os.environ["WF_PARK_WATCHDOG"] = "1"
os.environ.pop("WF_PARK_WATCHDOG_TIMEOUT_S", None)
os.environ.pop("WF_PARK_WATCHDOG_STRIKES", None)

try:
    # ---------- kernel: the tick state machine -------------------------------
    t0 = 1_000_000.0
    w = {}
    check(pw.tick(w, t0, dispatch_failed=True) is None and w["strikes"] == 1
          and w["blocked_since"] == t0,
          "kernel: first dispatcher-failure strike records, no settle")
    check(pw.tick(w, t0 + 1, dispatch_failed=True) is None and w["strikes"] == 2,
          "kernel: strikes accumulate across ticks")
    check(pw.tick(w, t0 + 2, dispatch_failed=False) is None and w["strikes"] == 0
          and w["blocked_since"] == t0,
          "kernel: a successful dispatch clears strikes but not the clock")
    for i in range(3):
        r = pw.tick(w, t0 + 3 + i, dispatch_failed=True)
    check(r == "strikes" and w["strikes"] == 3,
          "kernel: three consecutive dispatcher failures settle as 'strikes'")
    check(pw.tick(w, t0 + 9999, dispatch_failed=False) == "strikes",
          "kernel: a settled watch is one-shot and idempotent")

    w2 = {}
    check(pw.tick(w2, t0, timeout_s=100) is None,
          "kernel: a park inside its time-box keeps waiting")
    check(pw.tick(w2, t0 + 99.9, timeout_s=100) is None,
          "kernel: the box boundary is inclusive-exact below the limit")
    check(pw.tick(w2, t0 + 100, timeout_s=100) == "timebox",
          "kernel: the time-box settles an expired park as 'timebox'")
    cfg = pw.config(None)
    check(cfg[0] == 6 * 3600 and cfg[1] == 3,
          "kernel: defaults are a 6 h box and three strikes")

    w3 = {}
    check(pw.tick(w3, t0 + 10 * 3600, timeout_s=100) is None
          and w3["blocked_since"] == t0 + 10 * 3600 and w3["strikes"] == 0,
          "kernel: a clean wake (fresh state) starts a fresh window, never a retro-settle")

    # ---------- park_gate wiring: the machine-gate park ----------------------
    os.environ["WF_PARK_WATCHDOG_TIMEOUT_S"] = "1"
    os.environ.pop("WF_PARK_WATCHDOG_STRIKES", None)
    g1 = {"id": "await-ci", "type": "gate", "after": [],
          "wait": {"until_argv": PROBE_FAIL, "every_s": 0.2, "timeout_s": 600}}
    r1 = mk("pw-gate", {"name": "pw-gate", "nodes": [g1]})
    started = time.time()
    res = wf.park_gate(r1, "pw-gate", g1, {"await-ci": g1}, lambda: None)
    took = time.time() - started
    check(res == "failed" and took < 30,
          "park_gate: the persisted box settles the probe park failed", f"{res} in {took:.1f}s")
    we = watchdog_evs(r1)
    check(len(we) == 1 and we[0]["reason"] == "timebox",
          "park_gate: exactly one gate.watchdog_settled event, reason timebox", str(we))
    pk1 = json.loads((r1 / "gates" / "await-ci.parked.json").read_text())
    check(isinstance(pk1.get("watch"), dict)
          and int(pk1["watch"].get("strikes", -1)) == 0
          and isinstance(pk1["watch"].get("blocked_since"), (int, float)),
          "park_gate: an exit-1 probe is not a dispatcher strike (strikes stayed 0)")
    nrec = json.loads((r1 / "nodes" / "await-ci.json").read_text())
    check(nrec.get("status") == "failed" and "park-watchdog" in nrec.get("error", ""),
          "park_gate: the node commits failed with a named park-watchdog error")

    # restart replay: a fresh park on the SAME run dir keeps the clock
    os.environ["WF_PARK_WATCHDOG_TIMEOUT_S"] = "3600"
    res = wf.park_gate(r1, "pw-gate", g1, {"await-ci": g1}, lambda: "stopped")
    check(res == "stopped",
          "park_gate: re-park inside the still-live persisted box keeps waiting")
    pk1b = json.loads((r1 / "gates" / "await-ci.parked.json").read_text())
    check(abs(pk1b["watch"]["blocked_since"] - pk1["watch"]["blocked_since"]) < 1.0,
          "park_gate: the re-park REUSES the persisted blocked-since (no clock reset)")
    pk1b["watch"].pop("settled", None)
    pk1b["watch"]["blocked_since"] = time.time() - 3601
    (r1 / "gates" / "await-ci.parked.json").write_text(json.dumps(pk1b))
    started = time.time()
    res = wf.park_gate(r1, "pw-gate", g1, {"await-ci": g1}, lambda: None)
    check(res == "failed" and time.time() - started < 2,
          "park_gate: an aged persisted clock fails fast on the first tick after restart")
    nrec = json.loads((r1 / "nodes" / "await-ci.json").read_text())
    check(nrec.get("status") == "failed" and (nrec.get("output") or {}).get("attempt") == 0,
          "park_gate: the fast settle fired BEFORE re-probing (attempt 0)")
    check(len(watchdog_evs(r1)) == 2 and watchdog_evs(r1)[-1]["reason"] == "timebox",
          "park_gate: the restart settle is loud too (a second settled event)")

    # dispatcher strikes at the machine park: the probe itself cannot launch
    os.environ["WF_PARK_WATCHDOG_STRIKES"] = "2"
    g3 = {"id": "await-x", "type": "gate", "after": [],
          "wait": {"until_argv": PROBE_GONE, "every_s": 0.2, "timeout_s": 600}}
    r3 = mk("pw-strike", {"name": "pw-strike", "nodes": [g3]})
    started = time.time()
    res = wf.park_gate(r3, "pw-strike", g3, {"await-x": g3}, lambda: None)
    check(res == "failed" and time.time() - started < 30,
          "park_gate: an undispatchable probe strikes and settles failed before the author bound")
    we = watchdog_evs(r3)
    check(len(we) == 1 and we[0]["reason"] == "strikes",
          "park_gate: the strike settle names reason=strikes", str(we))

    # clean wake: a released park clears the persisted clock
    g4 = {"id": "timer", "type": "gate", "after": [], "wait": {"wait_s": 1}}
    r4 = mk("pw-timer", {"name": "pw-timer", "nodes": [g4]})
    res = wf.park_gate(r4, "pw-timer", g4, {"timer": g4}, lambda: None)
    pk4 = json.loads((r4 / "gates" / "timer.parked.json").read_text())
    check(res == "released" and "watch" not in pk4,
          "park_gate: a clean wake clears the persisted watchdog clock", str(pk4))

    # disabled: the aged file is left alone, the park holds as before
    os.environ["WF_PARK_WATCHDOG"] = "0"
    res = wf.park_gate(r1, "pw-gate", g1, {"await-ci": g1}, lambda: "stopped")
    check(res == "stopped",
          "park_gate: WF_PARK_WATCHDOG=0 disables the watchdog (aged clock ignored)")
    os.environ["WF_PARK_WATCHDOG"] = "1"

    # ---------- human-gate hold wiring ---------------------------------------
    os.environ["WF_PARK_WATCHDOG_TIMEOUT_S"] = "3600"
    g5, n5 = gate_graph("approve")
    r5 = mk("pw-held", g5)
    aged = {"since": time.time() - 3601, "strikes": 0}
    (r5 / "gates" / "approve.held.json").write_text(json.dumps({
        "since": time.time() - 3601,
        "watch": {"blocked_since": time.time() - 3601, "strikes": 0},
        "_def": c.efp({"approve": n5}, n5), "fp_rule_version": c.FP_RULE_VERSION}))
    res = wf.main("pw-held")
    check("held" not in str(res) and "blocked by failed" in str(res),
          "hold: an aged persisted box fails the run instead of re-holding", str(res))
    we = watchdog_evs(r5)
    check(len(we) == 1 and we[0]["reason"] == "timebox",
          "hold: the time-box settle is loud once (owner-null = zero strikes path)", str(we))

    g6, n6 = gate_graph("approve")
    r6 = mk("pw-strike-hold", g6, owner={"session_id": "s-pw"})
    os.environ["WF_PARK_WATCHDOG_STRIKES"] = "2"
    os.environ["WF_PARK_WATCHDOG_TIMEOUT_S"] = "600"
    # merged est-7rudf law: missing-endpoint is None (nowhere-ever) and settles
    # STRIKE-FREE; the strike class is a FAILED DELIVERY ATTEMPT. Simulate it at
    # the tri-state seam rather than the old missing-server shape.
    _real_deliver = wf._wake_deliver
    wf._wake_deliver = lambda rec, *a, **k: (rec.update(
        error="HTTP 500 simulated dispatcher failure"), False)[1]
    res = wf.main("pw-strike-hold")
    check("held at approve" in str(res),
          "hold: first undelivered wake strikes but still holds", str(res))
    hm = json.loads((r6 / "gates" / "approve.held.json").read_text())
    check(isinstance(hm.get("watch"), dict) and hm["watch"]["strikes"] == 1,
          "hold: the strike persisted into the gate's held record", str(hm))
    res = wf.main("pw-strike-hold")
    check("held" not in str(res) and "blocked by failed" in str(res),
          "hold: the second strike settles the park failed loudly", str(res))
    we = watchdog_evs(r6)
    check(len(we) == 1 and we[0]["reason"] == "strikes",
          "hold: the strike settle names strikes, once", str(we))
    wk = [json.loads(l) for l in (r6 / "wake.jsonl").read_text().splitlines()]
    gh = [l for l in wk if l.get("event") == "gate.held"]
    check(len(gh) >= 2 and all(l.get("delivered") is False for l in gh),
          "hold: each park attempt probed the wake undelivered (the strike evidence)")
    res = wf.main("pw-strike-hold")   # re-drive of the settled run: replay, no re-settle
    wf._wake_deliver = _real_deliver
    check("blocked by failed" in str(res) and len(watchdog_evs(r6)) == 1,
          "hold: the one-shot notice survives a later re-drive", str(res))

    print(f"\n{ok} checks passed")
finally:
    shutil.rmtree(TMP, ignore_errors=True)
sys.exit(0)
