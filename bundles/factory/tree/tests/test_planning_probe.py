"""The planning stages' sandbox probe (factory-smoke's planning-sandbox job, D2 rule 5, D3): it runs on the
planning tier in the planning stages' job setup, and the workflow policy lets that one job, and no other smoke
job, use the planning runners, environment and service slots. The planning tool policy is implement's, which
smoke probes, plus WebFetch (D3 rule 5)."""

import pathlib
import shlex
import sys
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import render  # noqa: E402

try:
    import yaml  # noqa: F401
    import workflow_policy as policy  # noqa: E402
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@unittest.skipUnless(HAS_YAML, "needs PyYAML")
class PlanningProbe(unittest.TestCase):
    def setUp(self):
        self.assertEqual(policy.configure(FACTORY), [])
        smoke = yaml.safe_load(render.render_all(FACTORY, FACTORY / "templates")["factory-smoke.yml"])
        self.workflow_env = smoke.get("env") or {}
        self.jobs = smoke["jobs"]
        self.probe = self.jobs["planning-sandbox"]

    def failures(self, name, job):
        return policy.job_failures(name, job, self.workflow_env, None, FACTORY, "factory-smoke.yml", set())

    def test_it_runs_where_the_planning_stages_run(self):
        self.assertIn(policy.PLANNING_LABEL, self.probe["runs-on"])
        self.assertEqual(self.probe["environment"], policy.PLANNING_ENVIRONMENT)
        run = "\n".join(str(s.get("run", "")) for s in self.probe["steps"])
        self.assertIn("planning-services.sh", run)  # the reader password, held by pgbouncer
        self.assertIn("python3 -I .github/factory/services.py .github/factory/services.json plan", run)
        agent = next(s for s in self.probe["steps"] if str(s.get("uses", "")).startswith(policy.ACTION))
        self.assertIn("planning-sandbox.settings.json", agent["with"]["settings"])
        self.assertEqual(set(agent["env"]), policy.SERVICE_SLOTS)

    def test_the_policy_admits_it(self):
        self.assertEqual(self.failures("planning-sandbox", self.probe), [])

    def test_no_other_smoke_job_may_use_the_planning_tier(self):
        failures = self.failures("bash-sandbox-on-planning", self.probe)
        self.assertTrue(any("only the planning workflows may run on" in f for f in failures), failures)
        self.assertTrue(any("FACTORY_SVC_1 reaches the agent" in f for f in failures), failures)

    def test_the_probe_must_run_on_the_planning_tier(self):
        moved = {**self.probe, "runs-on": ["self-hosted", self.jobs["bash-sandbox"]["runs-on"][1]]}
        failures = self.failures("planning-sandbox", moved)
        self.assertTrue(any("sandbox probe must run on" in f for f in failures), failures)


class PlanningToolPolicy(unittest.TestCase):
    def words(self, name):
        return shlex.split((FACTORY / name).read_text())

    def test_plan_is_implement_plus_webfetch(self):
        """plan-tools.args has no probe of its own in factory-smoke: implement's (probed by implement-tools)
        plus WebFetch, D3 rule 5's open internet, which runs outside the Bash sandbox, and the same denies."""
        plan, implement = self.words("plan-tools.args"), self.words("implement-tools.args")
        tools = lambda w: set(w[w.index("--tools") + 1].split(","))  # noqa: E731
        allowed = lambda w: set(w[w.index("--allowedTools") + 1:w.index("--disallowedTools")])  # noqa: E731
        denies = lambda w: w[w.index("--disallowedTools"):]  # noqa: E731 - every deny rule, in order
        self.assertEqual(tools(plan) - tools(implement), {"WebFetch"})
        self.assertLessEqual(tools(implement), tools(plan))
        self.assertEqual(allowed(plan) - allowed(implement), {"WebFetch"})
        self.assertEqual(denies(plan), denies(implement))


if __name__ == "__main__":
    unittest.main()
