feat(pack,door): one sidecar schema — install.json grows source_repo

The provenance record pack.py stamps at the ZIP root now names its ORIGIN:
{version, source_commit, packaged_at, source_repo}. The record rides the
package copy into the plugin directory, so an installed seat answers "what
am I" cold (sidecar, live manifest, and qualified archive stop disagreeing
without a re-resolve). pack.py resolves the
value from a HERMES_WF_PACK_REPO pin (echoed only when already owner/repo —
same sanitize law as the commit pin, never a raw caller string), else the
`git remote get-url origin` read, else "unknown". The door's doctor_version
surfaces it verbatim; a sidecar written under the old three-key schema still
loads and reads source_repo:null — honest absence, never an invented origin.

Tests: tests/test_version_truth_159.py (V3 four-key schema, V13/V13b repo
seams, V14/V14b malformed-pin refusal, D2/D9 field sets, D10 legacy-sidecar
back-compat, D11 end-to-end passthrough).
