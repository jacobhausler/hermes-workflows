# Operator playbook (measured lessons; each one was paid for)

Authoring rules for build sprints, fleets, and babysitting. The grammar lives in
`grammar.md`, the read model in `operations.md`; this file is what lane runs taught
the hard way (0.7–1.1 era, condensed from seven build waves and ~70 spooled
papercuts).

## Build-sprint lanes (parallel agent lanes on one repo)

- **ONE runner per worktree.** Pre-create every lane's worktree yourself before
  `run`; the goal says "your worktree ALREADY EXISTS, never create one". Two runs
  on the same worktrees (e.g. after a gateway restart killed wave 1) put two
  children in one branch; the survivor spent its whole budget diagnosing the
  collision.
- **Wall, not turns, is the binding cap** on a ~90 s/call route: 90 turns × 80 s
  ≈ 2 h, so a 3600 s wall kills the child at turn ~45 with uncommitted work.
  Explicit `timeout` ≥ `max_turns` × real per-call latency, or cut `max_turns`
  (4/8 wave-1 lanes died at the wall with 0 commits).
- **Bank the corpse:** before reading a dead lane's output,
  `git add -A && git commit -m 'WIP (banked by integrator)'` in its worktree — the
  diff is usually 60–90 % of the item and the lane's notes tell you the rest.
- **Merge in dependency order and run the FULL suite after each merge**, never
  after the batch — regressions show up as one existing test failing, and batch
  attribution is guesswork.
- **Lane scratch homes:** lanes commit their scratch `HERMES_HOME` (state.db,
  SOUL.md, run dirs) unless the fixture home is under `tests/` and gitignored.
  The scrub audit and graph gate catch it, but only after you built over it.
- **Shape before size:** derive T1, T∞, drag, and F from the last run's
  `events.jsonl` BEFORE choosing lane count, walls, or depth. Wide-fat-with-
  barriers is the wrong default: split only along disjoint write-sets at ≥5F,
  merge on arrival, synthesize over ≤2-call lane manifests.
- Give lanes two items each with file:line anchors IN the goal. A lane given
  seven items and "find the code" spends its budget on recon; lanes handed the
  previous wave's recon started at code and shipped.
- **Author-lane PRs route the review node to a consenting teammate profile from
  the start** (`profile` node field + target's `workflow_team.json`). A same-seat
  review is peer-law-bound to return `decision` — don't burn a node on it.

## Fleet children (audits, censuses, sweeps)

- **Write-first contract on flaky providers:** children create the artifact file
  FIRST and append findings after every 1–2 probes; the final answer is a pointer
  line. A connection-error death otherwise loses a finished investigation whose
  evidence already landed.
- **FILE-FIRST for big payloads:** any child whose answer can exceed a few KB
  writes the artifact to a file and returns only `{path, ≤200-char lines}` — a
  huge JSON answer line-truncates and fails schema, losing finished work.
- **Size the fan-out to the container's memory cgroup** (`memory.max`/
  `memory.current`), not host RAM — children are processes inside it; an OOM
  mid-wave kills parent and children and discards everything not mirrored.
- **Durable ground:** mirror every lane artifact out of ephemeral scratch into a
  durable dir the SAME turn the wave lands; later waves read only durable copies.
- A lane emitting the SAME tool error repeatedly is looping, not working:
  `status` shows rising idle with flat counts — `stop` it (or amend it out) and
  run its 3–5 probe commands yourself; sibling artifacts usually hold the answer.
- Every child gets the same hard-rules preamble in `context`: read-only on
  production, writes only under one named scratch dir, forbidden hosts named,
  honest-unknown valid, invented evidence not, cite exact commands + values.
- **Fan-out wait vs commit are separate rules:** unset `quorum` waits for EVERY
  item (no straggler cancellation), but the node COMMITS at majority
  (`len(items)//2 + 1`) — one flake in a lane of 3+ still commits with partial
  credit and survivors in `output.items`. Set `quorum:<n>` explicitly when you
  want early straggler cancellation or a stricter/looser commit bar; and read
  `failed_items`/`failed_detail` on a committed node — done does not mean all green.

## Babysitting (read model, not ps)

- **Stall detection:** a running node whose idle grows with flat `api_calls` is
  stalled — steer it or `stop` + amend; don't wait it out.
- **The host kills a tool call at ~420 s** (concurrent-batch deadline). `wait`
  self-yields in ~330 s segments with a "call wait again" note — loop on `wait`
  until terminal; never let your own sleeps approach 420 s.
- **STALENESS law for any external observer:** a node record stays present+`done`
  with its OLD efp while a re-run is in flight — the new record replaces it only
  at commit. Freshness = stored efp EQUALS current `wfcommon.efp(byid, node)`;
  efp presence proves era, not currency. Reuse `wfcommon.node_rec`; never invent
  a second validity rule.
- Failed fan-out nodes still commit survivors (`output.items` + `failed_detail`)
  — read them before rebuilding; and inspect a capped child's partial files
  before paying to re-run it.
- Recover publication-only failures publication-only: keep the finished
  investigation, amend only the failed handoff with an explicit fenced-json
  result contract. CLI banners around bare JSON can make a substantively
  finished review fail schema parsing.

## Ergonomics

- **Never hand-transcribe graph JSON over ~2 KB** — build the graph as a Python
  dict, `json.dumps` + `json_loads` to validate, then emit the compact string
  verbatim (or write it to a file and use `graph_path`). Generated → launches
  first try; hand-pasted → wasted calls on bare `not valid JSON` errors.
- **Model routing: pin provider+model when it matters.** A literal id that is a
  seat alias's TARGET can resolve differently than the alias (HTTP 400/404 from
  the wrong route), and an alias can preflight its bare name to the provider and
  die 404 (`opus` → `anthropic/opus` while the alias meant `claude-opus-5-5`).
  For anything but the seat default, pass explicit `provider` + literal `model`
  and read the `run` response's resolved route table — and check the child's
  served-model stamp before trusting execution.
- Bound reasoning as well as turns on recon nodes: set an explicit effort, make
  recovery consume existing artifacts, narrow unfinished checks; raising the
  timeout alone does not make a child write its conclusions.
- For a graph you'd build the same way again: `save` with a trigger description
  (+ `source` for provenance). One-offs stay in their run dir.
