"""Save a planning run's work when it stops, and restore it when CD's reply restarts it (factory-plan.yml).

Usage:
  python3 -I resume_state.py find-session <stamp> <checks-dir> <projects-dir>
      Prints the main session file an agent step wrote since <stamp> (a fresh session under HOME's
      projects directory; a resumed one beside the file it resumed from, in <checks-dir>), or nothing.
  python3 -I resume_state.py save <out-dir> <base>
      In the agent's repository, after git_guard.sh: writes <out-dir>/work.json, and work.bundle (the
      commits since <base>) and work.patch (uncommitted changes, new files included, ignored ones not)
      when there are any. Prints saved=yes|no.
  python3 -I resume_state.py restore <state-dir> <stage> <main-sha>
      In a fresh checkout of main with full history: checks the saved work and, if every path is one the
      stage may write, checks out the saved commits and applies the patch, then lays main's agent
      configuration over the tree (hidden from git, as revise does). Prints restored=yes|no, base=<sha>
      (the saved base, or main) and why=<reason> when it refuses. A refusal is not an error: the run
      continues from main, as it did before work was saved.

A run that stops for CD (a question, the discovery check-in, its time budget) used to resume its session
but not its working tree, and a run killed at its time limit kept nothing it could resume (handoff § work
survives no stop). What it restores is checked the way the publish guard checks a planning stage's
commits: a straight line on the base, only the paths the stage may write (docs/ and the SDLC hygiene
files), nothing CODEOWNERS owns and no agent configuration, no symlinks or submodules. The resumed job
loads the project's settings from this tree, so a path it can't vouch for means nothing is restored.
"""

import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import implement_guard as guard  # noqa: E402

SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_PATCH_BYTES = 2_000_000
CONFIG = (".claude", "CLAUDE.md", "CLAUDE.local.md", ".mcp.json", ".github/CODEOWNERS")
# What the job writes into the workspace for itself (gitignored there too).
SKIP = (".factory/",)


class Refused(Exception):
    pass


def git(*args, binary=False, check=True, data=None):
    # No background maintenance: a fetch or commit may start a detached gc that outlives this script.
    out = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
                          "-c", "diff.ignoreSubmodules=all", "-c", "gc.auto=0", "-c", "maintenance.auto=false",
                          *args], capture_output=True, input=data)
    if check and out.returncode:
        raise Refused(f"git {args[0]}: {out.stderr.decode(errors='replace').strip()[:300]}")
    return out.stdout if binary else out.stdout.decode(errors="replace")


def find_session(stamp, checks, projects):
    """The top-level session file written since the step began; subagents' live in <session>/subagents/."""
    since = os.stat(stamp).st_mtime
    candidates = []
    for root, depth in ((pathlib.Path(checks), 0), (pathlib.Path(projects), 1)):
        pattern = "*.jsonl" if depth == 0 else "*/*.jsonl"
        for f in root.glob(pattern) if root.is_dir() else []:
            if f.name != "session.jsonl" and f.is_file() and f.stat().st_mtime >= since:
                candidates.append(f)
    return max(candidates, key=lambda f: (f.stat().st_size, f.stat().st_mtime)) if candidates else None


def save(out, base):
    if not SHA.match(base):
        raise Refused("bad base")
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    head = git("rev-parse", "HEAD").strip()
    commits = int(git("rev-list", "--count", f"{base}..HEAD").strip())
    if commits:
        git("bundle", "create", "-q", str(out / "work.bundle"), f"{base}..HEAD")
    # Uncommitted work, new files included: stage everything (ignored files stay out), diff, unstage.
    git("add", "-A")
    git("reset", "-q", "--", *SKIP, check=False)
    patch = git("diff", "--cached", "--binary", "--no-renames", "HEAD", binary=True)
    git("reset", "-q")
    if len(patch) > MAX_PATCH_BYTES:
        raise Refused(f"uncommitted changes are {len(patch)} bytes (cap {MAX_PATCH_BYTES})")
    if patch:
        (out / "work.patch").write_bytes(patch)
    (out / "work.json").write_text(json.dumps({"base": base, "head": head, "commits": commits, "patch": bool(patch)}))
    return bool(commits or patch)


def allowed(path, stage, patterns):
    if not path or path.startswith("/") or {".", ".."} & set(path.split("/")):
        return False
    if guard.agent_config(path) or guard.protected(path, patterns):
        return False
    if stage in guard.DOC_STAGES:
        return path.startswith(guard.DOC_STAGE_PATHS)
    return True


def patch_paths(patch_file):
    """Every path the patch touches, and whether it adds or changes a symlink or submodule. Saved patches
    carry no renames (save uses --no-renames), so each entry names one path."""
    names = []
    for entry in git("apply", "--numstat", "-z", str(patch_file)).split("\0"):
        if not entry:
            continue
        fields = entry.split("\t", 2)
        if len(fields) != 3 or not fields[2]:
            raise Refused("the saved changes can't be read")
        names.append(fields[2])
    text = pathlib.Path(patch_file).read_bytes().decode(errors="replace")
    special = re.search(r"^(?:new file mode|deleted file mode|old mode|new mode|index [0-9a-f]+\.\.[0-9a-f]+) 1[26]0000$",
                        text, re.M)
    return names, bool(special)


def check(state, stage, main, patterns):
    """The saved work's base, head and patch file, if the stage may have all of it."""
    meta = json.loads((state / "work.json").read_text())
    base, head = meta.get("base", ""), meta.get("head", "")
    if not SHA.match(str(base)) or not SHA.match(str(head)):
        raise Refused("the saved state names no valid commits")
    if git("cat-file", "-t", base, check=False).strip() != "commit":
        raise Refused("the saved base isn't in this repository")
    if subprocess.run(["git", "merge-base", "--is-ancestor", base, main]).returncode:
        raise Refused("the saved base isn't on main")
    bundle = state / "work.bundle"
    if meta.get("commits"):
        if not bundle.is_file():
            raise Refused("the saved commits are missing")
        git("bundle", "verify", "-q", str(bundle))
        git("fetch", "-q", "--no-tags", str(bundle), "+HEAD:refs/factory/resume")
        if git("rev-parse", "refs/factory/resume").strip() != head:
            raise Refused("the saved commits don't end at the saved head")
        if git("rev-list", "--merges", f"{base}..{head}").strip():
            raise Refused("the saved commits include a merge")
        if subprocess.run(["git", "merge-base", "--is-ancestor", base, head]).returncode:
            raise Refused("the saved commits aren't on the saved base")
        if int(git("rev-list", "--count", f"{base}..{head}")) > guard.MAX_COMMITS:
            raise Refused("too many saved commits")
        changed = git("diff", "--name-only", "--no-renames", "-z", base, head).split("\0")
        modes = git("diff", "--raw", "--no-renames", base, head)
        if re.search(r"^:\d{6} 1[26]0000 ", modes, re.M):
            raise Refused("the saved commits add a symlink or submodule")
        bad = [p for p in changed if p and not allowed(p, stage, patterns)]
        if bad:
            raise Refused(f"the saved commits change {bad[0]}, which the {stage} stage may not")
    elif base != head:
        raise Refused("the saved state has no commits but a different head")
    patch = state / "work.patch"
    if meta.get("patch"):
        if not patch.is_file() or patch.stat().st_size > MAX_PATCH_BYTES:
            raise Refused("the saved changes are missing or too large")
        paths, special = patch_paths(patch)
        if special:
            raise Refused("the saved changes add a symlink or submodule")
        bad = [p for p in paths if not allowed(p, stage, patterns)]
        if bad:
            raise Refused(f"the saved changes touch {bad[0]}, which the {stage} stage may not")
    return base, head, patch if meta.get("patch") else None


def restore(state, stage, main):
    state = pathlib.Path(state)
    if not (state / "work.json").is_file():
        return {"restored": "no", "base": main, "why": "no saved work"}
    patterns = guard.codeowners_patterns(pathlib.Path(".github/CODEOWNERS").read_text())
    try:
        base, head, patch = check(state, stage, main, patterns)
    except (Refused, ValueError, OSError) as e:
        return {"restored": "no", "base": main, "why": str(e)}
    git("checkout", "-q", "--detach", head)
    if patch:
        git("apply", "--whitespace=nowarn", str(patch))
    # main's agent configuration (skills, agents, settings, CLAUDE.md) and CODEOWNERS over the older tree,
    # hidden from git so none of it can be committed: the run gets current skills and path rules.
    tracked = [p for p in git("ls-files", "-z", "--", *CONFIG).split("\0") if p]
    if tracked:
        git("update-index", "--skip-worktree", "--", *tracked)
    names = [n for n in git("ls-tree", "--name-only", main, "--", *CONFIG).split("\n") if n]
    if names:
        archive = git("archive", main, "--", *names, binary=True)
        subprocess.run(["tar", "-x"], input=archive, check=True)
    others = git("ls-files", "--others", "--exclude-standard", "--", *CONFIG)
    if others.strip():
        with open(".git/info/exclude", "a") as f:
            f.write(others if others.endswith("\n") else others + "\n")
    return {"restored": "yes", "base": base, "commits": git("rev-list", "--count", f"{base}..HEAD").strip(),
            "patch": "yes" if patch else "no"}


def main():
    cmd = sys.argv[1]
    if cmd == "find-session":
        found = find_session(*sys.argv[2:5])
        print(found or "")
        return 0
    if cmd == "save":
        try:
            print(f"saved={'yes' if save(sys.argv[2], sys.argv[3]) else 'no'}")
        except Refused as e:
            print(f"::warning::the work tree wasn't saved: {e}", file=sys.stderr)
            print("saved=no")
        return 0
    if cmd == "restore":
        result = restore(sys.argv[2], sys.argv[3], sys.argv[4])
        for key, value in result.items():
            print(f"{key}={' '.join(str(value).split())}")
        return 0
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    sys.exit(main())
