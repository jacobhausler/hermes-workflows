// QA remediation WF-02/03/04/05/06/07-display/09 — the desktop render group.
// Pins (all against the REAL desktop/plugin.js source, stub SDK/react like
// test_pill_rail — no DOM, no JSX syntax):
//  WF-02 a cancelled fan child (status failed + error_class cancelled, either
//        from all_results records or item.finished events) renders as
//        'cancelled' — neutral, never a red 'failed': fanItems/fanCounts/
//        fanSummary normalize it; the ONE tone table answers
//        NODE_TONE.cancelled === NODE_TONE.skipped; the chip ternary folds it
//        into the skipped tone; timelineTone reads it neutral. A TRUE failure
//        (provider_400 etc.) still reads 'failed' — the law is about cancelled,
//        not about hiding failures.
//  WF-03 the literal sentinel 'unknown' never prints raw in the NodePanel
//        facts column: unk/factText/logBase/attemptNo and the blocked_by /
//        schema-required / steer fallbacks answer an em-dash; an error fact
//        that IS the sentinel hides the box; statusLabel('') reads '—'. The
//        honest tab sentences (prompt/log/final: unknown) stay verbatim — they
//        are ratified by test_node_panel.
//  WF-04 the expanded terminal fold carries an overflow affordance when the
//        label counts more than the fold lists (label N, rendered K < N used
//        to silently lose N−K rows).
//  WF-05 the fold chevron flips with the state (▸ collapsed, ▾ expanded).
//  WF-06 the three concurrent elapsed clocks are labeled by source: the card/
//        record headers read `run <dur>`, the node card `node <dur>`, the
//        timeline row names the child-wall source and the axis total the
//        run-wall source.
//  WF-07 the pane census reads the payload's TOP-LEVEL total (run_summary
//        answers {total, counts}; counts.total is undefined -> 'runs ?').
//  WF-09 COST $0.0000 never prints on seat-billed runs: zero cost WITH
//        activity renders 'COST included'; zero without activity omits the
//        segment; usd() never answers '$0.0000' for a positive number; the
//        Vitals truthy guard stays.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// -- source extraction (house pattern) -------------------------------------------
const grab = name => {
  const i = src.indexOf(`function ${name}(`)
  assert.ok(i >= 0, `plugin.js must define ${name}`)
  let depth = 0, j = src.indexOf(') {', i) + 2
  for (; j < src.length; j++) if (src[j] === '{') depth++; else if (src[j] === '}' && --depth === 0) break
  return src.slice(i, j + 1)
}
const constGrab = name => {
  const i = src.indexOf(`const ${name} =`)
  assert.ok(i >= 0, `plugin.js must define const ${name}`)
  const rest = src.slice(i + 1)
  const nx = Math.min(...['\nconst ', '\nfunction ', '\n\n'].map(p => { const j = rest.indexOf(p); return j < 0 ? rest.length : j }))
  return src.slice(i, i + 1 + nx)
}
const jsx = (type, props, key) => ({ type, props: props || {}, key })
const jsxs = jsx
const walk = node => Array.isArray(node)
  ? node.flatMap(walk)
  : node && typeof node === 'object' ? [node, ...Object.values(node.props || {}).flatMap(walk)] : []
const texts = node =>
  node == null || typeof node === 'boolean' || typeof node === 'number' ? []
    : typeof node === 'string' ? [node]
    : Array.isArray(node) ? node.flatMap(texts)
    : typeof node === 'object' ? texts(node.props?.children)
    : []

// -- load the real module against a stub SDK (exported models + components) ------
const stubSdk = `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const navigations = []
export const host = { state: { focusedSessionId: atom(''), focusedStoredSessionId: atom('') }, navigate: p => navigations.push(p), notify: () => {} }
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
export const ledger = { list: null, run: null }
export const useQuery = q => (Array.isArray(q.queryKey) && q.queryKey[1] === 'run'
  ? { data: ledger.run, error: null }
  : { data: ledger.list, error: null })
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
const tmp = mkdtempSync(join(tmpdir(), 'wf-qa-render-'))
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

// ============================ WF-02 cancelled is never red =======================
{
  const fanItems = new Function(`${grab('fanItems')}\n${grab('itemLabel')}\n${grab('renderGoal')}\n${constGrab('fanCounts')}; return fanItems`)()
  const fanCounts = new Function(`${constGrab('fanCounts')}; return fanCounts`)()
  const fanSummary = new Function(`${constGrab('fanCounts')}\n${constGrab('fanSummary')}; return fanSummary`)()
  const def = { id: 'q', fanout: { items: ['a', 'b', 'c'], goal: 'work {item}' } }
  // quorum:1 committed aggregate — the two losers are status failed + error_class cancelled
  const st = { status: 'done', output: { all_results: [
    { item: 'a', status: 'done', output: { ok: true }, ms: 10 },
    { item: 'b', status: 'failed', error: 'cancelled: quorum already met (1/3)', error_class: 'cancelled', ms: 2 },
    { item: 'c', status: 'failed', error: 'cancelled: quorum already met (1/3)', error_class: 'cancelled', ms: 2 }
  ] } }
  const rows = fanItems(def, st, [])
  assert.equal(rows[0].status, 'done', 'the winner stays done')
  assert.equal(rows[1].status, 'cancelled', 'WF-02: failed+error_class=cancelled renders as cancelled, not failed')
  assert.equal(rows[1].errorClass, 'cancelled', 'WF-02: the row carries its error_class for the panel')
  const c = fanCounts(rows)
  assert.equal(c.failed, 0, 'WF-02: cancelled items never count as failed')
  assert.equal(c.cancelled, 2, 'WF-02: fanCounts has a cancelled bucket')
  assert.equal(c.terminal, 3, 'WF-02: cancelled IS terminal')
  const s = fanSummary(c)
  assert.ok(s.includes('·2 cancelled'), `WF-02: the summary names cancelled: ${s}`)
  assert.ok(!s.includes('failed'), `WF-02: no 'failed' word without a real failure: ${s}`)
  // the ratified no-cancelled shape is untouched (the contract test's exact keys)
  assert.deepEqual(fanCounts([{ status: 'done' }, { status: 'failed' }, { status: 'skipped' }, { status: 'running' }, { status: 'pending' }]),
    { total: 5, done: 1, failed: 1, running: 1, skipped: 1, stopped: 0, pending: 1, terminal: 3 },
    'WF-02: rows without cancelled keep the ratified fanCounts shape exactly')
  // events-only (live) source: item.finished carries error_class too
  const rowsEv = fanItems(def, { status: 'done', item_metrics: { 0: {}, 1: {}, 2: {} } }, [
    { node: 'q', index: 1, event: 'item.finished', status: 'failed', error: 'cancelled by stop', error_class: 'cancelled' }
  ])
  const loser = rowsEv.find(r => r.index === 1)
  assert.equal(loser.status, 'cancelled', 'WF-02: the events source normalizes too')
  // a real failure still renders red (the law is about cancelled, not about hiding failures)
  const rowsBad = fanItems(def, { status: 'done', output: { all_results: [
    { item: 'a', status: 'failed', error: 'boom', error_class: 'provider_400' }
  ] } }, [])
  assert.equal(rowsBad[0].status, 'failed', 'WF-02: a true failure keeps the failed word')
  // the ONE tone table answers cancelled — the same entry as skipped (neutral, calm)
  assert.equal(mod.NODE_TONE.cancelled, mod.NODE_TONE.skipped, 'WF-02: NODE_TONE.cancelled IS NODE_TONE.skipped (one table, one voice)')
  // ItemChips picks the skipped tone for a cancelled chip (source law, house idiom)
  assert.match(src, /r\.status === 'skipped' \|\| r\.status === 'stopped' \|\| r\.status === 'cancelled' \? EDGE_TONE\.skipped/,
    'WF-02: the chip tone ternary folds cancelled into the neutral skipped tone')
  // timelineTone (the timeline's own map) answers neutral for cancelled
  const timelineTone = new Function('NODE_TONE', `${constGrab('timelineTone')}; return timelineTone`)(mod.NODE_TONE)
  assert.equal(timelineTone({ status: 'cancelled' }), mod.NODE_TONE.skipped.color, 'WF-02: the timeline reads cancelled neutral')
  // the fan-item peek hides the red error tone for cancelled rows
  assert.match(src, /pre\('error',\s*row\.error,\s*row\.status === 'cancelled' \? undefined\s*:\s*EDGE_TONE\.failed\)/,
    'WF-02: ItemDetail prints a cancelled error neutral, never red')
  // and the NodePanel error pre is neutral when the record's class is cancelled
  assert.match(src, /cancelledClass \? undefined : EDGE_TONE\.failed/, 'WF-02: the NodePanel error box is neutral for cancelled')
}

// ============================ WF-03 no raw 'unknown' ============================
{
  const statusLabel = new Function(`${constGrab('statusLabel')}; return statusLabel`)()
  assert.equal(statusLabel(''), '—', 'WF-03: an empty status reads an em-dash, never the word unknown')
  assert.equal(statusLabel('done'), 'done', 'WF-03: present statuses pass through verbatim')
  const unk = new Function(`${constGrab('UNKNOWN')}\n${constGrab('unk')}; return unk`)()
  assert.equal(unk(null), 'unknown', 'the O2 law stands: unk PRODUCES the sentinel for absent facts')
  assert.match(src, /const factKnown = v => v != null && v !== '' && v !== UNKNOWN/,
    'WF-03: factKnown guards the section renderers (sentinel-valued facts HIDE, never print raw)')
  // Render the REAL NodePanel on a healthy node whose record carries the
  // sentinel everywhere: no bare 'unknown' may reach the screen.
  const code = [
    constGrab('EDGE_TONE'), constGrab('FACT_TONE'), constGrab('UNKNOWN'), constGrab('unk'), constGrab('factText'),
    constGrab('logBase'), constGrab('attemptNo'), constGrab('defaultTabFor'), constGrab('TAIL_BYTES'),
    grab('fanItems'), grab('itemLabel'), grab('renderGoal'), constGrab('fanCounts'), constGrab('fanSummary'),
    grab('useNodeLogTail')
  ].join('\n')
  const panel = new Function(
    'useValue', 'useState', 'useTick', 'useQuery', 'api', 'ID_OK', 'Q', '$selNode', '$fanItem',
    'ItemChips', 'box', 'label', 'statusLabel', 'fmtOutput', 'Dot', 'Badge', 'Button', 'Vitals', 'Fragment', 'jsx', 'jsxs',
    code + '\n' + grab('NodePanel') + '; return NodePanel'
  )(
    a => (a && a.sel ? { runId: 'r1', nodeId: 'a' } : null),
    () => [null, () => {}],
    () => {},
    () => ({ data: null, isPending: false }),
    async () => ({}),
    /^[\w.-]+$/, ['wf'], { sel: true }, { no: true },
    'ItemChips',
    (className, ...kids) => kids.length === 1 ? jsx('div', { className, children: kids[0] }) : jsxs('div', { className, children: kids }),
    text => jsx('div', { children: text }),
    s => s || '—',
    o => (o == null ? '' : typeof o === 'string' ? o : JSON.stringify(o, null, 2)),
    'Dot', 'Badge', 'Button', 'Vitals', 'Fragment', jsx, jsxs
  )
  const tree = panel({ detail: {
    id: 'r1', status: 'running',
    graph: { nodes: [{ id: 'a', type: 'agent' }] },
    nodes: { a: { status: 'running', error_class: 'unknown', error: 'unknown', attempts_log: 'unknown', blocked_by: null } },
    events: []
  } })
  const t = texts(tree).join('|')
  // WF-03 hide-law: no bare sentinel reaches the screen (only the honest
  // ratified tab sentences keep the word); sentinel facts hide their section.
  for (const seg of t.split('|')) {
    assert.ok(!/\bunknown\b/.test(seg) || /prompt: unknown|log: unknown|final: unknown/.test(seg),
      `WF-03: only the honest tab sentences may keep the word: ${seg}`)
  }
  assert.ok(!t.split('|').includes('error'), 'WF-03: a sentinel error hides the error section entirely')
  assert.ok(!t.split('|').includes('budgets'), 'WF-03: all-sentinel budgets hide themselves')
  assert.ok(!t.split('|').includes('blocked_by'), 'WF-03: absent blocked_by hides itself')
  assert.ok(!t.split('|').includes('attempts_log'), 'WF-03: absent attempts_log hides itself')
  assert.ok(!t.split('|').includes('schema required'), 'WF-03: a node without a schema hides the section')
  // a REAL error still rides the existing verbatim path
  const tree2 = panel({ detail: {
    id: 'r1', status: 'failed',
    graph: { nodes: [{ id: 'a', type: 'agent' }] },
    nodes: { a: { status: 'failed', error_class: 'crashed', error: 'segfault', log_path: '/r/a.a1.log' } },
    events: []
  } })
  const t2 = texts(tree2).join('|')
  assert.ok(t2.includes('segfault'), 'WF-03: a real error still renders verbatim')
  assert.ok(t2.includes('crashed'), 'WF-03: a real error_class renders verbatim')
}

// ====================== WF-04/WF-05 the terminal fold ============================
{
  const mk = (id, i) => ({ id, name: id, status: 'done', owner: { session_id: 'S1' }, started: `2026-09-26T04:0${i}:00Z`, updated: `2026-09-26T04:0${i}:00Z` })
  const many = [...Array(7)].map((_, i) => mk(`t${i}`, i))
  const s = mod.splitRuns(many)
  assert.equal(s.terminalTotal, 7, 'the fold label reports the true terminal count')
  sdkMod.host.state.focusedSessionId.set('S1')
  sdkMod.ledger.list = { runs: many, total: 7, counts: { running: 0 } }
  const strip = mod.SessionStrip()
  const txt = texts(strip).join('|')
  assert.ok(/▸ 7 finished/.test(txt), `WF-05: collapsed reads ▸ + the true count: ${txt.slice(0, 120)}`)
  const foldBtn = walk(strip).find(n => n.type === 'button' && texts(n).join('').includes('finished'))
  assert.ok(foldBtn, 'the fold toggle exists')
  foldBtn.props.onClick() // $stripFold.set(pairKey) on the writable stub atom
  const openStrip = mod.SessionStrip()
  const open = texts(openStrip).join('|')
  assert.ok(/▾ 7 finished/.test(open), `WF-05: expanded flips the chevron to ▾: ${open.slice(0, 120)}`)
  const foldRows = walk(openStrip).filter(n => n.type === 'button' && /· (done|failed|stopped) ·/.test(texts(n).join('')))
  const shown = foldRows.length
  assert.ok(shown > 0 && shown < 7, `the fold lists ${shown} of 7 rows`)
  const overflow = walk(openStrip).find(n => n.type === 'button' && /\+\s*\d+\s+more/.test(texts(n).join('')))
  assert.ok(overflow, `WF-04: the missing ${7 - shown} rows keep a "+N more" affordance`)
  assert.equal(texts(overflow).join(''), `+${7 - shown} more`, 'the affordance counts EXACTLY the hidden rows')
  overflow.props.onClick()
  assert.deepEqual(sdkMod.navigations, ['/workflows'], 'the affordance opens the pane where every run is listed')
}

// ============================ WF-06 labeled clocks ==============================
{
  const inlineHeader = new Function('nodesCount', 'fmtDur', 'kfmt', 'usd', 'idleS', 'TERMINAL',
    `${src.match(/const inlineHeader = \(data, elapsed\) => \{[\s\S]*?\n\}/)[0]}; return inlineHeader`)(
    r => `${r.nodes_done}/${r.nodes_total} terminal`, n => `${Math.round(n / 1000)}s`, String,
    n => `$${n.toFixed(2)}`, () => null, new Set(['done', 'failed', 'stopped'])
  )
  const [first] = inlineHeader({ id: 'x', name: 'x', status: 'running', nodes_done: 1, nodes_total: 2 }, 33000)
  assert.ok(first.some(x => /^run \d+s$/.test(x)), `WF-06: the card header clock is labeled run: ${first}`)
  assert.ok(!first.some(x => /^\d+s$/.test(x)), `WF-06: no unlabeled clock remains: ${first}`)
  assert.match(src, /children: `run \$\{hdr\.elapsedLabel\}`/, 'WF-06: the record header clock is labeled run')
  assert.match(src, /children: `node \$\{dur\}`/, 'WF-06: the node-card clock is labeled node')
  assert.match(src, /title: 'child wall \(node\.started → node\.finished\)'/, 'WF-06: the timeline row names the child-wall source')
  assert.match(src, /title: 'run wall span \(first → last event\)'/, 'WF-06: the timeline axis total names the run-wall source')
}

// ============================ WF-07 census reads data.total =====================
{
  sdkMod.ledger.list = {
    runs: [{ id: 'a', status: 'running', name: 'a', owner: { session_id: 'other' }, updated: '2026-09-26T04:00:00Z' }],
    total: 38, counts: { running: 2, held: 0, failed: 8 }
  }
  const tree = mod.WorkflowsPane()
  const t = texts(tree).join('|')
  const line = t.split('|').find(x => x.startsWith('runs '))
  assert.ok(line, 'the census row exists')
  assert.equal(line, 'runs 38 · running 2 · held 0 · failed 8',
    'WF-07: the census reads the payload top-level total (never ? when the payload answers)')
}

// ============================ WF-09 no COST $0.0000 =============================
{
  const inlineHeader = new Function('nodesCount', 'fmtDur', 'kfmt', 'usd', 'idleS', 'TERMINAL',
    `${src.match(/const inlineHeader = \(data, elapsed\) => \{[\s\S]*?\n\}/)[0]}; return inlineHeader`)(
    r => `${r.nodes_done}/${r.nodes_total} terminal`, n => `${n}ms`, String,
    n => `$${n.toFixed(2)}`, () => null, new Set(['done', 'failed', 'stopped'])
  )
  const [, second] = inlineHeader({ id: 'x', name: 'x', status: 'running', nodes_done: 1, nodes_total: 2,
    metrics: { api_calls: 3, tokens_in: 1200, tokens_out: 80, cost: 0, live: 1 } }, null)
  assert.ok(!second.some(x => /\$0\.0000/.test(x)), `WF-09: no zero-dollar literal: ${second}`)
  assert.ok(second.some(x => x === 'COST included'), `WF-09: seat-billed activity reads included: ${second}`)
  // zero cost with NO activity is nothing to say at all
  const [, secondIdle] = inlineHeader({ id: 'x', name: 'x', status: 'pending', nodes_done: 0, nodes_total: 2,
    metrics: { cost: 0 } }, null)
  assert.ok(!secondIdle.some(x => x.startsWith('COST')), 'WF-09: a fresh run with zero cost prints no COST segment')
  // a real cost still renders
  const [, secondPaid] = inlineHeader({ id: 'x', name: 'x', status: 'done', nodes_done: 2, nodes_total: 2,
    metrics: { cost: 0.25 } }, null)
  assert.ok(secondPaid.some(x => x === 'COST $0.25'), `a real estimate still prints: ${secondPaid}`)
  // the usd formatter itself never answers '$0.0000' for a positive number
  const usd = new Function(`${constGrab('usd')}; return usd`)()
  assert.equal(usd(0.000001), '<$0.0001', 'WF-09: sub-cent renders as <$0.0001, never $0.0000')
  assert.equal(usd(0.25), '$0.250', 'WF-09: normal costs keep the money format')
  assert.equal(usd(2), '$2.00')
  // Vitals (the other cost line) honors the same law: zero is never printed
  assert.match(src, /if \(cost && m\.cost\) parts\.push/, 'WF-09: Vitals keeps the truthy-cost guard')
}

rmSync(tmp, { recursive: true, force: true })
console.log('ALL PASS test_wf_qa_render_group (cancelled-neutral, no raw unknown, fold affordance + chevron flip, labeled clocks, census total, no $0.0000)')
