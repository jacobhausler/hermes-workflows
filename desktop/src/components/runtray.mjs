/**
 * runtray.mjs — SKELETON for the collapsible running-only session tray
 * (#230 items 1+2, design truth = the native collapsed background-task tray;
 * supersedes the #22 aggregate shape and the #28 sticky-rail shape for live
 * runs).
 *
 * Target shape: a collapsible situational tray stacked as a sibling of the
 * native task-list / subagents / queued-messages family directly above the
 * chat window, keyed on owner.session_id INCLUDING dispatch/cron-shaped
 * launches whose owner.session_id matches the focused chat.
 *
 *   - RUNNING-ONLY LEDGER: rows = runs whose status ∉ TERMINAL =
 *     {done, failed, stopped}. A terminal run LEAVES the tray outright — the
 *     #22 ack-away ledger (× per finished row, cap 10) and the 60 s recap
 *     (`last run done · n/n nodes`) are superseded and were deleted with
 *     their exports. Zero rows -> the tray row renders nothing
 *     (trayShouldShow false).
 *   - collapsed: ONE slim single-line row `[chevron] N running workflows` —
 *     numeral + label, muted secondary text (CSS var), 1px low-contrast
 *     border, ~4-6px above the composer. Theme-safe inline styles only.
 *   - expanded: one row per RUNNING run — status chip, name + lane_key, node
 *     dots + x/y ('?' when absent, never 0/0), current node, elapsed, token
 *     chip. Ordering is THE SAME comparator as splitRuns: held first, then
 *     the rest by started desc (asserted as trayRunModel order == splitRuns
 *     active order on one shared ledger). Row click accordion-expands the
 *     shared MiniGraph; `open ↗` escalates to the pane; click-away collapses;
 *     Esc collapses to the collapsed row.
 *
 * SKELETON LAWS (this file):
 *  - Bodies are TODO shells: importing this module must never throw and must
 *    never touch the network or persistent state (R6: no behaviour by
 *    source-text; atoms in-memory only, never localStorage).
 *  - The REAL integration today lives in desktop/plugin.js: SessionStrip is
 *    the mount owner and the tray models (trayScoping, trayRunModel,
 *    trayShouldShow, toggleTray, $trayOpen) are exported from there and
 *    exercised by tests/test_run_tray.mjs. This module is the component
 *    family the build lane grows those bodies into; plugin.js must stay
 *    import-clean on its own regardless (tests/test_11_ui_imports.mjs
 *    freezes plugin.js imports to exactly three sources, so plugin.js may
 *    NEVER import-reexport from this file).
 *  - Imports ride the frozen baseline only: @hermes/plugin-sdk, react,
 *    react/jsx-runtime — zero new sources. The shells below import NOTHING so
 *    the file also parses/loads clean under plain node until the build lane
 *    grows real bodies (the moment jsx is needed it comes from
 *    react/jsx-runtime, the repo's baseline).
 *
 * STATUS (build lane, #230): the REAL implementation landed IN PLACE in
 * desktop/plugin.js — trayScoping/trayRunModel/trayShouldShow/toggleTray +
 * RunTrayRow/RunTrayRunRow/RunTray are exported there (test_11_ui_imports
 * freezes plugin.js imports at the three SDK sources, so plugin.js may never
 * import-reexport from this file). The shells below are kept as DESIGN
 * DOCUMENTATION only: the contract tests/test_run_tray.mjs asserts, in shell
 * shape. They throw on call so any accidental live use is loud, never
 * silently divergent.
 */

/**
 * Pure model shells. Mirrors the contract tests/test_run_tray.mjs asserts —
 * the build lane ports these to desktop/plugin.js (or re-exports the real
 * implementations from there); until then they throw to make any accidental
 * live use loud instead of silently wrong.
 */
export function trayScoping(runs, sid, uiSid, pairKey) {
  // TODO(build-lane): keep every run whose owner.session_id === sid —
  // dispatch/cron-shaped launches included; other sessions and blank-owner
  // runs never appear (pane-only, ownedRuns law).
  throw new Error('runtray scaffold: trayScoping not implemented')
}

export function trayRunModel(runs) {
  // TODO(build-lane): RUNNING-ONLY ledger — rows = runs whose status ∉
  // TERMINAL={done,failed,stopped} (terminal runs LEAVE: no ack ledger, no
  // 60 s recap); order = the splitRuns comparator (held first, then the rest
  // by started desc), uncapped (every live run listed); null/empty ledgers
  // are clean empties, never throws.
  throw new Error('runtray scaffold: trayRunModel not implemented')
}

export function trayShouldShow(model) {
  // TODO(build-lane): true iff the running-only model has at least one row;
  // zero rows (empty ledger, null ledger, terminal-only ledger) -> false and
  // the collapsed row renders nothing.
  throw new Error('runtray scaffold: trayShouldShow not implemented')
}

export function toggleTray(state, runId) {
  // TODO(build-lane): collapsed → { expanded: true, openRun: null };
  // open tray: row click accordion-toggles that row only.
  throw new Error('runtray scaffold: toggleTray not implemented')
}

/** Collapsed affordance: ONE slim single-line row `[chevron] N running
 *  workflows` — numeral + label, muted secondary text (CSS var), 1px
 *  low-contrast border, ▾/▴ chevron. Click anywhere expands. The #22 shape
 *  (⌬ pulse glyph, aggregate segments, micro sparkline) is retired. */
export function RunTrayRow({ count, expanded, onExpand }) {
  // TODO(build-lane): render `${count} running workflows` as ONE label node
  // matching /^\d+ running workflows$/; zero rows => the owner (RunTray)
  // renders nothing.
  return null
}

/** One expanded row for a single RUNNING run: status chip, name + lane_key,
 *  per-node dots + x/y, current node label, elapsed, token chip; accordion
 *  MiniGraph when open; GateActions for held; `open ↗` to the pane. No ack ×
 *  — terminal runs LEAVE the tray, there is nothing to dismiss. */
export function RunTrayRunRow({ run, open, onOpenPane }) {
  // TODO(build-lane)
  return null
}

/** The tray family root: collapsed slim row + drop-down run rows (max ~40%
 *  viewport, internal scroll), ordering held → running by started desc (the
 *  splitRuns comparator), click-away + Esc collapse. Zero running rows
 *  renders nothing. Mounts beside PillRail inside the SessionStrip composer
 *  registration. */
export function RunTray({ runs, sid }) {
  // TODO(build-lane)
  return null
}
