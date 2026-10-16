"""sandbox_check.py and sandbox_probe.py: the test services the bash-sandbox smoke job requires come from the stack
profile's `services` file, not a fixed list, so a profile without Redis passes on its Postgres alone; a missing or
malformed list fails; and every profile's list names only ports its with-test-services forwards."""

import pathlib
import re
import sys
import tempfile
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import sandbox_check as check  # noqa: E402
import sandbox_probe as probe  # noqa: E402

PROFILES = sorted(p for p in (FACTORY / "profiles").iterdir() if p.is_dir())


def services_file(text):
    d = tempfile.mkdtemp()
    path = pathlib.Path(d, "services")
    path.write_text(text)
    return str(path)


class Services(unittest.TestCase):
    def test_every_profile_lists_its_services_and_forwards_each_port(self):
        self.assertTrue(PROFILES)
        for profile in PROFILES:
            listed = check.read_services(str(profile / "services"))
            self.assertTrue(listed, f"{profile.name}: no services file, or a malformed one")
            forwarding = re.search(r"for p in ([0-9 ]+); do", (profile / "with-test-services").read_text())
            forwarded = {int(p) for p in forwarding[1].split()}
            for label, port in listed:
                self.assertIn(port, forwarded, f"{profile.name}: {label} ({port}) isn't forwarded to sandboxed Bash")

    def test_the_probe_and_the_check_read_a_list_alike(self):
        for text in ("db 5432\nredis 6379\n", "# comment\n\ndb 5432  # Postgres\n", "", "db 5432\nbad line\n",
                     "db 70000\n", "Db 5432\n"):
            path = services_file(text)
            self.assertEqual(check.read_services(path), probe.read_services(path), text)
        self.assertEqual(check.read_services(services_file("# none\n")), [])
        self.assertIsNone(check.read_services(services_file("db 5432\nbad line\n")))
        self.assertIsNone(check.read_services("/nonexistent/services"))

    def test_a_profile_without_redis_passes_on_its_postgres(self):
        dotnet = [("db", 5432)]
        lines = ["localsvc db connected", "unixsock docker refused"]
        self.assertEqual(check.sockets(lines, dotnet), [])
        self.assertEqual(check.sockets(lines, [("db", 5432), ("redis", 6379)]), ["test service unreachable: redis"])

    def test_a_listed_service_must_answer_and_the_docker_socket_must_not(self):
        services = [("db", 5432)]
        self.assertEqual(check.sockets(["localsvc db refused", "unixsock docker refused"], services),
                         ["test service unreachable: db"])
        self.assertEqual(check.sockets(["localsvc db connected", "unixsock docker connected"], services),
                         ["the Docker socket accepts connections"])
        self.assertEqual(check.sockets(["localsvc none", "unixsock docker refused"], []), [])

    def test_the_planning_tiers_open_internet_still_goes_through_the_proxy(self):
        lines = ["net https://pypi.org/simple/ 200", "net https://example.com/ 200", "noproxy https://example.com/ 000",
                 "direct 1.1.1.1:443 closed", "dns example.com failed"]
        net = lambda failures: [f for f in failures if "allowlist" in f or "proxy" in f or "direct" in f  # noqa: E731
                                or "DNS" in f]
        self.assertEqual(net(check.judge_agent(lines, [], [])), ["host outside the allowlist reachable: "
                                                                  "https://example.com/ (200)"])
        self.assertEqual(net(check.judge_agent(lines, [], [], "open")), [])
        around = [l.replace("noproxy https://example.com/ 000", "noproxy https://example.com/ 200") for l in lines]
        self.assertEqual(net(check.judge_agent(around, [], [], "open")), ["reached a host without the sandbox proxy"])

    def test_from_inside_the_sandbox_no_unix_socket_may_answer(self):
        lines = ["unixsock-found /tmp/claude-http-1.sock blocked", "unixsock-found /run/other.sock connected"]
        self.assertEqual(check.found_sockets(lines), ["a Unix socket accepts connections: /run/other.sock"])
        self.assertIn("a Unix socket accepts connections: /run/other.sock", check.judge_agent(lines, [], []))
        # The control runs outside the sandbox: it reaches the job's own sockets, as it should.
        self.assertNotIn("a Unix socket accepts connections: /run/other.sock", check.judge_control(lines, []))

    def test_a_missing_or_malformed_list_fails_the_job(self):
        self.assertEqual(check.sockets(["localsvc db connected", "unixsock docker refused"], None),
                         ["the stack profile's services file is missing or malformed"])


if __name__ == "__main__":
    unittest.main()
