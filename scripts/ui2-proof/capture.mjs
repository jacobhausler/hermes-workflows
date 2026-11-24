#!/usr/bin/env node
// Canonical entry point for the real-app proof driver (bd_2026-11-13-3gh).
//
//   node scripts/ui2-proof/capture.mjs --case CASE [--only TOKENS] [--out DIR]
//
// The driver ENGINE lives at tests/proof-harness/capture.mjs (it resolves its
// repo root from its own location and its CLI guard fires on its own argv
// path, so this seam spawns rather than imports: same argv, same stdio, same
// identity/manifest/repro contracts, same exit-code law). This file is the
// work-order-facing path — later beads and CI call scripts/ui2-proof/
// capture.mjs; read tests/proof-harness/SETUP.md before provisioning a real
// app (bench profile law, app-copy law, ports, paint budget).
import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const driver = path.resolve(path.dirname(fileURLToPath(import.meta.url)),
  '..', '..', 'tests', 'proof-harness', 'capture.mjs')
const r = spawnSync(process.execPath, [driver, ...process.argv.slice(2)], { stdio: 'inherit' })
if (r.error) {
  console.error(`UI2_PROOF_FAIL(4): seam could not exec ${driver}: ${r.error.message}`)
  process.exit(4)
}
process.exit(r.status ?? 1)
