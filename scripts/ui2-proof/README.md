# scripts/ui2-proof — bead command path for the real-app proof driver

`bd_2026-11-13-1bm` verification names `scripts/ui2-proof/capture.mjs`; the
driver itself lives in `tests/proof-harness/` (source-only, never packaged).
`capture.mjs` here is a symlink to it — the driver's CLI guard resolves
`process.argv[1]` through `realpathSync`, so the symlink entry point runs the
same `main()` with the same `cases.json` next to the real file.
