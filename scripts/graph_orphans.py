#!/usr/bin/env python3
"""graph_orphans.py — the DELETION-AWARE graphify-out orphan check (est-i24i).

The conflict (#231 adversary, est-i24i): a PR that DELETES source files may not
regenerate graphify-out/ (single-writer law, scripts/graph_path_ban.py), yet the
committed graph still indexes the deleted paths. The naive orphan check in
tests/test_graph_gate.py — "every source_file the graph indexes is tracked in THIS
tree" — fails exactly that PR, while an in-PR regen fails the path ban. Both repairs
were impossible; the gates contradicted each other (suite-order-dependent: the
exact-head graph passes the orphan check and fails the ban; the base-restored graph
is the reverse).

The reconciled law (this module is its only home; both consumers share it):
  * an orphan whose source EXISTS in the PR's merge-base is EXPECTED-AND-TOLERATED
    until the next main-owned single-writer regen — that is precisely what the
    single-writer gate exists to defer;
  * an orphan indexing a source that was NEVER in the base is a HARD failure even
    in PR context (the graph may not invent files, deleted or otherwise);
  * tolerance applies ONLY in PR context (GITHUB_HEAD_REF + pull_request event).
    On main the graph must be exactly current — graph-main CI is that proof;
  * an unresolvable base FAILS CLOSED: every orphan is reported, none tolerated.

The ban itself (scripts/graph_path_ban.py) and the exact-head freshness check
(scripts/graph_check.py) are UNTOUCHED by this module — it only decides which
orphans the PR-time suite check may excuse.

The pure decision (orphan_decision) is split from git/env access so
tests/test_graph_orphan_deletion_231.py can unit-test the semantics directly and
drive the CLI against synthetic temp repos. Stdlib only.

  exit 0  no orphans, or every orphan was deleted by THIS PR (PR context only)
  exit 1  orphans that were not base-tracked — path list printed
  exit 2  git/graph unreadable — the check fails closed
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

GRAPH_PATH = "graphify-out/graph.json"


def graphify_out_orphans(graph, tracked):
    """Sorted source_file paths the graph indexes that are NOT tracked in `tracked`.
    `graph` is the parsed graph.json dict; `tracked` any container of tracked paths.
    Nodes without a source_file (semantic memory) never count: they are the
    graph's memory, not the tree's truth (same rule graph_check applies)."""
    src = {n.get("source_file") for n in graph.get("nodes", []) if n.get("source_file")}
    return sorted(s for s in src if s not in tracked)


def orphan_decision(orphans, in_base):
    """Pure decision. `orphans` = paths indexed but untracked in the HEAD tree.
    `in_base` = container/callable answering "was this path tracked at the PR base"
    or None when the base is unresolvable (fail-closed). Returns
    {"tolerated": [...deleted by this PR...], "missing": [...hard failures...]}.
    No source may be tolerated without a base that proves it was really there."""
    def _was(p):
        if in_base is None:
            return False
        return in_base(p) if callable(in_base) else (p in in_base)
    tolerated = sorted(p for p in orphans if _was(p))
    missing = sorted(p for p in orphans if not _was(p))
    return {"tolerated": tolerated, "missing": missing}


def _git(repo_dir, *args):
    return subprocess.run(["git", "-C", str(repo_dir), *args],
                          capture_output=True, text=True)


def tracked_files(repo_dir):
    """Paths tracked in the HEAD tree (None if git failed)."""
    r = _git(repo_dir, "ls-files")
    return set(r.stdout.split()) if r.returncode == 0 else None


def base_tracked(repo_dir, base):
    """Paths tracked at `base` (None if git failed)."""
    r = _git(repo_dir, "ls-tree", "-r", "--name-only", base)
    return set(r.stdout.split()) if r.returncode == 0 else None


def in_pr_context(env=None):
    """True only on a pull_request CI checkout with a head ref — the ONE context
    where a pre-regen orphan is legitimate. Local runs and main push builds
    resolve False and keep the check hard."""
    env = os.environ if env is None else env
    head_ref = (env.get("GITHUB_HEAD_REF") or "").strip()
    event = (env.get("GITHUB_EVENT_NAME") or "").strip()
    return bool(head_ref) and event == "pull_request"


def resolve_pr_base(repo_dir, env=None, explicit=None):
    """Base sha for the PR, or None if unresolvable. Priority: explicit --base >
    the event payload's pull_request.base.sha > merge-base origin/<base_ref> HEAD.
    A candidate that is not a commit object in this repo is NOT a base (deepen
    races on CI checkouts must fail closed, not tolerate everything)."""
    env = os.environ if env is None else env
    candidates = []
    if explicit:
        candidates.append(explicit)
    event_path = (env.get("GITHUB_EVENT_PATH") or "").strip()
    if event_path:
        try:
            payload = json.loads(Path(event_path).read_text())
            sha = ((payload.get("pull_request") or {}).get("base") or {}).get("sha")
            if sha:
                candidates.append(sha)
        except (OSError, ValueError):
            pass
    base_ref = (env.get("GITHUB_BASE_REF") or "").strip() or "main"
    r = _git(repo_dir, "merge-base", f"origin/{base_ref}", "HEAD")
    if r.returncode == 0 and r.stdout.strip():
        candidates.append(r.stdout.strip())
    for sha in candidates:
        v = _git(repo_dir, "cat-file", "-t", sha)
        if v.returncode == 0 and v.stdout.strip() == "commit":
            return sha
    return None


def decide_orphans(repo_dir, env=None, explicit_base=None, graph_path=None):
    """Wire the pieces: returns (decision, orphans, note). decision is None only
    when the inputs are unreadable (caller must fail closed, exit 2)."""
    repo_dir = Path(repo_dir)
    graph_file = repo_dir / (graph_path or GRAPH_PATH)
    try:
        graph = json.loads(graph_file.read_text())
    except (OSError, ValueError):
        return None, [], f"graph_orphans: cannot read {graph_file} — failing closed"
    tracked = tracked_files(repo_dir)
    if tracked is None:
        return None, [], "graph_orphans: git ls-files failed — failing closed"
    orphans = graphify_out_orphans(graph, tracked)
    if not orphans:
        return {"tolerated": [], "missing": []}, [], ""
    if in_pr_context(env):
        base = resolve_pr_base(repo_dir, env=env, explicit=explicit_base)
        base_files = base_tracked(repo_dir, base) if base else None
        if base_files is None:
            # fail-closed: an unresolvable base tolerates NOTHING
            note = (f"graph_orphans: PR base unresolvable "
                    f"(base={'-' if not base else base[:8]}) — no orphan tolerated")
            return {"tolerated": [], "missing": list(orphans)}, orphans, note
        d = orphan_decision(orphans, base_files)
        return d, orphans, f"graph_orphans: base {str(base)[:8]} resolved"
    return {"tolerated": [], "missing": list(orphans)}, orphans, \
        "graph_orphans: not a PR context — the tree must match the graph exactly"


def build_parser():
    ap = argparse.ArgumentParser(
        description="deletion-aware graphify-out orphan check (PR-time only; est-i24i)")
    ap.add_argument("--repo-dir", default=".",
                    help="repository root (default: cwd)")
    ap.add_argument("--base", default=None,
                    help="explicit PR base sha (default: event payload / merge-base)")
    ap.add_argument("--graph", default=None,
                    help=f"graph json path relative to repo (default {GRAPH_PATH})")
    return ap


def main(argv=None, env=None):
    args = build_parser().parse_args(argv)
    decision, orphans, note = decide_orphans(args.repo_dir, env=env,
                                             explicit_base=args.base,
                                             graph_path=args.graph)
    if decision is None:
        print(note)
        return 2
    if note:
        print(note)
    if not orphans:
        print("graph_orphans: OK — no orphan nodes")
        return 0
    if decision["tolerated"]:
        print(f"graph_orphans: {len(decision['tolerated'])} orphan(s) deleted by this "
              f"PR — tolerated until the next single-writer regen:")
        for p in decision["tolerated"]:
            print(f"  ~ {p}")
    if decision["missing"]:
        print(f"graph_orphans: FORBIDDEN — {len(decision['missing'])} orphan(s) index "
              f"sources that were never in the base (the graph may not invent files):")
        for p in decision["missing"]:
            print(f"  x {p}")
        print("fix: these are not deletions — restore the files or let the main-owned "
              "regen lane (branch ^chore/graph-) rebuild the graph.")
        return 1
    print("graph_orphans: OK — every orphan is a deletion owned by this PR's regen debt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
