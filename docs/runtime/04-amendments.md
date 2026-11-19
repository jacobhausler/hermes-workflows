# Amendment evidence: admission ledger and application proof

Two artifacts, two moments. Admission is the door's; application is the
runner's. Which definition fields move a fingerprint at all is the efp field
law — stated in prose in `references/operations.md` ("The efp field law: which
fields move a fingerprint") and its annotate verb; deliberately not restated
here.

## Admission: `amends.jsonl`

Every admitted amendment — whole-graph `amend` or a `patch:` edit — appends
one row to `runs/<run>/amends.jsonl`: the resolved whole graph, old and new.
The row's PHYSICAL LINE ORDINAL (1-based) IS the amendment revision — the same
identity as the door's `graph_revision` CAS token, so "revision 3" means the
same thing in the ledger and in a stale-token refusal. Admission never
interrupts a live wave: the runner consumes `restart.request` and reloads at
the next wave boundary. `diff` (or `dry_run:true`) is the confirm surface —
same door, writes nothing, returns the preview plus a unified `graph_diff`.

## Application: the promised paths (E18; ships in #691, open, layout final)

The doc map promised, and the runner now ships, application evidence AT
APPLICATION TIME — at boot (an amendment applied while the runner was down)
and at the wave boundary (restart.request consumed). Both artifacts are keyed
by the amends revision:

- `runs/<run>/nodes/<node>/amendment-applied.json` — the latest application
  for each node the amendment moved:
  `{node, from_efp (null on an honest add), to_efp, amendment_rev,
  trigger: "boot" | "wave-boundary", applied_at}`.
- `runs/<run>/logs/boundary.log` — one JSON line per revision:
  `{ts, event: "amendment.applied", rev, trigger, added: [ids],
  removed: [ids], changed: [{id, from_efp, to_efp}], unchanged: [ids]}`.
  An unparseable amends line gets one
  `{event: "amendment.row_torn", rev}` line instead of silence.

Together, the amends row, the named efp movement, and the
`graph.amended` / `graph.reloaded` event pair in `events.jsonl` ARE the proof:
`to_efp` equals the efp recomputed from `graph.json`, so "the amendment was
applied" is checkable from the journal, not remembered.

Laws that keep the evidence honest:

- Idempotent per revision — a revision already named in `boundary.log` writes
  nothing, so re-boots and re-reloads never duplicate the evidence.
- Fail-open (observer law) — an evidence bug can suppress evidence, never an
  application; the graph reload itself stands, and the failure prints loudly
  on stderr.

Launch-frozen knobs are not amendment content: a run whose launch baked
concurrency/retry/seat values answers `knobs_frozen` on amend — the graph may
ask, the run does not move (`references/operations.md`).

## Citations

- `wf.py` — section "E18 (bd_2026-11-13-4hc): amendment application evidence"
  (`_amend_revision_rows`, `_evidenced_amend_revs`, `_evidence_amendments`);
  ships in #691.
- `__init__.py` — `act_amend` (amends.jsonl append, `_graph_revision` seq,
  `graph_revision_stale` refusal shape, `knobs_frozen`), `act_diff`.
- `references/operations.md` — the efp field law in prose (fp_rule_version 2)
  and the annotate verb (PR #685); the `knobs_frozen` amend answer.
- `tests/test_amendment_evidence_e18.py` — the shipped paths pinned end-to-end
  (per-node movement, boundary rows, late/boot-trigger application, row_torn).
