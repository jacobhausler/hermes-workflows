#!/usr/bin/env python3
"""hw-73c: AGENTS.md must survive the core subdirectory-hint load untruncated.

Symptom (bead hw-73c): every mid-run touch of this repo re-loads AGENTS.md
through core's subdirectory-hint path, which caps one file at
`_MAX_HINT_CHARS = 32_000` (`agent/subdirectory_hints.py:26`, sole call site
:252-254 -> `agent/prompt_builder.py:_truncate_content`, head/tail ratios
0.7/0.2, `queue_warning=False` — the branch whose log wording matches every
observed `Context file AGENTS.md TRUNCATED` row). Over the cap the MIDDLE is
dropped and the only trace is a log line: the reader silently loses the
sections that live in the middle of the file. At tip the file was 38,883 chars,
so 10,083 middle chars — §3e and all of §4 Contribute — vanished from every
session that touched the repo mid-run.

`context_file_max_chars` is NOT the knob (it governs the startup load only);
the bead's CORRECTION rules the fold is the fix. So the contract pinned here
is the cap itself, plus the anti-deletion guards a fold must keep: the folded
tour still exists in `references/`, is linked from the front door, and still
carries the template names it carried.

Run: python3 tests/test_docs_hint_cap_73c.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Mirror of core's constants (agent/subdirectory_hints.py:26,
# agent/prompt_builder.py CONTEXT_TRUNCATE_HEAD/TAIL_RATIO) — the load contract.
MAX_HINT_CHARS = 32_000
HEAD_RATIO, TAIL_RATIO = 0.7, 0.2

FOLD = ROOT / "references" / "example-tour.md"
TOUR_MARKS = ("gated-publish", "machine-watch", "incident-response", "blind-council",
              "triage-route", "quorum-probe", "bulk-transform", "census-fanout",
              "escalation-ladder", "exchange-run")

fails = total = 0


def check(name, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not cond else ""),
          flush=True)
    if not cond:
        fails += 1


doc = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

# 1. THE SYMPTOM: what core's hint load would hand a mid-run session.
head = int(MAX_HINT_CHARS * HEAD_RATIO)
tail = int(MAX_HINT_CHARS * TAIL_RATIO)
middle = doc[head:len(doc) - tail] if len(doc) > MAX_HINT_CHARS else ""
lost = [s.strip() for s in middle.splitlines() if re.match(r"#{1,6} \S", s.strip())]
check("AGENTS.md fits the 32,000-char hint cap (nothing silently dropped)",
      len(doc) <= MAX_HINT_CHARS,
      f"{len(doc)} chars over {MAX_HINT_CHARS}: the hint load drops {len(middle)} middle chars, "
      f"taking the sections {lost[:6]}")

# 2. THE FOLD, not a deletion: the tour lives on in references/ ...
check("the §3c tour was folded into references/example-tour.md", FOLD.is_file(),
      "AGENTS.md is over the hint cap and no fold target exists")
if FOLD.is_file():
    folded = FOLD.read_text(encoding="utf-8")
    missing = [m for m in TOUR_MARKS if m not in folded]
    check("the folded tour still names every template it carried", not missing, f"missing: {missing}")
    check("the folded tour's links are valid from references/",
          not re.findall(r"\]\((?!https?:|#|\.\./)[^)]+\)", folded),
          "relative links must be ../-prefixed one level down")

# 3. ... and the front door still points at it.
check("AGENTS.md §3c points at the fold",
      "references/example-tour.md" in doc, "reader has no path to the moved content")

# 4. Review-round guards (zap @ f3be8476): the fold must not break fence parity,
# must fold (not clone), and every folded section keeps its own pointer/headings.
fences = re.findall(r"^(`{3,}|`{2})\s*$", doc, re.M)
check("AGENTS.md fence parity (no consumed closing fence)",
      len(fences) % 2 == 0 and "`Rules that bite:" not in doc,
      f"{len(fences)} fence lines (odd = unterminated block)")
if FOLD.is_file():
    paras = [p.strip() for p in folded.split("\n\n") if len(p.strip()) > 120]
    dupes = {p[:60] for p in paras if paras.count(p) > 1}
    check("the fold moves, never clones (no duplicated paragraphs)", not dupes,
          f"duplicated paragraphs: {sorted(dupes)[:2]}")
    check("folded sections carry their own headings",
          "§3b" in folded and "Where things live at runtime" in folded,
          "the §3b/§5 payloads need named sections in the fold file")
    check("no self-link inside the fold file",
          "../references/example-tour.md" not in folded)
check("AGENTS.md §3b points at the folded settings variant",
      "Folded out for the hint cap" in doc,
      "stranded fold: reader of §3b has no path to the moved variant")

print(f"TOTAL {total - fails} PASS {fails} FAIL", flush=True)
raise SystemExit(1 if fails else 0)
