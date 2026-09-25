"""Dashboard backend for hermes-workflows — thin projection of the SHARED read model.

State truth lives in wfcommon.run_state (same function the door uses); gate release
shares the door's single answer path. Endpoints land under /api/plugins/hermes-workflows.
The UI does NOT resume runs — the owning agent does (philosophy: agent owns the run).
"""
import hashlib, importlib.util, json, os, sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_COMMON_MODULE = "_hermes_workflows_wfcommon_" + hashlib.sha256(
    str(_PLUGIN_ROOT).encode("utf-8")).hexdigest()[:16]

def _workflow_common():
    """Load this plugin's sibling module without binding global ``wfcommon``."""
    module = sys.modules.get(_COMMON_MODULE)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(_COMMON_MODULE, _PLUGIN_ROOT / "wfcommon.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load workflow module from {_PLUGIN_ROOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_COMMON_MODULE] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_COMMON_MODULE, None)
        raise
    return module

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:
    router = None

def _root():
    home = os.environ.get("HERMES_HOME") or (Path.home() / ".hermes")
    return Path(home) / "workflows"

def _safe_run(run_id):
    rid = (run_id or "").strip()
    if not rid or rid != "".join(c for c in rid if c.isalnum() or c in "-_.") \
            or rid.startswith("."):
        return None
    r = _root() / rid
    return r if r.is_dir() else None

def _events(r, limit=400):
    out = []
    try:
        lines = (r / "events.jsonl").read_text().splitlines()[-limit:]
    except FileNotFoundError:
        return out
    for l in lines:
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def _view(r, full=False):
    st = _workflow_common().run_state(r)
    if not st:
        return None
    view = {"id": st["run_id"], "name": st["name"], "status": st["status"],
            "started": st.get("started"), "owner": st.get("owner"),
            "nodes_done": st["done"], "nodes_skipped": st["skipped"], "nodes_total": st["total"],
            "updated": (r / "events.jsonl").stat().st_mtime if (r / "events.jsonl").exists() else 0}
    if st["held_gate"]:
        view["held_gate"] = st["held_gate"]
    if st.get("runner_exit"):
        view["runner_exit"] = st["runner_exit"]  # shared read model (wfcommon.run_state)
    if full:
        import time
        common = _workflow_common()
        cm = common.child_metrics(st["run_id"])
        nodes = {}
        for nid, v in st["nodes"].items():
            rec = None
            if v["status"] in ("done", "failed"):
                try: rec = json.loads((r / "nodes" / f"{nid}.json").read_text())
                except Exception: pass
            nodes[nid] = {**v, "question": None, "options": None,
                          "goal": None, "ms": (rec or {}).get("ms"),
                          "error": (rec or {}).get("error"),
                          "output": (rec or {}).get("output") if full else None}
            # metrics: node-level = the node's own child, or the fold of its items' children.
            # Keys are prefix-matched (any efp suffix) so an amended re-run's fresh rows count.
            prefix = f"wf:{st['run_id']}:{nid}:"
            mine = {k: m for k, m in cm.items() if k.startswith(prefix)}
            active = v.get("active_spawns", [])
            if mine or active:
                groups = {}
                def item_index(key):
                    parts = key[len(prefix):].split(":")  # "<i>:<efp8>.<nonce>" | "<efp8>.<nonce>"
                    return int(parts[0]) if len(parts) == 2 and parts[0].isdigit() else None
                for k, m in mine.items():
                    groups.setdefault(item_index(k), {})[k] = m
                for spawn in active:
                    key = spawn["skey"].split("#a", 1)[0]
                    if key.startswith(prefix):
                        groups.setdefault(item_index(key), {})
                heartbeat = common.current_attempt(mine, active)
                nodes[nid]["metrics"] = _fold_metrics(mine.values()) or {}
                nodes[nid]["metrics"].update(heartbeat)
                nodes[nid]["metrics"]["scope"] = "cumulative"
                items = {}
                for i, ms in groups.items():
                    if i is not None:
                        items[i] = _fold_metrics(ms.values()) or {}
                        items[i].update(common.current_attempt(ms, [s for s in active
                            if s["skey"].split("#a", 1)[0].startswith(f"{prefix}{i}:")]))
                if items:
                    nodes[nid]["item_metrics"] = items
        for n in st["graph"]["nodes"]:
            nodes[n["id"]].update({"goal": n.get("goal") or (n.get("fanout") or {}).get("goal"),
                                   "question": n.get("question"), "options": n.get("options")})
        active = [s for v in st["nodes"].values() for s in v.get("active_spawns", [])]
        rollup = _fold_metrics(cm.values()) if cm else ({} if active else None)
        if rollup is not None:
            rollup.update(common.current_attempt(cm, active))
            rollup["scope"] = "cumulative"
            if any(not m.get("api_calls_known", True) for m in cm.values()):
                rollup.pop("api_calls", None)
        view.update({"graph": st["graph"], "nodes": nodes, "events": _events(r),
                     "gate": dict(st["held_gate"] or {}), "metrics": rollup})
    return view

def _fold_metrics(ms):
    ms = list(ms)
    if not ms:
        return None
    f = {"tokens_in": 0, "tokens_out": 0, "cache_read": 0, "reasoning": 0, "api_calls": 0,
         "tool_calls": 0, "cost": 0.0, "attempts": 0, "children": len(ms), "live": 0,
         "last_activity": None, "last_desc": None, "models": []}
    for m in ms:
        for k in ("tokens_in", "tokens_out", "cache_read", "reasoning", "api_calls", "tool_calls", "cost", "attempts"):
            f[k] += m.get(k) or 0
        if m.get("model") and m["model"] not in f["models"]:
            f["models"].append(m["model"])
    return f

def _list_runs():
    root = _root()
    runs = []
    if root.exists():
        for r in sorted(root.iterdir(), reverse=True):
            v = _view(r)
            if v: runs.append(v)
    return {"runs": runs[:100], **_workflow_common().run_summary(runs)}


if router is not None:
    @router.get("/runs")
    async def list_runs():
        return _list_runs()

    @router.get("/runs/{run_id}")
    async def get_run(run_id: str):
        r = _safe_run(run_id)
        return (_view(r, full=True) if r else None) or {"error": "unknown run"}

    @router.post("/runs/{run_id}/gate")
    async def release_gate(run_id: str, body: dict):
        """UI door onto the SAME answer path the tool uses (incl. stale-answer
        overwrite). Does NOT resume the run — the owning agent does."""
        r = _safe_run(run_id)
        if not r:
            return {"ok": False, "error": "unknown run"}
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_hermes_workflows_door", Path(__file__).resolve().parent.parent / "__init__.py")
        door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(door)
        return door._release_core(r, body.get("gate_id"), body.get("answer", ""), ui=True)
