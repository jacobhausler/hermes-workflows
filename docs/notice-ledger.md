# Notice ledger — the funnel's durable facts (est-mnd, E10/E11/E13)

Law in one sentence: an OWNER NOTICE must carry a delta of state over the last
delivered one. A transition with no delta costs an audit row in `wake.jsonl`,
never an owner turn. The settled-instance dedupe (B3 law) stays the first net
(a redrive of one delivered instance writes zero rows); the funnel is the net
for the SAME state reached over a DIFFERENT instance (a new call-site reason
string, a bumped crash generation, a re-observed commit at a wave boundary).

Every file below lives in the run dir, is written tmp+`os.replace` atomic, and
fail-OPEN on read: a store that cannot be read passes the transition through
— the funnel never eats a transition it cannot adjudicate.

## Named data shapes

`StateIdentity` — `sha256(json([skey, efp, attempts, rev]))[:16]`. The committed
record's `attempts` int is the size of the 0..N-1 attempt ladder, so the count
IS the attempts-set; `rev` is the durable amendment generation (the #610
amend-re-arm law: a re-notice after a genuine amendment is new state, while
the same generation under a different reason string is the zero-info re-notice
the funnel cuts). Computed by `_notice_state_identity` from the key payload
when present, else from the efp-valid committed record — the same facts
wake-observe/v2 already exposes, never a fresh guess.

`FailedSetBaseline` — `notices/failed_set.json`:

```json
{"state": {"ids": ["<sorted committed failed node ids>"],
           "efps": {"<id>": "<record efp or null>"},
           "rev": <int amendment generation>, "crash_gen": <int|str|null>},
 "at": "<iso now()>"}
```

The per-node efp is part of the state: a re-failure after an amend is a NEW
failure of a DIFFERENT node (its definition moved) — the FAILED->DONE->FAILED
wake-matrix law stays whole under the delta law. The amendment `rev` is part
of the state for the same reason: an amend RE-DECIDES the run (B3 law — a
reverted definition still lives at a rev the first notice never saw), so a
rev bump re-arms the delta. A later crash generation (`crash:gN`) likewise
re-arms: a new runner-process death is new state even at an unchanged failed
set (the wake-matrix catchable-crash pin). The baseline moves only when a
delivery SETTLES (delivered true or nowhere-ever null); a try-later False
leaves it stale so the retry re-notices.

`StateIdentityLedger` — `notices/state_seen.json`:
`{"ids": ["<hashes>", newest first, capped at NOTICE_SEEN_CAP=200]}`. A
`node.action_required` over an already-seen identity is suppressed
(`suppressed=state_identity_delivered`).

`CascadeRecord` — `notices/cascade.json`, keyed by root node id:

```json
{"<root id>": {"root": "<id>", "error_class": "<str|null>",
               "first_at": <epoch>, "members": ["<folded ids>"],
               "notified": <bool>, "key": "<wake key>"}}
```

The cascade LEAD is noticed IMMEDIATELY when its commit is observed (the 610
actionable-transition law: a committed failure wakes the owner while
independent siblings still run) and opens the record marked notified; a
delivery miss REOPENS it, and the next boundary drain (wave boundary,
terminal flush, runner boot — the same boundary law as the trailing
re-checks) re-notifies it once, naming the root AND the members folded so far
(`cascade_root`, `cascade_members`, `cascade_member_ids` pointer fields).
Folded members never fire their own notice: one audit row names the root.
Fold order: a causal `after`-ancestor with a committed failed record wins over
the same-error-class window (CASCADE_COALESCE_S = 120 s, the measured fan:
9 notices over 74 s). Redrives of an already-accounted commit are silent.

`NoticeDropRow` / drop store — `notice_drop.json`:
`{"rows": [{"event": ..., "class": ..., "at": ..., "tid": ...}, ...]}` (last
200). One row per delivery miss. `class` is the typed wake-row `error_class`
closed set: `missing_endpoint | http_status | redirect | timeout | transport |
native_retry | native_<outcome> | notify_prep` (`_wake_deliver` classes every
miss; `_notice_class_of_error` derives the class for any pre-typing row).
Every miss ALSO writes an `events.jsonl` `notice.drop` line and a field-loud
stdout line `WORKFLOW_NOTICE_DROP <run> <event> <class>`, and the finalize
line carries the LAST recorded class next to the verdict:
`WORKFLOW_DONE <run> notice_drop=<class>` (E11: a run that could not tell its
owner never looks silently done from outside).

`NoticeRouteStamp` — `notice_route.json`:
`{"reachable": <bool>, "error_class": <str|null>, "at": "<iso>"}` — written ONCE
at runner admission, before anything spawns (E11: the accepted run states its
drop risk). When unreachable, the boot also shouts
`WORKFLOW_NOTICE_ROUTE <run> drop_risk=<class> ...` on stdout. A
platform-native lane (non-local platform) has no legacy endpoint to probe and
stamps reachable; a local lane is reachable iff the native adapter file or a
resolvable api_server endpoint exists.

## Suppression audit rows

Every funnel suppression appends ONE row to `wake.jsonl`:

```json
{"ts": ..., "event": "<event>", "run_id": ...,
 "funnel": "suppressed", "suppressed": "<reason>", "delivered": false,
 "skey": ..., "rev": ..., "attempts": ...}
```

Reasons: `failed_set_unchanged`, `state_identity_delivered`,
`cascade_of=<root id>`. The row is the receipt of a decision — the difference
between a suppression and a hole — and the run also prints
`WORKFLOW_WAKE_SUPPRESSED <run> <event> <reason>`.

## Gate-hold payload (E13)

A `gate.held` notice renders, in the inert JSON-quoted pointer position
(before the em-dash separator, AUTHORITY LAW r5 intact — the call site passes
no text and a graph string can only speak from inside its quotes, the #501
precedent extended by the E13 owner ruling):

* `gate_id` — the holding gate;
* `gate_hold_diff` — diff-FIRST verdict over question/options/context
  (`new_hold` on first hold; else per-field `unchanged|added|removed|changed`
  against the previous non-suppressed gate.held ledger row's 12-char digests);
* `gate_hold_timeout_s` — the declared hold timeout, when the gate has one;
* `gate_hold_dwell_s` — age since the hold marker's `since`
  (`gates/<id>.held.json`), else since the previous hold notice;
* `gate_question` / `gate_options` / `gate_context` — the rendered question,
  read AT THE NOTIFY POINT from the run's COMMITTED `graph.json` (never a
  call-site string), clamped at GATE_HOLD_TEXT_CLAMP=2000 chars — the full
  text always stays in `status`/`events.jsonl`.

The ledger row itself carries `gate` and `gate_fields` (the digests) so the
diff verdict is durable and the re-fire adjudication never re-reads the wire.
