"""Pure output classifier — exit 0 is not success (est-imp1z / WF-GRAFT-2).

Semantics ported from the peer reference implementation
(iw-recon hermes_workflows/executor/outcome.py:33-131; their 2026-06 incident:
the agent CLI exits 0 after exhausted provider retries, printing
`API call failed after N retries: HTTP 429 …` as its final message). In THIS
repo the same lie reaches a verdict through extract_json's harvest-once
coercion — the failure line becomes {result: <prose>} and the node commits
`done` on garbage.

Authority order (FIXED by the bead acceptance — do not reorder):
    1. the self-reported node_outcome token  (the node's own verdict, either way)
    2. transient provider-error sentinels    (LINE-SCOPED, so prose cannot trip them)
    3. the exit code                         (0 -> success, non-zero -> deterministic)

The Verdict carries `kind` ∈ {success, transient, deterministic} so the retry
policy keys on kind WITHOUT re-parsing: kind=transient is the ONLY kind allowed
to feed the bounded transient retry ladder (wf.py maps it to error_class
`transport`, the ladder's gate class); a token-declared failure is deterministic
— terminal in both ladders (wf.py `declared_failure`).

Sentinels are matched per LINE, never across the capture: a false positive needs
the exact machine phrase on a line of its own, so a node that mentions
"429 lines" (no HTTP marker) or "HTTP-429 handling" (hyphen between marker and
digits) is never misclassified. The token grammar is pinned exact
(`{"node_outcome": "success"|"failure"}`, internal whitespace tolerated) and the
agent's FINAL (tail) token wins over any earlier one — the same contract the
spawn-prompt preamble teaches, so both sides speak one grammar.

No I/O, no side effects, stdlib only — unit-tested in isolation
(tests/test_outcome_classifier_imp1z.py); bound privately by wf.py
(`wf._outcome`) under the import-purity law (no bare top-level name).
"""

from __future__ import annotations

import re
from typing import Optional, TypedDict

# Transient provider-error sentinels. Matched against individual stdout lines
# (never the whole capture): the authoritative marker is the exhausted-retry
# line the agent CLI prints; the explicit `HTTP <code>` / overloaded / usage /
# connection-reset phrases cover the same family of provider faults.
TRANSIENT_SENTINELS = (
    re.compile(r"API call failed after \d+ retr(?:y|ies)", re.IGNORECASE),
    re.compile(r"HTTP\s*429", re.IGNORECASE),
    re.compile(r"HTTP\s*50[234]", re.IGNORECASE),
    re.compile(r"temporarily overloaded", re.IGNORECASE),
    re.compile(r"\boverloaded_error\b", re.IGNORECASE),
    re.compile(r"usage limit", re.IGNORECASE),
    re.compile(r"connection reset", re.IGNORECASE),
)

# The machine-readable self-report token — the agent's tail declaration, e.g.
# `{"node_outcome": "failure"}`. Tolerant of internal whitespace, pinned to the
# exact key/value so prose never trips it.
_NODE_OUTCOME_TOKEN = re.compile(
    r'\{\s*"node_outcome"\s*:\s*"(success|failure)"\s*\}'
)


class Verdict(TypedDict):
    outcome: str                 # "success" | "failure"
    kind: str                    # "success" | "transient" | "deterministic"
    detail: Optional[str]        # the matched sentinel line, when one tripped


def parse_node_outcome(text: Optional[str]) -> Optional[str]:
    """The agent's self-reported node_outcome token from its captured output,
    or None. When more than one token appears, the agent's FINAL (tail)
    declaration wins — it is the last word of the final turn."""
    if not text:
        return None
    matches = _NODE_OUTCOME_TOKEN.findall(text)
    if not matches:
        return None
    return matches[-1]


def _match_transient(text: Optional[str]) -> Optional[str]:
    """The first line carrying a transient sentinel (stripped), or None."""
    if not text:
        return None
    for line in text.splitlines():
        for pattern in TRANSIENT_SENTINELS:
            if pattern.search(line):
                return line.strip()
    return None


def classify(returncode: int, output: str, token: Optional[str] = None) -> Verdict:
    """Decide a node's outcome from its exit code, captured output, and
    self-report token. Precedence is FIXED (bead acceptance):

    1. A node_outcome token is authoritative in EITHER direction — a node that
       declares success despite a transient sentinel still succeeds, and one
       that declares failure on a clean exit 0 still fails (deterministic: it
       knows its own result).
    2. Otherwise a transient provider-error sentinel (line-scoped) fails the
       node even on exit 0, classified `transient` so ONLY the bounded
       transient retry ladder may re-drive it.
    3. Otherwise the exit code decides: 0 -> success, non-zero -> deterministic
       failure (real work failed; no transient retry).

    `detail` carries the matched sentinel line so a settle is never a bare exit
    code."""
    if token == "success":
        return {"outcome": "success", "kind": "success", "detail": None}
    if token == "failure":
        return {"outcome": "failure", "kind": "deterministic", "detail": None}

    matched = _match_transient(output)
    if matched is not None:
        return {"outcome": "failure", "kind": "transient", "detail": matched}

    if returncode == 0:
        return {"outcome": "success", "kind": "success", "detail": None}
    return {"outcome": "failure", "kind": "deterministic", "detail": None}
