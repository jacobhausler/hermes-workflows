// est-z717 ZERO-DIRECTIVE CAPTURE PIN: a run launched through the door
// (run-create, i.e. act_run) under a fake session env (HERMES_SESSION_ID=
// probe-sid) into a TEMP runs root appears in that chat's rail via ownedRuns
// — with NO ::workflow directive output anywhere on the surface the rail
// reads. The invocation stamp (owner{session_id<-HERMES_SESSION_ID} at
// creation, __init__.py) is the whole contract; the ::workflow directive is
// transcript-CARD only, never a rail requirement (owner ruling 10-06,
// est-z717; verified live at 81877ebc3).
//
// Shape: python launches the REAL door in a subprocess (isolated runner
// spawn, isolated WF_RUNS_ROOT + HERMES_HOME, wf_test_isolation resolver
// pin) and dumps {run.json, the dashboard /runs view} as JSON; this file
// loads the REAL plugin.js against stub SDK/react (test_session_tray idiom)
// and asserts the pure rail models against the real artifacts.
// RED-first was proven via a mutated model (ownedRuns capture removed);
// the mutation was reverted the same commit pass.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const root = join(here, '..')

// -- 1. launch the run through the door under the fake session env ----------
const py = `
import importlib.util, json, os, sys, tempfile
ROOT = ${JSON.stringify(root)}
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tests'))
tmp = tempfile.mkdtemp(prefix='wf-z717-')
os.environ['WF_RUNS_ROOT'] = tmp
os.environ['HERMES_HOME'] = os.path.join(tmp, 'home')
os.environ['HERMES_SESSION_ID'] = 'probe-sid'
os.environ.pop('WF_OWNER_SESSION', None)
spec = importlib.util.spec_from_file_location('wf_door_z717', os.path.join(ROOT, '__init__.py'))
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso
_iso.install(door)
door._spawn_runner = lambda r: None   # no runner in a capture pin
G = {'name': 'z717-capture', 'nodes': [{'id': 'x', 'type': 'echo', 'output': {'ok': True}}]}
out = door.act_run({'graph': G})
assert 'run_id' in out, out
run_dir = os.path.join(tmp, out['run_id'])
run_json = json.load(open(os.path.join(run_dir, 'run.json')))
spec2 = importlib.util.spec_from_file_location('hwapi_z717', os.path.join(ROOT, 'dashboard', 'plugin_api.py'))
api = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(api)
view = api._view(__import__('pathlib').Path(run_dir), full=False)
print('Z717_JSON' + json.dumps({'root': tmp, 'run_id': out['run_id'],
                                'run_json': run_json, 'view': view}))
`
const pyFile = join(mkdtempSync(join(tmpdir(), 'wf-z717-bin-')), 'launch.py')
writeFileSync(pyFile, py)
const res = spawnSync('python3', [pyFile], { encoding: 'utf8', timeout: 120000 })
assert.equal(res.status, 0, `door launch failed: ${res.stderr}`)
const line = res.stdout.split('\n').find(l => l.startsWith('Z717_JSON'))
assert.ok(line, `no Z717_JSON line in stdout: ${res.stdout.slice(0, 400)}`)
const art = JSON.parse(line.slice('Z717_JSON'.length))

// -- 2. the invocation stamp is real (no directive was ever emitted) -------
assert.equal(art.run_json.owner?.session_id, 'probe-sid',
  'run-create stamps owner.session_id from HERMES_SESSION_ID at creation')
assert.equal(art.view?.owner?.session_id, 'probe-sid',
  'the dashboard /runs view carries the same owner (what api(/runs) answers)')
for (const [label, blob] of [['run.json', JSON.stringify(art.run_json)],
                             ['/runs view', JSON.stringify(art.view)]]) {
  assert.ok(!blob.includes('::workflow'),
    `zero-directive law: ${label} carries no ::workflow output — capture is at INVOCATION, the directive is transcript-card only`)
}

// -- 3. the REAL pure rail models surface it with zero directives ----------
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
export const useQuery = () => ({ data: undefined })
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
export const ctxRestStub = () => Promise.reject(new Error('no backend in test'))
`
const stubReact = `
export const useEffect = () => {}, useId = () => 'z717-0', useRef = () => ({ current: null }), useState = i => [typeof i === 'function' ? i() : i, () => {}]
export default { useEffect, useId, useRef, useState }
`
const stubJsx = `
export const jsx = (type, props, key) => ({ type, props: props || {}, key })
export const jsxs = jsx
export const Fragment = 'Fragment'
`
const tmp = mkdtempSync(join(tmpdir(), 'wf-z717-mjs-'))
const sdkPath = join(tmp, 'sdk-stub.mjs'); writeFileSync(sdkPath, stubSdk)
const reactPath = join(tmp, 'react-stub.mjs'); writeFileSync(reactPath, stubReact)
const jsxPath = join(tmp, 'jsx-stub.mjs'); writeFileSync(jsxPath, stubJsx)
const modPath = join(tmp, 'plugin-under-test.mjs')
writeFileSync(modPath, readFileSync(join(root, 'desktop', 'plugin.js'), 'utf8')
  .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
  .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href))
  .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href)))
const mod = await import(pathToFileURL(modPath).href)

// The rail law: ownedRuns(runs, sid) includes the run under its session, and
// the pill model renders it — the 4 s poll over api('/runs') is what feeds
// this; no directive string participates anywhere in the chain.
const runs = [art.view]
const owned = mod.ownedRuns(runs, 'probe-sid', '')
assert.equal(owned.length, 1, 'ownedRuns includes the door-launched run under the fake session (zero directives)')
assert.equal(owned[0].id, art.run_id, 'the owned run IS the launched run')
const rail = mod.railModel(owned)
assert.ok(rail.pills.some(p => p.id === art.run_id),
  'railModel folds the live run into PillRail pills (the always-on surface)')
// A DIFFERENT chat sees nothing — honest absence, the run is not broadcast.
assert.equal(mod.ownedRuns(runs, 'some-other-sid', '').length, 0,
  'another chat owns nothing (the rail is owner-keyed, not a global feed)')
// Blank owner stays pane-only (the ownedRuns law the estate-shape rule rides).
assert.equal(mod.ownedRuns([{ ...art.view, owner: { session_id: null } }], 'probe-sid', '').length, 0,
  'blank/null owner => never in any rail (pane-only, honest absent)')

rmSync(tmp, { recursive: true, force: true })
rmSync(art.root, { recursive: true, force: true })
console.log('ALL PASS test_z717_zero_directive_capture (door run-create under HERMES_SESSION_ID=probe-sid -> ownedRuns + railModel surface it, zero ::workflow output on the rail surface, owner-keyed honest absence)')
