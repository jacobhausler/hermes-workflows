"""Session-keyed pending-card ledger (replaces the per-turn runs-root scan).

One small JSON file at ``<runs_root>/card-ledger.json``::

    {session_id: {run_id: {"state": "pending|held", "ts": iso, "name": str}}}

Hooks write it at the moment the facts happen (``post_tool_call`` sees every
``workflow`` launch); the card shipper and the ``pre_llm_call`` reminder only
READ it. Nothing here enumerates run directories.

Laws:
* atomic writes (tmp + os.replace) under an in-process lock AND an advisory
  ``flock`` on a sidecar file (stdlib ``fcntl``, skipped where absent);
* tolerant load: any unreadable/corrupt/wrong-shape file reads as ``{}`` with
  ONE warning line on stderr per path+reason — never an exception;
* every public function is fail-open (returns a neutral value on any error);
* the in-process dict is a write-through mirror, refreshed whenever the file's
  (mtime_ns, size) stamp moves, so a sibling process's writes are seen.
"""
import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

LEDGER_NAME = "card-ledger.json"
STATES = ("pending", "held")

_LOCK = threading.RLock()
_ROOT_FN = None          # callable -> runs root (bind())
_MIRROR = {}             # path str -> {"stamp": (mtime_ns, size), "data": dict}
_WARNED = set()


def bind(root_fn):
    """Wire the door's runs-root resolver (one resolver, never re-typed here)."""
    global _ROOT_FN
    _ROOT_FN = root_fn


def path():
    """The ledger file for the CURRENT runs root, or None when unbound/unresolvable."""
    try:
        if _ROOT_FN is None:
            return None
        return Path(_ROOT_FN()) / LEDGER_NAME
    except Exception:
        return None


def _warn(p, why):
    key = (str(p), why)
    if key in _WARNED:
        return
    _WARNED.add(key)
    try:
        print(f"card-ledger: {why} ({p}); treating as empty", file=sys.stderr)
    except Exception:
        pass


def _valid(raw):
    if not isinstance(raw, dict):
        return False
    for sess, runs in raw.items():
        if not isinstance(sess, str) or not isinstance(runs, dict):
            return False
        for rid, ent in runs.items():
            if not isinstance(rid, str) or not isinstance(ent, dict):
                return False
    return True


def _load(p):
    """The ledger dict for path p ({} on any problem). Caller holds _LOCK."""
    key = str(p)
    try:
        st = os.stat(p)
    except FileNotFoundError:
        _MIRROR.pop(key, None)
        return {}
    except OSError as exc:
        _warn(p, f"unreadable: {type(exc).__name__}")
        return {}
    stamp = (st.st_mtime_ns, st.st_size)
    hit = _MIRROR.get(key)
    if hit is not None and hit["stamp"] == stamp:
        return hit["data"]
    try:
        raw = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        _warn(p, f"corrupt or unreadable: {type(exc).__name__}")
        _MIRROR.pop(key, None)
        return {}
    if not _valid(raw):
        _warn(p, "wrong shape")
        _MIRROR.pop(key, None)
        return {}
    _MIRROR[key] = {"stamp": stamp, "data": raw}
    return raw


def _save(p, data):
    """Atomic write: tmp + os.replace. Caller holds _LOCK. Raises OSError."""
    tmp = Path(f"{p}.tmp.{os.getpid()}.{threading.get_ident()}")
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(tmp, p)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass
    try:
        st = os.stat(p)
        _MIRROR[str(p)] = {"stamp": (st.st_mtime_ns, st.st_size), "data": data}
    except OSError:
        _MIRROR.pop(str(p), None)


class _FileLock:
    """Cross-process advisory lock on <ledger>.lock; a no-op where fcntl is absent."""

    def __init__(self, p):
        self._path = f"{p}.lock"
        self._fh = None

    def __enter__(self):
        try:
            import fcntl
            self._fh = open(self._path, "a+")
            fcntl.flock(self._fh, fcntl.LOCK_EX)
        except Exception:
            self._fh = None
        return self

    def __exit__(self, *exc):
        if self._fh is not None:
            try:
                import fcntl
                fcntl.flock(self._fh, fcntl.LOCK_UN)
                self._fh.close()
            except Exception:
                pass
            self._fh = None
        return False


def _mutate(fn):
    """Read-modify-write under both locks. Returns True when the write landed."""
    p = path()
    if p is None:
        return False
    try:
        with _LOCK:
            try:
                Path(p).parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            with _FileLock(p):
                # deep copy: the mirror must not change before the write lands
                data = json.loads(json.dumps(_load(p)))
                if fn(data) is False:
                    return True          # nothing to change
                for sess in [s for s, runs in data.items() if not runs]:
                    del data[sess]
                _save(p, data)
                return True
    except Exception as exc:
        _warn(p, f"write failed: {type(exc).__name__}")
        return False


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def add(session_id, run_id, name="", state="pending"):
    """Record a launched run as owing a card. Idempotent (keeps the first ts)."""
    if not session_id or not run_id or state not in STATES:
        return False

    def fn(data):
        runs = data.setdefault(session_id, {})
        old = runs.get(run_id)
        runs[run_id] = {"state": state, "ts": (old or {}).get("ts") or _now(),
                        "name": str(name or (old or {}).get("name") or "")}
    return _mutate(fn)


def set_state(session_id, run_id, state):
    """Move an EXISTING entry between pending/held; unknown entries are untouched."""
    if state not in STATES:
        return False

    def fn(data):
        ent = (data.get(session_id) or {}).get(run_id)
        if ent is None or ent.get("state") == state:
            return False
        ent["state"] = state
    return _mutate(fn)


def drop(session_id, run_id):
    """Remove an entry (shipped, pasted, or terminal). Absent is fine."""
    def fn(data):
        runs = data.get(session_id)
        if not runs or run_id not in runs:
            return False
        del runs[run_id]
    return _mutate(fn)


def entries(session_id):
    """[(run_id, entry)] for one session, newest ts first; [] on any problem."""
    p = path()
    if p is None or not session_id:
        return []
    try:
        with _LOCK:
            runs = dict(_load(p).get(session_id) or {})
        return sorted(runs.items(), key=lambda kv: (str(kv[1].get("ts", "")), kv[0]),
                      reverse=True)
    except Exception:
        return []
