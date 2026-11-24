// Slice B reproducibility e2e (bd_2026-11-13-xow): the gate/toast proof —
// the case #717 deleted, restored onto the slice-A repro runner — was run
// TWICE, independently, against one candidate pin, and both capture sets
// are committed here. This spec re-verifies them from bytes: per-file
// sha256 (immutability), the volatile-masked content layer (nothing drifted
// on disk), the REPRO sections (the double-run hash diff is empty), and the
// plan/pair lockstep (what the driver PLANS at this head is exactly what
// the sets contain). CI-safe: no app, no gateway — the double run happened
// at capture time; the proof is the pinned pair.
import assert from 'node:assert/strict'
import crypto from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { maskVolatile, canonicalJson } from './proof-harness/capture.mjs'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const driver = join(root, 'tests', 'proof-harness', 'capture.mjs')
const setRoot = join(root, 'tests', 'proof-harness', 'captured', 'bd_2026-11-13-xow')
const sha256 = buf => crypto.createHash('sha256').update(buf).digest('hex')

// 1. mask law for the gate/toast layer specifically: every per-run token
//    inside the receipt toast line and the held cell must mask; the claim
//    prose (question, options, 'Answer saved', scope note) must survive.
{
  const sample = [
    'UI2 proof: record this answer?',
    'requester: @local-' + 'a'.repeat(64),
    'Approve review', 'Keep for revision',
    'Answer saved · Approve review · @local-' + 'b'.repeat(64)
      + ' · 20261124-051201-ui2-proof-gate / review · 2026-11-24T05:12:33.482+08:00',
    'Answered · 2026-11-24T05:12:33',
    'held 1m 42s', '2 min ago',
  ].join('\n')
  const masked = maskVolatile(sample)
  for (const gone of ['20261124-051201-ui2-proof-gate', 'a'.repeat(64), 'b'.repeat(64),
                      '2026-11-24T05:12:33.482+08:00', '2026-11-24T05:12:33',
                      'held 1m 42s', '2 min ago']) {
    assert.ok(!masked.includes(gone), `volatile token survived the gate/toast mask: ${gone}`)
  }
  for (const kept of ['UI2 proof: record this answer?', 'Approve review', 'Keep for revision',
                      'Answer saved', 'requester:', '/ review']) {
    assert.ok(masked.includes(kept), `stable gate prose destroyed by the mask: ${kept}`)
  }
  assert.ok(masked.includes('<HELD-CLOCK>'), 'held-elapsed chip must mask to <HELD-CLOCK>')
  // the status word and the census chip are NOT clocks:
  assert.ok(maskVolatile('ui2-proof-held · held · 1/3 terminal').includes('held · 1/3'),
    'bare held status word and census chip must survive the held-clock mask')
  console.log('PASS gate/toast mask law: run identity, clocks, held-elapsed chip and ISO times masked; receipt prose kept')
}

// 2. the committed pair: two independent benches, one candidate, hash-equal
//    repro layer — and every manifest hash true against the committed bytes.
function loadSet(name) {
  const dir = join(setRoot, name)
  const manifestPath = join(dir, 'manifest.json')
  assert.ok(existsSync(manifestPath), `capture set missing its manifest: ${manifestPath}`)
  const m = JSON.parse(readFileSync(manifestPath, 'utf8'))
  assert.equal(m.schema, 'proof-harness/1', `${name}: manifest schema`)
  assert.equal(m.case, 'gate', `${name}: captured case`)
  assert.deepEqual(m.only, ['gate_modal', 'toast'],
    `${name}: captured with the slice B --only gate,toast filter`)
  assert.deepEqual(m.surfaces, ['gate_modal', 'toast'],
    `${name}: exactly the two slice B surfaces`)
  for (const c of m.captures) {
    const png = join(dir, c.file)
    const bytes = readFileSync(png)
    assert.ok(bytes.length > 4096 && bytes[0] === 0x89 && bytes[1] === 0x50
      && bytes[2] === 0x4e && bytes[3] === 0x47, `${name}/${c.file}: PNG magic+size`)
    assert.equal(sha256(bytes), c.sha256, `${name}/${c.file}: committed bytes diverged from the manifest hash (immutable law)`)
    assert.equal(bytes.length, c.bytes, `${name}/${c.file}: byte count`)
    if (c.content_file) {
      const content = readFileSync(join(dir, c.content_file))
      assert.equal(sha256(content), c.content_sha256, `${name}/${c.content_file}: content layer diverged`)
      assert.equal(maskVolatile(content.toString('utf8')), content.toString('utf8'),
        `${name}/${c.content_file}: masking is idempotent on committed content`)
    }
  }
  // the repro-claiming frames carry a content layer (slice B law): the held
  // cell, the saved receipt, the after-view receipt and the toast. Pending
  // and the fail-once error ride raster-only (their text is a spinner and a
  // short banner — below the trivial-content threshold by design).
  for (const must of ['07-gate-held', '09-gate-saved', '10-gate-toast', '11-gate-after-view']) {
    const c = m.captures.find(x => x.file.endsWith(must + '.png'))
    assert.ok(c && c.content_file, `${name}: ${must}.png must carry a content layer (repro law)`)
  }
  const fileMap = Object.fromEntries(m.captures.filter(c => c.content_sha256).map(c => [c.file, c.content_sha256]))
  assert.equal(m.repro.combined_sha256, sha256(Buffer.from(canonicalJson(fileMap))),
    `${name}: repro.combined_sha256 recomputes from the per-capture content hashes`)
  return m
}

const [a, b] = ['set-1', 'set-2'].map(loadSet)
assert.equal(a.candidate.plugin_sha256, b.candidate.plugin_sha256,
  'both runs captured the SAME candidate bytes')
assert.match(a.candidate.plugin_sha256, /^[0-9a-f]{64}$/, 'candidate pinned by digest')
assert.match(a.candidate.repo_head, /^[0-9a-f]{40}$/, 'set-1 pins its repo head')
assert.match(b.candidate.repo_head, /^[0-9a-f]{40}$/, 'set-2 pins its repo head')
assert.match(a.candidate.merge_base_origin_main, /^[0-9a-f]{40,}$/, 'set-1 pins the merge-base')
assert.deepEqual(a.repro, b.repro,
  'DOUBLE-RUN REPRODUCIBILITY: the two manifests\' repro sections are not hash-equal')
assert.equal(a.repro.combined_sha256, b.repro.combined_sha256,
  'double-run combined repro hash differs — gate/toast capture is NOT reproducible')
// The toast surface claim: the pair's surfaces list (asserted above as
// exactly gate_modal + toast) and the content-layer rule below pin that the
// toast frame is present and hashed, not merely listed.
const rasterDrift = []
for (let i = 0; i < a.captures.length; i++) {
  assert.equal(a.captures[i].file, b.captures[i].file, 'capture file lists drifted')
  assert.equal(a.captures[i].surface, b.captures[i].surface, 'capture surfaces drifted')
  if (a.captures[i].sha256 !== b.captures[i].sha256) rasterDrift.push(a.captures[i].file)
}
console.log(`PASS committed pair: repro hash-equal (${a.repro.combined_sha256.slice(0, 12)}…), ${a.captures.length} captures per set, candidate pinned at ${a.candidate.repo_head.slice(0, 8)}${rasterDrift.length ? `; raster-only drift recorded for ${rasterDrift.length} file(s)` : ''}`)

// 3. CLI/committed-pair lockstep: what the driver PLANS at this head under
//    the slice B verification command is exactly what the sets contain —
//    including the case resolved from the tokens (no explicit --case).
{
  const r = JSON.parse(execFileSync('node', [driver, '--only', 'gate,toast', '--plan'],
    { encoding: 'utf8', timeout: 60_000 }))
  assert.equal(r.plan.case, 'gate',
    '--only gate,toast must resolve the gate case (slice B case-resolution law)')
  assert.deepEqual([...r.plan.surfaces].sort(), a.surfaces,
    'plan surfaces and committed set surfaces drifted apart')
  const bySurface = {}
  for (const c of a.captures) (bySurface[c.surface] ||= []).push(c.file)
  assert.deepEqual(Object.keys(bySurface).sort(), ['gate_modal', 'toast'])
  assert.deepEqual(bySurface.gate_modal.slice().sort(),
    ['captures/07-gate-held.png', 'captures/08-gate-pending.png', 'captures/08b-gate-error.png',
     'captures/09-gate-saved.png', 'captures/11-gate-after-view.png'])
  assert.deepEqual(bySurface.toast, ['captures/10-gate-toast.png'])
  console.log('PASS plan/pair lockstep: 5 gate + 1 toast capture per set, case resolved from tokens')
}

console.log('ALL PASS: proof-harness slice B reproducibility (gate/toast mask, committed double-run, plan lockstep)')
