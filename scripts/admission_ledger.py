#!/usr/bin/env python3
"""issue #104 (R10): consent/dissent ledger normalizer (source-only, stdlib).
Loads BOTH forms: old committed (no consent_battery.rows — defaults to [],
counts verbatim; the migration lives here) and new machine-row form. Refuses
(LedgerError): missing row keys, bad enums, non-64-hex digests, granted
without responded_at, rerun without receipts (run_id, runner_exit_reason,
fresh_output_digests), count-vs-rows drift, malformed admission_laps."""
import re

HEX64 = re.compile(r"[0-9a-f]{64}")
RESPONSES = {"granted", "denied", "timeout", "unanswered"}
ACTIONS = {"rerun", "noop"}
ROW_KEYS = ("candidate_alias", "candidate_run_id_sha256", "ask_at", "ask_body_sha256",
            "effect_inventory_sha256", "expected_side_effect_class", "response",
            "responded_at", "action_taken", "hold_timeout_seconds", "deny_default")
LAP_KEYS = ("blind_sha256", "candidate_sha256", "scores", "confusion", "unsafe", "at")

class LedgerError(Exception):
    pass

def _row(row, i, errs):
    if not isinstance(row, dict):
        errs.append(f"rows[{i}] is not an object")
        return 0, 0
    errs += [f"rows[{i}] missing {k}" for k in ROW_KEYS if k not in row]
    resp, act = row.get("response"), row.get("action_taken")
    errs += [f"rows[{i}] {n} {v!r} not in enum"
             for n, v, ok in (("response", resp, resp in RESPONSES),
                              ("action_taken", act, act in ACTIONS)) if not ok]
    errs += [f"rows[{i}].{k} is not 64-hex"
             for k in ("candidate_run_id_sha256", "ask_body_sha256", "effect_inventory_sha256")
             if k in row and not HEX64.fullmatch(str(row[k] or ""))]
    if resp == "granted" and row.get("responded_at") is None:
        errs.append(f"rows[{i}] response=granted without responded_at")
    if act == "rerun":
        dig = row.get("fresh_output_digests")
        errs += [f"rows[{i}] rerun without receipt field {k}"
                 for k in ("run_id", "runner_exit_reason") if not str(row.get(k) or "")]
        if not (isinstance(dig, list) and dig and all(HEX64.fullmatch(str(d)) for d in dig)):
            errs.append(f"rows[{i}] rerun without fresh-output digests")
    return int(resp == "granted"), int(act == "rerun")

def normalize(ledger):
    bat = ledger.get("consent_battery")
    if not isinstance(bat, dict):
        raise LedgerError("consent_battery missing")
    if any(type(bat.get(k)) is not int
           for k in ("required", "consented", "reruns_executed")):
        raise LedgerError("battery counts must be measured ints")
    old_form = "rows" not in bat
    rows = bat.setdefault("rows", [])
    if not isinstance(rows, list):
        raise LedgerError("consent_battery.rows must be a list")
    errs, granted, reruns = [], 0, 0
    for i, row in enumerate(rows):
        g, r = _row(row, i, errs)
        granted, reruns = granted + g, reruns + r
    if not old_form:  # old form: counts transcribed verbatim, no drift check possible
        errs += [f"{n} {got} != {want} per rows aggregation"
                 for n, want, got in (("required", len(rows), bat["required"]),
                                      ("consented", granted, bat["consented"]),
                                      ("reruns_executed", reruns, bat["reruns_executed"]))
                 if want != got]
    laps = ledger.setdefault("blind_holdout", {}).setdefault("admission_laps", [])
    if not isinstance(laps, list):
        errs.append("blind_holdout.admission_laps must be a list")
    else:
        errs += [f"admission_laps[{j}] missing lap keys" for j, lap in enumerate(laps)
                 if not isinstance(lap, dict) or any(k not in lap for k in LAP_KEYS)]
    if errs:
        raise LedgerError("; ".join(errs))
    return ledger
