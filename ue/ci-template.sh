#!/bin/bash
# In-lane CI-parity v3: mirrors .github/workflows/ci.yml exactly (pinned hermes
# editable install, suite, scrub, plugin validate). Baseline admission: the
# suite runs on the base SHA first; lane reds are only introduced reds.
set -u
export DEBIAN_FRONTEND=noninteractive PIP_BREAK_SYSTEM_PACKAGES=1
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq -t noble python3.12 python3.12-venv nodejs git curl ca-certificates >/dev/null 2>&1 || \
  apt-get install -y -qq python3 python3-venv nodejs git curl ca-certificates >/dev/null 2>&1
PY=python3.12; command -v python3.12 >/dev/null || PY=python3
$PY -c "import yaml" 2>/dev/null || $PY -m pip install -q pyyaml >/dev/null 2>&1 || true
git config --global --add safe.directory '*' || true
cd "$(dirname "$0")/.."
git init -q 2>/dev/null; git config user.email ci@local; git config user.name ci
BASE="${BASE_SHA:-$(git rev-parse HEAD~1 2>/dev/null || true)}"
git add -A -f >/dev/null 2>&1; git commit -qm "ci snapshot"
git update-ref refs/remotes/origin/main HEAD
[ -n "$BASE" ] && git tag ci-base "$BASE" 2>/dev/null || true

# pinned hermes-agent, editable — same install as ci.yml (line 69-72)
HERMES_PIN=d337b736aa1e8ebecfab043842d13e4a2d2f48a3
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
