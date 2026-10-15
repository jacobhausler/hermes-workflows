"""hooks_outbound.py — P1 outbound bridge: mirror typed lifecycle transitions to
an operator-configured HTTPS webhook. Default OFF, config-gated, fail-open.

The runner's typed run-level transitions (the same instances notify() pushes to
the owner session and appends to <run>/events.jsonl) can ALSO be mirrored to one
operator endpoint. This is notify()'s envelope discipline, not a second system:

  * ONE instance identity — `instance_id()` below is the sha256(run|event|
    discriminant)[:32] recipe notify()'s own tid line calls (via wf._wake_tid),
    so wake and outbound share one identity per transition instance; it rides
    the wire as Idempotency-Key, so the ENDPOINT (not this runner) owns retry
    collapse across transport retries.
  * bearer redaction on every persisted/logged field (the F4 net, ported): a
    stdlib error can embed the raw header value; nothing reaches disk raw.
  * NEVER raises into the run loop. Every attempt records a typed probe row in
    <run>/outbound.jsonl; every failure ALSO records a typed `outbound.failed`
    line in events.jsonl. A dead endpoint never costs a decided run its exit.
  * delivered-instance cache: outbound.jsonl rows with delivered=true form the
    dedupe set (durable, survives runner respawn — same law as wake.jsonl), so
    a retry of a DELIVERED instance writes nothing and POSTs nothing.
  * redirects are never followed (credentials must not ride a 30x; the redirect
    law wake obeys — a 3xx is recorded undelivered, retries stay on the
    configured host).

Config gate (fail-closed, DEFAULT OFF), read through the SAME owner-setting
helper the rest of the plugin uses (wfcommon.owner_setting — plugin ctx when a
door has one, raw config.yaml otherwise; `${VAR}` expansion; no restart):

    plugins.entries.hermes-workflows.settings.outbound_bridge:
      enabled: true                     # the operator switch
      url: "https://ops.example/webhook"  # https only; http only for loopback
      bearer: "${WF_OUTBOUND_TOKEN}"    # optional bearer token
      timeout_s: 10                     # optional, clamped 1..60
      events: ["run.*", "gate.held"]    # optional filter (exact or trailing *)

A per-run meta carrier may OPT IN when the operator shipped an endpoint without
switching it on globally: run.json `outbound_bridge: {"enabled": true}` or a
graph-level `meta.outbound_bridge: {"enabled": true}` subtree. Carriers can
never supply url/bearer (that authority is the operator's alone) and can never
re-arm an operator `enabled: false` floor. The submit grammar's top-level graph
keys are a CLOSED set, so a submitted graph cannot carry the meta subtree
today — the channel is read defensively for run dirs that do (hand-built runs,
future door support); the settings key is the supported lever, and a carrier
with no configured endpoint records a typed config failure, never silence.

Stdlib only; no host imports at module level. bind() receives the wfcommon
handle, notify()'s own discriminant function, and the runner's log fn — the
bridge is bound by the runner lazily (wf._outbound_bridge) and is inert if this
file is absent or broken (byte-identical degradation).
"""
import hashlib
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

SCHEMA = "wf-outbound/v1"            # the wire envelope (the only shape we POST)
LEDGER_SCHEMA = "outbound-probe/v1"  # the only shape outbound.jsonl ever holds
DEFAULT_TIMEOUT_S = 10.0             # wake's own window; a mirror must never stall a run
MIN_TIMEOUT_S, MAX_TIMEOUT_S = 1.0, 60.0
FAIL_CLASSES = ("config", "http_status", "redirect", "timeout", "transport")  # closed set

_common = None        # bound by bind(): the runner's PRIVATE wfcommon instance
_wake_identity = None  # bound by bind(): notify()'s own discriminant fn — not a copy
_log = None           # bound by bind(): the runner's events.jsonl voice

# Bearer/credential redaction — the F4 net ported verbatim from wf.py. A stdlib
# error can embed the whole header value ("Invalid header value b'Bearer
# <secret>'"), so EVERY persisted field runs this before it reaches disk.
_SECRET_PATTERNS = [
    re.compile(r"[Bb]earer\s+\S+"),                       # the wire scheme, any case
    re.compile(r"[Aa]uthorization['\"]?\s*[:=]\s*\S+"),   # header name + value
    re.compile(r"(?i)(api[_ -]?server[_ -]?key|secret|passwd|password|token)['\"]?\s*[:=]\s*\S+"),
]


def redact(value):
    """Cut credential shapes out of anything this module may persist or POST."""
    text = str(value)
    for pat in _SECRET_PATTERNS:
        text = pat.sub("[redacted]", text)
    return text


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def bind(wfcommon_mod, wake_identity_fn, log_fn):
    """Wire the bridge to the runner's world. Called once by wf._outbound_bridge
    right after the private spec-load; nothing reads config before this."""
    global _common, _wake_identity, _log
    _common, _wake_identity, _log = wfcommon_mod, wake_identity_fn, log_fn


def instance_id(run_name, event, discriminant):
    """THE transition-instance identity (B3 law, one recipe): sha256 over
    run|event|discriminant truncated to 32 hex chars — identical across retries
    of one lifecycle decision, fresh for every genuinely new one. notify()'s
    wake id and the outbound Idempotency-Key are this function's output; the
    bridge never mints a competing identity."""
    return hashlib.sha256(f"{run_name}\0{event}\0{discriminant}".encode()).hexdigest()[:32]


# ---------- config gate (fail-closed, default OFF) ----------

def _carrier_enabled(run):
    """Per-run opt-in carriers (NEVER url/bearer authority): run.json
    `outbound_bridge` first, then a graph-level `meta.outbound_bridge` subtree.
    True only for an explicit {"enabled": true}. Read defensively: an
    unreadable carrier is simply no opt-in, never a crash."""
    for path in (run / "run.json", run / "graph.json"):
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        cand = doc.get("outbound_bridge")
        if cand is None and path.name == "graph.json" and isinstance(doc.get("meta"), dict):
            cand = doc["meta"].get("outbound_bridge")
        if isinstance(cand, dict) and cand.get("enabled") is True:
            return True
    return False


def _url_refusal(url):
    """None when `url` is a deliverable endpoint, else the refusal reason.
    https always; http ONLY for loopback hosts (the local-collector / test-sink
    case — the same host shapes wake pins). A plaintext non-loopback url is
    refused: a bearer must never ride plaintext."""
    if not isinstance(url, str) or not url.strip():
        return "outbound_bridge: enabled but no url configured"
    try:
        parts = urllib.request.urlsplit(url.strip())
    except ValueError as e:
        return f"outbound_bridge: url unparseable ({type(e).__name__})"
    if parts.scheme == "https":
        return None
    if parts.scheme == "http" and (parts.hostname or "") in ("127.0.0.1", "localhost", "::1", "[::1]"):
        return None
    return (f"outbound_bridge: refused url {parts.scheme!r}://{parts.hostname!r} "
            "— https required (http only for loopback)")


def _filter_refusal(events):
    if events is None:
        return None
    if isinstance(events, list) and all(isinstance(x, str) and x for x in events):
        return None
    return "outbound_bridge: events filter must be a list of non-empty strings"


def _event_match(events, event):
    """Exact name or trailing-`*` prefix; a present filter that matches nothing
    simply means this transition is not this endpoint's business."""
    for pat in events:
        if pat.endswith("*"):
            if event.startswith(pat[:-1]):
                return True
        elif event == pat:
            return True
    return False


def _resolved(run, graph=None):
    """The gate + effective config for ONE mirror attempt, or None when this run
    is OFF. The operator's `enabled: false` (or a bare false setting) is a hard
    floor no carrier can re-arm; carriers can only raise an unset/true-without-
    switch setting. Returns a dict {url, bearer, timeout_s, events} (post
    refusal-checks) or raises nothing — refusals come back as ('refused', msg).
    """
    raw = None
    if _common is not None:
        try:
            raw = _common.owner_setting("outbound_bridge")
        except Exception:
            return None                      # a broken settings read is OFF, never a guess
    if raw is False or (isinstance(raw, dict) and raw.get("enabled") is False):
        return None                          # operator floor
    cfg = raw if isinstance(raw, dict) else {}
    enabled = raw is True or (isinstance(raw, dict) and raw.get("enabled") is True)
    if not enabled and not _carrier_enabled(run):
        return None                          # default OFF: nothing else is read or written
    bad = _url_refusal(cfg.get("url")) or _filter_refusal(cfg.get("events"))
    if bad:
        return ("refused", bad)
    try:
        timeout = float(cfg.get("timeout_s", DEFAULT_TIMEOUT_S))
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT_S          # malformed knob rides the default, loudly-clamped below
    timeout = max(MIN_TIMEOUT_S, min(MAX_TIMEOUT_S, timeout))
    return {"url": cfg["url"].strip(), "bearer": cfg.get("bearer"),
            "timeout_s": timeout, "events": cfg.get("events")}


# ---------- the ledger (probe rows = the durable delivered-cache) ----------

def _delivered_ids(run):
    """Delivered instance ids from outbound.jsonl, fail-open on every shape the
    file can be in (the wake-ledger discipline): corrupt lines, non-dict rows,
    an unreadable file degrade to 'nothing delivered yet', never a crash."""
    delivered = set()
    try:
        for line in (run / "outbound.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if isinstance(rec, dict) and rec.get("delivered") and rec.get("id"):
                delivered.add(rec["id"])
    except Exception:
        pass
    return delivered


def _append_ledger(run, rec):
    """One probe row; bearer-redacted, schema-stamped, and a write failure is
    loud on stderr and never fatal (the record-write law, wake's, unchanged)."""
    rec = dict(rec)
    rec["schema"] = LEDGER_SCHEMA
    if "id" in rec:
        rec["key"] = rec["id"]
    for f in ("error", "url"):
        if f in rec:
            rec[f] = redact(rec[f])
    try:
        with open(run / "outbound.jsonl", "a") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"WORKFLOW_OUTBOUND_RECORD_FAILED {run.name} {rec.get('event', '?')} ({redact(e)})",
              file=sys.stderr, flush=True)


def _fail_line(run, event, iid, error_class, error):
    """The typed events.jsonl line the spec law demands for every failure —
    written through the runner's own log voice, redacted before it is passed."""
    if _log is None:
        return
    try:
        _log(run, "outbound.failed", out_id=iid, out_event=event,
             error_class=error_class, error=redact(error))
    except Exception:
        pass                                 # the loud net itself must never raise


# ---------- the wire ----------

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Credentials must NEVER ride a redirect (wake's law, ported): the default
    handler follows 30x with a GET carrying Authorization cross-origin and the
    terminal 2xx would be recorded delivered. Hand the 3xx back to the caller."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _post(url, body, headers, timeout):
    """One POST through a fresh no-redirect opener; returns the status code.
    THE network seam (tests stand a local sink up against it; the module never
    touches the socket anywhere else)."""
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    opener = urllib.request.build_opener(_NoRedirect)
    with opener.open(req, timeout=timeout) as resp:
        return getattr(resp, "status", None) or resp.getcode()


# ---------- the seam notify() calls ----------

def mirror(run, event, key=None, graph=None):
    """Mirror ONE lifecycle transition instance to the operator endpoint.
    Config OFF / identity-unresolvable / already-delivered / filtered-out write
    NOTHING and POST nothing. Everything else POSTs at most once and records
    the attempt; every non-delivered outcome is typed in outbound.jsonl AND
    events.jsonl. NEVER raises — this is called from inside notify(), and a
    dead endpoint must not cost the run its exit."""
    try:
        cfg = _resolved(run, graph)
        if cfg is None:
            return
        if isinstance(cfg, tuple):                       # enabled-but-refused config
            _fail_line(run, event, "-", "config", cfg[1])
            _append_ledger(run, {"ts": now(), "event": event, "run_id": run.name,
                                 "delivered": False, "error": cfg[1], "error_class": "config"})
            return
        if cfg["events"] is not None and not _event_match(cfg["events"], event):
            return                                       # filtered: not an attempt, no row
        disc = _wake_identity(run, event, key, graph)
        if disc is None:
            return                                       # B3: unresolvable identity — silent, never duplicate
        iid = instance_id(run.name, event, disc)
        if iid in _delivered_ids(run):
            return                                       # delivered cache: zero rows, zero POSTs
        body = json.dumps({"schema": SCHEMA, "run_id": redact(run.name), "event": event,
                           "instance": iid, "discriminant": redact(disc), "ts": now()},
                          ensure_ascii=False, sort_keys=True).encode()
        headers = {"Content-Type": "application/json", "Idempotency-Key": iid}
        if cfg["bearer"]:
            headers["Authorization"] = "Bearer " + str(cfg["bearer"])
        rec = {"ts": now(), "event": event, "run_id": run.name, "id": iid,
               "url": redact(cfg["url"])}
        try:
            status = _post(cfg["url"], body, headers, cfg["timeout_s"])
            if 300 <= status < 400:
                rec.update(delivered=False, error_class="redirect",
                           error=f"HTTP {status} redirect not followed (undelivered)")
            else:
                rec["delivered"] = 200 <= status < 300
                if not rec["delivered"]:
                    rec.update(error_class="http_status", error=f"HTTP {status}")
        except urllib.error.HTTPError as e:
            rec.update(delivered=False, error_class="http_status", error=f"HTTP {e.code}")
        except (socket.timeout, TimeoutError):
            # A read timeout is NOT a delivery (wake's F5 law): we never saw a
            # status line, so the retry must stay live under the SAME id.
            rec.update(delivered=False, error_class="timeout",
                       error="timeout: read window closed before a response (retryable)")
        except Exception as e:
            # F4: the message can carry the bearer — persist TYPE + redacted text.
            rec.update(delivered=False, error_class="transport",
                       error=f"{type(e).__name__}: {redact(e)}")
        if not rec.get("delivered"):
            _fail_line(run, event, iid, rec.get("error_class", "transport"), rec.get("error", "?"))
        _append_ledger(run, rec)
    except Exception as e:                               # fail-open covers PREPARATION too
        try:
            _fail_line(run, event, "-", "transport", f"mirror-prep: {type(e).__name__}")
        except Exception:
            pass
