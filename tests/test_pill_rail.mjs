// Pill rail (plan #22 item 2): railModel is a pure model over the session's
// owned runs — held first, then running by started desc, capped at 3 with an
// overflow count (the same policy as splitRuns, which stays for the pane);
// progress renders from nodes_done/nodes_total and is '?' when absent (never
// fabricated). PillRail renders one horizontal row of compact pills
// [Dot][short name][done/total]; gate-held pills keep GateActions. SessionStrip
// renders PillRail for the active set; the terminal fold is unchanged. Pure +
// JSX-tree asserts only: there is no DOM under node --experimental-strip-types.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// -- load the real module against a stub SDK -----------------------------------
// Stub '@hermes/plugin-sdk', 'react', 'react/jsx-runtime' (no node_modules in
// this repo). Stub atoms are plain writable cells so the test sets the focused
// chat; useQuery answers listQuery() from a settable `queries.list` and
// runQuery() from `queries.run`.
const stubSdk = `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const atom0 = atom
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const atoms = { focusedSessionId: atom(''), focusedStoredSessionId: atom('') }
// The SDK exposes the focused-chat atoms ONLY under host.state (sdk/index.ts).
export const host = {
  state: atoms,
  navigate: () => {}, notify: () => {}
}
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const Tip = 'Tip'
export const SIDEBAR_NAV_AREA = 'sidebar.nav', STATUSBAR_AREAS = { left: 'statusBar.left', right: 'statusBar.right' }
export const queries = { list: { runs: [] }, run: null }
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQuery = q => (Array.isArray(q.queryKey) && q.queryKey[1] === 'run'
  ? { data: queries.run, error: null }
  : { data: queries.list, error: null })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
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
const tmp = mkdtempSync(join(tmpdir(), 'wf-pill-'))
const sdkPath = join(tmp, 'sdk-stub.mjs')
writeFileSync(sdkPath, stubSdk)
const reactPath = join(tmp, 'react-stub.mjs')
writeFileSync(reactPath, stubReact)
const jsxPath = join(tmp, 'jsx-stub.mjs')
writeFileSync(jsxPath, stubJsx)
const modPath = join(tmp, 'plugin-under-test.mjs')
writeFileSync(modPath, src
  .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
  .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href))
  .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href)))
const mod = await import(pathToFileURL(modPath).href)
const sdkMod = await import(pathToFileURL(sdkPath).href)

const { railModel, PillRail, SessionStrip } = mod
assert.equal(typeof railModel, 'function', 'railModel is an exported pure model')
assert.equal(typeof PillRail, 'function', 'PillRail is exported')

// -- helpers --------------------------------------------------------------------
const mk = (id, status, extra = {}) => ({
  id, name: id, status, owner: { session_id: 'S1' },
  started: '2026-09-26T04:00:00Z', updated: '2026-09-26T04:05:00Z', ...extra
})
const textOf = node => {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string') return node
  if (Array.isArray(node)) return node.map(textOf).join(' ')
  if (typeof node.type === 'function') return textOf(node.type(node.props)) // render the component
  return textOf(node.props?.children)
}
// walk the jsx tree, RENDERING function components on the way down so nested
// components (Pill inside PillRail, GateActions inside Pill) are visible.
const findBy = (node, pred, out = []) => {
  if (node == null || typeof node === 'boolean' || typeof node === 'string') return out
  if (Array.isArray(node)) { node.forEach(n => findBy(n, pred, out)); return out }
  if (pred(node)) out.push(node)
  if (typeof node.type === 'function') { findBy(node.type(node.props), pred, out); return out }
  findBy(node.props?.children, pred, out)
  return out
}
const render = n => (typeof n.type === 'function' ? n.type(n.props) : n)

// -- 1. railModel: [] for no owned runs ------------------------------------------
{
  assert.deepEqual(railModel([]).pills, [], 'no owned runs -> no pills')
  assert.equal(railModel([]).overflow, 0, 'no owned runs -> no overflow')
  assert.deepEqual(railModel(null).pills, [], 'null list is []')
  assert.ok(Array.isArray(railModel([mk('t', 'done')]).pills) && railModel([mk('t', 'done')]).pills.length === 0,
    'terminal runs never get pills (the rail is the live set)')
}

// -- 2. ordering: held first, then running by started desc -----------------------
{
  const runs = [
    mk('r-old', 'running', { started: '2026-09-26T03:00:00Z', nodes_done: 1, nodes_total: 5 }),
    mk('h1', 'held', { started: '2026-09-26T04:30:00Z', held_gate: { id: 'go', options: ['ship', 'hold'] } }),
    mk('r-new', 'running', { started: '2026-09-26T04:00:00Z', nodes_done: 4, nodes_total: 7 }),
    mk('t1', 'done'),
  ]
  const m = railModel(runs)
  assert.deepEqual(m.pills.map(p => p.id), ['h1', 'r-new', 'r-old'],
    'held first, then running by started desc')
  assert.equal(m.overflow, 0, 'exactly 3 active is the cap, not overflow')
  assert.equal(m.pills[0].status, 'held', 'pill carries the run status')
  assert.equal(m.pills[0].held, true, 'gate-held pill is flagged held')
  assert.equal(m.pills[1].held, false, 'a running pill is not held')
  assert.equal(m.pills[1].progress, '4/7', "progress is `${nodes_done}/${nodes_total}`")
  assert.ok(m.pills[1].label.includes('r-new'), 'pill label names the run')
  assert.equal(m.pills[0].id, 'h1')
}

// -- 3. cap 3 + overflow count ----------------------------------------------------
{
  const runs = [
    mk('h1', 'held', { started: '2026-09-26T03:50:00Z' }),
    mk('r1', 'running', { started: '2026-09-26T04:03:00Z' }),
    mk('r2', 'running', { started: '2026-09-26T04:02:00Z' }),
    mk('r3', 'pending', { started: '2026-09-26T04:01:00Z' }),
    mk('r4', 'running', { started: '2026-09-26T04:00:00Z' }),
    mk('t1', 'done'),
  ]
  const m = railModel(runs)
  assert.equal(m.pills.length, 3, 'pills capped at 3 (same policy as splitRuns)')
  assert.equal(m.overflow, 2, 'overflow counts the active runs beyond the cap')
  assert.equal(m.pills[0].id, 'h1', 'held still sorts first at the cap')
  assert.deepEqual(m.pills.slice(1).map(p => p.id), ['r1', 'r2'], 'then newest-started first')
}

// -- 4. progress: never fabricated -------------------------------------------------
{
  const m = railModel([
    mk('a', 'running', { started: '2026-09-26T04:02:00Z', nodes_done: 4, nodes_total: 7 }),
    mk('b', 'running', { started: '2026-09-26T04:01:00Z' }),
    mk('c', 'running', { started: '2026-09-26T04:00:00Z', nodes_done: 2 }),
  ])
  const m2 = railModel([
    mk('d', 'running', { nodes_total: 6 }),
    mk('e', 'running', { nodes_done: null, nodes_total: null }),
  ])
  const by = Object.fromEntries([...m.pills, ...m2.pills].map(p => [p.id, p]))
  assert.equal(by.a.progress, '4/7')
  assert.equal(by.b.progress, '?', 'absent counts render ? — never 0/N')
  assert.equal(by.c.progress, '?', 'nodes_done without nodes_total is not fabricated')
  assert.equal(by.d.progress, '?', 'nodes_total without nodes_done is not fabricated')
  assert.equal(by.e.progress, '?')
}

// -- 5. PillRail: one horizontal row; held pills keep GateActions ------------------
{
  const held = mk('gate-run', 'held', {
    started: '2026-09-26T03:50:00Z',
    held_gate: { id: 'go', question: 'Ship?', options: ['ship', 'hold'] },
  })
  const live = mk('live-run', 'running', { started: '2026-09-26T04:00:00Z', nodes_done: 4, nodes_total: 7 })

  const tree = PillRail({ runs: [held, live] })
  assert.ok(tree, 'PillRail renders for a non-empty set')
  assert.equal(tree.props.style?.flexDirection, 'row', 'one horizontal row')
  const texts = textOf(tree)
  assert.ok(texts.includes('live-run'), 'pill shows the short name')
  assert.ok(texts.includes('4/7'), 'pill shows done/total')
  const pills = findBy(tree, n => typeof n.type === 'function' && n.type.name === 'Pill')
  assert.equal(pills.length, 2, 'one Pill per live run')
  const dots = pills.flatMap(p => findBy(render(p), n => typeof n.type === 'function' && /Dot$/.test(n.type.name)))
  assert.equal(dots.length, 2, 'every pill leads with a Dot ([Dot][short name][done/total])')

  // the gate-held pill keeps GateActions — and it still renders question + options
  const ga = findBy(tree, n => typeof n.type === 'function' && n.type.name === 'GateActions')
  assert.equal(ga.length, 1, 'gate-held pill keeps GateActions')
  const gaText = textOf(render(ga[0]))
  assert.ok(gaText.includes('Ship?') && gaText.includes('ship') && gaText.includes('hold'),
    'GateActions keeps the question and its option buttons')

  // overflow surfaces as a +N count, never silently dropped pills
  const many = [held, live, mk('r3', 'running'), mk('r4', 'running'), mk('r5', 'pending')]
  assert.ok(/\+2\s*more/.test(textOf(PillRail({ runs: many }))), 'overflow renders as +2 more')

  // no runs -> nothing renders (never an empty bordered box)
  const empty = PillRail({ runs: [] })
  assert.ok(empty === null || textOf(empty).trim() === '', 'no runs -> empty render')
}

// -- 6. SessionStrip renders PillRail for the ACTIVE set ---------------------------
{
  sdkMod.atoms.focusedSessionId.set('S1')
  sdkMod.atoms.focusedStoredSessionId.set('U1')
  const held = mk('gate-run', 'held', {
    started: '2026-09-26T03:50:00Z',
    held_gate: { id: 'go', question: 'Ship?', options: ['ship', 'hold'] },
  })
  const live = mk('live-run', 'running', { started: '2026-09-26T04:00:00Z', nodes_done: 4, nodes_total: 7 })
  const extra = [mk('r3', 'running', { started: '2026-09-26T04:01:00Z' })]
  const terminal = [mk('t1', 'done', { updated: '2026-09-26T04:10:00Z' })]
  sdkMod.queries.list = { runs: [held, live, ...extra, ...terminal] }

  const strip = SessionStrip()
  assert.ok(strip, 'SessionStrip renders for an owned live set')
  const rails = findBy(strip, n => n.type === PillRail)
  assert.equal(rails.length, 1, 'SessionStrip renders exactly one PillRail')
  assert.deepEqual(rails[0].props.runs.map(r => r.id), ['gate-run', 'r3', 'live-run'],
    'PillRail gets the active set (held first, started desc, capped)')
  const railText = textOf(render(rails[0]))
  assert.ok(railText.includes('4/7'), 'strip rail carries progress')
  assert.ok(!railText.includes('more'), 'at the cap there is no overflow affordance')
  // terminal fold unchanged: the finished line is still the strip's own
  assert.ok(textOf(strip).includes('1 finished'), 'terminal fold unchanged in the strip')
  // and no live rows duplicated outside the rail
  assert.equal(findBy(strip, n => typeof n.type === 'function' && n.type.name === 'PillRail').length, 1)
}

console.log('ALL PASS test_pill_rail (railModel ordering/cap/overflow/progress, PillRail row + GateActions, SessionStrip integration)')
rmSync(tmp, { recursive: true, force: true })
