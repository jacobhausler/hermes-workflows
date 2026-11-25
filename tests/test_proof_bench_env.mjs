import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { buildBenchLaunchEnv } from './proof-harness/capture.mjs';

const hostile = {
  ...process.env,
  WF_RUNS_ROOT: '/hostile/proof/runs',
  HERMES_WORKFLOWS_HOME: '/hostile/proof/home',
};
const desktopEnv = buildBenchLaunchEnv(hostile, {
  HERMES_HOME: '/owned/bench/home',
  HERMES_GATEWAY_LOCK_DIR: '/owned/bench/locks',
  WF_RUNS_ROOT: '/owned/bench/runs',
});
const child = spawnSync(process.execPath, ['-e', `process.stdout.write(JSON.stringify({
  runs: process.env.WF_RUNS_ROOT ?? null,
  workflowsHome: process.env.HERMES_WORKFLOWS_HOME ?? null,
  home: process.env.HERMES_HOME,
  locks: process.env.HERMES_GATEWAY_LOCK_DIR
}))`], { encoding: 'utf8', env: desktopEnv });
assert.equal(child.status, 0, child.stderr);
assert.deepEqual(JSON.parse(child.stdout), {
  runs: '/owned/bench/runs',
  workflowsHome: null,
  home: '/owned/bench/home',
  locks: '/owned/bench/locks',
});
assert.equal(hostile.WF_RUNS_ROOT, '/hostile/proof/runs', 'builder must not mutate parent env');
assert.equal(hostile.HERMES_WORKFLOWS_HOME, '/hostile/proof/home');
console.log('PASS bench child gets only the owned home, locks, and runs root; parent unchanged');
