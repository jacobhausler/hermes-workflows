#!/usr/bin/env python3
"""est-clrlx — the ra-release merge step is GATED on a peer receipt at the
exact head (RED-class pin: without scripts/release_merge_gate.py a release
lane can merge on green CI alone, which is exactly what shipped #545).

Field evidence (read from run dirs + state.db session transcripts, 2026-10-25):
hermes-workflows#545 was merged 20:02:01Z by the prepare node of
20261025-193537-ra-release via an inline `gh.call("PUT", .../merge)` whose
preconditions were state/head/mergeable + green shards ONLY. The independent
deep peer lane 20261025-194341-ra-pr was still running; the PR carried
comments=[] reviews=[] (fresh GET). The zap verdict arrived 20:36:55Z — after
the merge — explicitly retrospective.

Pinned law (scripts/release_merge_gate.py), against a STATEFUL fake GitHub
whose compare oracle answers the SAME vocabulary the live API returned for this
repo's squash merges (measured 2026-11-08 on #613/#545: head NOT an ancestor
of the squash commit; the squash commit an ancestor of main):
  T1  POSITIVE: open PR at head H, author stamp bot-id=peer-bot, newest
      marker `reviewed=H verdict=merge reviewer=zap` -> the squash PUT issues
      ONCE, ANCESTRY proves the close (leg B: merge commit contained in the
      base branch), the verdict dict carries sha+marker+proof provenance.
  T2  NEGATIVE (the #545 shape): NO marker anywhere -> refuse no-peer-marker,
      ZERO writes attempted.
  T3  push-after-stamp: marker at the old head, PR now at H -> refuse
      marker-stale-head ("merge never carries to a new head").
  T4  PEER LAW: reviewer == author bot-id -> refuse self-review; no author
      stamp and no --owner-bot -> refuse author-unknown (fail-closed).
  T5  verdict=pending (deep lane mid-flight) -> refuse verdict-pending.
  T6  HEAD contract: PR head moved off --head -> refuse head-moved BEFORE any
      marker census (a fresh review must answer the CURRENT head).
  T7  newest marker rules: an old verdict=merge superseded by a newer
      verdict=changes -> refuse verdict-changes (never the stale seal).
  T8  merge write answered OK but the read-back disproves it -> merged False,
      reason read-back-unverified (loud, never silent).
  T9  every call rides the ONE token; the verdict dict prints no credential.
  T10 PEER FIXTURE "405-merged-stamped" (atbrace): the POST is refused 404/405
      on an already-merged PR; the containment read-back still proves the
      merge -> merged=True, post_status rides the receipt, never the verdict.
  T11 PEER FIXTURE "head-not-in-main" (atbrace): merged stamp present but the
      armed head is absent from the merge commit AND the merge commit is not
      on the base branch -> refuse merge-not-proven-by-ancestry. Ancestry,
      not a merged_at timestamp, not sha-equality alone.
  T12 re-push between gate and POST -> typed head-repushed-regate carrying the
      new head: RE-GATE, never bail (the old seal never carries).
  T13 merge-commit method (the forgejo-lane shape verbatim): head contained
      in the merge commit -> leg A alone proves merged; leg B never called.
Stdlib only; the network never runs — the transport seam is the fake.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_merge_gate.py"

spec = importlib.util.spec_from_file_location("_release_merge_gate_clrlx", SCRIPT)
fails = 0


def check(label, cond, detail: object = ""):
    global fails
    print(("PASS " if cond else "FAIL ") + label +
          (f"  {str(detail)[:400]}" if detail and not cond else ""))
    if not cond:
        fails += 1


if spec is None:
    check("scripts/release_merge_gate.py exists", False, str(SCRIPT))
    print("DONE release_merge_gate_clrlx FAIL")
    sys.exit(1)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as exc:
    check("module loads", False, f"{type(exc).__name__}: {exc}")
    print("DONE release_merge_gate_clrlx FAIL")
    sys.exit(1)

REPO = "octocat/whatever"
PR = 545
HEAD = "b67fa56a42d081fd5522a0f07a8b8d009f2f3993"      # the reviewed head
OLD = "6336b1a5a6bbb547281975e7bd148604b95fbe53"        # pre-push head
MERGE_SHA = "bca545b6a5f288939456edbe3c2b6122f59b8930"
AUTHOR_BODY = "release: v1.4.1\n\n<!-- repo-admin bot-id=peer-bot -->"


def marker(sha, verdict, reviewer, ts, profile="bot"):
    return (f"findings...\n<!-- repo-admin reviewed={sha} verdict={verdict} "
            f"profile={profile} reviewer={reviewer} -->")


class FakeGitHub:
    """Stateful transport: the PR, its comments and reviews, the merge
    shelf, and the compare oracle (status per pair — the same vocabulary the
    real API answers: behind/ahead/diverged/identical). `merge_lies=True`
    accepts the PUT but the read-back stays unmerged (models a lost write);
    `post_status` stamps the merge response (404/405 = the already-merged
    race class); `repush_to` lands a new head AT the merge instant, modeling
    the push between gate and POST. Writes are recorded — the gate must never
    write on a refusal, and a regate/ancestry refuse never accepts."""

    def __init__(self, head=HEAD, state="open", body=AUTHOR_BODY,
                 comments=(), reviews=(), merged=False, merge_lies=False,
                 post_status=200, repush_to=None, base="main",
                 compare=None):
        self.calls = []
        self.pr = {"state": state, "head": {"sha": head}, "body": body,
                   "user": {"login": "octocat"},
                   "base": {"ref": base},
                   "merged": merged,
                   "merge_commit_sha": MERGE_SHA if merged else ""}
        self.comments = list(comments)    # [{body, updated_at|created_at}]
        self.reviews = list(reviews)      # [{body, submitted_at}]
        self.merge_lies = merge_lies
        self.post_status = post_status
        self.repush_to = repush_to
        # pair "base...head" -> status; unknown pairs answer 404 (dead leg).
        self.compare = dict(compare or {})

    def __call__(self, method, url, body, token):
        self.calls.append((method, url, body, token))
        p = url.replace(mod.API, "")
        base = f"/repos/{REPO}"
        if method == "GET" and p == f"{base}/pulls/{PR}":
            return 200, dict(self.pr)
        if method == "GET" and p.startswith(f"{base}/issues/{PR}/comments"):
            return 200, list(self.comments)
        if method == "GET" and p.startswith(f"{base}/pulls/{PR}/reviews"):
            return 200, list(self.reviews)
        if method == "GET" and p.startswith(f"{base}/compare/"):
            pair = p[len(f"{base}/compare/"):]
            st = self.compare.get(pair)
            if st is None:
                return 404, {"message": "no exact match"}
            return 200, {"status": st, "ahead_by": 0, "behind_by": 1,
                         "total_commits": 1}
        if method == "PUT" and p == f"{base}/pulls/{PR}/merge":
            if self.repush_to:
                self.pr["head"]["sha"] = self.repush_to
            if not self.merge_lies and 200 <= self.post_status < 300:
                self.pr["merged"] = True
                self.pr["merge_commit_sha"] = MERGE_SHA
            if not 200 <= self.post_status < 300:
                return self.post_status, {"message":
                                         "Pull Request is not mergeable"}
            return 200, {"sha": MERGE_SHA, "merged": True,
                         "message": "Pull Request successfully merged"}
        raise AssertionError(f"unexpected call {method} {url}")

    def writes(self):
        return [c for c in self.calls if c[0] in ("PUT", "POST", "PATCH", "DELETE")]

    def merges(self):
        return [c for c in self.calls if c[0] == "PUT" and c[1].endswith("/merge")]


# The live-pinned compare truths (est-xihc8, measured 2026-11-08 on this
# repo's squash merges #613/#545): the armed head is NEVER an ancestor of a
# squash commit (leg pair MERGE_SHA...HEAD -> diverged), while the squash
# commit IS an ancestor of main (pair main...MERGE_SHA -> behind). The
# default fake models a squash merge; the merge-commit method flips leg A to
# behind (fixture T13).
SQUASH_COMPARE = {f"{MERGE_SHA}...{HEAD}": "diverged",
                  f"main...{MERGE_SHA}": "behind"}

SEAL = ({"body": marker(HEAD, "merge", "zap", "2026-10-25T19:59:00Z")},)

# ---- T1 POSITIVE: receipt at the exact head by a non-author -> merge issues
g = FakeGitHub(comments=SEAL, compare=SQUASH_COMPARE)
out = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g)
check("T1 peer receipt at exact head: merged=True with verified sha+marker",
      out.get("merged") is True and out.get("sha") == MERGE_SHA
      and out.get("marker", {}).get("reviewer") == "zap"
      and out.get("author_bot") == "peer-bot", out)
check("T1 the squash PUT issued exactly once, method=squash",
      len(g.merges()) == 1 and g.merges()[0][2] == {"merge_method": "squash"},
      g.merges())
_mi = next(i for i, c in enumerate(g.calls) if c in g.merges())
check("T1 merge is PROVEN by ancestry (PR GET after the PUT, then the "
      "leg-B compare proving the squash commit on main; no leg-A-only accept)",
      any(c[0] == "GET" and c[1].endswith(f"/pulls/{PR}")
          for c in g.calls[_mi + 1:])
      and g.pr["merged"] is True and out.get("sha") == g.pr["merge_commit_sha"]
      and out.get("proof", {}).get("leg") == "merge-commit-on-base"
      and out.get("proof", {}).get("sha_equals_post") is True,
      (out.get("proof"), g.calls[-2:]))

# ---- T2 NEGATIVE (the #545 shape): no marker at all -> refuse, zero writes
g2 = FakeGitHub()
out2 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g2)
check("T2 no receipt -> refuse no-peer-marker, ZERO writes attempted",
      out2.get("merged") is False and out2.get("reason") == "no-peer-marker"
      and g2.writes() == [], (out2, g2.writes()))

# ---- T3 push-after-stamp: seal sits at the OLD head -> refuse
g3 = FakeGitHub(comments=({"body": marker(OLD, "merge", "zap",
                                          "2026-10-25T19:40:00Z")},))
out3 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g3)
check("T3 seal at a superseded head -> refuse marker-stale-head (never carries)",
      out3.get("merged") is False and out3.get("reason") == "marker-stale-head"
      and g3.writes() == [], (out3, g3.writes()))

# ---- T4 PEER LAW: reviewer == author stamp; and fail-closed when unknown
g4 = FakeGitHub(comments=({"body": marker(HEAD, "merge", "peer-bot",
                                          "2026-10-25T19:59:00Z")},))
out4 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g4)
check("T4 reviewer == author bot-id -> refuse self-review",
      out4.get("merged") is False and out4.get("reason") == "self-review"
      and g4.writes() == [], (out4, g4.writes()))
g4b = FakeGitHub(body="release with no bot-id stamp",
                 comments=SEAL)
out4b = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g4b)
out4c = mod.gate(REPO, PR, HEAD, owner_bot="peer-bot", token="t0ken",
                 transport=FakeGitHub(body="release with no bot-id stamp",
                                      comments=SEAL, compare=SQUASH_COMPARE))
check("T4 no author stamp -> refuse author-unknown (fail-closed); "
      "--owner-bot fallback resolves the same verdict",
      out4b.get("reason") == "author-unknown"
      and out4c.get("merged") is True and out4c.get("author_bot") == "peer-bot",
      (out4b, out4c))

# ---- T5 mid-flight verdict does not authorize: pending -> refuse
g5 = FakeGitHub(comments=({"body": marker(HEAD, "pending", "zap",
                                          "2026-10-25T19:59:00Z")},))
out5 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g5)
check("T5 verdict=pending (deep lane mid-flight) -> refuse verdict-pending",
      out5.get("merged") is False and out5.get("reason") == "verdict-pending"
      and g5.writes() == [], (out5, g5.writes()))

# ---- T6 the PR head itself moved off the reviewed head -> refuse at step 1
g6 = FakeGitHub(head=OLD, comments=SEAL)
out6 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g6)
check("T6 PR head moved -> refuse head-moved before any marker census",
      out6.get("merged") is False and out6.get("reason") == "head-moved"
      and g6.writes() == []
      and not any("comments" in c[1] for c in g6.calls), (out6, g6.calls))

# ---- T7 the NEWEST marker rules: old merge seal superseded by changes
g7 = FakeGitHub(comments=({"body": marker(HEAD, "merge", "zap",
                                          "2026-10-25T19:40:00Z"),
                           "updated_at": "2026-10-25T19:40:00Z"},
                          {"body": marker(HEAD, "changes", "zap",
                                          "2026-10-25T20:00:00Z"),
                           "updated_at": "2026-10-25T20:00:00Z"}))
out7 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g7)
check("T7 newer verdict=changes supersedes an older merge seal -> refuse",
      out7.get("merged") is False and out7.get("reason") == "verdict-changes"
      and g7.writes() == [], (out7, g7.writes()))

# ---- T8 write accepted but disproved by read-back -> merged=False, loud
g8 = FakeGitHub(comments=SEAL, merge_lies=True)
out8 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g8)
check("T8 merge write not proven by read-back -> merged=False "
      "read-back-unverified (never silent success)",
      out8.get("merged") is False and out8.get("reason") == "read-back-unverified",
      out8)

# ---- T10 PEER FIXTURE "405-merged-stamped" (atbrace est-xihc8): the merge
# POST is refused 405 (an already-merged race), but the containment read-back
# proves the armed head landed — the ANCESTRY decides, never the POST status.
g10 = FakeGitHub(comments=SEAL, merged=True, post_status=405,
                 compare=SQUASH_COMPARE)
out10 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g10)
check("T10 POST stamped 405 on an already-merged PR -> merged=True "
      "via leg-B containment (post_status rides the receipt, not the verdict)",
      out10.get("merged") is True
      and out10.get("proof", {}).get("leg") == "merge-commit-on-base"
      and out10.get("proof", {}).get("post_status") == 405
      and g10.merges(), (out10, g10.merges()))

# ---- T11 PEER FIXTURE "head-not-in-main" (atbrace est-xihc8): the PR object
# claims merged, but the armed head is absent from the merge commit AND the
# merge commit is not an ancestor of the base branch (diverged on both legs
# — stamped lie / landed elsewhere). The close-out is REFUSED.
g11 = FakeGitHub(comments=SEAL,
                 compare={f"{MERGE_SHA}...{HEAD}": "diverged",
                          f"main...{MERGE_SHA}": "ahead"})
out11 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g11)
check("T11 head not contained, merge commit not on main -> refuse "
      "merge-not-proven-by-ancestry despite merged stamp (never a timestamp, "
      "never sha-equality alone)",
      out11.get("merged") is False
      and out11.get("reason") == "merge-not-proven-by-ancestry"
      and out11.get("sha") == MERGE_SHA, out11)

# ---- T12 re-push between gate and POST: RE-GATE, never bail.
g12 = FakeGitHub(comments=SEAL, compare=SQUASH_COMPARE,
                 repush_to="feedface0000000000000000000000badd0000000")
out12 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g12)
check("T12 head re-pushed between gate and POST -> typed head-repushed-regate "
      "carrying the new head (old seal never carries; babysit re-arms, no bail)",
      out12.get("merged") is False
      and out12.get("reason") == "head-repushed-regate"
      and out12.get("head_seen")
      == "feedface0000000000000000000000badd0000000", out12)

# ---- T13 merge-commit method (the atbrace forgejo-lane shape verbatim): the
# armed head IS an ancestor of the merge commit — leg A alone proves merged.
g13 = FakeGitHub(comments=SEAL,
                 compare={f"{MERGE_SHA}...{HEAD}": "behind"})
out13 = mod.gate(REPO, PR, HEAD, token="t0ken", transport=g13)
check("T13 head contained in the merge commit -> merged=True on leg A alone "
      "(leg B never called — containment, not timestamps)",
      out13.get("merged") is True
      and out13.get("proof", {}).get("leg") == "head-in-merge-commit"
      and not any(c[0] == "GET" and f"main...{MERGE_SHA}" in c[1]
                  for c in g13.calls), (out13.get("proof"), g13.calls[-2:]))

# ---- T9 every call rides the ONE credential
all_calls = (g.calls + g2.calls + g3.calls + g4.calls + g5.calls + g7.calls
             + g8.calls + g10.calls + g11.calls + g12.calls + g13.calls)
check("T9 every API call rides the ONE passed token; verdict dicts carry no token",
      all(c[3] == "t0ken" for c in all_calls)
      and all("t0ken" not in str(o) for o in (out, out2, out3, out4, out5,
                                              out6, out7, out8, out10, out11,
                                              out12, out13)))

print("DONE release_merge_gate_clrlx", "OK" if fails == 0 else "FAIL")
sys.exit(0 if fails == 0 else 1)
