"""#157 MACHINERY (backend half): card enforcement — the ::workflow card ships unasked.

core fires the ``transform_llm_output`` lifecycle hook once per turn BEFORE the
final assistant row is persisted (core: hermes_cli/plugins.py VALID_HOOKS;
agent/turn_finalizer.py apply_llm_output_transform — the first hook returning a
non-empty string wins and that string becomes the persisted+streamed text). This
module is the last-resort shipper: when a turn's text carries NO parseable
``::workflow{id="<run_id>"}`` directive, the cards for runs THIS session launched
inside the recency window are appended as bare lines, so the desktop directive
renderer (desktop/plugin.js DirectiveCard) renders even when the model never
pastes. The model's paste stays the primary path — this hook only fills silence.

Design notes:
* ONE-SHOT LEDGER (zero new files): a run's card counts as shipped when its
  events.jsonl carries a ``card.echoed`` marker (appended HERE, after the
  augmented text is computed — a failed write costs only a re-ship next turn,
  never a lost turn). run.json stays byte-identical.
* RECOGNITION parity with the directive renderer: the exact form
  ``::workflow{id="<run_id>"}`` with run_id matching [A-Za-z0-9._-]+, OUTSIDE any
  ``` fence or `inline code` span — a code-blocked directive is dead text to the
  renderer, so it does NOT count as shipped (the paste hint says the same).
* FAIL-OPEN: every path is guarded; any exception means "ship nothing, change
  nothing". A broken ledger must never eat the user's reply.
* The unknown surface (falsy platform) is never guessed: no surface, no append.

Path resolution is NOT reimplemented: the door injects its bound wfcommon
instance via bind() and every root comes from the existing resolvers
(runs_root / profiles_root+profile_home / launch_runs_root legacy).
"""
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Callable, Optional

_LOG = logging.getLogger(__name__)

# Cards appended per turn. ponytail: the launch turn carries one fan-out burst
# (1-3 launches is the measured shape); 3 keeps a runaway loop honest. Upgrade
# path: raise the constant (or move it to owner settings) once bursts > 3 are
# measured — the ledger makes every later card ship on a later turn anyway.
MAX_CARDS_PER_TURN = 3

DEFAULT_WINDOW_MINUTES = 30          # launched this recently = the launch turn's window
WINDOW_SETTING = "card_window_minutes"  # plugins.entries.hermes-workflows.settings.<k>
TERMINAL_STALE_MINUTES = 10          # done-and-stale runs are past the ship moment: never spam

_DIRECTIVE = re.compile(r'::workflow\{id="([A-Za-z0-9._-]+)"\}')
_FENCE_MARK = ("```", "~~~")
_INLINE_CODE = re.compile(r"`[^`\n]*`")

_COMMON: Any = None   # the door's bound wfcommon (bind())
_CARD: Optional[Callable[[str], str]] = None   # the door's _card helper (bind()) — one card grammar, no fork
_SEEN = {}            # (turn_id, run_id) -> True: in-turn retry dedupe (marker covers turns)


def bind(common, card_fn):
    """Wire the door's shared read model and card grammar into this module."""
    global _COMMON, _CARD
    _COMMON, _CARD = common, card_fn


def _strip_code(text):
    """Blank out ```/~~~ fenced blocks and `inline code` spans (line-wise), so a
    directive that only lives inside code never reads as shipped."""
    out, fence = [], None
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith(_FENCE_MARK):
                fence = stripped[:3]
                out.append("")
            else:
                out.append(_INLINE_CODE.sub("", line))
        else:
            out.append("")
            if stripped.startswith(fence):
                fence = None
    return "\n".join(out)


def _directive_present(text):
    return _DIRECTIVE.search(_strip_code(text)) is not None


def _age_minutes(ts, now):
    """Minutes before `now` of an ISO ts; None when unparseable (unreadable clock
    = not discoverable, fail-open)."""
    if not isinstance(ts, str) or not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 60.0


def _events(r):
    """events.jsonl lines as dicts; torn/unreadable lines are skipped, never fatal."""
    try:
        lines = (r / "events.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict):
            out.append(e)
    return out


def _roots():
    """Every runs root this session's launches could have landed in — the resolved
    root, EVERY profile root (a profile-scoped gateway lands runs under its own
    home), and the legacy launch root. Existing resolvers only; deduped."""
    roots = [_COMMON.runs_root(), _COMMON.launch_runs_root()]
    try:
        pr = _COMMON.profiles_root()
        if pr.is_dir():
            for child in sorted(pr.iterdir()):
                if child.is_dir():
                    # A profile-scoped gateway resolves hermes_home() to its own
                    # home, so its runs land under <profile_home>/workflows —
                    # answered by the SAME resolver, not a re-typed path law.
                    roots.append(_COMMON.effective_runs_root(
                        {"WF_RUNS_ROOT": "", "HERMES_HOME": str(child)}))
    except OSError:
        pass
    seen, out = set(), []
    for p in roots:
        key = str(p)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def _terminal_stale(r, now):
    """A run whose completion (run.done) happened more than TERMINAL_STALE_MINUTES
    ago is past the ship moment — the card belongs to the launch turn, and old
    runs must never be spammed. Completion is read from events.jsonl (the
    runner's record) or the run.done marker file's mtime."""
    done_ages = [a for e in _events(r) if e.get("event") == "run.done"
                 and (a := _age_minutes(e.get("ts"), now)) is not None]
    if done_ages:
        return min(done_ages) > TERMINAL_STALE_MINUTES
    try:
        marker = (r / "run.done")
        if marker.exists():
            age = (now.timestamp() - marker.stat().st_mtime) / 60.0
            return age > TERMINAL_STALE_MINUTES
    except OSError:
        pass
    return False


def _outstanding(session_id, now):
    """Run ids launched by this session, inside the window, card still unshipped —
    newest first (started desc)."""
    window = DEFAULT_WINDOW_MINUTES
    try:
        cfg = _COMMON.owner_setting(WINDOW_SETTING)
        if type(cfg) is int and 0 < cfg <= 24 * 60:
            window = cfg
    except Exception:
        pass
    hits = []
    for root in _roots():
        try:
            if not root.is_dir():
                continue
            entries = sorted(root.iterdir())
        except OSError:
            continue
        for r in entries:
            try:
                meta = _COMMON.jload(r / "run.json")
                if not isinstance(meta, dict):
                    continue
                owner = meta.get("owner") or {}
                if not isinstance(owner, dict) or owner.get("session_id") != session_id:
                    continue
                age = _age_minutes(meta.get("started") or meta.get("started_at"), now)
                if age is None or age < 0 or age > window:
                    continue
                if any(e.get("event") == "card.echoed" for e in _events(r)):
                    continue
                if _terminal_stale(r, now):
                    continue
                hits.append((age, r.name, r))
            except Exception:
                continue        # a torn run dir is invisible, never an exception upward
    hits.sort(key=lambda t: (t[0], t[1]))   # ascending age = newest launch first
    return [(rid, r) for _, rid, r in hits]


def _mark(r, session_id, turn_id):
    """Append the card.echoed marker. Best-effort: a failed write means the card
    ships once more next turn — never raise, never lose the text."""
    try:
        with (r / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(
                {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "event": "card.echoed",
                 "session_id": session_id, "turn_id": turn_id},
                ensure_ascii=False) + "\n")
    except Exception as exc:
        _LOG.debug("card.echoed marker failed for %s: %s", r, exc)


def _card_hook(response_text, session_id, turn_id="", model="", platform="", **_):
    """transform_llm_output callback: append outstanding cards, or return None.

    Fail-open law: any exception returns None — the user's reply is never eaten
    or blocked by this module. Nothing under .github is ever touched."""
    try:
        if _CARD is None or _COMMON is None:
            return None                 # unbound module = door never registered: no-op
        if not isinstance(response_text, str) or not response_text:
            return None                 # no final text: nothing to attach to
        if not platform:
            return None                 # unknown surface — never guess where this renders
        if not session_id:
            return None
        if _directive_present(response_text):
            return None                 # the model pasted (unfenced): hands off
        now = datetime.now(timezone.utc)
        pending, seen_rid = [], set()
        for rid, r in _outstanding(session_id, now):
            if rid in seen_rid:
                continue                # same run visible under two roots: ship once
            seen_rid.add(rid)
            if (turn_id, rid) not in _SEEN:
                pending.append((rid, r))
        if not pending:
            return None
        take = pending[:MAX_CARDS_PER_TURN]
        text = response_text.rstrip() + "\n\n" + "\n\n".join(_CARD(rid) for rid, _ in take)
        for rid, r in take:
            _SEEN[(turn_id, rid)] = True
            _mark(r, session_id, turn_id)   # append-after the found dir (never a re-resolve)
        if len(_SEEN) > 4096:
            _SEEN.clear()               # a turn key is turn-scoped; a full table just re-arms
        return text
    except Exception as exc:
        _LOG.debug("card enforcement skipped (fail-open): %s", exc)
        return None
