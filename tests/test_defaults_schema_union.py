"""est-j14j3: a JSON-Schema union type ('type': ['integer', 'null']) in a graph's
`defaults.schema` must be collected by the door, with boot's exact words, BEFORE
any write or spawn — the exact defect that killed run 20261111-211056-wof-pr-forge
(action=validate passed; the runner boot refused the baked node ~9 s later and
every claim stamp was lost).

Pins, in BOTH directions:
(1) refuse direction — door fault line for the defaults.schema union: msg is
    byte-identical to the boot refusal on the baked graph ("unsupported schema
    type"), exactly ONE fault line per occurrence, field points at the schema
    path (defaults.schema.properties.pr_number.type);
(2) the baked-node twin (per-node schema) keeps its refusal words untouched;
(3) accept direction — the same graph with a plain "type": "integer": door
    reports zero schema defects AND boot accepts the baked graph;
(4) the whole door seam: `wf.py validate` (which spec-loads the door and calls
    act_validate verbatim — the same pipeline action=validate walks) exits 1
    with the field and the boot words on stdout;
(5) apply_graph_defaults refuses via its ValueError channel carrying the same
    row (the run/amend door's materialization seam).
"""
import importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg}" + (f"  << {detail}" if detail and cond is not True else "")
    ok += 1; print("PASS", msg)

UNION_SCHEMA = {"type": "object", "required": ["opened"], "properties": {
    "opened": {"type": "boolean"},
    "pr_number": {"type": ["integer", "null"]},   # the shape that killed the run
    "notes": {"type": "string"}}}
CLEAN_SCHEMA = {"type": "object", "required": ["opened"], "properties": {
    "opened": {"type": "boolean"},
    "pr_number": {"type": "integer"},
    "notes": {"type": "string"}}}

def g_with_defaults(schema):
    return {"name": "union-probe", "defaults": {"timeout": 600, "schema": schema},
            "nodes": [{"id": "a", "type": "agent", "goal": "g"}]}

# The door measures a submitted graph with structural_graph_errors — the same
# half _validation_error (act_validate / act_run) delegates to, and which
# includes _defaults_errors for the graph-level defaults block.
DOOR = lambda g: wfcommon.structural_graph_errors(g)
# Boot validates the BAKED graph.json nodes with validate_graph (first-error
# string). The baked twin of a defaults.schema is the schema on every agent node.
BOOT = lambda nodes: wfcommon.validate_graph(nodes)
BAKED_UNION = [{"id": "a", "type": "agent", "goal": "g", "schema": UNION_SCHEMA}]
BAKED_CLEAN = [{"id": "a", "type": "agent", "goal": "g", "schema": CLEAN_SCHEMA}]

# --- (1) refuse direction: the union in defaults.schema ---
errs = DOOR(g_with_defaults(UNION_SCHEMA))
hits = [e for e in errs if e["msg"] == "unsupported schema type"]
check(len(hits) == 1, "door collects exactly ONE fault line per union occurrence "
      "(defaults.schema is one authored site, not one per baked node)",
      json.dumps(errs))
check(hits and hits[0]["field"] == "defaults.schema.properties.pr_number.type",
      "the fault line points at the schema path under defaults", hits)
check(hits and hits[0]["node"] is None,
      "the defaults row is graph-level (node None), like every other defaults row", hits)
b = BOOT(BAKED_UNION)
check(b == "node a: unsupported schema type",
      "boot refuses the baked union with the same words it used on 11-11", b)
check(bool(hits) and hits[0]["msg"] in b,
      "door fault text == boot error words, byte-identical (one shared helper)", b)

# --- (2) the per-node path keeps its words (no drift between the two passes) ---
node_graph = {"name": "n", "nodes": [{"id": "a", "type": "agent", "goal": "g",
                                      "schema": UNION_SCHEMA}]}
ne = wfcommon.validate_graph_errors(node_graph["nodes"])
check(any(e["msg"] == "unsupported schema type"
          and e["node"] == "a"
          and e["field"] == "schema.properties.pr_number.type" for e in ne),
      "per-node union refusal keeps its exact pre-fix row", json.dumps(ne))

# --- (3) accept direction: clean twin passes BOTH passes ---
ce = DOOR(g_with_defaults(CLEAN_SCHEMA))
check(not [e for e in ce if e["field"].startswith("defaults.schema")],
      "door admits the clean defaults.schema", json.dumps(ce))
check(BOOT(BAKED_CLEAN) is None, "boot admits the baked clean graph", BOOT(BAKED_CLEAN))
check(not any(e["msg"] == "unsupported schema type"
              for e in wfcommon.validate_graph_errors(BAKED_CLEAN)),
      "no false-refuse: validate_graph_errors green on the clean schema")

# --- (4) the whole CLI seam: `wf.py validate` is act_validate on argv ---
with tempfile.TemporaryDirectory() as td:
    gp = Path(td) / "g.json"
    gp.write_text(json.dumps(g_with_defaults(UNION_SCHEMA)))
    r = subprocess.run([sys.executable, str(BUILD / "wf.py"), "validate", str(gp)],
                       capture_output=True, text=True, cwd=BUILD)
    check(r.returncode == 1,
          "wf.py validate exits 1 on the defaults.schema union (no false green)",
          r.stdout + r.stderr)
    check("defaults.schema.properties.pr_number.type" in r.stdout
          and "unsupported schema type" in r.stdout,
          "CLI prints the schema path beside the boot words", r.stdout)

# --- (5) materialization seam: apply_graph_defaults refuses via ValueError ---
try:
    wfcommon.apply_graph_defaults(g_with_defaults(UNION_SCHEMA))
    raised = None
except ValueError as e:
    raised = json.loads(str(e))
check(raised and any(x["msg"] == "unsupported schema type"
                     and x["field"] == "defaults.schema.properties.pr_number.type"
                     for x in raised),
      "apply_graph_defaults raises the same row (run/amend door bakes nothing past it)",
      json.dumps(raised))

print(f"OK {ok}")
