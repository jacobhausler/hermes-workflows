/**
 * runtray.mjs — MIRROR of the collapsible running-only session tray
 * (#230, design truth = the native collapsed background-task tray; supersedes
 * the #22 aggregate shape and the #28 sticky-rail shape for live runs).
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
 *   - expanded: one THICK row per RUNNING run — status chip, name + lane_key,
 *     x/y, current node, gate-question snippet when held, elapsed, token
 *     chip. The mini progress bar renders ONLY under a REAL ratio ('?' in
 *     x/y when absent — absent is NOT 0%, no invented progress fill). The
 *     accordion-OPENED row gains a selection ring in its OWN status tone
 *     (per-status, never a fixed accent). Ordering is THE shared comparator
 *     liveOrder (held first in input order, then the rest by started desc,
 *     documented tie law; asserted as trayLiveModel order == splitRuns
 *     active order on one shared ledger). Row click accordion-expands the
 *     shared RunGraphPanel/MiniGraph for THAT run (the superseded per-surface
 *     TrayPanel twin is deleted, no compat shim); the gate cell renders the
 *     INJECTED gateSlot adapter when the caller passes one (plugin.js injects
 *     its real GateActions; the mirror falls back to question + option
 *     buttons — the injected adapter is distinguishable and never shadowed
 *     by the fallback); `open ↗` escalates to the pane and is SEPARATE from
 *     the row's accordion click; click-away collapses; Esc collapses. The
 *     terminal half of the collection lives in SessionStrip's
 *     attention-first fold (collectionModel: failed/stopped always explicit;
 *     clean finished folds only past six — six visible, seven folded, full
 *     counted list reachable; failures never counted into 'finished').
 *
 * MIRROR LAWS (this file):
 *  - Bodies are REAL (#230 acceptance section 8): importing this module never
 *    throws, never touches the network or persistent state (R6: no behaviour
 *    by source-text; atoms in-memory only, never localStorage). The pure
 *    models and the row renderers mirror desktop/plugin.js EXACTLY —
 *    tests/test_session_tray.mjs asserts the same trees and the same ordering
 *    on one shared fake ledger, so this file is design documentation that can
 *    no longer lie.
 *  - The REAL integration lives in desktop/plugin.js: SessionStrip is the
 *    mount owner and the tray models + components are exported from there and
 *    exercised by tests/test_run_tray.mjs and tests/test_session_tray.mjs.
 *    plugin.js may NEVER import-reexport from this file
 *    (tests/test_11_ui_imports.mjs freezes plugin.js imports at the three SDK
 *    sources), so the duplication is deliberate and the parity test is the
 *    leash.
 *  - Imports ride the frozen baseline only: react/jsx-runtime — zero new
 *    sources (the SDK stub substitutes all three baseline specifiers).
 */
import { jsxs, jsx } from 'react/jsx-runtime'

const TERMINAL = new Set(['done', 'failed', 'stopped'])

const parseTime = v => {
  if (!v) return NaN
  const t = Date.parse(v)
  return Number.isFinite(t) ? t : NaN
}
const runStatusOf = r => (r && r.status) || 'pending'
// Root parity (review #233): the public status word is the FINAL lifecycle
// table law — done reads Finished; every other raw status keeps its exact
// word (cancelled neutrality law). The absent-sentinel here ('unknown') is
// the tray's own ratified wording, unchanged.
const statusLabel = s => !s ? 'unknown' : s === 'done' ? 'Finished' : s
const pillProgress = r =>
  (r?.nodes_done != null && r?.nodes_total != null) ? `${r.nodes_done}/${r.nodes_total}` : '?'
function fmtDur(ms) {
  if (!(ms > 0)) return ''
  const s = Math.round(ms / 1000)
  if (s < 60) return s < 1 ? '<1s' : `${s}s`
  const m = Math.floor(s / 60)
  return m < 60 ? (s % 60 ? `${m}m ${s % 60}s` : `${m}m`) : `${Math.floor(m / 60)}h ${m % 60}m`
}
const kfmt = n => n == null ? '' : n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e4 ? `${Math.round(n / 1e3)}k` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(n)
// Same tone vocabulary as plugin.js NODE_TONE (the ONE tone table, EDGE_TONE
// colors verbatim — the mirror may no longer fork palette strings: the row
// border, chip colour and the SELECTED ring all read these values, and the
// parity test compares the ring FORMULA per implementation).
const NODE_TONE = {
  running: { color: 'var(--ui-accent)', borderColor: 'var(--ui-accent)' },
  held: { color: 'var(--ui-warning, var(--ui-accent))', borderColor: 'var(--ui-warning, var(--ui-accent))' },
  pending: { color: 'var(--ui-stroke-secondary)', borderColor: 'var(--ui-stroke-secondary)' },
  done: { color: 'var(--ui-success, var(--ui-accent))', borderColor: 'var(--ui-success, var(--ui-accent))' },
  failed: { color: 'var(--ui-danger, var(--ui-text-tertiary))', borderColor: 'color-mix(in srgb, var(--ui-danger, var(--ui-text-tertiary)) 70%, transparent)' },
  stopped: { color: 'var(--ui-text-tertiary)', borderColor: 'var(--ui-text-tertiary)' },
  skipped: { color: 'var(--ui-text-tertiary)', borderColor: 'var(--ui-text-tertiary)' },
}

/**
 * Pure models — REAL bodies, mirroring desktop/plugin.js.
 * Tray scoping: every run whose owner.session_id === sid — dispatch/cron-
 * shaped launches included; other sessions and blank-owner runs never appear
 * (pane-only, ownedRuns law).
 */
export function trayScoping(runs, sid) {
  if (!sid) return []
  return (runs || []).filter(r => {
    const o = r?.owner?.session_id
    if (!o) return false
    return o === sid || (typeof o === 'string' && o.startsWith('cron_'))
  })
}

/** THE shared live comparator — mirrored verbatim from plugin.js liveOrder
 *  (AGENTS 4c.12 collapse-to-one: held rows keep their INPUT order; every
 *  other live run sorts by started DESC). Documented tie law: Array#sort is
 *  stable in every shipping engine, so EQUAL (or both-unparseable) `started`
 *  keeps input order, and an absent/unparseable started sorts LAST. */
export function liveOrder(runs) {
  const live = (runs || []).filter(r => r && !TERMINAL.has(runStatusOf(r)))
  const held = live.filter(r => r.status === 'held')
  const rest = live.filter(r => r.status !== 'held')
    .sort((a, b) => {
      const ta = parseTime(a.started), tb = parseTime(b.started)
      if (!Number.isFinite(ta) && !Number.isFinite(tb)) return 0 // equal/unparseable: input order (stable sort)
      if (!Number.isFinite(ta)) return 1                         // unparseable started sorts last
      if (!Number.isFinite(tb)) return -1
      return tb - ta                                             // started desc; ties keep input order
    })
  return [...held, ...rest]
}

/** RUNNING-ONLY ledger: rows = runs whose status ∉ TERMINAL (terminal runs
 *  LEAVE: no ack ledger, no 60 s recap); order = THE shared comparator
 *  (liveOrder — held first in input order, then the rest by started desc,
 *  documented tie law), uncapped (every live run listed); null/empty ledgers
 *  are clean empties, never a throw. */
export function trayRunModel(runs) {
  return { rows: liveOrder(runs).map(r => ({ id: r.id, status: runStatusOf(r), run: r })) }
}

/** #22-parity alias — the ledger model, one name per the mirror contract. */
export const trayModel = trayRunModel

/** The live set as a PLAIN run array — same ledger, same comparator,
 *  uncapped. Terminal runs leave outright (no recap window). */
export function trayLiveModel(runs) {
  return trayRunModel(runs).rows.map(r => r.run)
}

/** Pictured density label over the given (already-scoped) set — the
 *  collapsed row's whole glance is `N running workflows`, never a fabricated
 *  count: an empty live set reads '0 running workflows'. Mirrors plugin.js. */
export function trayRunningLabel(runs) {
  const count = trayLiveModel(runs).length
  return { count, line: `${count} running workflows` }
}

/** #22-parity aggregate label (PANE-side only — the collapsed tray row is
 *  the running-only slim line). Pure; the running-only law means every live
 *  row is one of the bands. */
export function trayAggregateLabel(runs) {
  const rows = trayRunModel(runs).rows
  const held = rows.filter(r => r.status === 'held').length
  return `${rows.length} running · ${held} held · ${rows.length - held} building`
}

/** #22-parity RECAP model (PANE-side only — the #230 tray NEVER renders a
 *  recap): a terminal-only ledger yields a recap line for `now` within
 *  window_ms of the most recent `updated`, and nothing after that window.
 *  The tray never calls it; this pure model stays for pane-side parity. */
export function trayRecap(runs, now, windowMs = 60000) {
  const terminal = (runs || []).filter(r => r && TERMINAL.has(runStatusOf(r)))
    .sort((a, b) => parseTime(b.updated) - parseTime(a.updated))
  if (!terminal.length) return null
  const latest = terminal[0]
  const t = parseTime(latest.updated)
  if (!Number.isFinite(t) || !Number.isFinite(now) || now - t > windowMs) return null
  return {
    id: latest.id,
    line: `last run done · ${latest.nodes_done ?? '?'}/${latest.nodes_total ?? '?'} nodes`
  }
}

/** #22-parity ack-away ledger (PANE-side only; the tray has nothing to
 *  dismiss — terminal runs LEAVE): the finished rows NOT yet acked, capped
 *  at 10 most-recently-updated. Pure; the tray never calls it. */
export function ackFinished(runs, acked = []) {
  const finished = (runs || []).filter(r => r && TERMINAL.has(runStatusOf(r)) && !acked.includes(r.id))
    .sort((a, b) => parseTime(b.updated) - parseTime(a.updated))
  return finished.slice(0, 10).map(r => r.id)
}

/** Pure visibility rule: zero rows (an empty ledger, a null ledger, a bare
 *  {rows:[]} model, or a ledger of ONLY terminal runs — they all produce
 *  zero rows) hides the tray entirely: the collapsed row renders nothing.
 *  Accepts the trayRunModel model OR a plain live-set array.
 *  est-z717 SETTINGS GATE (2nd arg, mirrors plugin.js): the tray renders ONLY
 *  under the owner's explicit opt-in `gate === true` (plugins.entries.
 *  hermes-workflows.settings.tray via GET /settings). Absent/null/false/
 *  truthy-non-boolean all stay HIDDEN — default OFF until the native tray SDK
 *  area (hermes-agent#133724) lands; the PillRail is never gated. (The
 *  retired #22 wall-clock parity arg is replaced — no recap window exists.) */
export function trayShouldShow(model, gate) {
  if (gate !== true) return false
  const rows = Array.isArray(model) ? model : ((model && model.rows) || [])
  return !!rows.length
}

/** Pure tray/accordion transition table: collapsed → open with NO single
 *  row expanded; the open tray's HEADER (runId == null) collapses the tray;
 *  with the tray open a row click accordion-toggles that row, clicking the
 *  open row again closes just the row. */
export function toggleTray(state, runId) {
  if (!state || !state.expanded) return { expanded: true, openRun: null }
  if (runId == null) return null
  return { expanded: true, openRun: state.openRun === runId ? null : runId }
}

/** Pure chevron transition: given the current glyph or the expanded flag,
 *  answer the OTHER state's glyph. ▾ collapsed, ▴ expanded. */
export function flipChevron(current) {
  if (current === '▴') return '▾'
  if (current === '▾') return '▴'
  return current ? '▴' : '▾'
}

/** Collapsed affordance: ONE slim single-line row `[chevron] N running
 *  workflows` — numeral + label, muted secondary text (CSS var), 1px
 *  low-contrast border, ▾/▴ chevron via the PURE transition fn. Click
 *  anywhere expands. The #22 shape (⌬ pulse glyph, aggregate segments, micro
 *  sparkline) is retired. #230 spec shape: `runs` (the scoped ledger) computes
 *  the count itself; the legacy `{count}` call shape stays accepted. */
export function RunTrayRow({ runs, count, expanded, onExpand }) {
  const n = runs !== undefined ? trayRunningLabel(runs).count
    : (Number.isFinite(count) && count > 0 ? Math.trunc(count) : 0)
  const chev = flipChevron(!!expanded)
  return jsxs('div', {
    role: 'button',
    tabIndex: 0,
    title: 'Toggle the running-workflow tray',
    onClick: e => { e?.stopPropagation?.(); onExpand?.() },
    onKeyDown: e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); onExpand?.() }
    },
    style: {
      display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
      fontSize: '0.6875rem', lineHeight: '1.2', padding: '3px 8px', borderRadius: 8,
      // Slim + quiet: one low-contrast hairline, muted secondary text — the
      // row is an affordance, not an alert (CSS vars only, theme-safe).
      color: 'var(--ui-text-secondary)',
      border: '1px solid var(--ui-stroke-secondary)',
      background: 'var(--ui-sidebar-surface-background, var(--card))'
    },
    children: [
      jsx('span', { 'aria-hidden': true, style: { color: 'var(--ui-text-tertiary)' }, children: chev }, 'chev'),
      jsx('span', { style: { fontVariantNumeric: 'tabular-nums' }, children: `${n} running workflows` }, 'label')
    ]
  }, 'tray-row')
}

function trayElapsed(r) {
  // Wall-clock elapsed since started (the live tray re-renders every second
  // via the owner's tick; 'updated' is a node commit time, not "now").
  const start = parseTime(r.started)
  return start ? fmtDur(Math.max(0, Date.now() - start)) : ''
}

/** Mini progress bar width from the read model's counts — a REAL ratio or
 *  null (mirrors plugin.js: an absent count is never fabricated as 0%; the
 *  x/y chip beside the bar carries the absence as '?'). */
const trayBarPct = r => (r?.nodes_done != null && r?.nodes_total != null && r.nodes_total > 0)
  ? `${Math.floor((r.nodes_done / r.nodes_total) * 100)}%` : null

/** One expanded THICK row for a single RUNNING run: status chip, name +
 *  lane_key, x/y + mini progress bar (key 'bar', width = the ratio), current
 *  running/held node ('→ id'), gate-question snippet when held, elapsed,
 *  token chip, `open ↗` to the pane. The accordion MiniGraph body is the
 *  caller's (plugin.js renders the shared component for the opened row; the
 *  mirror may not import app components — release-surface parity is proven
 *  plugin-side). No ack × — terminal runs LEAVE the tray, nothing to
 *  dismiss. div (never <button>): GateActions carries SDK Buttons (F6 law). */
export function RunTrayRunRow({ run, open, band, onToggleRow, onOpenPane, gateSlot }) {
  const r = run || {}
  const tone = NODE_TONE[runStatusOf(r)] || NODE_TONE.pending
  const nodes = r.nodes || null
  const nodeIds = nodes ? Object.keys(nodes) : []
  const current = nodeIds.find(n => nodes[n]?.status === 'running')
    || nodeIds.find(n => nodes[n]?.status === 'held') || null
  const ti = r.tokens_in, to = r.tokens_out
  const gate = r.status === 'held' && r.held_gate ? r.held_gate : null
  return jsxs('div', {
    style: {
      display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.6875rem',
      padding: '3px 8px', cursor: 'pointer', borderRadius: 6,
      // Every row reads its own tone border — colour lives HERE, not on the
      // slim collapsed row. The SELECTED (accordion-open) row gains the ring
      // in its OWN status tone (per-status, never a fixed accent — same
      // color-mix formula as plugin.js RunTrayRunRow).
      border: `1px solid ${tone.borderColor}`,
      boxShadow: open ? `inset 0 0 0 1px color-mix(in srgb, ${tone.color} 55%, transparent)` : undefined
    },
    onClick: e => { e?.stopPropagation?.(); onToggleRow?.(r.id) },
    children: [
      jsx('span', { style: { color: tone.color }, children: statusLabel(r.status) }, 'chip'),
      jsx('span', { style: { fontWeight: 600 }, children: r.name || r.id || 'workflow' }, 'name'),
      r.lane_key ? jsx('span', { style: { opacity: 0.7 }, children: r.lane_key }, 'lane') : null,
      // x/y rides the read model's counts, '?' when absent — never 0/N; the
      // mini bar beside it SPEAKS the ratio (key 'bar', width = pct) and
      // renders ONLY when a real ratio exists (absent is not 0%).
      jsx('span', { style: { fontVariantNumeric: 'tabular-nums', opacity: 0.8 }, children: pillProgress(r) }, 'xy'),
      trayBarPct(r) ? jsx('span', {
        'aria-hidden': true,
        style: { width: trayBarPct(r), minWidth: 24, height: 4, borderRadius: 2, background: tone.color, opacity: 0.6 }
      }, 'bar') : null,
      current ? jsx('span', { style: { opacity: 0.7 }, children: `→ ${current}` }, 'current') : null,
      trayElapsed(r) ? jsx('span', { style: { opacity: 0.6 }, children: trayElapsed(r) }, 'elapsed') : null,
      (ti != null || to != null)
        ? jsx('span', { title: 'tokens in ▸ out', style: { opacity: 0.7 }, children: `${kfmt(ti ?? 0)}▸${kfmt(to ?? 0)}` }, 'tokens')
        : null,
      gate
        ? jsx('div', {
            onClick: e => e?.stopPropagation?.(),
            // plugin.js passes its own GateActions element via gateSlot; the
            // mirror renders the question + option buttons beside it so the
            // thick-row anatomy never forks into a null hole.
            children: gateSlot
              || jsxs('div', { children: [
                gate.question ? jsx('span', { style: { opacity: 0.8 }, children: gate.question }, 'q') : null,
                ...(gate.options || []).map(o => jsx('button', { type: 'button', children: o }, o))
              ] })
          }, 'gate')
        : null,
      jsx('button', {
        type: 'button', title: 'Open in the Workflows pane',
        style: { cursor: 'pointer', background: 'none', border: 'none', padding: '0 2px', fontSize: '0.6875rem' },
        onClick: e => { e?.stopPropagation?.(); onOpenPane?.(r.id) },
        children: 'open ↗'
      }, 'open')
    ]
  }, `rr-${r.id}`)
}

/** The tray family root: collapsed slim row + drop-down THICK run rows
 *  (max ~40% viewport, internal scroll), ordering held → running by started
 *  desc (the splitRuns comparator), click-away + Esc collapse wired by the
 *  mount owner (SessionStrip). Zero running rows renders nothing. The
 *  MiniGraph accordion body is the caller's (plugin.js owns the shared
 *  component); this root only signals which row is open. Mounts beside
 *  PillRail inside the SessionStrip composer registration. */
export function RunTray({ runs, sid, trayOpen, trayRef, onToggleHeader, onToggleRow, onOpenPane, trayEnabled }) {
  // sid blank = the mount owner pre-scoped (focus-degraded law): trust the
  // given live set — same contract as plugin.js RunTray.
  const scoped = sid
    ? trayScoping(runs, sid)
    : (runs || []).filter(r => r && !TERMINAL.has(runStatusOf(r)))
  const model = trayRunModel(scoped)
  // est-z717: settings gate rides as a prop (mirror parity with plugin.js);
  // default OFF — only literal true renders the tray.
  if (!trayShouldShow(model, trayEnabled)) return null
  const openRun = trayOpen && trayOpen.expanded && trayOpen.openRun ? trayOpen.openRun : null
  return jsxs('div', {
    ref: trayRef,
    style: { display: 'flex', flexDirection: 'column', gap: 2 },
    children: [
      jsx(RunTrayRow, {
        runs: scoped,
        expanded: !!(trayOpen && trayOpen.expanded),
        onExpand: () => onToggleHeader?.()
      }, 'row'),
      trayOpen && trayOpen.expanded
        ? jsxs('div', {
            style: { display: 'flex', flexDirection: 'column', gap: 2, maxHeight: '40vh', overflowY: 'auto' },
            children: model.rows.map(r => jsx(RunTrayRunRow, {
              run: r.run, open: openRun === r.id,
              onToggleRow, onOpenPane
            }, `rr-${r.id}`))
          }, 'drop')
        : null
    ]
  }, 'run-tray')
}
