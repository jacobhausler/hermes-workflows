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
# render + shoot with archify (any machine with node + a chrome-headless-shell):
#   node bin/archify.mjs finalize workflow examples/diagrams/<name>.candidate.json examples/diagrams/<name>.html --quality standard
#   chrome-headless-shell --headless --no-sandbox --virtual-time-budget=12000 \
#     --window-size=1500,1500 --screenshot=examples/diagrams/<name>.png examples/diagrams/<name>.html
python3 scripts/diagram_readme.py             # rebuild this table (derived)
python3 scripts/graph_diagram.py --check --all # CI freshness gate: exit 1 on drift
```

| example | diagram | candidate sha256 | png sha256 | profile | gates |
|---|---|---|---|---|---|
| examples/basics/branch-on-verdict.json | [branch-on-verdict.png](branch-on-verdict.png) | `3fad254249e6f32b` | `4451964ffa299c40` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/basics/smoke.json | [smoke.png](smoke.png) | `3d57b91c6d4ce841` | `ca87a97068fbda5c` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/build/census-fanout.workflow.json | [census-fanout.workflow.png](census-fanout.workflow.png) | `484b0733752dc923` | `7603620bd8ea95c5` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/build/quorum-probe.workflow.json | [quorum-probe.workflow.png](quorum-probe.workflow.png) | `6115c58a607959c5` | `0d8c41d7495e95e2` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/ops/incident-response.json | [incident-response.png](incident-response.png) | `e460883d28d85a2b` | `49ccf1ffd193b5c2` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/release/issue-to-pr.workflow.json | [issue-to-pr.workflow.png](issue-to-pr.workflow.png) | `9c9b14283d83ce3a` | `1392e2549905076f` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/release/submit-pr.workflow.json | [submit-pr.workflow.png](submit-pr.workflow.png) | `f093c5ab135b7848` | `7cac4c5f047c81b6` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |
| examples/review/portable-review.workflow.json | [portable-review.workflow.png](portable-review.workflow.png) | `4d801ce8a299c20e` | `eb9503ab13f3a095` | standard | derived + rendered via archify; browser-check not-run (authoring-env block) — visual QA lap per diagram before edits land |

Cards (the two panels inside each diagram) are the ONLY hand-authored
diagram input; they live in `<name>.cards.json` beside the graph. Every
number in a card must be recomputable from the graph bytes it describes.

Scope: every graph under `examples/` carries a conforming diagram.
Test fixtures (`tests/fixtures/`) are engine inputs consumed by test
code, not docs — no diagram (rung zero). Census command for the scope:
`git ls-tree -r --name-only HEAD | grep '\.json$' | grep -v '^graphify-out/'
 | grep -v '^examples/diagrams/' | grep -v '\.cards\.json$'` —
every file whose parsed JSON has a non-empty `nodes` array must have a
table row or queue row in this table (receipt at build: examples/ 17
= 8 table + 9 queue).

## Diagram queue (cards pending — generator skips, CI stays green)

- [ ] `examples/basics/approve-publish.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/basics/exchange-run.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/build/bulk-transform.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/build/triage-route.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/release/gated-publish.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/release/machine-watch.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/release/release-lifecycle.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/review/blind-council.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row
- [ ] `examples/review/escalation-ladder.workflow.json` — needs `<name>.cards.json`, then `--all` derives the row

