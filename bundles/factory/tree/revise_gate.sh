#!/usr/bin/env bash
# The revise stages' gate (F15/F16): is this an open factory PR the requester may have revised, and is
# it under its revision limit? Run by the gate job of factory-revise.yml (code) and
# factory-revise-doc.yml (doc), on a GitHub-hosted runner, from the default branch.
# Usage: revise_gate.sh <code|doc>
# Environment: PR, REQUESTER, REVISION_LIMIT, RUN_URL, GH_REPO; GH_TOKEN (the job's read-only token)
# and APP_TOKEN (the App's issues token: the requester notice, the limit comment and the labels).
# Writes proceed=true and the PR's facts to $GITHUB_OUTPUT when the revision may run; proceed=false
# otherwise. Exits 1 when the PR isn't one this stage revises.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
# The factory App's bot user (factory.json, beside this script).
app_id=$(jq -r .app.user_id "$here/factory.json")
[[ $app_id =~ ^[0-9]+$ ]] || { echo "::error::factory.json has no app.user_id"; exit 1; }
kind=${1:-}
case "$kind" in
  code) pattern='^factory/([0-9]+)-impl$'; what="factory code PR" ;;
  doc) pattern='^factory/([0-9]+)-(spec|plan)$'; what="factory spec or plan PR" ;;
  *) echo "usage: revise_gate.sh code|doc" >&2; exit 2 ;;
esac

# REST issue endpoints: the App token is issues-only, and gh pr uses GraphQL, which needs more.
say() { GH_TOKEN="$APP_TOKEN" gh api "repos/$GH_REPO/issues/$PR/comments" -f body="$1 <sub>factory revise · [run]($RUN_URL)</sub>" > /dev/null; }
unlabel() { GH_TOKEN="$APP_TOKEN" gh api -X DELETE "repos/$GH_REPO/issues/$PR/labels/factory:revise" > /dev/null 2>&1 || true; }
echo "proceed=false" >> "$GITHUB_OUTPUT"
pr="$RUNNER_TEMP/pr.json"
gh api "repos/$GH_REPO/pulls/$PR" > "$pr"
head=$(jq -r .head.ref "$pr")
if [[ ! $head =~ $pattern ]] || [ "$(jq -r .state "$pr")" != open ] \
   || [ "$(jq -r .head.repo.full_name "$pr")" != "$GH_REPO" ] || [ "$(jq -r .user.id "$pr")" != "$app_id" ]; then
  echo "::error::PR #$PR isn't an open $what"; exit 1
fi
issue=${BASH_REMATCH[1]}
stage=${BASH_REMATCH[2]:-code}
perm=$(gh api "repos/$GH_REPO/collaborators/$REQUESTER/permission" --jq .permission 2> /dev/null || echo none)
case "$perm" in admin|maintain|write) ;; *) unlabel; say "Revisions need a reviewer with write access."; exit 0 ;; esac

if [ "$kind" = doc ]; then
  # The PR's document, and the planning skill that wrote it.
  # Doubled backslashes: the pattern lands inside a jq string literal.
  if [ "$stage" = spec ]; then docpattern='^docs/current_work/specs/d[0-9]+[a-z]?_[a-z0-9_]+_spec\\.md$'
  else docpattern='^docs/current_work/(sdlc-lite|planning)/d[0-9]+[a-z]?_[a-z0-9_]+_plan\\.md$'; fi
  docs=$(gh api "repos/$GH_REPO/pulls/$PR/files" --paginate --jq ".[] | select(.status != \"removed\") | .filename | select(test(\"$docpattern\"))")
  [ "$(grep -c . <<< "$docs")" = 1 ] || { echo "::error::PR #$PR doesn't add or change exactly one $stage document"; exit 1; }
  case "$docs" in
    docs/current_work/sdlc-lite/*) skill=sdlc-lite-plan ;;
    *) skill=sdlc-plan ;;
  esac
  deliverable=$(basename "$docs" | sed -E 's/^d([0-9]+[a-z]?)_.*/D\1/')
fi

# Earlier revisions: the App's factory-revise markers on the PR (matched by the App's user ID).
done_=$(gh api "repos/$GH_REPO/issues/$PR/comments" --paginate \
        --jq '[.[] | select(.user.type == "Bot" and .user.id == '"$app_id"' and (.body | test("\\A<!-- factory-revise: [0-9]+ -->")))] | length' \
        | awk '{s += $1} END {print s + 0}')
revision=$((done_ + 1))
if [ "$revision" -gt "$REVISION_LIMIT" ]; then
  unlabel
  if [ "$kind" = code ]; then
    say "**Revision limit reached** ($REVISION_LIMIT for a code PR): no more automatic revisions. Push the changes yourself, or close the PR and re-triage the issue."
  else
    say "**Revision limit reached** ($REVISION_LIMIT for a $stage PR): no more automatic revisions. A document that needs another round usually needs a conversation: continue in an interactive \`sdlc-plan\` session on \`$head\` (it can read this review), push the changes yourself, or close the PR to stop."
  fi
  GH_TOKEN="$APP_TOKEN" gh issue edit "$issue" --add-label factory:escalated > /dev/null
  exit 0
fi
{
  echo "issue=$issue"; echo "branch=$head"; echo "base=$(jq -r .head.sha "$pr")"; echo "revision=$revision"
  if [ "$kind" = doc ]; then
    echo "stage=$stage"; echo "document=$docs"; echo "deliverable=$deliverable"; echo "skill=$skill"
  fi
  echo "proceed=true"
} >> "$GITHUB_OUTPUT"
if [ "$kind" = code ]; then
  echo "Revision $revision of $REVISION_LIMIT for PR #$PR (issue #$issue)" >> "$GITHUB_STEP_SUMMARY"
else
  echo "Revision $revision of $REVISION_LIMIT for $stage PR #$PR (issue #$issue, $docs, /$skill)" >> "$GITHUB_STEP_SUMMARY"
fi
