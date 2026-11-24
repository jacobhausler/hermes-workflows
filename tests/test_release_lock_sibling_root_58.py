#!/usr/bin/env python3
"""#58 write-verb law at the door: release_lock REFUSES a sibling-root run.

Cross-root READ answers from the hit with a resolved_via warning (pinned by
test_door_sibling_root_58.py); WRITE verbs never cross roots. The fixture is
a genuinely healable wedge (live flock holder, zero-row kernel-ledger seam,
dead lease), so the refusal is non-vacuous: the CONTROL calls the same heal
authority directly on the sibling dir and it DOES heal with a stranded rename
— only the door's sibling branch protects the foreign root. RED-first proof:
delete the resolved_via branch in act_release_lock and R3 flips to FAIL (the
heal delegates and renames).

Run (suite-style, fresh private root per invocation):
  env HERMES_HOME=$(mktemp -d) WF_RUNS_ROOT=$(mktemp -d) python3 tests/test_release_lock_sibling_root_58.py
"""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path
BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).resolve().parent.parent)
os.environ["WF_TEST_BUILD"] = str(BUILD)
HOME = Path(__file__).resolve().parent / "home-58-relsib"
shutil.rmtree(HOME, ignore_errors=True); HOME.mkdir()
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")            # #71 law: env pin
led = HOME / "zero-ledger"; led.write_text("")                  # field shape: the
os.environ["WF_PROC_LOCKS_PATH"] = str(led)                     # ledger knows no holder
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402
SIB = HOME / "profiles" / "seatA" / "workflows" / "relsib58"    # lives ONLY in a sibling root
(SIB / "nodes").mkdir(parents=True)
(SIB / "graph.json").write_text(json.dumps({"nodes": [{"id": "a", "type": "agent", "goal": "LIST: go"}]}))
(SIB / "run.json").write_text(json.dumps({"name": "relsib58"}))
(SIB / "runner.lease").write_text(json.dumps({"pid": 999993, "boottime": 1, "at": time.time() - 3600}))
(HOME / "h.py").write_text("import fcntl,os,signal,sys\nf=os.open(sys.argv[1],os.O_CREAT|os.O_RDWR,0o644)\nfcntl.flock(f,fcntl.LOCK_EX)\nopen(sys.argv[2],'w').write(str(os.fstat(f).st_ino))\nprint('held',flush=True)\nsignal.pause()\n")
ready = HOME / "held"
p = subprocess.Popen([sys.executable, str(HOME / "h.py"), str(SIB / "runner.lock"), str(ready)],
                     stdout=subprocess.PIPE, text=True)
assert p.stdout.readline().strip() == "held", "sibling holder failed to take the flock"
ino = int(ready.read_text())                                    # the ready inode lands first
spec = importlib.util.spec_from_file_location("hw58rl", BUILD / "__init__.py")
door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
try: import wf_test_isolation as _iso71; _iso71.install(door)   # #71 writer pin
except Exception: pass
def call(**a): return json.loads(door.handle(a))
ok = True
def check(label, cond, detail=""):
    global ok; print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}")); ok = ok and bool(cond)
st = call(action="status", run_id="relsib58")
rel = call(action="release_lock", run_id="relsib58")
check("R1 cross-root READ answers from the hit, resolved_via note present", "error" not in st and st.get("resolved_via") == str(SIB) and "resolved_via_note" in st, json.dumps(st))
check("R2 release_lock REFUSES the sibling root (verbatim #58 error)", rel.get("ok") is not True and "sibling root" in str(rel.get("error")) and "must be issued from the owning home" in str(rel.get("error")), json.dumps(rel))
check("R3 the refusal mutated NOTHING (inode byte-same, zero stranded renames)", (SIB / "runner.lock").exists() and os.stat(SIB / "runner.lock").st_ino == ino and not list(SIB.glob("runner.lock.stranded-*")), json.dumps(rel))
check("R4 CONTROL: direct heal authority DOES heal the same wedge (non-vacuous)", (ctl := wfcommon.heal_wedged_runner_lock(SIB)).get("ok") is True and ctl.get("reason") == "healed" and len(list(SIB.glob("runner.lock.stranded-*"))) == 1, json.dumps(ctl))
p.kill(); p.wait(); shutil.rmtree(HOME, ignore_errors=True)
print(("" if ok else "FAILURES PRESENT ") + "DONE"); sys.exit(0 if ok else 1)
