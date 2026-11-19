feat(wf): recovery-state readout, fan item-level ledger, amendment application evidence (E16/E17/E18, bd_2026-11-13-4hc)

RECOVERY-STATE READOUT. No command rendered "what effects are durable,
which record is torn, what re-drive order is idempotent" on a post-kill
run — every SIGKILL/torn-import family scored 0 on applied_set_exact.
`wf.py recover <run_id>` answers it in one JSON line, computed from the
side-effect journal + node records + graph.json alone (never memory):
{applied[], torn[], unprovable[], safe_redrive[]}. applied = journal rows
valid under the current graph; torn = physical lines that never fully
landed (UNPROVEN, not absent, named by line/bytes/head); unprovable =
parsed rows orphaned by node-gone / amended-efp / not-a-row; safe_redrive
= unfinished nodes in after-edge topological order with per-node
reconcile/fresh modes against the durable effects.

FAN ITEM-LEVEL LEDGER. Deferred item addressing became observed demand:
#61 tree quarantine now writes durable rows to
<run>/quarantine/<node>[.<index>].jsonl ({ts,node,index,stage,pids,proof})
at every kill/reap/fail-closed instant, and every finalized item record
carries `disposition` (the ONE total table), a `quarantine` target with a
path that EXISTS whenever the (node, item) was quarantined, and
`receipt_vs_parent` {claim_status, output_matches, problem, at} — each
item's receipt adjudicated against the parent aggregate claim, per
certification pass, idempotently.

AMENDMENT APPLICATION EVIDENCE. The runtime docs promised
runs/<run>/nodes/<name>/amendment-applied.json + logs/boundary.log and
the plugin wrote none of that. The runner now ships both AT APPLICATION
TIME (boot and wave boundary), keyed by the amends.jsonl revision, each
naming the from_efp/to_efp movement and the graph.amended/graph.reloaded
pair; an unparseable amends line lands an amendment.row_torn boundary row
instead of silence. Evidence writes are idempotent per revision and
fail-open: an evidence bug can suppress evidence, never an application.
