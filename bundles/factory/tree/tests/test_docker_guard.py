"""host/docker_guard.py: the CI tier's runners reach docker only through it. The runner's own commands pass
(argv as actions/runner v2.338.0 builds them); everything a hostile job definition could add is refused."""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

GUARD = pathlib.Path(__file__).resolve().parents[1] / "host" / "docker_guard.py"
sys.path.insert(0, str(GUARD.parent))
import docker_guard as guard  # noqa: E402

NETWORK = "github_network_" + "a" * 32
IMAGE = "ghcr.io/acme/e2e@sha256:" + "c" * 64


class Guard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.runner = root / "factory-ci" / "actions-runner-1"
        self.work = root / "factory-ci" / "_work-1"
        for d in (self.runner / "externals", self.work / "_temp" / "_github_home", self.work / "_temp" / "_github_workflow",
                  self.work / "_actions", self.work / "_tool"):
            d.mkdir(parents=True)
        (self.runner / ".credentials").write_text("{}")
        self.conf = {"docker": "/usr/bin/docker", "host": "unix:///run/user/1001/docker.sock",
                     "work": str(self.work), "externals": str(self.runner / "externals")}

    def tearDown(self):
        self.tmp.cleanup()

    def create(self, *extra, image=IMAGE):
        """The runner's job-container create (DockerCommandManager.DockerCreate), with options inserted where the
        job's own `container.options` go."""
        w, e = str(self.work), str(self.runner / "externals")
        return ["create", "--name", "a1b2c3_ghcrioacmee2e_d4e5f6", "--label", "1f6f2a", "--workdir", "/__w/widget/widget",
                "--network", NETWORK, *extra, "-e", "HOME=/github/home", "-e", "GITHUB_ACTIONS=true", "-e", "CI=true",
                "-v", "/var/run/docker.sock:/var/run/docker.sock", "-v", f"{w}:/__w", "-v", f"{e}:/__e:ro",
                "-v", f"{w}/_temp:/__w/_temp", "-v", f"{w}/_actions:/__w/_actions", "-v", f"{w}/_tool:/__t",
                "-v", f"{w}/_temp/_github_home:/github/home", "-v", f"{w}/_temp/_github_workflow:/github/workflow",
                "--entrypoint", "tail", image, "-f", "/dev/null"]

    def refused(self, argv, why):
        with self.assertRaises(guard.Refused) as e:
            guard.check(argv, self.conf)
        self.assertIn(why, str(e.exception))

    def test_the_runners_job_container_passes_with_no_new_privileges(self):
        argv = self.create("--security-opt", "seccomp=/etc/factory-runner/seccomp-bwrap.json",
                           "--security-opt", "systempaths=unconfined")
        out, keep_env = guard.check(argv, self.conf)
        self.assertFalse(keep_env)
        self.assertEqual(out[:3], ["--host", "unix:///run/user/1001/docker.sock", "create"])
        at = out.index(IMAGE)
        self.assertEqual(out[at - 2:], ["--security-opt", "no-new-privileges", IMAGE, "-f", "/dev/null"])
        # Anything after the image is the container's command, as docker reads it.
        out, _ = guard.check(self.create(image=IMAGE)[:-2] + ["--privileged"], self.conf)
        self.assertEqual(out[-2:], [IMAGE, "--privileged"])

    def test_the_runners_other_commands_pass(self):
        temp = f"{self.work}/_temp/.docker_1234"
        for argv in (["version", "--format", "{{.Server.APIVersion}}"], ["pull", IMAGE], ["--config", temp, "pull", IMAGE],
                     ["--config", temp, "login", "ghcr.io", "-u", "acme-bot", "--password-stdin"],
                     ["--config", temp, "login", "-u", "acme-bot", "--password-stdin"],  # Docker Hub: no registry
                     ["network", "create", "--label", "1f6f2a", NETWORK], ["network", "rm", NETWORK],
                     ["network", "prune", "--force", "--filter", "label=1f6f2a"], ["start", "abc"], ["rm", "--force", "abc"],
                     ["logs", "--details", "abc"], ["inspect", "--format", "{{.State.Running}}", "abc"],
                     ["ps", "--all", "--filter", "label=1f6f2a", "--no-trunc", "--format", "{{.ID}}"]):
            with self.subTest(argv=argv):
                out, keep_env = guard.check(argv, self.conf)
                self.assertEqual(out[:2], ["--host", "unix:///run/user/1001/docker.sock"])
                self.assertFalse(keep_env)
        # A step: its environment reaches docker exec (`-e KEY` hands KEY's value to the step).
        out, keep_env = guard.check(["exec", "-i", "--workdir", "/__w/widget/widget", "-e", "GITHUB_TOKEN", "-e",
                                     "PATH=/x:/usr/bin", "abc", "sh", "-e", "/__w/_temp/1.sh"], self.conf)
        self.assertTrue(keep_env)
        self.assertEqual(out[-4:], ["abc", "sh", "-e", "/__w/_temp/1.sh"])

    def test_privilege_and_namespace_options(self):
        for extra, why in ((["--privileged"], "create option --privileged"), (["--cap-add", "SYS_ADMIN"], "--cap-add"),
                           (["--pid", "host"], "--pid"), (["--ipc", "host"], "--ipc"), (["--userns", "host"], "--userns"),
                           (["-p", "8080:80"], "create option -p"), (["--network", "host"], "only the runner's job network"),
                           (["--network", "container:abc"], "only the runner's job network"),
                           (["--security-opt", "seccomp=unconfined"], "security option seccomp=unconfined"),
                           (["--security-opt", "apparmor=unconfined"], "security option apparmor=unconfined"),
                           (["--security-opt", "systempaths=unconfined"], "only with the factory seccomp profile")):
            with self.subTest(extra=extra):
                self.refused(self.create(*extra), why)

    def test_mounts_other_than_the_runners_own(self):
        runner = str(self.runner)
        for extra, why in ((["-v", f"{runner}:/runner"], "not one of the runner's own directories"),
                           (["-v", "/etc:/x"], "not one of the runner's own directories"),
                           (["-v", "cache:/root/.cache"], "a named volume"), (["-v", "cache"], "a named volume"),
                           (["--mount", f"type=bind,src={runner},dst=/r"], "create option --mount"),
                           (["--volumes-from", "other-job"], "create option --volumes-from"),
                           (["-v", f"{self.runner / 'externals'}:/__e"], "externals only read-only"),
                           (["-v", f"{self.work}/_tool:/t:rw"], "not source:target[:ro]"),
                           (["-v", "/var/run/docker.sock:/sock"], "the socket only at"),
                           # Only the separate-token form the runner writes: never attached or `=`.
                           ([f"-v{self.work}:/__w"], f"create option -v{self.work}"),
                           ([f"--volume={self.work}:/__w"], "create option --volume="),
                           # Files read or written by the docker CLI as the runner user.
                           (["--env-file", f"{runner}/.credentials"], "create option --env-file"),
                           (["--cidfile", f"{runner}/.env"], "create option --cidfile"),
                           (["--label-file", f"{runner}/.credentials"], "create option --label-file")):
            with self.subTest(extra=extra):
                self.refused(self.create(*extra), why)
        # An anonymous volume is new and empty.
        guard.check(self.create("-v", "/data"), self.conf)

    def test_a_symlink_below_the_work_directory(self):
        # A job's own code could replace a directory the runner mounts with a link to the runner's directory.
        home = self.work / "_temp" / "_github_home"
        home.rmdir()
        home.symlink_to(self.runner)
        self.refused(self.create(), "a symlink below")

    def test_docker_run_and_build_and_anything_else(self):
        self.refused(["run", "--rm", IMAGE], "docker run: the CI tier runs no docker:// step and no container action")
        self.refused(["build", "-t", "x", "."], "docker build")
        for command in ("cp", "commit", "save", "exec2", "volume", "plugin", "system"):
            with self.subTest(command=command):
                self.refused([command, "x"], f"docker {command}")
        self.refused(["--host", "tcp://1.2.3.4:2375", "ps"], "global option --host")
        self.refused(["--config", "/tmp/x", "pull", IMAGE], "not in the job's temp directory")
        self.refused(["exec", "--privileged", "abc", "sh"], "exec option --privileged")
        self.refused(["exec", "-i", "--workdir", "/w", "-u", "0", "abc", "sh"], "exec option -u")
        self.refused(["network", "create", "--label", "x", "host"], "only the runner's job network")
        self.refused(["network", "connect", NETWORK, "abc"], "network connect")
        self.refused(["pull", "--platform", "x", IMAGE], "option --platform")
        self.refused(["login", "ghcr.io", "-u", "a", "-p", "secret"], "option -p")

    def test_the_guard_runs_docker_with_its_own_host_and_a_minimal_environment(self):
        fake = pathlib.Path(self.tmp.name) / "fake-docker"
        fake.write_text("#!/usr/bin/env python3\nimport json, os, sys\n"
                        "print(json.dumps({'argv': sys.argv[1:], 'env': dict(os.environ)}))\n")
        fake.chmod(0o755)
        conf = pathlib.Path(self.tmp.name) / "instance.json"
        conf.write_text(json.dumps({**self.conf, "docker": str(fake)}))
        env = {"PATH": os.environ["PATH"], "HOME": "/home/x", "DOCKER_HOST": "tcp://evil:2375", "RUNNER_SECRET": "s",
               "GITHUB_TOKEN": "t"}

        def run(*argv):
            r = subprocess.run([sys.executable, "-I", str(GUARD), str(conf), *argv], capture_output=True, text=True, env=env)
            return r.returncode, (json.loads(r.stdout) if r.returncode == 0 else r.stderr)

        code, out = run(*self.create())
        self.assertEqual(code, 0, out)
        self.assertEqual(out["argv"][:2], ["--host", "unix:///run/user/1001/docker.sock"])
        self.assertNotIn("DOCKER_HOST", out["env"])
        self.assertNotIn("RUNNER_SECRET", out["env"])  # a container's `-e RUNNER_SECRET` reads nothing
        code, out = run("exec", "-i", "--workdir", "/w", "-e", "GITHUB_TOKEN", "abc", "sh")
        self.assertEqual(out["env"]["GITHUB_TOKEN"], "t")  # the step's own environment
        self.assertNotIn("DOCKER_HOST", out["env"])
        code, out = run("run", IMAGE)
        self.assertEqual(code, 125)
        self.assertIn("docker guard (CI tier): refused: docker run", out)


if __name__ == "__main__":
    unittest.main()
