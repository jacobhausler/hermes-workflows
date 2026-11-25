// Ship 2.0 (bd_2026-11-13-ah9): the shared lifecycle + numeric view models.
// Every law is exercised through the REAL production helpers/components
// extracted from desktop/plugin.js (stub SDK jsx only — no string-match-only
// acceptance):
//  - exact safe integer API/TOOL/attempt/member counts (never rounded,
//    never abbreviated; invalid/fractional/unsafe reads the dash);
//  - token volume at 2 significant figures (999999 -> 1.0M, 17739101 -> 18M),
//    actual zero stays 0, absence is a dash — never a fabricated 0;
//  - sub-cent cost floors to '<$0.0001'; zero cost reads COST included ONLY
//    with recorded activity; unpriced/invalid shows nothing;
//  - run clocks say `run`, child clocks do not (WF-06 law, one vocabulary);
//  - invalid or FUTURE activity stamps are activity-unknown, never 0 s;
//  - fresh <=5 s / quiet >5 s / stale and unknown inactivity follow the FINAL
//    lifecycle table words, with pulses only on KNOWN activity;
//  - raw statuses stay exact and cancelled keeps its own neutral word; the
//    only relabelling is successful done -> Finished.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
const src = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'desktop', 'plugin.js'), 'utf8')

const grab = name => {
  const i = src.indexOf(`function ${name}(`)
  assert.ok(i >= 0, name)
  let depth = 0, j = src.indexOf(') {', i) + 2
  for (; j < src.length; j++) if (src[j] === '{') depth++; else if (src[j] === '}' && --depth === 0) break
  return src.slice(i, j + 1)
}
const vm = src.match(/\/\/ BEGIN shared-view-model\n([\s\S]*?)\/\/ END shared-view-model/)
assert.ok(vm, 'plugin.js ships one marked shared-view-model block')
const statusLine = src.match(/const statusLabel = [^\n]+/)
assert.ok(statusLine, 'statusLabel law present')
const EDGE_TONE = { done: 'D', failed: 'F', running: 'R', held: 'H', skipped: 'S', pending: 'P' }
const PRELUDE = `${statusLine[0]}\n${vm[1]}`
const nodesLine = src.match(/const nodesCount = [^\n]+/)[0]
const evm = expr => new Function(`${PRELUDE}\n; return (${expr})`)()

const jsx = (type, props) => ({ type, props })
const jsxs = jsx
const walk = n => Array.isArray(n) ? n.flatMap(walk)
  : n && typeof n === 'object' ? [n, ...Object.values(n.props || {}).flatMap(walk)] : []
const texts = n => walk(n).flatMap(x => typeof x === 'string' ? [x] : typeof x.props?.children === 'string' ? [x.props.children] : [])

// -- 1. exact safe-integer count law -------------------------------------------------
{
  const r = evm(`({
    zero: exactCount(0),
    calls: exactCount(10001),
    frac: exactCount(2.5),
    neg: exactCount(-3),
    unsafe: exactCount(Number.MAX_SAFE_INTEGER + 2),
    nul: exactCount(null),
    str: exactCount('7'),
    memberFallback: countCell(undefined, '?'),
    freshBoundary: activityLaw(5) + '/' + activityLaw(6)
  })`)
  assert.deepEqual(r, {
    zero: '0', calls: '10001', frac: '—', neg: '—', unsafe: '—', nul: '—', str: '—',
    memberFallback: '?', freshBoundary: 'fresh/quiet'
  }, 'counts: exact safe nonnegative integers or the dash; the fresh/quiet boundary is 5 s (<=5 fresh, >5 quiet)')
}

// -- 2. token volume at 2 significant figures ----------------------------------------
{
  const r = evm(`({
    m: tokenMag(999999),
    big: tokenMag(17739101),
    zero: tokenMag(0),
    small: tokenMag(154),
    k: tokenMag(1234),
    nul: tokenMag(null),
    empty: tokenMag(''),
    nan: tokenMag(NaN),
    inf: tokenMag(Infinity),
    neg: tokenMag(-1)
  })`)
  assert.deepEqual(r, {
    m: '1.0M', big: '18M', zero: '0', small: '154', k: '1.2k',
    nul: '—', empty: '—', nan: '—', inf: '—', neg: '—'
  }, '2sf magnitudes; actual zero stays 0; absence/nonfinite is the dash, never 0')
}

// -- 3. sub-cent cost + the usd floor ------------------------------------------------
{
  const r = evm(`({
    floor: usd(0.000001),
    below: usd(0.00004),
    at: usd(0.0001),
    cents: usd(0.5),
    dollar: usd(2),
    zero: usd(0),
    nul: usd(null),
    str: usd('0.5'),
    nan: usd(NaN)
  })`)
  assert.deepEqual(r, {
    floor: '<$0.0001', below: '<$0.0001', at: '$0.0001', cents: '$0.500', dollar: '$2.00',
    zero: '—', nul: '—', str: '—', nan: '—'
  }, 'a positive cost never floors to $0.0000; non-numeric cost is absence')
}

// -- 4. real Vitals: counts, costs, heartbeat fresh/quiet/unknown --------------------
// W5 (bd_2026-11-13-lv1): the beat is an allocator-admitted glyph, not a host
// animate-* class. The sandbox injects the pure decision (the allocator's
// behaviour itself is pinned by test_ui2_motion): same evidence law — an
// invalid/future/absent stamp is unknown and admits nothing.
const glyphMotionStandIn = (id, m, stale = false) => {
  const la = m && m.last_activity
  if (!id || stale || typeof la !== 'number' || !Number.isFinite(la) || la <= 0) return { admitted: false, reason: 'unknown-activity' }
  const age = Date.now() / 1000 - la
  return { admitted: true, token: age <= 5 ? '--dur-pulse-fresh' : '--dur-pulse-quiet', phaseMs: 0 }
}
const glyphPulseStyleStandIn = g => g && g.admitted
  ? { animation: `wf-pulse var(${g.token}) var(--ease-breathe) infinite`, animationDelay: `${g.phaseMs}ms` }
  : null
const { Vitals } = new Function('EDGE_TONE', 'METER_TONE', 'jsx', 'jsxs', 'Fragment', 'glyphMotion', 'glyphPulseStyle',
  `${statusLine[0]}\n${vm[1]}\n${grab('Vitals')}; return { Vitals }`)(
  EDGE_TONE, { 'on-track': 'R' }, jsx, jsxs, 'Frag', glyphMotionStandIn, glyphPulseStyleStandIn)
{
  const now = () => Date.now() / 1000
  const t = row => texts(Vitals({ m: row, live: true, cost: true }))
  const pulses = row => walk(Vitals({ m: row, live: true, cost: true, motionId: 'glyph:sandbox-beat' }))
    .filter(n => String(n.props?.style?.animation || '').includes('wf-pulse')).length

  // fresh: <=5 s activity — the seconds ride and the glyph pulses
  assert.ok(t({ last_activity: now() - 3, api_calls: 4 }).some(x => /^\d?s$/.test(x)), 'fresh heartbeat shows seconds')
  assert.equal(pulses({ last_activity: now() - 3 }), 1, 'fresh (<=5 s) activity pulses')
  // quiet: >5 s — known alive still pulses (the table admits the quiet pulse)
  assert.equal(pulses({ last_activity: now() - 31 }), 1, 'quiet (>5 s) known activity still pulses')
  // unknown: invalid / future stamps — NOTHING pulses, the cell is a dash, never 'live'
  assert.equal(pulses({ last_activity: 'yesterday' }), 0, 'invalid stamp must not pulse')
  assert.equal(pulses({ last_activity: now() + 120 }), 0, 'FUTURE stamp is clock skew: activity unknown, must not fake fresh')
  assert.equal(pulses({}), 0, 'stored running alone must not pulse')
  assert.ok(t({}).includes('—'), 'unknown heartbeat reads the dash, never the word live')
  assert.ok(!t({}).includes('live'), 'no fabricated liveness word when the stamp is absent')
  // counts + cost law through the real vitals line
  const rich = t({ tokens_in: 999999, tokens_out: 17739101, api_calls: 10001, tool_calls: 154, cost: 0.00004, attempts: 3 })
  assert.ok(rich.some(x => x === '1.0M▸18M'), `tokens at 2sf: ${rich}`)
  assert.ok(rich.includes('10001⚡'), `API count stays exact: ${rich}`)
  assert.ok(rich.includes('154🔧'), `TOOL count stays exact: ${rich}`)
  assert.ok(rich.includes('<$0.0001'), `sub-cent floors: ${rich}`)
  assert.ok(rich.includes('↻3'), `attempt count exact: ${rich}`)
  assert.ok(rich.includes('↻—') === false, 'valid attempts never dash')
  assert.ok(t({ api_calls: 2.5, tokens_in: 0 }).some(x => x === '—⚡'), 'fractional attempts/calls render the dash, never a rounded count')
  // recorded-activity zero: COST included; zero WITHOUT activity: silent; unpriced: silent
  assert.ok(t({ cost: 0, api_calls: 5 }).includes('COST included'), 'zero cost with recorded activity reads COST included')
  assert.ok(!t({ cost: 0 }).some(x => /COST|\$0/.test(x)), 'zero cost with no activity says nothing about cost')
  assert.ok(!t({ cost: null }).some(x => /COST|\$0/.test(x)), 'unpriced shows no dollar figure at all')
}

// -- 5. real inlineHeader: run clock vs child clock + activity words -----------------
// l8i: inlineHeader/pillModel resolve titles through the exported resolvers —
// the sandboxes below evaluate the REAL displayTitle/templateTag too (same
// shared-source law as grab('parseTime')).
const resolver = [
  src.match(/const TITLE_MAX = [^\n]+/)[0],
  src.match(/export function displayTitle[\s\S]*?\n}/)[0].replace('export ', ''),
  src.match(/export function templateTag[\s\S]*?\n}/)[0].replace('export ', ''),
].join('\n')
{
  const headerGrab = src.match(/const inlineHeader = \(data, elapsed\) => \{[\s\S]*?\n\}/)[0]
  const inlineHeader = new Function('fmtDur', 'TERMINAL', `const EDGE_TONE = ${JSON.stringify(EDGE_TONE)}\n${PRELUDE}\n${nodesLine}\n${resolver}\n${headerGrab};\nreturn inlineHeader`)(
    ms => `${Math.round(ms / 1000)}s`, new Set(['done', 'failed', 'stopped']))
  const now = Date.now() / 1000
  const fresh = inlineHeader({ name: 'w', status: 'running', nodes_done: 1, nodes_total: 4,
    metrics: { last_activity: now - 1, live: 1 } }, 30000)
  assert.ok(fresh[0].includes('Running · fresh activity'), `<=5 s stamp: table wording: ${fresh[0]}`)
  assert.ok(fresh[0].includes('run 30s'), `the header clock is LABELLED run: ${fresh[0]}`)
  assert.ok(fresh[1].some(x => /^IDLE \d+s$/.test(x)), 'live row answers IDLE')
  const quiet = inlineHeader({ name: 'w', status: 'running', nodes_done: 1, nodes_total: 4,
    metrics: { last_activity: now - 6, live: 1 } }, 30000)
  assert.ok(quiet[0].includes('Running · quiet, alive'), `>5 s stamp: quiet, alive: ${quiet[0]}`)
  const unknown = inlineHeader({ name: 'w', status: 'running', nodes_done: 1, nodes_total: 4,
    metrics: { last_activity: now + 900, live: 1 } }, 30000)
  assert.ok(unknown[0].includes('Running · activity unknown'), `future stamp: activity unknown: ${unknown[0]}`)
  assert.ok(unknown[1].includes('LIVE 1') && unknown[1].includes('IDLE —'),
    `the running-unknown row answers LIVE n / IDLE —, never a silent or 0 IDLE: ${unknown[1]}`)
  // child clocks stay unlabeled-by-run: ItemDetail renders fmtDur(row.ms) only.
  const itemGrab = grab('ItemDetail')
  const { ItemDetail } = new Function('jsx', 'box', 'label', 'Dot', 'Badge', 'Vitals', 'fmtDur', 'fmtOutput', 'EDGE_TONE',
    `${itemGrab}; return { ItemDetail }`)(jsx, (cls, ...k) => jsx('div', { children: k }), x => x, 'Dot', 'Badge', 'Vitals',
    ms => `${ms}ms`, x => String(x), EDGE_TONE)
  const it = texts(ItemDetail({ row: { index: 0, status: 'done', label: 'a', ms: 5000, goal: 'g' } }))
  assert.ok(it.includes('5000ms'), 'the child duration renders without the run label')
  assert.ok(!it.some(x => /^run /.test(x)), 'no child span ever claims the run word')
}

// -- 6. real pillModel + DirectiveBody: public words, stale, clock ------------------
{
  const pillGrab = grab('pillModel')
  const pillModel = new Function('TERMINAL', 'NODE_TONE', 'fmtDur', `const EDGE_TONE = ${JSON.stringify(EDGE_TONE)}\n${PRELUDE}\n${nodesLine}\n${grab('parseTime')}\n${resolver}\n${pillGrab};\nreturn pillModel`)(
    new Set(['done', 'failed', 'stopped']), { pending: {} }, ms => `${Math.round(ms / 1000)}s`)
  const line = pillModel({ id: 'w', status: 'done', nodes_done: 4, nodes_total: 4,
    started: '2026-01-01T00:00:00Z', updated: '2026-01-01T00:02:00Z' }).collapsedLine
  assert.ok(line.includes('Finished'), `successful done reads the table word: ${line}`)
  assert.ok(line.includes('4/4 terminal'), `known census stays exact: ${line}`)
  assert.ok(line.includes('run 120s'), `the pill clock is labelled run (WF-06): ${line}`)
  const cancelled = pillModel({ id: 'w', status: 'cancelled' }).collapsedLine
  assert.ok(cancelled.includes('cancelled'), `cancelled keeps its own neutral word: ${cancelled}`)
  assert.ok(!/Finished|failed/i.test(cancelled), 'cancelled is never Finished and never failed')
  const gone = pillModel({ id: 'w', status: 'running', started: '2026-01-01T00:00:00Z' }, true).collapsedLine
  assert.ok(gone.startsWith('w · Disconnected · last known Running'), `cached-directive reads Disconnected, keeps last-known word: ${gone}`)
  assert.ok(!/fresh|quiet, alive/.test(gone), 'a disconnected record never infers present liveness')
  const empty = pillModel({}).collapsedLine
  assert.ok(empty.includes('—'), `an absent status is the em-dash: ${empty}`)
}

// -- 7. no palette fork: the view model touches words and digits, never tones -------
{
  assert.match(src, /const idleTone = s => s == null \? EDGE_TONE\.pending/, 'idle tones still read the ONE palette')
  assert.ok(!/NODE_TONE\.\w+ = '(?!var\()/.test(src), 'no tone-table entry was replaced by a literal word')
}

console.log('ALL PASS: shared lifecycle + numeric view models (exact counts, 2sf tokens, sub-cent floor, COST included law, run vs child clocks, invalid/future stamps, fresh/quiet/stale/unknown, cancelled neutral, no palette fork)')
