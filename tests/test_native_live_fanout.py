"""Native live fan-out projection: real runner + fake children + dashboard _view
replayed through the REAL GraphView (ship-2.0 graph-native proof).

The synthetic node-local fixtures all declare static fanout.items, so defItems
sized the rendered set and hid the dynamic gap: a running items_from fan-out
with BOTH spawn-time item records persisted and ZERO finished events projected
NO actionable cards until settle. This test drives the real engine, captures
the live snapshot from the dashboard read model mid-run, replays both live and
settled snapshots through the GraphView harness, and demands [0, 1] in both.
Stdlib-only; prints PASS/FAIL; exit 0 = green."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parent.parent
GREEN = []
RED = []


def check(name, ok, note=""):
    (GREEN if ok else RED).append(name)
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" — {note}" if note and not ok else ""))


def run_engine_and_capture(tmp):
    home = tmp / "home"
    run = tmp / "runs" / "native-live"
    for p in (home, run / "nodes", run / "gates", tmp / "desktop"):
        p.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("HERMES_", "WF_", "FAKE_"))}
    env.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(run.parent),
               TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE="1",
               HERMES_WF_PYTHON=sys.executable)
    os.environ.clear()
    os.environ.update(env)
    graph = {"name": "native-live", "nodes": [
        {"id": "prep", "type": "echo", "output": {"items": ["one", "two"]}},
        {"id": "f", "type": "agent", "goal": "Return a fenced result.",
         "after": ["prep"],
         "fanout": {"items_from": "prep.items", "goal": "QSLEEP 3 review {item}"}}]}
    (run / "graph.json").write_text(json.dumps(graph))
    (run / "run.json").write_text(json.dumps(
        {"hermes_bin": str(REPO / "tests" / "fake"), "item_concurrency": 2}))
    spec = importlib.util.spec_from_file_location("native_live_dashboard",
                                                  REPO / "dashboard" / "plugin_api.py")
    assert spec is not None and spec.loader is not None
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    argv = [sys.executable, "-B", str(REPO / "wf.py"), "run", run.name]
    with subprocess.Popen(argv, env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as engine:
        live = None
        deadline = time.monotonic() + 7
        while engine.poll() is None and time.monotonic() < deadline:
            snapshot = api._view(run, full=True)
            events = snapshot.get("events", []) if snapshot else []
            started = sorted(e["index"] for e in events if e["event"] == "item.started")
            item_records = [run / "nodes" / f"f.{i}.json" for i in (0, 1)]
            if (started == [0, 1] and all(p.is_file() for p in item_records)
                    and not any(e["event"] == "item.finished" for e in events)):
                live = snapshot
                break
            time.sleep(0.03)
        out, err = engine.communicate(timeout=20)
        check("runner exits 0", engine.returncode == 0,
              f"rc={engine.returncode} out={out[-400:]} err={err[-400:]}")
        check("live window captured (both started, spawn-time records persisted, "
              "zero finished)", live is not None,
              f"out={out[-400:]} err={err[-400:]}")
        if live is None:
            return None, None
        settled = api._view(run, full=True)
        fo = live["graph"]["nodes"][1]["fanout"]
        check("live snapshot still carries items_from (no runner-side materialize shim)",
              fo.get("items_from") == "prep.items", json.dumps(fo))
        check("node settles done", settled["nodes"]["f"]["status"] == "done",
              json.dumps(settled["nodes"]["f"])[:400])
        return live, settled


def replay_snapshots(tmp, live, settled):
    # GraphView replay: reuse the stub-React harness of test_fanout_expand.mjs
    # verbatim and append the actionable-card assertions, so the page canvas —
    # the same renderer the desktop half runs — sees the real snapshots.
    shutil.copyfile(REPO / "desktop" / "plugin.js", tmp / "desktop" / "plugin.js")
    shim = (REPO / "tests" / "test_fanout_expand.mjs").read_text()
    shim += """
const actual = JSON.parse(process.env.GRAPH_NATIVE_SNAPSHOTS)
const actionable = (detail) => itemBtns(view({runId:detail.id,nodeId:'f'},detail)).map(b => {
  click(b)
  const pick = calls.find(x => x[0] === 'fanItem')[1]
  assert.deepEqual(pick, {runId:detail.id,nodeId:'f',index:b.key})
  return b.key
}).sort()
const result = { live:actionable(actual.live), settled:actionable(actual.settled) }
console.log('NATIVE-LIVE-FANOUT ' + JSON.stringify(result))
assert.deepEqual(result.settled,[0,1], 'settled control must show both')
assert.deepEqual(result.live,[0,1], 'native dashboard must show both started dynamic items before either finishes')
"""
    script = tmp / "tests" / "native-live-review.mjs"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(shim)
    visual = subprocess.run(["node", "--experimental-strip-types", str(script)],
                            env={**os.environ,
                                 "GRAPH_NATIVE_SNAPSHOTS": json.dumps(
                                     {"live": live, "settled": settled})},
                            timeout=30, cwd=str(REPO))
    check("GraphView replay: both started dynamic items actionable live and settled",
          visual.returncode == 0, f"node rc={visual.returncode}")


def main():
    with tempfile.TemporaryDirectory(prefix="wf-native-live-") as d:
        tmp = Path(d)
        live, settled = run_engine_and_capture(tmp)
        if live is not None:
            replay_snapshots(tmp, live, settled)
    print(f"\n{len(GREEN)} passed, {len(RED)} failed"
          + (f" — {', '.join(RED)}" if RED else ""))
    return 1 if RED else 0


if __name__ == "__main__":
    sys.exit(main())
