#!/usr/bin/env python3
"""ui2-round4 (mesh fix): per-node metrics survive into the DURABLE receipt.

The dashboard's live read folds child metrics from state.db at query time
(68626>1902 style); this change lands the same facts in the committed
`nodes/<id>[.<i>].json` record so the receipt outlives the DB. The closed
metrics key set — tokens_in, tokens_out, api_calls, tool_calls, served_model,
model_source — rides EVERY commit site (normal, retry-resume, redrive, amend,
fanout-item). A child that reported nothing writes explicit nulls, never an
omitted key, so the design's em-dash path is driven by the receipt itself.
served_model->model_source precedence (owner-chosen): node pin > run meta >
billing. Re-running a commit UPDATES the block and never duplicates it.

Standalone (NOT pytest-only): python3 tests/test_node_metrics_receipt_r4.py
prints PASS/FAIL lines, exit 0 = green; pytest can collect the test_* funcs.
"""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wf            # noqa: E402
import wfcommon      # noqa: E402

FAKE = str(HERE / "fake")
fails = total = 0


def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not ok else ""), flush=True)
    if not ok:
        fails += 1


_scratch = Path(tempfile.mkdtemp(prefix="wf-r4-metrics-"))
BASE_ENV = {k: v for k, v in os.environ.items()
            if not k.startswith("WF_") and not k.startswith("FAKE_")
            and not k.startswith("HERMES_WF_") and k != "HERMES_HOME"}
BASE_ENV["HERMES_HOME"] = str(_scratch / "home")
BASE_ENV["WF_RUNS_ROOT"] = str(_scratch / "runs")
BASE_ENV["FAKE_LOG"] = str(_scratch / "fake.log")
os.makedirs(BASE_ENV["HERMES_HOME"], exist_ok=True)


def mk(run_id, graph, env_extra=None, item_concurrency=None):
    r = Path(BASE_ENV["WF_RUNS_ROOT"]) / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps(graph))
    meta = {"hermes_bin": FAKE}
    if item_concurrency is not None:
        meta["item_concurrency"] = item_concurrency
    (r / "run.json").write_text(json.dumps(meta))
    return r


def engine(run_id, env_extra=None, timeout=120):
    env = dict(BASE_ENV)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout)


def redrive(run_id, mode, env_extra=None, timeout=60):
    env = dict(BASE_ENV)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "redrive", run_id,
                           f"--mode={mode}"],
                          env=env, capture_output=True, text=True, timeout=timeout)


def rec_of(r, stem):
    try:
        return json.loads((r / "nodes" / f"{stem}.json").read_text())
    except Exception:
        return None


METRICS_KEYS = ("tokens_in", "tokens_out", "api_calls", "tool_calls",
                "served_model", "model_source")

SCHEMA = {"type": "object", "required": ["result"],
          "properties": {"result": {"type": "string"}}}

# ---------- 1. normal commit: the child's reported numbers land verbatim ----
r = mk("r4a", {"name": "r4a", "nodes": [
    {"id": "a", "type": "agent", "goal": 'TELEMETRY-EMIT JSON:{"result":"ok"}',
     "model": "fake-pin-seat", "require_route": False, "schema": SCHEMA}]},
    env_extra={"FAKE_TELEMETRY": "5,6,500,60"})
out = engine("r4a", {"FAKE_TELEMETRY": "5,6,500,60"})
rec = rec_of(r, "a")
check("normal run commits done", bool(rec) and rec.get("status") == "done", out.stdout + out.stderr)
m = (rec or {}).get("metrics")
check("metrics block carries the child-reported counters + pin attribution",
      m == {"tokens_in": 500, "tokens_out": 60, "api_calls": 5, "tool_calls": 6,
            "served_model": "fake-pin-seat", "model_source": "node_pin"}, json.dumps(m))
check("telemetry fact still rides (est-wqml6 untouched)",
      isinstance((rec or {}).get("telemetry"), dict)
      and rec["telemetry"].get("input_tokens") == 500, json.dumps((rec or {}).get("telemetry")))

# ---------- 2. child reported none: explicit nulls, never an omitted key ----
r = mk("r4b", {"name": "r4b", "nodes": [
    {"id": "b", "type": "agent", "goal": 'JSON:{"result":"ok"}', "schema": SCHEMA}]})
engine("r4b")
rec = rec_of(r, "b")
m = (rec or {}).get("metrics")
check("no-report child commits ALL SIX keys as explicit nulls",
      isinstance(m, dict) and set(m) >= set(METRICS_KEYS)
      and all(m[k] is None for k in METRICS_KEYS), json.dumps(m))

# ---------- 3. run-meta attribution (no node pin, graph defaults.model) -----
r = mk("r4c", {"name": "r4c", "defaults": {"model": "default-seat"}, "nodes": [
    {"id": "c", "type": "agent", "goal": 'JSON:{"result":"ok"}', "schema": SCHEMA}]})
engine("r4c")
rec = rec_of(r, "c")
m = (rec or {}).get("metrics") or {}
check("defaults.model attribution: served_model from run meta, source run_meta",
      m.get("served_model") == "default-seat" and m.get("model_source") == "run_meta",
      json.dumps(m))

# ---------- 4. precedence unit: node pin > run meta > billing ---------------
_s, _src = wf._model_attribution({"model": "p"}, {"defaults": {"model": "d"}},
                                 {"served_model": "b"})
check("precedence: node pin beats run meta and billing",
      (_s, _src) == ("p", "node_pin"), str((_s, _src)))
_s, _src = wf._model_attribution({}, {"defaults": {"model": "d"}},
                                 {"served_model": "b", "served_billing_provider": "x"})
check("precedence: run meta beats billing", (_s, _src) == ("d", "run_meta"), str((_s, _src)))
_s, _src = wf._model_attribution({}, {}, {"served_model": "b"})
check("precedence: billing is the last attribution", (_s, _src) == ("b", "billing"), str((_s, _src)))
_s, _src = wf._model_attribution({}, {}, {})
check("precedence: nothing named -> explicit nulls, never a guess",
      _s is None and _src is None, str((_s, _src)))

# ---------- 5. fan-out: every per-item record carries the block -------------
# (items run serialized HERE: this scenario tests the canonical COMMIT, not
# concurrency — est-wqml6 owns the sidecar-concurrency leg.)
r = mk("r4f", {"name": "r4f", "nodes": [
    {"id": "fan", "type": "agent",
     "fanout": {"items": ["one", "two"], "goal": 'TELEMETRY-EMIT item {index} JSON:{"result":"ok"}',
                "schema": SCHEMA},
     "model": "fake-pin-seat", "require_route": False, "timeout": 60, "schema": SCHEMA}]},
    item_concurrency=1)
engine("r4f")
agg = rec_of(r, "fan")
check("fan-out aggregate commits done", bool(agg) and agg.get("status") == "done")
ok_items = True
detail = ""
for i in (0, 1):
    irec = rec_of(r, f"fan.{i}")
    m = (irec or {}).get("metrics")
    if not (isinstance(m, dict) and m.get("api_calls") == 3 and m.get("tool_calls") == 2
            and m.get("tokens_in") == 100 and m.get("tokens_out") == 40
            and m.get("served_model") == "fake-pin-seat"
            and m.get("model_source") == "node_pin"):
        ok_items = False
        detail = f"fan.{i}: {json.dumps(m)}"
check("per-item canonical records carry the child-reported metrics block", ok_items, detail)
check("aggregate record also carries the closed six-key block (never an omitted key)",
      isinstance((agg or {}).get("metrics"), dict)
      and set(agg["metrics"]) >= set(METRICS_KEYS), json.dumps((agg or {}).get("metrics")))

# ---------- 6. redrive: CURRENT-attempt metrics, history preserved ----------
r = mk("r4d", {"name": "r4d", "nodes": [
    {"id": "d", "type": "agent", "goal": "FAILME TELEMETRY-EMIT", "schema": SCHEMA}]})
out = engine("r4d", {"FAKE_TELEMETRY": "1,1,10,20"})
rec = rec_of(r, "d")
check("first generation commits failed", bool(rec) and rec.get("status") == "failed",
      out.stdout + out.stderr)
m1 = (rec or {}).get("metrics") or {}
check("failed commit carries attempt-1 metrics",
      m1.get("api_calls") == 1 and m1.get("tool_calls") == 1
      and m1.get("tokens_in") == 10 and m1.get("tokens_out") == 20, json.dumps(m1))
out = redrive("r4d", "same-fingerprint-resume", {"FAKE_TELEMETRY": "7,9,70,90"})
check("redrive verb accepts the failed lane", out.returncode == 0, out.stdout + out.stderr)
rec2 = None
for _ in range(60):
    time.sleep(0.5)
    rec2 = rec_of(r, "d")
    if rec2 and rec2.get("status") == "failed" \
            and (rec2.get("metrics") or {}).get("api_calls") == 7:
        break
m2 = (rec2 or {}).get("metrics") or {}
check("redriven receipt shows the CURRENT attempt's metrics (not gen-1's)",
      m2.get("api_calls") == 7 and m2.get("tool_calls") == 9
      and m2.get("tokens_in") == 70 and m2.get("tokens_out") == 90, json.dumps(m2))
arch = [e for e in (rec2 or {}).get("attempts_log") or []
        if isinstance(e, dict) and e.get("redriven")]
check("attempt history preserved: the dropped generation rides attempts_log with its metrics",
      len(arch) == 1 and (arch[0].get("metrics") or {}).get("tokens_in") == 10,
      json.dumps((rec2 or {}).get("attempts_log")))
check("redrive archived the dropped record durably",
      (r / "nodes" / "d.redrive-history.jsonl").is_file())
# idempotent re-fold: committing again must not duplicate the history entry
node = wfcommon.jload(r / "graph.json")["nodes"][0]
byid = {node["id"]: node}
wf.save_node(r, node, byid, dict(rec2))
rec3 = rec_of(r, "d")
arch3 = [e for e in (rec3 or {}).get("attempts_log") or []
         if isinstance(e, dict) and e.get("redriven")]
check("re-running the commit UPDATES in place: history re-folds without duplicating",
      len(arch3) == 1 and (rec3 or {}).get("metrics") == m2, json.dumps((rec3 or {}).get("attempts_log")))

# ---------- 7. commit-site update, never duplicate (direct writer proof) ----
before = rec_of(Path(BASE_ENV["WF_RUNS_ROOT"]) / "r4a", "a")
node = wfcommon.jload(Path(BASE_ENV["WF_RUNS_ROOT"]) / "r4a" / "graph.json")["nodes"][0]
byid = {node["id"]: node}
upd = dict(before, metrics={**before["metrics"], "api_calls": 42, "tool_calls": 7})
wf.save_node(Path(BASE_ENV["WF_RUNS_ROOT"]) / "r4a", node, byid, upd)
wf.save_node(Path(BASE_ENV["WF_RUNS_ROOT"]) / "r4a", node, byid, upd)
after = rec_of(Path(BASE_ENV["WF_RUNS_ROOT"]) / "r4a", "a")
check("re-commit updates the block (closed key set, no duplicate keys)",
      after["metrics"]["api_calls"] == 42 and after["metrics"]["tool_calls"] == 7
      and sorted(k for k in after["metrics"] if k in METRICS_KEYS) == sorted(METRICS_KEYS),
      json.dumps(after["metrics"]))

print(f"\n{total - fails}/{total} checks passed")
sys.exit(1 if fails else 0)
