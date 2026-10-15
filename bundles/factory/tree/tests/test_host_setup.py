"""host/setup.sh's settings: the runner labels from factory.json, this host's from host.conf, defaults for
the rest (--print-settings resolves them without root). The setup itself needs root, systemd and rootless
Docker on the host, so its parts that decide something (the apt plan, the tier's owner, the CI key, the runner
homes' base) are functions, run here on their own with stand-ins for the system's tools; setup-ci.sh's units are
checked as text."""
import json
import os
import pathlib
import re
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "host" / "setup.sh"
SETUP_CI = SCRIPT.parent / "setup-ci.sh"
PRELUDE = 'die() { printf "ERROR: %s\\n" "$*" >&2; exit 1; }\nlog() { :; }\n'


def function(name):
    """One function of setup.sh, as written there."""
    m = re.search(rf"^{name}\(\) {{\n.*?^}}\n", SCRIPT.read_text(), re.S | re.M)
    assert m, name
    return m.group(0)


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
        self.assertEqual(s["SLICE_TASKS"], "16384")
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
                     "PLANNING_DB_PORT=5432\nPLANNING_DB_HOST=203.0.113.300\n",
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
        # The slice's process cap: every job at its CI_JOB_PIDS, and room for the manager and daemon besides.
        self.assertEqual(s["SLICE_TASKS"], str(2 * 8192 + 4096))
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
        self.assertEqual(s["SLICE_TASKS"], str(3 * 8192 + 4096))
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
        self.assertIn("factory.json names no runner label of its own for the ci tier (runners.ci)", r.stderr)

    def test_a_tier_needs_a_label_of_its_own(self):
        # A runner with none of the factory's labels would take any job asking only for self-hosted.
        for label in (",", " , ", "", "self-hosted", "Self-Hosted, ,", "self-hosted,Linux,X64"):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                conf, cfg = pathlib.Path(tmp) / "host.conf", pathlib.Path(tmp) / "factory.json"
                conf.write_text("FACTORY_ORG=acme\n")
                cfg.write_text(json.dumps({"runners": {"strict": label, "planning": "p"}}))
                r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True,
                                   env={**os.environ, "HOST_CONF": str(conf), "FACTORY_JSON": str(cfg), "TIER": "strict"})
                self.assertEqual(r.returncode, 1)
                self.assertIn("names no runner label of its own for the strict tier", r.stderr)

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
                          ("TIER_OWNER=acme/app", {"TIER": "ci"}),
                          # Any assignment, even one equal to the command line's, as the docs say.
                          ("TIER=planning", {"TIER": "planning"}), ("  export TIER=ci", {"TIER": "ci"}),
                          ("declare -x TIER_OWNER=acme/app", {"TIER": "ci", "TIER_OWNER": "acme/app"})):
            with self.subTest(line=line), tempfile.TemporaryDirectory() as tmp:
                conf = pathlib.Path(tmp) / "host.conf"
                conf.write_text(f"FACTORY_ORG=acme\n{line}\n")
                base = {k: v for k, v in os.environ.items() if k not in ("TIER", "TIER_OWNER")}
                r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True,
                                   env={**base, "HOST_CONF": str(conf), **env})
                self.assertEqual(r.returncode, 1)
                self.assertIn("sets TIER or TIER_OWNER: they belong on the command line", r.stderr)
        # A comment that mentions them is no assignment.
        self.assertEqual(self.settings("FACTORY_ORG=acme\n# TIER=ci never goes here\n", tier="planning")["TIER"],
                         "planning")

    def test_an_unknown_tier_is_refused(self):
        env = {**os.environ, "HOST_CONF": "/nonexistent", "TIER": "prod"}
        r = subprocess.run(["bash", str(SCRIPT), "--print-settings"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("TIER must be strict, planning or ci", r.stderr)


class SetupParts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def tool(self, name, body):
        (self.bin / name).write_text("#!/usr/bin/env bash\n" + body)
        (self.bin / name).chmod(0o755)

    def bash(self, script, **env):
        return subprocess.run(["bash", "-c", PRELUDE + script], capture_output=True, text=True,
                              env={**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", **env})

    def test_the_apt_plan_never_upgrades_or_removes(self):
        self.tool("dpkg-query", "exit 1\n")  # nothing installed
        self.tool("apt-cache", "exit 0\n")  # every candidate known
        self.tool("apt-get", f'echo "$*" >> {self.root}/apt.log\n'
                             f'if [[ $1 == install && $2 == -s ]]; then cat {self.root}/plan; fi\n')
        plans = {
            "Inst libicu74 (74.2-1ubuntu3 Ubuntu:24.04/noble [amd64])\n": None,
            "Inst libssl3t64 [3.0.13-0ubuntu3.4] (3.0.13-0ubuntu3.5 Ubuntu:24.04/noble [amd64])\n":
                "would upgrade libssl3t64",
            "Remv libfoo1 [1.0-1]\nInst libicu74 (74.2-1ubuntu3 Ubuntu:24.04/noble [amd64])\n": "would remove libfoo1",
        }
        for plan, refusal in plans.items():
            with self.subTest(plan=plan):
                (self.root / "plan").write_text(plan)
                (self.root / "apt.log").unlink(missing_ok=True)
                r = self.bash(function("runner_deps") + "runner_deps\n")
                installs = [line for line in (self.root / "apt.log").read_text().splitlines()
                            if line.startswith("install -y")]
                if refusal:
                    self.assertEqual(r.returncode, 1)
                    self.assertIn(refusal, r.stderr)
                    self.assertEqual(installs, [])
                else:
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertEqual(len(installs), 1)

    def checkout(self, origin):
        repo = self.root / "checkout"
        repo.mkdir(exist_ok=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "remove", "origin"], capture_output=True)
        if origin:
            subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", origin], check=True)
        return repo

    def claim(self, origin, **env):
        repo = self.checkout(origin)
        stub = 'install() { mkdir -p "${@: -2}"; }\n'  # root's install -o root, as a plain mkdir
        return self.bash(stub + function("claim_tier") + f"claim_tier {self.root}/etc/tiers\n",
                         SCRIPT_DIR=str(repo), RUNNER_UNIT="factory-runner", TIER="strict", **env)

    def test_a_tier_belongs_to_the_checkout_that_claimed_it(self):
        owner = self.root / "etc" / "tiers" / "factory-runner"
        r = self.claim("git@github.com:acme/app.git")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no checkout owns the strict tier", r.stderr)
        r = self.claim("git@github.com:acme/app.git", TIER_OWNER="acme/app")
        self.assertIn("name the tier you're giving acme/app", r.stderr)  # a dropped TIER would claim strict
        self.assertFalse(owner.exists())
        r = self.claim("git@github.com:acme/app.git", TIER_OWNER="acme/app", tier_named="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(owner.read_text(), "acme/app\n")
        self.assertEqual(self.claim("https://github.com/acme/app.git").returncode, 0)  # the same repository
        r = self.claim("git@github.com:acme/other.git", TIER_OWNER="acme/other", tier_named="1")
        self.assertEqual(r.returncode, 1)
        self.assertIn("is set up from acme/app's checkout", r.stderr)
        self.assertEqual(owner.read_text(), "acme/app\n")
        r = self.claim(None)
        self.assertIn("can't tell which repository this checkout is: git says: ", r.stderr)  # git's own words
        self.assertIn("safe.directory", r.stderr)

    def test_the_ci_key_is_roots_and_never_in_a_checkout(self):
        checkout, key = self.root / "checkout", self.root / "etc" / "app.pem"
        checkout.mkdir()
        key.parent.mkdir()
        stub = "chown() { :; }\n"  # root's chown
        run = lambda: self.bash(stub + function("check_ci_key") + f"check_ci_key {key}\n",  # noqa: E731
                                SCRIPT_DIR=str(checkout))
        self.assertIn("install the runner-registration App's private key first", run().stderr)
        key.symlink_to(self.root / "elsewhere.pem")
        (self.root / "elsewhere.pem").write_text("key")
        self.assertIn("install the runner-registration App's private key first", run().stderr)
        key.unlink()
        key.write_text("key")
        key.chmod(0o644)
        self.assertEqual(run().returncode, 0)
        self.assertEqual(key.stat().st_mode & 0o777, 0o600)
        (checkout / "ci-app.pem").write_text("key")
        r = run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("never goes in a checkout", r.stderr)

    def test_a_runner_home_base_a_person_owns_is_warned_about(self):
        base = self.root / "workbench" / "factory"
        base.mkdir(parents=True)
        r = self.bash(function("warn_home_base") + f"warn_home_base {base}\n", RUNNER_USER="factory-runner")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"WARNING: {base.resolve()} (at or above RUNNER_HOME_BASE) is owned by uid {os.getuid()}",
                      r.stdout)
        # A link is followed: the directories warned about are the ones the homes would really be in.
        link = self.root / "link"
        link.symlink_to(base)
        r = self.bash(function("warn_home_base") + f"warn_home_base {link}\n", RUNNER_USER="factory-runner")
        self.assertIn(f"WARNING: {base.resolve()} (at or above", r.stdout)
        self.assertNotIn(f"WARNING: {link} ", r.stdout)
        # Root's all the way up, a base not created yet included: nothing to say.
        r = self.bash(function("warn_home_base") + "warn_home_base /usr/factory-not-here\n",
                      RUNNER_USER="factory-runner")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_the_ci_units(self):
        text = SETUP_CI.read_text()
        units = dict(re.findall(r'cat > "/etc/systemd/system/\$RUNNER_UNIT-([\w@.]+)" <<EOF\n(.*?)\nEOF', text, re.S))
        self.assertEqual(set(units), {"trip.service", "gate.service", "check.service", "check.timer", "fw.service",
                                      "fw.timer", "slot@.service"})
        # The gate: before any slot, at boot too, its failure the trip.
        self.assertIn("OnFailure=$RUNNER_UNIT-trip.service", units["gate.service"])
        self.assertIn("ConditionPathExists=!$TRIPPED", units["gate.service"])
        self.assertIn("WantedBy=multi-user.target", units["gate.service"])
        # The timer's check starts nothing on its own: no Requires=.
        self.assertNotIn("Requires=", units["check.service"])
        for unit in ("check.service", "fw.service"):
            self.assertIn("OnFailure=$RUNNER_UNIT-trip.service", units[unit])
        slot = units["slot@.service"]
        self.assertIn("Requires=$FW_UNIT.service user@$RUID.service $RUNNER_UNIT-gate.service", slot)
        self.assertIn("ExecStopPost=$launcher stop $CONF %i", slot)
        # A setup run restarts a slot whose runner isn't running a job, so it takes the new launcher now: only when retire
        # deregistered it (10), since an error, or GitHub's refusal, means it's busy or can't tell.
        self.assertIn('$launcher retire "$CONF" "$i" || idle=$?', text)
        self.assertIn("if ((idle == 10)); then", text)
        # Records on the old tmpfs state move in as leftovers only after the slots' new settings are in place.
        self.assertLess(text.index('mv -f "$NEW_CONF" "$CONF"'), text.index('mv -f "$f" "$STATE/slot-$n.leftover-$id"'))
        self.assertLess(text.index('mv -f "$f" "$STATE/slot-$n.leftover-$id"'), text.index('$launcher retire'))
        self.assertIn("KillMode=mixed", slot)
        # Longer than the launcher's worst cleanup: docker rm, a token (openssl, the API) and the registration's
        # removal, the token and the removal twice over for a refused token minted again.
        self.assertGreater(int(re.search(r"TimeoutStopSec=(\d+)", slot).group(1)), 120 + 2 * (30 + 30 + 30))
        # The job image is kept while its inputs are, unless CI_REBUILD=1.
        self.assertIn('if [[ ${CI_REBUILD:-} != 1 && $inputs == "$old_inputs"', text)
        self.assertIn('"image_inputs=$(json_str "$inputs")"', text)
        # The slots' state outlives a reboot.
        self.assertRegex(text, r"(?m)^STATE=/var/lib/factory-runner/\$RUNNER_UNIT$")


if __name__ == "__main__":
    unittest.main()
