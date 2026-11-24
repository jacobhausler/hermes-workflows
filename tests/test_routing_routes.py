"""Deterministic regressions for explicit workflow provider/model routing."""
import importlib.util
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
sys.path.insert(0, str(BUILD))

with tempfile.TemporaryDirectory(prefix=".routing-test-", dir=HERE) as tmp:
    os.environ["HERMES_HOME"] = tmp
    os.environ["TMPDIR"] = tmp
    tempfile.tempdir = tmp

    import wfcommon
    door_spec = importlib.util.spec_from_file_location("routing_test_door", BUILD / "__init__.py")
    door = importlib.util.module_from_spec(door_spec)
    door_spec.loader.exec_module(door)
    import wf as engine

    class Ctx:
        def get_config(self, key, default=None):
            return {"luna-tier": "openai-codex/gpt-6-luna"} if key == "models" else default

    door._CTX = Ctx()
    door._seat_model_cfg = lambda: {
        "default": "seat-default",
        "aliases": {"luna": "openai-codex/gpt-6-luna"},
    }

    qualified = {
        "id": "qualified", "type": "agent", "goal": "route",
        "provider": "openai-codex", "model": "openai-codex/gpt-6-luna",
    }
    tiered = {
        "id": "tiered", "type": "agent", "goal": "route",
        "provider": "openai-codex", "model": "luna-tier",
    }
    graph_nodes = [qualified, tiered]
    assert wfcommon.validate_graph(graph_nodes) is None, "provider/model graph should validate"

    err, table, routes = door._resolve_models(graph_nodes)
    assert err is None, err
    assert qualified["provider"] == "openai-codex" and qualified["model"] == "gpt-6-luna"
    assert tiered["provider"] == "openai-codex" and tiered["model"] == "gpt-6-luna"
    assert tiered["tier"] == "luna-tier"
    assert routes["qualified"] == {
        "requested": {"provider": "openai-codex", "model": "openai-codex/gpt-6-luna"},
        "resolved": {"provider": "openai-codex", "model": "gpt-6-luna"},
    }
    assert routes["tiered"]["requested"] == {"provider": "openai-codex", "model": "luna-tier"}
    assert routes["tiered"]["resolved"] == {"provider": "openai-codex", "model": "gpt-6-luna"}
    assert table["qualified"] == "openai-codex/gpt-6-luna"
    assert table["tiered"] == "openai-codex/gpt-6-luna  (luna-tier)"

    bad_provider = {"id": "bad", "type": "agent", "goal": "x", "provider": "openai-codex"}
    errors = wfcommon.validate_graph_errors([bad_provider])
    assert any(e["field"] == "provider" and "model" in e["msg"] for e in errors), errors

    # A literal equal to a configured alias target bakes its provider like an alias does
    # (est-2ek.1.46: a bare `-m openai-codex/...` died HTTP 400 on the seat default route);
    # aliases remain accepted as aliases.
    literal = [{"id": "literal", "type": "agent", "goal": "x", "model": "openai-codex/gpt-6-luna"}]
    alias = [{"id": "alias", "type": "agent", "goal": "x", "model": "luna"}]
    assert door.resolve_models(literal)[0] is None
    assert (literal[0]["provider"], literal[0]["model"]) == ("openai-codex", "gpt-6-luna")
    assert door.resolve_models(alias)[0] is None and alias[0]["model"] == "luna"

    # Exercise the actual child command builder without launching Hermes or contacting a provider.
    run = Path(tmp) / "run"
    (run / "nodes").mkdir(parents=True)
    node = {"id": "child", "type": "agent", "goal": "route", "model": "gpt-6-luna",
            "provider": "openai-codex",
            # #709: the funnel strips both pairs before Popen — the split-ness
            # under test is proven by the JOURNALED pairs below (two distinct
            # flags, never the joined "provider/model" token), not by argv.
            "require_route": False}
    captured = []
    import subprocess as _spx
    _dummy = _spx.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    _dummy.wait(timeout=30)   # a REAL dead child: /proc gone, killpg ESRCH
    _dummy_pid = _dummy.pid   # own group leader, killable exactly like the truth

    class FakeProcess:
        # #709 darwin red-to-truth: pid must NOT be the test's own pid — darwin's
        # tree-proof channel KILLs the child's group at settle (killpg, each real
        # child is its own group leader via start_new_session), so a fake that
        # hands back os.getpid() SIGKILLs the process running the assertions.
        # A real, already-reaped pid is killable and census-invisible on BOTH
        # platforms — the happy path stays the happy path.
        # Call-aware too: on darwin run_child's aux probes ride the same patched
        # Popen (stdout=PIPE), so the fake answers quietly unless THIS call
        # carries a real log file — the child entry is then picked by its file
        # stdout, not by capture order.
        pid = _dummy_pid
        returncode = 0

        def __init__(self, argv, kwargs):
            self.argv = argv
            self.kwargs = kwargs
            captured.append((argv, kwargs))

        def communicate(self, timeout=None):
            so = self.kwargs.get("stdout")
            if hasattr(so, "write"):
                so.write('```json\n{"routed": true}\n```\n')
                so.flush()

        def poll(self):            # the runner polls (#18 liveness) instead of blocking
            self.communicate()
            return self.returncode

    def fake_popen(argv, **kwargs):
        return FakeProcess(argv, kwargs)

    meta = {
        "_run": run, "hermes_bin": "not-executed", "_procs": {},
        "_procs_lock": threading.Lock(), "_stop": threading.Event(), "_spawn_n": {}, "node_timeout": 5,
    }
    with patch.object(engine.subprocess, "Popen", fake_popen):
        child = engine.run_child(meta, node, {"child": node}, "route", "", None)
    assert child["status"] == "done", child
    _kids = [c for c in captured if hasattr(c[1].get("stdout"), "write")]
    assert _kids, captured
    argv = _kids[0][0]
    # #709 truth: the pairs never ride the child argv (funnel strip, pre-Popen);
    # what the builder appended — SPLIT into -m and --provider, never the joined
    # "provider/model" token — is durable in the run's dispatch.warn journal.
    assert "-m" not in argv and "--provider" not in argv and "gpt-6-luna" not in argv, argv
    _ev = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines()]
    _stripped = [p for e in _ev if e.get("event") == "dispatch.warn"
                 and e.get("kind") == "frozen_route_strip" for p in e.get("stripped") or []]
    assert _stripped == [["-m", "gpt-6-luna"], ["--provider", "openai-codex"]], _stripped
    assert "openai-codex/gpt-6-luna" not in [v for _, v in _stripped], _stripped

    # ------------------------------------------------------------------
    # 2.0 (bd_2026-11-13-jtf): the ONE tail route's bounds — containment,
    # the 16 KiB window, and attempt/index as ids. The client never sends a
    # path; the path comes ONLY from the record and must stay inside
    # <run>/logs; out-of-range params are a 404, never a best guess.
    # ------------------------------------------------------------------
    spec = importlib.util.spec_from_file_location("tail_test_api", BUILD / "dashboard" / "plugin_api.py")
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    assert api.LOG_TAIL == 16384, "the ONE tail cap is the ratified constant"
    js = (BUILD / "desktop" / "plugin.js").read_text()
    assert "const TAIL_BYTES = 16384" in js, "client and server mirror the same ratified constant"

    run2 = Path(tmp) / "tailrun"
    logs = run2 / "logs"
    (run2 / "nodes").mkdir(parents=True)
    logs.mkdir()
    def rec(nid_obj, name):
        (run2 / "nodes" / f"{name}.json").write_text(json.dumps(nid_obj))
    big = "HEAD-MARKER\n" + ("p" * (20 * 1024)) + "\nEND-BYTES"
    (logs / "f.1.a2.log").write_text(big)
    (logs / "f.1.a1.log").write_text("ATTEMPT-1")
    (logs / "f.1.a0.log").write_text("ATTEMPT-0")
    (logs / "f.1.a2.prompt.md").write_text("PROMPT-BODY")
    (logs / "a.a1.log").write_text("PLAIN-LOG")
    (run2 / "outside.log").write_text("OUTSIDE-LOGS")
    rec({"status": "done",
         "log_path": str(logs / "f.1.a2.log"), "prompt_path": str(logs / "f.1.a2.prompt.md")}, "f.1")
    rec({"status": "done", "log_path": str(logs / "a.a1.log")}, "a")
    rec({"status": "done", "log_path": str(run2 / "outside.log")}, "esc1")          # sibling of logs/
    rec({"status": "done", "log_path": str(logs / ".." / "outside.log")}, "esc2")   # textual escape
    rec({"status": "done"}, "nolog")                                                # no fact at all

    tail = api._node_log_tail
    # window: the last 16384 bytes, seeked — the head aged out, the end rides.
    out = tail(run2, "f", index=1, attempt=None, kind="log", tail=16384)
    assert out and out["bytes"] == 16384 and out["size"] == len(big.encode()), out
    assert out["content"].endswith("END-BYTES") and "HEAD-MARKER" not in out["content"], \
        "the tail is a bounded window, never a whole-file read"
    assert out["node"] == "f.1" and out["id"] == run2.name, "the response echoes ids, not paths"
    # attempt bounds: the record's own .a2 by default; siblings by number; a
    # negative class is refused outright; a missing sibling is a 404.
    assert tail(run2, "f", 1, 1, "log", 16384)["content"] == "ATTEMPT-1"
    assert tail(run2, "f", 1, 0, "log", 16384)["content"] == "ATTEMPT-0", "attempt 0 is a real sibling, not a sentinel"
    assert tail(run2, "f", 1, -1, "log", 16384) is None, "attempt < 0 is out of bounds"
    assert tail(run2, "f", 1, 5, "log", 16384) is None, "an unnumbered attempt is a 404, never a guess"
    # index bounds: the item record is addressed by index; unknown index = no record.
    assert tail(run2, "f", 7, None, "log", 16384) is None, "an index with no record is a 404"
    assert tail(run2, "a", None, None, "log", 16384)["content"] == "PLAIN-LOG"
    assert tail(run2, "nolog", None, None, "log", 16384) is None, "a record without log_path honestly has no tail"
    # containment: the record may name a path, but only inside <run>/logs survives.
    assert tail(run2, "esc1", None, None, "log", 16384) is None, "a path outside logs/ is refused"
    assert tail(run2, "esc2", None, None, "log", 16384) is None, "a textual ../ escape is refused after resolve"
    # kinds and malformed params: only log|prompt, only integers.
    assert tail(run2, "f", 1, None, "prompt", 16384)["content"] == "PROMPT-BODY"
    assert tail(run2, "f", 1, None, "sh", 16384) is None
    assert tail(run2, "f", 1, None, "log", 0) is None and tail(run2, "f", 1, None, "log", 16385) is None, \
        "tail is bounded to (0, 16384]"
    assert tail(run2, "f", 1, None, "log", 64)["bytes"] == 64, "a sub-window tail is honored exactly"
    assert tail(run2, "f", 1, "x", "log", 16384) is None, "a non-numeric attempt is refused"
    assert tail(run2, "../f", None, None, "log", 16384) is None, "the node id must match ID_OK — ids, never paths"

    # _view (full): a fan node's committed per-item files merge as
    # item_records[index] over the SAME closed fact set — the route-side half of
    # "item selection reads the item's record". A node without item files keeps
    # the exact pre-2.0 key set (absent, never an empty costume).
    run3 = Path(tmp) / "viewrun"
    (run3 / "nodes").mkdir(parents=True)
    byid3 = {
        "workers": {"id": "workers", "type": "agent", "goal": "g",
                    "fanout": {"goal": "g {item}", "items": ["a", "b"]}},
    }
    (run3 / "graph.json").write_text(json.dumps({"name": "viewrun", "nodes": list(byid3.values())}))
    (run3 / "run.json").write_text(json.dumps({"run_id": "viewrun", "name": "viewrun", "started": 4102444800.0}))
    e0 = wfcommon.efp(byid3, byid3["workers"])
    (run3 / "nodes" / "workers.json").write_text(json.dumps(
        {"status": "done", "efp": e0, "fp_rule_version": wfcommon.FP_RULE_VERSION,
         "output": {"all_results": [{"index": 0, "status": "done", "item": "a"}]}}))
    (run3 / "nodes" / "workers.1.json").write_text(json.dumps(
        {"status": "failed", "error_class": "cancelled", "error": "stopped", "final": "bye",
         "refusal": None, "attempts": 1, "attempts_log": [], "harvest": None, "output": None,
         "ms": 5, "started": 1, "log_path": "logs/workers.1.a1.log", "prompt_path": None,
         "efp": e0, "skey": "s", "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    (run3 / "events.jsonl").write_text(json.dumps({"ts": 4102444800.0, "event": "run.started"}) + "\n")
    view = api._view(run3, full=True)
    assert view, "the trio is valid through the shared read model"
    ir = view["nodes"]["workers"].get("item_records")
    assert ir and ir[1]["status"] == "failed" and ir[1]["error_class"] == "cancelled" \
        and ir[1]["final"] == "bye", ir
    assert set(ir[1]) >= {"status", "error_class", "refusal", "error", "attempts", "attempts_log",
                          "final", "harvest", "output", "ms", "started", "log_path", "prompt_path",
                          "efp", "skey", "steer"}, sorted(ir[1])
    assert 0 not in ir or ir[0]["status"] == "unknown", "an unwritten item index honestly has no facts"

print("ALL PASS")
