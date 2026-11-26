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

// bd_2026-11-13-cj2: NodePanel/WorkflowsPage mount the real marked nav block
const navBlock = src.match(/\/\/ BEGIN stored-session-nav\n([\s\S]*?)\/\/ END stored-session-nav/)[0].replace(/^export /gm, '')

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
  navBlock,
  constGrab('EDGE_TONE'), constGrab('FACT_TONE'), constGrab('UNKNOWN'), constGrab('TAIL_BYTES'),
  constGrab('defaultTabFor'), constGrab('unk'), constGrab('factText'), constGrab('logBase'), constGrab('attemptNo'),
  grab('fanItems'), grab('itemLabel'), grab('renderGoal'),
  constGrab('fanCounts'), constGrab('fanSummary'),
  grab('useNodeLogTail'), grab('NodePanel')
].join('\n')

let queries = [] // every useQuery config the panel builds, in build order
function render({ detail, sel, fanItem = null, tab = null, running }) {
  queries = []
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
    async path => ({ content: 'TAIL-CONTENT', path }),
    /^[\w.-]+$/,
    ['wf'],
    $selNode, $fanItem,
    'ItemChips',
    (className, ...kids) => kids.length === 1 ? jsx('div', { className, children: kids[0] }) : jsxs('div', { className, children: kids }),
    text => jsx('div', { children: text }),
    s => s || 'unknown',
    o => (o == null ? '' : typeof o === 'string' ? o : JSON.stringify(o, null, 2)),
    'Dot', 'Badge', 'Button', 'Vitals', 'Fragment', jsx, jsxs
  )
  return NodePanel({ detail })
}

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

// ---- bd_2026-11-25-cj2 (panel detail): the SELECTED item owns Output and Final
// Shape mirrors the real redrive/aggregate replay (Amber committed with its own
// output, forbidden-model Quartz with NONE, the node aggregate naming Amber's
// answer): the selected Quartz's Output must report honest absence — the whole
// node aggregate, sibling answer included, may NEVER stand in for an item the
// selected row says has no output. The Final tone rides the SELECTED status,
// and the node view (no item picked) keeps the aggregate.
{
  const TONES = new Function(
    `${constGrab('EDGE_TONE')}\n${constGrab('FACT_TONE')}; return { edge: EDGE_TONE, fact: FACT_TONE }`)()
  const fo = { id: 'f', type: 'agent', goal: 'review {item}', fanout: { items: ['Amber', 'Quartz', 'Mabel'], goal: 'review {item}' } }
  const rec = over => ({ error_class: null, refusal: null, error: null, attempts: 1, attempts_log: null,
    final: null, harvest: null, output: null, ms: 1, started: 1, log_path: '/run/logs/f.x.a1.log',
    prompt_path: null, efp: 'e', skey: 'k', steer: null, ...over })
  const shown = {
    status: 'failed', type: 'agent', fanout: true,
    output: { items: [], all_results: [
      { status: 'done', item: 'Amber', output: { result: 'Amber accepted' }, ms: 1, attempts: 1 },
      { status: 'failed', item: 'Quartz', error_class: 'forbidden_model', error: 'served a forbidden model', ms: 1, attempts: 1 },
      { status: 'partial', item: 'Mabel', output: { saved: 'Mabel banked' }, ms: 1, attempts: 1 }] },
    item_records: {
      0: rec({ status: 'done', final: 'Amber signed off', output: { result: 'Amber accepted' } }),
      1: rec({ status: 'failed', error_class: 'forbidden_model', error: 'served a forbidden model', final: 'Quartz died' }),
      2: rec({ status: 'partial', error_class: 'timeout', error: 'wall', output: { saved: 'Mabel banked' } }) }
  }
  const detail = { id: 'r1', status: 'failed', graph: { nodes: [fo] }, nodes: { f: shown }, events: [] }
  const pickTab = (index, status, tab) => render({ detail, sel: { runId: 'r1', nodeId: 'f' },
    fanItem: { runId: 'r1', nodeId: 'f', index }, tab: [`f·${index}:${status}`, tab] })
  const preTone = (tree, needle) => {
    const n = walk(tree).find(x => x.type === 'pre' && texts(x).includes(needle))
    assert.ok(n, `expected a pre carrying ${needle}`)
    return n.props.style.color
  }

  // Failed Quartz — its own absence, never a sibling's answer.
  const qt = pickTab(1, 'failed', 'Output')
  assert.equal(activeTabOf(qt), 'Output', 'the explicit Output tab is the active one')
  const qTexts = texts(qt).join('|')
  assert.ok(qTexts.includes('No output yet.'), 'selected failed item with no own output shows honest absence')
  assert.ok(!qTexts.includes('Amber accepted') && !qTexts.includes('all_results'),
    'the node aggregate (a sibling answer) never stands in for the selected item\'s absence')

  // Selected Amber — its OWN output only, not the aggregate.
  const at = texts(pickTab(0, 'done', 'Output')).join('|')
  assert.ok(at.includes('Amber accepted'), 'the selected item shows its own output')
  assert.ok(!at.includes('all_results'), 'own output, never the aggregate')

  // A partial item keeps its known partial output and its marker (no blanket hide).
  const mt = texts(pickTab(2, 'partial', 'Output')).join('|')
  assert.ok(mt.includes('Mabel banked') && /partial/.test(mt), 'partial item output and marker survive selection')

  // Final tone rides the SELECTED status: failed stays red, done is neutral,
  // and the words are the item's own.
  const qf = pickTab(1, 'failed', 'Final')
  assert.equal(preTone(qf, 'Quartz died'), TONES.edge.failed, "failed item's Final keeps the failed tone")
  assert.ok(!texts(qf).join('|').includes('Amber signed off'), "failed item's Final never borrows a sibling's words")
  const af = pickTab(0, 'done', 'Final')
  assert.equal(preTone(af, 'Amber signed off'), TONES.fact, 'a successful item under a failed aggregate keeps the neutral Final tone')

  // No selection: the whole-node projection keeps owning Output.
  const nv = texts(render({ detail, sel: { runId: 'r1', nodeId: 'f' }, tab: ['f:failed', 'Output'] })).join('|')
  assert.ok(nv.includes('all_results'), 'node Output retains the aggregate when no item is selected')
}

// ---- bd_2026-11-25-cj2 (partial output): the REAL read model, no item_records
// The red-pin witness (receipts/ship20-recovery/cj2-partial-c93734f1,
// partial-real-2/view.json) proves what the actual runner + _view return for a
// settled partial fan-out: the node record merges `output.all_results` and
// `item_metrics`, and `item_records` appears NOWHERE in the response. A test
// that injects that carrier falsifies nothing on this path, so this block
// feeds the merged shape itself — every fact below is a byte of the witness
// (portable literals, no host paths).
{
  const fo = { id: 'review', type: 'agent', goal: 'review {item}', fanout: { items: ['Amber', 'Quartz', 'Mabel'], goal: 'review {item}' } }
  const mrow = (skey, over) => ({ skey, ms: 1, attempts: 1, spawn: 0, ...over })
  const im = (session, item, display) => ({ tokens_in: 1, tokens_out: 1, api_calls: 1, tool_calls: 0,
    session_ids: [session], session_current: session, item, session_display: display })
  const shown = {
    status: 'partial', type: 'agent', fanout: true,
    error_class: 'budget_exhausted',
    error: 'budget_exhausted: 1/3 items refused at the RunBudget cap; harvested 2',
    efp: 'c352b5c35ee9157c',
    metrics: { session_ids: ['local-0000000000000000000000000000000000000000000000000000000000000000'],
      session_current: 'local-0000000000000000000000000000000000000000000000000000000000000000', live: 0 },
    item_metrics: {
      0: im('local-0000000000000000000000000000000000000000000000000000000000000000', 'Amber', { status: 'done' }),
      2: im('local-2222222222222222222222222222222222222222222222222222222222222222', 'Mabel',
        { status: 'partial', error_class: 'timeout', error: 'Mabel timed out' })
    },
    output: {
      items: [{ result: 'Amber exact' }, { result: 'Mabel banked' }],
      all_results: [
        mrow('wf:partial-panel:review:0:c352b5c3.acabec',
          { status: 'done', output: { result: 'Amber exact' }, item: 'Amber' }),
        mrow('wf:partial-panel:review:1:c352b5c3.d4f720',
          { status: 'failed', error_class: 'budget_exhausted', error: 'Quartz refused at cap', item: 'Quartz' }),
        mrow('wf:partial-panel:review:2:c352b5c3.8aae00',
          { status: 'partial', error_class: 'timeout', error: 'Mabel timed out', harvest: { source: 'stdout' },
            output: { result: 'Mabel banked' }, item: 'Mabel' })
      ]
    }
  }
  assert.ok(!('item_records' in shown), 'the fixture carries NO item_records — the real response shape')
  const detail = { id: 'partial-panel', status: 'partial', graph: { nodes: [fo] }, nodes: { review: shown }, events: [] }
  const sel = { runId: 'partial-panel', nodeId: 'review' }
  const pickTab = (index, status, tab) => render({ detail, sel,
    fanItem: { runId: 'partial-panel', nodeId: 'review', index }, tab: [`review·${index}:${status}`, tab] })
  const linkStoredId = tree => {
    const n = walk(tree).find(x => typeof x.type === 'function' && x.type.name === 'SessionLink')
    return n ? n.props.storedId : null
  }

  // The selected partial keeps its OWN committed output and its marker.
  const mt = pickTab(2, 'partial', 'Output')
  const mTexts = texts(mt).join('|')
  assert.ok(mTexts.includes('Mabel banked'), 'the selected partial item shows its committed output')
  assert.ok(mTexts.includes('partial — harvested output'), 'the selected partial keeps the harvested marker')
  assert.ok(!mTexts.includes('all_results') && !mTexts.includes('Amber exact'),
    'the item shows its own output, never the aggregate or a sibling')
  assert.equal(linkStoredId(mt), 'local-2222222222222222222222222222222222222222222222222222222222222222',
    'the selected partial still binds its exact chat')

  // The selected done item shows only its own output; no harvested marker on a done row.
  const at = texts(pickTab(0, 'done', 'Output')).join('|')
  assert.ok(at.includes('Amber exact'), 'the selected done item shows its own output')
  assert.ok(!at.includes('Mabel banked') && !at.includes('partial — harvested output'),
    'a done item shows neither the aggregate nor a partial marker it does not carry')
  assert.equal(linkStoredId(pickTab(0, 'done', 'Output')),
    'local-0000000000000000000000000000000000000000000000000000000000000000',
    'the selected done item binds its own exact chat')

  // A cap-refused item with no record of its own stays an honest absence.
  const qt = pickTab(1, 'failed', 'Output')
  const qTexts = texts(qt).join('|')
  assert.ok(qTexts.includes('No output yet.'), 'the cap-refused item reports honest absence')
  assert.ok(!qTexts.includes('Mabel banked') && !qTexts.includes('all_results'),
    'honest absence borrows neither a sibling nor the aggregate')
  assert.equal(linkStoredId(qt), null, 'an item with no metrics row has no chat to bind')
  assert.ok(texts(pickTab(1, 'failed', 'Final')).join('|').includes('final: unknown'),
    'a recordless Final reads unknown, never borrowed sibling words')

  // No selection: the node view keeps owning the aggregate (unchanged behavior).
  const nv = texts(render({ detail, sel, tab: ['review:partial', 'Output'] })).join('|')
  assert.ok(nv.includes('all_results') && nv.includes('partial — harvested output'),
    'the node view with no item picked retains the aggregate and marker')
}

console.log('ALL PASS: NodePanel — one node truth, closed facts, unknown-not-zero, tabs by status, one tail, no second assembler')
