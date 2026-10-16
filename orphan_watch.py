"""Orphan-held awareness (docs/orphan-held.md).

A run parked at a human gate whose OWNER session is dead waits silently forever.
Core fires `on_session_end` / `on_session_finalize` / `agent_loop_stopped` at the
moments "this session will never answer again"; these observers turn that into a
named state: an index row in `<runs_root>/orphan-held.jsonl`, an advisory
`orphan_at` stamp on the run's run.json, a status flag and `/wf orphans`.

Laws: advisory only (never kills, restarts, resumes or edits a graph); fail-open
everywhere (every public function swallows its own exceptions); stdlib-only; the
hook bodies do a few stat()s and a 64-line tail read, no subprocess/network.
Bound to the door's wfcommon via bind(), like card_enforcement.
"""
import fcntl
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

INDEX_NAME = "orphan-held.jsonl"
TAIL_LINES = 64
_COMMON = None
_TERMINAL_STATUS = {"done", "failed", "stopped"}
_RELEASE_EVENTS = {"gate.released", "gate.auto_released", "gate.skipped"}


def bind(common):
    global _COMMON
    _COMMON = common


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def enabled():
    """Default ON (`orphan_watch` owner setting; only an explicit false-ish value disables)."""
    try:
        v = _COMMON.owner_setting("orphan_watch")
    except Exception:
        return True
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() not in ("0", "false", "no", "off")
    return bool(v)


def _roots():
    primary = Path(_COMMON.runs_root())
    roots = [primary]
    try:
        legacy = Path(_COMMON.launch_runs_root())
        if legacy != primary:
            roots.append(legacy)
    except Exception:
        pass
    return roots


def index_path():
    return Path(_COMMON.runs_root()) / INDEX_NAME


# ---------- event tail ----------

def _tail_events(run, n=TAIL_LINES):
    """Last n parseable event dicts of <run>/events.jsonl (a truncated/garbled line is skipped)."""
    p = Path(run) / "events.jsonl"
    try:
        size = p.stat().st_size
        with open(p, "rb") as f:
            f.seek(max(0, size - 64 * 1024))
            data = f.read()
    except OSError:
        return []
    out = []
    for line in data.decode("utf-8", "replace").splitlines()[-n:]:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if isinstance(ev, dict):
            out.append(ev)
    return out


def held_gate(run):
    """The still-open `gate.held` in the events tail -> {gate_id, since, question} or None.
    Open = no later release/auto-release/skip of that gate and no later run.stopped."""
    open_gate = None
    for ev in _tail_events(run):
        name = ev.get("event")
        if name == "gate.held" and ev.get("node"):
            open_gate = {"gate_id": ev["node"], "since": ev.get("ts"), "question": ev.get("question")}
        elif name in _RELEASE_EVENTS and open_gate and ev.get("node") == open_gate["gate_id"]:
            open_gate = None
        elif name == "run.stopped":
            open_gate = None
    return open_gate


# ---------- index ----------

def read_rows(path=None):
    p = Path(path) if path else index_path()
    rows = []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rows
    for line in text.splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("run_id"):
            rows.append(row)
    return rows


def unrevoked(rows=None):
    """Latest row per (run_id, gate_id) that is not a revoke row, in file order."""
    latest = {}
    for row in (rows if rows is not None else read_rows()):
        latest[(row.get("run_id"), row.get("gate_id"))] = row
    return [r for r in latest.values() if not r.get("revoked")]


def _append(row):
    p = index_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _stamp(run, orphan_at):
    """Advisory run.json stamp/unstamp (orphan_at=None removes). Same lock file as the
    door's graph lock, taken NON-blocking: contention skips the stamp, never stalls a hook."""
    run = Path(run)
    try:
        lock = open(run / "graph.lock", "a+b")
    except OSError:
        return False
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        meta = _COMMON.jload(run / "run.json", None)
        if not isinstance(meta, dict):
            return False
        if orphan_at is None:
            if "orphan_at" not in meta:
                return True
            meta.pop("orphan_at", None)
        else:
            meta["orphan_at"] = orphan_at
        tmp = run / f"run.json.{os.getpid()}.orph.tmp"
        tmp.write_text(json.dumps(meta, ensure_ascii=False))
        os.replace(tmp, run / "run.json")
        return True
    finally:
        lock.close()


# ---------- the observers ----------

def session_matches(owner_sid, key):
    """Conservative fuzzy match: equal, or `key` ends with the id after a separator
    (gateway session keys are composite, the id is the suffix). Short ids never suffix-match."""
    if not owner_sid or not key:
        return False
    owner_sid, key = str(owner_sid), str(key)
    if key == owner_sid:
        return True
    return (len(owner_sid) >= 8 and key.endswith(owner_sid)
            and key[-len(owner_sid) - 1] in ":_-/|")


def mark_session(match, hook):
    """Scan candidate runs whose owner.session_id satisfies match(owner_sid); mark every
    orphan-held one. Returns the rows appended. Never raises."""
    rows_out = []
    try:
        if not enabled():
            return rows_out
        existing = {(r.get("run_id"), r.get("gate_id")) for r in unrevoked()}
        for run in _COMMON.iter_run_dirs(_roots()):
            try:
                meta = _COMMON.jload(run / "run.json", None)
                if not isinstance(meta, dict):
                    continue
                if meta.get("status") is not None and meta.get("status") not in ("running", "held"):
                    continue          # run.json rarely stores status; when it does, terminal is skipped
                sid = (meta.get("owner") or {}).get("session_id")
                if not sid or not match(sid):
                    continue
                gate = held_gate(run)
                if not gate or (run.name, gate["gate_id"]) in existing:
                    continue
                row = {"ts": _now(), "run_id": run.name, "gate_id": gate["gate_id"],
                       "session_id": sid, "hook": hook, "since": gate.get("since"),
                       "question": gate.get("question")}
                _append(row)
                _stamp(run, row["ts"])
                existing.add((run.name, gate["gate_id"]))
                rows_out.append(row)
            except Exception:
                continue
    except Exception:
        pass
    return rows_out


def _truthy(v):
    return bool(v) and str(v).lower() not in ("0", "false", "none")


def on_session_end(session_id=None, interrupted=None, turn_exit_reason=None, **_):
    """on_session_end fires after EVERY turn, not only at session death: a normally
    completed turn of a live session that parked a gate must NOT be marked. Only an
    interrupted turn (or an abort-shaped exit reason) means the session stopped answering."""
    try:
        reason = str(turn_exit_reason or "").lower()
        if not (_truthy(interrupted) or any(w in reason for w in ("interrupt", "abort", "shutdown", "cancel"))):
            return None
        if session_id:
            mark_session(lambda s: s == session_id, "on_session_end")
    except Exception:
        pass
    return None


def on_session_finalize(session_id=None, old_session_id=None, **_):
    """True session boundary (shutdown, /new, /reset). When a rotation carries old_session_id
    the OLD id is the dead one (session_id is its live successor)."""
    try:
        dead = old_session_id or session_id
        if dead:
            mark_session(lambda s: s == dead, "on_session_finalize")
    except Exception:
        pass
    return None


def on_agent_loop_stopped(session_key=None, **_):
    try:
        if session_key:
            mark_session(lambda s: session_matches(s, session_key), "agent_loop_stopped")
    except Exception:
        pass
    return None


HOOKS = {"on_session_end": on_session_end,
         "on_session_finalize": on_session_finalize,
         "agent_loop_stopped": on_agent_loop_stopped}


# ---------- read side + revoke ----------

def revoke_run(run_id, reason, by=None):
    """Append revoke rows for every unrevoked orphan row of run_id and clear the stamp.
    Returns the number revoked. Never raises."""
    n = 0
    try:
        for row in unrevoked():
            if row.get("run_id") != run_id:
                continue
            _append({"ts": _now(), "run_id": run_id, "gate_id": row.get("gate_id"),
                     "session_id": row.get("session_id"), "revoked": True,
                     "reason": reason, "by": by})
            n += 1
        for root in _roots():
            run = root / run_id
            if (run / "run.json").is_file():
                meta = _COMMON.jload(run / "run.json", None)
                if isinstance(meta, dict) and "orphan_at" in meta:
                    _stamp(run, None)
    except Exception:
        pass
    return n


def status_info(run, state, observer_sid=None):
    """For act_status: {gate_id, since} when this run is orphan-held, else None.
    A DIFFERENT live observer session revokes (re-attach) and sees no flag."""
    try:
        meta = _COMMON.jload(Path(run) / "run.json", None)
        if not isinstance(meta, dict) or not meta.get("orphan_at"):
            return None
        hg = (state or {}).get("held_gate") or {}
        if (state or {}).get("status") != "held" or not hg.get("id"):
            return None
        owner = (meta.get("owner") or {}).get("session_id")
        if observer_sid and owner and observer_sid != owner:
            revoke_run(Path(run).name, "reattach", by=observer_sid)
            return None
        since = next((r.get("since") or r.get("ts") for r in unrevoked()
                      if r.get("run_id") == Path(run).name and r.get("gate_id") == hg.get("id")),
                     meta["orphan_at"])
        return {"gate_id": hg.get("id"), "since": since}
    except Exception:
        return None


def render_orphans():
    """`/wf orphans` text: unrevoked rows still worth showing."""
    try:
        rows = unrevoked()
    except Exception:
        rows = []
    if not rows:
        return "No orphan-held runs."
    lines = [f"Orphan-held runs ({len(rows)}) — owner session ended while the run waits at a gate:"]
    for r in rows:
        q = r.get("question")
        lines.append(f"- {r.get('run_id')} gate `{r.get('gate_id')}` since {r.get('since') or r.get('ts')}"
                     f" (owner {r.get('session_id')}, seen by {r.get('hook')})"
                     + (f": {q}" if q else ""))
    lines.append("Answer: `workflow release run_id=<id> gate_id=<gate> answer=…` · "
                 "or `workflow stop run_id=<id>` · a new session's `wait`/`status` re-attaches.")
    return "\n".join(lines)
