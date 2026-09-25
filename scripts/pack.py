#!/usr/bin/env python3
"""Build the private, reproducible Hermes Workflows source ZIP (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.9.0"
PACKAGE_NAME = f"hermes-workflows-{VERSION}"

# Exact files plus deliberately narrow source patterns. Never package a worktree wholesale.
INCLUDE_FILES = (
    ".gitignore",
    "AGENTS.md",
    "INSTALL.md",
    "LICENSE",
    "README.md",
    "SKILL.md",
    "__init__.py",
    "dashboard/manifest.json",
    "dashboard/plugin_api.py",
    "desktop/plugin.js",
    "examples/approve-publish.json",
    "examples/branch-on-verdict.json",
    "examples/smoke.json",
    "plugin.yaml",
    "CHANGELOG.md",
    "scripts/graph_check.py",
    "scripts/pack.py",
    "scripts/suite.py",
    "graphify-out/GRAPH_REPORT.md",
    "graphify-out/graph.json",
    ".graphifyignore",
    "tests/fake",
    "tests/fake_hermes.py",
    "tests/fixtures/mac-source.txt",
    "tests/test_fanout_ui.mjs",
    "wf.py",
    "wfcommon.py",
)
INCLUDE_PATTERNS = ("tests/test_*.py", "tests/test_*.mjs", "references/*.md")
EXECUTABLE_FILES = {"scripts/pack.py", "tests/fake"}


def collect_sources() -> list[tuple[str, bytes]]:
    paths = {Path(name) for name in INCLUDE_FILES}
    for pattern in INCLUDE_PATTERNS:
        matches = sorted(ROOT.glob(pattern))
        if not matches:
            raise RuntimeError(f"include pattern matched no files: {pattern}")
        paths.update(path.relative_to(ROOT) for path in matches)

    sources: list[tuple[str, bytes]] = []
    for rel in sorted(paths, key=lambda p: p.as_posix()):
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"included path is not a regular file: {rel.as_posix()}")
        try:
            path.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"included path escapes source root: {rel.as_posix()}") from exc
        sources.append((rel.as_posix(), path.read_bytes()))

    manifest = dict(sources).get("plugin.yaml", b"").decode("utf-8")
    if not re.search(rf"(?m)^version:\s*{re.escape(VERSION)}\s*$", manifest):
        raise RuntimeError(f"plugin.yaml must declare version {VERSION}")
    return sources


def _zip_info(name: str, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o755 if executable else 0o644
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.extra = b""
    info.comment = b""
    return info


def build(output: Path) -> tuple[str, Path]:
    sources = collect_sources()
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    checksums = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name}\n" for name, data in sources
    ).encode("utf-8")

    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, strict_timestamps=True) as archive:
            for name, data in sources:
                archive.writestr(
                    _zip_info(f"{PACKAGE_NAME}/{name}", name in EXECUTABLE_FILES),
                    data,
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
            archive.writestr(
                _zip_info(f"{PACKAGE_NAME}/SHA256SUMS"), checksums,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    sidecar = output.with_suffix(output.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest, sidecar


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "artifacts" / f"{PACKAGE_NAME}.zip",
        help="output ZIP path (default: artifacts/<package>.zip)",
    )
    args = parser.parse_args()
    digest, sidecar = build(args.output)
    print(f"archive: {args.output.expanduser().resolve()}")
    print(f"sha256: {digest}")
    print(f"sha256 sidecar: {sidecar}")
    print(f"source files: {len(collect_sources())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
