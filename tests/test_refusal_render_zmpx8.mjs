// est-zmpx8 — the refusal stamp gets a desktop render surface.
//
// Residual from #584 peer review: `refusal` is a wfcommon.FACT_KEYS row (est-t7yod),
// so a spent-cap boot carries refusal=lifetime_cap_spent through node_facts and the
// door's A2 facts — but the Explorer V2 NodePanel renders node facts by NAMED sections
// (plugin.js) and had no row for it: the stamp rode the payload unshown. This lane
// renders the ACTUAL NodePanel (extracted from desktop/plugin.js, stub JSX — the
// test_node_panel.mjs / test_wf_qa_render_group.mjs idiom) against facts captured
// LIVE from the real read model (tests/fixtures/refusal_capture.py → wfcommon.node_facts),
// so the payload is never hand-typed.
//
// Pins:
//   P1 (the acceptance) a spent-cap boot's panel shows refusal=lifetime_cap_spent
//        verbatim, and the stamp rides BESIDE error_class — the #583/#584 facts are
//        not displaced by it.
//   P2 (rule 8, WF-03 hide-law) a node whose read-model refusal is the substituted
//        'unknown' sentinel HIDES the section: no label, no raw sentinel on screen.
//   P3 a fan-out item's stamp renders through the ITEM_FACTS synthesized fallback
//        (the row carries it), and an item with no stamp hides it.
//   P4 source law: 'refusal' is in the ITEM_FACTS fallback list, and the section is
//        factKnown-guarded (the file's non-refusal-death discipline), so an absent
//        key can never print a fabricated value.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const root = join(here, '..')
const src = readFileSync(join(root, 'desktop', 'plugin.js'), 'utf8')

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

// ---- the fixture is CAPTURED, not authored -----------------------------------
// One read of the real read model: wfcommon.node_facts over a run dir whose node `b`
// holds wf.py's `_window_spent_record` output verbatim.
const cap = spawnSync('python3', [join(here, 'fixtures', 'refusal_capture.py'), root],
  { encoding: 'utf8', cwd: root })
assert.equal(cap.status, 0, `the read-model capture must exit 0:\n${cap.stderr}`)
const captured = JSON.parse(cap.stdout)
assert.equal(captured.b.refusal, 'lifetime_cap_spent',
  'P1 precondition: the READ MODEL carries the stamp (est-t7yod, #584) — if this fails the backend regressed, not the render')
assert.equal(captured.a.refusal, 'unknown',
  'P2 precondition: node_facts substitutes the literal sentinel for an absent refusal (never fabricates)')

// ---- component harness (test_node_panel.mjs idiom, no React, no DOM) ---------
const jsx = (type, props) => ({ type, props })
const jsxs = jsx
const walk = node => Array.isArray(node)
  ? node.flatMap(walk)
  : node && typeof node === 'object' ? [node, ...Object.values(node.props || {}).flatMap(walk)] : []
const texts = node => walk(node).flatMap(n =>
  typeof n === 'string' ? [n] : typeof n.props?.children === 'string' ? [n.props.children] : [])

const code = [
  constGrab('EDGE_TONE'), constGrab('FACT_TONE'), constGrab('UNKNOWN'), constGrab('TAIL_BYTES'),
  constGrab('defaultTabFor'), constGrab('unk'), constGrab('factText'), constGrab('logBase'), constGrab('attemptNo'),
  grab('fanItems'), grab('itemLabel'), grab('renderGoal'),
  constGrab('fanCounts'), constGrab('fanSummary'),
  grab('useNodeLogTail'), grab('NodePanel')
].join('\n')

function render({ detail, sel, fanItem = null, tab = null }) {
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
    cfg => ({ data: cfg.enabled ? { content: 'TAIL-CONTENT' } : null, isPending: false }),
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
const graphNode = extra => ({ id: 'a', type: 'agent', goal: 'do work', model: 'm', provider: 'p', reasoning: 'medium', ...extra })
const detailFor = (def, shown) => ({ id: 'r1', status: shown.status, graph: { nodes: [def] }, nodes: { [def.id]: shown }, events: [] })

// ---- P1: the acceptance — a spent-cap boot SHOWS the stamp, beside error_class --
{
  const shown = { ...captured.b, type: 'agent' }          // nodes[b] exactly as the dashboard _view merges it
  const t = texts(render({
    detail: detailFor(graphNode({ id: 'b', after: ['a'] }), shown),
    sel: { runId: 'r1', nodeId: 'b' }, tab: 'Log'
  })).join('|')
  assert.ok(t.includes('lifetime_cap_spent'), `P1: the spent-cap stamp must render on the desktop: ${t.slice(0, 400)}`)
  const segs = t.split('|')
  assert.ok(segs.includes('refusal'), 'P1: the section is NAMED refusal (a reader can tell the stamp from the class)')
  const at = segs.indexOf('refusal')
  assert.equal(segs[at + 1], 'lifetime_cap_spent', 'P1: the refusal section is a label followed by the verbatim stamp')
  assert.ok(t.includes('transport_exhausted'), 'P1: the stamp rides BESIDE error_class — the #583/#584 class still renders')
  assert.ok(t.includes('spawn refused'), 'P1: the refusal prose still rides its own error section (nothing displaced)')
  assert.ok(t.includes('#0 transport'), 'P1: attempts_log renders unchanged beside the new section')
}

// ---- P2: rule 8 / WF-03 — an absent stamp hides, it never prints a sentinel ----
{
  const shown = { ...captured.a, type: 'agent' }          // refusal === 'unknown' from the read model
  const t = texts(render({
    detail: detailFor(graphNode({}), shown), sel: { runId: 'r1', nodeId: 'a' }
  })).join('|')
  const segs = t.split('|')
  assert.ok(!segs.includes('refusal'), 'P2: an unknown-law (absent) refusal hides its section')
  assert.ok(!segs.includes('lifetime_cap_spent'), 'P2: a stamp never leaks across nodes')
  for (const seg of segs) {
    assert.ok(!/\bunknown\b/.test(seg) || /prompt: unknown|log: unknown|final: unknown/.test(seg),
      `P2: the sentinel itself must not print raw (the WF-03 law holds for the new row): ${seg}`)
  }
}

// ---- P3: the fan-out surface — synthesized fallback + honest absence -----------
{
  const def = graphNode({ id: 'fan', fanout: { items: ['x', 'y'], goal: 'work {item}' } })
  // Item 1 refused on a spent lifetime cap; item 0 completed clean.
  const shown = {
    status: 'done', type: 'agent',
    output: {
      all_results: [
        { item: 'x', status: 'done', output: { ok: true }, ms: 10 },
        { item: 'y', status: 'failed', error: 'spawn refused', error_class: 'transport_exhausted',
          refusal: 'lifetime_cap_spent', ms: 0 }
      ]
    }
  }
  const fanItemsX = new Function(`${grab('fanItems')}\n${grab('itemLabel')}\n${grab('renderGoal')}; return fanItems`)()
  const rows = fanItemsX(def, shown, [])
  assert.equal(rows[1].refusal, 'lifetime_cap_spent', 'P3: fanItems carries the per-item stamp (the ITEM_FACTS fallback row reads it)')
  assert.equal(rows[0].refusal, null, 'P3: an item with no stamp reads null, never a fabricated one')
  const pickedT = texts(render({ detail: detailFor(def, shown), sel: { runId: 'r1', nodeId: 'fan' },
    fanItem: { runId: 'r1', nodeId: 'fan', index: 1 }, tab: 'Log' })).join('|').split('|')
  assert.ok(pickedT.includes('refusal') && pickedT[pickedT.indexOf('refusal') + 1] === 'lifetime_cap_spent',
    'P3: the picked item renders its stamp through the ITEM_FACTS synthesized facts')
  const cleanT = texts(render({ detail: detailFor(def, shown), sel: { runId: 'r1', nodeId: 'fan' },
    fanItem: { runId: 'r1', nodeId: 'fan', index: 0 }, tab: 'Output' })).join('|').split('|')
  assert.ok(!cleanT.includes('refusal'), 'P3: a clean item hides the section (no stamp, no surface)')
}

// ---- P4: source law — the row exists and the guard is the file's own -----------
{
  const itemFacts = constGrab('ITEM_FACTS')
  assert.ok(/'refusal'/.test(itemFacts), 'P4: refusal is in the ITEM_FACTS fallback list (the bead cure)')
  assert.ok(itemFacts.indexOf("'refusal'") < itemFacts.indexOf("'error'"),
    'P4: the row order mirrors wfcommon.FACT_KEYS (error_class, refusal, error) — one vocabulary, one order')
  const panel = src.slice(src.indexOf('function NodePanel('), src.indexOf('const Drawer = NodePanel'))
  const guard = /factKnown\(facts\?\.refusal \?\? shown\.refusal\)[\s\S]{0,260}?sect\('refusal'[\s\S]{0,160}?unk\(facts\?\.refusal \?\? shown\.refusal\)/
  assert.ok(guard.test(panel),
    'P4: the refusal section is factKnown-guarded and unk-printed — the exact discipline error_class gets (rule 8)')
  assert.ok(!/sect\('refusal',[^)]*UNKNOWN/.test(panel), 'P4: no path prints the raw sentinel for refusal')
  // refusal is an ADDITIVE row: it must not reach the status truth, the tab
  // default, or the header badge — those keep reading status/error_class.
  assert.ok(!/const effStatus =[^]{0,200}refusal/.test(panel),
    'P4: the refusal row never feeds effStatus (a refusal is a fact, not a status)')
  assert.ok(!/statusLabel\([^)]*refusal/.test(panel), 'P4: statusLabel still answers the status alone')
  // and it sits where the death facts live: after the error pre, before attempts_log
  const atError = panel.indexOf("pre('error'")
  const atRefusal = panel.indexOf("sect('refusal'")
  const atAttempts = panel.indexOf("sect('attempts_log'")
  assert.ok(atError > 0 && atRefusal > atError && atAttempts > atRefusal,
    'P4: the refusal section renders beside the error/attempts facts, not in some far corner of the sheet')
}

console.log('PASS refusal render: spent-cap stamp renders on the panel (P1); sentinel/absent hides (P2);')
console.log('PASS refusal render: fan-item stamp rides ITEM_FACTS, clean item hides (P3); source law pinned (P4)')
