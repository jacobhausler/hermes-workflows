"""A wake is delivered only after an exact native admission readback."""
import importlib.util
import os
from pathlib import Path
from contextlib import asynccontextmanager
import sys
import types
import unittest
from unittest.mock import patch

SOURCE = Path(os.environ.get('WAKE_NATIVE_MODULE', Path(__file__).parents[1] / 'wake_native.py'))
spec = importlib.util.spec_from_file_location('native_wake_identity_target', SOURCE)
assert spec is not None and spec.loader is not None
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)

SID = 'local-owner-session'


class Client:
    def __init__(self, snapshot=None, readback=None, failure=None):
        self.snapshot = snapshot if snapshot is not None else {'session_id': SID, 'stored_session_id': SID}
        self.readback = readback if readback is not None else {
            'admission_id': 'admission-1', 'ref': {'session_id': SID}, 'status': 'queued'}
        self.failure = failure
        self.calls = []

    async def rpc(self, method, **params):
        self.calls.append((method, params))
        if self.failure:
            raise self.failure
        return {'session.resume': self.snapshot,
                'prompt.submit': {'admission_id': 'admission-1', 'status': 'queued'},
                'prompt.receipt': self.readback}[method]


class AdmissionIdentity(unittest.TestCase):
    def send(self, client):
        @asynccontextmanager
        async def connect(endpoint):
            self.assertEqual(endpoint, 'discovered-endpoint')
            yield client
        with patch.object(native, 'discover', return_value='discovered-endpoint'), patch.object(native, '_connect', connect):
            return native.deliver(SID, 'workflow transition', 'stable-input-id', '/home')

    def test_exact_readback_accepts_and_retains_stable_input(self):
        client = Client()
        result = self.send(client)
        self.assertEqual(result['outcome'], 'delivered')
        self.assertEqual(result['admission_id'], 'admission-1')
        self.assertEqual([m for m, _ in client.calls], ['session.resume', 'prompt.submit', 'prompt.receipt'])
        submit = client.calls[1][1]
        self.assertEqual(submit['input_id'], 'stable-input-id')
        self.assertIs(submit['queued'], True)
        self.assertIs(submit['unattended'], False)

    def test_resume_cannot_switch_session(self):
        client = Client(snapshot={'session_id': 'other', 'stored_session_id': 'other'})
        self.assertEqual(self.send(client)['outcome'], 'refused')
        self.assertEqual([m for m, _ in client.calls], ['session.resume'])

    def test_resume_alias_cannot_switch_stored_identity(self):
        client = Client(snapshot={'session_id': SID, 'stored_session_id': 'other'})
        self.assertEqual(self.send(client)['outcome'], 'refused')
        self.assertEqual(len(client.calls), 1)

    def test_missing_resume_identity_is_not_acceptance(self):
        client = Client(snapshot={})
        self.assertEqual(self.send(client)['outcome'], 'refused')
        self.assertEqual(len(client.calls), 1)

    def test_receipt_must_name_returned_admission(self):
        client = Client(readback={'admission_id': 'other', 'ref': {'session_id': SID}, 'status': 'queued'})
        self.assertEqual(self.send(client)['outcome'], 'refused')

    def test_receipt_must_name_same_session(self):
        client = Client(readback={'admission_id': 'admission-1', 'ref': {'session_id': 'other'}, 'status': 'queued'})
        self.assertEqual(self.send(client)['outcome'], 'refused')

    def test_missing_readback_never_uses_submit_status(self):
        self.assertNotEqual(self.send(Client(readback={}))['outcome'], 'delivered')

    def test_missing_readback_status_is_retryable(self):
        client = Client(readback={'admission_id': 'admission-1', 'ref': {'session_id': SID}})
        self.assertEqual(self.send(client)['outcome'], 'retry')

    def test_unknown_readback_is_retryable(self):
        client = Client(readback={'admission_id': 'admission-1', 'ref': {'session_id': SID}, 'status': 'unknown'})
        self.assertEqual(self.send(client)['outcome'], 'retry')

    def test_transport_error_does_not_retain_raw_secret(self):
        result = self.send(Client(failure=RuntimeError('Bearer private-credential-in-exception')))
        self.assertEqual(result['outcome'], 'retry')
        self.assertNotIn('private-credential', str(result))


class DiscoveryBoundary(unittest.TestCase):
    def discover(self, state, endpoint=None):
        package = types.ModuleType('hermes_cli')
        package.__path__ = []
        module = types.ModuleType('hermes_cli.gateway_runtime')
        setattr(module, 'discover_gateway_endpoint', lambda home, timeout: types.SimpleNamespace(state=state, endpoint=endpoint))
        with patch.dict(sys.modules, {'hermes_cli': package, 'hermes_cli.gateway_runtime': module}):
            return native.deliver(SID, 'wake', 'stable-input-id', '/home')

    def test_absent_owner_allows_legacy_compatibility(self):
        self.assertEqual(self.discover('absent')['outcome'], 'unavailable')

    def test_authorization_refusal_cannot_use_legacy_transport(self):
        self.assertEqual(self.discover('inaccessible')['outcome'], 'refused')

    def test_draining_owner_remains_retryable_not_unavailable(self):
        self.assertEqual(self.discover('draining')['outcome'], 'retry')

    def test_ready_without_endpoint_cannot_start_an_owner(self):
        self.assertEqual(self.discover('ready')['outcome'], 'retry')


if __name__ == '__main__':
    unittest.main()
