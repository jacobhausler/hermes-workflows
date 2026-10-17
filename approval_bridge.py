"""P5 native approval surface for human gates (config-gated, default OFF).

When owner settings list the feature (``plugins.entries.hermes-workflows.settings
.hooks_bridge_allow`` containing ``"approval_bridge"``), a held human gate is
ALSO presented through the host's native approval channel: the same approve/deny
card the dangerous-command gate rides, so an operator already living in the
gateway surface sees the hold there without polling. This module is the ONLY
place the plugin registers the approval-hook pair; the door registers it from
register() behind the allow-list read (default-off = zero registrations, zero
threads, payloads byte-identical).

Authority law (the reason this bridge cannot speak): the emitted card text is
the runner's OWN wake sentence — the ``text`` field of the run's ``wake.jsonl``
gate.held row, verbatim. Gate question/options/context are graph-authored DATA
that live in events.jsonl, the status payload and the desktop gate card; they
never enter the approval surface, so a graph author cannot address the owner
through it. The bridge authors no gate prose: its ``description`` is a constant
protocol sentence, identical for every gate.

Lifecycle (one hold event = one instance = at most one release):
  * a daemon tailer watches ``<runs_root>/*/events.jsonl`` for appended
    ``gate.held`` rows (offsets seeded on first sight — history never re-fires);
  * each new row mints an idempotency token ``sha256(run|gate|offset|ts)[:16]``
    — the per-gate-instance identity — and an emitter thread presents it on the
    native channel with ``pattern_key = "wf-gate:<token>"``;
  * the core channel fires ``pre_approval_request`` (our observer correlates the
    token, records the sighting) and ``post_approval_response`` (our observer
    RESOLVES): an approve-shape choice maps to exactly one release through the
    plugin's OWN door path (``act_release`` — the same function the tool action
    dispatches to, so the answer rides the CAS, the answer file and the respawn
    law); deny answers NOTHING (a deny is a hard halt, and the gate keeps its
    own options for the tool/desktop path); timeout/cancel/notify_failed answer
    nothing either — silence is not consent.
  * FORGERY/DUPLICATION: a post response whose token this process never minted
    is ignored; a second response for a token already resolved is ignored; the
    door's ``gate already answered`` refusal backs both from the write side.

Degradation is SILENT for the bridge — no core, no gateway notifier, no wake
row, vanished run dir — and the desktop/tool release path is untouched. The
holder of record for a hold stays the run dir; this surface is a copy.
"""
import hashlib
import json
import re
import sys
import threading

FEATURE = "approval_bridge"
SETTING_KEY = "hooks_bridge_allow"          # settings key holding the allow-list
TOKEN_PREFIX = "wf-gate:"
TOKEN_RE = re.compile(r"^[0-9a-f]{16}$")
_APPROVE_SHAPED = ("once", "session", "always")   # core approval choices meaning yes
ANSWER_APPROVE = "approve"                  # the answer token the release records
TICK_S = 5.0
_MAX_INFLIGHT = 8                           # emissions presented and unanswered
_KEEP_RESOLVED = 256                        # resolved-token FIFO cap
DESCRIPTION = ("hermes-workflows gate approval — once answers the held gate with "
               "'approve'; deny leaves the hold untouched. Question and options: "
               "workflow status or the desktop gate card.")

_lock = threading.RLock()
_door = None
_common = None
_offsets = {}                # run_id -> byte offset seeded/consumed in events.jsonl
_instances = {}              # token -> {run_id, gate_id, state}
_resolved_order = []         # FIFO of resolved tokens for the bounded map
_watch_thread = None
_stop = threading.Event()
# Test seam: the presentation call. Returns the channel decision dict, or None
# when the native approval channel cannot be reached (silent degradation).
_native_present = None


def allowed(common):
    """True only when the owner allow-list names FEATURE. Anything unreadable,
    absent or wrongly shaped is OFF — the bridge fails closed, never guessed."""
    try:
        v = common.owner_setting(SETTING_KEY)
    except Exception:
        return False
    if v is None:
        return False
    if isinstance(v, (list, tuple)):
        return FEATURE in [str(x).strip() for x in v]
    if isinstance(v, str):
        return FEATURE in [s for s in v.replace(",", " ").split() if s]
    return False


def maybe_enable(ctx, door, common):
    """Called from the door's register(). Returns True when armed. With the
    allow-list off this reads one setting and returns — no import of core, no
    hook registration, no thread: every other path byte-identical."""
    global _door, _common, _watch_thread
    if not allowed(common):
        return None
    _door, _common = dict(door), common
    ctx.register_hook("pre_approval_request", _on_pre_approval)
    ctx.register_hook("post_approval_response", _on_post_approval)
    with _lock:
        if _watch_thread is None or not _watch_thread.is_alive():
            _stop.clear()
            _watch_thread = threading.Thread(target=_watch, args=(_door,), name="wf-approval-bridge", daemon=True)
            _watch_thread.start()
    return True


# ---------------------------------------------------------------- observers --

def _token_of(kw):
    pk = kw.get("pattern_key")
    if isinstance(pk, str) and pk.startswith(TOKEN_PREFIX):
        t = pk[len(TOKEN_PREFIX):]
        return t if TOKEN_RE.match(t) else None
    return None


def _on_pre_approval(**kw):
    """Observer only (the channel cannot be vetoed from here): correlate the
    request our emitter presented. Foreign/unknown tokens pass through unseen."""
    try:
        t = _token_of(kw)
        if t is None:
            return None
        with _lock:
            inst = _instances.get(t)
            if inst is not None and inst.get("state") == "issued":
                inst["state"] = "seen"
    except Exception:
        pass
    return None                              # observers never transform anything


def _on_post_approval(**kw):
    """Resolution channel: ONLY a token this process minted, still unresolved,
    may act — forged (never-minted) and duplicate responses cannot release.
    The door's already-answered refusal is the second net."""
    try:
        t = _token_of(kw)
        if t is None:
            return None
        with _lock:
            inst = _instances.get(t)
            if inst is None or inst.get("resolved"):
                return None                  # forged / foreign / duplicate
            choice = str(kw.get("choice") or "")
            inst["resolved"] = True
            inst["state"] = "resolved"
            inst["choice"] = choice
            _resolved_order.append(t)
            while len(_resolved_order) > _KEEP_RESOLVED:
                _instances.pop(_resolved_order.pop(0), None)
        if choice in _APPROVE_SHAPED and _door is not None:
            try:
                _door["act_release"]({"run_id": inst["run_id"], "gate_id": inst["gate_id"],
                                      "answer": ANSWER_APPROVE})
            except Exception:
                pass                         # honest degradation; the hold stands
    except Exception:
        pass
    return None


# ------------------------------------------------------------------ tailer --

def _watch(door):
    while not _stop.wait(TICK_S):
        try:
            _tick(door)
        except Exception:
            pass                             # silent: a bad tick loses one sweep, never a crash


def _tick(door):
    """One sweep: seed offsets for unseen runs, read appended bytes of every
    known run's events.jsonl, and bridge each fresh gate.held row."""
    try:
        root = door["runs_root"]()
        entries = sorted(p for p in root.iterdir() if p.is_dir())
    except Exception:
        return
    live = set()
    for run in entries:
        rid = run.name
        live.add(rid)
        ef = run / "events.jsonl"
        try:
            size = ef.stat().st_size
        except OSError:
            continue
        known = _offsets.get(rid)
        if known is None:                    # first sight: seed at EOF — history never re-fires
            _offsets[rid] = size
            continue
        if size <= known:
            _offsets[rid] = min(size, known)  # truncation/rotation: reseed honestly
            continue
        with open(ef, "r", encoding="utf-8", errors="replace") as f:
            f.seek(known)
            chunk = f.read()
        cut = chunk.rfind("\n")              # partial tail: consumed next tick
        if cut < 0:
            continue
        _offsets[rid] = known + len(chunk[:cut + 1].encode("utf-8", "replace"))
        line_off = known                     # per-LINE byte offset: the instance identity anchor
        for line in chunk[:cut].splitlines():
            off = line_off
            line_off += len(line.encode("utf-8", "replace")) + 1
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if isinstance(ev, dict) and ev.get("event") == "gate.held" \
                    and isinstance(ev.get("node"), str):
                _bridge(rid, run, ev, off)
    for rid in [r for r in _offsets if r not in live and _offsets.get(r) is not None]:
        _offsets.pop(rid, None)


def _bridge(rid, run, ev, line_off):
    """Mint the per-hold-instance token and present it (bounded), or degrade
    silently with a recorded state. The instance identity is the appended
    event row itself (offset + ts), so a re-hold is a fresh instance."""
    gate_id = ev["node"]
    ts = ev.get("ts")
    token = hashlib.sha256(("%s\0%s\0%s\0%s" % (rid, gate_id, line_off, ts)).encode()).hexdigest()[:16]
    with _lock:
        if token in _instances:
            return
        inflight = sum(1 for i in _instances.values()
                       if not i.get("resolved") and i.get("state") != "skipped")
        if inflight >= _MAX_INFLIGHT:
            _instances[token] = {"run_id": rid, "gate_id": gate_id, "state": "skipped", "resolved": False}
            # est-7m6wv horde: skipped rows are TERMINAL bookkeeping — enter the
            # FIFO so the bounded trim reaches them (before, they leaked forever).
            _resolved_order.append(token)
            while len(_resolved_order) > _KEEP_RESOLVED:
                _instances.pop(_resolved_order.pop(0), None)
            return
        _instances[token] = {"run_id": rid, "gate_id": gate_id, "state": "pending", "resolved": False}
    t = threading.Thread(target=_emit, args=(rid, run, gate_id, token),
                         name="wf-approval-emit-%s" % token, daemon=True)
    t.start()


def _wake_text(run):
    """The runner-authored wake sentence, verbatim, from the run's wake.jsonl
    (the bridge authors nothing; the wake row already passed the runner's own
    redaction). The gate.held template is constant, so any gate.held row of
    THIS run carries the same sentence. None = nothing presentable."""
    try:
        with open(run / "wake.jsonl", "r", encoding="utf-8", errors="replace") as f:
            text = None
            for line in f:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("event") == "gate.held" \
                        and isinstance(row.get("text"), str) and row["text"]:
                    text = row["text"]
            return text
    except OSError:
        return None


def _session_key(run):
    """Which gateway approval session to present on: the run owner's session id
    when a notifier is registered for exactly that key, else the sole registered
    session (single-seat hosts — the common shape). Never a guessed format."""
    try:
        meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
        sid = (meta.get("owner") or {}).get("session_id") if isinstance(meta.get("owner"), dict) else None
    except (OSError, ValueError):
        return None
    if not sid:
        return None
    try:
        from tools import approval as _ap
        cbs = getattr(_ap, "_gateway_notify_cbs", {}) or {}
        if sid in cbs:
            return sid
        keys = list(cbs.keys())
        return keys[0] if len(keys) == 1 else None
    except Exception:
        return None


def _emit(rid, run, gate_id, token):
    """Present ONE hold on the native channel. The hooks, not this return
    value, perform the release mapping (observer law)."""
    try:
        with _lock:
            inst = _instances.get(token)
            if inst is None:
                return
        graph = None
        try:
            graph = json.loads((run / "graph.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        gate = next((n for n in (graph or {}).get("nodes") or []
                     if isinstance(n, dict) and n.get("id") == gate_id
                     and n.get("type") == "gate"), None)
        if gate is None:
            _skip(token)
            return
        try:                                 # already answered (tool/desktop raced us)?
            if _common.gate_answer_valid(run, gate, {n["id"]: n for n in graph["nodes"] if isinstance(n, dict)}) is not None:
                _skip(token)
                return
        except Exception:
            pass
        text = _wake_text(run)
        session_key = _session_key(run)
        if text is None or session_key is None:
            _skip(token)                     # no runner-authored sentence / no reachable surface
            return
        present = _native_present or _native_present_default
        with _lock:
            inst = _instances.get(token)
            if inst is None or inst.get("state") != "pending":
                return
            inst["state"] = "issued"         # pre_approval_request flips this to 'seen'
        try:
            present(session_key, {"command": text, "description": DESCRIPTION,
                                  "pattern_key": TOKEN_PREFIX + token,
                                  "pattern_keys": [TOKEN_PREFIX + token],
                                  "allow_permanent": False, "allow_session": False})
        except Exception as e:                      # est-7m6wv: name the silent degradation once
            sys.stderr.write("WORKFLOW_APPROVAL_BRIDGE_PRESENT_FAILED %s %s\n" % (token, type(e).__name__))
            with _lock:
                inst = _instances.get(token)
                if inst is not None and not inst.get("resolved"):
                    inst["state"] = "failed"
                    # terminal row: enter the FIFO so the bounded trim reaches failures too
                    _resolved_order.append(token)
                    while len(_resolved_order) > _KEEP_RESOLVED:
                        _instances.pop(_resolved_order.pop(0), None)
    except Exception:
        pass                                 # the hold stands; tool/desktop paths untouched


def _skip(token):
    with _lock:
        inst = _instances.get(token)
        if inst is not None:
            inst["state"] = "skipped"


def _native_present_default(session_key, data):
    """The stock path: core's gateway approval wait, which fires the pre/post
    hook pair itself. None (silent) when the channel does not exist here."""
    from tools import approval as _ap
    from tools import approval_gateway_wait as _gw
    notify_cb = _ap._gateway_notify_cb(session_key)
    if notify_cb is None:
        return None
    return _gw._await_gateway_decision(session_key, notify_cb, data, surface="gateway")


def shutdown():
    """Stop the tailer (test/reload hygiene); hook registrations stay — they are
    inert observers without the emitter that mints their tokens."""
    _stop.set()
