#!/usr/bin/env bash
# Factory runner host setup (z-sdlc's factory bundle, design rules D2 and D3).
#
# Creates an unprivileged runner user with rootless Docker, firewalls that user away from every
# host-local and LAN address (databases, caches, admin panels, ...), verifies the isolation from
# inside a container, then installs the GitHub Actions runner as a systemd service that cannot start
# without the firewall: one or more instances, each with its own directory and work folder, so jobs
# run in parallel. The runners register to the organization's runner group, so every project that
# group allows shares them.
#
# Three tiers (design rule D3, and Enablement step 10's CI tier), each its own user, firewall table,
# runners and label (factory.json's runners.strict, runners.planning and runners.ci):
#   TIER=strict    factory-runner: implement, execute, revise. No host or LAN access.
#   TIER=planning  factory-planner: spec and plan. The same firewall, plus the open internet the stages
#                  need and, if host.conf names one, a database port on this host's own addresses.
#   TIER=ci        factory-ci: a project's own CI jobs that must run self-hosted (end-to-end suites that
#                  outgrow GitHub-hosted runners), pull requests included, one disposable runner per job.
#                  Steps 1-6 as for strict (its user, firewall, caps, rootless Docker, the isolation test),
#                  then setup-ci.sh: the job image (the project's toolchain with the runner on top, built
#                  here), the isolation checks, and one systemd slot per concurrent job running
#                  ci_launcher.py. A slot starts a fresh container per job from a just-in-time runner
#                  registration and removes it after, so whatever a pull request's job does, to the runner's
#                  own processes included, ends with its container. The runner-registration App's key must
#                  already be at /etc/factory-runner/factory-ci/app.pem, root-only (never in a checkout).
#
# One host can run several organizations' runners. The first keeps the plain names above; each other
# organization sets RUNNER_INSTANCE in its own host.conf (for example `acme`), and gets its own users
# (factory-runner-acme, factory-planner-acme), firewall tables, services and runners, isolated from the
# others' as from the host. Setup refuses to touch runners registered to another organization.
#
# This host's settings are host.conf beside this script (each has a default; see the file). Run from a
# checkout of the project's default branch, as root:
#   sudo bash setup.sh                          (strict tier)
#   sudo TIER=planning bash setup.sh            (planning tier)
#   sudo TIER=ci bash setup.sh                  (CI tier)
#   bash setup.sh --print-settings              (show the resolved settings and stop; no root needed)
# The first run for a tier also names the repository whose checkout owns it, which must be this one's:
#   sudo TIER_OWNER=<owner>/<repository> bash setup.sh
# Idempotent: safe to re-run. Runner registration happens only when a registration token file exists
# (default: <this dir>/reg-token, mode 600). One token registers every new instance (it stays valid for
# an hour); the file is deleted after use.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
FACTORY_JSON=${FACTORY_JSON:-$SCRIPT_DIR/../factory.json}
HOST_CONF=${HOST_CONF:-$SCRIPT_DIR/host.conf}
TOKEN_FILE=${TOKEN_FILE:-$SCRIPT_DIR/reg-token}
# host.conf is part of the reviewed checkout (code-owned), like this script.
if [[ -f $HOST_CONF ]]; then
  # shellcheck source=/dev/null
  source "$HOST_CONF"
fi
setting() { python3 -I -c 'import json,sys; v=json.load(open(sys.argv[1])); [v := v[k] for k in sys.argv[2].split(".")]; print(v)' "$FACTORY_JSON" "$1"; }
origin_owner() { { git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || true; } | sed -E 's#^(https://github\.com/|git@github\.com:)##; s#/.*##'; }

FACTORY_ORG=${FACTORY_ORG:-$(origin_owner)}
# A tier's runner group: factory.json's runners.groups.<shared|ci>, as bootstrap.py reads it.
group_setting() { python3 -I -c 'import json,sys; r=json.load(open(sys.argv[1])).get("runners") or {}; print((r.get("groups") or {}).get(sys.argv[2]) or sys.argv[3])' "$FACTORY_JSON" "$1" "$2"; }
RUNNER_HOME_BASE=${RUNNER_HOME_BASE:-/var/lib/factory}
RUNNER_NAME_PREFIX=${RUNNER_NAME_PREFIX:-$(hostname -s)}
LAN_DNS=${LAN_DNS:-}
PROBE_PORTS=${PROBE_PORTS:-22 80 443 3000 5432 6379 8000 8080}
PLANNING_DB_PORT=${PLANNING_DB_PORT:-}
RUNNER_INSTANCE=${RUNNER_INSTANCE:-}
if [[ -n $RUNNER_INSTANCE && ! $RUNNER_INSTANCE =~ ^[a-z][a-z0-9]{0,11}$ ]]; then
  printf 'ERROR: RUNNER_INSTANCE must be a lowercase letter then up to 11 lowercase letters or digits\n' >&2; exit 1
fi
# Names for this organization's runners: plain for the host's first organization, suffixed for another.
dash=${RUNNER_INSTANCE:+-$RUNNER_INSTANCE} under=${RUNNER_INSTANCE:+_$RUNNER_INSTANCE}

tier_named=${TIER:+yes}
TIER=${TIER:-strict}
case $TIER in
  strict)
    RUNNER_USER=factory-runner$dash
    NFT_TABLE=factory_runner$under; NFT_FILE=/etc/factory-runner/firewall$dash.nft; FW_UNIT=factory-firewall$dash
    RUNNER_UNIT=factory-runner$dash; RUNNER_LABELS=$(setting runners.strict); NAME_PREFIX=$RUNNER_NAME_PREFIX-factory
    DEFAULT_COUNT=${STRICT_RUNNERS:-3}; MEM_HIGH=${STRICT_MEMORY_HIGH:-8G}; MEM_MAX=${STRICT_MEMORY_MAX:-10G}
    CPU_QUOTA=${STRICT_CPU_QUOTA:-400%}
    RUNNER_GROUP=$(group_setting shared factory-pool)
    DB_PORT= ;;
  planning)
    RUNNER_USER=factory-planner$dash
    NFT_TABLE=factory_planner$under; NFT_FILE=/etc/factory-runner/planner-firewall$dash.nft
    FW_UNIT=factory-planner-firewall$dash
    RUNNER_UNIT=factory-planner$dash; RUNNER_LABELS=$(setting runners.planning); NAME_PREFIX=$RUNNER_NAME_PREFIX-planner
    DEFAULT_COUNT=${PLANNING_RUNNERS:-2}; MEM_HIGH=${PLANNING_MEMORY_HIGH:-4G}; MEM_MAX=${PLANNING_MEMORY_MAX:-5G}
    CPU_QUOTA=${PLANNING_CPU_QUOTA:-200%}
    RUNNER_GROUP=$(group_setting shared factory-pool)
    # The one exception D3 allows: a database the planning tier reads, published on this host.
    DB_PORT=$PLANNING_DB_PORT ;;
  ci)
    RUNNER_USER=factory-ci$dash
    NFT_TABLE=factory_ci$under; NFT_FILE=/etc/factory-runner/ci-firewall$dash.nft; FW_UNIT=factory-ci-firewall$dash
    # A factory.json from before the CI tier has no runners.ci: refused below, with the reason.
    RUNNER_UNIT=factory-ci$dash; RUNNER_LABELS=$(setting runners.ci 2> /dev/null || true); NAME_PREFIX=$RUNNER_NAME_PREFIX-ci
    # End-to-end suites (a server, a browser or two, a database) are CPU-bound. Each job's container has its own
    # caps (CI_JOB_*), and the slice caps every concurrent job together: its CPUQuota is what keeps the host's own
    # work (production included) its cores, since a weight here would only rank the CI user against other users.
    DEFAULT_COUNT=${CI_RUNNERS:-2}; MEM_HIGH=${CI_MEMORY_HIGH:-14G}; MEM_MAX=${CI_MEMORY_MAX:-16G}
    CPU_QUOTA=${CI_CPU_QUOTA:-800%}
    RUNNER_GROUP=$(group_setting ci factory-ci)
    CI_APP_CLIENT_ID=${CI_APP_CLIENT_ID:-}
    CI_JOB_CPUS=${CI_JOB_CPUS:-4}; CI_JOB_MEMORY=${CI_JOB_MEMORY:-6g}; CI_JOB_PIDS=${CI_JOB_PIDS:-8192}
    CI_JOB_SHM=${CI_JOB_SHM:-1g}; CI_JOB_HOURS=${CI_JOB_HOURS:-6}; CI_IDLE_HOURS=${CI_IDLE_HOURS:-24}
    CI_MIN_FREE_GB=${CI_MIN_FREE_GB:-20}
    DB_PORT= ;;
  *) printf 'ERROR: TIER must be strict, planning or ci\n' >&2; exit 1 ;;
esac
[[ -n $RUNNER_LABELS && $RUNNER_LABELS != None ]] \
  || { printf 'ERROR: factory.json names no runner label for the %s tier (runners.%s)\n' "$TIER" "$TIER" >&2; exit 1; }
RUNNER_HOME=$RUNNER_HOME_BASE/$RUNNER_USER
RUNNER_COUNT=${RUNNER_COUNT:-$DEFAULT_COUNT}
RUNNER_URL=https://github.com/$FACTORY_ORG
# The first organization's strict runner 1 keeps the paths and name from before there were several, so
# its registration carries over.
legacy_first() { [[ $TIER == strict && -z $RUNNER_INSTANCE ]] && (($1 == 1)); }
runner_dir() {
  if legacy_first "$1"; then echo "$RUNNER_HOME/actions-runner"; else echo "$RUNNER_HOME/actions-runner-$1"; fi
}
runner_work() {
  if legacy_first "$1"; then echo "$RUNNER_HOME/_work"; else echo "$RUNNER_HOME/_work-$1"; fi
}
runner_name() {
  if legacy_first "$1"; then echo "$NAME_PREFIX"; else echo "$NAME_PREFIX-$1"; fi
}
RUNNER_VERSION=2.338.0
RUNNER_SHA256=af4b794c1bc41d73d40535e3fe092a39f9679cd8d965954c2aca25a05ca41d32

if [[ ${1:-} == --print-settings ]]; then
  ci_settings=
  [[ $TIER == ci ]] && ci_settings="CI_APP_CLIENT_ID CI_JOB_CPUS CI_JOB_MEMORY CI_JOB_PIDS CI_JOB_SHM CI_JOB_HOURS CI_IDLE_HOURS CI_MIN_FREE_GB"
  for v in TIER FACTORY_ORG RUNNER_URL RUNNER_GROUP RUNNER_LABELS RUNNER_INSTANCE RUNNER_USER RUNNER_HOME RUNNER_UNIT \
           FW_UNIT NFT_TABLE NFT_FILE RUNNER_COUNT MEM_HIGH MEM_MAX CPU_QUOTA DB_PORT LAN_DNS PROBE_PORTS $ci_settings; do
    printf '%s=%s\n' "$v" "${!v}"
  done
  printf 'RUNNER_NAMES=%s\n' "$(for i in $(seq "$RUNNER_COUNT"); do runner_name "$i"; done | tr '\n' ' ' | sed 's/ $//')"
  exit 0
fi

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }


# Never take over another organization's runners: a runner directory this run would use must be
# registered to this organization, or not at all.
for i in $(seq 99); do
  conf=$(runner_dir "$i")/.runner
  [[ -r $conf ]] || continue
  url=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8-sig")).get("gitHubUrl", ""))' "$conf" 2>/dev/null) \
    || die "can't read $conf"
  if [[ ${url%/} != "$RUNNER_URL" ]]; then
    die "$RUNNER_USER's runner $i is registered to $url, not $RUNNER_URL: for a second organization on this host, set RUNNER_INSTANCE in its host.conf"
  fi
done

[[ $EUID -eq 0 ]] || die "run as root (sudo bash $0)"
command -v dockerd-rootless-setuptool.sh >/dev/null || die "docker-ce-rootless-extras is not installed"
command -v nft >/dev/null || die "nft is not installed"
[[ -f "$SCRIPT_DIR/seccomp-bwrap.json" ]] || die "seccomp-bwrap.json must sit next to this script"
[[ $RUNNER_COUNT =~ ^[1-9][0-9]?$ ]] || die "RUNNER_COUNT must be 1-99"
[[ $FACTORY_ORG =~ ^[A-Za-z0-9-]+$ ]] || die "set FACTORY_ORG in host.conf (the GitHub organization the runners register to)"
if [[ $TIER == ci ]]; then
  # Everything the CI tier needs, checked before anything on this host changes.
  for f in setup-ci.sh ci_launcher.py ci-runner.Dockerfile; do [[ -f $SCRIPT_DIR/$f ]] || die "$f must sit next to this script"; done
  [[ $CI_APP_CLIENT_ID =~ ^[A-Za-z0-9.]+$ ]] \
    || die "set CI_APP_CLIENT_ID in host.conf: the runner-registration App's client ID (create_app.py --runners)"
  # Zero means unlimited to Docker, so every cap must be positive.
  for v in CI_JOB_CPUS CI_JOB_HOURS CI_IDLE_HOURS; do
    [[ ${!v} =~ ^([1-9][0-9]*(\.[0-9]+)?|0\.[0-9]*[1-9][0-9]*)$ ]] || die "$v must be a number above 0"
  done
  for v in CI_JOB_PIDS CI_MIN_FREE_GB; do [[ ${!v} =~ ^[1-9][0-9]*$ ]] || die "$v must be a whole number above 0"; done
  for v in CI_JOB_MEMORY CI_JOB_SHM; do [[ ${!v} =~ ^[1-9][0-9]*[kmg]$ ]] || die "$v must be like 6g or 512m"; done
  python3 -I - "$CI_JOB_MEMORY" "$RUNNER_COUNT" "$MEM_HIGH" "$MEM_MAX" <<'PY' || die "the CI tier's memory settings (above)"
import sys
def size(text):
    text = text.strip().lower()
    return int(text[:-1]) * 1024 ** "kmgt".index(text[-1]) * 1024 if text[-1] in "kmgt" else int(text)
try:
    job, count, high, top = size(sys.argv[1]), int(sys.argv[2]), size(sys.argv[3]), size(sys.argv[4])
except ValueError:
    sys.exit("CI_MEMORY_HIGH and CI_MEMORY_MAX must be sizes like 14G")
# Two busy jobs at their caps must fit under MemoryHigh, with room for the daemon, or the slice reclaims constantly.
need = job * count + 2 * 1024 ** 3
if high < need or top < high:
    sys.exit(f"CI_MEMORY_HIGH ({sys.argv[3]}) must be at least CI_RUNNERS x CI_JOB_MEMORY + 2G ({need // 1024 ** 2}M), "
             f"and CI_MEMORY_MAX ({sys.argv[4]}) at least CI_MEMORY_HIGH")
PY
  # The runner-registration App's key reaches every runner group in the organization: root-only, never in a checkout.
  ci_key=/etc/factory-runner/$RUNNER_UNIT/app.pem
  if [[ -e $SCRIPT_DIR/ci-app.pem ]]; then
    die "a key at $SCRIPT_DIR/ci-app.pem: the runner-registration App's key never goes in a checkout. Install it with sudo install -D -m 600 -o root -g root <key> $ci_key, then delete every other copy"
  fi
  [[ -f $ci_key && ! -L $ci_key ]] \
    || die "install the runner-registration App's private key first: sudo install -D -m 600 -o root -g root <key> $ci_key (then delete every other copy)"
  chown root:root "$ci_key" && chmod 600 "$ci_key"
fi

# One designated checkout per tier: the repository whose checkout sets the tier up is recorded, and a run from
# another repository's checkout is refused, so its host.conf can't re-cap or re-label a tier it doesn't own (a
# dropped TIER would otherwise fall through to strict). The record is made only when the operator names that
# repository (TIER_OWNER): the first checkout to run doesn't get a tier by default.
tier_owner=$({ git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || true; } \
  | sed -E 's#^(https://github\.com/|git@github\.com:)##; s#\.git$##')
[[ -n $tier_owner ]] || die "can't tell which repository this checkout is (no origin remote)"
owner_file=/etc/factory-runner/tiers/$RUNNER_UNIT
if [[ -f $owner_file ]]; then
  [[ $(<"$owner_file") == "$tier_owner" ]] \
    || die "the $TIER tier ($RUNNER_UNIT) is set up from $(<"$owner_file")'s checkout: run setup there, or remove $owner_file to hand the tier to $tier_owner"
else
  [[ ${TIER_OWNER:-} == "$tier_owner" ]] \
    || die "no checkout owns the $TIER tier ($RUNNER_UNIT) yet: if $tier_owner's should, run again with TIER=$TIER TIER_OWNER=$tier_owner"
  # A claim names its tier too: a dropped TIER would claim strict.
  [[ -n $tier_named ]] || die "name the tier you're giving $tier_owner: TIER=strict, planning or ci, with TIER_OWNER"
  install -d -m 755 -o root -g root /etc/factory-runner /etc/factory-runner/tiers
  printf '%s\n' "$tier_owner" > "$owner_file"
fi

log "1/8 packages: uidmap, dbus-user-session"
missing=()
for p in uidmap dbus-user-session; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
if ((${#missing[@]})); then apt-get update -qq && apt-get install -y --no-install-recommends "${missing[@]}"; fi

log "2/8 user $RUNNER_USER (home $RUNNER_HOME)"
if ! id "$RUNNER_USER" >/dev/null 2>&1; then
  useradd --create-home --home-dir "$RUNNER_HOME" --shell /bin/bash --user-group "$RUNNER_USER"
fi
passwd -l "$RUNNER_USER" >/dev/null
chmod 750 "$RUNNER_HOME"
RUID=$(id -u "$RUNNER_USER")
for g in sudo docker adm lpadmin; do
  if id -nG "$RUNNER_USER" | tr ' ' '\n' | grep -qx "$g"; then die "$RUNNER_USER must not be in group $g"; fi
done
# Subordinate IDs for rootless Docker: a block of 65536 above every range already given out.
if ! grep -q "^$RUNNER_USER:" /etc/subuid || ! grep -q "^$RUNNER_USER:" /etc/subgid; then
  subids=$(awk -F: 'NF >= 3 && $2 + $3 > max { max = $2 + $3 } END { if (max < 165536) max = 165536; print max "-" max + 65535 }' \
    /etc/subuid /etc/subgid)
  grep -q "^$RUNNER_USER:" /etc/subuid || usermod --add-subuids "$subids" "$RUNNER_USER"
  grep -q "^$RUNNER_USER:" /etc/subgid || usermod --add-subgids "$subids" "$RUNNER_USER"
fi

host_ips=$(ip -4 -o addr show | awk '{print $4}' | cut -d/ -f1 | grep -v '^127\.' | tr '\n' ' ')
db_rule=
if [[ -n $DB_PORT ]]; then
  db_rule="ip daddr { $(echo $host_ips | tr ' ' ',') } tcp dport $DB_PORT counter accept comment \"production database (D3)\""
fi
log "3/8 firewall: $RUNNER_USER may reach the internet, nothing on this host or the LAN${DB_PORT:+ except port $DB_PORT}"
install -d -m 755 /etc/factory-runner
# Seccomp profile for agent jobs that run sandboxed Bash: Docker's default plus the namespace
# calls bubblewrap needs. Jobs name it with `--security-opt seccomp=/etc/factory-runner/seccomp-bwrap.json`
# and the rootless Docker CLI reads it. Root-owned, so no job can edit it (a workflow could still pass
# seccomp=unconfined itself; CI's workflow-policy check refuses that).
# Every organization's runners on this host share it: the last setup run installs its version.
python3 -m json.tool "$SCRIPT_DIR/seccomp-bwrap.json" >/dev/null || die "seccomp-bwrap.json is not valid JSON"
if ! cmp -s "$SCRIPT_DIR/seccomp-bwrap.json" /etc/factory-runner/seccomp-bwrap.json; then
  if [[ -f /etc/factory-runner/seccomp-bwrap.json ]]; then
    echo "Replacing /etc/factory-runner/seccomp-bwrap.json: the jobs of every organization's runners on this host use the new one."
  fi
  # Replaced only when it differs, and by a rename: a job created meanwhile reads the old file or the new one.
  install -m 644 -o root -g root "$SCRIPT_DIR/seccomp-bwrap.json" /etc/factory-runner/.seccomp-bwrap.json.new
  mv -f /etc/factory-runner/.seccomp-bwrap.json.new /etc/factory-runner/seccomp-bwrap.json
fi
cat > "$NFT_FILE" <<EOF
# Loaded by $FW_UNIT.service. Own table, never 'flush ruleset' (other tables, ufw's or another
# organization's runners', must stay).
# Matches by socket owner: rootless Docker egress leaves the host as $RUNNER_USER's sockets.
table inet $NFT_TABLE
delete table inet $NFT_TABLE
table inet $NFT_TABLE {
  set blocked4 {
    type ipv4_addr; flags interval
    elements = { 0.0.0.0/8, 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16,
                 172.16.0.0/12, 192.168.0.0/16, 224.0.0.0/4 }
  }
  chain output {
    # Before NAT (-100) so published-port DNAT can't rewrite the destination first.
    # Positive match + jump: socketless kernel packets (ICMP, RST) never enter runner_out.
    type filter hook output priority -150; policy accept;
    meta skuid $RUID jump runner_out
  }
  chain runner_out {
    ip daddr { 127.0.0.53${LAN_DNS:+, $LAN_DNS} } meta l4proto { tcp, udp } th dport 53 accept
    # No IPv6 at all: a host's global addresses and its LAN's global prefix are in no blocked set, and
    # everything a job needs answers over IPv4.
    meta nfproto ipv6 counter reject comment "no IPv6"
    $db_rule
    oifname "lo" counter reject comment "host-local services"
    ip daddr @blocked4 counter reject
  }
}
EOF
cat > /etc/systemd/system/$FW_UNIT.service <<EOF
[Unit]
Description=Firewall for the $RUNNER_USER user (blocks host and LAN${DB_PORT:+ except port $DB_PORT})
DefaultDependencies=no
Before=network-pre.target
Wants=network-pre.target
# nftables.service's stock ruleset starts with 'flush ruleset'. Its reload reloads this table, and its start or
# restart runs $FW_UNIT-reapply.service (below). Never a restart of this unit: user@ requires it, so that would
# restart the user's manager and kill its jobs.
After=nftables.service
ReloadPropagatedFrom=nftables.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft -f $NFT_FILE
ExecReload=/usr/sbin/nft -f $NFT_FILE
ExecStop=/usr/sbin/nft delete table inet $NFT_TABLE

[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/$FW_UNIT-reapply.service <<EOF
[Unit]
Description=Load the $RUNNER_USER firewall table again after nftables.service flushes the ruleset
DefaultDependencies=no
After=nftables.service $FW_UNIT.service

[Service]
Type=oneshot
ExecStart=/usr/sbin/nft -f $NFT_FILE

[Install]
WantedBy=nftables.service
EOF
# The user's systemd manager (and so rootless dockerd) never starts without the firewall.
install -d "/etc/systemd/system/user@$RUID.service.d"
cat > "/etc/systemd/system/user@$RUID.service.d/factory-firewall.conf" <<EOF
[Unit]
Requires=$FW_UNIT.service
After=$FW_UNIT.service
EOF
systemctl daemon-reload
systemctl enable "$FW_UNIT.service" "$FW_UNIT-reapply.service" >/dev/null
# Reload in place when already active: restarting would stop user@ (Requires=) and kill running jobs.
if systemctl is-active --quiet "$FW_UNIT.service"; then nft -f "$NFT_FILE"; else systemctl start "$FW_UNIT.service"; fi
nft list table inet "$NFT_TABLE" >/dev/null || die "firewall table did not load"

# Cap what factory jobs can take from everything else on this host. Rootless dockerd and every job
# container live in the user's slice; the runner itself is a system service (capped below).
install -d "/etc/systemd/system/user-$RUID.slice.d"
cat > "/etc/systemd/system/user-$RUID.slice.d/factory-limits.conf" <<EOF
[Slice]
MemoryHigh=$MEM_HIGH
MemoryMax=$MEM_MAX
CPUQuota=$CPU_QUOTA
TasksMax=16384
EOF
if [[ $TIER == ci ]]; then
  # Each job's container gets its own CPU, memory and process caps, which rootless Docker applies only when systemd
  # delegates those controllers to the user's manager.
  cat > "/etc/systemd/system/user@$RUID.service.d/factory-delegate.conf" <<EOF
[Service]
Delegate=cpu cpuset io memory pids
EOF
fi
systemctl daemon-reload

log "4/8 linger + user systemd session"
loginctl enable-linger "$RUNNER_USER"
systemctl start "user@$RUID.service"
for _ in $(seq 30); do [[ -S /run/user/$RUID/bus ]] && break; sleep 1; done
[[ -S /run/user/$RUID/bus ]] || die "user bus for $RUNNER_USER did not come up"
as_runner() {
  sudo -u "$RUNNER_USER" -H env XDG_RUNTIME_DIR="/run/user/$RUID" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$RUID/bus" \
    DOCKER_HOST="unix:///run/user/$RUID/docker.sock" PATH=/usr/bin:/bin:/usr/sbin:/sbin \
    bash -c "cd ~ && $1"
}

log "5/8 rootless Docker for $RUNNER_USER"
if [[ ! -f $RUNNER_HOME/.config/systemd/user/docker.service ]]; then
  as_runner "dockerd-rootless-setuptool.sh install"
fi
as_runner "systemctl --user enable --now docker.service"
# Weekly prune: every image bump leaves the old layers under $RUNNER_HOME_BASE. The user writes its
# own unit files: root never writes into a directory factory-runner controls (symlink safety).
sudo -u "$RUNNER_USER" mkdir -p "$RUNNER_HOME/.config/systemd/user"
sudo -u "$RUNNER_USER" tee "$RUNNER_HOME/.config/systemd/user/docker-prune.service" >/dev/null <<'EOF'
[Unit]
Description=Prune unused Docker data older than a week
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
Environment=DOCKER_HOST=unix://%t/docker.sock
# Never the CI tier's job image (labelled factory.keep): between jobs nothing uses it, and it can't be pulled back.
ExecStart=/usr/bin/docker system prune -af --filter until=168h --filter label!=factory.keep
EOF
sudo -u "$RUNNER_USER" tee "$RUNNER_HOME/.config/systemd/user/docker-prune.timer" >/dev/null <<'EOF'
[Unit]
Description=Weekly Docker prune for factory jobs

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
EOF
as_runner "systemctl --user daemon-reload && systemctl --user enable --now docker-prune.timer"
for _ in $(seq 30); do as_runner "docker info >/dev/null 2>&1" && break; sleep 1; done
as_runner "docker info --format '{{.SecurityOptions}} root={{.DockerRootDir}}'"
as_runner "docker info --format '{{.SecurityOptions}}' | grep -q rootless" || die "daemon is not rootless"

log "6/8 isolation test from inside a container (every probe must be BLOCKED${DB_PORT:+, except the database}; IPv6 always)"
probe_py=$(cat <<'PY'
import socket, sys
targets = sys.argv[1].split()
ports = [int(p) for p in sys.argv[2].split()]
bad = 0
for h in targets:
    for p in ports:
        try:
            socket.create_connection((h, p), timeout=3).close()
            print(f"REACHABLE {h}:{p}"); bad += 1
        except OSError as e:
            print(f"blocked   {h}:{p} ({e.__class__.__name__})")
try:
    s = socket.socket(socket.AF_UNIX); s.connect("/var/run/docker.sock")
    print("REACHABLE host docker.sock"); bad += 1
except OSError as e:
    print(f"blocked   host docker.sock ({e.__class__.__name__})")
try:
    socket.create_connection(("api.github.com", 443), timeout=10).close()
    print("ok        api.github.com:443 (internet works)")
except OSError as e:
    print(f"FAILED    api.github.com:443 ({e})"); bad += 1
sys.exit(1 if bad else 0)
PY
)
# IPv6 too: this host's global addresses and a public one, all of which the firewall rejects.
host_ips6=$(ip -6 -o addr show scope global 2>/dev/null | awk '{print $4}' | cut -d/ -f1 | tr '\n' ' ')
targets="127.0.0.1 10.0.2.2 $LAN_DNS $host_ips $host_ips6 2606:4700:4700::1111"
ports="$PROBE_PORTS"
# The planning tier may reach the database on the host's own addresses; probe the rest as usual.
if [[ -n $DB_PORT ]]; then ports=$(echo "$ports" | tr ' ' '\n' | grep -vx "$DB_PORT" | tr '\n' ' '); fi
echo "targets: $targets"
echo "ports:   $ports"
as_runner "docker pull -q python:3.12-slim" \
  || die "rootless Docker cannot pull images: check DNS/egress through the factory firewall (not an isolation failure)"
printf '%s' "$probe_py" | sudo -u "$RUNNER_USER" tee "$RUNNER_HOME/.isolation_probe.py" >/dev/null
as_runner "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v \$HOME/.isolation_probe.py:/probe.py:ro python:3.12-slim \
  python /probe.py '$targets' '$ports'" || die "isolation test FAILED: do not register the runner"
# Same probe on a user-defined network, the way Actions runs job containers.
as_runner "docker network inspect factory-probe >/dev/null 2>&1 || docker network create factory-probe >/dev/null"
as_runner "docker run --rm --network factory-probe -v \$HOME/.isolation_probe.py:/probe.py:ro \
  python:3.12-slim python /probe.py '$targets' '$(echo 5432 6379 | tr ' ' '\n' | grep -vx "${DB_PORT:-none}" | tr '\n' ' ')'" \
  || die "isolation test FAILED on a user network"
if [[ -n $DB_PORT ]]; then
  first_ip=${host_ips%% *}
  as_runner "docker run --rm --network factory-probe python:3.12-slim python -c \
    \"import socket; socket.create_connection(('$first_ip', $DB_PORT), timeout=5).close(); print('ok        $first_ip:$DB_PORT (database reachable)')\"" \
    || die "the planning tier cannot reach the database at $first_ip:$DB_PORT"
fi
as_runner "docker network rm factory-probe >/dev/null"

if [[ $TIER == ci ]]; then
  # One disposable runner per job, not registered runners: setup-ci.sh does the rest.
  # shellcheck source=setup-ci.sh
  source "$SCRIPT_DIR/setup-ci.sh"
  log "done"
  exit 0
fi

log "7/8 GitHub Actions runner v$RUNNER_VERSION x $RUNNER_COUNT"
# The runner's libraries (actions/runner v$RUNNER_VERSION, layoutbin/installdependencies.sh's Debian list), from
# apt as root. Root never runs a file the runner user can write, and the runner's own installdependencies.sh
# lives in its directory. A group is satisfied by any installed member, else by the first apt knows.
runner_deps() {
  local group pkg pick picks=()
  for group in "libkrb5-3" "zlib1g" "liblttng-ust1t64 liblttng-ust1 liblttng-ust0" "libssl3t64 libssl3 libssl1.1" \
               "libicu80 libicu79 libicu78 libicu77 libicu76 libicu75 libicu74 libicu73 libicu72 libicu71 libicu70 libicu69 libicu68 libicu67 libicu66"; do
    pick=
    for pkg in $group; do
      if dpkg-query -W -f '${Status}' "$pkg" 2>/dev/null | grep -q 'install ok installed'; then continue 2; fi
    done
    ((${#picks[@]})) || apt-get update -qq
    for pkg in $group; do apt-cache show "$pkg" > /dev/null 2>&1 && { pick=$pkg; break; }; done
    [[ -n $pick ]] || die "apt has no package for the runner's dependency ($group)"
    picks+=("$pick")
  done
  ((${#picks[@]})) || return 0
  # The picks aren't installed (that's why they're picked), but apt could still upgrade an installed library they
  # need, and a library upgrade can restart this host's other services. Simulated first, so any upgrade is the
  # operator's.
  local upgrades
  # An upgrade's line names the installed version in brackets straight after the package (every line has an
  # architecture in brackets later): "Inst libfoo1 [1.2-2] (1.2-3 ...)".
  upgrades=$(apt-get install -s -y --no-install-recommends "${picks[@]}" | awk '/^Inst / && $3 ~ /^\[/ {print $2}' \
    | tr '\n' ' ') || die "apt couldn't plan installing the runner's libraries (${picks[*]})"
  [[ -z $upgrades ]] \
    || die "installing the runner's libraries (${picks[*]}) would upgrade ${upgrades% }: upgrade those when it suits this host, then run setup again"
  apt-get install -y --no-install-recommends "${picks[@]}"
}
runner_deps
token=
if [[ -s $TOKEN_FILE ]]; then token=$(<"$TOKEN_FILE"); fi
for i in $(seq "$RUNNER_COUNT"); do
  dir=$(runner_dir "$i"); work=$(runner_work "$i"); name=$(runner_name "$i")
  if [[ ! -x $dir/config.sh ]]; then
    as_runner "mkdir -p '$dir' '$work' && cd '$dir' \
      && curl -fsSL -o runner.tgz https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-linux-x64-$RUNNER_VERSION.tar.gz \
      && echo '$RUNNER_SHA256  runner.tgz' | sha256sum -c - && tar xzf runner.tgz && rm runner.tgz"
  fi
  if [[ ! -f $dir/.runner ]]; then
    if [[ -n $token ]]; then
      as_runner "cd '$dir' && ./config.sh --unattended --replace \
        --url '$RUNNER_URL' --token '$token' --runnergroup '$RUNNER_GROUP' \
        --name '$name' --labels '$RUNNER_LABELS' --work '$work' --disableupdate"
    else
      echo "No registration token at $TOKEN_FILE: runner $i installed but NOT registered. Re-run with the token file."
    fi
  fi
  # Never self-update: runners stay at RUNNER_VERSION, whose checksum this script verifies; z-sdlc bumps it
  # within 30 days of each actions/runner release (GitHub stops sending jobs to older runners), and a run of
  # this setup installs it. A runner registered before this setting gets it in its settings file.
  if [[ -f $dir/.runner ]]; then
    as_runner "python3 -I -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p, encoding=\"utf-8-sig\")); d[\"disableUpdate\"]=True; json.dump(d, open(p, \"w\"), indent=2)' '$dir/.runner'"
  fi
  # Runner environment: talk to the rootless daemon; refuse any job without a container (F4).
  as_runner "cd '$dir' && touch .env && sed -i '/^\(DOCKER_HOST\|XDG_RUNTIME_DIR\|ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER\)=/d' .env \
    && printf '%s\n' 'DOCKER_HOST=unix:///run/user/$RUID/docker.sock' 'XDG_RUNTIME_DIR=/run/user/$RUID' 'ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER=true' >> .env \
    && cp -f bin/runsvc.sh ./runsvc.sh && chmod 755 runsvc.sh"
done
rm -f "$TOKEN_FILE"

log "8/8 systemd services $RUNNER_UNIT@1..$RUNNER_COUNT"
# One template; the instance number picks the runner directory.
cat > "/etc/systemd/system/$RUNNER_UNIT@.service" <<EOF
[Unit]
Description=GitHub Actions runner %i for the factory ($TIER tier)
Requires=$FW_UNIT.service user@$RUID.service
After=network-online.target $FW_UNIT.service user@$RUID.service
Wants=network-online.target

[Service]
User=$RUNNER_USER
WorkingDirectory=$RUNNER_HOME/actions-runner-%i
ExecStart=$RUNNER_HOME/actions-runner-%i/runsvc.sh
Environment=XDG_RUNTIME_DIR=/run/user/$RUID
NoNewPrivileges=yes
PrivateTmp=yes
MemoryMax=2G
TasksMax=512
KillMode=process
KillSignal=SIGTERM
TimeoutStopSec=5min

[Install]
WantedBy=multi-user.target
EOF
# The first organization's strict runner 1 lives in the original directory: point the template's path at it.
if legacy_first 1 && [[ ! -e $RUNNER_HOME/actions-runner-1 ]]; then ln -s actions-runner "$RUNNER_HOME/actions-runner-1"; fi
# An earlier version's single-runner unit is replaced by factory-runner@1, unless it is running a job:
# then it is left alone this time (the other instances still start) and a later run migrates it.
keep_old=
if legacy_first 1 && [[ -f /etc/systemd/system/factory-runner.service ]]; then
  if pgrep -u "$RUNNER_USER" -f "$(runner_dir 1)/bin/Runner.Worker" >/dev/null; then
    keep_old=1
    echo "The old factory-runner.service is running a job: left as runner 1 for now. Re-run setup when it is idle."
  else
    systemctl disable --now factory-runner.service >/dev/null 2>&1 || true
    rm -f /etc/systemd/system/factory-runner.service
  fi
fi
systemctl daemon-reload
for i in $(seq "$RUNNER_COUNT"); do
  dir=$(runner_dir "$i")
  if ((i == 1)) && [[ -n $keep_old ]]; then continue; fi
  if [[ ! -f $dir/.runner ]]; then
    echo "$RUNNER_UNIT@$i written but not started (runner $i not registered yet)."
    continue
  fi
  systemctl enable "$RUNNER_UNIT@$i.service" >/dev/null
  # Restart picks up unit edits, but never kill a running job (a cancelled job posts no comment).
  if pgrep -u "$RUNNER_USER" -f "$dir/bin/Runner.Worker" >/dev/null; then
    echo "Runner $i is running a job: $RUNNER_UNIT@$i NOT restarted. Re-run setup when idle."
  else
    systemctl restart "$RUNNER_UNIT@$i.service"
  fi
done
systemctl --no-pager --lines=0 status "$RUNNER_UNIT@*" | grep -E '●|Active:' || true

log "done"
nft list table inet "$NFT_TABLE" | grep counter || true
echo "Enforced limits (kernel):"
for f in memory.high memory.max cpu.max pids.max; do
  printf '  user-%s.slice %-12s %s\n' "$RUID" "$f" "$(cat "/sys/fs/cgroup/user.slice/user-$RUID.slice/$f" 2>/dev/null || echo n/a)"
done
for i in $(seq "$RUNNER_COUNT"); do
  for f in memory.max pids.max; do
    printf '  %s@%s %-12s %s\n' "$RUNNER_UNIT" "$i" "$f" \
      "$(cat "/sys/fs/cgroup/system.slice/system-${RUNNER_UNIT//-/\\x2d}.slice/$RUNNER_UNIT@$i.service/$f" 2>/dev/null || echo n/a)"
  done
done
