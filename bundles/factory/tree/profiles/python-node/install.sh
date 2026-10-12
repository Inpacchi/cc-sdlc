#!/usr/bin/env bash
# python-node profile: install the project's dependencies before the agent runs, outside the sandbox
# (implement's sandbox has no network at all). Run by agent_job.sh workspace from the frozen copy, in
# the workspace, after the test services start and after any secret is out of the environment: this
# runs the project's dependency manifests.
# Usage: install.sh <python-dir> <node-dir>
#   <python-dir>/requirements.txt is pip-installed; <node-dir> gets `npm ci`.
set -euo pipefail

python_dir=$1 node_dir=$2
pip install --quiet --no-cache-dir --root-user-action=ignore -r "$python_dir/requirements.txt"
(cd "$node_dir" && npm ci --no-audit --no-fund --loglevel=error)
# HOME is unreadable in the sandbox: npm's cache and user config live in the workspace.
touch .factory/npmrc
{
  echo "npm_config_cache=$GITHUB_WORKSPACE/.factory/npm-cache"
  echo "npm_config_userconfig=$GITHUB_WORKSPACE/.factory/npmrc"
} >> "$GITHUB_ENV"
