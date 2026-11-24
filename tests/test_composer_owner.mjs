// bd_2026-11-13-qri: the gate answer surface is the ONE decision surface.
// The retired nudgeOwner chain (composer submit/insertText/hydration, the
// "resume it now" turn, the five toast variants) is DELETED with no compat
// shim; this test drives the real module and the spy proves zero composer
// submit/insert/hydrate/nudge/resume calls across every answer flow:
// held -> pending -> saved receipt -> View exact gate (same-run identity),
// plus no-options, conflict/stale ok:false treated as an ERROR, requester
// identity and focus restoration.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const tmp = mkdtempSync(join(tmpdir(), 'wf-gate-flows-'))
try {
  const src = readFileSync(new URL('../desktop/plugin.js', import.meta.url), 'utf8')

  // -- 0. deletion laws (the repo's established idiom for retired paths) ------
  // The cj2 stored-session-nav block is the ONE legal home of openSession:
  // a read-only conversation link, proven by tests/test_stored_session_nav.mjs.
  // The retired-chain scan applies to everything OUTSIDE that marked block;
  // section 7 keeps its global BEHAVIOR pin — no answer flow may call the
  // openSession spy, inside or outside the block.
  const navBlock = src.match(/\/\/ BEGIN stored-session-nav\n([\s\S]*?)\/\/ END stored-session-nav/)
  assert.ok(navBlock, 'plugin.js ships one marked stored-session-nav block')
  const outsideNav = src.replace(/\/\/ BEGIN stored-session-nav\n[\s\S]*?\/\/ END stored-session-nav/g, '')
  for (const gone of [/nudgeOwner/, /composer\.submit/, /composer\.insertText/,
                      /openSession/, /awaitHydration/, /resume it now/,
                      /press Enter there to resume/]) {
    assert.doesNotMatch(outsideNav, gone, `${gone} is retired with nudgeOwner — no compat shim outside the marked nav block`)
  }
  assert.match(navBlock[1], /openSession/, 'the nav block is where the legal openSession call lives')

  globalThis.__calls = []        // every host surface call, in order
  globalThis.__notifs = []       // notify payloads (action objects included)
  globalThis.__rest = []         // REST calls through register()'s ctx.rest
  globalThis.__postResult = { ok: true }
  globalThis.__pending = false
  globalThis.__invalidations = 0
  globalThis.__receiptRef = { current: null }
  globalThis.__state = {}        // slot-backed component state (fresh mount = reset)

  const stubSdk = `
export const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export const Badge='Badge', cn=()=>'', Codicon='Codicon', COMPOSER_AREAS={}, EmptyState='EmptyState',
  PANES_AREA='panes', PanelListRow='PanelListRow', PanelPill='PanelPill', PanelSectionLabel='PanelSectionLabel',
  ROUTES_AREA='routes', ScrollArea='ScrollArea', StatusDot='StatusDot',
  TRANSCRIPT_DIRECTIVE_AREA='transcript.directives', Button='button'
export const useMutation = opts => { globalThis.__mut = opts
  return { isPending: !!globalThis.__pending, mutate: a => { globalThis.__mutated.push(a) } } }
export const useQueryClient = () => ({ invalidateQueries: () => { globalThis.__invalidations++ } })
export const useQuery = () => ({ data: null, error: null })
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
export const host = {
  state: { focusedSessionId: atom(''), focusedStoredSessionId: atom('') },
  navigate: p => { globalThis.__calls.push(['navigate', p]) },
  notify: n => { globalThis.__calls.push(['notify', n.kind]); globalThis.__notifs.push(n) },
  composer: {
    submit: (sid, t) => { globalThis.__calls.push(['submit', sid]); return true },
    insertText: (sid, t) => { globalThis.__calls.push(['insert', sid]); return Promise.resolve(true) }
  },
  openSession: async id => { globalThis.__calls.push(['openSession', id]) }
}
`
  const stubReact = `
export const useEffect = fn => { globalThis.__effects.push(fn) }
export const useId = () => 't-0'
export const useRef = () => (globalThis.__receiptRef)
export const useState = init => {
  // call-slot state: renders re-run GateActions in a fixed hook order, so a
  // setter from one render lands in the next render (behaviour, not a no-op).
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
  globalThis.__mutated = []
  const mod = await import(pathToFileURL(modPath).href)
  const { GateActions, gateRequester, gateAnswerFor, $selRun, $selNode } = mod
  assert.equal(typeof GateActions, 'function', 'GateActions is exported (the single decision surface)')

  // register the real way: the module wires ctxRest through default.register
  mod.default.register({
    rest: async (path, opts) => {
      globalThis.__rest.push([path, opts && opts.method, opts && opts.body])
      if (path === '/settings') return { tray: false }
      return globalThis.__postResult
    },
    register: () => {}
  })
  await new Promise(r => setTimeout(r, 0)) // the /settings bootstrap read

  // -- render + effect runner --------------------------------------------------
  const render = props => {
    globalThis.__effects = []
    globalThis.__si = 0
    const tree = GateActions(props)
    globalThis.__effects.forEach(f => f()) // effects run synchronously, as after paint
    return tree
  }
  const remount = () => { globalThis.__state = {} } // a fresh component instance
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
  const GATE = { id: 'review', question: 'Save this review decision?',
    options: ['Approve review', 'Keep for revision'], context: 'Isolated review workflow' }
  const OWNER = { session_id: 'owner-sess' }

  // -- 1. held: verbatim question, declared requester, every option enabled ----
  {
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    const text = textOf(t)
    assert.ok(text.includes('Save this review decision?'), 'question renders verbatim')
    assert.ok(text.includes('requester: Isolated review workflow'),
      'the graph-declared requester renders (identity, never the viewer)')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.equal(opts.length, 2, 'every recorded option is a button')
    assert.ok(opts.every(b => b.disabled === false), 'idle options are enabled')
  }

  // -- 2. no options: fail closed with a visible reason, no buttons invented ---
  {
    const t = render({ runId: 'R1', gate: { id: 'review', question: 'Q?', options: [] }, owner: OWNER, events: [] })
    const text = textOf(t)
    assert.ok(text.includes('No answer options recorded.'), 'options-less hold says so — never a silent nothing')
    assert.equal(buttons(t).length, 0, 'no option buttons on an options-less hold')
  }

  // -- 3. pending: EVERY option disabled (duplicate prevention) + saving row ---
  {
    globalThis.__pending = true
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(t).includes('Saving answer…'), 'pending says Saving answer…')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.ok(opts.length === 2 && opts.every(b => b.disabled === true),
      'pending disables every option — no duplicate write behind a slow POST')
    globalThis.__pending = false
  }

  // -- 4. mutation identity: ONE POST, body names gate + exact answer ----------
  {
    globalThis.__postResult = { ok: true, at: '2026-11-23T03:00:00+00:00' }
    const res = await globalThis.__mut.mutationFn('Approve review')
    assert.deepEqual(res, { ok: true, at: '2026-11-23T03:00:00+00:00' },
      'ok:true resolves with the durable receipt timestamp the door stamped')
    const post = globalThis.__rest.at(-1)
    assert.deepEqual(post, ['/runs/R1/gate', 'POST', { gate_id: 'review', answer: 'Approve review' }],
      'the write carries the SAME-run gate identity and the exact answer')
  }

  // -- 5. success: invalidation, ONE receipt toast, same-run View action -------
  {
    globalThis.__notifs.length = 0
    globalThis.__receiptRef.current = { focus: () => { globalThis.__calls.push(['focus-receipt']) } }
    globalThis.__mut.onSuccess({ ok: true, at: '2026-11-23T03:00:00+00:00' }, 'Approve review')
    assert.ok(globalThis.__invalidations >= 1, 'the census is invalidated before any re-read')
    const notif = globalThis.__notifs.find(n => n.kind === 'success')
    assert.ok(notif, 'a success receipt toast fires')
    assert.equal(notif.message,
      '◇ Answer saved · Approve review · Isolated review workflow · R1 / review · 2026-11-23T03:00:00+00:00',
      'the toast IS the receipt: answer saved, exact answer, requester, run / gate, server-stamped time (Q2)')
    assert.equal(notif.action.label, 'View exact gate', 'the toast action is the exact-gate jump')
    $selRun.set('OTHER') // viewer was somewhere else — the click must re-point identity
    $selNode.set(null)
    notif.action.onClick()
    assert.equal($selRun.get(), 'R1', 'View exact gate selects the SAME run the answer rode')
    assert.deepEqual($selNode.get(), { runId: 'R1', nodeId: 'review' },
      'and the EXACT gate — never a historical seed or a bare run')
    assert.ok(globalThis.__calls.some(c => c[0] === 'navigate' && c[1] === '/workflows'),
      'the jump routes to the record page')
    const tLocal = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(tLocal).includes('Answer saved · nothing will be sent on this path.'),
      'the receipt renders in place from this write, before any refetch lands')
    assert.ok(textOf(tLocal).includes('Answered · 2026-11-23T03:00:00+00:00'),
      'the pre-refetch receipt already carries the DOOR-stamped time, not a client clock')
  }

  // -- 5a. SAME-MOUNT refetch (review-2 Q1): the durable record outranks the
  //     local write state; the dwell freezes at the server `at`, never at
  //     "current time". No remount here — the bug lived exactly there.
  {
    const HELD = [{ event: 'gate.held', node: 'review', ts: '2026-11-23T02:55:00+00:00' }]
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER,
      answered: { answer: 'Approve review', at: '2026-11-23T03:00:00+00:00', _ui: true },
      events: HELD })
    const text = textOf(t)
    assert.ok(text.includes('held 5m'),
      'same-mount refetch: dwell is the FIXED recorded age (5m), not now-minus-held (Q1)')
    assert.ok(text.includes('Answered · 2026-11-23T03:00:00+00:00'),
      'the durable server timestamp renders once the read model carries it')
    // Durable truth outranks the optimistic local record: if the read model
    // shows a different answer (amend + re-answer beat our paint), the
    // receipt shows the SERVER answer, not what this click optimistically held.
    const tConflict = render({ runId: 'R1', gate: GATE, owner: OWNER,
      answered: { answer: 'Keep for revision', at: '2026-11-23T04:00:00+00:00', _ui: true },
      events: HELD })
    const ctext = textOf(tConflict)
    assert.ok(ctext.includes('Keep for revision') && !ctext.includes('Approve review'),
      'a refetched durable answer outranks the pre-refetch local record — only the server answer renders')
    assert.ok(ctext.includes('held 1h 5m'), 'dwell re-anchors to the durable at (1h 5m)')
    // Honest unknown: a receipt with no timestamp says so, never a silent drop.
    remount()
    globalThis.__mut.onSuccess({ ok: true }, 'Approve review') // older door: no at
    const tUnknown = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(tUnknown).includes('Answered · time not recorded'),
      'absent timestamp renders as honest unknown')
    assert.ok(globalThis.__notifs.at(-1).message ===
      '◇ Answer saved · Approve review · Isolated review workflow · R1 / review',
      'a receipt toast without a server time honestly omits the time')
  }

  // -- 5b. saved receipt renders from the READ MODEL (survives the refetch) ---
  {
    remount() // no local state: the receipt must come from the read model alone
    globalThis.__receiptRef.current = { focus: () => { globalThis.__calls.push(['focus-receipt']) } }
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER,
      answered: { answer: 'Approve review', at: '2026-11-23T03:00:00+00:00', _ui: true },
      events: [{ event: 'gate.held', node: 'review', ts: '2026-11-23T02:55:00+00:00' }] })
    const text = textOf(t)
    assert.ok(text.includes('Answer saved · nothing will be sent on this path.'), 'saved receipt copy')
    assert.ok(text.includes('Approve review'), 'the chosen answer renders verbatim')
    assert.ok(text.includes('held 5m'), 'dwell is the recorded gate.held -> answer age (5m)')
    assert.ok(text.includes('Nothing restarted'), 'the nothing-restarted line shows')
    assert.ok(text.includes('isolated runner'),
      'the nothing-restarted copy is scoped to the tested isolated runner, not a universal scheduler claim')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.equal(opts.length, 0, 'the saved surface has NO option buttons — a historical seed is never re-answerable')
    assert.ok(buttons(t).some(b => b.children === 'View exact gate'), 'the receipt carries the same View action')
    assert.ok(globalThis.__calls.filter(c => c[0] === 'focus-receipt').length >= 1,
      'focus is restored onto the receipt when the options unmount')
  }

  // -- 6. ok:false is an ERROR, never a successful mutation --------------------
  {
    globalThis.__postResult = { ok: false, error: 'gate already answered (current graph)' }
    await assert.rejects(() => globalThis.__mut.mutationFn('Keep for revision'),
      /gate already answered \(current graph\)/,
      'an {ok:false} door answer rejects — onSuccess can never see it')
    // fresh mount (no local record) BEFORE the refusal lands, so the inline
    // error state is the component's own, not residue from the success above:
    remount()
    globalThis.__notifs.length = 0
    globalThis.__mut.onError(new Error('gate already answered (current graph)'))
    assert.equal(globalThis.__notifs.find(n => n.kind === 'success'), undefined,
      'a refused answer never receipts as success')
    const err = globalThis.__notifs.find(n => n.kind === 'error')
    assert.ok(err && /Gate answer failed/.test(err.message), 'the refusal toasts as an error')
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(t).includes('Gate answer failed · gate already answered (current graph)'),
      'the conflict/stale answer renders inline')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.ok(opts.length === 2 && opts.every(b => !b.disabled),
      'after an error the options stay retryable (nothing was consumed)')
  }

  // -- 7. the spy ledger: zero composer submit/insert/hydrate/nudge/resume ----
  {
    const seen = globalThis.__calls.map(c => c[0])
    for (const banned of ['submit', 'insert', 'openSession']) {
      assert.equal(seen.filter(k => k === banned).length, 0,
        `the whole answer flow makes zero ${banned} calls (nudgeOwner path is gone)`)
    }
  }

  // -- 8. requester + receipt-source purity ------------------------------------
  {
    assert.equal(gateRequester({ context: '  Declared Lane  ' }, null), 'Declared Lane',
      'a declared context trims and wins')
    assert.equal(gateRequester({}, { session_id: 'cron_7' }), '@cron', 'a cron-shaped owner labels honestly')
    assert.equal(gateRequester({}, {}), '@unknown', 'absence is unknown, never fabricated')
    assert.deepEqual(gateAnswerFor({ gates: { review: { answer: 'a', at: 'x' } } }, { id: 'review' }, null),
      { answer: 'a', at: 'x' }, 'the gates block is the durable receipt source')
    assert.equal(gateAnswerFor({ gates: Object.create({ toString: { answer: 'proto' } }) }, { id: 'toString' }, null), null,
      'own-property only (est-wk7l): an inherited member never reads as a receipt')
    assert.deepEqual(gateAnswerFor({}, { id: 'g' }, { status: 'done', output: { answer: 'ship' } }),
      { answer: 'ship' }, 'a consumed gate commits its answer in the node output')
    assert.equal(gateAnswerFor({}, { id: 'g' }, { status: 'done', output: 'plain text' }), null,
      'a non-gate done output is not a receipt')
  }

  console.log('ALL PASS test_composer_owner (one decision surface; nudgeOwner deleted, zero composer calls; ' +
    'receipt, same-run View identity, focus restoration, ok:false-as-error)')
} finally { rmSync(tmp, { recursive: true, force: true }) }
