#!/usr/bin/env node
// Real-app proof driver for the hermes-workflows desktop UI (source-only helper).
//
// Captures the ACTUAL React/SDK renderer — not CHATFRAME, not a file-openable
// RC, not a JSX-to-DOM fake, and NEVER synthesis/index.html as production proof.
// Bench shape (proven by the hermes-workflows-ui-qa skill and the 2026-11-22
// lookbook wave): an owned dev Hermes app instance from the hermes-agent
// checkout, fresh Electron user-data, an isolated bench HERMES_HOME with the
// CANDIDATE plugin staged into its desktop-plugins root, an isolated test runs
// root the gateway serves during the run (config-set, then reverted), trusted
// CDP input, Page.captureScreenshot PNGs, and teardown that kills ONLY the
// process groups this driver spawned plus a survivor scan scoped to this
// bench's own --user-data-dir path.
//
// Interface used by later beads:
//   node tests/proof-harness/capture.mjs [--case CASE] [--only TOKENS] [--out DIR]
// CASE defaults to baseline. --only selects surfaces by short token
// (directive, pane, tray) or full surface name; it never ADDS a surface the
// case doesn't declare (intersection only). DIR defaults to
// tests/proof-harness/captured/run-<ts>.
// Cases and their seeds live in ./cases.json; every seed declares
// kind: engine_seed | historical_snapshot. A known case whose surfaces are
// not yet wired fails exit 3 as an explicitly NEW test — never an invented
// existing command.
//
// Slice A reproducibility law (bd_2026-11-13-iqf): every run writes an
// IMMUTABLE capture set — captures/*.png (0444), contents/*.txt (0444, the
// masked visible-text layer of each captured region), and manifest.json
// (0444, written last) pinning per-file sha256 plus a REPRO section:
// content hashes over the volatile-masked text layer only, so two
// independent live-app runs at one candidate pin the same repro hash even
// though raster bytes legitimately differ (run clock words, relative
// timestamps). The volatile classes are declared (VOLATILE_MASKS below);
// masking is exported so the double-run spec can pin it with samples.
//
// Failure law (fail nonzero, never a green no-op):
//   exit 2 usage / unknown case (lists known cases)
//   exit 3 case known, surface not yet implemented (new test)
//   exit 4 preflight: absent plugin/API tooling, busy ports, missing app repo
//   exit 5 renderer/electron boot or CDP attach timeout
//   exit 6 API attachment not proven (registry and/or live run row absent)
//   exit 7 empty/suspicious captures (missing PNG magic, tiny bytes)
//   exit 8 teardown: survivor under our owned path, or config revert failed
//
// Environment knobs: UI2_PROOF_APP_REPO (hermes-agent checkout),
// UI2_PROOF_HERMES_BIN (hermes CLI), UI2_PROOF_HOME (real Hermes home,
// default ~/.hermes). Bench knobs: --cdp-port, --renderer-port, --keep,
// --no-prebuild, --plan, --paint-budget S (first-paint budget; raise on a
// loaded box — field-proven: load avg 45 during a crew wave starves the
// 60 s default and the run dies exit 5 while healthy).
import { execFileSync, spawn, spawnSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const MANIFEST = path.join(HERE, 'cases.json');

const USAGE = `usage: node tests/proof-harness/capture.mjs [--case CASE] [--only TOKENS] [--out DIR]
       [--app-repo PATH] [--plugin PATH] [--cdp-port N] [--renderer-port N]
       [--hermes-bin PATH] [--plan] [--keep] [--no-prebuild] [--paint-budget S]
default case: baseline; --only tokens: directive,pane,tray (or full surface
names); default out: tests/proof-harness/captured/run-<ts>
cases: see tests/proof-harness/cases.json (setup: tests/proof-harness/SETUP.md)`;

// short token -> surface id (slice A: directive + pane; tray pre-wired on
// this branch, slices B extend the surfaces themselves, not this map law).
const ONLY_TOKENS = {
  directive: 'directive_card', pane: 'pane_workflows', tray: 'tray_row',
  directive_card: 'directive_card', pane_workflows: 'pane_workflows', tray_row: 'tray_row',
};

function parseOnly(raw) {
  const parts = String(raw).split(',').map(s => s.trim()).filter(Boolean);
  if (!parts.length) die(EX.usage, `--only needs at least one token (${Object.keys(ONLY_TOKENS).join(',')})\n${USAGE}`);
  const out = [];
  for (const p of parts) {
    const id = ONLY_TOKENS[p.toLowerCase()];
    if (!id) die(EX.usage, `unknown --only token ${JSON.stringify(p)}; known: ${Object.keys(ONLY_TOKENS).join(', ')}\n${USAGE}`);
    if (!out.includes(id)) out.push(id);
  }
  return out;
}

function parseArgs(argv) {
  const a = { caseName: 'baseline', cdpPort: 9394, rendererPort: 5194, prebuild: true, plan: false, keep: false,
              paintBudgetMs: 60_000 };
  for (let i = 0; i < argv.length; i++) {
    const take = () => {
      const v = argv[++i];
      if (v === undefined) die(EX.usage, `flag needs a value: ${argv[i - 1]}\n${USAGE}`);
      return v;
    };
    switch (argv[i]) {
      case '--case': a.caseName = take(); break;
      case '--only': a.only = parseOnly(take()); break;
      case '--out': a.outDir = path.resolve(take()); break;
      case '--app-repo': a.appRepo = path.resolve(take()); break;
      case '--plugin': a.plugin = path.resolve(take()); break;
      case '--cdp-port': a.cdpPort = Number(take()); break;
      case '--renderer-port': a.rendererPort = Number(take()); break;
      case '--paint-budget': a.paintBudgetMs = Number(take()) * 1000; break;
      case '--hermes-bin': a.hermesBin = take(); break;
      case '--plan': a.plan = true; break;
      case '--keep': a.keep = true; break;
      case '--no-prebuild': a.prebuild = false; break;
      case '--help': case '-h': console.log(USAGE); process.exit(0); break;
      default: die(EX.usage, `unknown argument: ${argv[i]}\n${USAGE}`);
    }
  }
  return a;
}

const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Volatile-text classes for the REPRO layer (slice A law): these are the
// only regions of captured text allowed to differ between two runs at one
// candidate pin. Anything else that changes is a REAL content change and
// must break the repro hash. Exported so the double-run spec pins the mask
// itself with samples (positive and negative).
export const VOLATILE_MASKS = [
  [/\b\d{8}-\d{6}-[A-Za-z0-9._-]+\b/g, '<RUN-ID>'],
  [/\brun\s+(?:\d+\s*(?:s|sec|secs?|m|min|mins?|h|hr|hrs?|d|day|days)?)(?:\s+\d+\s*(?:s|sec|secs?|m|min|mins?|h|hr|hrs?|d|day|days))?/gi, '<RUN-CLOCK>'],
  [/\b(?:now|just now|\d+\s*(?:s|sec|secs?|m|min|mins?|h|hr|hrs?|hour|hours?|d|day|days?)\s*ago)\b/gi, '<REL-TIME>'],
  [/\b\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}[^,\s]*)?\b/g, '<DATE>'],
  // field-proven (first paired run, detail column): owner/session tokens are
  // '@local-<hex>' — the hex is per-run — and the timeline renders elapsed
  // chips as '<1s>'/'<46s>' which tick between runs.
  [/\b[0-9a-f]{40,}\b/g, '<HEX-ID>'],
  [/<\d+\s*(?:s|sec|secs?|m|min|mins?|h|hr|hrs?|d|day|days)>/gi, '<ELAPSED>'],
  // field-proven (pair run try A/B): the transcript renders wall-clock
  // message times as '10:53 PM' — they shift between two captures minutes
  // apart and are pure clock, not content.
  [/\b\d{1,2}:\d{2}(?::\d{2})?\s*[AP]\.?M\.?\b/gi, '<CLOCK>'],
];
// The empty-state intro card rotates its headline/body per mount from the
// app's own intro-copy.jsonl — a rotation pool, so a regex cannot name it.
// The driver loads the pool from the app checkout at capture time and hands
// it to maskVolatile as exact-line literals; the committed masked content
// then carries <INTRO-COPY> and the mask stays idempotent under CI (where
// the pool file need not exist).
export function maskVolatile(text, literals = []) {
  let t = String(text);
  for (const [re, rep] of VOLATILE_MASKS) t = t.replace(re, rep);
  if (literals.length) {
    const pool = new Set(literals);
    t = t.split('\n').map(line => pool.has(line.trim()) ? '<INTRO-COPY>' : line).join('\n');
  }
  return t;
}
let CAPTURE_LITERALS = [];

// Deterministic JSON: sorted keys everywhere, so a manifest section hashed
// for repro is byte-stable regardless of object insertion order.
export function canonicalJson(v) {
  if (Array.isArray(v)) return '[' + v.map(canonicalJson).join(',') + ']';
  if (v && typeof v === 'object')
    return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonicalJson(v[k])).join(',') + '}';
  return JSON.stringify(v);
}

// Visible text of everything inside a content-column region (same region
// predicate the locators use): DOM-ordered text nodes whose painted rect
// lives in the column. This is the captured CONTENT of a viewport shot,
// minus the sidebar (session order/relative times) and the tray strip.
function columnTextJS(region) {
  return `(() => {
    const R = ${JSON.stringify(region)};
    const out = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const t = (n.textContent || '').trim();
      if (!t) continue;
      const el = n.parentElement;
      if (!el) continue;
      const r = el.getBoundingClientRect();
      if (!(r.width > 0 && r.height > 0)) continue;
      if (r.x + r.width < R.xMin || r.y < R.yMin) continue;
      if (r.y + r.height > innerHeight - R.bottomMargin) continue;
      out.push(t);
    }
    return out.join('\\n');
  })()`;
}

// Immutable write: content, then 0444 — a capture file is never rewritten
// in place (stale DIRS are archived whole; files inside are write-once).
function writeImmutable(file, data) {
  fs.writeFileSync(file, data);
  fs.chmodSync(file, 0o444);
}

// Crew-wave law (field-proven 2026-11-24): parallel benches sharing one
// hermes install serialize on a GLOBAL source-update lock — a CLI call
// landing mid-install exits 'an update is still running' / 'no dependency
// environment is committed'. Those are transient by definition: retry with
// backoff, but only that shape; anything else propagates immediately.
function retryCli(fn, { attempts = 12, delayMs = 5_000 } = {}) {
  for (let i = 1; ; i++) {
    try { return fn(); }
    catch (e) {
      const msg = String((e && (e.stderr || e.message)) || '');
      const transient = /update is still running|no dependency environment is committed|pm repair/.test(msg);
      if (!transient || i >= attempts) throw e;
      execFileSync('/bin/sleep', [String(Math.round(delayMs / 1000))]);
    }
  }
}

// exit codes (documented above; tests assert them)
const EX = { usage: 2, notImplemented: 3, preflight: 4, boot: 5, api: 6, capture: 7, teardown: 8 };
class Bail extends Error { constructor(code, msg) { super(msg); this.code = code; } }
const die = (code, msg) => { throw new Bail(code, msg); };

async function portFree(port) {
  const net = await import('node:net');
  return new Promise(res => {
    const srv = net.createServer();
    srv.once('error', () => res(false));
    srv.once('listening', () => srv.close(() => res(true)));
    srv.listen(port, '127.0.0.1');
  });
}

// -- CDP core: port of the proven wfqa.mjs attach/trusted-input primitives,
//    with the renderer-port filter parameterized (wfqa hard-codes 5174).
async function connectCdp(port, rendererPort, timeoutMs = 90_000) {
  const t0 = Date.now();
  let ws = null;
  for (;;) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      const page = list.find(t => t.type === 'page' && t.url.includes(`:${rendererPort}`));
      if (page) {
        ws = new WebSocket(page.webSocketDebuggerUrl);
        await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
        break;
      }
    } catch { /* backend not up yet */ }
    if (Date.now() - t0 > timeoutMs) die(EX.boot, `no CDP page target for renderer :${rendererPort} within ${timeoutMs}ms`);
    await sleep(500);
  }
  let id = 0;
  const pend = new Map();
  const bind = () => {
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    };
    // A dropped socket must REJECT its in-flight calls, not leave them hung:
    // the navigation-class message lets send()'s reattach loop decide.
    ws.onclose = () => {
      const gone = { error: { code: -32001, message: 'WebSocket is not open: target closed' } };
      const waiting = [...pend.entries()];
      pend.clear();
      for (const [, settle] of waiting) settle(gone);
    };
  };
  bind();
  // Field-proven (pair run, try3): throwing INSIDE the resolve callback
  // escapes through the event dispatcher as an uncaughtException — the
  // process dies and send()'s catch never sees the -32000. Reject instead;
  // the navigation-retry law below then actually governs the outcome.
  const rawSend = (method, params = {}) => new Promise((res, rej) => {
    const i = ++id;
    pend.set(i, m => { if (m.error) rej(new Error(`${method}: ${JSON.stringify(m.error).slice(0, 300)}`)); else res(m.result); });
    try { ws.send(JSON.stringify({ id: i, method, params })); }
    catch (e) { pend.delete(i); rej(new Error(`${method}: ${String(e?.message || e)}`)); }
  });
  // Field-proven (pair run, try2/3): the renderer can full-reload under us
  // (vite reload / app-init navigation) exactly between attach and eval —
  // one -32000 'Inspected target navigated or closed' killed the WHOLE run
  // via an uncaught rejection. The navigation class is transient: re-attach
  // to the fresh page target and retry, bounded, before giving up.
  const NAV_TRANSIENT = /navigated or closed|target closed|Cannot find context/i;
  const reattach = async () => {
    const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    const page = list.find(t => t.type === 'page' && t.url.includes(`:${rendererPort}`));
    if (!page) throw new Error('reattach: no page target yet');
    const nws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((res, rej) => { nws.onopen = res; nws.onerror = rej; });
    // Detach the dying socket's handlers BEFORE close: its async onclose must
    // not fire against the shared pend map after the new socket started using it.
    try { ws.onmessage = ws.onclose = null; ws.close(); } catch { /* already dead */ }
    ws = nws;
    pend.clear();
    bind();
    await rawSend('Page.enable').catch(() => { /* auto-enable builds */ });
  };
  const send = async (method, params = {}) => {
    for (let attempt = 0; ; attempt++) {
      try { return await rawSend(method, params); }
      catch (e) {
        if (!NAV_TRANSIENT.test(String(e?.message)) || attempt >= 3) throw e;
        await sleep(600 * (attempt + 1));
        await reattach().catch(() => { /* target storm; loop retries */ });
        if (attempt >= 3) throw e;
      }
    }
  };
  await send('Page.enable').catch(() => { /* most builds auto-enable; reload/shot prove it anyway */ });
  const evl = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) {
      die(EX.api, 'page eval threw: ' + JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails.text).slice(0, 400));
    }
    return r.result.value;
  };
  return { ws, send, evl };
}

// Locator JS: finds the DEEPEST visible element whose trimmed text contains
// `needle` (or the first, when `nth` given). `region` (field-proven overlay
// lesson: a full-window CONNECTING overlay paints OVER the chrome, so
// innerText/global hits can pass while the real target is occluded):
// {xMin, yMin, bottomMargin} restricts hits to the main content column,
// excluding the sidebar (x) and the tray strip (bottom).
function locateJS(needle, { exact = false, nth = null, ci = false, region = null } = {}) {
  return `(async () => {
    const needle = ${JSON.stringify(needle)}, exact = ${exact}, ci = ${ci};
    const region = ${JSON.stringify(region)};
    const nodes = [...document.querySelectorAll('div,button,a,span,li,td')];
    const norm = t => ci ? t.toLowerCase() : t;
    const hits = nodes.filter(n => {
      const t = norm((n.innerText || n.textContent || '').trim());
      if (t.length > 400 && !exact) return false;
      if (exact ? t.split('·')[0].trim() === norm(needle) : t.includes(norm(needle))) {
        const r = n.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0)) return false;
        if (region) {
          if (r.x + r.width < (region.xMin ?? 0)) return false;
          if (r.y < (region.yMin ?? 0)) return false;
          if (r.y + r.height > innerHeight - (region.bottomMargin ?? 0)) return false;
        }
        return true;
      }
      return false;
    });
    if (!hits.length) return { err: 'no-match' };
    // deepest = a hit that contains no other hit (leaf text row)
    const leaf = hits.find(h => !hits.some(o => o !== h && h.contains(o))) ?? hits[0];
    const el = ${nth === null ? 'leaf' : `hits[${nth}]`};
    el.scrollIntoView({ block: 'center', inline: 'center' });
    await new Promise(r => setTimeout(r, 120)); // settle: re-probe after scroll (skill law)
    const r = el.getBoundingClientRect();
    const out = { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height,
             rect: { x: r.x, y: r.y, width: r.width, height: r.height },
             text: (el.innerText || el.textContent || '').slice(0, 80) };
    ${region ? `
    // Occlusion truth test: trusted input lands on document.elementFromPoint
    // — a hit hidden under an overlay is NOT on the rendered page.
    const top = document.elementFromPoint(out.x, out.y);
    if (!top || !(el.contains(top) || top.contains(el)))
      return { err: 'occluded', over: (top && (top.innerText || top.textContent) || '').trim().slice(0, 60) };` : ''}
    return out;
  })()`;
}

// Rect probe on the upstream region-aware locator (gate case bd_2026-11-13-qri):
// same deepest-leaf rule, returns the bounding rect (null when not on the
// rendered page) for clip-sized shots.
async function rectOf(cdp, needle, opts = {}) {
  const pt = await cdp.evl(locateJS(needle, opts));
  return pt && !pt.err ? pt.rect : null;
}

// locateClickPoint is the locator probe WITHOUT the dispatch — the coverage
// case needs the row's rect for a clipped shot BEFORE the click navigates
// away (bd_2026-11-13-yjp). Occluded retries once, then dies honest.
async function locateClickPoint(cdp, needle, opts = {}) {
  let pt = await cdp.evl(locateJS(needle, opts));
  if (pt.err === 'occluded') { await sleep(1500); pt = await cdp.evl(locateJS(needle, opts)); }
  if (pt.err) die(EX.capture, `click target not found on rendered page: ${JSON.stringify(needle)} (${pt.err}${pt.over ? ` over: ${JSON.stringify(pt.over)}` : ''})`);
  return pt;
}

// Trusted input (real pipeline, per skill): moved -> pressed -> released at
// the element's rect center.
async function trustedClick(cdp, needle, opts = {}) {
  const pt = await locateClickPoint(cdp, needle, opts);
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: pt.x, y: pt.y });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: pt.x, y: pt.y, button: 'left', clickCount: 1, buttons: 1 });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: pt.x, y: pt.y, button: 'left', clickCount: 1, buttons: 0 });
  return pt;
}

// -- CDP Fetch-domain transport mock (bd_2026-11-13-yjp, coverage case) ------
// Manufactures loading / error / partial-fetch conditions ON THE REAL SURFACE:
// renderer, plugin, react-query loop and backend stay the actual code — only
// the network edge lies (stall, fail, or a short-page fulfill), so every frame
// captured behind a rule is the app's OWN honest state, never a fake DOM.
// Rules are evaluated in order against the paused request URL; a request that
// matches no rule simply continues (mock mounted, traffic untouched). The
// listener rides the raw ws exactly like the gate case's pauseOnce: the
// coverage path never closes/reconnects the session it armed (a reattach
// re-arms a fresh mock instead — see armMock at every reconnect site).
const urlGlob = p => {
  const re = new RegExp('^' + String(p).split('*').map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$');
  return u => re.test(u);
};
async function mockRuns(cdp) {
  let rules = [];
  const paused = new Map(); // requestId -> url while stalled (continued on release)
  cdp.ws.addEventListener('message', e => {
    let m; try { m = JSON.parse(e.data); } catch { return; }
    if (m.method !== 'Fetch.requestPaused') return;
    const ev = m.params;
    const url = ev.request.url;
    const rule = rules.find(r => r.g(url));
    if (rule && rule.action === 'stall') { paused.set(ev.requestId, url); return; }
    paused.delete(ev.requestId);
    if (rule && rule.action === 'fail')
      cdp.send('Fetch.failRequest', { requestId: ev.requestId, errorReason: 'Failed' }).catch(() => {});
    else if (rule && rule.action === 'fulfill')
      cdp.send('Fetch.fulfillRequest', {
        requestId: ev.requestId, responseCode: 200,
        responseHeaders: [{ name: 'content-type', value: 'application/json' }],
        body: Buffer.from(String(rule.body)).toString('base64')
      }).catch(() => {});
    else cdp.send('Fetch.continueRequest', { requestId: ev.requestId }).catch(() => {});
  });
  await cdp.send('Fetch.enable', { patterns: [{ urlPattern: '*workflows/runs*', requestStage: 'Request' }] });
  return {
    setRules(rs) { rules = rs.map(r => ({ ...r, g: urlGlob(r.urlPattern) })); },
    releaseStalled() {
      for (const rid of paused.keys()) cdp.send('Fetch.continueRequest', { requestId: rid }).catch(() => {});
      paused.clear();
      rules = [];
    },
    async off() {
      for (const rid of paused.keys()) cdp.send('Fetch.continueRequest', { requestId: rid }).catch(() => {});
      paused.clear(); rules = [];
      try { await cdp.send('Fetch.disable'); } catch { /* disable resumes held traffic; best-effort */ }
    }
  };
}

// The app paints a full-window CONNECTING splash over the chrome until its
// gateway WS attaches; input and screenshots are the SPLASH underneath it.
// Wait for the splash to actually clear (viewport center no longer splash text).
async function waitConnected(cdp, ms = 90_000) {
  const t0 = Date.now();
  for (;;) {
    const clear = await cdp.evl(`(() => {
      const el = document.elementFromPoint(Math.floor(innerWidth/2), Math.floor(innerHeight/2));
      const t = ((el && (el.innerText || el.textContent)) || '').trim().toLowerCase();
      // The boot-failure modal replaces the splash center; treat it as NOT
      // connected (field-proven: 'Hermes couldn't start' while the backend
      // installs deps) — waiting beats clicking blind through it.
      const modal = document.body.innerText.includes("couldn't start");
      return !modal && t.length > 0 && !t.includes('connecting') && !t.includes('loading');
    })()`);
    if (clear) return Date.now() - t0;
    if (Date.now() - t0 > ms) die(EX.api, 'app never attached to its backend: viewport center still shows the CONNECTING splash or the boot-failure modal');
    await sleep(600);
  }
}

// Field-proven bench lesson: the app's gateway ensure can lose the shared
// install.lock race when several benches boot at once -> "Hermes couldn't
// start" modal covers the chrome. The modal's Retry button re-runs that
// exact ensure; bounded re-tries turn a transient lock collision into a
// slow boot, never a red proof.
let retryGateBudget = 4;
async function retryGateIfModal(cdp) {
  if (retryGateBudget <= 0) return false;
  const modal = await cdp.evl(`(() => {
    const t = (document.body && document.body.innerText || '').toLowerCase();
    return t.includes("hermes couldn't start") ? 1 : 0;
  })()`).catch(() => 0);
  if (!modal) return false;
  retryGateBudget--;
  try { await trustedClick(cdp, 'Retry', { exact: true }); } catch { /* modal re-rendering */ }
  return true;
}

async function waitPainted(cdp, ms = 20_000) {
  const t0 = Date.now();
  for (;;) {
    const n = await cdp.evl(`document.body ? document.body.innerText.length : 0`);
    if (n > 40) return n;
    if (Date.now() - t0 > ms) die(EX.boot, 'renderer never painted a page (empty document)');
    await sleep(400);
  }
}

async function waitText(cdp, needle, ms = 30_000) {
  const t0 = Date.now();
  for (;;) {
    // a reload in flight (Retry after the startup modal) is 'not yet seen',
    // not a fatal: keep polling until the wall.
    const seen = await cdp.evl(`document.body.innerText.includes(${JSON.stringify(needle)})`).catch(() => false);
    if (seen) return Date.now() - t0;
    if (Date.now() - t0 > ms) die(EX.api, `never rendered on the real app: ${JSON.stringify(needle)} (within ${ms}ms)`);
    await sleep(400);
  }
}

async function shoot(cdp, outDir, name, clipRect = null, contentText = null) {
  const params = { format: 'png' };
  if (clipRect) {
    params.clip = { x: Math.max(0, clipRect.x), y: Math.max(0, clipRect.y),
                    width: Math.max(1, clipRect.width), height: Math.max(1, clipRect.height), scale: 1 };
  }
  const r = await cdp.send('Page.captureScreenshot', params);
  const buf = Buffer.from(r.data, 'base64');
  const file = path.join(outDir, 'captures', name);
  writeImmutable(file, buf);
  const ok = buf.length > 4096 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  if (!ok) die(EX.capture, `empty/suspicious PNG (need >4096B + magic): ${name} (${buf.length}B)`);
  const rec = { file: path.relative(outDir, file), bytes: buf.length, sha256: sha256(file),
           clip: clipRect ? 'element' : 'viewport', reviewed: false };
  if (contentText !== null) {
    const masked = maskVolatile(contentText, CAPTURE_LITERALS) + '\n';
    const cfile = path.join(outDir, 'contents', name.replace(/\.png$/, '.txt'));
    fs.mkdirSync(path.dirname(cfile), { recursive: true });
    writeImmutable(cfile, masked);
    const nontrivial = masked.replace(/\n+/g, '').length >= 40;
    if (!nontrivial) die(EX.capture, `content layer trivial (masked text < 40 chars): ${name}`);
    rec.content_file = path.relative(outDir, cfile);
    rec.content_sha256 = sha256(cfile);
  }
  return rec;
}

// -- owned process supervision: spawn detached (own pgid); teardown kills the
//    group, then scans survivors by THIS bench's --user-data-dir path only.
class Supervisor {
  constructor(outDir) { this.outDir = outDir; this.children = []; this.killed = false; }
  start(label, cmd, args, opts) {
    const log = fs.openSync(path.join(this.outDir, 'logs', `${label}.log`), 'a');
    const child = spawn(cmd, args, { detached: true, stdio: ['ignore', log, log], ...opts });
    child.on('exit', code => {
      fs.appendFileSync(path.join(this.outDir, 'logs', `${label}.exit`), `${Date.now()} code=${code ?? 'signal'}\n`);
    });
    this.children.push({ label, pid: child.pid });
    fs.writeFileSync(path.join(this.outDir, 'supervisors.json'),
      JSON.stringify(this.children, null, 2) + '\n');
    return child;
  }
  ownedUserData() { return this._ownedUserData || null; }
  async teardown() {
    if (this.killed) return;
    this.killed = true;
    const survivorsReport = [];
    for (const { pid } of this.children) {
      try { process.kill(-pid, 'SIGTERM'); } catch { /* already gone */ }
    }
    await sleep(2000);
    for (const { pid } of this.children) {
      try { process.kill(-pid, 'SIGKILL'); } catch { /* already dead */ }
    }
    // Survivor scan is PATH-scoped to this bench's owned dirs only — never a
    // broad electron pattern (cleanup law: kill only the owned supervisor +
    // Electron tree; other benches and the user's app stay untouched).
    if (this._ownedUserData) {
      for (const needle of [this._ownedUserData, `--user-data-dir=${this._ownedUserData}`,
                            this._viteMarker || '@@@never@@@']) {
        if (needle === '@@@never@@@') continue;
        try {
          const out = execFileSync('/bin/ps', ['-Ao', 'pid,command'], { encoding: 'utf8' });
          for (const line of out.split('\n')) {
            const m = line.match(/^\s*(\d+)\s+(.*)$/);
            if (m && Number(m[1]) !== process.pid && line.includes(needle) &&
                !line.includes(' grep')) {
              try { process.kill(Number(m[1]), 'SIGKILL'); } catch { /* raced away */ }
              survivorsReport.push({ pid: Number(m[1]), needle, line: m[2].slice(0, 200) });
            }
          }
        } catch { /* ps failed; the group kill above still stands */ }
      }
    }
    this.survivors = survivorsReport;
  }
}

function readConfigValue(hermesBin, key, env, profile = null) {
  // `hermes config get` exits 0 printing the value; a missing key prints a
  // "not set" notice. Presence probe stays honest via --json parse, else null.
  try {
    const out = execFileSync(hermesBin,
      [...(profile ? ['--profile', profile] : []), 'config', 'get', key, '--json'], { encoding: 'utf8', env });
    return JSON.parse(out);
  } catch { return null; }
}

function writeConfig(hermesBin, kv, env, profile = null) {
  execFileSync(hermesBin,
    [...(profile ? ['--profile', profile] : []), 'config', 'set', '--force', ...kv], { encoding: 'utf8', env });
}
function unsetConfig(hermesBin, key, env, profile = null) {
  try {
    execFileSync(hermesBin,
      [...(profile ? ['--profile', profile] : []), 'config', 'unset', key], { encoding: 'utf8', env });
  } catch { /* best-effort revert */ }
}

// RC ch4 graph-grammar measurement: pick the widest route-group svg and read
// its projected identity counts + STRICT crossings off the RENDERED geometry
// (bezier-sampled polylines; edges sharing an endpoint can never count as a
// crossing). The crossing number is a count of THIS geometry — never a
// transplanted constant.
async function measureGraphSvg(cdp, minGroups) {
  const m = await cdp.evl(`(() => {
    const svg = [...document.querySelectorAll('svg')]
      .filter(s => s.querySelectorAll('g').length >= ${minGroups})
      .sort((a, b) => b.querySelectorAll('g').length - a.querySelectorAll('g').length)[0]
    if (!svg) return { err: 'no svg with >= ${minGroups} route groups' }
    const gs = [...svg.querySelectorAll('g')]
    const flat = d => {
      const t = d.match(/[A-Za-z]|-?\\d+(?:\\.\\d+)?(?:e[+-]?\\d+)?/g), out = []
      let i = 0, x = 0, y = 0
      while (i < t.length) {
        const op = t[i++], ax = x, ay = y
        if (op === 'M') { x = +t[i++]; y = +t[i++]; out.push([x, y]); continue }
        if (op === 'C') {
          const bx = +t[i++], by = +t[i++], cx = +t[i++], cy = +t[i++]; x = +t[i++]; y = +t[i++]
          for (let j = 1; j <= 200; j++) { const s = j / 200, u = 1 - s
            out.push([u*u*u*ax + 3*u*u*s*bx + 3*u*s*s*cx + s*s*s*x, u*u*u*ay + 3*u*u*s*by + 3*u*s*s*cy + s*s*s*y]) }
          continue
        }
        if (op === 'H') x = +t[i++]; else if (op === 'V') y = +t[i++]; else if (op === 'L') { x = +t[i++]; y = +t[i++] }
        else break
        for (let j = 1; j <= 200; j++) out.push([ax + (x - ax) * j / 200, ay + (y - ay) * j / 200])
      }
      return out
    }
    const seg = (p1, p2, p3, p4) => {
      const d = (p2[0]-p1[0])*(p4[1]-p3[1]) - (p2[1]-p1[1])*(p4[0]-p3[0]); if (!d) return false
      const t = ((p3[0]-p1[0])*(p4[1]-p3[1]) - (p3[1]-p1[1])*(p4[0]-p3[0])) / d
      const u = ((p3[0]-p1[0])*(p2[1]-p1[1]) - (p3[1]-p1[1])*(p2[0]-p1[0])) / d
      return t > 0 && t < 1 && u > 0 && u < 1
    }
    const curves = gs.map(g => ({ pts: flat(g.querySelector('path').getAttribute('d')) }))
    const ends = gs.map(g => {
      const m2 = (g.querySelector('title')?.textContent || '').match(/^([^ ]+) → ([^ ]+)/)
      return m2 ? { a: m2[1], b: m2[2] } : {}
    })
    let crossings = 0
    const pairs = []
    for (let i = 0; i < curves.length; i++) for (let j = i + 1; j < curves.length; j++) {
      if (ends[i].a === ends[j].a || ends[i].a === ends[j].b ||
          ends[i].b === ends[j].a || ends[i].b === ends[j].b) continue
      let hit = false
      for (let p = 0; p + 1 < curves[i].pts.length && !hit; p++)
        for (let q = 0; q + 1 < curves[j].pts.length && !hit; q++)
          if (seg(curves[i].pts[p], curves[i].pts[p+1], curves[j].pts[q], curves[j].pts[q+1])) hit = true
      if (hit) { crossings++; pairs.push([i, j]) }
    }
    return {
      routeGroups: gs.length,
      echoCircles: svg.querySelectorAll('circle').length,
      edgeTitles: gs.filter(g => g.querySelector('title')).length,
      crossings, pairs,
      projectedPills: [...document.querySelectorAll('[data-node]')].map(e => e.dataset.node),
      geometry: { innerWidth, innerHeight, dpr: devicePixelRatio },
    }
  })()`)
  if (m && m.err) die(EX.api, `graph svg measurement failed: ${m.err}`)
  return m
}

async function main() {
  const A = parseArgs(process.argv.slice(2));
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
  const known = Object.keys(manifest.cases);
  if (!Object.hasOwn(manifest.cases, A.caseName)) {
    die(EX.usage, `unknown case ${JSON.stringify(A.caseName)}; known cases: ${known.join(', ')} ` +
        `— a later bead ADDS a case (new test); it is not an existing command`);
  }
  const c = manifest.cases[A.caseName];
  const isCoverage = A.caseName === 'coverage';
  const unwired = (c.surfaces || []).filter(s => !manifest.surfaces_registry.includes(s))
        .concat(c.implemented === false ? c.surfaces : []);
  if (unwired.length && c.implemented === false) {
    console.error(`EXIT 3: case ${A.caseName} is a documented NEW TEST (not yet wired): surfaces ${unwired.join(',')}`);
    process.exit(EX.notImplemented);
  }
  if (unwired.length) {
    die(EX.notImplemented, `case ${A.caseName} names surfaces outside the driver's registry (${unwired.join(', ')}): they are NEW TESTS, add them to capture.mjs + surfaces_registry`);
  }
  if (!A.outDir) {
    A.outDir = path.join(HERE, 'captured',
      'run-' + new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z'));
  }
  const surfacesFiltered = A.only
    ? (c.surfaces || []).filter(s => A.only.includes(s))
    : (c.surfaces || []);
  if (!surfacesFiltered.length) {
    die(EX.usage, `--only ${A.only.join(',')} selects nothing from case ${A.caseName} (case surfaces: ${(c.surfaces || []).join(', ')})`);
  }

  const appRepo = path.resolve(A.appRepo || process.env.UI2_PROOF_APP_REPO ||
    path.join(process.env.UI2_PROOF_HOME || path.join(os.homedir(), '.hermes'), 'hermes-agent'));
  const desktop = path.join(appRepo, 'apps', 'desktop');
  const pluginSrc = A.plugin || path.join(REPO, 'desktop', 'plugin.js');
  const realHome = process.env.UI2_PROOF_HOME || path.join(os.homedir(), '.hermes');
  const hermesBin = A.hermesBin || process.env.UI2_PROOF_HERMES_BIN || 'hermes';

  const identity = {
    ts: new Date().toISOString(),
    case: A.caseName,
    plugin: { candidate: pluginSrc },
    app: { repo: appRepo },
    bench: { ports: { cdp: A.cdpPort, renderer: A.rendererPort } },
    seeds: {},
    config_touched: {},
  };

  // -- preflight (nonzero on any absent input — never a green no-op) --------
  if (!fs.existsSync(pluginSrc)) die(EX.preflight, `candidate plugin missing: ${pluginSrc}`);
  const pluginSha = sha256(pluginSrc);
  identity.plugin.sha256 = pluginSha;
  // The candidate is pinned to THIS repo's head (slice A: "against current
  // merged head" — after merging origin/main, repo_head IS the merge result).
  try {
    identity.candidate_head = execFileSync('git', ['-C', REPO, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
  } catch { identity.candidate_head = 'unknown'; }
  try {
    identity.merge_base_origin_main = execFileSync('git', ['-C', REPO, 'merge-base', 'HEAD', 'origin/main'], { encoding: 'utf8' }).trim();
  } catch { identity.merge_base_origin_main = 'unknown'; }

  const plan = { case: A.caseName, surfaces: surfacesFiltered,
    only: A.only || null,
    seeds: (c.seeds || []).map(s => ({ name: s.name, kind: s.kind, method: s.method })),
    historical_snapshots: (c.historical_snapshots || []).map(s => s.name),
    plugin_sha256: pluginSha, ports: identity.bench.ports, out: A.outDir };
  if (A.plan) { console.log(JSON.stringify({ ok: true, mode: 'plan', plan }, null, 2)); return 0; }

  if (!fs.existsSync(desktop)) die(EX.preflight, `no apps/desktop in app repo ${appRepo} (read SETUP.md; --app-repo or UI2_PROOF_APP_REPO)`);
  // Load the app's intro-copy rotation pool: its headline/body lines mount
  // randomly on the empty-state card, so they are captured noise, not
  // content — masked as exact-line literals (see maskVolatile).
  try {
    for (const line of fs.readFileSync(path.join(desktop, 'src', 'components', 'chat', 'intro-copy.jsonl'), 'utf8').split('\n')) {
      if (!line.trim()) continue;
      const rec = JSON.parse(line);
      for (const f of ['headline', 'body']) if (typeof rec[f] === 'string') CAPTURE_LITERALS.push(rec[f]);
    }
  } catch { /* pool absent: intro lines simply stay unmasked (older app) */ }
  for (const bin of ['electron', 'vite', 'tsc']) {
    if (!fs.existsSync(path.join(desktop, 'node_modules', '.bin', bin)))
      die(EX.preflight, `app checkout not provisioned: node_modules/.bin/${bin} absent in ${desktop} (pnpm install first; see SETUP.md)`);
  }
  try { execFileSync(hermesBin, ['--version'], { stdio: ['ignore', 'pipe', 'pipe'] }); }
  catch { die(EX.preflight, `hermes CLI not runnable (${hermesBin}) — gateway discovery and config revert need it`); }
  identity.app.hermes_version = execFileSync(hermesBin, ['--version'], { encoding: 'utf8' }).trim();
  for (const port of [A.cdpPort, A.rendererPort]) {
    if (!(await portFree(port))) die(EX.preflight, `port ${port} already in use — one bench per port (another proof run or the user's dev server owns it)`);
  }
  let appCommit = 'unknown', appDirtyEntries = -1, appVersion = 'unknown', electronVersion = 'unknown';
  try {
    appCommit = execFileSync('git', ['-C', appRepo, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
    appDirtyEntries = execFileSync('git', ['-C', appRepo, 'status', '--porcelain'], { encoding: 'utf8' })
      .split('\n').filter(Boolean).length;
  } catch { /* keep 'unknown' — honest absence, never a fabricated identity */ }
  try { appVersion = JSON.parse(fs.readFileSync(path.join(desktop, 'package.json'), 'utf8')).version; } catch { /* honest unknown */ }
  Object.assign(identity.app, { commit: appCommit, dirty_entries: appDirtyEntries, package_version: appVersion, electronVersion });
  try {
    electronVersion = fs.readFileSync(path.join(desktop, 'node_modules', 'electron', 'package.json'), 'utf8');
    identity.app.electron_package_version = JSON.parse(electronVersion).version;
  } catch { /* honest unknown */ }

  // -- provision (owned scratch; stale dirs are archived, never rm'd) ------
  if (fs.existsSync(A.outDir)) {
    if (!fs.existsSync(path.join(A.outDir, '.ui2-proof-owned')))
      die(EX.preflight, `--out exists without ownership marker, refusing to touch: ${A.outDir}`);
    fs.renameSync(A.outDir, `${A.outDir}.stale-${Date.now()}`);
  }
  // Bench profile law (field-proven 2026-11-24, the estate-gateway era, twice
  // re-proven against the app-generation bump): a live host gateway makes
  // `gateway ensure` ATTACH-or-refuse for the DEFAULT profile ("one gateway
  // per host serves every profile"), and a STANDALONE default fork is refused
  // outright at this generation ("the host gateway still serves profile
  // 'default'"), so the bench serves its OWN standalone satellite profile
  // (gateway.standalone: true opts out of the host multiplexer) under an
  // isolated HERMES_GATEWAY_LOCK_DIR (the host rendezvous root is the lock
  // dir's own gateway-locks tree — $HERMES_GATEWAY_LOCK_DIR else
  // $XDG_STATE_HOME/hermes/gateway-locks — so the fork neither sees nor
  // claims the estate record). The app launches the pinned profile via
  // <userData>/active-profile.json, so the whole backend is bench-local:
  // the estate gateway is untouched and no trusted input ever lands in the
  // shared config again.
  // The profile REGISTRY enforces single use of a name across homes (hermes-agent
  // fe9a4b58ec): concurrent benches that all pin 'ui2bench' 403 every native call
  // as profile_scope_mismatch except the first holder (field-proven 2026-11-24
  // crew wave — three parallel captures, one green). The name must be unique per
  // bench home: derive it from the owned --out dir, sanitized to the CLI's
  // profile-name law, hash-suffixed for stable length.
  // FIELD-PROVEN APP-GENERATION LAW: the desktop app MUST be at (or under) a
  // build whose hermes:api honors that pinned profile — b9b36c9 (2026-11-24)
  // spawns hermes:api's gateway as the DEFAULT profile of HERMES_HOME instead,
  // which 403s profile_scope_mismatch against the satellite fork and wedges the
  // host record (exit-75 churn). Pass --app-repo at a green-era checkout
  // (0f602c5 proven) until the app half honors the pin again; the proof-harness
  // CI pins the app commit under identity.app.commit either way.
  const BENCH_PROFILE = 'ui2bench-' + crypto.createHash('sha1').update(A.outDir)
    .digest('hex').slice(0, 8);
  const B = { root: A.outDir, home: path.join(A.outDir, 'bench', 'home'),
              profile: path.join(A.outDir, 'bench', 'home', 'profiles', BENCH_PROFILE),
              locks: path.join(A.outDir, 'bench', 'locks'),
              userdata: path.join(A.outDir, 'bench', 'userdata'),
              runs: path.join(A.outDir, 'bench', 'runs'),
              plugins: path.join(A.outDir, 'bench', 'home', 'profiles', BENCH_PROFILE, 'plugins', 'hermes-workflows'),
              dplugins: path.join(A.outDir, 'bench', 'home', 'desktop-plugins', 'hermes-workflows') };
  for (const d of [B.home, B.profile, B.locks, B.userdata, B.runs, B.dplugins,
                   path.join(B.profile, 'plugins'),
                   path.join(A.outDir, 'captures'), path.join(A.outDir, 'logs'), path.join(A.outDir, 'seed')])
    fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(A.outDir, '.ui2-proof-owned'), `${identity.ts} capture.mjs --case ${A.caseName}\n`);

  // Stage the CANDIDATE into the bench home's desktop-plugins root — the app
  // loads exactly these bytes. Staged copy is re-hashed and must equal the
  // candidate before any capture is trusted.
  fs.copyFileSync(pluginSrc, path.join(B.dplugins, 'plugin.js'));
  const stagedSha = sha256(path.join(B.dplugins, 'plugin.js'));
  identity.plugin.staged = path.join(B.dplugins, 'plugin.js');
  identity.plugin.staged_sha256 = stagedSha;
  if (stagedSha !== pluginSha) die(EX.preflight, 'staged plugin bytes diverged from candidate');
  // Copy discovery/state the app's BENCH PROFILE reads (never the real
  // plugins dir — the desktop-half migration would resurrect the installed
  // half over the candidate; and never gateway_state.json — a copied
  // running-state poisons the fork's profile reservation, field-proven:
  // "Gateway runtime already owns profile <real home>").
  for (const f of ['spawn-ledger.json', 'auth.json', 'config.yaml']) {
    const src = path.join(realHome, f);
    if (fs.existsSync(src)) fs.copyFileSync(src, path.join(B.profile, f));
  }
  identity.bench.discovery_copied = ['spawn-ledger.json', 'auth.json', 'config.yaml']
    .filter(f => fs.existsSync(path.join(B.profile, f)));
  // The app's OWN connection state lives in its user-data: seed a local-kind
  // registry so the bench app serves the bench, and pin the launch profile
  // (active-profile.json → startHermes passes `--profile ui2bench`, the one
  // deterministic way to home the primary backend at the bench).
  fs.writeFileSync(path.join(B.userdata, 'connections.json'), JSON.stringify({
    version: 2, primary: 'local', launchMode: 'primary', lastUsed: 'local',
    connections: [{ id: 'local', kind: 'local', label: 'This device' }],
  }) + '\n');
  fs.writeFileSync(path.join(B.userdata, 'connection.json'), JSON.stringify({ mode: 'local', profiles: {} }) + '\n');
  fs.writeFileSync(path.join(B.userdata, 'active-profile.json'), JSON.stringify({ profile: BENCH_PROFILE }) + '\n');
  // Agent half of the CANDIDATE: the bench PROFILE links the repo checkout, so
  // the bench fork mounts /api/plugins/hermes-workflows/ FROM the tree under
  // proof (same symlinked-dev-checkout shape the desktop-half migration
  // supports — the migration re-syncs the desktop half from this symlink, and
  // it must equal the candidate bytes or the staged re-hash below goes red).
  fs.symlinkSync(REPO, path.join(B.profile, 'plugins', 'hermes-workflows'));
  identity.bench.plugins_symlink = REPO;
  identity.bench.profile = BENCH_PROFILE;
  identity.bench.locks = B.locks;

  const benchEnv = { ...process.env, HERMES_HOME: B.home, HERMES_GATEWAY_LOCK_DIR: B.locks };
  // The standalone opt-out rides the COPIED config BEFORE boot: decide() reads
  // it inside the ensure CLI fork (pre-boot plugin-settings writes are
  // fork-normalized away — separate law, see below), and gateway.standalone
  // is what lets the bench fork START beside a live estate multiplexer
  // instead of ATTACH/REFUSE. Written via the profile-scoped CLI so YAML
  // shape stays canonical.
  retryCli(() => writeConfig(hermesBin, ['gateway.standalone', 'true'], benchEnv, BENCH_PROFILE));
  const sup = new Supervisor(A.outDir);
  sup._ownedUserData = B.userdata;
  sup._viteMarker = `--port ${A.rendererPort} --strictPort`;
  const touched = [];
  const revertFailures = [];
  let py = process.env.UI2_PROOF_PYTHON || '';
  let hermesAbs = hermesBin;
  const seededRuns = [];

  try {
    // -- boot the dev renderer (owned vite, strict port) --------------------
    sup.start('renderer', process.execPath,
      [path.join(desktop, 'node_modules', 'vite', 'bin', 'vite.js'),
       '--host', '127.0.0.1', '--port', String(A.rendererPort), '--strictPort'],
      { cwd: desktop, env: process.env });
    let up = false;
    for (let i = 0; i < 120 && !up; i++) {
      try { up = (await fetch(`http://127.0.0.1:${A.rendererPort}/`)).ok; } catch { /* warming */ }
      if (!up) await sleep(500);
    }
    if (!up) die(EX.boot, `dev renderer never served http://127.0.0.1:${A.rendererPort}/ (see logs/renderer.log)`);

    // -- pre-ensure the bench fork BEFORE the app boots ----------------------
    // A fresh profile bootstraps its backend (plugin deps via uv) on first
    // ensure; a fresh boot's "Installing Python dependencies" phase outruns
    // the app's own boot modal deadline (field-proven: "Hermes couldn't
    // start" while uv installs under crew load). The CLI ensure pays that
    // cost here, under OUR paint budget, so electron attaches to a live
    // gateway on its first request. Idempotent once warm.
    try {
      retryCli(() => execFileSync(hermesBin, ['--profile', BENCH_PROFILE, 'gateway', 'ensure', '--json'],
        { encoding: 'utf8', timeout: A.paintBudgetMs + 30_000, maxBuffer: 8 * 1024 * 1024, env: benchEnv }));
      identity.bench.pre_ensure = 'ok';
    } catch (e) {
      identity.bench.pre_ensure = `best-effort failed: ${String(e.stderr || e.message).slice(0, 200)}`;
    }

    // -- prebuild the electron main (skill bench recipe), then boot ---------
    if (A.prebuild) {
      execFileSync(path.join(desktop, 'node_modules', '.bin', 'tsc'),
        ['--build', 'tsconfig.electron.json'], { cwd: desktop, stdio: 'ignore', timeout: 300_000 });
      execFileSync(process.execPath, ['scripts/bundle-electron-main.mjs', '--dev'],
        { cwd: desktop, stdio: 'ignore', timeout: 120_000 });
    }
    const electronEnv = { ...process.env,
      HERMES_DESKTOP_DEV_SERVER: `http://127.0.0.1:${A.rendererPort}`,
      HERMES_DESKTOP_CDP_PORT: String(A.cdpPort),
      HERMES_HOME: B.home, HERMES_GATEWAY_LOCK_DIR: B.locks };
    sup.start('electron', path.join(desktop, 'node_modules', '.bin', 'electron'),
      ['.', `--user-data-dir=${B.userdata}`], { cwd: desktop, env: electronEnv });

    // Trusted inputs are written AFTER the bench backend registers (the fork
    // normalizes config.yaml at boot — a pre-boot write is silently dropped,
    // field-proven). Both keys are read fresh by the door per request; the
    // tray settings-gate is a bootstrap read, so the mid-run reload below
    // re-runs plugin registration with the setting in place. The fork
    // registers gateway_state.json in the BENCH PROFILE home (the launch
    // profile pins it); the bench root path is accepted too (older homes).
    {
      const gT0 = Date.now();
      const statePaths = [path.join(B.profile, 'gateway_state.json'), path.join(B.home, 'gateway_state.json')];
      while (!statePaths.some(p => fs.existsSync(p)) && Date.now() - gT0 < 90_000)
        await sleep(500);
      if (!statePaths.some(p => fs.existsSync(p)))
        die(EX.boot, 'bench backend never registered gateway_state.json (see logs/electron.log)');
    }
    for (const [key, value] of [['plugins.entries.hermes-workflows.settings.runs_root', B.runs],
                                ['plugins.entries.hermes-workflows.settings.tray', true]]) {
      // A sibling bench mid-source-update makes EVERY CLI call exit transiently;
      // retry the read/write pair together so `before` and `after` stay coherent.
      const before = retryCli(() => {
        const b = readConfigValue(hermesBin, key, benchEnv, BENCH_PROFILE);
        writeConfig(hermesBin, [key, String(value)], benchEnv, BENCH_PROFILE);
        return b;
      });
      identity.config_touched[key] = { before, after: value, scope: `bench profile ${BENCH_PROFILE} (isolated — shared config untouched)` };
      touched.push(key);
    }

    // -- engine seed (baseline/gate): launch the held-gate graph through the
    // door. The coverage case seeds a FIXTURE CENSUS instead (seed_fixture.py
    // — read-model bytes, no door launch); the door graph stays non-coverage.
    const engSeed = (c.seeds || []).find(s => s.kind === 'engine_seed' && s.method === 'door_run');
    if (!engSeed && !isCoverage) die(EX.preflight, `case ${A.caseName} has no door_run engine seed`);
    const graphFile = path.join(A.outDir, 'seed', 'held-gate.graph.json');
    if (engSeed) fs.writeFileSync(graphFile, JSON.stringify(engSeed.graph, null, 2) + '\n');
    let runId = null;
    if (!hermesAbs.startsWith('/')) {
      try { hermesAbs = execFileSync('/usr/bin/which', [hermesAbs], { encoding: 'utf8' }).trim() || hermesAbs; } catch { /* PATH lookup stays the door's own problem */ }
    }
    // Door interpreter: the CLI shim itself names it (`exec <python> …`), so
    // the seed runs under the SAME interpreter the gateway loads the door
    // with. Fallbacks: UI2_PROOF_PYTHON (hoisted), then a >=3.10 python3 probe
    // (the door uses PEP-604 annotations at def time — system 3.9 dies on them).
    if (!py) {
      try {
        const shim = fs.readFileSync(hermesAbs, 'utf8').slice(0, 4000);
        const m = shim.match(/^exec\s+(\S*python\S*)\b/m);
        if (m && fs.existsSync(m[1])) py = m[1];
      } catch { /* not a readable shim */ }
    }
    if (!py) {
      for (const cand of ['python3', 'python3.14', 'python3.12', 'python3.10']) {
        try {
          execFileSync(cand, ['-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)']);
          py = cand; break;
        } catch { /* too old or absent */ }
      }
    }
    if (!py) die(EX.preflight, 'no >=3.10 interpreter found for the door (set UI2_PROOF_PYTHON)');
    // A case may run its door children through the repo's zero-token fake CLI
    // (tests/fake_hermes.py): not +x, so wrap it with the discovered python.
    let childBin = hermesAbs;
    if (engSeed?.child_binary) {
      const wrapper = path.join(A.outDir, 'seed', 'fake-hermes.sh');
      fs.writeFileSync(wrapper, `#!/bin/sh\nexec ${py} ${path.join(REPO, engSeed.child_binary)} "$@"\n`);
      fs.chmodSync(wrapper, 0o755);
      childBin = wrapper;
    }
    if (engSeed) try {
      runId = execFileSync(py, [path.join(HERE, 'seed_run.py'),
        '--repo', REPO, '--runs-root', B.runs, '--graph-file', graphFile,
        '--wait-held-s', String(engSeed.wait_held_s ?? 25)],
        { encoding: 'utf8', timeout: 60_000,
          env: { ...process.env, WF_RUNS_ROOT: B.runs, HERMES_WF_HERMES_BIN: childBin, HERMES_HOME: B.home, HERMES_GATEWAY_LOCK_DIR: B.locks } }).trim();
    } catch (e) {
      die(EX.api, `engine seed launch failed (seed_run.py): ${String(e.stderr || e.message).slice(0, 400)}`);
    }
    if (runId) {
      identity.seeds.held_gate_run = { kind: 'engine_seed', run_id: runId, graph_sha256: sha256(graphFile) };
      seededRuns.push(runId);
    }
    // Fixture census (coverage case): rows materialized THROUGH the shared
    // read model (wfcommon constants, run_state-acceptable trio + events) so
    // the route — not a mock — counts them. seed_fixture.py prints
    // {ids, names}; ids sort by name-DESC (the traversal contract), names are
    // what the pane rows render.
    const seedFixture = (count, start) => {
      const out = execFileSync(py, [path.join(HERE, 'seed_fixture.py'),
        '--repo', REPO, '--runs-root', B.runs, '--count', String(count), '--start', String(start)],
        { encoding: 'utf8', timeout: 120_000, env: { ...process.env, HERMES_HOME: B.home } });
      try { return JSON.parse(out); }
      catch { die(EX.api, `seed_fixture.py printed non-JSON: ${out.slice(0, 200)}`); }
    };

    // Graph case (bd 33h): materialize the pinned shelf snapshot + the MF1
    // synthetic trio beside the engine seed, then wait for the engine seed to
    // TERMINATE through the shared read model — the strip frames must show an
    // exact ENDED census, never a mid-flight count.
    let graphIds = null;
    if (A.caseName === 'graph') {
      const snap = (c.historical_snapshots || [])[0];
      if (!snap) die(EX.preflight, 'graph case pins no historical_snapshot');
      let seeded;
      try {
        seeded = JSON.parse(execFileSync(py, [path.join(HERE, 'seed_graph.py'),
          '--repo', REPO, '--runs-root', B.runs, '--fixture', snap.fixture,
          '--fixture-sha256', snap.run_json_sha256, '--wait-run', runId],
          { encoding: 'utf8', timeout: 150_000,
            env: { ...process.env, HERMES_HOME: B.home } }).trim().split('\n').pop());
      } catch (e) {
        die(EX.api, `graph fixture seed failed (seed_graph.py): ${String(e.stderr || e.message).slice(0, 400)}`);
      }
      graphIds = { council: seeded.council_run_id, mf1: seeded.mf1_run_id, thr: runId };
      identity.seeds.graph_fixtures = seeded;
    }

    // -- CDP attach; enable decision; reload (skill gotcha wall) ------------
    let cdp = await connectCdp(A.cdpPort, A.rendererPort);
    {
      // Storage can be briefly denied while the first document is replaced by
      // the app boot — bounded retry, then a real failure.
      let stored = 'denied';
      const dT0 = Date.now();
      while (stored !== 'ok' && Date.now() - dT0 < 20_000) {
        stored = await cdp.evl(`(() => { try {
          localStorage.setItem('hermes.desktop.pluginDecisions.v2', JSON.stringify({'hermes-workflows': true}));
          return 'ok';
        } catch { return 'denied' } })()`);
        if (stored !== 'ok') { await sleep(750); cdp = await connectCdp(A.cdpPort, A.rendererPort, 20_000); }
      }
      if (stored !== 'ok') die(EX.boot, 'localStorage never writable on the renderer — enable decision impossible');
    }
    // bd yjp (coverage case): arm the transport mock BEFORE the activation
    // reload — a same-session Fetch domain survives the reload, and the
    // pre-decision document CANNOT have fired /runs yet (the plugin is not
    // enabled until this reload), so the LOADING frame is deterministic:
    // activation's first census page meets the paused edge. Baseline/gate
    // keep their close/reconnect dance byte-for-byte.
    let mock = null;
    // Rules survive session churn: every re-arm re-applies them, and every
    // setRules site records them here (the field-proven #720 lesson — the
    // app's own gateway ensure can restart the fork mid-walk; the pane then
    // wears the boot-failure modal and a rule-less poll dies at 45 s).
    let mockRules = [];
    const armRules = rs => { mockRules = rs; if (mock) mock.setRules(rs); };
    const armMock = async () => {
      mock = await mockRuns(cdp);
      armRules([{ urlPattern: '*workflows/runs*', action: 'stall' }]);
    };
    if (isCoverage) await armMock();
    await cdp.send('Page.reload', { ignoreCache: true });
    if (!isCoverage) {
      cdp.ws.close();
      await sleep(1500);
      cdp = await connectCdp(A.cdpPort, A.rendererPort, 60_000);
    } else {
      await sleep(1500);   // keep the session — the armed mock must survive it
    }
    // Boot can re-navigate the window (main restores the dev-server URL after
    // an early reload): be resilient — reconnect and re-paint-probe for up to
    // 60 s instead of trusting one document. On give-up, dump what we are
    // actually attached to (target list + one shot) before dying.
    {
      const pT0 = Date.now();
      for (;;) {
        try { await waitPainted(cdp, 6_000); break; }
        catch (e) {
          if (Date.now() - pT0 > A.paintBudgetMs) {
            try {
              const list = await (await fetch(`http://127.0.0.1:${A.cdpPort}/json`)).json();
              fs.writeFileSync(path.join(A.outDir, 'logs', 'targets-on-fail.json'),
                JSON.stringify(list.map(t => ({ type: t.type, url: t.url })), null, 2));
              await shoot(cdp, A.outDir, '00-diagnostic-unpainted.png');
            } catch { /* diagnostics best-effort */ }
            throw e;
          }
          try { cdp.ws.close(); } catch { /* already gone */ }
          cdp = await connectCdp(A.cdpPort, A.rendererPort, 30_000);
          if (isCoverage) await armMock();   // the session moved — re-arm
        }
      }
    }

    // Checked API attachment (1): the dev-served registry shows the plugin's
    // surfaces registered on the REAL renderer (skill probe). Bounded poll:
    // activation follows the fs-watch push + bundle import and can lag boot.
    let registry = { routes: [], panes: [], directives: [], composer: [] }, records = {};
    // A cold bench profile bootstraps backend deps on first ensure; every
    // attach probe must outlast that install, so the probe budgets ride the
    // paint knob (default 60 s keeps CI-era benches honest; loaded boxes pass
    // --paint-budget 300 and wait accordingly).
    const probeBudgetMs = Math.max(45_000, A.paintBudgetMs);
    // Navigation-tolerant probe eval (field-proven 2026-11-24): an SPA route
    // reset or self-reload under crew load kills an in-flight Runtime.evaluate
    // with 'Inspected target navigated or closed'. Inside a POLL loop that is
    // a miss, not a death: reconnect and hand the loop its no-hit shape.
    const evlPoll = async (expr, fallback) => {
      try { return await cdp.evl(expr); }
      catch (e) {
        const m = String((e && e.message) || e);
        if (!/navigated or closed|WebSocket is not open|socket hang up|target closed|not attached/i.test(m)) throw e;
        await sleep(1200);
        try { cdp.ws.close(); } catch { /* already gone */ }
        cdp = await connectCdp(A.cdpPort, A.rendererPort, 30_000);
        return fallback;
      }
    };
    const rT0 = Date.now();
    while (Date.now() - rT0 < probeBudgetMs) {
      registry = await evlPoll(`(async () => {
        const mod = await import('/src/contrib/registry.ts');
        const reg = mod.registry;
        const names = area => { try { return (reg.getArea(area) || []).map(e => e.id ?? e.name ?? String(e)) } catch { return [] } };
        return { routes: names('routes'), panes: names('panes'),
                 directives: names('transcript.directives'), composer: names('composer.underside') };
      })()`, { routes: [], panes: [], directives: [], composer: [] });
      try {
        records = await cdp.evl(`(async () => {
          const m = await import('/src/contrib/plugins-store.ts');
          const rec = m.$pluginRecords.get();
          return Object.fromEntries(Object.entries(rec).map(([k, v]) => [k, { error: v?.error ?? null, active: !!v?.active }]))
        })()`) || records;
      } catch { /* store shape differs on older builds — registry alone decides */ }
      const attachedNow = registry.panes.some(x => String(x).includes('workflow'));
      if (attachedNow) break;
      await sleep(1500);
    }
    identity.registry = registry;
    identity.plugin_records = records;
    const surfacesWanted = new Set(surfacesFiltered);
    const attached = surfacesWanted.has('pane_workflows') ? registry.panes.some(x => String(x).includes('workflow'))
      : registry.panes.length > 0;
    const postLoadSha = sha256(path.join(B.dplugins, 'plugin.js'));
    identity.plugin.staged_sha256_after_load = postLoadSha;
    if (postLoadSha !== pluginSha)
      die(EX.api, `loaded desktop half drifted from the candidate during boot (${postLoadSha.slice(0,12)} != ${pluginSha.slice(0,12)})`);
    if (!attached) {
      try { await shoot(cdp, A.outDir, '00-diagnostic-unattached.png'); } catch { /* diagnostics are best-effort */ }
      die(EX.api, `plugin API attachment unproven: registry panes=${JSON.stringify(registry.panes)} ` +
          `plugin_records=${JSON.stringify(records).slice(0, 400)} (diagnostic shot in captures/ if present)`);
    }

    // Checked API attachment (2): the seeded run row can ONLY come from
    // GET /api/plugins/hermes-workflows/ — proven by its rendering.
    // Graph case: the pane proof centers on the PINNED shelf snapshot —
    // its row can only render from GET /runs too, and it is the fixture whose
    // projection arithmetic (10/14/28) the case measures.
    // The pane column only becomes real once the splash clears (field-proven:
    // global innerText/clicks pass on DOM UNDER a CONNECTING overlay). The
    // pane-rendered content can only come from GET /api/plugins/hermes-workflows/.
    const paneRegion = { xMin: 440, yMin: 40, bottomMargin: 90 };
    await waitConnected(cdp, probeBudgetMs);
    const shots = [];
    // Field-proven (pair regen try2): route-restore can re-mount the chat
    // empty-state over the pane column exactly between the question hit and
    // the content read — everything painted is then intro-copy + clocks, and
    // the masked content layer lands trivial. Poll the column text until the
    // MASKED layer is non-trivial (shoot's own threshold) before shooting.
    const stableColumnText = async (region, budgetMs = 25_000) => {
      const t0 = Date.now();
      for (;;) {
        const txt = await cdp.evl(columnTextJS(region));
        const masked = maskVolatile(txt, CAPTURE_LITERALS).replace(/\n+/g, '');
        if (masked.length >= 40 || Date.now() - t0 > budgetMs) return txt; // shoot() decides the death
        await sleep(1000);
      }
    };
    // Checked API attachment (2): proven per mode below (baseline/gate: the
    // seeded run row IN THE PANE COLUMN — rows render the run NAME, the id
    // rides card/directive text, not every row; coverage: the whole-census
    // summary rendered over a fixture census that exceeds one page).
    const runName = engSeed ? engSeed.graph.name : null;
    const paneRowNeedle = graphIds ? 'wave6-council' : runName;
    if (isCoverage) {
      const fixture = (c.seeds || []).find(s => s.kind === 'engine_seed' && s.method === 'fixture_census');
      if (!fixture) die(EX.preflight, `case ${A.caseName} has no fixture_census seed`);
      const COUNT = Number(fixture.count) || 133;
      // Re-click the WORKFLOWS tab until the pane content itself carries
      // `needle`. The pane LIST column is the left column under the tab
      // strip (vision-proven), so the probe is region-free with exact
      // matches — the needle texts here are census-state strings unique on
      // the page. Field-proven recoverances, one budget: (a) route-restore
      // flips the view back after the tab click — re-click every pass;
      // (b) a CONNECTING splash passes global innerText waits — re-wait the
      // attach; (c) the app's gateway ensure loses a restart race and paints
      // the "Hermes couldn't start" modal — click Retry (#720 law; coverage
      // frame 01's first real-app death, fork SIGTERM + status-1 re-ensure).
      // Dumps a diagnostic shot + body excerpt + /runs resource timing on
      // give-up.
      const covPoll = async (needle, shotName, why) => {
        const t0 = Date.now();
        let last = null;
        for (;;) {
          try {
            last = await cdp.evl(locateJS(needle, { exact: true }));
            if (!last.err) return;
          } catch (e) {
            const m = String((e && e.message) || e);
            if (!/navigated or closed|WebSocket is not open|socket hang up|target closed|not attached/i.test(m)) throw e;
            await sleep(1200);
            try { cdp.ws.close(); } catch { /* already gone */ }
            cdp = await connectCdp(A.cdpPort, A.rendererPort, 30_000);
            mock = await mockRuns(cdp);
            mock.setRules(mockRules);   // session moved: same rules back
            last = { err: 'reconnecting' };
          }
          if (Date.now() - t0 > probeBudgetMs) break;
          const modalUp = await cdp.evl(`document.body.innerText.includes("couldn't start")`).catch(() => false);
          if (modalUp) { try { await trustedClick(cdp, 'Retry', { exact: true, ci: true }); } catch { /* modal between frames */ } }
          const occludedBySplash = last.err === 'occluded' && /connecting/i.test(String(last.over || ''));
          if (occludedBySplash) {
            try { await waitConnected(cdp, 15_000); } catch { /* loop budget decides */ }
          }
          try { await trustedClick(cdp, 'workflows', { exact: true, ci: true }); } catch { /* tab not painted yet */ }
          await sleep(1200);
        }
        const diag = await cdp.evl(`(() => ({
          body: (document.body.innerText || '').replace(/\\s+/g, ' ').slice(0, 300),
          runsReqs: performance.getEntriesByType('resource').filter(r => r.name.includes('workflows/runs'))
            .map(r => ({ name: r.name.slice(0, 160), start: Math.round(r.startTime), dur: Math.round(r.duration) })).slice(-6)
        }))()`).catch(() => ({}));
        try { await shoot(cdp, A.outDir, shotName); } catch { /* best effort */ }
        try { fs.writeFileSync(path.join(A.outDir, 'logs', shotName.replace(/\.png$/, '-diag.json')),
                               JSON.stringify({ needle, locate: last, ...diag }, null, 2)); } catch { /* best effort */ }
        die(EX.api, `${why}: ${JSON.stringify(last.err || last)}${last.over ? ` over ${JSON.stringify(last.over)}` : ''} | body=${JSON.stringify((diag.body || '').slice(0, 160))} | runsReqs=${JSON.stringify(diag.runsReqs || [])}`);
      };
      // Scope probe (field-proven #12: hermes:api 403 profile_scope_mismatch
      // survived the satellite home + self-link): talk to the fork directly
      // over its UDS BEFORE the frame walk needs it, and record which
      // selector it accepts — unscoped, ?profile=<bench>, /p/<bench>/api/...
      // prefixed, and /api/profiles.
      try {
        const statePath = [path.join(B.profile, 'gateway_state.json'),
                           path.join(B.home, 'gateway_state.json')].find(p => fs.existsSync(p));
        const st = statePath ? JSON.parse(fs.readFileSync(statePath, 'utf8')) : null;
        const sockDir = statePath ? path.dirname(statePath) : null;
        const sock = sockDir && fs.existsSync(path.join(sockDir, 'gateway.sock'))
          ? path.join(sockDir, 'gateway.sock') : null;
        const hits = {};
        if (sock) {
          for (const [k, u] of Object.entries({
            unscoped: `/api/plugins/hermes-workflows/runs?offset=0&limit=2`,
            named: `/api/plugins/hermes-workflows/runs?offset=0&limit=2&profile=${BENCH_PROFILE}`,
            prefixed: `/p/${BENCH_PROFILE}/api/plugins/hermes-workflows/runs?offset=0&limit=2`,
            profiles: `/api/profiles`,
          })) {
            hits[k] = await new Promise(res => {
              const req = http.request({ socketPath: sock, path: u, method: 'GET',
                                         headers: { host: 'localhost' } },
                r => { let b = ''; r.on('data', d => { b += d; });
                       r.on('end', () => res({ status: r.statusCode, body: b.slice(0, 160) })); });
              req.on('error', e => res({ err: String(e.message).slice(0, 120) }));
              req.setTimeout(5000, () => { req.destroy(new Error('uds timeout')); });
            });
          }
        }
        identity.gateway_scope_probe = { sock, hits, state_pid: st?.pid ?? null, state_home: st?.hermes_home ?? null };
        fs.writeFileSync(path.join(A.outDir, 'logs', 'scope-probe.json'),
                         JSON.stringify(identity.gateway_scope_probe, null, 2) + '\n');
      } catch (e) { identity.gateway_scope_probe = { err: String(e).slice(0, 200) }; }
      try {
        // 01 LOADING: stall every /runs page, then open the pane — the one
        // honest costume for a census not yet answered.
        armRules([{ urlPattern: '*workflows/runs*', action: 'stall' }]);
        await covPoll('Loading…', '00-diagnostic-loading.png',
                      'loading state never rendered IN THE PANE COLUMN');
        shots.push({ surface: 'pane_workflows', state: 'loading (every /runs page stalled)',
                     ...(await shoot(cdp, A.outDir, '01-coverage-loading.png', null, await stableColumnText(paneRegion))) });
        // 02 EMPTY: release the stall on the unseeded bench — an ANSWERED
        // empty census names the roots it scanned; empty is not loading.
        mock.releaseStalled();
        await waitText(cdp, 'No runs', 30_000);
        identity.coverage = { roots_line_seen: await cdp.evl(`document.body.innerText.includes('roots:')`) };
        shots.push({ surface: 'pane_workflows', state: 'empty census answered (roots named)',
                     ...(await shoot(cdp, A.outDir, '02-coverage-empty.png', null, await stableColumnText(paneRegion))) });

        // Seed a >1-page census THROUGH the shared read model, then reload so
        // the pane performs a FRESH page-walk against the real route.
        const seeded = seedFixture(COUNT, 0);
        identity.coverage.fixture = { count: COUNT, first_id: seeded.ids[0],
          last_id: seeded.ids[seeded.ids.length - 1],
          ids_sha256: crypto.createHash('sha256').update(seeded.ids.join('\n')).digest('hex') };
        await cdp.send('Page.reload', { ignoreCache: true });
        await sleep(1500);
        {   // keep the armed session across the reload; re-arm if it moved
          const pT0 = Date.now();
          for (;;) {
            try { await waitPainted(cdp, 8_000); break; }
            catch (e) {
              if (Date.now() - pT0 > A.paintBudgetMs) throw e;
              try { cdp.ws.close(); } catch { /* already gone */ }
              cdp = await connectCdp(A.cdpPort, A.rendererPort, 30_000);
              mock = await mockRuns(cdp);
              mock.setRules(mockRules);   // session moved: same rules back
            }
          }
        }
        await covPoll(`runs ${COUNT} ·`, '00-diagnostic-census.png',
                      'census summary never rendered IN THE PANE COLUMN');
        identity.api_attachment = { via: 'whole-census summary rendered by the pane from GET /runs', counted: COUNT };
        shots.push({ surface: 'pane_workflows', state: `full census: ${COUNT} counted rows (>1 page), all loaded`,
                     ...(await shoot(cdp, A.outDir, '03-coverage-census-full.png', null, await stableColumnText(paneRegion))) });

        // 04/05 the FIRST-PAGE CEILING is gone: the DEEPEST counted row (last
        // position — only reachable from page 2 of the route) renders, and its
        // RECORD opens. The record-page proof is the hoisted style element
        // ONLY WorkflowsPage mounts (plugin.js PolishStyles, one per document).
        const deepest = seeded.names[0];
        await waitText(cdp, deepest, 20_000);
        const rowPt = await locateClickPoint(cdp, deepest);
        shots.push({ surface: 'pane_workflows', state: `counted row ${deepest} rendered past the first 100`,
                     ...(await shoot(cdp, A.outDir, '04-coverage-deepest-row.png', rowPt.rect)) });
        await trustedClick(cdp, deepest);
        let recordUp = false;
        const recT0 = Date.now();
        while (!recordUp && Date.now() - recT0 < 20_000) {
          recordUp = await cdp.evl(`!!document.querySelector('style[data-plugin="hermes-workflows"][href="hermes-workflows.3.css"]')`);
          if (!recordUp) await sleep(400);
        }
        if (!recordUp) die(EX.api, 'the deepest counted row never opened its record page (hoisted record style absent)');
        shots.push({ surface: 'pane_workflows', state: `record page for ${deepest} opened by runQuery(id)`,
                     ...(await shoot(cdp, A.outDir, '05-coverage-record-page.png')) });

        // 06 ERROR with cached data: fail every /runs poll — the fixture rows
        // read `interrupted` (never TERMINAL), so the pane's own 4 s loop
        // trips the error, and the CACHED CENSUS WINS: rows stay on screen and
        // the failure wears the clickable stale chip.
        armRules([{ urlPattern: '*workflows/runs*', action: 'fail' }]);
        await waitText(cdp, 'stale — retry', 25_000);
        if (!(await cdp.evl(`document.body.innerText.includes('runs ${COUNT}')`)))
          die(EX.api, 'a refetch failure evicted the cached census — data must win over error');
        shots.push({ surface: 'pane_workflows', state: 'refetch failed: cached census kept, stale chip clickable',
                     ...(await shoot(cdp, A.outDir, '06-coverage-error-cached.png', null, await stableColumnText(paneRegion))) });

        // 07 RECOVERY: the chip's click invalidates the runs key — the walk
        // re-runs from offset 0 and picks up a census that GREW while the edge
        // was failing (one more fixture row seeded first), so the count moving
        // proves a real re-walk, not a redraw.
        seedFixture(1, COUNT);
        armRules([]);
        await trustedClick(cdp, 'stale — retry');
        await waitText(cdp, `runs ${COUNT + 1} ·`, 25_000);
        const recovered = await cdp.evl(`(() => { const t = document.body.innerText;
          return { stale: t.includes('stale'), loaded: /loaded \\d+ of/.test(t) }; })()`);
        if (recovered.stale || recovered.loaded)
          die(EX.api, `retry did not fully recover (stale=${recovered.stale} loaded=${recovered.loaded})`);
        shots.push({ surface: 'pane_workflows', state: `retry re-walked every page: census now counts ${COUNT + 1}`,
                     ...(await shoot(cdp, A.outDir, '07-coverage-recovery.png', null, await stableColumnText(paneRegion))) });

        // 08 PARTIAL FETCH: fulfill the SECOND page with an honest empty slice
        // — the walk stops short, the summary stays GLOBAL (still counts 134),
        // and the line says `loaded 100 of 134` instead of implying coverage.
        armRules([{ urlPattern: '*offset=100*', action: 'fulfill',
                     body: JSON.stringify({ runs: [], total: COUNT + 1, counts: { running: 0 } }) }]);
        await waitText(cdp, `loaded 100 of ${COUNT + 1}`, 25_000);
        shots.push({ surface: 'pane_workflows', state: 'page-2 flake: loaded < total shown honestly',
                     ...(await shoot(cdp, A.outDir, '08-coverage-partial-fetch.png', null, await stableColumnText(paneRegion))) });
        await mock.off();
      } finally { await mock.off(); }
    } else {
    {
      let wT0 = Date.now();
      for (;;) {
        const hit = await evlPoll(locateJS(paneRowNeedle, { region: paneRegion }), { err: 'reconnecting' });
        if (!hit.err) break;
        if (Date.now() - wT0 > probeBudgetMs) {
          try { await shoot(cdp, A.outDir, '00-diagnostic-pane.png'); } catch { /* best effort */ }
          const loc = await cdp.evl('location.pathname').catch(() => 'unknown');
          die(EX.api, `seeded run row never rendered IN THE PANE COLUMN (${JSON.stringify(hit.err)}${hit.over ? ` over ${JSON.stringify(hit.over)}` : ''}; pathname=${JSON.stringify(loc)}) — diagnostic shot in captures/ if present`);
        }
        // Boot-modal recovery (field-proven): a backend still starting puts
        // the "Hermes couldn't start" modal over the chrome; dismiss it by
        // clicking Retry and keep polling within the probe budget.
        const modalUp = await evlPoll(`document.body.innerText.includes("couldn't start")`, false);
        if (modalUp) { try { await trustedClick(cdp, 'Retry', { exact: true, ci: true }); } catch { /* modal between frames */ } }
        // Splash recovery (field-proven, pair regen): after a route restore the
        // renderer can fall BACK to the CONNECTING splash; the pane poll then
        // burns its whole budget 'no-match' under the overlay (diagnostic shot
        // proves it). Re-wait the attach (bounded) before the next tab click.
        const underSplash = await evlPoll(`(() => {
          const el = document.elementFromPoint(Math.floor(innerWidth/2), Math.floor(innerHeight/2));
          const t = ((el && (el.innerText || el.textContent)) || '').trim().toLowerCase();
          return t.includes('connecting') || t.length === 0;
        })()`, true);
        // Occlusion-class recovery (field-proven, regen try2): the row IS
        // painted under a CONNECTING fragment INSIDE the pane column while
        // viewport-center shows restored chat — the center probe says false.
        // locateJS already reports the covering text: 'occluded over
        // CONNECTING' is direct splash evidence; re-wait attach on it too.
        const occludedBySplash = hit.err === 'occluded' && /connecting/i.test(String(hit.over || ''));
        if (underSplash || occludedBySplash) {
          try { await waitConnected(cdp, 15_000); wT0 = Date.now() - probeBudgetMs + 30_000; } catch { /* loop budget decides */ }
        }
        // Route-restore race (field-proven: diagnostic shows the app restored
        // the chat view AFTER the tab click — SESSIONS active, hero rendered):
        // re-click the sidebar WORKFLOWS tab every poll until the pane column
        // itself carries the seeded row. A startup modal (lock race) gets the
        // bounded Retry treatment — same field-proven lesson.
        try { if (await retryGateIfModal(cdp)) wT0 = Date.now(); } catch { /* eval transient */ }
        try { await trustedClick(cdp, 'workflows', { exact: true, ci: true }); } catch { /* tab not painted yet */ }
        await sleep(1200);
      }
    }
    identity.api_attachment = { via: 'registry + live seeded run row rendered through the plugin API route', run_id: runId };

    // 01/02 pane: runs list, then the held-gate run detail. The captured
    // CONTENT of each viewport shot is the pane column's painted text (same
    // region predicate as the locators), volatile-masked into contents/.
    shots.push({ surface: 'pane_workflows',
      state: graphIds ? 'runs list: engine-seeded fan + pinned snapshot + synthetic MF1' : 'runs list, seeded held-gate run',
      ...(await shoot(cdp, A.outDir, '01-pane-runs.png', null, await stableColumnText(paneRegion))) });
    await trustedClick(cdp, paneRowNeedle, { region: paneRegion });
    if (graphIds) {
      // 02 the pinned council's GraphView; 03 its fans expanded: projected
      // child pills (critics.0..5), footer attempt ticks, no ghost rings.
      {
        const gT0 = Date.now();
        let painted = false;
        while (!painted && Date.now() - gT0 < 30_000) {
          painted = await cdp.evl(`(() => { const s = [...document.querySelectorAll('svg')]
            .filter(x => x.querySelectorAll('path').length >= 3); return s.length > 0 })()`);
          if (!painted) await sleep(500);
        }
        if (!painted) die(EX.api, 'council detail GraphView never painted route paths in the pane');
      }
      shots.push({ surface: 'pane_workflows', state: 'council GraphView (pinned shelf fixture, no fan interaction)',
        ...(await shoot(cdp, A.outDir, '02-pane-council-graphview.png', null, await stableColumnText(paneRegion))) });
      const toggled = await cdp.evl(`(() => {
        const btn = [...document.querySelectorAll('button[aria-label]')].find(b => /fan-out items/i.test(b.getAttribute('aria-label') || ''));
        if (!btn) return null;
        const r = btn.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 } })()`);
      if (!toggled) die(EX.api, 'no fan-out expand toggle on the page canvas');
      for (const t of ['mouseMoved', 'mousePressed', 'mouseReleased'])
        await cdp.send('Input.dispatchMouseEvent', { type: t, x: toggled.x, y: toggled.y,
          button: t === 'mouseMoved' ? undefined : 'left', clickCount: 1, buttons: t === 'mouseReleased' ? 0 : 1 });
      await sleep(1300);
      shots.push({ surface: 'pane_workflows', state: 'council fans expanded on the page canvas (ItemCards + footer ticks)',
        ...(await shoot(cdp, A.outDir, '03-pane-council-expanded.png', null, await stableColumnText(paneRegion))) });
      identity.graph_measurement = { page: await measureGraphSvg(cdp, 14) };
      identity.graph_measurement.page.projected_pills = identity.graph_measurement.page.projectedPills.filter(n => /^critics\.\d+$/.test(n));
    } else {
    // The gate question must render IN THE DETAIL VIEW: the expanded tray run
    // card shows the same question text (field-proven: shot 02 was 'Loading…'
    // while the question wait passed on the tray card).
    {
      const qT0 = Date.now();
      let qRetryT0 = Date.now();
      for (;;) {
        const hit = await evlPoll(locateJS(engSeed.graph.nodes[1].question, { region: paneRegion }), { err: 'reconnecting' });
        if (!hit.err) break;
        try { if (await retryGateIfModal(cdp)) qRetryT0 = Date.now(); } catch { /* eval transient */ }
        // die only when the wall AND the post-Retry reload grace are both past
        // (Retry budget is bounded, so this cannot spin forever).
        if (Date.now() - qT0 > 30_000 && Date.now() - qRetryT0 > 15_000) {
          try { await shoot(cdp, A.outDir, '00-diagnostic-detail.png'); } catch { /* best effort */ }
          die(EX.api, `held-gate question never rendered IN THE PANE DETAIL (${JSON.stringify(hit.err)}) — diagnostic shot in captures/ if present`);
        }
        await sleep(600);
      }
    }
    shots.push({ surface: 'pane_workflows', state: 'run detail, held gate question',
      ...(await shoot(cdp, A.outDir, '02-pane-run-detail.png', null, await stableColumnText(paneRegion))) });
    }
    } // end non-coverage (baseline/gate/graph) pane list + detail frames

    // -- gate modal (bd_2026-11-13-qri): ONE decision surface, real trusted
    // click, REAL pending (the answer POST is held at Fetch interception so
    // the 'Saving answer…' frame is painted truthfully, not staged), durable
    // saved receipt, and the toast's 'View exact gate' jump proven from a
    // different route. kill_runner_after_hold: the isolated runner dies at the
    // hold BEFORE the answer, so the events ledger must stay byte-identical
    // afterwards — "nothing restarted" verified for THIS tested runner only.
    if (surfacesWanted.has('gate_modal')) {
      const gateDef = (engSeed.graph.nodes || []).find(n => n.type === 'gate');
      if (!gateDef) die(EX.preflight, 'gate case seed graph carries no gate node');
      const runDir = path.join(B.runs, runId);
      const shaFile = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
      const eventsBefore = shaFile(path.join(runDir, 'events.jsonl'));
      if (engSeed.kill_runner_after_hold) {
        try {
          const pid = parseInt(fs.readFileSync(path.join(runDir, 'wf.pid'), 'utf8').trim(), 10);
          if (pid) process.kill(pid, 'SIGKILL');
        } catch { /* already gone: the tested shape is a dead runner */ }
      }
      // 07: the held frame — verbatim question, declared requester, options.
      await waitText(cdp, gateDef.question, 20_000);
      const heldCell = await rectOf(cdp, gateDef.question);
      if (!heldCell) die(EX.capture, 'held gate cell never rendered on the record page');
      shots.push({ surface: 'gate_modal', state: 'held: question, requester, option buttons',
        ...(await shoot(cdp, A.outDir, '07-gate-held.png', heldCell)) });
      // Hold the answer POST mid-flight, then trusted-click the option. The
      // FIRST click is force-failed with a real {ok:false} door response
      // (Fetch.fulfillRequest, HTTP 200 like the door's semantic errors):
      // the error frame is the RENDERED failure, not a staged picture, and
      // it proves the options come back retryable. The SECOND click answers.
      await cdp.send('Fetch.enable', { patterns: [{ urlPattern: '*/gate', requestMethod: 'POST' }] });
      const pauseOnce = () => new Promise((resolve, reject) => {
        const t = setTimeout(() => reject(new Error('answer POST never paused')), 15_000);
        const on = e => {
          let m; try { m = JSON.parse(e.data); } catch { return; }
          if (m.method === 'Fetch.requestPaused') {
            clearTimeout(t); cdp.ws.removeEventListener('message', on); resolve(m.params.requestId);
          }
        };
        cdp.ws.addEventListener('message', on);
      });
      await trustedClick(cdp, gateDef.options[0], { exact: true });
      const requestId = await pauseOnce();
      await waitText(cdp, 'Saving answer…', 5_000);
      shots.push({ surface: 'gate_modal', state: 'pending: POST held at Fetch interception, options disabled (duplicate prevention)',
        ...(await shoot(cdp, A.outDir, '08-gate-pending.png', await rectOf(cdp, 'Saving answer…'))) });
      await cdp.send('Fetch.fulfillRequest', { requestId, responseCode: 200,
        responseHeaders: [{ name: 'content-type', value: 'application/json' }],
        body: Buffer.from(JSON.stringify({ ok: false, error: { message: 'ui2-proof forced error' } })).toString('base64') });
      await waitText(cdp, 'Gate answer failed', 10_000);
      const retryCell = await rectOf(cdp, 'Gate answer failed');
      const retryOpt = await rectOf(cdp, gateDef.options[0], { exact: true });
      if (!retryOpt) die(EX.capture, 'options not retryable after an ok:false answer — error state swallowed the gate');
      if (await cdp.evl(`!!document.querySelector('[data-gate-receipt]')`))
        die(EX.capture, 'ok:false rendered a saved receipt — error is not a successful mutation');
      shots.push({ surface: 'gate_modal', state: 'error: forced {ok:false} door answer -> inline failure + retryable options, no receipt',
        ...(await shoot(cdp, A.outDir, '08b-gate-error.png', retryCell || retryOpt)) });
      const paused2 = pauseOnce();
      await trustedClick(cdp, gateDef.options[0], { exact: true });
      await cdp.send('Fetch.continueRequest', { requestId: await paused2 });
      await cdp.send('Fetch.disable');
      // 09: the durable saved receipt (recorded answer, scoped copy).
      await waitText(cdp, 'Answer saved', 20_000);
      const receipt = await cdp.evl(`(() => {
        const el = document.querySelector('[data-gate-receipt]');
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
      })()`);
      if (!receipt) die(EX.capture, 'saved receipt surface [data-gate-receipt] absent after the answer');
      // Receipt time contract (review-2 Q1/Q2): the rendered receipt carries
      // the door-stamped Answered timestamp — who/WHAT/WHEN, not a bare word.
      const receiptText = await cdp.evl(`(() => {
        const el = document.querySelector('[data-gate-receipt]');
        return el ? (el.innerText || '') : '';
      })()`);
      if (!/Answered · \d{4}-\d{2}-\d{2}T/.test(receiptText))
        die(EX.capture, `saved receipt lacks the door-stamped Answered time: ${JSON.stringify(receiptText)}`);
      shots.push({ surface: 'gate_modal', state: 'saved: Answer saved receipt, exact answer, door-stamped Answered time, nothing-restarted scope note',
        ...(await shoot(cdp, A.outDir, '09-gate-saved.png', receipt)) });
      // 10: the toast — same ledger line, View exact gate action. The toast IS
      // the receipt (review-2 Q2): answer saved, exact answer, requester,
      // run / gate, server time — and the View exact gate closure.
      await waitText(cdp, 'View exact gate', 15_000);
      const toast = await rectOf(cdp, '◇ Answer saved ·', {});
      if (!toast) die(EX.capture, 'success toast does not carry the Answer saved + answer receipt line');
      shots.push({ surface: 'gate_modal', state: 'success toast: answer saved + exact answer + requester + run / gate + stamped time, action View exact gate',
        ...(await shoot(cdp, A.outDir, '10-gate-toast.png', toast)) });
      // Identity proof: leave the record entirely, then take the toast's (or
      // the receipt's) View exact gate — the route must return to THIS run's
      // gate cell showing the durable receipt, never a bare list.
      await trustedClick(cdp, 'SESSIONS', { exact: true });
      let view = toast && await cdp.evl(`(() => {
        const btns = [...document.querySelectorAll('button')].filter(b =>
          (b.innerText || '').trim() === 'View exact gate');
        const b = btns[btns.length - 1];
        if (!b) return null;
        const r = b.getBoundingClientRect();
        return r.width > 0 ? { x: r.x + r.width / 2, y: r.y + r.height / 2 } : null;
      })()`);
      if (view) {
        for (const t of ['mouseMoved', 'mousePressed', 'mouseReleased'])
          await cdp.send('Input.dispatchMouseEvent', { type: t, x: view.x, y: view.y,
            button: t === 'mouseMoved' ? undefined : 'left', clickCount: 1,
            buttons: t === 'mouseReleased' ? 0 : 1 });
      } else {
        await trustedClick(cdp, 'WORKFLOWS', { exact: true });
        await trustedClick(cdp, runName, { region: paneRegion });
        view = await cdp.evl(`(() => {
          const btns = [...document.querySelectorAll('button')].filter(b =>
            (b.innerText || '').trim() === 'View exact gate');
          const b = btns[0];
          if (!b) return null;
          const r = b.getBoundingClientRect();
          return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
        })()`);
        if (view) for (const t of ['mouseMoved', 'mousePressed', 'mouseReleased'])
          await cdp.send('Input.dispatchMouseEvent', { type: t, x: view.x, y: view.y,
            button: t === 'mouseMoved' ? undefined : 'left', clickCount: 1,
            buttons: t === 'mouseReleased' ? 0 : 1 });
      }
      if (!view) die(EX.capture, 'no View exact gate control remained to click');
      await waitText(cdp, gateDef.question, 20_000);
      const back = await cdp.evl(`!!document.querySelector('[data-gate-receipt]')`);
      if (!back) die(EX.capture, 'View exact gate did not land on the exact gate receipt');
      // Read back the recorded bytes: exact answer, _ui provenance, and the
      // untouched event ledger — the answer was RECORD-only on this path.
      const gatesRec = JSON.parse(fs.readFileSync(
        path.join(runDir, 'gates', `${gateDef.id}.json`), 'utf8'));
      const identityLine = {
        run_id: runId, gate_id: gateDef.id, answer: gatesRec.answer,
        _ui: gatesRec._ui === true,
        events_sha_before: eventsBefore, events_sha_after: shaFile(path.join(runDir, 'events.jsonl')),
        gate_node_committed: fs.existsSync(path.join(runDir, 'nodes', `${gateDef.id}.json`))
      };
      if (gatesRec.answer !== gateDef.options[0] || gatesRec._ui !== true)
        die(EX.capture, `answer read-back mismatch: ${JSON.stringify(identityLine)}`);
      if (identityLine.events_sha_before !== identityLine.events_sha_after)
        die(EX.capture, 'events ledger MOVED on the answer path — nothing-restarted claim false for this seed');
      if (identityLine.gate_node_committed)
        die(EX.capture, 'the killed runner consumed the answer — the seed is no longer isolated');
      identity.gate_answer = identityLine;
      shots.push({ surface: 'gate_modal', state: 'after View exact gate: exact receipt re-rendered from the read model',
        ...(await shoot(cdp, A.outDir, '11-gate-after-view.png', await rectOf(cdp, gateDef.question))) });
    }

    // 03/04 directive card: seed one real assistant turn, open its session,
    // find the plugin's card (its 'Open in Workflows' action is the stable
    // hook — plugin.js:554) in the message stream.
    const cardSeed = (c.seeds || []).find(s => s.kind === 'engine_seed' && s.method === 'oneshot_echo');
    if (cardSeed && surfacesWanted.has('directive_card')) {
      const ask = path.join(A.outDir, 'seed', 'ask.txt');
      // The graph case echoes ALL THREE run ids in one assistant turn — one
      // session, three cards, the same shared grammar on each mount.
      fs.writeFileSync(ask, graphIds
        ? `Echo these lines verbatim and nothing else:\n` +
          [graphIds.council, graphIds.thr, graphIds.mf1].map(i => `::workflow{id="${i}"}`).join('\n') + '\n'
        : `Echo this line verbatim and nothing else:\n::workflow{id="${runId}"}\n`);
      // --source desktop: the app's session list shows titled, desktop-sourced
      // sessions; a bare --oneshot stores source=oneshot WITHOUT a title and
      // the list filters it out (field-proven: state.db source columns).
      const chatArgs = ['--profile', BENCH_PROFILE, 'chat', '--query-file', ask, '--oneshot', '-Q', '--source', 'desktop'];
      if (cardSeed.model) chatArgs.push('-m', cardSeed.model);
      if (cardSeed.provider) chatArgs.push('--provider', cardSeed.provider);
      let cardSession = null;
      let cardSessionErr = '';
      {
        const r = spawnSync(hermesAbs, chatArgs, {
          encoding: 'utf8', timeout: 240_000, maxBuffer: 32 * 1024 * 1024, env: benchEnv });
        if (r.error || r.status !== 0) {
          die(EX.api, `directive card seed failed (hermes chat oneshot): ${String(r.stderr || r.error?.message).slice(0, 300)}`);
        }
        cardSession = r.stdout || '';
        cardSessionErr = r.stderr || '';
      }
      fs.writeFileSync(path.join(A.outDir, 'seed', 'oneshot-output.txt'), cardSession + '\n--- stderr ---\n' + cardSessionErr);
      const sidMatch = `${cardSessionErr}\n${cardSession}`.match(/session_id:\s*(\S+)/);
      identity.seeds.directive_card_echo = { kind: 'engine_seed', method: 'oneshot_echo',
        ask_sha256: sha256(ask), stdout_sha256: crypto.createHash('sha256').update(cardSession).digest('hex'),
        session_id: sidMatch ? sidMatch[1] : null,
        model: cardSeed.model || 'seat-default' };
      // The session list caches at page load — reload so the freshly seeded
      // one-shot (written straight to the bench store) is in the list.
      await cdp.send('Page.reload', { ignoreCache: true });
      cdp.ws.close();
      await sleep(2000);
      cdp = await connectCdp(A.cdpPort, A.rendererPort, 60_000);
      await waitPainted(cdp, A.paintBudgetMs);
      // Field-proven (set-1c): Page.reload can land the renderer's IPC
      // bootstrap mid gateway-ticket refresh ('Invalid gateway ticket
      // response' in renderer.log); the SESSIONS list stays empty through
      // that retry window, so the attach probe must be waited here — the
      // old hardcoded 20s row window lost it under crew load.
      await waitConnected(cdp, probeBudgetMs);
      await trustedClick(cdp, 'sessions', { exact: true, ci: true });
      // Row titles are summarized (never the raw ask); in a fresh bench home
      // the ONLY session is the seeded echo — click the topmost row-shaped
      // element in the sidebar column (title + relative-time pattern).
      let rowHit = null;
      let rowT0 = Date.now();
      let rowReloads = 0;
      while (!rowHit) {
        const modalUp2 = await evlPoll(`document.body.innerText.includes("couldn't start")`, false);
        if (modalUp2) { try { await trustedClick(cdp, 'Retry', { exact: true, ci: true }); } catch { /* between frames */ } }
        rowHit = await evlPoll(`(async () => {
          const cand = [...document.querySelectorAll('div,li,button,a')]
            .map(n => ({ n, t: (n.innerText || '').trim() }))
            .filter(({ n, t }) => {
              // session row shape = title line + relative-time line (field-proven:
              // a bare /now/ hit 'runs unkNOW' — the pane stats line). Require a
              // second line whose WHOLE trimmed text is a relative-time token.
              if (!t || t.length > 120) return false;
              const lines = t.split('\\n').map(s => s.trim()).filter(Boolean);
              if (lines.length < 2) return false;
              return /^(?:now|just now|\\d+\\s*(?:s|sec|secs?|m|min|mins?|h|hr|hrs?|hour|hours?|d|day|days?)\\s*ago)$/i.test(lines[lines.length - 1]);
            })
            .filter(({ n }) => { const r = n.getBoundingClientRect(); return r.width > 60 && r.height > 16 && r.x < 420 && r.y > 40; })
            .sort((a, b) => a.n.getBoundingClientRect().y - b.n.getBoundingClientRect().y);
          const leaf = cand.find(({ n }) => !cand.some(o => o.n !== n && n.contains(o.n))) ?? cand[0];
          if (!leaf) return null;
          const el = leaf.n;
          el.scrollIntoView({ block: 'center' });
          await new Promise(r => setTimeout(r, 350));
          const r = el.getBoundingClientRect();
          return { x: r.x + r.width / 2, y: r.y + r.height / 2, t: leaf.t.slice(0, 60) };
        })()`, null);
        if (rowHit) break;
        if (Date.now() - rowT0 > probeBudgetMs) {
          if (!rowReloads++) {
            // Field-proven (set-1c): the first reload can land the ticket-
            // refresh window and wedge the INITIAL list load — recover once,
            // fresh budget, and keep probing.
            await cdp.send('Page.reload', { ignoreCache: true });
            cdp.ws.close();
            await sleep(2000);
            cdp = await connectCdp(A.cdpPort, A.rendererPort, 60_000);
            await waitPainted(cdp, A.paintBudgetMs);
            await waitConnected(cdp, probeBudgetMs);
            await trustedClick(cdp, 'sessions', { exact: true, ci: true });
            rowT0 = Date.now();
          } else {
            break;
          }
          continue;
        }
        // Pane-loop discipline: re-click SESSIONS every poll to ride route
        // resets and reconnect churn (boot-modal Retry rides the loop head).
        try { await trustedClick(cdp, 'sessions', { exact: true, ci: true }); } catch { /* view already there */ }
        await sleep(750);
      }
      if (!rowHit) {
        try { await shoot(cdp, A.outDir, '00-diagnostic-sessions.png'); } catch { /* best effort */ }
        const sb = await cdp.evl(`document.body.innerText.slice(0, 900)`).catch(() => '');
        die(EX.api, `seeded one-shot session row not found in the SESSIONS list — diagnostic shot + body text in ${JSON.stringify(sb).slice(0, 900)}`);
      }
      identity.seeds.directive_card_echo.session_row_hit = rowHit;
      {
        // Click + assert, re-located on failure: a title-summary refresh can
        // re-measure the virtualized row between rect and button-down.
        let opened = false
        for (let attempt = 0; attempt < 3 && !opened; attempt++) {
          if (attempt > 0) rowHit = await evlPoll(`(async () => {
            const cand = [...document.querySelectorAll('div,li,button,a')]
              .map(n => ({ n, t: (n.innerText || '').trim() }))
              .filter(({ t }) => {
                if (!t || t.length > 120) return false;
                const lines = t.split('\\n').map(s => s.trim()).filter(Boolean);
                if (lines.length < 2) return false;
                return /^(?:now|just now|\\d+\\s*(?:s|sec|secs?|m|min|mins?|h|hr|hrs?|hour|hours?|d|day|days?)\\s*ago)$/i.test(lines[lines.length - 1]);
              })
              .filter(({ n }) => { const r = n.getBoundingClientRect(); return r.width > 60 && r.height > 16 && r.x < 420 && r.y > 40; })
              .sort((a, b) => a.n.getBoundingClientRect().y - b.n.getBoundingClientRect().y);
            const leaf = cand.find(({ n }) => !cand.some(o => o.n !== n && n.contains(o.n))) ?? cand[0];
            if (!leaf) return ${JSON.stringify(rowHit)};  // page JS cannot see the Node-side var
            const el = leaf.n; el.scrollIntoView({ block: 'center' });
            await new Promise(r => setTimeout(r, 350));
            const r = el.getBoundingClientRect();
            return { x: r.x + r.width / 2, y: r.y + r.height / 2, t: leaf.t.slice(0, 60) };
          })()`)
          for (const t of ['mouseMoved', 'mousePressed', 'mouseReleased'])
            await cdp.send('Input.dispatchMouseEvent', { type: t, x: rowHit.x, y: rowHit.y,
              button: t === 'mouseMoved' ? undefined : 'left', clickCount: 1, buttons: t === 'mouseReleased' ? 0 : 1 });
          await sleep(1200)
          opened = await evlPoll(`document.body.innerText.includes(${JSON.stringify(runId)})`, false)
        }
        if (!opened) die(EX.api, 'session row clicks never opened the seeded transcript (run id absent after 3 attempts)')
      }
      // Directive cards render COLLAPSED (the expanded card header carries
      // the Open-in-Workflows action — plugin.js:552-554, skill: expansion is
      // in-memory only). Click collapsed directive pills (up to 3 rounds),
      // then locate the wanted card. The graph case's ask echoes three
      // directives; the wanted card is the PINNED council one (its id is
      // first in the echo), so early rounds may open the other two first —
      // the loop only exits when the wanted card itself is up.
      const cardIdWant = graphIds ? graphIds.council : runId;
      let card = null;
      for (let expand = 0; expand < 3 && !card; expand++) {
        try {
          await trustedClick(cdp, 'workflow…');
        } catch { /* fall through to the button wait — a pre-expanded card also passes */ }
        let openBtnSeen = false;
        const bT0 = Date.now();
        while (!openBtnSeen && Date.now() - bT0 < 12_000) {
          openBtnSeen = await cdp.evl(`!!document.querySelector('button[title="Open in Workflows"],button[aria-label="Open in Workflows"]')`);
          if (!openBtnSeen) await sleep(500);
        }
        // Card = the innermost ancestor of the plugin's Open-in-Workflows button
        // that still holds exactly ONE such button (walk stops before the list).
        card = await cdp.evl(`(() => {
          const CARD_BTN = 'button[title="Open in Workflows"],button[aria-label="Open in Workflows"]';
          const btns = [...document.querySelectorAll(CARD_BTN)];
          for (const b of btns) {
            let n = b, last = null;
            for (let i = 0; i < 8 && n; i++) {
              if (n.querySelectorAll(CARD_BTN).length > 1) break;
              last = n; n = n.parentElement;
            }
            if (!last) continue;
            const host = last.closest('div') ?? last;
            const cardText = (host.innerText || '') + (host.parentElement?.innerText || '');
            if (!cardText.includes(${JSON.stringify(cardIdWant)}) && !cardText.includes(${JSON.stringify(runName)})) continue;
            host.scrollIntoView({ block: 'center' });
            const r = host.getBoundingClientRect();
            if (r.width > 40 && r.height > 20)
              return { x: r.x, y: r.y, width: r.width, height: r.height, text: host.innerText || '' };
          }
          return null;
        })()`, rowHit);
        if (!card) await sleep(700);
      }
      if (!card) die(EX.api, 'directive card not rendered for the seeded run (Open in Workflows hook absent)');
      // The card's own innerText is the reproducible content of BOTH card
      // shots (the crop proves pixels, the text layer proves content; the
      // surrounding chat prose is LLM output and deliberately NOT hashed).
      shots.push({ surface: 'directive_card',
        state: graphIds ? 'in-chat card for the pinned council run' : 'in-chat card for seeded held-gate run',
        ...(await shoot(cdp, A.outDir, '04-directive-card.png', card, card.text)) });
      shots.push({ surface: 'directive_card', state: 'full viewport with card',
        ...(await shoot(cdp, A.outDir, '03-directive-card-full.png', null, card.text)) });
      if (A.caseName === 'graph') {
        // 05-09: the SAME shared grammar on every expansion mount — pill →
        // MiniGraph → fan expansion → child projection, threshold ladder and
        // MF1 raw rows in-chat, then phone and sparse-2560 geometry.
        const graphClickXY = async (x, y) => {
          for (const t of ['mouseMoved', 'mousePressed', 'mouseReleased'])
            await cdp.send('Input.dispatchMouseEvent', { type: t, x, y,
              button: t === 'mouseMoved' ? undefined : 'left', clickCount: 1, buttons: t === 'mouseReleased' ? 0 : 1 });
          await sleep(1400);
        };
        const cardPillClick = async (node) => {
          const hit = await cdp.evl(`(() => { const el = document.querySelector('[data-node="${node}"]');
            if (!el) return null; el.scrollIntoView({ block: 'center' });
            const r = el.getBoundingClientRect(); return r.width > 0 ? { x: r.x + r.width / 2, y: r.y + r.height / 2 } : null })()`);
          if (!hit) die(EX.api, `graph card pill [data-node=${node}] never rendered`);
          await graphClickXY(hit.x, hit.y);
        };
        const stripTexts = () => cdp.evl(`(() => [...document.querySelectorAll('span,div')]
          .map(e => (e.innerText || '').trim())
          .filter(t => /terminal|results|cancelled|partial|failed|aggregate/i.test(t) && t.length < 200 && t.length > 0)
          .slice(0, 40))()`);
        const tickCount = () => cdp.evl(`(() => [...document.querySelectorAll('span')].filter(s => {
          const st = s.getAttribute('style') || ''; return st.includes('width: 3px') && st.includes('height: 3px') }).length)()`);

        // (a) council card fans -> CHILD PROJECTION on the MiniGraph mount.
        await cardPillClick('critics');
        const cardM = await measureGraphSvg(cdp, 14);
        const pills = cardM.projectedPills.filter(n => /^critics\\.\\d+$/.test(n));
        // The pinned law (unit-tested in test_edge_routing.mjs): this fixture
        // projects 10 identities / 14 dependencies / 28 echoes — two echoes
        // per route. Refuse the frame if the RENDERED graph disagrees.
        if (cardM.routeGroups !== 14 || cardM.echoCircles !== 28 || pills.length !== 6)
          die(EX.api, `council card projection diverged from the pinned law: groups=${cardM.routeGroups} echoes=${cardM.echoCircles} pills=${pills.length}`);
        identity.graph_measurement.card = { ...cardM, projectedPills: undefined, projected_pills: pills };
        shots.push({ surface: 'directive_card',
          state: `council card projection: 14 routes, 28 echoes, 6 child pills; ${cardM.crossings} strict crossings MEASURED at ${cardM.geometry.innerWidth}x${cardM.geometry.innerHeight}@${cardM.geometry.dpr}`,
          ...(await shoot(cdp, A.outDir, '05-card-council-projected.png')) });

        // (b) the engine-seeded threshold run: exact ENDED census on the
        //     strip — the DOM copy must equal the engine's own rows.
        await trustedClick(cdp, 'workflow…').catch(() => {});
        await cardPillClick('work');
        const thrRec = JSON.parse(fs.readFileSync(path.join(B.runs, runId, 'nodes', 'work.json'), 'utf8'));
        const rows = (thrRec.output || {}).all_results || [];
        const counts = { total: rows.length, done: 0, failed: 0, running: 0, skipped: 0, stopped: 0, pending: 0, terminal: 0, cancelled: 0, partial: 0 };
        for (const r of rows) {
          const s = (r.error_class === 'cancelled' || r.error_class === 'cancel') ? 'cancelled' : r.status;
          counts[s] = (counts[s] || 0) + 1;
          if (['done', 'failed', 'skipped', 'stopped', 'cancelled', 'partial'].includes(s)) counts.terminal++;
        }
        const expected = `${counts.terminal}/${counts.total} terminal${counts.cancelled ? ` \u00b7${counts.cancelled} cancelled` : ''}${counts.partial ? ` \u00b7${counts.partial} partial` : ''}${counts.running ? ` \u00b7${counts.running}\u25b6` : ''}${counts.failed ? `, ${counts.failed} failed` : ''}`;
        const thrTexts = await stripTexts();
        const thrSeen = thrTexts.some(t => t.includes(expected));
        identity.graph_measurement.threshold_strip = { engine_status: thrRec.status, rows: counts, expected_summary: expected,
                                                       summary_seen_in_dom: thrSeen, texts: thrTexts };
        if (!thrSeen) die(EX.api, `threshold strip never showed the engine's exact ended census (${JSON.stringify(expected)})`);
        shots.push({ surface: 'directive_card',
          state: `threshold ladder on engine records: exact ended census ${expected}, no fabricated intermediate`,
          ...(await shoot(cdp, A.outDir, '06-card-threshold-census.png')) });

        // (c) MF1 (clearly synthetic): raw child partial + cancelled survive
        //     under a done parent — no parent-metric borrowing, cancelled
        //     separated from failed, attempt ticks replace ghost rings.
        await trustedClick(cdp, 'workflow…').catch(() => {});
        await cardPillClick('fan');
        const mf1Ticks = await tickCount();
        const mf1Texts = await stripTexts();
        if (!mf1Texts.some(t => t.includes('3/3 terminal') && t.includes('cancelled') && t.includes('partial')))
          die(EX.api, `MF1 strip census wrong (expected 3/3 terminal + cancelled + partial buckets): ${JSON.stringify(mf1Texts).slice(0, 300)}`);
        await graphClickXY(...await (async () => {
          const hit = await cdp.evl(`(() => { const el = [...document.querySelectorAll('button,div')]
            .filter(n => (n.innerText || '').trim() === 'b');
            if (!el.length) return null; el[0].scrollIntoView({ block: 'center' });
            const r = el[0].getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 } })()`);
          if (!hit) die(EX.api, 'MF1 item chip "b" (raw partial row) never rendered');
          return [hit.x, hit.y];
        })());
        const detailText = await cdp.evl(`document.body.innerText`);
        if (!detailText.includes('partial') || !detailText.includes('cap_exhausted'))
          die(EX.api, 'MF1 item detail lost the child RAW status/error_class (partial/cap_exhausted absent)');
        if (!detailText.includes('fanout aggregate'))
          die(EX.api, 'MF1 parent aggregate label absent — projection law requires the parent keeps the fanout aggregate');
        identity.graph_measurement.mf1 = { tick_spans: mf1Ticks, strip_texts: mf1Texts, detail_has_raw: true };
        shots.push({ surface: 'directive_card',
          state: 'MF1 (synthetic): child raw partial + cancelled under done parent; footer attempt ticks, ghost rings retired',
          ...(await shoot(cdp, A.outDir, '07-card-mf1-partial-item.png')) });

        // (d) phone viewport (device metrics override on the REAL renderer).
        await cdp.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
        await sleep(1600);
        {
          const seen = await cdp.evl(`(() => { const el = document.querySelector('[data-node="critics"]'); if (el) el.scrollIntoView({ block: 'center' }); return !!el })()`);
          if (!seen) die(EX.api, 'council MiniGraph pill absent at phone metrics');
        }
        shots.push({ surface: 'directive_card', state: 'council card at phone metrics 390x844@2 (real renderer, device override)',
          ...(await shoot(cdp, A.outDir, '08-phone-council-card.png')) });
        await cdp.send('Emulation.clearDeviceMetricsOverride', {});
        await sleep(800);

        // (e) sparse 2560 window: bounds first, honest fallback to metrics.
        {
          let method = 'window-bounds';
          try {
            const { windowId } = await cdp.send('Browser.getWindowForTarget', {});
            await cdp.send('Browser.setWindowBounds', { windowId, bounds: { width: 2560, height: 1440 } });
            await sleep(1800);
            const iw = await cdp.evl('innerWidth');
            if (!(iw >= 2500)) {
              await cdp.send('Emulation.setDeviceMetricsOverride', { width: 2560, height: 1440, deviceScaleFactor: 1, mobile: false });
              await sleep(1600);
              method = 'device-metrics-override (window bounds clamped)';
            }
          } catch {
            await cdp.send('Emulation.setDeviceMetricsOverride', { width: 2560, height: 1440, deviceScaleFactor: 1, mobile: false });
            await sleep(1600);
            method = 'device-metrics-override (setWindowBounds refused)';
          }
          const geo = await cdp.evl(`({ innerWidth, innerHeight })`);
          const wide = await measureGraphSvg(cdp, 14).catch(() => null);
          identity.graph_measurement.sparse_2560 = { method, geometry: geo, page: wide };
          shots.push({ surface: 'directive_card',
            state: `sparse 2560x1440 (${method}): ${wide ? `${wide.crossings} strict crossings measured at this geometry` : 'graph off-screen'}`,
            ...(await shoot(cdp, A.outDir, '09-2560-council-card.png')) });
        }
      }
    }

    // 05 tray: settings-gated slim row in the composer underside
    // (plugin.js:1027/1111 — 'N running workflows'). OWNERSHIP LAW
    // (ownedRuns, plugin.js:728-737 + SessionStrip 1288/1326): the strip
    // renders ONLY the focused chat's owned runs — owner.session_id must
    // equal the focused session. A blank-owner run is pane-only (honest
    // absence), so the tray seed relaunches the SAME held-gate graph through
    // the door with WF_OWNER_SESSION=<the seeded one-shot's session id> —
    // the door's on-behalf stamp (__init__.py _owner_stamp), not a fixture
    // edit. Gate + runs-list refresh poll: the pane fetch is periodic.
    if (surfacesWanted.has('tray_row')) {
      const traySid = identity.seeds.directive_card_echo?.session_id;
      if (!traySid) die(EX.preflight, 'tray seed needs the one-shot session id (parse failed — see seed/oneshot-output.txt)');
      let trayRunId;
      try {
        trayRunId = execFileSync(py, [path.join(HERE, 'seed_run.py'),
          '--repo', REPO, '--runs-root', B.runs, '--graph-file', graphFile],
          { encoding: 'utf8', timeout: 60_000,
            env: { ...process.env, WF_RUNS_ROOT: B.runs, WF_OWNER_SESSION: traySid,
                   HERMES_WF_HERMES_BIN: hermesAbs, HERMES_HOME: B.home, HERMES_GATEWAY_LOCK_DIR: B.locks } }).trim();
      } catch (e) {
        die(EX.api, `tray engine seed launch failed: ${String(e.stderr || e.message).slice(0, 400)}`);
      }
      seededRuns.push(trayRunId);
      identity.seeds.tray_run = { kind: 'engine_seed', run_id: trayRunId, owner_stamped: traySid,
        graph_sha256: sha256(graphFile) };
      let tray = null;
      const tT0 = Date.now();
      while (!tray && Date.now() - tT0 < 45_000) {
        tray = await cdp.evl(`(() => {
          const els = [...document.querySelectorAll('div,span,button')].filter(n =>
            /\\d+ running workflows/.test((n.innerText || '').trim()) && n.getBoundingClientRect().height > 0);
          const leaf = els.find(h => !els.some(o => o !== h && h.contains(o))) ?? els[0];
          if (!leaf) return null;
          leaf.scrollIntoView({ block: 'center' });
          const r = leaf.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height };
        })()`);
        if (!tray) await sleep(1500);
      }
      if (!tray) {
        const tail = await cdp.evl(`(() => { const t = document.body.innerText; const i = t.toLowerCase().indexOf('running'); return i < 0 ? t.slice(-400) : t.slice(Math.max(0, i - 80), i + 80); })()`);
        try { await shoot(cdp, A.outDir, '00-diagnostic-tray.png'); } catch { /* best effort */ }
        die(EX.api, `tray row absent after 45s: settings.tray set, owner-stamped run ${trayRunId} live, session ${traySid} focused — check $trayGate (plugin.js:709) and owner stamp; text near 'running': ${JSON.stringify(String(tail).slice(0, 240))}`);
      }
      shots.push({ surface: 'tray_row', state: 'slim live-run tray row, owner-stamped live run', ...(await shoot(cdp, A.outDir, '05-tray-row.png', tray)) });
      shots.push({ surface: 'tray_row', state: 'full viewport with tray', ...(await shoot(cdp, A.outDir, '06-tray-full.png')) });
    }

    identity.renderer_probe = await cdp.evl(`(() => {
      const s = [...document.querySelectorAll('script')].map(x => x.src);
      return { script_srcs: s.filter(Boolean).length }
    })()`) || null;
    cdp.ws.close();

    const report = { ok: true, case: A.caseName, identity, shots,
      review_note: 'reviewed:false means THIS tool run only proved PNG magic+size; visual review (vision_analyze per hermes-workflows-ui-qa) is mandatory before any layout claim' };
    // Provenance serialization law: the capture machine's home path is
    // machine-local noise — write it as ~ so committed evidence never carries
    // an operator's absolute home (publish-scrub audits the evidence tree).
    const redactHome = obj => JSON.stringify(obj, null, 2).split(os.homedir()).join('~');
    fs.writeFileSync(path.join(A.outDir, 'report.json'), redactHome(report) + '\n');
    fs.writeFileSync(path.join(A.outDir, 'identity.json'), redactHome(identity) + '\n');

    // -- immutable capture manifest (written LAST; slice A reproducibility
    //    contract). Per-file sha256 pins THIS run's bytes (immutability);
    //    the repro section pins only the volatile-masked content layer, so
    //    two independent runs at one candidate hash-diff empty there.
    const reproMap = {};
    for (const s of shots) if (s.content_sha256) reproMap[s.file] = s.content_sha256;
    const repro = {
      content_sha256_by_file: reproMap,
      combined_sha256: crypto.createHash('sha256')
        .update(canonicalJson(reproMap)).digest('hex'),
    };
    const manifestOut = {
      schema: 'proof-harness/1',
      run_ts: identity.ts,
      case: A.caseName,
      only: A.only || null,
      surfaces: [...new Set(shots.map(s => s.surface))].sort(),
      candidate: { plugin: 'desktop/plugin.js', plugin_sha256: pluginSha,
                   repo_head: identity.candidate_head,
                   merge_base_origin_main: identity.merge_base_origin_main },
      app: identity.app,
      seeds: identity.seeds,
      captures: shots.map(s => ({ surface: s.surface, state: s.state, file: s.file,
        bytes: s.bytes, sha256: s.sha256, clip: s.clip,
        content_file: s.content_file ?? null, content_sha256: s.content_sha256 ?? null,
        reviewed: false })),
      repro,
      review_note: report.review_note,
    };
    writeImmutable(path.join(A.outDir, 'manifest.json'), redactHome(manifestOut) + '\n');
    console.log(JSON.stringify({ ok: true, out: A.outDir, run_id: runId,
      plugin_sha256: pluginSha, captures: shots.map(s => s.file),
      repro_combined_sha256: repro.combined_sha256 }));
    return 0;
  } finally {
    // Stop engine-seeded runs FIRST (parked held-gate runners outlive
    // electron otherwise): the same door, action:stop, isolated runs root.
    for (const rid of seededRuns) {
      try {
        execFileSync(py, [path.join(HERE, 'seed_run.py'), '--repo', REPO,
          '--runs-root', B.runs, '--stop', rid],
          { encoding: 'utf8', timeout: 30_000,
            env: { ...process.env, WF_RUNS_ROOT: B.runs, HERMES_HOME: B.home } });
      } catch (e) { revertFailures.push(`stop ${rid}: ${String(e.stderr || e.message).slice(0, 200)}`); }
    }
    // Bench fork down: profile-scoped `gateway stop`, then the pid the state
    // file names (only when that state file lives IN THIS BENCH and names
    // this bench's profile home — never a borrowed pid). The fork is spawned
    // detached by the ensure CLI and outlives electron's process group, so
    // this is its only teardown; a survivor here is a teardown failure.
    try {
      execFileSync(hermesBin, ['--profile', BENCH_PROFILE, 'gateway', 'stop'],
        { encoding: 'utf8', timeout: 30_000, env: benchEnv });
    } catch (e) { revertFailures.push(`gateway stop: ${String(e.stderr || e.message).slice(0, 200)}`); }
    try {
      const st = JSON.parse(fs.readFileSync(path.join(B.profile, 'gateway_state.json'), 'utf8'));
      if (st.pid && st.kind === 'hermes-gateway' && st.hermes_home
          && path.resolve(st.hermes_home) === path.resolve(B.profile)) {
        try { process.kill(st.pid, 'SIGKILL'); } catch { /* raced away */ }
      }
    } catch { /* no fork ever registered */ }
    // Revert the trusted inputs (config hygiene — now profile-local, still
    // reverted for honesty), then kill ONLY this supervisor's process groups
    // + the path-scoped survivor sweep.
    for (const key of touched.reverse()) {
      try {
        const before = identity.config_touched[key]?.before;
        if (before === null || before === undefined) retryCli(() => unsetConfig(hermesBin, key, benchEnv, BENCH_PROFILE), { attempts: 3 });
        else if (['string', 'number', 'boolean'].includes(typeof before)) retryCli(() => writeConfig(hermesBin, [key, String(before)], benchEnv, BENCH_PROFILE), { attempts: 3 });
        else revertFailures.push(`${key}: prior value ${JSON.stringify(before)} is non-scalar — restore by hand`);
      } catch (e) { revertFailures.push(`${key}: ${String(e.message).slice(0, 200)}`); }
    }
    if (A.keep) fs.writeFileSync(path.join(A.outDir, 'logs', 'KEEP.txt'),
      JSON.stringify(sup.children) + '\n');
    else await sup.teardown();
    identity.teardown = { survivors: sup.survivors || [], revert_failures: revertFailures };
    fs.writeFileSync(path.join(A.outDir, 'identity.json'),
      JSON.stringify(identity, null, 2).split(os.homedir()).join('~') + '\n');
  }
}

// CLI guard: importing this module (the repro spec imports maskVolatile +
// the parse helpers) must never boot the bench.
const isCli = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isCli) main().then(code => process.exit(code ?? 0)).catch(async e => {
  const code = e instanceof Bail ? e.code : 1;
  console.error(`UI2_PROOF_FAIL(${code}): ${e.message}`);
  if (e.stack && code === 1) console.error(e.stack.split('\n').slice(0, 4).join('\n'));
  process.exit(code);
});
