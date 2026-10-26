#!/usr/bin/env python3
"""Burn-token registry generator — P1 bootstrap (NEXTGEN-CI.md (c) registry law
S3b: rows exist for every test carrying a burn token in PATH or HEADER,
grep-derived, free — NOT for every test >= 20 s).

Rows: {case, tier, burn, order_group, after}. tier=1 for every burn-named
contract test ((c) Tier-1 law: every burn-named test that can fail on this
diff runs the pr-gate). order_group null / after [] except the S1 bootstrap
teeth: test_suite_runs_root_762.py and test_fakeb1_gitpin_954r.py get
after:["ALL_OTHERS_IN_LANE"] (guard-last).

Token law (mechanical, this is the census), priority order:
  1. `est-[a-z0-9][…]` id embedded in the filename, or the first est-id in the
     header (first 40 lines);
  2. the filename's trailing `_`-segment when it contains a digit
     (…, _8, _762, _954r, _1nkx, _0923, _237r3);
  3. header tokens: `#NNN` issue cite, `sprint N`, or a bare 7..40-hex git sha.
The first hit is the row's `burn`. A test with no token anywhere gets NO row —
the registry is keyed on burn tokens, not on wall.

Regeneration is census-owned: re-run this file, review the diff, commit with
the census run cited. Usage:
  python3 scripts/registry_observe.py [--out tests/registry.json] [--check]
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEADER_LINES = 40
HEADER_TOKENS = [
    re.compile(r'est-[0-9a-z][0-9a-z._-]{1,30}'),
    re.compile(r'#\d{1,4}\b'),
    re.compile(r'sprint[\s-]?\d+\w*', re.I),
    re.compile(r'\b[0-9a-f]{7,40}\b'),
]
PATH_EMBED_EST = re.compile(r'(est-[0-9a-z][0-9a-z._-]{1,30})')
PATH_TRAIL = re.compile(r'_([0-9a-z][0-9a-z.-]*)\.py$')  # segment holds no `_`
# bootstrap ordering teeth (NEXTGEN-CI (c), S1): guard-last in whichever lane
AFTER_GUARD_LAST = {'test_suite_runs_root_762.py', 'test_fakeb1_gitpin_954r.py'}


def header_token(text):
    head = '\n'.join(text.splitlines()[:HEADER_LINES])
    for rx in HEADER_TOKENS:
        m = rx.search(head)
        if m:
            return m.group(0).rstrip('.')
    return None


def burn_for(name, text):
    """Token priority: est-id (path, then header) > digit-bearing path tail >
    header sha/issue/sprint. First hit wins; None means no row."""
    m = PATH_EMBED_EST.search(name)
    if m:
        return m.group(1)
    head = header_token(text)
    tail = PATH_TRAIL.search(name)
    tail = tail.group(1) if (tail and any(c.isdigit() for c in tail.group(1))) else None
    return head if (head or '').startswith('est-') else (tail or head)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='tests/registry.json')
    ap.add_argument('--check', action='store_true',
                    help='diff against the committed registry instead of writing')
    a = ap.parse_args()
    root = Path(a.root)

    rows = []
    for f in sorted((root / 'tests').glob('test_*.py')) + \
            sorted((root / 'tests').glob('test_*.mjs')):
        burn = burn_for(f.name, f.read_text(errors='replace'))
        if not burn:
            continue
        rows.append({'case': f.name, 'tier': 1, 'burn': burn,
                     'order_group': None,
                     'after': ['ALL_OTHERS_IN_LANE'] if f.name in AFTER_GUARD_LAST else []})
    rows.sort(key=lambda r: r['case'])

    if a.check:
        committed = json.loads((root / a.out).read_text())
        if committed != rows:
            print('registry_observe: DRIFT — committed registry != regenerated '
                  f'({len(committed)} committed vs {len(rows)} regenerated)')
            sys.exit(1)
        print(f'registry_observe: no drift ({len(rows)} rows)')
        return
    Path(a.out).write_text(json.dumps(rows, indent=2) + '\n')
    total = len(list((root / 'tests').glob('test_*.py'))) + \
        len(list((root / 'tests').glob('test_*.mjs')))
    guarded = sum(1 for r in rows if r['after'])
    print(f'registry_observe: {len(rows)} of {total} gate tests carry a burn '
          f'token -> {a.out} (guard-last rows: {guarded})')


if __name__ == '__main__':
    main()
