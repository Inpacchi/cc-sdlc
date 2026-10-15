# Factory job image: the container every factory job runs in (F4), for the dotnet-node profile.
# Tooling only; project dependencies are installed by the jobs that need them.
# The .NET 10 SDK (a project's global.json may roll forward to it) and Node 22 with pnpm 10.
# Built and pushed to GHCR by .github/workflows/factory-image.yml.
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS dotnet
FROM node:22-bookworm-slim AS node

# The factory's own steps are Python, and some call /usr/local/bin/python3 by path.
FROM python:3.12-slim-bookworm

# The SDK is portable (built against an old glibc), so it runs on bookworm with libicu72 below.
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet
RUN ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
# pnpm as a plain package, not corepack (which keeps its downloads under HOME). A project's
# packageManager pin may name another version: install.sh runs pnpm with network, so pnpm fetches it.
RUN npm install -g --no-audit --no-fund --loglevel=error pnpm@10.33.0

# curl/unzip: the action installs Claude Code (install.sh) and Bun (zip) each run.
# bubblewrap/socat: Claude Code's Bash sandbox (process namespace and network proxy).
# libicu72: .NET's globalization. postgresql-16 (PGDG; bookworm ships 15): the throwaway test
# database for stages that run the test suite. test-services.sh starts it on the job container's
# loopback; its apt postinstall cluster and init scripts are never used.
# pgbouncer: the planning tier's database proxy (design rule D3). It holds the read-only login's
# password where the agent can't read it and serves the agent's connections on loopback.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash bubblewrap ca-certificates curl git gnupg jq libicu72 netcat-openbsd openssh-client procps socat unzip \
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
 && apt-get install -y --no-install-recommends gh postgresql-16 pgbouncer \
 && rm -rf /var/lib/apt/lists/*

RUN DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 dotnet --list-sdks \
 && node --version && npm --version && pnpm --version && python3 --version && gh --version && jq --version \
 && bwrap --version && socat -V | head -2 \
 && /usr/lib/postgresql/16/bin/postgres --version && pgbouncer --version
