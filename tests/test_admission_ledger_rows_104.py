#!/usr/bin/env python3
"""issue #104 item-3 (R10): consent/dissent ledger rows + old-form normalizer.
RED first vs the missing normalizer (verified pre-impl). A: exact OLD committed
shape loads (rows=[], counts verbatim). B: committed ledger clean (3
unanswered/noop deny-default rows, consented 0, laps []). C-E refusals:
granted+rerun without receipts, count drift, granted w/o responded_at, enums,
malformed admission_lap row."""
import copy, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("admission_ledger", ROOT / "scripts" / "admission_ledger.py")
al = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(al)  # RED until the module exists
fails = 0

def check(label, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + label)
    fails += 0 if cond else 1

def loads(view, label, cond):
    try:
        check(label, cond(al.normalize(view)))
    except al.LedgerError as e:
        check(f"{label} — refused [{e}]", False)

def refuses(view, label):
    try:
        al.normalize(view)
        check(label, False)
    except al.LedgerError:
        check(label, True)

COMMITTED = json.loads((ROOT / "receipts" / "workflow-mechanic"
                        / "admission-104.json").read_text())
tam = lambda: copy.deepcopy(COMMITTED)

old = tam(); old["consent_battery"].pop("rows"); old["blind_holdout"].pop("admission_laps")
loads(old, "A old committed form loads; rows=[]; counts verbatim; laps []",
      lambda v: (v["consent_battery"]["rows"] == [] and v["blind_holdout"]["admission_laps"] == []
                 and (v["consent_battery"]["consented"], v["consent_battery"]["required"]) == (0, 3)))

B = lambda v: (len(v["consent_battery"]["rows"]) == 3 and v["consent_battery"]["consented"] == 0
               and v["blind_holdout"]["admission_laps"] == []
               and all(r["response"] == "unanswered" and r["action_taken"] == "noop"
                       and r["deny_default"] is True and r["responded_at"] is None
                       for r in v["consent_battery"]["rows"]))
loads(tam(), "B committed ledger clean: 3 unanswered/noop deny-default rows", B)

t = tam()
t["consent_battery"]["rows"][0].update(response="granted", responded_at="2026-10-18T09:00:00Z",
                                       action_taken="rerun")
t["consent_battery"].update(consented=1, reruns_executed=1)  # only the receipt rule can catch it
refuses(t, "C granted+rerun without receipt fields refused")

d = tam(); d["consent_battery"]["consented"] = 2
refuses(d, "D consented-vs-rows drift refused")
d = tam(); d["consent_battery"]["required"] = 4
refuses(d, "D required-vs-rows drift refused")
g = tam(); g["consent_battery"]["rows"][1].update(response="granted"); g["consent_battery"]["consented"] = 1
refuses(g, "E granted without responded_at refused")
b = tam(); b["consent_battery"]["rows"][2]["response"] = "maybe"
refuses(b, "E unknown response enum refused")
l = tam(); l["blind_holdout"]["admission_laps"] = [{"blind_sha256": "0" * 64}]
refuses(l, "E malformed admission_lap row refused")

sys.exit(0 if fails == 0 else 1)
