"""host/ci_job_hook.sh: what each mode deletes from a CI-tier runner's work directory, and what it refuses.
nsenter is a stand-in here (it runs its command); on the host it enters the rootless daemon's namespaces."""

import os
import pathlib
import subprocess
import tempfile
import unittest

HOOK = pathlib.Path(__file__).resolve().parents[1] / "host" / "ci_job_hook.sh"


class Hook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.work = root / "factory-ci" / "_work-1"
        for d in ("_actions/actions/checkout", "_temp/_github_home", "_PipelineMapping/acme/widget", "_tool/node/22",
                  "widget/widget/.git", "other/other"):
            (self.work / d).mkdir(parents=True)
        (self.work / "_PipelineMapping/acme/widget/PipelineFolder.json").write_text('{"PipelineDirectory": "../x"}')
        (self.work / ".hidden").write_text("x")
        self.pidfile = root / "docker.pid"
        self.pidfile.write_text("4242\n")
        bindir = root / "bin"
        bindir.mkdir()
        # Runs its command; drops GNU rm's --one-file-system where rm is BSD's (macOS), as the host's is GNU's.
        (bindir / "nsenter").write_text(
            '#!/usr/bin/env bash\nwhile [[ $1 != -- ]]; do shift; done; shift\n'
            'if ! rm --version > /dev/null 2>&1; then set -- "${@/--one-file-system/}"; args=(); '
            'for a in "$@"; do [[ -n $a ]] && args+=("$a"); done; set -- "${args[@]}"; fi\nexec "$@"\n')
        (bindir / "nsenter").chmod(0o755)
        self.env = {**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"}

    def tearDown(self):
        self.tmp.cleanup()

    def hook(self, *args):
        return subprocess.run(["bash", str(HOOK), *args], capture_output=True, text=True, env=self.env)

    def left(self):
        return sorted(p.name for p in self.work.iterdir())

    def test_started_keeps_what_the_runner_made_for_this_job(self):
        (self.work / "widget/stray-file").write_text("x")
        r = self.hook("started", str(self.work), str(self.pidfile))
        self.assertEqual(r.returncode, 0, r.stderr)
        # The runner deleted _actions and recreated _temp for this job, and has read _PipelineMapping already.
        # It made widget/widget for this job's workspace (the container's working directory): kept, emptied.
        self.assertEqual(self.left(), ["_PipelineMapping", "_actions", "_temp", "other", "widget"])
        self.assertEqual(sorted(p.name for p in (self.work / "widget").iterdir()), ["widget"])
        self.assertEqual(list((self.work / "widget/widget").iterdir()), [])
        self.assertEqual(list((self.work / "other/other").iterdir()), [])

    def test_completed_leaves_nothing_for_the_next_job_to_read(self):
        r = self.hook("completed", str(self.work), str(self.pidfile))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.left(), ["_actions", "_temp"])

    def test_bad_work_directories_are_refused(self):
        other = pathlib.Path(self.tmp.name) / "factory-runner" / "_work-1"
        other.mkdir(parents=True)
        link = pathlib.Path(self.tmp.name) / "factory-ci" / "_work-2"
        link.symlink_to(self.work)
        for work in (str(other), str(link), f"{self.work}/../_work-1", "relative/factory-ci/_work-1",
                     str(self.work.parent / "actions-runner-1")):
            with self.subTest(work=work):
                r = self.hook("completed", work, str(self.pidfile))
                self.assertEqual(r.returncode, 1)
                self.assertIn("bad work directory", r.stderr)
        self.assertIn("widget", self.left())

    def test_without_the_daemons_pid_nothing_is_deleted(self):
        r = self.hook("started", str(self.work), str(self.pidfile.parent / "missing.pid"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no rootless daemon pid file", r.stderr)
        self.assertIn("_tool", self.left())

    def test_reset_runs_as_root_only_and_an_unknown_mode_is_refused(self):
        if os.geteuid() != 0:
            r = self.hook("reset", str(self.work))
            self.assertEqual(r.returncode, 1)
            self.assertIn("reset runs as root", r.stderr)
        r = self.hook("wipe", str(self.work), str(self.pidfile))
        self.assertEqual(r.returncode, 1)
        self.assertIn("mode must be", r.stderr)


if __name__ == "__main__":
    unittest.main()
