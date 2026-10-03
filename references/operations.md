# Run operations and read model

This is the run, monitoring, and recovery reference. The per-action contract table lives once in the [README](../README.md); the graph vocabulary lives in [grammar.md](grammar.md). Start a run with `workflow {"action":"run","graph":<object>}` (or `from:<saved-name>`, or `graph_path:<absolute local JSON file>`), then follow the returned `run_id` with `status` and `wait`. `save` first and `run from:<name>` next is the reusable path; `library` lists what is shelved. `graph_path` is an unsaved caller-supplied local regular file (≤1 MiB, no final symlink) accepted on run/save/amend — never a remote URL. `/wf` lists the library; `/wf <name> [note]` runs it with `note` as the `run_context` seed.

## Launch-time binding: `run_context`

Exactly one of two shapes, both validated **before any run directory is written or any child spawns** — a malformed binding is an error response, not a half-started run:

- **String seed** — appended to every first-wave agent's prompt (including agents behind gate-only paths). It cannot bind `{run.KEY}` references: a seed against a graph containing `{run.KEY}` is refused, and a seed never replaces a baked literal. At least one first-wave agent is required.
- **Map (identifier keys → non-empty strings)** — replaces only explicit `{run.KEY}` references in node goals/contexts, fan-out goals and per-item goals, and gate questions. A missing key, a malformed reference, a non-string or brace-containing value, or a map that was JSON-encoded and passed as a string is refused before any write.

Values bound this way are persisted into stored prompts: **never put secrets in `run_context`.**

## Run states

| State | Meaning | What to do |
|---|---|---|
| `running` | A verified live runner process holds this run | `wait` |
| `held` | Waiting on a human gate | ask the owner, then `release` |
| `interrupted` | Unfinished work with no verified live runner (raw files alone never prove "running") | inspect saved outputs and uncertain side effects, then explicitly resume with `wait` |
| `liveness-unknown` (open PR #47) | The process-liveness probe timed out or failed — the plugin will not guess | `runner_live:null`, derived `next:'observe'`; `wait` refuses to spawn anything while the probe cannot answer; `needs_resume` fires only on a definite `runner_live:false`; an explicit recorded crash outranks unknown |
| `done` | Terminal success | read outputs |
| `failed` | Terminal failure (including a recorded fatal runner crash) | answer from `node_facts`, then correct and `amend` — repeated `wait`/respawn does not fix a fatal crash |
| `stopped` | Stopped by `stop` | cancelled work re-drives on resume; a gate answer is refused while stopped |

Held gates and interrupted runs do not count as running: `running` in the strict sense means a live process matching the exact runner command and run identity — a persisted PID or parked marker alone is not sufficient. `status` and `wait` are read-only — `wait` is the sole read action that respawns an idle runner, and `status` never spawns (its `lane_key` form just reads the incumbent). List responses carry the full-census `run_summary` `{total, counts}` even when the recent-runs page is capped (50 rows across the resolved and legacy roots; resolved wins on collision).

Every `status`/`wait` payload carries the derived `next`: `held` → `release`, `running`/`interrupted` → `wait`, `failed` → `amend`, terminal → `[]`. Do what it says and `wait` again until it is empty. On a held gate `next` names the gate and its options; ask the owner, then `release` with the exact answer. A machine gate (a `gate` node with a `wait` block) can park with zero child tokens — on a timer and/or a fixed argv probe re-run until exit 0; read its attempt count, last exit/tail, and deadline. A human `release` pre-empts a machine park.

## `wait` and the host tool deadline

`wait` blocks while the runner is live: default 600 s, clamped to 1800 s. It **self-yields in 330 s segments** and returns the current status plus a "call wait again" note, so a long block never dies mid-sleep to the host's own tool-call timeout — the host kills a tool call at its own deadline, typically around 420 s but **host-dependent** (it is not a plugin constant; the 330 s segment is chosen to stay under that typical value with margin). Loop on `wait` until `next` is empty. `wait` also carries a dying-runner companion: at most three throttled re-spawns of an idle runner per call.

## Run directory layout

Everything a run persists lives under `<runs_root>/<run_id>/` (`runs_root` resolution below):

| File | What it holds |
|---|---|
| `run.json` | Run identity and request (name, team, lane_key, dispatched_by, targets, graph_source, includes record) |
| `graph.json` | The expanded, validated graph the runner actually drives (fully expanded and `include`-stripped; open PR #84) |
| `events.jsonl` | Append-only lifecycle event log (vocabulary below) |
| `summary.md` | Terminal summary |
| `nodes/<id>.json` | Committed per-node results (output, metrics, efp, session key) |
| `logs/<id>.a<n>.prompt.md` / `.log` | Per-attempt rendered prompt and child log |
| `steer/<id>.jsonl` | Queued steer lines per node |
| `gates/<id>.json` | Gate state files |
| `runner.lock` / `wf.pid` | Kernel `flock` admission lock and the runner's recorded pid |
| `runner_exit.json` | The runner's recorded exit verdict (a fatal-crash record outranks state guessing) |
| `restart.request` / `stop.request` | Marker files: hot restart requested, stop requested |
| `amends.jsonl` | Append-only amend history |
| `inbox.jsonl` | Steer lines a child pulls via the `inbox` action |
| `../lanes/<sha16>.json` | The lane registry entry (append-only, keyed by the lane_key hash) |

## `events.jsonl` vocabulary

Event families and what they signal:

| Event | Meaning |
|---|---|
| `run.started` / `run.resumed` / `run.done` / `run.stopped` | Run lifecycle bookends |
| `run.blocked` | Run parked with unfinished work; names the `failed` and `blocked` node sets — read this before deciding |
| `node.started` / `node.finished` / `node.done` / `node.skipped` / `node.failed` | Per-node lifecycle (`node.done` also marks echo nodes) |
| `node.retrying` / `node.retry_skipped` | A failed attempt entered the bounded retry path, or the per-run retry budget (6) was exhausted |
| `node.interrupted` / `node.extended` | Node cut by runner death; node's timeout extended once because its log was active in the last 120 s |
| `node.child_home` | Records the child's resolved home (relevant to where its metrics live) |
| `item.started` / `item.finished` / `item.retrying` / `item.retry_skipped` / `item.goal_dangling` | Per-fan-out-item lifecycle |
| `gate.parked` / `gate.held` / `gate.released` / `gate.skipped` | Machine park, human hold, release, `on_skip` skip |
| `gate.wait_timeout` / `gate.when_error` | Machine park exceeded its timeout (gate fails); a `when` predicate errored at runtime — fails safe by holding the gate, never a silent skip |
| `steer.queued` / `steer.baked` / `steer.consumed` | Steer lifecycle; `steer.baked` fires per spawn carrying the lines that went into that prompt (`n_lines:0` is noise) |
| `graph.amended` / `graph.reloaded` | Whole-graph replacement accepted; live runner hot-reloaded it at a wave boundary |
| `spawn.killed` / `runner.reaped` / `inbox.appended` | A child killed at a stop boundary; a dead runner cleaned up; a line appended to the run's inbox |
| `route.reverify_failed` | A served-model contradiction caught at commit — the node failed closed with `route_unavailable` |
| `meta.stopped` | Runner stopped for run-metadata reasons |

Failed and partial nodes additionally ship `node_facts` beside the error line: `error_class`, `attempts`, `attempts_log`, the child's `final` words, `log_path`, `prompt_path`. Answer questions from `node_facts` before re-driving anything. The `error_class` set is closed: `cancelled`, `cap_exhausted`, `crashed`, `early_death`, `fanout_empty`, `fatal_quota`, `forbidden_model`, `incomplete_work`, `inputs`, `precondition`, `quorum`, `route_unavailable`, `schema`, `spawn`, `timeout`, `transport`, `transport_exhausted`, `provider_400`, `unresolved_model`, `graph_invalid` (`unknown` is only a harvest-time default). A turn-cap death is typed `cap_exhausted` only when the child's own loop-budget stamp is in the record — prose about turn limits is never trusted, and an untyped budget death stays `unknown`.

## Reading status honestly

- `status.nodes` schedules from committed results; an uncommitted child spawn is projected as running only while its recorded process identity is verified. `blocked_by` points to unfinished ancestors. Outputs are pointers by default (`output_ptr`, `output_keys`, `output_bytes`); `detail:"full"` attaches them.
- Child spend metrics (tokens in/out, api_calls, tool_calls, cost_usd, live/idle) are cumulative across attempts and graph amendments. A node routed to another profile (`profile` field) folds its spend through **that child's own profile database**, not the launcher's (open PR #79), so routed children's spend shows up instead of reading as zero. Wherever evidence is missing it reads unknown/absent, **never a false zero**; not every run has a metrics row, and missing current activity means unknown idle, not zero.
- Liveness and heartbeat come only from exact, currently verified child process identities: `active_spawns` lists all live fan-out children; `active_spawn` retains the first for existing consumers.
- A run is only as billable as its evidence: `estimated_cost_usd` is an estimate, never a bill.
- Stale runner exits do not suppress amended work. A pruned/skipped node is terminal, not done output.
- Every `run`/`status`/`wait` payload carries a `card` line — a pasteable one-line run summary. Paste it alone on its own line in a chat reply and the desktop renders the live card (`::workflow{id="<run_id>"}`). The card is agent-authored; the backend never appends it. Backend and desktop plugin installations are separate.

## Steering, amending, stopping

- `steer` queues text for a **running or future** child spawn (run_id, node, text); it never rewrites a prompt mid-flight. Delivery is cooperative: a running child pulls at its next `inbox` call; a held run bakes the lines at release; an idle run bakes them at resume. Refused on gate, terminal, and already-done nodes. The child-side `inbox` action authenticates via the child's baked environment and is exactly-once per spawn via its cursor — lines queued after a spawn never reach that live child retroactively.
- `amend` replaces the **whole** graph (`graph` or `graph_path`). `dry_run:true` validates and previews `{added, removed, changed, will_rerun, unchanged}` and writes nothing. The freeze law: a node whose definition is unchanged (modulo budget/route/policy keys), whose route is untouched, whose efp (effective fingerprint — the content hash every node definition carries) still matches, and whose every ancestor is frozen keeps its committed result verbatim and replay-skips. Everything else re-runs. Appends `amends.jsonl`, rewrites `graph.json`, fires `graph.amended`; a live runner hot-reloads at the next wave boundary, otherwise respawn. Added nodes and their downstream work appear in `will_rerun`; matching committed results replay-skip.
- `stop` writes a stop marker and kills in-flight children at the next boundary. Stop is not rollback and not failure: reconcile external effects first; cancelled work re-drives on resume. Event: `run.stopped`.
- Resume, wait, and amend all re-drive under the run's own `runner.lock` `flock`: one runner process per run, spawned by the tool call itself — no daemon, no control plane. A losing spawner exits harmlessly printing `WORKFLOW_BUSY`; readers share one read model, and a re-probe across a dying runner's flock can disagree — take one read per decision.

## Wedged runner lock: `release_lock` (open PR #47)

If a runner dies holding its `runner.lock` in a way that blocks every legitimate re-spawn, the escape hatch is the `release_lock` action — `workflow {"action":"release_lock","run_id":"<id>"}` or the CLI `python3 wf.py release-lock <run_id>` (both share one verdict function). It **refuses unless all three proofs hold**:

1. the recorded runner pid is dead,
2. the run is not gate-held or machine-parked, and
3. two fresh `flock` probes 100 ms apart **both** acquire — proof no live process holds the lock.

It **never unlinks the lock file**. When the probes contest (something still holds it), it prints the believed holders, resolved from `/proc/*/fd` and `/proc/locks` by inode, so you can see who to wait for. When the verdict strands the run (the lock cannot be cleared and no holder can be identified), it returns a forensic payload, and the honest recovery is a **fresh run under a new `lane_key`** — not force-deleting anything.

## Lanes: in-flight dedupe for pollers

`run` accepts an optional `lane_key` (≤128 chars); `status` accepts `lane_key` instead of `run_id` (read-only, never spawns). The registry is an advisory index under a per-key kernel lock: while a claim is held, a second `run` with the same key never spawns — the unfinished incumbent wins. The dedupe response is `{deduped:true, run_id, state, runner_live, needs_resume, last_event_ts, hint}` with the incumbent's ids, regardless of runner liveness — an interrupted incumbent is resumed (`wait run_id=<id>`), never replaced. `stop` on the incumbent is the explicit abandonment: terminal `stopped` releases the key and the next claim creates a fresh run. Keys are global per runs root — callers namespace them (e.g. a `<team>/` prefix) themselves. Entries are append-only; a stored key must equal the supplied key exactly (a hash collision against a different key is an error, never a dedupe). `status lane_key=<key>` answers `{lane_key, run_id, state, runner_live, unfinished, needs_resume, last_event_ts}` — `runner_live` is `/proc` truth, not a persisted marker; `needs_resume` = unfinished **and** definitively dead runner, the poller's signal to `wait`. An unseen key returns `run_id:null, unfinished:false`. `list` rows carry `lane_key`/`team` when present. A `team` label (≤64) on `run` stamps `run.json` and shows in `list`; it changes nothing about scheduling. `list` also reports a per-root `provenance:{dispatched_by_set,total}` rollup folded over the run files the list loop already reads (zero extra scans): runs with a `dispatched_by` stamp count toward both counters; unstamped runs (or a null stamp) count toward `total` only. The `provenance` key is emitted only when at least one run carries the stamp — a root with no stamped runs keeps the plain `{runs,total,counts}` key set. Consumers read `provenance.dispatched_by_set` / `provenance.total`; these field names are a pinned output contract.

## Profile-routed children

`profile` on an agent node runs that node **as** a named local profile — delegation, not isolation: the child carries the target's instructions, memory, `.env`, and tools, running as the same OS user. Before launching, the target owner writes `<target_profile_home>/workflow_team.json` as `{"accept_from":["<launcher-profile-name>"]}`; the launcher name comes from the launching process's own resolved profile identity, never from a graph argument. The target must have a `config.yaml`; the default profile may launch but is never a target. Without target-owned consent, validation fails before any run write or spawn; a target deleted between validation and spawn fails with `error_class:"spawn"` (`profile gone`) rather than silently falling back to the launcher.

## Runs root, identity, and the trust boundary

Runs live under `<runs_root>`; resolution precedence, read at call time by every component (the tool entry point, runner, dashboard, liveness — one shared resolver, no restart needed): owner setting `plugins.entries.hermes-workflows.settings.runs_root` > `$WF_RUNS_ROOT` (absolute dir) > the resolved profile home's `workflows/` > `$HOME/.hermes/workflows`. `${VAR}` / `${env:VAR}` templates inside the settings value expand identically on every reader, and an unset variable makes every reader refuse the value with the same error rather than one component silently seeing a different root. Validation is fail-closed: after `expanduser` the result must be absolute, must not be the installation's `profiles/` root itself (that would mint run dirs and lane/library entries as sibling profile directories, mixing every installation's namespace into one runs root), and must not land inside another profile's home (a typo would make every other profile's runs vanish into one profile's private directory); the caller's own profile home is legal — it is the ordinary default. A malformed value is an `owner settings invalid: …` error on every action, never a silent fallback. Pointing `WF_RUNS_ROOT` at a shared directory lets runs created by a named profile survive deletion of that profile: `wait`, `status`, and the dashboard read them from anywhere.

A run's `run.json` gains identity keys only when derivable (a default-profile run with no custom root adds nothing): `dispatched_by` (launcher profile), `launch_root`, `team`, `lane_key`, `targets[]` (distinct node profiles), `graph_source` (when replaying a provenance-carrying library graph). Launcher identity ranks: the process's own resolved profile home > the owner's `settings.profile` (validated by the same name rule node `profile:` keys use, and refused if the named profile does not exist — a stamp nobody can verify is refused, not invented) > `"default"`. Environment-derived identity always wins when present; the setting only fills an identity the process could not carry (the desktop tool bridge and env-less gateways launch without a profile home). Consent gates then see the real launcher instead of `default`. Every child spawn carries the absolute run dir so its `inbox` pull resolves without guessing.

**Invariant: a launch is never invisible.** Whatever process starts a run — chat tool call, gateway, CLI, dashboard — the run lands under the one root every reader resolves, from the same ranked sources, at the same call. There is no second root the dashboard can look at that the tool does not write to; if the owner's setting is wrong the tool says so and refuses rather than quietly creating runs somewhere else.

**Trust boundary:** a shared `WF_RUNS_ROOT` — or its owner-settings equivalent, which outranks it — means same-user trust: any profile that can read the runs root can read, steer, and stop every run there. `dispatched_by`/`owner`/`source` stamps are provenance, not access control; nothing enforces them. Do not treat team fields as an ACL, and do not share a runs root across trust domains — the plugin has no isolation to offer there. `runs_root` and `profile` are deliberately owner-config vocabulary (they live in the owner's `config.yaml`), never tool arguments: a model-settable graph/run arg could pick the launcher identity or the root, which is exactly the spoof the consent gate refuses. A model that edits `config.yaml` mid-session is acting on the owner's config, not on the tool's grammar, and environment-derived identity still wins over anything it writes.

## Library provenance

`save` accepts an optional `source` (≤200 chars) and an optional `description`. When a source is supplied — or the saving profile is a named one — the library entry records `{owner, source, saved_at, source_digest}` provenance, written by the plugin's tool entry point at save time (sha256 over the canonical node definitions); a default-profile save without `source` writes exactly the pre-provenance bytes, and legacy entries list as always. `library` shows the fields only when present; `run from:<name>` copies the stamp into `run.json` as `graph_source`. Provenance is attribution, never permission: no veto, no ACL, no migration of old entries. (Open PR #84: `save` refuses a run whose `run.json` carries `include` directives — save the author form inline instead.)

## Small, parent-gated escalation recipe (no new engine feature)

Use a terminal, decision-only agent node with no automatically runnable work descendants. Its ordinary schema-defined final JSON can contain `needs_escalation: true` and a short reason (the node schema must actually permit these fields). The parent inspects that exact value and any external effects, selects an explicit model, and amends the graph with the original committed inputs plus a bounded factual handoff. Check `dry_run`'s `will_rerun` before applying. A timeout remains a failed node, not a safe auto-retry: the parent investigates and decides. Never use this on a work-product node with downstream execution; schema-valid JSON is committed as done even if its text requests escalation. This recipe adds no tool, status, automatic fallback or guarantee of side-effect rollback.
