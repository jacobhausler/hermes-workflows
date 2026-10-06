#!/usr/bin/env python3
"""est-g2xx follow-up — the global seat-ticket dir <runs_root>/.seats is NEVER a run.

The seat semaphore (test_seat_live_g2xx.py) keeps its tickets under
<runs_root>/.seats. Every runs-root enumeration — the door's `list`, the
dashboard read model, the card-enforcement outstanding scan — must skip it (and
any other dot-dir) by construction, through ONE shared helper
(wfcommon.iter_run_dirs), not by the accident that .seats happens to lack a
graph.json today. The adversarial case below plants a graph.json INSIDE .seats:
a name-blind enumeration would list it as a run.

Run: PYTHONPATH=/opt/hermes python3 tests/test_seats_not_a_run_g2xx.py
"""
import importlib.util, json, os, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HOME = HERE / "home-seats-not-run"
shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir()
RUNS = HOME / "workflows"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)
os.environ["HERMES_WF_HERMES_BIN"] = str(HERE / "fake")
(HOME / "config.yaml").write_text("model:\n  default: seat-default\n")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# one real-shaped run + an adversarial .seats dir that LOOKS like a run
GRAPH = {"name": "s", "nodes": [{"id": "a", "type": "agent", "goal": "x", "max_turns": 1}]}
run = RUNS / "20261006-000000-s"
(run / "nodes").mkdir(parents=True)
(run / "graph.json").write_text(json.dumps(GRAPH))
(run / "run.json").write_text(json.dumps({"name": "s"}))
seats = RUNS / ".seats"
seats.mkdir()
(seats / "123.json").write_text(json.dumps({"pid": 1}))
(seats / "graph.json").write_text(json.dumps(GRAPH))      # adversarial
(seats / "run.json").write_text(json.dumps({"name": "s"}))
(RUNS / "stray.txt").write_text("not a dir")

# (1) the shared helper
have = hasattr(wfcommon, "iter_run_dirs")
check("wfcommon exposes iter_run_dirs", have)
if have:
    got = [p.name for p in wfcommon.iter_run_dirs(RUNS)]
    check("iter_run_dirs yields the run, skips .seats and non-dirs", got == [run.name], got)
    check("iter_run_dirs on a missing root is empty", list(wfcommon.iter_run_dirs(HOME / "nope")) == [])

# (2) door `list` never shows .seats
spec = importlib.util.spec_from_file_location("door_seats", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
import wf_test_isolation as _iso; _iso.install(door)
lst = json.loads(door.handle({"action": "list"}))
ids = [r.get("run_id") for r in lst.get("runs", [])]
check("door list omits .seats", ".seats" not in ids, ids)
check("door list still shows the real run", run.name in ids, ids)

# (3) source pin: no product runs-root enumeration bypasses the helper
for rel, fn in (("__init__.py", "act_list"), ("dashboard/plugin_api.py", "_list_runs"),
                ("card_enforcement.py", "_outstanding")):
    src = (ROOT / rel).read_text(encoding="utf-8")
    m = re.search(rf"^def {fn}\(.*?(?=^def |\Z)", src, re.S | re.M)
    body = m.group(0) if m else ""
    check(f"{rel}:{fn} enumerates via iter_run_dirs, not root.iterdir()",
          bool(body) and "iter_run_dirs(" in body and "root.iterdir()" not in body)

shutil.rmtree(HOME, ignore_errors=True)
print("ALL PASS" if ok else "SOME FAIL")
raise SystemExit(0 if ok else 1)
