// L3 acceptance: the registration surface is exactly {transcript.directives,
// routes, panes, composer.top}; the pane docks {pane:'sessions', pos:'center',
// enforce:true}; groupRuns puts held/failed/interrupted under NEEDS YOU;
// SMIL <animate> rides ONLY paths leaving running nodes; the MiniGraph ghost
// stack is gone (one FanStack — grep 'inset: 4px 0 0 4px' must be 0).
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// -- load the real module against a stub SDK -----------------------------------
// Stub '@hermes/plugin-sdk', 'react', and 'react/jsx-runtime' (no node_modules
// in this repo); everything else is the real module.
const stubSdk = `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const atom0 = atom
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const host = { focusedStoredSessionId: atom(''), focusedSessionId: atom(''), navigate: () => {} }
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const useMutation = () => ({}), useQuery = () => ({})
export const useQueryClient = () => ({}), useValue = () => null
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
const tmp = mkdtempSync(join(tmpdir(), 'wf-reg-'))
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

// -- 1. registration surface ----------------------------------------------------
const regs = []
const ctx = { register: r => regs.push(r), rest: () => Promise.reject(new Error('no backend')) }
await mod.default.register(ctx)

const areas = [...new Set(regs.map(r => r.area))].sort()
assert.deepEqual(areas, ['composer.top', 'panes', 'routes', 'transcript.directives'],
  `areas registered must be exactly the four, got ${JSON.stringify(areas)}`)

// -- 2. the pane docks center into the sessions strip, enforced -----------------
const pane = regs.find(r => r.area === 'panes')
assert.ok(pane, 'a panes registration exists')
assert.equal(pane.id, 'pane')
assert.deepEqual(pane.data.dock, { pane: 'sessions', pos: 'center', enforce: true },
  'pane dock must be the BOTS-pattern center dock')
assert.equal(pane.data.placement, 'left')
assert.equal(pane.data.width, '260px')
assert.equal(pane.data.collapsible, true)
assert.equal(pane.data.hideOnly, true)
assert.equal(typeof pane.data.tabTitle, 'function', 'tabTitle renders WORKFLOWS · n')
assert.equal(typeof pane.data.tabTitleText, 'function')
assert.equal(typeof pane.render, 'function')

// -- 3. groupRuns: NEEDS YOU holds held + failed + interrupted ------------------
const mk = (id, status, updated) => ({ id, status, updated, owner: {} })
const runs = [
  mk('h1', 'held', 1), mk('f1', 'failed', 2), mk('i1', 'interrupted', 3),
  mk('r1', 'running', 4), mk('p1', 'pending', 5),
  mk('d1', 'done', 6), mk('s1', 'stopped', 7)
]
const g = mod.groupRuns(runs)
assert.deepEqual(g.needsYou.map(r => r.id), ['i1', 'f1', 'h1'],
  'held+failed+interrupted under NEEDS YOU, updated desc')
assert.deepEqual(g.running.map(r => r.id), ['p1', 'r1'], 'running+pending under RUNNING')
assert.deepEqual(g.done.map(r => r.id), ['s1', 'd1'], 'done+stopped under DONE')

// -- 4. SMIL candy: <animate> ONLY on paths leaving running nodes ----------------
const grab = name => {
  const i = src.indexOf(`function ${name}(`)
  if (i < 0) throw new Error(`missing function ${name}`)
  let depth = 0, j = src.indexOf(') {', i) + 2
  for (; j < src.length; j++) if (src[j] === '{') depth++; else if (src[j] === '}' && --depth === 0) break
  return src.slice(i, j + 1)
}
let instance = 0
const jsx = (type, props, key) => ({ type, props, key })
const { Edges, depthMap } = new Function('jsx', 'jsxs', 'useId',
  `const EDGE_TONE = { done:'teal', pending:'gray', failed:'red', running:'blue', held:'orange', skipped:'gray' };\n${['depthMap', 'edgePath', 'routeEdge', 'edgeTone', 'nodeState', 'Edges'].map(n => { try { return grab(n) } catch { return '' } }).join('\n')}\nreturn { Edges, depthMap }`)(jsx, jsx, () => `t-${++instance}`)
const nodes = [
  { id: 'a' }, { id: 'b', after: ['a'] }, { id: 'c', after: ['a'] }, { id: 'd', after: ['b'] },
  { id: 'e', after: ['c'] }
]
function rectsFor(defs) {
  const depths = depthMap(defs), rects = {}, cols = []
  for (const n of defs) (cols[depths.get(n.id)] ||= []).push(n)
  let x = 20
  cols.forEach(col => {
    let y = 80
    for (const n of col) { rects[n.id] = { x, y, w: 168, h: 74 }; y += 102 }
    x += 280
  })
  return rects
}
{
  const states = { a: { status: 'running' }, b: { status: 'pending' }, c: { status: 'failed' }, d: { status: 'pending' } }
  const svg = Edges({ nodes, rects: rectsFor(nodes), states, gate: null })
  const paths = svg.props.children.filter(x => x && x.type === 'path' && x.props.d)
  assert.equal(paths.length, 4, 'every edge renders')
  for (const p of paths) {
    const from = p.key.split('->')[0]
    const kids = (Array.isArray(p.props.children) ? p.props.children : [p.props.children]).filter(Boolean)
    const anims = kids.filter(k => k && k.type === 'animate')
    if (states[from].status === 'running') {
      assert.equal(anims.length, 1, `${p.key}: running source gets exactly one <animate>`)
      assert.equal(anims[0].props.attributeName, 'stroke-dashoffset')
    } else {
      assert.equal(anims.length, 0, `${p.key}: non-running source gets NO <animate>`)
    }
  }
}
{
  // all-terminal graph: zero animate children anywhere.
  const states = Object.fromEntries(nodes.map(n => [n.id, { status: 'done' }]))
  const svg = Edges({ nodes, rects: rectsFor(nodes), states, gate: null })
  const paths = svg.props.children.filter(x => x && x.type === 'path' && x.props.d)
  for (const p of paths) {
    const kids = (Array.isArray(p.props.children) ? p.props.children : [p.props.children]).filter(Boolean)
    assert.equal(kids.filter(k => k && k.type === 'animate').length, 0, `${p.key}: done source is still`)
  }
}

// -- 5. one fan-stack: the MiniGraph ghost-outline stack is deleted --------------
assert.equal(src.split("inset: '4px 0 0 4px'").length - 1, 0,
  "grep -c \"inset: '4px 0 0 4px'\" desktop/plugin.js must be 0 (FanStack is the only stack)")
assert.match(src, /function FanStack\(/, 'FanStack exists')
assert.match(src, /jsx\(FanStack, \{ count: \(items \?\? 1\) \+ 1, pill: true/,
  'MiniGraph pills reuse FanStack in pill mode')

// -- 6. deletions actually landed -------------------------------------------------
assert.doesNotMatch(src, /SIDEBAR_NAV_AREA/, 'sidebar nav import gone')
assert.doesNotMatch(src, /statusBar\.right/, 'statusbar chip registration gone')
assert.doesNotMatch(src, /function LiveChip\(/, 'LiveChip deleted')
assert.doesNotMatch(src, /function RunRow\(/, 'RunRow deleted')
assert.doesNotMatch(src, /w-60 shrink-0 flex-col border-r/, 'page runs column deleted')
// one global live count only: runningCount reads exclusively for the tab title.
const rcCalls = src.match(/runningCount\(/g).length
const rcDefs = src.match(/const runningCount =/g).length
assert.equal(rcCalls + rcDefs, 2, 'runningCount: definition + tabTitle call only')

console.log('ALL PASS: register surface, dock, NEEDS YOU grouping, SMIL-only-on-running, one fan-stack')
