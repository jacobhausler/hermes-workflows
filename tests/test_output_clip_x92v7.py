"""WF-GRAFT-11 (est-x92v7, peer row atbrace:hw-s53 #6): output clip at the capture
boundary + oversized-input budget.

Pins four behaviours at the persist choke:
  O1 an oversized captured output persisted through save_node is clipped to the
     default 100k ceiling with a head/tail retention marker naming the ceiling.
  O2 the marker round-trips: re-read from disk it is byte-identical, and
     re-clipping an already-clipped value changes nothing (idempotent store).
  O3 the ceiling is configurable: WORKFLOW_OUTPUT_CLIP overrides the default and
     the refusal stays bounded, never silent.
  I1 node inputs assembled past the budget REFUSE LOUDLY (build_inputs returns
     an error; the existing typed `inputs` spawn failure consumes it) instead of
     truncating; under budget the same inputs inject normally.
  R1 bearer redaction runs UPSTREAM of the clip: a credential sitting in the
     would-be cut region never survives as a readable fragment, and the value
     still carries the clip marker (both transformations applied, redaction
     first).

Run: python3 tests/test_output_clip_x92v7.py
"""
import json, os, shutil, sys, tempfile
from unittest.mock import patch
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok, checks = True, []
def check(label, cond, detail=""):
    global ok
    checks.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and bool(cond)

HOME = Path(tempfile.mkdtemp(prefix="wf-clipx92v7-"))

def fresh_run(rid, nodes):
    r = HOME / rid
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": "clip", "nodes": nodes}))
    return r

def agent(id):
    return {"id": id, "type": "agent", "after": [], "timeout": 30, "goal": "say hi"}

NODE_A = {"id": "a", "type": "agent", "after": [], "goal": "say hi", "timeout": 30}

def save(run, node, rec):
    byid = {n["id"]: n for n in json.loads((run / "graph.json").read_text())["nodes"]}
    wf.save_node(run, node, byid, rec)
    return json.loads((run / "nodes" / f"{node['id']}.json").read_text())

# ---- O1 oversized capture: default 100k ceiling, head/tail marker ----
big = "HEADMARK" + ("x" * (160_000 - 16)) + "TAILMARK"
r1 = fresh_run("clip-o1", [agent("a")])
rec1 = save(r1, NODE_A, {"status": "done", "output": {"big": big}, "ms": 1})
s1 = rec1["output"]["big"]
check("O1 oversized capture clipped to the 100k default ceiling",
      len(s1) <= 100_000, f"persisted {len(s1)} chars")
check("O1 clip carries a head/tail retention marker naming the ceiling",
      "clipped" in s1 and "head+tail" in s1 and "ceiling 100000" in s1, s1[:160])
check("O1 head and tail content retained verbatim",
      s1.startswith("HEADMARK") and s1.endswith("TAILMARK"))

# ---- O2 marker round-trip: disk truth identical, re-clip idempotent ----
disk2 = json.loads((r1 / "nodes" / "a.json").read_text())
check("O2 marker round-trips through the store byte-identically",
      disk2["output"]["big"] == s1)
again = wf._clip_record({"output": {"big": s1}})
check("O2 re-clipping an already-clipped value is a no-op",
      again["output"]["big"] == s1)

# ---- O3 config override: WORKFLOW_OUTPUT_CLIP ----
with patch.dict(os.environ, {"WORKFLOW_OUTPUT_CLIP": "1500"}):
    rec3 = save(r1, NODE_A,
                {"status": "done", "output": {"big": "H" + ("y" * 4_998) + "T"}, "ms": 1})
s3 = rec3["output"]["big"]
check("O3 WORKFLOW_OUTPUT_CLIP override clips at the configured ceiling",
      len(s3) <= 1_500 and "ceiling 1500" in s3, f"persisted {len(s3)} chars")
check("O3 override keeps head and tail", s3.startswith("H") and s3.endswith("T"))

# ---- I1 budget refusal: assembled inputs past budget never spawn silently ----
parents = [agent("a"), agent("b")]
ri = fresh_run("clip-i1", parents + [dict(agent("c"), after=["a", "b"])])
outs = {"a": {"blob": "m" * 3_000}, "b": {"blob": "n" * 3_000}}
node_c = {"id": "c", "type": "agent", "after": ["a", "b"], "goal": "say hi", "timeout": 30}
with patch.dict(os.environ, {"WORKFLOW_INPUTS_BUDGET": "2000"}):
    section, err = wf.build_inputs(ri, node_c, outs)
check("I1 assembled inputs past budget REFUSE loudly (error, no section)",
      err and section == "" and "budget" in err.lower(), f"err={err!r}")
check("I1 refusal names the measured size and the knob",
      bool(err) and "3" in err and "WORKFLOW_INPUTS_BUDGET" in err, f"err={err!r}")
section_ok, err_ok = wf.build_inputs(ri, node_c, outs)   # default budget: same bytes inject
check("I1 under the default budget the same inputs inject normally",
      err_ok is None and section_ok.startswith("## Inputs") and len(section_ok) > 5_000)

# ---- R1 redaction upstream of the clip ----
mid = " middle Authorization: Bearer SUPERSECRETBEARER123 tail "
riddled = "A" * 99_000 + mid + "A" * 61_000
rec5 = save(r1, NODE_A,
            {"status": "done", "output": {"big": riddled}, "ms": 1})
s5 = rec5["output"]["big"]
check("R1 bearer secret does not survive the clip as a readable fragment",
      "SUPERSECRETBEARER123" not in s5 and "[redacted]" in s5)
check("R1 the value still carries the clip marker (redaction first, then clip)",
      "clipped" in s5 and len(s5) <= 100_000)

shutil.rmtree(HOME, ignore_errors=True)
sys.exit(0 if ok else 1)
