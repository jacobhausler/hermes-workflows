#!/usr/bin/env python3
"""est-t3m6 / issue #104: workflow-mechanic admission-gate design-contract tests.

The admission gate itself as an executable check. Three layers:

L1 ENGINE MECHANICS (runs today, always): a mechanic-shaped probe graph is run
   through the real runner with the recording fake door. Proves the three
   properties the mechanic's consent architecture relies on:
     - gates with deny defaults auto-release on hold_timeout by timer
       (never silent, never held-forever);
     - a deny (or default) answer routes arms to the self-no-op verdict,
       and the run completes with ZERO mutating door calls and ZERO writes;
     - audit-mode booleans (all false) SKIP every gate (gate.skipped) and
       no arm child is ever spawned — audit-only cannot enter a side-effect
       arm (clause b/c).
L2 LEDGER HONESTY (runs today): receipts/workflow-mechanic/admission-104.json
   must carry the blind-holdout section with run.json.status blinded
   (clause a: state derived from events + node records + runner_exit only),
   every sealed-case digests present, and battery counts as measured ints.
L3 CANDIDATE LAWS (runs when a vendored graph is offered): set
   WF_MECHANIC_CANDIDATE=/path/to/graph.json (a vendoring PR MUST set it in CI
   — the gate is red, not skipped, when a candidate is present and violates).
   Asserts engine validation + deny-default + own-gate-only + hold_timeout
   bounds on every side-effect arm. Without a candidate this layer reports
   GATE-CLOSED and the file passes — the gate exists and holds; absence is
   the pre-admission state, never a fabricated pass.

See references/mechanic-battle-cards.md for the consent/diagnosis cards and
issue #104 for the design contract this encodes.
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

TMP = Path(tempfile.mkdtemp(prefix="mechg-", dir=str(ROOT / "tests")))
for k in [k for k in os.environ if k.startswith("HERMES_SESSION") or k == "HERMES_UI_SESSION_ID"]:
    os.environ.pop(k)
os.environ["HERMES_HOME"] = str(TMP / "home")
os.environ["WF_RUNS_ROOT"] = str(TMP / "workflows")
(TMP / "home").mkdir(parents=True, exist_ok=True)  # fake door's --continue needs a home

spec = importlib.util.spec_from_file_location("door_mechg", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)
import wfcommon as common

FAKE = str(ROOT / "tests" / "fixtures" / "11-fake-hermes.py")
os.environ["HERMES_WF_HERMES_BIN"] = FAKE

fails = 0


def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1


def until(pred, seconds=30):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(0.05)
    return False


def events_of(run_dir):
    out = []
    try:
        for line in (run_dir / "events.jsonl").open():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    except FileNotFoundError:
        pass
    return out


GATES = [("gate_local", ["deny_local", "approve_local_writes"], "deny_local",
          "local_fix_available"),
         ("gate_rerun", ["deny_rerun", "approve_fresh_run"], "deny_rerun",
          "rerun_recommended"),
         ("gate_outbound", ["deny_outbound", "approve_issue", "approve_pr"], "deny_outbound",
          "outbound_issue_recommended")]

ARM_NOOP = ('Read the gate answer in ## Inputs. If it is NOT one of the exact approve '
            'options: reply {"verdict":"skipped not approved"} and stop. Never touch the '
            'live store, never launch, never write. JSON: {"verdict":"skipped not approved"}')


def probe_graph(booleans):
    synth_json = json.dumps({"audit_mode": not any(booleans.values()), **booleans,
                             "classes_final": ["cancelled_by_stop"],
                             "outbound_pr_recommended": booleans.get("outbound_pr_recommended", False)})
    nodes = [{"id": "synth", "type": "agent",
              "goal": "Mechanic synth stub. JSON: " + synth_json}]
    for gid, opts, deny, flag in GATES:
        nodes.append({"id": gid, "type": "gate", "after": ["synth"],
                      "when": f"out.synth.{flag} == True", "on_skip": "prune",
                      "question": f"Authorize {gid}?", "options": opts,
                      "default_option": deny, "hold_timeout": 3})
        nodes.append({"id": gid.replace("gate_", "arm_"), "type": "agent",
                      "after": [gid], "goal": ARM_NOOP})
    return {"name": "mechg-probe", "nodes": nodes}


def run_probe(graph):
    res = door.act_run({"graph": graph})
    assert "run_id" in res, res
    return Path(os.environ["WF_RUNS_ROOT"]) / res["run_id"], res["run_id"]


# ---------------------------------------------------------------- L1
ARM_FLAGS_TRUE = {"local_fix_available": True, "rerun_recommended": True,
                  "outbound_issue_recommended": True, "outbound_pr_recommended": True}
# sentinel: a protected file a side-effect arm would have to touch to matter
SENTINEL = TMP / "sentinel.txt"
SENTINEL.write_text("do not touch\n")

try:
    rd, rid = run_probe(probe_graph(ARM_FLAGS_TRUE))
    parked = until(lambda: sum(e.get("event") == "gate.held" for e in events_of(rd)) >= 3, 20)
    check("L1 gates hold when armed (gate.held x3)", parked)
    # nobody answers: timer must apply the deny defaults
    released = until(lambda: sum(e.get("event") == "gate.auto_released"
                                 and str(e.get("option", "")).startswith("deny")
                                 for e in events_of(rd)) >= 3, 30)
    evs = events_of(rd)
    check("L1 deny-default auto-release x3 on hold_timeout (option=deny_*)", released,
          f"events={[e.get('event') for e in evs]}")
    done = until(lambda: (rd / "runner_exit.json").exists(), 20)
    check("L1 run reaches terminal exit after denies", done)
    trace = rd / "11-child-trace.jsonl"
    kids = [json.loads(l) for l in trace.open()] if trace.exists() else []
    prompts = " ".join(k.get("prompt", "") for k in kids)
    arm_kids = [k for k in kids if "skipped not approved" in k.get("prompt", "")]
    check("L1 arm nodes ran and carried the self-no-op protocol", len(arm_kids) >= 3,
          f"arm children={len(arm_kids)}")
    check("L1 zero mutating door traffic from an arms-armed deny lap",
          all("chat" in " ".join(k.get("argv", [])) for k in kids))
    check("L1 sentinel untouched by the whole lap",
          SENTINEL.read_text() == "do not touch\n")
    check("L1 no unauthorized second run minted",
          len([p for p in Path(os.environ["WF_RUNS_ROOT"]).iterdir()
               if p.is_dir() and not p.name.startswith(".") and p != rd]) == 0)

    # audit-mode shape: all gate booleans false -> every gate skips, no arm spawns
    rd2, rid2 = run_probe(probe_graph({k: False for k in ARM_FLAGS_TRUE}))
    skipped = until(lambda: sum(e.get("event") == "gate.skipped" for e in events_of(rd2)) >= 3, 20)
    check("L1 audit-mode shape skips all three gates (gate.skipped x3)", skipped)
    t2 = rd2 / "11-child-trace.jsonl"
    kids2 = [json.loads(l) for l in t2.open()] if t2.exists() else []
    until(lambda: (rd2 / "runner_exit.json").exists(), 20)
    check("L1 audit-mode spawns zero arm children",
          not any("skipped not approved" in k.get("prompt", "") for k in kids2),
          f"children={len(kids2)}")
except AssertionError as e:
    check("L1 probe lap executable", False, str(e)[:300])

# ---------------------------------------------------------------- L2
LED = ROOT / "receipts" / "workflow-mechanic" / "admission-104.json"
try:
    led = json.loads(LED.read_text())
    bl = led.get("blind_holdout", {})
    check("L2 ledger records blinded run.json.status (clause a)",
          bl.get("run_json_status_blind") is True)
    check("L2 sealed key digest pinned (64-hex)",
          bool(re.fullmatch(r"[0-9a-f]{64}", bl.get("sealed_labels_sha256", ""))))
    check("L2 withdrawn re-seal digests recorded",
          all(bool(re.fullmatch(r"[0-9a-f]{64}", d)) for d in bl.get("withdrawn_digests", [])))
    cases = bl.get("cases") or bl.get("old_cohort_lap_2026_10_18", {}).get("cases", [])
    check("L2 every case: status derived, never run.json.status",
          all(c.get("status_source") == "events+runner_exit" for c in cases) and len(cases) >= 3)
    check("L2 every case: prediction recorded against sealed truth",
          all("predicted_classes" in c and "sealed_classes" in c for c in cases))
    bat = led.get("consent_battery", {})
    check("L2 battery counts are measured ints (not prose)",
          isinstance(bat.get("consented"), int) and isinstance(bat.get("required"), int))
except Exception as e:  # ledger missing/corrupt = gate honesty broken
    check("L2 admission ledger present and parseable", False, str(e)[:200])

# ---------------------------------------------------------------- L3
cand = os.environ.get("WF_MECHANIC_CANDIDATE")
if cand:
    g = json.loads(Path(cand).read_text())
    nodes = g.get("nodes")
    if isinstance(nodes, dict):
        nodes = [dict(v, id=k) for k, v in nodes.items()]
    errs = common.validate_graph_errors(nodes, admission=True)
    check("L3 candidate passes engine validation (admission mode)", not errs, str(errs)[:400])
    byid = {n["id"]: n for n in nodes}
    gates = {n["id"]: n for n in nodes if n.get("type") == "gate"}
    check("L3 every gate has deny-named default inside its options + bounded hold_timeout",
          all(isinstance(n.get("default_option"), str)
              and n["default_option"] in (n.get("options") or [])
              and n["default_option"].startswith("deny")
              and isinstance(n.get("hold_timeout"), (int, float)) and 0 < n["hold_timeout"] <= 604800
              for n in gates.values()))
    # side-effect arms are STRUCTURAL: agent nodes hanging directly under one gate
    arms = [n for n in nodes if n.get("type") == "agent"
            and (n.get("after") or [""])[0] in gates]
    check("L3 graph offers at least one gated side-effect arm", len(arms) >= 1)
    for a in arms:
        aft = a.get("after") or []
        check(f"L3 side-effect node {a.get('id')} depends only on its own gate",
              len(aft) == 1 and aft[0] in gates)
    check("L3 audit-only release law: gates enter only via synth gate booleans",
          all(re.search(r"out\.\w+\.\w+\s*==\s*True", g.get("when") or "") for g in gates.values()))
else:
    print("L3 GATE-CLOSED: no vendored candidate offered (WF_MECHANIC_CANDIDATE unset) — "
          "vendoring PRs must ship it and the checks above become binding")

shutil.rmtree(TMP, ignore_errors=True)
print("RESULT", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(0 if fails == 0 else 1)
