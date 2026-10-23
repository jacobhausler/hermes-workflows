#!/usr/bin/env python3
"""est-wqml6 (WF-GRAFT-12): per-node telemetry for CLI-spawned children.

The peer mechanism (atbrace:hw-y2l; iw-recon observer.py/telemetry.py/engine.py
fold; SYNTHESIS.md #11) grafted onto this repo's skey machinery. Closed loop:

  1. GATE  the child-side observer registration exists ONLY where the runner's
     spawn env pins HERMES_WF_TELEMETRY (the join key: the session-key prefix,
     stable across retries) alongside HERMES_WF_RUN_DIR. No pin -> no hooks ->
     zero cost (gateway, door, interactive sessions carry neither).
  2. WRITE counters (api_calls, tool_calls, input/output/total tokens)
     accumulate in worker memory; ONE small JSON sidecar per node is rewritten
     atomically (tmp + os.replace) per event; no .tmp residue survives.
  3. JOIN  the runner folds the sidecar at the settle seam (_stamp_served, the
     commit-edge stamp every ladder path crosses), deriving the key from the
     result skey, and consumes the file. The fact rides the committed record
     and surfaces through node_facts; a fan-out item carries it through
     commit_item_record like the other committed facts.
  4. FAIL-OPEN (P3's law, peer's law): a missing, corrupt, empty, or
     un-writable telemetry NEVER raises into the worker and NEVER blocks a
     settle; absent evidence reads absent, never a fabricated zero (R2/rule 8).

The integration leg drives the real door -> runner -> fake-child loop: the fake
answers the TELEMETRY-EMIT prompt marker by writing the sidecar from its own
spawn env (the same path contract a real recorder derives), proving the pin
travels, the key joins, and the fold lands on the committed record.

Standalone (NOT pytest): python3 tests/test_node_telemetry_sidecar_wqml6.py
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_HOME = tempfile.mkdtemp(prefix="wf-ntsd-home-")
os.environ["HERMES_HOME"] = _HOME
os.environ["WF_RUNS_ROOT"] = str(Path(_HOME) / "workflows")
os.environ.pop("HERMES_WF_TELEMETRY", None)
os.environ.pop("HERMES_WF_RUN_DIR", None)

_nt_spec = importlib.util.spec_from_file_location("ntsd_wqml6", ROOT / "node_telemetry.py")
nt = importlib.util.module_from_spec(_nt_spec)
_nt_spec.loader.exec_module(nt)

ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


class Ctx:
    """Core-shaped registration surface; optional register_hook failure."""
    def __init__(self, fail=False):
        self.hooks = {}
        self._fail = fail

    def register_hook(self, name, fn):
        if self._fail:
            raise RuntimeError("core refused the registration")
        self.hooks[name] = fn


def setpin(run_dir, key):
    os.environ["HERMES_WF_TELEMETRY"] = key
    os.environ["HERMES_WF_RUN_DIR"] = str(run_dir)


def unpin():
    os.environ.pop("HERMES_WF_TELEMETRY", None)
    os.environ.pop("HERMES_WF_RUN_DIR", None)


KEY = "wf:ntsd:a"
FULL_SKEY = KEY + ":ab12cd34.ee00ff11"   # skey_for's shape: <prefix>:<efp8>.<nonce>
AGG = {"api_calls": 1, "tool_calls": 0}

td = Path(tempfile.mkdtemp(prefix="wf-ntsd-unit-"))

# ---------- 1. gate: registration only where BOTH pins exist -----------------
ctx_off = Ctx()
unpin()
n = nt.register_observer_hooks(ctx_off)
check("no env pins -> zero hooks registered (gateway/door/interactive pay nothing)",
      n == 0 and not ctx_off.hooks, str((n, ctx_off.hooks)))
ctx_only_key = Ctx()
os.environ["HERMES_WF_TELEMETRY"] = KEY
n = nt.register_observer_hooks(ctx_only_key)
check("key pin without the run-dir pin registers nothing (fail-closed gate)",
      n == 0 and not ctx_only_key.hooks, str(ctx_only_key.hooks))
unpin()

setpin(td, KEY)
ctx_on = Ctx()
n = nt.register_observer_hooks(ctx_on)
check("both pins -> exactly the two stock observer hooks",
      n == 2 and set(ctx_on.hooks) == {"post_api_request", "post_tool_call"}, str(ctx_on.hooks))

ctx_broken = Ctx(fail=True)
try:
    n2 = nt.register_observer_hooks(ctx_broken)
    survived = True
except Exception as e:  # noqa: BLE001
    survived, n2 = False, repr(e)
check("a host whose register_hook explodes never sees the exception (fail-open)",
      survived and n2 == 0, str(n2))

# ---------- 2. recorder: accumulate + atomic rewrite --------------------------
api, tool = ctx_on.hooks["post_api_request"], ctx_on.hooks["post_tool_call"]
sc = nt.sidecar_path(td, KEY)
api(usage={"input_tokens": 100, "output_tokens": 40}, model="m", provider="p",
    api_duration=0.1, api_call_count=1, session_id="x", api_mode="anthropic_messages")
one = json.loads(sc.read_text()) if sc.is_file() else {}
check("one post_api_request -> api_calls + usage tokens + total_tokens roll-up",
      one.get("api_calls") == 1 and one.get("input_tokens") == 100
      and one.get("output_tokens") == 40 and one.get("total_tokens") == 140, str(one))
api(usage={"prompt_tokens": 5, "completion_tokens": 2})   # provider-native aliases
tool(tool_name="terminal", status="ok", session_id="x")
tool(tool_name="browser", status="error", error_type="timeout", junk_field=None)
agg = json.loads(sc.read_text()) if sc.is_file() else {}
check("counters accumulate in memory and rewrite the ONE sidecar per event",
      agg.get("api_calls") == 2 and agg.get("tool_calls") == 2
      and agg.get("input_tokens") == 105 and agg.get("output_tokens") == 42
      and agg.get("total_tokens") == 147, str(agg))
residue = [p.name for p in (td / "telemetry").iterdir() if ".tmp" in p.name]
check("atomic rewrite leaves no tmp residue", not residue, str(residue))

api2_ctx = Ctx()
setpin(td, "wf:ntsd:b")
nt.register_observer_hooks(api2_ctx)
api2_ctx.hooks["post_api_request"](usage=None)            # usage-absent shape
b = nt.load(td, "wf:ntsd:b")
check("usage=None counts the api_call and invents no token figures (R2)",
      b == {"api_calls": 1}, str(b))

bad_root = td / "plain-file"
bad_root.write_text("not a dir")
api3_ctx = Ctx()
setpin(bad_root, "wf:ntsd:c")
nt.register_observer_hooks(api3_ctx)
try:
    api3_ctx.hooks["post_api_request"](usage={"input_tokens": 1})
    api3_ctx.hooks["post_tool_call"](status="ok")
    no_raise = True
except Exception as e:  # noqa: BLE001
    no_raise = repr(e)
check("un-writable root: the callbacks suppress telemetry, never raise",
      no_raise is True, str(no_raise))
unpin()

# ---------- 3. load rules: absent telemetry is the designed degradation -------
(td / "telemetry").mkdir(exist_ok=True)
nt.sidecar_path(td, "corrupt").write_bytes(b"{not json{{{")
check("corrupt sidecar loads None", nt.load(td, "corrupt") is None)
nt.sidecar_path(td, "aslist").write_text("[1, 2]")
check("a JSON list (non-dict) loads None", nt.load(td, "aslist") is None)
nt.sidecar_path(td, "empty").write_text("{}")
check("an empty dict loads None (absent, never a zero-illusion)", nt.load(td, "empty") is None)
check("missing sidecar loads None", nt.load(td, "never-written") is None)
nt.sidecar_path(td, "good").write_text(json.dumps(AGG))
check("valid aggregate loads verbatim", nt.load(td, "good") == AGG)

# ---------- 4. fold consumes at settle; corrupt included ----------------------
nt.sidecar_path(td, KEY).write_text(json.dumps(AGG))   # reset the fixture (the recorder used this key)
got = nt.fold_at_settle(td, FULL_SKEY)   # derives the key prefix from the skey
check("fold_at_settle joins by the env key derived from the skey and consumes the file",
      got == AGG and not nt.sidecar_path(td, KEY).exists(), str(got))
check("second fold of a consumed key reads None (settle stays clean)",
      nt.fold_at_settle(td, KEY) is None)
check("fold of a corrupt sidecar returns None and still consumes it (no bound growth)",
      nt.fold_at_settle(td, "corrupt") is None and not nt.sidecar_path(td, "corrupt").exists())
check("fold with no skey is None, never a raise", nt.fold_at_settle(td, None) is None)

# ---------- 5. the production settle seam: _stamp_served ----------------------
import wf  # noqa: E402  (import-time: spec-loads wfcommon only; no spawn)

srun = td / "run-settle"
(srun / "nodes").mkdir(parents=True)
(srun / "telemetry").mkdir()
(srun / "graph.json").write_text(json.dumps({"name": "settle", "nodes": []}))
nt.sidecar_path(srun, KEY).write_text(json.dumps(AGG))
res = wf._stamp_served({"_run": srun}, {"status": "done", "skey": FULL_SKEY})
check("_stamp_served folds the sidecar into the settle result and consumes it",
      res.get("telemetry") == AGG and not nt.sidecar_path(srun, KEY).exists(), str(res.get("telemetry")))
nt.sidecar_path(srun, KEY).write_bytes(b"}garbage{")
res2 = wf._stamp_served({"_run": srun}, {"status": "failed", "skey": FULL_SKEY,
                                         "error_class": "transport"})
check("corrupt sidecar never blocks the settle stamp; telemetry stays absent",
      "telemetry" not in res2 and not nt.sidecar_path(srun, KEY).exists(), str(res2.keys()))
res3 = wf._stamp_served({"_run": srun}, {"status": "done"})
check("no skey -> settle stamp unchanged (fail-open, no invented fact)",
      "telemetry" not in res3, str(res3.keys()))

# ---------- 6. fan-out carry: the canonical per-item commit ships it ----------
irun = td / "run-item"
(irun / "nodes").mkdir(parents=True)
node = {"id": "fan", "type": "agent"}
committed = wf.commit_item_record(irun, node, {"fan": node}, 0, {
    "status": "done", "output": {"result": "x"}, "skey": "wf:ntsd:fan:0:ab12cd34.ee00ff11",
    "attempts": 1, "telemetry": AGG})
disk = json.loads((irun / "nodes" / "fan.0.json").read_text())
check("commit_item_record carries telemetry like the other committed facts",
      committed.get("telemetry") == AGG and disk.get("telemetry") == AGG, str(disk.get("telemetry")))
wf.commit_item_record(irun, node, {"fan": node}, 1, {"status": "done", "output": {"result": "y"}})
disk1 = json.loads((irun / "nodes" / "fan.1.json").read_text())
check("a result without telemetry commits the key ABSENT, never a zero",
      "telemetry" not in disk1, str(sorted(disk1)))

# ---------- 7. the read model surfaces the fact; absent stays absent ----------
import wfcommon as WFC  # noqa: E402

frun = td / "run-facts"
(frun / "nodes").mkdir(parents=True)
(frun / "nodes" / "x.json").write_text(json.dumps({"status": "done", "telemetry": AGG}))
facts = WFC.node_facts(frun, "x")
check("node_facts surfaces a committed telemetry verbatim",
      isinstance(facts, dict) and facts.get("telemetry") == AGG, str(facts))
(frun / "nodes" / "y.json").write_text(json.dumps({"status": "done"}))
facts_y = WFC.node_facts(frun, "y")
check("node_facts keeps its byte-identical shape when telemetry is absent",
      isinstance(facts_y, dict) and "telemetry" not in facts_y, str(sorted(facts_y or {})))

# ---------- 8. end-to-end: door -> runner -> fake child -> join -> fact -------
door_spec = importlib.util.spec_from_file_location("wf_door_wqml6", ROOT / "__init__.py")
door = importlib.util.module_from_spec(door_spec)
door_spec.loader.exec_module(door)
sys.path.insert(0, str(ROOT / "tests"))
import wf_test_isolation as _iso; _iso.install(door)  # noqa: E402

home2 = Path(tempfile.mkdtemp(prefix="wf-ntsd-e2e-"))
runs2 = home2 / "runs"
runs2.mkdir()
fake2 = home2 / "fake-hermes"
shutil.copy(ROOT / "tests" / "fake_hermes.py", fake2)
os.chmod(fake2, 0o755)
env2 = {**os.environ, "HERMES_HOME": str(home2), "WF_RUNS_ROOT": str(runs2),
        "HERMES_WF_HERMES_BIN": str(fake2)}
env2.pop("WORKFLOW_MAX_SEATS", None)
rec = {}
with patch.dict(os.environ, env2, clear=True):
    resp = door.act_run({"graph": {"name": "nt-e2e",
                                   "nodes": [{"id": "a", "type": "agent", "goal": "TELEMETRY-EMIT"}]}})
    run_dir = None
    if isinstance(resp, dict) and resp.get("run_id"):
        run_dir = runs2 / resp["run_id"]
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            p = run_dir / "nodes" / "a.json"
            if p.is_file():
                rec = json.loads(p.read_text())
                if rec.get("status") in ("done", "partial", "failed"):
                    break
            time.sleep(0.25)
check("integration: the run settles done", isinstance(resp, dict) and bool(run_dir)
      and rec.get("status") == "done", str(resp)[:200] + str(rec.get("status")))
FAKE_AGG = {"api_calls": 3, "tool_calls": 2, "input_tokens": 100,
            "output_tokens": 40, "total_tokens": 140}
check("integration: the spawn env pin reached the child, the sidecar joined at settle",
      rec.get("telemetry") == FAKE_AGG, str(rec.get("telemetry")))
tdir = (run_dir / "telemetry") if run_dir else None
check("integration: the folded sidecar was consumed (no unbounded run-dir growth)",
      tdir is not None and (not tdir.exists() or not list(tdir.glob("*.json"))),
      str(list(tdir.glob("*")) if tdir and tdir.exists() else []))
facts_e = WFC.node_facts(run_dir, "a") if run_dir else None
check("integration: status read model (node_facts) surfaces the fact",
      isinstance(facts_e, dict) and facts_e.get("telemetry") == FAKE_AGG, str(facts_e))

shutil.rmtree(_HOME, ignore_errors=True)
shutil.rmtree(td, ignore_errors=True)
shutil.rmtree(home2, ignore_errors=True)
print("RESULT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
