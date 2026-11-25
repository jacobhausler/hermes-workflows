// Behaviour spec for the owned-bench retention step (bd_2026-11-13-4fy,
// fail-closed after the wave-B review): the startup sweep that reclaims
// proven-dead sibling bench trees under the driver's proof tree. Fake trees
// only — no bench, no app, no gateway, no electron boot (the one CLI leg
// dies in provisioning on a stub hermes, AFTER the sweep) — so it runs in
// CI anywhere. Pins the never-delete law: living, unknown, owner-held,
// tracked, git-query-unproven, scan-incomplete, manifest-corrupt-while-
// young, manifest-unreadable, reference-set-unproven and committed-manifest-
// referenced trees survive; ONLY proven-abandoned or proven-terminal trees
// go, one record each with path + MiB. Every premise the wave-B review
// named is pinned on its own leg: valid git + corrupt manifest, Git failure,
// incomplete scan, an alive DETACHED supervisor with a manifest present, and
// the boot window between the owned marker and the first supervisor record.
// The real CLI entrypoint is exercised on synthetic temp trees only (the
// review's retention-probe.mjs shape survives the shipped sweep). Imports
// the driver module (the CLI guard proves importing never boots the bench).
import assert from 'node:assert/strict'
import { execFileSync, spawn } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { planBenchRetention } from './proof-harness/capture.mjs'

const DAY = 86_400_000
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ui2-retention-4fy-'))
const proof = path.join(root, 'captured')
fs.mkdirSync(proof)
// repoRoot must be a REAL repo for the tracked-provenance leg to be PROVEN
// (empty index → nothing tracked, honestly). The 4fy fail-closed law refuses
// to read a git error as "no tracked bytes" (see the git-unproven leg).
execFileSync('git', ['-C', root, 'init', '-q', '-b', 'main'])
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
// writeImmutable) + payload, back-dated to ageMs. The sealed content is the
// driver's OWN terminal record shape (schema + captures) — existence alone
// is not terminality since the wave-B qualification.
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
    fs.writeFileSync(path.join(dir, 'manifest.json'),
      '{"schema":"proof-harness/1","captures":[],"repro":{}}\n')
    fs.chmodSync(path.join(dir, 'manifest.json'), 0o444)
  }
  stampBack(dir, ageMs)
  return dir
}
const keptReason = (res, name) =>
  (res.kept.find(k => k.dir === path.join(proof, name)) || {}).reason
const reclaimedRec = (res, name) =>
  res.reclaimed.find(r => r.dir === path.join(proof, name))
const repoOpts = { repoRoot: root } // real repo, empty index: tracked-proven absent

// --- fake proof tree --------------------------------------------------------
// (1) sealed run-* scratch older than the run start: reclaimable at once,
//     honest MiB — the acceptance shape of "run twice, second run's log
//     shows reclamation" (a VALID terminal manifest record proves terminal,
//     so no grace applies).
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

// --- PREMISE: valid git + corrupt manifest (wave-B review) -------------------
// The review's retention-probe.mjs shape against a repoRoot where git WORKS:
// a one-second-old owned scratch dir whose manifest.json is unreadable junk.
// A corrupt manifest is NOT the terminal record, so existence must not skip
// the grace window — the tree is kept. And the corrupt content never FREEZES
// an otherwise proved-abandoned tree: the same shape past every evidence
// gate still reclaims (positive control: fail-closed is not keep-forever).
{
  const cproof = path.join(root, 'corrupt')
  fs.mkdirSync(cproof)
  const fresh = bench(cproof, 'run-incomplete', { ageMs: 1000, extra: { 'manifest.json': 'not a terminal manifest' } })
  const oldScratch = bench(cproof, 'run-old-corrupt', { extra: { 'manifest.json': '{torn' } })
  const oldCustom = bench(cproof, 'set-old-corrupt', { extra: { 'manifest.json': 'x' } })
  const cres = planBenchRetention({ proofRoot: cproof,
    runStartMs: Date.now(), nowMs: Date.now(), graceMs: 600_000, repoRoot: root })
  const cReason = name =>
    (cres.kept.find(k => k.dir === path.join(cproof, name)) || {}).reason
  assert.equal(cReason('run-incomplete'), 'live-grace',
    'one-second-old tree with corrupt manifest: corrupt proves nothing, the grace window keeps it')
  assert.ok(fs.existsSync(fresh))
  assert.ok(cres.reclaimed.some(r => r.dir === oldScratch && r.reason === 'scratch'),
    'an OLD corrupt-manifest scratch tree still reclaims on abandonment evidence')
  assert.ok(cres.reclaimed.some(r => r.dir === oldCustom && r.reason === 'dead-attempt'),
    'a corrupt manifest never freezes an otherwise proved-dead attempt')
  console.log('PASS corrupt manifest: fresh kept by grace (never bypassed), old still reclaimable on evidence')
}

// --- PREMISE: Git failure = unproven, never "untracked" ----------------------
// The probe passed a non-repo repoRoot; base read the git error as zero
// tracked bytes and reclaimed. Fail closed: a failed git query keeps every
// tree, whatever its age or manifest state — reclaimed must be EMPTY.
{
  const nproof = path.join(root, 'nogit')
  fs.mkdirSync(nproof)
  bench(nproof, 'run-incomplete', { ageMs: 1000, extra: { 'manifest.json': 'not a terminal manifest' } })
  bench(nproof, 'set-ancient', { payloadKiB: 16 })
  const nres = planBenchRetention({ proofRoot: nproof,
    runStartMs: Date.now() - 120_000, nowMs: Date.now(), graceMs: 600_000,
    repoRoot: path.join(root, 'definitely-not-a-repo') })
  assert.equal(nres.reclaimed.length, 0, 'a failed git query reclaims NOTHING')
  for (const name of ['run-incomplete', 'set-ancient'])
    assert.equal((nres.kept.find(k => k.dir === path.join(nproof, name)) || {}).reason,
      'git-unproven', `${name} kept on unproven git state`)
  console.log('PASS git failure: failed query = unproven = kept (the probe\'s fail-open leg, closed)')
}

// --- PREMISE: incomplete tree scan is never "quiet" --------------------------
// An unreadable subtree could hide fresh writes; the walk must report
// incomplete and the sweep must keep, not reclaim on under-reported mtimes.
{
  const sproof = path.join(root, 'scanblocked')
  fs.mkdirSync(sproof)
  const t = bench(sproof, 'set-unreadable-subtree', { payloadKiB: 8, extra: { 'logs/keep.log': 'x' } })
  fs.chmodSync(path.join(t, 'logs'), 0o000)
  const sres = planBenchRetention({ proofRoot: sproof, ...opts })
  assert.equal((sres.kept.find(k => k.dir === t) || {}).reason, 'scan-incomplete',
    'a partial walk under-reports — the tree is kept, not reclaimed')
  fs.chmodSync(path.join(t, 'logs'), 0o755)
  console.log('PASS incomplete scan: unreadable subtree keeps the tree (scan-incomplete)')
}

// --- PREMISE: unreadable provenance legs --------------------------------------
// (a) present-but-unreadable manifest.json on the tree itself = unknown
//     terminality → kept outright. (b) a COMMITTED manifest whose bytes
//     cannot be read makes the whole reference set unproven: an incomplete
//     scan cannot prove the ABSENCE of a reference, so otherwise-dead trees
//     are kept — and once the manifest is readable, the reference itself
//     must show as the keeping reason (the unproven leg is the only wall).
{
  const uproof = path.join(root, 'unreadable')
  fs.mkdirSync(uproof)
  bench(uproof, 'run-man-unreadable', { extra: { 'bench/p.bin': 'x' } })
  fs.writeFileSync(path.join(uproof, 'run-man-unreadable', 'manifest.json'),
    '{"schema":"proof-harness/1","captures":[],"repro":{}}\n')
  fs.chmodSync(path.join(uproof, 'run-man-unreadable', 'manifest.json'), 0o000)
  let ures = planBenchRetention({ proofRoot: uproof, ...opts })
  assert.equal((ures.kept.find(k => k.dir === path.join(uproof, 'run-man-unreadable')) || {}).reason,
    'manifest-unreadable', 'present-but-unreadable manifest: unknown provenance, kept')
  fs.chmodSync(path.join(uproof, 'run-man-unreadable', 'manifest.json'), 0o444)

  // (b) one unreadable member of the reference set (a sibling tree's
  //     manifest under proofRoot): an incomplete scan proves nothing about
  //     the ABSENCE of a reference, so otherwise-dead trees are kept — and
  //     once readable, the mention itself must be the keeping reason.
  const r2 = path.join(root, 'refrepo')
  fs.mkdirSync(r2, { recursive: true })
  execFileSync('git', ['-C', r2, 'init', '-q', '-b', 'main'])
  const r2proof = path.join(r2, 'proof')
  fs.mkdirSync(r2proof)
  bench(r2proof, 'set-witness', { extra: { 'manifest.json': '{"note":"mentions run-refprobe"}\n' } })
  bench(r2proof, 'run-refprobe')
  const wit = path.join(r2proof, 'set-witness', 'manifest.json')
  fs.chmodSync(wit, 0o000)
  ures = planBenchRetention({ proofRoot: r2proof,
    runStartMs: Date.now() - 120_000, nowMs: Date.now(), graceMs: 600_000, repoRoot: r2 })
  assert.equal((ures.kept.find(k => k.dir === path.join(r2proof, 'run-refprobe')) || {}).reason,
    'manifest-set-unproven', 'unreadable manifest member: reference set unproven, kept')
  assert.equal((ures.kept.find(k => k.dir === path.join(r2proof, 'set-witness')) || {}).reason,
    'manifest-unreadable', 'the unreadable tree itself is kept on unknown provenance')
  fs.chmodSync(wit, 0o644)
  ures = planBenchRetention({ proofRoot: r2proof,
    runStartMs: Date.now() - 120_000, nowMs: Date.now(), graceMs: 600_000, repoRoot: r2 })
  assert.equal((ures.kept.find(k => k.dir === path.join(r2proof, 'run-refprobe')) || {}).reason,
    'referenced-by-committed-manifest', 'once readable, the reference itself keeps the tree')
  console.log('PASS unreadable manifest / unproven reference set: kept, and the reference keeps it once readable')
}

// --- active supervisors (4fy review): mtime silence is NOT terminal evidence.
// A gate-case bench parked past the grace is disk-quiet BY DESIGN — the tree's
// own supervisors.json (one writeFileSync per spawn) plus the ABSENT
// logs/<label>.exit record prove its supervisor lives. Trees whose supervisors
// are dead (exit record present, or pid ESRCH) still reclaim; a corrupt
// supervisors.json fails CLOSED (kept). Since the wave-B qualification the
// liveness check covers SEALED trees too: a recorded pid alive without its
// exit record contradicts terminality whatever the manifest says — and a
// detached-then-dead supervisor reaps to ESRCH, so dead sealed trees stay
// reclaimable (the sealed ESRCH leg is that negative control).
const liveSup = JSON.stringify([{ label: 'gateway', pid: process.pid }])
const esrchPid = 2_147_483_647 // out-of-range pid: kill(2) reports ESRCH everywhere
bench(proof, 'run-parked-gate', { extra: { 'supervisors.json': liveSup, 'logs/gateway.log': 'alive\n' } })
bench(proof, 'run-sup-exit-record', { extra: { 'supervisors.json': liveSup,
  'logs/gateway.log': 'was\n', 'logs/gateway.exit': `${Date.now()} code=signal\n` } })
bench(proof, 'run-sup-esrch', { extra: {
  'supervisors.json': JSON.stringify([{ label: 'gateway', pid: esrchPid }]) } })
bench(proof, 'run-sup-broken', { extra: { 'supervisors.json': '{oops' } })
bench(proof, 'run-sealed-livepid', { sealed: true, extra: { 'supervisors.json': liveSup } })
// PREMISE: alive DETACHED supervisor, manifest present. A real detached child
// (the Supervisor class spawns detached), its pid recorded, no exit record,
// the tree sealed and old — kill(pid,0) answers alive: kept, not reclaimed.
// The exit-record and ESRCH legs below keep the reclaim side honest.
const det = spawn('sleep', ['20'], { detached: true, stdio: 'ignore' })
det.unref()
bench(proof, 'run-sealed-detached-live', { sealed: true,
  extra: { 'supervisors.json': JSON.stringify([{ label: 'gateway', pid: det.pid }]) } })
bench(proof, 'run-sealed-detached-dead', { sealed: true,
  extra: { 'supervisors.json': JSON.stringify([{ label: 'gateway', pid: det.pid }]) } })
res = planBenchRetention({ proofRoot: proof, ...opts })
assert.equal(keptReason(res, 'run-parked-gate'), 'active-supervisor',
  'quiet past grace with a live supervisor pid = parked, not dead')
assert.equal(keptReason(res, 'run-sup-broken'), 'active-supervisor',
  'unparseable supervisors.json fails CLOSED: unproven-dead is never deleted')
assert.equal(keptReason(res, 'run-sealed-livepid'), 'active-supervisor',
  'sealed does NOT skip the liveness check: a live pid without exit record keeps the tree')
assert.equal(keptReason(res, 'run-sealed-detached-live'), 'active-supervisor',
  'alive detached supervisor with a valid manifest present: kept')
assert.ok(fs.existsSync(path.join(proof, 'run-parked-gate'))
  && fs.existsSync(path.join(proof, 'run-sup-broken'))
  && fs.existsSync(path.join(proof, 'run-sealed-livepid'))
  && fs.existsSync(path.join(proof, 'run-sealed-detached-live')))
for (const dead of ['run-sup-exit-record', 'run-sup-esrch'])
  assert.ok(res.reclaimed.some(r => r.dir === path.join(proof, dead) && r.reason === 'scratch'),
    `${dead}: exit-record / ESRCH each prove terminality`)
try { process.kill(det.pid, 'SIGKILL') } catch { /* already gone */ }
// await the reap (libuv waitpid completes before the exit event) so the
// recorded pid must now answer ESRCH — then the sealed tree reclaims.
await new Promise(r => { det.once('exit', r); setTimeout(r, 5000) })
res = planBenchRetention({ proofRoot: proof, ...opts })
assert.ok(res.reclaimed.some(r => r.dir === path.join(proof, 'run-sealed-detached-dead')
  && r.reason === 'scratch'),
  'sealed + dead detached supervisor (ESRCH) still reclaims: the liveness gate is evidence, not a blanket keep')
console.log('PASS active-supervisor: parked, corrupt, live-detached-sealed kept; exit-record, ESRCH (sealed included) reclaimed')

// --- PREMISE: the boot window between marker and first supervisor record ------
// The owned marker is written before any spawn is recorded; a live tree in
// that window has marker + log dir but NO supervisors.json yet. Missing
// supervisors.json alone must not reclaim it while the grace window still
// covers boot (spawn-time writes keep mtimes fresh); once quiet past grace
// the crash-before-first-spawn reading is PROVEN and the tree reclaims.
{
  bench(proof, 'run-boot-window', { ageMs: 180_000, extra: { 'logs/boot.log': '' } })
  bench(proof, 'set-boot-crash-old', { extra: { 'logs/boot.log': 'x' } })
  res = planBenchRetention({ proofRoot: proof, ...opts })
  assert.equal(keptReason(res, 'run-boot-window'), 'live-grace',
    'between marker and first supervisor record, inside grace = booting, not dead')
  assert.ok(reclaimedRec(res, 'set-boot-crash-old'), 'marker-only past grace = proven crash-before-spawn')
  console.log('PASS boot window: marker-only inside grace kept (live-grace); marker-only past grace reclaims')
}

// --- PREMISE: the real entrypoint, synthetic temp trees only ------------------
// Run the actual CLI (capture.mjs with a stub app repo and a stub hermes that
// answers --version then refuses, so the run dies in provisioning AFTER the
// sweep) against a temp proof root holding (a) an old dead attempt and (b)
// the probe's one-second-old corrupt-manifest tree. The sweep must reclaim
// (a) and keep (b), with the keeping reason on the kept line: proof the
// destructive path of the SHIPPED entrypoint is fail-closed, without ever
// touching a real bench tree (no real deletion — every byte here is
// synthetic).
{
  const cliRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ui2-retention-4fy-cli-'))
  try {
    const cproof = path.join(cliRoot, 'captured')
    fs.mkdirSync(cproof)
    const app = path.join(cliRoot, 'app')
    for (const bin of ['electron', 'vite', 'tsc']) {
      const f = path.join(app, 'apps', 'desktop', 'node_modules', '.bin', bin)
      fs.mkdirSync(path.dirname(f), { recursive: true })
      fs.writeFileSync(f, '#!/bin/sh\nexit 9\n')
      fs.chmodSync(f, 0o755)
    }
    const hermes = path.join(cliRoot, 'hermes-stub')
    fs.writeFileSync(hermes, '#!/bin/sh\ncase "$1" in --version) echo 0.0.0-retention-lane-test; exit 0;; *) exit 77;; esac\n')
    fs.chmodSync(hermes, 0o755)
    bench(cproof, 'set-crashed-attempt-cli', { payloadKiB: 4 })
    bench(cproof, 'run-incomplete-cli', { ageMs: 1000, extra: { 'manifest.json': 'not a terminal manifest' } })
    const capture = fileURLToPath(new URL('./proof-harness/capture.mjs', import.meta.url))
    let stderr = '', exit = 0
    try {
      execFileSync(process.execPath, [capture, '--case', 'baseline', '--no-prebuild',
        '--out', path.join(cproof, 'live-cli-run'), '--app-repo', app,
        '--hermes-bin', hermes, '--cdp-port', '43941', '--renderer-port', '43942'],
        { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] })
    } catch (e) {
      stderr = String(e.stderr || '')
      exit = typeof e.status === 'number' ? e.status : -1
    }
    assert.ok(exit !== 0, `stub hermes must stop the run in provisioning (exit ${exit})`)
    assert.match(stderr, /\[retention\] reclaimed .*set-crashed-attempt-cli.* \(dead-attempt\)/,
      `real entrypoint reclaimed the proven-dead tree\n${stderr}`)
    assert.match(stderr, /\[retention\] kept \d+ \([^)]*live-grace[^)]*\)/,
      `real entrypoint kept the corrupt-manifest fresh tree with a reason\n${stderr}`)
    assert.ok(!fs.existsSync(path.join(cproof, 'set-crashed-attempt-cli')))
    assert.ok(fs.existsSync(path.join(cproof, 'run-incomplete-cli')),
      'one-second-old corrupt-manifest tree SURVIVED the real entrypoint sweep')
    console.log(`PASS real entrypoint (synthetic trees): dead sibling reclaimed, probe-shape kept, exit=${exit}`)
  } finally {
    fs.rmSync(cliRoot, { recursive: true, force: true })
  }
}

// absent proof root: empty plan, no crash
assert.deepEqual(planBenchRetention({ proofRoot: path.join(root, 'nope'),
  runStartMs: Date.now(), repoRoot: root }), { reclaimed: [], kept: [] })
console.log('PASS absent proof root: empty plan, no crash')

console.log('ALL PASS: owned-bench retention (rotation/scratch/dead-attempt reclaim; unknown, live, young, owner-held, pending, committed, referenced, git-unproven, scan-incomplete, corrupt-manifest-young, unreadable, set-unproven never)')
fs.rmSync(root, { recursive: true, force: true })
