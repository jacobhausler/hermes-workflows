"""P3 subagent accounting: harvest delegate_task leaves onto an append-only spool.

ONE core hook, registered by the door's register() ONLY when the owner settings
list ``hooks_allow`` (``plugins.entries.hermes-workflows.settings.hooks_allow``)
carries the exact entry ``"subagent_accounting"`` — DEFAULT OFF, and the gate is
FAIL-CLOSED: a scalar, a mapping, or a reader failure all read as OFF. The feature
must be named to exist; it is never inferred.

WHAT THE SPOOL IS (the interface):
  ``<resolved hermes home>/plugin-state/hermes-workflows/subagent_accounting.jsonl``
  * one JSON object per delegate_task leaf child, appended in event order:
      {"ts": float epoch seconds,
       "parent_session_id": str|null,  # the session that delegated; null when absent
       "child_status": str,            # core's per-child status; "unknown" when absent
       "duration_ms": int|null,        # null when absent/unparseable — never fabricated
       "tool_call_count": int|null}    # len(tool_call_history); null when it is not a list
  * append-only: O_APPEND, one small write() per line, so concurrent appenders of
    the same home cannot interleave inside a line. Readers must tolerate a torn
    final line (skip unparseable lines; ``read_rows()`` below is the reference).
  * size law: past SPOOL_MAX_BYTES the spool rotates ONE bounded generation
    (spool -> spool.1, overwriting the previous .1). Nothing else is ever deleted;
    an operator may truncate or remove the spool at any time — the next harvest
    recreates it.
  No status/wait wiring: a read helper inside act_status would churn golden
  payloads for a metrics nicety, so the spool itself is the interface (this
  docstring is its man page); ``read_rows()`` serves ad-hoc tools.

HONEST COVERAGE: CLI-spawned workflow children do NOT fire ``subagent_stop`` —
core fires that hook only from the delegate_task result path
(hermes_cli: _fire_subagent_stop_hooks), i.e. in-process delegate_task leaves
inside plugin sessions. Workflow node accounting lives in the run dir
(run.json / events.jsonl / nodes/*.json); this spool complements those, it does
not replace them.

CALLER-THREAD LAW: core pins ``subagent_stop`` to the caller thread precisely so
an abandoned timeout worker cannot tear a half-write — the trade is that the
fire site waits on us. So the harvest is one mkdir probe + one small append, no
locking, no reading, no network.

FAIL-OPEN (card_enforcement's law): every path is guarded; a write that cannot
happen is a debug-log line. Accounting is optional, the session that pays for it
is not. Stdlib only; no host import beyond the wfcommon module the door injects
via bind() (path resolution is NOT reimplemented here).
"""
import json
import logging
import os
import time
from pathlib import Path

_LOG = logging.getLogger("hermes-workflows.subagent_accounting")

_COMMON = None        # the door injects its loaded wfcommon via bind()

ALLOW_KEY = "hooks_allow"
ALLOW_TOKEN = "subagent_accounting"
STATE_DIR_PARTS = ("plugin-state", "hermes-workflows")
SPOOL_NAME = "subagent_accounting.jsonl"
SPOOL_MAX_BYTES = 8 * 1024 * 1024


def bind(common):
    """The door injects its already-loaded wfcommon module (card_enforcement law)."""
    global _COMMON
    _COMMON = common


def enabled():
    """Fail-closed allow-list read, RAW (no plugin-ctx get_config): the gate is a
    register-time read and register()'s load-deadline budget is pinned at exactly
    ONE cached config read (test_hook_abandon_safety) — spent by model_tiers. The
    raw read answers the same ``settings.<key>``-else-legacy value with core's env
    expansion (same reader the runner/dashboard use), so every process agrees; a
    host with no YAML loader reads ``({}, {})`` — OFF, fail-closed."""
    if _COMMON is None:
        return False
    try:
        settings, legacy = _COMMON._raw_owner_settings()
        v = _COMMON._nested(settings, ALLOW_KEY)
        if v is _COMMON._UNSET:
            v = _COMMON._nested(legacy, ALLOW_KEY)
    except Exception:
        return False
    return isinstance(v, (list, tuple)) and ALLOW_TOKEN in v


def state_dir():
    """The plugin's state dir under the RESOLVED home, read at CALL time (the same
    profile-scoping law every other path in this plugin honours)."""
    return Path(_COMMON.hermes_home()) / Path(*STATE_DIR_PARTS)


def _spool_path():
    return state_dir() / SPOOL_NAME


def _row(parent_session_id, child_status, duration_ms, tool_call_history):
    """The accounting row: the four facts the spec names, honestly degraded —
    an absent or unparseable fact lands as null/'unknown', never a guessed number."""
    dur = duration_ms if isinstance(duration_ms, int) and not isinstance(duration_ms, bool) else None
    count = len(tool_call_history) if isinstance(tool_call_history, (list, tuple)) else None
    return {"ts": round(time.time(), 3),
            "parent_session_id": str(parent_session_id) if parent_session_id else None,
            "child_status": str(child_status) if child_status else "unknown",
            "duration_ms": dur,
            "tool_call_count": count}


def harvest(*, parent_session_id=None, child_status=None, duration_ms=None,
            tool_call_history=None, **_):
    """The ``subagent_stop`` callback. Named kwargs + absorb: core's payload evolves
    additively (parent_turn_id, child_session_id, child_role, child_summary,
    telemetry_schema_version, …) and none of it belongs on a metrics row —
    child_summary in particular is model prose. Returns None: this hook observes."""
    try:
        line = json.dumps(_row(parent_session_id, child_status, duration_ms,
                                tool_call_history), separators=(",", ":")) + "\n"
        p = _spool_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            if p.stat().st_size > SPOOL_MAX_BYTES:
                os.replace(p, p.with_name(p.name + ".1"))   # one bounded generation
        except FileNotFoundError:
            pass
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, line.encode("utf-8"))
        finally:
            os.close(fd)
    except Exception as exc:  # fail-open: never break the delegating session
        _LOG.debug("subagent accounting skipped (fail-open): %s", exc)


def read_rows(limit=None):
    """Reference reader (NOT wired into status/wait): parseable rows oldest-first,
    a torn or garbage line skipped not fatal, a missing spool reads as []."""
    try:
        raw = _spool_path().read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rows = []
    for ln in raw.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict):
            rows.append(r)
    return rows[-limit:] if isinstance(limit, int) and 0 < limit < len(rows) else rows
