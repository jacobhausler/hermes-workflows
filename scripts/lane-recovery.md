# Lane recovery: the wreckage is one lookup away

One page for the shape `error_class:"lane_wreckage"` — a (re-)drive refused at
admission because a node's declared `repo:` lane still carries the dead attempt's
uncommitted TRACKED changes (`git status --porcelain --untracked-files=no`). The
refusal lands before any spawn; nothing is lost, nothing is auto-committed, and the
verdict row carries its own retrieval instructions.

Named data shapes you will read:

- Offender row (`runner_exit.json` detail / `offenders` on the `run.lane_wreckage`
  event in `events.jsonl`):
  `{node, lane, dirty: ["<porcelain lines, max 20>"], bank_patch, bank_cmd}` —
  `lane` is the resolved worktree path (relative `repo:` values resolve against the
  run dir), `bank_patch` is the exact string `<run>/wip/<node>.patch`, `bank_cmd`
  is the exact command `git -C <lane> stash push -m redrive:<run>:<node>`.
- Journal-replay report (`<out>/lane_recover_report.json`):
  `{written, applied, unmatched, skipped, unconfirmed}` + one `<out>/<relpath>` per
  journaled file.
- Timeout corpus (`<run>/nodes/<id>[.<i>].corpus/`):
  `work/` (the corpse's work dir), `stdout_tail.txt`, `manifest.json`
  (file inventory, `last_written` first).

## The five commands

`<run>` is the run dir (`runs_root`/`<run-id>`, also on the `run.failed` wake as
`run_dir`); `<lane>` and `<node>` come from the offender row.

1. Read the verdict — the refusal names every dirty file and both banking paths:

   ```bash
   jq -s 'map(select(.event=="run.lane_wreckage") | .offenders)[]' "<run>/events.jsonl"   # runner_exit.json's reason/detail repeat it (detail capped at 300 chars)
   ```

2. Bank the wreckage to the `bank_patch` retrieval path (the runner never creates
   `wip/` — make it, then save exactly the path the row names):

   ```bash
   mkdir -p "<run>/wip" && git -C "<lane>" diff HEAD > "<run>/wip/<node>.patch" && git -C "<lane>" checkout -- .
   ```

   Or take the row's own `bank_cmd`, which banks and cleans in one step:
   `git -C "<lane>" stash push -m redrive:<run>:<node>`.

3. If the tree is gone entirely (killed before it wrote anything durable), rebuild
   it from the journaled tool calls — read-only over the profile `state.db`; drop
   `--out` for the triage call-list first:

   ```bash
   python3 scripts/lane_recover.py --run <run-id> --node <node> --out "<run>/wip/<node>-restore"
   ```

   (`--profile <name> --skey <skey>` works without a run dir; the skey is
   `nodes/<node>[.<i>].json` -> `skey`. Exit 3 = the lane journaled no writes.)

4. Harvest what a timed-out attempt already banked — timeout corpses land in the
   run dir's corpus, not the lane; read `manifest.json` before re-running anything
   so the resume prompt names what exists and forbids its redo:

   ```bash
   ls "<run>/nodes/<node>.corpus/" && jq '.last_written' "<run>/nodes/<node>.corpus/manifest.json"
   ```

   (Fan-out carriers bank per item: `nodes/<node>.<i>.corpus/`.)

5. Re-drive — the boot scan re-runs at admission and admits once the lane is
   tracked-clean:

   ```bash
   # workflow {action: "wait", run_id: "<run-id>"}   — or amend first if the node's
   # definition itself must change (efp law: operations.md; annotate needs no re-drive)
   ```

## Worktree paths

- Lane worktrees are the run's own (one runner per worktree; `lane_key` per lane
  refuses the double launch — operator-playbook.md).
- Per-node durable work: `<run>/work/<node>[.<i>]/` (every child starts there; what
  `resume_hint` inventories).
- Spawn capture: `log_path` / `prompt_path` on the node record (`node_facts`).
- Banked wreckage lands in lane-owned commits, `<run>/wip/`, or the stash reflog
  (`git -C <lane> stash list`) — cold-before-delete: read the bank before pruning
  the run dir.
