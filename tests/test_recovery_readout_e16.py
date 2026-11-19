#!/usr/bin/env python3
"""E16 (bd_2026-11-13-4hc) — the recovery-state readout.

The SIGKILL/torn-import family's open question: no command rendered "what
effects are durable, which record is torn, what re-drive order is idempotent".
The fenced-journal candidate now answers it from the journal ALONE:

  (1) deterministic seeded journal: wf.recovery_state names the exact applied
      set (committed rows valid under the current graph), the torn line
      (never fully landed -> UNPROVEN, not absent), the unprovable rows
      (node-gone / amended-efp / not-a-row) and the topological safe-redrive
      order with per-node reconcile/fresh modes;
  (2) post-kill integration: a real runner driven by the effect-executing fake
      child (FAKE_MODE=effect_once, journals under the SIDECAR pin),
      SIGKILLed mid-attempt — then the single query verb `wf.py recover` over
      the dead run prints the readout and its applied set matches the journal
      byte-for-byte (the applied_set_exact shape s27/s41 score).

Standalone, stdlib-only:
  PYTHONPATH=<clone> python3 tests/test_recovery_readout_e16.py
"""
import json, os, shutil, signal, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
sys.path.insert(0, str(BUILD))
import wf

HOME = HERE / "home-rece16"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " if cond is False else "ERR  ") + label
          + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}

# ------------------------------------------------------- (1) seeded journal
shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
run1 = RUNS / "e16-seeded"
(run1 / "nodes").mkdir(parents=True)
nodes = [
    {"id": "alpha", "type": "agent", "goal": "a", "schema": SCHEMA},
    {"id": "beta", "type": "agent", "goal": "b", "after": ["alpha"], "schema": SCHEMA},
    {"id": "gamma", "type": "agent", "goal": "c", "after": ["beta"], "schema": SCHEMA},
]
(run1 / "graph.json").write_text(json.dumps({"name": "e16-seeded", "nodes": nodes}))
byid = {n["id"]: n for n in nodes}
alpha_efp = wf.efp(byid, byid["alpha"])

# alpha committed done (efp-stamped): it must NOT appear in safe_redrive.
(run1 / "nodes" / "alpha.json").write_text(json.dumps(
    {"status": "done", "output": {"result": "ok"}, "efp": alpha_efp,
     "fp_rule_version": wf.FP_RULE_VERSION}))
# journal: valid alpha row, amended-efp beta row, node-gone row, torn line,
# and a parseable line that is not a row.
(run1 / "side_effects.jsonl").write_text(
    json.dumps({"node": "alpha", "kind": "push", "key": "br-1", "evidence": "sha", "spawn": 1,
                "node_efp": alpha_efp}) + "\n"
    + json.dumps({"node": "beta", "kind": "pr", "key": "pr-9", "evidence": "url", "spawn": 1,
                  "node_efp": "0" * 16}) + "\n"
    + json.dumps({"node": "vanished", "kind": "mail", "key": "m", "evidence": "e",
                  "spawn": 2, "node_efp": alpha_efp}) + "\n"
    + '{"node": "gamma", "kind": "push", "key": "br-2", "evid'      # torn: no newline, cut
    + "\n" + json.dumps({"nope": True}) + "\n")
rs = wf.recovery_state(run1, byid)
check("1 applied names exactly the valid row",
      [(r["node"], r["kind"], r["key"]) for r in rs["applied"]] == [("alpha", "push", "br-1")],
      json.dumps(rs["applied"]))
check("1 torn names the line that never landed",
      len(rs["torn"]) == 1 and rs["torn"][0]["line"] == 4
      and rs["torn"][0]["head"].startswith('{"node": "gamma"'),
      json.dumps(rs["torn"]))
reasons = {(r["node"], r["reason"]) for r in rs["unprovable"]}
check("1 unprovable carries amended-efp, node-gone and not-a-row",
      reasons == {("beta", "amended-efp"), ("vanished", "node-gone"), (None, "not-a-row")},
      json.dumps(rs["unprovable"]))
order = [(e["node"], e["mode"], e["committed_effects"]) for e in rs["safe_redrive"]]
check("1 safe_redrive is topological over unfinished only, modes honest",
      order == [("beta", "fresh", 0), ("gamma", "fresh", 0)], json.dumps(order))

# ----------------------------------------------- (2) post-kill via the CLI
RUN_ID = "e16-kill"
run2 = RUNS / RUN_ID
(run2 / "nodes").mkdir(parents=True); (run2 / "gates").mkdir()
nodes2 = [
    {"id": "seed", "type": "agent", "goal": "side effect EFFECTKEY=E16-A", "schema": SCHEMA},
    {"id": "after", "type": "agent", "goal": "follow-on", "after": ["seed"], "schema": SCHEMA},
]
(run2 / "graph.json").write_text(json.dumps({"name": RUN_ID, "nodes": nodes2}))
(run2 / "run.json").write_text(json.dumps(
    {"hermes_bin": FAKE, "concurrency": 2, "node_timeout": 30}))
env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
           FAKE_LOG=str(HOME / "fake.log"),
           FAKE_MODE="effect_once", FAKE_EFFECT_FILE=str(HOME / "ledger.txt"),
           FAKE_EFFECT_HOLD="30",          # stay alive so the kill is the seam
           FAKE_PID_LOG=str(HOME / "pids.txt"))
p = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", RUN_ID],
                     env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def wait_for(pred, timeout=30, tick=0.1):
    end = time.time() + timeout
    while time.time() < end:
        if pred():
            return True
        time.sleep(tick)
    return False
journal = run2 / "side_effects.jsonl"
have = wait_for(lambda: journal.exists() and journal.read_text().strip())
os.kill(p.pid, signal.SIGKILL); p.wait()
try:
    for pid in (HOME / "pids.txt").read_text().split():
        os.kill(int(pid), signal.SIGKILL)
except OSError:
    pass
check("2 setup: the child committed a journal row before the kill", have)
out = subprocess.run([sys.executable, str(BUILD / "wf.py"), "recover", RUN_ID],
                     env=env, capture_output=True, text=True)
check("2 recover verb exits 0 with one JSON line",
      out.returncode == 0, out.stdout + out.stderr)
rj = json.loads(out.stdout) if out.returncode == 0 else {}
journal_rows = [json.loads(l) for l in journal.read_text().splitlines() if l.strip()]
check("2 applied_set_exact: readout == every valid journal row, no more",
      [(r["node"], r["kind"], r["key"]) for r in rj.get("applied", [])]
      == [(r["node"], r["kind"], r["key"]) for r in journal_rows],
      out.stdout)
order2 = [(e["node"], e["mode"], e["committed_effects"]) for e in rj.get("safe_redrive", [])]
check("2 post-kill re-drive order: seed reconcile (effect durable, record uncommitted) then after",
      order2 == [("seed", "reconcile", 1), ("after", "fresh", 0)], json.dumps(order2))
check("2 torn/unprovable read empty on a clean-kill journal",
      rj.get("torn") == [] and rj.get("unprovable") == [], json.dumps(rj))

# refusing verb on an unknown run
out2 = subprocess.run([sys.executable, str(BUILD / "wf.py"), "recover", "no-such-run"],
                      env=env, capture_output=True, text=True)
check("2 unknown run refuses loudly", out2.returncode == 1 and "REFUSED" in out2.stdout,
      out2.stdout)

shutil.rmtree(HOME, ignore_errors=True)
print("RESULT " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
