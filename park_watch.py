"""park_watch.py - the parked-work watchdog (WF-GRAFT-9; peer row atbrace:hw-36y).

Work parked on an external event (a machine-gate probe, a human-gate hold) is a
legitimate wait, but an un-woken, un-answered park must not hang forever: the
peer audit caught their adopt lanes exactly there (a blocked card the dispatcher
cannot progress, polled in silence), and ours has the same shape at holds with
no `hold_timeout` and at expired holds with no `default_option`.

Law: the park stays legitimate while the dispatcher can still reach the world,
so a strike counts only a DISPATCHER failure (the probe/wake could not be
dispatched at all, or the wake came back undelivered), never a probe that ran
and honestly reported "not ready". N consecutive strikes settle the park failed
loudly, and so does the time-box: the system floor under any park (default 6 h,
the tour-demo burn was 9.3 h). The clock is a persisted dict (`watch`): the
caller stores it in the gate's own mirror (gates/<id>.parked.json,
gates/<id>.held.json), so a runner restart replays the elapsed window instead of
restarting it, and a clean wake clears it so the next park gets a fresh window.
Settling is one-shot and idempotent: a settled watch keeps reporting its reason
and never un-settles, so a re-drive can neither re-open nor double-notify the
verdict (the loud notice itself is the run's existing run.failed wake, deduped
by the B3 instance identity).

Pure stdlib, no I/O in this module, no host imports: config resolution reads
the owner setting `park_watch` (bool | seconds | {timeout_s, strikes}) through
the caller's wfcommon handle, with test/sidecar-only env hooks
WF_PARK_WATCHDOG / WF_PARK_WATCHDOG_TIMEOUT_S / WF_PARK_WATCHDOG_STRIKES
(the WF_WAKE_SINK_PORT law: env is a test/sidecar override, production rides
the setting). Disabled returns None and every call site degrades to exactly
yesterday's behavior.
"""
import json
import os

DEFAULT_TIMEOUT_S = 6 * 3600
DEFAULT_STRIKES = 3


def config(wfcommon=None):
    """Resolve the watchdog as (timeout_s, strikes_max), or None when disabled.
    Precedence: env hook, then owner setting, then defaults. Junk in any layer
    falls back instead of crashing a park (honest degradation)."""
    env = os.environ.get("WF_PARK_WATCHDOG", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return None
    timeout, strikes = DEFAULT_TIMEOUT_S, DEFAULT_STRIKES
    v = None
    if wfcommon is not None:
        try:
            v = wfcommon.owner_setting("park_watch")
        except Exception:
            v = None
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except ValueError:
            try:
                v = float(v)
            except ValueError:
                v = None
    if isinstance(v, bool) and not v:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
        timeout = float(v)
    elif isinstance(v, dict):
        t, s = v.get("timeout_s"), v.get("strikes")
        if isinstance(t, (int, float)) and not isinstance(t, bool) and t > 0:
            timeout = float(t)
        if isinstance(s, (int, float)) and not isinstance(s, bool) and s > 0:
            strikes = int(s)
    e = os.environ.get("WF_PARK_WATCHDOG_TIMEOUT_S", "").strip()
    if e:
        try:
            t = float(e)
            if t > 0:
                timeout = t
        except ValueError:
            pass
    e = os.environ.get("WF_PARK_WATCHDOG_STRIKES", "").strip()
    if e:
        try:
            s = int(e)
            if s > 0:
                strikes = s
        except ValueError:
            pass
    return timeout, strikes


def tick(watch, now, dispatch_failed=False, timeout_s=DEFAULT_TIMEOUT_S,
         strikes_max=DEFAULT_STRIKES):
    """One watchdog tick for a parked unit. Mutates the persisted `watch` dict
    ({blocked_since, strikes, settled}); returns None while the park stays
    legitimate, or the settle reason ("strikes" | "timebox"). The caller
    persists the dict where it already persists the park's other state."""
    settled = watch.get("settled")
    if isinstance(settled, str) and settled:
        return settled                          # one-shot: the verdict stands
    if not isinstance(watch.get("blocked_since"), (int, float)):
        watch["blocked_since"] = now
        watch["strikes"] = 0
    if dispatch_failed:
        try:
            watch["strikes"] = int(watch.get("strikes", 0)) + 1
        except (TypeError, ValueError):
            watch["strikes"] = 1
    else:
        watch["strikes"] = 0                    # the dispatcher reached the world
    if watch["strikes"] >= strikes_max:
        watch["settled"] = "strikes"
        return "strikes"
    if now - watch["blocked_since"] >= timeout_s:
        watch["settled"] = "timebox"
        return "timebox"
    return None
