import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ci-speed contract test: `suite.py --shard I/N` + `--merge` must reproduce the
# serial pass's ledger EXACTLY (same cases, same exits), and every fan-in refusal
# (missing lane, interrupted marker, empty lane, disjointness) must turn red —
# the shard/merge modes may bound wall clock, never the gate's honesty.

HERE = Path(__file__).resolve()
SUITE = HERE.parents[1] / 'scripts' / 'suite.py'

GREEN = "import sys; sys.exit(0)\n"
RED = "import sys; sys.exit(3)\n"


def make_root(td, names):
    root = Path(td) / 'root'
    (root / 'tests').mkdir(parents=True)
    for name, body in names.items():
        (root / 'tests' / name).write_text(body)
    return root


def run_suite(args):
    p = subprocess.run([sys.executable, str(SUITE)] + args,
                       capture_output=True, text=True, timeout=90)
    return p.returncode, p.stdout


def ledger_of(out):
    return {r['test']: r['exit'] for r in json.loads((out / 'exits.json').read_text())}


def test_shard_merge_reproduces_serial_ledger():
    with tempfile.TemporaryDirectory() as td:
        names = {f'test_ci_speed_{i}.py': (RED if i == 2 else GREEN) for i in range(5)}
        root = make_root(td, names)

        # serial reference pass (rc 1: it contains a red)
        serial = root / 'ci-serial'
        rc, _ = run_suite([str(root), str(serial)])
        assert rc == 1, f'serial reference must exit 1, got {rc}'
        base = ledger_of(serial)
        assert len(base) == 5 and sum(v != 0 for v in base.values()) == 1
        assert json.loads((serial / 'done.json').read_text()) == {'complete': True, 'total': 5}

        # 3 lanes, disjoint by position; merge must fuse to the same truth.
        # A lane's rc is lane-local law: red iff THIS lane holds the red case.
        dirs = []
        for i in range(3):
            d = root / f'ci-shard-{i}'
            rc, out = run_suite([str(root), str(d), '--shard', f'{i}/3'])
            lane = ledger_of(d)
            assert rc == (1 if any(v != 0 for v in lane.values()) else 0), \
                f'lane {i} rc diverges from its own rows:\n{out}'
            mk = json.loads((d / 'done.json').read_text())
            assert mk['complete'] is True and mk['shard'] == f'{i}/3'
            dirs.append(str(d))
        merged = root / 'ci-merged'
        rc, out = run_suite([str(root), str(merged), '--merge'] + dirs)
        assert rc == 1, f'merge must be red while a row is red:\n{out}'
        assert ledger_of(merged) == base, 'merged ledger diverges from serial truth'
        assert json.loads((merged / 'done.json').read_text())['total'] == 5
        assert 'TOTAL 5 FAIL 1 (merged)' in out
        adm = json.loads((merged / 'admission.json').read_text())
        assert adm['green'] is False and adm['zero_discovery'] is False


def test_green_merge_is_green():
    with tempfile.TemporaryDirectory() as td:
        names = {f'test_ci_speed_{i}.py': GREEN for i in range(5)}
        root = make_root(td, names)
        dirs = []
        for i in range(2):
            d = root / f'ci-shard-{i}'
            rc, out = run_suite([str(root), str(d), '--shard', f'{i}/2'])
            assert rc == 0, f'green lane must exit 0:\n{out}'
            dirs.append(str(d))
        merged = root / 'ci-merged'
        rc, out = run_suite([str(root), str(merged), '--merge'] + dirs)
        assert rc == 0, f'all-green lanes must merge green:\n{out}'
        assert 'TOTAL 5 FAIL 0 (merged)' in out
        assert json.loads((merged / 'admission.json').read_text())['green'] is True


def test_fan_in_refusals():
    with tempfile.TemporaryDirectory() as td:
        names = {f'test_ci_speed_{i}.py': GREEN for i in range(5)}
        root = make_root(td, names)

        good = root / 'ci-shard-0'
        rc, _ = run_suite([str(root), str(good), '--shard', '0/1'])
        assert rc == 0

        # interrupted lane: a valid all-green ledger WITHOUT its marker
        interrupted = root / 'ci-interrupted'
        interrupted.mkdir()
        (interrupted / 'exits.json').write_text(json.dumps(
            [{'test': f'test_ci_speed_{i}.py', 'exit': 0, 'log': 'x'} for i in range(5)]))
        rc, out = run_suite([str(root), str(root / 'out-i'), '--merge',
                             str(good), str(interrupted)])
        assert rc == 2 and 'done.json' in out, f'interrupted lane must refuse:\n{out}'
        # refused invocation leaves no standing green receipt
        assert not (root / 'out-i' / 'admission.json').exists()

        # missing lane dir entirely
        rc, out = run_suite([str(root), str(root / 'out-m'), '--merge',
                             str(good), str(root / 'does-not-exist')])
        assert rc == 2 and 'unusable' in out, f'missing lane must refuse:\n{out}'

        # zero-discovery lane: shard 7/8 over 5 cases runs nothing
        empty = root / 'ci-empty'
        rc, out = run_suite([str(root), str(empty), '--shard', '7/8'])
        assert rc == 1, f'zero-discovery shard must not exit 0:\n{out}'
        rc, out = run_suite([str(root), str(root / 'out-e'), '--merge',
                             str(good), str(empty)])
        assert rc == 2 and 'zero-discovery' in out, f'empty lane must refuse at merge:\n{out}'

        # disjointness: same lane fused twice
        rc, out = run_suite([str(root), str(root / 'out-d'), '--merge',
                             str(good), str(good)])
        assert rc == 2 and 'disjoint' in out, f'duplicate rows must refuse:\n{out}'


def test_shard_arg_validation():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td, {'test_ci_speed_0.py': GREEN})
        for bad in (['--shard', 'x/2'], ['--shard', '2/2'], ['--shard', '-1/2'], ['--shard', '0']):
            rc, out = run_suite([str(root), str(root / 'o')] + bad)
            assert rc == 2, f'{bad} must exit 2'
        rc, out = run_suite([str(root), str(root / 'o'), '--shard', '0/2', '--merge', 'x'])
        assert rc == 2 and 'exclusive' in out


if __name__ == '__main__':
    for fn in (test_shard_merge_reproduces_serial_ledger, test_green_merge_is_green,
               test_fan_in_refusals, test_shard_arg_validation):
        fn()
        print(f'OK {fn.__name__}')
    print('ci-speed: shard/merge contract green (4 tests)')
