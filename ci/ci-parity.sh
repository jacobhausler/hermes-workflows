#!/usr/bin/env bash
# ue-bead CI-parity gate lane script.
# Mirrors upstream .github/workflows/ci.yml gates on the cluster via crun.
# Verdict cache: $LANE/.ci-verdict (PASS/FAIL + rc + timestamp). CI gate re-invokes
# this script on `every_s` ticks; a PASS cache exits 0 immediately; a FAIL cache is
# honored for 1h (retry sooner only by deleting it).
set -uo pipefail
LANE="$(cd "$(dirname "$0")/.." && pwd)"
V="$LANE/.ci-verdict"
if [ -f "$V" ]; then
  now=$(date +%s); age=$(( now - $(stat -c %Y "$V") ))
  if grep -q '^PASS' "$V"; then exit 0; fi
  if grep -q '^FAIL' "$V" && [ "$age" -lt 3600 ]; then exit 1; fi
fi
export DEBIAN_FRONTEND=noninteractive PIP_BREAK_SYSTEM_PACKAGES=1
JOB="ue-ci-$(basename "$LANE")-$$"
cd "$LANE"
crun run --name "$JOB" --include-untracked --image ubuntu:24.04 -- bash -c '
set -u; rc=0
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq git openssh-client rsync python3-jsonschema nodejs npm >/dev/null 2>&1 || echo "WARN: apt partial"
PIN=d337b736aa1e8ebecfab043842d13e4a2d2f48a3
if command -v hermes >/dev/null 2>&1 && hermes --version >/dev/null 2>&1; then
  echo "HERMES: already present"
else
  git clone -q --filter=blob:none https://github.com/NousResearch/hermes-agent /tmp/hermes-agent \
    && git -C /tmp/hermes-agent checkout -q "$PIN" \
    && python3 -m pip install -q --break-system-packages --editable /tmp/hermes-agent >/dev/null 2>&1 \
    || echo "WARN: pinned core bootstrap failed"
fi
echo "=== suite (canonical entry) ==="
if [ -x tools/ci/run.sh ] || [ -f tools/ci/run.sh ]; then
  bash tools/ci/run.sh || rc=1
elif [ -f scripts/suite.py ]; then
  python3 scripts/suite.py . ci-out || rc=1
else
  echo "FATAL: no canonical suite entry (tools/ci/run.sh or scripts/suite.py)"; rc=1
fi
echo "=== node ESM parse ==="
cp desktop/plugin.js /tmp/ue-plugin.mjs && node --check /tmp/ue-plugin.mjs || rc=1
for f in $(git ls-files "bin/*.js"); do node --check "$f" || rc=1; done
[ -f tests/test_edge_routing.mjs ] && { node --experimental-strip-types tests/test_edge_routing.mjs || rc=1; }
echo "=== plugins validate (pinned core) ==="
hermes plugins validate . || { hermes --version 2>/dev/null || echo "NOTE: core absent — validate unrunnable in this image"; rc=1; }
echo "=== doctor ==="
hermes doctor 2>&1 | tail -2 || true
echo "=== scrub audit ==="
python3 scripts/make_public.py /tmp/ue-pub 2>&1 | tail -2 || rc=1
echo "CI_PARITY=$([ $rc -eq 0 ] && echo GREEN || echo RED)"
exit $rc
'
rc=$?
if [ "$rc" -eq 0 ]; then echo PASS > "$V"; else echo FAIL > "$V"; fi
echo "rc=$rc $(date -Is)" >> "$V"
exit "$rc"
