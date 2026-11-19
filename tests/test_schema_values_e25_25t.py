#!/usr/bin/env python3
"""est-25t / E25 — every schema rejection names the path AND the rejected value.

The corpus: the wave6 case already enumerated missing keys; the rest of the
validator returned bare rule text ("$.answer: expected string") that left the
typed-correction retry blind to what it actually emitted, and the s36 death
showed a bare trace names no violated rule at all. Pinned here:
  (1) every validate() error carries its JSON path and the rejected value —
      types, enums, floors, caps, and required-miss (which names the object's
      key-set; a rename suggestion still wins when one fires);
  (2) containers render as shape (never a flood) and long strings truncate —
      the message stays the smallest readable repair instruction;
  (3) end-to-end: a persistent out-of-set answer lands error_class=schema and
      the node.failed record text carries the path AND the rejected value, so
      the recovery is legible from the record alone.

Run: cd tests && python3 test_schema_values_e25_25t.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "home-ev25t"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# ---------- (1) the battery: path + value in every error family ----------
S = lambda t: {"type": "object", "properties": {"a": t}}
check("type miss names the rejected scalar",
      wf.validate({"a": 5}, S({"type": "string"})) == ["$.a: expected string, got 5"])
check("bool-never-a-number names the rejected True",
      wf.validate({"a": True}, S({"type": "integer"})) == ["$.a: expected number, got True"])
check("array-under-a-string-schema shows the shape, not a flood",
      wf.validate({"a": [1, 2]}, S({"type": "string"}))
      == ["$.a: expected string, got [1, 2] (2 items)"])
check("enum miss pairs the rejected value with the allowed set",
      wf.validate({"a": "passedd"}, S({"type": "string", "enum": ["pass", "fail"]}))
      == ["$.a: not an allowed value (got 'passedd'; allowed: 'pass', 'fail')"])
check("minItems miss names the empty array it rejected",
      wf.validate({"a": []}, S({"type": "array", "minItems": 1}))
      == ["$.a: expected at least 1 item(s), got [] (0 items)"])
check("minLength miss counts and quotes the offender",
      wf.validate({"a": "  x  "}, S({"type": "string", "minLength": 3}))
      == ["$.a: expected at least 3 non-blank char(s), got 1: '  x  '"])
check("maxItems miss names the over-cap list",
      wf.validate({"a": ["a", "b", "c"]}, S({"type": "array", "maxItems": 2}))
      == ["$.a: expected at most 2 item(s), got ['a', 'b', 'c'] (3 items)"])
check("required-miss is never bare: the object's keys ride the error",
      wf.validate({"summary": "s", "rationale": "r"},
                  {"type": "object", "required": ["answer"]})
      == ["$: missing required 'answer' (the object has {'summary', 'rationale'})"])
check("a rename suggestion still wins over the key-set form",
      "you wrote" in wf.validate({"ansr": "s"},
                                 {"type": "object", "required": ["answer"],
                                  "properties": {"answer": {"type": "string"}}})[0])

# ---------- (2) reader-load guards: shape-render and truncation ----------
big = {f"k{i}": i for i in range(12)}
e = wf.validate({"a": big}, S({"type": "string"}))
check("12-key dict renders first 8 keys + a count, never the values",
      e[0].count("'k") == 8 and "only 12 keys" in e[0], e[0])
e = wf.validate({"a": "z" * 500}, S({"type": "integer"}))
check("a 500-char offender is truncated, message stays bounded",
      len(e[0]) < 110 and e[0].endswith("..."), e[0])

# ---------- (3) end-to-end: the record text carries path + value ----------
if HOME.exists():
    shutil.rmtree(HOME)
(HOME / "workflows").mkdir(parents=True)
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
ENUM_SCHEMA = {"type": "object", "required": ["verdict"],
               "properties": {"verdict": {"type": "string",
                                          "enum": ["ship", "hold"]}}}
r = RUNS / "e25t"
(r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
(r / "graph.json").write_text(json.dumps(
    {"name": "e25t", "nodes": [{"id": "j", "type": "agent",
                                "goal": "ENUMTEST25 e25t", "schema": ENUM_SCHEMA}]}))
(HOME / "fake.log").write_text("")
(r / "run.json").write_text(json.dumps(
    {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 60}))
env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
           FAKE_LOG=str(HOME / "fake.log"), FAKE_MODE="enum_always_bad")
subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", "e25t"],
               env=env, capture_output=True, text=True, timeout=180)
rec = json.loads((r / "nodes" / "j.json").read_text())
err = rec.get("error") or ""
check("e2e: the death is typed schema", rec.get("error_class") == "schema", str(rec.get("error_class")))
check("e2e: the record text names the JSON path", "$.verdict" in err, err[:200])
check("e2e: the record text names the rejected value",
      "got 'passedd'" in err, err[:200])
check("e2e: and the allowed set beside it",
      "allowed: 'ship', 'hold'" in err, err[:200])
p2 = sorted((r / "logs").glob("j.a*.prompt.md"), key=lambda p: p.name)
check("e2e: the correction retry prompt reuses the enriched text verbatim",
      len(p2) == 2 and "got 'passedd'" in p2[1].read_text())

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
