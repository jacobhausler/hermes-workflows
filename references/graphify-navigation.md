# Navigating the repo with the knowledge graph (optional)

Folded out of `AGENTS.md` §4b′ so the front door stays inside core's 32,000-char
subdirectory-hint cap (`tests/test_docs_hint_cap_73c.py`) — the middle of an
over-cap AGENTS.md is dropped silently, so anything folded here is reachable
only through this file.

[`graphify`](https://github.com/Graphify-Labs/graphify) builds a code-navigation
graph locally (`uv tool install graphifyy` → `graphify update .`; query/path/
affected/god-nodes; `.graphifyignore` ships). Exploration aid, not a gate: never
committed, CI never builds it, a `graphify-out/` in your PR diff is deleted by
review. Source and tests are the spec. (`scripts/graph_diagram.py` +
`diagram_readme.py` are unrelated — they draw the `examples/README.md` diagrams.)
