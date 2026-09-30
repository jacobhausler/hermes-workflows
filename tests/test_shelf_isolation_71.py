#!/usr/bin/env python3
"""#71 regression pin: the shelf is a live production surface — no test may write
it, and nothing may rely on HERMES_HOME alone to sandbox door saves/runs.

Three parts, standalone (no pytest):
  S1 tripwire — snapshot the door's RESOLVED shelf + runs root, perform in-process
     door writes (save, run) under a pinned WF_RUNS_ROOT, assert the resolved
     production paths gained nothing and the writes landed in the sandbox.
  S2 leak-proof — simulate the accident that caused the 09-30 pollution: drop the
     WF_RUNS_ROOT pin and set the context-local home override (what a lane process
     carries). A save must then land under the OVERRIDE root, not where HERMES_HOME
     points — the proof that HERMES_HOME alone is not a sandbox and the pin is the
     only defense. The canary is cleaned up with the temp home.
  S3 static audit — every test file that calls door write verbs in-process must
     pin WF_RUNS_ROOT; a file reintroducing the leak pattern fails here RED.
"""
import importlib.util, json, os, shutil, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


sys.path.insert(0, "/opt/hermes")
import hermes_constants as hc  # noqa: E402

spec = importlib.util.spec_from_file_location("hw71", str(BUILD / "__init__.py"))
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)

G = {"name": "shelf-pollution-probe", "nodes": [{"id": "a", "type": "agent", "goal": "go"}]}

# Snapshot what the door resolves RIGHT NOW — in a lane/suite process this is the
# shared estate shelf; that is the surface nothing may gain entries on.
PROD_LIB = door.library_root()
PROD_RUNS = door.runs_root()
PROD_LIB_SNAP = {p.name: p.read_bytes() for p in PROD_LIB.glob("*.json")} if PROD_LIB.exists() else {}
PROD_RUNS_SNAP = {p.name for p in PROD_RUNS.iterdir()} if PROD_RUNS.exists() else set()

with tempfile.TemporaryDirectory(prefix="shelf71-") as td:
    sandbox = Path(td)
    saved_env = {k: os.environ.get(k) for k in ("WF_RUNS_ROOT", "HERMES_HOME")}
    try:
        # ---- S1: pinned sandbox keeps the production shelf untouched ----
        os.environ["WF_RUNS_ROOT"] = str(sandbox / "runs")
        os.environ["HERMES_HOME"] = str(sandbox / "home")

        r = json.loads(door.handle({"action": "save", "graph": G, "name": "shelf71-entry"}))
        check("S1a save succeeds under pin", r.get("saved") == "shelf71-entry", json.dumps(r))
        check("S1b save landed in sandbox", (sandbox / "runs" / "library" / "shelf71-entry.json").exists())
        lib_after = {p.name: p.read_bytes() for p in PROD_LIB.glob("*.json")} if PROD_LIB.exists() else {}
        runs_after = {p.name for p in PROD_RUNS.iterdir()} if PROD_RUNS.exists() else set()
        check("S1c production shelf gained NOTHING", lib_after == PROD_LIB_SNAP,
              f"new: {sorted(set(lib_after) - set(PROD_LIB_SNAP))}")
        stray_runs = {n for n in runs_after - PROD_RUNS_SNAP if "shelf71" in n or "pollution" in n}
        check("S1d no probe run dirs in the production runs root", not stray_runs, f"stray: {sorted(stray_runs)}")

        # ---- S2: without the pin, the context-local override outranks HERMES_HOME ----
        override_home = sandbox / "override-home"
        override_home.mkdir()
        token = hc.set_hermes_home_override(override_home)
        try:
            del os.environ["WF_RUNS_ROOT"]
            os.environ["HERMES_HOME"] = str(sandbox / "decoy-home")  # the test's naive claim
            r = json.loads(door.handle({"action": "save", "graph": G, "name": "shelf71-canary"}))
            canary_override = override_home / "workflows" / "library" / "shelf71-canary.json"
            canary_decoy = sandbox / "decoy-home" / "workflows" / "library" / "shelf71-canary.json"
            check("S2a save resolves via the OVERRIDE, not HERMES_HOME",
                  canary_override.exists() and not canary_decoy.exists(),
                  f"override={canary_override.exists()} decoy={canary_decoy.exists()} — "
                  "this is exactly how the 09-30 estate pollution happened")
        finally:
            hc.reset_hermes_home_override(token)
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

# ---- S3: static audit — in-process door writers must pin WF_RUNS_ROOT ----
import re
pattern = re.compile(r"(hw|door|plugin|mod|m|d)\.(handle|act_save|act_run|act_delete|act_amend)\(")
leakers = []
for p in sorted(HERE.glob("*.py")):
    if p.name == Path(__file__).name or p.name == "fake_hermes.py":
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    if pattern.search(t) and "WF_RUNS_ROOT" not in t:
        leakers.append(p.name)
check("S3 every in-process door writer pins WF_RUNS_ROOT", not leakers, f"leakers: {leakers}")

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
