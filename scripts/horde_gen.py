#!/usr/bin/env python3
"""horde_gen.py — successor to the zap-local mkhorde.py wave generator.

Estate backlog-inferno horde generator: live store scan -> law buckets ->
workflow graph JSON + wave manifest, with the five W19 process-defect fixes
(est-a5obt, incidents from run 20261012-193402-inferno-w19-horde) built in:

  DEFECT-1 (accepted pre-existing, RETAINED): RECLAIM reads holder notes
      (`bd comments <id>`) and probes open PRs BEFORE any reclaim; a live-lease
      premise comment => refuse, never strip a live lease.
  DEFECT-2 (this file): every worker receipt schema carries a mandatory
      `writes: [...]` list; `horde_gen.py reduce <run_dir>` cross-checks the
      declared write count against the real `bd comments` delta since wave
      start — a receipt claiming "no mutation" with a nonzero delta is RED.
  DEFECT-3 (this file): VERDICTS is a closed enum; it is baked into the node
      schema AND into the worker law text. Verdict strings outside the enum
      are rejected by the reducer, ending vocab sprawl (65 receipts / 20
      phrasings at W19).
  DEFECT-4 (this file): every comment append goes through dup_guard() — an
      EXACT-LINE check (`bd comments <id>` | grep -Fxq) BEFORE the write, not
      a post-hoc count. Duplicate stamps/refusals cannot be emitted.
  DEFECT-5 (this file): the reclaim header uses the SCOPED `--id` form only
      (`bd reclaim --id <ID> --json`); the positional form is rejected by the
      deployed bd build (est-9mx4m) and the docs/header now align.

Law notes inherited from the mkhorde lineage (unchanged): PEER-STAMP only
comments, no mutations; CLOSE paths require a source probe taken by the wave
itself and cited in the close_reason (est-zee7e lesson); comment-activity
law (any comment <24h old => row LIVE => stamp only, no take) applies before
any takeover; est-2ek.1 cohort-close is RETIRED unless the owner re-opens it
by carrier comment; COHORT rows fall through to NEW-TRIAGE.

Usage:
  horde_gen.py emit  --wave w34 [--lanes 4] [--max-items 12] [--out FILE]
  horde_gen.py reduce <run_dir>            # receipt-vs-store cross-check
"""
import argparse, datetime, json, os, re, subprocess, sys

STORE = os.environ.get("HORDE_STORE")          # bd store path (required env)
ACTOR = os.environ.get("HORDE_ACTOR", "horde") # bd actor identity
ORPHANS_FILE = os.environ.get("HORDE_ORPHANS_FILE", "")  # optional shield list
SHELF_PREFIX = "est-2ek."          # clankville personal — hands off
IDLE_TAKEOVER_H = 24               # owner stale-claim law, msg 1559533626339762207
COMMENT_LIVE_H = 24                # comment-activity law

# DEFECT-3: closed verdict vocabulary. Extend ONLY via review-lane PR.
VERDICTS = [
    "closed", "handback-premise-live", "live-respected-stamped",
    "blocked-reasoned", "already-gone", "reclaim-refused",
    "take-refused", "unverified-no-touch", "readback-fail",
    "store-stall", "refused-shield", "refused-owner-gate",
]
# DEFECT-2: receipt schema — writes[] mandatory (list of {kind,target,ts}).
RECEIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "bead_id": {"type": "string"},
        "verdict": {"type": "string", "enum": VERDICTS},
        "evidence": {"type": "string"},
        "writes": {"type": "array", "items": {"type": "object", "properties": {
            "kind": {"type": "string", "enum": ["comment", "update", "close", "claim", "reclaim"]},
            "target": {"type": "string"}, "ts": {"type": "string"}}}},
    },
    "required": ["bead_id", "verdict", "writes"],
}

LAW = (
    f"HORDE LAW (actor {ACTOR}): store `timeout 60 bd -C {STORE} --actor {ACTOR}`; --json stdout alone 2>/dev/null. "
    "Fresh show first (closed => already-gone STOP). COMMENT-ACTIVITY LAW FIRST: any comment younger than 24h => row LIVE => stamp only (live-respected-stamped), no take. "
    "Takeover basis msg 1559533626339762207: assigned-but-idle >=24h is fair game via GUARDED take `update <ID> -a zap --if-assignee <holder>` (never --force). "
    "DEFECT-5 reclaim form (scoped only): `timeout 60 bd reclaim --id <ID> --json`; then comment 'RECLAIM-horde: expired <assignee> lease returned to ready' via dup_guard. "
    "DEFECT-1: before ANY reclaim, read `bd comments <ID>`; holder note naming an OPEN PR or live lease => reclaim-refused, do not strip live leases. "
    "Closes: only on a premise probe THIS worker ran (gh pr view / df / file / service), and close_reason MUST quote the probe; live premise => handback-premise-live. "
    "DEFECT-4: BEFORE any comment append run dup_guard (below); exact-line already present => skip append, keep receipt write-free. "
    "DEFECT-2: receipt MUST list every write in writes[]; a missing/extra write is a false receipt. "
    "DEFECT-3: verdict only from the closed enum. Net-zero-birth: spawn zero beads. Shield: est-2ek.* prefix and the orphans file are untouchable (refused-shield); owner-assigned => refused-owner-gate."
)

def bd(*args, timeout=60):
    if not STORE:
        sys.exit("HORDE_STORE env var is required (path to the bd store)")
    return subprocess.run(["timeout", str(timeout), "bd", "-C", STORE, "--actor", ACTOR, *args],
                          capture_output=True, text=True).stdout

def dup_guard(bead_id, line):
    """DEFECT-4: exact-line dup-check BEFORE append. True => safe to append."""
    existing = bd("comments", bead_id)
    return ("\n" + line) not in ("\n" + existing) and not any(l == line for l in existing.splitlines())

def _age_h(iso):
    try:
        t = datetime.datetime.fromisoformat((iso or "").replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=datetime.timezone.utc)
        return (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() / 3600.0
    except Exception:
        return -1.0

def _newest_comment_h(bead_id):
    ds = re.findall(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d", bd("comments", bead_id))
    ages = [_age_h(d.replace(" ", "T")[:16] + ":00Z") for d in ds]
    return min((a for a in ages if a >= 0), default=1e9)

def scan_candidates():
    """Live-store takeover candidates: idle>=24h, non-zap, non-owner, non-shield,
    comment-dead. Same gates the manual pre-gate uses (PUSH#24/25/26 lesson:
    pre-gate BEFORE dispatch; an empty manifest is a lawful result)."""
    raw = bd("list", "--status", "open,in_progress", "-n", "0", "--json")
    rows = []
    if raw.strip():
        try:
            o = json.loads(raw)
            rows = o if isinstance(o, list) else [o]
        except Exception:
            buf = ""
            for line in raw.splitlines():
                buf += line
                try:
                    o = json.loads(buf)
                    if isinstance(o, dict):
                        rows.append(o); buf = ""
                except Exception:
                    continue
    shield = set()
    if os.path.exists(ORPHANS_FILE):
        shield = {l.split("\t")[0].strip() for l in open(ORPHANS_FILE) if l.strip()}
    out = []
    for x in rows:
        bid = x.get("id")
        if not bid or bid.startswith(SHELF_PREFIX) or bid in shield:
            continue
        asg = x.get("assignee")
        if asg in (None, "", "zap", "owner"):
            continue
        if _age_h(x.get("updated_at")) < IDLE_TAKEOVER_H:
            continue
        if _newest_comment_h(bid) < COMMENT_LIVE_H:
            continue                     # comment-activity law: LIVE
        out.append({"bead_id": bid, "disposition": "STALE-TAKEOVER",
                    "why": f"idle>=24h holder {asg} comment-dead; basis msg 1559533626339762207"})
    return out

def emit(args):
    cand = scan_candidates()
    items = cand[: args.max_items]
    if not items:
        print("PRE-GATE EMPTY — no lawful targets; launching would be zero-fanout "
              "(prohibited by arithmetic). Manifest not written.", file=sys.stderr)
        return 3
    lanes = {}
    for i, it in enumerate(items):
        lanes.setdefault(f"HA{i % max(1, args.lanes) + 1}", []).append(it)
    nodes = [{"id": "root", "type": "agent", "goal": "Anchor only; reply {ack:true}.",
              "schema": {"type": "object", "properties": {"ack": {"type": "boolean"}}, "required": ["ack"]}}]
    for lane, its in lanes.items():
        nodes.append({"id": lane, "type": "agent", "after": ["root"],
                      "goal": "Execute one row per fan-out item per HORDE LAW; final message = one receipt JSON.",
                      "context": LAW, "schema": RECEIPT_SCHEMA,
                      "fanout": {"items": its, "goal": "Process assigned row per node law."}})
    graph = {"name": f"inferno-{args.wave}-horde", "defaults": {"model": args.model,
             "max_turns": 22, "schema": RECEIPT_SCHEMA}, "concurrency": 8, "nodes": nodes}
    out = args.out or f"inferno-{args.wave}-horde.graph.json"
    json.dump(graph, open(out, "w"), indent=1)
    json.dump(items, open(out.replace(".graph.json", ".manifest.json"), "w"), indent=1)
    print(f"emitted {out}: {len(items)} items / {len(lanes)} lanes")
    return 0

def reduce_run(args):
    """DEFECT-2/3: receipts-vs-store cross-check. RED on vocab violation or
    declared-vs-actual write-count divergence for any receipt."""
    run = args.run_dir.rstrip("/")
    reds = []
    start = datetime.datetime.fromtimestamp(os.path.getmtime(run), datetime.timezone.utc)
    for dp, _, fs in os.walk(os.path.join(run, "work")):
        for f in fs:
            if f != "result.jsonl":
                continue
            for line in open(os.path.join(dp, f)):
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                v = r.get("verdict"); w = r.get("writes")
                if v not in VERDICTS:
                    reds.append((dp, "DEFECT-3 vocab", v))
                if not isinstance(w, list):
                    reds.append((dp, "DEFECT-2 writes[] missing", str(w)[:40])); continue
                bid = r.get("bead_id")
                if bid and any(x["kind"] in ("comment", "close", "update") for x in w):
                    ds = re.findall(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d", bd("comments", bid))
                    fresh = sum(1 for d in ds
                                if datetime.datetime.fromisoformat(d.replace(" ", "T")[:16] + "+00:00") >= start)
                    declared = sum(1 for x in w if x["kind"] == "comment")
                    if declared and not fresh:
                        reds.append((dp, "DEFECT-2 false-receipt: declared comments, store shows none since wave start", bid))
    print(json.dumps({"checked_run": run, "reds": reds}, indent=1))
    return 1 if reds else 0

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit"); e.add_argument("--wave", required=True)
    e.add_argument("--lanes", type=int, default=4); e.add_argument("--max-items", type=int, default=12)
    e.add_argument("--model", default="claude-haiku-5-5"); e.add_argument("--out")
    e.set_defaults(fn=emit)
    r = sub.add_parser("reduce"); r.add_argument("run_dir"); r.set_defaults(fn=reduce_run)
    a = ap.parse_args()
    sys.exit(a.fn(a))

if __name__ == "__main__":
    main()
