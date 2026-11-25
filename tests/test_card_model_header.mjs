// Pin (2.0, bd_2026-11-13-1bm): the RC card model answers the pill's census and
// the expanded word row with the FINAL lifecycle-table public labels and the
// FINAL numeric laws (tokens 2sf, counts exact safe integers, LIVE/IDLE cells
// always answered for a live running row). The 1.4-era two-row inlineHeader is
// retired — the same laws now ride cardModel.census/cardModel.metrics, word-
// labelled per INCHAT §2 (never the ambiguous IN/OUT/API/TOOL abbreviations).
// The real shared-view-model helpers are evaluated from the source block; only
// parseTime/fmtDur/TERMINAL/NODE_TONE stay injected, so this file stays about
// the card row layout law. The retired inlineHeader name must NEVER return.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const source = readFileSync(join(root, 'desktop', 'plugin.js'), 'utf8')
assert.ok(!/inlineHeader/.test(source), 'the legacy inlineHeader renderer is retired, not kept as a shim')
const vm = source.match(/\/\/ BEGIN shared-view-model\n([\s\S]*?)\/\/ END shared-view-model/)
assert.ok(vm, 'plugin.js ships the shared lifecycle + numeric view-model block')
const statusLine = source.match(/const statusLabel = [^\n]+/)
assert.ok(statusLine, 'statusLabel law present')
// l8i: cardModel titles through the REAL displayTitle/templateTag — the
// sandbox evaluates the exported resolvers too (shared-source law).
const resolver = [
  source.match(/const TITLE_MAX = [^\n]+/)[0],
  source.match(/export function displayTitle[\s\S]*?\n}/)[0].replace('export ', ''),
  source.match(/export function templateTag[\s\S]*?\n}/)[0].replace('export ', ''),
].join('\n')
const grab = name => {
  const i = source.indexOf(`function ${name}(`)
  assert.ok(i >= 0, `plugin.js must define ${name}`)
  let depth = 0, j = source.indexOf(') {', i) + 2
  for (; j < source.length; j++) if (source[j] === '{') depth++; else if (source[j] === '}' && --depth === 0) break
  return source.slice(i, j + 1)
}
const cardModel = new Function('fmtDur', 'TERMINAL', 'NODE_TONE',
  `const EDGE_TONE = { pending: 'P', running: 'R', held: 'H', failed: 'F' }\n${statusLine[0]}\n${vm[1]}\n${resolver}\n${grab('parseTime')}\n${grab('cardModel')};\nreturn cardModel`)(
  n => `${Math.round(n / 1000)}s`, new Set(['done', 'failed', 'stopped']),
  { pending: 'P', running: 'R', held: 'H', failed: 'F', done: 'D' })
const ago = s => new Date(Date.now() - s * 1000).toISOString()

const cm = cardModel({ id: 'id', name: 'Sample', status: 'running', nodes_done: 2, nodes_total: 3,
  started: ago(3), metrics: { tokens_in: 100, tokens_out: 12, api_calls: 4, tool_calls: 1, cost: 0.25, live: 1, last_activity: 1 } })
// Identity baseline: the name and the FINAL table's verbatim status word; a
// 1970 stamp is quiet, not fresh. Collapsed is the default state.
assert.equal(cm.name, 'Sample', 'the identity baseline names the run')
assert.equal(cm.statusWord, 'Running · quiet, alive', 'the status word is the FINAL table verbatim')
assert.equal(cm.expanded, false, 'the card renders collapsed by default')
// Census baseline (INCHAT §1): exact ended/total count, the run WALL clock
// labelled (WF-06), and the notices cell honestly dashed (the read model
// carries no notice stream — absent is `— notices`, never a silent 0).
assert.ok(cm.census.includes('2/3 nodes'), `exact census: ${cm.census}`)
assert.ok(cm.census.some(x => /^◷ run \d+s$/.test(x)), `the census clock is LABELLED run (WF-06): ${cm.census}`)
assert.ok(!cm.census.some(x => /^\d+s$/.test(x)), `no unlabeled clock remains: ${cm.census}`)
assert.ok(cm.census.includes('— notices'), `absent notices ride the dash: ${cm.census}`)
// Expanded word row (INCHAT §2): every cell names what it IS.
assert.deepEqual(cm.metrics.slice(0, 5), ['Model —', 'Input tokens 100', 'Output tokens 12', 'API calls 4', 'Tool calls 1'],
  `word-labelled metrics: ${cm.metrics}`)
assert.ok(cm.metrics.includes('COST $0.250'), `a real estimate still prints: ${cm.metrics}`)
assert.ok(cm.metrics.includes('LIVE 1'), 'a live running row always answers LIVE')
assert.ok(cm.metrics.some(x => /^IDLE \d+s$/.test(x)), 'the IDLE cell is answered, never silent')

// A genuinely absent rollup answers its own honest sentence, never zeros.
assert.deepEqual(cardModel({ id: 'unknown', status: 'pending', nodes_done: 0, nodes_total: 1 }).metrics,
  ['Metrics not recorded'], 'no metrics: an explicit not-recorded line, never a row of dashes')
// LIVE without an activity stamp: the IDLE cell answers the honest dash, never silence.
{
  const live = cardModel({ id: 'unknown', status: 'running', nodes_done: 0, nodes_total: 1, metrics: { live: 1 } })
  assert.ok(live.metrics.includes('LIVE 1') && live.metrics.includes('IDLE —'),
    `running-live answers both cells, dash for an unknown stamp: ${live.metrics}`)
}
// Count law: API/TOOL ride exactCount — 10001 calls stay 10001, never 10.0k.
assert.ok(cardModel({ id: 'x', status: 'done', nodes_done: 1, nodes_total: 1,
  metrics: { api_calls: 10001, tool_calls: 154 } }).metrics.includes('API calls 10001'),
  'counts are exact integers, never abbreviated')
// Token law: two significant figures, promotion after rounding.
{
  const m = cardModel({ id: 'x', status: 'done', nodes_done: 1, nodes_total: 1,
    metrics: { tokens_in: 17739101, tokens_out: 999999 } }).metrics
  assert.ok(m.includes('Input tokens 18M') && m.includes('Output tokens 1.0M'), `tokens 2sf: ${m}`)
}
// An absent census rides the em-dash, a recorded zero stays 0 (no-fabrication).
{
  assert.ok(cardModel({}).census.includes('—/— nodes'), 'absent counts dash')
  assert.ok(cardModel({ nodes_done: 0, nodes_total: 5 }).census.includes('0/5 nodes'), 'an actual zero stays 0')
}
// The failed bucket is explicit when the node records answer it, and a
// cancelled straggler (WF-02, the #7 law) is its OWN neutral word — a stop is
// history, never a failure: the read model re-reads the record pending with
// error_class 'cancelled' (and CANCELLED dispositions ride fan item records).
{
  const withFails = cardModel({ id: 'x', status: 'failed', nodes_done: 1, nodes_total: 3,
    nodes: { a: { status: 'failed', error_class: 'provider_error' }, b: { status: 'failed' } } })
  assert.ok(withFails.census.includes('! 2 failed'), `failures never hide behind the fraction: ${withFails.census}`)
  const cancelled = cardModel({ id: 'x', status: 'stopped', nodes_done: 0, nodes_total: 2,
    nodes: { a: { status: 'pending', error_class: 'cancelled' }, b: { status: 'done', disposition: 'CANCELLED' } } })
  assert.ok(cancelled.census.includes('· 2 cancelled'), `a stop is history, not failure: ${cancelled.census}`)
  assert.ok(cancelled.census.includes('! 0 failed'), `cancelled is never counted failed: ${cancelled.census}`)
}

// DOM laws (INCHAT §1): the container is not a click surface; disclosure and
// full-view are sibling native buttons with an aria pair; the card mounts the
// shared graph and fan strip when expanded.
{
  const body = source.slice(source.indexOf('function DirectiveBody'), source.indexOf('function DirectiveBody') + 6000)
  assert.match(body, /cm\.census\.map/, 'the census row maps the model cells')
  assert.match(body, /cm\.metrics\.map/, 'the metrics row maps the model cells')
  assert.match(body, /jsx\(MiniGraph, \{ detail: data \}\)/, 'the expanded card mounts the shared MiniGraph')
  assert.match(body, /jsx\(FanStrip, \{ runId: data\.id/, 'the expanded card mounts the shared FanStrip')
  assert.match(body, /'data-wf-expand'/, 'the disclosure button is hook-addressable')
  assert.match(body, /'data-wf-open'/, 'the full-view button is hook-addressable')
  assert.match(body, /'aria-expanded': open, 'aria-controls': bodyId/, 'the disclosure carries its aria pair')
  assert.ok(!/role:\s*'button'/.test(body), 'no role=button container — the whole-card click surface is retired')
  assert.ok(!/role:\s*'link'/.test(body), 'no role=link anywhere (one click, one effect)')
}

// l8i (instance-label-first, bd_2026-11-13-l8i) — the law SURVIVES the
// renderer swap: a LABELED run titles with the instance label; the template
// is demoted to a model slot + hover + the lead word of the expanded row,
// never the identity baseline; an unlabeled run never prints its name twice.
{
  const labeled = cardModel({ id: 'r', name: 'tpl', lane_key: 'ship20W2c', status: 'pending',
    nodes_done: 0, nodes_total: 1 })
  assert.equal(labeled.name, 'ship20W2c', 'the identity baseline carries the resolved label, not the template')
  assert.equal(labeled.template, 'tpl', 'the demoted template rides the model as secondary metadata')
  assert.equal(labeled.metrics[0], 'template tpl', 'the expanded word row leads with the labelled template')
  assert.equal(cardModel({ id: 'r', name: 'tpl', status: 'pending' }).template, null,
    'unlabeled run: title IS the name — the template nulls, never printed twice')
  const body = source.slice(source.indexOf('function DirectiveBody'))
  assert.match(body, /title: cm\.template \? `template \$\{cm\.template\}` : undefined/,
    'the compact pill hover is where the demoted template rides')
}

console.log('ALL PASS: RC card model rows, lifecycle words, numeric laws, cancelled-neutral census, retired inlineHeader, l8i label-first demotion, disclosure DOM laws')
