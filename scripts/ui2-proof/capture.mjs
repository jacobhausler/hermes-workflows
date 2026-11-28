// scripts/ui2-proof/capture.mjs — dispatch shim for the bead-named proof
// command (bd_2026-11-13-33h verification). The real-app proof driver lives
// at tests/proof-harness/capture.mjs (source-only, SETUP.md); this shim lets
// the documented invocation `node scripts/ui2-proof/capture.mjs --case graph
// --out DIR` run verbatim at the merged head. All argv passes through; the
// driver's own exit codes (2 usage, 3 unwired surface, 4..8 failure
// semantics) are returned untouched. Nothing here captures or fabricates:
// zero proof logic lives in this file.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const driver = path.resolve(here, "..", "..", "tests", "proof-harness", "capture.mjs");
const res = spawnSync(process.execPath, [driver, ...process.argv.slice(2)], { stdio: "inherit" });
if (res.error) {
  console.error(`ui2-proof: cannot launch driver ${driver}: ${res.error.message}`);
  process.exit(4);
}
process.exit(res.status === null ? 1 : res.status);
