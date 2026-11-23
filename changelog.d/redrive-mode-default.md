# defaults(redrive): the mode default lands on the safe side

`redrive` mode is now OPTIONAL. An omitted mode takes
`same-fingerprint-resume` — the side that re-drives only the failed lanes and
REFUSES (writing nothing, `redrive_fingerprint_drift`) when a completed
receipt sits under a drifted fingerprint. The token-spending
`new-fingerprint-rerun` stays explicit-only. The response echoes the applied
`mode` and stamps `mode_defaulted: true` when the key was absent; an unknown
mode keeps the closed-set `redrive_mode_required` refusal. CLI usage becomes
`wf.py redrive <run_id> [--mode=<mode>]`.

Why (defaults audit 2026-11-23, against the owner north star "takes care of
the rest with smart defaults"): 10 of 10 production redrives over the
2026-11-21..23 run shelf (estate-bead-crew, wave6-council, lookbook) answered
the mandatory mode question with `same-fingerprint-resume`, and the drift case
is self-policing — the refusal costs one typed round-trip and zero writes,
which is the same worst case the no-default law had. Wake-consumer law #692
is amended, not repealed: what remains mandatory is the decision that SPENDS
tokens, never the safe resume.
