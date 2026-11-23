#!/usr/bin/env python3
"""est-25t / E20 — the route-gate refusal is ONE conversation, not lore.

The corpus: the wall error was est-id lore with a 4-option fix menu;
substitution-denied told operators to amend a pin the first message said was
inexpressible; and the denial stranded lanes until someone deleted
route_receipts.json — an artifact the message never showed a path for.
Pinned here (the refusal TEXT is the observable):
  (1) a strip-armed route_inexpressible names the arm that fired (env with its
      value; marker with its path AND its armed-at mtime), and renders the
      exact amend snippet that clears the hold plus the exact rm that lifts the
      marker — no est-ids, no menu without a path;
  (2) route_substitution_denied names the holding artifact ABSOLUTE path, its
      armed-at mtime, the receipt row, and surfaces the receipt-deletion
      escape verbatim (rm <path>) — s31's receipt_artifact_named half;
  (3) idempotence: re-asking the gate re-renders the same dialog (a rerun
      converges).

Run: cd tests && python3 test_route_gate_dialog_25t.py
"""
import json, os, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-rg25t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
os.environ.pop("WF_OMIT_POLICY_FLAGS", None)
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

if HOME.exists():
    shutil.rmtree(HOME)
RUN = HOME / "workflows" / "20261119-rg25t"
(RUN / "nodes").mkdir(parents=True)
(RUN / "graph.json").write_text(json.dumps({"name": "rg25t", "nodes": []}))
ARMED_TS = 1794836179  # 2026-11-16T13:36:19Z — the s31 bank's marker-arm instant

MPATH = HOME / "workflows" / "omit-policy-flags.on"
MPATH.parent.mkdir(parents=True, exist_ok=True)
MPATH.write_text("")
os.utime(MPATH, (ARMED_TS, ARMED_TS))

node = {"id": "review", "type": "agent", "goal": "g",
        "model": "example-model-2", "provider": "example-provider"}
meta = {"_run": RUN}
BARE_CMD = ["/bin/hermes", "chat", "--query-file", "/tmp/q", "--oneshot"]

ref = wf._spawn_expressibility_refusal(meta, node, list(BARE_CMD), 1)
check("pinned spawn refuses before submit (marker presence irrelevant)",
      ref and ref.get("error_class") == "route_inexpressible", str(ref)[:120])
err = (ref or {}).get("error", "")
check("#709: the dead marker is INERT — error names no arms, no mtime, no rm",
      "omit-policy-flags.on" not in err and "WF_OMIT_POLICY_FLAGS" not in err
      and "2026-11-16" not in err, err[:300])
check("renders the amend snippet that clears the hold",
      '{"patch": {"nodes": {"review": {"require_route": false}}}}' in err, err[-300:])
check("one conversation, no est-id lore", "est-" not in err and "#483" not in err, err[:200])
ref2 = wf._spawn_expressibility_refusal(meta, node, list(BARE_CMD), 1)
check("rerun converges: the identical dialog, no drift", ref2 == ref)

os.environ["WF_OMIT_POLICY_FLAGS"] = "1"
try:
    ref3 = wf._spawn_expressibility_refusal(meta, node, list(BARE_CMD), 1) or {}
    check("#709: the env arm is inert too — identical refusal, no drift",
          ref3 == ref, str(ref3)[:300])
finally:
    os.environ.pop("WF_OMIT_POLICY_FLAGS", None)

# ---------- (2) the substitution denial names its holding artifact ----------
(RUN / "route_receipts.json").write_text(json.dumps({"review": "example-provider/example-model-2"}))
os.utime(RUN / "route_receipts.json", (ARMED_TS, ARMED_TS))
swapped = {"id": "review", "type": "agent", "goal": "g",
           "model": "gpt-y", "provider": "example-provider"}
ref4 = wf._route_substitution_refusal(meta, swapped, 2)
err4 = (ref4 or {}).get("error", "")
check("substitution of a receipted route is refused",
      ref4 and ref4.get("error_class") == "route_substitution_denied", str(ref4)[:120])
check("receipt_artifact_named: absolute route_receipts.json path",
      str(RUN / "route_receipts.json") in err4, err4[:200])
check("the receipt row and the armed-at mtime are rendered",
      "2026-11-16T13:36:19+00:00" in err4 and "example-provider/example-model-2" in err4,
      err4[:300])
check("the receipt-deletion escape is surfaced verbatim",
      f"rm {RUN / 'route_receipts.json'}" in err4, err4[-300:])
check("the receipted route is the ONLY amend target the dialog offers",
      "amend the node TO the receipted route" in err4, err4[-300:])

# a same-route respawn is not a refusal at all (the hold is a hold, not a lock)
same = {"id": "review", "type": "agent", "goal": "g",
        "model": "example-model-2", "provider": "example-provider"}
check("the receipted route respawns unrefused",
      wf._route_substitution_refusal(meta, same, 2) is None)

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
