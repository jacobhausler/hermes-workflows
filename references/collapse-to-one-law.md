# Collapse-to-one law (est-1n7gx, WF-GRAFT-7)

**Every site that collapses many rows to one — a sort feeding a head, a
first-seen dedupe, a max/min, a manifest `last_written` — names its TOTAL
order in code beside the sort/pick with a because-clause. Never let ties fall
through to filesystem-traversal or dict-insertion order. Where insertion order
IS the intended contract, say so in the comment and pin it with a test.**

## Why

Coarse timestamp granularity is routine: same-second (or float32) mtimes on
coarsely-timestamped filesystems, mirrored roots, twin dirs. A pick whose tie
is decided by readdir order splits the same bytes differently on every
machine — the "newest" artifact, the banked `last_written`, the incumbent lane
entry all become traversal luck. The peer plugin proved the fix at the SQL
layer: every collapse-to-one query carries `ORDER BY COALESCE(started_at, -1)
DESC, id DESC` (its run repository; its tests seed same-timestamp rows to pin
the id tie). A key whose last component is unique (path, id, attempt index)
cannot tie, so the order is total and any two machines agree on the head.

## The shape of a compliant site

- A sort key ending in a unique discriminator:
  `key=lambda f: (-f.stat().st_mtime, relpath)` (mtime DESC, ties by relative
  path ASC), or `(mtime, attempt_no)` with `reverse=True` (attempt DESC — the
  spawn index is the later-attempt signal mtime carries).
- A first-seen dedupe over an enumeration that is itself total: the ONE
  run-dir walk sorts by directory name — unique per root by filesystem law —
  and takes roots in argument order (resolved before legacy). Say so beside
  the pick.
- An explicit refusal in the order, not a hole in it: a key-mismatched lane
  entry refuses typed rather than falling through to its legacy twin.

## Named sites (census at est-1n7gx)

| Site | Pick-one | Total order |
|---|---|---|
| `wf._work_files` (the ONE durable-work walk) | head = newest artifact | mtime DESC, relpath ASC |
| `wf._bank_the_corpse` manifest | `last_written` = rows[0] | inherits the ONE walk above |
| `wf._resume_hint_block` | dead-attempt inventory work + attempt logs | ONE walk; logs mtime DESC, attempt DESC |
| `wfcommon.iter_run_dirs` | first-seen dedupe | roots-arg order, then name (unique per root) |
| `wfcommon.find_run` | run-by-name twin | roots [resolved, legacy], first dir yielding a view |
| dashboard `_list_runs` | same-view-id dedupe | iter_run_dirs name-DESC; resolved row wins |
| door `_library_rows` | same-name shelf pick | roots order, general/ group first, name ASC |
| door `_lane_entry` | lane incumbent | resolved file beats legacy twin |
| `wfcommon.seat_wait_view` | oldest open wait per node | since ASC, str(idx) ASC |
| `wfcommon.current_attempt` | most-recent activity | (last_activity, unique title) — total by construction |
| door `act_library` rarest-term hint | rarest starved term | count ASC, term ASC (query-order invariant) |
| door `act_status` seat_wait row cap | first cap-bearing node | node-name ASC scan (per-node cap from seat_wait_view) |

Graph-declaration-order scheduler picks (runner + read-model ready-gate
`next()`, consolidate-partner `next()`) carry because-comments naming the
declaration-order contract: they are deterministic in the graph.json bytes —
the DAG executes the graph's own enumeration — not filesystem/insertion luck.

## Enforcement

`tests/test_tiebreak_law_1n7gx.py` — one check per named site; the mtime sites
are driven with an adversarially forced traversal order (a real fs order is
not reproducible and must not be load-bearing), so the test flips RED iff a
tie again falls through to walk order. A later deterministic-tie-break graft
inherits this law; keep the rule text generic (not mtime-scoped) when quoting
it.
