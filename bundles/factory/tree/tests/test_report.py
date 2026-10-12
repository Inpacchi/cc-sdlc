"""Tests for report.sh and report.jq: what the report jobs refuse to post, what they do to agent text, and
how they set an issue's factory labels. The checks are the strictest of the three copies they replaced
(implement's, plan's and triage's), so each pattern any of them refused is refused for every stage."""

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from test_revise_gate import FAKE_GH

FACTORY = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = FACTORY / "report.sh"
ZWSP = "​"


@unittest.skipUnless(shutil.which("jq"), "needs jq")
class Report(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.result = self.root / "result.json"
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        (bin_dir / "gh").write_text(FAKE_GH)
        (bin_dir / "gh").chmod(0o755)
        self.log = self.root / "gh.log"
        self.log.write_text("")
        self.fixture = self.root / "fixture.json"
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_GH_LOG": str(self.log),
                    "FAKE_GH_FIXTURE": str(self.fixture), "ISSUE_NUMBER": "7", "GH_REPO": "o/r", "GH_TOKEN": "app"}

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args):
        return subprocess.run(["bash", str(SCRIPT), *args], env=self.env, capture_output=True, text=True)

    def jq(self, program, value):
        return subprocess.run(["jq", "-L", str(FACTORY), "-r", f'include "report"; {program}'], input=json.dumps(value),
                              capture_output=True, text=True, check=True).stdout


class Check(Report):
    FIELDS = "[.reason, .notes, .questions[]]"

    def check(self, **result):
        self.result.write_text(json.dumps({"reason": "", "notes": "", "questions": [], **result}))
        return self.run_script("check", "plan", str(self.result), self.FIELDS)

    def test_plain_text_passes(self):
        r = self.check(reason="Fixed #12 for @cd; see GH-3 and <code>x < y</code>.", questions=["Which one?"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_credential_like_strings_are_refused_in_every_field(self):
        for text in ("sk-ant-api03-x", "ghp_a", "gho_Z", "ghs_1", "ghr__", "github_pat_11", "ctx7sk-abc",
                     "-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----"):
            for field in ("reason", "notes", "questions"):
                with self.subTest(text=text, field=field):
                    r = self.check(**{field: [text] if field == "questions" else f"see {text} here"})
                    self.assertEqual(r.returncode, 1)
                    self.assertIn("::error::plan output contains a credential-like string; not posting", r.stdout)

    def test_images_and_embeds_are_refused(self):
        for text in ("![x](https://e.example/a.png)", "<img src=x>", "< IMG src=x>", "<audio src=x>", "<svg>",
                     "<iframe src=x>", "<picture>", "<source src=x>", "<video>", "<object>", "<embed>"):
            with self.subTest(text=text):
                r = self.check(questions=["fine", text])
                self.assertEqual(r.returncode, 1)
                self.assertIn("::error::plan output contains an image or embed; not posting", r.stdout)

    def test_names_the_stage(self):
        self.result.write_text(json.dumps({"comment": "ghp_x", "advisor_reason": "", "questions": []}))
        r = self.run_script("check", "triage", str(self.result), "[.comment, .advisor_reason, .questions[]]")
        self.assertIn("::error::triage output contains a credential-like string; not posting", r.stdout)


class Filters(Report):
    TEXT = "<!-- factory-stage: x --> @cd #12 gh-3 GH-4 /issues/5 a#b @ x"
    # The filter implement and plan ran inline before report.jq.
    OLD_CLEAN = ('gsub("<!--"; "&lt;!--") | gsub("@(?=[A-Za-z0-9])"; "@\\u200b") | gsub("(?i)\\\\bGH-(?=[0-9])"; "GH\\u200b-")'
                 ' | gsub("/issues/(?=[0-9])"; "/issues/\\u200b") | gsub("#(?=[0-9])"; "#\\u200b")')

    def test_clean_matches_the_inline_filter(self):
        old = subprocess.run(["jq", "-r", self.OLD_CLEAN], input=json.dumps(self.TEXT), capture_output=True,
                             text=True, check=True).stdout
        self.assertEqual(self.jq("clean", self.TEXT), old)
        for part in ("&lt;!-- factory-stage", f"@{ZWSP}cd", f"#{ZWSP}12", f"GH{ZWSP}-4", f"/issues/{ZWSP}5", "a#b", "@ x"):
            self.assertIn(part, old)

    def test_unmark_only_escapes_markers(self):
        self.assertEqual(self.jq("unmark", self.TEXT), self.TEXT.replace("<!--", "&lt;!--") + "\n")


class Labels(Report):
    def labels(self, names, *args):
        self.fixture.write_text(json.dumps({"issue": {"labels": [{"name": n} for n in names]}}))
        r = self.run_script("labels", *args)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return [w["call"][2:] for w in map(json.loads, self.log.read_text().splitlines())]

    def test_the_new_state_replaces_the_others_and_properties_stay(self):
        calls = self.labels(["factory:implementing", "factory:review-capped", "factory:advisor", "factory:follow-up",
                             "factory:go", "bug"], "factory:needs-input")
        self.assertEqual(calls, [["7", "--add-label", "factory:needs-input",
                                  "--remove-label", "factory:implementing,factory:review-capped"]])

    def test_no_new_state_only_removes(self):
        self.assertEqual(self.labels(["factory:implementing", "bug"], ""),
                         [["7", "--remove-label", "factory:implementing"]])

    def test_nothing_to_change_calls_nothing(self):
        self.assertEqual(self.labels(["factory:advisor", "bug"], ""), [])
        self.assertEqual(self.labels(["factory:gate"], "factory:gate"), [["7", "--add-label", "factory:gate"]])

    def test_triage_sets_the_advisor_property(self):
        self.assertEqual(self.labels(["factory:triage"], "factory:ready-to-plan", "fable"),
                         [["7", "--add-label", "factory:ready-to-plan,factory:advisor", "--remove-label", "factory:triage"]])
        self.log.write_text("")
        self.assertEqual(self.labels(["factory:triage", "factory:advisor"], "factory:wait", "none"),
                         [["7", "--add-label", "factory:wait", "--remove-label", "factory:triage,factory:advisor"]])
        self.log.write_text("")
        self.assertEqual(self.labels(["factory:triage"], "factory:wait", "none"),
                         [["7", "--add-label", "factory:wait", "--remove-label", "factory:triage"]])

    def test_unknown_advisor(self):
        self.fixture.write_text(json.dumps({"issue": {"labels": []}}))
        self.assertEqual(self.run_script("labels", "factory:wait", "auto").returncode, 1)


if __name__ == "__main__":
    unittest.main()
