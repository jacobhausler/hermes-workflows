# plugin-catalog: add `hermes-workflows` (community, automation)

Submitted by the plugin repository owner (rule 5).

## What it is

`workflow` tool for Hermes Agent: the calling agent owns a JSON graph of agent
nodes, fan-outs and gates; a background runner executes it with fingerprint
replay-skip resume, fan-out quorum, per-node retries, cooperative steer, and
typed failure events (`error_class` + `attempts` on every `node.failed` — the
parent never infers from exit code + prose). Ships a desktop DAG view (SDK
surface only), an inline `::workflow{id}` transcript card, and the authoring
skill with measured budget recipes. Children are spawned through the stock quiet
one-shot CLI (`hermes chat --query-file … -Q --max-turns N`).

Repo: https://github.com/jacobhausler/hermes-workflows — README with
screenshots, `AGENTS.md` (agent front door: install / operate / contribute),
`INSTALL.md`.

## Catalog rules, checked at the pinned SHA

| Rule | Evidence |
|---|---|
| 2 — exact pin | `sha` is the 40-char commit of tag `v0.9.0`; `image`/`screenshots` are raw URLs pinned to the same SHA |
| 3 — no self-updater | No update checks and no remote fetches anywhere: zero `fetch(` in `desktop/plugin.js`, zero `urlopen` outside `tests/`; the plugin never loads code it did not ship |
| 6 — capabilities match | `provides_tools: [workflow]`; hooks `transform_llm_output`, `on_session_end` (both in stock `VALID_HOOKS`); no middleware; `requires_env: []` — the runner's `HERMES_WF_STEER_*` vars are plugin-internal IPC set by the runner for its own children, never user-provided (`docs/manifest-decisions.md`) |
| 7 — install scanner | `hermes plugins validate .` → `Validation passed.`, security scan `safe`, zero `caution` findings |
| 8 — desktop surface | `desktop/plugin.js` imports only `@hermes/plugin-sdk` / `react`; no prototype patching, no `eval`, no dynamic `import()`, no app-store access; passes the `desktop surface` check |
| 9 — dependencies | None. Stdlib-only Python; no `python_dependencies`, no `pyproject.toml` |

## `requires_hermes: ">=0.21.4"` — measured, not guessed

The spawn contract needs every flag the plugin passes (`--query-file -Q
--source --create-if-missing --max-turns --run-budget --provider --reasoning
--toolsets`) in `hermes_cli/_parser.py` and the `HERMES_QUIET_TURN_REPORT_FILE`
turn-report contract in `hermes_cli/quiet_single_query.py`. Walking published
tags newest → older: `v2026.9.24` PASS, `v2026.9.21` PASS, `v2026.9.14` FAIL
(flags present, turn report absent). `v2026.9.21` is `pyproject.toml` version
`0.21.4`.

## Test evidence at the pin

- Serial suite `python3 scripts/suite.py . out` — **42/42** green (34 `test_*.py`
  + 8 `test_*.mjs`), run on the exact tree that was pushed.
- CI in the repo runs the same four gates (ESM parse, suite, private-string
  scrub audit, `hermes plugins validate`) against a clone of `hermes-agent`
  pinned to `v2026.9.21` (`.github/workflows/ci.yml`).
- Core imports are two, both soft with fallbacks (`hermes_constants`,
  `hermes_cli.config`); the state.db metrics join reads stock columns only,
  `mode=ro`.

## Relationship to a patched core

None required. Stock Hermes records a child that dies on its turn cap as
`error_class: unknown` (partial output and log preserved). Open PR #121041 adds
`turn_exit_reason` to the quiet turn report; with it the same death is typed
`max_turns`. The plugin reads the field if present and says `unknown` if not —
nothing auto-patches anyone's core, and `status` reports which tier a failed
child ran under (`turn_report: typed|untyped`). If #121041 merges, the
distinction disappears.
