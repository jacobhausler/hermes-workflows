// Behaviour spec for the owned-bench retention step (bd_2026-11-13-4fy):
// the startup sweep that reclaims proven-dead sibling bench trees under the
// driver's proof tree. Fake trees only — no bench, no app, no gateway, no
// electron — so it runs in CI anywhere. Pins the never-delete law: living,
// unknown, owner-held, tracked and committed-manifest-referenced trees
// survive; dead scratch/rotation/dead-attempt trees go, one record each with
// path + MiB. Imports the driver module (the CLI guard proves importing
// never boots the bench).
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { planBenchRetention } from './proof-harness/capture.mjs'

const DAY = 86_400_000
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ui2-retention-4fy-'))
const proof = path.join(root, 'captured')
fs.mkdirSync(proof)
const stampBack = (p, ageMs) => {
  const t = new Date(Date.now() - ageMs)
  for (const e of fs.readdirSync(p, { withFileTypes: true })) {
    const c = path.join(p, e.name)
    if (e.isDirectory() && !e.isSymbolicLink()) stampBack(c, ageMs)
    else fs.utimesSync(c, t, t)
  }
  fs.utimesSync(p, t, t)
}
// One fake bench tree: owned marker + optional sealed manifest (0444, like
// writeImmutable) + payload, back-dated to ageMs.
function bench(base, name, { owned = true, sealed = false, ageMs = DAY,
                             payloadKiB = 0, extra = {} } = {}) {
  const dir = path.join(base, name)
  fs.mkdirSync(dir, { recursive: true })
  if (owned) fs.writeFileSync(path.join(dir, '.ui2-proof-owned'), 'fake run\n')
  if (payloadKiB) {
    fs.mkdirSync(path.join(dir, 'bench'), { recursive: true })
    fs.writeFileSync(path.join(dir, 'bench', 'payload.bin'),
      Buffer.alloc(payloadKiB * 1024, 7))
  }
  for (const [rel, content] of Object.entries(extra)) {
    const p = path.join(dir, rel)
    fs.mkdirSync(path.dirname(p), { recursive: true })
    fs.writeFileSync(p, content)
  }
  if (sealed) {
    fs.writeFileSync(path.join(dir, 'manifest.json'), '{"schema":"proof-harness/1"}\n')
    fs.chmodSync(path.join(dir, 'manifest.json'), 0o444)
  }
  stampBack(dir, ageMs)
  return dir
}
const keptReason = (res, name) =>
  (res.kept.find(k => k.dir === path.join(proof, name)) || {}).reason
const reclaimedRec = (res, name) =>
  res.reclaimed.find(r => r.dir === path.join(proof, name))
const repoOpts = { repoRoot: root } // no git index here: nothing is tracked

// --- fake proof tree --------------------------------------------------------
// (1) sealed run-* scratch older than the run start: reclaimable at once,
//     honest MiB — the acceptance shape of "run twice, second run's log
//     shows reclamation" (the seal proves terminal, so no grace applies).
bench(proof, 'run-sealed-old', { sealed: true, payloadKiB: 3 * 1024 + 512 })
// (2) *.stale-* rotation of a dead run: reclaimable even when sealed.
bench(proof, 'run-rot.stale-1700000000000', { sealed: true, payloadKiB: 1024 })
// (3) *abandoned-* rotation: reclaimable.
bench(proof, 'gate.abandoned-5')
// (4) ROOT CAUSE: a dead capture attempt — custom proof-named dir, owned, NO
//     manifest ever written — older and silent past grace.
bench(proof, 'set-dead-attempt', { payloadKiB: 2048 })
// (5) LIVE crew-wave sibling: unsealed, last written BEFORE my run started
//     (so "older than the current run") but inside the grace window.
bench(proof, 'run-live-sibling', { ageMs: 180_000 })
// (6) a tree written after the run start: never touched.
bench(proof, 'run-fresh', { ageMs: 0 })
// (7) unknown trees (no ownership marker) survive everything.
bench(proof, 'run-unknown.stale-1', { owned: false })
// (8) an explicitly owner-held dead tree survives (retention.py marker law).
bench(proof, 'set-owner-held', { extra: { '.owner-held': '' } })
// (9) custom-named, sealed-but-uncommitted: pending proof bytes, kept.
bench(proof, 'set-pending-proof', { sealed: true })
// (10) a plain file at the proof root is not a tree; untouched.
fs.writeFileSync(path.join(proof, 'stray.txt'), 'x\n')

const opts = { runStartMs: Date.now() - 120_000, nowMs: Date.now(),
               graceMs: 600_000, ...repoOpts }

// dryRun first: the plan must name every dead tree and touch nothing.
let res = planBenchRetention({ proofRoot: proof, dryRun: true, ...opts })
assert.equal(reclaimedRec(res, 'run-sealed-old').reason, 'scratch')
assert.equal(reclaimedRec(res, 'run-sealed-old').mib, 3.5, 'MiB from real payload bytes')
assert.equal(reclaimedRec(res, 'run-rot.stale-1700000000000').reason, 'rotation')
assert.equal(reclaimedRec(res, 'gate.abandoned-5').reason, 'rotation')
assert.equal(reclaimedRec(res, 'set-dead-attempt').reason, 'dead-attempt')
assert.equal(keptReason(res, 'run-live-sibling'), 'live-grace',
  'sibling older than my run but written inside grace is LIVE')
assert.equal(keptReason(res, 'run-fresh'), 'younger-than-run')
assert.equal(keptReason(res, 'run-unknown.stale-1'), 'unowned')
assert.equal(keptReason(res, 'set-owner-held'), 'owner-held')
assert.equal(keptReason(res, 'set-pending-proof'), 'pending-proof-uncommitted')
assert.ok(fs.existsSync(path.join(proof, 'run-sealed-old')), 'dryRun touches no disk')
console.log('PASS dryRun plan: rotations/scratch/dead-attempt named, live+unknown+held+pending kept, nothing deleted')

// A live symlink inside a dead tree must survive the rm (rm never follows).
const outside = path.join(root, 'out-target.txt')
fs.writeFileSync(outside, 'do not delete me\n')
const linked = bench(proof, 'set-with-symlink', { payloadKiB: 64 })
fs.symlinkSync(outside, path.join(linked, 'link.txt'))
{ // re-age the tree (the link itself: lstat mtime never counts, symlinks skipped)
  const t = new Date(Date.now() - DAY)
  for (const p of [path.join(linked, 'bench', 'payload.bin'),
                   path.join(linked, 'bench'), path.join(linked, '.ui2-proof-owned')])
    fs.utimesSync(p, t, t)
  fs.utimesSync(linked, t, t)
}

// The real sweep.
res = planBenchRetention({ proofRoot: proof, ...opts })
assert.ok(reclaimedRec(res, 'set-with-symlink'), 'the dead tree with a live link is reclaimed')
assert.ok(!fs.existsSync(linked))
assert.ok(fs.existsSync(outside), 'the symlink TARGET is not the tree — untouched')
for (const gone of ['run-sealed-old', 'run-rot.stale-1700000000000',
                    'gate.abandoned-5', 'set-dead-attempt', 'set-with-symlink'])
  assert.ok(!fs.existsSync(path.join(proof, gone)), `${gone} reclaimed`)
for (const alive of ['run-live-sibling', 'run-fresh', 'run-unknown.stale-1',
                     'set-owner-held', 'set-pending-proof', 'stray.txt'])
  assert.ok(fs.existsSync(path.join(proof, alive)), `${alive} kept`)
console.log('PASS real sweep: dead trees rm-d (0444 bytes included), symlink target + every kept tree survive')

// --- git legs: committed proof bytes and manifest-referenced trees ----------
const gitRoot = path.join(root, 'gitrepo')
const gproof = path.join(gitRoot, 'captured')
fs.mkdirSync(gproof, { recursive: true })
const git = (...a) => execFileSync('git', ['-C', gitRoot, ...a], { encoding: 'utf8' })
git('init', '-q', '-b', 'main')
bench(gproof, 'set-evi', { extra: { 'manifest.json':
  '{"note":"points at run-mentioned-7 for provenance"}\n', 'contents/01.txt': 'evidence\n' } })
bench(gproof, 'run-tracked-proof', { sealed: true, extra: { 'captures/a.png': 'x' } })
bench(gproof, 'run-untracked-old', { sealed: true, extra: { 'bench/p.bin': 'x' } })
bench(gproof, 'run-mentioned-7')
git('add', '--', 'captured/set-evi', 'captured/run-tracked-proof')
execFileSync('git', ['-C', gitRoot, '-c', 'user.email=t@example.invalid',
  '-c', 'user.name=t', 'commit', '-q', '-m', 'committed proof'])
res = planBenchRetention({ proofRoot: gproof,
  runStartMs: Date.now() - 120_000, nowMs: Date.now(), graceMs: 600_000,
  repoRoot: gitRoot })
if (process.env.RET4FY_DEBUG) console.error(JSON.stringify(res, null, 1))
const gReason = name =>
  (res.kept.find(k => k.dir === path.join(gproof, name)) || {}).reason
assert.equal(gReason('set-evi'), 'committed-proof')
assert.equal(gReason('run-tracked-proof'), 'committed-proof')
assert.equal(gReason('run-mentioned-7'), 'referenced-by-committed-manifest')
assert.ok(res.reclaimed.some(r => r.dir === path.join(gproof, 'run-untracked-old')
  && r.reason === 'scratch'))
assert.ok(fs.existsSync(path.join(gproof, 'run-tracked-proof'))
  && fs.existsSync(path.join(gproof, 'run-mentioned-7'))
  && !fs.existsSync(path.join(gproof, 'run-untracked-old')),
  'tracked + referenced survive, unreferenced scratch does not')
console.log('PASS committed proof bytes + manifest-referenced trees: never deleted (git)')

// absent proof root: empty plan, no crash
assert.deepEqual(planBenchRetention({ proofRoot: path.join(root, 'nope'),
  runStartMs: Date.now(), repoRoot: root }), { reclaimed: [], kept: [] })
console.log('PASS absent proof root: empty plan, no crash')

console.log('ALL PASS: owned-bench retention (rotation/scratch/dead-attempt reclaim; unknown, live, young, owner-held, pending, committed, referenced never)')
fs.rmSync(root, { recursive: true, force: true })
