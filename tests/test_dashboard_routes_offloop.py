"""est-ey31s: dashboard routes must be plain-def (threadpool) handlers.

Why: an `async def` FastAPI handler runs ON THE EVENT LOOP. Every route in
dashboard/plugin_api.py does blocking work (directory walks, file reads,
subprocess probes), so one /runs scan froze every other dashboard endpoint on
the serve process (measured: 1.27s first / 0.60s warm over a few hundred run
dirs). Plain `def` handlers dispatch to the threadpool and cannot stall the
loop. This test pins the shape structurally against silent regression.
"""
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / 'dashboard' / 'plugin_api.py'


def _load():
    spec = importlib.util.spec_from_file_location('pa_routes_offloop', str(SPEC_PATH))
    pa = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = pa
    spec.loader.exec_module(pa)
    return pa


def test_dashboard_routes_are_sync_handlers():
    pa = _load()
    router = pa.router
    assert router is not None, 'fastapi must be importable in the suite env'
    names = {'list_runs', 'get_settings', 'get_run', 'get_node_log', 'release_gate'}
    seen = set()
    for route in router.routes:
        endpoint = getattr(route, 'endpoint', None)
        if endpoint is None or endpoint.__name__ not in names:
            continue
        seen.add(endpoint.__name__)
        assert not inspect.iscoroutinefunction(endpoint), (
            f'{endpoint.__name__} must be a plain def handler: blocking scans '
            f'inside async def freeze the dashboard event loop')
    assert seen == names, f'expected all dashboard routes present, missing {names - seen}'
