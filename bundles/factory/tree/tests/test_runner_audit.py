"""runner_audit.py: the organization's runner groups compared exactly with the expected state (every kind of
drift), a read that fails closed, the snapshot, the expected state's shape, and the workflow it writes (this script
and the expected state in it, nothing GitHub would read as an expression). GitHub is a fake organization."""
import contextlib
import copy
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))
import runner_audit as ra  # noqa: E402


def runner(rid, name, labels):
    defaults = [{"id": 1, "name": "self-hosted", "type": "read-only"}, {"id": 2, "name": "Linux", "type": "read-only"}]
    return {"id": rid, "name": name, "os": "Linux", "status": "online", "busy": False,
            "labels": defaults + [{"id": 10 + i, "name": label, "type": "custom"} for i, label in enumerate(labels)]}


TRIAGE = "acme/app/.github/workflows/factory-triage.yml@refs/heads/main"
GATE = "acme/app/.github/workflows/factory-gate.yml@refs/heads/main"


class FakeOrg:
    """acme's runner groups: the default one (empty), the shared pool, a production group and the CI tier's."""

    def __init__(self):
        self.groups = [
            {"id": 1, "name": "Default", "visibility": "all", "allows_public_repositories": False,
             "restricted_to_workflows": False, "selected_workflows": [], "default": True},
            {"id": 2, "name": "factory-pool", "visibility": "selected", "allows_public_repositories": False,
             "restricted_to_workflows": True, "selected_workflows": [TRIAGE]},
            {"id": 5, "name": "factory-pool-app-prod", "visibility": "selected", "allows_public_repositories": False,
             "restricted_to_workflows": True, "selected_workflows": [GATE]},
            {"id": 7, "name": "factory-ci", "visibility": "selected", "allows_public_repositories": False,
             "restricted_to_workflows": False, "selected_workflows": []},
        ]
        self.repos = {2: ["acme/app", "acme/game"], 5: ["acme/app"], 7: ["acme/game"]}
        self.runners = {1: [], 2: [runner(11, "box-factory", ["factory"]), runner(12, "box-planner-1", ["factory-plan"])],
                        5: [runner(53, "box-production", ["factory-prod"])],
                        7: [runner(901, "box-ci-1-a1b2c3", ["factory-ci"])]}
        self.fail = {}  # a path's start: the status it answers instead
        self.paths = []

    def get(self, path):
        self.paths.append(path)
        for start, status in self.fail.items():
            if path.startswith(start):
                return status, {"message": "no"}
        m = re.fullmatch(r"/orgs/acme/actions/runner-groups(?:/(\d+)/(repositories|runners))?\?per_page=100&page=(\d+)",
                         path)
        if not m:
            return 404, {"message": "Not Found"}
        gid, what, page = m.group(1), m.group(2), int(m.group(3))
        if gid is None:
            items, key = self.groups, "runner_groups"
        elif what == "repositories":
            items, key = [{"full_name": r} for r in self.repos.get(int(gid), [])], "repositories"
        else:
            items, key = self.runners.get(int(gid), []), "runners"
        return 200, {"total_count": len(items), key: items[(page - 1) * 100:page * 100]}


def expected_of(org):
    """The fake organization's state as an expected state, the CI tier's group as a pattern."""
    state = ra.snapshot("acme", "tok", call=lambda method, path, token: org.get(path))
    state["factory_labels"] = list(ra.DEFAULT_LABELS)
    state["groups"]["factory-ci"]["runners"] = {"pattern": r"box-ci-[0-9]+-[0-9a-f]{6}", "max": 2,
                                                "labels": ["factory-ci"]}
    return ra.load_expected(json.dumps(state))


class Audit(unittest.TestCase):
    def setUp(self):
        self.org = FakeOrg()
        self.expected = expected_of(self.org)

    def audit(self):
        return ra.audit(self.expected, self.org.get)

    def test_as_expected(self):
        self.assertEqual(self.audit(), (0, ["ok: 4 runner groups and 4 runners, as expected"]))
        # A just-in-time runner is registered with self-hosted itself, which may come back as a custom label: like the
        # other labels every self-hosted runner has, it's left out of the comparison, and never taken for a hosted one.
        self.org.runners[7][0]["labels"].append({"id": 40, "name": "self-hosted", "type": "custom"})
        self.assertEqual(self.audit()[0], 0)
        # Repositories are read only for a group open to selected ones; every list is read whole.
        self.assertNotIn("/orgs/acme/actions/runner-groups/1/repositories?per_page=100&page=1", self.org.paths)

    def test_every_kind_of_drift(self):
        cases = [
            (lambda o: o.groups.append({"id": 9, "name": "sneaky", "visibility": "selected"}),
             "group sneaky: not expected (a new group)"),
            (lambda o: o.groups.pop(2), "group factory-pool-app-prod: expected, but it's gone"),
            (lambda o: o.groups[2].update(visibility="all"), 'group factory-pool-app-prod: visibility is "all"'),
            (lambda o: o.groups[2].update(allows_public_repositories=True), "allows_public_repositories is true"),
            (lambda o: o.groups[2].update(restricted_to_workflows=False), "restricted_to_workflows is false"),
            (lambda o: o.groups[2].update(selected_workflows=[GATE, "acme/evil/.github/workflows/x.yml@refs/heads/main"]),
             "selected_workflows has acme/evil/.github/workflows/x.yml@refs/heads/main, not expected"),
            (lambda o: o.groups[1].update(selected_workflows=[]), f"selected_workflows is missing {TRIAGE}"),
            (lambda o: o.repos[5].append("acme/evil"), "group factory-pool-app-prod: repositories has acme/evil"),
            (lambda o: o.repos[2].remove("acme/game"), "group factory-pool: repositories is missing acme/game"),
            (lambda o: o.runners[5].append(runner(99, "rogue", ["factory-prod"])),
             "group factory-pool-app-prod: runner rogue (ID 99) not expected"),
            (lambda o: o.runners[2].pop(), "group factory-pool: runner box-planner-1 expected, but it's gone"),
            (lambda o: o.runners[5][0].update(id=54), "runner box-production is registered again (ID 54, expected 53)"),
            (lambda o: o.runners[5][0]["labels"].append({"id": 30, "name": "gpu", "type": "custom"}),
             "runner box-production has labels factory-prod, gpu, expected factory-prod"),
            (lambda o: o.runners[7].append(runner(902, "evil-1", ["factory-ci"])),
             r"runner evil-1 doesn't match box-ci-[0-9]+-[0-9a-f]{6}"),
            (lambda o: o.runners[7].extend([runner(902, "box-ci-2-aaaaaa", ["factory-ci"]),
                                            runner(903, "box-ci-1-bbbbbb", ["factory-ci"])]),
             "group factory-ci: 3 runners, at most 2 expected"),
            (lambda o: o.runners[7][0]["labels"].append({"id": 31, "name": "factory-prod", "type": "custom"}),
             "runner box-ci-1-a1b2c3 has labels factory-ci, factory-prod, expected factory-ci"),
            (lambda o: o.runners[1].append(runner(77, "box-factory-9", ["factory-prod"])),
             "group Default: runner box-factory-9 carries the factory label factory-prod, expected only in "
             "factory-pool-app-prod"),
            (lambda o: o.runners[2][0]["labels"].append({"id": 32, "name": "Ubuntu-Latest", "type": "custom"}),
             "runner box-factory carries Ubuntu-Latest, a GitHub-hosted runner's label"),
        ]
        for change, message in cases:
            with self.subTest(message=message):
                self.org = FakeOrg()
                change(self.org)
                status, lines = self.audit()
                self.assertEqual(status, 1, lines)
                self.assertTrue(all(line.startswith("DRIFT ") for line in lines), lines)
                self.assertTrue(any(message in line for line in lines), lines)

    def test_fails_closed(self):
        cases = [
            ("/orgs/acme/actions/runner-groups?", 500),
            ("/orgs/acme/actions/runner-groups/5/runners", 403),
            ("/orgs/acme/actions/runner-groups/2/repositories", 404),
        ]
        for start, status in cases:
            with self.subTest(path=start):
                self.org = FakeOrg()
                self.org.fail = {start: status}
                code, lines = self.audit()
                self.assertEqual(code, 2)
                self.assertIn(f"HTTP {status}", lines[0])
        self.org = FakeOrg()
        self.org.runners[5][0].pop("id")
        self.assertEqual(self.audit()[0], 2)
        self.org = FakeOrg()
        self.org.get = lambda path: (200, {"runner_groups": "not a list"})
        self.assertEqual(self.audit()[0], 2)

    def test_every_page_is_read(self):
        self.org.runners[2] += [runner(1000 + i, f"box-extra-{i}", ["factory"]) for i in range(150)]
        status, lines = self.audit()
        self.assertEqual(status, 1)
        self.assertEqual(sum("box-extra-" in line and "not expected" in line for line in lines), 150)
        self.assertIn("/orgs/acme/actions/runner-groups/2/runners?per_page=100&page=2", self.org.paths)

    def test_a_malformed_expected_state_is_refused(self):
        good = json.loads(json.dumps(self.expected))
        cases = [
            ({}, "the organization's name"),
            ({**good, "groups": {}}, "groups, by name"),
            ({**good, "factory_labels": "factory"}, "factory_labels"),
            ({**good, "groups": {"x": {"visibility": "selected"}}}, "group x: runners"),
            ({**good, "groups": {"x": {"runners": {"pattern": "(", "max": 1, "labels": []}}}}, "regular expression"),
            ({**good, "groups": {"x": {"runners": {"pattern": "a", "max": 0, "labels": []}}}}, "max (1 or more)"),
            ({**good, "groups": {"x": {"runners": {"pattern": ".*", "max": 2, "labels": []}}}}, "matches an empty name"),
            ({**good, "groups": {"x": {"runners": {"r": {"labels": []}}}}}, "each with its id and labels"),
            ({**good, "groups": {"x": {"runners": {"r": {"id": 1, "labels": ["a", 1]}}}}}, "each with its id and labels"),
            ({**good, "groups": {"x": {"runners": {"pattern": "a", "max": 1, "labels": [1]}}}}, "max (1 or more)"),
            ({**good, "groups": {"x": {"visibility": True, "runners": {}}}}, "group x: visibility"),
            ({**good, "groups": {"x": {"repositories": "acme/app", "runners": {}}}}, "group x: repositories"),
        ]
        for state, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, re.escape(message)):
                    ra.load_expected(json.dumps(state))


class Workflow(unittest.TestCase):
    def setUp(self):
        self.expected_text = json.dumps(expected_of(FakeOrg()), indent=2)
        self.script = (FACTORY / "runner_audit.py").read_text()

    def embedded(self, text, end):
        block = text.split(f"<<'{end}'\n", 1)[1].split(f"\n          {end}\n", 1)[0] + "\n"
        return "".join(line[10:] if line.strip() else line for line in block.splitlines(keepends=True))

    def test_the_workflow_carries_the_script_and_the_expected_state(self):
        text = ra.workflow(self.expected_text, self.script)
        self.assertEqual(self.embedded(text, ra.SCRIPT_END), self.script)
        self.assertEqual(json.loads(self.embedded(text, ra.EXPECTED_END)), json.loads(self.expected_text))
        self.assertEqual(re.findall(r"(?m)^    runs-on: (.+)$", text), ["ubuntu-latest"])  # the job's, not the script's
        self.assertIn("permissions:\n  issues: write\n\n", text)
        self.assertIn(f'    - cron: "{ra.CRON}"\n', text)
        self.assertIn("  workflow_dispatch:\n", text)
        # GitHub's expressions: the App's credentials and the issue's token, and nothing in the script or the state.
        self.assertEqual(re.findall(r"\$\{\{ ([^}]*) \}\}", text), [
            "vars.RUNNER_AUDIT_APP_CLIENT_ID", "secrets.RUNNER_AUDIT_APP_KEY", "github.token", "github.repository",
            "vars.RUNNER_AUDIT_NOTIFY"])
        self.assertIn("        if: failure() || cancelled()\n", text)  # a run that timed out raises it too

    def test_the_workflow_is_yaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("no PyYAML")
        doc = yaml.safe_load(ra.workflow(self.expected_text, self.script, cron="5 */2 * * *"))
        self.assertEqual(doc["name"], "factory-runner-audit")
        self.assertEqual(doc[True]["schedule"], [{"cron": "5 */2 * * *"}])  # YAML 1.1 reads `on` as true
        steps = doc["jobs"]["audit"]["steps"]
        self.assertEqual([s["shell"] for s in steps], ["bash", "bash"])
        self.assertIn('python3 -I "$RUNNER_TEMP/runner_audit.py" check', steps[0]["run"])

    def test_the_expected_state_goes_in_as_ascii_json(self):
        state = json.loads(self.expected_text)
        state["groups"]["factory-pool"]["repositories"].append("acme/\u2028line")
        text = ra.workflow(json.dumps(state, ensure_ascii=False), self.script)
        self.assertTrue(text.isascii())
        self.assertEqual(json.loads(self.embedded(text, ra.EXPECTED_END)), state)
        # The audit step has its own limit under the job's, so the alarm step still runs after it times out.
        self.assertIn("        timeout-minutes: 8\n", text)

    def test_what_the_workflow_refuses(self):
        expression = "$" + "{{ secrets.X }}"
        state = json.loads(self.expected_text)
        state["groups"]["factory-pool"]["selected_workflows"].append(expression)
        with self.assertRaisesRegex(ValueError, "the expected state can't contain a dollar sign"):
            ra.workflow(json.dumps(state), self.script)
        with self.assertRaisesRegex(ValueError, "the script can't contain"):
            ra.workflow(self.expected_text, self.script + ra.SCRIPT_END)
        with self.assertRaisesRegex(ValueError, "isn't a five-field schedule"):
            ra.workflow(self.expected_text, self.script, cron="hourly")
        with self.assertRaisesRegex(ValueError, "the expected state"):
            ra.workflow("{}", self.script)


class Alarm(unittest.TestCase):
    """The workflow's alarm step, run here with a stand-in for gh."""

    def setUp(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("no PyYAML")
        doc = yaml.safe_load(ra.workflow(json.dumps(expected_of(FakeOrg())), (FACTORY / "runner_audit.py").read_text()))
        self.run_text = doc["jobs"]["audit"]["steps"][1]["run"]
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "bin").mkdir()
        gh = self.root / "bin" / "gh"
        # Each call: its arguments, NUL-separated, then a record separator (bodies hold newlines).
        gh.write_text('#!/usr/bin/env bash\nprintf "%s\\0" "$@" >> "$ALARM_LOG"; printf "\\036" >> "$ALARM_LOG"\n'
                      'if [[ $1 == issue && $2 == list ]]; then echo "$LIST_OUT"; fi\n'
                      'if [[ $1 == issue && $2 == comment ]]; then exit "${COMMENT_RC:-0}"; fi\n')
        gh.chmod(0o755)
        (self.root / "report.txt").write_text("DRIFT group factory-pool: runner rogue (ID 99) not expected\n")

    def tearDown(self):
        self.tmp.cleanup()

    def alarm(self, notify="", list_out="", comment_rc="0"):
        log = self.root / "log"
        log.unlink(missing_ok=True)
        env = {**os.environ, "PATH": f"{self.root / 'bin'}:{os.environ['PATH']}", "RUNNER_TEMP": str(self.root),
               "NOTIFY": notify, "LIST_OUT": list_out, "COMMENT_RC": comment_rc, "ALARM_LOG": str(log),
               "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": "acme/docs", "GITHUB_RUN_ID": "7"}
        r = subprocess.run(["bash", "-eo", "pipefail", "-c", self.run_text], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return [call.split("\0")[:-1] for call in log.read_text().split("\036")[:-1]]

    def test_a_new_alarm_mentions_the_people_named(self):
        calls = self.alarm(notify="alice bob")
        listing, create = calls
        self.assertIn("app/github-actions", listing)  # only the workflow's own issue is commented on
        self.assertEqual(create[:4], ["issue", "create", "--title", ra.ISSUE_TITLE])
        body = create[create.index("--body") + 1]
        self.assertTrue(body.startswith("@alice @bob\n\nRun: https://github.com/acme/docs/actions/runs/7"), body)
        self.assertIn("runner rogue (ID 99) not expected", body)

    def test_an_open_alarm_is_commented_on_and_a_refused_comment_opens_another(self):
        calls = self.alarm(list_out="12")
        self.assertEqual([c[:3] for c in calls[1:]], [["issue", "comment", "12"]])
        calls = self.alarm(list_out="12", comment_rc="1")  # locked, say
        self.assertEqual([c[:2] for c in calls[1:]], [["issue", "comment"], ["issue", "create"]])

    def test_a_failed_search_still_raises_the_alarm(self):
        (self.root / "bin" / "gh").write_text(
            (self.root / "bin" / "gh").read_text().replace('echo "$LIST_OUT"; fi', 'exit 1; fi'))
        calls = self.alarm()
        self.assertEqual(calls[-1][:2], ["issue", "create"])

    def test_a_mention_is_only_logins(self):
        create = self.alarm(notify="x;$(touch pwned) `id`")[-1]
        body = create[create.index("--body") + 1]
        self.assertTrue(body.startswith("@x @touch @pwned @id\n\n"), body)
        self.assertFalse((pathlib.Path.cwd() / "pwned").exists())


class Check(unittest.TestCase):
    def setUp(self):
        self.org = FakeOrg()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / "expected.json"
        self.path.write_text(json.dumps(expected_of(self.org)))

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, env=None):
        out = io.StringIO()
        env = {"AUDIT_APP_CLIENT_ID": "Iv23audit", "AUDIT_APP_KEY": "key"} if env is None else env
        with mock.patch.dict(os.environ, env, clear=False), contextlib.redirect_stdout(out), \
                mock.patch.object(ra, "installation_token", return_value="tok") as token, \
                mock.patch.object(ra, "api", side_effect=lambda method, path, bearer: self.org.get(path)):
            status = ra.main(["check", str(self.path)])
        return status, out.getvalue(), token

    def test_a_check(self):
        status, out, token = self.check()
        self.assertEqual(status, 0)
        self.assertIn("ok: 4 runner groups", out)
        token.assert_called_once_with("acme", "Iv23audit", "key")
        self.org.runners[5].append(runner(99, "rogue", ["factory-prod"]))
        status, out, _ = self.check()
        self.assertEqual(status, 1)
        self.assertIn("DRIFT group factory-pool-app-prod: runner rogue (ID 99) not expected", out)

    def test_no_credentials_or_no_token_fails_closed(self):
        with mock.patch.dict(os.environ, {"AUDIT_APP_CLIENT_ID": "", "AUDIT_APP_KEY": ""}):
            status, out, _ = self.check(env={})
        self.assertEqual(status, 2)
        self.assertIn("no audit App client ID or key", out)
        with mock.patch.object(ra, "installation_token", side_effect=ra.Unreadable("the audit App isn't installed")):
            out = io.StringIO()
            with mock.patch.dict(os.environ, {"AUDIT_APP_CLIENT_ID": "Iv23audit", "AUDIT_APP_KEY": "key"}), \
                    contextlib.redirect_stdout(out):
                self.assertEqual(ra.main(["check", str(self.path)]), 2)
        self.assertIn("isn't installed", out.getvalue())
        self.path.write_text("{not json")
        self.assertEqual(self.check()[0], 2)

    @unittest.skipUnless(shutil.which("openssl"), "needs openssl")
    def test_the_token_is_read_only(self):
        key = subprocess.run(["openssl", "genrsa", "2048"], check=True, capture_output=True, text=True).stdout
        calls = []

        def call(method, path, bearer, body=None):
            calls.append((method, path, body))
            if path == "/orgs/acme/installation":
                return 200, {"id": 31}
            return 201, {"token": "ghs_audit"}

        self.assertEqual(ra.installation_token("acme", "Iv23audit", key, call=call), "ghs_audit")
        self.assertEqual(calls, [("GET", "/orgs/acme/installation", None),
                                 ("POST", "/app/installations/31/access_tokens",
                                  {"permissions": {"organization_self_hosted_runners": "read"}})])
        with self.assertRaisesRegex(ra.Unreadable, "isn't installed on acme"):
            ra.installation_token("acme", "Iv23audit", key, call=lambda *a, **k: (404, None))


if __name__ == "__main__":
    unittest.main()
