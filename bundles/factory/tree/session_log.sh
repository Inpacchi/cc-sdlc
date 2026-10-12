#!/usr/bin/env bash
# Keeps the record of an agent step that ended without a result. The time limit, the turn limit, a
# crash or a kill leave no execution file, so the transcripts the runtime wrote are all there is.
# Usage: session_log.sh STAMP OUT LIMIT [EXEC]
#   STAMP  a file touched just before the agent step; transcripts written since then are kept
#   OUT    the directory to copy them into (the caller uploads it when this prints saved=yes)
#   LIMIT  the agent step's timeout-minutes
#   EXEC   the step's execution file, when it left one
# Prints why=<a phrase for CD> and saved=yes|no, for $GITHUB_OUTPUT. A fresh session is written under
# HOME's projects directory; a resumed one continues beside the file it resumed from, in CHECKS.
# Subagents' transcripts sit in <session>/subagents/. OAUTH and GHTOKEN, when set, must not appear in
# what is kept.
set -uo pipefail
stamp=$1 out=$2 limit=$3 exec_file=${4:-}
start=$(stat -c %Y "$stamp" 2> /dev/null || date +%s)
mins=$(( ($(date +%s) - start) / 60 ))
if [ $((limit % 60)) -eq 0 ]; then span="$((limit / 60))-hour"; else span="$limit-minute"; fi
if [ -n "$exec_file" ] && [ -s "$exec_file" ]; then
  end=$(jq -r '[.[] | select(.type == "result")] | last | .subtype // "no result"' "$exec_file" 2> /dev/null || echo "no result")
  why="ended after $mins minutes without a usable result ($end)"
elif [ "$mins" -ge $((limit - 1)) ]; then
  why="stopped at the $span limit after $mins minutes with no result"
else
  why="stopped after $mins minutes with no result and no record of why (plan usage, a crash or a cancel)"
fi

install -d -m 700 "$out"
n=0
while IFS= read -r -d '' f; do
  dest="$out/${f#/}"
  install -d -m 700 "$(dirname "$dest")" && cp "$f" "$dest" && n=$((n + 1))
done < <(find /github/home/.claude/projects "${CHECKS:-/nonexistent}" -type f -name '*.jsonl' -newer "$stamp" -print0 2> /dev/null)
for v in "${OAUTH:-}" "${GHTOKEN:-}"; do
  if [ "$n" -gt 0 ] && [ -n "$v" ] && grep -rqF -- "$v" "$out"; then
    rm -rf "$out"; n=0; why="$why; its transcripts held a token and were not kept"
  fi
done

echo "why=$why"
if [ "$n" -gt 0 ]; then echo "saved=yes"; else echo "saved=no"; fi
