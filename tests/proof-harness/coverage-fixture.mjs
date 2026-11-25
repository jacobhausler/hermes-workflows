// Stage the candidate agent half for the isolated coverage bench. Only its
// dashboard API is copied: the renderer and the rest of the plugin stay at
// the exact candidate bytes. The installed plugin never imports this fixture.
import fs from 'node:fs';
import path from 'node:path';

export function stageCoveragePlugin(repo, pluginDir) {
  const api = path.join('dashboard', 'plugin_api.py');
  const fixtureAPI = path.join(pluginDir, api);
  const marker = path.join(pluginDir, 'dashboard', '.proof-short-page');
  fs.mkdirSync(path.dirname(fixtureAPI), { recursive: true });
  for (const name of fs.readdirSync(repo)) {
    if (name === 'dashboard' || name === '.git' || name === '__pycache__') continue;
    fs.symlinkSync(path.join(repo, name), path.join(pluginDir, name));
  }
  for (const name of fs.readdirSync(path.join(repo, 'dashboard'))) {
    if (name === 'plugin_api.py' || name === '__pycache__') continue;
    fs.symlinkSync(path.join(repo, 'dashboard', name), path.join(pluginDir, 'dashboard', name));
  }
  // The registered synchronous GET /runs handler calls _list_runs per request.
  // Wrap that call in the staged module; keep the real scan and summary intact.
  fs.writeFileSync(fixtureAPI, fs.readFileSync(path.join(repo, api), 'utf8') + `

# Coverage bench fixture; not installed with the production API.
_proof_original_list_runs = _list_runs
_proof_short_page = Path(__file__).with_name('.proof-short-page')
_proof_delay_census = Path(__file__).with_name('.proof-delay-census')
_proof_fail_census = Path(__file__).with_name('.proof-fail-census')
_proof_cap_census = Path(__file__).with_name('.proof-cap-census')
_proof_pending_census = Path(__file__).with_name('.proof-pending-census')

def _list_runs(offset=0, limit=100, *, _record=None):
    if _proof_delay_census.is_file():
        time.sleep(2.0)
    if _proof_fail_census.is_file():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail='bench-only census failure')
    if _proof_cap_census.is_file():
        # Cap-truncation frame: serve the FIRST window for EVERY offset with
        # the total removed — the real fetcher's bounded walk can never cover,
        # so its own 30-page cap clips (truncated:true rides the result). Real
        # truncation at the registered route, not a synthetic network body.
        page = _proof_original_list_runs(0, limit, _record=_record)
        return {k: v for k, v in page.items() if k != 'total'}
    page = _proof_original_list_runs(offset, limit, _record=_record)
    if _proof_pending_census.is_file():
        # Pending frame: counted-positive, loaded-zero. The honest counted
        # total rides; only the window is emptied.
        return {**page, 'runs': []}
    if offset >= 100 and _proof_short_page.is_file():
        return {**page, 'runs': []}
    return page
`);
  return marker;
}
