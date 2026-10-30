"""Native gateway owner-wake adapter — canonical WS admission, discover-only.

Why this module exists (estate lane native-wake-20261030): the wake sender in
wf.py knew only the legacy HTTP ``platforms.api_server`` route, so an owner
session owned by a READY canonical gateway recorded ``missing_endpoint`` and the
transition died unread (wake.jsonl of 20261030-014334-estate-agent-recovery-gr).
This adapter speaks the owner's own protocol instead of a parallel one.

Data shape — ``wake-native-admission/v1`` (defined BEFORE the logic):
  * ``input_id``  = the caller's stable wake instance id (the tid). Identical
    across retries and respawns of one transition decision, so an ambiguous
    call retried reuses stable identity and the owner's admission ledger replays
    instead of double-admitting.
  * ``receipt``   = ``{admission_id, submit_status, status}`` from
    ``prompt.submit``, read back through ``prompt.receipt``. A status in
    ``{queued, started, terminal}`` is DELIVERY ACCEPTANCE — the prompt is
    durably admitted against the exact stored owner session. It is NOT terminal
    task completion; the wake row records acceptance, nothing more.

Laws:
  * DISCOVER ONLY. ``gateway_runtime.discover_gateway_endpoint`` reads live
    control identity and is required to say ``ready``; ``ensure_gateway_runtime``
    is never imported. A wake must never spawn the daemon it is trying to reach.
  * NEVER pass ``endpoint=None`` to ``connect_gateway`` — that is the ensure
    form which may start a gateway. We only ever dial a discovered endpoint.
  * FAIL CLOSED on identity/authorization: a resume refusal
    (``permission_denied`` / ``not_found`` / ...) is returned as
    ``refused``; the caller must NOT retry it under another transport.
  * No credential ever crosses from this side: tickets are minted by core's own
    control-socket handshake inside ``connect_gateway``; we persist at most a
    bounded reason code (the ledger redactor runs again at append time).
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

SCHEMA = "wake-native-admission/v1"

# Discovery is a live control-socket read on a loopback owner: a short budget
# keeps a wedged probe from stalling the runner; the tri-state retry re-drives.
DISCOVER_TIMEOUT_S = 2.0
RPC_TIMEOUT_S = 30.0
ADMIT_DEADLINE_S = 60.0

# A receipt in one of these states is acceptance of THIS wake (durable admission
# bound to the exact session). `terminal` on readback can only mean this very
# input_id's turn already settled (server replays by input_id) — still accepted.
ACCEPTED_STATES = frozenset({"queued", "started", "terminal"})

# Bounded reason codes from gateway_client.rpc_error: refusals that mean THIS
# identity/authorization is wrong, not that the wire had a bad day. Anything
# else (timeouts, session_busy, request_failed, connection lost) is try-later:
# the SAME input_id makes the retry safe.
REFUSAL_REASONS = frozenset({
    "permission_denied", "not_found", "unauthorized", "forbidden",
    "invalid_params", "session_locked", "ticket_denied", "principal_mismatch",
})


class NativeAdmissionError(Exception):
    """A bounded adapter-level failure (never carries credentials or raw peer data)."""


def discover(home):
    """The ready canonical endpoint for this home, or None.

    Discover ONLY: ``discover_gateway_endpoint`` never spawns, and a state that
    is not exactly ``ready`` (draining/starting/inaccessible/absent) is treated
    as no owner to wake — the caller falls back to the documented legacy path.
    Every import/lookup error degrades to None (no hermes_cli on the box == no
    native owner, byte-identical to the pre-adapter head).
    """
    try:
        from hermes_cli.gateway_runtime import discover_gateway_endpoint
    except Exception:
        return None
    try:
        disc = discover_gateway_endpoint(str(home), timeout=DISCOVER_TIMEOUT_S)
    except Exception:
        return None
    if getattr(disc, "state", None) != "ready":
        return None
    return getattr(disc, "endpoint", None)


@asynccontextmanager
async def _connect(endpoint):
    """Dial the DISCOVERED endpoint as-is — the `endpoint=` form that can never
    start a gateway. The single transport seam tests replace."""
    if endpoint is None:
        raise NativeAdmissionError("refused_no_endpoint")   # the ensure form is banned here
    from hermes_cli.gateway_client import connect_gateway
    async with connect_gateway(endpoint=endpoint) as client:
        yield client


async def _admit(client, sid, text, input_id):
    """One admission turn of the wake protocol: resume the EXACT owner session
    (resume IS the subscribe), submit the runner-authored text under the stable
    input_id, queued and attended (never unattended — that would impersonate an
    operator batch flag), then read the durable receipt back."""
    await client.rpc("session.resume", session_id=sid)
    receipt = await client.rpc("prompt.submit", session_id=sid, text=text,
                               input_id=input_id, queued=True, unattended=False,
                               _timeout=RPC_TIMEOUT_S)
    admission_id = (receipt or {}).get("admission_id")
    if not isinstance(admission_id, str) or not admission_id:
        raise NativeAdmissionError("invalid_response")       # try-later: retry replays by input_id
    readback = await client.rpc("prompt.receipt", session_id=sid,
                                admission_id=admission_id, _timeout=RPC_TIMEOUT_S)
    return {"admission_id": admission_id,
            "submit_status": (receipt or {}).get("status"),
            "status": (readback or {}).get("status") or (receipt or {}).get("status")}


def _reason_of(exc):
    """The bounded reason code of an error: GatewayRPCError's str() IS the code;
    a dotted exception name is a poor man's code; raw messages stay truncated."""
    reason = str(exc).strip() or type(exc).__name__
    return reason[:80]


def deliver(sid, text, tid, home):
    """Synchronous entry: ONE native admission attempt for wake ``tid``.

    Returns ``{"outcome": ...}``:
      delivered   — durable acceptance; ``admission_id`` + readback ``status`` ride along.
      refused     — identity/authorization refusal: fail closed, NEVER re-routed.
      retry       — ambiguous/transport: try-later under the SAME input_id.
      unavailable — no ready gateway discovered: caller may use the legacy path.
    Never raises, never prints, never touches an approval verb."""
    endpoint = discover(home)
    if endpoint is None:
        return {"outcome": "unavailable"}

    async def _run():
        async with _connect(endpoint) as client:
            return await _admit(client, sid, text, tid)

    try:
        out = asyncio.run(asyncio.wait_for(_run(), timeout=ADMIT_DEADLINE_S))
    except Exception as exc:
        reason = _reason_of(exc)
        head = reason.split(":", 1)[0].split(" ", 1)[0]
        outcome = "refused" if head in REFUSAL_REASONS else "retry"
        return {"outcome": outcome, "reason": reason}
    if out.get("status") in ACCEPTED_STATES:
        return {"outcome": "delivered", "schema": SCHEMA, **out}
    return {"outcome": "retry", "reason": f"status_{out.get('status')}"}
