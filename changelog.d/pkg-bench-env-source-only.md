fix(packaging): `tests/test_proof_bench_env.mjs` is declared source-only — the #729
bench-env spec shipped in the release ZIP while its only import, the source-only
proof driver `tests/proof-harness/capture.mjs`, never travels, so the packaged
`node --experimental-strip-types tests/test_proof_bench_env.mjs` died at
`ERR_MODULE_NOT_FOUND` at an unpacked root (reproduced on a fresh 1.4.12 pack);
the #756 invariant grew a derived shipped-`.mjs` import sweep, so a mapping
removed from BOTH ledgers re-ships the hole red instead of passing vacuously.
