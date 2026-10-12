#!/usr/bin/env bash
# Check the agent's repository before the job runs git in it again (D2 rule 4).
# Usage: git_guard.sh <hooks-hash-file>   (run in the workspace; the hash file was written before the agent)
#
# The agent could plant files that make a later git command run a program outside the sandbox: a
# redirected or borrowed repository, changed hooks, config keys that name a program (filters,
# fsmonitor, includes, a remote carrying a token), or a staged submodule whose own config git would
# run. Refuse all of them; exit 1 with a ::error:: line naming which. Copied out of the workspace
# before the agent runs, like every check. Tested in CI by tests/test_git_guard.py.
set -euo pipefail

hooks_hash=$1
fail() { echo "::error::$1"; exit 1; }

# Claude Code's sandbox protects these paths by mounting over them, which leaves an empty file behind
# when the path didn't exist. An empty one is that placeholder: remove it. Anything else is refused.
for p in .git/commondir .git/objects/info/alternates .git/objects/info/http-alternates \
         .git/config.worktree .git/config.worktree.lock; do
  if [ -L "$p" ]; then fail "$p is a symlink"
  elif [ -f "$p" ] && [ ! -s "$p" ]; then rm -f -- "$p"
  elif [ -d "$p" ] && [ -z "$(ls -A -- "$p")" ]; then rmdir -- "$p"
  fi
done

[ -d .git ] && [ ! -L .git ] || fail "the repository's .git is not a plain directory"
describe() { stat -c '%F, %s bytes, mode %a' -- "$1"; [ -f "$1" ] && head -c 200 -- "$1" | od -c | head -3 || true; }
# A commondir that names the repository itself ("" or ".") redirects nothing.
if [ -f .git/commondir ] && [ ! -L .git/commondir ] && [ "$(tr -d ' \n' < .git/commondir)" = "" -o "$(tr -d ' \n' < .git/commondir)" = . ]; then
  echo "git_guard: .git/commondir names the repository itself; removed it"
  rm -f -- .git/commondir
fi
[ ! -e .git/commondir ] || fail "the repository's .git points at another repository (commondir: $(describe .git/commondir))"
[ ! -e .git/objects/info/alternates ] && [ ! -e .git/objects/info/http-alternates ] \
  || fail "the repository borrows objects (alternates)"
# The sandbox creates config.worktree on Linux to protect it. Git reads it only with
# extensions.worktreeConfig set, which the key allowlist below refuses, so it is inert: log, remove.
for p in .git/config.worktree .git/config.worktree.lock; do
  if [ -L "$p" ]; then fail "$p is a symlink"; fi
  if [ -e "$p" ]; then echo "git_guard: removed $p ($(describe "$p" | tr '\n' ' '))"; rm -rf -- "$p"; fi
done
[ "$(find .git/hooks -type f -exec sha256sum {} + | sort)" = "$(cat "$hooks_hash")" ] \
  || fail "the repository's hooks changed"
[ "$(git -c core.hooksPath=/dev/null rev-parse --git-common-dir)" = .git ] \
  || fail "git resolves a different repository"
# The action edits .git/config during the agent step (user.name, user.email), so check its keys
# rather than its hash. --file only parses the file; it follows no include.
extra=$(git config --file .git/config --name-only --list | grep -vxE \
  'core\.(repositoryformatversion|filemode|bare|logallrefupdates|ignorecase|precomposeunicode|sparsecheckout)|user\.(name|email)|extensions\.objectformat|gc\.auto|branch\.[a-z0-9._/-]+\.(remote|merge)' || true)
[ -z "$extra" ] || fail "unexpected .git/config keys: $(echo $extra)"
[ -z "$(git -c core.hooksPath=/dev/null ls-files -s | awk '$1 == "160000"')" ] || fail "the index holds a submodule"
