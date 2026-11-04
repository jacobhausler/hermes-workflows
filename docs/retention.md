# Run-dir + drill-scratch retention (scripts/retention.py)

The measured failure this rule answers: **age-only cleanup cannot bound a
seat's disk, because the mass is not where the age is.** On the Mac seat that
filed this, every run dir older than 14 days summed to ~4.5 GiB, while a
SINGLE nightly attempt dir carried ~19.5 GiB of extracted backup payloads —
one week old. The first-class criterion is therefore a **per-run SIZE CAP**;
the age cut is the second blade, not the first.

## The rule, per artifact class

| class | what it is | bound | what survives |
|---|---|---|---|
| A — per-node workspaces + validation copies | `<run>/work/**`, payload files (`*.tar*`, `*.tgz`, `*.gz`, `*.sqlite*`, `*-wal`, `.db`, `.zip`) and any `backup/` subtree; the extracted online-DB copies a nightly qualification round leaves behind | **cap:** a terminal run dir whose total exceeds **4 GiB** (`WF_RETENTION_CAP_BYTES`) loses them once **48 h** (`WF_RETENTION_PAYLOAD_HOURS`) past terminal | transcript/package files at the run-dir root (`run.json`, `graph.json`, `events.jsonl`, `runner.log`, `summary.md`, …) — small, and the transcript-mining substrate |
| B — run transcripts (whole dir) | the run dir itself | **age cut:** **14 days** (`WF_RETENTION_AGE_DAYS`) after last package-file activity. Age anchor is the newest of the package files, NEVER the dir mtime (a payload prune refreshes the dir and must not reset the clock) | protected dirs are skipped whole (below) |
| C — drill scratch | `$HOME/backup-assurance-YYYYMMDD-*` (dated dirs are the naming law) and drill leftovers under `~/.cache` (`f2-drill`, `hermes-source-*`, `*-hermes-*-a*`, `*drill*`) | **EVIDENCE-FIRST:** dated by the name-carried `YYYYMMDD` (fallback mtime); a completed drill closes **in the drill itself** with `retention.py prune --drill-now` (receipt-then-delete); an abandoned one only after **7 d** (`WF_RETENTION_DRILL_TTL_DAYS`); cache leftovers after **14 d** (`WF_RETENTION_CACHE_AGE_DAYS`) | the small evidence files (json/jsonl/log/py/txt/md/sh/out, ≤ 64 MiB) copied to `$HOME/.local/share/backup-assurance/<drill-dir>/` BEFORE the copy trees are deleted. The receipt is the evidence, not the 23 GiB of copies |

## Never-delete law (protection, evaluated first, fails toward keeping)

A run dir is skipped **whole** — no payload prune, no age cut — when:

1. its name is referenced by an **unclosed tracker row** (the
   `bd list --json` export of every not-closed row piped via
   `--beads-json`), or
2. its name appears in any file under the nightly **receipt roots**
   (`--receipt-root`, ≤ `--receipt-scan-days` old), or
3. it carries a `.owner-held` / `OWNER_HELD` marker, or an explicit
   `--protect <name>` pin, or
4. it is **in flight** (inside the 48 h grace on its package files), or
5. it is one of the newest `--keep-newest` (default 2) nightly-named dirs
   **and under the cap** — an over-cap attempt is capped even when newest,
   because that is exactly the size this rule exists to bound.

If the tracker export is unavailable, the prune still frees over-cap
payloads but performs no whole-dir age cut that tick (the receipt says
`tracker: UNREADABLE` / `absent` — honest instrument, never a guess).

## Schedule + receipt (no new timers)

`scripts/retention.py prune` is one leg of the existing hourly disk-janitor
tick on each seat (canonical `tools/janitor/disk-janitor.sh` in the estate's
ops-docs repo, run from the Mac seats' user crontab `0 * * * *`), placed
OUTSIDE the threshold gate so it runs every hour like the nightly-mirror leg
before it — retention must be calendar-independent or the fill comes back
between samples. It appends ONE line to the same `janitor.jsonl` the janitor
census already tails (`--receipt-file $RECEIPT_DIR/janitor.jsonl`), in the
same schema, and writes per-skip detail to `--report-dir`; the prune reports
its **freed bytes** on the existing rails:

```text
python3 scripts/retention.py prune --beads-json <(bd list --json) \
    --receipt-root ~/.local/share/estate-nightly/ledger \
    --receipt-root <seat nightly maintenance-receipt.json> \
    --report-dir "$RECEIPT_DIR" --receipt-file "$RECEIPT_DIR/janitor.jsonl"
→ retention: status=retention freed_bytes=… actions=N …
```

`--dry-run` plans without deleting and writes no janitor receipt line.

## Measured recovery (first apply, the Mac seat, 2026-11-04)

| class | freed (first apply, df-avail measured per action) |
|---|---|
| A — workspace + validation copies (2 over-cap nightly attempts, 25.3 GiB + 20.9 GiB) | **43.0 GiB** (46,190,714,880 B) |
| B — whole dirs at the 14 d age cut (238 dirs, Sep-23..Oct-21 incl. the 65-attempt wake burst) | **4.45 GiB** (4,777,074,688 B) |
| C — drill scratch (one completed 2026-11-04 backup-assurance drill; 56 MB of receipts copied out first) | **23.6 GiB** (25,327,509,504 B) |
| C — drill cache leftovers | **0 on first apply** — the nine row-listed dirs were 10–12 d old and skipped conservatively; ~6.8 GiB crosses the 14 d line 2026-11-06/09 and the hourly leg takes them then |
| total | **71.1 GiB** (76,316,307,456 B) |

Disk free moved from **52 GiB (88 % used)** to **123 GiB (72 % used,
26.7 % free)**; both `DiskAlmostFull` branches (free < 5 %, or free < 20 %
AND `predict_linear` 3 d negative) went false — `/api/v1/alerts` showed zero
`DiskAlmostFull` rows on the next 15 s rule evaluation after the prune
finished, read from Prometheus, not recounted by hand.

The protection law is pinned by `tests/test_run_retention_fxpsl.py`: an
over-cap run dir named by an open tracker row or a nightly receipt survives
whole, and the live first-apply left `20261028-000003-nightly-2026-10-28-a0`
(24.5 GiB, the day's drill input) untouched by name of this bead's own open
row — see the `retention:` stdout skip-reasons sample on the receipt run.
