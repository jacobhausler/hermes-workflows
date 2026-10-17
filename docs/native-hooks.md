# Native hooks (default-off operator integrations)

Two opt-in hook integrations ship since v1.3.9. Both are **DEFAULT OFF**: off
means zero registrations, zero threads, byte-identical payloads. Enabling one
never changes graph behavior — it only adds an observer (P3) or an extra
presentation surface for held human gates (P5). The authoritative spec for each
is its module docstring ("the docstring is its man page"); this file is the
pointer and the switch board.

| Feature | Settings key | Exact entry that arms it | Gate read |
|---|---|---|---|
| P3 subagent accounting | `plugins.entries.hermes-workflows.settings.hooks_allow` | `"subagent_accounting"` | fail-closed (a scalar, a mapping, or a read failure all read as OFF) |
| P5 native approval bridge | `plugins.entries.hermes-workflows.settings.hooks_bridge_allow` | `"approval_bridge"` | allow-list; off = defs-only module exec, no thread |

- **P3** (`subagent_accounting.py`) harvests `delegate_task` leaf children onto
  an append-only spool at
  `<hermes home>/plugin-state/hermes-workflows/subagent_accounting.jsonl`
  (one JSON row per leaf, one bounded rotation generation, torn-line tolerant;
  `read_rows()` is the reference reader). Honest coverage caveat, stated in the
  module: CLI-spawned workflow children do NOT fire `subagent_stop` — only
  in-process delegate_task leaves do. The spool itself is the interface; there
  is deliberately no status/wait wiring.
- **P5** (`approval_bridge.py`) presents a held human gate ALSO on the host's
  native approval channel (the same card the dangerous-command gate rides), so
  an operator already in the gateway surface sees the hold without polling.
  Authority law: the card text is the runner's own `wake.jsonl` `gate.held`
  sentence verbatim — graph-authored question/options never enter the approval
  surface, and the bridge authors no prose. One hold event mints one idempotency
  token and resolves to at most ONE release through the plugin's own
  `act_release` door (the same path the tool action rides: CAS, answer file,
  respawn). Desktop and tool release are untouched either way.

Proof (run at repo root):

```sh
python3 tests/test_subagent_accounting_p3.py     # P3 spool + fail-closed gate
python3 tests/test_approval_bridge_p5.py         # P5 token/once/door-path
grep -n "hooks_allow" __init__.py | head -2      # registration behind the gate
grep -n "SETTING_KEY" approval_bridge.py         # hooks_bridge_allow
```
