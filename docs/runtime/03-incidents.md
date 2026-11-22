# Incidents: dead lanes, walls, quarantine, recovery

Lane died? One command and one record answer it: `workflow {action:"status",
run_id:"<run>"}` → `failed_nodes[]` rows `{id, error, error_class}`, and the
committed record `nodes/<id>.json` → `node_facts` (`error_class`, `final`,
`log_path`, attempts) — a wall death rides the same record as `wall_account`
(§"How a wall death is accounted"). Full recovery readout — what is durable,
what is torn, what re-drive is safe: `wf.py recover <run_id>` →
`{applied, torn, unprovable, safe_redrive}` (§"Post-kill recovery"). The
details below.

## How a wall death is accounted (E24, merged #687)

A `timeout` death never shows you a wall you didn't write. One account is
built per spawn in `run_child` and rides the death record as the structured
`wall_account` field; its prose twin (`_wall_truth_phrase`) is inlined into
the record's `error` text, so the same account surfaces in `status`
`failed_nodes[].error` and in `nodes/<id>.json`.

```
wall_account = {
  "declared_s":     author's node timeout (or the run default),
  "baked_s":        the wall this spawn ACTUALLY got at bake — after
                    resume/park clamps; null = uncapped,
  "clamp_reasons":  ["resume_wall" | "park_cap" | ...],
  "grants":         [{"extra_s": int, "basis": "log" | "session" | "adopted"}],
  "effective_s":    the wall the kill happened at
}
```

Reading it: `declared_s != effective_s` is always explained in the account —
each entry in `clamp_reasons` narrowed the wall at bake, each `grants` entry
extended it mid-flight (a `node.extended` event at 50 % is the visible twin of
a log-basis grant). The prose reads like
`timeout after 2250s (declared 1500s, clamped at bake to 1400s (resume_wall), +850s extension grant (basis log), died at effective 2250s)`.
The adopted-orphan path stamps the same shape (`_adopt_acct`) so a death the
runner inherited is accounted like one it watched. The wall kill banks the
corpse first (`nodes/<id>[.<i>].corpus/`, death-table row `timeout`); a
harvested answer before the kill lands `partial` with the same account.
`wall_account` is per-death record bytes — durable evidence, recomputable from
the named fields, never a live guess.

## Where quarantine rows are written (E17; durable rows ship in #691, open)

The #61 quarantine law: attempt N+1 never shares a worktree with live
descendants of any prior generation; the kill is proven, then RECORDED at the
quarantine instant.

- Durable layout: `runs/<run>/quarantine/<node>[.<index>].jsonl` — one row
  per quarantine event on that (node, item):
  `{ts, node, index, stage, pids, proof}` with
  `stage ∈ {<ev>.tree_kill, <ev>.respawn_reap, <ev>.unprovable,
  <ev>.left_live}` and `proof ∈ {dead, unknown, stuck, unreadable}`.
  A ledger-write failure suppresses the ledger line, never the verdict
  (observer law).
- Every finalized fan item record stamps `quarantine: {rows_path, rows}` —
  `rows_path` is run-dir relative and the file EXISTS whenever that item was
  quarantined — plus `receipt_vs_parent: {claim_status, output_matches,
  problem, at}` at aggregate certification: the item's receipt adjudicated
  against the parent aggregate claim.
- The event twins (`*.tree_kill`, `*.respawn_reap`) ride `events.jsonl` even
  before the durable file (merged trunk), so tail the log or read the file —
  both name pids, proof, and the verified-empty `prior_alive: []` slate the
  next attempt started from.
- A fail-closed quarantine commits `left_live_descendants` (or an unreadable
  /proc types its own honest record): death could not be PROVEN, so no
  re-spawn into a contaminated tree — never a silent pass.

### Three quarantines, one word

- **Tree quarantine** — this section: process-tree kill evidence under
  `runs/<run>/quarantine/`.
- **Library quarantine** — a shelf entry that fails structural validation is
  a typed `quarantined` row in the `library` readout (name + typed reason,
  never replays from discovery); it is a read-side verdict, not a directory.
- **Study quarantine** — `workflow submit` parks a hand-rolled graph as
  `runs_root()/inbox/<ts-slug>.json` (`{submitted_at, submitted_by,
  why_not_library, lane, graph}`); `inbox kind=submissions` lists them
  newest-first. Promotion is the quartermaster's human-gated loop.

## Post-kill recovery: `wf.py recover <run_id>` (E16; ships in #691, open)

One JSON line answering "what effects are durable, which record is torn, what
re-drive is idempotent", computed from `side_effects.jsonl` + node records +
`graph.json` alone — never memory:

```
{ "applied":      [journal rows valid under the current graph],
  "torn":         [physical lines that never fully landed — UNPROVEN, not
                   absent, named by line/bytes/head],
  "unprovable":   [parsed rows orphaned by node-gone / amended-efp / non-row],
  "safe_redrive": [unfinished nodes in after-edge topological order, each with
                   a reconcile|fresh mode against the durable effects] }
```

Companion facts for the same incident: silent death is loud — a respawn over a
runner that died without a verdict writes `runner.reaped` + per-live-child
`node.interrupted` rows to `events.jsonl` BEFORE the replacement spawns; the
recovery ledger's reset-per-generation law is in `docs/orphan-held.md`.
Amendment application at the boundary writes
`nodes/<name>/amendment-applied.json` + `logs/boundary.log` — see
[04-amendments.md](04-amendments.md).

## Citations

- `wf.py` — section "E24 (bd_2026-11-13-42t): wall truth" (`NAMED DATA SHAPES`
  comment, `_wall_truth_phrase`); the timeout branch of `run_child`
  (`"wall_account": _wall_acct` on both the harvested-partial and the failed
  return); the adopt path (`_adopt_acct`).
- `references/death-table.md` — rows `timeout` (banked corpus) and
  `left_live_descendants`.
- `wf.py` — `_isolate_prior` (quarantine inside the ladders) and
  `_final_quiesce` (quarantine at the commit edge); the E17 block
  "the fan item-level ledger" (`_quarantine_file`, `_quarantine_row`,
  `commit_item_record`), ships in #691.
- `__init__.py` — `_library_rows` (typed `quarantined` rows), `act_submit`
  (`_submit_dir`, `O_EXCL` create, dedupe-before-write), `act_inbox`.
- `wf.py` — `recovery_state` and the `wf.py recover <run_id>` CLI leg (E16),
  plus the module-head layout line for `side_effects.jsonl`, ships in #691.
