#!/usr/bin/env python3
"""Serial bounded suite with durable per-case logs and atomic exit ledger."""
import json
import os
import subprocess
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
ledger = out / 'exits.json'
rows = json.loads(ledger.read_text()) if ledger.exists() else []
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
print(f'TOTAL {len(rows)} FAIL {sum(row["exit"] != 0 for row in rows)}', flush=True)
raise SystemExit(1 if any(row['exit'] != 0 for row in rows) else 0)
