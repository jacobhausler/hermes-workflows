#!/usr/bin/env python3
"""Suite hook for the standalone 20-cycle crash/resume harness."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
class CrashResume(unittest.TestCase):
    def test_twenty_real_runner_cycles(self):
        # est-rlfyo wall retime (was timeout=80; RED at the wall only): 20
        # cycles x 2 runner cold-spawns each. Quiet serial n=5 per harness at
        # e55f41f on the CI-pinned interpreter (3.14.9, 72-core estate host,
        # no competing suite procs, load1 9-19), 2026-10-27: canary walls
        # 89.03/89.55/90.13/90.39/90.93; sup 85.88/90.03/89.65/90.58/91.04;
        # all rc=0 with the '20/20' sentinel => timing drift only, same class
        # as #550 (v0.22.x cold-import floor ~0.43 s/hermes_cli.config spawn,
        # x40 spawns). 120 = measured max 91.04 + ~32% margin: absorbs CI
        # shard contention, still fails fast on real hangs; every crash/
        # resume/SIGKILL/dedupe/cycle-count/cleanup assertion unchanged.
        p=subprocess.run([sys.executable,str(ROOT/'tests/11-canary.py')],
                         text=True,capture_output=True,timeout=120)
        self.assertEqual(p.returncode,0,(p.stdout+'\n'+p.stderr)[-12000:])
        self.assertIn('20/20 crash/resume',p.stdout)
        self.assertEqual(sum('"cycle":' in line for line in p.stdout.splitlines()),20)
if __name__=='__main__': unittest.main()
