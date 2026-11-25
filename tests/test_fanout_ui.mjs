// Node-side unit test for the desktop half's fan-out normaliser (fanItems).
// Extracts the pure functions from plugin.js (no React/SDK needed) and feeds them
// REAL run records produced by the engine test-suite (tests/home6/workflows/*).
// The records are normally committed by tests/test_papercuts_0922b.py — but the
// CI shard lanes slice the serial case list by POSITION (#502), so a consumer
// may not assume its producer shares the lane. Missing fixture => run the
// producer case here, once: same real engine, one fixture source, no snapshot
// drift, and a standalone `node tests/test_fanout_ui.mjs` works from a clean
// checkout. (Hidden cross-case coupling is the lane-shift trap any new test
// file would re-trip; this closes it for the only affected consumer.)
import { readFileSync, existsSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')
const grab = name => {
  const i = src.indexOf(`function ${name}(`)
  if (i < 0) throw new Error(`no ${name}`)
  let depth = 0, j = src.indexOf('{', i)
  for (; j < src.length; j++) { if (src[j] === '{') depth++; else if (src[j] === '}' && --depth === 0) break }
  return src.slice(i, j + 1)
}
const constGrab = name => {
  const i = src.indexOf(`const ${name} =`)
  const j = src.indexOf('\n\n', i)
  return src.slice(i, j)
}
const code = [grab('fanItems'), grab('itemLabel'), grab('renderGoal'), constGrab('fanCounts'), constGrab('fanSummary'),
  grab('fanThreshold'), grab('fanOpenFor'), grab('fanPickedRow'), grab('fanProjection'), grab('fanPageProjection')].join('\n')
const { fanItems, fanCounts, fanSummary, fanThreshold, fanOpenFor, fanPickedRow, fanProjection, fanPageProjection } =
  new Function(`${code}; return { fanItems, fanCounts, fanSummary, fanThreshold, fanOpenFor, fanPickedRow, fanProjection, fanPageProjection }`)()

let fails = 0
const check = (label, cond, detail = '') => { console.log((cond ? 'PASS ' : 'FAIL ') + label + (cond ? '' : `  [${detail}]`)); if (!cond) fails++ }

const fixtureOk = run => existsSync(join(here, 'home6', 'workflows', run, 'nodes', 'f.json'))
if (!fixtureOk('pc2-mixed') || !fixtureOk('pc2-quorum')) {
  const prod = spawnSync('python3', [join(here, 'test_papercuts_0922b.py')],
                         { cwd: join(here, '..'), stdio: 'inherit', timeout: 180_000 })
  if (!fixtureOk('pc2-mixed') || !fixtureOk('pc2-quorum')) {
    console.error(`fanout_ui: engine fixture unavailable and producer run failed (rc=${prod.status}) — refusing to fabricate records`)
    process.exit(1)
  }
}

const load = run => {
  const r = join(here, 'home6', 'workflows', run)
  const graph = JSON.parse(readFileSync(join(r, 'graph.json'), 'utf8'))
  const rec = JSON.parse(readFileSync(join(r, 'nodes', 'f.json'), 'utf8'))
  const events = readFileSync(join(r, 'events.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l))
  return { def: graph.nodes.find(n => n.id === 'f'), st: { status: rec.status, output: rec.output, error: rec.error }, events }
}

// 1. failed node (quorum miss) — all_results carries both items
{
  const { def, st, events } = load('pc2-mixed')
  const rows = fanItems(def, st, events)
  check('mixed: 2 rows', rows.length === 2, JSON.stringify(rows))
  check('mixed: item 0 failed with reason', rows[0].status === 'failed' && /rc=2/.test(rows[0].error), rows[0].error)
  check('mixed: item 0 carries tail', /segfault/.test(rows[0].tail || ''), rows[0].tail)
  check('mixed: item 1 done with output', rows[1].status === 'done' && rows[1].output?.result === 'ok', JSON.stringify(rows[1].output))
  check('mixed: labels from item goal', rows[0].label === 'CRASHME now' && rows[1].label === 'fine task', rows.map(r => r.label).join('|'))
  check('mixed: goal rendered per item', rows[1].goal === 'fine task', rows[1].goal)
  const c = fanCounts(rows)
  check('mixed: counts 1 done 1 failed', c.done === 1 && c.failed === 1 && c.total === 2, JSON.stringify(c))
}
// 2. quorum:1 node done — survivors + all_results
{
  const { def, st, events } = load('pc2-quorum')
  const rows = fanItems(def, st, events)
  check('quorum: node done still shows failed item', rows[0].status === 'failed' && rows[1].status === 'done')
}
// 3. LIVE: node running, only events so far (no committed record)
{
  const { def, events } = load('pc2-mixed')
  const rows = fanItems(def, { status: 'running', output: null }, events)
  check('live: rows from def items', rows.length === 2)
  check('live: finished item from event carries error', rows[0].status === 'failed' && /rc=2/.test(rows[0].error), rows[0].error)
  const rows2 = fanItems(def, { status: 'running', output: null }, [])
  check('live: no events yet => running placeholders', rows2.every(r => r.status === 'running'))
}
// 4. pre-0.7.2 shape: done node, merged bare outputs only
{
  const def = { id: 'f', fanout: { goal: 'probe {host}', items: [{ host: 'a' }, { host: 'b' }] } }
  const rows = fanItems(def, { status: 'done', output: { items: [{ r: 1 }, { r: 2 }], failed_items: 0 } }, [])
  check('legacy: 2 rows, both done', rows.length === 2 && rows.every(r => r.status === 'done'))
  check('legacy: output mapped by index', rows[1].output?.r === 2, JSON.stringify(rows[1]))
  check('legacy: goal template rendered', rows[0].goal === 'probe a', rows[0].goal)
  check('legacy: label from host', rows[1].label === 'b')
}
// 5. items_from (no def items) + pending
{
  const def = { id: 'f', fanout: { goal: 'x {item}', items_from: 'plan.result' } }
  const rows = fanItems(def, { status: 'pending' }, [])
  check('items_from pending: zero rows, no crash', Array.isArray(rows) && rows.length === 0)
}
// 6. v0.7.3: item.started present ⇒ started item running, unstarted item PENDING
{
  const def = { id: 'f', fanout: { goal: 'g {index}', items: [{ id: 'a' }, { id: 'b' }, { id: 'c' }, { id: 'd' }] } }
  const started = [0, 2].map(i => ({ node: 'f', event: 'item.started', index: i }))
  const rows = fanItems(def, { status: 'running', output: null }, started)
  check('starts: 4 rows', rows.length === 4, JSON.stringify(rows.map(r => r.status)))
  check('starts: started items running, rest pending',
    rows.map(r => r.status).join(',') === 'running,pending,running,pending',
    rows.map(r => r.status).join(','))
  const c = fanCounts(rows)
  check('starts: running count 2', c.running === 2 && c.total === 4, JSON.stringify(c))
}
// 7. v0.7.3: no item.started at all ⇒ old guess (running node ⇒ running items)
{
  const def = { id: 'f', fanout: { goal: 'g {index}', items: [{ id: 'a' }, { id: 'b' }, { id: 'c' }] } }
  const rows = fanItems(def, { status: 'running', output: null }, [{ node: 'f', event: 'node.started' }])
  check('no-starts: running node ⇒ all running (legacy guess)', rows.every(r => r.status === 'running'),
    rows.map(r => r.status).join(','))
  const { def: mdef, events } = load('pc2-mixed')
  const noStarts = events.filter(e => e.event !== 'item.started' && !(e.event === 'item.finished' && e.index === 1))
  const rows2 = fanItems(mdef, { status: 'running', output: null }, noStarts)
  check('no-starts: item.finished wins, unstarted falls back to running (legacy guess)',
    rows2[0].status === 'failed' && rows2[1].status === 'running',
    rows2.map(r => r.status).join(','))
}
// 8. row.metrics folded from st.item_metrics (string AND numeric keys), missing ⇒ null
{
  const { def, events } = load('pc2-mixed')
  const mk = out => fanItems(def, { status: 'running', output: null, item_metrics: out }, events)
  const a = mk({ 0: { api_calls: 3, tokens_out: 120 }, 1: { api_calls: 1 } })
  check('metrics: string keys mapped to rows', a[0].metrics?.api_calls === 3 && a[1].metrics?.api_calls === 1,
    JSON.stringify(a.map(r => r.metrics)))
  const b = mk({ 1: { tool_calls: 4 } })
  check('metrics: missing index ⇒ null', b[0].metrics === null && b[1].metrics?.tool_calls === 4,
    JSON.stringify(b.map(r => r.metrics)))
  const c = mk({})
  check('metrics: no item_metrics ⇒ null rows, statuses intact',
    c.every(r => r.metrics === null) && c[0].status === 'failed' && c[1].status === 'done',
    JSON.stringify(c.map(r => [r.status, r.metrics])))
}
// 9. RC ch4 (bd_2026-11-13-33h) MF1 synthetic regression — CLEARLY SYNTHETIC:
//    parent done + raw child 'partial', no borrowed metrics. The frozen shelf
//    fixture (research ui2/synthesis/fixtures-real/20261122-121032-wave6-council.json,
//    sha256 8ad015ceb58e0dd8e61d017a279e654c5c33bd70ffcbfcbf159b4e7ae5139922)
//    reads done for parent AND children and is preserved byte-for-byte — the
//    source was NOT rewritten to fit the audit; this synthetic row exercises
//    the regression the audit named.
{
  const def = { id: 'synthmf1', fanout: { goal: 'g {index}', items: [{ id: 'a' }, { id: 'b' }] } }
  const st = {
    status: 'done',
    metrics: { api_calls: 99, tokens_out: 5000 }, // the PARENT's own vitals
    output: { all_results: [
      { status: 'done', output: { r: 1 } },
      { status: 'partial', output: { r: 2 }, error_class: 'cap_exhausted' }
    ] }
  }
  const rows = fanItems(def, st, [])
  check('mf1: child raw status preserved (no parent borrowing)', rows[1].status === 'partial', rows[1].status)
  check('mf1: child metrics stay null while the parent has vitals', rows.every(r => r.metrics === null), JSON.stringify(rows.map(r => r.metrics)))
  const c = fanCounts(rows)
  check('mf1: partial is terminal in its OWN bucket', c.terminal === 2 && c.partial === 1 && c.done === 1 && c.failed === 0, JSON.stringify(c))
  check('mf1: the ended census is 2/2 terminal with the partial spelled out', fanSummary(c) === '2/2 terminal ·1 partial', fanSummary(c))
  const proj = fanProjection({ id: 'runMF', graph: { nodes: [def] }, nodes: { synthmf1: st } }, { synthmf1: rows })
  check('mf1 projection: child identity carries the RAW status', proj.states['synthmf1.1']?.status === 'partial', JSON.stringify(proj.states))
  check('mf1 projection: the parent keeps the aggregate, not the reverse', proj.states.synthmf1?.status === 'done' && proj.nodes.some(n => n.id === 'synthmf1'))
  const liveRows = fanItems(def, { status: 'running', output: null }, [{ node: 'synthmf1', event: 'item.finished', index: 0, status: 'done' }])
  check('projection law: live-event rows never project (recorded-only)',
    fanProjection({ id: 'r', graph: { nodes: [def] }, nodes: {} }, { synthmf1: liveRows }).nodes.length === 1)
}
// 9b. fanPageProjection: the page canvas projects COMMITTED fans at rest —
//     the Council law (10 identities, 14 projected dependencies) must hold
//     WITHOUT opening the fan, and a live fan must pass through unchanged
//     (items stay chips under the stack; the page never fabricates children).
{
  const def = { id: 'critics', type: 'agent', after: ['charter'],
                fanout: { goal: 'c {index}', items: Array.from({ length: 6 }, (_, i) => ({ id: `c${i}` })) } }
  const st = { status: 'done', output: { all_results:
    Array.from({ length: 6 }, (_, i) => ({ status: 'done', output: { r: i } })) } }
  const adjudicate = { id: 'adjudicate', type: 'agent', after: ['critics'] }
  const report = { id: 'report', type: 'agent', after: ['adjudicate'] }
  const detail = { id: 'wave6', graph: { nodes: [{ id: 'charter', type: 'agent' }, def, adjudicate, report] },
                   nodes: { charter: { status: 'done' }, critics: st, adjudicate: { status: 'done' }, report: { status: 'done' } },
                   events: [] }
  const proj = fanPageProjection(detail)
  check('page projection: ten node identities at rest', proj.nodes.length === 10, proj.nodes.map(n => n.id).join(','))
  const deps = proj.nodes.reduce((k, n) => k + (n.after?.length || 0), 0)
  check('page projection: fourteen projected dependencies (Council law)', deps === 14, String(deps))
  check('page projection: parent keeps the aggregate, child carries its own state',
    proj.states.critics?.status === 'done' && proj.states['critics.0']?.status === 'done' && proj.states['critics.5']?.status === 'done')
  const liveDetail = { ...detail, nodes: { charter: { status: 'done' }, critics: { status: 'running' } } }
  const passthru = fanPageProjection(liveDetail)
  check('page projection: a live fan (no committed rows) passes through unchanged',
    passthru.nodes.length === 4 && passthru.nodes.every(n => !String(n.id).includes('.')), passthru.nodes.map(n => n.id).join(','))
  check('page projection: MF1 child raw status survives at the page mount too',
    (() => {
      const mst = { status: 'done', output: { all_results: [{ status: 'done' }, { status: 'partial', error_class: 'cap_exhausted' }] } }
      const m = fanPageProjection({ id: 'r', graph: { nodes: [{ id: 'seed', type: 'echo' }, def, adjudicate] },
                                    nodes: { seed: { status: 'done' }, critics: mst, adjudicate: { status: 'pending' } }, events: [] })
      return m.states['critics.1']?.status === 'partial' && m.states.critics?.status === 'done'
    })())
}
// 10. exact ended census: cancelled vs failed separated, every row counted
//     exactly once, and fanSummary spelling each non-zero bucket's own word.
{
  const def = { id: 'census', fanout: { goal: 'g', items: [{}, {}, {}, {}] } }
  const st = { status: 'stopped', output: { all_results: [
    { status: 'done' },
    { status: 'failed', error_class: 'cancelled', error: 'cancelled: stop' },
    { status: 'failed', error_class: 'transport', error: 'boom' },
    { status: 'partial', output: { r: 3 } }
  ] } }
  const rows = fanItems(def, st, [])
  check('census: cancelled separates from failed', rows[1].status === 'cancelled' && rows[2].status === 'failed', JSON.stringify(rows.map(r => r.status)))
  const c = fanCounts(rows)
  check('census: cancelled rides its own neutral bucket', c.cancelled === 1 && c.failed === 1, JSON.stringify(c))
  const summed = c.done + c.failed + (c.cancelled || 0) + c.skipped + c.stopped + (c.partial || 0) + c.running + c.pending
  check('census: every row lands in exactly one bucket; terminal is exact', summed === c.total && c.terminal === 4, JSON.stringify(c))
  check('census: fanSummary is the exact census sentence', fanSummary(c) === '4/4 terminal ·1 cancelled ·1 partial, 1 failed', fanSummary(c))
}
// 11. threshold ladder: 0/3 -> 2/3 -> ack (SAME fraction) -> 3/3, driven by
//     two same-instant finishes then one late arrival. No fabricated 1/3 ever
//     exists in the model; acknowledgement moves copy, never the numerator.
{
  const def = { id: 'fanthr', fanout: { goal: 'g {index}', quorum: 2, items: [{ id: 'a' }, { id: 'b' }, { id: 'c' }] } }
  const fin = (i) => ({ node: 'fanthr', event: 'item.finished', index: i, status: 'done' })
  const snap = evs => {
    const t = fanThreshold(def, fanItems(def, { status: 'running', output: null }, evs))
    return `${t.results}/${t.total}${t.acked ? ' ack' : ''}`
  }
  const seq = [snap([]), snap([fin(0), fin(1)]), snap([fin(0), fin(1), fin(2)])]
  check('threshold: exact ladder 0/3 -> 2/3 ack -> 3/3 ack', seq.join(' -> ') === '0/3 -> 2/3 ack -> 3/3 ack', seq.join(' -> '))
  check('threshold: no fabricated intermediate exists at the ack moment',
    fanThreshold(def, fanItems(def, { status: 'running', output: null }, [fin(0), fin(1)])).results === 2)
  const tAck = fanThreshold(def, fanItems(def, { status: 'running', output: null }, [fin(0), fin(1)]))
  check('threshold: fraction identical before and after acknowledgement (copy, not numerator)',
    `${tAck.results}/${tAck.total}` === '2/3' && tAck.acked === true)
  // implicit-majority law (runner: len//2+1 when no quorum declared)
  const noq = { id: 'noq', fanout: { goal: 'g', items: [{}, {}, {}] } }
  check('threshold: null quorum reads the engine implicit majority 2/3',
    fanThreshold(noq, []).threshold === 2, JSON.stringify(fanThreshold(noq, [])))
  // unknown stays unknown: items_from with zero rows has no total and no fraction
  const fromd = { id: 'from', fanout: { goal: 'x {item}', items_from: 'plan.result' } }
  const tu = fanThreshold(fromd, [])
  check('threshold: unknown threshold remains unavailable (never invented)',
    tu.total === null && tu.threshold === null && tu.acked === false, JSON.stringify(tu))
}
// 12. same-run identities: two runs sharing one node id must never share the
//     fan expansion; the selectors are the single law the components call.
{
  const detail = { id: 'runA', graph: { nodes: [{ id: 'shared', fanout: { items: [{}] } }] }, nodes: {} }
  check('identity: cross-run fanOpen resolves null even with the same node id',
    fanOpenFor(detail, { runId: 'runB', nodeId: 'shared' }) === null)
  check('identity: same-run fanOpen resolves the def',
    fanOpenFor(detail, { runId: 'runA', nodeId: 'shared' })?.id === 'shared')
  check('identity: cross-run pick resolves null',
    fanPickedRow(detail, { id: 'shared', fanout: {} }, { runId: 'runB', nodeId: 'shared', index: 0 }, [{ index: 0, status: 'done' }]) === null)
  check('identity: same-run pick resolves the row',
    fanPickedRow(detail, { id: 'shared', fanout: {} }, { runId: 'runA', nodeId: 'shared', index: 0 }, [{ index: 0, status: 'done' }])?.status === 'done')
  check('identity: runA pick never drives the runB card',
    fanPickedRow({ ...detail, id: 'runB' }, { id: 'shared', fanout: {} }, { runId: 'runA', nodeId: 'shared', index: 0 }, [{ index: 0, status: 'done' }]) === null)
}
console.log(fails ? `\n${fails} FAILED` : '\nALL PASS (fanout normaliser + RC ch4: MF1 synthetic, exact census, threshold ladder, same-run identities, recorded-only projection)')
process.exit(fails ? 1 : 0)
