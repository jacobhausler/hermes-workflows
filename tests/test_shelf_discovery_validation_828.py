"""est-2ek.1.828 (owner ruling 16): continuous discovery-time structural admission.

_library_rows must run the installed structural validator (defaults fill +
_validation_error — the same door pipeline act_validate uses, no liveness ping)
after envelope normalization, and route failures into the EXISTING typed
skipped/quarantined outputs. Pins:
  1. a structurally invalid shelf graph (unknown fanout key / missing node type)
     is quarantined with an 'invalid:' reason and never listed;
  2. bad JSON and wrong-shape files keep their existing quarantine behavior;
  3. a schema carrying `enum` (the ra-fix contract that started this) passes;
  4. a bare legacy entry still lists with the exact 1.1 key-set;
  5. discovery fires NO liveness ping.
Stdlib only; no runner, no network.
"""
import atexit, importlib, json, os, shutil, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-828-", dir=HERE / "tests",
                                      ignore_cleanup_errors=True)
atexit.register(lambda: shutil.rmtree(tmp_dir.name, ignore_errors=True))
os.environ["HERMES_HOME"] = tmp_dir.name
os.environ["WF_RUNS_ROOT"] = os.path.join(tmp_dir.name, "workflows")
door = importlib.import_module("__init__")
import wf_test_isolation as _iso; _iso.install(door)
import wfcommon

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

LIB = door.library_root() if hasattr(door, "library_root") else Path(os.environ["WF_RUNS_ROOT"]) / "library"
LIB.mkdir(parents=True, exist_ok=True)

def put(name, obj_or_text):
    p = LIB / f"{name}.json"
    p.write_text(obj_or_text if isinstance(obj_or_text, str)
                 else json.dumps(obj_or_text), encoding="utf-8")
    return p

GOOD = {"name": "good828", "nodes": [{"id": "a", "type": "agent", "goal": "do"}]}
ENUMFIX = {"name": "enumfix", "nodes": [{"id": "a", "type": "agent", "goal": "verdict",
    "schema": {"type": "object", "required": ["status"],
               "properties": {"status": {"type": "string", "enum": ["done", "blocked"]}}}}]}
BADSTRUCT = {"name": "badstruct", "nodes": [{"id": "a", "type": "agent", "goal": "g",
    "fanout": {"items": [1], "bogus_key": 1}}]}
BADSHAPE = {"foo": 1}

pings = []
_real = getattr(door, "_route_liveness_ping", None)
if _real is not None:
    door._route_liveness_ping = lambda *a, **k: (pings.append(1), _real(*a, **k))[1]

put("good828", GOOD)
put("enumfix828", ENUMFIX)
put("badstruct828", BADSTRUCT)
put("badjson828", "{not json")
put("badshape828", BADSHAPE)

rows, skipped, quarantined = door._library_rows()
names = [r["name"] for r in rows]
qids = {q["id"]: q for q in quarantined}
check("valid entry lists", any(n.endswith("good828") for n in names), str(names))
check("enum-carrying schema (the ra-fix contract) passes discovery",
      any(n.endswith("enumfix828") for n in names), str(names))
check("structurally invalid entry quarantined with typed invalid: reason",
      any(k.endswith("badstruct828.json") for k in qids)
      and all(v["reason"].startswith("invalid:") for k, v in qids.items()
              if k.endswith("badstruct828.json")),
      json.dumps(qids)[:300])
check("structurally invalid entry skipped, not listed",
      any(k.endswith("badstruct828.json") for k in skipped)
      and not any(n.endswith("badstruct828") for n in names))
check("bad JSON still quarantined", any(k.endswith("badjson828.json") for k in qids))
check("wrong shape still quarantined", any(k.endswith("badshape828.json") for k in qids))
check("discovery fired NO liveness ping", not pings)

# bare legacy entry keeps the exact 1.1 key-set (solo-golden law)
row = next((r for r in rows if r["name"].endswith("good828")), None)
check("bare legacy row keeps the exact 1.1 key-set",
      row is not None and set(row) == {"name", "nodes", "gates", "fanouts", "description"},
      json.dumps(row))

print("FAIL" if fails else "ALL PASS")
sys.exit(1 if fails else 0)
