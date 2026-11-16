#!/usr/bin/env python3
"""est-2lcp8: a lane kill must END the whole child tree of the killed attempt.

Reproduces run 20261116-131135's escape: the review.1 item record was final
killed at 13:59:58Z, yet the lane's detached (setsid) leftover writer posted
marker 6919844319 at 14:52:08Z and squash-merged #541 at 14:52:33Z. killpg on
the seat's own group cannot reach a setsid grandchild, so every kill seam must
snapshot the seat's subtree and kill + PROVE dead every attributed descendant
(#61c channels, #448 reap settle) at attempt end.

Shape: fan-out node "fan" (one item; child = fake seat_timing holding 8 s that
backgrounds a detached writer appending at t+FAKE_WRITER_DELAY=5) plus a plain
sibling node "b" (same hold) so the run outlives the writer's deadline — a
killed lane ends its tree, not the run. act_kill(node="fan") then:
  (a) the writer file NEVER gains a line (the writer dies at the kill seam,
      before its t+5 deadline — no post-hoc action);
  (b) the killed item record matches process reality: the writer pid is
      counted (tree_descendants), death is proven (tree_proof=dead), and the
      writer is really dead the instant the record is terminal.
RED before the fix: the writer escapes every kill channel until runner exit
(~t+8), appends at t+5 post-hoc, and the record carries no descendant proof.
"""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))
ROOT = BUILD.parent
sys.path.insert(0, str(ROOT))
HOME = BUILD / "home_2lcp8"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
RUNS = HOME / "workflows"
FAKE = str(BUILD / "fake")
LOG = BUILD / "fake_2lcp8.log"
WRITER = BUILD / "writer_2lcp8.txt"
WPIDS = BUILD / "writer_2lcp8.pids"

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1

def load_door():
    spec = importlib.util.spec_from_file_location("killtree_door", ROOT / "__init__.py")
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    return door

def writer_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        st = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (FileNotFoundError, IndexError, OSError):
        return False
    return not st.startswith("Z")

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
for f in (LOG, WRITER, WPIDS):
    if f.exists():
        f.unlink()

rid = "2lcp8-killtree"
r = RUNS / rid
(r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
nodes = [{"id": "fan", "type": "agent", "timeout": 60,
          "fanout": {"items": ["541"], "goal": "PROCESS item {index} DETACH-WRITER"}},
         {"id": "b", "type": "agent", "goal": "sibling lane"}]
(r / "graph.json").write_text(json.dumps({"name": rid, "nodes": nodes}))
(r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 60}))

env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS), FAKE_LOG=str(LOG),
           FAKE_MODE="seat_timing", FAKE_SEAT_HOLD="8",
           FAKE_DETACH_WRITER=str(WRITER), FAKE_WRITER_DELAY="5", FAKE_WRITER_PIDS=str(WPIDS))
proc = subprocess.Popen([sys.executable, str(ROOT / "wf.py"), "run", rid], env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

t0 = time.time()
while time.time() - t0 < 60:
    if LOG.exists() and len(LOG.read_text().splitlines()) >= 2 and WPIDS.exists():
        break
    time.sleep(0.1)
check("fan child (with detached writer) and sibling both in flight",
      LOG.exists() and len(LOG.read_text().splitlines()) >= 2 and WPIDS.exists())
wpid = int(WPIDS.read_text().splitlines()[0]) if WPIDS.exists() else -1

door = load_door()
kr = door.act_kill({"run_id": rid, "node": "fan"})
check("act_kill accepts the node-targeted kill", kr.get("ok") is True, json.dumps(kr)[:200])

rec = {}
while time.time() - t0 < 60:
    p = r / "nodes" / "fan.0.json"
    if p.exists():
        rec = json.loads(p.read_text())
        if rec.get("error_class") == "killed":
            break
    time.sleep(0.1)
check("item record terminal error_class=killed", rec.get("error_class") == "killed",
      json.dumps(rec)[:300])
check("no live descendant when the killed record became final (writer dead at the seam)",
      not writer_alive(wpid), f"writer pid {wpid} still live at judgment")

try:
    proc.wait(timeout=240)
except subprocess.TimeoutExpired:
    proc.kill()
    check("run finished within 240s", False, "timeout")

# The writer's own deadline (t+5) has passed BEFORE the run could end
# (sibling holds 8 s): any writer that survived the kill had appended by now.
time.sleep(max(0.0, t0 + 6.5 - time.time()))
check("(a) no post-kill writer line",
      (not WRITER.exists()) or WRITER.read_text() == "",
      WRITER.read_text() if WRITER.exists() else "")
check("(b) record counts the orphaned writer",
      wpid in (rec.get("tree_descendants") or []), json.dumps(rec.get("tree_descendants")))
check("(b) record proves the child tree dead", rec.get("tree_proof") == "dead",
      str(rec.get("tree_proof")))
rec_b = json.loads((r / "nodes" / "b.json").read_text()) if (r / "nodes" / "b.json").exists() else {}
check("sibling lane b kept running to done (kill is lane-scoped)",
      rec_b.get("status") == "done", json.dumps(rec_b)[:200])

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
