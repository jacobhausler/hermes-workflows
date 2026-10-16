#!/usr/bin/env python3
"""P3 subagent accounting (config-gated, default-off): the harvest contract.

Pinned laws (module docstring in subagent_accounting.py is the man page):
 1. OFF by default: register() wires NO subagent_stop hook when the allow-list is
    unset or malformed (scalar / mapping / other-token-only all read OFF), and the
    #157 card hook survives the gate untouched.
 2. Gated ON: allow-list containing 'subagent_accounting' registers exactly one
    subagent_stop hook.
 3. Row shape: core's _fire_subagent_stop_hooks kwargs land as
    {ts, parent_session_id, child_status, duration_ms, tool_call_count}; unknown
    extra kwargs (summary, role, turn, telemetry version) are absorbed, never shipped.
 4. Fail-open: junk kwargs and an un-writable spool root never raise; absent facts
    land as honest nulls, and no torn file is left behind.
 5. Size law: past the cap the spool rotates exactly one generation (spool -> .1)
    and the newest row lands on the fresh spool.
 6. read_rows(): torn/garbage lines skipped, missing spool reads [].

Run: python3 tests/test_subagent_accounting_p3.py
"""
import importlib.util, json, os, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT / "home-sacct-p3"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, "/opt/hermes")

spec = importlib.util.spec_from_file_location("wf_door_sacct", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso71; _iso71.install(door)

sa_spec = importlib.util.spec_from_file_location("sacct_p3", ROOT / "subagent_accounting.py")
sa = importlib.util.module_from_spec(sa_spec)
sa_spec.loader.exec_module(sa)
sa.bind(door._common)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

class Ctx:
    """Core-shaped registration surface; get_config answers like a plugin ctx
    reading plugins.entries.hermes-workflows.settings.* (unset -> default)."""
    def __init__(self, cfg=None):
        self.hooks, self.tools, self._cfg = {}, [], (cfg or {})
    def register_hook(self, name, fn): self.hooks[name] = fn
    def register_tool(self, **kw): self.tools.append(kw)
    def register_command(self, *_, **__): pass
    def register_skill(self, *_, **__): pass
    def get_config(self, key, default=None): return self._cfg.get(key, default)

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)
_orig_spawn = door._spawn_runner
door._spawn_runner = lambda r: None
SPOOL = HOME / "plugin-state" / "hermes-workflows" / "subagent_accounting.jsonl"
CFG = HOME / "config.yaml"
def settings_yaml(body):   # raw-read gate variants ride the owner settings file
    CFG.write_text("plugins:\n  entries:\n    hermes-workflows:\n      settings:\n" + body)
    return CFG

def rows():
    return sa.read_rows()

try:
    # ---- 1: default OFF, and malformed allow-lists read OFF (fail-closed) ------
    ctx = Ctx(); door.register(ctx)
    check("default-off: no subagent_stop registration", "subagent_stop" not in ctx.hooks)
    check("default-off: #157 card hook still registered", "transform_llm_output" in ctx.hooks)
    check("fail-closed gate: enabled() agrees no-file is False", sa.enabled() is False)
    for label, body in (("scalar", "        hooks_allow: subagent_accounting\n"),
                        ("mapping", "        hooks_allow: {subagent_accounting: true}\n"),
                        ("other-token-only", "        hooks_allow:\n          - something_else\n"),
                        ("empty-list", "        hooks_allow: []\n")):
        settings_yaml(body); c2 = Ctx(); door.register(c2)
        check(f"fail-closed gate: {label} reads OFF", "subagent_stop" not in c2.hooks,
              repr(door._common._raw_owner_settings()[0].get("hooks_allow")))
    check("fail-closed gate: malformed leaves the #157 card hook on every register",
          "transform_llm_output" in c2.hooks)

    # ---- 2: gated ON -----------------------------------------------------------
    settings_yaml("        hooks_allow:\n          - subagent_accounting\n")
    ctx_on = Ctx(); door.register(ctx_on)
    check("allow-list token registers exactly one subagent_stop hook",
          callable(ctx_on.hooks.get("subagent_stop")))
    check("enabled() agrees the listed gate is ON", sa.enabled() is True)
    hook = ctx_on.hooks["subagent_stop"]

    # ---- 3: row shape (core kwargs shape, additive extras absorbed) -------------
    hook(parent_session_id="sess-parent", parent_turn_id="t-9", child_session_id="child-a",
         child_role=None, child_summary="some model prose that must not ship",
         child_status="completed",
         tool_call_history=[{"tool_name": "write_file"}, {"tool_name": "read_file"}],
         duration_ms=1234, telemetry_schema_version=1)
    r = rows()
    check("one row appended", len(r) == 1, json.dumps(r)[:200])
    row = r[0] if r else {}
    check("row keys are exactly the accounting shape",
          set(row) == {"ts", "parent_session_id", "child_status", "duration_ms", "tool_call_count"},
          json.dumps(row))
    check("row carries the four facts",
          row.get("parent_session_id") == "sess-parent" and row.get("child_status") == "completed"
          and row.get("duration_ms") == 1234 and row.get("tool_call_count") == 2, json.dumps(row))
    check("ts is epoch seconds", isinstance(row.get("ts"), (int, float)) and row.get("ts", 0) > 1e9)
    check("no summary prose in the spool", b"model prose" not in SPOOL.read_bytes())
    hook(parent_session_id="sess-parent", child_status="error", duration_ms=7,
         tool_call_history=[])                      # a fan-out's second leaf, in order
    check("append-only: two rows in event order", len(rows()) == 2 and rows()[1]["duration_ms"] == 7)

    # ---- 4: fail-open (driven on the test's own module instance; wiring of the
    #      registered twin is already pinned by check 2) ---------------------------
    sa.harvest(parent_session_id=None, child_status=None, duration_ms="junk",
               tool_call_history="not-a-list")      # unparseable facts -> honest nulls
    j = rows()[-1]
    check("junk facts never raise and land as nulls",
          j["child_status"] == "unknown" and j["duration_ms"] is None
          and j["tool_call_count"] is None and j["parent_session_id"] is None, json.dumps(j))
    _orig_home = door._common.hermes_home
    try:
        blocker = HOME / "blocker"
        blocker.write_text("a file where a directory must be")
        door._common.hermes_home = lambda: blocker
        sa.harvest(parent_session_id="s", child_status="completed", duration_ms=1,
                   tool_call_history=[])            # mkdir fails: must swallow
        check("un-writable spool root: fail-open, no raise", True)
    finally:
        door._common.hermes_home = _orig_home
    check("fail-open left the spool byte-parseable line-wise",
          all(json.loads(ln) for ln in SPOOL.read_text().splitlines()))

    # ---- 5: size law: one bounded rotation generation ---------------------------
    _cap = sa.SPOOL_MAX_BYTES
    try:
        sa.SPOOL_MAX_BYTES = 10
        sa.harvest(parent_session_id="rot", child_status="completed", duration_ms=9,
                   tool_call_history=[])            # spool over the cap -> rotate + fresh row
        rot = SPOOL.with_name(SPOOL.name + ".1")
        check("over-cap rotates to exactly one .1 generation", rot.is_file() and not SPOOL.with_name(SPOOL.name + ".2").exists())
        check("rotated spool holds only the newest row", len(rows()) == 1 and rows()[0]["parent_session_id"] == "rot",
              json.dumps(rows())[:200])
    finally:
        sa.SPOOL_MAX_BYTES = _cap

    # ---- 6: reference reader tolerates a torn tail ------------------------------
    with open(SPOOL, "a") as f:
        f.write('{"ts": truncated\n')
    check("read_rows skips the torn line", all(isinstance(x, dict) for x in rows()))
    shutil.rmtree(HOME / "plugin-state", ignore_errors=True)
    check("missing spool reads []", rows() == [])
finally:
    door._spawn_runner = _orig_spawn
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
