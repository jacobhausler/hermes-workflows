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
export const host = { state: { focusedSessionId: atom(''), focusedStoredSessionId: atom('') }, navigate: () => {}, notify: () => {} }
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
  assert.equal(trayShouldShow(trayRunModel([])), false, 'zero rows -> trayShouldShow false')
  assert.equal(trayShouldShow(trayRunModel([mk('b1', 'running', 'S1')])), true, 'a live row -> visible')
  assert.equal(trayShouldShow(trayRunModel([mk('d1', 'done', 'S1'), mk('f1', 'failed', 'S1'), mk('s1', 'stopped', 'S1')])),
    false, 'a ledger of ONLY terminal runs is a zero-row tray (terminal runs LEAVE — no recap linger)')
  assert.equal(trayShouldShow({ rows: [] }), false, 'a bare zero-row model hides')
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
  globalThis.__stubRuns = [
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:50:00Z', held_gate: { id: 'go', question: 'Ship?', options: ['ship', 'hold'] } }),
    mk('b1', 'running', 'S1', { nodes_done: 2, nodes_total: 5 }),
    mk('d1', 'done', 'S1', { nodes_done: 3, nodes_total: 3, updated: '2026-10-05T04:04:50Z' }),
  ]
  const tree = SessionStrip()
  assert.ok(tree, 'live runs -> tray renders')
  const txt = textOf(tree)
  assert.match(txt, /2 running workflows/, 'collapsed row reads N over RUNNING-only (terminal excluded)')
  assert.ok(/▾|▴/.test(txt), 'the row has the disclosure chevron')
  assert.ok(!txt.includes('⌬'), 'the collapsed row is not the #22 pulse-glyph shape')
  assert.ok(!/3 runs · 1 building · 1 held/.test(txt), 'the #22 aggregate label is retired')

  // expanded: one row per RUNNING run, MiniGraph for the opened row only,
  // gate release reuses the existing GateActions surface, and the steer/stop
  // buttons are ABSENT (the plugin ships no steer/stop action surface today —
  // graceful degrade, recorded as a gap in the PR body, no new server endpoint).
  globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: true, openRun: 'b1' }]])
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
  globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: false, openRun: 'b1' }]])
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

rmSync(tmp, { recursive: true, force: true })
console.log('ALL PASS test_run_tray (trayScoping, trayRunModel running-only ledger + splitRuns order parity, visibility zero->false, toggleTray, slim collapsed row contract, SessionStrip mount/hide, collapse laws)')
