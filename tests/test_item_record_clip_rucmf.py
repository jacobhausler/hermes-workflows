"""est-rucmf (residual of wf#568): fanout item-record clip parity + certify-side
normalization.

The capture-boundary clip (est-x92v7) sits at the persist choke `save_node`
(`_clip_record`: bearer redaction FIRST, then head/tail clip at
WORKFLOW_OUTPUT_CLIP). The fan-out per-item COMMIT path `commit_item_record`
bypassed that choke — raw result-merge then tmp+replace — so `nodes/<id>.<i>.json`
committed facts persisted UNCLIPPED while the aggregate record was clipped:
the same capture boundary was enforced on one side of a paired ledger and not
the other.

Routing the commit through `_clip_record` alone would BREAK the 765 certification
law: `item_records_certified` compares the aggregate's in-memory claim against
the committed record byte-for-byte after stable serialization, and a >clip claim
can never be byte-equal to a clipped record on raw bytes. The fix is a PAIR:
clip at the item commit AND normalize the claim through the identical transform
at certify time (idempotent on already-clipped records; under-clip values pass
through unchanged, so byte-for-byte claim equality is preserved exactly where
it existed before).

Pins:
  C1 an oversized fanout item commit persists clipped at the same default
     100k ceiling with the same head/tail marker, spawn evidence merged,
     record efp-valid; the ceiling knob WORKFLOW_OUTPUT_CLIP is honoured
     fresh at commit time (same knob as save_node — "same ceiling" proven,
     not asserted by shared constant alone).
  C2 certify round-trip OVER the clip boundary: a raw >clip claim certifies
     against its clipped committed record (both sides normalized identically),
     an under-clip sibling certifies byte-for-byte (no marker, exact equality),
     and a forged >clip claim whose retained head diverges is STILL refused
     (normalization shares the clip window, it does not weaken the guard).
  C3 bearer redaction stays UPSTREAM of the clip on the item-commit path:
     a credential in the retained head never persists as a readable fragment
     and the value still carries the clip marker.

Run: python3 tests/test_item_record_clip_rucmf.py   (pytest: plain asserts)
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wf            # noqa: E402
import wfcommon      # noqa: E402

CEILING = wf.OUTPUT_CLIP_DEFAULT  # 100_000 — the save_node choke's default

NODE = {"id": "fan", "type": "agent", "timeout": 30,
        "fanout": {"items": [{"n": 0}], "goal": "PROCESS item {index} reply"}}
BYID = {NODE["id"]: NODE}

_homes = []

def mkrun(tag):
    r = Path(tempfile.mkdtemp(prefix=f"wf-rucmf-{tag}-")) / "run"
    (r / "nodes").mkdir(parents=True)
    _homes.append(r.parent)
    return r

def rec_at(r, index):
    return json.loads((r / "nodes" / f"fan.{index}.json").read_text())

def oversized(tag_ch, total=160_000):
    body = "HEADMARK" + (tag_ch * (total - 16)) + "TAILMARK"
    assert len(body) == total
    return body


def test_oversized_fanout_item_commit_is_clipped_at_the_same_ceiling():
    """C1: the committed per-item record honors the capture boundary — same
    default ceiling, same marker, head/tail retained, efp still valid, and the
    merge keeps spawn evidence (clip must not clobber the merged fact)."""
    r = mkrun("c1")
    big = oversized("x")
    wf.commit_item_record(r, NODE, BYID, 0,
                          {"status": "done", "output": {"result": big}, "ms": 5})
    rec = rec_at(r, 0)
    s = rec["output"]["result"]
    assert len(s) <= CEILING, (
        f"item commit persisted {len(s)} chars — bypassed the capture-boundary clip")
    assert "clipped" in s and "head+tail" in s and f"ceiling {CEILING}" in s, s[:160]
    assert s.startswith("HEADMARK") and s.endswith("TAILMARK")
    assert rec["status"] == "done"
    assert wfcommon.record_efp_valid(rec, BYID, NODE)
    # same ceiling law as save_node: the operator knob is read fresh at the
    # commit instant, and the marker names the configured ceiling
    with patch.dict(os.environ, {"WORKFLOW_OUTPUT_CLIP": "1500"}):
        wf.commit_item_record(r, NODE, BYID, 1,
                              {"status": "done", "output": {"result": big}, "ms": 5})
    s2 = rec_at(r, 1)["output"]["result"]
    assert len(s2) <= 1_500 and "ceiling 1500" in s2, f"persisted {len(s2)} chars"
    assert s2.startswith("HEADMARK") and s2.endswith("TAILMARK")


def test_certify_round_trip_over_clip_boundary():
    """C2: certify stays green on BOTH sides of the boundary. An in-memory
    done claim with a raw >clip output certifies against the clipped committed
    record (identical normalization both sides); an under-clip item certifies
    byte-for-byte with no marker on disk."""
    r = mkrun("c2")
    big = oversized("y")
    claim_big = {"status": "done", "output": {"result": big}}
    claim_small = {"status": "done", "output": {"result": "small"}}
    wf.commit_item_record(r, NODE, BYID, 0, claim_big)
    wf.commit_item_record(r, NODE, BYID, 1, claim_small)
    rec0 = rec_at(r, 0)
    assert len(rec0["output"]["result"]) <= CEILING and "clipped" in rec0["output"]["result"]
    # the under-clip record is byte-identical to the claim — clip parity is a
    # no-op below the ceiling, byte-for-byte claim equality preserved
    assert rec_at(r, 1)["output"] == claim_small["output"]
    ok, problems = wf.item_records_certified(r, NODE, BYID, [claim_big, claim_small])
    assert ok is True, f"certify rejected honest claims: {problems}"


def test_forged_oversized_claim_still_refused_under_normalization():
    """C2b (regression guard): the certify-side normalization shares the CLIP
    WINDOW, not the verdict — a >clip claim whose retained head/tail diverge
    from the committed record is still refused."""
    r = mkrun("c2b")
    big = oversized("z")
    wf.commit_item_record(r, NODE, BYID, 0,
                          {"status": "done", "output": {"result": big}})
    forged = "FORGEDHEAD" + ("z" * (160_000 - 18)) + "TAILMARK"
    ok, problems = wf.item_records_certified(
        r, NODE, BYID, [{"status": "done", "output": {"result": forged}}])
    assert ok is False, "normalization turned the byte-for-byte guard off"
    assert problems and problems[0].get("index") == 0


def test_bearer_redaction_stays_upstream_of_the_item_clip():
    """C3: an item commit with a credential in the would-be cut region persists
    NEITHER the secret NOR an unmarked value — redaction first, then clip, the
    same ordering save_node enforces (est-x92v7 R1 parity)."""
    r = mkrun("c3")
    secret = "TOPSECRE" + "TVALUE789"
    head = "HDR Authorization: Bearer " + secret + " END "
    big = head + ("q" * (160_000 - len(head)))
    wf.commit_item_record(r, NODE, BYID, 0,
                          {"status": "done", "output": {"result": big}})
    raw = (r / "nodes" / "fan.0.json").read_text()
    assert secret not in raw, "credential survived the item-commit persist"
    assert "[redacted]" in raw
    s = rec_at(r, 0)["output"]["result"]
    assert "clipped" in s and len(s) <= CEILING, "redaction replaced the clip (R1 half-miss)"


def main():
    rcs = []
    for fn in (test_oversized_fanout_item_commit_is_clipped_at_the_same_ceiling,
               test_certify_round_trip_over_clip_boundary,
               test_forged_oversized_claim_still_refused_under_normalization,
               test_bearer_redaction_stays_upstream_of_the_item_clip):
        try:
            fn()
            print("PASS " + fn.__name__, flush=True)
            rcs.append(0)
        except AssertionError as e:
            print("FAIL " + fn.__name__ + f" :: {e}", flush=True)
            rcs.append(1)
    for h in _homes:
        shutil.rmtree(h, ignore_errors=True)
    print(f"TOTAL {rcs.count(0)} PASS {rcs.count(1)} FAIL", flush=True)
    return 1 if any(rcs) else 0


if __name__ == "__main__":
    sys.exit(main())
