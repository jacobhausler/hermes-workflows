// bd_2026-11-13-s20-gate-product (ship-2.0 gate product, UI half): the gate
// answer SURFACE acceptance, driven from the real desktop/plugin.js module
// with stub SDK hooks — independent of native app acceptance (the xow /
// s20-native-gate captures prove the same frames in the real surface; this
// suite needs neither a driver nor a running app).
//
// Pins the shipped acceptance list:
//   - nudge path DELETED atomically: no nudgeOwner / composer / hydration /
//     resume calls or strings (openSession is pinned absent on the ANSWER
//     PATH, not globally — the CJ2 read-only stored-session nav adapter
//     bd_2026-11-13-cj2 legitimately opens recorded chats through the SDK's
//     own host.openSession door and is not the nudge path), and the answer
//     surface keeps exactly ONE success toast variant (the exact receipt
//     toast) and one error variant; every old toast variant string is gone.
//   - failed-answer control: an {ok:false} door answer through the REAL api()
//     rejects (onSuccess never sees it); onError toasts once as error, the
//     inline row names the refusal, and the options stay retryable.
//   - exact-toast control: byte-exact `◇ Answer saved · <answer> · <requester>
//     · <run> / <gate> · <at>` (honestly omitting an absent time) whose
//     action re-selects the SAME run and the EXACT gate and routes.
//   - invalidate-before-read order, pending duplicate prevention, no-options
//     fail-closed, requester identity, focus restoration, stale durable-record
//     outranking the optimistic local record, and the isolated-runner-scoped
//     nothing-restarted copy.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const tmp = mkdtempSync(join(tmpdir(), 'wf-s20-gate-'))
try {
  const src = readFileSync(new URL('../desktop/plugin.js', import.meta.url), 'utf8')

  // -- 0. atomic-removal laws (one PR deleted callers, function and variants) --
  // openSession is deliberately NOT in the global set: the CJ2 stored-session
  // nav adapter (bd_2026-11-13-cj2, the BEGIN/END stored-session-nav block)
  // legitimately opens the RECORDED chat through the SDK's own
  // host.openSession door — a read-only view whose own wiring law forbids
  // composer, hydration wait, resume, submit, insert and nudge, and whose
  // call counts are pinned by tests/test_stored_session_nav.mjs. A global
  // absence could not distinguish that authorized open from a nudge-path
  // compat shim, so the no-open law is pinned at its true scope below: 0b
  // (static, the gate answer path, with discriminating controls) and §8
  // (runtime, the whole flow makes zero openSession calls).
  for (const gone of [/nudgeOwner/, /composer\.submit/, /composer\.insertText/,
                      /awaitHydration/, /resume it now/,
                      /press Enter there to resume/, /◇ Held ·/]) {
    assert.doesNotMatch(src, gone, `${gone} is retired with the nudge path — no compat shim`)
  }
  const region = src.slice(src.indexOf('export function GateActions'),
                           src.indexOf('export function NodeCard'))
  assert.ok(region.length > 0, 'GateActions region located before NodeCard')
  assert.equal((region.match(/host\.notify\(/g) || []).length, 2,
    'the answer surface owns exactly two toast variants: one success receipt, one error')
  assert.equal((region.match(/kind: 'success'/g) || []).length, 1,
    'old success toast variants are gone — one variant remains')
  assert.equal((region.match(/kind: 'error'/g) || []).length, 1, 'exactly one error variant')

  // -- 0b. the no-open law, scoped to the gate answer path (0a rationale) --
  // The answer path spans gateViewAction -> GateActions: the jump helper
  // rides the success toast's action and the receipt's view button, so the
  // slice starts at gateViewAction and ends where the surface stops being
  // the answering path — every helper an answer can reach is covered.
  const answerPath = src.slice(src.indexOf('export function gateViewAction'),
                               src.indexOf('export function NodeCard'))
  assert.ok(answerPath.length > region.length,
    'answer-path slice covers the gateViewAction helper plus the whole GateActions surface')
  assert.doesNotMatch(answerPath, /openSession/,
    'the gate answer path never opens a session — no nudge, no navigation-as-wake, no compat shim')
  // Discriminating control A (the matcher is not vacuous): openSession DOES
  // live in the source — inside the authorized read-only nav adapter, which
  // sits outside the answer-path slice. That is exactly the shape the
  // over-broad global check punished; if the nav block were deleted this
  // control goes red even though 0b stays green.
  const navBeg = src.indexOf('// BEGIN stored-session-nav')
  const navEnd = src.indexOf('// END stored-session-nav')
  assert.ok(navBeg !== -1 && navEnd > navBeg,
    'stored-session-nav block located (scope anchor for control A)')
  assert.ok(navEnd <= src.indexOf('export function gateViewAction') ||
            navBeg >= src.indexOf('export function NodeCard'),
    'the nav adapter sits outside the gate answer path — the two scopes are disjoint')
  assert.match(src.slice(navBeg, navEnd), /host\.openSession/,
    '(control A) openSession matches where it is authorized — the scoped absence is a scope proof, not a dead pattern')
  // Discriminating control B (the scoped check can fail): the same matcher
  // applied to the same slice with a re-introduced shim must catch it.
  const poisoned = answerPath.slice(0, answerPath.length >> 1) +
    "\n  await host.openSession(sid, { intent: 'in-place' }) // shim reborn\n" +
    answerPath.slice(answerPath.length >> 1)
  assert.match(poisoned, /openSession/,
    '(control B) a re-introduced openSession shim inside the answer path trips the 0b assertion')

  globalThis.__calls = []
  globalThis.__notifs = []
  globalThis.__order = []          // invalidate vs notify ordering witness
  globalThis.__rest = []
  globalThis.__postResult = { ok: true }
  globalThis.__pending = false
  globalThis.__receiptRef = { current: null }
  globalThis.__state = {}
  globalThis.__effects = []
  globalThis.__mutated = []

  const stubSdk = `
export const atom = v => { let x = v; return { get: () => x, set: n => { x = n } } }
export const Badge='Badge', cn=()=>'', Codicon='Codicon', COMPOSER_AREAS={}, EmptyState='EmptyState',
  PANES_AREA='panes', PanelListRow='PanelListRow', PanelPill='PanelPill', PanelSectionLabel='PanelSectionLabel',
  ROUTES_AREA='routes', ScrollArea='ScrollArea', StatusDot='StatusDot',
  TRANSCRIPT_DIRECTIVE_AREA='transcript.directives', Button='button'
export const useMutation = opts => { globalThis.__mut = opts
  return { isPending: !!globalThis.__pending, mutate: a => { globalThis.__mutated.push(a) } } }
export const useQueryClient = () => ({ invalidateQueries: () => { globalThis.__order.push('invalidate') } })
export const useQuery = () => ({ data: null, error: null })
export const useValue = a => (a && typeof a.get === 'function' ? a.get() : null)
export const host = {
  state: { focusedSessionId: atom(''), focusedStoredSessionId: atom('') },
  navigate: p => { globalThis.__calls.push(['navigate', p]) },
  notify: n => { globalThis.__order.push('notify'); globalThis.__calls.push(['notify', n.kind]); globalThis.__notifs.push(n) },
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
  const mod = await import(pathToFileURL(modPath).href)
  const { GateActions, gateRequester, $selRun, $selNode } = mod

  // the real api() rides ctx.rest — register a transport, not a stubbed mutation
  mod.default.register({
    rest: async (path, opts) => {
      globalThis.__rest.push([path, opts && opts.method, opts && opts.body])
      if (path === '/settings') return { tray: false }
      return globalThis.__postResult
    },
    register: () => {}
  })
  await new Promise(r => setTimeout(r, 0))

  const render = props => {
    globalThis.__effects = []
    globalThis.__si = 0
    const tree = GateActions(props)
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
  const GATE = { id: 'review', question: 'Save this review decision?',
    options: ['Approve review', 'Keep for revision'], context: 'Isolated review workflow' }
  const OWNER = { session_id: 'owner-sess' }
  const AT = '2026-11-26T00:00:00+00:00'

  // -- 1. held surface: question verbatim, requester declared, options enabled --
  {
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    const text = textOf(t)
    assert.ok(text.includes('Save this review decision?'), '(requester) question renders verbatim')
    assert.ok(text.includes('requester: Isolated review workflow'),
      '(requester) the declared requester is named — identity, never the viewer')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.ok(opts.length === 2 && opts.every(b => b.disabled === false), '(held) every option is offered')
  }

  // -- 2. no-options: fail closed with a reason, zero invented buttons ----------
  {
    const t = render({ runId: 'R1', gate: { id: 'review', question: 'Q?', options: [] }, owner: OWNER, events: [] })
    assert.ok(textOf(t).includes('No answer options recorded.'), '(no-options) the reason is visible')
    assert.equal(buttons(t).length, 0, '(no-options) no buttons are invented')
  }

  // -- 3. pending: duplicate prevention — every option disabled + saving row ----
  {
    globalThis.__pending = true
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(t).includes('Saving answer…'), '(duplicate) pending says Saving answer…')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.ok(opts.length === 2 && opts.every(b => b.disabled === true),
      '(duplicate) pending disables every option — no second write behind a slow POST')
    globalThis.__pending = false
  }

  // -- 4. exact-toast + invalidate-before-read, through the REAL api() ----------
  {
    globalThis.__postResult = { ok: true, at: AT }
    globalThis.__notifs.length = 0
    globalThis.__order.length = 0
    globalThis.__receiptRef.current = { focus: () => { globalThis.__calls.push(['focus-receipt']) } }
    const res = await globalThis.__mut.mutationFn('Approve review')  // real api(): ok:true resolves
    globalThis.__mut.onSuccess(res, 'Approve review')
    assert.equal(globalThis.__order[0], 'invalidate',
      '(invalidate-before-read) the census is invalidated before the receipt toast, hence before any re-read')
    const ok_notifs = globalThis.__notifs.filter(n => n.kind === 'success')
    assert.equal(ok_notifs.length, 1, '(exact-toast) exactly one success toast fires')
    assert.equal(ok_notifs[0].message,
      `◇ Answer saved · Approve review · Isolated review workflow · R1 / review · ${AT}`,
      '(exact-toast) the toast IS the receipt: answer, requester, run / gate, door-stamped time')
    assert.equal(ok_notifs[0].action.label, 'View exact gate', '(exact-toast) the action is the exact-gate jump')
    $selRun.set('OTHER'); $selNode.set(null)
    ok_notifs[0].action.onClick()
    assert.equal($selRun.get(), 'R1', '(exact-toast) same-run identity — never the viewer elsewhere')
    assert.deepEqual($selNode.get(), { runId: 'R1', nodeId: 'review' }, '(exact-toast) the EXACT gate')
    assert.ok(globalThis.__calls.some(c => c[0] === 'navigate' && c[1] === '/workflows'),
      '(exact-toast) the jump routes to the record page')
    const post = globalThis.__rest.at(-1)
    assert.deepEqual(post, ['/runs/R1/gate', 'POST', { gate_id: 'review', answer: 'Approve review' }],
      '(one-door) the surface POSTs the ONE door with the exact answer')
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(t).includes(`Answered · ${AT}`), '(exact-toast) the receipt shows the door-stamped time')
  }

  // -- 5. failed-answer control: ok:false through the REAL api() is an ERROR ----
  {
    globalThis.__postResult = { ok: false, error: 'gate already answered (current graph)' }
    await assert.rejects(() => globalThis.__mut.mutationFn('Keep for revision'),
      /gate already answered \(current graph\)/,
      '(failed-answer) the real api() throws on {ok:false} — onSuccess can never treat it as success')
    remount()
    globalThis.__notifs.length = 0
    globalThis.__mut.onError(new Error('gate already answered (current graph)'))
    assert.equal(globalThis.__notifs.find(n => n.kind === 'success'), undefined,
      '(failed-answer) a refused answer never receipts as success')
    const err = globalThis.__notifs.find(n => n.kind === 'error')
    assert.ok(err && /^Gate answer failed: /.test(err.message), '(failed-answer) the refusal toasts once as error')
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(textOf(t).includes('Gate answer failed · gate already answered (current graph)'),
      '(failed-answer) the inline row names the refusal — stale/conflict is visible, not swallowed')
    const opts = buttons(t).filter(b => b.children === 'Approve review' || b.children === 'Keep for revision')
    assert.ok(opts.length === 2 && opts.every(b => !b.disabled),
      '(failed-answer) the options stay retryable — nothing was consumed')
  }

  // -- 6. stale control: the durable record OUTRANKS the optimistic local one ---
  {
    remount()
    globalThis.__postResult = { ok: true, at: AT }
    const t = render({ runId: 'R1', gate: GATE, owner: OWNER,
      answered: { answer: 'Keep for revision', at: '2026-11-26T04:00:00+00:00', _ui: true },
      events: [{ event: 'gate.held', node: 'review', ts: '2026-11-26T03:55:00+00:00' }] })
    const text = textOf(t)
    assert.ok(text.includes('Keep for revision') && !text.includes('Approve review'),
      '(stale) the refetched durable answer wins over any local optimistic record')
    assert.ok(text.includes('held 5m'), '(stale) the dwell freezes at the durable at — never a ticking now')
    assert.ok(text.includes('Nothing restarted') && text.includes('isolated runner'),
      '(no-scheduler) the nothing-restarted copy is scoped to the tested isolated runner')
  }

  // -- 7. focus restoration onto the receipt -----------------------------------
  {
    const before = globalThis.__calls.filter(c => c[0] === 'focus-receipt').length
    remount()
    globalThis.__mut.onSuccess({ ok: true, at: AT }, 'Approve review')
    render({ runId: 'R1', gate: GATE, owner: OWNER, events: [] })
    assert.ok(globalThis.__calls.filter(c => c[0] === 'focus-receipt').length > before,
      '(focus) when options unmount, focus lands on the receipt, not the body')
  }

  // -- 8. requester purity + zero-execution ledger ------------------------------
  {
    assert.equal(gateRequester({ context: '  Declared Lane  ' }, null), 'Declared Lane',
      '(requester) a declared context trims and wins')
    assert.equal(gateRequester({}, { session_id: 'cron_7' }), '@cron', '(requester) a cron owner labels honestly')
    assert.equal(gateRequester({}, {}), '@unknown', '(requester) absence is unknown, never fabricated')
    const seen = globalThis.__calls.map(c => c[0])
    for (const banned of ['submit', 'insert', 'openSession']) {
      assert.equal(seen.filter(k => k === banned).length, 0,
        `(nudge-removed) the whole flow makes zero ${banned} calls`)
    }
  }

  console.log('ALL PASS ship20-gate-ui — nudge path atomically gone (one success variant); no-open law holds scoped to the answer path with discriminating controls (CJ2 read-only nav adapter authorized outside it); failed-answer and exact-toast hold with NO native acceptance; stale/duplicate/no-options/requester/focus controls pinned')
} finally { rmSync(tmp, { recursive: true, force: true }) }
