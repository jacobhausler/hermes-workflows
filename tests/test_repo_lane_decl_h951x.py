#!/usr/bin/env python3
"""est-h951x: every ra-work verb that hands an agent a git worktree must DECLARE
the lane via node `repo: {run.lane_root}/{run.bead}` — otherwise the mechanical
lane guards (incomplete_work / lane_wreckage) never see the lane and a dead
child's uncommitted tree silently becomes the next child's base.

Contracts pinned here:
  (1) verb=fix renders fix node with non-empty repo equal to the template;
  (2) verb=build-deep renders build node with the same template;
  (3) verb=build-deep REFUSES (exit 2) when --lane-root or --bead missing —
      no silent default, law 4.

The binder lives on the runtime shelf (not the public tree): skip when absent.

Standalone script (no pytest):
  python3 tests/test_repo_lane_decl_h951x.py
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SHELF = Path(os.path.expanduser("~/.hermes/workflows/library/binders/ra_work.py"))

BASE = dict(verb="fix", repo="octo/widgets", bead="est-t", store="/s",
            lane_root="/lr", test_cmd="t", acceptance="a")


def render(verb, **overrides):
    args = {"fix": ["--repo", "--bead", "--store", "--lane-root", "--test-cmd",
                    "--acceptance"],
            "build-deep": ["--item", "--repo", "--base-branch", "--lane-root",
                           "--bead"]}[verb]
    vals = {"fix": {"--repo": overrides.get("repo", "octo/widgets"),
                    "--bead": overrides.get("bead", "est-t"),
                    "--store": "/s",
                    "--lane-root": overrides.get("lane_root", "/lr"),
                    "--test-cmd": "t",
                    "--acceptance": "a"},
            "build-deep": {"--item": "x", "--repo": "r",
                           "--base-branch": "main",
                           "--lane-root": overrides.get("lane_root", "/lr"),
                           "--bead": overrides.get("bead", "est-t")}}[verb]
    cmd = [sys.executable, str(SHELF), "--verb", verb]
    for f in args:
        cmd += [f, vals[f]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc


@unittest.skipUnless(SHELF.is_file(), "ra_work binder not on this shelf")
class RepoLaneDeclH951x(unittest.TestCase):
    def test_fix_node_declares_lane(self):
        proc = render("fix")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        graph = json.loads(proc.stdout)
        node = [n for n in graph["nodes"] if n["id"] == "fix"][0]
        self.assertEqual(node.get("repo"), "{run.lane_root}/{run.bead}")

    def test_build_deep_node_declares_lane(self):
        proc = render("build-deep")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        graph = json.loads(proc.stdout)
        node = [n for n in graph["nodes"] if n["id"] == "build"][0]
        self.assertEqual(node.get("repo"), "{run.lane_root}/{run.bead}")

    def test_build_deep_refuses_missing_lane_root(self):
        cmd = [sys.executable, str(SHELF), "--verb", "build-deep",
               "--item", "x", "--repo", "r", "--base-branch", "main",
               "--bead", "est-t"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("lane-root", proc.stderr.lower())
        self.assertEqual(proc.stdout, "")

    def test_build_deep_refuses_missing_bead(self):
        cmd = [sys.executable, str(SHELF), "--verb", "build-deep",
               "--item", "x", "--repo", "r", "--base-branch", "main",
               "--lane-root", "/lr"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
