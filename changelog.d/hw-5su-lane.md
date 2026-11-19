docs(lanes): anchor the lane-wreckage retrieval surface — bank_patch, worktree paths, corpus harvest

bd_2026-11-13-5su (E27). A lane_wreckage hold did its job — the cost was the hold,
not confusion — only because the operator already knew where the machinery lives.
The refusal row names `bank_patch` and `bank_cmd` verbatim, but no doc said where
to read that row, who creates `wip/` (nobody — mkdir it), where a timeout corpse
banks, or how the journal replay names its paths. That surface is now written down.

operator-playbook.md gains the lane-wreckage bullet naming the bank_patch retrieval
path `<run>/wip/<node>.patch` and the playbook route to the new one-page anchor,
scripts/lane-recovery.md: named shapes for the offender row
({node, lane, dirty[], bank_patch, bank_cmd}), the lane_recover report
({written, applied, unmatched, skipped, unconfirmed}), and the timeout corpus
(work/, stdout_tail.txt, manifest.json with last_written first), then the exact
five commands — read the events.jsonl row, bank via patch or the row's own
bank_cmd, replay journaled writes with scripts/lane_recover.py, harvest
nodes/<id>[.<i>].corpus/, re-drive through the boot rescan — plus the worktree
path map (work/<node>[.<i>]/, log_path/prompt_path, stash reflog). All paths
verified against wf.py _boot_lane_assert / _bank_the_corpse / child_work_dir and
scripts/lane_recover.py's shipped CLI.
