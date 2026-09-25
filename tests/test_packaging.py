"""Packaging-specific reproducibility, manifest, and import-isolation checks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


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
            root = "hermes-workflows-0.9.0/"
            check("archive includes runtime, docs, skill, examples, tests, and checksum manifest",
                  all(root + rel in members for rel in (
                      "plugin.yaml", "__init__.py", "wf.py", "wfcommon.py",
                      "dashboard/manifest.json", "dashboard/plugin_api.py", "desktop/plugin.js",
                      "README.md", "INSTALL.md", "SKILL.md", "examples/smoke.json",
                      "examples/approve-publish.json", "examples/branch-on-verdict.json",
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
                          "examples/branch-on-verdict.json"})
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

    print("ALL PASS")


if __name__ == "__main__":
    main()
