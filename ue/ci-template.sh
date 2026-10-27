#!/bin/bash
# In-lane CI-parity v3: mirrors .github/workflows/ci.yml exactly — the pin and
# the interpreter are PARSED from ci.yml at run time (est-rmsro), never hardcoded
# here, so a repin of the workflow cannot leave this mirror stale. Gates: pinned
# hermes editable install, suite, scrub, plugin validate. Baseline admission: the
# suite runs on the base SHA first; lane reds are only introduced reds.
set -u
export DEBIAN_FRONTEND=noninteractive PIP_BREAK_SYSTEM_PACKAGES=1
apt-get update -qq >/dev/null 2>&1
git config --global --add safe.directory '*' || true
cd "$(dirname "$0")/.."
# single source of truth: parse pin + interpreter from ci.yml (est-rmsro)
HERMES_PIN="$(sed -n 's/^[[:space:]]*HERMES_PIN:[[:space:]]*\([0-9a-f]\{7,\}\).*/\1/p' .github/workflows/ci.yml | head -1)"
[ -n "$HERMES_PIN" ] || { echo "FATAL: HERMES_PIN not parseable from .github/workflows/ci.yml"; exit 1; }
PYV="$(sed -n 's/^[[:space:]]*python-version:[[:space:]]*"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' .github/workflows/ci.yml | head -1)"
PY=python3
if [ -n "$PYV" ]; then
  apt-get install -y -qq "python${PYV}" "python${PYV}-venv" nodejs git curl ca-certificates >/dev/null 2>&1 && PY="python${PYV}"
fi
command -v "$PY" >/dev/null || { echo "WARN: python${PYV:-?} unavailable in the image — suite arms ride the image-default interpreter"; PY=python3; }
apt-get install -y -qq "$PY" "${PY}-venv" nodejs git curl ca-certificates >/dev/null 2>&1 || true
$PY -c "import yaml" 2>/dev/null || $PY -m pip install -q pyyaml >/dev/null 2>&1 || true
git init -q 2>/dev/null; git config user.email ci@local; git config user.name ci
BASE="${BASE_SHA:-$(git rev-parse HEAD~1 2>/dev/null || true)}"
git add -A -f >/dev/null 2>&1; git commit -qm "ci snapshot"
git update-ref refs/remotes/origin/main HEAD
[ -n "$BASE" ] && git tag ci-base "$BASE" 2>/dev/null || true

# pinned hermes-agent, editable — same install as ci.yml (pin parsed above)
git clone -q --filter=blob:none https://github.com/NousResearch/hermes-agent /opt/hermes-agent
git -C /opt/hermes-agent checkout -q $HERMES_PIN || git -C /opt/hermes-agent checkout -q main
$PY -m venv /opt/hv
/opt/hv/bin/pip install -q -e /opt/hermes-agent 2>/dev/null || { git -C /opt/hermes-agent checkout -q main; /opt/hv/bin/pip install -q -e /opt/hermes-agent; }
. /opt/hv/bin/activate

RC=0
gate() {
  local name=$1; shift
  if "$@" >/tmp/g-$name.log 2>&1; then echo "GATE $name pass"; else echo "FAIL $name"; tail -25 /tmp/g-$name.log; RC=1; fi
}
gate node-check bash -c 'cp desktop/plugin.js /tmp/plugin.check.mjs && node --check /tmp/plugin.check.mjs'
if [ -n "$(git tag -l ci-base)" ]; then
  gate base-suite bash -c "git checkout -q ci-base && python3 scripts/suite.py . /tmp/base-out; rc=\$?; git checkout -q -; [ \$rc -le 1 ]"
  gate suite python3 scripts/suite.py . /tmp/ci-out --baseline /tmp/base-out/exits.json
else
  gate suite python3 scripts/suite.py . /tmp/ci-out
fi
gate scrub python3 scripts/make_public.py /tmp/public-tree
gate plugins-validate hermes plugins validate .
echo "CI-EXIT $RC"
[ "$RC" = 0 ] && echo "CI PASS" || echo "CI FAIL"
exit $RC
