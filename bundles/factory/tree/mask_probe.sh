#!/usr/bin/env bash
# factory-smoke credential-mask probe, run as sandboxed agent Bash. Prints what the sandbox sees for two
# masked dummy variables (a credential-shaped name and a plain one), then sends both to the echo host
# ($1, factory.json's smoke.echo_host), which echoes the request headers back: the proxy should have put
# the real values there.
host=${1:?usage: mask_probe.sh <echo host>}
printf 'secret=%s value=%s\n' "${FACTORY_PROBE_SECRET:-unset}" "${FACTORY_PROBE_VALUE:-unset}"
curl -sS --max-time 20 "https://$host/headers" -H "X-Secret: ${FACTORY_PROBE_SECRET:-}" -H "X-Value: ${FACTORY_PROBE_VALUE:-}"
echo
echo end
