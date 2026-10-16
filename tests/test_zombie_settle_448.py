#!/usr/bin/env python3
"""#448 regression: zombie/empty-tree processes count as REAPED before the
#61 guard fail-closes with left_live_descendants.

Repro (run 20261016-112721-ra-issue-427-nightly, events.jsonl 14:22:50-
14:23:54Z): the triage answer was banked (node.banked, 3015 files), the tree
died naturally between the commit-edge guard's liveness sample and
_tree_quiesce's first pass. _tree_quiesce returned ('', []) — dead-or-empty by
its own contract — but _final_quiesce only believed proof == 'dead' and
replaced the verdict with `left-live-descendants ... live process tree []`:
an EMPTY list quoted as proof of liveness. A transient timeout-with-corpus
record (re-drivable, resume=true) was dead-lettered under the TERMINAL class,
so the nightly ra-issue lane needed a manual close.

Laws proven here:
  1. _final_quiesce: proof == '' (drained mid-check) returns the record
     untouched — the banked/death record keeps its own verdict; it is never
     replaced by a left_live_descendants dead-letter.
  2. A bounded settle between the last SIGKILL and the fail-closed verdict
     (2 re-checks x 0.5 s, re-waiting first): a pid caught mid-reap is the
     same race as an already-dead tree and lands as ('dead', []).
  3. Fail-closed stays fail-closed: a genuinely live pid after the settle
     still returns stuck — the settle never weakens the #61 gate.
  4. _proc_alive identity law: a real zombie is dead; a /proc row that
     vanishes between os.kill 0 and the read is a reaped-class death; an
     empty ps row means the pid is GONE (never "live" on missing state).
"""
import itertools
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

BUILD = Path(os.environ.get('WF_TEST_BUILD') or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(BUILD))
import wf

passed = True


def check(label, good, detail):
    global passed
    print(('PASS ' if good else 'FAIL ') + label, detail, flush=True)
    passed = passed and good


fake_pid = 987654321
SOURCE_DONE = {'status': 'done', 'pid': fake_pid, 'spawn': 1, 'attempts': 2,
               'tree_pids': [fake_pid], 'skey': 'probe-key', 'ms': 2250197,
               'attempts_log': [{'attempt': 0, 'error_class': 'timeout',
                                 'resume': True, 'banked': '/x/triage.corpus'}],
               'output': {'verdict': 'ship'}}
SOURCE_TIMEOUT = {'status': 'failed', 'error': 'timeout after 3600s',
                  'error_class': 'timeout', 'pid': fake_pid, 'spawn': 1,
                  'attempts': 2, 'banked': '/x/triage.corpus',
                  'final': 'Triage completed and verified on GitHub',
                  'tree_pids': [fake_pid], 'skey': 'probe-key', 'ms': 2250197}


def final_quiesce(monkey_proof, source):
    """Drive _final_quiesce with a readable-live guard sample and a controlled
    _tree_quiesce verdict. Returns (out_record, logged_events)."""
    meta = {'_run': Path('/tmp/wf-448-nonexistent'), 'proctree_hold_s': 0,
            'proctree_kill_proof_s': 0}
    events = []
    with patch.object(wf, '_proc_pids_by_pgid', return_value=[fake_pid]), \
         patch.object(wf, '_proc_alive', return_value=True), \
         patch.object(wf, '_sidecar_live_registered', return_value=set()), \
         patch.object(wf, '_survivors', return_value=set()), \
         patch.object(wf, '_tree_quiesce', return_value=monkey_proof), \
         patch.object(wf, 'log', side_effect=lambda *a, **kw: events.append(kw)):
        out = wf._final_quiesce(meta, dict(source), 'node', {'node': 'probe'})
    return out, events


# --- 1. THE REPRO: drained mid-check must never dead-letter -----------------
out, events = final_quiesce(('', []), SOURCE_DONE)
check('final: drained-mid-check keeps a done verdict',
      out.get('status') == 'done' and not out.get('error_class')
      and out.get('tree_proof') is None,
      f"status={out.get('status')} error_class={out.get('error_class')}")
check('final: the race leaves an honest tree_kill receipt',
      any(e.get('proof') == '' and e.get('final') for e in events),
      f"events={[e.get('proof') for e in events]}")

out, _ = final_quiesce(('', []), SOURCE_TIMEOUT)
check('final: banked-complete timeout keeps its class and corpus pointer',
      out.get('error_class') == 'timeout' and out.get('banked') == '/x/triage.corpus'
      and out.get('final', '').startswith('Triage'),
      f"error_class={out.get('error_class')} banked={out.get('banked')}")
check('final: no left_live dead-letter is manufactured',
      out.get('error_class') != 'left_live_descendants'
      and 'left-live' not in (out.get('error') or ''),
      f"error={out.get('error')!r:.80}")

# controls: the guard's real stuck/unknown verdicts still replace the record
out, _ = final_quiesce(('stuck', [fake_pid]), SOURCE_DONE)
check('control: proven-stuck still fails closed',
      out.get('error_class') == 'left_live_descendants'
      and out.get('tree_descendants') == [fake_pid],
      f"error_class={out.get('error_class')}")
with patch.object(wf, '_proc_pids_by_pgid', return_value=[fake_pid]), \
     patch.object(wf, '_proc_alive', return_value=True), \
     patch.object(wf, '_sidecar_live_registered', return_value=set()), \
     patch.object(wf, '_survivors', return_value=set()), \
     patch.object(wf, 'log'):
    out = wf._final_quiesce({'_run': Path('/tmp/wf-448-nonexistent'),
                             'proctree_hold_s': 0, 'proctree_kill_proof_s': 0},
                            dict(SOURCE_DONE), 'node', {'node': 'probe'})
check('control: unreadable table still fails closed typed',
      out.get('error_class') == 'left_live_descendants',
      f"error_class={out.get('error_class')}")

# --- 2. the bounded settle rescues a mid-reap race --------------------------
def flip_alive(seq):
    it = iter(seq)
    return lambda p: next(it, False)


sleeps = []
# alive through hold+kill; dead on the settle re-checks => ('dead', [])
with patch.object(wf, '_proc_pids_by_pgid', return_value=[fake_pid]), \
     patch.object(wf, '_proc_alive', side_effect=flip_alive([True, True, True, True,
                                                             False, False, False, False])), \
     patch.object(wf, '_reap_zombie'), \
     patch.object(wf.time, 'sleep', side_effect=lambda s: sleeps.append(s)), \
     patch.object(wf.os, 'kill'), patch.object(wf.os, 'killpg'):
    result = wf._tree_quiesce({fake_pid}, fake_pid, 0, 0, term_grace_s=0)
check('settle: pid dying inside the settle window lands dead',
      result == ('dead', []), result)
check('settle: the window is bounded', 0 < len(sleeps) <= wf.PROCREE_SETTLE_CHECKS + 1,
      f'sleep_calls={len(sleeps)}')

sleeps = []
with patch.object(wf, '_proc_pids_by_pgid', return_value=[fake_pid]), \
     patch.object(wf, '_proc_alive', return_value=True), \
     patch.object(wf, '_reap_zombie'), \
     patch.object(wf.time, 'sleep', side_effect=lambda s: sleeps.append(s)), \
     patch.object(wf.os, 'kill'), patch.object(wf.os, 'killpg'):
    result = wf._tree_quiesce({fake_pid}, fake_pid, 0, 0, term_grace_s=0)
check('settle: a still-live pid after the settle stays stuck (fail-closed intact)',
      result == ('stuck', [fake_pid]), result)

# _wait_pids_dead rides the same settle law
with patch.object(wf, '_proc_alive', side_effect=flip_alive([True, False, False])), \
     patch.object(wf, '_reap_zombie'), \
     patch.object(wf.time, 'sleep'), \
     patch.object(wf.os, 'kill'):
    result = wf._wait_pids_dead([fake_pid], 0)
check('wait_pids_dead: mid-reap settle proves death', result == (True, []), result)
with patch.object(wf, '_proc_alive', return_value=True), \
     patch.object(wf, '_reap_zombie'), \
     patch.object(wf.time, 'sleep'), \
     patch.object(wf.os, 'kill'):
    result = wf._wait_pids_dead([fake_pid], 0)
check('wait_pids_dead: genuinely live still reports (False, live)',
      result == (False, [fake_pid]), result)

# --- 3. reaped-class identity: a real zombie is dead ------------------------
if os.name == 'posix':
    proc = subprocess.Popen([sys.executable, '-c', 'pass'])
    deadline = time.time() + 5
    state = ''
    while time.time() < deadline:
        try:
            state = Path(f'/proc/{proc.pid}/stat').read_text().rsplit(')', 1)[1].split()[0]
        except OSError:
            state = '?'
        if state.startswith('Z'):
            break
        time.sleep(0.05)
    if state.startswith('Z'):
        check('real zombie counts as dead (_proc_alive)', wf._proc_alive(proc.pid) is False,
              f'pid={proc.pid} state={state}')
        res = wf._tree_quiesce({proc.pid}, proc.pid, 0, 0, term_grace_s=0)
        check('real zombie: quiesce returns dead-or-empty, never stuck',
              res == ('', []), res)
    else:
        check('real zombie fixture reached Z state', False, f'state={state!r}')
    wf._reap_zombie(proc.pid)
else:
    check('real zombie fixture (posix only)', True, 'skipped')

# /proc row vanishes mid-read AND the kernel re-ask returns ESRCH: the process
# exited in the race window — reaped-class death, never "live on missing row".
def _enoent(*a, **k):
    raise FileNotFoundError(2, 'No such file or directory')


# kill-0 answers once (pre-check), the re-ask after the vanished row says ESRCH.
with patch.object(wf.os, 'kill',
                  side_effect=[None, ProcessLookupError(3, 'No such process')]), \
     patch.object(Path, 'read_text', _enoent):
    check('row vanished + ESRCH re-ask counts as dead (reaped-class)',
          wf._proc_alive(fake_pid) is False, 'FileNotFoundError + ProcessLookupError')
# The g255 inverse: row unreadable but the pid re-asks alive and ps is dead —
# unknown state is NOT death (fail-open stands; seat lending must see the holder).
with patch.object(wf.os, 'kill'), \
     patch.object(Path, 'read_text', _enoent), \
     patch.object(wf.subprocess, 'run',
                  side_effect=OSError(2, 'no ps (simulated)')):
    check('unreadable row + alive re-ask + dead ps stays live (g255 law intact)',
          wf._proc_alive(fake_pid) is True, 'unknown state is not death')

# ps fallback: an empty row means GONE (never "live" on missing state)
class _Ps:
    def __init__(self, out): self.stdout = out
for raw, want in (('  ', False), ('Z ', False), ('Ss', True)):
    with patch.object(wf.os, 'kill'), \
         patch.object(Path, 'read_text', side_effect=PermissionError(13, 'denied')), \
         patch.object(wf.subprocess, 'run', return_value=_Ps(raw)):
        check(f'ps fallback {raw.strip()!r} -> {want}', wf._proc_alive(fake_pid) is want,
              f'raw={raw!r}')

print()
print('ALL PASS' if passed else 'FAILURES')
sys.exit(0 if passed else 1)
