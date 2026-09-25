# Catalog PR: add `hermes-workflows` (community, automation)

## What it is

`workflow` tool for Hermes Agent: the spawning agent owns a JSON graph of agent
nodes and human gates; a background runner executes it with replay-skip resume,
fan-outs with quorum, per-node retries with backoff, and effective-fingerprint
staleness. Ships a desktop DAG view, an inline `::workflow{id}` transcript card,
and the authoring skill (SKILL.md + references/). Submitted by the repo owner
(jacobhausler), per admission rule 5.

## Features

- `workflow` tool: agent-owned DAG of agent nodes, fan-outs, human gates, quorum
  partial credit, steer via spool, fingerprint-resume (unchanged nodes skip).
- Typed failure facts: every `node.failed` / `item.finished` carries
  `error_class` + `attempts` (parent never infers from exit code + prose).
- Desktop DAG view inside the plugin SDK surface only; inline transcript card.
- Dashboard page (`dashboard/`), authoring skill, serial-runnable test suite.
- No self-updating code, no remote fetches anywhere (catalog rule 3); desktop JS
  is a single SDK-only file (rule 8); capabilities block matches registrations
  exactly (rule 6).

## Validation evidence

- `hermes plugins validate <release-tree>` — ALL GREEN, including the
  `desktop surface` check ("stays inside the plugin SDK surface") and the
  `security scan` check ("safe"). (Evidence inventory:
  workflow-081/PUBLISH-PLAN.md, run on the live release tree.)
- Serial suite: 41/41 green on the release tree at commit 42e99d8 — 33 `test_*.py`
  + 8 `test_*.mjs` (file counts verified against the tree; RELEASE.json records
  the merge-train qualification 2026-09-24).
- Spawn contract is stock: `hermes_cli/_parser.py` at the floor tag carries every
  flag the plugin spawns (`--query-file --oneshot --quiet --source
  --create-if-missing --max-turns --run-budget --provider --reasoning
  --toolsets`) and `hermes_cli/quiet_single_query.py` carries the
  `HERMES_QUIET_TURN_REPORT_FILE` contract. Verified by walking the published tag
  list newest→older (unauthenticated raw fetches, evidence:
  publish-0924/catalog-evidence/{tags.json,walk-result.json}):
  v2026.9.24 PASS, v2026.9.21 PASS, v2026.9.14 FAIL (all 10 flags present but
  `HERMES_QUIET_TURN_REPORT_FILE` absent from quiet_single_query.py).
  **requires_hermes floor: v2026.9.21 = 0.21.4** (`pyproject.toml` at the tag).
- Capabilities block matches reality at the pinned SHA:
  `provides_tools: [workflow]`, hooks `transform_llm_output`, `on_session_end`
  (both in stock `VALID_HOOKS`), no middleware, `requires_env: []` — the runner's
  `HERMES_WF_STEER_*` vars are plugin-internal IPC set by the runner itself and
  are deliberately not declared (requires_env means user-provided env only).
- No private/host-specific strings in the shipped tree (scrub pass lane; the
  packaging tests assert exclusion of the internal examples).

## Two-build install table (stock vs full capabilities)

From PUBLISH-PLAN.md — one codebase; the only capability needing a patched core is
typed turn-cap termination, and the plugin degrades honestly without it:

| | catalog / stock-hermes | full-capabilities |
|---|---|---|
| graphs, fan-out, gates, steer, resume, dashboard, cards | ✓ | ✓ |
| `max_turns` death | `unknown` + preserved partial/log | typed `max_turns` + reason |
| install | `hermes plugins install` at pinned SHA | + one patch step from `docs/patched-core.md` (or a `hermes update` pin, LEAN-NIGHTLY style) |

## Patched-core relationship

The plugin needs exactly ONE carried core patch — upstream PR #121041 (open),
which adds `turn_exit_reason` to the quiet `-Q` turn report — to type turn-cap
deaths as `max_turns` instead of `unknown`. Nothing auto-patches anyone's core:
the catalog install is pure stock; the patch is a documented operator choice
(`docs/patched-core.md`). The plugin's read model tells you which side you are on
without guessing: a turn-cap death surfaces `error_class=max_turns` on a core
that carries the field, and honestly stays `error_class=unknown` on stock
(`wf.py::_typed_error_class` reads the child's turn report; prose is never
grepped). The two core imports the plugin makes (`hermes_constants`,
`hermes_cli.config`) are soft with fallbacks, and the state.db join reads
stock columns only, `mode=ro`. If #121041 merges, the full-capabilities column
collapses into the stock column and the docs line deletes itself.

## Pins

- `sha` above is REPLACE_AT_RELEASE — a maintainer should not merge until it is
  a full 40-char commit SHA of https://github.com/jacobhausler/hermes-workflows
  (rule 2); the bump stays the review anchor for future updates (rule 4).
