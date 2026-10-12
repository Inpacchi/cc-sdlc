#!/usr/bin/env bash
# factory-smoke services probe, run as sandboxed agent Bash. FACTORY_SVC_1 is the stand-in service
# (the echo host, $1: factory.json's smoke.echo_host, wired by services.py); FACTORY_SVC_2 is a slot no
# service uses. Prints what the sandbox sees for both, then sends both to the echo host, which echoes the
# request headers: only slot 1's real value may arrive there.
host=${1:?usage: services_probe.sh <echo host>}
printf 'svc1=%s svc2=%s\n' "${FACTORY_SVC_1:-unset}" "${FACTORY_SVC_2:-unset}"
curl -sS --max-time 20 "https://$host/headers" -H "X-Svc-One: ${FACTORY_SVC_1:-}" -H "X-Svc-Two: ${FACTORY_SVC_2:-}"
echo
echo end
