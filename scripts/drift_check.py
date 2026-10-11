#!/usr/bin/env python3
"""On-demand, offline checkout drift probe; never fetches or starts a daemon."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wfcommon import drift_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT,
                        help='checkout to scan (default: script parent)')
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code != 2:  # --help retains argparse's normal exit/output.
            raise
        report = dict(installed_version='unknown', upstream_latest='unknown',
                      local_only_commits=None, trailers_missing=None, verdict='error')
    else:
        report = drift_report(args.repo)
    if report.get('error'):
        print(report['error'], file=sys.stderr)
    fields = ('installed_version', 'upstream_latest', 'local_only_commits',
              'trailers_missing', 'verdict')
    print(' '.join(f'{key}={report[key] if report[key] is not None else "unknown"}'
                   for key in fields))
    return 2 if report['verdict'] == 'error' else int(report['verdict'] != 'clean')


if __name__ == '__main__':
    raise SystemExit(main())
