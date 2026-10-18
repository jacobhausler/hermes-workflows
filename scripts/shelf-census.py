#!/usr/bin/env python3
"""shelf-census.py — committed on-demand shelf census (launch attribution,
deadweight rows, cell-consumer scan). Stdlib-only; never a monitor (launch
counts change bytes and would wake an agent on every launch).

Second-real-census re-admission of the W1-13 census tool (SH-07): absorbs the
one-off scan scripts banked as fixtures at
library-archive/fixtures/wof-census-20261016/oneoffs/ — runcensus.py (root
enumeration + realpath dedupe + envelope meta read), match2.py (run-to-row
launch attribution; the node-id law below is its sharpened form), and the
row-name reference grep (widenet lane pattern + SH-04's zero-ref clause),
plus the run-1 mention-scan phase folded into the consumer-vs-mention law
below. NOT absorbed (kept as fixtures): libcalls.py (state.db `from:`
archaeology — obsoleted by FB-D3 launch receipts), widenet_check.py /
widenet_paths.py (door-shape and ghost-path audits — orthogonal to census).

Census law (lifecycle-governor re-measure notes):
  - run roots are deduped by realpath + (st_dev, st_ino) — mirrored/symlinked
    run roots counted twice inflate every launch number.
  - three named root sets: live/ + archive/ + quarantine (absent roots report 0,
    never crash).
  - attribution per row: exact-name (run.json name == row), prefix (name == row
    or name startswith row+'-'), node-id (run graph node-id set == row node-id
    set — catches hand-rebuilt runs whose title differs).
  - envelope-aware node counts (the {meta, graph} envelope form counts the
    inner graph's nodes — the FB-D1 under-read fix).
  - consumer scan: live rows referencing archived cell rows (measured consumers
    > 0 is the SH-03 revival trigger).

--out defaults to <HERMES_HOME>/work/shelf-census/latest.json and is a LOCAL
artifact. It is explicitly NOT a cross-seat truth registry: each seat re-runs
this committed tool and diffs the outputs (SH-04 law).

Exit codes: 0 ok; 1 when a row is NEW deadweight (zero launches, zero refs,
not kind:draft) relative to a previously stored census; 2 usage/store missing.
"""
import argparse
import json
import os
import sys
import time

def _hermes_home_default():
    h = os.environ.get("HERMES_HOME")
    if h:
        return h
    return os.path.join(os.path.expanduser("~"), ".hermes")


HERMES_HOME_DEFAULT = _hermes_home_default()
WF_ROOT_DEFAULT = os.path.join(HERMES_HOME_DEFAULT, "workflows")
OUT_DEFAULT = os.path.join(HERMES_HOME_DEFAULT, "work", "shelf-census", "latest.json")

CELLS_20261016 = [  # archived cell rows (library-archive/cells-<census-id>/, fixture F1-03)
]


def load_row(path):
    """Return (name, node_ids, kind_tags, meta) for a shelf row in either form."""
    try:
        with open(path) as fh:
            d = json.load(fh)
    except Exception:
        return None
    if isinstance(d, dict) and isinstance(d.get("graph"), dict):  # envelope form
        g, meta = d["graph"], d.get("meta") or {}
        name = meta.get("name") or g.get("name") or os.path.basename(path)[:-5]
        nodes = [n.get("id") for n in g.get("nodes", []) if isinstance(n, dict)]
        tags = meta.get("tags") or []
        return name, nodes, tags, meta
    if isinstance(d, dict) and "name" in d:  # bare form
        nodes = [n.get("id") for n in d.get("nodes", []) if isinstance(n, dict)]
        return d["name"], nodes, d.get("tags") or [], None
    return None


def row_files(directory):
    out = {}
    if not os.path.isdir(directory):
        return out
    for fn in sorted(os.listdir(directory)):
        if fn.endswith(".json"):
            r = load_row(os.path.join(directory, fn))
            if r:
                out[fn[:-5]] = r
    return out


def root_id(path):
    st = os.stat(path)
    return (os.path.realpath(path), st.st_dev, st.st_ino)


def run_dirs(roots):
    """Yield (dirpath, name_mtime) for every run dir (one holding run.json) under
    the given workflow roots, deduped by realpath+(dev,ino)."""
    seen_roots, seen_dirs, out = set(), set(), []
    for root in roots:
        if not os.path.isdir(root) or root_id(root) in seen_roots:
            continue
        seen_roots.add(root_id(root))
        for entry in sorted(os.listdir(root)):
            d = os.path.join(root, entry)
            if not os.path.isdir(d):
                continue
            try:
                rid = root_id(d)
            except OSError:
                continue
            if rid in seen_dirs or entry in ("library", "library-archive"):
                continue
            seen_dirs.add(rid)
            if os.path.exists(os.path.join(d, "run.json")):
                out.append(d)
    return out


def run_record(d):
    rec = {"dir": d, "name": None, "node_ids": None, "ts": None}
    try:
        with open(os.path.join(d, "run.json")) as fh:
            rec["name"] = (json.load(fh) or {}).get("name")
    except Exception:
        pass
    try:
        with open(os.path.join(d, "graph.json")) as fh:
            g = json.load(fh) or {}
        rec["node_ids"] = frozenset(
            n.get("id") for n in g.get("nodes", []) if isinstance(n, dict))
    except Exception:
        pass
    base = os.path.basename(d)
    rec["ts"] = base.split("-" + base.split("-")[-1])[0] if "-" in base else None
    try:
        rec["mtime"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.path.getmtime(os.path.join(d, "run.json"))))
    except OSError:
        rec["mtime"] = None
    return rec


def grep_refs(term, roots):
    """Count files containing `term` under grep roots (skills/scripts/cron).
    LIVE-REF LAW: transcript dirs (cron output, bot_chat_pending, logs, state)
    are historical echoes, not demand — a row mentioned in yesterday's cron
    output is not referenced by anything."""
    hits = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [x for x in dirnames if x not in (
                ".git", "node_modules", "work", "cache", "scratch",
                "output", "bot_chat_pending", "logs", "state", "wake_ledger")]
            for fn in filenames:
                if not fn.endswith((".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt")):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(p) > 400_000:
                        continue
                    with open(p, "rb") as fh:
                        if term.encode("utf-8", "ignore") in fh.read():
                            hits.append(p)
                except OSError:
                    continue
    return hits


def main():
    ap = argparse.ArgumentParser(description="WOF shelf census (SH-07; local artifact, not a registry)")
    ap.add_argument("--wf-root", default=WF_ROOT_DEFAULT, help="workflows root (library/ + run dirs)")
    ap.add_argument("--hermes-home", default=HERMES_HOME_DEFAULT)
    ap.add_argument("--extra-run-root", action="append", default=[],
                    help="additional run root (deduped by realpath+dev+ino)")
    ap.add_argument("--quarantine", action="append", default=[],
                    help="quarantine dir(s) to census (absent = 0)")
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--no-refs", action="store_true", help="skip the grep-ref scan (fast mode)")
    a = ap.parse_args()

    live_dir = os.path.join(a.wf_root, "library")
    arch_dir = os.path.join(a.wf_root, "library-archive")
    live, archive = row_files(live_dir), row_files(arch_dir)
    # archived rows incl. nested retire dirs (cells-20261016/, one dirs committed flat)
    if os.path.isdir(arch_dir):
        for sub in sorted(os.listdir(arch_dir)):
            p = os.path.join(arch_dir, sub)
            if os.path.isdir(p) and not sub.startswith(("fixtures", ".")):
                for k, v in row_files(p).items():
                    archive.setdefault(k, v)

    run_roots = [a.wf_root] + list(a.extra_run_root)
    prof = os.path.join(a.hermes_home, "profiles")
    if os.path.isdir(prof):
        for seat in sorted(os.listdir(prof)):
            w = os.path.join(prof, seat, "workflows")
            if os.path.isdir(w):
                run_roots.append(w)
    runs = [run_record(d) for d in run_dirs(run_roots)]

    quar = {}
    for q in a.quarantine:
        quar[q] = len(row_files(q)) if os.path.isdir(q) else 0

    grep_roots = [os.path.join(a.hermes_home, "scripts"),
                  os.path.join(a.hermes_home, "skills")]
    prof2 = os.path.join(a.hermes_home, "profiles")
    if os.path.isdir(prof2):
        for seat in sorted(os.listdir(prof2)):
            for sub in ("scripts", "cron", "skills"):
                p = os.path.join(prof2, seat, sub)
                if os.path.isdir(p):
                    grep_roots.append(p)

    archived_names = sorted(set(archive) - {k for k in archive if k in live})
    # CONSUMER LAW: a consumer is a live reference in CONSUMPTION syntax —
    # `from:<row>` (the door-launch form). Bare name mentions are provenance
    # prose (fold receipts name their retired rows) and are counted separately,
    # never as demand. Measured consumers > 0 is the SH-03 revival trigger.
    consumer_hits, mention_hits = {}, {}
    texts = {}
    for name in live:
        try:
            with open(os.path.join(live_dir, name + ".json")) as fh:
                texts[name] = fh.read()
        except OSError:
            pass
    for cell in archived_names:
        for name, body in texts.items():
            if "from:" + cell in body:
                consumer_hits.setdefault(cell, []).append(name)
            elif cell in body:
                mention_hits.setdefault(cell, []).append(name)
    consumers = sum(len(v) for v in consumer_hits.values())

    rows = {}
    for name, (rname, node_ids, tags, meta) in live.items():
        exact = [r for r in runs if r["name"] == name]
        prefix = [r for r in runs if r["name"] and r["name"] != name and r["name"].startswith(name + "-")]
        nodeid = [r for r in runs if r["node_ids"] and len(node_ids) >= 2
                  and r["node_ids"] == frozenset(node_ids)
                  and r not in exact and r not in prefix]
        # NODE-ID LAW: a row's node-id set attributes a hand-rebuilt run ONLY if
        # the set is distinctive (>=2 nodes). Single-node rows ('review' alone)
        # are a grammar dialect, not a fingerprint — measured: pr-review-xbot
        # false-matched 9 ra-pr light runs under the loose rule.
        launched = exact + prefix + nodeid
        last = max((r["mtime"] or r["ts"] or "" for r in launched), default=None)
        refs = []
        if not a.no_refs:
            refs = grep_refs(name, grep_roots)
        kind_draft = "kind:draft" in (tags or []) or (meta or {}).get("kind") == "draft"
        rows[name] = {
            "nodes": len(node_ids),
            "envelope": meta is not None,
            "launches": {"exact": len(exact), "prefix": len(prefix), "node_id": len(nodeid),
                         "total": len(launched)},
            "last_run": last,
            "refs": len(refs),
            "ref_files": refs[:8],
            "kind_draft": kind_draft,
            "deadweight": len(launched) == 0 and len(refs) == 0 and not kind_draft,
        }

    prior = {}
    if os.path.exists(a.out):
        try:
            with open(a.out) as fh:
                prior = {k: v for k, v in (json.load(fh).get("rows") or {}).items()}
        except Exception:
            prior = {}
    new_dead = sorted(k for k, v in rows.items() if v["deadweight"]
                      and not (prior.get(k) or {}).get("deadweight"))

    result = {
        "tool": "shelf-census.py",
        "spec": "wof-census-20261016 Gate A (lifecycle-governor/rt-exec W1-13)",
        "seat": os.uname().nodename,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "out_is": "local artifact — NOT a cross-seat truth registry (rt-min K2)",
        "rows_live": len(live),
        "rows_archive": len(archive),
        "quarantine": quar,
        "row_delta_note": "compare rows_live against prior census at this --out path",
        "consumers": consumers,
        "consumer_hits": {k: v for k, v in sorted(consumer_hits.items())},
        "provenance_mentions": {k: v for k, v in sorted(mention_hits.items())},
        "rows": rows,
        "deadweight": sorted(k for k, v in rows.items() if v["deadweight"]),
        "new_deadweight": new_dead,
    }

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print(json.dumps({k: result[k] for k in
                      ("rows_live", "rows_archive", "consumers",
                       "deadweight", "new_deadweight")}, indent=1))
    print("written:", a.out)
    if new_dead:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()