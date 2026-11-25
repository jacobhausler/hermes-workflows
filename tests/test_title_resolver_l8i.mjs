// l8i (instance-label-first display law): ONE resolver (displayTitle) feeds
// every title surface — in-chat pill, tray accordion row, fleet landing row.
// Precedence: lane_key's last HUMAN segment (after the final '/'; a door-
// synthesized `start-<slug>` segment is machine-derived and skipped, else the
// template name rides the pill back in), else the description's first clause
// (capped one line), else run.name, else id, else 'workflow'. The template
// renders ONLY as secondary metadata (templateTag; the fleet row has width
// and keeps a template COLUMN). The real module is loaded against SDK/react
// stubs (test_pill_rail precedent): JSX atoms are recorded calls, no DOM.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

const stubSdk = `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const atom0 = atom
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const atoms = { focusedSessionId: atom(''), focusedStoredSessionId: atom('') }
export const host = { state: atoms, navigate: () => {}, notify: () => {} }
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const Tip = 'Tip'
export const SIDEBAR_NAV_AREA = 'sidebar.nav', STATUSBAR_AREAS = { left: 'statusBar.left', right: 'statusBar.right' }
export const queries = { list: { runs: [] }, run: null }
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQuery = q => (Array.isArray(q.queryKey) && q.queryKey[1] === 'run'
  ? { data: queries.run, error: null }
  : { data: queries.list, error: null })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
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
const tmp = mkdtempSync(join(tmpdir(), 'wf-l8i-'))
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

const { displayTitle, templateTag, cardModel, railModel, RunTrayRunRow, PaneRow } = mod
for (const [name, fn] of [['displayTitle', displayTitle], ['templateTag', templateTag],
  ['cardModel', cardModel], ['railModel', railModel],
  ['RunTrayRunRow', RunTrayRunRow], ['PaneRow', PaneRow]]) {
  assert.equal(typeof fn, 'function', `${name} is exported`)
}

// -- 1. resolver precedence: every arm, one at a time -------------------------
// lane_key arm: the last human segment after the final '/'.
assert.equal(displayTitle({ id: 'r', name: 'estate-bead-crew', lane_key: 'ship20-m/W2c' }), 'W2c',
  'lane_key arm: team prefix drops, the human segment titles')
assert.equal(displayTitle({ id: 'r', name: 'estate-bead-crew', lane_key: 'ship20W2c' }), 'ship20W2c',
  'lane_key arm: a flat key rides whole (no slash, no cut)')
// A door-synthesized key IS the template slug — machine-derived, never human.
assert.equal(displayTitle({ id: 'r', name: 'estate-bead-crew', lane_key: 'start-estate-bead-crew',
  description: 'Close out the wave. Then file receipts.' }), 'Close out the wave',
  'machine-synthesized start-<slug> is skipped: the description arm takes over')
assert.equal(displayTitle({ id: 'r', name: 'estate-bead-crew', lane_key: 'ship20/start-estate-bead-crew',
  description: 'Close out the wave' }), 'Close out the wave',
  'team-prefixed synthesized key skips to the same arm')
// description arm: FIRST CLAUSE only, then falls to name when description is empty.
assert.equal(displayTitle({ id: 'r', name: 'tpl', description: 'Review the PRs; file the receipts. Ship it.' }), 'Review the PRs',
  'description arm: the first clause, nothing past the first boundary')
assert.equal(displayTitle({ id: 'r', name: 'tpl', description: '   ' }), 'tpl',
  'blank description is absent description (honest absence, name arm)')
// one line of room: a long clause clips, never wraps
const long = displayTitle({ id: 'r', description: 'x'.repeat(200) })
assert.ok(long.length === 64 && long.endsWith('…'), `long clause clipped to one line, got ${long.length}`)
// name arm, id arm, floor
assert.equal(displayTitle({ id: 'r-9', name: 'estate-bead-crew' }), 'estate-bead-crew',
  'unlabeled run falls to name (the door warned at launch)')
assert.equal(displayTitle({ id: 'r-9' }), 'r-9', 'no name falls to id')
assert.equal(displayTitle({}), 'workflow', 'nothing at all reads the honest floor')

// -- 2. templateTag: secondary only, never a duplicate of the title -----------
assert.equal(templateTag({ id: 'r', name: 'estate-bead-crew', lane_key: 'ship20W2c' }), 'estate-bead-crew',
  'labeled run: the demoted template is available as metadata')
assert.equal(templateTag({ id: 'r', name: 'estate-bead-crew' }), null,
  'unlabeled run: title IS the name, the tag nulls (never printed twice)')

// -- 3. ACCEPTANCE PROOF CASE: the RC pill titles with the label ---------------
// bd_2026-11-13-1bm: pillModel is retired — cardModel is the pill's ONE model.
// The identity baseline carries the resolved label; the demoted template is
// secondary metadata (model slot + hover + leading word of the expanded row),
// never a headline word.
const proof = { id: '20261124-123529-ship20-m', name: 'estate-bead-crew',
  lane_key: 'ship20W2c', status: 'done', nodes_done: 4, nodes_total: 4 }
const pill = cardModel(proof)
assert.equal(pill.name, 'ship20W2c',
  `card identity row leads with the instance label, got ${pill.name}`)
assert.ok(!pill.statusWord.includes('estate-bead-crew')
  && !pill.census.some(x => x.includes('estate-bead-crew')),
  'the template name is GONE from the collapsed identity and census baselines')
assert.equal(pill.template, 'estate-bead-crew', 'the template rides the model as secondary metadata')
assert.equal(pill.metrics[0], 'template estate-bead-crew',
  'the expanded word row leads with the demoted template, labelled')

// -- 4. tray accordion row: label title + muted template badge + lane chip ----
const tree = RunTrayRunRow({ run: { ...proof, status: 'running' }, open: false })
const byKey = {}
for (const child of tree.props.children) if (child && child.key) byKey[child.key] = child
assert.equal(byKey.name.props.children, 'ship20W2c', 'tray row titles with the label')
assert.equal(byKey.tmpl.props.children, 'estate-bead-crew', 'tray row carries the muted template badge')
assert.equal(byKey.tmpl.props.title, 'template estate-bead-crew', 'badge names what it is')
assert.equal(byKey.lane.props.children, 'ship20W2c', 'the full lane_key chip stays whole beside the short title')
const bare = RunTrayRunRow({ run: { id: 'r', name: 'tpl', status: 'running' }, open: false })
assert.ok(!bare.props.children.some(c => c && c.key === 'tmpl'),
  'unlabeled row grows no template badge (the title already IS the name)')

// -- 5. fleet landing row: template COLUMN beside the label -------------------
const row = PaneRow({ run: { ...proof, status: 'done', updated: '2026-11-24T00:00:00Z' }, thisChat: false })
const titleChildren = row.props.title.props.children
assert.equal(titleChildren[0].props.children, 'ship20W2c', 'fleet row titles with the label')
const col = titleChildren.find(c => c && c.props && c.props.title === 'template')
assert.ok(col && col.props.children === 'estate-bead-crew', 'fleet row keeps the template COLUMN')
const bareRow = PaneRow({ run: { id: 'r', name: 'tpl', status: 'done' }, thisChat: false })
assert.ok(!bareRow.props.title.props.children.some(c => c && c.props && c.props.title === 'template'),
  'unlabeled fleet row prints its name once (no duplicate column)')

// -- 6. rail model: pills carry the resolved label ----------------------------
const rail = railModel([{ ...proof, status: 'running', started: '2026-11-24T00:00:00Z', owner: { session_id: 'S' } }])
assert.equal(rail.pills[0].label, 'ship20W2c', 'rail pill labels with the instance')

console.log('PASS test_title_resolver_l8i.mjs: resolver arms, template demotion, pill/tray/fleet proof-cases')
