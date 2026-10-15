"""Door-side index of currently-open human gates (PR-3: zero-turn gate answers).

``<runs_root>/gate-index.jsonl`` is append-only JSON lines::

    {"ts", "op": "open"|"close", "run_id", "gate_id", "session_key", "session_id",
     "options": [...], "expires"?}

It exists so the ``post_gateway_admission`` handler (see ``__init__.py::_admission_handler``)
can answer "does THIS session hold exactly one open gate, and what are its options?" with
one small file read and no run-dir scan.

Power, not correctness: every public function swallows its own exceptions (debug line only).
The index can only ever cause a *missed* shortcut (the human's message then runs as an ordinary
agent turn); it can never release anything by itself — the handler re-verifies the hold against
the run's own read model and the release route re-checks everything.

Stdlib-only; no host imports.
"""
import fcntl
import json
import os
import sys
import time
from pathlib import Path

INDEX_NAME = "gate-index.jsonl"
COMPACT_ROWS = 500          # rewrite to the open set past this many rows
SCAN_MAX_BYTES = 1 << 20    # tail-scan bound; compaction keeps the file far below this

# In-process fast path: root -> ((size, mtime_ns), {(run_id, gate_id), ...}) of OPEN keys as of
# the last scan/append WE did. Valid only while the file signature is unchanged; any other
# writer (another process, compaction) changes the signature and forces a re-scan.
_SEEN = {}


def _dbg(msg):
    if os.environ.get("WF_GATE_INDEX_DEBUG"):
        print(f"gate_index: {msg}", file=sys.stderr)


def index_path(root):
    return Path(root) / INDEX_NAME


def _sig(p):
    try:
        st = p.stat()
        return (st.st_size, st.st_mtime_ns)
    except OSError:
        return None


def _read_rows(p):
    """Parsed rows, tail-bounded. Corrupt / non-dict lines are skipped."""
    try:
        size = p.stat().st_size
    except OSError:
        return [], 0
    with open(p, "rb") as f:
        if size > SCAN_MAX_BYTES:
            f.seek(size - SCAN_MAX_BYTES)
            f.readline()                      # drop the (probably partial) first line
        raw = f.read()
    rows = []
    for line in raw.splitlines():
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue
        if isinstance(row, dict) and row.get("op") in ("open", "close") \
                and isinstance(row.get("run_id"), str) and isinstance(row.get("gate_id"), str):
            rows.append(row)
    return rows, len(raw.splitlines())


def _fold(rows):
    """Open set as an insertion-ordered dict {(run_id, gate_id): last open row}."""
    open_ = {}
    for row in rows:
        key = (row["run_id"], row["gate_id"])
        if row["op"] == "open":
            open_[key] = row
        else:
            open_.pop(key, None)
    return open_


def open_rows(root, session_key=None):
    """Currently-open rows (optionally for one session), oldest first. Never raises."""
    try:
        p = index_path(root)
        if not p.exists():
            return []
        rows, _n = _read_rows(p)
        now = time.time()
        out = []
        for row in _fold(rows).values():
            if session_key is not None and row.get("session_key") != session_key:
                continue
            exp = row.get("expires")
            if isinstance(exp, (int, float)) and exp < now:
                continue
            out.append(row)
        return out
    except Exception as e:  # noqa: BLE001 — best-effort by design
        _dbg(f"open_rows: {type(e).__name__}: {e}")
        return []


def _append(root, row):
    p = index_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    with open(p.with_name(INDEX_NAME + ".lock"), "a+b") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
            try:
                os.write(fd, line)
            finally:
                os.close(fd)
            _maybe_compact_locked(p)
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def _maybe_compact_locked(p):
    rows, n = _read_rows(p)
    if n <= COMPACT_ROWS:
        return False
    _rewrite_open_locked(p, rows)
    return True


def _rewrite_open_locked(p, rows):
    keep = list(_fold(rows).values())
    tmp = p.with_name(f"{INDEX_NAME}.{os.getpid()}.tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n"
                           for r in keep), encoding="utf-8")
    os.replace(tmp, p)


def compact(root):
    """Force-compact to exactly the open set. Returns the number of rows kept (None on error)."""
    try:
        p = index_path(root)
        if not p.exists():
            return 0
        with open(p.with_name(INDEX_NAME + ".lock"), "a+b") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            try:
                rows, _n = _read_rows(p)
                _rewrite_open_locked(p, rows)
                _SEEN.pop(str(root), None)
                return len(_fold(rows))
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)
    except Exception as e:  # noqa: BLE001
        _dbg(f"compact: {type(e).__name__}: {e}")
        return None


def _is_open(root, key):
    p = index_path(root)
    sig = _sig(p)
    seen = _SEEN.get(str(root))
    if seen and seen[0] == sig and sig is not None:
        return key in seen[1]
    rows, _n = _read_rows(p) if sig is not None else ([], 0)
    keys = set(_fold(rows))
    _SEEN[str(root)] = (sig, keys)
    return key in keys


def _remember(root):
    p = index_path(root)
    rows, _n = _read_rows(p) if p.exists() else ([], 0)
    _SEEN[str(root)] = (_sig(p), set(_fold(rows)))


def note_open(root, run_id, gate_id, session_key, session_id=None, options=None, expires=None):
    """Record that (run_id, gate_id) is holding for ``session_key``. Dedupes: a gate already open
    in the index is not re-appended. Returns True when a row was appended."""
    try:
        if not (root and run_id and gate_id and session_key):
            return False
        key = (run_id, gate_id)
        if _is_open(root, key):
            return False
        row = {"ts": round(time.time(), 3), "op": "open", "run_id": run_id, "gate_id": gate_id,
               "session_key": session_key, "session_id": session_id or None,
               "options": [str(o) for o in (options or [])]}
        if expires is not None:
            row["expires"] = expires
        _append(root, row)
        _remember(root)
        return True
    except Exception as e:  # noqa: BLE001
        _dbg(f"note_open: {type(e).__name__}: {e}")
        return False


def note_close(root, run_id, gate_id=None):
    """Close one gate, or (gate_id=None) every open gate of the run. Returns rows appended."""
    try:
        if not (root and run_id):
            return 0
        p = index_path(root)
        if not p.exists():
            return 0
        rows, _n = _read_rows(p)
        n = 0
        for (rid, gid), orow in _fold(rows).items():
            if rid != run_id or (gate_id is not None and gid != gate_id):
                continue
            _append(root, {"ts": round(time.time(), 3), "op": "close", "run_id": rid,
                           "gate_id": gid, "session_key": orow.get("session_key")})
            n += 1
        if n:
            _remember(root)
        return n
    except Exception as e:  # noqa: BLE001
        _dbg(f"note_close: {type(e).__name__}: {e}")
        return 0


# ---------- dispatch witness (observer half; flag `dispatch_witness`) ----------
WITNESS_NAME = "dispatch-witness.jsonl"
WITNESS_MAX_BYTES = 2 * 1024 * 1024


def witness_row(event=None, **_kw):
    """One correlation row from a ``pre_gateway_dispatch`` payload. Never raises; junk -> nulls.

    ``decision_allowed`` is None BY DESIGN: core runs every ``pre_gateway_dispatch`` callback
    before it picks a winner and does not pass earlier verdicts to later callbacks, so an
    observer cannot see the final decision. The row's value is existence: an inbound with a
    row here and no downstream turn/admission is a dropped inbound, typed instead of forensic.
    """
    src = getattr(event, "source", None)

    def _s(v):
        if v is None:
            return None
        v = getattr(v, "value", v)          # Platform enum -> its string
        return str(v)[:200]

    return {"ts": round(time.time(), 3),
            "platform": _s(getattr(src, "platform", None)),
            "chat_id": _s(getattr(src, "chat_id", None)),
            "user_id": _s(getattr(src, "user_id", None)),
            "message_id": _s(getattr(event, "message_id", None)),
            "internal": bool(getattr(event, "internal", False)),
            "text_len": len(getattr(event, "text", "") or "") if isinstance(getattr(event, "text", ""), str) else None,
            "decision_allowed": None,
            "decision_skipped_reason": None}


def witness_append(root, row, max_bytes=WITNESS_MAX_BYTES):
    """Append one row to ``<root>/dispatch-witness.jsonl``; rotate to ``.1`` at the cap
    (one generation kept). Never raises. Returns True when written."""
    try:
        p = Path(root) / WITNESS_NAME
        p.parent.mkdir(parents=True, exist_ok=True)
        line = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        with open(p.with_name(WITNESS_NAME + ".lock"), "a+b") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            try:
                try:
                    if p.stat().st_size + len(line) > max_bytes:
                        os.replace(p, p.with_name(WITNESS_NAME + ".1"))
                except FileNotFoundError:
                    pass
                fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
                try:
                    os.write(fd, line)
                finally:
                    os.close(fd)
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)
        return True
    except Exception as e:  # noqa: BLE001
        _dbg(f"witness_append: {type(e).__name__}: {e}")
        return False
