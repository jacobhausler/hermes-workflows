#!/usr/bin/env python3
"""pr_formal_review.py — the AUTHOR-AWARE formal-review step (est-2ek.1.866).

The ra-pr-deep reconcile lane must post a formal REQUEST_CHANGES review, but the
shared GitHub credential (jacobhausler) IS the PR author for our own repo PRs:
`POST /repos/{repo}/pulls/{n}/reviews` with event=REQUEST_CHANGES then returns
HTTP 422 ("Can not request changes on your own pull request" — exact receipt:
/home/hermes/.hermes/workflows/20261008-135336-ra-hermes-workflows-245-/work/
reconcile/review-refused.json, #245 @ e08513f8). The lane wasted the doomed POST
and, worse, a bare traceback could read as "review not done" rather than
"self-review refused".

The verified fallback (proven live on hermes-workflows#245: issue comment
6019510641 + the `changes-requested` label PATCH, both read back):
  1. detect self-review BEFORE posting — compare the credential login
     (GET /user) with the PR author (GET pulls/{n}); never forge another identity;
  2. skip the doomed POST when they match;
  3. post the evidence as an issue comment ending in the repo-admin marker plus
     a `formal-review-fallback=<reason>` line (the fallback used is RECORDED,
     never silent);
  4. add the `changes-requested` label (PATCH on the issue, the GitHub-sanctioned
     labels endpoint) and READ BOTH artifacts back (GET comment list + label
     list) — no read-back, no claim.
  5. if the preflight says clean (different identities) but the POST still
     comes back 422, take the same fallback (defense in depth).

Exit codes: 0 = review posted OR fallback fully verified; 1 = fallback
incomplete (missing read-back — loud, never silent); 2 = preflight/transport
failure. Usage:
  python3 scripts/pr_formal_review.py --repo owner/name --pr N \
      --body-file finding.md [--event REQUEST_CHANGES] [--token-env GITHUB_TOKEN]
Stdlib only; the transport is one seam (`_transport`) so tests mock the 422
without the network. The token is read from the env and NEVER printed.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def _transport(method, url, body, token):
    """The ONE network seam: tests replace this with a recording mock.
    Returns (status:int, parsed_json_or_{})."""
    req = urllib.request.Request(
        url, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "hermes-repo-admin-formal-review"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read())
        except Exception:
            payload = {}
        return e.code, payload


def self_review_state(repo, pr, token, transport=_transport):
    """Compare credential login vs PR author BEFORE posting (law: detect,
    skip, fallback — never attempt-and-hope, never forge an identity)."""
    st_me, me = transport("GET", API + "/user", None, token)
    st_pr, issue = transport("GET", f"{API}/repos/{repo}/pulls/{pr}", None, token)
    login = str((me or {}).get("login") or "") if 200 <= st_me < 300 else ""
    author = str(((issue or {}).get("user") or {}).get("login") or "") if 200 <= st_pr < 300 else ""
    return {"credential": login, "author": author,
            "self_review": bool(login and author and login.lower() == author.lower())}


def _fallback(repo, pr, body, token, transport, reason, receipts):
    """The #245-proven fallback: issue comment + changes-requested label PATCH,
    each READ BACK. The fallback reason is recorded IN the body marker."""
    marked = (body.rstrip()
              + f"\n\n<!-- repo-admin formal-review-fallback={reason} -->\n")
    st_c, comment = transport("POST", f"{API}/repos/{repo}/issues/{pr}/comments",
                              {"body": marked}, token)
    cid = (comment or {}).get("id") if 200 <= st_c < 300 else None
    st_l, _ = transport("PATCH", f"{API}/repos/{repo}/issues/{pr}",
                        {"labels": ["changes-requested"]}, token)
    # read-backs: the write is only CLAIMED once the GET proves it landed
    st_rb, comments = transport("GET", f"{API}/repos/{repo}/issues/{pr}/comments",
                                None, token)
    ids = [(c or {}).get("id") for c in (comments or [])] if isinstance(comments, list) else []
    st_lb, pr_rb = transport("GET", f"{API}/repos/{repo}/pulls/{pr}", None, token)
    labels = [str((l or {}).get("name")) for l in ((pr_rb or {}).get("labels") or [])]
    verified = cid is not None and cid in ids and "changes-requested" in labels
    receipts["fallback"] = {"reason": reason, "comment_id": cid,
                            "comment_post_status": st_c, "label_status": st_l,
                            "comment_readback_ids": ids, "labels_readback": labels,
                            "verified": verified}
    return {"posted": "fallback", "fallback_used": reason, "verified": verified,
            "self_review": receipts.get("self_review"), "receipts": receipts}


def post_formal_review(repo, pr, body, event="REQUEST_CHANGES", token=None,
                       transport=_transport):
    """Author-aware formal review. Returns a verdict dict; the caller exits
    non-zero when `verified` is False (loud, never silent)."""
    token = token or os.environ.get("GITHUB_TOKEN") or ""
    receipts = {"steps": []}
    ss = self_review_state(repo, pr, token, transport)
    receipts["self_review"] = ss
    if ss["self_review"]:
        # The doomed POST is NEVER attempted (the 422 is known a priori; the
        # field receipt review-refused.json is exactly this POST).
        return _fallback(repo, pr, body, token, transport, "self-review-preflight", receipts)
    st, rev = transport("POST", f"{API}/repos/{repo}/pulls/{pr}/reviews",
                        {"body": body, "event": event}, token)
    if st == 422:
        return _fallback(repo, pr, body, token, transport, "post-422-self-review", receipts)
    if 200 <= st < 300:
        return {"posted": "review", "fallback_used": None, "verified": True,
                "review_id": (rev or {}).get("id"), "self_review": ss,
                "receipts": receipts}
    receipts["review_attempt"] = {"status": st, "body": rev}
    return {"posted": "failed", "fallback_used": None, "verified": False,
            "self_review": ss, "receipts": receipts}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", required=True, type=int)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--event", default="REQUEST_CHANGES")
    a = ap.parse_args(argv)
    body = open(a.body_file, encoding="utf-8").read()
    out = post_formal_review(a.repo, a.pr, body, event=a.event)
    print(json.dumps(out, indent=2, default=str)[:6000])
    if out["verified"]:
        return 0
    return 1 if out["posted"] == "fallback" else 2


if __name__ == "__main__":
    sys.exit(main())
