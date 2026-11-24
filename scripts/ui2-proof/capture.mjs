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
//   node scripts/ui2-proof/capture.mjs --case CASE --out DIR
// Cases and their seeds live in ./cases.json; every seed declares
// kind: engine_seed | historical_snapshot. A known case whose surfaces are
// not yet wired fails exit 3 as an explicitly NEW test — never an invented
// existing command.
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
// --no-prebuild, --plan.
import { execFileSync, spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const MANIFEST = path.join(HERE, 'cases.json');

const USAGE = `usage: node scripts/ui2-proof/capture.mjs --case CASE --out DIR
       [--app-repo PATH] [--plugin PATH] [--cdp-port N] [--renderer-port N]
       [--hermes-bin PATH] [--plan] [--keep] [--no-prebuild]
cases: see scripts/ui2-proof/cases.json (setup: scripts/ui2-proof/SETUP.md)`;

function parseArgs(argv) {
  const a = { cdpPort: 9394, rendererPort: 5194, prebuild: true, plan: false, keep: false };
  for (let i = 0; i < argv.length; i++) {
    const take = () => {
      const v = argv[++i];
      if (v === undefined) die(EX.usage, `flag needs a value: ${argv[i - 1]}\n${USAGE}`);
      return v;
    };
    switch (argv[i]) {
      case '--case': a.caseName = take(); break;
      case '--out': a.outDir = path.resolve(take()); break;
      case '--app-repo': a.appRepo = path.resolve(take()); break;
      case '--plugin': a.plugin = path.resolve(take()); break;
      case '--cdp-port': a.cdpPort = Number(take()); break;
      case '--renderer-port': a.rendererPort = Number(take()); break;
      case '--hermes-bin': a.hermesBin = take(); break;
      case '--plan': a.plan = true; break;
      case '--keep': a.keep = true; break;
      case '--no-prebuild': a.prebuild = false; break;
      case '--help': case '-h': console.log(USAGE); process.exit(0); break;
      default: die(EX.usage, `unknown argument: ${argv[i]}\n${USAGE}`);
    }
  }
  if (!a.caseName) die(EX.usage, `--case is required\n${USAGE}`);
  if (!a.outDir) die(EX.usage, `--out is required\n${USAGE}`);
  return a;
}

const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const sleep = ms => new Promise(r => setTimeout(r, ms));

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
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (method, params = {}) => new Promise(res => {
    const i = ++id;
    pend.set(i, m => { if (m.error) throw new Error(`${method}: ${JSON.stringify(m.error).slice(0, 300)}`); res(m.result); });
    ws.send(JSON.stringify({ id: i, method, params }));
  });
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

// Trusted input (real pipeline, per skill): moved -> pressed -> released at
// the element's rect center. Locator JS finds the DEEPEST visible element
// whose trimmed text contains `needle` (or the first, when `nth` given).
async function trustedClick(cdp, needle, { exact = false, nth = null } = {}) {
  const pt = await cdp.evl(`(async () => {
    const needle = ${JSON.stringify(needle)}, exact = ${exact};
    const nodes = [...document.querySelectorAll('div,button,a,span,li,td')];
    const hits = nodes.filter(n => {
      const t = (n.innerText || n.textContent || '').trim();
      if (t.length > 400 && !exact) return false;
      if (exact ? t === needle : t.includes(needle)) {
        const r = n.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
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
    return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height,
             rect: { x: r.x, y: r.y, width: r.width, height: r.height },
             text: (el.innerText || el.textContent || '').slice(0, 80) };
  })()`);
  if (pt.err) die(EX.capture, `click target not found on rendered page: ${JSON.stringify(needle)}`);
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: pt.x, y: pt.y });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: pt.x, y: pt.y, button: 'left', clickCount: 1, buttons: 1 });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: pt.x, y: pt.y, button: 'left', clickCount: 1, buttons: 0 });
  return pt;
}

async function waitText(cdp, needle, ms = 30_000) {
  const t0 = Date.now();
  for (;;) {
    const seen = await cdp.evl(`document.body.innerText.includes(${JSON.stringify(needle)})`);
    if (seen) return Date.now() - t0;
    if (Date.now() - t0 > ms) die(EX.api, `never rendered on the real app: ${JSON.stringify(needle)} (within ${ms}ms)`);
    await sleep(400);
  }
}

async function shoot(cdp, outDir, name, clipRect = null) {
  const params = { format: 'png' };
  if (clipRect) {
    params.clip = { x: Math.max(0, clipRect.x), y: Math.max(0, clipRect.y),
                    width: Math.max(1, clipRect.width), height: Math.max(1, clipRect.height), scale: 1 };
  }
  const r = await cdp.send('Page.captureScreenshot', params);
  const buf = Buffer.from(r.data, 'base64');
  const file = path.join(outDir, 'captures', name);
  fs.writeFileSync(file, buf);
  const ok = buf.length > 4096 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  if (!ok) die(EX.capture, `empty/suspicious PNG (need >4096B + magic): ${name} (${buf.length}B)`);
  return { file: path.relative(outDir, file), bytes: buf.length, sha256: sha256(file),
           clip: clipRect ? 'element' : 'viewport', reviewed: false };
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

function readConfigValue(hermesBin, key) {
  // `hermes config get` exits 0 printing the value; a missing key prints a
  // "not set" notice. Presence probe stays honest via --json parse, else null.
  try {
    const out = execFileSync(hermesBin, ['config', 'get', key, '--json'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return JSON.parse(out);
  } catch { return null; }
}

function writeConfig(hermesBin, kv) {
  execFileSync(hermesBin, ['config', 'set', '--force', ...kv], { encoding: 'utf8' });
}
function unsetConfig(hermesBin, key) {
  try { execFileSync(hermesBin, ['config', 'unset', key], { encoding: 'utf8' }); } catch { /* best-effort revert */ }
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
  const unwired = (c.surfaces || []).filter(s => !manifest.surfaces_registry.includes(s))
        .concat(c.implemented === false ? c.surfaces : []);
  if (unwired.length && c.implemented === false) {
    console.error(`EXIT 3: case ${A.caseName} is a documented NEW TEST (not yet wired): surfaces ${unwired.join(',')}`);
    process.exit(EX.notImplemented);
  }
  if (unwired.length) {
    die(EX.notImplemented, `case ${A.caseName} names surfaces outside the driver's registry (${unwired.join(', ')}): they are NEW TESTS, add them to capture.mjs + surfaces_registry`);
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

  const plan = { case: A.caseName, surfaces: c.surfaces,
    seeds: (c.seeds || []).map(s => ({ name: s.name, kind: s.kind, method: s.method })),
    historical_snapshots: (c.historical_snapshots || []).map(s => s.name),
    plugin_sha256: pluginSha, ports: identity.bench.ports, out: A.outDir };
  if (A.plan) { console.log(JSON.stringify({ ok: true, mode: 'plan', plan }, null, 2)); return 0; }

  if (!fs.existsSync(desktop)) die(EX.preflight, `no apps/desktop in app repo ${appRepo} (read SETUP.md; --app-repo or UI2_PROOF_APP_REPO)`);
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
  const B = { root: A.outDir, home: path.join(A.outDir, 'bench', 'home'),
              userdata: path.join(A.outDir, 'bench', 'userdata'),
              runs: path.join(A.outDir, 'bench', 'runs'),
              plugins: path.join(A.outDir, 'bench', 'home', 'desktop-plugins', 'hermes-workflows') };
  for (const d of [B.home, B.userdata, B.runs, B.plugins,
                   path.join(A.outDir, 'captures'), path.join(A.outDir, 'logs'), path.join(A.outDir, 'seed')])
    fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(A.outDir, '.ui2-proof-owned'), `${identity.ts} capture.mjs --case ${A.caseName}\n`);

  // Stage the CANDIDATE into the bench home's desktop-plugins root — the app
  // loads exactly these bytes. Staged copy is re-hashed and must equal the
  // candidate before any capture is trusted.
  fs.copyFileSync(pluginSrc, path.join(B.plugins, 'plugin.js'));
  const stagedSha = sha256(path.join(B.plugins, 'plugin.js'));
  identity.plugin.staged = path.join(B.plugins, 'plugin.js');
  identity.plugin.staged_sha256 = stagedSha;
  if (stagedSha !== pluginSha) die(EX.preflight, 'staged plugin bytes diverged from candidate');
  // Copy discovery/state the app READS (never the real plugins dir — the
  // desktop-half migration would resurrect the installed half over the
  // candidate; never workflows — the test runs root owns that name).
  for (const f of ['spawn-ledger.json', 'gateway_state.json', 'auth.json', 'config.yaml']) {
    const src = path.join(realHome, f);
    if (fs.existsSync(src)) fs.copyFileSync(src, path.join(B.home, f));
  }
  identity.bench.discovery_copied = ['spawn-ledger.json', 'gateway_state.json', 'auth.json', 'config.yaml']
    .filter(f => fs.existsSync(path.join(B.home, f)));

  const sup = new Supervisor(A.outDir);
  sup._ownedUserData = B.userdata;
  sup._viteMarker = `--port ${A.rendererPort} --strictPort`;
  const touched = [];
  const revertFailures = [];

  try {
    // Trusted inputs written to the SHARED gateway config (skill-proven
    // recipe): runs_root isolates what the pane lists; tray arms the gated
    // tray row. Both are read fresh by the serving gateway per request; the
    // window is minutes, and teardown reverts (records prior absence).
    for (const [key, value] of [['plugins.entries.hermes-workflows.settings.runs_root', B.runs],
                                ['plugins.entries.hermes-workflows.settings.tray', true]]) {
      const before = readConfigValue(hermesBin, key);
      identity.config_touched[key] = { before, after: value };
      touched.push(key);
      writeConfig(hermesBin, [key, String(value)]);
    }

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
      HERMES_HOME: B.home };
    if (!fs.existsSync(path.join(B.home, 'spawn-ledger.json')) &&
        !fs.existsSync(path.join(B.home, 'gateway_state.json')))
      die(EX.boot, `bench home has no gateway discovery input (copied neither spawn-ledger.json nor gateway_state.json from ${realHome}) — the pane API cannot attach`);
    sup.start('electron', path.join(desktop, 'node_modules', '.bin', 'electron'),
      ['.', `--user-data-dir=${B.userdata}`], { cwd: desktop, env: electronEnv });

    // -- engine seed: launch the held-gate graph through the door -----------
    const engSeed = (c.seeds || []).find(s => s.kind === 'engine_seed' && s.method === 'door_run');
    if (!engSeed) die(EX.preflight, `case ${A.caseName} has no door_run engine seed`);
    const graphFile = path.join(A.outDir, 'seed', 'held-gate.graph.json');
    fs.writeFileSync(graphFile, JSON.stringify(engSeed.graph, null, 2) + '\n');
    let runId;
    let hermesAbs = hermesBin;
    if (!hermesAbs.startsWith('/')) {
      try { hermesAbs = execFileSync('/usr/bin/which', [hermesAbs], { encoding: 'utf8' }).trim() || hermesAbs; } catch { /* PATH lookup stays the door's problem */ }
    }
    try {
      runId = execFileSync('python3', [path.join(HERE, 'seed_run.py'),
        '--repo', REPO, '--runs-root', B.runs, '--graph-file', graphFile],
        { encoding: 'utf8', timeout: 60_000,
          env: { ...process.env, WF_RUNS_ROOT: B.runs, HERMES_WF_HERMES_BIN: hermesAbs } }).trim();
    } catch (e) {
      die(EX.api, `engine seed launch failed (seed_run.py): ${String(e.stderr || e.message).slice(0, 400)}`);
    }
    identity.seeds.held_gate_run = { kind: 'engine_seed', run_id: runId, graph_sha256: sha256(graphFile) };

    // -- CDP attach; enable decision; reload (skill gotcha wall) ------------
    let cdp = await connectCdp(A.cdpPort, A.rendererPort);
    await cdp.evl(`localStorage.setItem('hermes.desktop.pluginDecisions.v2', JSON.stringify({'hermes-workflows': true}))`);
    await cdp.send('Page.reload', { ignoreCache: true });
    cdp.ws.close();
    await sleep(1500);
    cdp = await connectCdp(A.cdpPort, A.rendererPort, 60_000);

    // Checked API attachment (1): the dev-served registry shows the plugin's
    // surfaces registered on the REAL renderer (skill probe).
    const registry = await cdp.evl(`(async () => {
      const mod = await import('/src/contrib/registry.ts');
      const reg = mod.registry;
      const names = area => { try { return (reg.getArea(area) || []).map(e => e.id ?? e.name ?? String(e)) } catch { return [] } };
      return { routes: names('routes'), panes: names('panes'),
               directives: names('transcript.directives'), composer: names('composer.underside') };
    })()`);
    identity.registry = registry;
    const surfacesWanted = new Set(c.surfaces);
    const attached = surfacesWanted.has('pane_workflows') ? registry.panes.some(x => String(x).includes('workflow'))
      : registry.panes.length > 0;
    if (!attached) die(EX.api, `plugin API attachment unproven: registry panes=${JSON.stringify(registry.panes)} (bundle loaded but nothing registered — enable/reload/marker issue)`);
    if (surfacesWanted.has('directive_card') && !registry.directives.some(x => String(x).includes('workflow')))
      die(EX.api, `directive not registered on the real renderer: transcript.directives=${JSON.stringify(registry.directives)}`);

    // Checked API attachment (2): the seeded run row can ONLY come from
    // GET /api/plugins/hermes-workflows/ — proven by its rendering.
    await trustedClick(cdp, 'WORKFLOWS', { exact: true });
    await waitText(cdp, runId, 30_000);
    identity.api_attachment = { via: 'registry + live seeded run row rendered through the plugin API route', run_id: runId };
    const shots = [];

    // 01/02 pane: runs list, then the held-gate run detail
    shots.push({ surface: 'pane_workflows', state: 'runs list, seeded held-gate run', ...(await shoot(cdp, A.outDir, '01-pane-runs.png')) });
    await trustedClick(cdp, runId);
    await waitText(cdp, engSeed.graph.nodes[1].question, 20_000);
    shots.push({ surface: 'pane_workflows', state: 'run detail, held gate question', ...(await shoot(cdp, A.outDir, '02-pane-run-detail.png')) });

    // 03/04 directive card: seed one real assistant turn, open its session,
    // find the plugin's card (its 'Open in Workflows' action is the stable
    // hook — plugin.js:554) in the message stream.
    const cardSeed = (c.seeds || []).find(s => s.kind === 'engine_seed' && s.method === 'oneshot_echo');
    if (cardSeed && surfacesWanted.has('directive_card')) {
      const ask = path.join(A.outDir, 'seed', 'ask.txt');
      fs.writeFileSync(ask, `Echo this line verbatim and nothing else:\n::workflow{id="${runId}"}\n`);
      const chatArgs = ['chat', '--query-file', ask, '--oneshot', '-Q'];
      if (cardSeed.model) chatArgs.push('-m', cardSeed.model);
      if (cardSeed.provider) chatArgs.push('--provider', cardSeed.provider);
      let cardSession = null;
      try {
        cardSession = execFileSync(hermesBin, chatArgs, { encoding: 'utf8', timeout: 240_000, maxBuffer: 32 * 1024 * 1024 });
      } catch (e) {
        die(EX.api, `directive card seed failed (hermes chat oneshot): ${String(e.message).slice(0, 300)}`);
      }
      fs.writeFileSync(path.join(A.outDir, 'seed', 'oneshot-output.txt'), cardSession);
      identity.seeds.directive_card_echo = { kind: 'engine_seed', method: 'oneshot_echo',
        ask_sha256: sha256(ask), stdout_sha256: crypto.createHash('sha256').update(cardSession).digest('hex'),
        model: cardSeed.model || 'seat-default' };
      await trustedClick(cdp, 'SESSIONS', { exact: true });
      // Row titles derive from the first user message; the ask text embeds the
      // directive, so match any of: ask text, raw directive, bare run id.
      const rowHit = await cdp.evl(`(() => {
        const nodes = [...document.querySelectorAll('div,li,button,a')].filter(n => {
          const t = (n.innerText || '').trim();
          if (!t || t.length > 300) return false;
          return t.includes('Echo this line') || t.includes(${JSON.stringify(runId)}) || t.includes('::workflow{id=');
        });
        const leaf = nodes.find(h => !nodes.some(o => o !== h && h.contains(o))) ?? nodes[0];
        if (!leaf) return null;
        leaf.scrollIntoView({ block: 'center' });
        const r = leaf.getBoundingClientRect();
        return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
      })()`);
      if (!rowHit) die(EX.api, 'seeded one-shot session row not found in the SESSIONS list');
      for (const t of ['mouseMoved', 'mousePressed', 'mouseReleased'])
        await cdp.send('Input.dispatchMouseEvent', { type: t, x: rowHit.x, y: rowHit.y,
          button: t === 'mouseMoved' ? undefined : 'left', clickCount: 1, buttons: t === 'mouseReleased' ? 0 : 1 });
      await waitText(cdp, runId, 30_000);           // inert user-role directive text carries the id
      // Card = the innermost ancestor of the plugin's Open-in-Workflows button
      // that still holds exactly ONE such button (walk stops before the list).
      const card = await cdp.evl(`(() => {
        const btns = [...document.querySelectorAll('button[aria-label="Open in Workflows"]')];
        for (const b of btns) {
          let n = b, last = null;
          for (let i = 0; i < 8 && n; i++) {
            if (n.querySelectorAll('button[aria-label="Open in Workflows"]').length > 1) break;
            last = n; n = n.parentElement;
          }
          if (!last) continue;
          const host = last.closest('div') ?? last;
          if (!(host.innerText || '').includes(${JSON.stringify(runId)}) &&
              !(host.parentElement?.innerText || '').includes(${JSON.stringify(runId)})) continue;
          host.scrollIntoView({ block: 'center' });
          const r = host.getBoundingClientRect();
          if (r.width > 40 && r.height > 20)
            return { x: r.x, y: r.y, width: r.width, height: r.height };
        }
        return null;
      })()`);
      if (!card) die(EX.api, 'directive card not rendered for the seeded run (Open in Workflows hook absent)');
      shots.push({ surface: 'directive_card', state: 'in-chat card for seeded held-gate run', ...(await shoot(cdp, A.outDir, '04-directive-card.png', card)) });
      shots.push({ surface: 'directive_card', state: 'full viewport with card', ...(await shoot(cdp, A.outDir, '03-directive-card-full.png')) });
    }

    // 05 tray: settings-gated slim row in the composer underside
    // (plugin.js:1027/1111 — 'N running workflows').
    if (surfacesWanted.has('tray_row')) {
      const tray = await cdp.evl(`(() => {
        const els = [...document.querySelectorAll('div,span,button')].filter(n =>
          /\\d+ running workflows/.test((n.innerText || '').trim()) && n.getBoundingClientRect().height > 0);
        const leaf = els.find(h => !els.some(o => o !== h && h.contains(o))) ?? els[0];
        if (!leaf) return null;
        leaf.scrollIntoView({ block: 'center' });
        const r = leaf.getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
      })()`);
      if (!tray) die(EX.api, 'tray row absent: settings.tray was set and the seeded run is live — check $trayGate (plugin.js:709) and reload');
      shots.push({ surface: 'tray_row', state: 'slim live-run tray row, seeded live run', ...(await shoot(cdp, A.outDir, '05-tray-row.png', tray)) });
      shots.push({ surface: 'tray_row', state: 'full viewport with tray', ...(await shoot(cdp, A.outDir, '06-tray-full.png')) });
    }

    identity.renderer_probe = await cdp.evl(`(() => {
      const s = [...document.querySelectorAll('script')].map(x => x.src);
      return { script_srcs: s.filter(Boolean).length }
    })()`) || null;
    cdp.ws.close();

    const report = { ok: true, case: A.caseName, identity, shots,
      review_note: 'reviewed:false means THIS tool run only proved PNG magic+size; visual review (vision_analyze per hermes-workflows-ui-qa) is mandatory before any layout claim' };
    fs.writeFileSync(path.join(A.outDir, 'report.json'), JSON.stringify(report, null, 2) + '\n');
    fs.writeFileSync(path.join(A.outDir, 'identity.json'), JSON.stringify(identity, null, 2) + '\n');
    console.log(JSON.stringify({ ok: true, out: A.outDir, run_id: runId,
      plugin_sha256: pluginSha, captures: shots.map(s => s.file) }));
    return 0;
  } finally {
    // Revert the two trusted inputs FIRST (config hygiene), then kill ONLY
    // this supervisor's process groups + the path-scoped survivor sweep.
    for (const key of touched.reverse()) {
      try {
        const before = identity.config_touched[key]?.before;
        if (before === null || before === undefined) unsetConfig(hermesBin, key);
        else if (['string', 'number', 'boolean'].includes(typeof before)) writeConfig(hermesBin, [key, String(before)]);
        else revertFailures.push(`${key}: prior value ${JSON.stringify(before)} is non-scalar — restore by hand`);
      } catch (e) { revertFailures.push(`${key}: ${String(e.message).slice(0, 200)}`); }
    }
    if (A.keep) fs.writeFileSync(path.join(A.outDir, 'logs', 'KEEP.txt'),
      JSON.stringify(sup.children) + '\n');
    else await sup.teardown();
    identity.teardown = { survivors: sup.survivors || [], revert_failures: revertFailures };
    fs.writeFileSync(path.join(A.outDir, 'identity.json'), JSON.stringify(identity, null, 2) + '\n');
  }
}

main().then(code => process.exit(code ?? 0)).catch(async e => {
  const code = e instanceof Bail ? e.code : 1;
  console.error(`UI2_PROOF_FAIL(${code}): ${e.message}`);
  if (e.stack && code === 1) console.error(e.stack.split('\n').slice(0, 4).join('\n'));
  process.exit(code);
});
