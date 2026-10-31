feat(pack,door): one sidecar schema — install.json grows source_repo

The provenance record pack.py stamps at the ZIP root now names its ORIGIN:
{version, source_commit, packaged_at, source_repo}. The record rides the
package copy into the plugin directory, so an installed seat answers "what
am I" cold (sidecar, live manifest, and qualified archive stop disagreeing
without a re-resolve). pack.py resolves the
value from a HERMES_WF_PACK_REPO pin (echoed only when already owner/repo —
same sanitize law as the commit pin, never a raw caller string), else the
`git remote get-url origin` read, else "unknown". The git fallback accepts
only host-carrying remote URLs (scheme://[user@]host/… or scp-style
user@host:…), so a bare path or file:// origin answers "unknown" rather than
a fabricated owner, and the owner segment is dot-free (a dotted pin like an
IP host is refused, never echoed verbatim). The packing clone's origin is a
named build input: the byte-identity test leg pins HERMES_WF_PACK_REPO. The
door's doctor_version surfaces it verbatim; a sidecar written under the old
three-key schema still loads and reads source_repo:null — honest absence,
never an invented origin.

Tests: tests/test_version_truth_159.py (V3 four-key schema, V13/V13b repo
seams, V14/V14b malformed-pin refusal, V15/V15b dotted-owner-pin refusal,
V16 unit legs for host-less origins, D2/D9 field sets, D10 legacy-sidecar
back-compat, D11 composed passthrough) and the pinned-origin byte-identity
leg in tests/test_packaging.py.
