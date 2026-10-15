#!/usr/bin/env bash
# Start a throwaway Postgres 16 for a stage that runs the test suite, on the job container's loopback
# (127.0.0.1:5432), plus a Unix socket under <dir> for this script. Sandboxed Bash reaches the port
# through with-test-services, which forwards it over the sandbox's HTTP proxy (the sandbox blocks
# Unix sockets and has a loopback of its own).
# Run as root before the agent starts (copied out of the workspace first, like every check);
# the server runs as its own user. Prints the settings, for the project's env file (agent_job.sh
# services). ASP.NET Core reads no env file: a project whose default connection string names
# <database> as its database and user (password ignored: trust) reaches this one unchanged.
# The server runs outside the sandbox with open network access, so the agent must not be able to
# make it run code: the only login is the project's (<database>, also its role), which can create
# databases but isn't a superuser (a superuser can run shell commands with COPY ... TO PROGRAM). It
# starts with an empty environment, so it never holds the step's tokens. The script checks all of this
# before it returns. The data is disposable: no fsync, gone with the container.
# Usage: test-services.sh <socket-dir> <database>
set -euo pipefail

dir=$1 db=$2
[[ $db =~ ^[a-z_][a-z0-9_]*$ ]] || { echo "test-services: bad database name $db" >&2; exit 1; }
pgbin=/usr/lib/postgresql/16/bin
data=/var/lib/postgresql/factory
# The server process gets only these variables.
as() { local user=$1; shift; env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin LANG=C.UTF-8 runuser -u "$user" -- "$@"; }

install -d -m 755 "$dir"
install -d -m 755 -o postgres -g postgres "$dir/pg" "$data"
chmod 700 "$data"

as postgres "$pgbin/initdb" -D "$data" -U postgres --auth-local=peer --auth-host=reject > /dev/null
as postgres "$pgbin/pg_ctl" -D "$data" -l "$data/server.log" -w start \
  -o "-c listen_addresses=127.0.0.1 -c unix_socket_directories='$dir/pg' -c fsync=off -c full_page_writes=off" > /dev/null
# A test harness may create its own databases, so the role gets CREATEDB; no migration needs a superuser.
as postgres psql -q -h "$dir/pg" -U postgres -d postgres \
  -c "CREATE ROLE $db LOGIN CREATEDB" -c "CREATE DATABASE $db OWNER $db"
# From here on only the project's role can log in (trust: the socket is the boundary); postgres is refused.
printf 'local all %s trust\nhost all %s 127.0.0.1/32 trust\nlocal all all reject\nhost all all all reject\n' "$db" "$db" \
  > "$data/pg_hba.conf"
as postgres "$pgbin/pg_ctl" -D "$data" reload > /dev/null

# Fail closed if the lockdown didn't take.
fail() { echo "test-services: $1" >&2; exit 1; }
# The project's role: no superuser, no role creation, no membership (pg_execute_server_program and the file roles).
[ "$(psql -h "$dir/pg" -U "$db" -d "$db" -tAc "select rolsuper or rolcreaterole
     or exists (select 1 from pg_auth_members where member = oid) from pg_roles where rolname = current_user")" = f ] \
  || fail "$db has more than LOGIN and CREATEDB"
# Even as the postgres OS user (peer auth would admit it), the superuser login is refused.
! as postgres psql -h "$dir/pg" -U postgres -d postgres -tAc 'select 1' > /dev/null 2>&1 || fail "postgres login allowed"
! psql -h 127.0.0.1 -U postgres -d postgres -tAc 'select 1' > /dev/null 2>&1 || fail "postgres login allowed over TCP"
[ "$(psql -h 127.0.0.1 -U "$db" -d "$db" -tAc 'select 1')" = 1 ] || fail "$db can't log in over TCP"
# The server started under env -i is the postgres user's oldest process (the postmaster); every other
# server process is its fork, and Postgres blanks a child's environ when it sets the child's process
# title, so only this one can be read, and it's the one that matters. Read as the owning user:
# container root has no CAP_SYS_PTRACE, so it can't read another user's environ.
pid=$(pgrep -o -u postgres) || fail "no postgres process"
env_vars=$(runuser -u postgres -- cat "/proc/$pid/environ" | tr '\0' '\n') || fail "can't read postgres's environment"
printf '%s\n' "$env_vars" | grep -qx 'LANG=C.UTF-8' || fail "postgres process $pid has no readable environment"
if printf '%s\n' "$env_vars" | grep -vE '^(PATH|LANG|HOME|SHELL|USER|LOGNAME|PWD|PG[A-Z_]*|LC_[A-Z]*)=|^$' > /dev/null; then
  fail "the postgres server holds variables it was not given"
fi

# Quoted, so a shell can source the file too.
cat <<ENV
ConnectionStrings__DefaultConnection='Host=127.0.0.1;Port=5432;Database=$db;Username=$db;Password=unused-trust-auth'
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=$db
POSTGRES_USER=$db
ENV
