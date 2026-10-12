"""Tests for render.py: this project's workflows are its templates rendered with its factory.json, byte for
byte; another project's settings render workflows that pass workflow_policy.py with none of this project's
values left; and what the renderer refuses."""

import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = FACTORY.parent / "workflows"
sys.path.insert(0, str(FACTORY))

import render  # noqa: E402

HAS_YAML = importlib.util.find_spec("yaml") is not None


def quiet_main(args):
    """render.main, with its output (::error:: lines CI would annotate) captured."""
    with contextlib.redirect_stdout(io.StringIO()):
        return render.main(args)

# Another project: every setting differs from any real project's.
OTHER = {
    "app": {"user_id": 123456, "login": "other-factory[bot]"},
    "image": {"repository": "ghcr.io/other-org/job", "digest": "sha256:" + "b" * 64},
    "runners": {"strict": "strict-pool", "planning": "plan-pool", "production": "prod-pool"},
    "environments": {"writer": "writer-env", "planning": "planning-env", "production": "production-env"},
    "models": {
        "triage": {"default": "claude-test-a", "options": ["claude-test-a", "claude-test-b"]},
        "implement": {"default": "claude-test-b", "options": ["claude-test-b"]},
        "plan": {"default": "claude-test-c", "options": ["claude-test-c", "claude-test-a"]},
        "revise": "claude-test-d", "revise_doc": "claude-test-e", "improve": "claude-test-f",
        "smoke": {"default": "claude-test-a", "options": ["claude-test-a"]},
        "probe": "claude-test-g",
    },
    "limits": {"agent_minutes": 100, "code_revisions": 2, "doc_revisions": 4},
    "improve": {"cron": "5 4 * * 1"},
    "smoke": {"echo_host": "echo.other.example", "host_probes": "10.9.9.9 10.9.9.10"},
    "stack": {"profile": "python-node", "python": "server", "node": "client", "env_file": "server/.env",
              "database": "otherdb", "env": {}},
}
OTHER_PLANNING = {"database": {"host": "10.0.0.9", "port": 5433, "name": "otherdb", "user": "reader2", "local_port": 7432}}
THIS = json.loads((FACTORY / "factory.json").read_text())
THIS_PLANNING = json.loads((FACTORY / "planning.json").read_text()) if (FACTORY / "planning.json").exists() else {}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def this_projects_values():
    """This project's settings as they appear in its rendered workflows (values too short to be telling left out)."""
    c, db = THIS, THIS_PLANNING.get("database") or {}
    values = [str(c["app"]["user_id"]), c["app"]["login"].removesuffix("[bot]"), *c["environments"].values(),
              c["image"]["repository"], c["image"]["digest"].removeprefix("sha256:")[:8],
              *(f"[self-hosted, {label}]" for label in c["runners"].values() if isinstance(label, str)),
              *strings(c["models"]), f'"{c["improve"]["cron"]}"', f'AGENT_MINUTES: "{c["limits"]["agent_minutes"]}"',
              f'REVISION_LIMIT: "{c["limits"]["code_revisions"]}"', f'REVISION_LIMIT: "{c["limits"]["doc_revisions"]}"',
              c["smoke"]["echo_host"]]
    if db.get("host"):
        values += [f"database {db['name']}", f"127.0.0.1:{db['local_port']}"]
    return [v for v in dict.fromkeys(values) if len(v) >= 4]


class ThisProject(unittest.TestCase):
    def test_the_workflows_are_the_templates_rendered(self):
        rendered = render.render_all(FACTORY, FACTORY / "templates")
        on_disk = {p.name: p.read_text() for p in WORKFLOWS.glob("factory-*.yml")}
        self.assertEqual(sorted(rendered), sorted(on_disk))
        for name, text in rendered.items():
            with self.subTest(workflow=name):
                self.assertEqual(text, on_disk[name], f"{name}: edit templates/{name}, then run render.py")

    def test_check_mode_passes(self):
        self.assertEqual(quiet_main(["--check"]), 0)


class AnotherProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        # The other project's factory directory: this project's files, its own settings.
        self.factory = root / "factory"
        shutil.copytree(FACTORY, self.factory, ignore=shutil.ignore_patterns("tests", "templates", "__pycache__"))
        (self.factory / "factory.json").write_text(json.dumps(OTHER))
        (self.factory / "planning.json").write_text(json.dumps(OTHER_PLANNING))
        self.out = root / "workflows"
        self.out.mkdir()
        self.rendered = render.render_all(self.factory, FACTORY / "templates")
        for name, text in self.rendered.items():
            (self.out / name).write_text(text)

    def tearDown(self):
        self.tmp.cleanup()

    def test_none_of_this_projects_settings_are_left(self):
        for name, text in self.rendered.items():
            for value in this_projects_values():
                with self.subTest(workflow=name, value=value):
                    self.assertNotIn(value, text)

    def test_its_settings_are_where_this_projects_were(self):
        implement = self.rendered["factory-implement.yml"]
        self.assertIn("runs-on: [self-hosted, strict-pool]", implement)
        self.assertIn("image: ghcr.io/other-org/job@sha256:" + "b" * 64, implement)
        self.assertIn("timeout-minutes: 130", implement)
        self.assertIn('AGENT_MINUTES: "100"', implement)
        self.assertIn("options: [claude-test-b]", implement)
        self.assertIn('bot_id: "123456"', implement)
        self.assertIn("bot_name: other-factory[bot]", implement)
        plan = self.rendered["factory-plan.yml"]
        self.assertIn("runs-on: [self-hosted, plan-pool]", plan)
        self.assertIn("environment: planning-env", plan)
        self.assertIn("timeout-minutes: 145", plan)
        self.assertIn("127.0.0.1:7432 (database otherdb, user reader2,", plan)
        self.assertIn("psql -h 127.0.0.1 -p 7432 -U reader2 otherdb.", plan)
        self.assertIn('cron: "5 4 * * 1"', self.rendered["factory-improve.yml"])
        smoke = self.rendered["factory-smoke.yml"]
        self.assertIn('allowedDomains = ["echo.other.example"]', smoke)
        self.assertIn("bash /opt/factory-probe/services_probe.sh echo.other.example", smoke)
        self.assertIn('FACTORY_HOST_PROBES: "10.9.9.9 10.9.9.10 172.17.0.1 10.0.2.2"', smoke)
        self.assertIn("runs-on: [self-hosted, prod-pool]", self.rendered["factory-gate.yml"])

    @unittest.skipUnless(HAS_YAML, "needs PyYAML")
    def test_the_policy_holds_with_its_labels_and_environments(self):
        # ci.yml isn't the factory's; the policy checks the factory workflows of the other project.
        r = subprocess.run([sys.executable, str(FACTORY / "workflow_policy.py"), str(self.out), str(self.factory)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("0 violations", r.stdout)

    @unittest.skipUnless(HAS_YAML, "needs PyYAML")
    def test_the_policy_reads_the_labels_from_factory_json(self):
        # With this project's factory.json, the other project's planning jobs are on unknown runners.
        shutil.copy(FACTORY / "factory.json", self.factory / "factory.json")
        r = subprocess.run([sys.executable, str(FACTORY / "workflow_policy.py"), str(self.out), str(self.factory)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"a planning agent job must run on {THIS['runners']['planning']} runners", r.stdout)


class Refusals(unittest.TestCase):
    VALUES = {"a": {"n": 3, "s": "x", "l": ["p", "q"], "b": True}, "_doc": "notes", "planning": {"x": 1}}

    def test_substitution(self):
        self.assertEqual(render.render("%{a.s}:%{a.n}:%{a.n+4}:[%{a.l}]", self.VALUES), "x:3:7:[p, q]")

    def test_unknown_or_group_or_unrenderable(self):
        for template in ("%{a.z}", "%{a}", "%{z.y}", "%{a.b}", "%{a.s+1}"):
            with self.subTest(template=template):
                with self.assertRaises(render.Invalid):
                    render.render(template, self.VALUES)

    def test_a_percent_brace_that_isnt_a_placeholder(self):
        with self.assertRaises(render.Invalid) as e:
            render.render("ok\n%{A}\n", self.VALUES)
        self.assertIn("line 2", str(e.exception))

    def test_unused_settings_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            (d / "templates").mkdir()
            (d / "factory.json").write_text(json.dumps({"a": {"used": 1, "unused": 2}, "_doc": "x"}))
            (d / "templates/factory-x.yml").write_text("v: %{a.used}\n")
            with self.assertRaises(render.Invalid) as e:
                render.render_all(d, d / "templates")
            self.assertIn("a.unused", str(e.exception))

    def test_check_finds_a_hand_edited_workflow_and_a_missing_template(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            (d / "templates").mkdir()
            (d / "workflows").mkdir()
            (d / "factory.json").write_text(json.dumps({"a": {"v": 1}}))
            (d / "templates/factory-x.yml").write_text("v: %{a.v}\n")
            self.assertEqual(quiet_main([str(d), str(d / "templates"), str(d / "workflows")]), 0)
            self.assertEqual(quiet_main(["--check", str(d), str(d / "templates"), str(d / "workflows")]), 0)
            (d / "workflows/factory-x.yml").write_text((d / "workflows/factory-x.yml").read_text() + "# hand edit\n")
            self.assertEqual(quiet_main(["--check", str(d), str(d / "templates"), str(d / "workflows")]), 1)
            (d / "workflows/factory-x.yml").unlink()
            (d / "workflows/factory-y.yml").write_text("unmanaged\n")
            self.assertEqual(quiet_main(["--check", str(d), str(d / "templates"), str(d / "workflows")]), 1)


if __name__ == "__main__":
    unittest.main()
