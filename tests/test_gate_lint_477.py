#!/usr/bin/env python3
"""test_gate_lint_477 — the #477 law in code: every gate option string must
appear VERBATIM (exact substring, case-sensitive) in its gate's own doc text
(question + context), across every shipped example graph and doc snippet.

Symptom this pins (issue #477): a feature-gate question said "answer fix-round
then relaunch" while the option string was "fix-round: relaunch this WOF with
findings" — a releaser typing the token the question showed matched NO option
and the hold sat there. Docs carry truth: the fix is to repair doc text, never
to soften the match. This test is the refusal seam wired into
scripts/make_public.py; the mutation cases below prove the check bites.

Run: python3 tests/test_gate_lint_477.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_lint  # noqa: E402


def write_graph(base, rel, node):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"name": "t", "nodes": [node]}, indent=1),
                 encoding="utf-8")
    return p


class ShippedCorpus(unittest.TestCase):
    def test_repo_shipped_corpus_is_verbatim_clean(self):
        scan = gate_lint.collect(ROOT)
        drift = [str(v) for v in scan.violations]
        self.assertEqual(drift, [],
                         f"gate doc text drifts from option strings:\n"
                         + "\n".join(drift))

    def test_inventory_is_not_vacuous(self):
        # A lint that scans nothing passes for the wrong reason; the shipped
        # corpus must keep feeding it real gates. Floors are below the actual
        # count at the time of writing (12 gates / 26 options), so adding or
        # removing an example cannot silently starve the walk.
        scan = gate_lint.collect(ROOT)
        self.assertGreaterEqual(scan.gates, 10)
        self.assertGreaterEqual(scan.options_checked, 20)


class LintBites(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gate-lint-477-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_missing_option_in_graph_is_flagged(self):
        write_graph(self.tmp, "examples/x/drift.json", {
            "id": "hold", "type": "gate",
            "question": "Judge said park it — override?",
            "options": ["override: ship anyway", "stop"],
        })
        scan = gate_lint.collect(self.tmp)
        self.assertEqual(scan.gates, 1)
        self.assertEqual(sorted(v.option for v in scan.violations),
                         ["override: ship anyway", "stop"])
        self.assertEqual(scan.violations[0].rel, "examples/x/drift.json")

    def test_verbatim_is_case_sensitive(self):
        # 'Ship' must not bless option 'ship': the executor matches exactly.
        write_graph(self.tmp, "examples/x/case.json", {
            "id": "approve", "type": "gate",
            "question": "Ship the artifact?",
            "options": ["ship"],
        })
        scan = gate_lint.collect(self.tmp)
        self.assertEqual([v.option for v in scan.violations], ["ship"])

    def test_context_counts_as_doc_text(self):
        write_graph(self.tmp, "examples/x/ctx.json", {
            "id": "approve", "type": "gate",
            "question": "Proceed?",
            "options": ["publish", "rewrite"],
            "context": "'publish' ships it, 'rewrite' sends it back.",
        })
        scan = gate_lint.collect(self.tmp)
        self.assertEqual(scan.violations, [])
        self.assertEqual(scan.options_checked, 2)

    def test_partial_fix_still_lists_every_remaining_drift(self):
        write_graph(self.tmp, "examples/x/partial.json", {
            "id": "esc", "type": "gate",
            "question": "Answer 'act' to authorize.",
            "options": ["act", "hold", "dismiss"],
        })
        scan = gate_lint.collect(self.tmp)
        self.assertEqual(sorted(v.option for v in scan.violations),
                         ["dismiss", "hold"])

    def test_machine_and_when_gates_without_options_are_skipped(self):
        write_graph(self.tmp, "examples/x/route.json", {
            "id": "go", "type": "gate",
            "when": "out.j.verdict == 'ship'", "on_skip": "prune",
        })
        write_graph(self.tmp, "examples/x/machine.json", {
            "id": "wait", "type": "gate", "wait": {"wait_s": 0.01},
        })
        scan = gate_lint.collect(self.tmp)
        self.assertEqual(scan.gates, 0)
        self.assertEqual(scan.violations, [])

    def test_markdown_fence_gate_snippet_checked(self):
        (self.tmp / "GUIDE.md").write_text(
            "# guide\n\n```json\n{ \"id\": \"approve\", \"type\": \"gate\",\n"
            "  \"question\": \"Ship?\", \"options\": [\"ship\", \"hold\"] }\n"
            "```\n", encoding="utf-8")
        scan = gate_lint.collect(self.tmp)
        # GUIDE.md is not in the linted doc set — must be invisible...
        self.assertEqual([v.rel for v in scan.violations], [])
        # ...while the same snippet under a linted name fails.
        shutil.move(str(self.tmp / "GUIDE.md"), str(self.tmp / "AGENTS.md"))
        scan = gate_lint.collect(self.tmp)
        self.assertEqual(sorted(v.option for v in scan.violations),
                         ["hold", "ship"])
        self.assertEqual(scan.violations[0].rel, "AGENTS.md")


class LibraryEnvelope(unittest.TestCase):
    def test_meta_graph_envelope_walked(self):
        tmp = Path(tempfile.mkdtemp(prefix="gate-lint-477-env-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        p = tmp / "library" / "general" / "tpl.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({
            "meta": {"name": "tpl"},
            "graph": {"nodes": [{
                "id": "approve", "type": "gate",
                "question": "Approve?", "options": ["publish"]}]},
        }), encoding="utf-8")
        scan = gate_lint.collect(tmp)
        self.assertEqual(scan.gates, 1)
        self.assertEqual([v.option for v in scan.violations], ["publish"])


class MakePublicWiring(unittest.TestCase):
    """#477 refuses at the publish door, not only in tests."""

    def _mk_repo(self, drift):
        repo = Path(tempfile.mkdtemp(prefix="gate-lint-477-mp-"))
        (repo / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts" / "make_public.py", repo / "scripts")
        shutil.copy2(ROOT / "scripts" / "gate_lint.py", repo / "scripts")
        (repo / "scripts" / ".scrub-guards").write_text(
            "# guards copy\nscripts/make_public.py\n", encoding="utf-8")
        opts = ["drift-me", "also-drift"] if drift else ["ok"]
        ctx = "nothing quoted here" if drift else "'ok' is the only answer."
        (repo / "examples").mkdir()
        (repo / "examples" / "g.json").write_text(json.dumps({
            "nodes": [{"id": "gate1", "type": "gate",
                       "question": "Proceed?", "options": opts,
                       "context": ctx}]}), encoding="utf-8")
        subprocess.run(["/usr/bin/git", "-C", str(repo), "init", "-q"],
                       check=True)
        subprocess.run(["/usr/bin/git", "-C", str(repo), "add", "-A"],
                       check=True)
        subprocess.run(["/usr/bin/git", "-C", str(repo),
                        "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-q", "-m", "t"], check=True)
        return repo

    def _run(self, repo):
        out = repo / "pub-out"
        r = subprocess.run(
            [sys.executable, str(repo / "scripts" / "make_public.py"),
             str(out), "--repo", str(repo)],
            capture_output=True, text=True, timeout=120)
        return r

    def test_make_public_refuses_gate_drift(self):
        repo = self._mk_repo(drift=True)
        self.addCleanup(shutil.rmtree, repo, True)
        r = self._run(repo)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("GATE LINT FAILED", r.stderr)
        for opt in ("drift-me", "also-drift"):
            self.assertIn(opt, r.stderr)
        self.assertFalse((repo / "pub-out").exists(),
                         "refusal must copy nothing")

    def test_make_public_publishes_verbatim_clean_repo(self):
        repo = self._mk_repo(drift=False)
        self.addCleanup(shutil.rmtree, repo, True)
        r = self._run(repo)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("0 scrub hits", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
