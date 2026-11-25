// bd_2026-11-13-cj2: stored-session navigation is fail-closed and side-effect
// free. Behavior-level (the bead bans string-match-only acceptance): every
// rule below drives the REAL module through the same stub-host harness idiom
// as test_composer_owner.mjs — the spy ledger proves the call counts, the
// rendered tree proves the states.
// Laws pinned here:
//   1. IDs come only from recorded fields (metrics.session_ids / the owner
//      stamp); runtime-shaped IDs are dropped, never repaired, never swapped
//      for another session's ID.
//   2. The adapter makes EXACTLY ONE host.openSession per user action, with
//      options drawn from the real SDK PluginOpenSessionOptions union (the
//      wire-time inspection named the union explicitly; no invented readOnly).
//   3. Missing/expired/unverified ID or an absent adapter renders
//      'Session unavailable' and makes ZERO host calls.
//   4. A rejection stays a local error state with the exact ID — no second
//      call, no composer submit/insert, no notify, no fallback session.
//   5. Rotation: the link always rides the CURRENT recorded ID (last entry of
//      the shipped list), never a cached first ID.
//   6. Back/focus restoration is a one-shot module token, never core storage.
//   7. Gate 'View exact gate' after the viewer changed runs navigates on the
//      TOAST's own run identity, never the stale selection.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const tmp = mkdtempSync(join(tmpdir(), 'wf-nav-cj2-'))
try {
  const src = readFileSync(new URL('../desktop/plugin.js', import.meta.url), 'utf8')

  globalThis.__calls = []        // every host surface call, in order
  globalThis.__reject = false    // flip: host.openSession starts refusing
  globalThis.__state = {}
  globalThis.__ref = { current: { focus: () => { globalThis.__calls.push(['focus-link']) } } }

  const stubSdk = `
export const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export const Badge='Badge', cn=()=>'', Codicon='Codicon', COMPOSER_AREAS={}, EmptyState='EmptyState',
  PANES_AREA='panes', PanelListRow='PanelListRow', PanelPill='PanelPill', PanelSectionLabel='PanelSectionLabel',
  ROUTES_AREA='routes', ScrollArea='ScrollArea', StatusDot='StatusDot',
  TRANSCRIPT_DIRECTIVE_AREA='transcript.directives', Button='button'
export const useMutation = () => ({ isPending: false, mutate: () => {} })
export const useQueryClient = () => ({ invalidateQueries: () => {} })
export const useQuery = () => ({ data: null, error: null })
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
export const host = {
  state: { focusedSessionId: atom(''), focusedStoredSessionId: atom('') },
  navigate: p => { globalThis.__calls.push(['navigate', p]) },
  notify: n => { globalThis.__calls.push(['notify', n.kind]) },
  composer: {
    submit: (sid, t) => { globalThis.__calls.push(['submit', sid]); return true },
    insertText: (sid, t) => { globalThis.__calls.push(['insert', sid]); return Promise.resolve(true) }
  },
  openSession: async (id, opts) => {
    globalThis.__calls.push(['openSession', id, JSON.stringify(opts || null)])
    if (globalThis.__reject) throw new Error('stale binding')
  }
}
`
  const stubReact = `
export const useEffect = fn => { globalThis.__effects.push(fn) }
export const useId = () => 't-0'
export const useRef = () => (globalThis.__ref)
export const useState = init => {
  const k = 'st' + (globalThis.__si = (globalThis.__si || 0) + 1)
  if (!(k in globalThis.__state)) globalThis.__state[k] = typeof init === 'function' ? init() : init
  const set = v => { globalThis.__state[k] = typeof v === 'function' ? v(globalThis.__state[k]) : v }
  return [globalThis.__state[k], set]
}
export default { useEffect, useId, useRef, useState }
`
  const stubJsx = `
export const jsx = (type, props, key) => ({ type, props: props || {}, key })
export const jsxs = jsx
export const Fragment = 'Fragment'
`
  const sdkPath = join(tmp, 'sdk-stub.mjs'), reactPath = join(tmp, 'react-stub.mjs')
  const jsxPath = join(tmp, 'jsx-stub.mjs'), modPath = join(tmp, 'plugin-under-test.mjs')
  writeFileSync(sdkPath, stubSdk)
  writeFileSync(reactPath, stubReact)
  writeFileSync(jsxPath, stubJsx)
  writeFileSync(modPath, src
    .replaceAll("'@hermes/plugin-sdk'", JSON.stringify(pathToFileURL(sdkPath).href))
    .replaceAll("'react'", JSON.stringify(pathToFileURL(reactPath).href))
    .replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href)))
  globalThis.__effects = []
  const mod = await import(pathToFileURL(modPath).href)
  const {
    storedSessionIds, latestStoredSessionId, ownerStoredSessionId,
    openRecordedSession, SessionLink, markNavFocus, consumeNavFocus,
    gateViewAction, $selRun, $selNode
  } = mod

  const A = 'local-' + 'a'.repeat(64)
  const B = 'local-' + 'b'.repeat(64)
  const C = 'local-' + 'c'.repeat(64)
  const RUNTIME = '20260923_143041_27e8d2'

  const render = props => {
    globalThis.__effects = []
    globalThis.__si = 0
    const tree = SessionLink(props)
    globalThis.__effects.forEach(f => f())
    return tree
  }
  const remount = () => { globalThis.__state = {} }
  const textOf = node => {
    if (node == null || typeof node === 'boolean') return ''
    if (typeof node === 'string') return node
    if (Array.isArray(node)) return node.map(textOf).join(' ')
    if (node && typeof node.type === 'function') return textOf(node.type(node.props))
    return textOf(node.props && node.props.children)
  }
  const buttons = node => {
    const out = []
    const walk = n => {
      if (n == null || typeof n === 'boolean' || typeof n === 'string') return
      if (Array.isArray(n)) return n.forEach(walk)
      if (n && n.type === 'button') out.push(n.props)
      if (n && typeof n.type === 'function') return walk(n.type(n.props))
      walk(n && n.props && n.props.children)
    }
    walk(node)
    return out
  }
  const openCalls = () => globalThis.__calls.filter(c => c[0] === 'openSession')

  // -- 1. selectors: recorded fields only, runtime IDs dropped ---------------
  {
    assert.deepEqual(storedSessionIds({ session_ids: [A, RUNTIME, B, 42, null, 'local-zz'] }), [A, B],
      'runtime-shaped and malformed entries are dropped; recorded order survives')
    // Wave A review counterexample (additional-boundaries.json): the read model ships
    // attempts in (started_at, rowid) order, so the OLDER #a2@t2 -> A lands FIRST and
    // the NEWER #a10@t10 -> B lands LAST. Order survives the selector verbatim — it
    // never re-sorts (that lexicon is what opened the older chat). Matching backend
    // pin at the production seam: tests/test_stored_session_order_cj2.py.
    assert.deepEqual(storedSessionIds({ session_ids: [A, B] }), [A, B],
      'chronological entries pass through in the shipped order, unsorted')
    assert.equal(latestStoredSessionId({ session_ids: [A, B] }), B, 'the link rides the NEWEST recorded attempt')
    assert.equal(latestStoredSessionId({ session_ids: [A, RUNTIME] }), A,
      'a fresher runtime-shaped entry is dropped, never substituted — the newest recorded-shape entry is the honest destination')
    assert.equal(latestStoredSessionId({ session_ids: [] }), null, 'an empty list is honest absence')
    assert.equal(latestStoredSessionId(undefined), null, 'absent metrics is absence, not a crash')
    assert.equal(ownerStoredSessionId({ ui_session_id: '  ' + A + '  ', session_id: B }), A,
      'the designated ui stamp wins (trimmed)')
    assert.equal(ownerStoredSessionId({ ui_session_id: null, session_id: A }), A,
      'a stored-SHAPED session_id is the recorded owner (measured desktop launch shape)')
    assert.equal(ownerStoredSessionId({ ui_session_id: null, session_id: RUNTIME }), null,
      'a runtime-shaped session_id NEVER becomes a guessed destination')
    assert.equal(ownerStoredSessionId(null), null, 'absence stays absence')
  }

  // -- 2. the adapter: ONE call, real-union options, or zero ------------------
  {
    const h = { openSession: async (id, opts) => { globalThis.__calls.push(['openSession', id, JSON.stringify(opts || null)]) } }
    const r = await openRecordedSession(h, A)
    assert.equal(r.ok, true, 'a recorded id opens')
    const [name, id, opts] = openCalls().at(-1)
    assert.equal(name, 'openSession')
    assert.equal(id, A, 'the call carries the opaque recorded id verbatim')
    const o = JSON.parse(opts)
    assert.deepEqual(Object.keys(o), ['intent'],
      'only real SDK options ride — no invented readOnly, no stray keys')
    assert.ok(['in-place', 'main', 'stack', 'tab', 'window'].includes(o.intent),
      'intent is a member of the inspected OpenSessionIntent union')

    assert.equal((await openRecordedSession(h, '')).ok, false, 'empty id refuses')
    assert.equal((await openRecordedSession(h, '  \x01 ')).ok, false, 'blank/control id refuses')
    assert.equal((await openRecordedSession(h, null)).ok, false, 'absent id refuses')
    assert.equal(openCalls().length, 1, 'every refusal made NO host call — the count is the law')
    assert.equal((await openRecordedSession({}, A)).reason, 'host session adapter absent')
    assert.equal((await openRecordedSession(null, A)).reason, 'host session adapter absent')
    assert.equal(openCalls().length, 1, 'an absent adapter is fail-closed with zero calls')
  }

  // -- 3. SessionLink: live link, rotation, and the zero-call states ---------
  {
    // live link: button + the full id visible (identity, never a short key)
    remount()
    let t = render({ storedId: latestStoredSessionId({ session_ids: [A, B] }) })
    assert.ok(buttons(t).some(b => b.children === 'open recorded chat'), 'an explicit labeled link renders')
    assert.ok(textOf(t).includes(B), 'the full recorded id renders beside the link')
    assert.ok(!textOf(t).includes('Session unavailable'), 'no unavailable row while the link is live')

    // click: exactly one openSession on the CURRENT (newest) id
    globalThis.__calls.length = 0
    await buttons(t).find(b => b.children === 'open recorded chat').onClick()
    assert.equal(openCalls().length, 1, 'one user action, one call')
    assert.equal(openCalls()[0][1], B, 'rotation law: the click rides the NEWEST recorded id')
    assert.equal(globalThis.__calls.filter(c => ['submit', 'insert', 'notify'].includes(c[0])).length, 0,
      'read-only viewing: zero composer submit/insert and zero notify')

    // rotation between fetches: the re-rendered link uses the FRESH id, never the stale one
    t = render({ storedId: latestStoredSessionId({ session_ids: [C] }) })
    globalThis.__calls.length = 0
    await buttons(t).find(b => b.children === 'open recorded chat').onClick()
    assert.equal(openCalls()[0][1], C, 'a rotated recorded session re-lands the link on the fresh id')

    // unverified/missing id: unavailable, zero calls, no composer fallback.
    // The WIRED shape: a runtime-id-only row yields null from the selector —
    // the unavailable state is what the user sees, with no attempted jump.
    for (const bad of [undefined, null,
                       latestStoredSessionId({ session_ids: [RUNTIME] }),
                       latestStoredSessionId({ session_ids: [] })]) {
      remount()
      globalThis.__calls.length = 0
      t = render({ storedId: bad, note: 'no verified recorded session' })
      assert.ok(textOf(t).includes('Session unavailable · no verified recorded session'),
        `unverified id ${JSON.stringify(bad)} renders the honest unavailable state`)
      assert.equal(openCalls().length, 0, 'unavailable states make no navigation call')
    }

    // adapter rejection: local error state, the id stays inspectable, NO second call
    remount()
    globalThis.__calls.length = 0
    globalThis.__reject = true
    t = render({ storedId: A })
    await buttons(t).find(b => b.children === 'open recorded chat').onClick()
    assert.equal(openCalls().length, 1, 'a refusal is never retried behind the user’s back')
    t = render({ storedId: A })
    assert.ok(textOf(t).includes('Session unavailable · host refused'),
      'the rejection renders as the local unavailable/error state')
    assert.ok(textOf(t).includes(A), 'the exact id stays visible for inspection/copy')
    assert.equal(buttons(t).filter(b => b.children === 'open recorded chat').length, 0,
      'the refused link does not stay armed as if nothing happened')
    globalThis.__reject = false
  }

  // -- 4. back/focus restoration: one-shot module token, never core storage --
  {
    remount()
    globalThis.__calls.length = 0
    markNavFocus('R1:work')
    assert.equal(consumeNavFocus('R1:work'), true, 'the first render of the launching link restores focus')
    assert.equal(consumeNavFocus('R1:work'), false, 'exactly once — a later mount must not steal focus')
    markNavFocus('R1:work')
    assert.equal(consumeNavFocus('R2:work'), false, 'restoration is keyed to the SAME run/node, never a stale surface')
    const callsBefore = globalThis.__calls.length
    render({ storedId: A, focusKey: 'R1:owner' })
    assert.equal(consumeNavFocus('R1:owner'), false, 'an unmatched key consumed nothing')
    // a focused restore lands on the plugin-owned link (spy event), touching no core surface
    markNavFocus('R1:nf')
    remount()
    render({ storedId: A, focusKey: 'R1:nf' })
    assert.ok(globalThis.__calls.some(c => c[0] === 'focus-link'), 'restore focuses the link itself')
    assert.equal(globalThis.__calls.length, callsBefore + 1, 'restoration is one focus event — no navigation, no composer, no storage write')
  }

  // -- 5. gate cross-surface law: never reuse the stale selection ------------
  {
    $selRun.set('R1'); $selNode.set(null)
    gateViewAction('R2', 'review').onClick()   // the viewer sits on R1; the toast rode R2
    assert.equal($selRun.get(), 'R2', 'View exact gate selects the TOAST run, never the stale selection')
    assert.deepEqual($selNode.get(), { runId: 'R2', nodeId: 'review' },
      'and that toast’s exact gate — identity comes from the action, not the viewer’s history')
    assert.ok(globalThis.__calls.some(c => c[0] === 'navigate' && c[1] === '/workflows'),
      'the jump routes to the record page')
    assert.equal(openCalls().length, 0, 'gate navigation never reaches for openSession')
  }

  console.log('ALL PASS test_stored_session_nav (recorded-id-only selectors; one-call fail-closed adapter; ' +
    'unavailable/absent/rejected states make zero calls; rotation rides the fresh id; ' +
    'one-shot focus restoration; gate navigation ignores the stale selection)')
} finally { rmSync(tmp, { recursive: true, force: true }) }
