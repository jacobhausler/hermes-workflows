#!/bin/bash
# In-container CI-parity: replicates .github/workflows/ci.yml gates on ubuntu:24.04.
# The pin and the python-version ride ci.yml — parsed after checkout (est-rmsro),
# never hardcoded here.
# usage (inside container): bash /ci/ue/ci-parity-run.sh <lane-sha>
set -u
SHA="${1:-}"
cd /ci
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq python3 python3-pip python3-venv nodejs npm git curl ca-certificates >/dev/null 2>&1
git config --global --add safe.directory /ci
[ -n "$SHA" ] && git cat-file -e "$SHA^{commit}" 2>/dev/null && git checkout -q "$SHA" 2>/dev/null || true

# single source of truth: parse pin + interpreter from the checked-out ci.yml (est-rmsro)
HERMES_PIN="$(sed -n 's/^[[:space:]]*HERMES_PIN:[[:space:]]*\([0-9a-f]\{7,\}\).*/\1/p' .github/workflows/ci.yml | head -1)"
[ -n "$HERMES_PIN" ] || { echo "FATAL: HERMES_PIN not parseable from .github/workflows/ci.yml"; exit 1; }
PYV="$(sed -n 's/^[[:space:]]*python-version:[[:space:]]*"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' .github/workflows/ci.yml | head -1)"
if [ -n "$PYV" ]; then
  apt-get install -y -qq "python${PYV}" "python${PYV}-pip" "python${PYV}-venv" nodejs npm git curl ca-certificates >/dev/null 2>&1 \
    || echo "WARN: python${PYV} unavailable in the image — suite arms ride the image-default interpreter"
fi

git clone -q --filter=blob:none https://github.com/NousResearch/hermes-agent /opt/hermes-agent 2>/dev/null
git -C /opt/hermes-agent checkout -q $HERMES_PIN
python3 -m venv --without-pip /opt/hermes-venv 2>/dev/null || python3 -m venv /opt/hermes-venv
curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
/opt/hermes-venv/bin/python /tmp/get-pip.py -q
/opt/hermes-venv/bin/pip install -q -e /opt/hermes-agent || { echo "pin install failed, falling back to main"; git -C /opt/hermes-agent checkout -q main; /opt/hermes-venv/bin/pip install -q -e /opt/hermes-agent; }
HERMES=/opt/hermes-venv/bin/hermes

RC=0
gate() {
  local name=$1; shift
  if "$@" >/tmp/gate-$name.log 2>&1; then echo "##GATE## $name pass"; else echo "##GATE## $name FAIL rc=$?"; tail -25 /tmp/gate-$name.log; RC=1; fi
}

gate node-check bash -c 'cp desktop/plugin.js /tmp/plugin.check.mjs && node --check /tmp/plugin.check.mjs'
gate suite python3 scripts/suite.py . ci-out
gate scrub python3 scripts/make_public.py /tmp/public-tree
gate plugins-validate $HERMES plugins validate .
gate doctor bash -c "XDG_CONFIG_HOME=/tmp/hcfg HOME=/tmp/hhome $HERMES doctor"
[ "$RC" = 0 ] && echo "##GREEN##"
exit $RC
