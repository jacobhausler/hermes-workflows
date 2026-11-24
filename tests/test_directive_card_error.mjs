// Pin: the directive card must never degrade to dead text when a refetch
// fails with cached data, and the never-fetched error branch must be clickable
// (retry), not inert. Root cause of the flip-flop: `if (error)` ran BEFORE
// `if (!data)`, so any transient auth/transport blip evicted a good pill into
// `workflow ${id}` dead text — and the error span had no click affordance.
// Ship 2.0 (bd_2026-11-13-1bm): the model behind these laws is the RC
// cardModel — data-wins, stale-marked and retry laws ride the new renderer
// unchanged; the stub mirrors the RC shape (statusWord), not the retired
// one-line collapsedLine. The RC disclosure DOM is pinned behaviorally here
// (stateful useState, tree walk): two sibling native buttons, aria pair, the
// body region mounted only when expanded, and NO nested buttons anywhere.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const plugin = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// Extract the real DirectiveBody (and DirectiveCard) by brace-matching (house pattern).
function grabSource(marker) {
  const start = plugin.indexOf(marker)
  assert.notEqual(start, -1, `${marker} exists`)
  let depth = 0, end = start + marker.length - 1 // the body's opening brace
  for (; end < plugin.length; end++) {
    if (plugin[end] === '{') depth++
    else if (plugin[end] === '}' && --depth === 0) { end++; break }
  }
  return plugin.slice(start, end)
}
const src = grabSource('function DirectiveBody({ id }) {')

// stateful useState slot: the toggle law needs a render BEYOND the initial
// collapsed state — a stateless stub could never prove the disclosure opens.
function render(queryState, st = { open: false }) {
  const jsx = (type, props) => ({ type, props })
  const invalidated = []
  const runQuery = () => queryState
  const fn = new Function(
    'jsx', 'jsxs', 'useQuery', 'useQueryClient', 'useValue', 'useTick', 'useState', 'useId',
    'Dot', 'cardModel', 'host', '$selRun', 'Q', 'runQuery', '$fanOpen', '$fanItem',
    'fanOpenFor', 'fanItems', 'fanPickedRow', 'MiniGraph', 'FanStrip',
    `${src}; return DirectiveBody`
  )(
    jsx,
    (type, props) => ({ type, props, many: true }),
    qfn => qfn,
    () => ({ invalidateQueries: q => invalidated.push(q) }),
    () => false,
    () => {},
    init => [st.open ?? (typeof init === 'function' ? init() : init),
      v => { st.open = typeof v === 'function' ? v(st.open) : v }],
    () => 'wf-card-body-1',
    () => jsx('dot', {}),
    (run, stale) => ({
      name: 'run',
      statusWord: `run · done · 2/2${stale ? ' · Disconnected · last known Finished' : ''}`,
      tone: {}, census: ['2/2 nodes', '— notices'], metrics: ['Model —'], expanded: false
    }),
    { navigate: () => {} },
    { set: () => {} },
    ['hermes-workflows'],
    () => queryState,
    { get: () => false },
    { get: () => null },
    () => null, () => null, () => null, 'MiniGraph', 'FanStrip'
  )
  const out = fn({ id: 'wf-1' })
  return { out, invalidated, st }
}

// 1) data present + error present -> the RC pill renders (data wins), not dead text.
{
  const { out } = render({ data: { id: 'wf-1', status: 'done' }, error: new Error('401'), isFetching: true })
  assert.notEqual(out.props.children?.toString?.(), undefined)
  const text = JSON.stringify(out)
  assert.ok(!text.includes('workflow…'), 'cached data must not render the loading branch')
  assert.ok(!/"workflow \(wf-1\)"/.test(text), 'cached data must not render the error dead-text branch')
  assert.ok(text.includes('run · done · 2/2 · Disconnected · last known Finished'),
    'cached data over a refetch error renders the pill in the DISCONNECTED state (Cached directive 04: last-good is kept, liveness never inferred)')
}

// 1b) clean fetch (no error) -> the same pill WITHOUT the stale word.
{
  const { out } = render({ data: { id: 'wf-1', status: 'done' }, error: null, isFetching: false })
  const text = JSON.stringify(out)
  assert.ok(text.includes('run · done · 2/2'), 'clean pill renders')
  assert.ok(!text.includes('Disconnected'), 'no disconnect word without a fetch error')
}

// 2) no data ever + error -> clickable RETRY button carrying the id.
{
  const { out, invalidated } = render({ data: undefined, error: new Error('401'), isFetching: false })
  assert.equal(out.type, 'button', 'error branch must be a button, never inert chrome')
  assert.match(String(out.props.children), /wf-1/, 'error branch keeps the id visible')
  out.props.onClick({})
  assert.equal(invalidated.length, 1, 'click invalidates the run query (retry)')
  assert.deepEqual(invalidated[0].queryKey, ['hermes-workflows', 'run', 'wf-1'])
}

// 3) no data, no error -> quiet loading span (unchanged).
{
  const { out } = render({ data: undefined, error: null, isFetching: false })
  assert.equal(out.type, 'span')
  assert.equal(out.props.children, 'workflow…')
}

// 4) error branch while retrying shows the loading label inside the button.
{
  const { out } = render({ data: undefined, error: new Error('401'), isFetching: true })
  assert.equal(out.type, 'button')
  assert.equal(out.props.children, 'workflow…')
}

// 5) RC disclosure DOM (behavior, via the stateful stub): the container is not
//    a click surface; expand and open are SIBLING native buttons; the aria
//    pair targets the body region that mounts only when expanded; the identity
//    row never remounts, so its buttons are the same objects across the toggle;
//    no button is ever nested in another button.
{
  const walk = n => Array.isArray(n) ? n.flatMap(walk)
    : n && typeof n === 'object' ? [n, ...Object.values(n.props || {}).flatMap(walk)] : []
  const q = { data: { id: 'wf-1', status: 'done' }, error: null, isFetching: false }
  const st = { open: false }
  const { out: collapsed } = render(q, st)
  assert.equal(collapsed.type, 'div', 'the container is a plain div')
  assert.equal(collapsed.props.onClick, undefined, 'the container is NOT a click surface (one click, one effect)')
  assert.equal(collapsed.props.role, undefined, 'no role=button/link container (the 1.4-era whole-pill click is retired)')
  const buttons = walk(collapsed).filter(n => n.type === 'button')
  assert.equal(buttons.length, 2, `collapsed pill has exactly two buttons: ${buttons.map(b => b.props['aria-label'])}`)
  const expand = buttons.find(b => b.props['data-wf-expand'] === '')
  const open = buttons.find(b => b.props['data-wf-open'] === '')
  assert.ok(expand && open, 'disclosure and full-view are distinct hook-addressable buttons')
  assert.equal(expand.props['aria-expanded'], false, 'collapsed carries aria-expanded=false')
  assert.notEqual(String(expand.props.onClick), String(open.props.onClick), 'one click, one effect: the two buttons carry distinct handlers')
  const controls = expand.props['aria-controls']
  assert.ok(typeof controls === 'string' && controls.length > 0, 'aria-controls names the body region')
  assert.ok(!walk(collapsed).some(n => n.props?.id === controls), 'the body region is absent while collapsed')
  for (const b of buttons) assert.equal(walk(b.props.children).some(n => n.type === 'button'), false, 'no button nests another button')

  expand.props.onClick()
  assert.equal(st.open, true, 'the disclosure handler flips the state')
  const { out: expanded } = render(q, st)
  const body = walk(expanded).find(n => n.props?.id === controls)
  assert.ok(body, 'aria-controls resolves to the mounted body region after expand')
  const expandBtns = walk(expanded).filter(n => n.type === 'button' && n.props['data-wf-expand'] === '')
  assert.equal(expandBtns.length, 1, 'the identity row (and its disclosure) renders in BOTH states — the toggle never remounts it')
  const expand2 = expandBtns[0]
  assert.equal(expand2.props['aria-expanded'], true, 'expanded carries aria-expanded=true (same identity row, never remounted)')
  assert.ok(JSON.stringify(expanded).includes('Model —'), 'the expanded body renders the word row')

  expand2.props.onClick()
  const { out: recollapsed } = render(q, st)
  assert.equal(st.open, false, 'the same disclosure collapses in place')
  assert.ok(!walk(recollapsed).some(n => n.props?.id === controls), 'collapse unmounts the body region')
}

// 6) malformed directive id -> inert label, zero fetch (DirectiveCard guard).
{
  const jsx = (type, props) => ({ type, props })
  const card = new Function('ID_OK', 'jsx', 'DirectiveBody',
    `${grabSource('function DirectiveCard({ id }) {')};\nreturn DirectiveCard`)(
    /^[\w.-]+$/, jsx, () => ({ type: 'DirectiveBody' }))(
    { id: 'wf/../x' })
  assert.equal(card.type, 'span', 'a malformed id renders the inert label, no query')
  assert.equal(card.props.children, 'workflow')
}

console.log('ALL PASS: directive card — data wins over error, error branch retries, RC disclosure DOM (siblings, aria pair, no nesting), malformed id inert')
