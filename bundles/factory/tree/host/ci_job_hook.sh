#!/usr/bin/env bash
# The CI tier's job hooks (z-sdlc process/factory.md, Enablement step 10, The CI tier): nothing a job writes
# reaches the next job on the same runner. A job's containers get the runner's whole work directory
# read-write, and a pull request's job can be hostile.
#   started    the runner's ACTIONS_RUNNER_HOOK_JOB_STARTED: after the runner has downloaded the job's
#              actions and before it creates its containers (actions/runner v2.338.0, JobExtension.cs).
#   completed  ACTIONS_RUNNER_HOOK_JOB_COMPLETED: the job's last post step, after its containers stopped.
#   reset      as root, the runner unit's ExecStartPre: the whole work directory, on every runner start.
# The runner itself deletes _actions at every job start (ActionManager.cs) and recreates _temp
# (JobExtension.cs, InitializeTempDirectory). What persists is _tool (the setup-* actions' tool cache), the
# workspaces, and _PipelineMapping, which the runner reads at the next job's start, before any hook, to
# place that job's workspace (PipelineDirectoryManager.cs joins its paths to _work unchecked). So:
#   started    deletes _tool and what every workspace holds, keeping the <repo>/<repo> directories the
#              runner made for this job and points the container's working directory at;
#   completed  deletes those and _PipelineMapping, before the next job's start can read it.
#   reset      everything, for a run whose completed hook never ran.
# A container wrote some files as subordinate IDs, which the runner user can't delete itself: the hooks
# delete in the rootless daemon's user namespace, where it is root.
# Usage (from the root-owned per-instance hooks and unit setup.sh writes; never from the job's environment,
# which a hook runs with): ci_job_hook.sh <started|completed> <work directory> <rootless daemon pid file>
#                          ci_job_hook.sh reset <work directory>
set -euo pipefail

mode=${1:-} work=${2:-} pidfile=${3:-}
fail() { echo "CI tier job hook: $*" >&2; exit 1; }
case $mode in started|completed|reset) ;; *) fail "mode must be started, completed or reset" ;; esac
[[ $work =~ ^/[A-Za-z0-9._/-]+/factory-ci[a-z0-9-]*/_work-[0-9]+$ && $work != *..* && ! -L $work ]] \
  || fail "bad work directory $work"
if [[ $mode == reset ]]; then
  ((EUID == 0)) || fail "reset runs as root"
  rm -rf --one-file-system -- "$work"
  exit 0
fi
[[ -d $work ]] || exit 0

targets=()
shopt -s nullglob dotglob
for entry in "$work"/*; do
  case ${entry##*/} in
    _actions|_temp) continue ;;
    _PipelineMapping) [[ $mode == completed ]] && targets+=("$entry"); continue ;;
    _tool) targets+=("$entry"); continue ;;
  esac
  if [[ $mode == completed || -L $entry || ! -d $entry ]]; then
    targets+=("$entry")
    continue
  fi
  for child in "$entry"/*; do
    if [[ -d $child && ! -L $child ]]; then targets+=("$child"/*); else targets+=("$child"); fi
  done
done
((${#targets[@]})) || exit 0
[[ -r $pidfile ]] || fail "no rootless daemon pid file at $pidfile"
pid=$(<"$pidfile")
[[ $pid =~ ^[0-9]+$ ]] || fail "no pid in $pidfile"
nsenter -U --preserve-credentials -m -t "$pid" -- rm -rf --one-file-system -- "${targets[@]}" \
  || fail "couldn't delete what the last job left in $work"
echo "CI tier job hook ($mode): deleted ${#targets[@]} entries of $work"
