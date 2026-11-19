docs(efp): state the fingerprint field law in prose + name the annotate verb

bd_2026-11-13-5su (E22). Engine B died on an undocumented boundary: runtime docs
never stated the graph-amendment fingerprint rule, so "which field moves an efp"
had to be reverse-engineered from the amends.jsonl base_revision hash chain, and
the only change-the-record-keep-the-result path (patch efp-inert fields on a DONE
node) existed in code with no named door.

operations.md gains "The efp field law" section: the efp construction, where each
fingerprint lives (graph.json / node-record _def+fp_rule_version / graph_fingerprint
on runner_exit.json / amends.jsonl base_revision rows), when fp_rule_version
rotates (membership change only; v1->v2 at b79fa21, budgets excluded), and a table
listing every efp-inert field (max_turns, timeout, run_budget, shape, budget,
concurrency, item_concurrency, require_route, route_verified,
substrate_substituted, resume_hint) vs efp-moving fields, rule fp_rule_version=2.
The annotate procedure: `amend` with a node-scoped `patch` over inert fields only —
`diff` shows `changed` non-empty with `will_rerun` empty; the commit replays, the
ledger row lands, descendants keep their efp. Boundary cases pinned:
`max_api_calls`/`max_input_tokens`/node `retry` MOVE; the graph-level knob family
is launch-frozen and never reaches def_hash.

Membership table verified against wfcommon.def_hash: 11 inert fields no-op under
both add- and modify-pass, 29 moving fields all shift def_hash, a 2-node chain
keeps the descendant's efp under an inert ancestor annotate and shifts it under a
provider re-route, and rule 1 still hashes a pre-b79fa21 record. SKILL.md routes
to the section from the amend bullet.
