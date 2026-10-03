#!/usr/bin/env python3
"""graph_path_ban.py — PR branches do not touch the knowledge graph (single-writer, #153).

graphify-out/ is a committed derived artifact with exactly ONE writer: the main-owned
regen lane (scripts/graph_regen.py via the ra-graph-regen graph, which opens a
chore(graph): PR). Every other PR is forbidden from the path: an author-side regen
was the r10 pattern that made every two open PRs collide on cosmetic graph churn.

The ban: base = `git merge-base origin/<base-ref> HEAD` (default main; CI passes
the event's base_ref), changed = `git diff --name-only base..HEAD -- graphify-out/`.
Non-empty changed → exit 1 printing the offending files, UNLESS the head branch
matches ^chore/graph- AND every changed file lives under graphify-out/ — the regen
lane's own PR shape (branch chore/graph-<sha7>, ONLY graphify-out/ files). A
mixed PR that claims the exempt branch prefix but also edits source is not a
regen PR and fails.

The core decision is split from argv (build_parser / head_branch / changed_files /
ban_decision) so tests/test_graph_single_writer_153.py can unit-test the semantics
directly and drive the CLI against a temp clone. Stdlib only.

  exit 0  no graphify-out/ paths in the PR diff (or an exempt regen-lane PR)
  exit 1  the diff touches graphify-out/ outside the regen lane — file list printed
  exit 2  git failed (not a repo, base-ref unknown) — the gate fails closed
"""
import argparse
import os
import re
import subprocess
import sys

GRAPH_OUT_PREFIX = "graphify-out/"
EXEMPT_BRANCH_RE = re.compile(r"^chore/graph-")


def exempt_branch(branch):
    """True only for the regen lane's own branch pattern ^chore/graph-."""
    return bool(EXEMPT_BRANCH_RE.match(branch or ""))


def ban_decision(changed, branch, *, graphify_out_prefix=GRAPH_OUT_PREFIX):
    """Pure decision. `changed` = every path changed base..HEAD (all paths, not
    only the graph path). Returns None when the PR is exempt (regen lane: branch
    matches AND the whole diff lives under the graph prefix — that is exactly the
    shape scripts/graph_regen.py's caller is allowed to open), else the list of
    offending graphify-out/ paths (empty list = clean, no ban triggered)."""
    graph_touched = [f for f in changed if f.startswith(graphify_out_prefix)]
    if not graph_touched:
        return []
    if exempt_branch(branch) and all(f.startswith(graphify_out_prefix) for f in changed):
        return None
    return graph_touched


def _git(repo_dir, *args):
    return subprocess.run(["git", "-C", str(repo_dir), *args],
                          capture_output=True, text=True)


def merge_base(repo_dir, base_ref):
    """base = git merge-base origin/<base-ref> HEAD (None if git failed)."""
    r = _git(repo_dir, "merge-base", f"origin/{base_ref}", "HEAD")
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def head_branch(repo_dir, env=None):
    """Head branch name, CI-first: GITHUB_HEAD_REF is the only truth when
    actions/checkout leaves a detached HEAD on the PR merge ref; GITHUB_REF_NAME
    covers the push-event case; otherwise ask git (local contributor run)."""
    env = os.environ if env is None else env
    for key in ("GITHUB_HEAD_REF", "GITHUB_REF_NAME"):
        v = (env.get(key) or "").strip()
        if v:
            return v
    r = _git(repo_dir, "branch", "--show-current")
    return r.stdout.strip() if r.returncode == 0 else ""


def changed_files(repo_dir, base, head="HEAD"):
    """All paths changed base..head (full diff — the exemption check needs to see
    whether ANY non-graph file moved, not only the offending slice)."""
    r = _git(repo_dir, "diff", "--name-only", f"{base}..{head}")
    if r.returncode != 0:
        return None
    return [f for f in r.stdout.splitlines() if f]


def build_parser():
    ap = argparse.ArgumentParser(
        description="PR branches do not touch the knowledge graph (single-writer, #153)")
    ap.add_argument("--base-ref", default="main",
                    help="base branch to compute merge-base against (CI passes "
                         "the event's github.base_ref; empty falls back to main)")
    ap.add_argument("--repo-dir", default=".",
                    help="repository root (default: cwd)")
    return ap


def main(argv=None, env=None):
    args = build_parser().parse_args(argv)
    base_ref = args.base_ref or "main"  # a non-PR event hands us an empty base_ref
    base = merge_base(args.repo_dir, base_ref)
    if base is None:
        print(f"graph_path_ban: cannot compute merge-base against origin/{base_ref} "
              f"(does the CI checkout fetch it?) — failing closed")
        return 2
    changed = changed_files(args.repo_dir, base)
    if changed is None:
        print("graph_path_ban: git diff failed — failing closed")
        return 2
    branch = head_branch(args.repo_dir, env=env)
    offenders = ban_decision(changed, branch)
    if offenders is None:
        print(f"graph_path_ban: OK — regen-lane PR ({branch}) touches only "
              f"{GRAPH_OUT_PREFIX} ({len(changed)} files) — exempt")
        return 0
    if not offenders:
        print(f"graph_path_ban: OK — no {GRAPH_OUT_PREFIX} paths in the PR diff")
        return 0
    print(f"graph_path_ban: FORBIDDEN — PR branch '{branch}' touches the "
          f"single-writer path {GRAPH_OUT_PREFIX} ({len(offenders)} files):")
    for f in offenders:
        print(f"  {f}")
    print(f"only the main-owned regen lane (branch ^chore/graph-, graphify-out/ "
          f"files only) may change it — see issue #153. Drop these files from "
          f"the PR; main's graph refreshes itself after merge.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
