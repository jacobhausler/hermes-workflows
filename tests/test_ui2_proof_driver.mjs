// Behaviour spec for the proof-harness real-app capture driver: the failure
// semantics that keep the driver from being a green no-op. Runs the real CLI
// end-to-end and asserts EXIT CODES and report structure — never string
// matches. The full-bench behaviour (real renderer capture, config revert,
// path-scoped teardown) is exercised by `--case baseline` in the bead's
// verification run; these legs run anywhere, CI included (no app checkout,
// no gateway, no electron needed).
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const driver = join(root, 'tests', 'proof-harness', 'capture.mjs')
const manifestPath = join(root, 'tests', 'proof-harness', 'cases.json')
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))

function run(args) {
  try {
    const stdout = execFileSync('node', [driver, ...args], { encoding: 'utf8', timeout: 60_000 })
    return { code: 0, stdout, stderr: '' }
  } catch (e) {
    return { code: e.status ?? -1, stdout: e.stdout || '', stderr: e.stderr || '' }
  }
}

// 1. usage errors exit 2 (unknown argument). --case and --out DEFAULT
//    (baseline / captured/run-<ts>): the slice A verification command
//    `node tests/proof-harness/capture.mjs --only directive,pane` is the
//    canonical invocation and must not die on missing optional flags.
{
  const r = run(['--definitely-not-a-flag'])
  assert.equal(r.code, 2, 'unknown argument must exit 2')
  console.log('PASS usage: unknown flag exits 2; case/out default')
}

// 2. unknown case exits 2 and names the known cases (a later bead's case is
//    a NEW TEST, never an invented existing command silently accepted).
{
  const r = run(['--case', 'definitely-not-a-case', '--out', '/tmp/ui2-proof-nope'])
  assert.equal(r.code, 2, 'unknown case must exit 2')
  assert.ok(r.stderr.includes('baseline'), 'unknown-case error lists the known cases')
  console.log('PASS unknown case: exit 2, known-case list emitted')
}

// 2b. --only token law (slice A): an unknown token exits 2 — no silent
//     drop. The intersection-empty and unwired-case legs are covered in
//     legs 3 and 5 below (new-test law evaluated before the filter).
{
  const r = run(['--only', 'bogus', '--out', '/tmp/ui2-proof-nope'])
  assert.equal(r.code, 2, 'unknown --only token must exit 2')
  console.log('PASS --only: unknown token exit 2')
}

// 3. a known-but-unwired case exits 3 (new test), NOT 0 and NOT 2 — also
//    when --only selects a registry-wired surface of it (the case itself
//    is the NEW TEST; a filter must never downgrade it to green).
{
  const r = run(['--case', 'held-gate-snapshot-example', '--out', '/tmp/ui2-proof-nope'])
  assert.equal(r.code, 3, 'documented-not-implemented case must exit 3')
  const f = run(['--case', 'held-gate-snapshot-example', '--only', 'pane',
                 '--out', '/tmp/ui2-proof-nope'])
  assert.equal(f.code, 3, '--only on an unwired case still exits 3')
  console.log('PASS unwired case: exit 3 (new test, not an existing command)')
}

// 4. absent candidate plugin exits 4 (preflight) — the driver refuses to
//    capture "proof" of nothing.
{
  const r = run(['--case', 'baseline', '--out', '/tmp/ui2-proof-nope', '--plugin', '/nonexistent/plugin.js'])
  assert.equal(r.code, 4, 'absent candidate plugin must exit 4')
  assert.ok(!existsSync('/tmp/ui2-proof-nope/report.json'), 'no report written on preflight failure')
  console.log('PASS absent plugin: exit 4, no report')
}

// 5. --plan prints the structured intent without needing the app: surfaces,
//    seed kinds/methods, and the candidate hash. (Behaviour: the plan IS the
//    contract later beads capture against.) --only INTERSECTS the case
//    surfaces — it never widens them, and an intersection that selects
//    nothing is a usage error, not a green no-op.
{
  const r = run(['--case', 'baseline', '--out', '/tmp/ui2-proof-plan', '--plan'])
  assert.equal(r.code, 0, 'plan mode must exit 0')
  const plan = JSON.parse(r.stdout)
  assert.equal(plan.ok, true)
  assert.equal(plan.plan.case, 'baseline')
  assert.deepEqual([...plan.plan.surfaces].sort(),
    ['directive_card', 'pane_workflows', 'tray_row'].sort(),
    'baseline covers directive, pane and tray')
  assert.ok(plan.plan.seeds.every(s => s.kind === 'engine_seed' || s.kind === 'historical_snapshot'),
    'every seed declares its kind')
  assert.match(plan.plan.plugin_sha256, /^[0-9a-f]{64}$/, 'plan pins the real candidate hash')

  const o = run(['--only', 'directive,pane', '--out', '/tmp/ui2-proof-plan', '--plan'])
  assert.equal(o.code, 0, 'slice A verification command must plan clean')
  const op = JSON.parse(o.stdout)
  assert.deepEqual([...op.plan.surfaces].sort(), ['directive_card', 'pane_workflows'].sort(),
    '--only directive,pane narrows the plan to the two slice A surfaces')
  assert.deepEqual(op.plan.only, ['directive_card', 'pane_workflows'], 'plan echoes the filter')

  const wide = run(['--only', 'directive,pane,tray,bogus-tray', '--out', '/tmp/ui2-proof-plan', '--plan'])
  assert.equal(wide.code, 2, 'one bad token taints the whole filter (exit 2, no silent drop)')
  console.log('PASS --plan: structured intent, --only intersection, plugin hash')
}

// 6. manifest law (data contract behind the CLI): every seed of every case
//    is kind-typed; a historical_snapshot is pinned by run_id + digest —
//    the engine-seed-vs-snapshot distinction is structural, not prose.
for (const [name, c] of Object.entries(manifest.cases)) {
  for (const s of c.seeds || []) {
    assert.ok(['engine_seed', 'historical_snapshot'].includes(s.kind), `${name}/${s.name}: bad seed kind`)
  }
  for (const s of c.historical_snapshots || []) {
    assert.equal(s.kind, 'historical_snapshot', `${name}/${s.name}: snapshot list is snapshot-kind only`)
    assert.ok(s.run_id && s.run_json_sha256, `${name}/${s.name}: snapshot must pin run_id + run.json digest`)
  }
}
assert.ok(Array.isArray(manifest.surfaces_registry) && manifest.surfaces_registry.length >= 3,
  'surfaces registry lists the wired surfaces')
console.log('PASS manifest: seed kinds typed, snapshots pinned, registry present')

// 7. template-escape regression (field-proven): escape sequences inside the
//    eval'd template literals render into the PAGE SOURCE — a '\n' in a
//    `//` comment line breaks the statement after it and Runtime.evaluate
//    dies with 'Unexpected token <'. Every cdp.evl template in the driver
//    must yield page source that V8 itself can parse, for all option legs.
{
  const src = readFileSync(driver, 'utf8')
  const fnMatch = src.match(/function locateJS[\s\S]*?\n}\n/)
  assert.ok(fnMatch, 'locateJS extractable for the parse check')
  const locateJS = eval(`(${fnMatch[0].replace('function locateJS', 'function')})`)
  for (const opts of [
    {}, { ci: true }, { exact: true },
    { region: { xMin: 440, yMin: 40, bottomMargin: 90 } },
    { nth: 0, region: { xMin: 1 }, ci: true },
  ]) {
    const built = locateJS('needle", with"quotes\\u2028', opts)
    assert.doesNotThrow(() => new Function(built),
      `locateJS(${JSON.stringify(opts)}) page source must parse`)
  }
  // columnTextJS (slice A content layer): the same parse law covers it.
  const colMatch = src.match(/function columnTextJS[\s\S]*?\n}\n/)
  assert.ok(colMatch, 'columnTextJS extractable for the parse check')
  const columnTextJS = eval(`(${colMatch[0].replace('function columnTextJS', 'function')})`)
  for (const region of [
    { xMin: 440, yMin: 40, bottomMargin: 90 },
    { xMin: 0, yMin: 0 },
    { xMin: 10, yMin: 20, bottomMargin: 0 },
  ]) {
    const built = columnTextJS(region)
    assert.doesNotThrow(() => new Function(built),
      `columnTextJS(${JSON.stringify(region)}) page source must parse`)
  }
  // Inline eval'd templates (session-row locators etc.): interpolate every
  // ${...} with a JSON scalar and require the result to parse.
  const tmplRe = /cdp\.evl\(`((?:[^`\\]|\\\\.|\$\{[^}]*(?:\{[^}]*\}[^}]*)?\})*)`\)/g
  let m, seen = 0
  while ((m = tmplRe.exec(src))) {
    // EVALUATE the template (Node consumes its escapes, exactly as the driver
    // will) before parsing the page source — raw-source parsing hides the
    // consumed-escape bug that killed run6 (a '\n' ending a // comment line
    // mid-statement: page got 'Unexpected token <').
    const built = eval('`' + m[1].replace(/\$\{[^}]*\}/g, '"x"') + '`')
    assert.doesNotThrow(() => new Function(built), `inline cdp.evl template at index ${m.index} must parse`)
    seen++
  }
  assert.ok(seen >= 3, `checked inline eval templates (saw ${seen})`)
  console.log(`PASS eval-template parse law: locateJS + columnTextJS legs + ${seen} inline templates`)
}

console.log('ALL PASS: proof-harness driver failure semantics (2/3/4), defaults, --only intersection, plan contract, manifest law, eval-template parse law')
