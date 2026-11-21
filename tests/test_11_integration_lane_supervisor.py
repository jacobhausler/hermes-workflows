#!/usr/bin/env python3
"""Suite hook for the standalone 20-cycle lane-supervisor kill/resume harness."""
import select
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
def run_progress_walled(cmd,idle=60.0,cap=600.0):
    # est-bwqq1 (#699): paired with test_11_integration_crash_resume.py — same
    # flat 120s wall (est-rlfyo retime, quiet n=5 max 91.04 + ~32%), RED under
    # suite concurrency (nightly serial ci-out-1121) yet standalone-green.
    # Progress-aware: the harness streams one flush=True '"cycle":N' line per
    # cycle, so idle>60s (~13x the quiet per-cycle pace of ~4.5 s) is a hang,
    # not tenant load; the 600s hard cap still fails real hangs fast. Every
    # kill/resume/dedupe/cycle-count/cleanup assertion unchanged.
    t0=tlast=time.monotonic();out=[]
    p=subprocess.Popen(cmd,text=True,stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,bufsize=1)
    assert p.stdout is not None
    while True:
        now=time.monotonic()
        if now-t0>cap or now-tlast>idle:
            p.kill();out.append(f'\nWALL idle={now-tlast:.1f}s cap={cap}\n');break
        if select.select([p.stdout],[],[],max(0.05,min(idle-(now-tlast),cap-(now-t0))))[0]:
            line=p.stdout.readline()
            if not line:break
            out.append(line);tlast=time.monotonic()
    return p.wait(),''.join(out)
class LaneSupervisor(unittest.TestCase):
    def test_twenty_real_runner_cycles(self):
        rc,out=run_progress_walled([sys.executable,str(ROOT/'tests/11-lane-supervisor.py')])
        self.assertEqual(rc,0,out[-12000:])
        self.assertIn('20/20 lane-supervisor kill/resume',out)
        self.assertEqual(sum('"cycle":' in line for line in out.splitlines()),20)
if __name__=='__main__': unittest.main()
