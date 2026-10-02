"""Packaging-specific reproducibility, manifest, and import-isolation checks."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERSION = re.search(r"^version:\s*([\d.]+)", (ROOT / "plugin.yaml").read_text(), re.M).group(1)


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print("PASS", label)


def main() -> None:
    manifest = json.loads((ROOT / "dashboard/manifest.json").read_text(encoding="utf-8"))
    check("dashboard backend manifest is API-only with a hidden tab",
          manifest.get("api") == "plugin_api.py" and manifest.get("tab", {}).get("hidden") is True
          and "entry" not in manifest)

    collision = types.ModuleType("wfcommon")
    sys.modules["wfcommon"] = collision
    api_path = ROOT / "dashboard/plugin_api.py"
    before_path = list(sys.path)
    spec = importlib.util.spec_from_file_location("packaging_dashboard_probe", api_path)
    if spec is None or spec.loader is None:
        raise AssertionError("dashboard plugin API cannot be loaded")
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    scoped = api._workflow_common()
    check("dashboard resolves its sibling wfcommon under a private module name",
          Path(scoped.__file__).resolve() == (ROOT / "wfcommon.py").resolve()
          and scoped is not collision and sys.modules["wfcommon"] is collision
          and list(sys.path) == before_path)
    sys.modules.pop("wfcommon", None)

    with tempfile.TemporaryDirectory(prefix=".tmp-package-", dir=HERE) as temp_dir:
        temp = Path(temp_dir)
        first = temp / "first.zip"
        second = temp / "second.zip"
        for target in (first, second):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/pack.py"), "--output", str(target)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise AssertionError(
                    f"pack.py exit {result.returncode}:\n{result.stdout}\n{result.stderr}"
                )
        first_bytes, second_bytes = first.read_bytes(), second.read_bytes()
        check("identical source trees produce byte-identical archives", first_bytes == second_bytes)
        check("sidecar pins the archive bytes",
              first.with_suffix(".zip.sha256").read_text(encoding="utf-8")
              == f"{hashlib.sha256(first_bytes).hexdigest()}  first.zip\n")

        with zipfile.ZipFile(first) as archive:
            members = set(archive.namelist())
            root = f"hermes-workflows-{VERSION}/"
            check("archive includes runtime, docs, skill, examples, tests, and checksum manifest",
                  all(root + rel in members for rel in (
                      "plugin.yaml", "__init__.py", "wf.py", "wfcommon.py",
                      "dashboard/manifest.json", "dashboard/plugin_api.py", "desktop/plugin.js",
                      "README.md", "INSTALL.md", "SKILL.md", "examples/smoke.json",
                      "examples/approve-publish.json", "examples/blind-council.workflow.json",
                      "examples/branch-on-verdict.json",
                      "examples/triage-route.workflow.json",
                      "examples/portable-review.workflow.json",
                      "examples/incident-response.json",
                      "examples/gated-publish.workflow.json",
                      "examples/machine-watch.workflow.json",
                      "examples/exchange-run.workflow.json",
                      "examples/quorum-probe.workflow.json",
                      "examples/census-fanout.workflow.json", "examples/escalation-ladder.workflow.json", "examples/bulk-transform.workflow.json", "references/portable.md",
                      "tests/test_packaging.py", "tests/test_fanout_ui.mjs", "tests/test_card_frontend_contract.mjs",
                      "tests/test_inline_header.mjs", "tests/fixtures/mac-source.txt",
                      "references/grammar.md", "references/operations.md", "SHA256SUMS")))
            check("fake child retains executable mode in ZIP",
                  (archive.getinfo(root + "tests/fake").external_attr >> 16) & 0o111 == 0o111)
            unsafe = ("/.git/", "/home", "/workflows/", "/state.db", "/runner.log",
                      "/pre-lanes", "/home1/", "/.tmp-")
            check("archive excludes generated homes, owner-local examples, state, backups, logs, and Git metadata",
                  not any(part.endswith("/.git") or any(token in part for token in unsafe)
                          for part in members)
                  and {m[len(root):] for m in members if m.startswith(root + "examples/")}
                      == {"examples/smoke.json", "examples/approve-publish.json",
                          "examples/blind-council.workflow.json",
                          "examples/branch-on-verdict.json",
                          "examples/triage-route.workflow.json",
                          "examples/incident-response.json",
                          "examples/portable-review.workflow.json",
                          "examples/gated-publish.workflow.json",
                          "examples/machine-watch.workflow.json",
                          "examples/quorum-probe.workflow.json",
                          "examples/census-fanout.workflow.json", "examples/escalation-ladder.workflow.json", "examples/bulk-transform.workflow.json",
                          "examples/exchange-run.workflow.json"})
            checksum_text = archive.read(root + "SHA256SUMS").decode("utf-8")
            rows = [line.split("  ", 1) for line in checksum_text.splitlines()]
            check("SHA256SUMS verifies every pinned source entry",
                  bool(rows) and all(len(row) == 2 and root + row[1] in members
                                     and hashlib.sha256(archive.read(root + row[1])).hexdigest() == row[0]
                                     for row in rows))
            manifest = archive.read(root + "plugin.yaml").lower()
            check("public manifest declares license, homepage and requires_hermes",
                  b"license: mit" in manifest and b"homepage: https://github.com/" in manifest
                  and b"requires_hermes:" in manifest)

        # #105 discharge: membership-by-glob passed while the shipped test_*.py died
        # ModuleNotFoundError on wf_test_isolation — assert the import CLOSURE from the
        # unpacked package root instead of just listing names.
        with tempfile.TemporaryDirectory(prefix=".tmp-unpack-") as unpack_dir:
            unpacked = Path(unpack_dir)
            with zipfile.ZipFile(first) as archive:
                archive.extractall(unpacked)
            pkg = unpacked / root.rstrip("/")
            core_allowlist = {"hermes_constants", "fastapi"}  # supplied by the pinned /opt/hermes env
            missing: dict[str, list[str]] = {}
            for test_file in sorted(pkg.glob("tests/test_*.py")):
                tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
                names: set[str] = set()
                for node in tree.body:  # top-level imports only: the shipped-entry contract
                    if isinstance(node, ast.Import):
                        names.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        names.add(node.module.split(".")[0])
                # Resolution mirrors the shipped-entry reality: running tests/test_X.py puts
                # tests/ (script dir) on sys.path; root and dashboard/ ride along as the
                # tests themselves insert them. A top-level import that resolves in NONE of
                # these is the #105 dead-package shape.
                probe = (
                    "import importlib.util, json, sys\n"
                    "root = sys.argv[1]\n"
                    "for p in (root, root + '/tests', root + '/dashboard'):\n"
                    "    sys.path.insert(0, p)\n"
                    "mods = json.loads(sys.argv[2])\n"
                    "bad = []\n"
                    "for m in mods:\n"
                    "    try:\n"
                    "        importlib.import_module(m)\n"
                    "    except Exception as exc:\n"
                    "        bad.append(f'{m}: {type(exc).__name__}: {exc}')\n"
                    "print('MISSING:' + json.dumps(bad))\n"
                )
                candidates = sorted(
                    n for n in names
                    if n not in sys.stdlib_module_names and n not in core_allowlist
                    and n != test_file.stem
                )
                env = {k: v for k, v in os.environ.items()
                       if k not in {"WF_RUNS_ROOT", "HERMES_HOME"}}
                env.setdefault("PYTHONPATH", "/opt/hermes")
                result = subprocess.run(
                    [sys.executable, "-c", probe, str(pkg), json.dumps(candidates)],
                    capture_output=True, text=True, env=env,
                )
                line = [l for l in result.stdout.splitlines() if l.startswith("MISSING:")]
                bad = json.loads(line[-1][len("MISSING:"):]) if line else [result.stderr[-200:]]
                for failure in bad:
                    missing.setdefault(test_file.name, []).append(failure)
            check("every shipped tests/test_*.py import-closure resolves from the unpacked package root",
                  not missing and repr(missing) == "{}")

    print("ALL PASS")


if __name__ == "__main__":
    main()
