"""#157 MACHINERY (backend half): card enforcement — the ::workflow card ships unasked.

core fires the ``transform_llm_output`` lifecycle hook once per turn BEFORE the
final assistant row is persisted (core: hermes_cli/plugins.py VALID_HOOKS;
agent/turn_finalizer.py apply_llm_output_transform — the first hook returning a
non-empty string wins and that string becomes the persisted+streamed text). This
module is the last-resort shipper: when a turn's text carries NO parseable
``::workflow{id="<run_id>"}`` directive, the cards for runs THIS session launched
and still owes (the pending ledger) are appended as bare lines, so the desktop
directive renderer (desktop/plugin.js DirectiveCard) renders even when the model
never pastes. The model's paste stays the primary path — this hook only fills silence.

Design notes:
* HOOK-LED LEDGER (card_ledger.py, ``<runs_root>/card-ledger.json``): discovery
  is event-driven, never a scan. ``post_tool_call`` records every ``workflow``
  launch (and held/terminal reports), ``pre_llm_call`` reminds the model of
  owed cards, and this shipper READS the ledger. A card counts as shipped when
  its ledger entry is dropped on CONFIRMATION (below; a failed write costs only
  a re-ship next turn, never a lost turn). Nothing enumerates run directories;
  entries left over from before a gateway restart simply ship late.
* SHIPPED MEANS SELECTED (#168 P1): core's dispatch (plugins_dispatch.invoke_hook)
  fires EVERY transform_llm_output callback and apply_llm_output_transform keeps
  the FIRST non-empty string — so a return value is a HOPE, not a shipment.
  A proposal is therefore recorded in-memory (_PENDING) and the card.echoed
  marker is written only on CONFIRMATION that the text was selected:
  (1) the returned text is touched — core truth-tests each result at selection
      time (isinstance + bool) and str-manipulates the winner, so any attribute
      access or bool coercion of our return proves delivery;
  (2) a proposal still referenced at the next hook call is NOT treated as
      shipped: the dispatch results list retains losers too (#304 peer
      review), so an unconfirmed entry is dropped and the card replays;
  (3) an optional module-level ``_witness`` callable (test seam / durable-row
      probe) vouches for the committed row directly and suppresses (1).
  An unconfirmed proposal is simply dropped — the card replays next turn
  instead of being silently lost. A second proposal for the SAME (session,
  turn) can never win (first non-empty already holds) and returns None.
* PASTE RETIREMENT (#168 P2): a bare directive seen in this session's turn text
  retires that run's owed card PER RUN (a sibling run's card is untouched),
  even when the directive arrived through a different route (model paste);
  a fenced/inline-code directive is dead text and retires nothing.
* FENCE TRAP (#168 P3): appending into a text that ends INSIDE an open ```
  fence buries the card renderer-dead while the ledger says shipped — the
  append closes the open fence first so the card always lands outside every
  fence, as the final lines of the text.
* RECOGNITION parity with the directive renderer: the exact form
  ``::workflow{id="<run_id>"}`` with run_id matching [A-Za-z0-9._-]+, OUTSIDE any
  ``` fence or `inline code` span — a code-blocked directive is dead text to the
  renderer, so it does NOT count as shipped (the paste hint says the same).
* ABANDON-SAFE (core v0.21.5): plugins_dispatch bounds this hook by
  ``plugins.hook_callback_timeout`` and, on overrun, ABANDONS the worker
  without joining it ("do not join") — the result is dropped, the thread keeps
  running, and a fresh call id may start a new worker after the suppression
  window. So two workers can race on one run's claim. Three rules hold the
  one-ship law across that: (1) a live claim in _PENDING is never replaced
  (setdefault) and a dying text only drops ITS OWN claim; (2) selection is
  proof of delivery, so a selected text ledgers its own cards even if a racing
  worker moved the claim; (3) the marker is appended BEFORE the claim is
  released, so at every instant a run is covered by the marker or the claim.
* FAIL-OPEN: every path is guarded; any exception means "ship nothing, change
  nothing". A broken ledger must never eat the user's reply.
* The unknown surface (falsy platform) is never guessed: no surface, no append.

Path resolution is NOT reimplemented: the door injects its bound ledger via
bind(); the ledger root comes from the existing runs_root resolver.
"""
import json
import logging
import os
import re
import weakref
from typing import Any, Callable, Optional

_LOG = logging.getLogger(__name__)

# Cards appended per turn. ponytail: the launch turn carries one fan-out burst
# (1-3 launches is the measured shape); 3 keeps a runaway loop honest. Upgrade
# path: raise the constant (or move it to owner settings) once bursts > 3 are
# measured — the ledger makes every later card ship on a later turn anyway.
MAX_CARDS_PER_TURN = 3

_DIRECTIVE = re.compile(r'::workflow\{id="([A-Za-z0-9._-]+)"\}')
_FENCE_MARK = ("```", "~~~")
_INLINE_CODE = re.compile(r"`[^`\n]*`")

_LEDGER: Any = None   # the door's bound card_ledger module (bind())
_CARD: Optional[Callable[[str], str]] = None   # the door's _card helper (bind()) — one card grammar, no fork
# In-memory proposal table (#168 P1): (session_id, run_id) ->
# {"turn_id": str, "ref": weakref to the proposed text}.
# Nothing leaves the ledger until a proposal is CONFIRMED selected; a
# proposal whose text died unconfirmed is dropped so the card replays.
_PENDING: dict = {}
# Paste retirement (#168 P2): (session_id, run_id) whose bare directive was
# seen in this session's turn text — delivered through the paste route, so
# the owed card retires (its ledger entry is dropped).
_RETIRED = set()
# (session_id, turn_id) -> True once this hook proposed text for that turn:
# a second proposal in the same turn (duplicate registration / in-turn retry)
# can never be selected (first non-empty wins), so it ships nothing.
_PROPOSED = {}
_witness: Optional[Callable[..., bool]] = None   # durable-row probe (test seam)


def bind(ledger, card_fn):
    """Wire the door's card ledger and card grammar into this module."""
    global _LEDGER, _CARD
    _LEDGER, _CARD = ledger, card_fn


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


def _bare_directive_ids(text):
    """Run ids whose directive appears LIVE (outside any fence / inline-code
    span) in this turn's text — the renderer will see them; fenced examples
    are dead text and never qualify."""
    return _DIRECTIVE.findall(_strip_code(text))


def _open_fence(text):
    """The fence marker (``` or ~~~) the text ENDS inside, or None. Line-wise
    toggle parity, same walk the recognition path uses."""
    open_mark = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if open_mark is None:
            if stripped.startswith(_FENCE_MARK):
                open_mark = stripped[:3]
        elif stripped.startswith(open_mark):
            open_mark = None
    return open_mark


def _session():
    return os.environ.get("HERMES_SESSION_ID", "")


def _owed(session_id):
    """Run ids this session still owes a card for, newest first — read from the
    ledger, never discovered. A pasted (retired) run or a live proposal is skipped."""
    out = []
    for rid, _ent in _LEDGER.entries(session_id):
        if (session_id, rid) in _RETIRED or (session_id, rid) in _PENDING:
            continue
        out.append(rid)
    return out


_TERMINAL = ("done", "failed", "stopped")


def _as_dict(v):
    if isinstance(v, dict):
        return v
    if isinstance(v, str):
        try:
            d = json.loads(v)
        except ValueError:
            return None
        return d if isinstance(d, dict) else None
    return None


def _post_tool_call(tool_name="", args=None, result=None, session_id="", **_):
    """post_tool_call callback: keep the ledger in step with `workflow` calls.

    Cheap guard first — this fires for EVERY tool call. Never raises, returns None."""
    try:
        if tool_name != "workflow" or _LEDGER is None:
            return None
        res = _as_dict(result)
        if not res or res.get("error"):
            return None
        rid = res.get("run_id")
        if not isinstance(rid, str) or not rid:
            return None
        sid = session_id or _session()
        if not sid:
            return None
        a = _as_dict(args) or {}
        action = a.get("action")
        status = res.get("status")
        if action == "stop" or status in _TERMINAL:
            _LEDGER.drop(sid, rid)
        elif status == "held" or res.get("held_gate"):
            _LEDGER.set_state(sid, rid, "held")
        elif action == "release":
            _LEDGER.set_state(sid, rid, "pending")
        elif action == "run":
            graph = a.get("graph") if isinstance(a.get("graph"), dict) else {}
            _LEDGER.add(sid, rid, a.get("name") or graph.get("name") or res.get("name") or "")
    except Exception as exc:
        _LOG.debug("card ledger post_tool_call skipped (fail-open): %s", exc)
    return None


def _pre_llm_call(session_id="", **_):
    """pre_llm_call callback: remind the model of owed cards, only when some exist."""
    try:
        if _LEDGER is None:
            return None
        sid = session_id or _session()
        if not sid:
            return None
        lines = []
        for rid, ent in _LEDGER.entries(sid):
            if (sid, rid) in _RETIRED:
                continue
            lines.append(f"workflow run {rid} ({ent.get('name') or 'workflow'}) finished but has "
                         f"no card in chat yet \u2014 attach its card this turn")
        if not lines:
            return None
        return {"context": "\n".join(lines[:MAX_CARDS_PER_TURN * 3])}
    except Exception as exc:
        _LOG.debug("card ledger pre_llm_call skipped (fail-open): %s", exc)
        return None


def _confirm(session_id, run_id, turn_id):
    """Drop the ledger entry for a proposal proven SELECTED, THEN release the
    in-memory claim. Order is deliberate (ABANDON-SAFE rule 3): the core may
    have abandoned a worker that is still reading the ledger concurrently;
    releasing first opens a window where neither the claim nor the entry's
    absence covers the run and that worker re-proposes it — a double-ship. A
    failed ledger write still clears the claim: a dead ledger must not suppress
    forever (re-ships next turn)."""
    key = (session_id, run_id)
    _LEDGER.drop(session_id, run_id)
    entry = _PENDING.get(key)
    if entry is not None:
        _PENDING.pop(key, None)


def _reconcile(session_id, turn_id):
    """Decide the fate of PROPOSALS FROM EARLIER TURNS at this session's next
    call. Confirmed (delivered) -> stamp card.echoed; denied -> drop the entry
    so the card replays. Reference liveness settles nothing (#304 peer
    review): the dispatch results list retains losers too, so an unconfirmed
    entry is always denied here — only the selection witness on the text (or
    a selection-proof ``_witness``) ever stamps. With ``_witness`` bound the
    probe answers instead (durable-row truth, same shape as the reconcile probe
    for #161's notice belt)."""
    for key in [k for k in _PENDING if k[0] == session_id]:
        entry = _PENDING.get(key)            # an abandoned worker may race us here
        if entry is None or entry.get("turn_id") == turn_id:
            continue                        # this turn proposed it; selection hasn't run
        rid = key[1]
        try:
            if _witness is not None:
                ok = bool(_witness(session_id=session_id,
                                   turn_id=entry.get("turn_id", ""), run_id=rid))
            else:
                # #304 peer review: reference liveness is NOT delivery. The
                # dispatch results list retains LOSING proposals until the
                # call returns, and an abandoned worker's reconcile can run
                # mid-dispatch — before winner selection. A text that never
                # witnessed selection (bool coercion or str work, below) is
                # unshipped: drop the claim so the card replays, never stamp.
                ok = False
            if ok:
                _confirm(session_id, rid, entry.get("turn_id", ""))
            else:
                _PENDING.pop(key, None)     # never selected: replayable, not lost
        except Exception as exc:
            _LOG.debug("card pending reconcile skipped for %s (fail-open): %s", rid, exc)
            _PENDING.pop(key, None)


def _drop_own(key, wr):
    """weakref callback: drop the claim only if it is still the one this text made."""
    entry = _PENDING.get(key)
    if entry is not None and entry.get("ref") is wr:
        _PENDING.pop(key, None)


class _CardText(str):
    """The augmented reply. A str in every respect, plus the #168 P1 witness:
    core selection (``isinstance(r, str) and r``) truth-tests and str-methods
    the WINNER and only the winner, so the first non-dunder attribute access
    or bool coercion of this object proves it was selected -> stamp the ledger
    then. A loser is never touched by selection; its only touches are the
    resolver's pre-selection dunders (isawaitable -> __class__/__await__),
    which confirm nothing (#304 peer review)."""

    def __new__(cls, text, entries, session_id, turn_id):
        self = str.__new__(cls, text)
        self._ce_entries = entries          # [run_id]
        self._ce_session = session_id
        self._ce_turn = turn_id
        self._ce_done = False
        return self

    def _ce_confirm(self):
        if object.__getattribute__(self, "_ce_done"):
            return
        if _witness is not None:
            return                          # the probe alone vouches (witness mode)
        entries = object.__getattribute__(self, "_ce_entries")
        sid = object.__getattribute__(self, "_ce_session")
        turn = object.__getattribute__(self, "_ce_turn")
        object.__setattr__(self, "_ce_done", True)
        # Selection IS delivery (ABANDON-SAFE rule 2): ledger our own cards from
        # what this text carries, never from _PENDING — a racing abandoned
        # worker may own the claim now, and skipping the marker would re-ship.
        for rid in entries:
            _confirm(sid, rid, turn)

    def __bool__(self):
        try:
            self._ce_confirm()
        except Exception as exc:            # fail-open: never break selection
            _LOG.debug("card confirm skipped (fail-open): %s", exc)
        return True                         # non-empty by construction

    def __getattribute__(self, name):
        # #304 peer review: stock core resolves EVERY dispatch result through
        # resolve_plugin_command_result before selection, and its first move
        # (inspect.isawaitable -> hasattr("__await__") + __class__ touches)
        # lands on losers too. Dunder access is therefore NOT delivery proof;
        # only real str work on the selected text (non-dunder attributes,
        # bool coercion) confirms. A persisted winner always passes a truth
        # check or a str operation on the way to the store/renderer.
        if (not name.startswith("_ce_")
                and not (name.startswith("__") and name.endswith("__"))):
            try:
                object.__getattribute__(self, "_ce_confirm")()
            except Exception as exc:
                _LOG.debug("card confirm skipped (fail-open): %s", exc)
        return object.__getattribute__(self, name)


def _propose(response_text, take, session_id, turn_id):
    """Build the augmented text as a _CardText and register the proposals. The
    weakref callback (not a __del__ hook) drops an unconfirmed proposal the
    moment core discards the text, keeping the card replayable."""
    text = response_text.rstrip() + "\n\n" + "\n\n".join(_CARD(rid) for rid in take)
    open_mark = _open_fence(response_text)
    if open_mark:                           # fence trap (#168 P3): never ship buried
        text = response_text.rstrip() + "\n\n" + open_mark + "\n\n" + \
            "\n\n".join(_CARD(rid) for rid in take)
    obj = _CardText(text, list(take), session_id, turn_id)
    keys = []
    for rid in take:
        key = (session_id, rid)
        # ABANDON-SAFE rule 1: never replace a live claim (an abandoned worker
        # resuming late must not evict the fresh call's), and the dying text
        # drops only the claim it owns.
        _PENDING.setdefault(key, {"turn_id": turn_id,
                                  "ref": weakref.ref(obj, lambda wr, k=key: _drop_own(k, wr))})
        keys.append(key)
    _PROPOSED[(session_id, turn_id)] = True
    if len(_PROPOSED) > 4096:
        _PROPOSED.clear()                   # a turn key is turn-scoped; a full table just re-arms
    if len(_RETIRED) > 4096:
        _RETIRED.clear()
    return obj


def _card_hook(response_text, session_id, turn_id="", model="", platform="", **_):
    """transform_llm_output callback: append outstanding cards, or return None.

    Fail-open law: any exception returns None — the user's reply is never eaten
    or blocked by this module. Nothing under .github is ever touched."""
    try:
        if _CARD is None or _LEDGER is None:
            return None                 # unbound module = door never registered: no-op
        if not isinstance(response_text, str) or not response_text:
            return None                 # no final text: nothing to attach to
        if not platform:
            return None                 # unknown surface — never guess where this renders
        if not session_id:
            return None
        # Turn ledger bookkeeping first: last turn's hopes are settled against
        # this call (#168 P1 — shipped means SELECTED, not returned).
        _reconcile(session_id, turn_id)
        ids = _bare_directive_ids(response_text)
        if ids:
            for rid in ids:             # paste route delivered: retire THAT run
                _RETIRED.add((session_id, rid))
                _PENDING.pop((session_id, rid), None)
                _LEDGER.drop(session_id, rid)
            return None                 # the model pasted (unfenced): hands off
        if _PROPOSED.get((session_id, turn_id)):
            return None                 # this turn already proposed; a duplicate
                                        # registration can never win selection
        take = _owed(session_id)[:MAX_CARDS_PER_TURN]
        if not take:
            return None                 # no proposal may carry the empty string:
                                        # core keeps non-None results and an
                                        # empty winner would hijack the reply
        return _propose(response_text, take, session_id, turn_id)
    except Exception as exc:
        _LOG.debug("card enforcement skipped (fail-open): %s", exc)
        return None
