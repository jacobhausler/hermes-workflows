/*
 * test_ui2_motion.mjs — behavior tests for the ONE shared motion allocator
 * and the registered token engine (ship 2.0 W4, bd_2026-11-13-32i).
 *
 * Pinned laws (DESIGN Round 10 "motion is data", FINAL.md Motion-and-budget):
 *  - ONE global pool for graph AND collection: active + reserved <= 12 at
 *    every request, update, cancellation and settle. Counting targets, never
 *    CSS declarations.
 *  - Priority transition > attention > running glyph > edge; ties order by
 *    event timestamp then stable ID; higher priorities PREEMPT lower ones;
 *    every rejection spills to the truthful static state IMMEDIATELY.
 *  - Only DESIGN's fifteen dur/ease tokens are registered; a 0ms token is a
 *    no-animation admission; phase derives from the ORIGINAL event timestamp
 *    (remount/re-admission continuity), missing/invalid/future is unknown.
 *  - One-shots consume once per event identity, never per render.
 *  - Insertion may reserve <=30ms between arrivals, <=90ms total, inside the
 *    same N=12 budget; excess spills to static.
 *  - The reduced preference flips to ZERO effects and reservations (settled
 *    static states at full opacity, never paused low-opacity frames).
 *  - The hoisted <style> is emitted ONCE and its identity is the content
 *    digest of the FULL emitted bytes (replaces the version-counter bump).
 */
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

const stubSdk = `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const atom0 = atom
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const atoms = { focusedSessionId: atom(''), focusedStoredSessionId: atom('') }
export const host = { state: atoms, navigate: () => {}, notify: () => {} }
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const Tip = 'Tip'
export const SIDEBAR_NAV_AREA = 'sidebar.nav', STATUSBAR_AREAS = { left: 'statusBar.left', right: 'statusBar.right' }
export const queries = { list: { runs: [] }, run: null }
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQuery = () => ({ data: queries.list, error: null })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
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
const tmp = mkdtempSync(join(tmpdir(), 'wf-motion32i-'))
writeFileSync(join(tmp, 'sdk.mjs'), stubSdk)
writeFileSync(join(tmp, 'react.mjs'), stubReact)
writeFileSync(join(tmp, 'jsx.mjs'), stubJsx)
// every loadMint() gets its OWN module instance — its own MOTION singleton,
// so pool state cannot leak across behavior sections.
let mint = 0
async function loadMint () {
  const p = join(tmp, `plugin-${++mint}.mjs`)
  writeFileSync(p, src
    .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(join(tmp, 'sdk.mjs')).href))
    .replaceAll("'react'", JSON.stringify(pathToFileURL(join(tmp, 'react.mjs')).href))
    .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(join(tmp, 'jsx.mjs')).href)))
  return await import(pathToFileURL(p).href)
}
const mod = await loadMint()

// fake clock the tests advance by hand — no wall sleeps, fully deterministic
const tick = { now: 100_000 }
const alloc = () => mod.createMotionAllocator({ clock: () => tick.now })

// =================================================================================
// 1. The token table is EXACTLY the fifteen DESIGN dur/ease tokens
// =================================================================================
{
  const EXPECT = {
    '--dur-pulse-fresh': '2000ms', '--dur-pulse-quiet': '4000ms', '--dur-flow': '1200ms',
    '--dur-attention': '4000ms', '--dur-failed': '320ms', '--dur-done': '240ms',
    '--dur-insert': '240ms', '--dur-collapse': '240ms', '--dur-expand': '0ms',
    '--dur-progress': '0ms', '--ease-breathe': 'cubic-bezier(.4,0,.6,1)',
    '--ease-flow': 'linear', '--ease-settle': 'cubic-bezier(.16,1,.3,1)',
    '--ease-step': 'steps(1,end)', '--ease-expand': 'linear'
  }
  assert.deepEqual(mod.MOTION_TOKENS, EXPECT, 'MOTION_TOKENS is the DESIGN Round 10 table, verbatim (15 rows, no extras)')
  assert.equal(Object.keys(mod.MOTION_TOKENS).length, 15, 'exactly fifteen registered dur/ease tokens')
  assert.deepEqual(mod.MOTION_PRIORITY, ['transition', 'attention', 'glyph', 'edge'],
    'priority order is transition > attention > running glyph > edge')
  assert.equal(mod.MOTION_CAP, 12, 'N=12 is the hard concurrent budget')
  assert.equal(mod.MOTION_INSERT_GAP_MS, 30, 'insertion gap ceiling 30ms')
  assert.equal(mod.MOTION_INSERT_TOTAL_MS, 90, 'insertion total-delay ceiling 90ms')
}

// =================================================================================
// 2. The cap is global: mixed-class flood admits exactly 12, denies 52 to
//    immediate static spill — and the pool NEVER exceeds 12 across the
//    graph+collection mix (DESIGN's 64-request reference measurement).
// =================================================================================
{
  const A = alloc()
  const results = []
  for (let i = 0; i < 64; i++) {
    results.push(A.claim({ id: `n${String(i).padStart(2, '0')}`, cls: 'attention', ts: tick.now - 10, durToken: '--dur-attention' }))
  }
  const s = A.stats()
  assert.equal(s.total, 12, '64 requests -> the pool holds exactly 12 (N=12 hard cap)')
  assert.equal(results.filter(r => r.admitted).length, 12, 'twelve admissions counted per-request')
  assert.equal(results.filter(r => !r.admitted).length, 52, 'fifty-two denials — DESIGN\'s reference 12/52')
  assert.deepEqual(s.holders.map(h => h.id),
    ['n00', 'n01', 'n02', 'n03', 'n04', 'n05', 'n06', 'n07', 'n08', 'n09', 'n10', 'n11'],
    'same class + same timestamp: the twelve stable-smallest IDs hold, no preemption churn inside a tie')
  assert.ok(results.every(r => r.admitted || (r.spill === 'static' && r.reason === 'cap')),
    'every cap-denied effect spills to static immediately (never queued)')
  // a denial that later re-claims after a release IS admitted (no expiry queue)
  const held = s.holders[0]
  assert.equal(A.release({ id: held.id, gen: held.gen }), true, 'release of the current generation works')
  const re = A.claim({ id: held.id, cls: 'attention', ts: tick.now - 10, durToken: '--dur-attention' })
  assert.equal(re.admitted, true, 'a spilled effect re-admits when a slot opens (spill is not a ban)')
}

// =================================================================================
// 3. Priority + preemption: a transition evicts the weakest holder; ties
//    order by timestamp then stable ID; equal-class newcomers only steal
//    from OLDER events.
// =================================================================================
{
  const A = alloc()
  const T = { transition: '--dur-collapse', attention: '--dur-attention', glyph: '--dur-pulse-fresh', edge: '--dur-flow' }
  for (const e of ['e01', 'e02', 'e03']) A.claim({ id: e, cls: 'edge', ts: 1000, durToken: T.edge })
  for (const g of ['g01', 'g02', 'g03', 'g04', 'g05', 'g06']) A.claim({ id: g, cls: 'glyph', ts: 1000, durToken: T.glyph })
  for (const t of ['tr01', 'tr02', 'tr03']) A.claim({ id: t, cls: 'transition', ts: 1000, durToken: T.transition })
  assert.equal(A.stats().total, 12, 'pool exactly full with one transition-free mix')
  const a1 = A.claim({ id: 'att1', cls: 'attention', ts: 1000, durToken: T.attention })
  assert.equal(a1.admitted, true, 'attention preempts the lowest class')
  let s = A.stats()
  assert.equal(s.holders.filter(h => h.cls === 'edge').length, 2, 'the victim came from the LOWEST class (one edge gone)')
  assert.ok(!s.holders.some(h => h.id === 'e03'), 'the last-stable-ID edge lost its slot')
  assert.equal(s.counters.preempted, 1, 'preemption instrumented')
  const a2 = A.claim({ id: 'att2', cls: 'attention', ts: 1000, durToken: T.attention })
  assert.equal(a2.admitted, true, '...and it repeats deterministically')
  assert.ok(!A.stats().holders.some(h => h.id === 'e02'), 'the next-oldest edge fell (id order inside the tie)')
  // Same-class same-timestamp contention obeys the stable ID: a LARGER id
  // cannot evict a smaller one; a SMALLER id can.
  const worse = A.claim({ id: 'e04', cls: 'edge', ts: 1000, durToken: T.edge })
  assert.equal(worse.admitted, false, 'a same-class claim with a larger stable ID does not preempt (ties order by ID)')
  const better = A.claim({ id: 'e00', cls: 'edge', ts: 1000, durToken: T.edge })
  assert.equal(better.admitted, true, 'a same-class claim with the smallest stable ID DOES win the slot')
  assert.ok(!A.stats().holders.some(h => h.id === 'e01'), 'the lowest-ranked edge yielded to the smaller ID')

  // Same-class contention by EVENT TIMESTAMP: a NEWER event steals; an OLDER
  // event loses outright.
  const B = alloc()
  for (let i = 1; i <= 12; i++) B.claim({ id: `s${String(i).padStart(2, '0')}`, cls: 'attention', ts: 5000, durToken: T.attention })
  const old = B.claim({ id: 's99', cls: 'attention', ts: 4000, durToken: T.attention })
  assert.equal(old.admitted, false, 'an older same-class event cannot steal a slot')
  const newer = B.claim({ id: 's98', cls: 'attention', ts: 9000, durToken: T.attention })
  assert.equal(newer.admitted, true, 'a newer same-class event steals the weakest slot')
  assert.ok(!B.stats().holders.some(h => h.id === 's12' && h.ts === 5000), 'the oldest/last tie lost, not the newer')

  // Stable-ID tie: with identical class AND identical timestamp the lower id
  // wins deterministically, whatever the arrival order.
  const C = alloc()
  for (const id of ['k01', 'k02', 'k03', 'k04', 'k05', 'k06', 'k07', 'k08', 'k09', 'k10', 'k11', 'k12', 'k13', 'k14']) {
    C.claim({ id, cls: 'attention', ts: 7000, durToken: T.attention })
  }
  assert.deepEqual(C.stats().holders.map(h => h.id).sort(),
    ['k01', 'k02', 'k03', 'k04', 'k05', 'k06', 'k07', 'k08', 'k09', 'k10', 'k11', 'k12'],
    'equal class + equal timestamp -> the twelve stable-smallest IDs hold the pool')
}

// =================================================================================
// 4. Original-timestamp phase: remount, release/re-admission and redraw
//    cannot restart or shift the cycle; the negative delay advances with
//    wall time from the ORIGINAL event.
// =================================================================================
{
  const A = alloc()
  const ts = tick.now - 10_000 // held 10s ago; --dur-attention = 4000ms
  const r1 = A.claim({ id: 'hold', cls: 'attention', ts, durToken: '--dur-attention' })
  assert.equal(r1.admitted, true)
  assert.equal(r1.phaseMs, -(10_000 % 4000), 'phase = -(elapsed mod dur) — anchored to the event, not the mount')
  tick.now += 1000
  const r2 = A.claim({ id: 'hold', cls: 'attention', ts, durToken: '--dur-attention' }) // redraw
  assert.equal(r2.phaseMs, -(11_000 % 4000), 'a redraw continues the same cycle (no restart)')
  A.release(r1.token)
  const r3 = A.claim({ id: 'hold', cls: 'attention', ts, durToken: '--dur-attention' }) // remount re-admission
  assert.equal(r3.admitted, true)
  assert.equal(r3.phaseMs, -(11_000 % 4000), 're-admission to the budget retains the timestamp phase (DESIGN law)')
  // idempotent re-claim never double-counts
  const before = A.stats()
  A.claim({ id: 'hold', cls: 'attention', ts, durToken: '--dur-attention' })
  assert.equal(A.stats().total, before.total, 're-claiming a held id consumes no extra slot')
  assert.equal(A.stats().counters.admitted, before.counters.admitted, 'idempotent re-claims do not recount admissions')
}

// =================================================================================
// 5. Unknown timestamps: missing, invalid and FUTURE times claim no recency
//    cue — the cycle opens at its head instead of fabricating one. The
//    running-glyph recency helper says `unknown` rather than guessing.
// =================================================================================
{
  const A = alloc()
  for (const [label, ts] of [['missing', null], ['invalid', Number.NaN], ['string', 'yesterday'], ['future', tick.now + 60_000]]) {
    const r = A.claim({ id: label, cls: 'attention', ts, durToken: '--dur-attention' })
    assert.equal(r.admitted, true, `${label}: the state effect is still admitted`)
    assert.equal(r.phaseMs, 0, `${label}: unknown time opens the cycle at its head, never a fabricated recency`)
    assert.equal(r.unknownTs, true, `${label}: the claim is stamped unknown-timestamp`)
  }
  const G = alloc()
  assert.deepEqual(G.recencyToken({ ts: null, alive: true }), { token: null, unknown: true }, 'no activity time -> unknown, no pulse')
  assert.deepEqual(G.recencyToken({ ts: tick.now + 1000, alive: true }), { token: null, unknown: true }, 'future time -> unknown')
  assert.deepEqual(G.recencyToken({ ts: tick.now - 4999, alive: true }), { token: '--dur-pulse-fresh', unknown: false }, '<=5s fresh')
  assert.deepEqual(G.recencyToken({ ts: tick.now - 5000, alive: true }), { token: '--dur-pulse-fresh', unknown: false }, 'the exact 5s boundary is fresh')
  assert.deepEqual(G.recencyToken({ ts: tick.now - 5001, alive: true }), { token: '--dur-pulse-quiet', unknown: false }, '>5s quiet')
  assert.deepEqual(G.recencyToken({ ts: tick.now - 1, alive: false }), { token: null, unknown: true }, 'absent alive evidence never infers recency')
}

// =================================================================================
// 6. Stale cancellation: an old release token cannot evict a newer holder;
//     holders stop being re-claimed (unmount/route-away) and expire after the
//     bounded idle window (nobody animates from off-screen).
// =================================================================================
{
  const A = alloc()
  const t1 = A.claim({ id: 'x', cls: 'attention', ts: 1000, durToken: '--dur-attention' }).token
  assert.equal(A.release(t1), true, 'fresh token releases')
  const t2 = A.claim({ id: 'x', cls: 'attention', ts: 1000, durToken: '--dur-attention' }).token
  assert.equal(t2.gen, t1.gen + 1, 're-admission is a new generation')
  assert.equal(A.release(t1), false, 'the STALE token cannot cancel the new generation')
  assert.equal(A.stats().total, 1, 'the live holder kept its slot through the stale release')
  // Zombie expiry: stop re-claiming and the next round of claims finds the
  // pool with the idle holder gone (same render pass -> zero elapsed ->
  // no false eviction; past the idle window -> evicted).
  tick.now += 15_000
  for (let i = 0; i < 5; i++) A.claim({ id: `keep${i}`, cls: 'edge', ts: 1000, durToken: '--dur-flow' })
  assert.ok(!A.stats().holders.some(h => h.id === 'x'), 'the un-reclaimed holder was swept (stale cancellation)')
  assert.ok(A.stats().holders.some(h => h.id === 'keep0'), 'the sweep only takes IDLE holders, not the live ones')
}

// =================================================================================
// 7. One-shot settle: a failure entry animates once per event IDENTITY —
//    repeated renders of the settled event never re-admit it; only the
//    labelled replay seam resets consumption.
// =================================================================================
{
  const A = alloc()
  const r = A.claim({ id: 'f', cls: 'transition', ts: tick.now, durToken: '--dur-failed', once: true, eventKey: 'runA/f1:failed' })
  assert.equal(r.admitted, true, 'the failed entry gets its one animator')
  tick.now += 400 // --dur-failed = 320ms: it has SETTLED
  const s1 = A.stats()
  assert.equal(s1.active, 0, 'the settled one-shot released its slot automatically (one terminal entry, then stillness)')
  const again = A.claim({ id: 'f', cls: 'transition', ts: tick.now, durToken: '--dur-failed', once: true, eventKey: 'runA/f1:failed' })
  assert.equal(again.admitted, false)
  assert.equal(again.reason, 'consumed', 'the SAME event identity is consumed-once, not once-per-render')
  const second = A.claim({ id: 'f2', cls: 'transition', ts: tick.now, durToken: '--dur-failed', once: true, eventKey: 'runA/f2:failed' })
  assert.equal(second.admitted, true, 'a NEW event identity still gets its settle')
  A.replayReset()
  const replayed = A.claim({ id: 'f', cls: 'transition', ts: tick.now, durToken: '--dur-failed', once: true, eventKey: 'runA/f1:failed' })
  assert.equal(replayed.admitted, true, 'only a user-selected labelled replay re-arms the consumption ledger')
  // unregistered durations cannot animate at all
  const bad = A.claim({ id: 'z', cls: 'transition', ts: tick.now, durToken: '--dur-slosh' })
  assert.equal(bad.admitted, false)
  assert.equal(bad.reason, 'unregistered', 'no unregistered motion: a token outside the table denies the claim to static')
  // registered 0ms tokens are static by law: admitted WITHOUT a slot
  const zero = A.claim({ id: 'exp', cls: 'transition', ts: tick.now, durToken: '--dur-expand' })
  assert.equal(zero.admitted, true, '--dur-expand:0ms admits')
  assert.equal(zero.zeroDuration, true, '...without occupying an animator')
  assert.equal(A.stats().holders.some(h => h.id === 'exp'), false, 'the 0ms admission consumed no slot')
}

// =================================================================================
// 8. Insertion reservations: <=30ms between arrivals, <=90ms total, EVERY
//    delay reserving inside N=12; excess spills to static instead of
//    extending a queue; reservations count in the budget stats.
// =================================================================================
{
  const A = alloc()
  const plan = A.planInsertion(['runA', 'runB', 'runC', 'runD', 'runE', 'runF'], { ts: tick.now })
  assert.deepEqual(plan.map(p => p.delayMs), [0, 30, 60, 90, null, null],
    'four arrivals get the 0/30/60/90ms ladder; the fifth would break the 90ms total -> static')
  assert.ok(plan.every(p => (p.delayMs ?? 0) <= 90), 'no arrival exceeds the total delay ceiling')
  const gaps = plan.filter(p => p.admitted).map(p => p.delayMs)
  assert.ok(gaps.every((d, i) => i === 0 || d - gaps[i - 1] <= 30), 'gaps between admitted arrivals are <=30ms')
  const s = A.stats()
  assert.equal(s.reserved, 3, 'three not-yet-arrived reservations (0ms lands immediately)')
  assert.equal(s.total, 4, 'reservations occupy the SAME budget (active + reserved <= 12 law)')
  // mixed pool: a full transition pool leaves no room for attention-class
  // delays — the excess spills, no queue (preemption only runs DOWN class)
  const B = alloc()
  for (let i = 1; i <= 10; i++) B.claim({ id: `h${i}`, cls: 'transition', ts: tick.now - 100, durToken: '--dur-flow' })
  const p2 = B.planInsertion(['p1', 'p2', 'p3', 'p4'], { ts: tick.now, cls: 'attention' })
  assert.deepEqual(p2.map(p => p.admitted), [true, true, false, false], 'only two slots fit -> two delays; the rest spill static NOW')
  assert.ok(p2.filter(p => !p.admitted).every(p => p.reason === 'cap'), 'cap denials, not a queue')
  assert.equal(B.stats().total, 12, 'never above 12 across claims and reservations together')
  // reservations settle: advancing past delay+dur frees the slots (--dur-insert 240ms)
  tick.now += 400
  const s3 = A.stats()
  assert.equal(s3.reserved, 0, 'the delayed insertions arrived and finished — slots released')
  assert.ok(!s3.holders.some(h => /^run[A-F]$/.test(h.id)), 'settled one-shot-like reservations leave no residue')
}

// =================================================================================
// 9. Reduced preference FLIP: zero effects, zero reservations, every later
//    claim denied to the full-opacity static state; flip back retains the
//    ORIGINAL timestamp phase (nothing restarted from a paused frame).
// =================================================================================
{
  const A = alloc()
  A.claim({ id: 'c1', cls: 'attention', ts: tick.now - 2000, durToken: '--dur-attention' })
  A.claim({ id: 'c2', cls: 'glyph', ts: tick.now, durToken: '--dur-pulse-fresh' })
  A.planInsertion(['i1', 'i2'], { ts: tick.now })
  assert.ok(A.stats().total >= 4, 'pool has active and reserved effects before the flip')
  assert.equal(A.setReduced(true), true)
  const s = A.stats()
  assert.equal(s.active, 0, 'the flip cancels every active effect (no paused frames)')
  assert.equal(s.reserved, 0, 'the flip cancels every reservation (reduced mode has no insertion delay)')
  assert.equal(s.reduced, true)
  const denied = A.claim({ id: 'c3', cls: 'transition', ts: tick.now, durToken: '--dur-done', once: true })
  assert.equal(denied.admitted, false, 'while reduced, NOTHING is admitted')
  assert.equal(denied.reason, 'reduced')
  A.setReduced(false)
  const back = A.claim({ id: 'c1', cls: 'attention', ts: tick.now - 2000, durToken: '--dur-attention' })
  assert.equal(back.admitted, true)
  assert.equal(back.phaseMs, -(2000 % 4000), 'post-flip re-admission continues the original cycle (settled, not restarted)')
}

// =================================================================================
// 10. Emitted stylesheet: ONE emission, full bytes define the identity, and
//     the digest changes iff the bytes change (replaces the version bump).
// =================================================================================
{
  const el = mod.PolishStyles()
  const css = el.props.children
  assert.equal(el.props.href, mod.styleHrefFor(css), 'href is the digest of the FULL emitted bytes (not a lane fragment)')
  assert.match(el.props.href, /^hermes-workflows\.[0-9a-f]{16}\.css$/, 'digest identity shape')
  assert.notEqual(mod.styleHrefFor(css), mod.styleHrefFor(css + '\n'), 'one byte of drift re-versions the emission')
  assert.equal(mod.styleHrefFor(css), mod.styleHrefFor(css), 'the identity is stable across recomputation')
  for (const k of Object.keys(mod.MOTION_TOKENS)) {
    assert.ok(css.includes(`${k}: ${mod.MOTION_TOKENS[k]};`), `the emission registers ${k}`)
  }
  assert.ok(css.indexOf('prefers-reduced-motion') >= 0, 'keyframes sit behind prefers-reduced-motion: no-preference')
  assert.ok(/@keyframes\s+wf-gate-nag\s*{[^}]*border-color/.test(css), 'the nag keyframes animate border-color (never glyph opacity)')
  const styleCalls = (src.match(/jsx\(\s*'style'/g) || []).length
  assert.equal(styleCalls, 1, 'CSS is emitted once: exactly one hoisted <style> in the file')
}

// =================================================================================
// 11. NodeCard renders the allocator's verdicts (behavior through the real
//     component, not a grep): admitted animates with the tokens; spilled
//     keeps the constant amber border at full opacity, immediately.
// =================================================================================
{
  const renderCard = props => {
    const n = mod.NodeCard(props)
    return typeof n.type === 'function' ? n.type(n.props) : n
  }
  const heldDef = { id: 'gate1', type: 'gate' }
  const heldSt = {}
  const heldGate = { id: 'gate1', held_at: new Date(Date.now() - 6000).toISOString(), question: 'q', options: ['go'] }
  const card = renderCard({ runId: 'r', def: heldDef, st: heldSt, gate: heldGate, owner: {}, events: [], selected: false })
  assert.equal(card.props.style.animation, 'wf-gate-nag var(--dur-attention) var(--ease-breathe) infinite',
    'admitted held card animates the hoisted nag via the REGISTERED tokens')
  const ph = Number(String(card.props.style.animationDelay).replace('ms', ''))
  assert.ok(Number.isInteger(ph) && ph <= 0 && ph > -4000,
    `card phase ${ph}ms is the timestamp cycle offset inside the registered 4000ms period (the exact value rides the live clock; the law itself is pinned by the fake-clock section)`)
  assert.equal(card.props['data-motion'], 'admitted:active', 'the admission verdict is instrumented as a DOM attribute (element prop, not a style key — a style-embedded data-* is dropped by React)')
  assert.equal(card.props['data-motion-id'], 'attention:r:gate1', 'the effect ID rides the attribute for probe correlation')
  // FINAL.md reference canary: twelve transition claims deny the attention,
  // leaving ZERO gate animation and its static border.
  const A2 = await loadMint()
  for (let i = 0; i < 12; i++) A2.MOTION.claim({ id: `tr${i}`, cls: 'transition', ts: tick.now, durToken: '--dur-flow' })
  const cardFor = m => props => {
    const n = m.NodeCard(props)
    return typeof n.type === 'function' ? n.type(n.props) : n
  }
  const spilled = cardFor(A2)({ runId: 'r', def: heldDef, st: heldSt, gate: heldGate, owner: {}, events: [], selected: false })
  assert.equal(spilled.props.style.animation, undefined, 'a denied claim leaves zero gate animation')
  assert.equal(spilled.props['data-motion'], 'spill:cap', 'and instruments the immediate static spill')
  assert.equal(spilled.props.style.borderColor, A2.NODE_TONE.held.borderColor, 'the spilled card keeps the constant amber border')
  assert.notEqual(spilled.props.style.opacity, 0.7, 'spill settles at full opacity — never a paused/faded frame')
  // the pending card breathes through the allocator too (incumbent, W5 retires)
  const waiting = renderCard({ runId: 'r', def: { id: 'tail', type: 'agent' }, st: {}, gate: null, owner: {}, events: [], selected: false })
  assert.ok(String(waiting.props.style.animation).includes('wf-breathe'), 'waiting breathes via an allocator claim')
  assert.equal(waiting.props['data-motion'], 'admitted:active', 'the breathe claim is instrumented too')
  // terminals never claim (calm law survives the allocator)
  const doneCard = renderCard({ runId: 'r', def: heldDef, st: { status: 'done' }, gate: null, owner: {}, events: [], selected: false })
  assert.equal(doneCard.props['data-motion'], 'none', 'a calm terminal holds no slot')
}

// =================================================================================
// 12. The bench seam: the plugin exposes the ONE instance (never a per-lane
//     allocator) for real-app instrumentation.
// =================================================================================
{
  assert.equal(typeof globalThis.__wfMotion, 'object', 'globalThis.__wfMotion is the bench seam')
  assert.equal(typeof globalThis.__wfMotion.stats, 'function', '...carrying the allocator readback')
  const s = globalThis.__wfMotion.stats()
  assert.equal(s.cap, 12, 'the shipped pool carries the N=12 cap')
  assert.ok(s.total <= s.cap, 'at every read, active+reserved <= 12')
}

console.log('ALL PASS test_ui2_motion (token table, global N=12 cap, priority preemption + ts/id ties, timestamp phase continuity, unknown/future timestamps, stale cancellation, consume-once one-shots, insertion reservation ladder, reduced flip to zero, content-digest single emission, NodeCard spill/admit rendering, bench seam)')
