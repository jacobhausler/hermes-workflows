// bd_2026-11-13-s20-cj2-recovery (selected Final): the SELECTED item's Final
// tab must carry the selected record's own committed `final`, through the same
// verified row path its Output, error and chat already ride.
//
// The blocking witness (cj2-qualify receipt, tabs-distinct-both): a real
// settled partial full view (runner + dashboard _view, `--distinct-final`)
// carries per-item committed Finals on the certified `all_results` rows
// (Mabel/MABEL_OWN_FINAL partial, Amber/AMBER_SIBLING_FINAL done, cap-refused
// Quartz with none) and NO `item_records` carrier anywhere. The panel projected
// the row's output/error but dropped `final`, so BOTH distinct committed Finals
// rendered as an honest-unknown absence — a product red, not a fixture-
// injection artifact.
//
// Harness law (same offline rules the witness used): the ACTUAL plugin source
// is imported whole with only import shims and added visibility exports — no
// function-extraction proxy stands in for the real module, the real ItemChips/
// NodePanel/SessionLink click handlers run against observed SDK calls, and no
// item_records is ever injected. Fixtures are portable literals (the witness's
// observed bytes, no host paths).
import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const dir = mkdtempSync(join(tmpdir(), 'wf-selected-final-'))
const write = (name, src) => writeFileSync(join(dir, name + '.mjs'), src)
globalThis.calls = []
write('sdk', `
export function atom(value) { return {get:()=>value,set:v=>{value=v}} }
export const Badge='Badge', Button='button', cn=(...x)=>x.join(' '), Codicon='Codicon',
 COMPOSER_AREAS={}, EmptyState='EmptyState', PANES_AREA='panes', PanelListRow='PanelListRow',
 PanelPill='PanelPill', PanelSectionLabel='PanelSectionLabel', ROUTES_AREA='routes',
 ScrollArea='ScrollArea', StatusDot='StatusDot', TRANSCRIPT_DIRECTIVE_AREA='directive'
const track = name => (...args) => { globalThis.calls.push([name,...args]) }
export const host={openSession:track('openSession'),navigate:track('navigate'),notify:track('notify'),
 composer:{insertText:track('insertText'),submit:track('submit')},
 state:{focusedSessionId:atom(''),focusedStoredSessionId:atom('')}}
export const useValue=x=>x.get(), useQuery=()=>({isPending:false,data:null,refetchInterval:false,queryKey:[],queryFn:()=>({})}),
 useMutation=()=>({mutate:track('mutate')}), useQueryClient=()=>({invalidateQueries:track('invalidateQueries')})
`)
write('react', `
export const useEffect=()=>{}, useId=()=>'witness', useRef=()=>({current:null}),
 useState=x=>{
 const panel=(new Error().stack.split('\\n')[2] || '').includes('NodePanel')
 return panel ? [globalThis.tab ?? x,v=>{globalThis.tab=v}] : [typeof x==='function'?x():x,()=>{}]
 }
`)
write('jsx', `export const jsx=(type,props)=>({type,props}),jsxs=jsx,Fragment='fragment'`)
write('product', readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')
  .replace("'@hermes/plugin-sdk'", "'./sdk.mjs'")
  .replace("'react'", "'./react.mjs'")
  .replace("'react/jsx-runtime'", "'./jsx.mjs'")
  + '\nexport { NodePanel, $fanItem, EDGE_TONE, FACT_TONE }\n')
const { NodePanel, $selNode, $fanItem, markNavFocus, EDGE_TONE, FACT_TONE } = await import(join(dir, 'product.mjs'))

const material = n => !n || typeof n !== 'object' ? n : Array.isArray(n) ? n.map(material)
  : typeof n.type === 'function' ? material(n.type(n.props))
  : { ...n, props: { ...n.props, children: material(n.props?.children) } }
const walk = function* (n) {
  if (!n || typeof n !== 'object') return
  if (Array.isArray(n)) { for (const i of n) yield* walk(i); return }
  yield n
  yield* walk(n.props?.children)
}
const text = n => Array.isArray(n) ? n.map(text).join(' ') : typeof n === 'string' ? n : textMaybe(n?.props?.children)
const textMaybe = n => n == null ? '' : text(n)
const buttons = tree => [...walk(tree)].filter(n => n.type === 'button').map(n => n.props)
const chipButtons = tree => buttons(tree).filter(p => Array.isArray(p.children) && p.children[0]?.type === 'StatusDot')
const show = view => material(NodePanel({ detail: view }))
const norm = s => s.trim().replace(/\s+/g, ' ')
const UNKNOWN_FINAL = /^final:? unknown$/ // the sectioned honest-absence rendering

// One pass over the ACTUAL tab and chat controls on a single snapshot state:
// click the item chip, then each of the four tabs, then the recorded-chat link.
// `text` is the tab column; `body` drops the four tab-button labels so a
// substring can never match the '…Prompt Final' tab strip instead of content.
async function witness(view, nodeId, index) {
  $selNode.set({ runId: view.id, nodeId }); $fanItem.set(null); markNavFocus(null); globalThis.tab = null; calls.length = 0
  const chips0 = chipButtons(show(view))
  const title = index === null ? null : chips0[index]?.title
  if (index !== null) {
    assert.ok(chips0[index], `chip ${index}`)
    chips0[index].onClick({ stopPropagation() {} })
    assert.deepEqual($fanItem.get(), { runId: view.id, nodeId, index }, 'the real chip selects the item')
  }
  const tabs = {}
  let finalTone
  for (const name of ['Log', 'Output', 'Final', 'Prompt']) {
    globalThis.tab = [`$${name}`, name] // fresh panel state each render; re-click to land the tab
    const tree = show(view)
    const tab = buttons(tree).find(p => p.children === name)
    assert.ok(tab, name)
    tab.onClick()
    const after = show(view)
    assert.ok(buttons(after).find(p => p.children === name).style.border.includes('--ui-accent'), `active ${name}`)
    const body = after.props.children[1].props.children.props.children[1]
    const full = norm(text(body))
    tabs[name] = { text: full, body: norm(full.replace(/^(Log Output Prompt Final) /i, '')).replace(/ (Log Output Prompt Final) /gi, ' ') }
    // The Final body pre sits in its `final`-labelled section inside the tab
    // column (after.children[1]). The Output dump is itself a JSON pre whose
    // nested keys can read 'final', and other sections carry their own pres,
    // so the section is bounded by its label and the next one.
    if (name === 'Final') {
      const nodes = [...walk(body)]
      const isLabel = x => x === 'final' || (typeof x === 'object' && x !== null && x.props?.children === 'final')
      const at = nodes.findIndex(isLabel)
      const next = at < 0 ? -1 : nodes.findIndex((x, i) => i > at && isLabel(x))
      finalTone = at < 0 ? undefined
        : (nodes.slice(at + 1, next < 0 ? nodes.length : next).find(x => x.type === 'pre')?.props.style?.color) ?? null
    }
  }
  const tree = show(view)
  const badges = [...walk(tree.props.children[0])].filter(x => x.type === 'Badge').map(text)
  const chat = buttons(tree).find(p => p.children === 'open recorded chat')
  if (chat) await chat.onClick()
  return { tabs, badges, title, finalTone, calls: [...calls] }
}

const MABEL = 'MABEL_OWN_FINAL', AMBER = 'AMBER_SIBLING_FINAL'
const CHAT_MABEL = 'local-' + '2'.repeat(64), CHAT_AMBER = 'local-' + '0'.repeat(64)
const FAILED_TONE = EDGE_TONE.failed
assert.ok(FAILED_TONE.includes('--ui-danger'), 'the failed tone is the EDGE_TONE.failed token itself')

// The modern read model: bytes of the real settled partial full view (rows
// carry skeys and Finals; the node flat `final` is the 'unknown' sentinel).
const row = (skey, over) => ({ skey, ms: 1, attempts: 1, spawn: 0, served_model: 'fake', served_billing_provider: null, attempts_log: [], ...over })
const im = (session, item, display) => ({
  tokens_in: 1, tokens_out: 1, cache_read: 0, reasoning: 0, api_calls: 1, tool_calls: 0,
  cost: 0.0, attempts: 1, children: 1, live: 0, last_activity: null, last_desc: null,
  models: ['fake'], session_ids: [session], session_current: session, item, session_display: display
})
const fo = { id: 'review', type: 'agent', goal: 'review {item}', fanout: { items: ['Amber', 'Quartz', 'Mabel'], goal: 'review {item}' } }
const modernNode = (amberFinal, mabelFinal) => ({
  type: 'agent', status: 'partial', after: [], fanout: true, disposition: 'PARTIAL', stale_of_amend: null,
  error_class: 'budget_exhausted', refusal: 'unknown',
  error: 'budget_exhausted: 1/3 items refused at the RunBudget cap; harvested 2',
  attempts: 'unknown', attempts_log: 'unknown', final: 'unknown', harvest: 'unknown',
  efp: 'c352b5c35ee9157c', skey: 'unknown', steer: null, ms: 'unknown', started: 'unknown',
  log_path: 'unknown', prompt_path: 'unknown',
  output: {
    items: [{ result: 'Amber exact' }, { result: 'Mabel banked' }],
    all_results: [
      row('wf:partial-panel:review:0:c352b5c3.5be48a', { status: 'done', item: 'Amber', output: { result: 'Amber exact' }, ...(amberFinal ? { final: amberFinal } : {}) }),
      row('wf:partial-panel:review:1:c352b5c3.1e7ee5', { status: 'failed', item: 'Quartz', error_class: 'budget_exhausted', error: 'Quartz refused at cap', metrics: { tokens_in: null, tokens_out: null, api_calls: null, tool_calls: null, served_model: null, model_source: null }, served_model: null }),
      row('wf:partial-panel:review:2:c352b5c3.95fbff', { status: 'partial', item: 'Mabel', error_class: 'timeout', error: 'Mabel timed out', harvest: { source: 'stdout' }, output: { result: 'Mabel banked' }, ...(mabelFinal ? { final: mabelFinal } : {}) })
    ]
  },
  metrics: {
    tokens_in: 2, tokens_out: 2, cache_read: 0, reasoning: 0, api_calls: 2, tool_calls: 0,
    cost: 0.0, attempts: 2, children: 2, live: 0, last_activity: null, last_desc: null, models: ['fake'],
    session_ids: [CHAT_AMBER, CHAT_MABEL], session_current: CHAT_MABEL, scope: 'cumulative'
  },
  item_metrics: {
    0: im(CHAT_AMBER, 'Amber', { status: 'done' }),
    2: im(CHAT_MABEL, 'Mabel', { status: 'partial', error_class: 'timeout', error: 'Mabel timed out' })
  }
})
const viewFor = nodes => ({ id: 'partial-panel', status: 'partial', graph: { nodes: [fo] }, nodes: { review: nodes }, events: [] })
const strip = s => JSON.parse(JSON.stringify(s, (k, v) => k === 'log_path' ? 'runner.log' : v))

// ---- the blocking check: each selected record shows its OWN committed Final --
const committed = viewFor(modernNode(AMBER, MABEL))
assert.ok(!('item_records' in committed.nodes.review), 'the real response shape carries NO item_records — nothing was injected')
{
  const mabel = await witness(committed, 'review', 2)
  assert.match(mabel.tabs.Output.body, /partial — harvested output/)
  assert.match(mabel.tabs.Output.body, /Mabel banked/)
  assert.doesNotMatch(mabel.tabs.Output.body, /all_results|Amber exact/)
  assert.equal(mabel.title, 'Mabel timed out', "the chip carries the item's own error")
  assert.match(mabel.tabs.Final.body, new RegExp(MABEL), 'the selected partial shows its own committed Final')
  assert.doesNotMatch(mabel.tabs.Final.body, new RegExp(`${AMBER}|all_results|unknown`), 'no sibling, no aggregate, no unknown cover')
  // Words AND tone ride the same selected record (shipped law: only a `failed`
  // status wears the failed tone; a harvested partial keeps the neutral one).
  assert.equal(mabel.finalTone, FACT_TONE, "the partial item's own status decides the Final tone")
  assert.deepEqual(mabel.calls, [['openSession', CHAT_MABEL, { intent: 'in-place' }]], 'Final, chat and marker all ride the SAME selected execution')
}
{
  const amber = await witness(committed, 'review', 0)
  assert.match(amber.tabs.Output.body, /Amber exact/)
  assert.doesNotMatch(amber.tabs.Output.body, /Mabel banked|all_results|harvested output/)
  assert.match(amber.tabs.Final.body, new RegExp(AMBER), 'the selected done sibling shows its own committed Final')
  assert.doesNotMatch(amber.tabs.Final.body, new RegExp(`${MABEL}|all_results|unknown`))
  assert.deepEqual(amber.calls, [['openSession', CHAT_AMBER, { intent: 'in-place' }]], 'the sibling binds its own exact chat')
}
{
  const quartz = await witness(committed, 'review', 1)
  assert.match(quartz.tabs.Output.body, /No output yet\./)
  assert.match(quartz.tabs.Final.body, UNKNOWN_FINAL, 'a record with no committed Final stays an honest unknown')
  assert.doesNotMatch(quartz.tabs.Final.body, new RegExp(`${MABEL}|${AMBER}|all_results`), 'never borrows a sibling Final')
  assert.ok(!quartz.finalTone, 'an honest unknown is a plain-text box — no styled Final section is built')
  assert.equal(quartz.title, 'Quartz refused at cap')
  assert.deepEqual(quartz.calls, [], 'no metrics row, no chat to bind')
}

// ---- read-order and stale-final pairs: same snapshot, independent of order --
// Order A is the witness key order (output before item_metrics, rows 0,1,2);
// order B serialises item_metrics first with the ids and Finals exchanged
// between the two committed rows — each row keeps its OWN skey, so no tab may
// move and the (skey, final) pairing must survive. A stale or reordered read
// must never lend another row's Final.
{
  const a = strip(await witness(viewFor(modernNode(AMBER, MABEL)), 'review', null))
  const swapped = modernNode(MABEL, AMBER)
  const nodeB = { item_metrics: swapped.item_metrics, output: swapped.output }
  for (const k of Object.keys(swapped)) if (!['item_metrics', 'output'].includes(k)) nodeB[k] = swapped[k]
  const b = strip(await witness(viewFor(nodeB), 'review', null))
  const SLOTS = { 0: '5be48a', 2: '95fbff' }
  const weld = (snap, tail) => {
    const m = snap.tabs.Output.text.match(new RegExp(`"skey": "[^"]*${tail}".*?"final": "[A-Z_]+"`))
    assert.ok(m, `row for ${tail} keeps its skeyed Final slot`)
    return m[0].slice(m[0].indexOf('"final": "'))
  }
  const aW = Object.values(SLOTS).map(t => weld(a, t))
  const bW = Object.values(SLOTS).map(t => weld(b, t))
  assert.deepEqual([...aW].sort(), [...bW].sort(), 'the two reads carry the SAME committed Finals')
  assert.notEqual(aW[0], bW[0], 'the deliberate (id, final) exchange moves the pair, never splits it')
  for (const [tag, snap] of [['A', a], ['B', b]]) {
    assert.match(snap.tabs.Output.body, /all_results/)
    assert.match(snap.tabs.Output.body, /partial — harvested output/, `aggregate ${tag} keeps the harvested marker`)
    assert.match(snap.tabs.Final.body, UNKNOWN_FINAL, `no pick (${tag}): the node's own absent Final stays unknown despite item Finals`)
    // Node-level view: the chat follows the payload's node-current id in both
    // reads — it never tracks a row swap positionally (the exchanged ids live
    // only on the item rows and their metrics; per-item pairing is proven by
    // the picked-row blocks above).
    assert.deepEqual(snap.calls, [['openSession', CHAT_MABEL, { intent: 'in-place' }]], `the node view (${tag}) binds its own current session`)
  }
  assert.notEqual(a.tabs.Output.text, b.tabs.Output.text, 'the exchanged payloads differ in content only')
  assert.equal(a.tabs.Log.body + a.tabs.Final.body + a.tabs.Prompt.body + a.badges.join(),
               b.tabs.Log.body + b.tabs.Final.body + b.tabs.Prompt.body + b.badges.join(),
               'record key order alone moves no tab')

  // A stale committed Final at the same width: the OLD value only exists on
  // the row that names it. With Mabel's key absent, the panel must not
  // resurrect any Final for that row and must not move Amber's onto it.
  const stale = await witness(viewFor(modernNode(AMBER, null)), 'review', 2)
  assert.match(stale.tabs.Output.body, /Mabel banked/, 'the output is unchanged by the absent Final')
  assert.match(stale.tabs.Final.body, UNKNOWN_FINAL, 'an item whose own record committed no Final reads unknown')
  assert.doesNotMatch(stale.tabs.Final.body, new RegExp(`${AMBER}|${MABEL}`), 'no old-or-sibling Final is borrowed over the absence')
  const both = await witness(viewFor(modernNode(AMBER, MABEL)), 'review', 2)
  // Same node, two reads (Final present vs absent on the selected row): the
  // other tabs are untouched, and the Final tab differs ONLY by its payload —
  // one styled section carrying the committed text, versus the plain-text
  // honest absence (the shipped renderers differ in form: `final <value>` pre
  // vs a `final: unknown` box — the payloads above pin each exactly).
  assert.ok(both.tabs.Final.body.includes(MABEL) && !both.tabs.Final.body.includes(AMBER))
  assert.ok(UNKNOWN_FINAL.test(stale.tabs.Final.body) && !new RegExp(`${MABEL}|${AMBER}`).test(stale.tabs.Final.body))
  assert.equal(both.tabs.Output.text, stale.tabs.Output.text, 'the row\'s committed Output is identical with and without a Final')
  assert.equal(both.tabs.Log.text + both.tabs.Prompt.text + both.badges.join(),
               stale.tabs.Log.text + stale.tabs.Prompt.text + stale.badges.join(), 'no other tab or badge moves')
}

// ---- historical compatibility: status-bearing legacy item rows ride the path
{
  const legacy = {
    type: 'agent', status: 'done', after: [], fanout: true,
    error_class: 'unknown', refusal: 'unknown', error: 'unknown', attempts: 'unknown', attempts_log: 'unknown',
    final: 'AGGREGATE_CLOSE_OUT', harvest: 'unknown', efp: 'e', skey: 'unknown', steer: null,
    ms: 1, started: 1, log_path: 'runner.log', prompt_path: null,
    output: {
      items: [
        { status: 'done', item: 'Amber', output: { result: 'A1' }, final: 'LEGACY_AMBER_FINAL' },
        { status: 'failed', item: 'Quartz', error_class: 'forbidden_model', error: 'served a forbidden model', final: 'LEGACY_QUARTZ_FINAL' },
        { status: 'done', item: 'Mabel', output: { result: 'M2' } }
      ]
    }
  }
  const legacyView = { id: 'r-legacy', status: 'done', graph: { nodes: [{ ...fo }] }, nodes: { review: legacy }, events: [] }
  const q = await witness(legacyView, 'review', 1)
  assert.match(q.tabs.Final.body, /LEGACY_QUARTZ_FINAL/, 'a legacy committed Final rides the same row path')
  assert.doesNotMatch(q.tabs.Final.body, /LEGACY_AMBER_FINAL/)
  assert.equal(q.finalTone, FAILED_TONE, "the legacy failed row's own status decides the Final tone")
  const m = await witness(legacyView, 'review', 2)
  assert.match(m.tabs.Final.body, UNKNOWN_FINAL, 'a legacy row without Final stays unknown')
  assert.ok(!m.finalTone, 'an honest unknown is a plain-text box — no styled Final section is built')
  const node = await witness(legacyView, 'review', null)
  assert.match(node.tabs.Final.body, /AGGREGATE_CLOSE_OUT/, "no pick: the node's own committed Final still owns the tab")
  assert.doesNotMatch(node.tabs.Final.body, /LEGACY_/)
}

console.log('ALL PASS: selected-item Final rides its own record — distinct committed text, own tone, exact chat, honest unknown, order-independent')
