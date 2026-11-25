// Reproduce the step-2 recon lap: skip-column dependencies cross coverage/critic.
// RC ch4 (bd_2026-11-13-33h): Edges renders ONE GROUP PER ROUTE — the state
// stroke (incumbent dash/marker laws), a static identity-tint overlay (6
// deterministic host-palette aliases cycling by dependency order), matching
// open-ring endpoint echoes at the exact ports, and an edge-state title.
// The Council section pins the child-projection arithmetic (10 identities,
// 14 projected dependencies, 28 echoes from the frozen wave6-council shelf
// topology) and MEASURES strict crossings at THIS geometry — it reports the
// measured number; it never transplants the bench's 20/22/24.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const src = readFileSync(new URL('../desktop/plugin.js', import.meta.url), 'utf8')
const grab = name => {
  const i = src.indexOf(`function ${name}(`)
  if (i < 0) return ''
  let depth = 0, j = src.indexOf(') {', i) + 2
  for (; j < src.length; j++) if (src[j] === '{') depth++; else if (src[j] === '}' && --depth === 0) break
  return src.slice(i, j + 1)
}
const constGrab = name => {
  const i = src.indexOf(`const ${name} =`)
  const j = src.indexOf('\n\n', i)
  return src.slice(i, j)
}
let instance = 0
const jsx = (type, props, key) => ({ type, props, key })
const { Edges, depthMap, fanProjection, routeTint, ROUTE_TINTS } = new Function('jsx', 'jsxs', 'useId',
  `const EDGE_TONE = { done:'teal', pending:'gray', failed:'red', running:'blue', held:'orange', skipped:'gray' };\nconst NODE_TONE = Object.fromEntries(Object.entries(EDGE_TONE).map(([k,v]) => [k, { color:v, borderColor:v, shadow:null, shadowHover:null, pulseMs:null, calm:true, ui:'muted', gate:null, breathe:null }]));\nNODE_TONE.waiting = NODE_TONE.pending;\n${['edgeFlowPolicy', 'depthMap', 'graphLinks', 'edgePath', 'routeEdge', 'edgeTone', 'nodeState', 'fanRowPartition', 'fanProjection', 'Edges'].map(grab).join('\n')}\n${constGrab('ROUTE_TINTS')}\n${grab('routeTint')}\nreturn { Edges, depthMap, fanProjection, routeTint, ROUTE_TINTS }`)(jsx, jsx, () => `test-${++instance}`)
const nodes = [
  {id:'hub-a'}, {id:'hub-b'}, {id:'mac'},
  {id:'coverage', after:['hub-a']},
  {id:'verify', after:['hub-a','hub-b','mac','coverage']},
  {id:'critic', after:['verify']},
  {id:'consolidate', after:['verify','critic']}
]
function rectsFor(defs, mini = false) {
  const depths = depthMap(defs), rects = {}, cols = []
  for (const n of defs) (cols[depths.get(n.id)] ||= []).push(n)
  let x = 20
  cols.forEach(col => {
    let y = 80
    for (const n of col) {
      rects[n.id] = {x,y,w:mini ? 50+n.id.length*4 : 168,h:mini ? 20 : 74}
      y += rects[n.id].h + (mini ? 6 : 28)
    }
    x += Math.max(...col.map(n=>rects[n.id].w)) + (mini ? 34 : 112)
  })
  return rects
}
function points(d) {
  const t = d.match(/[A-Za-z]|-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/g), out = []
  let i=0, x=0, y=0
  while (i<t.length) {
    const op=t[i++], ax=x, ay=y
    if(op==='M') {x=+t[i++];y=+t[i++];out.push([x,y]);continue}
    if(op==='C') {
      const bx=+t[i++],by=+t[i++],cx=+t[i++],cy=+t[i++];x=+t[i++];y=+t[i++]
      for(let j=1;j<=200;j++) {const s=j/200,u=1-s;out.push([u*u*u*ax+3*u*u*s*bx+3*u*s*s*cx+s*s*s*x,u*u*u*ay+3*u*u*s*by+3*u*s*s*cy+s*s*s*y])}
    } else {
      if(op==='H') x=+t[i++]; else if(op==='V') y=+t[i++]; else if(op==='L') {x=+t[i++];y=+t[i++]} else throw new Error('unknown path '+op)
      for(let j=1;j<=200;j++) out.push([ax+(x-ax)*j/200,ay+(y-ay)*j/200])
    }
  }
  return out
}
// One group per dependency: [title, state path, tint path, echo, echo].
const groupsOf = svg => (svg?.props.children || []).filter(x => x && x.type === 'g')
const pathsOf = g => g.props.children.filter(c => c && c.type === 'path')
const echoesOf = g => g.props.children.filter(c => c && c.type === 'circle')
function check(defs, rects, label) {
  const states=Object.fromEntries(defs.map(n=>[n.id,{status:'done'}]))
  const svg=Edges({nodes:defs,rects,states}), groups=groupsOf(svg)
  assert.equal(groups.length,defs.reduce((n,d)=>n+(d.after?.length||0),0),'retain every explicit dependency')
  const ports={}
  for(const group of groups) {
    const [a,b]=group.key.split('->'), ps=pathsOf(group), sp=ps[0], p=points(sp.props.d), from=rects[a], to=rects[b]
    // Ports sit ON the card edge but may spread along it so arrowheads never pile.
    assert.equal(p[0][0],from.x+from.w);assert.equal(p.at(-1)[0],to.x)
    assert.ok(p[0][1]>=from.y+1 && p[0][1]<=from.y+from.h-1,`${label}: exit port on ${a} edge`)
    assert.ok(p.at(-1)[1]>=to.y+1 && p.at(-1)[1]<=to.y+to.h-1,`${label}: entry port on ${b} edge`)
    assert.ok(p.every(([x,y])=>Number.isFinite(x)&&Number.isFinite(y)&&x>=0&&y>=0), 'path stays in reserved canvas')
    for(const [id,r] of Object.entries(rects)) {
      if(id===a||id===b) continue
      assert.ok(!p.some(([x,y])=>x>r.x && x<r.x+r.w && y>r.y && y<r.y+r.h),`${label}: ${group.key} passes through unrelated ${id}`)
    }
    ;(ports[b] ||= []).push(p.at(-1)[1])
    // RC ch4 identity layer: static tint overlay on the SAME routed curve,
    // open-ring echoes at the EXACT ports, edge-state title reachable.
    const tp = ps[1]
    assert.equal(ps.length, 2, `${label}: ${group.key} = one state stroke + one static identity overlay`)
    assert.equal(tp.props.d, sp.props.d, `${label}: ${group.key} identity stroke rides the same routed path`)
    assert.equal(tp.props.strokeWidth, 0.8, `${label}: identity overlay keeps the 0.8px token value`)
    assert.match(String(tp.props.strokeDasharray), /2 3/, `${label}: identity overlay is dashed (static, never marching)`)
    assert.ok(tp.props.children == null, `${label}: identity overlay never animates`)
    const echo = echoesOf(group)
    assert.equal(echo.length, 2, `${label}: ${group.key} carries matching open-ring echoes at BOTH endpoints`)
    assert.deepEqual([echo[0].props.cx, echo[0].props.cy], p[0], `${label}: source echo sits on the exit port`)
    assert.deepEqual([echo[1].props.cx, echo[1].props.cy], p.at(-1), `${label}: target echo sits on the entry port`)
    assert.equal(echo[0].props.fill, 'none', `${label}: echoes are OPEN rings`)
    assert.equal(echo[0].props.stroke, echo[1].props.stroke, `${label}: matching endpoint echoes share the route tint`)
    assert.equal(tp.props.stroke, echo[0].props.stroke, `${label}: overlay and echoes share the route identity`)
    assert.ok(group.props.children.some(c => c.type === 'title'), `${label}: ${group.key} carries an edge-state title`)
  }
  for(const ys of Object.values(ports)) assert.equal(new Set(ys).size,ys.length,'incoming arrowheads must not pile onto one point')
  return {svg,rects}
}
const page=check(nodes,rectsFor(nodes),'page')
check(nodes,rectsFor(nodes,true),'mini: variable-width pills')
const chain=[{id:'a'},{id:'b',after:['a']},{id:'c',after:['b']}]
check(chain,rectsFor(chain),'ordinary chain')
// Resized content and scrolled coordinate offsets use the same measured-rect contract.
const shifted=Object.fromEntries(Object.entries(rectsFor(nodes)).map(([id,r])=>[id,{...r,x:r.x+73,y:r.y+20}]))
check(nodes,shifted,'scrolled canvas')
const tall=rectsFor(nodes);tall.coverage.h=130;check(nodes,tall,'expanded middle card')
const omitted={...rectsFor(nodes)};delete omitted.coverage
assert.doesNotThrow(()=>Edges({nodes,rects:omitted,states:{}}),'unmeasured cards during mount are safe')
const failed=Edges({nodes:chain,rects:rectsFor(chain),states:{a:{status:'failed'}}})
const deadGroup=groupsOf(failed).find(g=>g.key==='a->b')
const dead=pathsOf(deadGroup)[0]
assert.equal(dead.props.strokeDasharray,'3 3');assert.match(dead.props.markerEnd,/-dead\)/)
assert.notEqual(pathsOf(deadGroup)[0].props.markerEnd, pathsOf(groupsOf(page.svg)[0])[0].props.markerEnd,'markers remain per-instance')

// -- RC ch4: the route identity layer cycles six deterministic host-palette
// aliases by dependency order. Tint is IDENTITY, not state: every route in a
// calm all-done render still carries overlay + echoes, and the cycle is
// reproducible from the graph order alone (no RNG, no layout dependence).
{
  assert.equal(ROUTE_TINTS.length, 6, 'six deterministic palette aliases')
  assert.equal(new Set(ROUTE_TINTS).size, 6, 'the six aliases are distinct')
  for (let i = 0; i < 13; i++) assert.equal(routeTint(i), ROUTE_TINTS[i % 6], `cycle position ${i}`)
  assert.equal(routeTint(-1), ROUTE_TINTS[5], 'negative indices stay inside the cycle')
  const svg = Edges({ nodes, rects: rectsFor(nodes), states: Object.fromEntries(nodes.map(n => [n.id, { status: 'done' }])) })
  const tints = groupsOf(svg).map(g => pathsOf(g)[1].props.stroke)
  assert.equal(tints.length, 8, 'the fixture graph routes all eight dependencies')
  tints.forEach((t, i) => assert.equal(t, ROUTE_TINTS[i % 6], `route ${i} carries alias ${i % 6} in dependency order`))
}

// -- RC ch4: Council child projection (frozen shelf topology, source-cited
// below). Six committed child records of node `critics` project as their own
// identities: 10 nodes, 14 dependencies, 28 endpoint echoes — MEASURED here,
// never transplanted from a bench report.
{
  // Source: research ui2/synthesis/fixtures-real/20261122-121032-wave6-council.json
  // (sha256 8ad015ceb58e0dd8e61d017a279e654c5c33bd70ffcbfcbf159b4e7ae5139922):
  // graph.nodes verbatim (4); critics.output.all_results carried 6 done records.
  const council = {
    id: '20261122-121032-wave6-council',
    graph: { nodes: [
      { id: 'charter', type: 'agent' },
      { id: 'critics', type: 'agent', after: ['charter'], fanout: { items: [{}, {}, {}, {}, {}, {}] } },
      { id: 'adjudicate', type: 'agent', after: ['critics'] },
      { id: 'report', type: 'agent', after: ['adjudicate'] }
    ] },
    nodes: { charter: { status: 'done' }, critics: { status: 'done' }, adjudicate: { status: 'done' }, report: { status: 'done' } }
  }
  const rows = Array.from({ length: 6 }, (_, i) => ({ index: i, status: 'done', recorded: true }))
  const proj = fanProjection(council, { critics: rows })
  assert.equal(proj.nodes.length, 10, 'ten node identities: 4 shelf + 6 projected children')
  const deps = proj.nodes.reduce((n, d) => n + (d.after?.length || 0), 0)
  assert.equal(deps, 14, 'fourteen projected dependencies (1 + 6 + 6 + 1)')
  const adj = proj.nodes.find(n => n.id === 'adjudicate')
  assert.deepEqual(adj.after, rows.map((_, i) => `critics.${i}`), 'fan-in rehangs onto EVERY projected child identity')
  assert.ok(proj.nodes.some(n => n.id === 'critics'), 'the projected parent keeps its identity (the fanout aggregate)')
  for (let i = 0; i < 6; i++) assert.equal(proj.states[`critics.${i}`].status, 'done', `projected child ${i} carries its raw record status`)
  const cRects = rectsFor(proj.nodes)
  const svg = Edges({ nodes: proj.nodes, rects: cRects, states: proj.states })
  const groups = groupsOf(svg)
  assert.equal(groups.length, 14, 'every projected dependency renders as its own route group')
  assert.equal(groups.reduce((n, g) => n + echoesOf(g).length, 0), 28, 'twenty-eight endpoint echoes — two per route')
  // MEASURED strict crossings at THIS geometry (sampled polylines; proper
  // crossings only; shared-endpoint pairs excluded — endpoint touches and
  // collinear overlaps do not count, and a crossing is not a junction).
  const curves = groups.map(g => {
    const [a, b] = g.key.split('->')
    return { key: g.key, a, b, pts: points(pathsOf(g)[0].props.d) }
  })
  const seg = (p1, p2, p3, p4) => {
    const d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if (!d) return false
    const t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    const u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    return t > 0 && t < 1 && u > 0 && u < 1
  }
  let crossings = 0
  for (let i = 0; i < curves.length; i++) for (let j = i + 1; j < curves.length; j++) {
    const A = curves[i], B = curves[j]
    if (A.a === B.a || A.a === B.b || A.b === B.a || A.b === B.b) continue // shared endpoint: not a strict crossing
    outer: for (let m = 0; m + 1 < A.pts.length; m++)
      for (let n = 0; n + 1 < B.pts.length; n++)
        if (seg(A.pts[m], A.pts[m + 1], B.pts[n], B.pts[n + 1])) { crossings++; break outer }
  }
  console.log(`council projection: 14 routes, 28 echoes, ${crossings} strict crossings MEASURED at this test geometry (a count of the CURRENT geometry only — the bench reports 20 at 1600x1300 and 22 at 1600x1000, neither is transplanted here)`)
  // The unit-level claim is DETERMINISM at this geometry (the same graph
  // rendered twice measures the same number) — crossing behaviour at real
  // geometries is proven by the actual-app capture in the bead receipt.
  const curves2 = groupsOf(Edges({ nodes: proj.nodes, rects: cRects, states: proj.states }))
    .map(g => { const [a, b] = g.key.split('->'); return { key: g.key, a, b, pts: points(pathsOf(g)[0].props.d) } })
  let crossings2 = 0
  for (let i = 0; i < curves2.length; i++) for (let j = i + 1; j < curves2.length; j++) {
    const A = curves2[i], B = curves2[j]
    if (A.a === B.a || A.a === B.b || A.b === B.a || A.b === B.b) continue
    outer2: for (let m = 0; m + 1 < A.pts.length; m++)
      for (let n = 0; n + 1 < B.pts.length; n++)
        if (seg(A.pts[m], A.pts[m + 1], B.pts[n], B.pts[n + 1])) { crossings2++; break outer2 }
  }
  assert.equal(crossings2, crossings, 'crossing measurement is deterministic (re-render idempotent)')
}
if(process.argv.includes('--fixture')) writeFileSync(fileURLToPath(new URL('../edge-fixture.json',import.meta.url)),JSON.stringify(page,null,2))
console.log('edge routing PASS: real skip-column graph, page/mini, resize, scroll, chain, missing measurements, failed tone and markers, RC route identity (6-alias cycle, static overlay, echoes, titles), Council projection (10/14/28) with measured crossings')
