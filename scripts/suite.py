#!/usr/bin/env python3
"""Serial bounded suite with durable per-case logs and atomic exit ledger.

The ledger resets per run: exits.json reports the CURRENT pass only.

Pass-gate admission contract (#17): with --baseline <exits.json> (a prior run's
ledger, e.g. the clean base SHA), the run additionally writes admission.json
next to exits.json carrying the EXACT red identities (test name + exit code)
split into introduced vs pre-existing, plus fixed reds. The gate never waives
anything: only a fully-green integrated SHA (zero reds, base or fix) is green
and exits 0; pre-existing reds land in blocking_base_reds for a linked fix
item, never hand-carried. Without --baseline every red is reported as
introduced (there is no evidence it pre-existed).
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def load_baseline(path):
    """Read a prior ledger into {test: exit}. Contract is exact identities, so
    an unreadable/malformed baseline is a hard error (exit 2), never a silent
    fallback that could launder an introduced red as pre-existing."""
    try:
        rows = json.loads(Path(path).read_text())
        if not isinstance(rows, list):
            raise ValueError('ledger is not a list')
        for row in rows:
            if not isinstance(row, dict) or 'test' not in row or 'exit' not in row:
                raise ValueError(f'ledger row missing test/exit: {row!r}')
        return {row['test']: int(row['exit']) for row in rows}
    except Exception as exc:
        print(f'suite: baseline ledger unusable ({path}): {type(exc).__name__}: {exc}',
              flush=True)
        raise SystemExit(2)


def admission(base_reds, reds):
    """Diff red identities base vs fix. An identity match requires BOTH the
    test name and the exit code: the same test dying differently (1 vs 124) is
    a different failure and counts as introduced."""
    base = dict(base_reds) if base_reds is not None else {}
    introduced = sorted(n for n, rc in reds.items() if base.get(n) != rc)
    pre_existing = sorted(n for n, rc in reds.items() if base.get(n) == rc)
    fixed = sorted(n for n, rc in base.items() if n not in reds and rc != 0)
    return {
        'baseline': None if base_reds is None else str(_baseline_path),
        'base_reds': dict(sorted(base.items())),
        'reds': dict(sorted(reds.items())),
        'introduced': introduced,
        'pre_existing': pre_existing,
        'blocking_base_reds': pre_existing,  # never waived: each needs its own fix item
        'fixed': fixed,
        'green': not reds,  # fully-green integrated SHA only
    }


def parse_args(argv):
    root = Path(argv[1]).resolve()
    out = Path(argv[2]).resolve()
    baseline = None
    rest = argv[3:]
    i = 0
    while i < len(rest):
        if rest[i] == '--baseline':
            if i + 1 >= len(rest):
                print('suite: --baseline needs a path to an exits.json ledger', flush=True)
                raise SystemExit(2)
            baseline = Path(rest[i + 1]).resolve()
            i += 2
        else:
            print(f'suite: unknown argument {rest[i]!r}', flush=True)
            raise SystemExit(2)
    return root, out, baseline


root, out, _baseline_path = parse_args(sys.argv)
base_reds = load_baseline(_baseline_path) if _baseline_path else None
out.mkdir(parents=True, exist_ok=True)
ledger = out / 'exits.json'
# fb 3d2175e9cd75d2a1: a suite run reports the CURRENT pass only — reset the
# ledger at start instead of appending to a stale dir's rows. Durability is
# kept: the per-case atomic tmp+os.replace write below persists progress.
rows = []
tmp = ledger.with_suffix('.tmp')
tmp.write_text('[]\n')
os.replace(tmp, ledger)
py = sorted((root / 'tests').glob('test_*.py'))
js = sorted((root / 'tests').glob('test_*.mjs'))
cases = [[sys.executable, str(p)] for p in py] + [['node', '--experimental-strip-types', str(p)] for p in js]
for argv in cases:
    name = Path(argv[-1]).name
    log = out / (name + '.log')
    try:
        with log.open('w') as fh:
            result = subprocess.run(argv, cwd=root, env={**os.environ, 'HERMES_HOME': str(root / 'tests' / '.suite-home')},
                                    stdout=fh, stderr=subprocess.STDOUT, timeout=90)
        rc = result.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    except Exception as exc:
        log.write_text(f'{type(exc).__name__}: {exc}\n')
        rc = 125
    rows.append({'test': name, 'exit': rc, 'log': str(log)})
    tmp = ledger.with_suffix('.tmp')
    tmp.write_text(json.dumps(rows, indent=2) + '\n')
    os.replace(tmp, ledger)
    print(f'{name}: {rc}', flush=True)
reds = {row['test']: row['exit'] for row in rows if row['exit'] != 0}
adm = admission(None if base_reds is None else dict(base_reds), reds)
tmp = (out / 'admission.json').with_suffix('.tmp')
tmp.write_text(json.dumps(adm, indent=2) + '\n')
os.replace(tmp, out / 'admission.json')
print(f'TOTAL {len(rows)} FAIL {sum(row["exit"] != 0 for row in rows)}', flush=True)
if _baseline_path:
    print(f"ADMISSION introduced={len(adm['introduced'])} pre_existing={len(adm['pre_existing'])} "
          f"fixed={len(adm['fixed'])} green={'true' if adm['green'] else 'false'}", flush=True)
raise SystemExit(1 if any(row['exit'] != 0 for row in rows) else 0)
