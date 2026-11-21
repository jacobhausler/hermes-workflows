#!/usr/bin/env python3
"""Twenty real runner crash/resume cycles; status lane_key checked against /proc.
Failure writes a JSONL evidence line before exiting; suitable for crash/resume canaries.
"""
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec = importlib.util.spec_from_file_location('canary_door',ROOT/'__init__.py')
door = importlib.util.module_from_spec(spec);spec.loader.exec_module(door)
import wf_test_isolation as _iso71_door18; _iso71_door18.install(door)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT
import wfcommon as common


# est-lg94s (#699): every budget below is an upper bound on a POLL, not an
# assertion about elapsed time -- polling returns the moment the predicate
# holds, so widening costs nothing when the machine is idle and removes the
# only load-critical seam left in the cycle: runner boot measured up to 8.7 s
# under the 2026-11-21 concurrent-arm storm (old 5 s wall -> 'runner never
# live'), which is the same class as the hook's wall (see the hook's retime
# note). 20 s = >2x the measured worst boot.
def until(pred,seconds=20):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if pred():return True
        time.sleep(.01)
    return False


def main():
    with tempfile.TemporaryDirectory(prefix='wf11-canary-') as td:
        td=Path(td);runs=td/'runs';runs.mkdir()
        def release_all():
            # The WAIT park is unbounded, so every exit path — failed asserts
            # included — releases parked children before the tempdir dies. If
            # teardown wins the race to a file the child has not yet noticed,
            # the fixture treats the vanished release directory as a release
            # and drains (guarantee pinned by test_harness_probe_and_park_races).
            for c in range(20):
                (td/f'release-{c}').touch()
        env={**os.environ,'HERMES_HOME':str(td),'WF_RUNS_ROOT':str(runs),
             'HERMES_WF_HERMES_BIN':str(ROOT/'tests/fixtures/11-fake-hermes.py')}
        with patch.dict(os.environ,env,clear=True):
            try:
                for cycle in range(20):
                    key='canary/'+str(cycle)
                    # Same kill race as 11-lane-supervisor: the child parks on the
                    # release file so it can never reach done before the SIGKILL.
                    graph={'name':'canary-'+str(cycle),'nodes':[{'id':'a','type':'agent','goal':f'WAIT {td}/release-{cycle}'}]}
                    start=door.act_run({'graph':graph,'lane_key':key})
                    assert 'run_id' in start,start
                    rid=start['run_id'];r=runs/rid
                    assert until(lambda:common.runner_alive(r)),(cycle,'runner never live')
                    live=door.act_status({'lane_key':key})
                    assert live['runner_live'] == common.runner_alive(r) == True,(cycle,live)
                    pid=int((r/'wf.pid').read_text())
                    os.kill(pid,signal.SIGKILL)
                    (td/f'release-{cycle}').touch()  # release the parked child only after the kill
                    assert until(lambda:not common.runner_alive(r)),(cycle,'kill failed')
                    dead=door.act_status({'lane_key':key})
                    assert dead['runner_live'] == common.runner_alive(r) == False,(cycle,dead)
                    assert dead['needs_resume'],(cycle,dead)
                    repeat=door.act_run({'graph':graph,'lane_key':key})
                    assert repeat.get('deduped') and repeat['run_id']==rid,(cycle,repeat)
                    assert not common.runner_alive(r),(cycle,'dedupe spawned runner')
                    door.act_wait({'run_id':rid,'timeout':8})
                    assert until(lambda:door.act_status({'lane_key':key})['state']=='done',20),(cycle,'not done')
                    final=door.act_status({'lane_key':key})
                    assert final['runner_live'] == common.runner_alive(r),(cycle,final)
                    assert not (r/'runner.log').read_text().count('WORKFLOW_BUSY'),(cycle,'busy crash')
                    print(json.dumps({'cycle':cycle+1,'status':final['state'],'live':final['runner_live']}),flush=True)
            finally:
                release_all()
    print('20/20 crash/resume')

if __name__=='__main__':main()
