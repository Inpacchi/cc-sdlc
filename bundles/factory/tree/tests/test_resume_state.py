"""Tests for resume_state.py: a planning run's work is saved when it stops and restored on the restart, and
nothing a planning stage couldn't publish is ever restored into the tree the next run loads settings from."""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = FACTORY / "resume_state.py"
sys.path.insert(0, str(FACTORY))

import resume_state as rs  # noqa: E402

# The usual shape: owned paths listed, owner-less lines last to unown the hygiene files.
CODEOWNERS = """/.github/ @cd
/.claude/ @cd
/CLAUDE.md @cd
/api/requirements.txt @cd
/ops/sdlc/ @cd
/ops/sdlc/disciplines/*.md
/ops/sdlc/knowledge/**/*.yaml
/ops/sdlc/knowledge/agent-context-map.yaml @cd
/ops/sdlc/process/sdlc_changelog.md
"""


def git(*args, cwd, check=True):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@e", "-c", "gc.auto=0", "-c", "maintenance.auto=false",
                           *args], cwd=cwd, check=check,
                          capture_output=True, text=True).stdout.strip()


def write(root, path, text):
    f = root / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)


def run(*args, cwd):
    out = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
    return dict(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = pathlib.Path(self.tmp.name)
        self.src = self.root / "src"
        self.src.mkdir()
        git("init", "-q", "-b", "main", cwd=self.src)
        write(self.src, ".github/CODEOWNERS", CODEOWNERS)
        write(self.src, ".claude/skills/x/SKILL.md", "old skill\n")
        write(self.src, "CLAUDE.md", "old\n")
        write(self.src, "docs/_index.md", "catalog\n")
        write(self.src, "api/app.py", "code\n")
        write(self.src, ".gitignore", ".factory/\n.env\n")
        git("add", "-A", cwd=self.src)
        git("commit", "-q", "-m", "base", cwd=self.src)
        self.base = git("rev-parse", "HEAD", cwd=self.src)
        # The first run's workspace.
        self.ws = self.root / "ws1"
        git("clone", "-q", "--no-local", str(self.src), str(self.ws), cwd=self.root)
        self.state = self.root / "state"

    def tearDown(self):
        self.tmp.cleanup()

    def work(self, commits=(), uncommitted=()):
        for path, text in commits:
            write(self.ws, path, text)
            git("add", "-A", cwd=self.ws)
            git("commit", "-q", "-m", f"add {path}", cwd=self.ws)
        for path, text in uncommitted:
            write(self.ws, path, text)

    def save(self):
        return run("save", str(self.state), self.base, cwd=self.ws)

    def fresh(self, main_moves=True):
        """The restart: main may have moved on (newer skills), a fresh full clone of it."""
        if main_moves:
            write(self.src, ".claude/skills/x/SKILL.md", "new skill\n")
            write(self.src, "api/app.py", "newer code\n")
            git("add", "-A", cwd=self.src)
            git("commit", "-q", "-m", "main moves", cwd=self.src)
        ws2 = self.root / "ws2"
        git("clone", "-q", "--no-local", str(self.src), str(ws2), cwd=self.root)
        return ws2, git("rev-parse", "HEAD", cwd=ws2)

    def restore(self, ws2, main, stage="spec"):
        return run("restore", str(self.state), stage, main, cwd=ws2)


class SaveAndRestore(Base):
    def test_round_trip(self):
        self.work(commits=[("docs/current_work/specs/d1_x_spec.md", "draft 1\n")],
                  uncommitted=[("docs/current_work/specs/d1_x_spec.md", "draft 2\n"),
                               ("ops/sdlc/disciplines/testing.md", "new entry\n"),
                               (".factory/issue-context.json", "{}"), ("api/.env", "SECRET=1\n")])
        self.assertEqual(self.save()["saved"], "yes")
        meta = json.loads((self.state / "work.json").read_text())
        self.assertEqual((meta["commits"], meta["patch"]), (1, True))
        patch = (self.state / "work.patch").read_text()
        self.assertNotIn(".factory", patch)
        self.assertNotIn("SECRET", patch)
        # The agent's own index is left as it was.
        self.assertEqual(git("diff", "--cached", "--name-only", cwd=self.ws), "")
        ws2, main = self.fresh()
        out = self.restore(ws2, main)
        self.assertEqual((out["restored"], out["base"], out["commits"], out["patch"]), ("yes", self.base, "1", "yes"))
        self.assertEqual((ws2 / "docs/current_work/specs/d1_x_spec.md").read_text(), "draft 2\n")
        self.assertEqual((ws2 / "ops/sdlc/disciplines/testing.md").read_text(), "new entry\n")
        # main's agent configuration is laid over the older tree and hidden from git.
        self.assertEqual((ws2 / ".claude/skills/x/SKILL.md").read_text(), "new skill\n")
        self.assertNotIn(".claude", git("status", "--porcelain", cwd=ws2))
        # The code is the saved base's, not main's: the restored commits sit on their own base.
        self.assertEqual((ws2 / "api/app.py").read_text(), "code\n")

    def test_nothing_to_save(self):
        self.assertEqual(self.save()["saved"], "no")
        ws2, main = self.fresh()
        self.assertEqual(self.restore(ws2, main)["restored"], "yes")
        self.assertEqual(git("rev-parse", "HEAD", cwd=ws2), self.base)

    def test_no_saved_state(self):
        ws2, main = self.fresh()
        out = self.restore(ws2, main)
        self.assertEqual((out["restored"], out["base"]), ("no", main))

    def test_find_session(self):
        checks, projects = self.root / "checks", self.root / "projects"
        (projects / "proj" / "abc" / "subagents").mkdir(parents=True)
        checks.mkdir()
        old = projects / "proj" / "old.jsonl"
        old.write_text("x")
        os.utime(old, (time.time() - 100, time.time() - 100))
        stamp = self.root / "stamp"
        stamp.write_text("")
        os.utime(stamp, (time.time() - 50, time.time() - 50))
        (checks / "session.jsonl").write_text("the file it resumed from")
        (projects / "proj" / "abc" / "subagents" / "agent-1.jsonl").write_text("subagent " * 100)
        main = projects / "proj" / "abc.jsonl"
        main.write_text("main session " * 10)
        self.assertEqual(rs.find_session(stamp, checks, projects), main)
        resumed = checks / "abc.jsonl"
        resumed.write_text("resumed session " * 20)
        self.assertEqual(rs.find_session(stamp, checks, projects), resumed)
        self.assertIsNone(rs.find_session(stamp, self.root / "none", self.root / "none"))


class Refusals(Base):
    def refused(self, why, stage="spec", main_moves=True):
        ws2, main = self.fresh(main_moves)
        before = git("rev-parse", "HEAD", cwd=ws2)
        out = self.restore(ws2, main, stage)
        self.assertEqual(out["restored"], "no", out)
        self.assertIn(why, out["why"])
        self.assertEqual(out["base"], main)
        # A refusal leaves main checked out, untouched.
        self.assertEqual(git("rev-parse", "HEAD", cwd=ws2), before)
        self.assertEqual(git("status", "--porcelain", cwd=ws2), "")

    def test_agent_configuration_in_commits(self):
        self.work(commits=[("docs/a.md", "a\n"), (".claude/settings.json", "{}")])
        self.save()
        self.refused(".claude/settings.json")

    def test_owned_path_in_changes(self):
        self.work(uncommitted=[("ops/sdlc/knowledge/agent-context-map.yaml", "x: 1\n")])
        self.save()
        self.refused("agent-context-map.yaml")

    def test_code_in_a_planning_stage(self):
        self.work(uncommitted=[("api/app.py", "changed\n")])
        self.save()
        self.refused("api/app.py")

    def test_claude_md_anywhere(self):
        self.work(uncommitted=[("docs/sub/CLAUDE.md", "x\n")])
        self.save()
        self.refused("CLAUDE.md")

    def test_symlink(self):
        os.symlink("../api/app.py", self.ws / "docs" / "link.md")
        self.save()
        self.refused("symlink")

    def test_tampered_bundle(self):
        self.work(commits=[("docs/a.md", "a\n")])
        self.save()
        meta = json.loads((self.state / "work.json").read_text())
        meta["head"] = "0" * 40
        (self.state / "work.json").write_text(json.dumps(meta))
        self.refused("saved head")

    def test_base_not_on_main(self):
        self.work(commits=[("docs/a.md", "a\n")])
        self.save()
        meta = json.loads((self.state / "work.json").read_text())
        meta["base"] = meta["head"]  # a commit main doesn't have
        meta["commits"] = 0
        (self.state / "work.json").write_text(json.dumps(meta))
        self.refused("isn't in this repository")

    def test_merge_in_commits(self):
        git("checkout", "-q", "-b", "side", cwd=self.ws)
        self.work(commits=[("docs/side.md", "s\n")])
        git("checkout", "-q", "-", cwd=self.ws)
        self.work(commits=[("docs/a.md", "a\n")])
        git("merge", "-q", "--no-edit", "side", cwd=self.ws)
        self.save()
        self.refused("merge")

    def test_bad_metadata(self):
        self.state.mkdir()
        (self.state / "work.json").write_text('{"base": "x", "head": "y"}')
        self.refused("no valid commits")


if __name__ == "__main__":
    unittest.main()
