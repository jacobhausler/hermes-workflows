#!/usr/bin/env python3
"""est-fxpsl: run-dir retention — size cap first-class, age cut second,
never-delete law for referenced dirs.

Contracts pinned here (one behaviour each, failing if the rule erodes):
  (1) an over-cap terminal run dir loses its work/ subtree and payload files
      but keeps its transcript/package files (the cap is the size bound;
      transcripts are the mining substrate and never the mass);
  (2) a run dir named by an UNCLOSED tracker row survives whole (acceptance-4
      shape: point the board at a fat dir, show the prune skips it);
  (3) a run dir named in a nightly receipt file survives whole;
  (4) age cuts the whole dir, but the newest KEEP_NEWEST nightly-named dirs
      under the cap are kept; a young dir is in grace; an owner-held dir
      never goes;
  (5) drill scratch is RECEIPT-THEN-DELETE: evidence files land in the receipt
      store before the copy trees die; a completed drill closes on --drill-now
      and an abandoned one only past its TTL;
  (6) the run reports freed bytes + actions into the janitor-receipt schema.

Standalone script (no pytest):
  python3 tests/test_run_retention_fxpsl.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "retention.py"

OLD = 20 * 86400
FAT_AGE = 5 * 86400


def run_dir(root, name, *, age=FAT_AGE, work_payloads=0, extra_files=(),
            exit_file=True, marker=None, payload_bytes=6 * 1024 * 1024,
            cap_small=False):
    d = root / name
    (d / "work" / "maintain" / "backend").mkdir(parents=True, exist_ok=True)
    stamps = []
    for f in ("graph.json", "run.json", "events.jsonl"):
        p = d / f
        p.write_text("{}\n")
        stamps.append(p)
    if exit_file:
        p = d / "runner_exit.json"
        p.write_text(json.dumps({"reason": "done", "at": "2026-11-01T00:00:00+00:00"}))
        stamps.append(p)
    p = d / "summary.md"
    p.write_text("transcript stays\n")
    for f in extra_files:
        p = d / f
        p.write_text("note\n")
        stamps.append(p)
    if marker:
        (d / marker).write_text("")
    n = work_payloads
    for i in range(n):
        tp = d / "work" / "maintain" / "backend" / f"state{i}.tar"
        with tp.open("wb") as fh:
            fh.write(b"\0" * payload_bytes)
    for p in stamps:
        ts = time.time() - age
        os.utime(p, (ts, ts))
    ts = time.time() - age
    os.utime(d, (ts, ts))
    return d


class RetentionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wf-retention-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.runs = self.home / ".hermes" / "workflows"
        self.runs.mkdir(parents=True)
        self.ledger = self.home / ".local" / "share" / "nightly"
        self.ledger.mkdir(parents=True)
        self.receipts = self.home / "receipts"
        self.receipts.mkdir()
        self.beads = self.home / "open-rows.json"

    def prune(self, *extra):
        cmd = [sys.executable, str(SCRIPT), "prune",
               "--runs-root", str(self.runs), "--home", str(self.home),
               "--receipt-root", str(self.ledger),
               "--beads-json", str(self.beads),
               "--report-dir", str(self.receipts),
               "--receipt-file", str(self.receipts / "janitor.jsonl"),
               "--receipt-root-drill", str(self.home / ".local" / "share" / "backup-assurance"),
               "--cap-bytes", str(1 * 1024 * 1024),
               "--payload-after-hours", "1"] + list(extra)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_cap_prunes_payloads_keeps_transcripts(self):
        d = run_dir(self.runs, "20261101-000000-fat-a0", work_payloads=2)
        self.beads.write_text("[]")
        out = self.prune()
        self.assertIn("retention-workspace-cap:20261101-000000-fat-a0", out)
        self.assertFalse((d / "work").exists(), "workspace subtree must be gone")
        self.assertTrue((d / "summary.md").exists(), "transcript must survive")
        self.assertTrue((d / "runner_exit.json").exists())

    def test_open_row_reference_wins_over_cap(self):
        d = run_dir(self.runs, "20261101-000001-nightly-keep-a0", work_payloads=2)
        self.beads.write_text(json.dumps(
            [{"id": "est-pin", "title": "t", "description": "pinned 20261101-000001-nightly-keep-a0"}]))
        self.prune()
        self.assertTrue((d / "work" / "maintain" / "backend" / "state0.tar").exists(),
                        "a run dir referenced by an open row must never be deleted or pruned")

    def test_nightly_receipt_reference_wins_over_cap(self):
        d = run_dir(self.runs, "20261101-000005-refer-a0", work_payloads=1)
        self.beads.write_text("[]")
        (self.ledger / "2026-11-01.jsonl").write_text(json.dumps(
            {"date": "2026-11-01", "id": "x", "note": "run 20261101-000005-refer-a0 ok"}) + "\n")
        self.prune()
        self.assertTrue((d / "work").exists(), "receipt-referenced run dir must survive whole")

    def test_age_cut_keep_newest_grace_and_marker(self):
        self.beads.write_text("[]")
        old1 = run_dir(self.runs, "20261001-000000-nightly-old-a0", age=OLD, work_payloads=0,
                       extra_files=("receipt.txt",))
        old2 = run_dir(self.runs, "20261010-000000-nightly-old-a0", age=OLD - 86400, work_payloads=0)
        old3 = run_dir(self.runs, "20261009-000000-nightly-old-a0", age=OLD - 2 * 86400, work_payloads=0)
        young = run_dir(self.runs, "20261104-000000-young-a0", age=1800, work_payloads=1)
        held = run_dir(self.runs, "20261008-000000-held-a0", age=OLD, work_payloads=0,
                       marker=".owner-held")
        out = self.prune("--keep-newest", "2")
        self.assertFalse(old1.exists(), "oldest nightly dir beyond keep-newest must age out")
        self.assertTrue(old2.exists(), "newest nightly dir (under cap) is kept by keep-newest")
        self.assertTrue(old3.exists(), "second-newest nightly dir (under cap) is kept by keep-newest")
        self.assertTrue(young.exists(), "a dir inside the grace window is in-flight")
        self.assertTrue(held.exists(), "owner-held marker must never be deleted")
        self.assertIn("retention-run-age:20261001-000000-nightly-old-a0", out)

    def test_drill_receipt_then_delete(self):
        self.beads.write_text("[]")
        stamp = time.strftime("%Y%m%d", time.gmtime(time.time() - 3 * 86400))
        d = self.home / f"backup-assurance-{stamp}-seat"
        (d / "mirror-0").mkdir(parents=True)
        (d / "mirror-0" / "extracted.json").write_text('{"members": 1}')
        big = d / "mirror-0" / "blob.bin"
        with big.open("wb") as fh:
            fh.write(b"\0" * (3 * 1024 * 1024))
        (d / "results.json").write_text('{"completed": 3}')
        (d / "supplemental-complete.json").write_text('{"completed": 3}')
        (d / "deep_restore.py").write_text("pass\n")
        out = self.prune("--drill-now")
        self.assertIn(f"retention-drill:backup-assurance-{stamp}-seat", out)
        self.assertFalse(d.exists(), "drill scratch must be deleted after its receipt")
        ev = self.home / ".local" / "share" / "backup-assurance" / d.name
        self.assertTrue((ev / "results.json").exists())
        self.assertTrue((ev / "deep_restore.py").exists())
        self.assertFalse((ev / "mirror-0" / "blob.bin").exists(),
                        "the 3 MiB copy is not the evidence; the receipts are")

    def test_abandoned_drill_waits_for_ttl(self):
        self.beads.write_text("[]")
        stamp = time.strftime("%Y%m%d", time.gmtime(time.time() - 3 * 86400))
        d = self.home / f"backup-assurance-{stamp}-seat"
        d.mkdir()
        (d / "pid").write_text("123")
        out = self.prune()  # NO --drill-now: the TTL (7d) has not passed
        self.assertTrue(d.exists(), "an unfinished drill younger than TTL must not vanish")
        self.assertIn("drill-ttl", out)

    def test_cache_drill_leftovers_age_out(self):
        self.beads.write_text("[]")
        old = self.home / ".cache" / "f2-drill"
        old.mkdir(parents=True)
        (old / "dump.sqlite3").write_text("x")
        ts = time.time() - 20 * 86400
        os.utime(old, (ts, ts))
        fresh = self.home / ".cache" / "hermes-source-a9-test"
        fresh.mkdir()
        (fresh / "payload").write_text("x")
        out = self.prune()
        self.assertFalse(old.exists(), "17+-day-old drill leftovers age out")
        self.assertTrue(fresh.exists(), "young leftovers stay")
        self.assertIn("retention-cache:f2-drill", out)

    def test_age_cut_withheld_without_tracker_export(self):
        # documented fail-toward-keeping: a missing/unreadable tracker export
        # withholds WHOLE-DIR age cuts that tick, but the size cap still runs
        old_small = run_dir(self.runs, "20261001-000000-noexport-old-a0", age=OLD)
        fat = run_dir(self.runs, "20261001-000001-noexport-fat-a0", age=OLD,
                      work_payloads=2)
        out = self.prune("--beads-json", str(self.home / "missing-rows.json"))
        self.assertTrue(old_small.exists(), "age cut must be withheld without the export")
        self.assertFalse((fat / "work").exists(), "the size cap is independent of the export")
        self.assertIn("UNREADABLE", out)

    def test_receipt_line_carries_freed_bytes_schema(self):
        self.beads.write_text("[]")
        run_dir(self.runs, "20261101-000009-fat2-a0", work_payloads=2)
        self.prune()
        lines = (self.receipts / "janitor.jsonl").read_text().strip().splitlines()
        row = json.loads(lines[-1])
        for key in ("ts", "host", "fs", "used_pct", "freed_bytes", "status", "actions"):
            self.assertIn(key, row)
        self.assertEqual(row["status"], "retention")
        self.assertTrue(any(a["action"].startswith("retention-workspace-cap")
                            for a in row["actions"]))

    def test_dry_run_deletes_nothing(self):
        self.beads.write_text("[]")
        d = run_dir(self.runs, "20261101-000010-fatdry-a0", work_payloads=2)
        out = self.prune("--dry-run")
        self.assertTrue(d.exists() and (d / "work").exists(),
                        "dry run must not remove bytes")
        self.assertIn("status=dry-run", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
