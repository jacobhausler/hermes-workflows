#!/usr/bin/env python3
"""est-1bojj check: ra-release-peer peer_review must spawn AS {run.PEER_PROFILE}
(-p seat), and a verdict!=merge outcome must have a leg that terminally stamps the
live PR marker (pending never survives the run).

usage: check_peer_seat.py <plugin_root> <graph.json>
Prints one CHECK line per assertion, then PASS/FAIL; exit 0 only on PASS.
"""
import importlib.util
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

ROOT = Path(sys.argv[1]).resolve()
GRAPH = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

spec = importlib.util.spec_from_file_location("door_1bojj", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
wspec = importlib.util.spec_from_file_location("wf_1bojj", ROOT / "wf.py")
wf = importlib.util.module_from_spec(wspec)
wspec.loader.exec_module(wf)

BIND = {"REPO": "jacobhausler/disposable", "VERSION": "0.0.1",
        "OWNER_PROFILE": "gh-dispatch", "PEER_PROFILE": "zap"}
fails = []


def check(name, ok, detail=""):
    print(f"CHECK {'ok ' if ok else 'FAIL'} {name}" + (f" :: {detail}" if detail else ""))
    if not ok:
        fails.append(name)


g = json.loads(GRAPH.read_text())
nodes = {n["id"]: n for n in g["nodes"]}
pr = nodes.get("peer_review", {})
check("peer_review.profile == '{run.PEER_PROFILE}'",
      pr.get("profile") == "{run.PEER_PROFILE}", f"profile={pr.get('profile')!r}")

# non-merge arm: complementary gate on peer_review.verdict != 'merge' + an agent
# under the peer seat that stamps the live marker terminal.
hold = [n for n in g["nodes"] if n.get("type") == "gate" and "peer_review" in n.get("after", [])
        and "!=" in (n.get("when") or "") and "merge" in (n.get("when") or "")]
check("complementary gate when verdict != 'merge'", bool(hold),
      f"gates={[n['id'] for n in hold]}")
stamp = [n for n in g["nodes"] if n.get("type") == "agent" and hold
         and set(n.get("after", [])) & {h["id"] for h in hold}]
check("stamp agent after the non-merge gate", bool(stamp), f"agents={[n['id'] for n in stamp]}")
if stamp:
    s = stamp[0]
    check("stamp agent runs as {run.PEER_PROFILE}", s.get("profile") == "{run.PEER_PROFILE}",
          f"profile={s.get('profile')!r}")
    goal = s.get("goal", "")
    check("stamp goal forbids surviving pending + reads back",
          "pending" in goal and "read-back" in goal.lower() and "{run.PEER_PROFILE}" in goal)

# door: graph validates unbound and bound with the live binding
# act_validate takes no run_context, and profile validation runs AFTER {run.KEY}
# rendering on the run door (__init__.py run path: _bind_run_context then
# _profile_error) -- so the unbound form is checked structurally only.
sv = door._validation_error(g)
check("workflow validate structural (unbound shelf form)", sv is None, json.dumps(sv)[:400])
bound = door._bind_run_context(wfcommon.apply_graph_defaults(g), BIND)
vb = door.act_validate({"graph": bound})
check("workflow validate (bound PEER_PROFILE=zap)", vb.get("ok") is True,
      json.dumps({k: vb.get(k) for k in ("ok", "error", "errors", "resolved_routes")})[:600])
bn = {n["id"]: n for n in bound["nodes"]}
check("bound peer_review.profile == zap", bn["peer_review"].get("profile") == "zap",
      f"profile={bn['peer_review'].get('profile')!r}")

# dry resolved spawn identity: real wf.run_child against a fake hermes bin + temp profiles
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    home = root / "profiles" / "gh-dispatch"
    target = root / "profiles" / "zap"
    home.mkdir(parents=True)
    target.mkdir(parents=True)
    (target / "config.yaml").write_text("{}")
    run = root / "runs" / "r1"
    (run / "nodes").mkdir(parents=True)
    node = dict(bn["peer_review"], goal="dry", schema=None)
    node.pop("schema")
    (run / "graph.json").write_text(json.dumps({"nodes": [node]}))
    binpath = root / "hermes"
    binpath.write_text("#!/usr/bin/python3\nimport json,os,sys\nfrom pathlib import Path\n"
                       "Path(os.environ['HERMES_WF_RUN_DIR'],'capture.json').write_text(json.dumps(sys.argv[1:]))\n"
                       "print('```json\\n{\"verdict\":\"decision\",\"why\":\"dry\"}\\n```')\n")
    binpath.chmod(0o755)
    meta = {"_run": run, "hermes_bin": str(binpath), "_spawn_n": {}, "_procs_lock": threading.Lock(),
            "_procs": {}, "_stop": threading.Event(), "node_timeout": 10}
    with patch.dict(os.environ, {"HERMES_HOME": str(home), "WF_RUNS_ROOT": str(root / "runs"),
                                  "HERMES_WRITE_SAFE_ROOT": str(root / "safe")}, clear=False):
        r = wf.run_child(meta, node, {node["id"]: node}, "dry", "", None, skey="wf:r1:peer_review")
    cap = run / "capture.json"
    argv = json.loads(cap.read_text()) if cap.exists() else None
    rec = json.loads((run / "nodes" / "peer_review.json").read_text()) if (run / "nodes" / "peer_review.json").exists() else {}
    print("SPAWN argv[:3]=", argv[:3] if argv else argv, "record.profile=", rec.get("profile"),
          "status=", r.get("status"))
    check("resolved spawn_cmd carries -p zap", bool(argv) and argv[:3] == ["-p", "zap", "chat"],
          f"argv={argv[:3] if argv else argv}")
    check("node record profile == zap", rec.get("profile") == "zap" and r.get("profile") == "zap")

print("PASS" if not fails else f"FAIL {len(fails)}: {fails}")
sys.exit(0 if not fails else 1)
