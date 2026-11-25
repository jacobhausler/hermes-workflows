// Pin test: agent-first pane model with the FIVE-WAY fleet taxonomy
// (owner directive 2026-10-03; bd_2026-11-13-e7h, RC ch1). Law: the WORKFLOWS
// pane is a human EXPLORER's index, agent-forward. The All/Held/Interrupted/
// Running/Finished filters correspond 1:1 to identically named sections and
// All is their union, in held-first attention order; every row keeps its RAW
// status word; the index is uncapped and never wears "needs you" framing.
// Interrupted buckets failed, stopped, cancelled/skipped, partial and
// unknown-status work — a bucket, never a rewrite. The hygiene strip is a
// WINDOW census (Live/Done/Unowned + Asks decisions) computed from current
// state, bound to what the SDK can actually expose; cross-window ownership it
// cannot see renders as explicit unavailable, never a fabricated zero.
// Notices never become permissions. Pure functions, no DOM.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')
// stub-SDK pattern of test_register_surface: the plugin imports the SDK/react.
const tmp = mkdtempSync(join(tmpdir(), 'wf-pane-'))
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
export const useQuery = () => ({ data: undefined })
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
const { paneModel, originLabel, fleetSectionOf, applyFleetFilter, hygieneModel, askJumpAt } = mod

const run = (id, status, updated, owner = null, extra = {}) =>
  ({ id, status, updated, owner, name: id, ...extra })

// originLabel: every source of truth, in priority order, never invented.
assert.equal(originLabel({ session_id: '20260101_000000_fa11e1' }, 'alpha-bot'), 'alpha-bot',
  'resolved profile wins')
assert.equal(originLabel({ session_id: '20260101_000000_fa11e1' }, null), '20260101_000000_fa11e1',
  'session id fallback')
assert.equal(originLabel({ session_id: 'cron_95bb2ef2ef4d_20261002_191640' }, null), 'cron',
  'cron-shaped session')
assert.equal(originLabel({ platform: 'discord' }, null), 'discord',
  'platform run')
assert.equal(originLabel(null, null), 'unknown', 'absent owner is never fabricated')

// fleetSectionOf: the ONE membership law, exhaustive over every status the
// plugin vocabulary speaks. Only held/running/done leave the interrupted
// bucket; everything else (incl. unknown words) is interrupted work.
for (const [status, section] of [
  ['held', 'held'], ['running', 'running'], ['done', 'finished'],
  ['failed', 'interrupted'], ['stopped', 'interrupted'], ['interrupted', 'interrupted'],
  ['partial', 'interrupted'], ['cancelled', 'interrupted'], ['skipped', 'interrupted'],
  ['nonsense', 'interrupted'], [undefined, 'interrupted'], [null, 'interrupted']
]) assert.equal(fleetSectionOf(status), section, `${status} -> ${section}`)

// paneModel: every row lands in exactly one section; each section descends by
// last action (updated); `all` is the union in held-first attention order.
const now = Date.now()
const iso = min => new Date(now - min * 60000).toISOString()
const rows = [
  run('old-done', 'done', iso(5), { session_id: 's1' }),
  run('slow-run', 'running', iso(50), { session_id: 's2' }),
  run('fast-run', 'running', iso(1), { session_id: 's3' }),
  run('held-gate', 'held', iso(2), { session_id: 's1' }),
  run('held-newer', 'held', iso(9), { session_id: 's9' }),
  run('husk', 'pending', iso(3), { session_id: 's1' }),
  run('dead', 'failed', iso(10), { session_id: 's4' }),
  run('killed', 'stopped', iso(11), { session_id: 's4' }),
  run('capped', 'partial', iso(12), { session_id: 's5' }),
  run('rot-away', 'cancelled', iso(13), { session_id: 's6' }),
  run('smashed', 'interrupted', iso(14), { session_id: 's7' })
]
const m = paneModel(rows, { 's1': 'beta-bot', 's3': 'alpha-bot' })
assert.deepEqual(m.held.map(r => r.id), ['held-gate', 'held-newer'], 'held descends by last action')
assert.deepEqual(m.running.map(r => r.id), ['fast-run', 'slow-run'], 'running descends by last action')
assert.deepEqual(m.finished.map(r => r.id), ['old-done'], 'Finished is ONLY the clean done group')
assert.deepEqual(m.interrupted.map(r => r.id),
  ['dead', 'killed', 'capped', 'rot-away', 'smashed'],
  'Interrupted holds failed, stopped, partial, cancelled and interrupted together, updated desc')

// All is the UNION with held-first attention order (blocks, not a global resort).
assert.deepEqual(m.all.map(r => r.id),
  [...m.held, ...m.running, ...m.interrupted, ...m.finished].map(r => r.id),
  'all = held block, running block, interrupted block, finished block')
const ids = m.all.map(r => r.id)
assert.equal(new Set(ids).size, ids.length, 'no row appears twice in the union')
assert.equal(ids.length, m.counts.all, 'counts.all equals the rendered union length')
assert.equal(m.counts.all, m.held.length + m.running.length + m.interrupted.length + m.finished.length,
  'the four sections partition the index')
assert.equal(m.counts.all, rows.length - 1, 'every non-husk counted row is in a section — uncapped')
for (const r of m.all) {
  const orig = rows.find(x => x.id === r.id)
  assert.equal(r.status, orig.status, `${r.id}: the row keeps its RAW status word — a bucket never rewrites`)
}
assert.equal(m.all.find(r => r.id === 'husk'), undefined, 'never-started husks stay unrendered')
assert.deepEqual(applyFleetFilter(m, 'held').map(s => s.id), ['held'],
  'the Held filter shows exactly the Held section — 1:1, no re-derivation')
assert.deepEqual(applyFleetFilter(m, 'interrupted').map(s => s.id), ['interrupted'],
  'the Interrupted filter shows exactly the Interrupted section')
assert.deepEqual(applyFleetFilter(m, 'garbage').map(s => s.id), ['held', 'running', 'interrupted', 'finished'],
  'an unknown filter falls back to the union — no filter may silently hide counted work')
assert.deepEqual(applyFleetFilter(m, 'all').map(s => s.rows.length),
  [m.counts.held, m.counts.running, m.counts.interrupted, m.counts.finished],
  'the All union renders sections in held-first attention order')
assert.deepEqual(Object.fromEntries(m.all.map(r => [r.id, r.origin])),
  {
    'held-gate': 'beta-bot', 'held-newer': 's9', 'fast-run': 'alpha-bot', 'slow-run': 's2',
    'smashed': 's7', 'rot-away': 's6', 'capped': 's5', 'killed': 's4', 'dead': 's4', 'old-done': 'beta-bot'
  },
  'every row carries its resolved-or-fallback origin')

// Absent profiles map entirely: every row falls back honestly, nothing thrown.
const bare = paneModel(rows, null)
assert.equal(bare.running.length, 2)
assert.equal(bare.running[0].origin, 's3', 'unknown profile -> raw session id')
assert.equal(bare.held.find(r => r.id === 'held-gate').origin, 's1',
  'unresolved sessions fall back to the raw id, never a guess')

// Empty input is not a crash and not a lie.
const none = paneModel([], {})
assert.deepEqual(none.counts, { all: 0, held: 0, interrupted: 0, running: 0, finished: 0 })

// ---- hygiene strip: a WINDOW census + decisions, never a workflow census ----
const liveOwned = run('mine-live', 'running', iso(1), { session_id: 'chat-1' })
const heldOwned = run('mine-held', 'held', iso(2), { session_id: 'chat-1' }, { held_gate: { id: 'g1', question: 'ship?' } })
const doneOwned = run('mine-done', 'done', iso(3), { session_id: 'chat-2' })
const failedOwned = run('mine-fail', 'failed', iso(4), { session_id: 'chat-3' })
const foreign = run('elsewhere', 'held', iso(5), { session_id: 'chat-9' }, { held_gate: { id: 'g9', question: 'no?' } })
const noticeOnly = run('notice-row', 'failed', iso(6), { session_id: 'chat-8' })
const CENSUS = [liveOwned, heldOwned, doneOwned, failedOwned, foreign, noticeOnly]

// A census row that merely failed is a NOTICE: it carries no held_gate and
// must never inflate the ask census — notices never become permissions.
const h1 = hygieneModel(CENSUS, [liveOwned, heldOwned], { closed: [] })
assert.equal(h1.live, 1, 'focused chat owning live work is a LIVE window')
assert.equal(h1.done, 0)
assert.equal(h1.unowned, 0)
assert.equal(h1.asks, 2, 'Asks counts the two unresolved gate decisions ONLY — the failed notice rows are not asks')
assert.deepEqual(h1.askRuns.map(r => r.id), ['mine-held', 'elsewhere'], 'ask runs descend by last action')
assert.equal(h1.record.kind, 'live', 'live is read-only navigation — nothing silently closes a working window')
assert.equal(h1.record.shown, undefined, 'an open record is shown')

// Done vs Idle: clean finished work earns Done; a failure ending never does.
const h2 = hygieneModel(CENSUS, [doneOwned], { closed: [] })
assert.equal(h2.done, 1, 'a chat whose only runs ended clean reads Done')
const h2b = hygieneModel(CENSUS, [failedOwned], { closed: [] })
assert.equal(h2b.done, 0, 'a failed ending is NOT sold as Done')
assert.equal(h2b.idle, 1, 'it reads as an idle window instead')

// Resolved-but-empty ownership is the honest Unowned fact, closable.
const h3 = hygieneModel(CENSUS, [], { closed: [] })
assert.equal(h3.unowned, 1, 'a focused chat that owns no run is Unowned: no work owns this window')
assert.equal(h3.record.kind, 'unowned')

// Fail CLOSED on an unresolved focus: no ownership claim, no close affordance.
const h4 = hygieneModel(CENSUS, null, { closed: [] })
assert.equal(h4.unknown, true, 'an unreadable/rotated focused session claims nothing')
assert.equal(h4.record, null, 'no record — so no Close button can be pressed against an unknown')
assert.equal(h4.unowned, 0, 'unknown is NOT rendered as unowned — the census does not guess')
assert.equal(h4.asks, 2, 'Asks still answers from the census even when window state is unknown')

// No window roster is exposed by the SDK today -> explicit unavailable.
assert.equal(h1.rosterUnavailable, true, 'cross-window ownership is unavailable until the SDK exposes it')
assert.equal(hygieneModel(CENSUS, [], { roster: [] }).rosterUnavailable, false,
  'a roster (empty array) flips the unavailable mark — the binding is the SDK state, not a constant')

// Close removes ONLY the plugin-local record and leaves a receipt.
const h5 = hygieneModel(CENSUS, [], { closed: [{ recId: 'win:unowned', kind: 'unowned' }] })
assert.equal(h5.closed, true, 'the closed record is hidden')
assert.equal(h5.record.shown, false, 'and the receipt rides the record')
const h6 = hygieneModel(CENSUS, [liveOwned], { closed: [{ recId: 'win:unowned', kind: 'unowned' }] })
assert.equal(h6.closed, undefined,
  'the close applies to THAT record state only — new ownership re-surfaces the window honestly')

// ---- Asks jump: exact identity or nothing, rotating, fail-closed -----------
const jump = askJumpAt(h1.askRuns, 0)
assert.equal(jump.action.label, 'View exact gate', 'the jump is the gate lane identity law')
assert.equal(jump.next, 1)
mod.$selRun.set(null)
globalThis.__NAV = []
jump.action.onClick()
assert.equal(mod.$selRun.get(), 'mine-held', 'the click carries the EXACT ask identity, not the viewer selection')
assert.deepEqual(globalThis.__NAV, ['/workflows'], 'the route only selects the record page')
const jump2 = askJumpAt(h1.askRuns, 1)
mod.$selRun.set(null)
jump2.action.onClick()
assert.equal(mod.$selRun.get(), 'elsewhere', 'the cursor rotates to the next unresolved decision')
assert.equal(askJumpAt(h1.askRuns, 5).action.label, 'View exact gate', 'cursor math stays inside the asks')
assert.equal(askJumpAt([], 0).action, null, 'no unresolved decision — nothing to jump to')
const mangled = askJumpAt([run('bad', 'held', iso(1), { session_id: 's' }, { held_gate: { id: 'gate/1' } })], 0)
assert.equal(mangled.action, null, 'a malformed gate id fails CLOSED — no invented route (INERT law)')
assert.equal(mangled.next, 0, 'the cursor does not advance past an inert ask')
const noId = askJumpAt([run('bad2', 'held', iso(1), { session_id: 's' }, { held_gate: {} })], 0)
assert.equal(noId.action, null, 'a gate with no id at all fails CLOSED')

console.log('pane model pins: OK (five-way taxonomy + hygiene + asks jump)')
