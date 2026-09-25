#!/usr/bin/env python3
"""Graph drift gate: is the committed graphify-out/graph.json current for this tree?

Usage: python3 scripts/graph_check.py [--fix]

Runs `graphify update .` (AST only, no LLM, no network) into a scratch copy and compares
the node/edge SET with the committed graph. Community labels and layout are ignored —
they are the one LLM-derived artifact and are refreshed by hand (`graphify label .`).

  exit 0  graph current
  exit 1  graph stale → prints the delta; `--fix` rewrites the committed graph in place
  exit 2  graphify not installed (uv tool install graphifyy) or no committed graph

WHY a gate and not auto-commit: the graph is a build product of the source; a stale
committed graph is a lie the agents will read. Making the contributor run one command
is cheaper than a bot commit racing every push.
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graphify-out"
GRAPH = OUT / "graph.json"


def sig(g):
    nodes = sorted(n["id"] for n in g["nodes"])
    edges = sorted((e["source"], e["target"], e.get("relation", "")) for e in g.get("links", g.get("edges", [])))
    return nodes, edges


def main():
    fix = "--fix" in sys.argv
    if not shutil.which("graphify"):
        print("graph_check: graphify not on PATH (uv tool install graphifyy)"); return 2
    if not GRAPH.exists():
        print(f"graph_check: no committed graph at {GRAPH}"); return 2
    committed = json.loads(GRAPH.read_text())

    with tempfile.TemporaryDirectory(prefix="graph-check-") as td:
        work = Path(td) / "tree"
        # Snapshot the WORKING TREE (tracked + staged + unstaged), not HEAD: the local
        # use is "did I regenerate after my edit", and that edit is usually not yet
        # committed. `git ls-files` honours .gitignore exactly like a contributor's checkout.
        work.mkdir()
        files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-co", "--exclude-standard", "-z"],
                               capture_output=True, check=True).stdout.split(b"\0")
        for rel in files:
            if not rel or rel.startswith(b"graphify-out/"): continue
            src = ROOT / rel.decode()
            if not src.is_file(): continue
            dst = work / rel.decode(); dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy(src, dst)
        # carry the committed graph so update is incremental and keeps labels
        (work / "graphify-out").mkdir(exist_ok=True)
        for f in OUT.iterdir():
            if f.is_file():
                shutil.copy(f, work / "graphify-out" / f.name)
        r = subprocess.run(["graphify", "update", str(work), "--force"], capture_output=True, text=True,
                           env={**os.environ, "GRAPHIFY_NO_LLM": "1"})
        if r.returncode != 0:
            print(r.stdout[-1500:], r.stderr[-1500:]); print("graph_check: graphify update failed"); return 2
        fresh_path = work / "graphify-out" / "graph.json"
        fresh = json.loads(fresh_path.read_text())

        cn, ce = sig(committed); fn, fe = sig(fresh)
        if cn == fn and ce == fe:
            print(f"graph_check: OK — {len(cn)} nodes, {len(ce)} edges match the tree"); return 0

        add_n = sorted(set(fn) - set(cn)); del_n = sorted(set(cn) - set(fn))
        add_e = len(set(fe) - set(ce)); del_e = len(set(ce) - set(fe))
        print(f"graph_check: STALE — nodes +{len(add_n)} -{len(del_n)}, edges +{add_e} -{del_e}")
        for n in add_n[:12]: print(f"  + {n}")
        for n in del_n[:12]: print(f"  - {n}")
        if fix:
            for name in ("graph.json", "GRAPH_REPORT.md", "manifest.json"):
                src = work / "graphify-out" / name
                if src.exists(): shutil.copy(src, OUT / name)
            print("graph_check: rewrote graphify-out/{graph.json,GRAPH_REPORT.md,manifest.json} — commit them")
            return 0
        print("fix: python3 scripts/graph_check.py --fix   (or: graphify update .)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
