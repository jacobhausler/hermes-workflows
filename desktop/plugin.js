/**
 * hermes-workflows — desktop half of the unified plugin package.
 * Plain ESM, loaded uncompiled: UI is jsx()/jsxs() calls, never JSX syntax.
 * Imports only @hermes/plugin-sdk, react (hooks) and react/jsx-runtime.
 */

import {
  atom,
  Badge,
  Button,
  cn,
  Codicon,
  COMPOSER_AREAS,
  EmptyState,
  host,
  PANES_AREA,
  PanelListRow,
  PanelPill,
  PanelSectionLabel,
  ROUTES_AREA,
  ScrollArea,
  StatusDot,
  TRANSCRIPT_DIRECTIVE_AREA,
  useMutation,
  useQuery,
  useQueryClient,
  useValue
} from '@hermes/plugin-sdk'
import { useEffect, useId, useRef, useState } from 'react'
import { Fragment, jsx, jsxs } from 'react/jsx-runtime'

const ID = 'hermes-workflows'
const Q = ['hermes-workflows']
const ID_OK = /^[\w.-]+$/
const TERMINAL = new Set(['done', 'failed', 'stopped'])

async function api(path, opts) {
  const res = await ctxRest(path, opts)
  // The backend answers semantic errors as plain objects; reject them so callers
  // hit onError instead of treating an {ok:false} as success.
  if (res && typeof res === 'object' && (res.ok === false || res.error)) {
    throw new Error(res.error?.message || String(res.error || 'request failed'))
  }
  return res
}
let ctxRest = async () => { throw new Error('workflows backend unavailable') }

// Plugin-local selection state (write .set() in handlers, useValue in leaves).
// Exported for behavior tests (gate view-action identity — test_composer_owner.mjs).
export const $selRun = atom(null)
export const $selNode = atom(null)

// -- helpers -------------------------------------------------------------------

// Compact div builder: one child -> jsx, many -> jsxs.
const box = (className, ...kids) =>
  kids.length === 1 ? jsx('div', { className, children: kids[0] }) : jsxs('div', { className, children: kids })

const label = text => jsx('div', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: text })

function Labeled({ name, text, pre }) {
  if (!text) return null
  return box('', label(name), box('text-xs text-(--ui-text-secondary)' + (pre ? ' whitespace-pre-wrap' : ''), text))
}

function parseTime(v) {
  if (v == null) return 0
  if (typeof v === 'number') return v < 1e12 ? v * 1000 : v
  const t = Date.parse(v)
  return Number.isNaN(t) ? 0 : t
}

function ago(v) {
  const t = parseTime(v)
  if (!t) return ''
  const s = Math.max(0, (Date.now() - t) / 1000)
  if (s < 45) return 'now'
  if (s < 3600) return `${Math.round(s / 60)}m`
  return s < 86400 ? `${Math.round(s / 3600)}h` : `${Math.round(s / 86400)}d`
}

function fmtDur(ms) {
  if (!(ms > 0)) return ''
  const s = Math.round(ms / 1000)
  if (s < 60) return s < 1 ? '<1s' : `${s}s`
  const m = Math.floor(s / 60)
  return m < 60 ? (s % 60 ? `${m}m ${s % 60}s` : `${m}m`) : `${Math.floor(m / 60)}h ${m % 60}m`
}

function fmtOutput(o) {
  if (o == null) return ''
  if (typeof o === 'string') return o
  try {
    return JSON.stringify(o, null, 2)
  } catch {
    return String(o)
  }
}

const isBusy = status => status === 'running'
const runningCount = data => data?.counts?.running ?? (data?.runs || []).filter(r => isBusy(r.status)).length
// WF-03 (QA 2026-10-27): an absent status reads an em-dash, never the raw
// sentinel word — 'unknown' on the screen reads like a broken sensor.
// Ship 2.0 (FINAL lifecycle table): the table IS the public-label law. Every
// raw status keeps its exact word (cancelled stays its own neutral word, never
// folded into failed); only successful done is relabelled to Finished.
const statusLabel = s => !s ? '—' : s === 'done' ? 'Finished' : s
// Census: an absent count keeps the '?' sentinel, never a fabricated 0 —
// painting absence as zero is the bug class (FINAL sparse specimen).
const nodesCount = r => `${countCell(r?.nodes_done, '?')}/${countCell(r?.nodes_total, '?')} terminal`

// Fan-out expansion state: which fan-out node is fanned open, and which item is
// picked. Keyed per run so cards for different runs never share an open state.
const $fanOpen = atom(null) // { runId, nodeId }
const $fanItem = atom(null) // { runId, nodeId, index }
const $fanExpanded = atom(null) // { runId, nodeId } — page-level stacked-card expand

/** One item record per fan-out child, from the best source available:
 *  v0.7.2+ committed `output.all_results` (status/error/raw per index) → older
 *  per-item records in `output.items` → live progress from `item.finished`
 *  events (index/status/error/tail) → pending placeholders from the graph def.
 *  Labels come from the item's own goal/host/name/id or the rendered index. */
function fanItems(def, st, events) {
  const fo = def.fanout
  if (!fo) return null
  const out = st?.output
  const defItems = Array.isArray(fo.items) ? fo.items : null
  let recs = null
  if (out && Array.isArray(out.all_results)) recs = out.all_results
  else if (out && Array.isArray(out.items) && out.items.some(i => i && typeof i === 'object' && i.status)) recs = out.items
  const byIdx = new Map()
  const startedIdx = new Set()
  for (const e of events || []) {
    if (e.node !== def.id || typeof e.index !== 'number') continue
    if (e.event === 'item.finished') byIdx.set(e.index, e)
    else if (e.event === 'item.started') { startedIdx.add(e.index); byIdx.delete(e.index) }
  }
  const n = recs ? recs.length : defItems ? defItems.length : byIdx.size ? Math.max(...byIdx.keys()) + 1 : 0
  const nodeLive = st?.status === 'running'
  // v0.7.3 runners emit item.started: an unstarted item on a running node is PENDING (queued
  // behind the concurrency cap), not running. Older runs (no item.started at all) keep the
  // old "running node ⇒ running items" guess.
  const hasStarts = startedIdx.size > 0
  const im = st?.item_metrics
  const verified = im != null && typeof im === 'object'
  // pre-0.7.2 done node: bare merged outputs, no per-item records => every item done
  const legacyDone = !recs && st?.status === 'done' && out && Array.isArray(out.items) && !out.failed_items
  const rows = []
  for (let i = 0; i < n; i++) {
    const rec = recs ? recs[i] : null
    const ev = byIdx.get(i)
    const item = rec?.item ?? (defItems ? defItems[i] : undefined)
    const metrics = im?.[i] || null
    const ec0 = rec?.error_class || ev?.error_class || null
    // est-zmpx8 (the #584 peer-review residual): the spent-cap refusal stamp is a
    // record fact like error_class — read it verbatim where the source carries it,
    // never invent one where it does not (AGENTS rule 8).
    const rf0 = rec?.refusal || ev?.refusal || null
    const rawStatus = rec?.status || (verified
      ? (nodeLive && metrics?.live > 0 ? 'running' : ev?.status || 'pending')
      : ev?.status || (legacyDone ? 'done' : nodeLive ? (hasStarts ? (startedIdx.has(i) ? 'running' : 'pending') : 'running') : 'pending'))
    // WF-02 (QA 2026-10-27): cancelled is never a failure (the #7 law — a stop
    // re-drives cancelled work). A quorum loser / stopped straggler is recorded
    // failed+error_class=cancelled; the panel renders it as its own neutral
    // terminal word, never as a red 'failed'.
    const status = rawStatus === 'failed' && ec0 === 'cancelled' ? 'cancelled' : rawStatus
    const goal = item && typeof item === 'object' && typeof item.goal === 'string' ? item.goal : fo.goal ? renderGoal(fo.goal, item, i) : ''
    rows.push({
      index: i, status, errorClass: ec0, refusal: rf0, item, goal,
      // RC ch4 (ui2 FINAL): projection provenance — a row is a COMMITTED child
      // record (all_results / per-item records), not a live-event guess. Only
      // recorded rows project into the graph; live rows stay chips.
      recorded: !!rec,
      label: itemLabel(item, i),
      output: rec && rec.status === 'done' ? rec.output : (recs == null && out && Array.isArray(out.items) && st?.status === 'done' ? out.items[i] : undefined),
      error: rec?.error || ev?.error || null,
      tail: ev?.tail || null, // O2: record `raw` is gone; the log route tails the truth
      ms: rec?.ms ?? ev?.ms,
      metrics
    })
  }
  return rows
}

function itemLabel(item, i) {
  if (item == null) return `#${i}`
  if (typeof item !== 'object') return String(item).slice(0, 24)
  for (const k of ['label', 'name', 'host', 'id', 'title']) if (typeof item[k] === 'string' && item[k]) return item[k].slice(0, 24)
  if (typeof item.goal === 'string' && item.goal) return item.goal.slice(0, 24)
  return `#${i}`
}

function renderGoal(tmpl, item, i) {
  return String(tmpl).replace(/\{(\w+)\}/g, (m, k) => {
    if (k === 'index') return String(i)
    if (k === 'item') return typeof item === 'object' ? JSON.stringify(item) : String(item ?? '')
    return item && typeof item === 'object' && k in item ? String(item[k]) : m
  })
}

// WF-02 (QA 2026-10-27): cancelled joins the terminal tally as its OWN neutral
// bucket — never folded into failed. The key rides the counts ONLY when
// non-zero (the ratified no-cancelled fanCounts shape stays byte-identical for
// every contract pin that deep-equals it).
// RC ch4 (MF1 law): 'partial' joins the same way — its OWN bucket, terminal
// (the child finished) yet NEVER counted as a success. The exact ended census
// is the one fraction the surface may print; a raw child PARTIAL is spelled
// out by the bucket suffix, not smoothed into the parent's verdict.
const fanCounts = rows => {
  const counts = { total: rows.length, done: 0, failed: 0, running: 0, skipped: 0, stopped: 0, pending: 0, terminal: 0 }
  for (const row of rows) {
    const status = row.status
    if (status === 'done' || status === 'failed' || status === 'skipped' || status === 'stopped' || status === 'cancelled' || status === 'partial') {
      counts[status] = (counts[status] || 0) + 1
      counts.terminal++
    } else if (status === 'running' || status === 'pending') {
      counts[status]++
    }
  }
  return counts
}

const fanSummary = c => `${c.terminal}/${c.total} terminal${c.skipped ? ` ·${c.skipped} skipped` : ''}${c.stopped ? ` ·${c.stopped} stopped` : ''}${c.cancelled ? ` ·${c.cancelled} cancelled` : ''}${c.partial ? ` ·${c.partial} partial` : ''}${c.running ? ` ·${c.running}▶` : ''}${c.failed ? `, ${c.failed} failed` : ''}`

// RC ch4 (threshold ladder): the quorum progress model — pure, exported, no
// DOM. `results` counts COMMITTED DONE results (a cancelled straggler or a
// partial harvest is census, not a result); `threshold` is the declared quorum,
// else the engine's implicit majority over a KNOWN item count — and stays null
// (unknown) until the item count exists. `acked` is a separate static state,
// never a numerator tweak: the fraction reads the same before and after.
// Copy law: "2/3 results" / "Enough results to continue" — never "quorum".
export function fanThreshold(def, rows) {
  const c = fanCounts(rows || [])
  const defN = Array.isArray(def?.fanout?.items) ? def.fanout.items.length : null
  const total = c.total || defN || null
  const declared = def?.fanout && Number.isFinite(def.fanout.quorum) && def.fanout.quorum > 0 ? def.fanout.quorum : null
  const threshold = declared != null ? declared : (total ? Math.floor(total / 2) + 1 : null)
  return { total, results: c.done, threshold, acked: threshold != null && c.done >= threshold }
}

// RC ch4 (same-run identities): the fan open/pick guards as ONE law, so two
// runs carrying the same node id can never share an expansion. Keyed atoms
// ({runId, nodeId[, index]}); the selectors refuse a cross-run match.
export function fanOpenFor(detail, fanOpen) {
  if (!detail || !fanOpen || fanOpen.runId !== detail.id) return null
  return (detail.graph?.nodes || []).find(n => n.id === fanOpen.nodeId && n.fanout) || null
}

export function fanPickedRow(detail, openDef, fanItem, rows) {
  if (!detail || !openDef || !fanItem) return null
  if (fanItem.runId !== detail.id || fanItem.nodeId !== openDef.id) return null
  return (rows || []).find(r => r.index === fanItem.index) || null
}

// RC ch4 (child projection): fan-out child RECORDS project into the graph as
// their own node identities (Council law: 10 identities, 14 projected
// dependencies from 6 committed child records). Pure + exported so the unit
// test pins the topology arithmetic without a DOM.
//   def.id -> def.id.i (after: [def.id]) for every RECORDED row
//   every dependent's after: [.., def.id, ..] rewrites to the child identities
//   the projected parent keeps its own state (the fanout aggregate); each
//   child pill/card carries its RAW row status — never borrowed from the
//   parent's verdict (MF1).
// statesByNode maps parent nodeId -> rows (already through fanItems).
export function fanProjection(detail, statesByNode) {
  const graph = detail?.graph?.nodes || []
  const states = { ...(detail?.nodes || {}) }
  const rowsFor = id => (statesByNode && (statesByNode.get?.(id) ?? statesByNode[id])) || null
  let projected = false
  let nodes = graph.map(n => ({ ...n }))
  const childNodes = []
  for (const n of nodes) {
    const rows = n.fanout ? rowsFor(n.id) : null
    const kids = (rows || []).filter(r => r.recorded)
    if (!kids.length) continue
    projected = true
    for (const r of kids) {
      childNodes.push({ id: `${n.id}.${r.index}`, after: [n.id], _fanChild: { parent: n.id, row: r } })
      states[`${n.id}.${r.index}`] = { status: r.status }
    }
  }
  if (!projected) return { nodes: graph, states: detail?.nodes || {}, childRows: new Map() }
  const parentIds = new Set(childNodes.map(c => c._fanChild.parent))
  nodes = nodes.map(n => ({
    ...n,
    after: n.after?.some(a => parentIds.has(a))
      ? [...new Set(n.after.flatMap(a => parentIds.has(a) ? graph.some(g => g.id === a) ? childNodes.filter(c => c._fanChild.parent === a).map(c => c.id) : [a] : [a]))]
      : n.after
  }))
  return { nodes: [...nodes, ...childNodes], states, childRows: statesByNode }
}

// ---- vitals: dense spend + liveness ----------------------------------------------
// Backend joins each child's state.db sessions row (title = wf:<run>:<node>[:<i>]:<efp8>)
// into node.metrics / node.item_metrics / run.metrics. Liveness is deterministic: while a
// child cooks, api_calls/tool_calls rise and last_activity moves; flat + old = stalling.
//
// -- shared lifecycle + numeric view model (ship 2.0, ui2 FINAL lifecycle table) --
// The public-label and number laws live in this ONE block so every production
// surface reads the same words and digits. Laws:
//  - Exact raw statuses: no word folds into another; cancelled keeps its own
//    neutral word and tone (the #7 law). Only successful done is relabelled, to
//    the table's Finished; an absent status stays the WF-03 em-dash.
//  - Inactivity: an activity stamp <=5 s is fresh, >5 s is quiet, and a
//    missing/invalid/future stamp is activity-unknown — stored `running` alone
//    is not proof of life: nothing pulses off it and no cell may claim 0.
//  - Counts (API/TOOL, attempts, memberships): exact safe nonnegative integers;
//    invalid, fractional or beyond-safe counts read a dash, never rounded.
//  - Token volume: two significant figures (999999 -> 1.0M, 17739101 -> 18M);
//    an actual zero stays 0; null/empty/nonfinite is a dash, never a 0.
//  - Cost (WF-09): a positive below the 4-dp render floor reads '<$0.0001',
//    never '$0.0000'; zero dollars reads COST included ONLY with recorded
//    activity; an unpriced or invalid cost shows nothing.
// BEGIN shared-view-model
const FRESH_ACTIVITY_S = 5
const ACTIVITY_WORD = {
  fresh: 'Running · fresh activity',
  quiet: 'Running · quiet, alive',
  unknown: 'Running · activity unknown'
}
const activityLaw = idle => idle == null ? 'unknown' : idle <= FRESH_ACTIVITY_S ? 'fresh' : 'quiet'
const activityLabel = idle => ACTIVITY_WORD[activityLaw(idle)]
const capLabel = s => { const w = statusLabel(s); return w.charAt(0).toUpperCase() + w.slice(1) }
// Cached directive 04: a refetch failure over last-good data never infers
// present liveness — the word names the disconnect and keeps the last-known
// status verbatim.
const staleLabel = lastKnown => `Disconnected · last known ${capLabel(lastKnown)}`
// The run-scoped public state word: activity-qualified running, the table's
// Finished, every other raw status its exact word.
const runStatusLabel = (run, stale = false) => stale ? staleLabel(run?.status)
  : run?.status === 'running' ? activityLabel(idleS(run?.metrics))
  : statusLabel(run?.status)
const countCell = (n, fallback) => Number.isSafeInteger(n) && n >= 0 ? String(n) : fallback
const exactCount = n => countCell(n, '—')
function tokenMag(n) {
  if (typeof n !== 'number' || !Number.isFinite(n) || n < 0) return '—'
  if (n < 1e3) return String(n)
  const r = Number(n.toPrecision(2))
  const [v, unit] = r >= 1e9 ? [r / 1e9, 'B'] : r >= 1e6 ? [r / 1e6, 'M'] : [r / 1e3, 'k']
  return `${v >= 10 ? v.toFixed(0) : v.toFixed(1)}${unit}`
}
// kfmt keeps its name at every token cell and now IS the 2sf law; count
// cells moved to exactCount, so a count is never abbreviated again.
const kfmt = tokenMag
// WF-09 (QA 2026-10-27): a positive estimate must never render as '$0.0000' —
// a sub-cent number floors to '<$0.0001'; zero is only reached through the
// callers' truthy guards (seat-billed routes report cost 0 → 'included', no
// dollar figure at all). An invalid/non-numeric cost is absence, not $0.
const usd = v => typeof v === 'number' && Number.isFinite(v) && v > 0
  ? (v >= 1 ? `$${v.toFixed(2)}` : v >= 0.01 ? `$${v.toFixed(3)}` : v < 0.00005 ? '<$0.0001' : `$${v.toFixed(4)}`)
  : '—'
const hasRecordedActivity = m => (m?.api_calls ?? 0) > 0 || (m?.tokens_in ?? 0) > 0 || (m?.tokens_out ?? 0) > 0
// An absent, zero-sentinel, non-numeric or FUTURE last_activity is unknown
// activity — a future stamp means the record and this clock disagree, and the
// honest read is the dash, never a fabricated fresh.
const idleS = m => {
  const la = m && m.last_activity
  if (typeof la !== 'number' || !Number.isFinite(la) || la <= 0) return null
  const s = Math.round(Date.now() / 1000 - la)
  return s >= 0 ? s : null
}
const idleCell = idle => idle != null ? `IDLE ${idle}s` : 'IDLE —'
// 0–30 s = cooking (accent), 30–90 s = watch (warning), >90 s = stalled (danger).
// Exactly 30 s is warning and exactly 90 s danger — the registered idle-tone
// scale, separate from the <=5 s freshness cutoff above.
const idleTone = s => s == null ? EDGE_TONE.pending : s < 30 ? EDGE_TONE.running : s < 90 ? EDGE_TONE.held : EDGE_TONE.failed
// END shared-view-model

/** One dense line: `1.2k▸86 · 3⚡ · 4🔧 [· $0.012]`; live adds a heartbeat `● 4s`.
 *  Ship 2.0 (FINAL lifecycle table): the heartbeat pulses on KNOWN activity —
 *  fresh (<=5 s) or quiet (>5 s) alike, glyph-only — and a running child with
 *  no valid activity stamp reads an em-dash with nothing pulsing: stored
 *  `running` alone is not proof of life. Counts are exact safe integers; token
 *  volume rides the 2sf law; zero cost reads COST included only with recorded
 *  activity (never '$0.0000' — WF-09).
 *  #133: live also carries the wall meter word — `● 4s · near-wall` — the read
 *  model's {elapsed_s, wall_s, p95_s, meter} for a running node. Absent stays
 *  absent (never invented); the words are the run_state vocabulary verbatim. */
function Vitals({ m, live, size, cost, wall }) {
  if (!m) return null
  const fs = size === 'xs' ? 10 : 11
  const sep = jsx('span', { style: { opacity: 0.45 }, children: '·' })
  const parts = []
  if (m.tokens_in != null || m.tokens_out != null) parts.push(jsx('span', { title: `${m.tokens_in ?? '—'} in ▸ ${m.tokens_out ?? '—'} out${m.cache_read ? ` (${kfmt(m.cache_read)} cached)` : ''}`, children: `${kfmt(m.tokens_in)}▸${kfmt(m.tokens_out)}` }))
  if (m.api_calls != null) parts.push(jsx('span', { title: 'api calls', children: `${exactCount(m.api_calls)}⚡` }))
  if (m.tool_calls != null) parts.push(jsx('span', { title: 'tool calls', children: `${exactCount(m.tool_calls)}🔧` }))
  if (cost) {
    if (m.cost > 0) parts.push(jsx('span', { title: 'estimated cost', children: usd(m.cost) }))
    else if (m.cost === 0 && hasRecordedActivity(m)) parts.push(jsx('span', { title: 'zero cost with recorded activity — seat-billed', children: 'COST included' }))
  }
  if (m.attempts > 1) parts.push(jsx('span', { title: 'schema/parse retry', children: `↻${exactCount(m.attempts)}` }))
  const s = live ? idleS(m) : null
  const beat = live
    ? jsxs('span', {
        title: m.last_desc ? `last: ${m.last_desc}` : 'seconds since the child last did something',
        style: { display: 'inline-flex', alignItems: 'center', gap: 3, color: idleTone(s), fontVariantNumeric: 'tabular-nums' },
        children: [
          jsx('span', { className: s != null ? 'animate-pulse' : '', style: { display: 'inline-block', width: 6, height: 6, borderRadius: 999, background: idleTone(s) } }),
          jsx('span', { children: s == null ? '—' : `${s}s` })
        ]
      })
    : null
  const kids = []
  parts.forEach((p, i) => { if (i) kids.push(sep); kids.push(p) })
  if (beat) { if (kids.length) kids.push(sep); kids.push(beat) }
  // #133: the wall meter rides right after the heartbeat, one word, tone-coded
  // against the same EDGE_TONE palette the heartbeat already uses. Only when
  // the read model published it — an absent meter renders nothing at all.
  const meter = live && wall && typeof wall.meter === 'string' ? wall.meter : null
  if (meter) {
    if (kids.length) kids.push(sep)
    const bound = wall.wall_s ?? wall.p95_s ?? null
    kids.push(jsx('span', {
      title: `elapsed ${wall.elapsed_s}s of wall ${wall.wall_s ?? '?'}s (shape p95 ${wall.p95_s ?? '?'})${bound != null ? ` — ${Math.round(100 * (wall.elapsed_s || 0) / bound)}%` : ''}`,
      style: { color: METER_TONE[meter] || 'var(--ui-text-tertiary)', fontVariantNumeric: 'tabular-nums' },
      children: meter
    }))
  }
  return jsx('span', {
    style: { display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: fs, lineHeight: 1, whiteSpace: 'nowrap', color: 'var(--ui-text-tertiary)', fontVariantNumeric: 'tabular-nums' },
    children: jsxs(Fragment, { children: kids })
  })
}

/** Ticks once a second while `on` so idle-seconds re-render between refetches. */
function useTick(on) {
  const [, set] = useState(0)
  useEffect(() => {
    if (!on) return
    const t = setInterval(() => set(v => v + 1), 1000)
    return () => clearInterval(t)
  }, [on])
}

/** Per-item peek for the transcript card's FanStrip ONLY. The page's node truth
 *  lives in NodePanel (O2); the tail pre is gone — the log route is the one tail. */
function ItemDetail({ row, compact }) {
  const pre = (name, text, tone) => text
    ? box('', label(name), jsx('pre', {
        style: { maxHeight: compact ? 160 : '35vh', color: tone || 'var(--ui-text-secondary)' },
        className: 'overflow-auto whitespace-pre-wrap break-words rounded border border-(--ui-stroke-secondary) p-2 text-[0.6875rem]',
        children: text
      }))
    : null
  // read-once: guards and derefs share this binding, a torn update can't split them
  const m = row.metrics || null
  const lastDesc = row.status === 'running' ? m?.last_desc : null
  return box(
    'flex flex-col gap-2',
    box('flex items-center gap-2 text-xs',
      jsx(Dot, { status: row.status }),
      jsx('span', { className: 'font-medium', children: `item ${row.index}` }),
      jsx('span', { className: 'text-(--ui-text-tertiary)', children: row.label }),
      jsx(Badge, { variant: 'outline', children: row.status }),
      row.ms ? jsx('span', { className: 'text-(--ui-text-tertiary)', children: fmtDur(row.ms) }) : null,
      m ? jsx(Vitals, { m, live: row.status === 'running', cost: true }) : null),
    lastDesc ? box('text-[0.6875rem] text-(--ui-text-tertiary)', `last: ${lastDesc}`) : null,
    pre('goal', row.goal),
    // WF-02: a cancelled child is not a failure — its reason line rides the
    // neutral secondary colour, never the failed red.
    pre('error', row.error, row.status === 'cancelled' ? undefined : EDGE_TONE.failed),
    pre('output', fmtOutput(row.output)),
    row.status === 'running' ? box('text-xs text-(--ui-text-tertiary)', 'child running…') : null,
    row.status === 'pending' ? box('text-xs text-(--ui-text-tertiary)', 'not started.') : null
  )
}

/** Row of clickable item chips (Dot + label). */
function ItemChips({ runId, nodeId, rows, picked, size }) {
  return jsx('span', {
    style: { display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' },
    children: rows.map(r => {
      const on = picked === r.index
      // WF-02 (QA 2026-10-27): cancelled joins the neutral skipped tone.
      const tone = r.status === 'done' ? EDGE_TONE.done : r.status === 'failed' ? EDGE_TONE.failed : r.status === 'running' ? EDGE_TONE.running : r.status === 'skipped' || r.status === 'stopped' || r.status === 'cancelled' ? EDGE_TONE.skipped : EDGE_TONE.pending
      // read-once: one binding shared by the guards and the derefs below
      const m = r.metrics || null
      const idle = m ? idleS(m) : null
      const calls = m ? m.api_calls : null
      const outTok = m ? m.tokens_out : null
      return jsxs('button', {
        type: 'button',
        title: r.error ? r.error : r.goal,
        onClick: e => { e.stopPropagation(); $fanItem.set(on ? null : { runId, nodeId, index: r.index }) },
        style: {
          display: 'inline-flex', alignItems: 'center', gap: 4, height: size === 'sm' ? 18 : 22, padding: '0 7px',
          fontSize: size === 'sm' ? 10 : 11, lineHeight: 1, whiteSpace: 'nowrap', cursor: 'pointer',
          border: `1px solid ${on ? 'var(--ui-accent)' : tone}`, borderRadius: 999,
          background: on ? 'var(--ui-bg-secondary, transparent)' : 'transparent',
          color: r.status === 'pending' || r.status === 'skipped' || r.status === 'stopped' || r.status === 'cancelled' ? 'var(--ui-text-tertiary)' : 'var(--ui-text-secondary)',
          textDecoration: r.status === 'skipped' ? 'line-through' : 'none'
        },
        children: [jsx(Dot, { status: r.status }), jsx('span', { children: r.label }),
          r.status === 'running' && m
            ? jsx('span', { style: { color: idleTone(idle), opacity: 0.9 }, children: `${countCell(calls, '?')}⚡${idle != null ? ` ${idle}s` : ''}` })
            : outTok != null ? jsx('span', { style: { opacity: 0.6 }, children: kfmt(outTok) }) : null]
      }, r.index)
    })
  })
}

// Full-census fetch (bd_2026-11-13-yjp): /runs is PAGED — one call answers the
// first 100 rows plus the WHOLE-CENSUS summary, so a single fetch silently
// stopped at page 1 while the pane's census line promised every counted run.
// This queryFn walks bounded pages into one deduped index. Laws:
//   - known total: page until covered; a short/empty page means the census
//     shrank mid-walk — stop and report loaded honestly (loaded < total
//     renders as a partial, never as a lie about the count);
//   - unknown total (legacy payload without `total`): keep walking while pages
//     stay full; the total is never fabricated;
//   - dedupe by id across pages — slices from two snapshot scans (a walk that
//     crosses a TTL boundary) may repeat a row;
//   - honours the AbortSignal BETWEEN pages: a cancelled/invalidated query
//     stops walking instead of continuing to hammer the route on a timer;
//   - hard page cap — the walk is finite even against a server whose total is
//     a lie, and the shortfall renders as a visible partial.
// Pure over an injected request fn so node behavior tests drive a fake server.
const RUNS_PAGE_SIZE = 100   // the server's own page size — no bespoke cap
const RUNS_MAX_PAGES = 30    // bounded walk: a >3000-row census shows a partial, never hangs

export function runsIndexFetcher(request) {
  return async ({ signal } = {}) => {
    const cancelled = () => signal?.aborted === true
    let first
    const index = []
    const seen = new Set()
    let offset = 0
    let pages = 0
    for (;;) {
      if (cancelled()) throw new Error('workflows census fetch cancelled')
      const page = await request(`/runs?offset=${offset}&limit=${RUNS_PAGE_SIZE}`)
      if (cancelled()) throw new Error('workflows census fetch cancelled')
      pages++
      const rows = Array.isArray(page?.runs) ? page.runs : []
      for (const r of rows)
        if (r && typeof r.id === 'string' && !seen.has(r.id)) { seen.add(r.id); index.push(r) }
      if (!first) first = page
      const total = typeof first.total === 'number' ? first.total : null
      const covered = total != null ? offset + rows.length >= total : rows.length < RUNS_PAGE_SIZE
      if (!rows.length || covered || pages >= RUNS_MAX_PAGES) break
      offset += rows.length
    }
    // The global summary (total/counts/roots) rides through UNTOUCHED from the
    // first page — it describes the whole census and stays distinct from the
    // locally loaded rows; `loaded` makes the coverage honest.
    return { ...first, runs: index, loaded: index.length }
  }
}

export function listQuery() {
  return {
    queryKey: [...Q, 'runs'],
    queryFn: runsIndexFetcher(api),
    refetchInterval: q => ((q.state.data?.runs || []).some(r => !TERMINAL.has(r.status)) ? 4000 : 30000)
  }
}

function runQuery(id, enabled = true) {
  return {
    queryKey: [...Q, 'run', id],
    queryFn: () => api(`/runs/${id}`),
    enabled: enabled && !!id && ID_OK.test(String(id)),
    refetchInterval: q => (q.state.data && !TERMINAL.has(q.state.data.status) ? 4000 : false)
  }
}

// Longest-path depth from roots, cycle-guarded.
function depthMap(nodes) {
  const byId = new Map(nodes.map(n => [n.id, n]))
  const memo = new Map()
  const depth = (id, guard) => {
    if (memo.has(id)) return memo.get(id)
    if (guard.has(id)) return 0
    guard.add(id)
    const deps = (byId.get(id)?.after || []).filter(a => byId.has(a))
    const v = deps.length ? Math.max(...deps.map(a => depth(a, guard))) + 1 : 0
    guard.delete(id)
    memo.set(id, v)
    return v
  }
  return new Map(nodes.map(n => [n.id, depth(n.id, new Set())]))
}

// Depth columns as [depth, defs] pairs ordered by depth; insertion order of
// the graph's node list is kept within a column. Shared seed of both layouts.
function columnGroups(nodes, depths) {
  const cols = new Map()
  for (const n of nodes) {
    const d = depths.get(n.id) || 0
    if (!cols.has(d)) cols.set(d, [])
    cols.get(d).push(n)
  }
  return [...cols.entries()].sort((a, b) => a[0] - b[0])
}

/** WRAP LAW (feedback #10): pack depth columns left-to-right into row bands
 *  that fit the MEASURED canvas width. A column whose right edge would pass
 *  the available width opens a NEW band below, left-anchored — never a
 *  horizontal scrollbar, never clipping at the window edge. Returns bands:
 *  arrays of [depth, defs, x] (x = left within the band, the pack's proof
 *  that every band fits). One depth lives in exactly one band, the invariant
 *  Edges/routeEdge rely on to route across wrapped coords via measured rects.
 *  A lone column wider than the canvas keeps its own band at x=0. */
function bandRows(cols, availW, widthOf, colGap) {
  const bands = []
  let row = [], x = 0
  const flush = () => { if (row.length) bands.push(row); row = [] }
  for (const [d, defs] of cols) {
    const w = Math.max(...defs.map(n => widthOf(n) || 0))
    if (row.length) {
      if (x + colGap + w > availW) { flush(); x = 0 } else x += colGap
    }
    row.push([d, defs, x])
    x += w
  }
  flush()
  return bands
}

export function Dot({ status }) {
  if (status === 'running') {
    // #48 F3 (deep review): the running branch consults the ONE table BEFORE
    // its early return — the accent colour rides an inline style read from
    // NODE_TONE.running.color at render time, so perturbing the table moves
    // this dot too (a frozen Tailwind bg-(--ui-accent) class could not).
    return jsx('span', {
      'aria-hidden': true,
      className: 'inline-block size-1.5 shrink-0 animate-pulse rounded-full',
      style: { background: (NODE_TONE.running || NODE_TONE.pending).color }
    })
  }
  // #48: the ui tone column of the ONE table is the single source (the old
  // ternary said exactly these words; extracting here makes a fork impossible).
  return jsx(StatusDot, { tone: (NODE_TONE[status] || NODE_TONE.pending).ui })
}

// -- 1. transcript directive: ::workflow{id="runid"} ---------------------------

function DirectiveCard({ id }) {
  if (!ID_OK.test(id)) {
    return jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', children: 'workflow' })
  }
  return jsx(DirectiveBody, { id })
}

// -- instance-label-first display title (l8i; owner axiom 2026-11-24: "the
// name of a WOF instance describing it is more important than the name of the
// template"). ONE resolver, every surface (in-chat pill, tray accordion row,
// fleet landing row, rail, record header): title := the last human segment of
// lane_key (after the final '/'), else the description's first clause, else
// run.name. Door-synthesized keys (wfstart.lane_key: `start-<template-slug>`,
// team-prefix optional) ARE the template re-promoted through the back door —
// a `start-` segment is machine-derived, not human, so the chain skips it.
// The template word then renders ONLY as secondary metadata (templateTag):
// a hover/detail badge on the compact surfaces; the fleet row has width and
// keeps a template COLUMN.
const TITLE_MAX = 64   // one line of room (owner): clip long clauses, never wrap

export function displayTitle(run) {
  const lane = typeof run?.lane_key === 'string' ? run.lane_key.trim() : ''
  if (lane) {
    const seg = lane.slice(lane.lastIndexOf('/') + 1).trim()
    if (seg && !seg.startsWith('start-')) return seg
  }
  const desc = typeof run?.description === 'string' ? run.description.trim() : ''
  if (desc) {
    const clause = desc.split(/[.,;\n]/)[0].trim()
    if (clause) return clause.length > TITLE_MAX ? clause.slice(0, TITLE_MAX - 1) + '…' : clause
  }
  return run?.name || run?.id || 'workflow'
}

/** The template name as secondary metadata — null when the title already IS
 *  the name (an unlabeled run never prints its own name twice), else the
 *  demoted template. */
export function templateTag(run) {
  const t = typeof run?.name === 'string' && run.name ? run.name : null
  return t && t !== displayTitle(run) ? t : null
}

// Two compact rows; absent metrics stay absent, never displayed as zero.
// WF-06 (QA 2026-10-27): the header elapsed is the RUN clock — the word rides
// the value so the same run's node-card and timeline clocks (different
// sources) can never be mistaken for it.
// WF-09: a zero cost is the seat-billed truth, not a dollar figure — never
// 'COST $0.0000'; activity at zero reads 'COST included' (SKILL.md: report
// metrics, not dollars; subscription routes report 'included').
const inlineHeader = (data, elapsed) => {
  const m = data.metrics
  const first = [displayTitle(data), runStatusLabel(data), nodesCount(data)]
  // WF-06: the pill's elapsed is the RUN clock — the word rides the value so
  // node-card and timeline child clocks can never be mistaken for it.
  if (elapsed != null) first.push(`run ${fmtDur(elapsed)}`)
  const second = []
  // l8i: the demoted template rides the SECOND (muted, small) row of the
  // expanded card — secondary metadata, never the headline word.
  const tmpl = templateTag(data)
  if (tmpl) second.push(`template ${tmpl}`)
  if (m) {
    // FINAL numeric laws: token volume is 2sf (IN/OUT), counts are exact safe
    // integers (API/TOOL) — a count is never abbreviated, never rounded.
    if (m.tokens_in != null) second.push(`IN ${tokenMag(m.tokens_in)}`)
    if (m.tokens_out != null) second.push(`OUT ${tokenMag(m.tokens_out)}`)
    if (m.api_calls != null) second.push(`API ${exactCount(m.api_calls)}`)
    if (m.tool_calls != null) second.push(`TOOL ${exactCount(m.tool_calls)}`)
    if (m.cost > 0) second.push(`COST ${usd(m.cost)}`)
    else if (m.cost === 0 && hasRecordedActivity(m)) second.push('COST included')
    // Running-with-live always answers both cells: an unknown activity stamp
    // reads IDLE —, never silence and never 0 (FINAL running-unknown row:
    // LIVE — / IDLE —).
    if (m.live > 0 && data.status === 'running') {
      second.push(`LIVE ${exactCount(m.live)}`)
      second.push(idleCell(idleS(m)))
    }
  }
  return [first, second]
}

// The collapsed-pill model, pure so node can test it without a DOM: one
// line for a transcript card, expanded in place by local useState (never
// localStorage, never tracking whether the agent emitted the card).
// stale=true is the CACHED-directive state: a refetch failure over last-good
// data reads Disconnected · last known <status> and never infers liveness.
export function pillModel(run, stale = false) {
  const start = parseTime(run?.started)
  const end = TERMINAL.has(run?.status) ? parseTime(run?.updated) : Date.now()
  const bits = [displayTitle(run), runStatusLabel(run, stale), nodesCount(run)]
  const elapsed = start && end > start ? end - start : null
  // WF-06: the pill's elapsed is the RUN clock — the word rides the value so
  // node-card and timeline child clocks can never be mistaken for it.
  if (elapsed != null) bits.push(`run ${fmtDur(elapsed)}`)
  // #48: the pill speaks the ONE tone table — its tone entry IS NODE_TONE's
  // (parity is a law; a forked palette is the bug class).
  // l8i: the demoted template rides the model as secondary metadata — the
  // collapsed line never prints it; the card surfaces it on hover/detail.
  return { collapsedLine: bits.join(' · '), expanded: false, template: templateTag(run),
           tone: NODE_TONE[run?.status] || NODE_TONE.pending }
}

function DirectiveBody({ id }) {
  const qc = useQueryClient()
  const { data, error, isFetching } = useQuery(runQuery(id))
  const fanOpen = useValue($fanOpen)
  const fanItem = useValue($fanItem)
  const [open, setOpen] = useState(false)
  // idle seconds on live chips / item vitals move between the 4 s refetches
  useTick(!!data && data.status === 'running')
  const frame = {
    display: 'inline-flex', flexDirection: 'column', gap: 6, maxWidth: '100%',
    border: '1px solid var(--ui-stroke-secondary)', borderRadius: 8, padding: '8px 10px',
    background: 'var(--ui-bg-secondary, transparent)', verticalAlign: 'top'
  }
  // data WINS over error. A refetch failure with a cached success keeps
  // showing the last good pill (slightly stale beats dead text); the error
  // branch only renders when NOTHING was ever fetched, and it is clickable —
  // retry via invalidate — never inert chrome.
  const retry = () => qc.invalidateQueries({ queryKey: [...Q, 'run', id] })
  if (!data) {
    if (error) {
      return jsx('button', {
        type: 'button', style: { ...frame, cursor: 'pointer' }, title: 'Retry',
        onClick: retry,
        children: `${isFetching ? 'workflow…' : `workflow (${id})`}`
      })
    }
    return jsx('span', { style: frame, className: 'text-xs text-(--ui-text-tertiary)', children: 'workflow…' })
  }
  const openRun = e => { if (e) e.stopPropagation(); $selRun.set(data.id); host.navigate('/workflows') }
  // Cached directive 04: data still wins over a refetch failure, but the pill
  // says Disconnected · last known — last-good is retained, present liveness
  // is never inferred from it.
  const pill = pillModel(data, !!error)
  // Collapsed (the default): one line + ▾ toggles expand in place, ↗ opens
  // /workflows explicitly. One click cannot both, so the whole-card navigate
  // onClick is gone — no role=link, the card body is inert chrome.
  if (!open) {
    return jsxs('span', {
      style: { ...frame, flexDirection: 'row', alignItems: 'center', gap: 6, cursor: 'pointer' },
      role: 'button',
      // l8i: hover is where the demoted template rides on the compact pill.
      title: pill.template ? `template ${pill.template} — Expand` : 'Expand',
      onClick: () => setOpen(true),
      children: [
        jsx(Dot, { status: data.status }),
        jsx('span', { className: 'text-xs text-(--ui-text-secondary)', children: pill.collapsedLine }),
        jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', children: '▾' }),
        jsx('button', { type: 'button', title: 'Open in Workflows', className: 'text-xs text-(--ui-text-tertiary)',
          style: { cursor: 'pointer' }, onClick: openRun, children: '↗' })
      ]
    })
  }
  const start = parseTime(data.started)
  const end = TERMINAL.has(data.status) ? parseTime(data.updated) : Date.now()
  const nodes = data.graph?.nodes || []
  // RC ch4 (same-run identities): one selector law for the fan open/pick
  // guards — a fanOpen/fanItem from ANOTHER run can never drive this card.
  const openDef = fanOpenFor(data, fanOpen)
  const rows = openDef ? fanItems(openDef, (data.nodes || {})[openDef.id], data.events) : null
  const picked = fanPickedRow(data, openDef, fanItem, rows)
  const headerRows = inlineHeader(data, start ? end - start : null)
  return jsxs('span', {
    style: frame,
    children: [
      jsxs('span', {
        style: { display: 'flex', flexDirection: 'column', gap: 2, maxWidth: '100%' },
        children: [
          jsxs('span', { style: { display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '2px 8px' },
            className: 'text-xs text-(--ui-text-secondary)',
            children: [jsx(Dot, { status: data.status }), ...headerRows[0].map((text, i) => jsx('span', {
              className: i === 0 ? 'font-medium' : 'text-(--ui-text-tertiary)', children: text
            }, i)),
            jsx('button', { type: 'button', title: 'Collapse', 'aria-label': 'Collapse',
              style: { marginLeft: 'auto', cursor: 'pointer', opacity: 0.8 }, onClick: () => setOpen(false), children: '▾' }),
            jsx('button', { type: 'button', title: 'Open in Workflows', 'aria-label': 'Open in Workflows',
              style: { cursor: 'pointer', opacity: 0.8 }, onClick: openRun, children: '↗' })] }),
          headerRows[1].length ? jsx('span', { style: { display: 'flex', flexWrap: 'wrap', gap: '2px 8px', fontSize: 10, fontVariantNumeric: 'tabular-nums' },
            className: 'text-(--ui-text-tertiary)',
            children: headerRows[1].map((text, i) => jsx('span', { children: text }, i)) }) : null
        ]
      }),
      nodes.length ? jsx(MiniGraph, { detail: data }) : null,
      rows ? jsx(FanStrip, { runId: data.id, def: openDef, rows, picked }) : null
    ]
  })
}

/** Inline fan-out expansion under the mini-DAG: item chips, then the picked
 *  item's detail. Clicks inside never bubble to the card's navigate.
 *  RC ch4: the header labels the fraction as the FANOUT AGGREGATE (MF1 fix —
 *  an aggregate badge never poses as the child's verdict) and the threshold
 *  ladder rides its own row: exact `${results}/${total} results` + threshold
 *  tick, never a tweened numerator, "quorum" never surfaces as copy. */
function FanStrip({ runId, def, rows, picked }) {
  const c = fanCounts(rows)
  const t = fanThreshold(def, rows)
  const known = t.total && t.threshold != null
  return jsxs('span', {
    onClick: e => e.stopPropagation(),
    style: { display: 'flex', flexDirection: 'column', gap: 6, cursor: 'default', borderTop: '1px solid var(--ui-stroke-secondary)', paddingTop: 6, maxWidth: 520 },
    children: [
      jsxs('span', {
        className: 'flex items-center gap-2 text-[0.6875rem] text-(--ui-text-tertiary)',
        children: [
          jsx('span', { className: 'font-medium text-(--ui-text-secondary)', children: def.id }),
          jsx('span', { children: 'fanout aggregate' }),
          jsx('span', { children: fanSummary(c) }),
          jsx('button', {
            type: 'button', 'aria-label': 'Collapse', style: { marginLeft: 'auto', cursor: 'pointer', opacity: 0.8 },
            onClick: () => { $fanOpen.set(null); $fanItem.set(null) }, children: '×'
          })
        ]
      }),
      known ? jsxs('span', {
        className: 'flex items-center gap-2 text-[0.6875rem]',
        style: { color: 'var(--ui-text-tertiary)', fontVariantNumeric: 'tabular-nums' },
        children: [
          // Threshold tick law (DESIGN): discrete fill at results/total, a
          // 2px solid currentColor tick at threshold/total. No intermediate
          // values exist between polls — the fill IS the integer count.
          jsx('span', {
            'aria-hidden': true,
            style: { position: 'relative', display: 'inline-block', width: 120, height: 4, background: 'var(--ui-stroke-secondary)', borderRadius: 2 },
            children: jsxs(Fragment, { children: [
              jsx('span', { style: { position: 'absolute', left: 0, top: 0, bottom: 0, width: `${(100 * t.results) / t.total}%`, background: 'var(--ui-accent)', borderRadius: 2 } }, 'fill'),
              jsx('span', {
                title: `threshold ${t.threshold}/${t.total}`,
                style: { position: 'absolute', left: `${(100 * t.threshold) / t.total}%`, top: -1, bottom: -1, width: 2, background: 'currentColor' }
              }, 'tick')
            ] })
          }),
          jsx('span', { children: `${t.results}/${t.total} results` }),
          t.acked ? jsx('span', { style: { color: 'var(--ui-success, var(--ui-accent))' }, children: 'Enough results to continue' }) : null,
          t.acked && t.results < t.total ? jsx('span', { children: 'Any late results will be added as they arrive.' }) : null
        ]
      }) : null,
      jsx(ItemChips, { runId, nodeId: def.id, rows, picked: picked?.index, size: 'sm' }),
      picked ? jsx(ItemDetail, { row: picked, compact: true }) : null
    ]
  })
}

// Compact DAG for the transcript card: same band-wrap layout + edge tones as
// the page, pills instead of cards. Pills are measured after mount AND every
// column is placed by bandRows, so it shares the page's no-clip no-scroll law.
// RC ch4 (shared grammar, ported ONCE): this one function serves every
// expansion mount (directive card, rail strip, tray accordion) — route
// identity, echoes and attempt ticks arrive here for all of them together.
// When this run's open fan has COMMITTED child records they project as their
// own pill identities (`node.i`) carrying their RAW status (Council law:
// ten identities, fourteen projected dependencies) — the parent pill keeps
// the fanout aggregate, never the reverse (MF1).
const CARD_W = 168
const MINI = { pillW: 84, pillH: 20, colGap: 34, rowGap: 6, pad: 4 }
export function MiniGraph({ detail }) {
  const ref = useRef(null)
  const gate = detail.gate
  const fanOpen = useValue($fanOpen)
  // Same-run identity first (fanOpenFor), then the projection over THIS run's
  // open fan only. No committed records => the graph renders unchanged.
  const openDef = fanOpenFor(detail, fanOpen)
  const openRows = openDef ? fanItems(openDef, (detail.nodes || {})[openDef.id], detail.events) : null
  const proj = openDef && openRows?.some(r => r.recorded)
    ? fanProjection(detail, { [openDef.id]: openRows })
    : { nodes: detail.graph?.nodes || [], states: detail.nodes || {} }
  const nodes = proj.nodes
  const states = proj.states
  const stateKey = nodes.map(n => `${n.id}:${states[n.id]?.status || ''}`).join('|')
  const rects = useCardRects(ref, [detail.id, stateKey, nodes.length])
  const canvasW = useCanvasWidth(ref, [detail.id, nodes.length])
  const pill = def => {
    const st = nodeState(def, states, gate)
    const isGate = def.type === 'gate'
    // #48: the pill border reads the ONE tone table (the old ternary spelled
    // exactly these EDGE_TONE picks; NODE_TONE's colour column IS EDGE_TONE).
    const tone = (NODE_TONE[st] || NODE_TONE.pending).color
    const fo = def.fanout
    const nstate = states[def.id] || null
    const out = nstate?.output
    // read-once: the guard and the interpolation below share this binding
    const apiCalls = nstate ? nstate.metrics?.api_calls : null
    const items = out && Array.isArray(out.all_results) ? out.all_results.length : out && Array.isArray(out.items) ? out.items.length : Array.isArray(fo?.items) ? fo.items.length : null
    const isOpen = !!fo && openDef?.id === def.id
    const label = jsxs('span', {
      'data-node': def.id,
      title: fo ? (isOpen ? 'Collapse items' : 'Fan out: show items') : undefined,
      onClick: fo ? e => {
        e.stopPropagation()
        $fanItem.set(null)
        $fanOpen.set(isOpen ? null : { runId: detail.id, nodeId: def.id })
      } : undefined,
      style: {
        position: 'relative', zIndex: 1, display: 'inline-flex', alignItems: 'center', gap: 5,
        height: MINI.pillH, padding: '0 8px', fontSize: 11, lineHeight: 1, whiteSpace: 'nowrap',
        border: '1px solid', borderColor: isOpen ? (NODE_TONE.running || NODE_TONE.pending).color : tone, borderRadius: isGate ? 4 : 999,
        borderStyle: isGate ? 'dashed' : 'solid',
        background: st === 'pending' || st === 'skipped' ? 'transparent' : 'var(--ui-bg-secondary, transparent)',
        color: st === 'pending' || st === 'skipped' ? 'var(--ui-text-tertiary)' : 'var(--ui-text-secondary)',
        opacity: st === 'pending' ? 0.7 : st === 'skipped' ? 0.45 : 1,
        textDecoration: st === 'skipped' ? 'line-through' : 'none',
        cursor: fo ? 'pointer' : undefined
      },
      children: [
        jsx(Dot, { status: st }),
        jsx('span', { children: def.id }),
        st === 'running' && apiCalls != null
          ? jsx('span', { title: 'api calls', style: { fontSize: 9, color: EDGE_TONE.running }, children: `${apiCalls}⚡` })
          : null,
        def.tier ? jsx('span', { style: { fontSize: 9, opacity: 0.7 }, children: def.tier }) : null,
        fo ? jsx('span', { style: { fontSize: 9, opacity: 0.8 }, children: `${isOpen ? '▾' : '×'}${items ?? '?'}` }) : null
      ]
    })
    if (!fo) return label
    // One fan-stack, not two (O4): MiniGraph's pill reuses the page canvas's
    // FanStack in pill mode — 2px ghost outlines in the pill's own tone.
    return jsx(FanStack, { count: (items ?? 1) + 1, pill: true, tone, children: label })
  }
  const cols = columnGroups(nodes, depthMap(nodes))
  // Mini canvas: measured width minus padding; pills fall back to MINI.pillW
  // until measured. Each band is its own left-anchored flex row, so a column
  // dropped by bandRows always starts below the previous band; the reserved
  // minHeight keeps the canvas height stable until pills are measured.
  const availW = canvasW ? Math.max(1, canvasW - MINI.pad * 2) : Infinity
  const bands = bandRows(cols, availW, def => rects[def.id]?.w || MINI.pillW, MINI.colGap)
  const colH = defs => Math.max(...defs.map(def => rects[def.id]?.h || MINI.pillH))
    + Math.max(0, defs.length - 1) * MINI.rowGap
  return jsxs('span', {
    ref,
    style: { position: 'relative', display: 'block', maxWidth: '100%', padding: MINI.pad },
    children: [
      jsx(Edges, { nodes, rects, states, gate }),
      ...bands.map((row, bi) =>
        jsxs('span', {
          style: { position: 'relative', display: 'flex', alignItems: 'flex-start', gap: MINI.colGap, minWidth: 0 },
          children: row.map(([d, defs]) =>
            jsx('span', {
              style: { position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: MINI.rowGap, flexShrink: 0, minHeight: colH(defs) },
              children: defs.map(def => jsx('span', { children: pill(def) }, def.id))
            }, `col-${d}`)
          )
        }, `band-${bi}`)
      )
    ]
  })
}

// -- 1b. composer session strip (composer.underside, fallback composer.top) -----
// The runs of the FOCUSED chat at its composer. Pure core (ownedRuns,
// splitRuns, railModel, pillModel) so node can test the model without a DOM;
// the O3 pane reuses ownedRuns for its "this chat" tag. Live runs render as one
// horizontal PillRail row, one pill expanding to a MiniGraph node-strip above
// the rail; terminal runs keep the fold. Fold/rail state is an in-memory
// plugin atom — never localStorage.

const $stripFold = atom(null) // focused sid while its terminal fold is expanded
// Which pill is expanded into the mini node-strip ABOVE the rail (#22 item 4):
// {sid, runId} or null. In-memory plugin atom — never persisted, so a reload
// never resurrects an expanded panel.
const $railOpen = atom(null)
// Collapsible live-run tray (#22, design contract on issue #22):
// {expanded, openRun} or null. In-memory plugin atom — never localStorage,
// so a reload never resurrects an expanded tray. EXPORTED so the contract
// test can drive the expanded state (same seam the rail tests probe via
// atom instrumentation); component bodies live beside the models below.
// (test_register_surface locks the 'session-strip' registration.)
export const $trayOpen = atom(null)
// est-z717 SETTINGS GATE: the live-run tray is OPTIONAL until the native tray
// SDK area lands (NousResearch/hermes-agent#133724). Tri-state atom:
// null = not yet answered (renders HIDDEN — default OFF), true/false = the
// answer of GET /settings (the door's owner_settings shape, plugins.entries.
// hermes-workflows.settings.tray). In-memory plugin atom — never localStorage.
// The PillRail is UNTOUCHED by this gate: it stays the always-on surface.
// When #133724 lands, default-on rides that mount (one line in register()).
export const $trayGate = atom(null)

/** Pure pill-toggle (exported so node can test the transition table without a
 *  DOM): null → open {sid, runId}; clicking the OPEN pill (same sid AND same
 *  runId) → null; anything else (other pill, or same runId under a new sid) →
 *  that pill opens fresh. SessionStrip already subscribes to $railOpen via
 *  useValue and passes `open`/`onToggle` as PROPS (repo precedent
 *  test_node_click_expand: "no atom .get, toggle from prop") — the handler
 *  closes over the render's value, so no module-global parking is needed. */
export function toggleRail(state, sid, runId) {
  return state && state.sid === sid && state.runId === runId ? null : { sid, runId }
}
// Feature-detect the focused-chat atoms: packaged apps older than the SDK
// checkout may not expose every atom (the Sep-16 build has no runtime-id atom,
// and `useValue(undefined)` dies as "reading 'get'"). A missing atom degrades
// to a permanently-null one — the strip/pane go quiet, they never red-banner.
const $null = atom(null)
const focusAtom = a => a || $null

/** Runs owned by one chat: owner.session_id === sid (the durable stored id).
 *  Cron launches carry owner.session_id '' and therefore never appear here —
 *  honest absence; they surface in the pane only. uiSid is the optional
 *  second key (owner.ui_session_id, the live runtime id stamped at spawn):
 *  it catches chats whose durable id rotated (compression) mid-run. */
export function ownedRuns(runs, sid, uiSid = '') {
  if (!sid && !uiSid) return []
  return (runs || []).filter(r =>
    (sid && r?.owner?.session_id === sid) || (uiSid && r?.owner?.ui_session_id === uiSid))
}

/** Feature-detected composer mount for the session strip (#230 item 0):
 *  tray ?? underside ?? top. COMPOSER_AREAS is an SDK const map — a key EXISTS
 *  ONLY on cores that mount that area, so a missing key reads undefined and ??
 *  falls through: exactly one mount, never two. `composer.tray` is the tray
 *  accumulation slot (subagents / background scripts / task lists — core's
 *  ComposerStatusStack, internal as of hermes-agent@8b66a51036); the upstream
 *  SDK-surface ask is filed (esc key wf230-composer-tray-area, issue #230), so
 *  the day core exposes it the strip rides the real tray with no plugin change.
 *  Today no shipped key is `tray` ⇒ underside (core >= v2026.7.30) ⇒ top. */
export function sessionStripArea(composerAreas) {
  return composerAreas?.tray ?? composerAreas?.underside ?? composerAreas?.top
}

/** Model split of one chat's runs: held first, then running by started desc,
 *  active capped at 3 with the rest as an overflow count; terminal runs fold
 *  into at most 5 lines (most recently updated first). */
export function splitRuns(runs) {
  const list = runs || []
  const live = list.filter(r => !TERMINAL.has(r.status))
  const terminal = list.filter(r => TERMINAL.has(r.status))
  const held = live.filter(r => r.status === 'held')
  const rest = live.filter(r => r.status !== 'held')
    .sort((a, b) => parseTime(b.started) - parseTime(a.started))
  const active = [...held, ...rest]
  return {
    active: active.slice(0, 3),
    overflow: Math.max(0, active.length - 3),
    terminalFold: terminal
      .sort((a, b) => parseTime(b.updated) - parseTime(a.updated))
      .slice(0, 5),
    terminalTotal: terminal.length
  }
}

/** Originator label (owner directive 2026-10-03, agent-first pane): every run
 *  row shows WHO launched it — a human explores agent runs, they don't own any.
 *  Priority: resolved profile name (owner_profile, from the read model) > raw
 *  session id > 'cron' for a cron-shaped session > the platform name >
 *  'unknown'. An absent fact is never fabricated as a name. Pure, node-testable. */
export function originLabel(owner, resolvedProfile) {
  if (resolvedProfile) return resolvedProfile
  const o = owner || {}
  if (o.session_id) return String(o.session_id).startsWith('cron_') ? 'cron' : String(o.session_id)
  if (o.platform) return String(o.platform)
  return 'unknown'
}

/** Agent-first pane model (owner directive 2026-10-03): the pane is an INDEX
 *  for a human viewer — they never launch runs, so there is no "mine" split.
 *  RUNNING on top (any owner), every other status in THE REST descending by
 *  last action (`updated`) — held/done/failed interleaved as history, never as
 *  a queue addressed to the reader ('NEEDS YOU' stays dead). No caps: a human
 *  explores every agent run like any other row. Husks (pending = runner dead +
 *  no events.jsonl) stay unrendered. Each row gains `origin` via originLabel
 *  over the census-wide session->profile map. Pure, node-testable. */
export function paneModel(runs, profilesBySession) {
  const byUpdated = (a, b) => parseTime(b.updated) - parseTime(a.updated)
  const list = (runs || []).filter(r => r && r.status !== 'pending')
    .map(r => ({
      ...r,
      origin: originLabel(r.owner,
        r.owner_profile || safeProfileLabel(profilesBySession, r.owner?.session_id))
    }))
  return {
    running: list.filter(r => r.status === 'running').sort(byUpdated),
    rest: list.filter(r => r.status !== 'running').sort(byUpdated)
  }
}

/** Own-property-only session->profile read (est-wk7l): a persisted session id
 *  that collides with an Object.prototype member (toString / constructor /
 *  __proto__) must never resolve through the prototype chain — the pane would
 *  print a native function or '[object Object]' as the agent's name. Only an
 *  OWN, typed-string entry counts; anything else reads as no-resolution and the
 *  row falls back honestly to its raw owner fields. */
export function safeProfileLabel(map, sessionId) {
  if (!map || sessionId === null || sessionId === undefined) return null
  if (!Object.prototype.hasOwnProperty.call(map, String(sessionId))) return null
  const v = map[String(sessionId)]
  return typeof v === 'string' && v ? v : null
}

// O4 (owner 2026-10-02) had RUNNING + WAITING-ON-AGENT + RECENTLY FINISHED; the
// agent-first revision (owner 2026-10-03) collapsed held into The Rest — a held
// row is history between actions, not a section nagging the reader. groupRuns
// is DELETED, paneModel is the one table (husk law rides unchanged).

// Compact progress for the rail pills: `${nodes_done}/${nodes_total}`, and
// '?' whenever either count is absent — an absent count is never fabricated
// as '?' when either count is absent — the same honest sentinel as
// nodesCount(); a known zero still reads 0 (no-fabrication law).
const pillProgress = r =>
  (r?.nodes_done != null && r?.nodes_total != null) ? `${countCell(r.nodes_done, '?')}/${countCell(r.nodes_total, '?')}` : '?'

/** Rail model over one chat's owned runs: the LIVE set folded into pills —
 *  held first, then running by started desc, capped at 3 (the same policy as
 *  splitRuns, which stays for the pane and the terminal fold). Pure, so node
 *  can test it without a DOM. */
export function railModel(ownedRunsList) {
  const live = (ownedRunsList || []).filter(r => !TERMINAL.has(r.status))
  const held = live.filter(r => r.status === 'held')
  const rest = live.filter(r => r.status !== 'held')
    .sort((a, b) => parseTime(b.started) - parseTime(a.started))
  const active = [...held, ...rest]
  return {
    pills: active.slice(0, 3).map(r => ({
      id: r.id,
      // l8i: instance label first — same resolver as the directive pill.
      label: displayTitle(r),
      status: runStatusLabel(r),
      progress: pillProgress(r),
      held: r.status === 'held',
    })),
    overflow: Math.max(0, active.length - 3)
  }
}

export function Pill({ run, sid, open, onToggle, suppressGates }) {
  // #48 F3 (deep review): the ACTUAL Pill (not just pillModel) borders itself
  // from the ONE tone table — border colour and the open ring both read the
  // run's NODE_TONE entry at render time; a table perturbation moves them.
  const tone = NODE_TONE[run?.status] || NODE_TONE.pending
  // A div, not a <button>: held pills embed GateActions whose option buttons
  // are SDK Buttons — button-in-button is invalid DOM nesting and every gate
  // click would bubble into the pill's toggle (review #28 F6). The label span
  // carries the toggle; GateActions sit beside it, not inside the clickable.
  return jsxs('div', {
    role: 'group',
    // l8i: instance label in the tooltip headline; the demoted template rides
    // behind it as the secondary fact.
    title: templateTag(run)
      ? `${displayTitle(run)} (template ${run.name}) — node strip above the rail`
      : `${displayTitle(run)} — node strip above the rail`,
    // Toggle the mini node-strip (item 4), do NOT navigate: the rail is the
    // glanceable view; the +N overflow and the terminal rows still deep-link.
    // The open state rides as a PROP (no module-global read at render — repo
    // precedent test_node_click_expand: "no atom .get, toggle from prop").
    style: {
      display: 'inline-flex', alignItems: 'center', gap: 6, maxWidth: 260,
      fontSize: '0.6875rem', padding: '2px 8px', borderRadius: 999,
      background: 'var(--ui-sidebar-surface-background, var(--card))',
      // F8 (deep review): the previous value concatenated a box-shadow into the
      // `border` shorthand — an invalid declaration the browser drops WHOLE, so
      // the open pill lost its border entirely (inverted signal, not cosmetic).
      // Ring rides on its own real property. #48 F3: both colours come from the
      // ONE tone table (border = the state's borderColor; the open ring rides
      // boxShadow as a centered color-mix of the state's accent).
      border: `1px solid ${tone.borderColor}`,
      boxShadow: open ? `inset 0 0 0 1px color-mix(in srgb, ${tone.color} 55%, transparent)` : undefined,
    },
    children: [
      jsxs('span', {
        role: 'button',
        // F7 (deep review): role=button WITHOUT tabIndex is not focusable — a
        // pill click left focus in the composer, the rail's onKeyDown never saw
        // Escape, and the advertised Esc-collapse was dead (the first reader
        // verified F6 closed but missed the regression F6 itself introduced).
        // Focusable label + keyboard activation = the a11y contract of role=button.
        tabIndex: 0,
        onClick: e => { e?.stopPropagation?.(); onToggle?.() },
        onKeyDown: e => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); onToggle?.() }
        },
        style: {
          display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer',
          overflow: 'hidden', maxWidth: 220,
        },
        children: [
          jsx(Dot, { status: run.status }),
          jsx('span', { style: { overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }, children: displayTitle(run) }),
          jsx('span', { style: { fontVariantNumeric: 'tabular-nums', opacity: 0.7 }, children: pillProgress(run) }),
        ],
      }, 'label'),
      // Gate-held pills keep GateActions (question + option buttons inline),
      // OUTSIDE the toggle span so a gate answer never bubbles into the toggle.
      // The #22 tray takes over the release surface inside SessionStrip
      // (suppressGates) so a held run never shows two release surfaces.
      run.status === 'held' && run.held_gate && !suppressGates
        ? jsx(GateActions, { runId: run.id, gate: run.held_gate, owner: run.owner || {} }, 'gate')
        : null,
    ]
  }, run.id)
}

/** One horizontal row of compact pills for the session's live runs, plus the
 *  +N overflow affordance beyond the cap. Renders nothing for an empty set —
 *  never an empty bordered box. */
export function PillRail({ runs, sid, railOpen, onPill, suppressGates }) {
  const { pills, overflow } = railModel(runs)
  if (!pills.length) return null
  const byId = Object.fromEntries((runs || []).map(r => [r.id, r]))
  return jsxs('div', {
    style: {
      display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 6,
      flexWrap: 'wrap', padding: '2px 0',
    },
    children: [
      ...pills.map(p => jsx(Pill, {
        run: byId[p.id] || { id: p.id, name: p.label, status: p.status }, sid,
        open: !!(railOpen && railOpen.sid === sid && railOpen.runId === p.id),
        suppressGates,
        onToggle: () => onPill?.(p.id),
      }, p.id)),
      overflow > 0
        ? jsx('button', {
            type: 'button',
            style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0, fontSize: '0.6875rem' },
            onClick: () => host.navigate('/workflows'),
            children: `+${overflow} more → Workflows`
          }, 'overflow')
        : null,
    ]
  })
}

/** Mini node-strip ABOVE the pills for the one expanded run (#22 item 4):
 *  the run's existing MiniGraph fed by runQuery. Its own component so the
 *  runQuery hook runs only while expanded (rendering a component conditionally
 *  is legal; hooks behind an early return would not be). */
function RailPanel({ runId }) {
  const { data } = useQuery(runQuery(runId))
  if (!data) return null
  return jsx('div', {
    style: {
      maxWidth: '100%', maxHeight: 160, overflowY: 'auto',
      border: '1px solid var(--ui-stroke-secondary)', borderRadius: 8,
      background: 'var(--ui-sidebar-surface-background, var(--card))',
      padding: '4px 6px'
    },
    children: jsx(MiniGraph, { detail: data })
  }, 'rail-panel')
}

/** ---- Live-run tray (#22, design contract on issue #22) -----------------
 *  Collapsible situational tray stacked as a sibling of the native
 *  task-list/subagents/queued-messages family directly above the chat window.
 *  The pure models (trayScoping/trayRunModel/trayShouldShow/toggleTray) live
 *  HERE because test_11_ui_imports freezes plugin.js imports at exactly the
 *  three SDK sources — the scaffold mirror in
 *  desktop/src/components/runtray.mjs is design documentation only.
 *  #230 RUNNING-ONLY LAW: rows = runs whose status ∉ TERMINAL — terminal
 *  runs LEAVE the tray (the #22 ack-away ledger and the 60 s recap were
 *  deleted with their exports); zero rows hides the tray entirely.
 *  Mount law: SessionStrip stays the mount owner; the collapsed RunTrayRow
 *  stacks as a sibling tray row (same composer registration as PillRail).
 *  SCOPING: trayScoping keys on the owner.session_id VALUE — dispatch/cron-
 *  shaped launches whose owner.session_id matches the focused chat belong in
 *  the tray (closes the auto-cards half of #22); blank-owner cron launches
 *  stay honest-absent, pane-only (the ownedRuns law). */

/** Tray scoping (pure): every run whose owner.session_id === sid, INCLUDING
 *  dispatch/cron-shaped launches (launched_by is irrelevant — the owner VALUE
 *  is the contract). A run owned by ANOTHER session, or with a blank owner,
 *  never appears: the pane is its only home (the ownedRuns law). A
 *  cron-shaped owner id ('cron_...') is the one design-carved inclusion: a
 *  schedule-launched run has no chat of its own, and the tray of the session
 *  that surfaced it is its glanceable home (the auto-cards half of #22). */
export function trayScoping(runs, sid) {
  if (!sid) return []
  return (runs || []).filter(r => {
    const o = r?.owner?.session_id
    if (!o) return false
    return o === sid || (typeof o === 'string' && o.startsWith('cron_'))
  })
}

const runStatusOf = r => (r && r.status) || 'pending'

/** ---- #230 RUNNING-ONLY LEDGER -------------------------------------------------
 *  The tray's ledger is the live set ONLY: rows = runs whose status ∉
 *  TERMINAL={done,failed,stopped}. A terminal run LEAVES the tray outright —
 *  no ack-away ledger, no 60 s recap (both superseded, deleted with their
 *  exports). Ordering is THE SAME comparator as splitRuns: held first, then
 *  the rest by started desc — asserted as trayRunModel order == splitRuns
 *  active order on one shared ledger (splitRuns caps `active` at 3; the tray
 *  lists every live run, uncapped, same comparator). Pure, node-testable. */
export function trayRunModel(runs) {
  const live = (runs || []).filter(r => r && !TERMINAL.has(runStatusOf(r)))
  const held = live.filter(r => runStatusOf(r) === 'held')
  const rest = live.filter(r => runStatusOf(r) !== 'held')
    .sort((a, b) => parseTime(b.started) - parseTime(a.started))
  return { rows: [...held, ...rest].map(r => ({ id: r.id, status: runStatusOf(r), run: r })) }
}

/** The live set as a PLAIN run array (#230 spec): the running-only ledger
 *  (status ∉ TERMINAL) in THE SAME comparator as splitRuns — held first,
 *  then the rest by started desc, uncapped. Terminal runs leave outright
 *  (no ack-away ledger, no 60 s recap window — the tray never renders one). */
export function trayLiveModel(runs) {
  return trayRunModel(runs).rows.map(r => r.run)
}

export function trayRunningLabel(runs) {
  const count = trayLiveModel(runs).length
  return { count, line: `${count} running workflows` }
}

/** Pure chevron transition (item 2): given the current glyph or the
 *  expanded flag, answer the OTHER state's glyph. ▾ collapsed, ▴ expanded. */
export function flipChevron(current) {
  if (current === '▴') return '▾'
  if (current === '▾') return '▴'
  return current ? '▴' : '▾'
}

/** Pure visibility rule: zero rows (an empty ledger, a null ledger, a bare
 *  {rows:[]} model, or a ledger of ONLY terminal runs — they all produce
 *  zero rows) hides the tray entirely: the collapsed row renders nothing.
 *  Accepts the trayRunModel model OR a plain live-set array (the
 *  trayLiveModel shape) — both are zero when nothing lives.
 *  est-z717 SETTINGS GATE (2nd arg): the tray renders ONLY under the owner's
 *  explicit opt-in — `gate === true`, the answer of GET /settings (the door's
 *  owner_setting('tray'), plugins.entries.hermes-workflows.settings.tray).
 *  Anything else — absent, null (never fetched / backend down), false, a
 *  truthy non-boolean — stays HIDDEN: default OFF while the native tray SDK
 *  area (hermes-agent#133724) is unlanded; when it lands, default-on rides
 *  that mount. (The retired #22 wall-clock parity arg is replaced here —
 *  #230 already ignored it, there is no recap window.) */
export function trayShouldShow(model, gate) {
  if (gate !== true) return false
  const rows = Array.isArray(model) ? model : ((model && model.rows) || [])
  return !!rows.length
}

/** Pure tray/accordion transition table (exported so node can drive it
 *  without a DOM): collapsed tray → open with NO single row expanded; an
 *  open tray's HEADER collapses the tray (back to the collapsed row — Esc
 *  / click-away parity); with the tray open, a row click accordion-toggles
 *  that row, clicking the open row again closes just the row. */
export function toggleTray(state, runId) {
  if (!state || !state.expanded) return { expanded: true, openRun: null }
  if (runId == null) return null
  return { expanded: true, openRun: state.openRun === runId ? null : runId }
}

/** Collapsed affordance (#230 items 1+2, design truth = the native collapsed
 *  background-task tray): ONE slim single-line row `[chevron] N running
 *  workflows` — numeral + label, muted secondary text via a CSS var, 1px
 *  low-contrast border. The #22 shape (pulse glyph, `N runs · X building ·
 *  Y held` segments, micro sparkline) is retired with its exports: a count of
 *  RUNNING workflows is the whole glance, per-band colour belongs on the
 *  expanded rows. Theme-safe: inline styles ride CSS vars only, never a
 *  forked palette. Click / Enter / Space expands (the row click also clears
 *  the accordion row via the owner's handler). `count` is ALWAYS the
 *  running-only count — terminal runs are already out of the model. */
export function RunTrayRow({ runs, count, expanded, onExpand }) {
  // #230 spec shape: pass the scoped ledger via `runs` and the row computes
  // its own count over the live set (never fabricates: empty reads 0). The
  // legacy {count} call shape stays accepted (test_run_tray precedent).
  const n = runs !== undefined ? trayRunningLabel(runs).count
    : (Number.isFinite(count) && count > 0 ? Math.trunc(count) : 0)
  // Chevron is the PURE transition fn's answer for the current state.
  const chev = flipChevron(!!expanded)
  return jsxs('div', {
    role: 'button',
    tabIndex: 0,
    title: 'Toggle the running-workflow tray',
    onClick: e => { e?.stopPropagation?.(); onExpand?.() },
    onKeyDown: e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); onExpand?.() }
    },
    style: {
      display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
      fontSize: '0.6875rem', lineHeight: '1.2', padding: '3px 8px', borderRadius: 8,
      // Slim + quiet: one low-contrast hairline, muted secondary text — the
      // row is an affordance, not an alert (CSS vars only, theme-safe).
      color: 'var(--ui-text-secondary)',
      border: '1px solid var(--ui-stroke-secondary)',
      background: 'var(--ui-sidebar-surface-background, var(--card))'
    },
    children: [
      jsx('span', {
        'aria-hidden': true,
        style: { color: 'var(--ui-text-tertiary)' },
        children: chev
      }, 'chev'),
      jsx('span', {
        style: { fontVariantNumeric: 'tabular-nums' },
        children: `${n} running workflows`
      }, 'label')
    ]
  }, 'tray-row')
}

function trayElapsed(r) {
  // Wall-clock elapsed since the run started (useTick re-renders the live
  // tray every second, so the figure ages honestly; 'updated' is a node
  // commit time, not "now" — a held run's elapsed must keep counting).
  const start = parseTime(r.started)
  return start ? fmtDur(Math.max(0, Date.now() - start)) : ''
}

const trayBarPct = r => (r?.nodes_done != null && r?.nodes_total != null && r.nodes_total > 0)
  ? `${Math.floor((r.nodes_done / r.nodes_total) * 100)}%` : '0%'

/** Per-run chip (design row anatomy). Title is the ONE l8i resolver
 *  (instance label first — lane_key's human segment, else description, else
 *  name); the demoted template rides a muted badge beside it. lane_key and
 *  token totals have NO read-model surface on rows predating the l8i read
 *  (the door's lane ledger and per-run token rollup are not exposed on
 *  /runs): the chips render ONLY when the run record carries the field — an
 *  absent fact is never fabricated (the rail's '?' law). The current-node
 *  label derives from the nodes map when present.
 *  #230: rows are RUNNING-ONLY — no finished band, no ack × (terminal runs
 *  leave the tray; there is nothing to dismiss). */
export function RunTrayRunRow({ run, open, onToggleRow, onOpenPane }) {
  const r = run || {}
  const tone = NODE_TONE[runStatusOf(r)] || NODE_TONE.pending
  const nodes = r.nodes || null
  const nodeIds = nodes ? Object.keys(nodes) : []
  const current = nodeIds.find(n => nodes[n]?.status === 'running')
    || nodeIds.find(n => nodes[n]?.status === 'held') || null
  const ti = r.tokens_in, to = r.tokens_out
  const gate = r.status === 'held' && r.held_gate ? r.held_gate : null
  // div (never <button>): GateActions carries SDK Buttons (F6 law).
  // Key 'rr-<id>' rides the ROOT div (the RunTray call-site keys the
  // component element 'rrc-<id>'): the acceptance spec locates the clickable
  // thick row by key and calls its onClick directly.
  return jsxs('div', {
    style: {
      display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.6875rem',
      padding: '3px 8px', cursor: 'pointer', borderRadius: 6,
      // Every row reads its own NODE_TONE border — the colour lives HERE,
      // not on the slim collapsed row.
      border: `1px solid ${tone.borderColor}`
    },
    onClick: e => { e?.stopPropagation?.(); onToggleRow?.(r.id) },
    children: [
      jsx('span', { style: { color: tone.color }, children: statusLabel(r.status) }, 'chip'),
      jsx('span', { style: { fontWeight: 600 }, children: displayTitle(r) }, 'name'),
      // l8i: the template word is secondary metadata — muted, after the
      // (also-secondary) lane chip; the full lane_key chip stays so a
      // team-prefixed key reads whole next to its short title segment.
      templateTag(r)
        ? jsx('span', { style: { opacity: 0.55 }, title: `template ${templateTag(r)}`, children: templateTag(r) }, 'tmpl')
        : null,
      r.lane_key ? jsx('span', { style: { opacity: 0.7 }, children: r.lane_key }, 'lane') : null,
      // Node dots are MiniGraph's visual language at row density; the x/y
      // count rides the read model's counts, '?' when absent — never 0/N.
      // The mini bar (key 'bar') beside it SPEAKS the ratio as its width.
      jsx('span', { style: { fontVariantNumeric: 'tabular-nums', opacity: 0.8 }, children: pillProgress(r) }, 'xy'),
      jsx('span', {
        'aria-hidden': true,
        style: { width: trayBarPct(r), minWidth: 24, height: 4, borderRadius: 2, background: tone.color, opacity: 0.6 }
      }, 'bar'),
      current ? jsx('span', { style: { opacity: 0.7 }, children: `→ ${current}` }, 'current') : null,
      trayElapsed(r) ? jsx('span', { style: { opacity: 0.6 }, children: trayElapsed(r) }, 'elapsed') : null,
      (ti != null || to != null)
        ? jsx('span', { title: 'tokens in ▸ out', style: { opacity: 0.7 }, children: `${kfmt(ti ?? 0)}▸${kfmt(to ?? 0)}` }, 'tokens')
        : null,
      gate
        ? jsx('div', {
            onClick: e => e?.stopPropagation?.(),
            children: jsx(GateActions, { runId: r.id, gate, owner: r.owner || {} }, 'gate')
          }, 'gate')
        : null,
      jsx('button', {
        type: 'button', title: 'Open in the Workflows pane',
        style: { cursor: 'pointer', background: 'none', border: 'none', padding: '0 2px', fontSize: '0.6875rem' },
        onClick: e => { e?.stopPropagation?.(); onOpenPane?.(r.id) },
        children: 'open ↗'
      }, 'open')
    ]
  }, `rr-${r.id}`)
}

/** Accordion body: the SHARED MiniGraph (#28 visual language, same
 *  runQuery-fed pattern as RailPanel) for the one opened row only. Its own
 *  component so the runQuery hook runs only while a row is open. */
function TrayPanel({ runId }) {
  const { data } = useQuery(runQuery(runId))
  if (!data) return null
  return jsx('div', {
    style: {
      maxWidth: '100%', maxHeight: 160, overflowY: 'auto',
      border: '1px solid var(--ui-stroke-secondary)', borderRadius: 8,
      background: 'var(--ui-sidebar-surface-background, var(--card))',
      padding: '4px 6px'
    },
    children: jsx(MiniGraph, { detail: data })
  }, 'tray-panel')
}

/** The tray family root — collapsed RunTrayRow + drop-down RunTrayRunRow
 *  list (max ~40% viewport, internal scroll). #230 RUNNING-ONLY: the ledger
 *  is trayRunModel (status ∉ TERMINAL), so zero live rows renders NOTHING
 *  (terminal-only ledgers included — no recap linger, no ack ledger). Hooks
 *  run UNCONDITIONALLY (the parent SessionStrip owns the hook order; this
 *  component's hooks never sit behind a return). The collapse affordances
 *  ride SessionStrip's wiring (Esc onKeyDown, click-away via trayRef); row
 *  handlers stopPropagation so tray clicks never look like click-away. */
export function RunTray({ runs, sid, trayOpen, trayRef, onToggleHeader, onToggleRow, onOpenPane, trayEnabled }) {
  // sid blank = the mount owner pre-scoped under the focus-degraded law
  // (SessionStrip): trust the given live set (running-only still applies).
  const scoped = sid
    ? trayScoping(runs, sid)
    : (runs || []).filter(r => r && !TERMINAL.has(runStatusOf(r)))
  const model = trayRunModel(scoped)
  // est-z717: the settings gate rides as a PROP from the mount owner (the
  // $trayGate atom value resolved by SessionStrip via useValue — F2 law,
  // never an atom .get inside a component). Default OFF: only literal true
  // shows the tray; the PillRail below is never gated.
  const show = trayShouldShow(model, trayEnabled)
  useTick(show)
  if (!show) return null
  // The accordion only ever renders while the TRAY itself is expanded — a
  // stale openRun from a collapsed tray never leaks a MiniGraph into the
  // collapsed state.
  const openRun = trayOpen && trayOpen.expanded && trayOpen.openRun ? trayOpen.openRun : null
  return jsxs('div', {
    ref: trayRef,
    style: { display: 'flex', flexDirection: 'column', gap: 2 },
    children: [
      jsx(RunTrayRow, {
        runs: scoped,
        expanded: !!(trayOpen && trayOpen.expanded),
        onExpand: () => onToggleHeader?.()
      }, 'row'),
      trayOpen && trayOpen.expanded
        ? jsx(ScrollArea, {
            className: 'min-h-0',
            children: jsxs('div', {
              style: { display: 'flex', flexDirection: 'column', gap: 2, maxHeight: '40vh', overflowY: 'auto' },
              children: model.rows.map(r => [
                jsx(RunTrayRunRow, {
                  run: r.run, open: openRun === r.id,
                  onToggleRow, onOpenPane
                }, `rrc-${r.id}`),
                openRun === r.id ? jsx(TrayPanel, { runId: r.id }, `tp-${r.id}`) : null
              ])
            })
          }, 'drop')
        : null
    ]
  }, 'run-tray')
}

export function SessionStrip() {
  // KEY PAIRING (measured 2026-09-26 against this desktop): run.json.owner.session_id
  // carries the GATEWAY runtime id (`20260923_143041_27e8d2` — state.db sessions.id),
  // owner.ui_session_id carries the DESKTOP stored id (`3184ce5e`). The SDK names them
  // inversely to intuition: host.state.focusedSessionId is $focusedRuntimeId (the runtime
  // id), host.state.focusedStoredSessionId is the desktop token — the SDK exposes both
  // ONLY under host.state (sdk/index.ts:665-697); reading them at the top level is what
  // made the strip and the pane's "this chat" pill render nothing forever (#23). Pair
  // each owner key with its SAME-SHAPE host key; a swapped pair silently renders nothing,
  // which no unit test can see.
  const runtimeSid = useValue(focusAtom(host?.state?.focusedSessionId))
  const storedSid = useValue(focusAtom(host?.state?.focusedStoredSessionId))
  const { data } = useQuery(listQuery())
  const foldOpen = useValue($stripFold)
  const railOpen = useValue($railOpen)
  const trayState = useValue($trayOpen)
  const owned0 = ownedRuns(data?.runs || [], runtimeSid || '', storedSid || '')
  // #230 focus-degradation law: the tray accumulates by the run's OWN
  // ownership stamp. On packaged apps / SDK shapes where neither focused-chat
  // atom answers (both read null/blank) an owned live run would render
  // nothing forever — fall back to the first LIVE run's own
  // owner.session_id so the pictured density still ships. Honest absence is
  // preserved: a blank ledger, an all-terminal ledger, or blank-owner
  // (cron) runs still derive nothing and the strip stays hidden.
  const degradedSid = runtimeSid || storedSid ? ''
    : ((data?.runs || []).find(r => r && !TERMINAL.has(runStatusOf(r)) && r?.owner?.session_id)
        ?.owner?.session_id || '')
  const owned = (owned0.length || !degradedSid)
    ? owned0
    : ownedRuns(data?.runs || [], degradedSid, '')
  const pairKey = runtimeSid || storedSid || degradedSid
  const expanded = railOpen && railOpen.sid === pairKey ? railOpen.runId : null
  const trayExpanded = !!(trayState && trayState.expanded)
  const railRef = useRef(null)
  const trayRef = useRef(null)
  // est-z717 settings gate (in-memory atom, hook order unconditional): null =
  // unanswered => HIDDEN (default OFF); register()'s bootstrap fills it from
  // GET /settings. PillRail stays mounted regardless (always-on surface).
  const trayGate = useValue($trayGate)
  // Hooks run UNCONDITIONALLY (fixed order across renders); the bodies guard
  // themselves. Switching focused chat collapses the expanded panel.
  useEffect(() => { $railOpen.set(null) }, [pairKey])
  // Switching chat likewise collapses the tray to hidden state (in-memory
  // atom law: a session switch never resurrects an expanded tray).
  useEffect(() => { $trayOpen.set(null) }, [pairKey])
  // Click-away collapse (item 4 + #22 tray), armed while EITHER the rail
  // panel or the tray is expanded. ONE window-level listener (the plugin's
  // listener budget is 1 — test_tab_polish_48); clicks landing inside the
  // open surface are excluded by its contains check (the tray's own row
  // handlers additionally stopPropagation, so tray clicks never look like
  // click-away).
  useEffect(() => {
    if (!expanded && !trayExpanded) return
    const onDocClick = e => {
      if (expanded && railRef.current && railRef.current.contains(e.target)) return
      if (trayExpanded && trayRef.current && trayRef.current.contains(e.target)) return
      if (expanded) $railOpen.set(null)
      if (trayExpanded) $trayOpen.set(null)
    }
    window.addEventListener('click', onDocClick)
    return () => window.removeEventListener('click', onDocClick)
  }, [expanded, trayExpanded])
  if (!pairKey || !owned.length) return null
  const { active, terminalFold, terminalTotal } = splitRuns(owned)
  const openRun = id => { $selRun.set(id); host.navigate('/workflows') }
  const folded = foldOpen !== pairKey
  return jsxs('div', {
    ref: railRef,
    className: 'flex flex-col gap-0.5 border-b border-(--ui-stroke-secondary) px-3 py-1',
    // Esc collapse (item 4): scoped to the rail via onKeyDown — the ⌘K law
    // forbids global keydown listeners (test_fanout_expand). The pill label is
    // tabIndex:0 (F7), so a pill click/Tab moves focus into the strip and
    // Escape lands on this handler. Nothing else intercepts keys; ⌘K stays
    // app-owned. The tray collapses FIRST (Esc collapses to collapsed-row
    // state); with the tray already collapsed, Esc collapses the rail panel.
    onKeyDown: e => { if (e.key === 'Escape') { if (trayExpanded) $trayOpen.set(null); else if (expanded) $railOpen.set(null) } },
    children: [
      // Expanded panel sits ABOVE the pills: the strip stacks bottom-anchored
      // (composer.underside grows upward over the thread).
      expanded ? jsx(RailPanel, { runId: expanded }, expanded) : null,
      // Live set: one horizontal pill rail. Pass the UNCAPPED owned set —
      // railModel filters TERMINAL and caps at 3 itself, so the +N overflow
      // stays visible (passing splitRuns' capped `active` pinned overflow to 0
      // and silently lost the affordance — review #28 F1).
      // #230 running-only tray: the collapsed RunTrayRow is the slim
      // '[chevron] N running workflows' row stacking as the SIBLING tray row
      // above the chat window (same composer registration, native tray family
      // — task-list/subagents/queued-messages). The tray takes over the
      // live-run glance + gate-release surface from PillRail, so the rail
      // renders below it WITHOUT duplicating GateActions (suppressGates — one
      // release surface per held run; test_run_tray locks exactly one
      // GateActions in the strip). Handlers close over this render's
      // trayState (F2 law: no atom .get in handlers, open state rides props).
      jsx(RunTray, {
        runs: owned, sid: pairKey, trayOpen: trayState, trayRef, trayEnabled: trayGate,
        onToggleHeader: () => $trayOpen.set(trayState && trayState.expanded ? null : toggleTray(trayState, null)),
        onToggleRow: id => $trayOpen.set(toggleTray(trayState, id)),
        onOpenPane: openRun
      }, 'run-tray'),
      jsx(PillRail, {
        // The rail yields its gate controls ONLY while the tray actually
        // renders them (enabled + expanded with live rows); disabled,
        // unanswered settings, or a collapsed tray keep the rail release.
        runs: owned, sid: pairKey, railOpen,
        suppressGates: trayExpanded && trayShouldShow(trayRunModel(trayScoping(owned, pairKey)), trayGate),
        onPill: id => $railOpen.set(toggleRail(railOpen, pairKey, id)),
      }),
      terminalTotal
        ? jsxs('button', {
            type: 'button', className: 'text-[0.6875rem] text-(--ui-text-tertiary)',
            style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0, textAlign: 'left' },
            onClick: () => $stripFold.set(folded ? pairKey : null),
            // WF-05 (QA 2026-10-27): the chevron answers the CURRENT state —
            // ▸ points right while collapsed, ▾ opens downward when expanded
            // (the fold's own disclosure vocabulary, one glyph one truth).
            children: [`${folded ? '▸' : '▾'} ${terminalTotal} finished`]
          })
        : null,
      !folded
        ? box(
            'flex flex-col gap-0.5 pl-3',
            ...terminalFold.map(r => jsx('button', {
              type: 'button', className: 'text-left text-[0.6875rem] text-(--ui-text-tertiary)',
              style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0 },
              onClick: () => openRun(r.id),
              // l8i: the fold's row leads with the instance label, same law.
              children: `${displayTitle(r)} · ${runStatusLabel(r)} · ${ago(r.updated) || 'unknown'}`
            }, r.id)),
            // WF-04 (QA 2026-10-27): the fold lists at most 5 but the label
            // counts ALL N — the hidden rows keep an explicit affordance to
            // the pane that lists every one (label N, rendered K used to
            // silently lose N−K finished runs).
            terminalTotal > terminalFold.length
              ? jsx('button', {
                  type: 'button', className: 'text-left text-[0.6875rem] text-(--ui-text-tertiary)',
                  title: 'Open the Workflows pane — every finished run is listed there',
                  style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0 },
                  onClick: () => host.navigate('/workflows'),
                  children: `+${terminalTotal - terminalFold.length} more`
                }, 'fold-more')
              : null
          )
        : null
    ]
  })
}

// -- 2. page /workflows ---------------------------------------------------------

/** The gate surface's requester line: the requester the GRAPH declares
 *  (gate context), else the recorded origin via originLabel — never a
 *  fabricated name, never the viewer's own chat. Pure, node-testable. */
export function gateRequester(gate, owner) {
  const ctx = gate && gate.context
  if (typeof ctx === 'string' && ctx.trim()) return ctx.trim()
  return `@${originLabel(owner, null)}`
}

/** Toast/ledger jump to the EXACT gate of the SAME run the answer rode:
 *  identity is the one the click carried (runId + gateId closure), never the
 *  viewer's current selection, and the route only selects the record page.
 *  No session hydration, no composer, no resume. Pure, node-testable. */
export function gateViewAction(runId, gateId) {
  return {
    label: 'View exact gate',
    onClick: () => {
      $selRun.set(runId)
      $selNode.set({ runId, nodeId: gateId })
      host.navigate('/workflows')
    }
  }
}

/** Hold age from the event ledger: gate.held -> answer `at` (receipt, a fixed
 *  number) or -> this render (held surface, a captured age, never a fake
 *  ticking clock). Either end absent -> null: honest absence. */
function gateDwell(gate, answered, events) {
  const held = (events || []).find(e => e && e.event === 'gate.held' && e.node === gate.id)
  const t0 = held ? parseTime(held.ts) : null
  if (!t0) return null
  const tEnd = answered && answered.at ? parseTime(answered.at) : null
  return fmtDur(Math.max(0, (tEnd || Date.now()) - t0))
}

/** The read model's answer record for a gate cell: the full view's `gates`
 *  block (an answer that survived invalidate-then-read but has not been
 *  consumed yet), else a released gate's committed node output. Neither ->
 *  null: honest absence, never a fabricated receipt. Pure, node-testable. */
export function gateAnswerFor(detail, def, st) {
  const gs = detail && detail.gates
  if (gs && Object.prototype.hasOwnProperty.call(gs, String(def.id))) {
    const g = gs[String(def.id)]   // own-property only (est-wk7l): a node id
    if (g && typeof g === 'object' && 'answer' in g) return g  // like 'toString' never resolves via the prototype
  }
  const out = st && st.status === 'done' ? st.output : null
  return out && typeof out === 'object' && 'answer' in out ? out : null
}

/** The one decision surface for a held human gate (UI-2 RC, gate-answer-flow):
 *  verbatim question, declared requester, every recorded option; a click
 *  POSTs the SAME answer path the tool uses (_release_core(ui=True)) and the
 *  surface becomes a durable receipt. The submit/draft/resume-toast chain is
 *  RETIRED (no compat shim): an answer records gates/<id>.json with `_ui`
 *  provenance, never touches a composer, and never resumes — the owning
 *  agent drives the runner. An {ok:false} door answer is an ERROR, not a
 *  successful mutation (api() throws; the options stay retryable). */
export function GateActions({ runId, gate, owner, answered, events }) {
  const qc = useQueryClient()
  const [recorded, setRecorded] = useState(null) // {answer, at} — this write, pre-refetch
  const [failed, setFailed] = useState(null)
  const receiptRef = useRef(null)
  const mut = useMutation({
    mutationFn: answer => api(`/runs/${runId}/gate`, { method: 'POST', body: { gate_id: gate.id, answer } }),
    onSuccess: (res, answer) => {
      setFailed(null)
      // The door's success response carries the server-stamped `at` (receipt
      // contract): the local record keeps the DURABLE timestamp, so a
      // same-mounted component never renders a client-clock guess for when
      // its own answer was written.
      setRecorded({ answer, at: typeof res?.at === 'string' ? res.at : null })
      // Invalidate before reading: the refetch re-projects the census and the
      // read-model gates block, so the receipt survives on recorded bytes.
      qc.invalidateQueries({ queryKey: Q })
      host.notify({
        kind: 'success',
        message: `◇ Answer saved · ${answer} · ${gateRequester(gate, owner)} · ${runId} / ${gate.id}` +
          (typeof res?.at === 'string' ? ` · ${res.at}` : ''),
        action: gateViewAction(runId, gate.id)
      })
    },
    onError: err => {
      setFailed(String(err?.message || err))
      host.notify({ kind: 'error', message: `Gate answer failed: ${err?.message || err}` })
    }
  })
  // Hooks above follow the hook law; the state returns below are hooks-first.
  // The durable read-model record OUTRANKS the local write state once it
  // arrives (review-2 Q1): `answered` carries the server `at`, so the dwell
  // freezes at the recorded answer time instead of shadowing to current time.
  const savedSrc = answered && answered.answer !== undefined ? answered : recorded
  const saved = savedSrc && savedSrc.answer !== undefined ? savedSrc.answer : undefined
  useEffect(() => {
    // Focus restoration: when the option buttons are replaced by the receipt,
    // keyboard focus lands ON the receipt instead of falling to the body.
    if (saved !== undefined && receiptRef.current && typeof receiptRef.current.focus === 'function') {
      receiptRef.current.focus()
    }
  }, [saved !== undefined])
  const head = [
    gate.question ? box('text-[0.6875rem] leading-snug text-(--ui-text-secondary)', gate.question) : null,
    box('text-[0.6875rem] text-(--ui-text-tertiary)', `requester: ${gateRequester(gate, owner)}`)
  ]
  if (saved !== undefined) {
    const dwell = gateDwell(gate, savedSrc, events)
    return jsxs('div', {
      ref: receiptRef, tabIndex: -1, 'data-gate-receipt': gate.id || '',
      className: 'flex flex-col border-t border-(--ui-stroke-secondary)',
      style: { gap: 4, padding: '6px 8px 8px', outline: 'none' },
      children: [
        ...head,
        box('text-[0.6875rem] text-(--ui-success, var(--ui-text-secondary))', 'Answer saved · nothing will be sent on this path.'),
        box('text-[0.6875rem] font-mono text-(--ui-text-secondary)', String(saved)),
        // who/WHAT/WHEN: the recorded answer time is rendered (review-2 Q1) —
        // the durable server `at` once the read model carries it, and an
        // honest unknown when a record has no timestamp, never a silent drop.
        box('text-[0.6875rem] tabular-nums text-(--ui-text-tertiary)',
          `Answered · ${savedSrc && savedSrc.at ? String(savedSrc.at) : 'time not recorded'}`),
        dwell ? box('text-[0.6875rem] tabular-nums text-(--ui-text-tertiary)', `held ${dwell}`) : null,
        box('text-[0.6875rem] text-(--ui-text-tertiary)',
          'Nothing restarted. The UI answer path records only — verified against the tested isolated runner; a live scheduler may consume the answer when it next checks.'),
        jsx(Button, {
          size: 'xs', variant: 'outline', className: 'w-full justify-start text-[0.6875rem]',
          onClick: gateViewAction(runId, gate.id).onClick, children: 'View exact gate'
        }, 'view-gate')
      ]
    })
  }
  const opts = (gate.options || []).map(opt =>
    jsx(
      Button,
      { size: 'xs', variant: 'outline', className: 'w-full justify-start text-[0.6875rem]', disabled: mut.isPending, onClick: () => mut.mutate(opt), children: opt },
      opt
    )
  )
  return jsxs('div', {
    className: 'flex flex-col border-t border-(--ui-stroke-secondary)',
    style: { gap: 4, padding: '6px 8px 8px' },
    children: [
      ...head,
      ...opts,
      mut.isPending ? box('text-[0.6875rem] text-(--ui-text-tertiary)', 'Saving answer…') : null,
      failed ? box('text-[0.6875rem] text-(--ui-danger, var(--ui-text-secondary))', `Gate answer failed · ${failed}`) : null,
      // Fail-closed on an options-less hold: the reason shows, no buttons are
      // invented, and the hold never renders as a silent nothing.
      opts.length ? null : box('text-[0.6875rem] text-(--ui-text-tertiary)', 'No answer options recorded.')
    ]
  })
}

export function NodeCard({ runId, def, st, gate, selected, owner, events, answered = null, hovered = false }) {
  const isGate = def.type === 'gate'
  const liveGate = gate && gate.id === def.id ? gate : null
  // A live held gate outranks the read model's raw 'pending' node status.
  const status = isGate && liveGate ? 'held' : st?.status || 'pending'
  useTick(status === 'running')
  const rows = def.fanout ? fanItems(def, st, events) : null
  const fc = rows && rows.length ? fanCounts(rows) : null
  const dur = st?.ms ? fmtDur(st.ms) : ''
  const m = st?.metrics || null
  // #48: every visual decision reads the ONE tone table. Running glows (soft
  // accent shadow + the live-dot pulse from Dot); held-at-gate nags with a
  // slow border pulse; terminal states are calm and FLAT (no shadow, no
  // animation — the calm law), with failed keeping a loud static red tint on
  // its border. Ship 2.0 (bd_2026-11-13-32i): every animation this card may
  // run is admitted by the ONE motion allocator (W4) — a denied or preempted
  // effect renders its truthful static state IMMEDIATELY (spill, never a
  // hidden queue). The pending breathe stays the incumbent #48 animation
  // until the W5 binding wave applies DESIGN Round 10 ("pending -> None").
  const tone = NODE_TONE[status] || NODE_TONE.pending
  // Attention motion goes through the ONE allocator (W4): a denied or
  // preempted claim renders the constant amber border — the static
  // equivalent — immediately, never a queued retry. Phase rides the gate's
  // own hold event (spelling-tolerant on the gate object, else the SAME
  // gate.held ledger row gateDwell reads — one source, never the mount);
  // an absent/future/invalid time claims no recency cue.
  const heldFromGate = liveGate ? parseTime(liveGate.held_at ?? liveGate.heldAt ?? liveGate.at ?? liveGate.held) : 0
  const heldEv = heldFromGate ? 0 : (events || []).find(e => e && e.event === 'gate.held' && e.node === def.id)
  const heldAt = heldFromGate || (heldEv ? parseTime(heldEv.ts) : 0)
  const motionAnim = tone.calm || status === 'running' ? null
    : status === 'held' && tone.gate
      ? { spec: tone.gate, anim: 'var(--dur-attention) var(--ease-breathe)',
          claim: MOTION.claim({ id: `attention:${runId}:${def.id}`, cls: 'attention', ts: heldAt || null, durToken: '--dur-attention' }) }
      : tone.breathe
        ? { spec: tone.breathe, anim: `${tone.pulseMs}ms ease-in-out`,
            // The incumbent pending breathe keeps its table period until the
            // W5 binding wave retires it (DESIGN Round 10: pending -> None).
            claim: MOTION.claim({ id: `attention:${runId}:${def.id}:breathe`, cls: 'attention', ts: null, durMs: tone.pulseMs }) }
        : null
  const animation = motionAnim && motionAnim.claim.admitted
    ? `${motionAnim.spec.name} ${motionAnim.anim} infinite`
    : undefined
  const glow = hovered ? (tone.shadowHover || tone.shadow) : tone.shadow
  return jsxs(
    'div',
    {
      className: 'shrink-0 rounded-md border bg-transparent',
      style: {
        width: CARD_W,
        background: 'var(--ui-sidebar-surface-background, var(--card))',
        opacity: status === 'pending' ? 0.7 : 1,
        borderColor: tone.borderColor,
        borderStyle: status === 'pending' || isGate ? 'dashed' : 'solid',
        boxShadow: selected
          // #48 F3: the selection ring rides the ONE table (centered color-mix
          // of the state's accent — hover/selected stay a distinct intensity,
          // but the colour is modeled centrally, not a stray token).
          ? [glow, `inset 0 0 0 1px color-mix(in srgb, ${tone.color} 55%, transparent)`].filter(Boolean).join(', ')
          : glow || undefined,
        transform: hovered && !tone.calm ? 'translateY(-1px)' : undefined,
        transition: 'transform 120ms ease, box-shadow 160ms ease, border-color 160ms ease',
        animation,
        // Timestamp-aligned phase (DESIGN Round 10): the offset derives from
        // the ORIGINAL hold event, so redraws and remounts cannot restart it.
        animationDelay: motionAnim && motionAnim.claim.admitted ? `${motionAnim.claim.phaseMs}ms` : undefined,
        // Admission instrumentation (bd_2026-11-13-32i): the allocator's
        // verdict per effect ID — the real-app proof driver reads these off
        // the ACTUAL renderer; invisible in screenshots, never user copy.
        'data-motion': motionAnim
          ? motionAnim.claim.admitted
            ? `admitted:${motionAnim.claim.reserved ? 'reserved' : 'active'}`
            : `spill:${motionAnim.claim.reason}`
          : 'none',
        'data-motion-id': motionAnim ? `attention:${runId}:${def.id}` : undefined
      },
      children: [
        jsxs(
          'button',
          {
            type: 'button',
            // Toggle from the `selected` prop GraphView already passes — the
            // SDK atom is set/useValue only; a read via .get() throws inside
            // the handler and the click dies silently (non-stack nodes never
            // opened the panel). Never call .get() on an atom.
            onClick: () => $selNode.set(selected ? null : { runId, nodeId: def.id }),
            className: 'w-full cursor-pointer px-2 py-1.5 text-left transition-colors hover:text-foreground',
            children: [
              box(
                'flex items-center gap-1.5',
                jsx(Dot, { status }),
                jsx(Codicon, { name: isGate ? 'eye' : 'robot', size: '0.8em', className: 'text-(--ui-text-tertiary)' }),
                box('min-w-0 flex-1 truncate text-xs font-medium', def.id)
              ),
              box(
                'mt-1 flex items-center gap-1.5 text-[0.6875rem] text-(--ui-text-tertiary)',
                jsx('span', { children: statusLabel(status) }),
                fc ? jsx('span', { children: fanSummary(fc) }) : null,
                // WF-06 (QA 2026-10-27): the card's elapsed is the NODE clock
                // (record ms — the child wall this node billed), a different
                // source than the header's run clock; the word labels it.
                dur ? jsx('span', { children: `node ${dur}` }) : null,
                def.optional ? jsx('span', { children: 'opt' }) : null,
                // F2 desktop (RATIFY): the delegation badge — ONLY when the node
                // def carries `profile` (read model passes def through verbatim;
                // a no-team graph never has the key, so the card is byte-identical).
                def.profile ? jsx('span', { title: `as @${def.profile}`, children: `as @${def.profile}` }) : null,
                modelTag(def) ? jsx('span', { title: def.model, style: { marginLeft: 'auto', opacity: 0.85 }, children: modelTag(def) }) : null
              ),
              m ? box('mt-1', jsx(Vitals, { m, live: status === 'running', size: 'xs' })) : null
            ]
          },
          'head'
        ),
        // The gate cell lives with the card (one release surface per held
        // run). A recorded answer keeps the cell mounted as the durable
        // receipt: question + requester + answer provenance, no option
        // buttons — a historical seed is never re-answerable.
        isGate && (status === 'held' || answered)
          ? jsx(GateActions, {
              runId, owner, events, answered,
              gate: Object.assign({ id: def.id, question: def.question, options: def.options, context: def.context }, liveGate || {})
            })
          : null
      ]
    },
    def.id
  )
}

// Layered left-to-right columns with REAL edges: cards are measured after layout
// (ResizeObserver on the canvas) and each `after` relation becomes an SVG cubic
// from the upstream card's right-middle to the downstream card's left-middle.
// Edge tone = upstream node state: data flowed (done) / blocked at a hold /
// dead (failed => downstream never ran) / pending. Fan-out nodes render as a
// short stack of cards so N children read as N, not as one card run N times.

const EDGE_TONE = {
  done: 'var(--ui-success, var(--ui-accent))',
  running: 'var(--ui-accent)',
  held: 'var(--ui-warning, var(--ui-accent))',
  failed: 'var(--ui-danger, var(--ui-text-tertiary))',
  pending: 'var(--ui-stroke-secondary)',
  skipped: 'var(--ui-text-tertiary)'
}

// #133: wall-meter word tones (Vitals). Declared here, right after EDGE_TONE:
// a top-level const here reads EDGE_TONE at module-eval time, so it must not
// sit above the palette (TDZ). The words are the run_state meter vocab verbatim.
const METER_TONE = { 'on-track': EDGE_TONE.running, 'near-wall': EDGE_TONE.held, 'over-p95': EDGE_TONE.failed }

// ONE tone vocabulary for every reader (issue #48): the rail pill (pillModel),
// the canvas NodeCard, the mini-DAG pill, the edges and the timeline all read
// this table — colours come from EDGE_TONE (the single literal palette), so a
// forked palette is impossible by construction. state x intensity ->
// {color, borderColor, shadow, pulseMs, calm, ui, gate, breathe}.
// Laws: running/held glow (shadow) and carry a pulse period; EVERY terminal
// state (done/failed/stopped/skipped) is calm: pulseMs null && shadow null —
// terminal states stop every animation. failed stays LOUD through its static
// red borderColor tint, not a glow.
// ── ui2 W4 motion allocator (bd_2026-11-13-32i) ─────────────────────────────
// DESIGN Round 10 ("motion is data"): ONE global animator budget across the
// graph AND its associated collection — active + reserved <= 12 at every
// claim, release and settle, counting targets/effects, never CSS declarations.
// Priority: transition > attention > running glyph > edge; ties order by
// event timestamp (newer event outranks an older one for a contended slot),
// then by the stable effect ID. A rejected or preempted effect spills to its
// truthful STATIC state immediately — never a hidden queue; a timer cannot
// evade the cap. Recurrent effects re-admitted to the budget retain the
// ORIGINAL event timestamp as their phase, so redraws and remounts cannot
// restart or shift them. Failure/done/insertion/fold settle one-shots are
// consumed once per event identity, never once per render (only a labelled
// replay resets consumption — replayReset below is that seam). Insertion is
// the only effect allowed to delay, at most 30ms between arrivals and at most
// 90ms in total, and every delay RESERVES its slot inside the same N=12 pool.
// The fifteen dur/ease tokens below are the whole registered timing
// vocabulary (the DESIGN Round 10 token table, verbatim values); the
// consolidated sheet emits them once and the content-digest href versions
// that emission.
export const MOTION_TOKENS = {
  '--dur-pulse-fresh': '2000ms',
  '--dur-pulse-quiet': '4000ms',
  '--dur-flow': '1200ms',
  '--dur-attention': '4000ms',
  '--dur-failed': '320ms',
  '--dur-done': '240ms',
  '--dur-insert': '240ms',
  '--dur-collapse': '240ms',
  '--dur-expand': '0ms',
  '--dur-progress': '0ms',
  '--ease-breathe': 'cubic-bezier(.4,0,.6,1)',
  '--ease-flow': 'linear',
  '--ease-settle': 'cubic-bezier(.16,1,.3,1)',
  '--ease-step': 'steps(1,end)',
  '--ease-expand': 'linear'
}
export const MOTION_PRIORITY = ['transition', 'attention', 'glyph', 'edge']
export const MOTION_CAP = 12
export const MOTION_INSERT_GAP_MS = 30
export const MOTION_INSERT_TOTAL_MS = 90

function motionTokenMs (token) {
  const v = Object.prototype.hasOwnProperty.call(MOTION_TOKENS, token) ? MOTION_TOKENS[token] : null
  const m = typeof v === 'string' && /^(\d+)ms$/.exec(v)
  return m ? Number(m[1]) : null
}

// createMotionAllocator: the pure pool (injectable clock for behavior tests).
// MOTION below is the ONE global instance — graph and collection share it
// (FINAL.md: do not instantiate one allocator per lane).
export function createMotionAllocator ({
  cap = MOTION_CAP, insertGapMs = MOTION_INSERT_GAP_MS, insertTotalMs = MOTION_INSERT_TOTAL_MS,
  clock = null, idleMs = 15_000
} = {}) {
  const nowFn = clock || (() => Date.now())
  const holders = new Map() // id -> {id, cls, ts, durMs, phaseMs, once, key, arriveAt, until, gen, lastSeen}
  const consumed = new Set() // one-shot event identities already granted their single animator
  const consumedFifo = []
  let reduced = false
  let genSeq = 1
  const counters = { admitted: 0, denied: 0, preempted: 0, released: 0, consumedDenied: 0 }

  const rank = cls => MOTION_PRIORITY.indexOf(cls)
  // Slot-order key: (class rank, newest event first, stable id). A claim
  // admits into free space, or by ranking STRICTLY below the current weakest
  // holder (preemption of a lower class — or, inside the same class, of the
  // older event; the id is the deterministic final tie).
  const keyOf = h => [rank(h.cls), -h.ts, h.id]
  const below = (a, b) => {
    for (let i = 0; i < 3; i++) {
      if (a[i] < b[i]) return true
      if (a[i] > b[i]) return false
    }
    return false
  }
  const validTs = ts => typeof ts === 'number' && Number.isFinite(ts) && ts <= nowFn()
  // Original-timestamp phase: the cycle offset at time `at` derived from the
  // event's own timestamp — a negative animation-delay. A missing, invalid or
  // FUTURE timestamp is unknown (DESIGN Round 10): it claims no recency cue,
  // so the cycle opens at its head (phase 0) instead of fabricating one.
  const phaseFor = (ts, dur, at) =>
    (!Number.isFinite(ts) || !(dur > 0)) ? 0 : -((((at - ts) % dur) + dur) % dur)
  const consume = key => {
    if (consumed.has(key)) return
    consumed.add(key)
    consumedFifo.push(key)
    while (consumedFifo.length > 512) consumed.delete(consumedFifo.shift())
  }
  function sweep () {
    const now = nowFn()
    for (const [id, h] of holders) {
      // one-shots and reservations expire at their settle instant; infinite
      // holders expire when they stop being re-claimed (unmount/route-away)
      // — the stale cancellation law: nobody may hold a slot from off-screen.
      // The pane re-claims every visible effect each poll, so an un-refreshed
      // holder after idleMs (>=3 lost 4 s cycles) is gone, not resting.
      const dead = h.until != null ? h.until <= now : h.lastSeen + idleMs <= now
      if (dead) {
        holders.delete(id)
        if (h.key) consume(h.key)
        counters.released++
      }
    }
  }
  function claim (req) {
    sweep()
    const { id, cls, ts = null, durToken = null, durMs = null, once = false, eventKey = null, delayMs = 0 } = req || {}
    const reject = reason => { counters.denied++; return { admitted: false, reason, spill: 'static', phaseMs: 0 } }
    if (typeof id !== 'string' || !id || rank(cls) < 0) return { admitted: false, reason: 'invalid', spill: 'static', phaseMs: 0 }
    if (reduced) return reject('reduced')
    const dur = durMs != null ? durMs : motionTokenMs(durToken)
    if (dur == null) return reject('unregistered')
    const known = validTs(ts)
    // A registered 0ms duration IS the static state (expand/progress): admit
    // with no slot, so zero-duration vocabulary never occupies animators.
    if (dur === 0) return { admitted: true, zeroDuration: true, phaseMs: 0, delayMs: 0, token: null, unknownTs: !known }
    const d = Math.max(0, Number(delayMs) || 0)
    const cur = holders.get(id)
    if (cur) {
      cur.lastSeen = nowFn()
      cur.phaseMs = phaseFor(known ? ts : Number.NaN, dur, nowFn() + d)
      return { admitted: true, idempotent: true, phaseMs: cur.phaseMs, delayMs: d, token: { id, gen: cur.gen }, unknownTs: !known }
    }
    const key = once ? (eventKey || `${id}@${known ? ts : nowFn()}`) : null
    if (once && consumed.has(key)) { counters.consumedDenied++; return reject('consumed') }
    const h = {
      id, cls, ts: known ? ts : 0, durMs: dur, once, key, gen: genSeq++, lastSeen: nowFn(),
      phaseMs: phaseFor(known ? ts : Number.NaN, dur, nowFn() + d),
      arriveAt: d > 0 ? nowFn() + d : null,
      until: (once || d > 0) ? nowFn() + d + dur : null
    }
    const admit = () => {
      if (h.key) consume(h.key)
      holders.set(id, h)
      counters.admitted++
      return { admitted: true, phaseMs: h.phaseMs, delayMs: d, token: { id, gen: h.gen }, unknownTs: !known, reserved: h.arriveAt != null }
    }
    if (holders.size < cap) return admit()
    let victim = null
    for (const hh of holders.values()) if (!victim || below(keyOf(victim), keyOf(hh))) victim = hh
    if (below(keyOf(h), keyOf(victim))) {
      holders.delete(victim.id)
      if (victim.key) consume(victim.key)
      counters.preempted++
      return admit()
    }
    return reject('cap') // immediate static spill — the cap never queues
  }
  function release (tok) {
    if (!tok || typeof tok.id !== 'string') return false
    const h = holders.get(tok.id)
    // Stale cancellation: a release from an old generation (unmount of a view
    // that a newer claim already re-took) must never evict the live holder.
    if (!h || (tok.gen != null && h.gen !== tok.gen)) return false
    holders.delete(tok.id)
    if (h.key) consume(h.key)
    counters.released++
    return true
  }
  // planInsertion: the ONLY delayed-effect scheduler. Gaps between admitted
  // arrivals are insertGapMs (<=30ms), the total ladder is capped at
  // insertTotalMs (<=90ms), and every delay reserves its slot NOW inside the
  // N=12 pool. Excess arrivals spill to static rather than extend a queue —
  // identity and status are already on screen, the tween is decoration.
  function planInsertion (ids, { ts = null, cls = 'transition' } = {}) {
    sweep()
    const out = []
    let n = 0
    for (const id of [...ids].sort()) {
      const delay = n * insertGapMs
      if (delay > insertTotalMs) { out.push({ id, delayMs: null, admitted: false, reason: 'over-schedule' }); continue }
      // Insertions animate with the registered --dur-insert token: a delay
      // without a settle instant would hold its slot forever.
      const r = claim({ id, cls, ts, delayMs: delay, once: true, durToken: '--dur-insert' })
      if (r.admitted) { out.push({ id, delayMs: delay, admitted: true }); n++ }
      else out.push({ id, delayMs: null, admitted: false, reason: r.reason })
    }
    return out
  }
  // Running-glyph recency (DESIGN matrix: <=5s fresh, >5s quiet, unknown is
  // unknown): returns the registered token to use, never an invented period.
  function recencyToken ({ ts = null, alive = false } = {}) {
    if (!alive || !validTs(ts)) return { token: null, unknown: true }
    return { token: nowFn() - ts <= 5000 ? '--dur-pulse-fresh' : '--dur-pulse-quiet', unknown: false }
  }
  function setReduced (v) {
    reduced = !!v
    // The reduced flip zeroes effects AND reservations at once: no paused,
    // half-faded frames — every target sits in its truthful static state at
    // full opacity (the renderers' spill path is exactly that state).
    if (reduced) { counters.released += holders.size; holders.clear() }
    return reduced
  }
  function replayReset () { consumed.clear(); consumedFifo.length = 0 }
  function stats () {
    sweep()
    const now = nowFn()
    let active = 0, reserved = 0
    const held = []
    for (const h of [...holders.values()].sort((a, b) => (a.id < b.id ? -1 : 1))) {
      if (h.arriveAt != null && h.arriveAt > now) reserved++
      else active++
      held.push({ id: h.id, cls: h.cls, ts: h.ts, phaseMs: h.phaseMs, durMs: h.durMs, gen: h.gen, reserved: h.arriveAt != null && h.arriveAt > now })
    }
    return { active, reserved, total: holders.size, cap, reduced, counters: { ...counters }, holders: held }
  }
  return { claim, release, planInsertion, recencyToken, setReduced, replayReset, stats }
}
export const MOTION = createMotionAllocator()
// The one bench seam the real-app proof driver uses to walk a controlled
// labelled event schedule and read instrumented admissions off the ACTUAL
// renderer. The only global the plugin ever assigns; never read by the UI.
globalThis.__wfMotion = MOTION

const GATE_PULSE = {
  // The held-gate nag period is the registered --dur-attention token (4000ms),
  // not a second source (W4: no unregistered durations on new motion).
  name: 'wf-gate-nag', durMs: 4000,
  keyframes: '@keyframes wf-gate-nag {\n  0%, 100% { border-color: var(--ui-warning, var(--ui-accent)); }\n  50% { border-color: color-mix(in srgb, var(--ui-warning, var(--ui-accent)) 30%, transparent); }\n}'
}
const BREATHE = {
  name: 'wf-breathe', durMs: 2600,
  keyframes: '@keyframes wf-breathe {\n  0%, 100% { opacity: 1; }\n  50% { opacity: 0.45; }\n}'
}

export const NODE_TONE = {
  pending: { color: EDGE_TONE.pending, borderColor: EDGE_TONE.pending, shadow: null, pulseMs: BREATHE.durMs, calm: false, ui: 'muted', gate: null, breathe: BREATHE },
  running: { color: EDGE_TONE.running, borderColor: EDGE_TONE.running, shadow: '0 0 10px 0 color-mix(in srgb, var(--ui-accent) 30%, transparent)', shadowHover: '0 2px 14px 1px color-mix(in srgb, var(--ui-accent) 45%, transparent)', pulseMs: 900, calm: false, ui: 'accent', gate: GATE_PULSE, breathe: BREATHE },
  held: { color: EDGE_TONE.held, borderColor: EDGE_TONE.held, shadow: '0 0 10px 0 color-mix(in srgb, var(--ui-warning, var(--ui-accent)) 26%, transparent)', pulseMs: GATE_PULSE.durMs, calm: false, ui: 'warn', gate: GATE_PULSE, breathe: null },
  done: { color: EDGE_TONE.done, borderColor: EDGE_TONE.done, shadow: null, pulseMs: null, calm: true, ui: 'good', gate: null, breathe: null },
  failed: { color: EDGE_TONE.failed, borderColor: 'color-mix(in srgb, var(--ui-danger, var(--ui-text-tertiary)) 70%, transparent)', shadow: null, pulseMs: null, calm: true, ui: 'bad', gate: null, breathe: null },
  stopped: { color: EDGE_TONE.skipped, borderColor: EDGE_TONE.skipped, shadow: null, pulseMs: null, calm: true, ui: 'muted', gate: null, breathe: null },
  skipped: { color: EDGE_TONE.skipped, borderColor: EDGE_TONE.skipped, shadow: null, pulseMs: null, calm: true, ui: 'muted', gate: null, breathe: null }
}
// The ask vocabulary says 'waiting', the read model says 'pending' — the SAME
// entry, not a twin: one table, one voice.
NODE_TONE.waiting = NODE_TONE.pending
// WF-02 (QA 2026-10-27): cancelled is never a failure — the SAME neutral, calm
// entry as skipped (stop != failure, the #7 law; a resume re-drives it).
NODE_TONE.cancelled = NODE_TONE.skipped

// Hoisted animation CSS (#48, retooled by bd_2026-11-13-32i): ONE <style>,
// injected once by PolishStyles, deduped by React 19 via a stable href. The
// href is a CONTENT digest (FNV-1a/64 over the full emitted bytes), replacing
// the hand-bumped version counter: every lane's edit auto-versions the
// emission — the digest is of the exact children string the single injector
// mounts, never a lane fragment — and it stays a plain JS computation, so
// single-file SDK packaging is untouched. Pulse keyframes sit behind
// prefers-reduced-motion: no-preference so the animations simply never
// resolve for users who ask for calm.
function fnv1a64 (text) {
  let h = 0xcbf29ce484222325n
  const PRIME = 0x100000001b3n
  const MASK = 0xffffffffffffffffn
  for (let i = 0; i < text.length; i++) {
    h = (h ^ BigInt(text.charCodeAt(i))) * PRIME & MASK
  }
  return h.toString(16).padStart(16, '0')
}
// The consolidated token block: the fifteen registered dur/ease tokens are
// the only motion vocabulary the plugin ships (DESIGN Round 10 table).
const MOTION_TOKEN_CSS = `:root {\n${Object.keys(MOTION_TOKENS).map(k => `  ${k}: ${MOTION_TOKENS[k]};`).join('\n')}\n}`
export const MOTION_CSS = `${MOTION_TOKEN_CSS}\n@media (prefers-reduced-motion: no-preference) {\n${GATE_PULSE.keyframes}\n${BREATHE.keyframes}\n}`
export function styleHrefFor (css) { return `hermes-workflows.${fnv1a64(css)}.css` }
export const STYLE_HREF = styleHrefFor(MOTION_CSS)

// The single hoisted style injector (the ONLY style-element call in the file).
// Styles only plugin-owned @keyframes and custom properties — never global
// page chrome.
export function PolishStyles() {
  return jsx('style', { 'data-plugin': ID, href: STYLE_HREF, children: MOTION_CSS })
}

/** Pure edge-flow decision (exported so node can pin the truth table):
 *  running upstream => march; items_from data edge => shimmer ONLY while the
 *  consumer runs (data arriving is the live moment, calm after); dead dashed,
 *  never animated, when the upstream failed OR — F5 (#48 deep review) — the
 *  downstream can no longer run (`canRun === false`, the canRun-style
 *  readiness the read model derives from dependencies + blocked_by) and its
 *  upstream is settled: done | failed | blocked. Pending => faint dots;
 *  everything else calm. */
export function edgeFlowPolicy(upState, downState, dataFlow = false, canRun = true) {
  if (upState === 'failed') return { flow: false, shimmer: false, dead: true, dash: '3 3' }
  // Readiness-aware dead-dash: a join whose deps are no longer all satisfiable
  // (a failed sibling makes dep_satisfied false / blocked_by non-empty for the
  // whole fan-in) is dead for EVERY settled edge feeding it — the ok→join link
  // of a diamond reads dead too, not only the bad→join one.
  if (downState === 'pending' && canRun === false && (upState === 'done' || upState === 'failed' || upState === 'blocked')) {
    return { flow: false, shimmer: false, dead: true, dash: '3 3' }
  }
  if (dataFlow) return downState === 'running'
    ? { flow: false, shimmer: true, dead: false, dash: '6 4' }
    : { flow: false, shimmer: false, dead: false, dash: null }
  if (upState === 'running') return { flow: true, shimmer: false, dead: false, dash: '6 4' }
  if (upState === 'pending') return { flow: false, shimmer: false, dead: false, dash: '2 4' }
  return { flow: false, shimmer: false, dead: false, dash: null }
}

/** Pure run-header model for the tab strip (#48): the accent + gradient read
 *  alive while the run lives and calm-but-keyed once terminal. */
export function runHeaderModel(run) {
  const status = (run && run.status) || 'pending'
  const t = NODE_TONE[status] || NODE_TONE.pending
  const calm = TERMINAL.has(status)
  const start = parseTime(run?.started)
  const end = calm ? (parseTime(run?.updated) || Date.now()) : Date.now()
  const elapsed = start && end > start ? end - start : 0
  const accent = t.color
  return {
    status, accent, calm, elapsed, elapsedLabel: fmtDur(elapsed),
    gradient: calm
      ? `linear-gradient(90deg, ${accent} 0%, transparent 72%)`
      : `linear-gradient(90deg, ${accent} 0%, color-mix(in srgb, ${accent} 45%, transparent) 45%, transparent 100%)`
  }
}

// RC ch4 (route identity): every route carries a static identity stroke, a
// static target arrow (the existing marker) and matching open-ring endpoint
// echoes. Six deterministic palette aliases cycle by dependency order; they
// REUSE host palette tokens (--ui-purple/-cyan/-orange/-green/-yellow are the
// host's own tokens — no new colors, no registrations here). Tint means route
// IDENTITY, never execution state: the state stroke, dashes and markers are
// untouched underneath. This is a bounded port over the incumbent measured-rect
// cubic router (routeEdge), NOT an arbitrary-DAG equivalence claim.
export function routeTint(i) {
  const t = i % ROUTE_TINTS.length
  return ROUTE_TINTS[(t + ROUTE_TINTS.length) % ROUTE_TINTS.length]
}
const ROUTE_TINTS = [
  'var(--ui-accent)', 'var(--ui-purple)', 'var(--ui-cyan)',
  'var(--ui-orange)', 'var(--ui-green)', 'var(--ui-yellow)'
]

function edgeTone(upState, downState) {
  // #48: reads the ONE tone table (colours are EDGE_TONE's by construction —
  // NODE_TONE extracts them). Same decision tree as before, no new palette.
  if (upState === 'failed') return NODE_TONE.failed.color
  if (upState === 'held') return NODE_TONE.held.color
  if (upState === 'done') return downState === 'pending' ? NODE_TONE.held.color : NODE_TONE.done.color
  if (upState === 'skipped') return NODE_TONE.skipped.color
  if (upState === 'running') return NODE_TONE.running.color
  return NODE_TONE.pending.color
}

// #48: the timeline reads the ONE tone table's colour column too — the same
// decision tree as before, no parallel palette. WF-02 (QA 2026-10-27):
// cancelled reads neutral like skipped/stopped, never the failed red.
const timelineTone = sp => sp.status === 'pending' ? NODE_TONE.pending.color
  : sp.status === 'skipped' || sp.status === 'stopped' || sp.status === 'cancelled' ? NODE_TONE.skipped.color
  : sp.kind === 'gate' && sp.status === 'held' ? NODE_TONE.held.color
    : sp.status === 'failed' ? NODE_TONE.failed.color
      : sp.status === 'done' ? NODE_TONE.done.color
        : NODE_TONE.running.color

// Tier name if the owner's vocabulary was used, else the model id's last segment.
const modelTag = def => def.tier || (def.model ? String(def.model).split('/').pop() : '')

function nodeState(def, states, gate) {
  const isGate = def.type === 'gate'
  const liveGate = gate && gate.id === def.id ? gate : null
  return isGate && liveGate ? 'held' : states[def.id]?.status || 'pending'
}

/** Measure every [data-node] card relative to the canvas; re-run on resize. */
function useCardRects(canvasRef, deps) {
  const [rects, setRects] = useState({})
  useEffect(() => {
    const el = canvasRef.current
    if (!el) return
    const measure = () => {
      const base = el.getBoundingClientRect()
      const out = {}
      for (const c of el.querySelectorAll('[data-node]')) {
        const r = c.getBoundingClientRect()
        out[c.dataset.node] = {
          x: r.left - base.left + el.scrollLeft, y: r.top - base.top + el.scrollTop, w: r.width, h: r.height
        }
      }
      setRects(out)
    }
    measure()
    const ro = new ResizeObserver(measure)
    ro.observe(el)
    for (const c of el.querySelectorAll('[data-node]')) ro.observe(c)
    return () => ro.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  return rects
}

/** Canvas clientWidth — the measure bandRows packs against; re-runs on resize
 *  so a window resize recomputes the bands. 0 until the element exists. */
function useCanvasWidth(canvasRef, deps) {
  const [w, setW] = useState(0)
  useEffect(() => {
    const el = canvasRef.current
    if (!el) return
    const measure = () => setW(el.getBoundingClientRect().width)
    measure()
    const ro = new ResizeObserver(measure)
    ro.observe(el)
    return () => ro.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  return w
}

/**
 * Cubic from (x1,y1) to (x2,y2) that bends AROUND unrelated cards: when the
 * straight corridor crosses another node's box (long skip edges like A -> C
 * over an intermediate B column), sink or rise both control points past the
 * colliding row, escalating until the sampled curve is clear.
 */
function routeEdge(x1, y1, x2, y2, rects, skip) {
  const cx = (x2 - x1) / 2
  // WRAPPED band-to-band edges (feedback #10): the next band restarts
  // left-anchored, so x runs BACKWARDS and the source column itself blocks
  // every simple curve (the stack spans the corridor). Route like an
  // orthogonal router: exit the source's right edge, sweep into the RIGHT
  // GUTTER past every card, run along a clear horizontal band, then rise
  // into the target's left port. The gutter y escalates (hit -> step away)
  // until the whole three-segment path pierces no unrelated card.
  if (x2 < x1) {
    const gx = Math.max(x1, ...Object.values(rects).map(r => r.x + r.w)) + 24
    const lx = Math.max(8, x2 - 60)
    const cub = (t, a, b, c, d) => { const u = 1 - t; return u * u * u * a + 3 * u * u * t * b + 3 * u * t * t * c + t * t * t * d }
    const hitRy = ry => {
      const S = 24
      const probes = []
      for (let i = 1; i <= S; i++) {
        const t = i / S
        probes.push([cub(t, x1, x1 + 60, gx, gx), cub(t, y1, y1, y1, ry)])           // exit sweep
        probes.push([lx + (gx - lx) * (1 - t), ry])                                   // gutter run
        probes.push([cub(t, gx, lx, lx, x2), cub(t, ry, ry, y2, y2)])                 // rise-in
      }
      for (const [id, r] of Object.entries(rects)) {
        if (skip.includes(id)) continue
        if (r.x + r.w > Math.min(x2, gx) && r.x < gx) {
          for (const [x, y] of probes) if (x > r.x && x < r.x + r.w && y > r.y && y < r.y + r.h) return r
        }
      }
      return null
    }
    const mid = (y1 + y2) / 2
    let ry = Math.max(8, mid)
    let first = hitRy(ry)
    for (let i = 0; first && i < 96; i++) {
      const down = first.y + first.h + 18, up = Math.max(8, first.y - 18)
      const step = Math.abs(down - ry) <= Math.abs(ry - up) ? Math.max(18, down - ry) : Math.min(-18, up - ry)
      ry = Math.max(8, ry + step)
      first = hitRy(ry)
    }
    return `M ${x1} ${y1} C ${x1 + 60} ${y1}, ${gx} ${y1}, ${gx} ${ry} L ${lx} ${ry} C ${lx} ${ry}, ${lx} ${y2}, ${x2} ${y2}`
  }
  const sampleY = (t, c1y, c2y) => {
    const u = 1 - t
    return u * u * u * y1 + 3 * u * u * t * c1y + 3 * u * t * t * c2y + t * t * t * y2
  }
  const sampleX = (t) => {
    const u = 1 - t, a = x1 + cx * 0.6, b = x2 - cx * 0.6
    return u * u * u * x1 + 3 * u * u * t * a + 3 * u * t * t * b + t * t * t * x2
  }
  const inSpan = r => r.x + r.w > Math.min(x1, x2) + 2 && r.x < Math.max(x1, x2) - 2
  const blockers = () => Object.entries(rects).filter(([id, r]) => !skip.includes(id) && inSpan(r))
  const hit = (c1y, c2y) => {
    for (const [, r] of blockers()) {
      for (let i = 1; i < 40; i++) {
        const x = sampleX(i / 40), y = sampleY(i / 40, c1y, c2y)
        if (x > r.x && x < r.x + r.w && y > r.y && y < r.y + r.h) return r
      }
    }
    return null
  }
  let c1y = y1, c2y = y2
  const first = hit(c1y, c2y)
  if (first) {
    const mid = (y1 + y2) / 2
    // Pick the nearer side of the colliding card and ESCALATE AWAY FROM IT
    // (direction fixed by the chosen side, never by mid drift).
    const down = first.y + first.h + 18, up = Math.max(8, first.y - 18)
    const goDown = Math.abs(down - mid) <= Math.abs(mid - up)
    let off = goDown ? down : up
    const step = goDown ? 18 : -18
    for (let i = 0; i < 24 && hit(off, off); i++) off += step
    c1y = off; c2y = off
  }
  return `M ${x1} ${y1} C ${x1 + cx * 0.6} ${c1y}, ${x2 - cx * 0.6} ${c2y}, ${x2} ${y2}`
}

function Edges({ nodes, rects, states, gate, dataEdges = [] }) {
  // Marker ids are document-global in SVG; several graphs on one page (page
  // canvas + N transcript cards) must not share them or arrowheads cross-wire.
  const mid = `wf-arrow-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
  const byKey = new Map()
  for (const n of nodes) {
    if (!rects[n.id]) continue
    for (const a of n.after || []) if (rects[a]) byKey.set(`${a}>${n.id}`, { from: a, to: n.id, data: false })
  }
  // #48: items_from data-flow edges (producer -> fan-out consumer) ride the
  // same rails as dependency edges but shimmer ONLY while the consumer runs.
  // F4 (deep review): the dedup keeps ONE edge per link and ORs the data
  // flags — the ordinary producer->fan-out shape (after:['gen'] AND
  // fanout.items_from:'gen.items') must reach the policy data-classified,
  // or the shimmer the promise makes is silently dropped by the seen-set.
  for (const e of dataEdges) {
    if (!rects[e.from] || !rects[e.to] || e.from === e.to) continue
    const k = `${e.from}>${e.to}`
    const cur = byKey.get(k)
    if (cur) cur.data = cur.data || true
    else byKey.set(k, { from: e.from, to: e.to, data: true })
  }
  const edges = [...byKey.values()]
  // F5 (#48 deep review): canRun-style readiness derived the way the read
  // model spells it — every `after` dep must be satisfied (done/skipped/
  // partial) for a pending node to run; anything else is its blocked_by list.
  const depSatisfied = st => st === 'done' || st === 'skipped' || st === 'partial'
  const canRunNow = def => {
    if (!def) return true
    return (def.after || []).every(a => depSatisfied(states[a]?.status || 'pending'))
  }
  // Spread ports: N arrows touching one card land at N distinct, edge-sorted
  // points instead of piling every arrowhead on the card's middle pixel.
  const port = new Map()
  const spread = (key, far, setPort) => {
    const groups = new Map()
    for (const e of edges) {
      if (!groups.has(e[key])) groups.set(e[key], [])
      groups.get(e[key]).push(e)
    }
    for (const [, list] of groups) {
      const r = rects[list[0][key]]
      list.sort((a, b) => (rects[a[far]].y + rects[a[far]].h / 2) - (rects[b[far]].y + rects[b[far]].h / 2))
      list.forEach((e, i) => {
        if (!port.has(e)) port.set(e, {})
        setPort(port.get(e), r, r.y + (r.h * (i + 1)) / (list.length + 1))
      })
    }
  }
  spread('from', 'to', (rec, r, y) => { rec.x1 = r.x + r.w; rec.y1 = y })
  spread('to', 'from', (rec, r, y) => { rec.x2 = r.x; rec.y2 = y })
  const paths = []
  edges.forEach((e, i) => {
    const { x1, y1, x2, y2 } = port.get(e)
    const up = states[e.from]?.status || 'pending'
    const down = nodeState(nodes.find(n => n.id === e.to), states, gate)
    const tone = edgeTone(up, down)
    // #48: the flow/shimmer/dead-dash decision is the ONE exported policy
    // (edgeFlowPolicy) — this render reads it, it does not re-decide. F5: the
    // policy gets the readiness input (canRun) derived above, so a join a
    // failed sibling doomed reads dead on EVERY feeding edge, not just the
    // one leaving the failure.
    const policy = edgeFlowPolicy(up, down, e.data, canRunNow(nodes.find(n => n.id === e.to)))
    const d = routeEdge(x1, y1, x2, y2, rects, [e.from, e.to])
    // RC ch4 (identity layer): one deterministic tint per route, cycling by
    // dependency order. The identity stroke rides the SAME routed d as a
    // static 0.8px dashed overlay; matching open-ring echoes mark both ports;
    // the state stroke underneath keeps every incumbent dash/marker law.
    // Nothing here claims a general DAG router or junction semantics.
    const tint = routeTint(i)
    paths.push(
      jsxs('g', {
        children: [
          jsx('title', {
            children: `${e.from} → ${e.to} · ${up} → ${down}${e.data ? ' · data flow' : ''}${policy.dead ? ' · unavailable' : ''}`
          }, 't'),
          jsx('path', {
            d,
            fill: 'none', stroke: policy.shimmer ? NODE_TONE.running.color : tone, strokeWidth: 1.5,
            strokeDasharray: policy.dash ?? undefined,
            markerEnd: `url(#${mid}-${policy.dead ? 'dead' : 'live'})`,
            opacity: up === 'pending' && !e.data ? 0.55 : 0.95,
            // SMIL candy: flowing while live (inline <animate>, no Tailwind
            // animate-*); terminal states never get an <animate> child — the calm
            // law is enforced inside edgeFlowPolicy (flow/shimmer false once calm).
            children: policy.flow || policy.shimmer
              ? jsx('animate', { attributeName: 'stroke-dashoffset', from: 10, to: 0, dur: '0.9s', repeatCount: 'indefinite' })
              : undefined
          }, 'state'),
          jsx('path', {
            d, fill: 'none', stroke: tint, strokeWidth: 0.8, strokeDasharray: '2 3', opacity: 0.85
          }, 'tint'),
          // Endpoint echoes: open rings, same tint, at the exact ports.
          jsx('circle', { cx: x1, cy: y1, r: 3, fill: 'none', stroke: tint, strokeWidth: 1 }, 'echo-src'),
          jsx('circle', { cx: x2, cy: y2, r: 3, fill: 'none', stroke: tint, strokeWidth: 1 }, 'echo-dst')
        ]
      }, `${e.from}->${e.to}${e.data ? ':data' : ''}`)
    )
  })
  if (!paths.length) return null
  return jsxs('svg', {
    className: 'pointer-events-none absolute inset-0 h-full w-full overflow-visible',
    'aria-hidden': true,
    children: [
      jsxs('defs', { children: [
        jsx('marker', { id: `${mid}-live`, viewBox: '0 0 10 10', refX: 10, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto', markerUnits: 'userSpaceOnUse',
          children: jsx('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: 'context-stroke' }) }),
        jsx('marker', { id: `${mid}-dead`, viewBox: '0 0 10 10', refX: 10, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto', markerUnits: 'userSpaceOnUse',
          // F3 (deep review): the dead arrowhead follows the ONE table — it
          // reads NODE_TONE.failed.color at render time like the failed edge
          // stroke does, so a table perturbation moves stroke and head
          // together (the old hardcoded EDGE_TONE.failed drifted on its own).
          children: jsx('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: (NODE_TONE.failed || NODE_TONE.pending).color }) })
      ] }),
      ...paths
    ]
  })
}

/** Fan-out: the real card in front + the numeric items badge.
 *  THE one fan-stack (O4): the page canvas uses the card geometry (badge);
 *  MiniGraph's pills reuse it in pill mode (the pill carries its own ×N count).
 *  RC ch4 (ui2 FINAL incumbent-replacement ledger): the ghost rings/offset
 *  cards are RETIRED — footer ATTEMPT TICKS (3px squares, DESIGN ladder
 *  "Attempts: short footer ticks") replace ghost multiplication, not graph
 *  membership. The numeric terminal/count data the ghosts were decoration for
 *  stays exactly where it was (badge `${terminal}/${count}` / `×${count}`).
 *  Calm by construction: the stack mounts no <animate> in any state — flow
 *  lives only on edges via edgeFlowPolicy (the retired FanStack mapping was
 *  inferred liveness; ticks are static facts). Expanded: no ticks (the real
 *  cards are right there). */
const ATTEMPT_TICK = { size: 3, gap: 2, max: 3 }
export function attemptTicks(count) {
  return Math.min(Math.max((count | 0) - 1, 0), ATTEMPT_TICK.max)
}
export function FanStack({ children, count, terminal, expanded, onToggleExpand, size = 6, pill = false, tone }) {
  const ticks = expanded ? 0 : attemptTicks(count)
  const tickTone = pill ? (tone || (NODE_TONE.pending || {}).color) : EDGE_TONE.skipped
  return jsxs('div', {
    className: 'relative',
    style: { paddingBottom: ATTEMPT_TICK.size + 3 },
    children: [
      jsx('div', { className: 'relative', style: { zIndex: 1 }, children }),
      ticks
        ? jsx('div', {
            'aria-hidden': true,
            title: `${count} fan-out items — ${ticks} more behind this card (footer attempt ticks)`,
            className: 'absolute flex items-center',
            style: { left: 1, bottom: 0, gap: ATTEMPT_TICK.gap, zIndex: 2 },
            children: Array.from({ length: ticks }, (_, i) =>
              jsx('span', {
                style: { display: 'inline-block', width: ATTEMPT_TICK.size, height: ATTEMPT_TICK.size, background: tickTone }
              }, `tick-${i}`))
          }, 'ticks')
        : null,
      // Pill mode carries its own ×N count on the pill itself — no badge.
      pill ? null : onToggleExpand ? jsxs('button', {
        type: 'button',
        title: expanded ? 'Collapse items' : 'Expand items',
        'aria-label': expanded ? 'Collapse fan-out items' : 'Expand fan-out items',
        'aria-expanded': !!expanded,
        onClick: e => { e.stopPropagation(); onToggleExpand() },
        className: 'absolute cursor-pointer rounded-full border text-(--ui-text-secondary)',
        style: {
          zIndex: 2, top: -9, right: -6, padding: '0 6px', fontSize: 10, lineHeight: '16px',
          background: 'var(--ui-sidebar-surface-background, var(--card))',
          borderColor: expanded ? 'var(--ui-accent)' : 'var(--ui-stroke-secondary)',
          color: 'var(--ui-text-secondary)'
        },
        children: [`${terminal != null ? `${terminal}/${count}` : `×${count}`}`, expanded ? ' ▴' : ' ▾']
      }) : jsx('span', {
        className: 'absolute rounded-full border border-(--ui-stroke-secondary) text-(--ui-text-secondary)',
        title: 'Terminal fan-out items — finished, not necessarily successful',
        style: { zIndex: 2, top: -9, right: -6, padding: '0 6px', fontSize: 10, lineHeight: '16px', background: 'var(--ui-sidebar-surface-background, var(--card))' },
        children: terminal != null ? `${terminal}/${count}` : `×${count}`
      })
    ]
  })
}

/** Compact per-item card revealed when a stacked fan-out card is expanded on the
 *  page canvas. Reads the same fanItems rows the stacked badge counts — index,
 *  status, duration, vitals. Clicking it selects the item (same pick as the chips). */
function ItemCard({ runId, def, row, picked, nodeSelected, ms }) {
  return jsxs('button', {
    type: 'button',
    title: row.error || row.goal || undefined,
    onClick: e => {
      e.stopPropagation()
      const on = picked === row.index
      $fanItem.set(on ? null : { runId, nodeId: def.id, index: row.index })
      // The report panel needs the node selected to show the picked item's detail.
      if (!on && !nodeSelected) $selNode.set({ runId, nodeId: def.id })
    },
    className: cn(
      'shrink-0 rounded-md border bg-transparent text-left transition-colors hover:text-foreground',
      picked === row.index ? 'border-(--ui-accent)' : 'border-(--ui-stroke-secondary)'
    ),
    style: { width: 168, background: 'var(--ui-sidebar-surface-background, var(--card))', opacity: row.status === 'pending' ? 0.6 : 1 },
    children: [
      box(
        'flex items-center gap-1.5',
        jsx(Dot, { status: row.status }),
        jsx('span', { className: 'min-w-0 flex-1 truncate text-xs font-medium', children: `#${row.index} ${row.label}` }),
        jsx('span', { className: 'shrink-0 text-[0.6875rem] text-(--ui-text-tertiary)', children: statusLabel(row.status) })
      ),
      box(
        'mt-1 flex items-center gap-1.5 text-[0.6875rem] text-(--ui-text-tertiary)',
        ms ? jsx('span', { children: ms }) : null,
        row.metrics ? jsx(Vitals, { m: row.metrics, live: row.status === 'running', size: 'xs' }) : null
      )
    ]
  }, row.index)
}

export function GraphView({ detail }) {
  const sel = useValue($selNode)
  const fanPicked = useValue($fanItem)
  const expanded = useValue($fanExpanded)
  const canvasRef = useRef(null)
  const nodes = detail.graph?.nodes || []
  const states = detail.nodes || {}
  const isExpanded = def => !!expanded && expanded.runId === detail.id && expanded.nodeId === def.id
  // While expanded, item statuses move mid-run: re-measure so edges track the
  // growing item column (the item-keyed render below keeps scroll position).
  const stateKey = nodes.map(n => `${n.id}:${states[n.id]?.status || ''}${isExpanded(n) ? `:${fanItems(n, states[n.id], detail.events)?.length ?? 0}` : ''}`).join('|')
  const rects = useCardRects(canvasRef, [detail.id, stateKey, nodes.length])
  const picked = fanPicked && fanPicked.runId === detail.id && fanPicked.nodeId === expanded?.nodeId ? fanPicked.index : undefined
  const canvasW = useCanvasWidth(canvasRef, [detail.id, nodes.length])
  // #48: hover lift rides a single hover atom for the canvas (one hook, fixed
  // order, above the empty-graph early return); entering a card lifts it.
  const [hoverId, setHoverId] = useState(null)
  if (!nodes.length) {
    return jsx(EmptyState, { title: 'No graph yet', description: 'The run has not published a graph.' })
  }
  const cols = columnGroups(nodes, depthMap(nodes))
  // #48: items_from data-flow edges (producer card -> fan-out consumer card).
  const dataEdges = nodes.filter(n => n.fanout?.items_from)
    .map(n => ({ from: String(n.fanout.items_from).split('.')[0], to: n.id }))
    .filter(e => nodes.some(p => p.id === e.from))
  const fanMeta = def => {
    if (!def.fanout) return null
    const rows = fanItems(def, states[def.id], detail.events) || []
    const c = fanCounts(rows)
    const started = rows.some(r => r.status !== 'pending')
    return { count: c.total || 2, terminal: started ? c.terminal : null, rows }
  }
  // paddingBottom 48 reserves the gutter routed skip-edges bend into: the
  // SVG layer clips at the canvas's padding box, so routed curves need
  // vertical room below the last card row.
  // WRAP LAW (feedback #10): bandRows packs the depth columns left-to-right
  // into row bands that fit the MEASURED canvas width — when the next column
  // would overflow, it starts a NEW band below, left-anchored. No
  // horizontal scrollbar, no clipping at the window edge; window resize
  // re-measures and re-packs. Column widths come from the same
  // ResizeObserver-measured rects the edges use (card width until first
  // measure). Edges/routeEdge consume the post-wrap rects, so cubics
  // re-route to the new geometry automatically, band-to-band included.
  const availW = canvasW ? Math.max(1, canvasW - 48 * 2) : Infinity
  const bands = bandRows(cols, availW, def => rects[def.id]?.w || CARD_W, 112)
  const column = (d, defs) =>
    jsxs('div', {
      className: 'relative flex shrink-0 flex-col items-start',
      style: { zIndex: 1, gap: 28 },
      children: defs.flatMap(def => {
        const st = states[def.id]
        const card = jsx('div', {
          'data-node': def.id,
          onMouseEnter: () => setHoverId(def.id),
          onMouseLeave: () => setHoverId(h => (h === def.id ? null : h)),
          children: jsx(NodeCard, {
            runId: detail.id, def, st, gate: detail.gate, owner: detail.owner, events: detail.events,
            answered: def.type === 'gate' ? gateAnswerFor(detail, def, st) : null,
            hovered: hoverId === def.id,
            selected: sel?.runId === detail.id && sel?.nodeId === def.id
          })
        }, def.id)
        const fm = fanMeta(def)
        if (!fm) return [card]
        const exp = isExpanded(def)
        // RC ch4: the stack retired its ghost links (attempt ticks are
        // static), so it no longer consumes the flow policy — the live/
        // dataFlow props and their GraphView-side derivation went with them.
        const stack = jsx(FanStack, {
          count: fm.count, terminal: fm.terminal, expanded: exp, children: card,
          onToggleExpand: () => {
            $fanExpanded.set(exp ? null : { runId: detail.id, nodeId: def.id })
            if (exp) $fanItem.set(null)
          }
        }, def.id)
        // Expanded: compact per-item cards as siblings BELOW the stack —
        // never inside the [data-node] rect, so edges keep landing on the
        // stack's front card. Keyed by item index: late arrivals mount at
        // the end and never shift the rows already on screen.
        if (!exp) return [stack]
        return [stack, jsxs('div', {
          className: 'flex flex-col items-start',
          style: { gap: 8, marginTop: -16 },
          children: (fm.rows || []).map(r =>
            jsx(ItemCard, {
              runId: detail.id, def, row: r, picked, ms: fmtDur(r.ms),
              nodeSelected: sel?.runId === detail.id && sel?.nodeId === def.id
            }, r.index))
        }, 'items')]
      })
    }, `col-${d}`)
  return jsxs('div', {
    ref: canvasRef,
    className: 'relative flex items-start flex-col',
    style: { gap: 112, padding: '20px 48px 48px' },
    children: [
      jsx(Edges, { nodes, rects, states, gate: detail.gate, dataEdges }),
      ...bands.map((row, bi) =>
        jsx('div', {
          className: 'flex w-full shrink-0 items-start',
          style: { gap: 112 },
          children: row.map(([d, defs]) => column(d, defs))
        }, `band-${bi}`)
      )
    ]
  })
}

// Wave timeline: one bar per node from node.started -> node.finished/failed on a
// shared run-relative axis. Held gates render as an amber span from gate.held to
// gate.released. Where the time went, at a glance.
function Timeline({ detail }) {
  const sel = useValue($selNode) // hooks first — early returns follow
  useTick(detail.status === 'running') // only a verified runner advances the clock
  const ev = detail.events || []
  const t0 = ev.length ? parseTime(ev[0].ts) : null
  if (!t0) return null
  const spans = new Map()
  const startOf = (id, ts) => { if (!spans.has(id)) spans.set(id, { id, start: ts, end: null, kind: 'node', status: 'running' }) }
  for (const e of ev) {
    const ts = parseTime(e.ts)
    if (!e.node || !ts) continue
    if (e.event === 'node.started') { spans.delete(e.node); startOf(e.node, ts) }
    else if (e.event === 'node.finished' || e.event === 'node.failed') {
      const sp = spans.get(e.node) || { id: e.node, start: ts, end: null, kind: 'node' }
      sp.end = ts; sp.status = e.event === 'node.failed' ? 'failed' : 'done'; spans.set(e.node, sp)
    } else if (e.event === 'gate.held') { spans.delete(e.node); spans.set(e.node, { id: e.node, start: ts, end: null, kind: 'gate', status: 'held' }) }
    else if (e.event === 'gate.released' || e.event === 'gate.skipped' || e.event === 'gate.answered') {
      const sp = spans.get(e.node); if (sp) { sp.end = ts; sp.status = e.on_skip === 'prune' ? 'skipped' : 'done' }
    } else if (e.event === 'node.skipped') {
      spans.set(e.node, { id: e.node, start: ts, end: ts, kind: 'node', status: 'skipped' })
    }
  }
  const last = parseTime(ev[ev.length - 1].ts) || Date.now()
  const live = detail.status === 'running'
  for (const sp of spans.values()) {
    if (!sp.end) sp.status = detail.held_gate?.id === sp.id ? 'held'
      : live && detail.nodes?.[sp.id]?.status === 'running' ? 'running' : 'pending'
  }
  const tEnd = Math.max(live ? Date.now() : last, ...[...spans.values()].map(s => s.end || last))
  const total = Math.max(tEnd - t0, 1)
  const rows = [...spans.values()]
  if (!rows.length) return null
  const pct = v => `${Math.max(0, Math.min(100, ((v - t0) / total) * 100))}%`
  // Right rail: one stacked row per node (id + duration over a full-width bar) — clicking
  // a row selects the node so the wide Report panel shows it.
  return box(
    'flex w-60 shrink-0 flex-col gap-1.5 overflow-y-auto border-l border-(--ui-stroke-secondary) px-3 py-2',
    // WF-06 (QA 2026-10-27): the axis total is the RUN wall measured on the
    // event spine — named so it can't be confused with the header's clock.
    box('mb-1 flex items-center justify-between text-[0.6875rem] text-(--ui-text-tertiary)',
      jsx('span', { children: 'timeline' }), jsx('span', { title: 'run wall span (first → last event)', children: fmtDur(total) })),
    ...rows.map(sp => {
      const end = sp.end || (live ? Date.now() : last)
      const tone = timelineTone(sp)
      const active = sel && sel.runId === detail.id && sel.nodeId === sp.id
      // read-once: the node row can vanish between the guard and the Vitals deref
      const nstate = (detail.nodes || {})[sp.id] || null
      const nmetrics = nstate?.metrics || null
      return jsxs('button', {
        type: 'button',
        onClick: () => { $selNode.set(active ? null : { runId: detail.id, nodeId: sp.id }); $fanItem.set(null); $fanExpanded.set(null) },
        className: cn('flex w-full flex-col gap-0.5 rounded border bg-transparent px-1.5 py-1 text-left text-[0.6875rem] hover:bg-(--chrome-action-hover)',
          active ? 'border-(--ui-stroke-secondary)' : 'border-transparent'),
        children: [
          box('flex items-center justify-between gap-2',
            box('min-w-0 flex-1 truncate text-(--ui-text-secondary)', sp.id),
            // WF-06: each row duration is the CHILD wall for that node
            // (node.started → node.finished on the event spine).
            jsx('span', { className: 'shrink-0 text-(--ui-text-tertiary)', title: 'child wall (node.started → node.finished)', children: fmtDur(end - sp.start) })),
          jsx('div', {
            className: 'relative h-2 w-full rounded-sm bg-(--ui-stroke-secondary)/40',
            children: jsx('div', {
              className: cn('absolute top-0 h-2 rounded-sm', !sp.end && live && 'animate-pulse'),
              style: { left: pct(sp.start), width: `calc(${pct(end)} - ${pct(sp.start)})`, minWidth: 2, background: tone, opacity: sp.kind === 'gate' ? 0.7 : 0.9 }
            })
          }),
          nmetrics
            ? jsx('div', { style: { display: 'flex', justifyContent: 'flex-end' }, children: jsx(Vitals, { m: nmetrics, live: !sp.end && live, size: 'xs', wall: !sp.end && live ? nstate?.wall : null }) })
            : null
        ]
      }, sp.id)
    })
  )
}

// -- O2 NodePanel: one node truth, two readers --------------------------------
// Replaces Drawer + the drawer's ItemDetail use. Every field reads verbatim from
// the record the backend merges into nodes[id] (wfcommon.node_facts via the
// dashboard _view); an absent fact reads `unknown`, never 0 and never fabricated.
// The only text sources are the graph def (already in detail.graph) and the one
// read-only log route — there is NO second prompt assembler here.
const FACT_TONE = 'var(--ui-text-secondary)'
const UNKNOWN = 'unknown'
const TAIL_BYTES = 16384          // the contract's chosen constant, mirrored
const defaultTabFor = st =>
  st === 'running' || st === 'failed' || st === 'partial' ? 'Log' : st === 'done' ? 'Output' : 'Prompt'

// WF-03 (QA 2026-10-27): the backend node_facts substitutes the literal string
// 'unknown' for every absent fact. unk stays the sentinel producer (the O2
// contract — absent reads `unknown`, never a fabricated 0); the NodePanel
// section renderers below HIDE sentinel-valued sections instead of printing
// the raw word (factKnown guards them). The tab bodies keep their ratified
// honest sentences ('prompt: unknown (not persisted)' etc.).
const unk = v => v == null || v === '' ? UNKNOWN : v
const factText = v => typeof v === 'string' ? v : v == null ? UNKNOWN : (() => { try { return JSON.stringify(v, null, 2) } catch { return String(v) } })()
// WF-03 (QA 2026-10-27): logBase/attemptNo are DISPLAY helpers of the panel
// log-head — an absent path/attempt reads an em-dash, never the raw word.
const logBase = p => { const s = String(p ?? ''); const i = s.lastIndexOf('/'); return i < 0 ? (s || '—') : s.slice(i + 1) || '—' }
const attemptNo = facts => {
  const m = /(\d+)\.log$/.exec(String(facts?.log_path ?? ''))
  return m ? m[1] : '—'
}

function useNodeLogTail(runId, nodeId, facts, tab, open, live) {
  // ONE read-only route, the client never sends a path; polled at 4 s only while
  // the panel is open on the Log tab and the node is running.
  const want = open && (tab === 'Log' || tab === 'Prompt') && facts
    && (tab === 'Log' ? facts.log_path : facts.prompt_path)
  const q = want ? `?kind=${tab === 'Log' ? 'log' : 'prompt'}&tail=${TAIL_BYTES}` : null
  return useQuery({
    queryKey: [...Q, 'log', runId, nodeId, q || 'off'],
    enabled: !!q && ID_OK.test(String(runId)) && ID_OK.test(String(nodeId)),
    queryFn: () => api(`/runs/${encodeURIComponent(runId)}/nodes/${encodeURIComponent(nodeId)}/log${q}`),
    refetchInterval: tab === 'Log' && live ? 4000 : false
  })
}

function NodePanel({ detail }) {
  // WF-03 (QA 2026-10-27): the backend node_facts substitutes the literal
  // string 'unknown' for absent facts. On screen that raw sentinel reads like
  // a broken sensor, so every FACTS section HIDES itself when its fact is not
  // known (unk stays the sentinel producer for the data layer; the tab bodies
  // keep their ratified honest sentences). Declared inside the panel so the
  // existing source-grab harnesses keep the whole truth local.
  const factKnown = v => v != null && v !== '' && v !== UNKNOWN
  const sel = useValue($selNode)
  const fanItem = useValue($fanItem)
  const open = !!sel && sel.runId === detail.id && !!detail.graph
  const def = open ? (detail.graph.nodes || []).find(n => n.id === sel.nodeId) : null
  const [tab, setTab] = useState(null)
  const shown = def ? (detail.nodes || {})[def.id] || {} : {}
  const status = shown.status || 'pending'
  const live = status === 'running'
  useTick(live) // only current activity ticks
  const rows = def && def.fanout ? fanItems(def, shown, detail.events) : null
  const picked = rows && fanItem && fanItem.runId === detail.id && fanItem.nodeId === def.id
    ? rows.find(r => r.index === fanItem.index) : null
  // Picking a fan-out item swaps FACTS to that item's record: the backend ships
  // per-item records merged as item_records[i] (same closed key set); where they
  // are absent, the fanItems row is the only truth and every other fact reads
  // `unknown`. Node-level facts arrive merged flat onto nodes[id] (the _view
  // merge of wfcommon.node_facts), so `shown` IS the record read.
  // est-zmpx8: 'refusal' rides the closed set (wfcommon.FACT_KEYS carries it since
  // #584), so the synthesized fan-item shape stays key-complete; an item whose row
  // carries no stamp keeps a null there — the section below hides it, never prints
  // a fabricated one.
  const ITEM_FACTS = ['status', 'error_class', 'refusal', 'error', 'attempts', 'attempts_log', 'final', 'harvest', 'output', 'ms', 'started', 'log_path', 'prompt_path', 'efp', 'skey', 'steer']
  const facts = picked
    ? (shown.item_records && shown.item_records[picked.index])
      || Object.fromEntries(ITEM_FACTS.map(k => k === 'status' ? [k, picked.status]
        : k === 'error_class' ? [k, picked.errorClass ?? null]
        : k === 'refusal' ? [k, picked.refusal ?? null]
        : k === 'error' ? [k, picked.error ?? null]
        : k === 'output' ? [k, picked.output ?? null]
        : k === 'ms' ? [k, picked.ms ?? null] : [k, null]))
    : shown
  const effStatus = (facts && facts.status != null && facts.status !== UNKNOWN ? facts.status : status) || 'pending'
  const name = def ? (picked != null ? `${def.id}·${picked.index}` : def.id) : ''
  // No remembered state: a manual pick lives only for this node+status; a new
  // selection (or a status change) re-derives the default tab.
  const activeTab = (tab && tab[0] === `${name}:${effStatus}` ? tab[1] : null) || defaultTabFor(effStatus)
  const logQ = useNodeLogTail(detail.id, def?.id, facts, activeTab, open && !!def, live && activeTab === 'Log')
  if (!def) return null
  const fc = rows && rows.length ? fanCounts(rows) : null
  const preCls = 'overflow-auto whitespace-pre-wrap break-words rounded border border-(--ui-stroke-secondary) p-2 text-[0.6875rem]'
  const sect = (name, child) => child ? box('flex flex-col gap-1 min-w-0', label(name), child) : null
  const pre = (name, text, tone) => text
    ? sect(name, jsx('pre', {
        style: { color: tone || FACT_TONE, maxHeight: '20vh' },
        className: 'overflow-auto whitespace-pre-wrap break-words rounded border border-(--ui-stroke-secondary) p-2 text-[0.6875rem]',
        children: text }))
    : null
  // FACTS (left column). WF-03 (QA 2026-10-27): a sentinel-valued or absent fact HIDES
  // its section instead of printing the raw word 'unknown' — hidden is honest absence,
  // never a fabricated value; structured facts print as JSON.
  const chip = (text, onClick, on) => jsx('button', {
    type: 'button', onClick,
    style: {
      display: 'inline-flex', alignItems: 'center', height: 18, padding: '0 7px', fontSize: 10,
      lineHeight: 1, whiteSpace: 'nowrap', cursor: 'pointer', borderRadius: 999,
      border: `1px solid ${on ? 'var(--ui-accent)' : 'var(--ui-stroke-secondary)'}`,
      background: 'transparent', color: 'var(--ui-text-secondary)'
    },
    children: text })
  const inputChips = box('flex flex-wrap gap-1',
    ...(def.after || []).map(a => chip(a, () => { $selNode.set({ runId: detail.id, nodeId: a }); $fanItem.set(null) }, false)),
    ...(Array.isArray(def.inputs) ? def.inputs : []).map(s => chip(String(s), undefined, false)))
  const budgetBits = [['max_turns', def.max_turns], ['timeout', def.timeout], ['run_budget', def.run_budget], ['shape', def.shape]]
    .filter(([, v]) => factKnown(v))
  // WF-02: a cancelled class keeps the error text but loses the red tone.
  const cancelledClass = (facts && facts.error_class) === 'cancelled'
    || (picked && picked.errorClass) === 'cancelled'
    || shown.error_class === 'cancelled'
  const steerTrip = facts?.steer
    ? `queued ${unk(facts.steer.queued)} · baked ${unk(facts.steer.baked)} · consumed ${unk(facts.steer.consumed)}`
    : null
  const left = box(
    'flex min-w-0 flex-col gap-3',
    factKnown(def.question) || factKnown(def.goal)
      ? sect(def.type === 'gate' ? 'question' : 'goal',
          box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)', unk(def.type === 'gate' ? def.question : def.goal)))
      : null,
    def.context ? sect('context', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)', def.context)) : null,
    sect('inputs', inputChips),
    def.schema?.required?.length
      ? sect('schema required', box('flex flex-wrap gap-1', ...def.schema.required.map(k => chip(String(k), undefined, false))))
      : null,
    budgetBits.length
      ? sect('budgets', box('flex flex-wrap gap-x-3 gap-y-1 text-[0.6875rem] text-(--ui-text-tertiary)',
          ...budgetBits.map(([k, v]) => jsx('span', { children: `${k}: ${unk(v)}` }))))
      : null,
    Array.isArray(shown.blocked_by) && shown.blocked_by.length
      ? sect('blocked_by', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)', shown.blocked_by.join(', ')))
      : null,
    shown.parked ? sect('parked', box('text-xs text-(--ui-text-secondary)', factText(shown.parked))) : null,
    pre('error', facts && facts.error !== UNKNOWN ? facts.error : shown.error !== UNKNOWN ? shown.error : null, cancelledClass ? undefined : EDGE_TONE.failed),
    // est-zmpx8 (the #584 residual): the refusal stamp — the machine-readable class
    // of a REFUSAL (wf.py `_window_spent_record` → wfcommon.FACT_KEYS `refusal`) —
    // renders verbatim beside the death facts. Same WF-03 discipline as error_class
    // above: a sentinel/absent stamp hides its section, so rule 8 holds both ways —
    // honest absence on screen, never a fabricated value.
    factKnown(facts?.refusal ?? shown.refusal)
      ? sect('refusal', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)',
          unk(facts?.refusal ?? shown.refusal)))
      : null,
    Array.isArray(facts?.attempts_log) && facts.attempts_log.length
      ? sect('attempts_log', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)',
          facts.attempts_log.map(a => `#${a.attempt} ${unk(a.error_class)}`).join(' · ')))
      : null,
    factKnown(facts?.efp) ? sect('efp', box('text-xs text-(--ui-text-secondary)',
      `${facts.efp}${shown.stale_of_amend ? ' · stale of amend' : ''}`)) : null,
    steerTrip ? sect('steer', box('text-xs text-(--ui-text-secondary)', steerTrip)) : null,
    factKnown(facts?.skey) ? sect('skey', box('text-xs select-text text-(--ui-text-tertiary)', facts.skey)) : null,
    fc
      ? box('flex flex-col gap-2',
          label(`items · ${fanSummary(fc)}`),
          jsx(ItemChips, { runId: detail.id, nodeId: def.id, rows, picked: picked?.index }))
      : null
  )
  // TABS (right column): no remembered state across node switches (keyed below).
  const logHead = activeTab === 'Log'
    ? box('text-[0.6875rem] text-(--ui-text-tertiary)', `attempt ${attemptNo(facts)} · ${logBase(facts?.log_path)}`)
    : activeTab === 'Prompt'
      ? box('text-[0.6875rem] text-(--ui-text-tertiary)', logBase(facts?.prompt_path)) : null
  const tabBody = () => {
    if (activeTab === 'Output') {
      const out = fmtOutput(facts?.output ?? shown.output)
      return out
        ? box('flex flex-col gap-1',
            effStatus === 'partial' ? jsx(Badge, { variant: 'outline', children: 'partial — harvested output' }) : null,
            pre('output', out))
        : box('text-xs text-(--ui-text-tertiary)', 'No output yet.')
    }
    if (activeTab === 'Final') {
      const f = facts && typeof facts.final === 'string' ? facts.final : null
      return f ? pre('final', f, status === 'failed' ? EDGE_TONE.failed : FACT_TONE)
        : box('text-xs text-(--ui-text-tertiary)', 'final: unknown')
    }
    if (activeTab === 'Prompt') {
      if (!facts?.prompt_path) return box('text-xs text-(--ui-text-tertiary)', 'prompt: unknown (not persisted)')
      return logQ.data?.content
        ? jsx('pre', { className: preCls, style: { maxHeight: '60vh' }, children: logQ.data.content })
        : box('text-xs text-(--ui-text-tertiary)', logQ.isPending ? 'loading…' : 'prompt: unknown (not persisted)')
    }
    // Log
    return logQ.data?.content
      ? jsx('pre', { className: preCls, style: { maxHeight: '60vh' }, children: logQ.data.content })
      : box('text-xs text-(--ui-text-tertiary)', facts?.log_path ? (logQ.isPending ? 'loading…' : 'log: unknown') : 'log: unknown')
  }
  const right = box(
    'flex min-w-0 flex-col gap-2',
    box('flex items-center gap-1',
      ...['Log', 'Output', 'Prompt', 'Final'].map(t => jsx('button', {
        type: 'button', onClick: () => setTab([`${name}:${effStatus}`, t]),
        style: {
          display: 'inline-flex', height: 20, padding: '0 8px', fontSize: 11, cursor: 'pointer',
          borderRadius: 6, border: `1px solid ${activeTab === t ? 'var(--ui-accent)' : 'var(--ui-stroke-secondary)'}`,
          background: 'transparent', color: 'var(--ui-text-secondary)'
        },
        children: t }, t))),
    logHead,
    box('flex min-h-0 flex-col gap-1', tabBody())
  )
  return box(
    'flex flex-col gap-3 border-t border-(--ui-stroke-secondary) p-4',
    box(
      'flex items-center gap-2',
      jsx(Dot, { status }),
      box('min-w-0 flex-1 truncate text-sm font-medium', name),
      jsx(Badge, { variant: 'outline', children: statusLabel(status) }),
      // F2 desktop (RATIFY): delegation badge — ONLY when the def carries
      // `profile`; a no-team def yields null and the panel is byte-identical.
      def.profile ? jsx('span', { title: `as @${def.profile}`, className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: `as @${def.profile}` }) : null,
      // WF-03: the header never prints a raw sentinel — an unknown error_class
      // hides its chip; the model·provider·reasoning line renders only the
      // parts the record actually carries.
      factKnown(facts?.error_class ?? shown.error_class)
        ? jsx('span', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: unk(facts?.error_class ?? shown.error_class) })
        : null,
      (facts?.attempts ?? shown.attempts) > 1 ? jsx('span', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: `↻${facts.attempts}` }) : null,
      factKnown(def.model) || factKnown(def.provider) || factKnown(def.reasoning)
        ? box('min-w-0 truncate text-[0.6875rem] text-(--ui-text-tertiary)',
            [def.model, def.provider, def.reasoning].filter(factKnown).join(' · '))
        : null,
      shown.metrics ? jsx(Vitals, { m: shown.metrics, live, cost: true, wall: live ? shown.wall : null }) : null,
      jsx(Button, { size: 'xs', variant: 'ghost', 'aria-label': 'Close', onClick: () => { $selNode.set(null); $fanItem.set(null) }, children: '×' })
    ),
    jsx('div', {
      key: `${detail.id}:${name}:${status}`,
      style: { display: 'grid', gridTemplateColumns: 'minmax(260px, 2fr) minmax(0, 3fr)', gap: 16 },
      children: jsxs(Fragment, { children: [left, right] })
    })
  )
}
// L3 calls the panel under the old name; one alias keeps its region unchanged.
const Drawer = NodePanel

export function WorkflowsPage() {
  const list = useQuery(listQuery())
  const selId = useValue($selRun)
  const runs = list.data?.runs || []
  const active = runs.find(r => r.id === selId) || runs[0]
  const detail = useQuery(runQuery(active?.id || '', !!active))
  const d = detail.data
  return box(
    'flex h-full min-h-0',
    box(
      'min-w-0 flex-1 overflow-y-auto',
      !active
        ? jsx(EmptyState, { title: 'Nothing to watch', description: 'No workflow runs reported yet.' })
        : d
          ? (function () {
              const hdr = runHeaderModel(d)
              return jsxs(Fragment, {
              children: [
                // #48: run header strip — one hoisted <style> mounts here so
                // the canvas keyframes exist exactly once per document, then
                // a state-keyed accent GRADIENT bar (runHeaderModel, same
                // tone table as everything else) over the run name / state /
                // elapsed: the tab reads ALIVE while the run lives and CALM
                // once terminal, like RailPanel's measured bar.
                jsx(PolishStyles, {}),
                jsx('span', {
                  'aria-hidden': true,
                  style: { display: 'block', height: 2, background: hdr.gradient }
                }, 'run-accent'),
                box(
                  'flex items-center gap-2 border-b border-(--ui-stroke-secondary) px-4 py-2',
                  jsx(Dot, { status: d.status }),
                  // l8i: the record page heads with the instance label; the
                  // demoted template rides a muted kind badge beside it.
                  box('text-sm font-medium', displayTitle(d)),
                  templateTag(d) ? jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', title: 'template', children: `template ${templateTag(d)}` }) : null,
                  box('text-xs text-(--ui-text-tertiary)', runStatusLabel(d)),
                  // Agent-first (2026-10-03): the record page names the launching
                  // agent next to the state — the same fact the pane row shows,
                  // honest 'unknown' included (deep review #156 A2 — one law,
                  // both surfaces; never a fabricated name).
                  jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', title: 'launched by this agent', children: `@${originLabel(d.owner, d.owner_profile)}` }),
                  // WF-06 (QA 2026-10-27): the record header shows the RUN
                  // wall — the word keeps it distinct from the node cards'
                  // node clocks and the timeline's child spans.
                  hdr.elapsed ? jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', children: `run ${hdr.elapsedLabel}` }) : null,
                  d.metrics ? jsx(Vitals, { m: d.metrics, live: false, size: 'xs', cost: true }) : null,
                  d.metrics?.live ? jsx('span', { className: 'text-(--ui-text-tertiary)', style: { fontSize: 10 }, children: `${d.metrics?.live} live` }) : null,
                  d.held_gate ? jsx(Badge, { variant: 'outline', children: 'gate held' }) : null
                ),
                jsx(GraphView, { detail: d }),
                jsx(Drawer, { detail: d })
              ]
            })
          }())
          : jsx(EmptyState, {
              title: detail.error ? 'Backend unreachable' : 'Loading…',
              description: detail.error ? String(detail.error?.message || detail.error) : undefined
            })
    ),
    active && d ? jsx(Timeline, { detail: d }) : null
  )
}

// -- 3. WORKFLOWS pane (panes area, docked into the sessions strip) -------------
// The pane is the index; the /workflows route is the record. One global live
// count (the tab title); no statusbar chip, no second count anywhere.

function PaneTabTitle() {
  const { data } = useQuery(listQuery())
  return jsx('span', { children: `WORKFLOWS · ${runningCount(data)}` })
}

export function PaneRow({ run, thisChat }) {
  // l8i (instance-label-first law): the fleet landing row has WIDTH, so it is
  // the one surface that keeps a template COLUMN — run.name (the template)
  // renders as a muted column beside the instance label, never as the title.
  const t = templateTag(run)
  const open = () => {
    $selRun.set(run.id)
    $selNode.set(null)
    host.navigate('/workflows')
  }
  // Line 2 is the ONE fact to act on, never a decoration. A held run waits on
  // its ORIGINATING AGENT (owner directive 2026-10-02): the pane is an index,
  // not a queue addressed to its reader — say who the run waits on.
  let fact
  if (run.status === 'held') fact = run.held_gate?.question || `gate · ${run.held_gate?.id || 'unknown'}`
  else if (run.status === 'failed') fact = run.runner_exit?.reason || 'failed'
  else if (run.status === 'interrupted') fact = `interrupted · ${nodesCount(run)}`
  else if (run.status === 'running') {
    const start = parseTime(run.started)
    const elapsed = start ? fmtDur(Date.now() - start) : ''
    const idle = run.metrics ? idleS(run.metrics) : null
    fact = [`${nodesCount(run)}`, elapsed, idleCell(idle)].filter(Boolean).join(' · ')
  } else fact = ago(run.updated)
  return jsx(PanelListRow, {
    active: false,
    lead: jsx(Dot, { status: run.status }),
    title: jsxs('span', {
      className: 'inline-flex min-w-0 items-center gap-1',
      children: [
        jsx('span', { className: 'truncate', children: displayTitle(run) }),
        // l8i: the template COLUMN (the fleet view has the width for it).
        // Unlabeled runs resolve to name, so the column prints only when it
        // is a genuinely SECOND fact (templateTag nulls the duplicate).
        t ? jsx('span', { className: 'shrink-0 text-[0.6875rem] text-(--ui-text-tertiary)', title: 'template', children: t }) : null,
        // Agent-first (2026-10-03): who launched it, on EVERY row — including
        // the honest word 'unknown' when the read model cannot attribute it
        // (deep review #156 A2: 'originator on every row' is the law; silence
        // was a contrary contract). Never a fabricated name.
        jsx('span', { className: 'shrink-0 text-[0.6875rem] text-(--ui-text-tertiary)', title: `launched by @${run.origin || 'unknown'}`, children: `@${run.origin || 'unknown'}` }),
        thisChat ? jsx(PanelPill, { tone: 'muted', children: 'this chat' }) : null
      ]
    }),
    meta: jsx('span', { className: 'max-w-[8rem] truncate', children: fact }),
    onSelect: open,
    rowKey: run.id
  }, run.id)
}

export function WorkflowsPane() {
  const { data, error } = useQuery(listQuery())
  const qc = useQueryClient()
  // Same law as the directive card (test_directive_card_error): data WINS over
  // error. A failed refetch keeps the last good index on screen and says so —
  // the stale chip is a clickable RETRY, and invalidating the runs key re-runs
  // the whole bounded page-walk from offset 0 (no client-side memo to defeat
  // it). The error branch only owns the screen when NOTHING was ever loaded,
  // and it is a button, never a false 'No runs'.
  const retry = () => qc.invalidateQueries({ queryKey: [...Q, 'runs'] })
  const staleChip = error && data
    ? jsx('button', {
        type: 'button', title: 'Retry', onClick: retry,
        style: { cursor: 'pointer', font: 'inherit', color: 'inherit', background: 'none', border: 0, padding: 0 },
        children: ' · stale — retry'
      }, 'census-stale')
    : null
  // Same key pairing as SessionStrip: owner.session_id pairs with the runtime id,
  // both atoms live under host.state (sdk/index.ts:665-697 — see #23).
  const runtimeSid = useValue(focusAtom(host?.state?.focusedSessionId))
  const storedSid = useValue(focusAtom(host?.state?.focusedStoredSessionId))
  const runs = data?.runs || []
  const owned = new Set(ownedRuns(runs, runtimeSid, storedSid).map(r => r.id))
  // Agent-first index (owner 2026-10-03): a human viewer never launches runs,
  // so there is no 'mine' ordering — RUNNING on top, The Rest by last action,
  // every row labelled with its originating bot. The 'this chat' chip stays:
  // it's a fact about the row, not an ownership gate.
  const { running, rest } = paneModel(runs, null)
  // The census counts are the backend's full-census numbers (wfcommon
  // run_summary); absent means unknown, never a fabricated zero. WF-07
  // (QA 2026-10-27): run_summary answers the full-census count at the TOP
  // LEVEL ({total, counts}) — counts carries no total key, so the census
  // reads data.total first (counts.total stays the fallback for legacy
  // payloads; 'runs ?' on a payload that answers a number was the bug).
  // bd_2026-11-13-yjp: the summary stays GLOBAL and distinct from the loaded
  // rows — when the bounded walk could not cover the counted census (a page
  // flaked mid-walk, or the hard page cap was hit) the line says
  // `loaded N of M` instead of implying every counted run is on screen.
  const counts = data?.counts
  const total = data?.total ?? counts?.total
  const loaded = data ? (typeof data.loaded === 'number' ? data.loaded : runs.length) : null
  let census
  if (!counts) census = 'runs unknown'
  else {
    census = `runs ${data?.total ?? counts.total ?? '?'} · running ${counts.running ?? 0} · held ${counts.held ?? 0} · failed ${counts.failed ?? 0}`
    if (typeof total === 'number' && typeof loaded === 'number' && loaded < total)
      census += ` · loaded ${loaded} of ${total}`
  }
  // Agent-first pane law (owner, est-wk7l round): THE REST renders EVERY row —
  // no pane-level cap, no fold. paneModel is uncapped and the consumer must
  // not re-introduce one (the old slice(0,10)+show-all fold made the PR body's
  // "no caps on foreign runs" a lie; the render pin mounts the pane with >10
  // foreign rows to keep them welded together).
  const group = (title, list) => (list.length
    ? [
        jsx(PanelSectionLabel, { children: `${title} · ${list.length}` }, title),
        ...list.map(r => jsx(PaneRow, { run: r, thisChat: owned.has(r.id) }, r.id))
      ]
    : [])
  const body = running.length || rest.length
    ? [
        ...group('RUNNING', running),
        ...group('THE REST', rest)
      ]
    : data
      // A healthily-loaded empty census is the ONLY honest owner of 'No runs'
      // (bd yjp: loading and unreachable must never wear the empty costume).
      // The backend names the scanned roots on an empty census — showing them
      // turns 'nothing found' into 'nothing found WHERE'.
      ? [
          jsx(EmptyState, { title: 'No runs', description: 'Ask the agent to start a workflow.' }, 'empty'),
          Array.isArray(data.roots) && data.roots.length
            ? label(`roots: ${data.roots.join(', ')}`)
            : null
        ]
      : error
        ? jsx('button', {
            type: 'button', title: 'Retry', onClick: retry,
            className: 'self-start text-[0.6875rem] text-(--ui-text-tertiary) cursor-pointer',
            children: `workflows unreachable (${error?.message || error}) — retry`
          }, 'census-error')
        : jsx(EmptyState, { title: 'Loading…' }, 'loading')
  return box(
    'flex h-full min-h-0 flex-col',
    box('px-2 py-1.5 text-[0.6875rem] text-(--ui-text-tertiary)', census, staleChip),
    jsx(ScrollArea, {
      className: 'min-h-0 flex-1',
      children: box(
        'flex flex-col gap-0.5 px-1 pb-2',
        body
      )
    })
  )
}

export default {
  id: ID,
  name: 'Workflows',
  register(ctx) {
    ctxRest = (path, opts) => ctx.rest(path, opts)   // keep the api() error wrapper — never reassign api

    // est-z717 tray settings gate: ONE bootstrap read of the door's owner
    // settings (GET /settings -> {tray}) resolved into $trayGate. FAIL-CLOSED
    // by construction: until the answer arrives $trayGate stays null and the
    // tray hides; a backend error leaves it null (hidden) forever — the
    // default-OFF law (the native tray SDK area #133724 is unlanded).
    api('/settings').then(s => { $trayGate.set(s?.tray === true) }).catch(() => {})

    ctx.register({
      id: 'directive',
      area: TRANSCRIPT_DIRECTIVE_AREA,
      data: { name: 'workflow', render: ({ attrs }) => jsx(DirectiveCard, { id: String(attrs?.id ?? '') }) }
    })

    ctx.register({ id: 'page', area: ROUTES_AREA, data: { path: '/workflows' }, render: () => jsx(WorkflowsPage, {}) })

    // SESSIONS | BOTS | WORKFLOWS: verbatim the hermes-bots pane pattern.
    // dock enforce: standing invariant — the pane re-homes into the sessions
    // strip at EVERY boot it isn't already there. collapsible: it lives in the
    // sessions zone, so it must leave the grid with that zone at the
    // sidebar-collapse breakpoint.
    ctx.register({
      id: 'pane',
      area: PANES_AREA,
      title: 'Workflows',
      data: {
        placement: 'left',
        width: '260px',
        collapsible: true,
        hideOnly: true,
        tabTitle: () => jsx(PaneTabTitle, {}),
        tabTitleText: () => 'Workflows',
        dock: { pane: 'sessions', pos: 'center', enforce: true }
      },
      render: () => jsx(WorkflowsPane, {})
    })

    // Feature-detected composer slot (#22 item 3, chain head added by #230 item 0):
    // sessionStripArea = COMPOSER_AREAS.tray ?? COMPOSER_AREAS.underside ??
    // COMPOSER_AREAS.top. `composer.tray` is the tray accumulation slot (subagents
    // / background scripts / task lists) — NOT SDK-exposed as of
    // hermes-agent@8b66a51036 (the native bar is the internal ComposerStatusStack,
    // composer/index.tsx:1344), so the ask is filed upstream and the head is
    // inert until core adds the key; the day it lands the strip rides the real
    // tray with zero plugin change. `composer.underside` is the floating strip
    // BELOW the composer dock on core >= v2026.7.30 — bottom-anchored, grows
    // upward over the thread, and it is NOT inside the composer-fade div, so it
    // does not dim when the thread scrolls up (composer/index.tsx:1558-1560).
    // COMPOSER_AREAS is an SDK const map, so a key EXISTS ONLY on cores that
    // mount the area — missing key ⇒ undefined ⇒ ?? falls back to today's
    // composer.top on older shells. One mount, never both.
    ctx.register({ id: 'session-strip', area: sessionStripArea(COMPOSER_AREAS), render: () => jsx(SessionStrip, {}) })
  }
}
