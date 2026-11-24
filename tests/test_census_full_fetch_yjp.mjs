// bd_2026-11-13-yjp: the full-census fetch and coverage-state binding.
// Behavior, not strings: a fake /runs server that PAGES (default window 100 —
// the route's real contract, pinned server-side by test_runs_offloop_ey31s
// pin P and tests/test_census_pages_full_yjp.py) drives the ACTUAL transport
// (runsIndexFetcher) and the ACTUAL pane component (mounted with stubbed SDK
// atoms, house pattern of test_pane_render_uncapped.mjs).
//
// Pins (each maps to an acceptance bullet):
//  (1) >100 rows: every counted run reachable, exact page requests, no
//      duplicate and no lost page.
//  (2) unstable snapshots across a TTL boundary: ids deduped, never doubled.
//  (3) mid-walk shrink: stop at the empty page, loaded<total reported — the
//      pane renders the partial honestly, the summary stays global.
//  (4) unknown totals: no `total` key -> walk while pages are full; the
//      total is never fabricated (census line says 'runs unknown').
//  (5) the walk is BOUNDED: a server whose answer never covers stops at the
//      hard page cap instead of hammering forever.
//  (6) cancellation: an aborted signal (react-query cancels on invalidate /
//      unmount / key change) stops the walk — no further requests, and the
//      half-walk result is never written. No cross-wiring of runs.
//  (7) pane honesty: cached data WINS over a refetch error (stale chip is the
//      error's costume, clickable), the never-loaded error branch is a retry
//      BUTTON (never a false 'No runs'), loading renders 'Loading…', and
//      only a healthy empty census may say 'No runs' (with the roots it
//      scanned). Retry REALLY invalidates: the click calls
//      invalidateQueries on ['hermes-workflows','runs'] — the queryFn re-
//      walks from offset 0 (no client-side memo exists to defeat it).
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const here = dirname(new URL(import.meta.url).pathname)
const src = readFileSync(join(here, '..', 'desktop', 'plugin.js'), 'utf8')

const tmp = mkdtempSync(join(tmpdir(), 'wf-census-yjp-'))
const jsxPath = join(tmp, 'jsx-stub.mjs')
writeFileSync(jsxPath, `
export const jsx = (type, props, key) => ({ type, props: props || {}, key })
export const jsxs = jsx
export const Fragment = 'Fragment'
`)
const reactPath = join(tmp, 'react-stub.mjs')
writeFileSync(reactPath, `
export const useEffect = () => {}, useId = () => 't-0', useRef = () => ({ current: null }), useState = i => [typeof i === 'function' ? i() : i, () => {}]
export default { useEffect, useId, useRef, useState }
`)
const sdkPath = join(tmp, 'sdk-stub.mjs')
writeFileSync(sdkPath, `
const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export { atom }
export const atom0 = atom
export const Badge = 'Badge', Button = 'Button', cn = (...a) => a.filter(Boolean).join(' ')
export const Codicon = 'Codicon', EmptyState = 'EmptyState', ScrollArea = 'ScrollArea'
export const StatusDot = 'StatusDot', PanelListRow = 'PanelListRow', PanelPill = 'PanelPill'
export const PanelSectionLabel = 'PanelSectionLabel'
export const host = { state: { focusedStoredSessionId: atom(''), focusedSessionId: atom('') }, navigate: () => {} }
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
// The mounted pane reads whatever the LAST setState call installed; the last
// invalidateQueries calls are recorded for the retry pin.
export const useQuery = () => globalThis.__WF_STATE__
export const useQueryClient = () => ({ invalidateQueries: q => (globalThis.__WF_INV__ ||= []).push(q) })
export const ROUTES_AREA = 'routes', PANES_AREA = 'panes', TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directives'
export const COMPOSER_AREAS = { top: 'composer.top' }
export const useMutation = () => ({})
`)
const modPath = join(tmp, 'plugin-under-test.mjs')
writeFileSync(modPath, src
  .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
  .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href))
  .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href)))
const mod = await import(pathToFileURL(modPath).href)

// -- fake paging server ------------------------------------------------------
// Mirrors the real route: windowed slice over one census, whole-census
// summary on every page (total/counts are CENSUS-wide by contract).
function makeServer(rows, { withTotal = true, overlap = 0, shrink = null, lie = false } = {}) {
  const calls = []
  return {
    calls,
    async request(path) {
      const url = new URL('http://x' + path)
      const offset = Number(url.searchParams.get('offset') || 0)
      const limit = Number(url.searchParams.get('limit') || 100)
      calls.push({ offset, limit })
      let page = rows.slice(offset, offset + limit)
      if (overlap && offset > 0) {
        // an unstable snapshot: the previous window's last rows repeat here
        page = rows.slice(Math.max(0, offset - overlap), offset + limit)
      }
      if (shrink !== null && offset >= shrink) page = []
      const body = { runs: page, counts: { running: rows.filter(r => r.status === 'running').length } }
      if (withTotal) body.total = lie ? rows.length + 1000 : rows.length
      return body
    }
  }
}
const row = i => ({ id: `20990101-${String(i).padStart(6, '0')}-yjp`, name: `run ${i}`, status: 'done', updated: '2099-01-01T00:00:00+00:00' })

// (1) >100 rows: every counted run reachable; exact requests; no dupes/loss.
{
  const N = 237
  const rows = Array.from({ length: N }, (_, i) => row(i))
  const srv = makeServer(rows)
  const out = await mod.runsIndexFetcher(srv.request)()
  assert.equal(out.runs.length, N, 'the merged index carries EVERY counted run, not page 1')
  assert.deepEqual(out.runs.map(r => r.id), rows.map(r => r.id), 'ids and order are complete — no lost page')
  assert.equal(new Set(out.runs.map(r => r.id)).size, N, 'no duplicate row')
  assert.deepEqual(srv.calls, [{ offset: 0, limit: 100 }, { offset: 100, limit: 100 }, { offset: 200, limit: 100 }],
    'requests are exact page windows — the walk is bounded per page, no bespoke cap')
  assert.equal(out.total, N, 'the global summary rides through from the census')
  assert.equal(out.loaded, N, 'coverage: loaded equals the counted total')
}

// (2) unstable snapshots across the 2 s TTL boundary dedupe by id.
{
  const rows = Array.from({ length: 150 }, (_, i) => row(i))
  const srv = makeServer(rows, { overlap: 3 })
  const out = await mod.runsIndexFetcher(srv.request)()
  assert.equal(out.runs.length, 150, 'a row repeated across two scans lands ONCE')
  assert.equal(new Set(out.runs.map(r => r.id)).size, out.runs.length, 'never doubled')
}

// (3) mid-walk shrink: stop at the empty page; loaded<total is HONEST, the
// counted total is never rewritten down to what happened to load.
{
  const rows = Array.from({ length: 237 }, (_, i) => row(i))
  const srv = makeServer(rows, { shrink: 200 })
  const out = await mod.runsIndexFetcher(srv.request)()
  assert.equal(out.runs.length, 200, 'the walk stopped at the empty page')
  assert.equal(out.total, 237, 'the counted census is NOT rewritten down to the loaded rows')
  assert.equal(out.loaded, 200, 'loaded reports the shortfall — the pane renders the partial')
  assert.equal(srv.calls.length, 3, 'no request after the empty page')
}

// (4) unknown totals stay unavailable: no `total` key -> walk while full.
{
  const rows = Array.from({ length: 137 }, (_, i) => row(i))
  const srv = makeServer(rows, { withTotal: false })
  const out = await mod.runsIndexFetcher(srv.request)()
  assert.equal(out.runs.length, 137, 'short page ends the walk without any total')
  assert.equal(srv.calls.length, 2, 'exactly ceil(137/100) requests — stopped at the short page')
  assert.equal('total' in out, false, 'no total key was fabricated')
}

// (5) bounded: a server whose pages never "cover" stops at the hard cap.
{
  let i = 0
  const srv = { calls: [], async request(path) {
    const url = new URL('http://x' + path)
    srv.calls.push(Number(url.searchParams.get('offset')))
    const page = Array.from({ length: 100 }, () => row(i++))
    return { runs: page } // no total, forever-full pages
  } }
  const out = await mod.runsIndexFetcher(srv.request)()
  assert.equal(srv.calls.length, 30, 'hard page cap 30 — the walk is finite')
  assert.equal(out.runs.length, 3000, 'what loaded stays visible (rendered as a partial)')
}

// (6) cancellation: session-change/invalidate cancels the walk, mid-page.
{
  const rows = Array.from({ length: 237 }, (_, i) => row(i))
  const ac = new AbortController()
  const srv = makeServer(rows)
  const wrapped = async path => { const p = await srv.request(path); if (srv.calls.length === 1) ac.abort(); return p }
  await assert.rejects(mod.runsIndexFetcher(wrapped)({ signal: ac.signal }), /cancel/)
  assert.equal(srv.calls.length, 1, 'the walk issued no second page after cancellation — no cross-wired merge of a stale walk')
}
{
  const srv = makeServer(Array.from({ length: 237 }, (_, i) => row(i)))
  const ac = new AbortController()
  ac.abort()
  await assert.rejects(mod.runsIndexFetcher(srv.request)({ signal: ac.signal }), /cancel/)
  assert.equal(srv.calls.length, 0, 'a cancelled query never starts a walk')
}

// (7) listQuery transport shape (what react-query mounts).
{
  const q = mod.listQuery ? mod.listQuery() : null
  assert.ok(q, 'listQuery exported for the contract pin')
  assert.deepEqual(q.queryKey, ['hermes-workflows', 'runs'], 'ONE runs key — the pane, tab title, tray and page share it')
  assert.equal(typeof q.queryFn, 'function', 'queryFn is the paged fetcher')
}

// -- pane state mounts (real component, stubbed data channel) ----------------
function mount(state) {
  globalThis.__WF_STATE__ = state
  globalThis.__WF_INV__ = []
  return mod.WorkflowsPane()
}
const walkTree = (node, fn) => {
  if (node == null) return
  if (Array.isArray(node)) return node.forEach(n => walkTree(n, fn))
  if (typeof node !== 'object') return
  fn(node)
  walkTree(node.props?.children, fn)
}
const texts = tree => {
  const t = []
  const w = n => {
    if (n == null) return
    if (Array.isArray(n)) return n.forEach(w)
    if (typeof n === 'string') return t.push(n) // bare string child (box(..., census))
    if (typeof n !== 'object') return
    if (typeof n.props?.children === 'string') t.push(n.props.children)
    w(n.props?.children)
  }
  w(tree)
  return t.join(' | ')
}
const buttons = tree => { const b = []; walkTree(tree, n => { if (n.type === 'button') b.push(n) }); return b }
const emptyStates = tree => { const e = []; walkTree(tree, n => { if (n.type === 'EmptyState') e.push(n.props.title) }); return e }

const FLEET100 = Array.from({ length: 100 }, (_, i) => row(i)).map(r => ({ ...r, owner: { session_id: '20260101_000000_x' } }))

// (7a) cached data WINS over a refetch error: rows render, a clickable STALE
// chip carries the error — and clicking it invalidates the runs key (retry
// really re-walks: the fetcher has no memo, offset 0 is re-requested).
{
  const tree = mount({ data: { runs: FLEET100, total: 100, loaded: 100, counts: { running: 0 } }, error: new Error('401') })
  assert.match(texts(tree), /runs 100 · running 0/, 'the census line renders from the cached payload')
  const stale = buttons(tree).find(b => String(b.props.children).includes('stale'))
  assert.ok(stale, 'a refetch failure shows the stale chip, it does not evict the rows')
  stale.props.onClick({})
  assert.deepEqual(globalThis.__WF_INV__, [{ queryKey: ['hermes-workflows', 'runs'] }],
    'stale-chip click invalidates the LIST key — retry re-walks every page')
}

// (7b) partial coverage renders as a partial: the global summary and the
// loaded rows are DISTINCT facts on one honest line.
{
  const tree = mount({ data: { runs: FLEET100, total: 237, loaded: 100, counts: { running: 0 } } })
  assert.match(texts(tree), /runs 237 · running 0 · held 0 · failed 0 · loaded 100 of 237/,
    'counted total stays 237 while loaded reports 100')
}

// (7c) unknown totals remain unavailable.
{
  const tree = mount({ data: { runs: FLEET100 } })
  assert.match(texts(tree), /runs unknown/)
}

// (7d) never-loaded error: a RETRY BUTTON, never a false 'No runs'.
{
  const tree = mount({ data: undefined, error: new Error('backend down') })
  assert.ok(!emptyStates(tree).includes('No runs'), 'unreachable must not wear the empty costume')
  const retry = buttons(tree).find(b => String(b.props.children).includes('retry'))
  assert.ok(retry, 'the error branch is clickable')
  assert.match(String(retry.props.children), /backend down/, 'the failure reason is visible')
  retry.props.onClick({})
  assert.deepEqual(globalThis.__WF_INV__, [{ queryKey: ['hermes-workflows', 'runs'] }],
    'error-branch retry invalidates the runs key too')
}

// (7e) loading: no data, no error -> Loading…, never 'No runs'.
{
  const tree = mount({ data: undefined, error: null })
  assert.deepEqual(emptyStates(tree), ['Loading…'])
}

// (7f) a healthy empty census is the ONLY owner of 'No runs' — and it names
// the roots it scanned.
{
  const tree = mount({ data: { runs: [], total: 0, loaded: 0, counts: { running: 0 }, roots: ['/home/u/.hermes/workflows'] } })
  assert.deepEqual(emptyStates(tree), ['No runs'], 'empty says empty only when the census ANSWERED empty')
  assert.match(texts(tree), /roots: \/home\/u\/\.hermes\/workflows/, 'where it looked is honest, not fabricated')
}

console.log('ALL PASS: full-census fetch — paged, deduped, bounded, cancellable; pane states honest')
