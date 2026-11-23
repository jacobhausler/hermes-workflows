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

print("ALL PASS")
