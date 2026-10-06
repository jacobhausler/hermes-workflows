// Session workflow tray above the composer (#230): the shipped #22 tray is
// aligned to the owner's PICTURED density — collapsed default is ONE slim
// row `[chevron] N running workflows`, expand-in-place renders THICK per-run
// rows (name, status dot, nodes_done/nodes_total + mini progress bar, current
// running node id, gate-question snippet when held, elapsed), a run-row click
// opens the EXISTING shared MiniGraph for THAT run, and terminal runs leave
// the tray with NO 60 s recap window (the owner's screenshot template has
// none; the pure trayRecap model stays for pane-side parity, the tray itself
// never renders it). Same idiom as test_run_tray.mjs: fake run ledgers +
// stub SDK/react/jsx, R6 (no test reads plugin source text for behaviour —
// only the established atom/no-localStorage/collapse LAWS are asserted at
// source). The desktop/src/components/runtray.mjs mirror must render the
// SAME trees as plugin.js (design-doc contract truthfulness; plugin.js may
// never import it — test_11_ui_imports freezes its imports at the three SDK
// sources).
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

// -- 0. static laws (established precedent: state law only, never behaviour) -----
assert.match(src, /const \$trayOpen = atom\(null\)/,
  'tray open state stays the in-memory plugin atom — never localStorage')
assert.doesNotMatch(src, /localStorage\s*\.\s*(setItem|getItem|removeItem)/,
  'the desktop half never persists state to localStorage (comments may name it)')

// -- 1. load the real module against stub SDK/react/jsx ---------------------------
const stubSdk = `
export const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const host = { state: { focusedSessionId: atom(''), focusedStoredSessionId: atom(''), }, navigate: () => {}, notify: () => {} }
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const Tip = 'Tip'
export const SIDEBAR_NAV_AREA = 'sidebar.nav', STATUSBAR_AREAS = { left: 'statusBar.left', right: 'statusBar.right' }
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
export const useQuery = q => {
  const key = q && q.queryKey
  if (key && key[1] === 'run') { globalThis.__stubLastRunId = key[2]; return { data: globalThis.__stubDetail } }
  return { data: globalThis.__stubRuns ? { runs: globalThis.__stubRuns } : undefined }
}
export const useValue = a => {
  if (!a || typeof a.get !== 'function') return null
  if (globalThis.__stubOverrides && globalThis.__stubOverrides.has(a)) return globalThis.__stubOverrides.get(a)
  return a.get()
}
export const ctxRestStub = () => Promise.reject(new Error('no backend in test'))
`
const stubReact = `
export const useEffect = () => {}, useId = () => 'st-0', useRef = () => ({ current: null }), useState = i => [typeof i === 'function' ? i() : i, () => {}]
export default { useEffect, useId, useRef, useState }
`
const stubJsx = `
export const jsx = (type, props, key) => ({ type, props: props || {}, key })
export const jsxs = jsx
export const Fragment = 'Fragment'
`
const tmp = mkdtempSync(join(tmpdir(), 'wf-sess-tray-'))
const sdkPath = join(tmp, 'sdk-stub.mjs'); writeFileSync(sdkPath, stubSdk)
const reactPath = join(tmp, 'react-stub.mjs'); writeFileSync(reactPath, stubReact)
const jsxPath = join(tmp, 'jsx-stub.mjs'); writeFileSync(jsxPath, stubJsx)
const load = async (file, subst) => {
  const modPath = join(tmp, subst)
  writeFileSync(modPath, readFileSync(file, 'utf8')
    .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
    .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href))
    .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href)))
  return import(pathToFileURL(modPath).href)
}
const mod = await load(join(here, '..', 'desktop', 'plugin.js'), 'plugin-under-test.mjs')
const mirror = await load(join(here, '..', 'desktop', 'src', 'components', 'runtray.mjs'), 'mirror-under-test.mjs')

// -- helpers (test_run_tray idiom) -------------------------------------------------
const mk = (id, status, sid, extra = {}) => ({
  id, name: id, status, owner: { session_id: sid },
  started: '2026-10-05T04:00:00Z', updated: '2026-10-05T04:05:00Z', ...extra
})
const textOf = node => {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string') return node
  if (Array.isArray(node)) return node.map(textOf).join(' ')
  if (typeof node.type === 'function') return textOf(node.type(node.props))
  return textOf(node.props?.children)
}
const findBy = (node, pred, out = []) => {
  if (node == null || typeof node === 'boolean' || typeof node === 'string') return out
  if (Array.isArray(node)) { node.forEach(n => findBy(n, pred, out)); return out }
  if (pred(node)) out.push(node)
  if (typeof node.type === 'function') { findBy(node.type(node.props), pred, out); return out }
  findBy(node.props?.children, pred, out)
  return out
}
const keyed = (node, key, out = []) => findBy(node, n => n.key === key, out)

const { trayLiveModel, trayRunningLabel, flipChevron, toggleTray, SessionStrip } = mod
assert.equal(typeof trayLiveModel, 'function', 'trayLiveModel is an exported pure model (#230 item 1)')
assert.equal(typeof trayRunningLabel, 'function', 'trayRunningLabel is exported (#230 pictured density)')
assert.equal(typeof flipChevron, 'function', 'flipChevron is the pure chevron transition fn (item 2)')

// -- 2. live-set session model: held first, then running by started desc -----------
// SAME ordering as splitRuns (the rail law), proven against splitRuns on one
// fake ledger; cron_-shaped owner inclusion + blank-owner exclusion per the
// ownedRuns law (the tray keys on the owner VALUE).
{
  const runs = [
    mk('r-old', 'running', 'S1', { started: '2026-10-05T03:55:00Z' }),
    mk('r-new', 'running', 'S1', { started: '2026-09-23T14:30:41Z' }),
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:40:00Z', held_gate: { id: 'go', question: 'Ship the cut?', options: ['ship', 'hold'] } }),
    mk('done1', 'done', 'S1'),
    mk('fail1', 'failed', 'S1'),
    mk('stop1', 'stopped', 'S1'),
    mk('cron-owned', 'running', 'cron_daily_report'),
    mk('blank', 'running', ''),
    mk('other', 'running', 'S2'),
  ]
  const scoped = mod.trayScoping(runs, 'S1')
  const live = trayLiveModel(scoped)
  assert.deepEqual(live.map(r => r.id), ['h1', 'cron-owned', 'r-old', 'r-new'],
    'live set: held pinned first, then running by started desc; terminal runs left; cron_-shaped owner included; blank-owner excluded')
  // Same ordering as splitRuns over the identical owned set (minus terminal):
  // splitRuns caps active at 3 (the rail policy), so the parity check is the
  // PREFIX — the live set is the uncapped superset in the same order.
  const { active } = mod.splitRuns(scoped)
  assert.deepEqual(live.slice(0, active.length).map(r => r.id), active.map(r => r.id),
    'the tray live-set ordering is THE SAME ordering as splitRuns (prefix parity; tray stays uncapped)')
  assert.ok(live.length >= active.length, 'the live set holds every splitRuns active row')
}

// -- 3. pictured density: `N running workflows` over the live set -------------------
{
  const runs = [
    mk('h1', 'held', 'S1'),
    mk('b1', 'running', 'S1'),
    mk('b2', 'running', 'S1'),
    mk('f1', 'done', 'S1'),   // terminal -> NOT counted, NEVER lingers
  ]
  const label = trayRunningLabel(runs)
  assert.equal(label.count, 3, 'count is the LIVE set (held + running); terminal runs leave')
  assert.match(label.line, /^3 running workflows$/, `pictured line, got: ${label.line}`)
  assert.equal(trayRunningLabel([]).line, '0 running workflows', 'empty live set reads 0 running workflows (never fabricated)')
  // No 60 s recap window on the tray: finished-only ledgers are hidden AT ONCE
  // at any wall clock (trayRecap remains a pure pane-side model, untouched).
  const T = Date.parse('2026-10-05T06:00:00Z')
  const doneRuns = [mk('d1', 'done', 'S1', { nodes_done: 4, nodes_total: 4, updated: '2026-10-05T05:59:59Z' })]
  assert.equal(mod.trayShouldShow(trayLiveModel(mod.trayScoping(doneRuns, 'S1')), T), false,
    'terminal-only ledger -> tray hidden IMMEDIATELY (no 60 s recap window)')
  assert.equal(mod.trayShouldShow(trayLiveModel(mod.trayScoping([mk('b', 'running', 'S1')], 'S1')), T), true,
    'a live run keeps the tray visible')
  assert.equal(mod.trayShouldShow(trayLiveModel([]), T), false, 'zero live rows -> tray hidden')
}

// -- 4. collapsed default: ONE slim row [chevron] + label, chevron from flipChevron --
{
  const collapsed = mod.RunTrayRow({ runs: mod.trayScoping([mk('b1', 'running', 'S1'), mk('f1', 'done', 'S1')], 'S1'), expanded: false })
  assert.ok(collapsed, 'collapsed tray row renders')
  const txt = textOf(collapsed)
  assert.match(txt, /1 running workflows/, `collapsed row reads the pictured density, got: ${txt}`)
  assert.equal(txt.trim().split(/\s+/).filter(t => t === '▾' || t === '▴').length, 1,
    'exactly ONE chevron on the slim row')
  assert.ok(/▾/.test(txt), 'collapsed chevron points down (flipChevron(false) === ▾)')
  assert.equal(flipChevron(false), '▾'); assert.equal(flipChevron(true), '▴')
  assert.equal(flipChevron('▴'), '▾', 'flipChevron flips the current glyph (pure transition fn)')
  // Inline styles only (purged Tailwind): no className on the collapsed row.
  const row = collapsed.type === 'div' || typeof collapsed.type === 'string' ? collapsed : null
  assert.ok(row, 'collapsed row is a plain element')
  assert.equal(row.props.className, undefined, 'collapsed slim row uses INLINE styles only (no Tailwind class)')
  assert.ok(row.props.style, 'collapsed row carries inline styles')
  // Every colour on the collapsed row reads the ONE --ui var table.
  const flat = JSON.stringify(collapsed)
  for (const m of flat.matchAll(/color:\s*["']([^"']+)["']/g)) {
    assert.ok(m[1].includes('--ui'), `collapsed colour '${m[1]}' must read a --ui CSS var (ONE tone table)`)
  }
}

// -- 5. expand-in-place: THICK rows with name, dot, x/y + bar, node id, snippet, elapsed --
{
  globalThis.__stubRuns = [
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:40:00Z', nodes_done: 1, nodes_total: 3, nodes: { prep: { status: 'done' }, go: { status: 'held' }, post: { status: 'pending' } }, held_gate: { id: 'go', question: 'Ship the cut to prod?', options: ['ship', 'hold'] } }),
    mk('b1', 'running', 'S1', { nodes_done: 2, nodes_total: 5, nodes: { a: { status: 'done' }, b: { status: 'done' }, c: { status: 'running' }, d: { status: 'pending' }, e: { status: 'pending' } } }),
    mk('d1', 'done', 'S1', { nodes_done: 3, nodes_total: 3 }),
  ]
  globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: true, openRun: 'b1' }]])
  globalThis.__stubDetail = { id: 'b1', name: 'b1', status: 'running', nodes: { a: { status: 'done' }, b: { status: 'done' }, c: { status: 'running' }, d: { status: 'pending' }, e: { status: 'pending' } } }
  const open = SessionStrip()
  assert.ok(open, 'tray renders with live runs')
  const txt = textOf(open)
  assert.ok(txt.includes('b1') && txt.includes('h1'), 'expanded tray names each live run')
  assert.ok(txt.includes('2/5'), 'thick row shows nodes_done/nodes_total')
  assert.ok(txt.includes('→ c'), 'thick row shows the CURRENT running node id')
  assert.ok(txt.includes('Ship the cut'), 'held row shows the gate-question snippet')
  assert.ok(/\d+m( \d+s)?/.test(txt), 'thick row shows elapsed time')
  // Mini progress bar: a bar element whose width speaks the ratio, beside x/y.
  const byKey = key => findBy(open, n => n.key === key)
  assert.equal(byKey('bar').length, 2, 'every thick row carries a mini progress bar (2 live rows)')
  const widths = byKey('bar').map(n => String(n.props?.style?.width ?? ''))
  assert.ok(widths.includes('40%') && widths.includes('33%'),
    `bar widths speak the ratio (2/5 -> 40%, 1/3 -> 33%), got: ${JSON.stringify(widths)}`)
  // The terminal run left the tray — no 'open ↗' row, no recap line.
  assert.ok(!txt.includes('last run done'), 'NO 60 s recap window on the tray')
  const doneRows = findBy(open, n => n.key === 'rr-d1')
  assert.equal(doneRows.length, 0, 'terminal runs leave the expanded tray (running-only accumulator)')
  // Click 2: the row click opens the EXISTING shared MiniGraph for THAT run —
  // the runQuery key equals the clicked id (stub records it).
  const rowClick = keyed(open, 'rr-b1')[0]
  assert.ok(rowClick, 'b1 thick row rendered')
  rowClick.props.onClick({ stopPropagation: () => {} })
  const mini = findBy(open, n => typeof n.type === 'function' && n.type.name === 'MiniGraph')
  assert.equal(mini.length, 1, 'exactly one accordion-opened row renders the shared MiniGraph')
  assert.equal(globalThis.__stubLastRunId, 'b1', 'runQuery key equals the CLICKED run id')
  assert.ok(txt.includes('open ↗'), 'row keeps the bigger-pane escalation')
  globalThis.__stubOverrides = null
}

// -- 6. dedupe via the REAL SessionStrip render (item 5) ----------------------------
{
  sdkReload: {
    // DirectiveCard + pill rail stay as they are; exactly ONE GateActions per
    // held run across the WHOLE strip (tray owns the release surface; the
    // rail keeps suppressGates).
    const runs = [
      mk('h1', 'held', 'S1', { held_gate: { id: 'g1', question: 'Ship?', options: ['a'] } }),
      mk('h2', 'held', 'S1', { started: '2026-10-05T03:30:00Z', held_gate: { id: 'g2', question: 'Deploy?', options: ['a'] } }),
      mk('b1', 'running', 'S1'),
    ]
    globalThis.__stubRuns = runs
    globalThis.__stubOverrides = new Map([[mod.$trayOpen, { expanded: true, openRun: null }]])
    const tree = SessionStrip()
    const ga = findBy(tree, n => typeof n.type === 'function' && n.type.name === 'GateActions')
    assert.equal(ga.length, 2, 'exactly ONE GateActions per held run (2 held runs -> 2 release surfaces, no dupes)')
    const rail = findBy(tree, n => typeof n.type === 'function' && n.type.name === 'PillRail')
    assert.equal(rail.length, 1, 'the pill rail stays mounted, untouched, beside the tray')
    assert.equal(rail[0].props.suppressGates, true, 'the rail never re-adds a second gate release surface')
    assert.equal(findBy(tree, n => typeof n.type === 'function' && n.type.name === 'DirectiveCard').length, 0,
      'SessionStrip renders no DirectiveCard (the in-transcript card stays transcript-side, untouched)')
    assert.match(src, /TRANSCRIPT_DIRECTIVE_AREA/, 'DirectiveCard registration untouched (transcript directives area)')
    globalThis.__stubOverrides = null
  }
}

// -- 7. collapse laws on the TRAY path (source-assert precedent, item 4) -----------
assert.match(src, /if \(e\.key === 'Escape'\)\s*\{\s*if \(trayExpanded\) \$trayOpen\.set\(null\)/,
  'Esc collapses the expanded tray FIRST on the tray path')
assert.match(src, /trayExpanded && trayRef\.current && trayRef\.current\.contains\(e\.target\)/,
  'click-away excludes clicks inside the open tray (trayRef contains check)')
assert.match(src, /\$trayOpen\.set\(null\) \}, \[pairKey\]/,
  'sid-change collapses the tray (in-memory atom reset on pairKey change)')
assert.match(src, /window\.addEventListener\('click', onDocClick\)/,
  'click-away rides the single window-level listener (no DOM-node listeners)')
// #230 spec 5 (feature-detect idiom, corrected on harvest): the issue body's
// item 6 demands the strip "rides the real tray area when core exposes it —
// same feature-detect idiom as COMPOSER_AREAS.underside ?? COMPOSER_AREAS.top",
// so the single-mount chain is tray ?? underside ?? top (test_register_surface
// 1b′ locks the tray head at the registration site). The harvested literal
// `underside ?? top` regex contradicted the issue body and the merged item-0
// test — widened to the real feature-detected mount: the inline ?? chain OR
// the sessionStripArea helper that carries it.
assert.match(src, /register\(\{[^}]*id: 'session-strip'[^}]*area: (sessionStripArea\(COMPOSER_AREAS\)|COMPOSER_AREAS\.underside \?\? COMPOSER_AREAS\.top)/,
  'the tray rides the feature-detected composer mount (no duplicate surface — spec 5)')
assert.match(src, /composerAreas\?\.tray \?\? composerAreas\?\.underside \?\? composerAreas\?\.top/,
  'the feature-detect chain carries the tray head — rides the real tray area when core exposes it (#230 item 6)')

// -- 8. the runtray.mjs mirror grows REAL bodies (item 6) ---------------------------
{
  // plugin.js may NEVER import the mirror (test_11_ui_imports freezes its
  // imports at the three SDK sources): assert the freeze from here too.
  assert.doesNotMatch(src, /import\s[^\n]*runtray/, 'plugin.js never imports runtray.mjs')
  for (const name of ['trayScoping', 'trayModel', 'trayLiveModel', 'trayRunningLabel',
    'trayAggregateLabel', 'trayRecap', 'ackFinished', 'toggleTray', 'flipChevron',
    'RunTrayRow', 'RunTrayRunRow', 'RunTray']) {
    assert.equal(typeof mirror[name], 'function', `mirror exports ${name} as a real body (never a throwing shell)`)
  }
  // Mirror pure models agree with plugin.js on the SAME fake ledger.
  const runs = [
    mk('h1', 'held', 'S1', { started: '2026-10-05T03:40:00Z' }),
    mk('b1', 'running', 'S1', { started: '2026-10-05T04:01:00Z' }),
    mk('b2', 'running', 'S1', { started: '2026-10-05T04:02:00Z' }),
    mk('f1', 'done', 'S1'),
    mk('blank', 'running', ''),
  ]
  assert.deepEqual(mirror.trayLiveModel(mirror.trayScoping(runs, 'S1')).map(r => r.id),
    mod.trayLiveModel(mod.trayScoping(runs, 'S1')).map(r => r.id),
    'mirror trayLiveModel mirrors plugin.js on the same ledger')
  assert.equal(mirror.trayRunningLabel(runs).line, mod.trayRunningLabel(runs).line,
    'mirror trayRunningLabel mirrors the pictured line')
  assert.deepEqual(mirror.toggleTray(null, 'a'), mod.toggleTray(null, 'a'), 'mirror toggleTray mirrors')
  assert.equal(mirror.flipChevron(true), mod.flipChevron(true), 'mirror flipChevron mirrors')
  // Collapsed row: the mirror renders the SAME visible text + the SAME shape
  // (normalised: drop keys/styles — pure bodies must not fork the density).
  const norm = node => {
    if (node == null || typeof node === 'boolean' || typeof node === 'string') return node
    if (Array.isArray(node)) return node.map(norm)
    return { type: node.type, children: norm(node.props?.children) }
  }
  const props = { runs: mod.trayScoping([mk('b1', 'running', 'S1')], 'S1'), expanded: false }
  assert.deepEqual(norm(mirror.RunTrayRow(props)), norm(mod.RunTrayRow(props)),
    'mirror collapsed row renders the SAME tree as plugin.js (design-doc truth)')
  const mTxt = textOf(mirror.RunTrayRow(props))
  assert.match(mTxt, /1 running workflows/, 'mirror collapsed row reads the pictured density too')
  assert.ok(/▾/.test(mTxt), 'mirror collapsed chevron points down')
  // Thick rows render through the mirror too (real bodies, not null).
  const thick = mirror.RunTrayRunRow({ run: mk('b1', 'running', 'S1', { nodes_done: 2, nodes_total: 5 }), band: 'building', open: false })
  assert.ok(thick, 'mirror RunTrayRunRow renders a real body')
  assert.match(textOf(thick), /2\/5/, 'mirror thick row shows node progress')
}

rmSync(tmp, { recursive: true, force: true })
console.log('ALL PASS test_session_tray (live-set model + splitRuns parity, cron/owner law, pictured `N running workflows` density, slim collapsed row + flipChevron, thick rows w/ bar+node id+snippet+elapsed, MiniGraph for the clicked run, dedupe GateActions, collapse laws, runtray.mjs mirror)')
