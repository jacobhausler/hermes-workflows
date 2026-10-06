# examples/diagrams/ — derived diagram table

Every template below ships with a diagram that is **derived from its
graph bytes**, never drawn by hand (DIAGRAM LAW v1). The layout rule
(lane/col/stack, compared bytes) is the **LAYOUT RULE paragraph in
`scripts/graph_diagram.py`'s docstring** — one-source law: that
paragraph is the spec, this README cites it, a contradiction between
diagram and graph is a bug in that file (named defendant).
Regenerate everything after editing any example:

```sh
python3 scripts/graph_diagram.py --all        # candidates (stdlib, deterministic)
# render + shoot with the VENDORED archify (scripts/vendor/archify/, version in
# ARCHIFY_VERSION — the only oven the repo owns; any machine with node >= 18:
#   node scripts/vendor/archify/renderers/workflow/render-workflow.mjs \
#     examples/diagrams/<name>.candidate.json examples/diagrams/<name>.html
#   # then screenshot examples/diagrams/<name>.html with any headless chromium
#   # (chrome-headless-shell --headless --no-sandbox --screenshot=... works;
#   #  strip the viewer chrome before saving the records png)
#   # and record a QA lap per diagram at examples/diagrams/qa/<name>.qa.json:
#   #  {browser, expected_nodes (= candidate nodes length), clipped, legible,
#   #   chrome_free} — this table DERIVES the gates column from those receipts,
python3 scripts/diagram_readme.py             # rebuild this table (derived)
python3 scripts/graph_diagram.py --check --all # CI freshness gate: exit 1 on drift
```

| example | diagram | candidate sha256 | png sha256 | profile | gates |
|---|---|---|---|---|---|
| examples/basics/branch-on-verdict.json | [branch-on-verdict.png](branch-on-verdict.png) | `77280e59eaacd37d` | `0b7e44fa842cdc6e` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/basics/smoke.json | [smoke.png](smoke.png) | `55eeebdc657b4750` | `ba070f54366d7e27` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/build/census-fanout.workflow.json | [census-fanout.workflow.png](census-fanout.workflow.png) | `484b0733752dc923` | `877f81acd8de3de7` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/build/quorum-probe.workflow.json | [quorum-probe.workflow.png](quorum-probe.workflow.png) | `dae0138a65df9fa9` | `20748709a9d73684` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/ops/incident-response.json | [incident-response.png](incident-response.png) | `e460883d28d85a2b` | `67a2d81174071f72` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/release/issue-to-pr.workflow.json | [issue-to-pr.workflow.png](issue-to-pr.workflow.png) | `9c9b14283d83ce3a` | `91f3d09b532379cd` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/release/submit-pr.workflow.json | [submit-pr.workflow.png](submit-pr.workflow.png) | `f093c5ab135b7848` | `ed27a91e1e21df34` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |
| examples/review/portable-review.workflow.json | [portable-review.workflow.png](portable-review.workflow.png) | `eca24a58063b50cd` | `9c5a940488c4676d` | standard | derived + rendered via vendored archify; browser-check done (cloud-chromium via CDP Page.captureScreenshot (captureBeyondViewport); authoring box has no local chromium — recorded honestly as cloud, not local, no-clip, legible, chrome-free); receipts in qa/ (generator + renderer version-stamped) |

Cards (the two panels inside each diagram) are the ONLY hand-authored
diagram input; they live in `<name>.cards.json` beside the graph. Every
number in a card must be recomputable from the graph bytes it describes.

Scope: every graph under `examples/` carries a conforming diagram.
Test fixtures (`tests/fixtures/`) are engine inputs consumed by test
code, not docs — no diagram (rung zero). Census command for the scope:
`git ls-tree -r --name-only HEAD | grep '\.json$' | grep -v '^graphify-out/'
 | grep -v '^examples/diagrams/' | grep -v '\.cards\.json$'` —
every file whose parsed JSON has a non-empty `nodes` array must have a
table row or queue row in this table (receipt at build: examples/ 25
= 8 table + 17 queue).

## Diagram queue (cards pending — generator skips, CI stays green)

- [ ] `examples/basics/approve-publish.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/basics/exchange-run.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/build/bulk-transform.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/build/triage-route.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/branch-on-verdict.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/census-fanout.workflow.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/incident-response.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/issue-to-pr.workflow.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/portable-review.workflow.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/quorum-probe.workflow.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/smoke.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/diagrams/qa/submit-pr.workflow.qa.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/release/gated-publish.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/release/machine-watch.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/release/release-lifecycle.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/review/blind-council.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/review/escalation-ladder.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row

