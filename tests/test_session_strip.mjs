// L1 acceptance (O1 desktop): ownedRuns keeps only the focused chat's runs and
// returns [] for an empty key; splitRuns caps active at 3 (held first) with an
// overflow count (THE shared liveOrder comparator; the cap-5 terminal fold is
// deleted — collectionModel owns the terminal half); the pill model is collapsed
// by default and its collapsed line carries name/status/progress. Pure-model
// asserts only: there is no DOM under node --experimental-strip-types.
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
// The SDK exposes the focused-chat atoms ONLY under host.state (sdk/index.ts
// stubs them there; a top-level stub encoded bug #23 and kept the suite green
// while the strip never rendered).
export const host = { state: { focusedStoredSessionId: atom(''), focusedSessionId: atom('') }, navigate: () => {} }
export const q = { data: undefined }
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
export const useQuery = () => ({ data: q.data })
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const Tip = 'Tip'
export const SIDEBAR_NAV_AREA = 'sidebar.nav', STATUSBAR_AREAS = { left: 'statusBar.left', right: 'statusBar.right' }
export const useMutation = () => ({})
export const useQueryClient = () => ({})
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


const { ownedRuns, splitRuns, pillModel, SessionStrip } = mod
assert.equal(typeof SessionStrip, 'function', 'SessionStrip is exported for L3 to register in composer.top')

// -- 1. ownedRuns ---------------------------------------------------------------
const mk = (id, status, sid, started, updated, extra = {}) => ({ id, name: id, status, owner: { session_id: sid }, started, updated, ...extra })
const runs = [
  mk('a', 'running', 'S1', '2026-09-26T04:00:00Z', '2026-09-26T04:05:00Z', { nodes_done: 3, nodes_total: 6 }),
  mk('b', 'held',    'S1', '2026-09-26T04:01:00Z', '2026-09-26T04:06:00Z'),
  mk('c', 'running', 'S2', '2026-09-26T04:02:00Z', '2026-09-26T04:07:00Z'),
  mk('d', 'done',    'S1', '2026-09-26T03:00:00Z', '2026-09-26T03:30:00Z'),
  mk('e', 'failed',  'S1', '2026-09-26T03:10:00Z', '2026-09-26T03:40:00Z'),
  mk('f', 'running', '',   '2026-09-26T04:03:00Z', '2026-09-26T04:08:00Z'),   // cron launch, no owner
]
assert.deepEqual(ownedRuns(runs, '').map(r => r.id), [], 'empty sid owns nothing (cron launches show only in the pane)')
assert.deepEqual(ownedRuns(runs, 'S1').map(r => r.id).sort(), ['a', 'b', 'd', 'e'], 'only owner.session_id===sid')
assert.deepEqual(ownedRuns(runs, 'S2').map(r => r.id), ['c'])
assert.deepEqual(ownedRuns(null, 'S1'), [], 'null list is []')

// -- 2. splitRuns: held first, active<=3 + overflow (NO terminal fields left) ----
// The W3 collection law: splitRuns speaks only the live half; the cap-5
// terminal fold is deleted with no compat shim, and collectionModel owns the
// terminal half (see -- 2b).
const many = [
  mk('r1', 'running', 'S', '2026-09-26T04:00:00Z', '2026-09-26T04:00:00Z'),
  mk('r2', 'running', 'S', '2026-09-26T04:03:00Z', '2026-09-26T04:00:00Z'),
  mk('h1', 'held',    'S', '2026-09-26T03:50:00Z', '2026-09-26T04:00:00Z'),
  mk('r3', 'pending', 'S', '2026-09-26T04:02:00Z', '2026-09-26T04:00:00Z'),
  mk('r4', 'running', 'S', '2026-09-26T04:01:00Z', '2026-09-26T04:00:00Z'),
  ...['t1','t2','t3','t4','t5','t6','t7'].map((id, i) => mk(id, i % 2 ? 'done' : 'failed', 'S', '2026-09-26T02:00:00Z', `2026-09-26T03:0${i}:00Z`)),
]
const s = splitRuns(many)
assert.equal(s.active.length, 3, 'active capped at 3')
assert.equal(s.active[0].id, 'h1', 'held run sorts first')
assert.deepEqual(s.active.slice(1).map(r => r.id), ['r2', 'r3'], 'then running/pending by started desc')
assert.equal(s.overflow, 2, 'overflow counts the active runs beyond 3')
assert.ok(!('terminalFold' in s) && !('terminalTotal' in s),
  'the cap-5 terminal fold fields are GONE (superseded, no compat shim)')
const empty = splitRuns([])
assert.deepEqual([empty.active, empty.overflow], [[], 0])

// -- 2b. collectionModel: attention-first, clean-finished fold >6 ------------------
// (INCHAT:111-112, 136 — failures partition out before the finished label;
// six visible, seven folded; full counted list reachable.)
const cm = mod.collectionModel(many)
assert.equal(cm.finishedTotal, 3, "'finished' counts ONLY clean done (t2,t4,t6) — failures are attention, not finished")
assert.equal(cm.attentionTotal, 4, 'failed runs are attention rows (t1,t3,t5,t7)')
assert.deepEqual(cm.attention.map(r => r.id), ['t7', 't5', 't3', 't1'], 'attention sorts updated DESC (same tie law)')
assert.equal(cm.finishedFolded, false, '3 clean finished do NOT engage the fold (strictly greater than six)')
assert.equal(mod.CLEAN_FOLD_MAX, 6, 'the fold boundary is the named six-row constant')
const mkDone = i => mk(`d${i}`, 'done', 'S', '2026-09-26T02:00:00Z', `2026-09-26T03:${String(i).padStart(2, '0')}:00Z`)
const six = [...Array(6)].map((_, i) => mkDone(i + 1))
const cm6 = mod.collectionModel(six)
assert.equal(cm6.finishedTotal, 6, 'six clean finished')
assert.equal(cm6.finishedFolded, false, 'EXACTLY six visible — the fold condition is strictly greater than six')
const cm7 = mod.collectionModel([...six, mkDone(7)])
assert.equal(cm7.finishedFolded, true, 'SEVEN clean finished — the fold engages (seven folded)')
const cm17 = mod.collectionModel([...Array(17)].map((_, i) => mkDone(i + 1)))
assert.equal(cm17.finishedTotal, 17, 'the seventeen-row specimen counts all clean finished')
assert.deepEqual(cm17.finished.map(r => r.id).slice(0, 3), ['d17', 'd16', 'd15'], 'folded list still updated DESC — every counted row present (full counted list, no cap, no hidden rows)')
assert.equal(cm17.finished.length, 17, 'the model enumerates ALL 17 — reachability is the render side, the model never truncates')
// attention > 3 is a required specimen: the collection is NOT capped to three records.
const manyFail = [...Array(4)].map((_, i) => mk(`f${i}`, 'failed', 'S', '2026-09-26T02:00:00Z', `2026-09-26T03:0${i}:00Z`))
assert.deepEqual(mod.collectionModel(manyFail).attention.map(r => r.id), ['f3', 'f2', 'f1', 'f0'],
  'more than three attention rows: all enumerated, none hidden')
assert.equal(mod.collectionModel(manyFail).finishedTotal, 0, 'failures never count into finished')
// documented tie law on the terminal half: equal updated keeps INPUT order,
// unparseable updated sorts LAST (never interleaved at random).
const ties = mod.collectionModel([
  mk('ta', 'done', 'S', 'x', '2026-09-26T04:00:00Z'),
  mk('tb', 'done', 'S', 'x', '2026-09-26T04:00:00Z'),
  mk('tz', 'done', 'S', 'x', 'not-a-date'),
  mk('tw', 'done', 'S', 'x', '2026-09-26T05:00:00Z'),
])
assert.deepEqual(ties.finished.map(r => r.id), ['tw', 'ta', 'tb', 'tz'],
  'terminal tie law: updated desc, equal keeps input order, unparseable LAST')
assert.deepEqual(mod.collectionModel(null).finished, [], 'null ledger is a clean empty')

// -- 3. pillModel: collapsed by default, one line ---------------------------------
const pm = pillModel(runs[0])
assert.equal(pm.expanded, false, 'pill renders collapsed by default')
assert.equal(typeof pm.collapsedLine, 'string')
assert.ok(pm.collapsedLine.includes('a'), 'collapsed line names the run')
assert.ok(!pm.collapsedLine.includes('\n'), 'collapsed line is one line')
const pmUnknown = pillModel({})
assert.ok(pmUnknown.collapsedLine.length > 0, 'an empty record still renders a line, never throws')

// -- 4. the whole-card navigate is gone: DirectiveBody has no role=link ----------
assert.ok(!/role:\s*'link'/.test(src.slice(src.indexOf('function DirectiveBody'), src.indexOf('function DirectiveBody') + 4000)),
  'DirectiveBody must not keep the whole-card role=link navigate (one click cannot both expand and navigate)')

// -- 5. KEY PAIRING lock (measured): owner.session_id is the runtime id, so it
// pairs with host.state.focusedSessionId ($focusedRuntimeId, sdk index.ts:668);
// owner.ui_session_id pairs with host.state.focusedStoredSessionId. A swapped pair
// renders nothing forever — assert the source wires them same-shape.
const stripSrc = src.slice(src.indexOf('export function SessionStrip'), src.indexOf('export function SessionStrip') + 1200)
assert.ok(/const runtimeSid = useValue\(focusAtom\(host\?\.state\?\.focusedSessionId\)\)/.test(stripSrc),
  'owner.session_id (runtime shape) must pair with host.state.focusedSessionId (feature-detected)')
assert.ok(/ownedRuns\(data\?\.runs \|\| \[\], runtimeSid \|\| ''\, storedSid \|\| ''\)/.test(stripSrc),
  'ownedRuns args must be (runtime, stored), never (stored, runtime)')

// -- 6. RED ON BASE (bug #23): the SDK exposes the focused-chat atoms ONLY under
// host.state (sdk/index.ts:665-697). With the stub atoms under host.state and an
// owning sid in host.state.focusedStoredSessionId, SessionStrip() must render a
// tree — on base it reads host.focusedSessionId, sees undefined, and returns null
// forever. And with a focused chat that owns no run it must return null.
const sdkMod = await import(pathToFileURL(sdkPath).href)
{
  const ownedByStored = [
    { id: 'u1', name: 'u1', status: 'running', owner: { session_id: '', ui_session_id: 'STORED-1' }, started: '2026-09-26T04:00:00Z', updated: '2026-09-26T04:05:00Z' },
    { id: 'u2', name: 'u2', status: 'done', owner: { session_id: 'OTHER' }, started: '2026-09-26T03:00:00Z', updated: '2026-09-26T03:30:00Z' },
  ]
  sdkMod.q.data = { runs: ownedByStored }
  sdkMod.host.state.focusedStoredSessionId.set('STORED-1')
  const tree = mod.SessionStrip()
  assert.ok(tree && typeof tree === 'object',
    'SessionStrip must render a tree when host.state.focusedStoredSessionId owns a run (was null on base — the atoms are only under host.state)')
  // null when the focused chat owns nothing
  sdkMod.host.state.focusedStoredSessionId.set('NOBODY')
  assert.equal(mod.SessionStrip(), null, 'no owned run -> null (honest absence)')
  // null when there is no focused chat at all
  sdkMod.host.state.focusedStoredSessionId.set('')
  assert.equal(mod.SessionStrip(), null, 'no focused sid -> null')
}

rmSync(tmp, { recursive: true, force: true })
console.log('ALL PASS test_session_strip (ownedRuns, splitRuns, pillModel, SessionStrip export, no whole-card link, host.state atoms render)')
