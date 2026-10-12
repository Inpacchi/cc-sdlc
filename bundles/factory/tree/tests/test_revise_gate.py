"""Tests for revise_gate.sh: which PRs a revise stage takes, who may ask, and the revision limit. A fake
gh serves fixture responses (applying --jq with jq) and logs every write, so the comments, labels and
outputs are checked exactly."""

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import textwrap
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = FACTORY / "revise_gate.sh"
APP_USER_ID = 339877552
RUN_URL = "https://github.com/o/r/actions/runs/1"

FAKE_GH = textwrap.dedent("""\
    #!/usr/bin/env python3
    # A stand-in for gh: GET requests read the fixture, anything else is logged.
    import json, os, subprocess, sys
    args = sys.argv[1:]
    log = open(os.environ["FAKE_GH_LOG"], "a")
    if args[:2] == ["issue", "edit"]:
        log.write(json.dumps({"call": args, "token": os.environ.get("GH_TOKEN")}) + "\\n")
        sys.exit(0)
    if args[:2] == ["issue", "view"]:
        issue = json.load(open(os.environ["FAKE_GH_FIXTURE"]))["issue"]
        jq = args[args.index("-q") + 1]
        sys.stdout.write(subprocess.run(["jq", "-r", jq], input=json.dumps(issue), capture_output=True, text=True,
                                        check=True).stdout)
        sys.exit(0)
    assert args[0] == "api", args
    method, path, jq, fields = "GET", None, None, {}
    i = 1
    while i < len(args):
        a = args[i]
        if a == "-X":
            method = args[i + 1]; i += 2
        elif a == "--jq":
            jq = args[i + 1]; i += 2
        elif a in ("-f", "-F"):
            k, _, v = args[i + 1].partition("="); fields[k] = v; i += 2
            method = "POST" if method == "GET" else method
        elif a == "--paginate":
            i += 1
        else:
            path = a; i += 1
    if method != "GET":
        log.write(json.dumps({"method": method, "path": path, "fields": fields,
                              "token": os.environ.get("GH_TOKEN")}) + "\\n")
        print("{}")
        sys.exit(0)
    data = json.load(open(os.environ["FAKE_GH_FIXTURE"]))
    if path not in data:
        print("gh: Not Found (HTTP 404)", file=sys.stderr)
        sys.exit(1)
    body = json.dumps(data[path])
    if jq is None:
        print(body)
    else:
        sys.stdout.write(subprocess.run(["jq", "-r", jq], input=body, capture_output=True, text=True,
                                        check=True).stdout)
""")


def comment(body, user_id=APP_USER_ID, kind="Bot"):
    return {"user": {"id": user_id, "type": kind}, "body": body, "created_at": "2026-10-12T00:00:00Z"}


@unittest.skipUnless(shutil.which("jq"), "needs jq")
class ReviseGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.log = self.root / "gh.log"
        self.fixture = self.root / "fixture.json"
        self.output = self.root / "output"
        self.summary = self.root / "summary"
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_GH_LOG": str(self.log),
                    "FAKE_GH_FIXTURE": str(self.fixture), "PR": "5", "REQUESTER": "cd", "RUN_URL": RUN_URL,
                    "GH_REPO": "o/r", "GH_TOKEN": "read-token", "APP_TOKEN": "app-token",
                    "RUNNER_TEMP": str(self.root), "GITHUB_OUTPUT": str(self.output),
                    "GITHUB_STEP_SUMMARY": str(self.summary)}
        self.fresh()

    def fresh(self):
        """A new case: no calls logged, no outputs, the default fixture (an open factory code PR, one
        earlier revision by the App, and markers by others that don't count)."""
        for f in (self.log, self.output, self.summary):
            f.write_text("")
        self.data = {
            "repos/o/r/pulls/5": {"head": {"ref": "factory/7-impl", "sha": "a" * 40, "repo": {"full_name": "o/r"}},
                                  "state": "open", "user": {"id": APP_USER_ID}},
            "repos/o/r/collaborators/cd/permission": {"permission": "admin"},
            "repos/o/r/issues/5/comments": [comment("<!-- factory-revise: 1 -->\nRevised."),
                                            comment("<!-- factory-revise: 2 -->\nby a person", 1, "User"),
                                            comment("<!-- factory-revise: 3 -->\nanother bot", 41898282)],
            "repos/o/r/pulls/5/files": [],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def run_gate(self, kind, limit):
        self.fixture.write_text(json.dumps(self.data))
        return subprocess.run(["bash", str(SCRIPT), kind], env={**self.env, "REVISION_LIMIT": str(limit)},
                              cwd=self.root, capture_output=True, text=True)

    def outputs(self):
        out = {}
        for line in self.output.read_text().splitlines():
            k, _, v = line.partition("=")
            out[k] = v
        return out

    def writes(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def doc_pr(self, ref, files):
        self.data["repos/o/r/pulls/5"]["head"]["ref"] = ref
        self.data["repos/o/r/pulls/5/files"] = [{"filename": f, "status": s} for f, s in files]


class Code(ReviseGate):
    def test_proceeds_with_the_next_revision(self):
        r = self.run_gate("code", 3)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Only the App's own markers count: one earlier revision.
        self.assertEqual(self.outputs(), {"proceed": "true", "issue": "7", "branch": "factory/7-impl",
                                          "base": "a" * 40, "revision": "2"})
        self.assertEqual(self.summary.read_text(), "Revision 2 of 3 for PR #5 (issue #7)\n")
        self.assertEqual(self.writes(), [])

    def test_refuses_what_isnt_an_open_factory_code_pr(self):
        cases = [("head", {"ref": "factory/7-plan", "sha": "a" * 40, "repo": {"full_name": "o/r"}}),
                 ("head", {"ref": "feature/x", "sha": "a" * 40, "repo": {"full_name": "o/r"}}),
                 ("head", {"ref": "factory/7-impl", "sha": "a" * 40, "repo": {"full_name": "fork/r"}}),
                 ("state", "closed"), ("user", {"id": 1})]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                self.fresh()
                self.data["repos/o/r/pulls/5"][key] = value
                r = self.run_gate("code", 3)
                self.assertEqual(r.returncode, 1)
                self.assertIn("::error::PR #5 isn't an open factory code PR", r.stdout)
                self.assertEqual(self.outputs(), {"proceed": "false"})
                self.assertEqual(self.writes(), [])

    def test_a_requester_without_write_access_is_told_and_nothing_runs(self):
        for permission in ("read", "triage", None):
            with self.subTest(permission=permission):
                self.fresh()
                if permission:
                    self.data["repos/o/r/collaborators/cd/permission"] = {"permission": permission}
                else:
                    del self.data["repos/o/r/collaborators/cd/permission"]
                r = self.run_gate("code", 3)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.outputs(), {"proceed": "false"})
                self.assertEqual(self.writes(), [
                    {"method": "DELETE", "path": "repos/o/r/issues/5/labels/factory:revise", "fields": {},
                     "token": "app-token"},
                    {"method": "POST", "path": "repos/o/r/issues/5/comments", "token": "app-token",
                     "fields": {"body": f"Revisions need a reviewer with write access. <sub>factory revise · [run]({RUN_URL})</sub>"}}])

    def test_the_limit_escalates_the_issue(self):
        r = self.run_gate("code", 1)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.outputs(), {"proceed": "false"})
        body = ("**Revision limit reached** (1 for a code PR): no more automatic revisions. Push the changes "
                f"yourself, or close the PR and re-triage the issue. <sub>factory revise · [run]({RUN_URL})</sub>")
        self.assertEqual(self.writes(), [
            {"method": "DELETE", "path": "repos/o/r/issues/5/labels/factory:revise", "fields": {}, "token": "app-token"},
            {"method": "POST", "path": "repos/o/r/issues/5/comments", "fields": {"body": body}, "token": "app-token"},
            {"call": ["issue", "edit", "7", "--add-label", "factory:escalated"], "token": "app-token"}])


class Doc(ReviseGate):
    def test_a_lite_plan(self):
        self.doc_pr("factory/7-plan", [("docs/current_work/sdlc-lite/d12_rate_limits_plan.md", "added"),
                                       ("docs/_index.md", "modified"),
                                       ("docs/current_work/sdlc-lite/d3_old_plan.md", "removed")])
        r = self.run_gate("doc", 5)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.outputs(), {
            "proceed": "true", "issue": "7", "branch": "factory/7-plan", "base": "a" * 40, "revision": "2",
            "stage": "plan", "document": "docs/current_work/sdlc-lite/d12_rate_limits_plan.md",
            "deliverable": "D12", "skill": "sdlc-lite-plan"})
        self.assertEqual(self.summary.read_text(), "Revision 2 of 5 for plan PR #5 (issue #7, "
                         "docs/current_work/sdlc-lite/d12_rate_limits_plan.md, /sdlc-lite-plan)\n")

    def test_a_spec_and_a_full_plan(self):
        for ref, doc, stage in (("factory/7-spec", "docs/current_work/specs/d12a_feeds_spec.md", "spec"),
                                ("factory/7-plan", "docs/current_work/planning/d12a_feeds_plan.md", "plan")):
            with self.subTest(stage=stage):
                self.fresh()
                self.doc_pr(ref, [(doc, "modified")])
                r = self.run_gate("doc", 5)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                out = self.outputs()
                self.assertEqual((out["stage"], out["document"], out["deliverable"], out["skill"]),
                                 (stage, doc, "D12a", "sdlc-plan"))

    def test_needs_exactly_one_document_of_its_stage(self):
        for files in ([], [("docs/current_work/specs/d12_x_spec.md", "added")],
                      [("docs/current_work/sdlc-lite/d12_x_plan.md", "added"),
                       ("docs/current_work/planning/d12_x_plan.md", "added")]):
            with self.subTest(files=files):
                self.fresh()
                self.doc_pr("factory/7-plan", files)
                r = self.run_gate("doc", 5)
                self.assertEqual(r.returncode, 1)
                self.assertIn("::error::PR #5 doesn't add or change exactly one plan document", r.stdout)
                self.assertEqual(self.outputs(), {"proceed": "false"})

    def test_refuses_a_code_pr(self):
        r = self.run_gate("doc", 5)
        self.assertEqual(r.returncode, 1)
        self.assertIn("::error::PR #5 isn't an open factory spec or plan PR", r.stdout)

    def test_the_limit_points_at_an_interactive_session(self):
        self.doc_pr("factory/7-spec", [("docs/current_work/specs/d12_x_spec.md", "added")])
        r = self.run_gate("doc", 1)
        self.assertEqual(r.returncode, 0, r.stderr)
        body = ("**Revision limit reached** (1 for a spec PR): no more automatic revisions. A document that needs "
                "another round usually needs a conversation: continue in an interactive `sdlc-plan` session on "
                "`factory/7-spec` (it can read this review), push the changes yourself, or close the PR to stop. "
                f"<sub>factory revise · [run]({RUN_URL})</sub>")
        self.assertEqual(self.writes()[1], {"method": "POST", "path": "repos/o/r/issues/5/comments",
                                            "fields": {"body": body}, "token": "app-token"})
        self.assertEqual(self.writes()[2]["call"], ["issue", "edit", "7", "--add-label", "factory:escalated"])


class Usage(unittest.TestCase):
    def test_unknown_kind(self):
        r = subprocess.run(["bash", str(SCRIPT), "other"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
