#!/usr/bin/env python3
"""The child launcher is operator-controlled, never a tool argument."""
import importlib.util
import json
import os
import tempfile
from pathlib import Path

os.environ['HERMES_HOME'] = tempfile.mkdtemp(prefix='wf-launcher-test-')
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wf_door_launcher_test', ROOT / '__init__.py')
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

graph = {'name': 'probe', 'nodes': [{'id': 'a', 'type': 'echo', 'output': 'ok'}]}
result = json.loads(wf.handle({'action': 'run', 'graph': graph, 'hermes_bin': '/bin/false'}))
assert 'hermes_bin' in result.get('error', '') and 'not' in result['error'].lower(), result
assert 'hermes_bin' not in wf.WORKFLOW_PARAMS['properties']

class Context:
    """Core-faithful get_config: plugin-scoped, reserved roots RAISE.

    The real core (hermes_cli/plugins_state._plugin_relative_segments) rejects
    'plugins'/'model'/'security'/'settings' with ValueError, so the pre-fix fake
    that answered get_config('plugins') modeled an API core never had — which is
    how the illegal cross-plugin read slipped past this test. get_config(key)
    resolves plugins.entries.<id>.settings.<key>, so the real core answers the
    bare relative key with the same value.
    """
    RESERVED = {'model', 'plugins', 'security', 'settings'}
    settings = {'hermes_bin': '/config/hermes'}
    def get_config(self, key, default=None):
        if not isinstance(key, str) or '/' in key or key.split('.')[0].lower() in self.RESERVED:
            raise ValueError('Expected a plugin-relative config key such as \'endpoint\' '
                             'or \'retry.policy\'; global, cross-plugin, and traversal '
                             'paths are forbidden')
        cur = self.settings
        for seg in key.split('.'):
            if not isinstance(cur, dict) or seg not in cur:
                return default
            cur = cur[seg]
        return cur

old = os.environ.get('HERMES_WF_HERMES_BIN')
try:
    wf._CTX = Context()
    os.environ['HERMES_WF_HERMES_BIN'] = '/env/hermes'
    assert wf._hermes_bin() == '/config/hermes'
    wf._CTX = None
    assert wf._hermes_bin() == '/env/hermes'
finally:
    wf._CTX = None
    if old is None:
        os.environ.pop('HERMES_WF_HERMES_BIN', None)
    else:
        os.environ['HERMES_WF_HERMES_BIN'] = old
print('ALL PASS test_launcher_config')
