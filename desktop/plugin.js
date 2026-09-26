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
const $selRun = atom(null)
const $selNode = atom(null)

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
const statusLabel = s => s || 'unknown'
const nodesCount = r => `${r.nodes_done ?? 0}/${r.nodes_total ?? '?'} terminal`

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
    const status = rec?.status || (verified
      ? (nodeLive && metrics?.live > 0 ? 'running' : ev?.status || 'pending')
      : ev?.status || (legacyDone ? 'done' : nodeLive ? (hasStarts ? (startedIdx.has(i) ? 'running' : 'pending') : 'running') : 'pending'))
    const goal = item && typeof item === 'object' && typeof item.goal === 'string' ? item.goal : fo.goal ? renderGoal(fo.goal, item, i) : ''
    rows.push({
      index: i, status, item, goal,
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

const fanCounts = rows => {
  const counts = { total: rows.length, done: 0, failed: 0, running: 0, skipped: 0, stopped: 0, pending: 0, terminal: 0 }
  for (const row of rows) {
    const status = row.status
    if (status === 'done' || status === 'failed' || status === 'skipped' || status === 'stopped') {
      counts[status]++
      counts.terminal++
    } else if (status === 'running' || status === 'pending') {
      counts[status]++
    }
  }
  return counts
}

const fanSummary = c => `${c.terminal}/${c.total} terminal${c.skipped ? ` ·${c.skipped} skipped` : ''}${c.stopped ? ` ·${c.stopped} stopped` : ''}${c.running ? ` ·${c.running}▶` : ''}${c.failed ? `, ${c.failed} failed` : ''}`

// ---- vitals: dense spend + liveness ----------------------------------------------
// Backend joins each child's state.db sessions row (title = wf:<run>:<node>[:<i>]:<efp8>)
// into node.metrics / node.item_metrics / run.metrics. Liveness is deterministic: while a
// child cooks, api_calls/tool_calls rise and last_activity moves; flat + old = stalling.
const kfmt = n => n == null ? '' : n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e4 ? `${Math.round(n / 1e3)}k` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(n)
const usd = v => v >= 1 ? `$${v.toFixed(2)}` : v >= 0.01 ? `$${v.toFixed(3)}` : `$${v.toFixed(4)}`
const idleS = m => m && m.last_activity ? Math.max(0, Math.round(Date.now() / 1000 - m.last_activity)) : null
// 0–30 s = cooking (accent), 30–90 s = watch (warning), >90 s = stalled (danger)
const idleTone = s => s == null ? EDGE_TONE.pending : s < 30 ? EDGE_TONE.running : s < 90 ? EDGE_TONE.held : EDGE_TONE.failed

/** One dense line: `1.2k▸86 · 3⚡ · 4🔧 [· $0.012]`; live adds a heartbeat `● 4s`. */
function Vitals({ m, live, size, cost }) {
  if (!m) return null
  const fs = size === 'xs' ? 10 : 11
  const sep = jsx('span', { style: { opacity: 0.45 }, children: '·' })
  const parts = []
  if (m.tokens_in != null || m.tokens_out != null) parts.push(jsx('span', { title: `${m.tokens_in ?? 0} in ▸ ${m.tokens_out ?? 0} out${m.cache_read ? ` (${kfmt(m.cache_read)} cached)` : ''}`, children: `${kfmt(m.tokens_in ?? 0)}▸${kfmt(m.tokens_out ?? 0)}` }))
  if (m.api_calls != null) parts.push(jsx('span', { title: 'api calls', children: `${m.api_calls}⚡` }))
  if (m.tool_calls != null) parts.push(jsx('span', { title: 'tool calls', children: `${m.tool_calls}🔧` }))
  if (cost && m.cost) parts.push(jsx('span', { title: 'estimated cost', children: usd(m.cost) }))
  if (m.attempts > 1) parts.push(jsx('span', { title: 'schema/parse retry', children: `↻${m.attempts}` }))
  const s = live ? idleS(m) : null
  const beat = live
    ? jsxs('span', {
        title: m.last_desc ? `last: ${m.last_desc}` : 'seconds since the child last did something',
        style: { display: 'inline-flex', alignItems: 'center', gap: 3, color: idleTone(s), fontVariantNumeric: 'tabular-nums' },
        children: [
          jsx('span', { className: s != null && s < 30 ? 'animate-pulse' : '', style: { display: 'inline-block', width: 6, height: 6, borderRadius: 999, background: idleTone(s) } }),
          jsx('span', { children: s == null ? 'live' : `${s}s` })
        ]
      })
    : null
  const kids = []
  parts.forEach((p, i) => { if (i) kids.push(sep); kids.push(p) })
  if (beat) { if (kids.length) kids.push(sep); kids.push(beat) }
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
    pre('error', row.error, EDGE_TONE.failed),
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
      const tone = r.status === 'done' ? EDGE_TONE.done : r.status === 'failed' ? EDGE_TONE.failed : r.status === 'running' ? EDGE_TONE.running : r.status === 'skipped' || r.status === 'stopped' ? EDGE_TONE.skipped : EDGE_TONE.pending
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
          color: r.status === 'pending' || r.status === 'skipped' || r.status === 'stopped' ? 'var(--ui-text-tertiary)' : 'var(--ui-text-secondary)',
          textDecoration: r.status === 'skipped' ? 'line-through' : 'none'
        },
        children: [jsx(Dot, { status: r.status }), jsx('span', { children: r.label }),
          r.status === 'running' && m
            ? jsx('span', { style: { color: idleTone(idle), opacity: 0.9 }, children: `${calls != null ? calls : '?'}⚡${idle != null ? ` ${idle}s` : ''}` })
            : outTok != null ? jsx('span', { style: { opacity: 0.6 }, children: kfmt(outTok) }) : null]
      }, r.index)
    })
  })
}

function listQuery() {
  return {
    queryKey: [...Q, 'runs'],
    queryFn: () => api('/runs'),
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

function Dot({ status }) {
  if (status === 'running') {
    return jsx('span', { 'aria-hidden': true, className: 'inline-block size-1.5 shrink-0 animate-pulse rounded-full bg-(--ui-accent)' })
  }
  return jsx(StatusDot, {
    tone: status === 'held' ? 'warn' : status === 'done' ? 'good' : status === 'failed' ? 'bad' : 'muted'
  })
}

// -- 1. transcript directive: ::workflow{id="runid"} ---------------------------

function DirectiveCard({ id }) {
  if (!ID_OK.test(id)) {
    return jsx('span', { className: 'text-xs text-(--ui-text-tertiary)', children: 'workflow' })
  }
  return jsx(DirectiveBody, { id })
}

// Two compact rows; absent metrics stay absent, never displayed as zero.
const inlineHeader = (data, elapsed) => {
  const m = data.metrics
  const first = [data.name || data.id, data.status, nodesCount(data)]
  if (elapsed != null) first.push(fmtDur(elapsed))
  const second = []
  if (m) {
    for (const [key, label] of [['tokens_in', 'IN'], ['tokens_out', 'OUT'], ['api_calls', 'API'], ['tool_calls', 'TOOL']]) {
      if (m[key] != null) second.push(`${label} ${kfmt(m[key])}`)
    }
    if (m.cost != null) second.push(`COST ${usd(m.cost)}`)
    if (m.live > 0 && data.status === 'running') {
      second.push(`LIVE ${m.live}`)
      const idle = idleS(m)
      if (idle != null) second.push(`IDLE ${idle}s`)
    }
  }
  return [first, second]
}

// The collapsed-pill model, pure so node can test it without a DOM: one
// line for a transcript card, expanded in place by local useState (never
// localStorage, never tracking whether the agent emitted the card).
export function pillModel(run) {
  const start = parseTime(run?.started)
  const end = TERMINAL.has(run?.status) ? parseTime(run?.updated) : Date.now()
  const bits = [run?.name || run?.id || 'workflow', statusLabel(run?.status), nodesCount(run)]
  const elapsed = start && end > start ? end - start : null
  if (elapsed != null) bits.push(fmtDur(elapsed))
  return { collapsedLine: bits.join(' · '), expanded: false }
}

function DirectiveBody({ id }) {
  const { data, error } = useQuery(runQuery(id))
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
  if (error) return jsx('span', { style: frame, className: 'text-xs text-(--ui-text-tertiary)', children: `workflow ${id}` })
  if (!data) return jsx('span', { style: frame, className: 'text-xs text-(--ui-text-tertiary)', children: 'workflow…' })
  const openRun = e => { if (e) e.stopPropagation(); $selRun.set(data.id); host.navigate('/workflows') }
  const pill = pillModel(data)
  // Collapsed (the default): one line + ▾ toggles expand in place, ↗ opens
  // /workflows explicitly. One click cannot both, so the whole-card navigate
  // onClick is gone — no role=link, the card body is inert chrome.
  if (!open) {
    return jsxs('span', {
      style: { ...frame, flexDirection: 'row', alignItems: 'center', gap: 6, cursor: 'pointer' },
      role: 'button',
      title: 'Expand',
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
  const openDef = fanOpen && fanOpen.runId === data.id ? nodes.find(n => n.id === fanOpen.nodeId && n.fanout) : null
  const rows = openDef ? fanItems(openDef, (data.nodes || {})[openDef.id], data.events) : null
  const picked = fanItem && fanItem.runId === data.id && openDef && fanItem.nodeId === openDef.id ? rows?.find(r => r.index === fanItem.index) : null
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
 *  item's detail. Clicks inside never bubble to the card's navigate. */
function FanStrip({ runId, def, rows, picked }) {
  const c = fanCounts(rows)
  return jsxs('span', {
    onClick: e => e.stopPropagation(),
    style: { display: 'flex', flexDirection: 'column', gap: 6, cursor: 'default', borderTop: '1px solid var(--ui-stroke-secondary)', paddingTop: 6, maxWidth: 520 },
    children: [
      jsxs('span', {
        className: 'flex items-center gap-2 text-[0.6875rem] text-(--ui-text-tertiary)',
        children: [
          jsx('span', { className: 'font-medium text-(--ui-text-secondary)', children: def.id }),
          jsx('span', { children: fanSummary(c) }),
          jsx('button', {
            type: 'button', 'aria-label': 'Collapse', style: { marginLeft: 'auto', cursor: 'pointer', opacity: 0.8 },
            onClick: () => { $fanOpen.set(null); $fanItem.set(null) }, children: '×'
          })
        ]
      }),
      jsx(ItemChips, { runId, nodeId: def.id, rows, picked: picked?.index, size: 'sm' }),
      picked ? jsx(ItemDetail, { row: picked, compact: true }) : null
    ]
  })
}

// Compact DAG for the transcript card: same band-wrap layout + edge tones as
// the page, pills instead of cards. Pills are measured after mount AND every
// column is placed by bandRows, so it shares the page's no-clip no-scroll law.
const CARD_W = 168
const MINI = { pillW: 84, pillH: 20, colGap: 34, rowGap: 6, pad: 4 }
function MiniGraph({ detail }) {
  const ref = useRef(null)
  const nodes = detail.graph?.nodes || []
  const states = detail.nodes || {}
  const gate = detail.gate
  const stateKey = nodes.map(n => `${n.id}:${states[n.id]?.status || ''}`).join('|')
  const rects = useCardRects(ref, [detail.id, stateKey, nodes.length])
  const canvasW = useCanvasWidth(ref, [detail.id, nodes.length])
  const fanOpen = useValue($fanOpen)
  const pill = def => {
    const st = nodeState(def, states, gate)
    const isGate = def.type === 'gate'
    const tone = st === 'done' ? EDGE_TONE.done : st === 'running' ? EDGE_TONE.running : st === 'held' ? EDGE_TONE.held : st === 'failed' ? EDGE_TONE.failed : st === 'skipped' ? EDGE_TONE.skipped : EDGE_TONE.pending
    const fo = def.fanout
    const nstate = states[def.id] || null
    const out = nstate?.output
    // read-once: the guard and the interpolation below share this binding
    const apiCalls = nstate ? nstate.metrics?.api_calls : null
    const items = out && Array.isArray(out.all_results) ? out.all_results.length : out && Array.isArray(out.items) ? out.items.length : Array.isArray(fo?.items) ? fo.items.length : null
    const isOpen = !!fo && fanOpen && fanOpen.runId === detail.id && fanOpen.nodeId === def.id
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
        border: `1px solid ${isOpen ? 'var(--ui-accent)' : tone}`, borderRadius: isGate ? 4 : 999,
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

// -- 1b. composer session strip (composer.top) ----------------------------------
// The runs of the FOCUSED chat, above its composer. Pure core (ownedRuns,
// splitRuns, pillModel) so node can test the model without a DOM; the O3
// pane reuses ownedRuns for its "this chat" tag. Fold state is an in-memory
// plugin atom — never localStorage.

const $stripFold = atom(null) // focused sid while its terminal fold is expanded
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

/** O3 pane action-first grouping: NEEDS YOU (held + failed + interrupted — the
 *  owner must act on all three), RUNNING (running + pending), DONE (done +
 *  stopped). Within each group, newest `updated` first. Pure, so node can
 *  test it without a DOM. */
export function groupRuns(runs) {
  const byUpdated = (a, b) => parseTime(b.updated) - parseTime(a.updated)
  const list = runs || []
  return {
    needsYou: list.filter(r => ['held', 'failed', 'interrupted'].includes(r.status)).sort(byUpdated),
    running: list.filter(r => ['running', 'pending'].includes(r.status)).sort(byUpdated),
    done: list.filter(r => ['done', 'stopped'].includes(r.status)).sort(byUpdated)
  }
}

function StripRow({ run }) {
  const start = parseTime(run.started)
  const end = TERMINAL.has(run.status) ? parseTime(run.updated) : Date.now()
  const [row1, row2] = inlineHeader(run, start && end > start ? end - start : null)
  return jsxs('div', {
    className: 'flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[0.6875rem]',
    children: [
      jsx(Dot, { status: run.status }),
      ...row1.map((text, i) => jsx('span', {
        className: i === 0 ? 'font-medium text-(--ui-text-secondary)' : 'text-(--ui-text-tertiary)',
        children: text
      }, i)),
      ...row2.map((text, i) => jsx('span', {
        className: 'text-(--ui-text-tertiary)', style: { fontSize: 10, fontVariantNumeric: 'tabular-nums' },
        children: text
      }, row1.length + i)),
      run.status === 'held' && run.held_gate
        ? jsx(GateActions, {
            runId: run.id, gate: run.held_gate, owner: run.owner || {},
            // The focused chat IS the owner here — nudgeOwner's hand-off
            // lands in this composer. No new DOM coupling.
          }, 'gate')
        : null
    ]
  })
}

export function SessionStrip() {
  // KEY PAIRING (measured 2026-09-26 against this desktop): run.json.owner.session_id
  // carries the GATEWAY runtime id (`20260923_143041_27e8d2` — state.db sessions.id),
  // owner.ui_session_id carries the DESKTOP stored id (`3184ce5e`). The SDK names them
  // inversely to intuition: host.focusedSessionId is $focusedRuntimeId (the runtime id),
  // host.focusedStoredSessionId is the desktop token. Pair each owner key with its SAME-SHAPE
  // host key; a swapped pair silently renders nothing, which no unit test can see.
  const runtimeSid = useValue(focusAtom(host?.focusedSessionId))
  const storedSid = useValue(focusAtom(host?.focusedStoredSessionId))
  const { data } = useQuery(listQuery())
  const foldOpen = useValue($stripFold)
  const owned = ownedRuns(data?.runs || [], runtimeSid || '', storedSid || '')
  const pairKey = runtimeSid || storedSid || ''
  if (!pairKey || !owned.length) return null
  const { active, overflow, terminalFold, terminalTotal } = splitRuns(owned)
  const openRun = id => { $selRun.set(id); host.navigate('/workflows') }
  const folded = foldOpen !== pairKey
  return box(
    'flex flex-col gap-0.5 border-b border-(--ui-stroke-secondary) px-3 py-1',
    ...active.map(r => jsx(StripRow, { run: r }, r.id)),
    overflow > 0
      ? jsx('button', {
          type: 'button', className: 'text-left text-[0.6875rem] text-(--ui-text-tertiary)',
          style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0 },
          onClick: () => host.navigate('/workflows'),
          children: `+${overflow} more → Workflows`
        })
      : null,
    terminalTotal
      ? jsxs('button', {
          type: 'button', className: 'text-[0.6875rem] text-(--ui-text-tertiary)',
          style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0, textAlign: 'left' },
          onClick: () => $stripFold.set(folded ? pairKey : null),
          children: [`▸ ${terminalTotal} finished`]
        })
      : null,
    !folded
      ? box(
          'flex flex-col gap-0.5 pl-3',
          ...terminalFold.map(r => jsx('button', {
            type: 'button', className: 'text-left text-[0.6875rem] text-(--ui-text-tertiary)',
            style: { cursor: 'pointer', background: 'none', border: 'none', padding: 0 },
            onClick: () => openRun(r.id),
            children: `${r.name || r.id} · ${statusLabel(r.status)} · ${ago(r.updated) || 'unknown'}`
          }, r.id))
        )
      : null
  )
}

// -- 2. page /workflows ---------------------------------------------------------

/** Hand the answer to the agent as a hidden user turn in the ACTIVE chat — the
 *  same door ::preview widgets use (`hermes:composer-submit`, display_kind=hidden).
 *  Fail-closed by design: no visible composer ⇒ false, and we say so. The run
 *  stays owned by the agent: the UI never respawns the runner, it only asks. */
/** Route a gate answer to the run's OWNER session (stamped at spawn by the tool
 *  door: run.json.owner.session_id). host.openSession brings that stored session
 *  to the foreground and awaits hydration; the hidden turn then lands in ITS
 *  composer — not in whichever chat happened to be open. Unknown owner (tests,
 *  CLI spawns, old runs) => fall back to the active composer, and say so. */
async function nudgeOwner(owner, text) {
  const sid = owner?.session_id
  if (sid && host.openSession) {
    try {
      await host.openSession(sid, { awaitHydration: true, expectHistory: true, intent: 'plugin' })
      // give the composer a paint to publish its surface id
      for (let i = 0; i < 20; i++) {
        if (nudgeAgent(text)) return 'owner'
        await new Promise(r => setTimeout(r, 100))
      }
      return 'owner-open-no-composer'
    } catch (e) {
      console.warn('[hermes-workflows] openSession(owner) failed, falling back', e)
    }
  }
  return nudgeAgent(text) ? 'active' : 'none'
}

function nudgeAgent(text) {
  // Mirror focus.ts: the composer publishes `data-composer-target` +
  // `data-composer-surface-id`; the submit handler only honours a VISIBLE one.
  const visible = el => {
    if (!el) return false
    const r = el.getBoundingClientRect()
    return r.width > 0 && r.height > 0
  }
  const candidates = [...document.querySelectorAll('[data-composer-target]')].filter(visible)
  const el = candidates.find(c => c.dataset.composerTarget === 'main') || candidates[0]
  const surfaceId = el?.dataset?.composerSurfaceId
  if (!el || !surfaceId) return false
  try {
    window.dispatchEvent(new CustomEvent('hermes:composer-submit', {
      detail: { surfaceId, target: el.dataset.composerTarget, text, displayKind: 'hidden' }
    }))
    return true
  } catch {
    return false
  }
}

function GateActions({ runId, gate, owner }) {
  const qc = useQueryClient()
  const mut = useMutation({
    mutationFn: answer => api(`/runs/${runId}/gate`, { method: 'POST', body: { gate_id: gate.id, answer } }),
    onSuccess: async (_res, answer) => {
      qc.invalidateQueries({ queryKey: Q })
      const how = await nudgeOwner(owner,
        `Workflow gate answered in the UI: run ${runId}, gate "${gate.id}" → "${answer}". ` +
        `You own this run — resume it now (workflow wait run_id=${runId}).`
      )
      const msg = {
        owner: 'Gate answered — owning agent nudged to resume',
        active: owner?.session_id ? 'Gate answered — owner session unavailable; nudged the active chat instead' : 'Gate answered — run has no recorded owner; nudged the active chat',
        'owner-open-no-composer': 'Gate answered — opened the owner session but found no composer; tell it to resume',
        none: 'Gate answered — no chat composer visible; tell the owning agent to resume the run'
      }[how]
      host.notify({ kind: how === 'owner' ? 'success' : 'info', message: msg })
    },
    onError: err => host.notify({ kind: 'error', message: `Gate answer failed: ${err?.message || err}` })
  })
  if (!gate.options?.length) return null
  return jsxs('div', {
    className: 'flex flex-col border-t border-(--ui-stroke-secondary)',
    style: { gap: 4, padding: '6px 8px 8px' },
    children: [
    gate.question ? box('text-[0.6875rem] leading-snug text-(--ui-text-secondary)', gate.question) : null,
    ...gate.options.map(opt =>
      jsx(
        Button,
        { size: 'xs', variant: 'outline', className: 'w-full justify-start text-[0.6875rem]', disabled: mut.isPending, onClick: () => mut.mutate(opt), children: opt },
        opt
      )
    )
  ] })
}

function NodeCard({ runId, def, st, gate, selected, owner, events }) {
  const isGate = def.type === 'gate'
  const liveGate = gate && gate.id === def.id ? gate : null
  // A live held gate outranks the read model's raw 'pending' node status.
  const status = isGate && liveGate ? 'held' : st?.status || 'pending'
  useTick(status === 'running')
  const rows = def.fanout ? fanItems(def, st, events) : null
  const fc = rows && rows.length ? fanCounts(rows) : null
  const dur = st?.ms ? fmtDur(st.ms) : ''
  const m = st?.metrics || null
  return jsxs(
    'div',
    {
      className: cn(
        'shrink-0 rounded-md border bg-transparent transition-colors',
        (isGate && liveGate) || status === 'running' || selected ? 'border-(--ui-accent)' : 'border-(--ui-stroke-secondary)'
      ),
      style: { width: CARD_W, background: 'var(--ui-sidebar-surface-background, var(--card))', opacity: status === 'pending' ? 0.6 : 1 },
      children: [
        jsxs(
          'button',
          {
            type: 'button',
            onClick: () => {
              const cur = $selNode.get()
              $selNode.set(cur && cur.runId === runId && cur.nodeId === def.id ? null : { runId, nodeId: def.id })
            },
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
                dur ? jsx('span', { children: dur }) : null,
                def.optional ? jsx('span', { children: 'opt' }) : null,
                modelTag(def) ? jsx('span', { title: def.model, style: { marginLeft: 'auto', opacity: 0.85 }, children: modelTag(def) }) : null
              ),
              m ? box('mt-1', jsx(Vitals, { m, live: status === 'running', size: 'xs' })) : null
            ]
          },
          'head'
        ),
        isGate && status === 'held' ? jsx(GateActions, { runId, gate: liveGate || { id: def.id }, owner }) : null
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

function edgeTone(upState, downState) {
  if (upState === 'failed') return EDGE_TONE.failed
  if (upState === 'held') return EDGE_TONE.held
  if (upState === 'done') return downState === 'pending' ? EDGE_TONE.held : EDGE_TONE.done
  if (upState === 'skipped') return EDGE_TONE.skipped
  if (upState === 'running') return EDGE_TONE.running
  return EDGE_TONE.pending
}

const timelineTone = sp => sp.status === 'pending' ? EDGE_TONE.pending
  : sp.status === 'skipped' || sp.status === 'stopped' ? EDGE_TONE.skipped
  : sp.kind === 'gate' && sp.status === 'held' ? EDGE_TONE.held
    : sp.status === 'failed' ? EDGE_TONE.failed
      : sp.status === 'done' ? EDGE_TONE.done
        : EDGE_TONE.running

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

function Edges({ nodes, rects, states, gate }) {
  // Marker ids are document-global in SVG; several graphs on one page (page
  // canvas + N transcript cards) must not share them or arrowheads cross-wire.
  const mid = `wf-arrow-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
  const edges = []
  for (const n of nodes) {
    if (!rects[n.id]) continue
    for (const a of n.after || []) if (rects[a]) edges.push({ from: a, to: n.id })
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
  for (const e of edges) {
    const { x1, y1, x2, y2 } = port.get(e)
    const up = states[e.from]?.status || 'pending'
    const down = nodeState(nodes.find(n => n.id === e.to), states, gate)
    const tone = edgeTone(up, down)
    const dead = up === 'failed'
    // SMIL candy: edges leaving a RUNNING node flow (dash march via inline
    // <animate>, no CSS keyframes — purged-Tailwind-safe). Terminal states
    // stop the animation: no <animate> child leaves a non-running node.
    const flow = up === 'running'
    paths.push(
      jsx('path', {
        d: routeEdge(x1, y1, x2, y2, rects, [e.from, e.to]),
        fill: 'none', stroke: tone, strokeWidth: 1.5,
        strokeDasharray: dead ? '3 3' : flow ? '6 4' : up === 'pending' ? '2 4' : undefined,
        markerEnd: `url(#${mid}-${dead ? 'dead' : 'live'})`,
        opacity: up === 'pending' ? 0.55 : 0.95,
        children: flow
          ? jsx('animate', { attributeName: 'stroke-dashoffset', from: 10, to: 0, dur: '0.9s', repeatCount: 'indefinite' })
          : undefined
      }, `${e.from}->${e.to}`)
    )
  }
  if (!paths.length) return null
  return jsxs('svg', {
    className: 'pointer-events-none absolute inset-0 h-full w-full overflow-visible',
    'aria-hidden': true,
    children: [
      jsxs('defs', { children: [
        jsx('marker', { id: `${mid}-live`, viewBox: '0 0 10 10', refX: 10, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto', markerUnits: 'userSpaceOnUse',
          children: jsx('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: 'context-stroke' }) }),
        jsx('marker', { id: `${mid}-dead`, viewBox: '0 0 10 10', refX: 10, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto', markerUnits: 'userSpaceOnUse',
          children: jsx('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: EDGE_TONE.failed }) })
      ] }),
      ...paths
    ]
  })
}

/** Fan-out: the real card in front, N-1 ghost offsets behind + an items badge.
 *  THE one fan-stack (O4): the page canvas uses the card geometry (size 6,
 *  rounded-md, badge); MiniGraph's pills reuse it with size 2 and the pill
 *  outline tone (pill:true, badge:false — the pill carries its own ×N count).
 *  Expanded (page canvas): the badge becomes a chevron toggle that collapses the
 *  stack back, and the per-item cards render as its sibling (see GraphView). */
function FanStack({ children, count, terminal, expanded, onToggleExpand, size = 6, pill = false, tone }) {
  const ghosts = expanded ? 0 : Math.min(Math.max(count - 1, 0), 3)
  return jsxs('div', {
    className: 'relative',
    style: { paddingRight: ghosts * size, paddingBottom: ghosts * size },
    children: [
      ...Array.from({ length: ghosts }, (_, i) =>
        jsx('div', {
          'aria-hidden': true,
          className: pill ? 'absolute inset-0' : 'absolute inset-0 rounded-md border border-(--ui-stroke-secondary)',
          style: pill
            ? {
                transform: `translate(${(ghosts - i) * size}px, ${(ghosts - i) * size}px)`, zIndex: i,
                right: ghosts * size, bottom: ghosts * size,
                border: `1px solid ${tone}`, borderRadius: 999, opacity: i === ghosts - 1 ? 0.55 : 0.35
              }
            : { transform: `translate(${(ghosts - i) * size}px, ${(ghosts - i) * size}px)`, zIndex: i, right: ghosts * size, bottom: ghosts * size, background: 'var(--ui-sidebar-surface-background, var(--card))' }
        }, `g${i}`)
      ),
      jsx('div', { className: 'relative', style: { zIndex: ghosts + 1 }, children }),
      // Pill mode carries its own ×N count on the pill itself — no badge.
      pill ? null : onToggleExpand ? jsxs('button', {
        type: 'button',
        title: expanded ? 'Collapse items' : 'Expand items',
        'aria-label': expanded ? 'Collapse fan-out items' : 'Expand fan-out items',
        'aria-expanded': !!expanded,
        onClick: e => { e.stopPropagation(); onToggleExpand() },
        className: 'absolute cursor-pointer rounded-full border text-(--ui-text-secondary)',
        style: {
          zIndex: ghosts + 2, top: -9, right: ghosts * 6 - 6, padding: '0 6px', fontSize: 10, lineHeight: '16px',
          background: 'var(--ui-sidebar-surface-background, var(--card))',
          borderColor: expanded ? 'var(--ui-accent)' : 'var(--ui-stroke-secondary)',
          color: 'var(--ui-text-secondary)'
        },
        children: [`${terminal != null ? `${terminal}/${count}` : `×${count}`}`, expanded ? ' ▴' : ' ▾']
      }) : jsx('span', {
        className: 'absolute rounded-full border border-(--ui-stroke-secondary) text-(--ui-text-secondary)',
        title: 'Terminal fan-out items',
        style: { zIndex: ghosts + 2, top: -9, right: ghosts * 6 - 6, padding: '0 6px', fontSize: 10, lineHeight: '16px', background: 'var(--ui-sidebar-surface-background, var(--card))' },
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

function GraphView({ detail }) {
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
  if (!nodes.length) {
    return jsx(EmptyState, { title: 'No graph yet', description: 'The run has not published a graph.' })
  }
  const cols = columnGroups(nodes, depthMap(nodes))
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
        const card = jsx('div', {
          'data-node': def.id,
          children: jsx(NodeCard, {
            runId: detail.id, def, st: states[def.id], gate: detail.gate, owner: detail.owner, events: detail.events,
            selected: sel?.runId === detail.id && sel?.nodeId === def.id
          })
        }, def.id)
        const fm = fanMeta(def)
        if (!fm) return [card]
        const exp = isExpanded(def)
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
      jsx(Edges, { nodes, rects, states, gate: detail.gate }),
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
    box('mb-1 flex items-center justify-between text-[0.6875rem] text-(--ui-text-tertiary)',
      jsx('span', { children: 'timeline' }), jsx('span', { children: fmtDur(total) })),
    ...rows.map(sp => {
      const end = sp.end || (live ? Date.now() : last)
      const tone = timelineTone(sp)
      const active = sel && sel.runId === detail.id && sel.nodeId === sp.id
      // read-once: the node row can vanish between the guard and the Vitals deref
      const nmetrics = (detail.nodes || {})[sp.id]?.metrics || null
      return jsxs('button', {
        type: 'button',
        onClick: () => { $selNode.set(active ? null : { runId: detail.id, nodeId: sp.id }); $fanItem.set(null); $fanExpanded.set(null) },
        className: cn('flex w-full flex-col gap-0.5 rounded border bg-transparent px-1.5 py-1 text-left text-[0.6875rem] hover:bg-(--chrome-action-hover)',
          active ? 'border-(--ui-stroke-secondary)' : 'border-transparent'),
        children: [
          box('flex items-center justify-between gap-2',
            box('min-w-0 flex-1 truncate text-(--ui-text-secondary)', sp.id),
            box('shrink-0 text-(--ui-text-tertiary)', fmtDur(end - sp.start))),
          jsx('div', {
            className: 'relative h-2 w-full rounded-sm bg-(--ui-stroke-secondary)/40',
            children: jsx('div', {
              className: cn('absolute top-0 h-2 rounded-sm', !sp.end && live && 'animate-pulse'),
              style: { left: pct(sp.start), width: `calc(${pct(end)} - ${pct(sp.start)})`, minWidth: 2, background: tone, opacity: sp.kind === 'gate' ? 0.7 : 0.9 }
            })
          }),
          nmetrics
            ? jsx('div', { style: { display: 'flex', justifyContent: 'flex-end' }, children: jsx(Vitals, { m: nmetrics, live: !sp.end && live, size: 'xs' }) })
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
const unk = v => v == null || v === '' ? UNKNOWN : v
const factText = v => typeof v === 'string' ? v : v == null ? UNKNOWN : (() => { try { return JSON.stringify(v, null, 2) } catch { return String(v) } })()
const logBase = p => { const s = String(p ?? ''); const i = s.lastIndexOf('/'); return i < 0 ? (s || UNKNOWN) : s.slice(i + 1) }
const attemptNo = facts => {
  const m = /(\d+)\.log$/.exec(String(facts?.log_path ?? ''))
  return m ? m[1] : UNKNOWN
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
  const ITEM_FACTS = ['status', 'error_class', 'error', 'attempts', 'attempts_log', 'final', 'harvest', 'output', 'ms', 'started', 'log_path', 'prompt_path', 'efp', 'skey', 'steer']
  const facts = picked
    ? (shown.item_records && shown.item_records[picked.index])
      || Object.fromEntries(ITEM_FACTS.map(k => k === 'status' ? [k, picked.status]
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
  // FACTS (left column). Absent facts read `unknown`; structured facts print as JSON.
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
  const left = box(
    'flex min-w-0 flex-col gap-3',
    def.type === 'gate'
      ? sect('question', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)', unk(def.question)))
      : sect('goal', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)', unk(def.goal))),
    def.context ? sect('context', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)', def.context)) : null,
    sect('inputs', inputChips),
    sect('schema required', box('flex flex-wrap gap-1',
      ...(def.schema?.required?.length ? def.schema.required.map(k => chip(String(k), undefined, false))
        : [box('text-xs text-(--ui-text-tertiary)', UNKNOWN)]))),
    sect('budgets', box('flex flex-wrap gap-x-3 gap-y-1 text-[0.6875rem] text-(--ui-text-tertiary)',
      jsx('span', { children: `max_turns: ${unk(def.max_turns)}` }),
      jsx('span', { children: `timeout: ${unk(def.timeout)}` }),
      jsx('span', { children: `run_budget: ${unk(def.run_budget)}` }),
      jsx('span', { children: `shape: ${unk(def.shape)}` }))),
    sect('blocked_by', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)',
      Array.isArray(shown.blocked_by) && shown.blocked_by.length ? shown.blocked_by.join(', ') : UNKNOWN)),
    shown.parked ? sect('parked', box('text-xs text-(--ui-text-secondary)', factText(shown.parked))) : null,
    pre('error', facts && facts.error !== UNKNOWN ? facts.error : shown.error, EDGE_TONE.failed),
    sect('attempts_log', box('text-xs whitespace-pre-wrap text-(--ui-text-secondary)',
      Array.isArray(facts?.attempts_log) && facts.attempts_log.length
        ? facts.attempts_log.map(a => `#${a.attempt} ${unk(a.error_class)}`).join(' · ') : UNKNOWN)),
    sect('efp', box('text-xs text-(--ui-text-secondary)',
      `${unk(facts?.efp)}${shown.stale_of_amend ? ' · stale of amend' : ''}`)),
    sect('steer', box('text-xs text-(--ui-text-secondary)',
      facts?.steer ? `queued ${facts.steer.queued ?? UNKNOWN} · baked ${facts.steer.baked ?? UNKNOWN} · consumed ${facts.steer.consumed ?? UNKNOWN}` : UNKNOWN)),
    sect('skey', box('text-xs select-text text-(--ui-text-tertiary)', unk(facts?.skey))),
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
      jsx('span', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: unk(facts?.error_class ?? shown.error_class) }),
      (facts?.attempts ?? shown.attempts) > 1 ? jsx('span', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: `↻${facts.attempts}` }) : null,
      box('min-w-0 truncate text-[0.6875rem] text-(--ui-text-tertiary)',
        `${unk(def.model)} · ${unk(def.provider)} · ${unk(def.reasoning)}`),
      shown.metrics ? jsx(Vitals, { m: shown.metrics, live, cost: true }) : null,
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

function WorkflowsPage() {
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
          ? jsxs(Fragment, {
              children: [
                box(
                  'flex items-center gap-2 border-b border-(--ui-stroke-secondary) px-4 py-2',
                  jsx(Dot, { status: d.status }),
                  box('text-sm font-medium', d.name || d.id),
                  box('text-xs text-(--ui-text-tertiary)', statusLabel(d.status)),
                  d.metrics ? jsx(Vitals, { m: d.metrics, live: false, size: 'xs', cost: true }) : null,
                  d.metrics?.live ? jsx('span', { className: 'text-(--ui-text-tertiary)', style: { fontSize: 10 }, children: `${d.metrics?.live} live` }) : null,
                  d.held_gate ? jsx(Badge, { variant: 'outline', children: 'gate held' }) : null
                ),
                jsx(GraphView, { detail: d }),
                jsx(Drawer, { detail: d })
              ]
            })
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

function PaneRow({ run, thisChat }) {
  const open = () => {
    $selRun.set(run.id)
    $selNode.set(null)
    host.navigate('/workflows')
  }
  // Line 2 is the ONE fact to act on, never a decoration.
  let fact
  if (run.status === 'held') fact = run.held_gate?.question || `gate · ${run.held_gate?.id || 'unknown'}`
  else if (run.status === 'failed') fact = run.runner_exit?.reason || 'failed'
  else if (run.status === 'interrupted') fact = `interrupted · ${nodesCount(run)}`
  else if (run.status === 'running' || run.status === 'pending') {
    const start = parseTime(run.started)
    const elapsed = start ? fmtDur(Date.now() - start) : ''
    const idle = run.metrics ? idleS(run.metrics) : null
    fact = [`${nodesCount(run)}`, elapsed, idle != null ? `IDLE ${idle}s` : null].filter(Boolean).join(' · ')
  } else fact = ago(run.updated)
  return jsx(PanelListRow, {
    active: false,
    lead: jsx(Dot, { status: run.status }),
    title: jsxs('span', {
      className: 'inline-flex min-w-0 items-center gap-1',
      children: [
        jsx('span', { className: 'truncate', children: run.name || run.id }),
        thisChat ? jsx(PanelPill, { tone: 'muted', children: 'this chat' }) : null
      ]
    }),
    meta: jsx('span', { className: 'max-w-[8rem] truncate', children: fact }),
    onSelect: open,
    rowKey: run.id
  }, run.id)
}

function WorkflowsPane() {
  const { data } = useQuery(listQuery())
  // Same key pairing as SessionStrip: owner.session_id pairs with the runtime id.
  const runtimeSid = useValue(focusAtom(host?.focusedSessionId))
  const storedSid = useValue(focusAtom(host?.focusedStoredSessionId))
  const [showAllDone, setShowAllDone] = useState(false)
  const runs = data?.runs || []
  const owned = new Set(ownedRuns(runs, runtimeSid, storedSid).map(r => r.id))
  const { needsYou, running, done } = groupRuns(runs)
  // The census counts are the backend's full-census numbers (wfcommon
  // run_summary); absent means unknown, never a fabricated zero.
  const counts = data?.counts
  const census = counts
    ? `runs ${counts.total ?? '?'} · running ${counts.running ?? 0} · held ${counts.held ?? 0} · failed ${counts.failed ?? 0}`
    : 'runs unknown'
  const doneShown = showAllDone ? done : done.slice(0, 10)
  const group = (title, list) => (list.length
    ? [
        jsx(PanelSectionLabel, { children: `${title} · ${list.length}` }, title),
        ...list.map(r => jsx(PaneRow, { run: r, thisChat: owned.has(r.id) }, r.id))
      ]
    : [])
  return box(
    'flex h-full min-h-0 flex-col',
    box('px-2 py-1.5 text-[0.6875rem] text-(--ui-text-tertiary)', census),
    jsx(ScrollArea, {
      className: 'min-h-0 flex-1',
      children: box(
        'flex flex-col gap-0.5 px-1 pb-2',
        runs.length
          ? [
              ...group('NEEDS YOU', needsYou),
              ...group('RUNNING', running),
              ...group('DONE', doneShown),
              !showAllDone && done.length > 10
                ? jsx(Button, { size: 'xs', variant: 'ghost', onClick: () => setShowAllDone(true), children: `show all ${done.length}` }, 'show-all')
                : null
            ]
          : jsx(EmptyState, { title: 'No runs', description: 'Ask the agent to start a workflow.' })
      )
    })
  )
}

export default {
  id: ID,
  name: 'Workflows',
  register(ctx) {
    ctxRest = (path, opts) => ctx.rest(path, opts)   // keep the api() error wrapper — never reassign api

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

    ctx.register({ id: 'session-strip', area: COMPOSER_AREAS.top, render: () => jsx(SessionStrip, {}) })
  }
}
