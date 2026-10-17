"""est-55z04: a node pinned to a seat alias WITH an explicit provider ({model:'bigseat',
provider:'example-provider'}) must PING and REPORT the alias TARGET id, not the bare alias.
Before the fix, the alias expansion ran only under `not provider`, so the route fell back to
the bare alias ('bigseat' -> HTTP 404 model: bigseat). Stdlib only, no network (ping stubbed)."""
import importlib, atexit, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-alias55z04-", dir=HERE / "tests")
atexit.register(tmp_dir.cleanup)
tmp = tmp_dir.name
os.environ["HERMES_HOME"] = tmp
os.environ.setdefault("WF_RUNS_ROOT", str(Path(tmp) / "workflows"))
door = importlib.import_module("__init__")
import wf_test_isolation as _iso71; _iso71.install(door)

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

class Ctx:
    def __init__(self, tiers): self.t = tiers
    def get_config(self, k, d=None): return self.t if k == "models" else d

door._CTX = Ctx({})
door._seat_model_cfg = lambda: {"default": "seat-default",
                                "aliases": {"bigseat": "example-provider/example-model-1"}}
pinged = []
def _fake_ping(p, m):
    pinged.append((p, m))
    return {"liveness": "alive"}
door._ping_route_once = _fake_ping

# 1. explicit provider + seat alias: route speaks the TARGET id
nodes = [{"id": "a", "type": "agent", "goal": "x", "provider": "example-provider", "model": "bigseat"}]
err, table, routes = door._resolve_models(nodes)
check("explicit-provider alias resolves without error", err is None, err)
res = (routes or {}).get("a", {}).get("resolved", {})
check("routes[a].resolved.model is the alias TARGET id (not bare alias)",
      res.get("model") == "example-model-1", res)
check("routes[a].resolved.provider is the explicit provider",
      res.get("provider") == "example-provider", res)
check("node def keeps model:'bigseat' verbatim", nodes[0]["model"] == "bigseat", nodes[0])
door._route_liveness_ping(routes or {})
check("liveness ping is handed the TARGET id, not the bare alias",
      pinged == [("example-provider", "example-model-1")], pinged)

print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
