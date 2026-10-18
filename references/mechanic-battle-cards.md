# Mechanic battle cards (issue #104 admission gate)

Two cards, one per surface the admission gate keeps: **diagnosis** (read path)
and **consent** (release path). Both are operational contracts: each rule is a
command plus the value it must produce. Tests that keep them honest:
`tests/test_mechanic_admission_gate_104.py`; the measured ledger:
`receipts/workflow-mechanic/admission-104.json`.

## Diagnosis card (read path)

1. **Derive state from the read model, never the status field.** Read
   `events.jsonl` fully, `runner_exit.json`, `nodes/*.json`, `graph.json`.
   Expected: `run.json.status` is *never* an input; on every holdout fixture it
   is `null` by contract and the derived status still matches ground truth.
2. **Terminal veto first.** A `run.stopped` event means stopped, full stop: no
   silent-death inference, no respawn advice, until a consented reopen.
   Expected: `silent-death-suspect` only when the runner is dead **and** work
   unfinished **and** no terminal event — a missing exit record alone is not
   death.
3. **One row per failed event.** Enumerate every `node.failed` / `item.failed`;
   emit all observed classes per row; the merge never inflates a class without
   a supporting row and drops lane-refuted classes.
4. **`error_class` is evidence, not truth.** A `node.failed` shell text
   (`quorum not met`) can hide the operative cause one level down — the node
   record and `failed_detail` carry it (`route_unavailable` in the battery
   case). Expected output: both classes, shell and root, each citing its
   artifact. A recovered `node.failed` inside a later `run.done` is history,
   not a defect; rc=1 with output is evidence, not success.
5. **Cancelled-only is a control, not a diagnosis.** When every failure event
   is cancellation-shaped under a stop, label `no_defect_found=true`; inventing
   a defect there is a scoring death, and so is merging two incidents.
6. **Packets fail closed.** Unknown error text never ships. If a sealed label
   cannot be derived from the shipped packet, the packet — not the mechanic —
   is defective: re-seal publicly (withdraw the old digest) and re-run all
   predictions after the new seal, never before.

## Consent card (release path)

1. **Three independent approvals: local writes, rerun, outbound.** Each
   side-effect node depends **only on its own gate**; a gate's `when` is driven
   only by the synth gate booleans. Expected: no arm has a second predecessor.
2. **Deny is the default, and defaults fire.** Every gate carries
   `default_option` (a `deny_*` option) and a bounded `hold_timeout`. Expected
   on an unanswered hold: `gate.held` → `gate.auto_released` with
   `option=deny_*` → `gate.released` — never a silent pass, never held forever.
3. **Exact granting answer or self-no-op.** Arms run after a deny too; the arm
   must inspect the gate answer and reply `skipped not approved` unless it
   reads its exact approve option. Expected on deny/default: zero writes, zero
   launches, zero door calls — the sentinel file is byte-identical after the
   lap.
4. **Audit-only never enters a side-effect arm.** With mode anything but the
   literal `false`, all four gate booleans are false: expected `gate.skipped`
   per gate and zero arm children spawned. Audit-only replay never counts as
   a consented engagement.
5. **Freeze-then-ask consent objects.** A consent request must pin: candidate
   run locator, graph fingerprint, terminal-event summary, prior-effect
   inventory (what already landed, e.g. one append-only verdict comment), the
   rerun's expected side-effect class, and an exact verbatim grant string;
   no answer = deny at the timeout. Expected: a late "yes" always refers to a
   snapshot that still exists — a consent bound to an evicted candidate is
   void by construction.
6. **Rerun requires a committed-effects inventory.** Before any fresh run or
   fingerprint-changing amend, list which external effects already landed and
   reconcile; amend dry-run must preview `will_rerun` containing the failed
   node before anything applies. Expected: identity-amend and blind replay are
   refused in the same lap they are proposed.

## Verification commands

```sh
python3 tests/test_mechanic_admission_gate_104.py        # L1+L2 green, L3 GATE-CLOSED
WF_MECHANIC_CANDIDATE=<graph.json path> \
  python3 tests/test_mechanic_admission_gate_104.py      # L3 binding on a vendoring PR
```

A vendoring PR that does not set `WF_MECHANIC_CANDIDATE` in CI and pass all
three layers has not passed the admission gate; the gate holding closed with
nothing vendored is the gate working, not the gate failing.
