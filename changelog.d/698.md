chore(ci): roll HERMES_PIN v0.23.1 -> v0.23.3 (current stable; two lint rows retired)

CI pins the core for reproducible gates; v0.23.3 is current stable. The
re-pin probe ran clean at the tag: hook contract PASS, validate 57/57,
soft-guard variant green, and every consumed symbol intact. v0.23.3
published agent.retry_utils:parse_retry_after_seconds and
hermes_yaml:safe_load into the plugin API, so the private-import lint no
longer reports them — the two matching allow-list rows retired (v0.22.6
session_context precedent). The v0.23.1..v0.23.3 delta was scanned by
scripts/pin_delta_check.py (fail-closed gate, first run under it): every
finding allowlisted with per-class evidence in
docs/pin-delta-v0.23.3-allowlist.txt. No behavioral delta for plugin
runtimes beyond the tag bump; the measured requires_hermes floor is
unchanged.
