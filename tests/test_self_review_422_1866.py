#!/usr/bin/env python3
"""est-2ek.1.866 — the formal-review step is AUTHOR-AWARE (RED on base, GREEN on branch).

Field evidence: hermes-workflows#245 reconcile tried the formal REQUEST_CHANGES
review as the shared credential (jacobhausler) WHO IS ALSO the PR author — the
POST answered HTTP 422 with the verbatim errors text "Can not request changes
on your own pull request" (receipt: .../work/reconcile/review-refused.json,
PR at e08513f8a5ed2fd325f0d5c5afc9d18bf9d1bebf). The verified fallback that DID
land the verdict on #245: issue comment 6019510641 + the `changes-requested`
label PATCH, both read back — and no merge happened.

Pinned law (scripts/pr_formal_review.py):
  T1  self-review detected BEFORE posting (credential login == PR author):
      the doomed POST /reviews is NEVER attempted; the fallback runs (issue
      comment ending in the marker + a formal-review-fallback record, label
      PATCH) and is verified ONLY by read-backs.
  T2  clean preflight (different identities) -> the formal review POSTs and no
      fallback artifacts are written.
  T3  the 422 shape itself mocked (defense in depth): preflight clean but the
      POST still returns 422 -> the same fallback is taken, reason recorded.
  T4  a fallback whose read-back does NOT prove the write claims verified=False
      (loud, never silent).
  T5  the verdict always RECORDS which path was used (posted + fallback_used)
      and the compared identities — and no identity is ever forged: every call
      rides the ONE token passed in.
Stdlib only; the network never runs — the transport seam is a recording mock.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pr_formal_review.py"

spec = importlib.util.spec_from_file_location("_self_review_1866", SCRIPT)
fails = 0
total = 0


def check(label, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL " if not cond else "PASS ") + label +
          (f"  {str(detail)[:400]}" if detail and not cond else ""))
    if not cond:
        fails += 1


if spec is None:
    check("scripts/pr_formal_review.py exists", False, str(SCRIPT))
    print("DONE self_review_422_1866 FAIL")
    sys.exit(1)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as exc:
    check("module loads", False, f"{type(exc).__name__}: {exc}")
    print("DONE self_review_422_1866 FAIL")
    sys.exit(1)

REPO = "octocat/whatever"
PR = 245
MARKER = "repo-admin formal-review-fallback"

# the #245 field receipt, verbatim shape
HTTP_422_SELF_REVIEW = (422, {"message": "Unprocessable Entity",
                              "errors": ["Review Can not request changes on your own pull request"],
                              "documentation_url": "https://docs.github.com/rest/pulls/reviews",
                              "status": "422"})


class Mock:
    """Recording transport: answers by (method, url-suffix); records every call."""
    def __init__(self, answers, me="jacobhausler", author="jacobhausler"):
        self.calls = []
        self.answers = answers
        self.me, self.author = me, author

    def __call__(self, method, url, body, token):
        self.calls.append((method, url, body, token))
        for (m, suffix), val in self.answers.items():
            if method == m and url.endswith(suffix):
                return val if isinstance(val, tuple) else (200, val)
        raise AssertionError(f"unexpected call {method} {url}")

    def posted_reviews(self):
        return [c for c in self.calls if c[0] == "POST" and c[1].endswith("/reviews")]

    def tokens(self):
        return {c[3] for c in self.calls}


def answers(me="jacobhausler", author="jacobhausler", labels=("changes-requested",),
            review=None):
    """One builder for the shared keys: the PR GET carries BOTH the author (for
    preflight) and the post-fallback label state (for the read-back)."""
    a = {("GET", "/user"): {"login": me},
         ("GET", f"/repos/{REPO}/pulls/{PR}"): {
             "user": {"login": author},
             "labels": [{"name": l} for l in labels]},
         ("POST", f"/repos/{REPO}/issues/{PR}/comments"): {"id": 6019510641},
         ("PATCH", f"/repos/{REPO}/issues/{PR}"): {},
         ("GET", f"/repos/{REPO}/issues/{PR}/comments"): [{"id": 6019510641}]}
    if review is not None:
        a[("POST", f"/repos/{REPO}/pulls/{PR}/reviews")] = review
    return a


# ---- T1: self-review preflight -> doomed POST NEVER attempted, fallback verified
m = Mock(answers())
out = mod.post_formal_review(REPO, PR, "FINDINGS: request changes.", token="t0ken", transport=m)
check("T1 self-review detected BEFORE posting (credential == author recorded)",
      out.get("self_review", {}).get("self_review") is True
      and out["self_review"].get("credential") == "jacobhausler"
      and out["self_review"].get("author") == "jacobhausler", out.get("self_review"))
check("T1 the doomed POST /reviews is NEVER attempted", m.posted_reviews() == [],
      m.posted_reviews())
check("T1 fallback: issue comment carries the marker + recorded reason",
      any(c[0] == "POST" and c[1].endswith(f"/issues/{PR}/comments")
          and MARKER in c[2]["body"] and "self-review" in c[2]["body"] for c in m.calls),
      [c[2] for c in m.calls if c[0] == "POST"])
check("T1 fallback: changes-requested label PATCHed",
      any(c[0] == "PATCH" and c[1].endswith(f"/issues/{PR}")
          and "changes-requested" in c[2]["labels"] for c in m.calls))
check("T1 fallback verified by READ-BACK (comment id + label both proven)",
      out.get("posted") == "fallback" and out.get("verified") is True
      and out.get("fallback_used") == "self-review-preflight", out)

# ---- T2: clean preflight -> formal review posts, zero fallback artifacts
m2 = Mock(answers(author="contributor-x", review={"id": 42}))
out2 = mod.post_formal_review(REPO, PR, "FINDINGS.", token="t0ken", transport=m2)
check("T2 different identities: the formal REQUEST_CHANGES review POSTs",
      out2.get("posted") == "review" and out2.get("verified") is True
      and len(m2.posted_reviews()) == 1
      and m2.posted_reviews()[0][2].get("event") == "REQUEST_CHANGES", out2)
check("T2 no fallback writes when the review landed",
      not any(c[0] in ("POST", "PATCH") and "/issues/" in c[1] for c in m2.calls),
      [(c[0], c[1]) for c in m2.calls])

# ---- T3: the 422 field shape mocked — preflight clean, POST refuses -> fallback
m3 = Mock(answers(author="contributor-x", review=HTTP_422_SELF_REVIEW))
out3 = mod.post_formal_review(REPO, PR, "FINDINGS.", token="t0ken", transport=m3)
check("T3 mocked 422 (GitHub refuses the review): fallback taken and verified",
      out3.get("posted") == "fallback" and out3.get("verified") is True
      and out3.get("fallback_used") == "post-422-self-review", out3)

# ---- T4: incomplete fallback -> verified=False, loud (read-back rules)
BAD = answers()
BAD[("GET", f"/repos/{REPO}/issues/{PR}/comments")] = []      # comment NOT read back
m4 = Mock(BAD)
out4 = mod.post_formal_review(REPO, PR, "FINDINGS.", token="t0ken", transport=m4)
check("T4 fallback write not proven by read-back -> verified False (never silent)",
      out4.get("posted") == "fallback" and out4.get("verified") is False, out4)

# ---- T5: one credential, never forged
for mm in (m, m2, m3):
    pass
check("T5 every API call rides the ONE passed token (no forged identity)",
      all(c[3] == "t0ken" for c in m.calls + m2.calls + m3.calls))

print("DONE self_review_422_1866", "OK" if fails == 0 else "FAIL")
sys.exit(0 if fails == 0 else 1)
