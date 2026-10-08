# Contributing to hermes-workflows

This repo is maintained continuously, and most contributions arrive from coding
agents. The rules below are the exact checklist the maintainer runs on your PR —
run it first and review stays cheap.

## What lands fast

- Bug fixes with a failing-then-passing test.
- Doc fixes where the doc disagreed with the code.
- Small features that stay inside the boundaries below (SDK-only desktop,
  stdlib-only backend, stock Hermes core).

## What needs an issue first

- Anything touching `plugin.yaml`, `.github/`, `scripts/make_public.py`, or the
  persisted data shape. Open an issue, get a `needs-decision` ruling, then code.
- New settings, new dependencies, new tools/hooks. Default answer is no; a use case
  the current form cannot serve is what changes it.

## Before you push (mechanical gates)

One canonical entry — `python3 scripts/suite.py . ci-out` is exactly what CI runs.
It executes every `tests/test_*.py` serially and every `tests/test_*.mjs` under
`node --experimental-strip-types`; do not hand-run the `.mjs` files with bare
`node`. `node --check desktop/plugin.js` is the quick desktop syntax gate.

```sh
node --check desktop/plugin.js                    # desktop half parses
python3 scripts/suite.py . ci-out                 # full serial suite → ci-out/exits.json all 0
python3 scripts/suite.py . ci-fix --baseline <measured-ledger>
                                                  # optional diagnosis: admission.json splits reds into
                                                  # introduced vs pre-existing (exact name+exit identities),
                                                  # compared against a ledger MEASURED on the PR's
                                                  # merge-base; only a fully-green SHA is green; base
                                                  # reds block, never waived
hermes plugins validate .                         # → Validation passed.
python3 scripts/make_public.py /tmp/public-tree   # → 0 scrub hits
python3 scripts/graph_path_ban.py                 # PR diff touches no graphify-out/ — single writer (#153); a local `graphify update` for your own navigation is fine, committing generated graph data never is
python3 scripts/pr_tag_audit.py                   # release step: every `(open PR #NN)` doc tag still
                                                  # points at an OPEN PR; a merged PR's tag must be
                                                  # rewritten to (shipped in vX) in that release commit
```

Admission is strict: a suite run that **discovers zero test cases counts as a
failure, never green** `(shipped in v1.2.1)`. Every line must pass on your branch. If a
test fails, run it on a clean `main` too — a failure that also fails on `main` is a
pre-existing red (say so in the PR; it blocks merge and needs its own fix item), a
failure only on your branch is yours.

## Review checklist (the maintainer runs exactly this)

R1 **Scope** — every changed line traces to the PR's stated purpose; adjacent
    refactors are a separate PR.
R2 **Stock core** — no import from a patched Hermes; core imports are soft
    (`try/except`), core DB columns are read-only, an absent field reads `unknown`
    and is never invented.
R3 **SDK-only desktop** — `desktop/plugin.js` imports only `@hermes/plugin-sdk`,
    `react`, `react/jsx-runtime`; no `window.hermesDesktop`, `localStorage`,
    `document`, `eval`, or dynamic `import()`.
R4 **Stdlib backend** — no new Python dependency; no self-updater.
R5 **Manifest parity** — `plugin.yaml`'s `provides_*` entries match what
    `register()` actually registers; the version is bumped only by the release lane (PUBLIC release only — never a gate on local dogfood installs of our own packages, see release-train scope).
R6 **Tests** — every behaviour change ships its check: one test that fails if the
    behaviour breaks. No snapshot/change-detector tests; no test reads source text.
R7 **Docs drift** — if a user-visible string or flag changed, README/AGENTS.md/
    SKILL.md are grepped for the old form and fixed in the same PR.
R8 **Sibling completeness** — the fixed pattern is checked across the repo and
    every sibling instance is fixed too. Proof: `graphify affected "<changed
    symbol>" --depth 2` (after a local `graphify update .`) lists every caller;
    each one updated or shown unaffected in the PR body.
R9 **Private strings** — `scripts/make_public.py` exits 0: no hostnames, LAN
    addresses, tokens, or personal paths in shipped files.
R10 **Migration safety** — persisted shapes (stored settings, run dirs, JSON files)
    keep loading old data; any migration lives in the normalizer with a test that
    feeds it the old form.

## For agents

You are contributing on behalf of a user. Do this, in order:

1. **Search first.** `gh pr list --search "<keywords>"` and `gh issue list --search`.
   An open PR on the same issue → stop and tell your user; don't race it.
2. **Read `AGENTS.md`** in the repo root — the repo map, the build rule, the
   invariants. For caller lookup run `graphify update .` in your own checkout
   (~3 s, no API key) and navigate with `graphify query "<question>"` /
   `graphify affected "<symbol>"`; commit nothing from `graphify-out/` — the
   committed graph is single-writer (#153, `scripts/graph_path_ban.py`).
3. **Reproduce before fixing.** Point at the `file:line` where the bug manifests and
   show your fix changes that line's behaviour. A plausible rationale is not a repro.
4. **Smallest diff that passes R1–R10.** Check siblings (R8). No drive-by cleanups.
5. **Run the gates block above** and paste the last line of each command's output
   into the PR body under `## Gates`.
6. **PR body** = what/why in two sentences, `Fixes #n` if any, `## Gates`, and one
   line: `Author: agent (<model>) on behalf of @<user>` or `Author: human`.
7. **Do not push to `main`, do not tag, do not touch `.github/`.** Those are the
   release lane's.

A PR that follows 1–7 merges on the first review.

## What happens after you open the PR

A review comment appears with one `file:line` per finding and a verdict — `merge`,
`changes`, or `decision`. `merge` + green CI → squash-merged, authorship kept.
`changes` → the comment lists the exact commands to re-check; push and the same
comment updates in place. `decision` → the maintainer needs the owner's call.
First PR from a fork: CI waits for a maintainer to approve the run (GitHub default).

## Issues

Include: Hermes version (`hermes --version`), OS, the exact command or click, what
you expected, what happened, and the `hermes plugins validate .` output if relevant.
A bug we cannot reproduce gets `needs-repro` and a comment saying exactly what is
missing; replying reopens the issue at any time.

Labels you will see: `P0`–`P3` (severity), `needs-repro`, `needs-info`,
`needs-decision`, `question`, `duplicate`. One label means it was triaged.

## License

By contributing you agree your work is released under the repo's [LICENSE](LICENSE).

Cross-estate joint eng protocol v1 is the SSOT mirrored publicly at [issue #174](https://github.com/jacobhausler/hermes-workflows/issues/174), sha256 `a7f424c5be3f5d6d1cbeb590f6cd02b6699a60090a3a45646853c67b2360345b` (of the issue body including its trailing newline); private working copy: `jacobhausler/joint-eng-protocol@0bf569a`, file `docs/specs/hermes-workflows-joint-eng-protocol-v1.md`.
