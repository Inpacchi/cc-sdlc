#!/usr/bin/env bash
# Start the planning tier's database proxy (design rule D3): pgbouncer on the job container's
# loopback, holding the read-only factory_reader login's password, so the agent can query the
# production database without ever seeing the password. Run as root before the agent, with the
# password in FACTORY_DB_READER_PASSWORD (that step's env only). The config sits in a directory only
# the postgres user can read, under the runner temp directory the sandbox can't see.
# Usage: planning-services.sh <planning.json> <config-dir>
set -euo pipefail

cfg=$1
dir=$2
[ -n "${FACTORY_DB_READER_PASSWORD:-}" ] || { echo "planning-services: no database password" >&2; exit 1; }
host=$(jq -r .database.host "$cfg"); port=$(jq -r .database.port "$cfg"); name=$(jq -r .database.name "$cfg")
user=$(jq -r .database.user "$cfg"); local_port=$(jq -r .database.local_port "$cfg")

# A fresh directory each run: the runner's temp directory can outlive a job, and a stale pidfile or
# config from an earlier run would stop pgbouncer from starting (silently, before this fix).
rm -rf "$dir"
install -d -m 700 -o postgres -g postgres "$dir"
umask 077
cat > "$dir/pgbouncer.ini" <<INI
[databases]
$name = host=$host port=$port dbname=$name user=$user password=$FACTORY_DB_READER_PASSWORD

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = $local_port
unix_socket_dir =
auth_type = trust
auth_file = $dir/userlist.txt
pool_mode = session
max_client_conn = 20
default_pool_size = 4
ignore_startup_parameters = extra_float_digits,options
logfile = $dir/pgbouncer.log
pidfile = $dir/pgbouncer.pid
INI
printf '"%s" ""\n' "$user" > "$dir/userlist.txt"
chown postgres:postgres "$dir/pgbouncer.ini" "$dir/userlist.txt"
if ! env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin LANG=C.UTF-8 runuser -u postgres -- pgbouncer -d "$dir/pgbouncer.ini" > "$dir/start.log" 2>&1; then
  echo "planning-services: pgbouncer didn't start:" >&2
  # Its own messages only (no password: that's in the ini, which isn't printed).
  tail -20 "$dir/start.log" "$dir/pgbouncer.log" 2> /dev/null >&2 || true
  exit 1
fi

for _ in $(seq 50); do (exec 3<> "/dev/tcp/127.0.0.1/$local_port") 2> /dev/null && break; sleep 0.1; done
answer=$(psql -h 127.0.0.1 -p "$local_port" -U "$user" -d "$name" -tAc 'select 1' 2>&1) || true
if [ "$answer" != 1 ]; then
  echo "planning-services: the database proxy can't reach $host:$port ($answer)" >&2
  tail -20 "$dir/pgbouncer.log" 2> /dev/null >&2 || true
  exit 1
fi
echo "planning-services: $name at 127.0.0.1:$local_port (read-only, as $user)" >&2
