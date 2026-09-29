# Portable workflow files (publish = put the file on git)

There is no index, service, or marketplace: a workflow is published when someone commits the file to a repo and shares the path. The convention, in ten lines:

1. One graph per file, named `<name>.workflow.json` — plain UTF-8 JSON, ≤ 1 MiB, the same `{name, nodes, …}` object `run` accepts inline.
2. State the dialect at the top: `"grammar": "wf/1"`. Absent means `wf/1` (every pre-#32 file is a `wf/1` file); a value this reader does not know is refused before any write or spawn, with the supported list in the error — a newer dialect is never misrun.
3. Add a `provenance` block (encouraged, optional): `owner` (who maintains it), `source` (where the canonical copy lives, ≤ 200 chars), `source_digest` (sha256 of the canonical `nodes` JSON — `wfcommon.source_digest(graph)`). Attribution only; nothing reads it to allow or deny.
4. Drop the file anywhere on disk and run it: `workflow{action:"run", graph_path:"/abs/path/<name>.workflow.json"}`; `save` with `graph_path` shelves it in the library for `run from:<name>`.
5. Keep it self-contained: no absolute paths of your machine, no secrets, no profile names — `{run.KEY}` inputs and `profile` are the receiver's to bind.
6. Budgets (`max_turns`, `timeout`, `shape`) travel with the file but are policy, not work: a receiver may raise them without changing any node's fingerprint.
7. Pin what you publish: record the file's sha256 next to the link so a reader can check `sha256sum <file>` before running it.
8. A `wf/1` file carries NO code. Nodes are goals, schemas, edges and gates; every action is performed by the receiver's own Hermes with the receiver's own tools and consent. Contrast Anthropic-style `.js` workflow files, which DO carry executable code — that is the dialect line, and the reason `grammar` exists.
9. Validate before sharing: `python3 -c 'import json,wfcommon; print(wfcommon.validate_graph_errors(json.load(open("<file>"))))'` from the plugin root must print `[]`.
10. `grammar` and `provenance` are top-level annotations: they never enter `def_hash`, `efp`, `graph_fingerprint` or `source_digest`, so adding them to an existing file changes no committed node.

## Walk-in example

`examples/portable-review.workflow.json` — recon → two-way fan-out review → summary, `grammar: "wf/1"` with a provenance block. Pinned:

- file sha256 (`sha256sum examples/portable-review.workflow.json`): `5111407e02f483b249bef292eec79f4aa8b760caf60a9b6f725c4a4c471c7b62`
- `source_digest` (canonical `nodes` JSON): `a4961c82014e102debfe254a3f022e958edc8c8a69da8df81be9b16341bf26b1`

`tests/test_portable_32.py` asserts the example validates and that both digests still match this page; editing the example means re-pinning here in the same commit.
