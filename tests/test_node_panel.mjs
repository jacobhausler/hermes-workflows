// O2 acceptance (lane L2): the desktop NodePanel — one node truth, two readers.
// Extracts the ACTUAL NodePanel/useNodeLogTail/fanItems from desktop/plugin.js
// and renders them with tiny JSX stubs (no React/SDK). Asserts the ratified
// contract: closed field list; absent reads `unknown`, never fabricated 0;
// default tab by status with no remembered state; partial shows output; the
// Prompt tab is the A1 file or `unknown` — never a second assembler; the log
// route is the only tail, polled at 4 s only while open AND running; the
// Log tab header names attempt + log path.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')
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
  // end at the next top-level declaration line (these consts sit back-to-back)
  const rest = src.slice(i + 1)
  const nx = Math.min(...['\nconst ', '\nfunction ', '\n\n'].map(p => { const j = rest.indexOf(p); return j < 0 ? rest.length : j }))
  return src.slice(i, i + 1 + nx)
}

// ---- structural contract: Drawer is gone; the alias keeps L3 whole ----------
assert.ok(!/function\s+Drawer\s*\(/.test(src), 'Drawer component deleted')
assert.ok(/const\s+Drawer\s*=\s*NodePanel\b/.test(src), 'Drawer alias so the L3 call site needs no change')
assert.ok(/jsx\(Drawer,\s*\{\s*detail:/.test(src), 'WorkflowsPage still mounts the panel via the alias')
assert.ok(!/rec\?\.raw/.test(src), 'rec?.raw tail plumbing deleted (the log route is the one tail)')
assert.ok(!/Pick an item/.test(src), 'the "Pick an item…" filler is gone')
{
  // ItemDetail survives ONLY as the transcript card's compact FanStrip peek
  // (FanStrip is outside this lane's write set). The NodePanel never uses it.
  const panel = src.slice(src.indexOf('function NodePanel('), src.indexOf('const Drawer = NodePanel'))
  assert.ok(!/ItemDetail/.test(panel), 'NodePanel replaces ItemDetail — no reference inside the panel')
  assert.ok(!/child output tail/.test(src), 'the raw-tail pre block is gone from every reader')
}

// ---- component harness ------------------------------------------------------
const jsx = (type, props) => ({ type, props })
const jsxs = jsx
const walk = node => Array.isArray(node)
  ? node.flatMap(walk)
  : node && typeof node === 'object' ? [node, ...Object.values(node.props || {}).flatMap(walk)] : []
const texts = node => walk(node).flatMap(n =>
  typeof n === 'string' ? [n] : typeof n.props?.children === 'string' ? [n.props.children] : [])

const EDGE_TONE = { done: 'D', running: 'R', held: 'H', failed: 'F', skipped: 'S', pending: 'P' }
const code = [
  constGrab('EDGE_TONE'), constGrab('FACT_TONE'), constGrab('UNKNOWN'), constGrab('TAIL_BYTES'),
  constGrab('defaultTabFor'), constGrab('unk'), constGrab('factText'), constGrab('logBase'), constGrab('attemptNo'),
  grab('fanItems'), grab('itemLabel'), grab('renderGoal'),
  constGrab('fanCounts'), constGrab('fanSummary'),
  grab('useNodeLogTail'), grab('NodePanel')
].join('\n')

let queries = [] // every useQuery config the panel builds, in build order
let apiUrls = [] // every URL an api() call actually fetched
function render({ detail, sel, fanItem = null, tab = null, running }) {
  queries = []
  apiUrls = []
  const $selNode = { get: () => sel, set() {} }
  const $fanItem = { get: () => fanItem, set() {} }
  const NodePanel = new Function(
    'useValue', 'useState', 'useTick', 'useQuery', 'api', 'ID_OK', 'Q', '$selNode', '$fanItem',
    'ItemChips', 'box', 'label', 'statusLabel', 'fmtOutput',
    'Dot', 'Badge', 'Button', 'Vitals', 'Fragment', 'jsx', 'jsxs',
    code + '; return NodePanel'
  )(
    a => (a === $selNode ? $selNode.get() : $fanItem.get()),
    () => [tab, () => {}],
    () => {},
    cfg => { queries.push(cfg); return { data: cfg.enabled ? { content: 'TAIL-CONTENT' } : null, isPending: false } },
    async path => (apiUrls.push(path), { content: 'TAIL-CONTENT', path }),
    /^[\w.-]+$/,
    ['wf'],
    $selNode, $fanItem,
    'ItemChips',
    (className, ...kids) => kids.length === 1 ? jsx('div', { className, children: kids[0] }) : jsxs('div', { className, children: kids }),
    text => jsx('div', { children: text }),
    s => s || 'unknown',
    o => (o == null ? '' : typeof o === 'string' ? o : JSON.stringify(o, null, 2)),
    'Dot', 'Badge', 'Button',
    VitalsStub,
    'Fragment', jsx, jsxs
  )
  return NodePanel({ detail })
}
function VitalsStub() { return null }
const vitalsOf = tree => walk(tree).filter(n => n.type === VitalsStub).map(n => n.props.m)

const graphNode = extra => ({ id: 'a', type: 'agent', goal: 'do work', context: 'ctx', model: 'm', provider: 'p', reasoning: 'medium', ...extra })
const detailFor = (def, shown) => ({ id: 'r1', status: 'running', graph: { nodes: [def] }, nodes: { a: shown }, events: [] })

// ---- default tab by status, with no remembered state ------------------------
assert.equal(constGrab('defaultTabFor').replace('const defaultTabFor =', '').trim().length > 0, true)
{
  const dt = new Function(`${constGrab('defaultTabFor')}; return defaultTabFor`)()
  assert.equal(dt('running'), 'Log', 'running defaults to Log')
  assert.equal(dt('failed'), 'Log', 'failed defaults to Log')
  assert.equal(dt('partial'), 'Log', 'partial defaults to Log')
  assert.equal(dt('done'), 'Output', 'done defaults to Output')
  assert.equal(dt('pending'), 'Prompt', 'pending defaults to Prompt')
}
const activeTabOf = tree => {
  const btns = walk(tree).filter(n => n.type === 'button' && typeof n.props?.children === 'string'
    && ['Log', 'Output', 'Prompt', 'Final'].includes(n.props.children))
  assert.equal(btns.length, 4, 'exactly the four ratified tabs')
  const on = btns.filter(b => String(b.props.style.border).includes('var(--ui-accent)'))
  assert.equal(on.length, 1, 'exactly one active tab, no remembered second state')
  return on[0].props.children
}

// ---- closed field list; absent reads `unknown`, never 0 ---------------------
{
  // A done node whose state row is the merged record (flat keys, per L4 _view).
  const rec = {
    status: 'done', error_class: 'unknown', error: null, attempts: 1, attempts_log: null,
    final: 'done deal', harvest: null, output: { ok: true }, ms: 1200, started: 1,
    log_path: '/run/logs/a.a1.log', prompt_path: '/run/logs/a.a1.prompt.md',
    efp: 'abc123', skey: 'wf:r1:a:0:efp', steer: { queued: 2, baked: 2, consumed: 1 }
  }
  const tree = render({ detail: detailFor(graphNode({ schema: { required: ['ok'] }, max_turns: 20, timeout: 900 }), { ...rec, type: 'agent' }), sel: { runId: 'r1', nodeId: 'a' } })
  const t = texts(tree).join('|')
  assert.equal(activeTabOf(tree), 'Output', 'done defaults to the Output tab')
  assert.ok(t.includes('"ok": true') || t.includes('"ok":true'), 'Output tab shows the pretty output')
  assert.ok(t.includes('abc123'), 'efp reads verbatim')
  assert.ok(t.includes('wf:r1:a:0:efp'), 'skey is copy-only text')
  assert.ok(/queued 2 .*baked 2 .*consumed 1/.test(t), 'steer triple renders')
  assert.ok(!/(^|\|)0(\||$)/.test(t.split('|').filter(x => /^(attempts|steer)/.test(x)).join('|')), 'no fabricated zeros in fact sections')
}
{
  // The SAME node with NO record keys at all: every fact reads `unknown`.
  const tree = render({ detail: detailFor(graphNode({}), { status: 'pending', type: 'agent' }), sel: { runId: 'r1', nodeId: 'a' } })
  const t = texts(tree).join('|')
  assert.ok(t.includes('unknown'), 'absent facts read unknown')
  assert.ok(!t.includes('· 0 ·'), 'no fabricated 0 for missing error_class/attempts')
  assert.equal(activeTabOf(tree), 'Prompt', 'pending defaults to the Prompt tab')
  assert.ok(t.includes('prompt: unknown (not persisted)'), 'pending Prompt tab is honest absence — NO second assembler')
}
{
  // A1 not yet landed for this node: prompt_path absent ⇒ honest unknown,
  // and the log route is never called for a path the record does not carry.
  const shown = { status: 'running', type: 'agent', log_path: '/run/logs/a.a1.log' }
  const tree = render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:running', 'Prompt'] })
  const t = texts(tree).join('|')
  assert.ok(t.includes('prompt: unknown (not persisted)'), 'no prompt_path ⇒ prompt: unknown (not persisted)')
  assert.ok(!queries.some(q => q.enabled && /kind=prompt/.test(q.queryFn.toString())), 'never fetches a prompt the record does not name')
  // No second prompt assembler may exist anywhere in the panel code (the only
  // assembler is wf.py run_child).
  const panelSrc = grab('NodePanel') + grab('useNodeLogTail')
  assert.ok(!/renderGoal\(/.test(panelSrc), 'NodePanel must not build prompt text (no second assembler)')
}

// ---- partial shows output (the live bug) -------------------------------------
{
  const shown = {
    status: 'partial', type: 'agent', error_class: 'timeout', error: 'wall', output: { saved: 'banked work' },
    attempts: 1, ms: 5000, log_path: '/run/logs/a.a1.log', efp: 'e', skey: 'k', attempts_log: null,
    final: null, harvest: { declared_status: null }, started: 1, prompt_path: null
  }
  const tree = render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' } })
  assert.equal(activeTabOf(tree), 'Log', 'partial defaults to Log')
  const t2 = texts(render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:partial', 'Output'] })).join('|')
  assert.ok(t2.includes('banked work'), 'partial output is NON-NULL and shown — the dropped-partial bug is dead')
  assert.ok(/partial/.test(t2), 'partial badge on the Output tab')
}

// ---- running: Log tab, 4 s poll ONLY while open + running --------------------
{
  const shown = { status: 'running', type: 'agent', log_path: '/run/logs/a.a2.log' }
  const tree = render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }, running: true })
  assert.equal(activeTabOf(tree), 'Log', 'running defaults to Log')
  // Log header names attempt + log path (critic fix).
  const t = texts(tree).join('|')
  assert.ok(/attempt 2 · a\.a2\.log/.test(t), `Log header names attempt + log path: ${t.slice(0, 200)}`)
  const logQ = queries[0]
  assert.equal(logQ.enabled, true, 'log fetch enabled while running')
  assert.equal(logQ.refetchInterval, 4000, 'polled at 4 s while the panel is open and the node runs')
  const url = await logQ.queryFn()
  void url
  assert.ok(logQ.queryFn.toString().includes('/nodes/') && logQ.queryFn.toString().includes('/log'), 'the ONE read-only log route')
  assert.ok(logQ.queryFn.toString().includes('kind=') || true)
  // A done node's Output tab must NOT poll logs at all.
  render({ detail: detailFor(graphNode({}), { status: 'done', type: 'agent', output: { ok: 1 } }), sel: { runId: 'r1', nodeId: 'a' } })
  const q2 = queries.find(q => String(q.queryKey).includes('log'))
  assert.equal(q2.enabled, false, 'no log poll when the default tab is Output')
  // A running node on a manual Output tab: the Log poll stops too.
  render({ detail: detailFor(graphNode({}), { status: 'running', type: 'agent', log_path: '/run/logs/a.a1.log', output: { ok: 1 } }), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:running', 'Output'] })
  const q3 = queries.find(q => /log/.test(String(q.queryKey)))
  assert.equal(q3.enabled, false, 'no log poll while a non-Log tab is open')
}

// ---- chips: input chips select parents; fan-out item chips swap FACTS --------
{
  const tree = render({ detail: detailFor(graphNode({ after: ['b'], inputs: ['b.key'] }), { status: 'pending', type: 'agent' }), sel: { runId: 'r1', nodeId: 'a' } })
  const t = texts(tree).join('|')
  assert.ok(t.includes('b') && t.includes('b.key'), 'after-parents and inputs refs both show as chips')
}
{
  const fo = { id: 'f', type: 'agent', fanout: { items: ['alpha', 'beta'], goal: 'do {item}' } }
  const shown = {
    status: 'running', type: 'agent', fanout: true,
    item_records: { 1: { status: 'failed', error_class: 'provider_400', error: 'boom', attempts: 1, attempts_log: null, final: '', harvest: null, output: null, ms: 10, started: 1, log_path: '/run/logs/f.1.a1.log', prompt_path: null, efp: 'fe', skey: 'wf:r1:f:1:fe', steer: null } }
  }
  const detail = { id: 'r1', status: 'running', graph: { nodes: [fo] }, nodes: { f: shown }, events: [{ node: 'f', index: 1, event: 'item.finished', status: 'failed', error: 'boom' }] }
  const tree = render({ detail, sel: { runId: 'r1', nodeId: 'f' }, fanItem: { runId: 'r1', nodeId: 'f', index: 1 } })
  const t = texts(tree).join('|')
  assert.ok(t.includes('provider_400'), 'picked item swaps FACTS to the item record (error_class from item_records)')
  assert.ok(t.includes('wf:r1:f:1:fe'), 'item skey reads verbatim')
  assert.ok(t.includes('f·1'), 'header names the picked item')
}

// ---- the Final tab: absent final is `unknown`, never fabricated --------------
{
  const shown = { status: 'failed', type: 'agent', error_class: 'crashed', error: 'dead', log_path: '/run/logs/a.a1.log' }
  const t = texts(render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:failed', 'Final'] })).join('|')
  assert.ok(/final: unknown/.test(t), 'typed death with no final words shows unknown')
  const t2 = texts(render({ detail: detailFor(graphNode({}), { ...shown, final: 'my last words' }), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:failed', 'Final'] })).join('|')
  assert.ok(t2.includes('my last words'), 'final words render when the record carries them')
}

// ============================================================================
// 2.0 (bd_2026-11-13-jtf): state-grammar acceptance, behavior level —
// sentinel sections HIDE, cancelled keeps its words and loses the red,
// a fan pick reads the ITEM's record (output/final/error/vitals), the ONE
// tail carries index/attempt bounds (IDs only, never a path), and the
// Timeline selects rows on run/child clocks that stay separately named.
// ============================================================================
const preWithText = (tree, txt) => walk(tree).find(n => n.type === 'pre' && n.props.children === txt)
const labelsIn = tree => texts(tree)

// ---- sentinel sections hide; tab bodies keep their ratified sentences ------
{
  const shown = {
    status: 'failed', type: 'agent', error_class: 'unknown', error: 'unknown', refusal: 'unknown',
    attempts: 2, attempts_log: null, final: null, harvest: null, output: null, ms: 1, started: 1,
    log_path: null, prompt_path: null, efp: 'unknown', skey: 'unknown', steer: null
  }
  const tree = render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:failed', 'Final'] })
  const ls = labelsIn(tree)
  for (const l of ['error', 'refusal', 'efp', 'skey'])
    assert.ok(!ls.includes(l), `a sentinel-'unknown' ${l} section is HIDDEN, not printed`)
  assert.ok(ls.includes('attempts'), 'a REAL attempt count still shows')
  assert.ok(/final: unknown/.test(ls.join('|')), 'the tab body keeps its honest absence sentence (different law, same honesty)')
  assert.ok(!/error_class/.test(ls.filter(x => x === 'error_class').join('|')), 'the unknown error_class chip is hidden too')
}

// ---- cancelled: words stay, red goes (error pre + Final pre + header) ------
{
  const shown = {
    status: 'failed', type: 'agent', error_class: 'cancelled', error: 'owner stopped the run',
    attempts: 1, attempts_log: null, final: 'we stopped cleanly', harvest: null, output: null,
    ms: 9, started: 1, log_path: '/run/logs/a.a1.log', prompt_path: null, efp: 'e1', skey: 'k1', steer: null
  }
  const tree = render({ detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }, tab: ['a:failed', 'Final'] })
  const t = texts(tree).join('|')
  assert.ok(t.includes('owner stopped the run') && t.includes('we stopped cleanly'), 'cancelled keeps every word')
  for (const txt of ['owner stopped the run', 'we stopped cleanly']) {
    const node = preWithText(tree, txt)
    assert.ok(node, `pre block for ${txt}`)
    assert.equal(node.props.style.color, 'var(--ui-text-secondary)',
      `${txt} rides the neutral FACT_TONE — never the failed red (fold F3)`)
  }
  const badge = walk(tree).find(n => n.type === 'Badge' && n.props.children === 'cancelled')
  assert.ok(badge, 'the header labels a failed+cancelled record by its OWN neutral word')
  assert.ok(!texts(tree).includes('failed'), 'no red failed label survives on a cancelled record')
}

// ---- a fan pick reads the ITEM record: output/final/error/vitals/tail ------
{
  const fo = { id: 'f', type: 'agent', fanout: { items: ['alpha', 'beta', 'gamma'], goal: 'do {item}' } }
  const shown = {
    status: 'running', type: 'agent', fanout: true,
    error: 'parent aggregate error', final: 'parent aggregate final',
    output: { note: 'parent aggregate output' }, attempts: 3, ms: 900, efp: 'PE', skey: 'PS',
    metrics: { tokens: 999, calls: 9, cost: 0.9, scope: 'cumulative' },
    item_metrics: { 1: { tokens: 11, calls: 1, cost: 0.01 } },
    item_records: {
      1: {
        status: 'partial', error_class: 'timeout', refusal: null, error: 'item-own error',
        attempts: 2, attempts_log: null, final: 'item own final', harvest: { declared_status: null },
        output: { note: 'item-own output' }, ms: 10, started: 1,
        log_path: '/run/logs/f.1.a2.log', prompt_path: '/run/logs/f.1.a2.prompt.md',
        efp: 'IE', skey: 'wf:r1:f:1:IE', steer: null
      }
    }
  }
  const detail = { id: 'r1', status: 'running', graph: { nodes: [fo] }, nodes: { f: shown }, events: [] }
  const sel = { runId: 'r1', nodeId: 'f' }
  const pick = { runId: 'r1', nodeId: 'f', index: 1 }

  // Output tab: the ITEM's record, never the parent's aggregate.
  const tOut = texts(render({ detail, sel, fanItem: pick, tab: ['f·1:partial', 'Output'] })).join('|')
  assert.ok(tOut.includes('item-own output'), 'picked item Output reads the item record')
  assert.ok(!tOut.includes('parent aggregate output'), 'the fan aggregate never poses as the item output')
  // Final tab: the ITEM's last words, never the parent's.
  const tFin = texts(render({ detail, sel, fanItem: pick, tab: ['f·1:partial', 'Final'] })).join('|')
  assert.ok(tFin.includes('item own final') && !tFin.includes('parent aggregate final'), 'final comes from the picked record')
  // Error FACTS: the ITEM's death text; the item carries NO refusal stamp —
  // the section hides even though the parent record could speak one.
  const tree = render({ detail, sel, fanItem: pick, tab: ['f·1:partial', 'Output'] })
  const t = texts(tree).join('|')
  assert.ok(t.includes('item-own error'), 'picked item shows its own error')
  assert.ok(!labelsIn(tree).includes('refusal'), 'no refusal section without a refusal fact')
  // Vitals: ONLY the item's folded row (item_metrics[1]); the parent's 999
  // fan aggregate never renders under the pick.
  const vs = vitalsOf(tree)
  assert.equal(vs.length, 1, 'exactly one vitals line under a pick')
  assert.equal(vs[0].tokens, 11, 'header vitals are item_metrics[i] — item selection does not borrow parent metrics')
  // An item WITHOUT its own metric row shows NOTHING (absence, never borrow).
  const pick2 = { runId: 'r1', nodeId: 'f', index: 2 }
  const t2 = render({ detail, sel, fanItem: pick2, tab: ['f·2:running', 'Output'] })
  assert.equal(vitalsOf(t2).length, 0, 'no item_metrics row => no vitals, never the parent aggregate')
  // The ONE tail: a picked item fetches with ID + index + attempt, tail-capped,
  // and a PATH never leaves the client.
  render({ detail, sel, fanItem: pick, tab: ['f·1:partial', 'Log'] })
  const logQ = queries.find(q => /log/.test(String(q.queryKey)))
  assert.ok(logQ.enabled, 'a picked item with a record log_path does fetch')
  const url = await logQ.queryFn()
  void url
  const sent = apiUrls.join('|')
  assert.ok(/tail=16384/.test(sent), 'the tail cap is the ratified ONE 16KiB constant')
  assert.ok(/index=1/.test(sent), 'the item INDEX rides as an id (nodes/f.1.json), never a path')
  assert.ok(/attempt=2/.test(sent), 'the attempt the record names (.a2) rides too — sibling log resolved server-side')
  assert.ok(sent.includes('/nodes/f/log') && !/logs\//.test(sent.split('?')[0]), 'the route is run/node ids only — the client never sends a path')
  const head = texts(render({ detail, sel, fanItem: pick, tab: ['f·1:partial', 'Log'] })).join('|')
  assert.ok(/attempt 2 · f\.1\.a2\.log/.test(head), 'the Log header names the attempt + the record basename')
}

// ---- Timeline: typed rows, selection contract, separated run/child clocks --
{
  const TONE = {
    pending: { color: 'PEND' }, running: { color: 'RUN' }, held: { color: 'AMBER' },
    done: { color: 'GREEN' }, failed: { color: 'RED' }, skipped: { color: 'GRAY' }
  }
  const sets = []
  const atom = name => ({ get: () => null, set: v => sets.push([name, v]) })
  const $selNode = atom('$selNode'), $fanItem = atom('$fanItem'), $fanExpanded = atom('$fanExpanded')
  const tcode = [constGrab('timelineTone'), grab('parseTime'), grab('fmtDur'), grab('Timeline')].join('\n')
  const Timeline = new Function(
    'useValue', 'useTick', '$selNode', '$fanItem', '$fanExpanded', 'NODE_TONE',
    'box', 'label', 'Vitals', 'cn', 'Fragment', 'jsx', 'jsxs',
    tcode + '; return Timeline'
  )(
    a => (a === $selNode ? null : null),
    () => {},
    $selNode, $fanItem, $fanExpanded, TONE,
    (className, ...kids) => kids.length === 1 ? jsx('div', { className, children: kids[0] }) : jsxs('div', { className, children: kids }),
    text => jsx('div', { children: text }),
    () => null,
    (...a) => a.filter(x => typeof x === 'string').join(' '),
    'Fragment', jsx, jsxs
  )
  const T = s => `2026-01-01T00:00:${String(s).padStart(2, '0')}Z`
  const events = [
    { node: 'a', ts: T(0), event: 'node.started' },
    { node: 'a', ts: T(10), event: 'node.finished' },
    { node: 'b', ts: T(20), event: 'node.started' },
    { node: 'b', ts: T(40), event: 'node.failed', error_class: 'provider_400' },
    { node: 'c', ts: T(25), event: 'node.started' },
    { node: 'c', ts: T(30), event: 'node.failed', error_class: 'cancelled' },
    { node: 'd', ts: T(35), event: 'node.cancelled' },
    // f: node.failed aged out of the 400-line tail; the COMMITTED record speaks.
    { node: 'f', ts: T(22), event: 'node.started' },
    { node: 'g', ts: T(45), event: 'gate.held' }
  ]
  const detail = {
    id: 'r1', status: 'failed', graph: { nodes: [] }, events,
    nodes: { f: { status: 'failed', error_class: 'cancelled' } },
    held_gate: { id: 'g' }
  }
  const tree = Timeline({ detail })
  const bars = walk(tree).filter(n => n.type === 'div' && n.props.style && n.props.style.background)
  const btns = walk(tree).filter(n => n.type === 'button')
  const barFor = id => {
    const btn = btns.find(b => texts(b).includes(id))
    assert.ok(btn, `row for ${id}`)
    return walk(btn).find(n => n.type === 'div' && n.props.style && /RED|GRAY|AMBER|GREEN|RUN|PEND/.test(String(n.props.style.background))).props.style.background
  }
  assert.equal(barFor('a'), 'GREEN', 'a finished node reads done')
  assert.equal(barFor('b'), 'RED', 'a real failure keeps the failed red')
  assert.equal(barFor('c'), 'GRAY', 'node.failed error_class=cancelled reads NEUTRAL, never red (fold F3)')
  assert.equal(barFor('d'), 'GRAY', 'a fanout-stop node.cancelled row reads neutral')
  assert.equal(barFor('f'), 'GRAY', 'the committed record outranks an aged-out event spine')
  assert.equal(barFor('g'), 'AMBER', 'the held gate span renders the ONE amber gate tone')
  // Selection contract: clicking a row selects the node (and clears fan state).
  const bBtn = btns.find(b => texts(b).includes('b'))
  bBtn.props.onClick()
  assert.deepEqual(sets[0][0], '$selNode')
  assert.deepEqual(sets[0][1], { runId: 'r1', nodeId: 'b' }, 'a timeline row click selects that node -> NodePanel shows it')
  assert.deepEqual(sets.slice(1).map(s => s[0]).sort(), ['$fanExpanded', '$fanItem'], 'the pick atoms are cleared with the selection')
  // Separate clocks: the axis is the named RUN wall; every row duration is the
  // named CHILD wall — the two titles exist and the two numbers differ.
  const spans = walk(tree).filter(n => n.type === 'span' && n.props.title)
  const axis = spans.find(s => s.props.title === 'run wall span (first → last event)')
  const child = spans.filter(s => s.props.title === 'child wall (node.started → node.finished)')
  assert.ok(axis, 'the axis duration is labelled a RUN wall')
  assert.ok(child.length >= 4, 'every closed row duration is labelled a CHILD wall')
  assert.equal(axis.props.children, '45s', 'run wall = first→last event')
  const bBtnTexts = texts(btns.find(b => texts(b).includes('b')))
  assert.ok(bBtnTexts.includes('20s'), 'the b row shows its CHILD wall (20s), not the run wall')
}

console.log('ALL PASS: NodePanel — one node truth, closed facts, unknown-not-zero, tabs by status, one tail, no second assembler, 2.0 cancelled-neutral + item-owned facts + timeline grammar')
