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
        self.assertEqual(s["DB_HOST"], "")
        self.assertEqual(s["RUNNER_NAMES"], "box-planner-1 box-planner-2")
        # Production on another machine: the exception names its one address.
        s = self.settings("FACTORY_ORG=acme\nPLANNING_DB_PORT=5432\nPLANNING_DB_HOST=203.0.113.7\n", tier="planning")
        self.assertEqual((s["DB_PORT"], s["DB_HOST"]), ("5432", "203.0.113.7"))
        # The strict tier never gets one.
        s = self.settings("FACTORY_ORG=acme\nPLANNING_DB_PORT=5432\nPLANNING_DB_HOST=203.0.113.7\n")
        self.assertEqual((s["DB_PORT"], s["DB_HOST"]), ("", ""))

    def test_a_remote_planning_database_is_one_address_with_a_port(self):
        for conf in ("PLANNING_DB_PORT=5432\nPLANNING_DB_HOST=db-host\n",
                     "PLANNING_DB_PORT=5432\nPLANNING_DB_HOST=10.0.0.1,10.0.0.2\n",
                     "PLANNING_DB_HOST=203.0.113.7\n"):
            with self.subTest(conf=conf), tempfile.TemporaryDirectory() as tmp:
                host_conf = pathlib.Path(tmp) / "host.conf"
                host_conf.write_text("FACTORY_ORG=acme\n" + conf)
                cfg = pathlib.Path(tmp) / "factory.json"
                cfg.write_text(json.dumps({"runners": {"strict": "strict-pool", "planning": "plan-pool"}}))
                r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True,
                                   env={**os.environ, "HOST_CONF": str(host_conf), "FACTORY_JSON": str(cfg),
                                        "TIER": "planning"})
                self.assertEqual(r.returncode, 1)
                self.assertIn("PLANNING_DB_HOST must be one IPv4 address, with PLANNING_DB_PORT set", r.stderr)

    def test_the_ci_tier(self):
        runners = {"strict": "strict-pool", "planning": "plan-pool", "ci": "ci-pool"}
        s = self.settings("FACTORY_ORG=acme\nRUNNER_NAME_PREFIX=box\n", tier="ci", factory={"runners": runners})
        self.assertEqual((s["RUNNER_LABELS"], s["RUNNER_GROUP"]), ("ci-pool", "factory-ci"))
        self.assertEqual((s["RUNNER_USER"], s["RUNNER_UNIT"], s["FW_UNIT"], s["NFT_TABLE"], s["NFT_FILE"]),
                         ("factory-ci", "factory-ci", "factory-ci-firewall", "factory_ci", "/etc/factory-runner/ci-firewall.nft"))
        self.assertEqual((s["RUNNER_COUNT"], s["MEM_HIGH"], s["MEM_MAX"], s["CPU_QUOTA"], s["DB_PORT"]),
                         ("2", "14G", "16G", "800%", ""))
        self.assertEqual(s["RUNNER_NAMES"], "box-ci-1 box-ci-2")
        # One disposable runner per job: each job's caps and limits, the registration App, and no CPU weight (it
        # would rank the CI user against other users only; the slice's CPUQuota is the bound).
        self.assertEqual((s["CI_JOB_CPUS"], s["CI_JOB_MEMORY"], s["CI_JOB_PIDS"], s["CI_JOB_SHM"], s["CI_JOB_HOURS"],
                          s["CI_IDLE_HOURS"], s["CI_MIN_FREE_GB"]), ("4", "6g", "8192", "1g", "6", "24", "20"))
        self.assertEqual(s["CI_APP_CLIENT_ID"], "")
        self.assertNotIn("CPU_WEIGHT", s)
        self.assertNotIn("CI_JOB_CPUS", self.settings("FACTORY_ORG=acme\n", factory={"runners": runners}))
        # host.conf's caps, factory.json's group, and a second organization's names.
        s = self.settings("FACTORY_ORG=other\nRUNNER_INSTANCE=other\nCI_RUNNERS=3\nCI_CPU_QUOTA=1200%\n", tier="ci",
                          factory={"runners": {**runners, "groups": {"shared": "other-pool", "ci": "other-ci"}}})
        self.assertEqual((s["RUNNER_COUNT"], s["CPU_QUOTA"], s["RUNNER_GROUP"]), ("3", "1200%", "other-ci"))
        self.assertEqual((s["RUNNER_USER"], s["FW_UNIT"], s["NFT_TABLE"]),
                         ("factory-ci-other", "factory-ci-firewall-other", "factory_ci_other"))
        # The other tiers keep the shared pool.
        self.assertEqual(self.settings("FACTORY_ORG=acme\n", factory={"runners": runners})["RUNNER_GROUP"], "factory-pool")

    def test_a_factory_json_from_before_the_ci_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = pathlib.Path(tmp) / "factory.json"
            cfg.write_text(json.dumps({"runners": {"strict": "s", "planning": "p"}}))
            env = {**os.environ, "HOST_CONF": "/nonexistent", "FACTORY_JSON": str(cfg), "TIER": "ci"}
            r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("factory.json names no runner label for the ci tier (runners.ci)", r.stderr)

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

    def test_a_second_organization_gets_its_own_names(self):
        first = self.settings("FACTORY_ORG=acme\nRUNNER_NAME_PREFIX=box\n")
        self.assertEqual((first["RUNNER_USER"], first["RUNNER_UNIT"], first["FW_UNIT"], first["NFT_TABLE"], first["NFT_FILE"]),
                         ("factory-runner", "factory-runner", "factory-firewall", "factory_runner",
                          "/etc/factory-runner/firewall.nft"))
        s = self.settings("FACTORY_ORG=other\nRUNNER_NAME_PREFIX=box\nRUNNER_INSTANCE=other\n")
        self.assertEqual((s["RUNNER_USER"], s["RUNNER_UNIT"], s["FW_UNIT"], s["NFT_TABLE"], s["NFT_FILE"]),
                         ("factory-runner-other", "factory-runner-other", "factory-firewall-other", "factory_runner_other",
                          "/etc/factory-runner/firewall-other.nft"))
        self.assertEqual(s["RUNNER_HOME"], "/var/lib/factory/factory-runner-other")
        self.assertEqual(s["RUNNER_NAMES"], "box-factory-1 box-factory-2 box-factory-3")
        p = self.settings("FACTORY_ORG=other\nRUNNER_INSTANCE=other\n", tier="planning")
        self.assertEqual((p["RUNNER_USER"], p["FW_UNIT"], p["NFT_TABLE"]),
                         ("factory-planner-other", "factory-planner-firewall-other", "factory_planner_other"))

    def test_a_bad_instance_name_is_refused(self):
        for name in ("Acme", "1acme", "acme-co", "a" * 13):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                conf = pathlib.Path(tmp) / "host.conf"
                conf.write_text(f"RUNNER_INSTANCE={name}\n")
                env = {**os.environ, "HOST_CONF": str(conf)}
                r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True, env=env)
                self.assertEqual(r.returncode, 1)
                self.assertIn("RUNNER_INSTANCE must be", r.stderr)

    def test_another_organizations_runners_are_never_taken_over(self):
        # Checked before anything else, root or not: the runner directory belongs to another organization.
        with tempfile.TemporaryDirectory() as tmp:
            runner = pathlib.Path(tmp) / "factory-runner" / "actions-runner"
            runner.mkdir(parents=True)
            (runner / ".runner").write_bytes(b"\xef\xbb\xbf" + json.dumps(
                {"agentName": "box-factory", "gitHubUrl": "https://github.com/first-org"}).encode())
            conf, cfg = pathlib.Path(tmp) / "host.conf", pathlib.Path(tmp) / "factory.json"
            conf.write_text(f"FACTORY_ORG=second-org\nRUNNER_HOME_BASE={tmp}\n")
            cfg.write_text(json.dumps({"runners": {"strict": "s", "planning": "p"}}))
            env = {**os.environ, "HOST_CONF": str(conf), "FACTORY_JSON": str(cfg)}
            r = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("registered to https://github.com/first-org, not https://github.com/second-org", r.stderr)
        self.assertIn("set RUNNER_INSTANCE", r.stderr)

    def test_host_conf_never_sets_the_tier_or_its_owner(self):
        # A claim must name its tier on the command line; a host.conf default would claim for it.
        for line, env in (("TIER=${TIER:-ci}", {}), ("TIER=ci", {"TIER": "strict"}),
                          ("TIER_OWNER=acme/app", {"TIER": "ci"})):
            with self.subTest(line=line), tempfile.TemporaryDirectory() as tmp:
                conf = pathlib.Path(tmp) / "host.conf"
                conf.write_text(f"FACTORY_ORG=acme\n{line}\n")
                base = {k: v for k, v in os.environ.items() if k not in ("TIER", "TIER_OWNER")}
                r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True,
                                   env={**base, "HOST_CONF": str(conf), **env})
                self.assertEqual(r.returncode, 1)
                self.assertIn("sets TIER or TIER_OWNER: they belong on the command line", r.stderr)
        # The same value on both is no override.
        self.assertEqual(self.settings("FACTORY_ORG=acme\nTIER=planning\n", tier="planning")["TIER"], "planning")

    def test_an_unknown_tier_is_refused(self):
        env = {**os.environ, "HOST_CONF": "/nonexistent", "TIER": "prod"}
        r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("TIER must be strict, planning or ci", r.stderr)


if __name__ == "__main__":
    unittest.main()
