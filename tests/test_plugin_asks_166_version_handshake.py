#!/usr/bin/env python3
"""est-2ek.1.166: version handshake — the plugin reports its OWN version
(plugin.yaml) and an optional graph key `requires_plugin` fails a STALE runner
LOUDLY AT ARM TIME, naming both versions (spool key e6e55416cd78c9bd: a stale
seat ran hermes-workflows 0.8.0 and a 1.0.x graph died at 03:00 on a
boolean schema the old door never saw coming).

Three surfaces:
  * door run/amend: graph.requires_plugin > runner version => refusal BEFORE any
    write/spawn, error names the runner version AND the required minimum;
  * run.json stamps plugin_version (the arming door's truth) and act_status
    passes it back, so a stale seat is visible without opening a run dir;
  * the runner itself re-checks at boot (old door + new runner still safe) and
    dies typed, naming both versions in runner_exit.
Coarse >= comparison (dot-integer tuples); absent key = no check; a malformed
value is a named validation error, never a crash.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
ROOT = BUILD.parent
sys.path.insert(0, str(ROOT))
HOME = BUILD / "home_166"
env = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(BUILD / "fake_166.log"))
FAKE = str(BUILD / "fake")

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
os.environ["HERMES_WF_HERMES_BIN"] = FAKE

spec = importlib.util.spec_from_file_location("asks166_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)

import re
m = re.search(r"(?m)^version:\s*(\S+)\s*$", (ROOT / "plugin.yaml").read_text())
RUNNER_V = m.group(1)
check("(0) plugin.yaml carries the runner version", bool(RUNNER_V), RUNNER_V)

G = {"name": "asks166", "nodes": [{"id": "a", "type": "agent", "goal": "GO asks166"}]}

# ---- (1) RED: stale runner refuses AT ARM TIME naming BOTH versions ----
bad = door.act_run({"graph": dict(G, requires_plugin="99.0.0")})
err = bad.get("error", "")
check("(1) requires_plugin=99.0.0 refuses immediately", "error" in bad, json.dumps(bad)[:200])
check("(1) refusal names runner-version and required",
      RUNNER_V in err and "99.0.0" in err and "requires_plugin" in err, err[:300])
check("(1) refused before any run dir was created",
      not any((HOME / "workflows").glob("*")) if (HOME / "workflows").exists() else True)

# ---- (2) coarse >= OK: a satisfied requirement launches and reports ----
ok = door.act_run({"graph": dict(G, requires_plugin="0.1.0"), "dry_run": True})
check("(2) satisfied requires_plugin passes (dry_run ok)", ok.get("ok") is True,
      json.dumps(ok)[:200])

real = door.act_run({"graph": dict(G, requires_plugin="0.1.0")})
rid = real.get("run_id")
check("(2) armed run carries requires_plugin provenance", bool(rid), real)
if rid:
    meta = json.loads((HOME / "workflows" / rid / "run.json").read_text())
    check("(2) run.json reports the plugin's own version (plugin.yaml)",
          meta.get("plugin_version") == RUNNER_V, json.dumps(meta)[:200])
    # let the runner finish so status is terminal
    t = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", rid],
                       env={**env, "WF_RUNS_ROOT": str(HOME / "workflows")},
                       capture_output=True, text=True, timeout=120)
    st = door.act_status({"run_id": rid})
    check("(2) status reports the plugin version too",
          st.get("plugin_version") == RUNNER_V, json.dumps(st)[:200])

# ---- (3) absent key = byte-identical old behavior (no key forced, no refusal) ----
plain = door.act_run({"graph": dict(G, name="asks166-plain"), "dry_run": True})
check("(3) no requires_plugin: unchanged pass", plain.get("ok") is True, json.dumps(plain)[:150])

# ---- (4) malformed value is a NAMED validation error, never a crash ----
bad4 = door.act_run({"graph": dict(G, name="asks166-bad", requires_plugin="latest")})
check("(4) non-numeric requires_plugin rejected at validation",
      "error" in bad4 and "requires_plugin" in json.dumps(bad4), json.dumps(bad4)[:250])

# ---- (5) runner-side boot check: an armed run whose graph demands a future
# ---- plugin dies typed at boot, naming both versions, zero children ----
r5 = HOME / "workflows" / "asks166-stale"
if r5.exists():
    shutil.rmtree(r5)
(r5 / "nodes").mkdir(parents=True)
(r5 / "gates").mkdir()
(r5 / "graph.json").write_text(json.dumps(
    {"name": "asks166-stale", "requires_plugin": "99.0.0",
     "nodes": [{"id": "a", "type": "agent", "goal": "GO asks166-stale"}]}))
(r5 / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "node_timeout": 30}))
fake_log5 = BUILD / "fake_166_stale.log"
fake_log5.write_text("")
p5 = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", "asks166-stale"],
                    env=dict(env, FAKE_LOG=str(fake_log5), WF_RUNS_ROOT=str(HOME / "workflows")),
                    capture_output=True, text=True, timeout=60)
out5 = p5.stdout
rx = json.loads((r5 / "runner_exit.json").read_text()) if (r5 / "runner_exit.json").exists() else {}
check("(5) stale runner refuses at boot, typed",
      "WORKFLOW_FAILED" in out5, out5[:200])
check("(5) boot refusal names BOTH versions",
      RUNNER_V in json.dumps(rx) + out5 and "99.0.0" in json.dumps(rx) + out5,
      json.dumps(rx)[:250])
check("(5) refused with ZERO children spawned",
      fake_log5.read_text().strip() == "", fake_log5.read_text()[:120])

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
