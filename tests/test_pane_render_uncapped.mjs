// Render-level pins for the fleet landing (deep review #156 A4 +
// bd_2026-11-13-e7h). The pane's uncapped law lives in the CONSUMER: the old
// slice(0,10)+show-all fold made "no caps on foreign runs" a lie, so this
// harness mounts the ACTUAL pane component and walks the emitted tree at
// >100 foreign rows. Law (e7h): every non-husk row renders as a PaneRow under
// exactly one of the five named section labels; All is the union and shows
// them ALL — no cap, no fold, no show-all affordance at any count. The census
// sentence carries ONLY workflow counts; the hygiene strip is its own row and
// carries ONLY window/decision counts — and with an unresolved focus (both
// focused ids empty — the missing/rotated-id shape) it must fail CLOSED to
// 'unknown' with NO Close affordance and NO unowned claim. Selection state is
// a data-selected attribute, not a hover style, and every row carries its
// 44x44 open-arrow control. Geometry (44x44 at the tablet bands) is proven by
// the real-app capture (tests/proof-harness --case fleet), not by string here.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// The pane reads data via useQuery(listQuery()); the stub answers with a full
// census of 109 non-husk rows + one pending husk — >100 is the point (the
// paged walk's first page stops at 100; the ancient fold stopped at 10).
const now = Date.now()
const iso = min => new Date(now - min * 60000).toISOString()
const run = (id, status, extra = {}) => ({ id, status, updated: iso(3), name: id,
  owner: { session_id: `20260101_000000_${id}` }, ...extra })
const many = (n, status, tag) => Array.from({ length: n }, (_, i) => run(`${tag}-${i}`, status))
const FLEET = [
  run('run-a', 'running'), run('run-b', 'running'),
  run('held-q1', 'held', { held_gate: { id: 'gate-q1', question: 'ship it?' } }),
  run('held-q2', 'held', { held_gate: { id: 'gate/q2', question: 'malformed id — inert' } }),
  ...many(40, 'done', 'done'),
  ...many(20, 'failed', 'fail'),
  ...many(10, 'stopped', 'stop'),
  ...many(15, 'interrupted', 'brk'),
  ...many(10, 'partial', 'cap'),
  ...many(10, 'cancelled', 'cxl'),
  run('husk', 'pending')
]
// 2 running + 2 held + 40 done + 65 interrupted-bucket = 109 rendered rows.
const CENSUS_DATA = {
  runs: FLEET,
  total: 109,
  counts: { running: 2, held: 2, failed: 20 }
}

const tmp = mkdtempSync(join(tmpdir(), 'wf-render-'))
const jsxPath = join(tmp, 'jsx-stub.mjs')
writeFileSync(jsxPath, `
export const jsx = (type, props, key) => ({ type, props: props || {}, key })
export const jsxs = jsx
export const Fragment = 'Fragment'
`)
const reactPath = join(tmp, 'react-stub.mjs')
writeFileSync(reactPath, `
export const useEffect = () => {}, useId = () => 't-0', useRef = () => ({ current: null }), useState = i => [typeof i === 'function' ? i() : i, () => {}]
export default { useEffect, useId, useRef, useState }
`)
const sdkPath = join(tmp, 'sdk-stub.mjs')
writeFileSync(sdkPath, `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const atom0 = atom
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const host = { state: { focusedStoredSessionId: atom(''), focusedSessionId: atom('') }, navigate: p => { (globalThis.__NAV ||= []).push(p) } }
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
export const useQuery = () => ({ data: ${JSON.stringify(CENSUS_DATA)} })
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const useMutation = () => ({})
export const useQueryClient = () => ({})
`)
const modPath = join(tmp, 'plugin-under-test.mjs')
writeFileSync(modPath, src
  .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
  .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href))
  .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href)))
const mod = await import(pathToFileURL(modPath).href)

const tree = mod.WorkflowsPane()
const texts = []
const walk = (node, fn) => {
  if (node == null) return
  if (Array.isArray(node)) return node.forEach(n => walk(n, fn))
  if (typeof node === 'string') { texts.push(node); fn(node); return }
  if (typeof node !== 'object') return
  fn(node)
  walk(node.props?.children, fn)
  walk(node.props?.title, fn)   // PanelListRow carries its cells in props, not children
  walk(node.props?.meta, fn)
  walk(node.props?.lead, fn)
}
const rows = []
const labels = []
const pills = []
const hyg = []
const arrows = []
let closeBtn = 0, showAll = 0, asksBtn = null
walk(tree, el => {
  const t = el.type
  if (typeof t === 'function' && t.name === 'PaneRow') rows.push(el)
  if (t === 'PanelSectionLabel') labels.push(String(el.props.children))
  if (t === 'Button' && /show all/i.test(String(el.props?.children))) showAll++
  if (t === 'button') {
    if (el.props?.className === 'wf-pill') pills.push(el)
    if (/wf-hyg-close/.test(String(el.props?.className || ''))) closeBtn++
    if (el.props?.className === 'wf-row-open') arrows.push(el)
    if (String(el.props?.children || '').startsWith('Asks')) asksBtn = el
  }
  if (t === 'span' && el.props?.['data-hyg']) hyg.push([el.props['data-hyg'], String(el.props.children)])
  if (typeof el.props?.children === 'string') texts.push(el.props.children)
})

// (1) The WHOLE census renders, uncapped, five-way labels, one section each.
assert.equal(rows.length, 109, `every non-husk row renders — saw ${rows.length}`)
for (const want of ['Held · 2', 'Running · 2', 'Interrupted · 65', 'Finished · 40'])
  assert.ok(labels.includes(want), `section label present: ${want} (saw ${labels.join(' | ')})`)
assert.ok(!labels.some(l => /RUNNING|THE REST/.test(l)), 'RUNNING/THE REST headings are replaced')
const keys = rows.map(r => r.key)
for (const r of FLEET.filter(r => r.status !== 'pending'))
  assert.equal(keys.filter(k => k === r.id).length, 1, `${r.id} exactly once — a partition, not a duplication`)
assert.ok(!keys.includes('husk'), 'the pending husk renders nowhere — no section, no union')
assert.equal(showAll, 0, 'no show-all affordance may exist at any count')

// (2) Filter pills: five, named, 1:1 with sections; All selected; selection is
// the data-selected attribute (distinct from any hover style — hover is CSS).
assert.equal(pills.length, 5, 'All/Held/Interrupted/Running/Finished pills')
assert.deepEqual(pills.map(p => String(p.props.children).split(' ')[0]),
  ['All', 'Held', 'Interrupted', 'Running', 'Finished'])
assert.equal(pills.filter(p => p.props['data-selected'] === 'true').length, 1,
  'exactly one pill is selected (the user selection, never inferred from hover)')
assert.equal(pills[0].props['data-selected'], 'true', 'the default is the union')
assert.equal(pills[0].props['aria-pressed'], true)

// (3) Workflow counts and window counts NEVER share a sentence.
const censusLine = texts.find(t => t.startsWith('runs 109'))
assert.ok(censusLine, 'census line present')
assert.ok(!/live|unowned|asks/i.test(censusLine),
  `census sentence carries workflow counts only: ${censusLine}`)

// (4) Hygiene strip: unresolved focus (both ids empty — missing/rotated) fails
// CLOSED to unknown: no unowned claim, no Close affordance, Asks still answer.
const h = Object.fromEntries(hyg)
assert.equal(h.live, 'Live 0')
assert.equal(h.done, 'Done 0')
assert.equal(h.unowned, 'Unowned 0', 'unknown focus is NOT rendered as unowned — no fabricated census')
assert.equal(h.unknown, '· window: unknown (session unresolved)')
assert.equal(closeBtn, 0, 'fail-closed: no Close window affordance against an unknown ownership')
assert.ok(texts.includes('· other windows: unavailable'),
  'no SDK window roster -> explicit unavailable')

// (5) Asks: the two held-gate rows are unresolved decisions. The first jump
// carries the EXACT identity; when the cursor reaches the malformed gate id
// the jump goes INERT — a broken sibling never disables the strip, and the
// count never lies.
assert.equal(asksBtn.props.children, 'Asks 2')
assert.equal(asksBtn.props.disabled, false, 'a resolvable ask keeps the jump live')
mod.$selRun.set(null)
globalThis.__NAV = []
asksBtn.props.onClick()                                  // -> gate-q1 (exact)
assert.equal(mod.$selRun.get(), 'held-q1', 'the jump selects the exact ask run, not the viewer selection')
assert.deepEqual(globalThis.__NAV, ['/workflows'], 'the route only selects the record page')
// Re-render (the cursor moved): the next ask is the malformed one — its jump
// is INERT and must not touch selection or the router.
const tree2 = mod.WorkflowsPane()
let asksBtn2 = null
walk(tree2, el => { if (el.type === 'button' && String(el.props?.children || '').startsWith('Asks')) asksBtn2 = el })
asksBtn2.props.onClick()
assert.equal(mod.$selRun.get(), 'held-q1',
  'the malformed ask is INERT (no invented route) and did not clobber the last good selection')
assert.deepEqual(globalThis.__NAV, ['/workflows'], 'the inert click never reached the router')

// (6) Every row carries its open-arrow control: invoke the actual PaneRow
// component per row and walk ITS subtree (the 44x44 geometry itself is
// measured on the real app by the fleet proof case).
let arrowCount = 0, inertFact = 0
for (const el of rows) {
  walk(el.type({ run: el.props.run, thisChat: el.props.thisChat }), n => {
    if (n.type === 'button' && n.props?.className === 'wf-row-open') arrowCount++
    if (typeof n === 'string' && /^interrupted · /.test(n)) inertFact++
  })
}
assert.equal(arrowCount, 109, 'every rendered row has its own open control')
assert.ok(inertFact >= 15, 'interrupted rows keep their raw fact line')

// (7) Resolved focus -> the strip DOES make ownership claims, and Close
// window is a plugin-local record round trip: record -> receipt -> gone,
// never the chat, never conversation history. A different window state is a
// different record — the old receipt does not silence it.
const sdkMod = await import(pathToFileURL(sdkPath).href)
const hygOf = t => {
  const out = { texts: [], close: null }
  walk(t, el => {
    if (typeof el === 'string') out.texts.push(el)
    if (typeof el === 'object' && typeof el.props?.children === 'string') out.texts.push(el.props.children)
    if (el.type === 'button' && /wf-hyg-close/.test(String(el.props?.className))) out.close = el
  })
  out.has = s => out.texts.includes(s)
  return out
}
sdkMod.host.state.focusedSessionId.set('20260101_000000_fail-0')  // owns one FAILED run
const g3 = hygOf(mod.WorkflowsPane())
assert.ok(!g3.has('· window: unknown (session unresolved)'), 'a resolved focus lifts the unknown costume')
assert.ok(g3.has('· Idle window · work ended here'), 'failed ending reads Idle, never sold as Done')
assert.ok(g3.close, 'Idle exposes an explicit Close window')
g3.close.props.onClick()
const g4 = hygOf(mod.WorkflowsPane())
assert.ok(g4.has('· closed · conversation kept'), 'Close leaves a visible receipt')
assert.ok(!g4.has('· Idle window · work ended here') && !g4.close,
  'the closed record is gone — plugin-local state only')
assert.ok(g4.has('Unowned 0') && g4.has('Done 0'), 'counts recomputed after close: nothing left to claim')
sdkMod.host.state.focusedSessionId.set('chat-none')               // resolved, owns NOTHING
const g5 = hygOf(mod.WorkflowsPane())
assert.ok(g5.has('Unowned 1'), 'a different window state is a fresh record')
assert.ok(g5.has('· No work owns this window') && g5.close,
  'the earlier receipt does not silence the new unowned window')
g5.close.props.onClick()
const g6 = hygOf(mod.WorkflowsPane())
assert.ok(g6.has('Unowned 0') && g6.has('· closed · conversation kept'),
  'Unowned 1 -> Close -> 0, receipt shown — the doctrine cleanup loop, no conversation touched')

console.log('OK — pane renders all 109 foreign rows across five sections, uncapped, hygiene fail-closed')
