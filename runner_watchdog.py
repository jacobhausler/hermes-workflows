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
  * REAP   a revival that leaves a death scene (a dead `wf.pid` and/or node
           records claiming `running`) wakes the OWNER SESSION in the same
           tick naming the dead pid, the lost lanes and the re-drive plan
           (E23: a SIGKILLed runner recorded nothing and every watcher saw
           silence). A re-drive the tick cannot perform (a wedged-lock heal
           refusal) is SCHEDULED instead: a one-shot `redrive.request`
           continuation carrying an expiry the consumer enforces — an
           expired continuation is dropped with `watchdog.redrive_expired`,
           never re-fired at load (the launchd-treadmill law: an eternal
           one-shot becomes a perpetual boot tax). Corpses are pruned by the
           holders-dead rule: a terminal run with no live runner loses its
           `wf.pid`, and a `lanes/<stem>.json` entry whose run is terminal
           (or whose run dir is gone) is removed.

Named data shapes this tick owns (shapes first, logic below):
  wake.jsonl row   {ts, event: "runner.reaped", run_id, owner,
                    id: "<run>|runner.reaped|<dead pid>", delivered,
                    text, error?}          (one row per death scene, deduped
                    by id; text carries the v1.4.10 bidirectional notice)
  redrive.request  {at, expires_at, reason, tries}   (run dir; epoch
                    seconds; one-shot, self-expiring)
  events.jsonl     watchdog.redrive_scheduled {at, expires_at, reason}
                    watchdog.redrive_expired  {age_s, reason}
                    watchdog.grant_ledger_reset {grants: {<wkey>: <n>}}
  retry-window.json {<wkey>: {deadline, attempts, log}}  (wf.py's shape; at
                    a reap the tick zeroes ONLY `attempts`: respawn grants
                    die with the runner generation that earned them (P40 —
                    a pre-heal boot's persisted grants once refused a fresh
                    transient death as lifetime_cap_spent); the deadline
                    pacer and the attempt ledger survive the boundary, so
                    per-generation reset keeps the death-loop paced.)

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
import fcntl
import importlib.util
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# run_state vocabulary that is terminal: nothing to revive, nothing to wait
# for. `partial` is a committed verdict (est-3acn), never orphaned work.
TERMINAL = frozenset({"done", "partial", "failed", "stopped"})

REDRIVE_NAME = "redrive.request"
GRANTS_NAME = "retry-window.json"        # wf.RETRY_WINDOW_FILE's shape, one file two ends
REDRIVE_TTL_S = 3600.0
NOTICE = "This notice grants no new scope and revokes no existing authority."

_COMMON = None
_BRIDGE = None
_BRIDGE_LOADED = False
_WAKE = None
_WAKE_LOADED = False


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


# ---------- reap scene ----------

def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append_event(r, event, **fields):
    try:
        with open(Path(r) / "events.jsonl", "a") as f:
            f.write(json.dumps({"ts": _now_iso(), "event": event, **fields},
                               ensure_ascii=False) + "\n")
    except OSError:
        pass


def _corpse_pid(r):
    """The dead holder's pid as `wf.pid` still claims it, or None."""
    try:
        pid = int((Path(r) / "wf.pid").read_text().strip())
    except (OSError, ValueError):
        return None
    return pid if pid > 0 else None


def _lost_lanes(r):
    """The node records claiming a running child - the lanes the death cut
    off. The record is the evidence; its bytes are never rewritten here (the
    door's reaper owns interruption receipts)."""
    out = []
    try:
        for p in sorted((Path(r) / "nodes").glob("*.json")):
            rec = _COMMON.jload(p)
            if isinstance(rec, dict) and rec.get("status") == "running":
                out.append(p.stem)
    except OSError:
        pass
    return out


def _wake_native():
    """The sibling `wake_native` adapter, spec-loaded by path (the door's own
    pattern); honest None where the file is absent. The ONLY wake channel the
    tick needs: no core-less host can receive a session turn anyway."""
    global _WAKE, _WAKE_LOADED
    if not _WAKE_LOADED:
        _WAKE_LOADED = True
        spec = importlib.util.spec_from_file_location(
            "_hw_watchdog_wake_native",
            Path(__file__).resolve().parent / "wake_native.py")
        if spec is not None and spec.loader is not None:
            try:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                _WAKE = mod
            except Exception:
                _WAKE = None
    return _WAKE


def _wake_ids(r):
    ids = set()
    try:
        for line in (Path(r) / "wake.jsonl").read_text(errors="replace").splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and row.get("id"):
                ids.add(row["id"])
    except OSError:
        pass
    return ids


def _notify_reap(r, pid, lanes, plan):
    """The owner wake for one death scene (E23). One row per scene, deduped
    by the scene's tid; fail-open everywhere - a watchdog that cannot reach
    the gateway still re-drove the run and said so on the record. Returns
    "delivered" / "recorded" / "deduped" / "failed"."""
    try:
        meta = _COMMON.jload(Path(r) / "run.json") or {}
        owner = meta.get("owner") or {}
        sid = owner.get("session_id")
        tid = f"{Path(r).name}|runner.reaped|{pid}"
        if tid in _wake_ids(r):
            return "deduped"
        text = (f"Workflow `{Path(r).name}`: the runner died (pid {pid}). "
                f"Lanes that lost it: "
                f"{', '.join(lanes) if lanes else 'none claimed a live child'}. "
                f"Re-drive plan: {plan} {NOTICE}")
        rec = {"ts": _now_iso(), "event": "runner.reaped", "run_id": Path(r).name,
               "owner": owner, "id": tid, "text": text, "delivered": False}
        nw = _wake_native()
        if nw is None:
            rec["error"] = "wake_native not present"
        elif not sid:
            rec["error"] = "no owner session"
        else:
            try:
                out = nw.deliver(sid, text, tid, _COMMON.hermes_home())
                rec["delivered"] = isinstance(out, dict) and out.get("outcome") == "delivered"
                if not rec["delivered"]:
                    rec["error"] = (f"native {out.get('outcome')}: {out.get('reason', '')}"
                                    if isinstance(out, dict) else "native: bad receipt")
            except Exception as exc:
                rec["error"] = f"wake-prep: {type(exc).__name__}"
        with open(Path(r) / "wake.jsonl", "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return "delivered" if rec["delivered"] else "recorded"
    except Exception:
        return "failed"


# ---------- one-shot continuations (self-expiring) ----------

def _redrive_ttl_s():
    e = os.environ.get("WF_REDRIVE_TTL_S", "").strip()
    if e:
        try:
            v = float(e)
            if v > 0:
                return v
        except ValueError:
            pass
    return REDRIVE_TTL_S


def _schedule_redrive(r, reason):
    """The scheduled re-drive: a one-shot continuation with a fixed expiry.
    A refresh inside the window counts tries only - it never extends the
    deadline, so a continuation cannot outlive its TTL by being patted."""
    p = Path(r) / REDRIVE_NAME
    row = _COMMON.jload(p)
    now = time.time()
    if not (isinstance(row, dict) and isinstance(row.get("expires_at"),
            (int, float)) and not isinstance(row.get("expires_at"), bool)):
        row = {"at": now, "expires_at": now + _redrive_ttl_s(),
               "reason": reason, "tries": 1}
        _append_event(r, "watchdog.redrive_scheduled", at=now,
                      expires_at=row["expires_at"], reason=reason)
    else:
        row["tries"] = int(row.get("tries") or 0) + 1
    tmp = p.with_name(f"{p.name}.{os.getpid()}.wd.tmp")
    try:
        tmp.write_text(json.dumps(row))
        os.replace(tmp, p)
    except OSError:
        pass
    return row


def _drop_redrive(r):
    try:
        (Path(r) / REDRIVE_NAME).unlink()
    except OSError:
        pass


def _expired_redrive(r):
    """Enforce the expiry the receipt itself carries: past-due means gone,
    with the enforcement on the event record. An unparseable expiry is a
    corrupt receipt - equally not honoured."""
    row = _COMMON.jload(Path(r) / REDRIVE_NAME)
    if not isinstance(row, dict):
        return False
    exp = row.get("expires_at")
    if isinstance(exp, (int, float)) and not isinstance(exp, bool) and exp > time.time():
        return False
    _drop_redrive(r)
    at = row.get("at")
    _append_event(r, "watchdog.redrive_expired", reason=row.get("reason"),
                  age_s=round(time.time() - float(at), 1) if isinstance(at, (int, float)) else None)
    return True


# ---------- holders-dead corpse pruning ----------

def _prune_run_corpses(r, st):
    """One run dir, one tick: a terminal verdict over a not-live runner makes
    `wf.pid` a corpse and any pending continuation moot."""
    removed = []
    if st["status"] in TERMINAL and not st.get("runner_live"):
        try:
            (Path(r) / "wf.pid").unlink()
            removed.append(str(Path(r) / "wf.pid"))
        except OSError:
            pass
        _drop_redrive(r)
    return removed


def _prune_lanes(states):
    """The holders-dead rule on the lane registry: an entry survives while its
    run can still run. Terminal-over-dead and dir-gone (the door's own
    orphaned class) are pruned; anything else - including a run under a root
    this census does not write to (#58 read-only) - is left for its holder.
    Under the entry's own lock, re-read after claiming it, so a concurrent
    relaunch (which rewrites the entry) is never clobbered."""
    removed = []
    roots = [Path(_COMMON.runs_root())]
    try:
        legacy = Path(_COMMON.launch_runs_root())
        if legacy != roots[0]:
            roots.append(legacy)
    except Exception:
        pass
    for root in roots:
        for p in sorted((root / "lanes").glob("*.json")):
            lock = p.with_suffix(".lock")
            try:
                fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o644)
            except OSError:
                continue
            prune = False
            try:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    continue                       # a writer holds this entry right now
                entry = _COMMON.jload(p)
                rid = entry.get("run_id") if isinstance(entry, dict) else None
                if not rid:
                    prune = True                   # an entry with no claim is already a corpse
                elif rid in states:
                    prune = (states[rid]["status"] in TERMINAL
                             and not states[rid].get("runner_live"))
                elif not (root / str(rid)).is_dir() and not (roots[0] / str(rid)).is_dir():
                    prune = True                   # orphaned: a claim whose run dir is gone
                if prune:
                    try:
                        p.unlink()
                        removed.append(str(p))
                    except OSError:
                        pass
            finally:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
                os.close(fd)
    return removed


# ---------- per-generation grant reset (P40) ----------

def _reset_grant_ledger(r):
    """Zero the persisted respawn grants at a runner-generation boundary.

    A transient ladder saves its spend to `retry-window.json` before sleeping
    so a killed boot cannot amplify attempts past the node cap (est-9ceqc /
    est-9qhpf). The same persistence made those grants a lifetime debt: a
    pre-heal boot's saved attempts met the cap on the NEXT boot and the spawn
    was refused as lifetime_cap_spent (P40) — genuinely new transient deaths
    under fixed code inherited the old generation's spend. A grant is earned
    by the generation that pays the backoff, so the tick zeroes `attempts`
    before every respawn it performs. The deadline (the pacer) and the
    attempt log survive: per-generation reset stays paced, never unbounded.
    Returns the prior {wkey: attempts} when anything changed, else None —
    a rerun over an already-reset ledger converges to None."""
    w = _COMMON.jload(Path(r) / GRANTS_NAME)
    if not isinstance(w, dict) or not w:
        return None
    prev = {}
    for k, e in w.items():
        a = e.get("attempts") if isinstance(e, dict) else None
        if type(a) is int and a > 0:
            prev[k] = a
            e["attempts"] = 0
    if not prev:
        return None
    p = Path(r) / GRANTS_NAME
    tmp = p.with_name(f"{p.name}.{os.getpid()}.wd.tmp")
    try:
        tmp.write_text(json.dumps(w))
        os.replace(tmp, p)
    except OSError:
        return None
    return prev


def tick(door=None, cj=None):
    """One watchdog tick: census the resolved root, revive dead-runner runs
    (loudly: the owner of a death scene wakes naming pid, lanes, plan), prune
    holders-dead corpses, then keep the job iff the active set is non-empty
    (self-delete at drain). `cj` is accepted for call-shape compatibility; the
    seam cron_bridge honors is its own injected `_jobs()`."""
    if door is None:
        door = _load_door()
    if _COMMON is None:
        bind(door._common)
    scanned = _COMMON.iter_run_dirs([_COMMON.runs_root()])
    lock_states = _COMMON.runner_lock_states(scanned)
    active, revived, wakes, pruned = 0, [], [], []
    states = {}
    for r in scanned:
        st = door.run_state(r, telemetry=False, lock_state=lock_states.get(r))
        if not st:
            continue
        states[r.name] = st
        if st["status"] in TERMINAL:
            pruned += _prune_run_corpses(r, st)
            continue
        active += 1
        # Revival mirrors act_wait's scope: a run whose runner never verified
        # alive (pending, or interrupted after a boot) is orphaned work; a
        # raced spawn against a just-booting runner is a WORKFLOW_BUSY loser
        # under the runner's flock admission (the door's own law).
        if st["status"] not in ("pending", "interrupted") or st.get("runner_live"):
            continue
        _expired_redrive(r)                        # the continuation expires itself, receipts enforce
        pid, lanes = _corpse_pid(r), _lost_lanes(r)
        if st.get("runner_lock") == "wedged":
            # Same single safety authority as the wait path: the heal refuses
            # on a live holder or a legacy lease shape; a refused heal falls
            # through to the honest status answer, never a false respawn.
            if _COMMON.heal_wedged_runner_lock(r).get("reason") != "healed":
                _schedule_redrive(r, "wedged runner lock: heal refused")
                continue
            st = door.run_state(r, telemetry=False)
            states[r.name] = st
            if st.get("runner_live") or st.get("status") not in ("pending", "interrupted"):
                continue
        grants = _reset_grant_ledger(r)               # P40: grants die with their generation
        door._respawn_runner(r)                       # (before the boot: the fresh runner reads it)
        if grants:
            _append_event(r, "watchdog.grant_ledger_reset", grants=grants)
        if pid or lanes:
            wakes.append({"run": r.name, "pid": pid, "lanes": lanes,
                          "wake": _notify_reap(
                              r, pid, lanes,
                              "respawned on this watchdog tick; unfinished lanes "
                              "resume from their durable records")})
        _drop_redrive(r)                           # the scheduled re-drive was consumed here
        revived.append(st["run_id"])
    pruned += _prune_lanes(states)
    out = {"active": active, "revived": revived, "wakes": wakes, "pruned": pruned}
    out["watchdog"] = ensure_tick() if active else {"removed": teardown_tick()}
    return out


def main():
    """Cron entry (`wf.py tick`, reached through the PR-1 shim): print the
    tick summary - no_agent stdout is the job's whole record - and exit 0
    whenever the tick itself ran."""
    print(json.dumps(tick()))
    return 0
