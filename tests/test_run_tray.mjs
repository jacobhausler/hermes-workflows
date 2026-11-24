// Running-only session tray (#230 items 1+2, design truth = the native
// collapsed background-task tray screenshot): the collapsed tray row is ONE
// slim single-line row `[chevron] N running workflows` — numeral + label,
// muted secondary text, 1px low-contrast border — replacing the #22 aggregate
// shape (⌬ pulse glyph + `N runs · X building · Y held` segments + sparkline).
//
// Ledger rule: rows = runs whose status ∉ TERMINAL={done,failed,stopped}.
// Terminal runs LEAVE the tray outright — this supersedes the #22 ack-away
// ledger and the 60 s recap (both deleted with their exports and tests).
// Zero rows -> trayShouldShow false and the tray row renders nothing.
//
// Ordering is THE SAME comparator as splitRuns: held first, then the rest by
// started desc — asserted as trayRunModel output order == splitRuns active
// order on one shared ledger.
//
// State stays the in-memory $trayOpen atom (never localStorage); theme-safe
// inline styles / CSS vars only. SessionStrip stays the mount owner
// (test_register_surface locks the 'session-strip' registration). R6: fake
// ledgers, no behaviour-by-source-text; atom/listener laws are asserted at
// source per the repo's established precedent.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// -- 0. static laws ---------------------------------------------------------------
// The tray's open state is an in-memory plugin atom (same law as $stripFold):
// a reload never resurrects an expanded tray, and state never hits localStorage.
assert.match(src, /const \$trayOpen = atom\(null\)/,
  '$trayOpen must be an in-memory atom(null) — never localStorage')
assert.doesNotMatch(src, /localStorage\s*\.\s*(setItem|getItem|removeItem)/,
  'the desktop half never persists state to localStorage (comments may name it)')
assert.doesNotMatch(src, /\$[A-Za-z0-9_]+\.get\(\)/,
  'atoms are set/useValue only — a .get() call throws inside click handlers')

// The superseded #22 collapsed shape is GONE (deleted with its exports): no
// pulse glyph, no sparkline blocks, no aggregate/recap/ack machinery left in
// the desktop half (source-text deletion law, the repo's established idiom —
// same shape as the localStorage law above).
assert.doesNotMatch(src, /⌬/, 'the #22 ⌬ pulse glyph is retired from the collapsed row')
assert.doesNotMatch(src, /▁▃/, 'the #22 micro sparkline is retired')
assert.doesNotMatch(src, /function trayRecap\b/, 'the 60 s recap is superseded (terminal runs LEAVE)')
assert.doesNotMatch(src, /function ackFinished\b/, 'the ack-away ledger is superseded (terminal runs LEAVE)')
assert.doesNotMatch(src, /function trayAggregateLabel\b/, 'the aggregate label is superseded by the slim running-only row')
assert.doesNotMatch(src, /runs · .* building · .* held/, 'the #22 aggregate copy is gone')

// -- 1. load the real module against stub SDK/react/jsx ---------------------------
const stubSdk = `
export const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const host = { state: { focusedSessionId: atom(''), focusedStoredSessionId: atom('') }, navigate: p => { (globalThis.__stubNav ||= []).push(p) }, notify: () => {} }
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const Tip = 'Tip'
export const SIDEBAR_NAV_AREA = 'sidebar.nav', STATUSBAR_AREAS = { left: 'statusBar.left', right: 'statusBar.right' }
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
export const useQuery = q => {
  const key = q && q.queryKey
  if (key && key[1] === 'run') { globalThis.__stubLastRunId = key[2]; return { data: globalThis.__stubDetail } }
  return { data: globalThis.__stubRuns ? { runs: globalThis.__stubRuns } : undefined }
}
export const useValue = a => {
  if (!a || typeof a.get !== 'function') return null
  if (globalThis.__stubOverrides && globalThis.__stubOverrides.has(a)) return globalThis.__stubOverrides.get(a)
  return a.get()
}
export const ctxRestStub = () => Promise.reject(new Error('no backend in test'))
`
const stubReact = `
export const useEffect = () => {}, useId = () => 't-0', useRef = () => ({ current: null }), useState = i => [typeof i === 'function' ? i() : i, () => {}]
export default { useEffect, useId, useRef, useState }
`
const stubJsx = `
export const jsx = (type, props, key) => ({ type, props: props || {}, key })
export const jsxs = jsx
export const Fragment = 'Fragment'
`
const tmp = mkdtempSync(join(tmpdir(), 'wf-tray-'))
const sdkPath = join(tmp, 'sdk-stub.mjs'); writeFileSync(sdkPath, stubSdk)
const reactPath = join(tmp, 'react-stub.mjs'); writeFileSync(reactPath, stubReact)
const jsxPath = join(tmp, 'jsx-stub.mjs'); writeFileSync(jsxPath, stubJsx)
const modPath = join(tmp, 'plugin-under-test.mjs')
writeFileSync(modPath, src
  .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
  .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href))
  .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href)))
const mod = await import(pathToFileURL(modPath).href)

// -- helpers ----------------------------------------------------------------------
const mk = (id, status, sid, extra = {}) => ({
  id, name: id, status, owner: { session_id: sid },
  started: '2026-10-05T04:00:00Z', updated: '2026-10-05T04:05:00Z', ...extra
})
const textOf = node => {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string') return node
  if (Array.isArray(node)) return node.map(textOf).join(' ')
  if (typeof node.type === 'function') return textOf(node.type(node.props))
  return textOf(node.props?.children)
}
const findBy = (node, pred, out = []) => {
  if (node == null || typeof node === 'boolean' || typeof node === 'string') return out
  if (Array.isArray(node)) { node.forEach(n => findBy(n, pred, out)); return out }
  if (pred(node)) out.push(node)
  if (typeof node.type === 'function') { findBy(node.type(node.props), pred, out); return out }
  findBy(node.props?.children, pred, out)
  return out
}

const { trayRunModel, trayShouldShow, trayScoping, toggleTray, RunTrayRow, SessionStrip } = mod
assert.equal(typeof trayRunModel, 'function', 'trayRunModel is an exported pure model')
assert.equal(typeof trayShouldShow, 'function', 'trayShouldShow is exported')
assert.equal(typeof trayScoping, 'function', 'trayScoping is exported')
assert.equal(typeof toggleTray, 'function', 'toggleTray is exported')
assert.equal(typeof RunTrayRow, 'function', 'RunTrayRow is exported')

// -- 2. owner.session_id scoping, INCLUDING dispatch/cron-shaped launches ----------
// The tray keys on the owner.session_id VALUE, not the launch surface: a
// dispatch-launched run (and even a cron_-shaped session id) whose
// owner.session_id matches the focused chat belongs in the tray — this is
// the auto-cards half of #22, unchanged by #230. A run owned by a DIFFERENT
// session never appears. The blank-session cron launch (owner.session_id '')
// stays honest-absent, pane-only — the same law ownedRuns already enforces.
{
  const runs = [
    mk('chat-launched', 'running', 'S1'),
    mk('dispatch-launched', 'running', 'S1', { launched_by: 'dispatch' }),
    mk('cron-owned', 'running', 'cron_daily_report'),
    mk('other', 'running', 'S2'),
    mk('blank', 'running', ''),
  ]
  const scoped = trayScoping(runs, 'S1', '', 'S1')
  assert.deepEqual(scoped.map(r => r.id).sort(),
    ['chat-launched', 'cron-owned', 'dispatch-launched'],
    'tray scoping keeps every run whose owner.session_id === sid (dispatch/cron-shaped launches join); other sessions and blank-owner runs never do')
}

// -- 3. ledger rule: terminal runs LEAVE --------------------------------------------
{
  const runs = [
    mk('b1', 'running', 'S1'),
    mk('h1', 'held', 'S1'),
    mk('d1', 'done', 'S1'),
    mk('f1', 'failed', 'S1'),
    mk('s1', 'stopped', 'S1'),
  ]
  const m = trayRunModel(runs)
  assert.deepEqual(m.rows.map(r => r.id), ['h1', 'b1'],
    'rows = runs whose status ∉ TERMINAL={done,failed,stopped} — terminal runs leave, no ack ledger, no recap')
  assert.deepEqual(trayRunModel([]).rows, [], 'empty ledger is a clean empty, never a throw')
  assert.deepEqual(trayRunModel(null).rows, [], 'null ledger is a clean empty, never a throw')
  assert.deepEqual(trayRunModel([null, mk('b1', 'running', 'S1')]).rows.map(r => r.id), ['b1'],
    'null rows are dropped, never a throw')
}

// -- 4. ordering parity: SAME comparator as splitRuns -------------------------------
{
  // One shared ledger; the tray's order must equal splitRuns' active order
  // exactly (held first, then the rest by started desc). Kept at 3 live rows
  // so splitRuns' cap-3 never truncates the compared window.
  const ledger = [
    mk('b2', 'running', 'S1', { started: '2026-10-05T04:03:00Z' }),
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:50:00Z', held_gate: { id: 'go', question: 'Ship?', options: ['ship', 'hold'] } }),
    mk('b1', 'running', 'S1', { started: '2026-10-05T04:01:00Z' }),
    mk('d1', 'done', 'S1', { started: '2026-10-05T04:00:00Z', updated: '2026-10-05T04:10:00Z' }),
    mk('f1', 'failed', 'S1', { started: '2026-10-05T04:00:00Z', updated: '2026-10-05T04:12:00Z' }),
    mk('s1', 'stopped', 'S1', { started: '2026-10-05T04:00:00Z', updated: '2026-10-05T04:11:00Z' }),
  ]
  assert.deepEqual(trayRunModel(ledger).rows.map(r => r.id),
    mod.splitRuns(ledger).active.map(r => r.id),
    'trayRunModel order == splitRuns active order on one shared ledger (held first, then running by started desc)')
  // Beyond splitRuns' cap-3 the tray lists EVERY live run (no cap), still
  // held-first with the rest by started desc.
  const big = [
    mk('h2', 'held', 'S1', { started: '2026-10-05T03:55:00Z' }),
    mk('h1', 'held', 'S1', { started: '2026-10-05T04:05:00Z' }),
    mk('b1', 'running', 'S1', { started: '2026-10-05T04:04:00Z' }),
    mk('b2', 'running', 'S1', { started: '2026-10-05T04:09:00Z' }),
    mk('b3', 'running', 'S1', { started: '2026-10-05T04:06:00Z' }),
    mk('d1', 'done', 'S1'),
  ]
  assert.deepEqual(trayRunModel(big).rows.map(r => r.id), ['h2', 'h1', 'b2', 'b3', 'b1'],
    'uncapped drop-down lists every live run: held first, then running by started desc')
}

// -- 5. visibility: zero rows -> false / null render --------------------------------
{
  assert.equal(trayShouldShow(trayRunModel([]), true), false, 'zero rows -> trayShouldShow false')
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')]), true), true, 'a live row -> visible')
  assert.equal(trayShouldShow(trayRunModel([mk('d1', 'done', 'S1'), mk('f1', 'failed', 'S1'), mk('s1', 'stopped', 'S1')]), true),
    false, 'a ledger of ONLY terminal runs is a zero-row tray (terminal runs LEAVE — no recap linger)')
  assert.equal(trayShouldShow({ rows: [] }, true), false, 'a bare zero-row model hides')
  // est-z717 SETTINGS GATE (pure model): the tray renders ONLY when the
  // owner's settings opt in — default OFF (native tray SDK area #133724 not
  // landed; when it lands, default-on rides that mount). absent/false/null/
  // non-true gate => hidden EVEN WITH live runs; true => today's behavior.
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')])), false,
    'z717: gate ABSENT -> no tray even with live runs (default OFF)')
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')]), false), false,
    'z717: gate false -> no tray even with live runs')
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')]), null), false,
    'z717: gate null (settings fetch never answered) -> fail-closed hidden')
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')]), 'true'), false,
    'z717: only literal true enables — a truthy non-boolean does not')
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')]), undefined), false,
    'z717: undefined gate -> hidden (default OFF)')
}

// -- 6. toggleTray: the tray row + in-tray row accordion (unchanged laws) ----------
{
  assert.deepEqual(toggleTray(null, 'a'), { expanded: true, openRun: null },
    'collapsed tray -> expanding the tray opens no single row')
  assert.deepEqual(toggleTray({ expanded: true, openRun: null }, 'a'), { expanded: true, openRun: 'a' },
    'open tray: row click accordion-opens that row')
  assert.deepEqual(toggleTray({ expanded: true, openRun: 'a' }, 'a'), { expanded: true, openRun: null },
    'clicking the OPEN row again closes just the row')
  assert.deepEqual(toggleTray({ expanded: true, openRun: 'a' }, 'b'), { expanded: true, openRun: 'b' },
    'another row switches')
}

// -- 7. the collapsed row: slim `[chevron] N running workflows` ---------------------
{
  // Pure render of the collapsed affordance: numeral + label ONLY, theme-safe
  // inline styles (muted secondary text, 1px low-contrast border), chevron.
  const row = RunTrayRow({ count: 3, expanded: false, onExpand: () => {} })
  const labelNodes = findBy(row, n => typeof n.props?.children === 'string' && /running workflows$/.test(n.props.children))
  assert.equal(labelNodes.length, 1, 'exactly one label node')
  assert.match(labelNodes[0].props.children, /^\d+ running workflows$/,
    'collapsed text matches /^\\d+ running workflows$/ (numeral + label, nothing else)')
  assert.equal(labelNodes[0].props.children, '3 running workflows', 'the numeral is the running count')
  const txt = textOf(row)
  assert.ok(!txt.includes('⌬'), 'no #22 pulse glyph')
  assert.ok(!txt.includes('·'), 'no aggregate separators')
  assert.ok(!/[▁▂▃▄▅▆▇]/.test(txt), 'no sparkline blocks')
  assert.ok(!/building|held\b/.test(txt), 'no per-band segments in the collapsed row')
  assert.ok(/▾|▴/.test(txt), 'the row carries the disclosure chevron')
  const rowNode = findBy(row, n => n.props?.role === 'button')[0]
  assert.ok(rowNode, 'the row is a focusable button row')
  const st = rowNode.props.style || {}
  assert.match(String(st.border || ''), /1px solid/, 'slim 1px border')
  assert.match(String(st.color || ''), /--ui-text-(secondary|tertiary)/, 'muted secondary text via a CSS var (theme-safe)')
  assert.equal(RunTrayRow({ count: 1, expanded: true, onExpand: () => {} }) && 1, 1, 'count=1 renders without throwing')
}

// -- 8. the REAL SessionStrip: mount/hide rules -------------------------------------
{
  const sdkMod = await import(pathToFileURL(sdkPath).href)
  sdkMod.host.state.focusedSessionId.set('S1')
  sdkMod.host.state.focusedStoredSessionId.set('')

  // zero runs -> tray hidden
  globalThis.__stubRuns = []
  globalThis.__stubOverrides = null
  assert.equal(SessionStrip(), null, 'zero runs -> tray hidden')

  // terminal-only ledger -> the tray row renders nothing (RunTray null)
  const terminalOnly = [mk('d1', 'done', 'S1'), mk('f1', 'failed', 'S1'), mk('s1', 'stopped', 'S1')]
  assert.equal(mod.RunTray({ runs: terminalOnly, sid: 'S1', trayOpen: null, trayRef: { current: null } }), null,
    'terminal-only ledger -> zero rows -> the tray renders nothing')

  // live runs -> collapsed row is the SLIM 'N running workflows' (terminal
  // rows do NOT count into N — d1 is in the ledger but leaves the tray)
  // est-z717: gate OFF (atom null = unanswered / settings say no) -> the
  // STRIP still mounts for its owned runs (PillRail is the always-on
  // surface), but the tray row renders NOTHING — no slim 'N running
  // workflows' line anywhere.
  globalThis.__stubRuns = [
    mk('b1', 'running', 'S1', { nodes_done: 2, nodes_total: 5 }),
  ]
  globalThis.__stubOverrides = new Map([[mod.$trayGate, false]])
  const gated = SessionStrip()
  assert.ok(gated, 'z717: gate off -> the strip stays mounted (rail untouched)')
  assert.ok(!textOf(gated).includes('running workflows'),
    'z717: gate off -> NO tray row even with a live run (default OFF)')
  assert.equal(findBy(gated, n => typeof n.type === 'function' && n.type.name === 'PillRail').length, 1,
    'z717: the PillRail is UNTOUCHED by the gate — always-on surface')
  globalThis.__stubRuns = [
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:50:00Z', held_gate: { id: 'go', question: 'Ship?', options: ['ship', 'hold'] } }),
    mk('b1', 'running', 'S1', { nodes_done: 2, nodes_total: 5 }),
    mk('d1', 'done', 'S1', { nodes_done: 3, nodes_total: 3, updated: '2026-10-05T04:04:50Z' }),
  ]
  globalThis.__stubOverrides = new Map([[mod.$trayGate, true]])
  const tree = SessionStrip()
  assert.ok(tree, 'live runs + gate ON -> tray renders')
  const txt = textOf(tree)
  assert.match(txt, /2 running workflows/, 'collapsed row reads N over RUNNING-only (terminal excluded)')
  assert.ok(/▾|▴/.test(txt), 'the row has the disclosure chevron')
  assert.ok(!txt.includes('⌬'), 'the collapsed row is not the #22 pulse-glyph shape')
  assert.ok(!/3 runs · 1 building · 1 held/.test(txt), 'the #22 aggregate label is retired')

  // expanded: one row per RUNNING run, MiniGraph for the opened row only,
  // gate release reuses the existing GateActions surface, and the steer/stop
  // buttons are ABSENT (the plugin ships no steer/stop action surface today —
  // graceful degrade, recorded as a gap in the PR body, no new server endpoint).
  globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: true, openRun: 'b1' }], [mod.$trayGate, true]])
  globalThis.__stubDetail = { id: 'b1', name: 'b1', status: 'running', nodes: { a: { status: 'done' }, b: { status: 'running' }, c: { status: 'pending' } } }
  const open = SessionStrip()
  const openTxt = textOf(open)
  assert.ok(openTxt.includes('b1'), 'expanded tray names each run')
  assert.ok(openTxt.includes('2/5'), 'row shows node progress x/y')
  assert.ok(openTxt.includes('open ↗'), 'row offers the bigger-pane escalation')
  assert.ok(!openTxt.includes('×'), 'no ack-away × — terminal runs LEAVE, nothing to dismiss')
  const mini = findBy(open, n => typeof n.type === 'function' && n.type.name === 'MiniGraph')
  assert.equal(mini.length, 1, 'exactly one accordion-opened row renders the shared MiniGraph')
  assert.equal(globalThis.__stubLastRunId, 'b1', 'MiniGraph is fed by the opened run only')
  const ga = findBy(open, n => typeof n.type === 'function' && n.type.name === 'GateActions')
  assert.equal(ga.length, 1, 'held row keeps the existing gate-release surface (no new server surface)')
  assert.ok(!/steer/.test(openTxt) && !/⏹/.test(openTxt),
    'steer/stop buttons are ABSENT — no such plugin surface exists today (degrade, do not invent one)')
  // a stale openRun from a collapsed tray never leaks a MiniGraph into the
  // collapsed state (RunTray gates the accordion on trayOpen.expanded)
  globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: false, openRun: 'b1' }], [mod.$trayGate, true]])
  const staleClosed = SessionStrip()
  assert.equal(findBy(staleClosed, n => typeof n.type === 'function' && n.type.name === 'MiniGraph').length, 0,
    'expanded:false with a stale openRun renders NO MiniGraph')
  globalThis.__stubOverrides = null
}

// -- 9. scoping guards at the pure edge ----------------------------------------------
{
  assert.deepEqual(trayScoping([mk('a', 'running', 'S1')], ''), [], 'no focused session -> no tray rows')
  assert.deepEqual(trayScoping(null, 'S1'), [], 'null ledger is a clean empty, never a throw')
}

// Click-away / Esc collapse (scoped-listener laws, asserted at source per
// precedent): Esc collapses the tray FIRST ($trayOpen -> null), the rail
// panel only after; click-away excludes clicks inside the tray via trayRef
// (never a DOM-node listener, the window listener stays the plugin's ONE —
// test_tab_polish_48 locks the budget).
assert.match(src, /if \(e\.key === 'Escape'\)\s*\{\s*if \(trayExpanded\) \$trayOpen\.set\(null\)/,
  "Esc collapses the expanded tray to the collapsed-row state BEFORE the rail panel")
assert.match(src, /trayExpanded && trayRef\.current && trayRef\.current\.contains\(e\.target\)/,
  'click-away excludes clicks inside the open tray (trayRef contains check)')
assert.match(src, /window\.addEventListener\('click', onDocClick\)/,
  'click-away rides the single window-level listener (no DOM-node listeners)')

// -- 10. W3 collection + accordion acceptance (bd_2026-11-13-3gh) -------------------
// Per-status SELECTED RING (never a fixed accent), REAL RATIO ONLY (absent
// is not 0%), cap-3 +N BEHAVIOUR (the affordance reaches the uncapped pane
// index), SEPARATE Open-in-pane (row click toggles, open button navigates),
// SINGLE ACCORDION (one opened row, one MiniGraph), the clean-finished fold
// boundary SPECIMENS (six flat, seven folded, seventeen all reachable,
// failures/attention excluded from the finished count) — all driven through
// the REAL SessionStrip over fake ledgers (behavior, not source text).
{
  const sdkMod = await import(pathToFileURL(sdkPath).href)
  sdkMod.host.state.focusedSessionId.set('S1')
  sdkMod.host.state.focusedStoredSessionId.set('')
  const trayLedger = [
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:50:00Z', nodes_done: 1, nodes_total: 3,
      held_gate: { id: 'go', question: 'Ship?', options: ['ship', 'hold'] } }),
    mk('b1', 'running', 'S1', { started: '2026-10-05T04:01:00Z', nodes_done: 2, nodes_total: 5 }),
    mk('b2', 'running', 'S1', { started: '2026-10-05T04:02:00Z' }), // NO counts: ratio absent
  ]
  globalThis.__stubRuns = trayLedger
  globalThis.__stubDetail = { id: 'b1', name: 'b1', status: 'running', nodes: { a: { status: 'done' } } }

  // (a) per-status selected ring + (b) real-ratio-only bar, on the OPEN row.
  globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: true, openRun: 'b1' }], [mod.$trayGate, true]])
  let tree = SessionStrip()
  const rowOf = (t, id) => findBy(t, n => n.key === `rr-${id}`)[0]
  const b1 = rowOf(tree, 'b1')
  assert.ok(b1 && String(b1.props.style.boxShadow || '').includes('var(--ui-accent)'),
    'the accordion-open RUNNING row rings in the running tone (per-status, not a fixed accent)')
  assert.equal(rowOf(tree, 'b2').props.style.boxShadow, undefined,
    'an unselected row carries NO ring')
  assert.equal(findBy(tree, n => n.key === 'bar').length, 2,
    'rows WITHOUT a real ratio render NO progress bar (absent is not 0%): h1+b1 only')
  assert.ok(!findBy(tree, n => n.key === 'bar').some(n => n.props.style.width === '0%'),
    'no fabricated 0% width survives anywhere in the tray rows')
  assert.ok(textOf(tree).includes('?'), 'the absent ratio reads ? in x/y (honest absence)')
  globalThis.__stubOverrides.set(mod.$trayOpen, { expanded: true, openRun: 'h1' })
  tree = SessionStrip()
  assert.ok(String(rowOf(tree, 'h1').props.style.boxShadow || '').includes('var(--ui-warning'),
    'the held row rings in the HELD tone — the ring follows the row status, differing from the running ring')

  // (c) separate Open-in-pane: the row click toggles the accordion, the open
  // button navigates to the pane and NEVER toggles the accordion.
  globalThis.__stubOverrides.set(mod.$trayOpen, { expanded: true, openRun: null })
  tree = SessionStrip()
  globalThis.__stubNav = []
  const b1Row = rowOf(tree, 'b1')
  const openInB1 = findBy(b1Row, n => n.key === 'open')[0]
  const trayBefore = JSON.stringify(mod.$trayOpen.get())
  openInB1.props.onClick({ stopPropagation: () => {} })
  assert.deepEqual(globalThis.__stubNav, ['/workflows'], 'open ↗ escalates to the pane (separate intent)')
  assert.equal(JSON.stringify(mod.$trayOpen.get()), trayBefore,
    'open ↗ does NOT toggle the accordion — the two controls are separate')
  b1Row.props.onClick({ stopPropagation: () => {} })
  assert.equal(mod.$trayOpen.get().openRun, 'b1', 'the ROW click is what accordion-opens the row')

  // (d) single accordion: two live rows, one opened — exactly ONE shared
  // RunGraphPanel/MiniGraph mount, fed by the opened run only.
  globalThis.__stubOverrides.set(mod.$trayOpen, { expanded: true, openRun: 'b1' })
  const panels = findBy(SessionStrip(), n => typeof n.type === 'function' && n.type.name === 'RunGraphPanel')
  assert.equal(panels.length, 1, 'one opened row -> exactly one shared RunGraphPanel')
  assert.equal(globalThis.__stubLastRunId, 'b1', 'the shared panel is fed the opened run')

  // (e) cap-3 +N reaches the uncapped index: with 5 live owned runs the
  // rail caps at 3 pills and the +N affordance OPENS THE PANE (the full
  // index), it never silently drops the overflow.
  globalThis.__stubOverrides = new Map([[mod.$trayGate, false]])
  globalThis.__stubRuns = [1, 2, 3, 4, 5].map(i => mk(`m${i}`, 'running', 'S1', { started: `2026-10-05T04:0${i}:00Z` }))
  tree = SessionStrip()
  const overflowBtn = findBy(tree, n => n.key === 'overflow')[0]
  assert.ok(overflowBtn && /\+2 more/.test(textOf(overflowBtn)), 'cap-3 rail shows +2 more over 5 live runs')
  globalThis.__stubNav = []
  overflowBtn.props.onClick({ stopPropagation: () => {} })
  assert.deepEqual(globalThis.__stubNav, ['/workflows'],
    'the +N affordance navigates to the pane that lists EVERY live run uncapped')

  // (f) terminal eviction = no tray DOM at all when zero rows live.
  globalThis.__stubRuns = [mk('d1', 'done', 'S1'), mk('f1', 'failed', 'S1'), mk('s1', 'stopped', 'S1')]
  globalThis.__stubOverrides = new Map([[mod.$trayGate, true]])
  tree = SessionStrip()
  assert.ok(tree, 'the strip still renders its collection for a terminal-owned ledger')
  assert.equal(findBy(tree, n => typeof n.type === 'function' && n.type.name === 'RunTrayRow').length, 0,
    'terminal-only ledger -> ZERO tray DOM (the slim row is not rendered at all)')
  assert.ok(!textOf(tree).includes('running workflows'), 'no slim row text survives eviction')

  // (g) clean-finished fold specimens: SIX lie flat (no fold chrome), SEVEN
  // fold (six visible + ▸ 7 finished), SEVENTEEN all reachable when the fold
  // opens — and failures/attention are explicit rows EXCLUDED from the
  // finished count.
  const doneRow = i => mk(`d${i}`, 'done', 'S1', { updated: `2026-10-05T03:${String(i).padStart(2, '0')}:00Z` })
  const sixLedger = [...Array(6)].map((_, i) => doneRow(i + 1))
  globalThis.__stubRuns = sixLedger
  tree = SessionStrip()
  assert.ok(tree, 'six owned finished still render the strip')
  assert.equal(findBy(tree, n => String(n.key).startsWith('cr-')).length, 6, 'SIX clean rows visible')
  assert.ok(!/\d+ finished/.test(textOf(tree)), 'no fold chrome at exactly six (strictly greater than folds)')
  assert.equal(findBy(tree, n => n.key === 'fold-toggle').length, 0, 'the fold toggle does not exist at six')
  globalThis.__stubRuns = [...sixLedger, doneRow(7)]
  tree = SessionStrip()
  assert.equal(findBy(tree, n => String(n.key).startsWith('cr-')).length, 6, 'SEVEN finished -> six visible (the seventh is folded)')
  assert.ok(/▸ 7 finished/.test(textOf(tree)), 'the fold label names the true clean count 7')
  findBy(tree, n => n.key === 'fold-toggle')[0].props.onClick()
  tree = SessionStrip()
  assert.equal(findBy(tree, n => String(n.key).startsWith('cr-')).length, 7, 'the collapsed-then-expanded fold reveals the seventh row')
  const seventeen = [...Array(17)].map((_, i) => doneRow(i + 1))
  globalThis.__stubRuns = [...seventeen,
    mk('atf1', 'failed', 'S1', { updated: '2026-10-05T04:20:00Z' }),
    mk('atf2', 'stopped', 'S1', { updated: '2026-10-05T04:21:00Z' })]
  tree = SessionStrip()
  const txt17 = textOf(tree)
  assert.ok(/▾ 17 finished/.test(txt17), 'SEVENTEEN finished: the label counts the CLEAN ledger (attention excluded — 17, not 19)')
  assert.equal(findBy(tree, n => String(n.key).startsWith('cr-')).length, 19,
    'expanded fold lists every counted row (17 finished) AND every attention row (2) — none hidden, none capped')
  assert.ok(/atf1 · failed ·/.test(txt17) && /atf2 · stopped ·/.test(txt17),
    'attention rows are explicit with their status word')
  globalThis.__stubOverrides.set(mod.$stripFold, null)
  globalThis.__stubOverrides = null
}

rmSync(tmp, { recursive: true, force: true })
console.log('ALL PASS test_run_tray (trayScoping, trayRunModel running-only ledger + splitRuns order parity, visibility zero->false, toggleTray, slim collapsed row contract, SessionStrip mount/hide, collapse laws)')
