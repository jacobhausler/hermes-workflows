"""Concurrent committed failures must not miss healthy native admission."""
import importlib.util
import fcntl
import json
from pathlib import Path
import sys
import tempfile
import threading
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wf


def concurrent_failures():
    with tempfile.TemporaryDirectory(prefix="wf-native-concurrent-") as tmp:
        run = Path(tmp)
        nodes = [{"id": x, "type": "agent", "goal": "work"} for x in ("a", "b", "healthy")]
        byid = {n["id"]: n for n in nodes}
        (run / "graph.json").write_text(json.dumps({"name": "concurrent", "nodes": nodes}))
        (run / "run.json").write_text(json.dumps({"owner": {"session_id": "owner", "platform": "local"}}))
        initializing = threading.Event()
        release_init = threading.Event()
        healthy_started = threading.Event()
        release_healthy = threading.Event()
        second_started = threading.Event()
        admissions = []
        errors = []
        real_spec = importlib.util.spec_from_file_location
        delivery_barrier = threading.Barrier(2)

        def spec(name, path, *args, **kwargs):
            result = real_spec(name, path, *args, **kwargs)
            if Path(path).name == "wake_native.py":
                assert result is not None and result.loader is not None
                original = result.loader.exec_module

                def load(module):
                    initializing.set()
                    assert release_init.wait(10), "initialization latch timed out"
                    original(module)

                    def deliver(sid, text, tid, home):
                        # Delivery must not retain graph.lock. A different thread
                        # must be able to read the committed graph during admission.
                        with (run / "graph.lock").open("a+b") as lock:
                            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        delivery_barrier.wait(5)
                        assert not release_healthy.is_set(), "sibling drained before admission"
                        admissions.append(tid)
                        return {"outcome": "delivered", "admission_id": tid, "status": "queued"}

                    module.deliver = deliver

                result.loader.exec_module = load
            return result

        def commit(node):
            try:
                if node["id"] == "b":
                    second_started.set()
                wf.save_node(run, node, byid, {"status": "failed", "error_class": "precondition"})
            except BaseException as exc:
                errors.append(exc)

        def healthy():
            healthy_started.set()
            release_healthy.wait(15)

        wf._WAKE_NATIVE = None
        wf._WAKE_NATIVE_TRIED = False
        threads = [threading.Thread(target=commit, args=(node,)) for node in nodes[:2]]
        sibling = threading.Thread(target=healthy)
        with patch.object(wf, "_outbound_bridge", return_value=None), patch.object(wf.importlib.util, "spec_from_file_location", side_effect=spec):
            sibling.start()
            try:
                assert healthy_started.wait(5)
                threads[0].start()
                assert initializing.wait(5)
                threads[1].start()
                assert second_started.wait(5)
                # Observe the second loader entering before releasing the first.
                # It may wait for initialization; completing early is not required.
                assert second_entered.wait(5)
                release_init.set()
                for thread in threads:
                    thread.join(10)
                    assert not thread.is_alive(), "failure commit deadlocked"
                assert not errors, errors
                assert sibling.is_alive() and not release_healthy.is_set()
                rows = wf._wake_ledger_read(run)[0]
                assert len(admissions) == len(set(admissions)) == 2, (admissions, rows)
                assert len(rows) == 2 and all(row.get("delivered") for row in rows), rows
                for node in nodes[:2]:
                    wf._notify_node_failure(run, node["id"])
                assert len(admissions) == 2, "settled transition admitted twice"
            finally:
                release_init.set()
                release_healthy.set()
                for thread in threads:
                    if thread.ident is not None:
                        thread.join(10)
                sibling.join(5)


second_entered = threading.Event()
real_native = wf._native_wake
native_calls = []


def observed_native():
    native_calls.append(threading.get_ident())
    if len(native_calls) == 2:
        second_entered.set()
    return real_native()


def optional_loaders():
    for loader, value, tried in (
        (wf._native_wake, "_WAKE_NATIVE", "_WAKE_NATIVE_TRIED"),
        (wf._outbound_bridge, "_OUTBOUND", "_OUTBOUND_TRIED"),
    ):
        for mode in ("absent", "invalid_spec", "broken_import"):
            setattr(wf, value, None)
            setattr(wf, tried, False)
            if mode == "absent":
                seam = patch.object(wf.Path, "is_file", return_value=False)
            elif mode == "invalid_spec":
                seam = patch.object(wf.importlib.util, "spec_from_file_location", return_value=None)
            else:
                seam = patch.object(wf.importlib.util, "spec_from_file_location", side_effect=ImportError("broken optional adapter"))
            with seam as observed:
                assert loader() is None
                assert loader() is None
                assert observed.call_count == 1, (mode, observed.call_count)
                assert getattr(wf, tried) is True
        setattr(wf, value, None)
        setattr(wf, tried, False)
    print("PASS absent, invalid and failed optional loaders settle once without raising")


optional_loaders()
with patch.object(wf, "_native_wake", side_effect=observed_native):
    concurrent_failures()
print("PASS two distinct native admissions before healthy sibling drain; replay stable; graph reader live")
