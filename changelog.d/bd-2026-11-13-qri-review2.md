feat(desktop): the gate answer receipt carries its WHEN (bd_2026-11-13-qri, review-2 Q1/Q2)

Review-2 reproduced the same-mount shadowing bug: after a successful
answer the local `recorded = {answer}` outranked the refetched read-model
record forever, so `answered.at` never anchored the dwell — a 5-minute
hold answered at 03:00 rendered `held 26h 33m` and kept ticking. The
receipt also never showed WHEN the answer was written, and the success
toast said `◇ Held · ...` without the answer or the time: an event
notification, not the receipt it claims to be.

- `_release_core`'s success return gains an additive `at` — the SAME
  server-stamped ISO time written into `gates/<id>.json`. Every existing
  caller reads `.get("ok")` (tool path ignores the dict on success), so
  this is a pure receipt-contract widening of the one answer path.
- `GateActions` keeps `at` in its local record and MERGES the durable
  read: once the refetched `answered` carries an answer it OUTRANKS the
  optimistic local state (durable truth wins, dwell freezes at the
  server `at`), never the other way around.
- The receipt renders `Answered · <time>` — the door-stamped time pre-
  refetch, the durable record's time after, and an honest
  `time not recorded` when a record has none (never a silent drop).
- The success toast IS the receipt:
  `◇ Answer saved · <answer> · <requester> · <run> / <gate> · <time>`
  with the unchanged `View exact gate` same-run identity action. An
  older door without `at` honestly omits the time instead of inventing
  a client clock.

The ui2-proof `gate` case now refuses the run unless the rendered
receipt carries the door-stamped `Answered` line and the toast matches
the receipt prefix — the frame is the contract, verified on the real
renderer (SETUP.md updated; tests/test_composer_owner.mjs gains the
same-mount refetch case the reviewer's reproduction demanded).

## Bench-home law (field-proven, this bead's capture attempt)

`_hermes_root_of` forces the default hermes root to the native
`~/.hermes` whenever `HERMES_HOME` lives under it, so a bench provisioned
under the native home resolves `ui2bench` at the REAL profile registry.
The app (hermes-agent >= the plugin-run-backend feature, which names the
active profile on registry API requests) then 403s
`profile_scope_mismatch` on every plugin call — the old exit-6
"row never rendered" was that auth failure wearing a UI costume.
The driver now dies at preflight (exit 4) with the law spelled out when
`--out` lands under the native home; provision at the repo's
`captured/` or a TMPDIR path and copy the finished set to the ledger.

- proof-harness: pass `HERMES_DESKTOP_HERMES` (the preflight CLI, absolute)
  to the electron boot — the app since b9b36c9 resolves its
  backend at `$HERMES_HOME/hermes-agent`, which a bench home never has, and
  otherwise halts on the bootstrap first-run setup choice (no plugin, no
  frame). SETUP.md documents the dedicated-app-copy provisioning law.

- door: bench-only proof knobs on POST /runs/{id}/gate —
  UI2_PROOF_GATE_FAIL_ONCE (first armed answer is a typed ok:false before any
  write) and UI2_PROOF_GATE_POST_DELAY_MS (sleep AFTER the durable write,
  BEFORE the response). The current desktop's plugin REST rides the
  'hermes:api' IPC bridge — no renderer network request exists to intercept —
  so the gate capture's error/pending frames are real door behavior now.
  Pinned by behavior checks in test_gate_answer_flows (33 total).
