"""est-2del: the patch surface for amend + the diff confirm surface.

The ask (est-2ek.1.56 closeout, re-filed): amending two fields must not
resubmit the whole multi-KB graph, and the amend needs a real confirm surface.
Pins, all door-level, no runner spawned:
  1. patch applies: 2-field edit lands; untouched nodes byte-identical;
     amends.jsonl records the resolved FULL graph (old,new row);
  2. fail-closed refusals name what they refuse (unknown id; id change;
     new node; unknown patch key; patch+graph both present) and write nothing;
  3. action=diff = the amend door with dry_run FORCED: preview + graph_diff,
     graph.json and amends.jsonl byte-identical;
  4. null deletes a field; name patch replaces the graph name.
Stdlib only.
"""
import atexit, copy, importlib, json, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-2del-", dir=HERE / "tests", ignore_cleanup_errors=True)
def _cleanup():
    import shutil; shutil.rmtree(tmp_dir.name, ignore_errors=True)
atexit.register(_cleanup)
home = Path(tmp_dir.name)
os.environ["HERMES_HOME"] = str(home)
os.environ["WF_RUNS_ROOT"] = str(home / "workflows")
door = importlib.import_module("__init__")
import wf_test_isolation as _iso; _iso.install(door)

fails = 0
SNAP = {}
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

def author():
    return {"name": "probe2del",
            "nodes": [{"id": "a", "type": "echo", "output": {"x": 1}},
                      {"id": "b", "type": "echo", "after": ["a"], "output": {"y": 2}},
                      {"id": "c", "type": "echo", "after": ["b"], "output": {"z": 3}}]}

R = home / "workflows" / "r2del"
def _rm(p):
    import shutil, time
    for _ in range(5):
        shutil.rmtree(p, ignore_errors=True)
        if not p.exists():
            return
        for f in p.rglob("*"):
            try:
                f.unlink() if f.is_file() or f.is_symlink() else None
            except OSError:
                pass
        time.sleep(0.05)
    raise RuntimeError(f"cannot clear {p}")


def fresh():
    if R.exists():
        _rm(R)
    for d in ("nodes", "gates", "logs"):
        (R / d).mkdir(parents=True)
    (R / "graph.json").write_text(json.dumps(author()))
    (R / "amends.jsonl").write_text("")
    SNAP["graph"] = (R / "graph.json").read_bytes()
    SNAP["amends"] = (R / "amends.jsonl").read_bytes()

# 1) the 2-field amend without the whole graph
fresh()
out = door.act_amend({"run_id": "r2del", "patch": {"nodes": {"b": {"output": {"y": 9}, "after": ["a"]}}}})
g = json.loads((R / "graph.json").read_text())
byid = {n["id"]: n for n in g["nodes"]}
check("patch amend applies (no full graph submitted)", not out.get("error"),
      str(out)[:200])
check("patched node landed", byid["b"]["output"] == {"y": 9} and byid["b"]["after"] == ["a"], json.dumps(byid["b"]))
check("untouched nodes byte-identical", byid["a"] == author()["nodes"][0] and byid["c"] == author()["nodes"][2])
rows = [json.loads(ln) for ln in (R / "amends.jsonl").read_text().splitlines() if ln.strip()]
check("amends.jsonl records the resolved FULL graph",
      len(rows) == 1 and len(rows[0]["new"]["nodes"]) == 3
      and {n["id"]: n for n in rows[0]["new"]["nodes"]}["b"]["output"] == {"y": 9})
check("echo amends list ride back on the patch apply", "will_rerun" in out or "changed" in out, str(out)[:160])

# 2) fail-closed refusals, nothing written
for label, patch_obj, needle in [
    ("unknown node id named", {"nodes": {"zz": {"output": {}}}}, "zz"),
    ("id change refused", {"nodes": {"b": {"id": "q"}}}, "id"),
    ("new node refused by name", {"nodes": {"newb": {"type": "echo", "output": {}}}}, "newb"),
    ("unknown patch key refused", {"node": {"b": {}}}, "node"),
]:
    fresh()
    out = door.act_amend({"run_id": "r2del", "patch": patch_obj})
    err = out.get("error", "")
    check(f"refusal names it: {label}",
          err.startswith("patch:") and needle in err
          and (R / "graph.json").read_bytes() == SNAP["graph"]
          and (R / "amends.jsonl").read_bytes() == SNAP["amends"],
          err[:160])
fresh()
out = door.act_amend({"run_id": "r2del", "patch": {"nodes": {"b": {"output": {}}}}, "graph": author()})
check("patch is exclusive with graph", "exclusive" in out.get("error", "")
      and (R / "graph.json").read_bytes() == SNAP["graph"], str(out)[:140])

# 3) action=diff — the confirm surface writes nothing
fresh()
out = door.act_diff({"run_id": "r2del", "patch": {"nodes": {"b": {"output": {"y": 99}}}}})
gd = out.get("graph_diff") or {}
check("diff returns the forced-dry_run preview",
      out.get("ok") and out.get("dry_run") and "b" in (out.get("changed") or []), str(out)[:200])
check("diff carries a unified graph_diff",
      isinstance(gd.get("lines"), list) and any(l.startswith("+") for l in gd["lines"])
      and gd.get("changed_lines", 0) > 0, str(gd)[:160])
check("diff touched NOTHING", (R / "graph.json").read_bytes() == SNAP["graph"]
      and (R / "amends.jsonl").read_bytes() == SNAP["amends"])
out2 = door.act_diff({"run_id": "r2del", "patch": {"nodes": {"b": {"output": {"y": 99}}}}, "dry_run": False})
check("diff forces dry_run even when the caller asks false", out2.get("dry_run") is True)

# 4) null deletes a field; name replaces the name
fresh()
out = door.act_amend({"run_id": "r2del", "patch": {"nodes": {"c": {"after": None}}, "name": "renamed2del"}})
g = json.loads((R / "graph.json").read_text())
byid = {n["id"]: n for n in g["nodes"]}
check("null deletes the field; name replaces the graph name",
      not out.get("error") and "after" not in byid["c"] and g["name"] == "renamed2del",
      str(out)[:160])

print("FAIL" if fails else "ALL PASS")
sys.exit(1 if fails else 0)
