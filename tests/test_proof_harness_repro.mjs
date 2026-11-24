// Slice A reproducibility e2e (bd_2026-11-13-iqf): the proof driver was run
// TWICE, independently, against the same merged head, and both capture sets
// are committed here. This spec is the in-repo proof that the capture is
// reproducible: the two manifests' REPRO sections (volatile-masked content
// hashes) must be hash-equal — the double-run hash diff is empty — while
// every raster file's sha256 in each manifest must match the bytes in-repo
// (immutability). Runs anywhere, CI included: no app, no gateway — the
// double run happened at capture time; the proof of reproducibility is the
// pinned pair.
//
// The volatile classes this tolerates (and ONLY these) are the driver's
// exported VOLATILE_MASKS; the mask itself is pinned with samples below so
// the tolerance can never silently widen to "hash nothing".
import assert from 'node:assert/strict'
import crypto from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { maskVolatile, canonicalJson } from './proof-harness/capture.mjs'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const driver = join(root, 'tests', 'proof-harness', 'capture.mjs')
const setRoot = join(root, 'tests', 'proof-harness', 'captured', 'bd_2026-11-13-iqf')
const sha256 = buf => crypto.createHash('sha256').update(buf).digest('hex')

// 1. mask law (positive + negative control): declared volatile tokens are
//    masked; stable UI prose survives; the census line survives.
{
  const sample = [
    'ui2-proof-held · held · 1/3 terminal · run 46s',
    'run 5m 54s', '20261123-205616-ui2-proof-held', '1 min ago', 'now',
    '2026-11-23T21:00:00', 'runs 1 · running 0 · held 1 · failed 0',
    'UI2 proof: release this held gate after capture?',
  ].join('\n')
  const masked = maskVolatile(sample)
  for (const gone of ['20261123-205616-ui2-proof-held', 'run 46s', '5m 54s',
                      '1 min ago', '2026-11-23T21:00:00']) {
    assert.ok(!masked.includes(gone), `volatile token survived the mask: ${gone}`)
  }
  for (const kept of ['1/3 terminal', 'runs 1 · running 0 · held 1 · failed 0',
                      'UI2 proof: release this held gate after capture?']) {
    assert.ok(masked.includes(kept), `stable content was destroyed by the mask: ${kept}`)
  }
  assert.ok(masked.includes('<RUN-ID>') && masked.includes('<RUN-CLOCK>')
    && masked.includes('<REL-TIME>') && masked.includes('<DATE>'),
  'all four volatile classes must actually fire on the sample (mask is not a no-op)')
  console.log('PASS mask law: volatile classes masked, stable prose kept')
}

// 2. the committed pair: two independent runs, one candidate, hash-equal
//    repro layer (the double-run hash diff is empty at the content layer).
function loadSet(name) {
  const dir = join(setRoot, name)
  const manifestPath = join(dir, 'manifest.json')
  assert.ok(existsSync(manifestPath), `capture set missing its manifest: ${manifestPath}`)
  const m = JSON.parse(readFileSync(manifestPath, 'utf8'))
  assert.equal(m.schema, 'proof-harness/1', `${name}: manifest schema`)
  assert.equal(m.case, 'baseline', `${name}: captured case`)
  assert.deepEqual(m.only, ['directive_card', 'pane_workflows'],
    `${name}: captured with the slice A --only filter`)
  assert.deepEqual(m.surfaces, ['directive_card', 'pane_workflows'],
    `${name}: exactly the two slice A surfaces`)
  for (const c of m.captures) {
    const png = join(dir, c.file)
    const bytes = readFileSync(png)
    assert.ok(bytes.length > 4096 && bytes[0] === 0x89 && bytes[1] === 0x50
      && bytes[2] === 0x4e && bytes[3] === 0x47, `${name}/${c.file}: PNG magic+size`)
    assert.equal(sha256(bytes), c.sha256, `${name}/${c.file}: committed bytes diverged from the manifest hash (immutable law)`)
    assert.equal(bytes.length, c.bytes, `${name}/${c.file}: byte count`)
    assert.ok(c.content_file && c.content_sha256, `${name}/${c.file}: slice A captures all carry a content layer`)
    const content = readFileSync(join(dir, c.content_file))
    assert.equal(sha256(content), c.content_sha256, `${name}/${c.content_file}: content layer diverged`)
    // masked layer really is masked (recompute from disk prose is not
    // possible — the raster is truth — but idempotence of the mask is)
    assert.equal(maskVolatile(content.toString('utf8')), content.toString('utf8'),
      `${name}/${c.content_file}: masking is idempotent on committed content`)
  }
  const fileMap = Object.fromEntries(m.captures.map(c => [c.file, c.content_sha256]))
  assert.equal(m.repro.combined_sha256, sha256(Buffer.from(canonicalJson(fileMap))),
    `${name}: repro.combined_sha256 recomputes from the per-capture content hashes`)
  return m
}

const [a, b] = ['set-1', 'set-2'].map(loadSet)
assert.equal(a.candidate.plugin_sha256, b.candidate.plugin_sha256,
  'both runs captured the SAME candidate bytes')
assert.match(a.candidate.plugin_sha256, /^[0-9a-f]{64}$/, 'candidate pinned by digest')
assert.equal(a.candidate.repo_head, b.candidate.repo_head,
  'both runs ran at the same repo head (current merged head at capture time)')
assert.deepEqual(a.repro, b.repro,
  'DOUBLE-RUN REPRODUCIBILITY: the two manifests\' repro sections are not hash-equal')
assert.equal(a.repro.combined_sha256, b.repro.combined_sha256,
  'double-run combined repro hash differs — capture is NOT reproducible')
// Rasters may legitimately differ between runs (clock pixels); when they
// do, that is recorded, not hidden — the content layer is the claim.
const rasterDrift = []
for (let i = 0; i < a.captures.length; i++) {
  assert.equal(a.captures[i].file, b.captures[i].file, 'capture file lists drifted')
  if (a.captures[i].sha256 !== b.captures[i].sha256) rasterDrift.push(a.captures[i].file)
}
console.log(`PASS committed pair: repro hash-equal (${a.repro.combined_sha256.slice(0, 12)}…), ${a.captures.length} captures per set, candidate pinned at ${a.candidate.repo_head.slice(0, 8)}${rasterDrift.length ? `; raster-only drift recorded for ${rasterDrift.length} file(s)` : ''}`)

// 3. CLI/committed-pair lockstep: what the driver PLANS at this head is
//    exactly what the sets contain (drift = red, not a stale-trust pass).
{
  const r = JSON.parse(execFileSync('node', [driver, '--only', 'directive,pane', '--plan'],
    { encoding: 'utf8', timeout: 60_000 }))
  assert.deepEqual([...r.plan.surfaces].sort(), a.surfaces,
    'plan surfaces and committed set surfaces drifted apart')
  const bySurface = {}
  for (const c of a.captures) (bySurface[c.surface] ||= []).push(c.file)
  assert.deepEqual(Object.keys(bySurface).sort(), ['directive_card', 'pane_workflows'])
  assert.deepEqual(bySurface.directive_card.slice().sort(),
    ['captures/03-directive-card-full.png', 'captures/04-directive-card.png'])
  assert.deepEqual(bySurface.pane_workflows.slice().sort(),
    ['captures/01-pane-runs.png', 'captures/02-pane-run-detail.png'])
  console.log('PASS plan/pair lockstep: 2 directive + 2 pane captures per set')
}

console.log('ALL PASS: proof-harness slice A reproducibility (mask law, committed double-run, plan lockstep)')
