# wake-evidence-nyf — owner-bound production wake receipt fixtures (bd_2026-11-13-nyf)

Why this directory exists: the ui2 synthesis (FINAL.md:271) had to report
`wake.gate_held owner turn + wake.jsonl pointers = absent` because the isolated
lookbook seed carried NO owner stamp — and manufacturing a wake on an owner-null
seed would launder an evidence hole into a "proof". These fixtures supply the
missing production wake evidence on NATIVE isolated gateway/runner state: no
desktop, no live personal chat, no scheduler or wake-default changes.

Layout:

- `seeds/held/` — gate.held receipt input: owner stamp, committed gate defs
  (g1 full tier with hold_timeout, g2 `wake_tier: silent` = the DND probe),
  a pinned hold-marker clock offset, and the amend/re-fire question.
- `seeds/failed_delta/` — run.failed receipt input: an efp-valid committed-failure
  record body + a pinned FailedSetBaseline, so the notice must render the
  NEWLY-FAILED set and the funnel must cut an unchanged-set re-notice.
- `seeds/cascade/` — node.action_required receipt input: root leads, child
  causal-folds, ONE notice names root + members; the fold is an audit row.
- `seeds-owner-null/held/` — the REJECTION twin: `owner: null`. The validator
  refuses it before transport, and `wf.notify()` on it writes NOTHING.

Run (deterministic, stdlib, serial):

```sh
python3 tests/test_wake_evidence_nyf.py
# or directly, with a fresh PROOF_DIR:
python3 scripts/wake_evidence.py validate --seeds tests/wake-evidence-nyf/seeds \
  --out "$PROOF_DIR" --owner-null-seed tests/wake-evidence-nyf/seeds-owner-null/held
```

The validator exits 0 only when every law line PASSes: pointer->source-event
links (gate subject + 12-hex field digests, failed_delta/failed_set/run_dir/
failed_node_logs, cascade trio + member ids, transition identity), tri-state
delivery (delivered true/false/null always typed — distinct from any unresolved
action), DND suppression recorded-once-and-never-erased, and the nowhere-ever
miss loud in `notice_drop.json`. Harvested receipts land under
`$PROOF_DIR/receipts/`; the isolated sink's captured POSTs (session header +
Idempotency-Key + runner-authored body) are the delivery evidence.

PENDING (kept separate, not manufactured here): desktop capture
(`capture.mjs --case owner-wake` on the real app surface) and the actual
rendered owner turn. The old phase-L failure remains historical.
