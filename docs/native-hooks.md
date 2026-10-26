# Native hooks (default-off operator integrations)

Three default-off hook integrations live on main. All are **DEFAULT OFF**: off
means zero registrations, zero threads, byte-identical payloads. Enabling one
never changes graph behavior — it only adds an observer (P1, P3) or an extra
presentation surface for held human gates (P5). Ship state: P1 (outbound bridge)
shipped in the v1.3.9 cut; P3 and P5 landed on main after that tag and ship in
the v1.4.0 cut. The authoritative spec for each is its module docstring ("the
docstring is its man page"); this file is the pointer and the switch board.

| Feature | Settings key | Exact entry that arms it | Gate read |
|---|---|---|---|
| P1 outbound bridge | `plugins.entries.hermes-workflows.settings.outbound_bridge` | operator setting ON + per-run carrier opt-in (`outbound_bridge` in run meta/graph meta) | fail-open (webhook delivery is best-effort; the run never waits on the network) |
| P3 subagent accounting | `plugins.entries.hermes-workflows.settings.hooks_allow` | `"subagent_accounting"` | fail-closed (a scalar, a mapping, or a read failure all read as OFF) |
| P5 native gate presentation | `plugins.entries.hermes-workflows.settings.hooks_bridge_allow` | `"approval_bridge"` | allow-list; off = defs-only module exec, no thread; core consent `settings.allow_gateway_injection: true` is required for the injection route to accept anything |

- **P3** (`subagent_accounting.py`) harvests `delegate_task` leaf children onto
  an append-only spool at
  `<hermes home>/plugin-state/hermes-workflows/subagent_accounting.jsonl`
  (one JSON row per leaf, one bounded rotation generation, torn-line tolerant;
  `read_rows()` is the reference reader). Honest coverage caveat, stated in the
  module: CLI-spawned workflow children do NOT fire `subagent_stop` — only
  in-process delegate_task leaves do. The spool itself is the interface; there
  is deliberately no status/wait wiring.
- **P5** (`approval_bridge.py`) presents a held human gate ALSO into the run
  owner's OWN gateway session as a plugin-injected message — core's public
  route `ctx.inject_message` (`gateway/run_plugin_injection.py`) — so an
  operator already in the gateway surface sees the hold without polling. The
  answer comes back on the door's own `post_gateway_admission` `wf release`
  lane (zero turns) or the tool/desktop paths; there is **no fallback to any
  other session** and no read of core private approval internals (upstream
  review NousResearch/hermes-agent#141665 point 2). Authority law: the injected
  body is the runner's own `wake.jsonl` `gate.held` sentence verbatim plus one
  constant protocol footer — graph-authored question/options never enter the
  surface, and the bridge authors no prose. One hold event mints one idempotency
  token; the tailer reconciles each instance against the run dir (the holder of
  record), so an answer on any release path is terminal bookkeeping — never a
  re-present, never a second release. The `pre_approval_request` /
  `post_approval_response` observer pair stays registered behind the same flag
  as a guarded compatibility path (it acts only on tokens this process minted).
  Desktop and tool release are untouched either way.

Proof (run at repo root):

```sh
python3 tests/test_subagent_accounting_p3.py     # P3 spool + fail-closed gate
python3 tests/test_approval_bridge_p5.py         # P5 token/once/door-path
grep -n "hooks_allow" __init__.py | head -2      # registration behind the gate
grep -n "SETTING_KEY" approval_bridge.py         # hooks_bridge_allow
```
