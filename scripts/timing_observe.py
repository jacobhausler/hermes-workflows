#!/usr/bin/env python3
"""Timing-manifest generator, OBSERVE mode (NEXTGEN-CI.md (c) manifest split,
S3a + S3 addendum; (e) P1).

Parses THIS repo's own CI log (`gh run view --log`) — the suite's printed
per-case completion lines `NAME: rc`, one per case, timestamped per shard lane
(`gates-shard (I/8)` job prefix) — and writes tests/timing.json rows of EXACTLY
{case, wall_s, timeout_s}. wall = completion-delta within the lane; the first
case of a lane absorbs suite startup, anchored at the lane's
`suite: shard I/N` header line. timeout = ceil(wall * 3) (TIERS law).

Generator law (S3 addendum — kills timeout self-inflation): the generator may
only DECREASE a weight; raising an existing case's wall_s requires
--cite-run <id>, naming a Tier-2 run whose uploaded ledger shows the new p95.
Uncited raises are clamped to the committed value and reported; the citation
belongs in the commit message, not the row (rows carry three keys and nothing
else — the hunk rule of (c)). New cases may be added at measured weight;
dropped cases are reported (deletion law: burn token in the PR body).

Observe mode: no repacking, no suite changes — this file only writes the
manifest and reports. Validation teeth: the parsed row count must equal the
`gates` job's `TOTAL n FAIL m (merged)` marker, else the parse is refused
(TIERS precedent: 339/339; run ids and counts are printed for the PR body).

Usage:
  python3 scripts/timing_observe.py [--run-id N] [--log FILE]
      [--repo owner/repo] [--workflow ci]
      [--existing tests/timing.json] [--out tests/timing.json]
      [--cite-run ID]
"""
import argparse
import datetime
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

def _derive_repo():
    """owner/repo of the `origin` remote — the generator must carry NO
    hardcoded repo handle: the publish-scrub forbids shipping one, and a
    derived default survives forks and renames (fail-closed if absent)."""
    import subprocess
    try:
        url = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                             capture_output=True, text=True, check=True,
                             cwd=Path(__file__).resolve().parent.parent
                             ).stdout.strip()
    except Exception:
        return None
    m = re.search(r'github\.com[:/](?P<r>[\w.-]+/[\w.-]+?)(?:\.git)?/?$', url)
    return m.group('r') if m else None


_REPO_DEFAULT = None
# shard lane completion line inside the gh log prefix
JOB_RE = re.compile(r'^gates-shard \((?P<i>\d+)/(?P<n>\d+)\)\t(?P<step>[^\t]*)\t'
                    r'(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.]+Z)\s(?P<msg>.*)$')
CASE_RE = re.compile(r'^(?P<case>test_[\w.+-]+\.(?:py|mjs)): (?P<rc>\d+)$')
SHARD_HDR_RE = re.compile(r'^suite: shard (?P<i>\d+)/(?P<n>\d+) ')
MERGED_RE = re.compile(r'^TOTAL (?P<total>\d+) FAIL (?P<fail>\d+) \(merged\)$')


def ts_s(text):
    return datetime.datetime.strptime(text[:26], '%Y-%m-%dT%H:%M:%S.%f').timestamp()


def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f'timing_observe: command failed {args}: {p.stderr.strip()[:400]}')
    return p.stdout


def resolve_latest_green(repo, workflow):
    out = sh(['gh', 'run', 'list', '-R', repo, '-b', 'main', '--workflow', workflow,
              '--status', 'success', '--event', 'push', '-L', '1',
              '--json', 'databaseId,headSha,conclusion'])
    row = json.loads(out)[0]
    if row.get('conclusion') != 'success':
        sys.exit('timing_observe: resolved run is not success — refusing')
    return int(row['databaseId'])


def fetch_log(repo, run_id):
    return sh(['gh', 'run', 'view', '-R', repo, '--log', str(run_id)])


def parse(text):
    """-> {case: wall_s} plus the merged TOTAL for validation."""
    per_lane_prev = {}     # lane i -> last completion ts (or lane anchor)
    walls, merged = {}, None
    for line in text.splitlines():
        m = JOB_RE.match(line)
        if not m:
            mm = MERGED_RE.match(line.split('\t')[-1].split('Z ', 1)[-1].strip())
            if mm:
                merged = int(mm.group('total'))
            continue
        ts, msg, lane = ts_s(m.group('ts')), m.group('msg').strip(), m.group('i')
        if lane not in per_lane_prev:
            per_lane_prev[lane] = None
        h = SHARD_HDR_RE.match(msg)
        if h:
            per_lane_prev[lane] = ts
            continue
        c = CASE_RE.match(msg)
        if c and per_lane_prev[lane] is not None:
            wall = ts - per_lane_prev[lane]
            per_lane_prev[lane] = ts
            walls[c.group('case')] = round(walls.get(c.group('case'), 0.0) + wall, 1)
    return walls, merged


def apply_law(parsed, existing, cite_run):
    """S3 addendum: decrease freely; raise only citing a run id; add new;
    report drops. Returns (rows, report_lines)."""
    old = {}
    if existing.exists():
        rows = json.loads(existing.read_text())
        old = {r['case']: r for r in rows}
    report, out_rows, clamped = [], [], []
    for case, wall in sorted(parsed.items()):
        tmo = math.ceil(wall * 3)
        if case in old:
            ow, ot = float(old[case]['wall_s']), int(old[case]['timeout_s'])
            if wall > ow and not cite_run:
                out_rows.append({'case': case, 'wall_s': ow, 'timeout_s': ot})
                clamped.append(f'{case}: parsed {wall} > committed {ow}')
                continue
            if wall > ow:
                report.append(f'RAISE cited run={cite_run}: {case} {ow} -> {wall}')
        out_rows.append({'case': case, 'wall_s': wall, 'timeout_s': tmo})
    for case in sorted(set(old) - set(parsed)):
        report.append(f'DROP (not in this run — deletion law applies to burn-named '
                      f'rows: token in PR body): {case}')
    if clamped:
        report.append(f'RAISE-CLAMPED {len(clamped)} row(s) (generator may only '
                      f'decrease; raise needs --cite-run <Tier-2 run id>, '
                      f'citation goes in the commit message):')
        report.extend('  ' + c for c in clamped)
    return out_rows, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', type=int)
    ap.add_argument('--log')
    ap.add_argument('--repo', default=_derive_repo(),
                    help='owner/repo (default: git origin remote)')
    ap.add_argument('--workflow', default='ci')
    ap.add_argument('--existing', default='tests/timing.json')
    ap.add_argument('--out', default='tests/timing.json')
    ap.add_argument('--cite-run')
    a = ap.parse_args()

    run_id = a.run_id
    if a.log:
        text = Path(a.log).read_text()
    else:
        if run_id is None:
            run_id = resolve_latest_green(a.repo, a.workflow)
        text = fetch_log(a.repo, run_id)
    if run_id is None:
        run_id = -1  # log came from file; no run id to echo

    walls, merged = parse(text)
    if not walls:
        sys.exit('timing_observe: parsed zero cases — wrong log shape?')
    if merged is None:
        sys.exit('timing_observe: no `TOTAL n FAIL m (merged)` marker found — '
                 'refusing a partial manifest')
    if merged != len(walls):
        sys.exit(f'timing_observe: parse coverage {len(walls)} != merged TOTAL '
                 f'{merged} — refusing')

    rows, report = apply_law(walls, Path(a.existing), a.cite_run)
    Path(a.out).write_text(json.dumps(rows, indent=2) + '\n')
    total = sum(r['wall_s'] for r in rows)
    print(f'timing_observe: run={run_id} rows={len(rows)} TOTAL-marker={merged} '
          f'(100% parsed) sum_wall={total:.1f}s -> {a.out}')
    cap = 150
    print(f'timing_observe: at lane_cap_s={cap} the contract would compute '
          f'shards=ceil({total:.1f}/{cap})={math.ceil(total / cap)} (observe only, '
          f'no repack)')
    for line in report:
        print('timing_observe:', line)
    print(f'timing_observe: cite this run id in the commit/PR body: '
          f'{"" if run_id < 0 else f"https://github.com/{a.repo}/actions/runs/{run_id}"}')


if __name__ == '__main__':
    main()
