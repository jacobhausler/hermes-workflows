#!/usr/bin/env node
// scripts/ui2-proof — the stable proof entrypoint (bd_2026-11-13-jtf).
//
// The driver itself lives at tests/proof-harness/capture.mjs (slice A,
// bd_2026-11-13-iqf): ONE implementation, ONE failure law. This forwarder
// exists so the documented contract
//
//   node scripts/ui2-proof/capture.mjs --case CASE --out DIR
//
// works no matter where the driver file itself lives; every argument passes
// through untouched, including --only, --plan and the bench knobs.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const target = path.resolve(here, '..', '..', 'tests', 'proof-harness', 'capture.mjs');
const r = spawnSync(process.execPath, [target, ...process.argv.slice(2)], { stdio: 'inherit' });
if (r.error) {
  console.error(`ui2-proof forwarder: ${r.error.message}`);
  process.exit(2);
}
process.exit(r.status ?? 2);
