# Admission gates — zero-turn answers to human gates

Answering a human gate normally costs two agent turns: one to present the question, one after your
reply to release it. With `admission_gates` on, a **human-typed** plain answer releases the gate
without touching a model.

## Scope law: human-typed answers only

The handler is registered on core's `post_gateway_admission` hook (verified at hermes-agent
`origin/main` 20c9da14eb). That hook fires from `gateway/run_inbound_consumer.py::run_post_admission_hook`,
called at `gateway/run_inbound.py:1363` under `if not is_internal:` — non-internal messages only.
Gateway wakes never reach it: push platforms admit a synthetic `MessageEvent(internal=True)`, and
api_server sessions get `gateway/wake.py` self-POSTing `/v1/chat/completions`, which runs the turn
directly. So the handler only sees text a human typed, and cannot impersonate a wake.
**Wake-delivered text is out of scope, by the core's contract.**

Return contract (same file): `{"action": "handled", "reply": "..."}` skips the agent turn; anything
else — `None`, another shape, an exception, a timeout — is fail-open and the ordinary turn runs.

## Settings (`plugins.entries.hermes-workflows.settings`)

| key | default | effect |
|---|---|---|
| `admission_gates` | `false` | index open gates; enable the admission handler and `/wf gates` |
| `dispatch_witness` | `false` | `pre_gateway_dispatch` observer appends `<runs_root>/dispatch-witness.jsonl` (rotates at 2 MB to `.1`) |

Both are read at call time (no restart). Off means no index reads or writes and no behavior change.

## What matches

The handler acts only when ALL hold; otherwise it returns `None` and your message runs as an
ordinary turn:

1. `admission_gates` is true.
2. Your session (routing key) has open gates in `<runs_root>/gate-index.jsonl`, and the run's own
   read model still shows each one held (stale rows are closed, never trusted).
3. Either the exact form `wf release <run> <gate> <answer...>` for one of YOUR open gates (works with
   any number of open gates), or — only when you have **exactly one** open gate — the bare text equals
   one of its options (case-insensitive, trimmed) or is its 1-based number.

Ambiguity (two or more open gates, unknown option, release refused) always falls through to the
ordinary turn. On a match the gate is released through the same route as `workflow release` and the
reply reads `Workflow "<run>": gate "<gate>" released with "<answer>" (zero-turn admission path).`

`/wf gates` lists the open gates for the invoking session so you can see what a bare answer would hit.

## The index

Rows are appended when `status`/`wait` returns a held gate to the run's owning session, and closed on
release and on `stop`. Duplicate opens are deduped; the file is compacted to the open set past 500 rows.
Index operations are best-effort and never raise.

## The witness

`dispatch-witness.jsonl` rows: `{ts, platform, chat_id, user_id, message_id, internal, text_len,
decision_allowed, decision_skipped_reason}`. `decision_allowed` is `null` by design: core runs all
`pre_gateway_dispatch` callbacks and does not hand earlier verdicts to later ones, so an observer
cannot see the final decision. A row with no downstream turn is a dropped inbound — typed, not forensic.
Message text is never recorded, only its length.
