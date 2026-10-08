#!/usr/bin/env python3
"""est-2ek.1.80 finding 3 — the registered `workflow` tool description tells the model when to
use it and when not to.

The model sees only the schema the plugin registers (tool_search / tool_describe), not
SKILL.md. The description listed features with no use/avoid threshold and no pointer to
delegate_task, so a one-or-two-call task was not steered away from a full graph. The
registered description now carries one selection sentence naming delegate_task.
"""
import importlib.util, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = tempfile.mkdtemp(prefix="wf-tool-selection-80-")
os.environ["HERMES_HOME"] = HOME
os.environ["WF_RUNS_ROOT"] = str(Path(HOME) / "runs")
spec = importlib.util.spec_from_file_location("hw_door_80", BUILD / "__init__.py")
hw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (" " + str(detail)[:300] if not cond and detail else ""))
    ok = ok and bool(cond)

class Ctx:
    tools = {}
    def register_skill(self, *_, **__): pass
    def register_hook(self, *_, **__): pass
    def register_command(self, *_, **__): pass
    def register_tool(self, **kw): self.tools[kw["name"]] = kw
    def get_config(self, _key, default): return default

ctx = Ctx()
hw.register(ctx)
desc = ctx.tools["workflow"]["schema"]["description"]
check("registered description names delegate_task", "delegate_task" in desc, desc)
check("registered description states a use threshold (independent lanes / human gate / resumable graph)",
      "independent lanes" in desc and "human gate" in desc and "resumable graph" in desc, desc)
check("registered description states the avoid case (one or two independent calls)",
      "one or two independent calls" in desc, desc)
check("description still points at parameters and the skill",
      "parameters" in desc and "`workflow` skill" in desc, desc)
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
