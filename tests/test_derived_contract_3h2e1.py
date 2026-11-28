#!/usr/bin/env python3
"""est-3h2e1 — pin wf.derived_contract's reply-contract sentence (sweep-c test gain).

Unpinned semantics the Sprint101 #9 auto-contract rests on: only a non-empty
dict with at least one usable required key says anything; the sentence names
keys in schema order and annotates each with its declared type, degrading to
'any' for absent, non-dict, or type-less property entries — never crashing.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf


def check(value, label):
    assert value, label
    print("PASS", label)


check(wf.derived_contract({}) == "" and wf.derived_contract(None) == ""
      and wf.derived_contract([]) == "" and wf.derived_contract("x") == "",
      "empty/None/non-dict schemas say nothing")

check(wf.derived_contract({"required": []}) == ""
      and wf.derived_contract({"required": [3, None, ""]}) == ""
      and wf.derived_contract({"properties": {"a": {"type": "string"}}}) == "",
      "no usable required key -> no contract (properties alone don't speak)")

s = wf.derived_contract({"required": ["verdict", "reason"]})
check(s.startswith("Reply with ONLY a fenced ```json block whose keys are: "),
      "fixed opener")
check("keys are: verdict, reason" in s,
      "keys kept in schema order, comma-joined")
check(s.endswith("(types: verdict=any, reason=any)."),
      "unannotated required keys degrade to 'any'")

s2 = wf.derived_contract({"required": ["n", "v"],
                          "properties": {"n": {"type": "integer"},
                                         "v": {"type": "string"}}})
check("keys are: n, v" in s2 and "(types: n=integer, v=string)." in s2,
      "declared property types ride the annotation")

s3 = wf.derived_contract({"required": ["n", "x"],
                          "properties": {"n": {"type": "number"},
                                         "x": "junk", "y": {"type": "string"}}})
check("(types: n=number, x=any)." in s3 and " y=" not in s3,
      "garbage property entry degrades to 'any'; optional props stay out")

check("keys are: a, b" in wf.derived_contract({"required": ["a", 5, "", "b"]}),
      "non-string and empty required entries filtered, survivors kept")

print("OK")
