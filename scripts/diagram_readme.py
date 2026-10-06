#!/usr/bin/env python3
"""Build examples/diagrams/README.md — the derived diagram table.

Owns that file wholesale (it lives beside the artifacts it describes; the
hand-authored map at examples/README.md is NOT touched — it carries jsonc
invocations other tests gate).

Stdlib-only. The table is derived: every row is computed from files on disk at
generation time — never hand-edited. Run after graph_diagram.py + render step.
"""
import hashlib, json, os, re, sys


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ex = os.path.join(here, "examples")
    dia = os.path.join(ex, "diagrams")
    graphs = sorted(
        os.path.join(dp, f) for dp, _, fs in os.walk(ex) for f in fs
        if f.endswith(".json") and not f.endswith(".cards.json")
        and os.path.basename(dp) != os.path.basename(dia))
    rows, pending_rows = [], []
    for g in graphs:
        stem = os.path.basename(g)[:-5]
        cand = os.path.join(dia, stem + ".candidate.json")
        stem_png = os.path.join(dia, stem + ".png")
        if not os.path.exists(cand):
            pending_rows.append(f"examples/{os.path.relpath(g, ex)}")
            continue
        c = json.load(open(cand))
        q = c["meta"].get("quality_profile", "standard")
        gates = ("derived + rendered via archify; browser-check not-run "
                 "(authoring-env block) — visual QA lap per diagram before edits land")
        rel = os.path.relpath(g, here)
        rows.append((f"examples/{os.path.relpath(g, ex)}",
                     f"[{stem}.png]({stem}.png)",
                     f"`{sha(cand)}`", f"`{sha(stem_png) if os.path.exists(stem_png) else '—'}`",
                     q, gates, rel))
    out = ["# examples/diagrams/ — derived diagram table",
           "",
           "Every template below ships with a diagram that is **derived from its",
           "graph bytes**, never drawn by hand (DIAGRAM LAW v1). The layout rule",
           "(lane/col/stack, compared bytes) is the **LAYOUT RULE paragraph in",
           "`scripts/graph_diagram.py`'s docstring** — one-source law: that",
           "paragraph is the spec, this README cites it, a contradiction between",
           "diagram and graph is a bug in that file (named defendant).",
           "Regenerate everything after editing any example:",
           "",
           "```sh",
           "python3 scripts/graph_diagram.py --all        # candidates (stdlib, deterministic)",
           "# render + shoot with archify (any machine with node + a chrome-headless-shell):",
           "#   node bin/archify.mjs finalize workflow examples/diagrams/<name>.candidate.json examples/diagrams/<name>.html --quality standard",
           "#   chrome-headless-shell --headless --no-sandbox --virtual-time-budget=12000 \\",
           "#     --window-size=1500,1500 --screenshot=examples/diagrams/<name>.png examples/diagrams/<name>.html",
           "python3 scripts/diagram_readme.py             # rebuild this table (derived)",
           "python3 scripts/graph_diagram.py --check --all # CI freshness gate: exit 1 on drift",
           "```",
           "",
           "| example | diagram | candidate sha256 | png sha256 | profile | gates |",
           "|---|---|---|---|---|---|"]
    for name, link, cs, hs, q, g_ in [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]:
        out.append(f"| {name} | {link} | {cs} | {hs} | {q} | {g_} |")
    out.append("")
    out.append("Cards (the two panels inside each diagram) are the ONLY hand-authored")
    out.append("diagram input; they live in `<name>.cards.json` beside the graph. Every")
    out.append("number in a card must be recomputable from the graph bytes it describes.")
    out.append("")
    out.append("Scope: every graph under `examples/` carries a conforming diagram.")
    out.append("Test fixtures (`tests/fixtures/`) are engine inputs consumed by test")
    out.append("code, not docs — no diagram (rung zero). Census command for the scope:")
    out.append(r"`git ls-tree -r --name-only HEAD | grep '\.json$' | grep -v '^graphify-out/'")
    out.append(r" | grep -v '^examples/diagrams/' | grep -v '\.cards\.json$'` —")
    out.append("every file whose parsed JSON has a non-empty `nodes` array must have a")
    out.append(f"table row or queue row in this table (receipt at build: examples/ {len(rows)+len(pending_rows)}")
    out.append(f"= {len(rows)} table + {len(pending_rows)} queue).")
    if pending_rows:
        out.append("")
        out.append("## Diagram queue (cards pending — generator skips, CI stays green)")
        out.append("")
        for p in sorted(pending_rows):
            out.append(f"- [ ] `{p}` — needs `<name>.cards.json`, then `--all` derives the row")
    out.append("")
    p = os.path.join(dia, "README.md")
    old = open(p).read() if os.path.exists(p) else ""
    if old != "\n".join(out) + "\n":
        open(p, "w").write("\n".join(out) + "\n")
        print(f"WROTE {p}")
    else:
        print(f"UNCHANGED {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
