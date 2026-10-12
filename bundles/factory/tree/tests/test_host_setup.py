"""host/setup.sh's settings: the runner labels from factory.json, this host's from host.conf, defaults for
the rest (--print-settings resolves them without root). The setup itself needs root, systemd and rootless
Docker on the host."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "host" / "setup.sh"


class HostSettings(unittest.TestCase):
    def settings(self, host_conf="", tier="strict", factory=None):
        with tempfile.TemporaryDirectory() as tmp:
            conf, cfg = pathlib.Path(tmp) / "host.conf", pathlib.Path(tmp) / "factory.json"
            conf.write_text(host_conf)
            cfg.write_text(json.dumps(factory or {"runners": {"strict": "strict-pool", "planning": "plan-pool"}}))
            env = {**os.environ, "HOST_CONF": str(conf), "FACTORY_JSON": str(cfg), "TIER": tier}
            r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            return dict(line.split("=", 1) for line in r.stdout.splitlines())

    def test_defaults(self):
        s = self.settings("FACTORY_ORG=acme\nRUNNER_NAME_PREFIX=box\n")
        self.assertEqual(s["RUNNER_URL"], "https://github.com/acme")
        self.assertEqual(s["RUNNER_GROUP"], "factory-pool")
        self.assertEqual(s["RUNNER_LABELS"], "strict-pool")
        self.assertEqual(s["RUNNER_HOME"], "/var/lib/factory/factory-runner")
        self.assertEqual((s["RUNNER_COUNT"], s["MEM_HIGH"], s["MEM_MAX"], s["CPU_QUOTA"]), ("3", "8G", "10G", "400%"))
        self.assertEqual(s["RUNNER_NAMES"], "box-factory box-factory-2 box-factory-3")
        self.assertEqual((s["DB_PORT"], s["LAN_DNS"]), ("", ""))

    def test_the_planning_tier(self):
        s = self.settings("FACTORY_ORG=acme\nRUNNER_NAME_PREFIX=box\nPLANNING_DB_PORT=5433\n", tier="planning")
        self.assertEqual(s["RUNNER_LABELS"], "plan-pool")
        self.assertEqual(s["RUNNER_USER"], "factory-planner")
        self.assertEqual(s["DB_PORT"], "5433")
        self.assertEqual(s["RUNNER_NAMES"], "box-planner-1 box-planner-2")

    def test_host_conf_overrides(self):
        s = self.settings("FACTORY_ORG=acme\nRUNNER_HOME_BASE=/srv/f\nLAN_DNS=10.1.1.1\n"
                          "STRICT_RUNNERS=1\nSTRICT_MEMORY_HIGH=2G\nPROBE_PORTS=\"22 5432\"\n")
        self.assertEqual((s["RUNNER_HOME"], s["LAN_DNS"]), ("/srv/f/factory-runner", "10.1.1.1"))
        self.assertEqual((s["RUNNER_COUNT"], s["MEM_HIGH"], s["PROBE_PORTS"]), ("1", "2G", "22 5432"))

    def test_outside_a_checkout_the_org_is_unset(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = pathlib.Path(tmp) / "setup.sh"
            script.write_text(SCRIPT.read_text())
            (pathlib.Path(tmp) / "factory.json").write_text(json.dumps({"runners": {"strict": "s", "planning": "p"}}))
            env = {**os.environ, "HOST_CONF": "/nonexistent", "FACTORY_JSON": str(pathlib.Path(tmp) / "factory.json"),
                   "GIT_CEILING_DIRECTORIES": tmp}
            env.pop("FACTORY_ORG", None)
            r = subprocess.run(["bash", str(script), "--print-settings"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("FACTORY_ORG=\n", r.stdout)

    def test_the_runner_group_is_factory_jsons(self):
        s = self.settings("FACTORY_ORG=acme\n", factory={"runners": {"strict": "s", "planning": "p",
                                                                      "groups": {"shared": "acme-pool"}}})
        self.assertEqual(s["RUNNER_GROUP"], "acme-pool")

    def test_an_unknown_tier_is_refused(self):
        env = {**os.environ, "HOST_CONF": "/nonexistent", "TIER": "prod"}
        r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("TIER must be strict or planning", r.stderr)


if __name__ == "__main__":
    unittest.main()
