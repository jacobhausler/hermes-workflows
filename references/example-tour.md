# Fan-out, gates, branches — the tested tour

The operating rules live in [../references/grammar.md](../references/grammar.md); this file is
the fold of AGENTS.md §3c (bead hw-73c): the snippet, the gate/fan-out laws, and what
each shipped TEMPLATE guarantees beside its author-run receipt. AGENTS.md stays under
core's 32,000-char subdirectory-hint cap so a mid-run load drops no middle.

```json
{ "id": "lanes", "type": "agent",
  "fanout": { "items": ["alpha", "beta"], "goal": "Audit {item}. Write <path>/{item}.md first.", "quorum": 1 } }

{ "id": "approve", "type": "gate", "after": ["lanes"],
  "question": "Ship the report? Answer 'ship' to publish, 'hold' to stop.", "options": ["ship", "hold"] }

{ "id": "go",   "type": "gate", "after": ["judge"], "when": "out.judge.verdict == 'ship'", "on_skip": "prune" }
{ "id": "hold", "type": "gate", "after": ["judge"], "when": "out.judge.verdict != 'ship'", "on_skip": "prune" }
```

A human gate holds until `release`; the desktop view shows the question and hands
the answer back to the owning session. `hold_timeout` + `default_option` makes a
decorative gate release itself (`gate.auto_released`); `hold_timeout` alone logs
`gate.expired` once and keeps holding. Fan-out `quorum` (optional) races: once N
succeed, the rest are cancelled; without it the fan-out waits for every item;
`goal` is optional when items carry their own. Machine gates: `wait:{"wait_s":N}` or
`wait:{"until_argv":[…],"every_s":60,"timeout_s":3600}`. Tested examples:
[examples/basics/approve-publish.json](../examples/basics/approve-publish.json),
[examples/basics/branch-on-verdict.json](../examples/basics/branch-on-verdict.json).
[examples/release/gated-publish.workflow.json](../examples/release/gated-publish.workflow.json) is a
human-gated publish TEMPLATE built from the approve-publish seed (draft -> owner
gate -> complementary `when`+`on_skip:"prune"` pair on the answer -> exactly one
arm; no node names a vendor model — role vocabulary lives in prose, routing is the
seat default). Launch seeds `run_context:{"artifact":"<name>"}`. Validate + author
run tested (receipts/gated-publish/).
[examples/release/machine-watch.workflow.json](../examples/release/machine-watch.workflow.json) is a
scheduled-watcher TEMPLATE (zero-token machine-gate poll, releases on exit 0;
launch with `lane_key` so cron double-fire dedupes; timeout fails loudly for
the next deduped dispatch). Validate + smoke-run tested.
[examples/ops/incident-response.json](../examples/ops/incident-response.json) is a full
lifecycle TEMPLATE (alert-triggered incident: verdict-branch gate pair, machine
recovery probe with human escalation, merge-gated close) meant to be adapted —
its `run_context` seeds and the sweep-adapter contract are the swap points; it
validates but is not smoke-run (real lanes need your stack).
[examples/review/blind-council.workflow.json](../examples/review/blind-council.workflow.json) is
a review-council TEMPLATE (blind independent seats -> synthesis with mandatory
verify-list). Its seats pin CAPABILITY CLASSES (`council_a`, `council_b`) bound
through `settings.models` — no vendor model id appears in the file; an unbound
class fails the launch closed. Author-run receipt:
[receipts/blind-council/author-run.json](../receipts/blind-council/author-run.json).
[examples/build/triage-route.workflow.json](../examples/build/triage-route.workflow.json) is a
queue-triage TEMPLATE (intake -> classifier -> complementary `when` +
`on_skip: prune` carried by the arm heads themselves: human escalation gate with
the answer consumed as data, or a rule-driven batch fan-out). The classifier emits
a `has_urgent` boolean because the when grammar cannot see array length; each arm
head hangs on the classifier and carries its own predicate (prune law: a cascade
skip needs ALL `after` deps skipped, so only what hangs BEHIND a dead head
cascade-prunes — the head's own `when` decides its fate); the fan-out head is an
arm-scoped `batch-prep` forwarding the routine set, not the classifier itself.
Author-run receipt:
[receipts/triage-route/author-run.json](../receipts/triage-route/author-run.json).
[examples/build/quorum-probe.workflow.json](../examples/build/quorum-probe.workflow.json) folds
the speed/coverage contrast into one file: a `quorum`-raced probe fan-out whose
report must state the cancelled straggler set honestly, beside a no-quorum barrier
that reconciles survivors against an explicit master catalog so a dead lane prints
as a loud coverage gap, never silent loss. The two fan-outs are sibling nodes with no
branch gates, so every author/peer lap walks both folded modes in a single launch;
laps exist per-engine-side, not per-mode.
[examples/build/bulk-transform.workflow.json](../examples/build/bulk-transform.workflow.json) is a barrier-fan-out TEMPLATE (declared manifest -> per-file transform lanes -> audit that reconciles all_results against the manifest via an ancestor `inputs:` ref and re-checks the filesystem itself; evidence-without-command is a failed lane). Smoke-run on the author's deployment: [receipts/bulk-transform/author-run.json](../receipts/bulk-transform/author-run.json).
[examples/build/census-fanout.workflow.json](../examples/build/census-fanout.workflow.json) is a
census TEMPLATE (fan-out auditing N generic machine items with a DETERMINISTIC
TALLY): an echo roster node carries the master item list, a no-quorum barrier
audits every item against `{item, observed, ok}`, and the tally synth READS
`audit.all_results` against the roster — every item answered or NAMED missing,
counts computed from the record, never prose. One item (battery-gauge) is a
designed dead gauge so the tally's loud-row law is exercised on every run; the
report node consumes the tally via `after_partial`. Two author laps — honest
(dead gauge as a loud red row) and severed (a child cut from the record becomes
a NAMED missing row): [receipts/census-fanout/author-run.json](../receipts/census-fanout/author-run.json).
[examples/review/escalation-ladder.workflow.json](../examples/review/escalation-ladder.workflow.json) is a verify-then-branch TEMPLATE (builder -> fresh independent verifier -> when-pair carried by the two human arm gates themselves: verified lands behind the land gate, failed escalates to a human hold with the whole packet; core has NO loop idiom - retry ownership is spelled out, not implied). Both arms smoke-run: [receipts/escalation-ladder/author-run.json](../receipts/escalation-ladder/author-run.json).
[examples/basics/exchange-run.workflow.json](../examples/basics/exchange-run.workflow.json) is the
byte-portability TEACHING PAIR — the file itself is the artifact that travels the
save → library → re-run loop (the loop's verbs, told in the description; the proof
laps live in the author receipt, never in node prose). An echo commits the token at
zero tokens, a courier copies it as pure data from its declared input, and the leaf
proves the hand-off only by re-reading both committed records from its `## Inputs` —
never from chat memory. No node names a model; children ride seat defaults.
Author-run receipt: [receipts/exchange-run/author-run.json](../receipts/exchange-run/author-run.json).

Library templates: `workflow {"action":"library","name":"<name>"}` or
`/wf show <name>` lists required `{run.KEY}` inputs and an instantiate command.
Supply explicit nonempty string values with `run from:<name>`; the door binds
all shared text fields and refuses any surviving ref before writing or spawning.
Optional `save params:{KEY:{desc,default}}` describes those refs in `meta.params`;
missing/dead declarations on an envelope save warn (non-fatal `s12`; bare saves
derive the contract from refs and never warn s12), omission retains prior params,
and `{}` clears them. Defaults are suggestions, never automatic launch inputs.
Inline unbound machine argv remains refused; ordinary inline text keeps its
existing verbatim leniency.

## Moved from AGENTS.md §3c (verbatim fold)

## The 1.0.1 settings variant (folded from AGENTS.md §3b)

Or, the 1.0.1 way — settings once, nodes carry only their work:

```json
{ "name": "check",
  "defaults": { "model": "<model-id>", "provider": "<provider-name>", "reasoning": "medium",
                "schema": { "type": "object", "required": ["ok"] } },
  "nodes": [
    { "id": "inspect", "type": "agent", "shape": "recon", "goal": "Inspect <target>." },
    { "id": "verdict", "type": "agent", "after": ["inspect"], "goal": "Judge the inspection." }
  ] }
```

## 5. Where things live at runtime

| What | Where |
|---|---|
| Run directories | `<runs_root>/<run_id>/` (`$WF_RUNS_ROOT`, else `<resolved home>/workflows` — core's `get_hermes_home()`, which on a profile-scoped host is the profile's home, not the launch-root `$HERMES_HOME`) — `graph.json`, `run.json`, `events.jsonl`, `nodes/<id>.json`, `logs/<id>.a<n>.log`, `steer/`, `gates/` |
| Library | `<runs_root>/library/` |
| Child turn report | `HERMES_QUIET_TURN_REPORT_FILE` (per spawn, read then unlinked) |
| Tier stamp | `<run>/turn_report.tier` (`typed` / `untyped`, write-once) |
| Dashboard API | `/api/plugins/hermes-workflows/runs`, `/runs/{id}`, `POST /runs/{id}/gate` |
| Desktop plugin | `~/.hermes/desktop-plugins/hermes-workflows/plugin.js` on the **app** machine |
