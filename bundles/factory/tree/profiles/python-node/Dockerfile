# Factory job image: the container every factory job runs in (F4).
# Tooling only; project dependencies are installed by the jobs that need them.
# Python and Node majors match api/Dockerfile and web/Dockerfile.
# Built and pushed to GHCR by .github/workflows/factory-image.yml.
FROM node:20-bookworm-slim AS node

FROM python:3.12-slim-bookworm

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# curl/unzip: the action installs Claude Code (install.sh) and Bun (zip) each run.
# bubblewrap/socat: Claude Code's Bash sandbox (process namespace and network proxy).
# postgresql-16 (PGDG; bookworm ships 15) and redis-server (7.0): throwaway test services for
# stages that run the test suite, matching CI's postgres:16 and redis:7. test-services.sh starts
# them on the job container's loopback; their apt postinstall clusters and init scripts are never used.
# pgbouncer: the planning tier's database proxy (design rule D3). It holds the read-only login's
# password where the agent can't read it and serves the agent's connections on loopback.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash bubblewrap ca-certificates curl git gnupg jq netcat-openbsd openssh-client procps socat unzip \
 && install -d -m 755 /etc/apt/keyrings \
 && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
 && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      | gpg --dearmor -o /etc/apt/keyrings/postgresql.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends gh postgresql-16 redis-server pgbouncer \
 && rm -rf /var/lib/apt/lists/*

# Redis must carry the 2025 Lua fixes (CVE-2025-49844, -46817, -46818, -46819; DSA-6020-1): EVAL stays
# enabled for channels-redis. Debian backports them without changing 7.0.15, so compare the package.
RUN dpkg --compare-versions "$(dpkg-query -W -f '${Version}' redis-server)" ge '5:7.0.15-1~deb12u6' \
 || { echo "redis-server predates the Lua CVE fixes (DSA-6020-1)" >&2; exit 1; }

RUN node --version && npm --version && python3 --version && gh --version && jq --version \
 && bwrap --version && socat -V | head -2 \
 && /usr/lib/postgresql/16/bin/postgres --version && redis-server --version && pgbouncer --version
