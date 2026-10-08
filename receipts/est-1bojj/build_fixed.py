#!/usr/bin/env python3
"""Build ra-release-peer.fixed.json from the shelf copy (est-1bojj); shelf untouched."""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
g = json.load(open(src))
nodes = g["nodes"]
by = {n["id"]: n for n in nodes}

# 1) peer_review spawns AS the peer seat (wf.py run_child: -p <profile> chat ...)
pr = by["peer_review"]
new_pr = {}
for k, v in pr.items():
    new_pr[k] = v
    if k == "type":
        new_pr["profile"] = "{run.PEER_PROFILE}"
nodes[nodes.index(pr)] = new_pr

# 2) non-merge arm: complementary gate + peer-seat stamp leg so pending never survives
hold = {"id": "peer_hold", "type": "gate", "after": ["peer_review"],
        "when": "out.peer_review.verdict != 'merge'", "on_skip": "prune"}
stamp = {
    "id": "peer_stamp", "type": "agent", "profile": "{run.PEER_PROFILE}",
    "after": ["peer_hold"], "model": pr["model"], "provider": pr["provider"],
    "timeout": 900, "max_turns": 15,
    "inputs": ["prepare.pr_url", "peer_review.verdict", "peer_review.why"],
    "goal": ("You are the PEER reviewer seat ({run.PEER_PROFILE}) closing the non-merge arm for "
             "{run.REPO} v{run.VERSION}. The peer verdict in ## Inputs is NOT merge, so publish is "
             "pruned and the PR's live PEER-LAW marker comment must not be left at verdict=pending "
             "(a pending marker on a finished run is indistinguishable from a mid-flight lane). "
             "Fresh-GET the PR's marker comment. If it still reads verdict=pending, PATCH it to the "
             "terminal verdict from ## Inputs (changes|decision; anything else -> decision) with "
             "reviewer={run.PEER_PROFILE} and the one-line why. If it already carries a terminal "
             "verdict, leave it. Then fresh-GET it again (read-back) and report what it says. Never "
             "stamp merge, never merge, never tag. Reply fenced JSON: {\"marker_verdict\": "
             "\"changes|decision\", \"reviewer\": \"{run.PEER_PROFILE}\", \"marker_url\": \"...\", "
             "\"readback\": \"verbatim verdict/reviewer line from the fresh GET\"}."),
    "schema": {"type": "object",
               "required": ["marker_verdict", "reviewer", "marker_url", "readback"],
               "properties": {"marker_verdict": {"type": "string",
                                                 "description": "Exactly changes or decision (never pending)."},
                              "reviewer": {"type": "string"},
                              "marker_url": {"type": "string"},
                              "readback": {"type": "string"}}},
}
gi = next(i for i, n in enumerate(nodes) if n["id"] == "peer_gate")
nodes[gi + 1:gi + 1] = [hold, stamp]

g["description"] = g["description"].replace(
    "a changes verdict terminally skips publish)",
    "a changes verdict terminally skips publish; complementary peer_hold(verdict!=merge) -> "
    "peer_stamp(peer seat) PATCHes the live marker off pending to the terminal verdict with read-back; "
    "est-1bojj: peer_review/peer_stamp carry profile:{run.PEER_PROFILE} so the spawn is -p <peer seat>)", 1)
assert "est-1bojj" in g["description"], "description anchor moved"
json.dump(g, open(dst, "w"), indent=1, ensure_ascii=False)
open(dst, "a").write("\n")
print("wrote", dst, [n["id"] for n in nodes])
