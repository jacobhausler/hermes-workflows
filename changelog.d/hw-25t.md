### Changed
- **Disposition legibility (E15):** `wfcommon.DISPOSITION_BY_STATUS` is ONE total
  state->disposition mapping (done/partial/failed/skipped/running/interrupted/
  registered, the failed+cancelled fact, and garbage -> UNKNOWN); `run_state`'s
  per-node view carries `disposition` for EVERY node — an unpinnable record says
  UNKNOWN as a value, never an absence read as success.
- **wake.jsonl first-class fields (E12):** every persisted wake row carries
  `skey`/`rev`/`attempts` as JSON values (null for honest absence) — the
  dedupe law's own inputs no longer require substring-parsing a
  backslash-escaped `|x:{...}` payload inside a JSON string. The legacy
  string payload still rides the text for one release.
- **Error-classification honesty (E19):** rc!=0 deaths classify from the
  child's LAST `Error:` line (the capture head is CLI banner — quoting it
  pointed 661/662 operators at a gateway restart that never was the disease);
  the resume-policy argv death types `resume_policy`, outside both ladders,
  terminal at the first attempt with the real refusal rendered.
- **quota_exhausted vs the credential window (E21):** deterministic
  account-state 429s (phrase set widened: quota limit, limit reached, billing,
  hard limit, usage cap, plus the #24 phrases) type `quota_exhausted` — the
  record carries `quota{identity, reset}` (`reset: null` when the provider
  names no horizon), the node parks pending at attempt 1, and the transient
  ladder draws zero respawns. `fatal_quota` remains a valid class name for
  historical records; the banner-named credential window keeps its own
  time-bound `ratelimit` park.
- **Route-gate refusal is one conversation (E20):** the substitution and
  expressibility refusals name the concrete state — the receipt file's
  absolute path and armed-at mtime, the EXACT strip arm that fired
  (`env WF_OMIT_POLICY_FLAGS=…` and/or the marker path with its mtime) — and
  surface the escapes: the receipt-deletion `rm` line, and a literal amend
  patch snippet that clears the hold.

### Fixed
- **Schema refusals name what they reject (E25):** every `validate()` error
  carries the violating JSON path AND the rejected value — type misses render
  the offender (containers as shape, long strings truncated), enum misses
  pair it with the allowed set, floors/caps report the count they saw, and a
  required-miss names the object's key-set when no rename suggestion fires.
  Any `error_class=schema` record text is now self-contained recovery
  instruction, not a bare rule name.

Tests: tests/test_disposition_table_25t.py, tests/test_wake_first_class_25t.py,
tests/test_resume_policy_25t.py, tests/test_quota_horizonless_25t.py,
tests/test_route_gate_dialog_25t.py, tests/test_schema_values_e25_25t.py, plus
retargeted equality pins in tests/test_boolean_schema_0924.py,
tests/test_numeric_type_validation_113.py, tests/test_schema_enum_107.py,
tests/test_schema_key_suggest_62.py, tests/test_schema_max_472.py,
tests/test_schema_min_96.py.
