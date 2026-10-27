"""Tick BODY of the self-terminating watchdog tick (est-ip975, PR-2 of 3).

PR-1 (cron_bridge.py) landed the job lifecycle: one core cron job keyed BY
NAME (`cron_bridge.TICK_NAME`, no_agent, prompt None), find-then-create arm,
deletion-not-disable teardown, and the bash shim the core scheduler runs
argument-free - which execs `wf.py tick`, the subcommand that reaches this
module. What lands here is the body that shim reaches:

  * TICK   census the door's resolved runs root and re-drive every dead-runner
           run (act_wait's scope: pending/interrupted, runner not verified
           alive) through the door's ONE respawn bridge (`_respawn_runner`;
           flock admission makes a raced spawn a harmless loser).
  * RE-ARM keep the job while any run stays active - a manually deleted job
           comes back on the next tick while work is live.
  * DRAIN  the tick body ITSELF tears the job down once the active set is
           empty (`cron_bridge.teardown_tick`: deletion, never disable). Zero
           idle wakes: between runs there is no job to fire.

Laws: stdlib-only; core cron stays behind cron_bridge's guarded seam - a
core-less host, or a partial-tree door copy that ships without either module,
degrades to `{"armed": false, "reason": ...}` and never a failed launch. The
census and revival are scoped to the door's resolved runs root only (the #58
write-verb law: a run found solely under a foreign root is read-only from
here, exactly as `wait` refuses to respawn it). Revival mirrors act_wait's
scope: failed/stopped/done/partial are verdicts, not orphaned work. Every hook
is fail-open; a watchdog that cannot arm must never block a run. Bound to the
door's wfcommon via bind(), like orphan_watch.
"""
import importlib.util
import json
from pathlib import Path

# run_state vocabulary that is terminal: nothing to revive, nothing to wait
# for. `partial` is a committed verdict (est-3acn), never orphaned work.
TERMINAL = frozenset({"done", "partial", "failed", "stopped"})

_COMMON = None
_BRIDGE = None
_BRIDGE_LOADED = False


def bind(common):
    global _COMMON
    _COMMON = common


def _bridge():
    """The sibling `cron_bridge` module (PR-1), spec-loaded by path like the
    door loads its parts; honest None where the file is absent (partial-tree
    copies). Memoized: the module is pure-stdlib, exec is safe once."""
    global _BRIDGE, _BRIDGE_LOADED
    if not _BRIDGE_LOADED:
        _BRIDGE_LOADED = True
        spec = importlib.util.spec_from_file_location(
            "_hw_cron_bridge", Path(__file__).resolve().parent / "cron_bridge.py")
        if spec is not None and spec.loader is not None:
            try:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                _BRIDGE = mod
            except Exception:
                _BRIDGE = None
    return _BRIDGE


def ensure_tick(core_config=None):
    """Arm the singleton through cron_bridge (find-by-name first, create only
    when absent). Adapter shape only - the lifecycle laws live once, in
    cron_bridge. Degrades honestly to armed:false on a core-less host or a
    copy shipped without the bridge."""
    cb = _bridge()
    if cb is None:
        return {"armed": False, "reason": "cron_bridge not present"}
    jid = cb.ensure_tick(core_config)
    if jid is None:
        return {"armed": False, "reason": "core cron not importable"}
    return {"armed": True, "id": jid}


def teardown_tick():
    """Delete the tick job (never disable); False when absent or bridged to
    nothing."""
    cb = _bridge()
    return bool(cb is not None and cb.teardown_tick())


def _load_door():
    """Standalone door load for the cron subprocess (same by-path bootstrap
    the tests and the core plugin loader use; stdlib-only, no core needed)."""
    spec = importlib.util.spec_from_file_location(
        "_hw_watchdog_door", Path(__file__).resolve().parent / "__init__.py")
    assert spec is not None and spec.loader is not None
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    return door


def tick(door=None, cj=None):
    """One watchdog tick: census the resolved root, revive dead-runner runs,
    then keep the job iff the active set is non-empty (self-delete at drain).
    `cj` is accepted for call-shape compatibility; the seam cron_bridge
    honors is its own injected `_jobs()`."""
    if door is None:
        door = _load_door()
    if _COMMON is None:
        bind(door._common)
    scanned = _COMMON.iter_run_dirs([_COMMON.runs_root()])
    lock_states = _COMMON.runner_lock_states(scanned)
    active, revived = 0, []
    for r in scanned:
        st = door.run_state(r, telemetry=False, lock_state=lock_states.get(r))
        if not st or st["status"] in TERMINAL:
            continue
        active += 1
        # Revival scope mirrors act_wait: a run whose runner never verified
        # alive (pending, or interrupted after a boot) is orphaned work; a
        # raced spawn against a just-booting runner is a WORKFLOW_BUSY loser
        # under the runner's flock admission (the door's own law).
        if st["status"] not in ("pending", "interrupted") or st.get("runner_live"):
            continue
        if st.get("runner_lock") == "wedged":
            # Same single safety authority as the wait path: the heal refuses
            # on a live holder or a legacy lease shape; a refused heal falls
            # through to the honest status answer, never a false respawn.
            if _COMMON.heal_wedged_runner_lock(r).get("reason") != "healed":
                continue
            st = door.run_state(r, telemetry=False)
            if st.get("runner_live") or st.get("status") not in ("pending", "interrupted"):
                continue
        door._respawn_runner(r)
        revived.append(st["run_id"])
    out = {"active": active, "revived": revived}
    out["watchdog"] = ensure_tick() if active else {"removed": teardown_tick()}
    return out


def main():
    """Cron entry (`wf.py tick`, reached through the PR-1 shim): print the
    tick summary - no_agent stdout is the job's whole record - and exit 0
    whenever the tick itself ran."""
    print(json.dumps(tick()))
    return 0
