"""Tests for git_guard.sh: the checks factory-implement's Package step runs before it uses git on the
agent's repository. Each case booby-traps a fresh repository one way and expects a refusal."""

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

APP = json.loads((pathlib.Path(__file__).resolve().parents[1] / "factory.json").read_text())["app"]

GUARD = pathlib.Path(__file__).resolve().parents[1] / "git_guard.sh"


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class GitGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        # What the job has after checkout and its prepare step: a clone with origin removed.
        src = root / "src"
        src.mkdir()
        git("init", "-q", "-b", "main", cwd=src)
        (src / "a.txt").write_text("a\n")
        git("add", "-A", cwd=src)
        git("-c", "user.name=t", "-c", "user.email=t@e", "commit", "-q", "-m", "base", cwd=src)
        self.repo = root / "ws"
        git("clone", "-q", "--no-local", str(src), str(self.repo), cwd=root)
        git("remote", "remove", "origin", cwd=self.repo)
        self.hooks = root / "git-hooks.sha256"
        hashes = subprocess.run("find .git/hooks -type f -exec sha256sum {} + | sort", shell=True,
                                cwd=self.repo, check=True, capture_output=True, text=True).stdout
        self.hooks.write_text(hashes)
        # What the action does during the agent step.
        git("config", "user.name", APP["login"], cwd=self.repo)
        git("config", "user.email", f"{APP['user_id']}+{APP['login']}@users.noreply.github.com", cwd=self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def guard(self):
        return subprocess.run(["bash", str(GUARD), str(self.hooks)], cwd=self.repo, capture_output=True, text=True)

    def refused(self, why):
        out = self.guard()
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        self.assertIn(why, out.stdout)

    def test_accepts_a_normal_run(self):
        (self.repo / "b.txt").write_text("b\n")
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", "work", cwd=self.repo)
        out = self.guard()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_removes_the_sandbox_placeholders(self):
        # What the sandbox leaves behind: empty files at the protected paths that didn't exist.
        info = self.repo / ".git" / "objects" / "info"
        info.mkdir(parents=True, exist_ok=True)
        for p in [self.repo / ".git" / "commondir", info / "alternates", self.repo / ".git" / "config.worktree"]:
            p.write_text("")
        out = self.guard()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertFalse((self.repo / ".git" / "commondir").exists())

    def test_removes_an_inert_worktree_config(self):
        (self.repo / ".git" / "config.worktree").write_text("[core]\n\tfsmonitor = /tmp/p\n")
        out = self.guard()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertFalse((self.repo / ".git" / "config.worktree").exists())

    def test_refuses_the_worktree_config_extension(self):
        git("config", "extensions.worktreeConfig", "true", cwd=self.repo)
        self.refused("unexpected .git/config keys")

    def test_refuses_a_symlinked_git_dir(self):
        real = pathlib.Path(self.tmp.name) / "elsewhere.git"
        os.rename(self.repo / ".git", real)
        os.symlink(real, self.repo / ".git")
        self.refused("not a plain directory")

    def test_removes_a_commondir_naming_itself(self):
        (self.repo / ".git" / "commondir").write_text(".\n")
        out = self.guard()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_refuses_commondir(self):
        (self.repo / ".git" / "commondir").write_text("../elsewhere\n")
        self.refused("commondir")

    def test_refuses_alternates(self):
        (self.repo / ".git" / "objects" / "info").mkdir(parents=True, exist_ok=True)
        (self.repo / ".git" / "objects" / "info" / "alternates").write_text("/tmp/objects\n")
        self.refused("alternates")

    def test_refuses_a_new_hook(self):
        hook = self.repo / ".git" / "hooks" / "post-checkout"
        hook.write_text("#!/bin/sh\n")
        self.refused("hooks changed")

    def test_refuses_config_keys_that_run_programs(self):
        for key, value in [("filter.x.clean", "touch /tmp/p"), ("core.fsmonitor", "/tmp/p"),
                           ("include.path", "/tmp/c"), ("core.sshCommand", "/tmp/p"),
                           ("remote.origin.url", "https://x-access-token:t@github.com/o/r")]:
            with self.subTest(key=key):
                git("config", key, value, cwd=self.repo)
                self.refused("unexpected .git/config keys")
                git("config", "--unset", key, cwd=self.repo)

    def test_refuses_a_staged_submodule(self):
        sub = self.repo / "api" / "sub"
        git("init", "-q", "--separate-git-dir", str(self.repo / "api" / "evil"), str(sub), cwd=self.repo)
        (sub / "f").write_text("x\n")
        git("add", "-A", cwd=sub)
        git("-c", "user.name=t", "-c", "user.email=t@e", "commit", "-q", "-m", "s", cwd=sub)
        git("add", "api/sub", cwd=self.repo)
        self.refused("submodule")


if __name__ == "__main__":
    unittest.main()
