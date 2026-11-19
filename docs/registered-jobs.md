# Registered external jobs

A solo agent node can hand long external work to the runner without extending
its own turn/wall budget. Linux process identity and verified spawn ancestry are
required; fan-out registration is not supported. This is not permission to leave
unregistered background work or bypass the process-tree completion gate.

Before the agent exits, launch the external process in its own process group,
with stdout/stderr already redirected to a log inside the run directory. Register
its pid, a new (not yet existing) artifact path and that log using:

    python3 /path/to/plugin/wf.py register-job EXACT_RUN_ID NODE_ID PID ARTIFACT LOG

The child may also import `wf.register_job(run, node, byid, pid, artifact, log)`.
Both the caller and job must belong to that node's currently verified spawn.
Only one registration per node is accepted. Registration lives in
`jobs/NODE_ID.json`, bound to the node fingerprint, kernel boot id and process
start tick. A stale/invalid receipt fails rather than relaunching work.

The external job must atomically publish its artifact before exiting:

    {"exit_code": 0, "output": {"your": "schema-valid node output"}}

The runner waits for that job and its observed family to die before the existing
process-tree proof and commit gates run. An agent's progress reply is not a
result. A missing artifact, missing typed exit code, nonzero exit, invalid schema
or changed process identity is not success. Re-drive polls the original job
before the prior-generation sweep and consumes its durable harvest without a
new agent launch. The job does not inherit the departed agent's wall deadline.
The runner still observes stop; this contract does not grant an unlimited or
unmanaged job lifetime. Use an external job deadline when bounded work requires
one. The durable receipt/log are retained for review.

Silent runner deaths are reaped on mutation/resume paths and, while any run is
active, by the self-terminating watchdog cron tick (`cron_bridge.py` +
`runner_watchdog.py`, est-ip975): the door arms one named `no_agent` job at its post-flock launch tail
that revives dead-runner runs — cadence resolved by `cron_bridge.tick_schedule`
(env `WF_TICK_SCHEDULE` > config `workflows.tick_schedule` > every 2m) — and
the tick body removes the job itself at drain, so an
interrupted run needs no manual sweep and the idle cost is zero wakes. The door writes
a graph-bound typed exit receipt and claim-bound interruption receipts under
`interruptions/`. The node read model exposes current interrupted truth while
preserving original spawn bytes as cold incident evidence. Reads remain pure.

## The tick launcher is interpreter-pinned (P41)

The baked job script (`<HERMES_HOME>/scripts/hermes-workflows-tick.sh`) is

    #!/usr/bin/env bash
    exec <INTERPRETER> <plugin>/wf.py tick

with `<INTERPRETER>` absolute at bake time (env `WF_TICK_PYTHON` > the bundled
python that ran the bake). The entrypoint rides as an argument, so the launch
needs neither `wf.py`'s exec bit nor a shebang resolution — `hermes update`
reinstalling plugin files at mode 0644, or `env python3` resolving to the
macOS 3.9.6 system python (the plugin is >=3.10 syntax), cannot silently
revert the tick. Every re-arm over a running tick re-bakes the launcher on
drift (content or exec mode) only, so the repair converges and a settled
launcher is never clobbered. After any plugin update, the self-check re-pins,
runs the tick once through the baked shim exactly as the scheduler will, and
exits with the tick's rc:

    python3 ~/.hermes/plugins/hermes-workflows/cron_bridge.py selfcheck
    TICK SELFCHECK rc=0 shim=$HOME/.hermes/scripts/hermes-workflows-tick.sh

One-line rule-out when runs look stuck under a "⏳ Gateway draining" banner:
run that line — `rc=0` means the watchdog tick is alive and re-driving, so the
drain is real (agents genuinely active), not a dead tick leaving interrupted
runs unreaped (the P41 shape); a nonzero rc names the launcher itself as the
suspect, not the gateway.
