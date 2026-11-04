#!/usr/bin/env python3
"""retention.py — run-dir + drill-scratch retention with a SIZE CAP first-class.

Why (the measured failure): age-only cleanup cannot bound a seat's disk, because
the mass is not where the age is. On the seat that started this, the whole
set of run dirs older than 14 days was ~4.5 GiB, while a SINGLE nightly attempt
dir carried ~19.5 GiB of extracted backup payloads — and it was one week old.
The bound must therefore be a per-run size cap, with the age cut as the second
blade, not the first.

Rule (three classes, all fail-closed toward keeping bytes):
  A. WORKSPACE / VALIDATION-COPIES (size cap): a terminal run dir whose total
     size exceeds the cap loses its workspace subtree and payload files
     (*.tar*, *.sqlite*, *-wal/-shm, any `backup/` subtree) once it is older
     than the post-terminal grace; the small transcript/package files at the
     run-dir root are kept forever. A retry that re-takes the runner lock is
     protected by the grace window.
  B. WHOLE RUN DIR (age cut): at AGE_DAYS, the whole dir goes (transcripts and
     all) — UNLESS protected. Age anchor is the newest of the package files
     (run.json / graph.json / runner_exit.json / events.jsonl /
     spawn-ledger.jsonl), never the dir mtime: a payload prune refreshes the
     dir and must not reset the clock.
  C. DRILL SCRATCH: dated scratch dirs (name-carried YYYYMMDD, else mtime) are
     EVIDENCE-FIRST: the small evidence files (json/jsonl/log/py/txt/md, capped)
     are copied to the receipt store BEFORE the copy trees are deleted. A drill
     that finished cleanly may be closed immediately (`--drill-now`, the
     receipt-then-delete step the drill itself calls at the end of its run);
     an abandoned one only after the TTL. Cache drill leftovers age out.

PROTECTION (never-delete law): a run dir is skipped, whole, when its name is
referenced by an UNCLOSED tracker row (the `list --json` export of every
not-closed row, given via --beads-json), by any file under the nightly
receipt roots, by an explicit --protect NAME, or by a .owner-held / OWNER_HELD
marker inside it. A live run is
skipped (fresh package-file mtime inside the grace). The newest KEEP_NEWEST
nightly-named dirs stay whole while under the cap — an over-cap attempt is
pruned by rule A even when it is among the newest two, because that is exactly
the size the rule exists to bound.

Receipt: one JSONL line appended to the disk-janitor receipt file (--receipt-
file, the SAME schema the janitor census already tails: {ts,host,fs,used_pct,
freed_bytes,status,actions:[{action,bytes,out}]}), so a prune run reports its
freed bytes on the existing rails instead of a second status surface; the full
per-skip detail goes to --report-dir/retention-report.jsonl. Freed bytes are
measured by filesystem-availability deltas (APFS clones share blocks; sums of
st_blocks would lie).

Stdlib-only. Env overrides (documented defaults): WF_RETENTION_CAP_BYTES,
WF_RETENTION_PAYLOAD_HOURS, WF_RETENTION_AGE_DAYS, WF_RETENTION_KEEP_NEWEST,
WF_RETENTION_DRILL_TTL_DAYS, WF_RETENTION_CACHE_AGE_DAYS,
WF_RETENTION_REPORT_DIR, WF_RUNS_ROOT, WF_RECEIPT_DIR.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

GIB = 1024 ** 3
PACKAGE_FILES = ("run.json", "graph.json", "runner_exit.json", "events.jsonl",
                 "spawn-ledger.jsonl", "run_state.json")
PAYLOAD_PATTERNS = (".tar", ".tar.gz", ".tgz", ".gz", ".sqlite", ".sqlite3",
                    "-wal", ".db", ".zip")
PAYLOAD_DIRS = ("backup",)
EVIDENCE_SUFFIXES = (".json", ".jsonl", ".log", ".py", ".txt", ".md", ".pub",
                    ".sh", ".out")
NIGHTLY_RE = re.compile(r"nightly[-_\d]")
DATE_IN_NAME_RE = re.compile(r"(20\d{6})")


def env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def iso_now():
    return now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def avail_bytes(fs_path):
    st = os.statvfs(str(fs_path))
    return st.f_bavail * st.f_frsize


def used_pct(fs_path):
    st = os.statvfs(str(fs_path))
    total = (st.f_blocks - st.f_bfree) + st.f_bavail
    return round(100.0 * (total - st.f_bavail) / total, 2) if total else 0.0


def tree_bytes(path):
    """Rough size for CAP decisions only; freed bytes are always the df delta."""
    total = 0
    stack = [path]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        if e.is_symlink():
                            continue
                        if e.is_dir(follow_symlinks=False):
                            stack.append(e.path)
                        else:
                            total += e.stat(follow_symlinks=False).st_blocks * 512
                    except OSError:
                        pass
        except OSError:
            pass
    return total


def newest_mtime(d):
    newest = 0.0
    for name in PACKAGE_FILES:
        try:
            m = (d / name).stat().st_mtime
            newest = max(newest, m)
        except OSError:
            pass
    if newest == 0.0:
        try:
            newest = d.stat().st_mtime
        except OSError:
            return 0.0
    return newest


def run_dirs(root):
    seen, out = set(), []
    if not root.is_dir():
        return out
    for e in os.scandir(root):
        if not e.is_dir(follow_symlinks=False) or e.name.startswith("."):
            continue
        if not (Path(e.path) / "graph.json").exists():
            continue
        st = e.stat(follow_symlinks=False)
        key = (st.st_dev, st.st_ino)
        if key in seen:
            continue
        seen.add(key)
        out.append(Path(e.path))
    return out


def load_protected(args, roots_text=()):
    """Run-dir names referenced by open tracker rows, nightly receipts, pins."""
    names, sources = set(), {}
    blob = []
    if args.beads_json and args.beads_json != "-":
        try:
            blob.append(Path(args.beads_json).read_text(encoding="utf-8",
                                                        errors="replace"))
            sources["tracker"] = "export-read"
        except OSError:
            sources["tracker"] = "UNREADABLE"
    else:
        sources["tracker"] = "absent"
    for root in args.receipt_root:
        p = Path(root)
        if not p.is_dir() and not p.is_file():
            continue
        files = [p] if p.is_file() else [
            f for f in p.rglob("*") if f.is_file()
            and f.suffix in (".json", ".jsonl", ".log", ".txt")
            and f.stat().st_mtime > time.time() - args.receipt_scan_days * 86400]
        for f in files:
            try:
                blob.append(f.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                pass
        sources["receipts"] = "scanned"
    if args.protect:
        names.update(args.protect)
        sources["pins"] = ",".join(args.protect)
    text = "\n".join(blob)
    return text, names, sources


def match_payload_files(d):
    hits = []
    stack = [d]
    while stack:
        cur = stack.pop()
        try:
            it = list(os.scandir(cur))
        except OSError:
            continue
        for e in it:
            try:
                if e.is_dir(follow_symlinks=False):
                    if e.name in PAYLOAD_DIRS:
                        hits.append(Path(e.path))
                    else:
                        stack.append(e.path)
                elif e.is_file(follow_symlinks=False):
                    low = e.name.lower()
                    if any(low.endswith(p) or p in low for p in PAYLOAD_PATTERNS
                           if p.startswith(".") or p.startswith("-")):
                        hits.append(Path(e.path))
                    elif low.endswith((".tar", ".tgz")):
                        hits.append(Path(e.path))
            except OSError:
                pass
    return hits


def prune(args):
    home = Path(os.path.expanduser(args.home))
    roots = [Path(r) for r in args.runs_root]
    if not roots and getattr(args, "runs_root_default", ""):
        roots = [Path(args.runs_root_default)]
    roots = [r for r in roots if r.is_dir()]
    if not roots:
        print("retention: no runs root exists — nothing to do")
        return 0
    fs_probe = Path(args.fs) if args.fs else (roots[0] if roots else home)
    protected_text, pinned, sources = load_protected(args)
    tracker_ok = sources.get("tracker") == "export-read"
    actions, skipped = [], {}
    a0 = avail_bytes(fs_probe)
    freed = 0
    report_rows = []

    def record(action, nbytes, outcome):
        nonlocal freed
        freed += max(nbytes, 0)
        actions.append({"action": action, "bytes": max(nbytes, 0), "out": outcome})

    def remove(path, action):
        before = avail_bytes(fs_probe)
        try:
            shutil.rmtree(path)
        except OSError as exc:
            record(action, 0, f"error:{exc.strerror}")
            return False
        record(action, avail_bytes(fs_probe) - before, "removed")
        return True

    all_dirs = [d for r in roots for d in run_dirs(r)]
    # nightly keep-newest (under cap only — the cap rule outranks it)
    nightly = sorted((d for d in all_dirs if NIGHTLY_RE.search(d.name)),
                     key=newest_mtime, reverse=True)

    def protected_reason(d):
        if (d / ".owner-held").exists() or (d / "OWNER_HELD").exists():
            return "owner-held-marker"
        if d.name in pinned:
            return "pin"
        if re.search(re.escape(d.name), protected_text):
            return "reference(open-rows|nightly-receipts)"
        age_h = (time.time() - newest_mtime(d)) / 3600.0
        if age_h < args.payload_after_hours:
            return "in-grace"
        return None

    keep_newest = {d.name for d in nightly[:args.keep_newest]}
    for d in all_dirs:
        reason = protected_reason(d)
        if reason:
            skipped[d.name] = reason
            continue
        anchor = newest_mtime(d)
        age_days = (time.time() - anchor) / 86400.0
        size = tree_bytes(d)
        whole_hit = (anchor > 0 and age_days >= args.age_days)
        if whole_hit and not tracker_ok:
            skipped[d.name] = "no-tracker-export(age-cut-withheld)"
            whole_hit = False
        cap_hit = (size > args.cap_bytes and
                   (d / "runner_exit.json").exists())
        if whole_hit and not (d.name in keep_newest and size <= args.cap_bytes):
            if not args.dry_run:
                est = remove(d, f"retention-run-age:{d.name}")
            else:
                record(f"retention-run-age:{d.name}", size, "dry")
            continue
        if cap_hit:
            work = d / "work"
            freed_here = 0
            if work.is_dir():
                b = avail_bytes(fs_probe)
                if not args.dry_run:
                    shutil.rmtree(work)
                    freed_here += max(avail_bytes(fs_probe) - b, 0)
                else:
                    freed_here = tree_bytes(work)
            leftover = tree_bytes(d)
            if leftover > args.cap_bytes:
                for f in match_payload_files(d):
                    if not f.exists():
                        continue
                    b = avail_bytes(fs_probe)
                    if not args.dry_run:
                        shutil.rmtree(f) if f.is_dir() else f.unlink()
                        freed_here += max(avail_bytes(fs_probe) - b, 0)
                    else:
                        freed_here += tree_bytes(f)
            record(f"retention-workspace-cap:{d.name}", freed_here,
                   "dry" if args.dry_run else "work+payloads")
            continue
        skipped.setdefault(d.name, f"under-cap-age({size // (1024*1024)}MiB,{round(age_days)}d)")

    # class C — drill scratch under $HOME
    drill_roots = [home]
    for base in drill_roots:
        try:
            entries = [Path(p) for p in base.glob("backup-assurance-*")
                       if Path(p).is_dir()]
        except OSError:
            entries = []
        for d in entries:
            m = DATE_IN_NAME_RE.search(d.name)
            if m:
                try:
                    created = dt.datetime.strptime(m.group(1), "%Y%m%d").replace(
                        tzinfo=dt.timezone.utc)
                    age_days = (now_utc() - created).total_seconds() / 86400.0
                except ValueError:
                    age_days = (time.time() - d.stat().st_mtime) / 86400.0
            else:
                age_days = (time.time() - d.stat().st_mtime) / 86400.0
            complete = any((d / f).exists() for f in
                           ("supplemental-complete.json", "complete.json",
                            "results.json", "receipt.json"))
            if not (args.drill_now and complete) and age_days < args.drill_ttl_days:
                skipped[d.name] = f"drill-ttl({round(age_days)}d<{args.drill_ttl_days}d)"
                continue
            ev_dir = Path(args.receipt_root_drill) / d.name
            b = avail_bytes(fs_probe)
            copied = 0
            try:
                ev_dir.mkdir(parents=True, exist_ok=True)
                budget = args.receipt_max_bytes
                for f in sorted(d.rglob("*")):
                    if f.is_file() and f.suffix in EVIDENCE_SUFFIXES:
                        try:
                            sz = f.stat().st_size
                        except OSError:
                            continue
                        if sz > budget:
                            continue
                        dst = ev_dir / f.relative_to(d)
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dst)
                        budget -= sz
                        copied += sz
            except OSError as exc:
                record(f"retention-drill:{d.name}", 0, f"receipt-copy-failed:{exc.strerror}")
                continue
            if args.dry_run:
                record(f"retention-drill:{d.name}", tree_bytes(d), "dry")
                continue
            shutil.rmtree(d)
            record(f"retention-drill:{d.name}", avail_bytes(fs_probe) - b,
                   f"receipt-then-delete({copied}B to {ev_dir})")

    # class C — drill leftovers under the cache dir
    cache = home / ".cache"
    for pat in args.cache_patterns.split(","):
        pat = pat.strip()
        if not pat:
            continue
        for d in sorted(cache.glob(pat)):
            if not d.is_dir():
                continue
            age_days = (time.time() - d.stat().st_mtime) / 86400.0
            if age_days < args.cache_age_days:
                skipped[d.name] = f"cache-ttl({round(age_days)}d<{args.cache_age_days}d)"
                continue
            b = avail_bytes(fs_probe)
            if args.dry_run:
                record(f"retention-cache:{d.name}", tree_bytes(d), "dry")
                continue
            shutil.rmtree(d)
            record(f"retention-cache:{d.name}", avail_bytes(fs_probe) - b, "removed")

    freed_total = avail_bytes(fs_probe) - a0
    if freed_total < 0:
        freed_total = 0   # concurrent writers on a shared volume may outrun the
                          # prune between the two reads; per-action bytes carry the truth
    status = "dry-run" if args.dry_run else "retention"
    line = {"ts": iso_now(), "host": socket.gethostname().split(".")[0],
            "fs": str(fs_probe), "used_pct": used_pct(fs_probe),
            "freed_bytes": freed_total, "status": status, "actions": actions}
    rdir = args.report_dir or (str(Path(args.receipt_file).parent)
                               if args.receipt_file else "")
    if rdir:
        report_dir = Path(rdir)
        report_dir.mkdir(parents=True, exist_ok=True)
        rpt = report_dir / "retention-report.jsonl"
    else:
        rpt = None
    with rpt.open("a") as fh:
        fh.write(json.dumps({**line, "skipped": skipped,
                             "skip_count": len(skipped),
                             "protection_sources": sources}) + "\n")
    if not args.dry_run and args.receipt_file:
        with Path(args.receipt_file).open("a") as fh:
            fh.write(json.dumps(line) + "\n")
    sample = "; ".join(f"{k}:{v}" for k, v in sorted(skipped.items())[:6])
    print(f"retention: status={status} freed_bytes={freed_total} actions={len(actions)} "
          f"skipped={len(skipped)} [{sample}] protection={sources} report={rpt}")
    for a in actions:
        print(f"  {a['action']} bytes={a['bytes']} out={a['out']}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="retention.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prune", help="apply the retention rule")
    p.add_argument("--runs-root", action="append", default=[],
                   help="run root (default $WF_RUNS_ROOT or ~/.hermes/workflows)")
    p.add_argument("--home", default=os.environ.get("HOME") or str(Path.home()))
    p.add_argument("--fs", default="", help="filesystem for freed-bytes deltas (default runs root)")
    p.add_argument("--beads-json", default="",
                   help="JSON export of OPEN tracker rows ('list --status open --json')")
    p.add_argument("--receipt-root", action="append", default=[],
                   help="file or dir whose text names protected run dirs")
    p.add_argument("--receipt-scan-days", type=int, default=90)
    p.add_argument("--protect", action="append", default=[],
                   help="explicit run-dir name pin")
    p.add_argument("--cap-bytes", type=int, default=env_int("WF_RETENTION_CAP_BYTES", 4 * GIB))
    p.add_argument("--payload-after-hours", type=int, default=env_int("WF_RETENTION_PAYLOAD_HOURS", 48))
    p.add_argument("--age-days", type=int, default=env_int("WF_RETENTION_AGE_DAYS", 14))
    p.add_argument("--keep-newest", type=int, default=env_int("WF_RETENTION_KEEP_NEWEST", 2))
    p.add_argument("--drill-ttl-days", type=int, default=env_int("WF_RETENTION_DRILL_TTL_DAYS", 7))
    p.add_argument("--drill-now", action="store_true",
                   help="close a completed drill immediately (receipt-then-delete)")
    p.add_argument("--cache-age-days", type=int, default=env_int("WF_RETENTION_CACHE_AGE_DAYS", 14))
    p.add_argument("--cache-patterns", default=os.environ.get(
        "WF_RETENTION_CACHE_PATTERNS",
        "f2-drill,hermes-source-*,*-hermes-*-a*,*drill*"))
    p.add_argument("--receipt-root-drill",
                   default=os.path.expanduser("~/.local/share/backup-assurance"))
    p.add_argument("--receipt-max-bytes", type=int, default=64 * 1024 * 1024)
    p.add_argument("--report-dir",
                   default=os.environ.get("WF_RETENTION_REPORT_DIR", ""))
    p.add_argument("--receipt-file",
                   default=os.environ.get("WF_JANITOR_RECEIPT", ""))
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=prune)
    p.add_argument("--runs-root-default-off", action="store_true",
                   help="do not default the runs root to ~/.hermes/workflows")
    args = ap.parse_args(argv)
    if getattr(args, "runs_root_default_off", False) and not args.runs_root:
        args.runs_root_default = ""
    else:
        args.runs_root_default = os.environ.get("WF_RUNS_ROOT") or str(
            Path(args.home) / ".hermes" / "workflows")
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
