#!/usr/bin/env node
/*
 * scripts/ui2-proof/capture.mjs — the later-bead interface to the real-app
 * proof driver (the path PLAN-2.0.md names for `--case CASE --out DIR`).
 *
 * The driver BODY is tests/proof-harness/capture.mjs (the W1-harness era
 * real-client driver, proven by the merged slice-A/QRI/graph/coverage
 * captures): it boots the owned dev-app bench, stages the candidate desktop
 * half, seeds through the door, captures, and tears down. This file is the
 * documented entry point the case commands invoke, forwarding argv verbatim
 * and the driver's exit codes:
 *
 *   0 ok | 2 usage/unknown case | 3 known-but-unwired new test | other: see
 *   the driver header for the exit map.
 *
 * Cases live in tests/proof-harness/cases.json; setup notes in
 * tests/proof-harness/SETUP.md. Adding a case ADDS A NEW TEST.
 */
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const driver = join(here, '..', '..', 'tests', 'proof-harness', 'capture.mjs')
const r = spawnSync(process.execPath, [driver, ...process.argv.slice(2)], { stdio: 'inherit' })
if (r.error) { console.error('UI2_PROOF_ENTRY_FAIL: ' + r.error.message); process.exit(1) }
process.exit(r.status === null ? 1 : r.status)
