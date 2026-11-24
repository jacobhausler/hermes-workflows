#!/usr/bin/env node
/**
 * The bead-facing path for the ui2 proof driver (bd_2026-11-13-cj2 onward):
 * the driver LANDED at tests/proof-harness/capture.mjs (slice A, bd 33h/qri
 * law), and work orders name `node scripts/ui2-proof/capture.mjs` — this
 * shim forwards every argument verbatim to the landed driver and propagates
 * its exit code, so both paths run the SAME code (no second implementation,
 * no divergence surface). Relative --out defaults resolve from the repo
 * exactly as when invoked at the driver path (this file only spawns).
 */
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const target = path.resolve(here, '..', '..', 'tests', 'proof-harness', 'capture.mjs');
const r = spawnSync(process.execPath, [target, ...process.argv.slice(2)], { stdio: 'inherit' });
if (r.error) { console.error(String(r.error.message)); process.exit(1); }
process.exit(r.status ?? 1);
