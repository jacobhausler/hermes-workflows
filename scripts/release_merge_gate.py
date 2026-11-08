#!/usr/bin/env python3
"""release_merge_gate.py — the peer-receipt-before-merge predicate for the
ra-release lane (est-clrlx, hermes-workflows#545 class).

Incident: run 20261025-193537-ra-release prepare issued
`PUT /pulls/545/merge` on gates-green + mergeable ALONE, while the independent
deep peer lane was still in flight; the PR carried comments=[] reviews=[] at
merge time. The merge authority lived only as prose (repo-admin SKILL.md
review-marker law; the watcher's MARK grammar) and the promoted peer-gated
shelf template was gone. Prose is not a gate: the release lane's merge step
must not be issuable without a machine check. This script IS that check — the
lane calls it instead of hand-writing a merge PUT.

Predicate (the EXISTING review-marker law, ported to code verbatim — no new
law invented here):
  1. GET pulls/{n}: state == open AND head.sha == --head. A head that moved
     since the review is `head-moved`: the exact-head contract says the old
     seal does not carry (SKILL.md: "merge never carries to a new head").
  2. The LATEST `repo-admin reviewed=` marker across the PR's issue comments
     (ordered by updated_at) and reviews (submitted_at) — the one newest marker
     decides, an older seal never outranks a newer verdict (team-watch
     reviewed() ordering law; an old merge stamp superseded by a newer
     changes/decision stamp REFUSES) — must carry verdict=merge with
     reviewed= matching the CURRENT head (7-40 hex prefix of --head exactly).
  3. Non-author (PEER LAW): the marker's reviewer= must exist and differ from
     the PR's author bot stamp `repo-admin bot-id=` in the body (fallback
     --owner-bot; no author identity known = refuse, fail-closed). The shared
     GitHub login is NOT authorship — markers are the identity of record.
  4. Only when 1-3 hold: PUT /merge {merge_method: squash}, then PROVE the
     merge by ANCESTRY, never by the POST status, a merged_at timestamp, or
     sha-equality alone (est-xihc8, atbrace forgejo-lane shape): GET the PR,
     require merged == true, and run the compare containment discriminator
     `GET /repos/{repo}/compare/{base}...{head}` — a leg resolves CONTAINED
     only on status ∈ {behind, identical}:
       leg A  compare/{merge_commit_sha}...{armed head} — the head is an
              ancestor of the merge commit (true merge-commit / ff method);
       leg B  compare/{base ref}...{merge_commit_sha} — the merge commit is
              an ancestor of the base branch (squash/rebase rewrite the head,
              so leg A cannot hold for them; live-pinned 2026-11-08 on this
              repo's #613 and #545: both legs diverged for leg A, leg B
              reads status=behind for the squash commit on main).
     Contained on either leg => merged. Neither leg => NOT merged, refuse
     the close (`merge-not-proven-by-ancestry`) even when the PR object
     claims merged — a stamp is not ancestry. A POST refused with 404/405
     (e.g. an already-merged race) is NOT a death: the containment read-back
     decides (fixture class: 405-merged-stamped). The returned sha must
     equal the PR's merge_commit_sha as an integrity stamp, never as the
     discriminator.
  5. RE-GATE, never bail: if the read-back shows the head moved off the
     armed head between the predicate and the POST (re-push mid-flight),
     the old seal does not carry (law 1) — refuse typed `head-repushed-regate`
     with the new head, so the babysit loop re-arms the gate at that head
     once a fresh peer marker sits on it. This is never `merge-write-failed`
     and never a silent success.

Exit codes: 0 = merged AND ancestry-proven (receipt written when --receipt
given); 1 = refused (typed reason — a pre-merge refuse attempts ZERO writes; a
post-merge close-out refuse means the merge, if it happened, rode no proof and
is never accepted); 2 = transport/read failure (predicate or ancestry
unverifiable — fail-closed, zero merge acceptance).
The token is read from GITHUB_TOKEN (or --token-file) and NEVER printed.
Stdlib only; one network seam (`_transport`) so behavior tests fake GitHub.
Usage:
  GITHUB_TOKEN=... python3 scripts/release_merge_gate.py \
      --repo owner/name --pr N --head <40-hex> [--owner-bot b] [--receipt PATH]
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
# MARK/BOTID grammars: the watcher's own (scripts/team-watch.py), ported verbatim.
MARK = re.compile(r"<!--\s*repo-admin\s+reviewed=([0-9a-f]{7,40})"
                  r"(?:\s+verdict=(\w+))?(?:\s+profile=\S+)?"
                  r"(?:\s+reviewer=([\w.-]+))?")
BOTID = re.compile(r"<!--\s*repo-admin\s+bot-id=([\w.-]+)\s*-->")


def _transport(method, url, body, token):
    """The ONE network seam: tests replace it with a fake.
    Returns (status:int, parsed_json_or_{})."""
    req = urllib.request.Request(
        url, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "hermes-workflows-release-merge-gate"})
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


def _ok(st):
    return 200 <= st < 300


def latest_marker(repo, pr, token, transport):
    """(ts, reviewed_sha_prefix, verdict, reviewer) of the NEWEST repo-admin
    marker across issue comments (ordered by updated_at — law 3 PATCHes one
    live marker) and reviews (submitted_at — reviews are immutable). A failed
    read raises: an unverifiable marker census is never 'no marker'."""
    best = ("", "", None, None)
    for path, ts_key in ((f"{API}/repos/{repo}/issues/{pr}/comments?per_page=100",
                          "updated_at"),
                         (f"{API}/repos/{repo}/pulls/{pr}/reviews?per_page=100",
                          "submitted_at")):
        st, rows = transport("GET", path, None, token)
        if not _ok(st) or not isinstance(rows, list):
            raise RuntimeError(f"marker-read-failed {path} status={st}")
        for c in rows:
            m = MARK.search(str((c or {}).get("body") or ""))
            if m:
                ts = str(c.get(ts_key) or c.get("created_at") or "")
                if ts >= best[0]:
                    best = (ts, m.group(1), m.group(2), m.group(3))
    return best


def refuse(reason, **extra):
    out = {"merged": False, "reason": reason}
    out.update({k: v for k, v in extra.items() if v not in ("", None)})
    return out


def contained(repo, base, head_sha, token, transport):
    """One compare leg: True when the armed pair proves CONTAINMENT —
    GET /repos/{repo}/compare/{base}...{head_sha} answers status ∈
    {behind, identical} (head_sha is an ancestor of base, or the same commit).
    A 404 is a dead leg (unknown ref => not contained, another leg may still
    hold). Any other non-2xx or a body without a status RAISES: an
    unverifiable ancestry is never silently 'not merged' — the caller rides
    exit 2, fail-closed, exactly like the marker census."""
    st, cmp_ = transport("GET", f"{API}/repos/{repo}/compare/"
                                f"{base}...{head_sha}", None, token)
    if st == 404:
        return False
    if not _ok(st) or not isinstance(cmp_, dict) or "status" not in cmp_:
        raise RuntimeError(f"compare-read-failed {base}...{head_sha} "
                           f"status={st}")
    return str(cmp_.get("status")) in ("behind", "identical")


def gate(repo, pr, head, owner_bot="", token=None, transport=_transport):
    """The predicate + (only on pass) the squash-merge + read-back. Returns a
    verdict dict; `merged=True` only ever alongside a verified read-back."""
    token = token or os.environ.get("GITHUB_TOKEN") or ""
    st, pull = transport("GET", f"{API}/repos/{repo}/pulls/{pr}", None, token)
    if not _ok(st):
        return refuse("pr-read-failed", status=st)
    if str((pull or {}).get("state")) != "open":
        return refuse("pr-not-open", state=pull.get("state"))
    actual = str(((pull or {}).get("head") or {}).get("sha") or "")
    if actual != head:
        return refuse("head-moved", head_expected=head, head_seen=actual)
    ts, m_sha, verdict, reviewer = latest_marker(repo, pr, token, transport)
    if not m_sha:
        return refuse("no-peer-marker")
    if verdict != "merge":
        return refuse(f"verdict-{verdict or 'missing'}", reviewed=m_sha)
    if not head.startswith(m_sha):
        # A push after the stamp invalidates it: the seal must sit at THIS head.
        return refuse("marker-stale-head", reviewed=m_sha, head_expected=head)
    author_m = BOTID.search(str((pull or {}).get("body") or ""))
    author_id = author_m.group(1) if author_m else (owner_bot or "")
    if not author_id:
        return refuse("author-unknown", reviewed=m_sha)
    if not reviewer:
        return refuse("marker-no-reviewer", reviewed=m_sha)
    if reviewer.lower() == author_id.lower():
        return refuse("self-review", reviewer=reviewer, author=author_id)
    # Predicate holds — issue the merge, then PROVE it by ANCESTRY (law 4).
    st_m, res = transport("PUT", f"{API}/repos/{repo}/pulls/{pr}/merge",
                          {"merge_method": "squash"}, token)
    post_sha = str((res or {}).get("sha") or "")
    st_b, back = transport("GET", f"{API}/repos/{repo}/pulls/{pr}", None, token)
    if not _ok(st_b):
        return refuse("read-back-unverified", sha=post_sha, status=st_b)
    rb_head = str(((back or {}).get("head") or {}).get("sha") or "")
    if rb_head and rb_head != head:
        # Re-push between gate and POST (law 5): RE-GATE, never bail — the
        # old seal does not carry; the babysit loop re-arms at the new head
        # once a fresh peer marker sits on it. Never merge-write-failed,
        # never a silent accept.
        return refuse("head-repushed-regate", head_seen=rb_head,
                      post_status=st_m)
    sha = str((back or {}).get("merge_commit_sha") or "") or post_sha
    if not (back or {}).get("merged") or not sha:
        # A POST refused 404/405 (already-merged race is the benign class)
        # is final ONLY when the read-back also shows no merge (fixture:
        # 405-merged-stamped proves merged CONTAINED, not POST status).
        if _ok(st_m):
            return refuse("read-back-unverified", sha=sha, status=st_b)
        return refuse("merge-write-failed", status=st_m, sha=sha)
    base = str(((back or {}).get("base") or {}).get("ref")
               or ((pull or {}).get("base") or {}).get("ref") or "")
    if not base:
        raise RuntimeError("compare-leg-base-unknown: no base ref to grade")
    # leg A: head contained in the merge commit (merge-commit/ff methods);
    # leg B: merge commit contained in the base branch (squash/rebase truth).
    in_merge = contained(repo, sha, head, token, transport)
    on_base = in_merge or contained(repo, base, sha, token, transport)
    if not (in_merge or on_base):
        return refuse("merge-not-proven-by-ancestry", sha=sha,
                      post_status=st_m)
    return {"merged": True, "sha": sha, "head": head,
            "proof": {"leg": ("head-in-merge-commit" if in_merge
                              else "merge-commit-on-base"),
                      "post_status": st_m,
                      "sha_equals_post": bool(post_sha) and post_sha == sha},
            "marker": {"ts": ts, "reviewed": m_sha, "verdict": verdict,
                       "reviewer": reviewer},
            "author_bot": author_id}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Peer-receipt-before-merge gate (est-clrlx)")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", required=True, type=int)
    ap.add_argument("--head", required=True,
                    help="the exact reviewed head (40-hex) the seal must sit at")
    ap.add_argument("--owner-bot", default="",
                    help="author fallback when the body carries no bot-id stamp")
    ap.add_argument("--token-file", default=None,
                    help="file holding the GitHub token (else GITHUB_TOKEN env)")
    ap.add_argument("--receipt", default=None,
                    help="write the verified merge receipt JSON here")
    a = ap.parse_args(argv)
    token = ""
    if a.token_file:
        with open(a.token_file, encoding="utf-8") as f:
            token = f.read().strip()
    try:
        out = gate(a.repo, a.pr, a.head, owner_bot=a.owner_bot, token=token)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2, default=str)[:4000])
    if out.get("merged"):
        if a.receipt:
            with open(a.receipt, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, default=str)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
