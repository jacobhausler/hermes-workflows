"""Release ZIP omits tests whose fixtures only exist in the source checkout."""
from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ONLY_TESTS = {
    "tests/test_diagram_law.py", "tests/test_example_census_fanout.py",
    "tests/test_example_issue_to_pr.py", "tests/test_example_release_lifecycle.py",
    "tests/test_lane_recover_8edcc9bf.py", "tests/test_example_exchange_run.py",
}


def main():
    spec = importlib.util.spec_from_file_location("pack_756", ROOT / "scripts/pack.py")
    assert spec is not None and spec.loader is not None
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    with tempfile.TemporaryDirectory(prefix="pack-756-") as tmp:
        archive = Path(tmp) / "release.zip"
        pack.build(archive)
        with zipfile.ZipFile(archive) as z:
            prefix = pack.PACKAGE_NAME + "/"
            members = {name.removeprefix(prefix) for name in z.namelist()}
        for path in sorted(SOURCE_ONLY_TESTS):
            assert path not in members, f"source-only test shipped without its inputs: {path}"
            print("PASS source-only test excluded:", path)
        for path in ("tests/test_packaging.py", "tests/test_package_source_only_756.py",
                     "post_exit_hook.py"):
            assert path in members, f"package regression gate omitted: {path}"
            print("PASS package gate still ships:", path)
        reasons = getattr(pack, "SOURCE_ONLY_TESTS", {})
        assert set(reasons) == SOURCE_ONLY_TESTS, "each exclusion needs an explicit include decision"
        assert all(isinstance(reason, str) and reason.strip() for reason in reasons.values())
        print("PASS each source-only exclusion has a reason")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
