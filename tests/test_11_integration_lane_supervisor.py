#!/usr/bin/env python3
"""Suite hook for the standalone 20-cycle lane-supervisor kill/resume harness."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
class LaneSupervisor(unittest.TestCase):
    def test_twenty_real_runner_cycles(self):
        # est-rlfyo wall retime (was timeout=80; RED at the wall only): paired
        # hook to test_11_integration_crash_resume.py — same measurement set
        # (quiet serial n=5 at e55f41f, CI-pinned interpreter 3.14.9, 72-core
        # estate host, load1 9-19, 2026-10-27): sup walls
        # 85.88/90.03/89.65/90.58/91.04 (canary 89.03-90.93); all rc=0 with
        # the '20/20' sentinel => timing drift only, #550 class (cold-import
        # floor ~0.43 s/spawn x 40 spawns). 120 = measured max 91.04 + ~32%
        # margin; every kill/resume/dedupe/cycle-count/cleanup assertion
        # unchanged.
        p=subprocess.run([sys.executable,str(ROOT/'tests/11-lane-supervisor.py')],
                         text=True,capture_output=True,timeout=120)
        self.assertEqual(p.returncode,0,(p.stdout+'\n'+p.stderr)[-12000:])
        self.assertIn('20/20 lane-supervisor kill/resume',p.stdout)
        self.assertEqual(sum('"cycle":' in line for line in p.stdout.splitlines()),20)
if __name__=='__main__': unittest.main()
