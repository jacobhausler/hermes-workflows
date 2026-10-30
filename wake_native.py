"""Deliver a stable workflow wake through an existing gateway admission."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

SCHEMA = "wake-native-admission/v1"
DISCOVER_TIMEOUT_S = 2.0
RPC_TIMEOUT_S = 30.0
ADMIT_DEADLINE_S = 60.0
ACCEPTED_STATES = frozenset({"queued", "started", "terminal"})
REFUSAL_REASONS = frozenset({
    "permission_denied", "not_found", "unauthorized", "forbidden",
    "invalid_params", "session_locked", "ticket_denied", "principal_mismatch",
})


class NativeAdmissionError(Exception):
    def __init__(self, reason, retry=True):
        super().__init__(reason)
        self.reason = reason
        self.retry = retry


def discover(home):
    try:
        from hermes_cli.gateway_runtime import discover_gateway_endpoint
    except ImportError:
        return None
    try:
        result = discover_gateway_endpoint(str(home), timeout=DISCOVER_TIMEOUT_S)
    except Exception as exc:
        raise NativeAdmissionError("discovery_error") from exc
    state = getattr(result, "state", None)
    if state == "absent":
        return None
    if state != "ready":
        reason = "discovery_refused" if state == "inaccessible" else "discovery_not_ready"
        raise NativeAdmissionError(reason, retry=state != "inaccessible")
    endpoint = getattr(result, "endpoint", None)
    if endpoint is None:
        raise NativeAdmissionError("discovery_missing_endpoint")
    return endpoint


@asynccontextmanager
async def _connect(endpoint):
    if endpoint is None:
        raise NativeAdmissionError("refused_no_endpoint", retry=False)
    from hermes_cli.gateway_client import connect_gateway
    async with connect_gateway(endpoint=endpoint) as client:
        yield client


def _same_session(snapshot, sid):
    return (isinstance(snapshot, dict)
            and snapshot.get("session_id") == sid
            and snapshot.get("stored_session_id") == sid)


async def _admit(client, sid, text, input_id):
    snapshot = await client.rpc("session.resume", session_id=sid, _timeout=RPC_TIMEOUT_S)
    if not _same_session(snapshot, sid):
        raise NativeAdmissionError("session_identity_mismatch", retry=False)
    receipt = await client.rpc("prompt.submit", session_id=sid, text=text,
                               input_id=input_id, queued=True, unattended=False,
                               _timeout=RPC_TIMEOUT_S)
    admission_id = receipt.get("admission_id") if isinstance(receipt, dict) else None
    if not isinstance(admission_id, str) or not admission_id:
        raise NativeAdmissionError("invalid_submit_receipt")
    readback = await client.rpc("prompt.receipt", session_id=sid,
                                admission_id=admission_id, _timeout=RPC_TIMEOUT_S)
    if not isinstance(readback, dict) or readback.get("admission_id") != admission_id:
        raise NativeAdmissionError("admission_identity_mismatch", retry=False)
    ref = readback.get("ref")
    if not isinstance(ref, dict) or ref.get("session_id") != sid:
        raise NativeAdmissionError("receipt_session_mismatch", retry=False)
    return {"admission_id": admission_id, "submit_status": receipt.get("status"),
            "status": readback.get("status")}


def deliver(sid, text, tid, home):
    async def admit(endpoint):
        async with _connect(endpoint) as client:
            return await _admit(client, sid, text, tid)

    try:
        endpoint = discover(home)
        if endpoint is None:
            return {"outcome": "unavailable"}
        result = asyncio.run(asyncio.wait_for(admit(endpoint), timeout=ADMIT_DEADLINE_S))
    except NativeAdmissionError as exc:
        return {"outcome": "retry" if exc.retry else "refused", "reason": exc.reason}
    except Exception as exc:
        code = str(exc).strip().split(":", 1)[0].split(" ", 1)[0]
        if code in REFUSAL_REASONS:
            return {"outcome": "refused", "reason": code}
        return {"outcome": "retry", "reason": "transport_error"}
    if result.get("status") in ACCEPTED_STATES:
        return {"outcome": "delivered", "schema": SCHEMA, **result}
    return {"outcome": "retry", "reason": "receipt_not_accepted"}
