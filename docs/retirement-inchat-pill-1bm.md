# Retirement inventory — in-chat directive card (bd_2026-11-13-1bm, ship 2.0 W3)

Atomic transcript-path replacement: the RC pill+expand renderer shipped and
the legacy card-body renderer was deleted in the same PR. No runtime compat
flag, no shim, no parallel legacy path. This file is the record of every
caller that migrated and every symbol that died.

## Deleted symbols (desktop/plugin.js)

| Symbol | Was | Where it lives now |
|---|---|---|
| `pillModel(run, stale)` | one-line collapsed model (`collapsedLine`), exported for tests | `cardModel(run, stale)` — two baselines (identity + census) + the expanded word row, one record |
| `inlineHeader(data, elapsed)` | two-row expanded header (IN/OUT/API/TOOL abbreviations) | `cardModel.census` / `cardModel.metrics` — word-labelled (INCHAT §2), the run clock labelled (WF-06), cancelled neutral (WF-02) |
| `collapsedLine` field | the pill's single sentence | no field replaced it by design: identity + census cells; nothing renders one joined line |
| whole-pill `role: 'button'` span + nested `▾`/`↗` glyph buttons | click-anywhere expand with a button nested inside the click surface | two SIBLING native buttons `[data-wf-expand]` (aria-expanded/aria-controls) and `[data-wf-open]` (`Open full view ↗`); the container is inert chrome |
| CSS | — | none to delete: the retired renderer styled itself with inline styles that died with its JSX; plugin.js never carried a card-specific class block (verified by source grep at deletion) |

## Migrated callers (same PR)

| Caller | Migration |
|---|---|
| `desktop/plugin.js` `DirectiveBody` | renders the RC pill (two baselines, census row, body region behind the disclosure); MiniGraph/FanStrip mounts and the fan-guard laws (fanOpenFor/fanItems/fanPickedRow) unchanged — the SHARED graph/state helpers stay the only grammar |
| `tests/test_inline_header.mjs` | renamed `tests/test_card_model_header.mjs`; every law re-pinned on the real `cardModel` (2sf tokens, exact counts, LIVE/IDLE, COST words, honest dashes, cancelled partition, disclosure DOM regex); asserts the retired name never returns |
| `tests/test_lifecycle_numeric_view_models.mjs` | sections 5–6 evaluate `cardModel` instead of `inlineHeader`/`pillModel` (run-clock label, activity words, cancelled neutrality, stale word, honest-absent census) |
| `tests/test_directive_card_error.mjs` | stub mirrors the RC shape (`statusWord`); gains the stateful disclosure pin (sibling buttons, aria pair resolves to the body region, body mounts only expanded, no nested buttons, container has no click handler) and the malformed-id INERT pin through `DirectiveCard` itself |
| `tests/test_session_strip.mjs` | imports `cardModel`; the one-line law migrates to one-line-per-cell |
| `tests/test_tab_polish_48.mjs` | tone-parity probes ride `cardModel.tone`; pins `pillModel === undefined` (the retired export must not return as a shim) |
| `tests/test_wf_qa_render_group.mjs` | WF-06 clock and WF-09 COST probes evaluate `cardModel` over the shared view-model block (no header helper left to grab) |
| `tests/proof-harness/capture.mjs` (the driver is a caller of the DOM contract) | card location migrated from the `'Open in Workflows'` whole-card button walk to the RC `[data-wf-directive="<id>"]` hook (mounted in BOTH states); the graph case's `workflow…` pill-click preamble replaced by explicit `[data-wf-expand]` disclosure clicks via probe-first open; new `--case chat` drives the state matrix |
| `tests/proof-harness/cases.json` | adds `chat` (surfaces: directive_card; held+Finished engine seeds, `seed_chat.py` read-model fixtures, flock keeper, one nine-directive echo turn) |

Kept deliberately: `nodesCount` (the rail/pane `N/M terminal` copy lives on
those surfaces), `Dot`, the fan guards, and every numeric/lifecycle helper in
the shared view-model block — this bead retired the CARD RENDERER, not the
laws the whole plugin shares.

## Preserved laws (behavior tests migrated, not deleted)

- directive input grammar + registration (`test_card_frontend_contract.mjs`
  passes UNCHANGED — the parsed attr id still maps into `DirectiveCard`,
  `runQuery` still keys the read model by it);
- malformed id INERT, valid unknown retries, data-wins-over-error,
  `Disconnected · last known` stale word (Cached directive 04);
- WF-06 (run clock labelled), WF-09 (never `$0.0000`; `COST included` with
  recorded activity), WF-02/#7 (cancelled is never failed — the card census
  now partitions it explicitly: `! N failed` excludes cancelled records and
  `· N cancelled` rides its own neutral cell, pinned on real materialized
  rows in the chat case);
- #48 one-tone-table parity (cardModel.tone IS NODE_TONE's entry);
- census honesty: absent cells dash, recorded zeros stay 0.

## Historical records, untouched (byte-for-byte law)

`changelog.d/bd-2026-11-13-ah9.md` and the committed capture sets under
`tests/proof-harness/captured/` still speak the retired words — they record
what the code then was and are never rewritten.
