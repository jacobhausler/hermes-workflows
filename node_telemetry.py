"""est-wqml6: per-node telemetry for CLI-spawned children (env-gated sidecar).

The cross-process channel between a workflow child's own observer hooks and the
runner. CLI-spawned children never fire the in-process accounting hooks (the
P3 spool covers delegate_task leaves only; docs/native-hooks.md states the
blind spot), so the child reports for itself from inside its own process:

  * GATE: registration happens ONLY where the runner's spawn env pinned both
    ``HERMES_WF_TELEMETRY`` (the join key: the session-key prefix, stable
    across retries) and ``HERMES_WF_RUN_DIR`` (F1's pin). Gateway, door, and
    interactive sessions carry neither, register nothing, and pay nothing, in the spirit of the host's cheap-path rule: only hooks we consume.
  * WRITE: counters accumulate in process memory into ONE small JSON
    aggregate (``api_calls``, ``tool_calls``, ``input_tokens``,
    ``output_tokens``, and the ``total_tokens`` roll-up) rewritten atomically
    (tmp + ``os.replace``, the repo store idiom) per event at
    ``<run dir>/telemetry/<sanitized key>.json``. A retried attempt rewrites
    the same file, so the aggregate reflects the latest attempt, the same
    law as ``output`` riding the latest record.
  * JOIN: the runner folds and CONSUMES the sidecar at the settle seam
    (``wf._stamp_served``, the commit-edge stamp every ladder path crosses);
    corrupt files are consumed too, so the dir stays bounded. The fact rides
    the committed node record and surfaces through ``node_facts``.
  * FAIL-OPEN: P3's law, verbatim in force: a telemetry bug can suppress
    telemetry, never break the worker, a settle, or a request handler. Every
    path is guarded; absent, corrupt, or un-writable telemetry reads absent,
    never a fabricated zero (rule 8).

The env var doubles as the join key on purpose (peer mechanism, SYNTHESIS #11):
the runner names the key at spawn, the child writes where the pins point, the
runner joins by the same key at settle. Stdlib only; no host imports.
"""
import json
import os
import sys
from pathlib import Path

TELEMETRY_ENV = "HERMES_WF_TELEMETRY"
RUN_DIR_ENV = "HERMES_WF_RUN_DIR"   # the F1 pin the runner already sets per spawn


def _safe(key):
    """Filesystem-safe sidecar name (the join key carries wf: colons)."""
    return str(key).replace("/", "_").replace("\\", "_").replace(":", "_")


def sidecar_path(run_dir, key):
    return Path(run_dir) / "telemetry" / (_safe(key) + ".json")


def node_key(skey):
    """The join key a settle folds by: the session-key prefix of a full skey
    (skey_for appends ``:<efp8>.<nonce>`` per spawn; the prefix is the
    per-node constant the spawn env pinned). Empty skey -> empty key."""
    return str(skey).rsplit(":", 1)[0] if skey else ""


def load(run_dir, key):
    """The persisted aggregate, or None for missing/corrupt/non-dict/empty:
    absent telemetry is the designed degradation, never a zero."""
    try:
        data = json.loads(sidecar_path(run_dir, key).read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) and data else None


def clear(run_dir, key):
    """Remove a sidecar; idempotent and fail-open."""
    try:
        sidecar_path(run_dir, key).unlink(missing_ok=True)
    except Exception:
        pass


def fold_at_settle(run_dir, skey):
    """Read-and-consume the child's aggregate at settle (corrupt files
    included, so the telemetry dir cannot grow without bound). Fail-open:
    anything un-read foldable returns None; this never raises."""
    key = node_key(skey)
    if not key:
        return None
    try:
        data = load(run_dir, key)
        clear(run_dir, key)
        return data
    except Exception:
        return None


def register_observer_hooks(ctx):
    """Register the consumed stock hooks (post_api_request, post_tool_call)
    when, and only when, both spawn pins exist. Returns the number of hooks
    registered (0 = gate closed, ctx unusable, or any failure: fail-open,
    never raises). Each call builds a fresh recorder closure, so the process
    that hosts the gate owns exactly one node key.
    """
    try:
        key = os.environ.get(TELEMETRY_ENV)
        root = os.environ.get(RUN_DIR_ENV)
        if not key or not root:
            return 0
        register_hook = getattr(ctx, "register_hook", None)
        if not callable(register_hook):
            return 0
        state = {}
        path = sidecar_path(root, key)

        def _flush():
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
            tmp.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
            os.replace(tmp, path)

        def _swallow(exc):
            print(f"hermes-workflows: telemetry write failed for {key}: {exc}",
                  file=sys.stderr)

        def _add_usage(usage):
            if not isinstance(usage, dict):
                return                       # absent/junk usage counts the call, invents no tokens (R2)
            ti = usage.get("input_tokens", usage.get("prompt_tokens"))
            to = usage.get("output_tokens", usage.get("completion_tokens"))
            for k, v in (("input_tokens", ti), ("output_tokens", to)):
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    state[k] = int(state.get(k, 0)) + int(v)
            if "input_tokens" in state or "output_tokens" in state:
                state["total_tokens"] = int(state.get("input_tokens", 0)) + \
                    int(state.get("output_tokens", 0))

        def _on_post_api_request(**kwargs):
            try:
                state["api_calls"] = int(state.get("api_calls", 0)) + 1
                _add_usage(kwargs.get("usage"))
                _flush()
            except Exception as exc:         # noqa: BLE001 - fail-open law
                _swallow(exc)

        def _on_post_tool_call(**kwargs):
            try:
                state["tool_calls"] = int(state.get("tool_calls", 0)) + 1
                _flush()
            except Exception as exc:         # noqa: BLE001 - fail-open law
                _swallow(exc)

        register_hook("post_api_request", _on_post_api_request)
        register_hook("post_tool_call", _on_post_tool_call)
        return 2
    except Exception:                        # noqa: BLE001 - a gate that cannot gate registers nothing
        return 0
