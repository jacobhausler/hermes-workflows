// Pin: the expanded directive card's two-row header renders the FINAL
// lifecycle-table public labels and the FINAL numeric laws (tokens 2sf,
// counts exact safe integers, LIVE/IDLE cells always answered for a live
// running row), retains interactions. The real shared-view-model helpers are
// evaluated from the source block; only nodesCount/fmtDur stay injected so
// this file stays about the header layout law.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const source = readFileSync(join(root, 'desktop/plugin.js'), 'utf8')
const match = source.match(/const inlineHeader = \(data, elapsed\) => \{[\s\S]*?\n\}/)
assert.ok(match, 'inline header helper exists')
const vm = source.match(/\/\/ BEGIN shared-view-model\n([\s\S]*?)\/\/ END shared-view-model/)
assert.ok(vm, 'plugin.js ships the shared lifecycle + numeric view-model block')
const statusLine = source.match(/const statusLabel = [^\n]+/)
assert.ok(statusLine, 'statusLabel law present')
// l8i: inlineHeader resolves titles through the REAL displayTitle/templateTag —
// the sandbox evaluates the exported resolvers too (same shared-source law).
const resolver = [
  source.match(/const TITLE_MAX = [^\n]+/)[0],
  source.match(/export function displayTitle[\s\S]*?\n}/)[0].replace('export ', ''),
  source.match(/export function templateTag[\s\S]*?\n}/)[0].replace('export ', ''),
].join('\n')
const header = new Function('nodesCount', 'fmtDur', 'TERMINAL',
  `const EDGE_TONE = { pending: 'P', running: 'R', held: 'H', failed: 'F' }\n${statusLine[0]}\n${vm[1]}${resolver}\n${match[0]}; return inlineHeader`)(
  r => `${r.nodes_done ?? 0}/${r.nodes_total ?? '?'} terminal`, n => `${n}ms`,
  new Set(['done', 'failed', 'stopped'])
)
const [first, second] = header({ id: 'id', name: 'Sample', status: 'running', nodes_done: 2, nodes_total: 3,
  metrics: { tokens_in: 100, tokens_out: 12, api_calls: 4, tool_calls: 1, cost: 0.25, live: 1, last_activity: 1 } }, 3000)
// A 1970 stamp is quiet, not fresh; the word is the FINAL table's verbatim.
assert.deepEqual(first, ['Sample', 'Running · quiet, alive', '2/3 terminal', 'run 3000ms'])
assert.deepEqual(second.slice(0, 6), ['IN 100', 'OUT 12', 'API 4', 'TOOL 1', 'COST $0.250', 'LIVE 1'])
assert.match(second[6], /^IDLE \d+s$/, 'a live running row always answers the IDLE cell')
assert.deepEqual(header({ id: 'unknown', status: 'pending', nodes_done: 0, nodes_total: 1 }, null)[1], [])
// LIVE without an activity stamp: the IDLE cell answers the honest dash, never silence.
assert.deepEqual(header({ id: 'unknown', status: 'running', nodes_done: 0, nodes_total: 1,
  metrics: { live: 1 } }, null)[1], ['LIVE 1', 'IDLE —'])
// Count law: API/TOOL ride exactCount — 10001 calls stay 10001, never 10.0k.
assert.ok(header({ id: 'x', status: 'done', nodes_done: 1, nodes_total: 1,
  metrics: { api_calls: 10001, tool_calls: 154 } }, null)[1].includes('API 10001'))
assert.match(source, /headerRows\[0\]\.map/)
assert.match(source, /headerRows\[1\]\.map/)
assert.match(source, /jsx\(MiniGraph, \{ detail: data \}\)/)
assert.match(source, /jsx\(FanStrip, \{ runId: data.id/)
console.log('ALL PASS: inline two-row header, lifecycle words, numeric laws, unknown metrics, retained interactions')
