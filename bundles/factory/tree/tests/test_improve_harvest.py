"""Tests for improve_harvest.py: the window, trust, each signal, the ledger rebuilt from report issues and CD's
replies, and the metrics records, against a fake GitHub API."""

import datetime as dt
import io
import json
import pathlib
import sys
import unittest
import zipfile

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import improve_harvest as ih  # noqa: E402
import improve_report as ir  # noqa: E402

REPO = "o/r"
APP = {"login": "z-software-factory[bot]", "id": ih.APP_USER_ID, "type": "Bot"}
LEGACY = {"login": "github-actions[bot]", "id": ih.LEGACY_BOT_ID, "type": "Bot"}
CD = {"login": "cd", "id": 1, "type": "User"}
READER = {"login": "reader", "id": 2, "type": "User"}
NOW = dt.datetime(2026, 10, 18, 22, 23, tzinfo=dt.timezone.utc)
IN = "2026-10-15T10:00:00Z"


class FakeApi:
    def __init__(self, data, raw=None, perms=None):
        self.data, self.raw_data = data, raw or {}
        self.perms = perms if perms is not None else {"cd": "admin", "reader": "read"}
        self.calls = []

    def _find(self, path):
        self.calls.append(path)
        base = path.split("?", 1)[0]
        for key in (path, base):
            if key in self.data:
                return self.data[key]
        return None

    def get(self, path):
        if "/collaborators/" in path:
            self.calls.append(path)
            login = path.split("/collaborators/")[1].split("/")[0]
            perm = self.perms.get(login)
            if perm == "error":
                raise RuntimeError("gh api: HTTP 500")
            if perm is None:
                raise RuntimeError("gh api: HTTP 404")
            return {"permission": perm}
        found = self._find(path)
        return found if found is not None else {}

    def list(self, path, key=None):
        found = self._find(path)
        return list(found or [])

    def raw(self, path):
        return self.raw_data[path]


def comment(cid, user, at, body, **kw):
    return {"id": cid, "user": user, "created_at": at, "body": body, "html_url": f"https://github.com/{REPO}/issues/1#c{cid}",
            **kw}


def issue(n, updated=IN, user=CD, body="", pr=False):
    out = {"number": n, "user": user, "updated_at": updated, "body": body, "html_url": f"https://github.com/{REPO}/issues/{n}"}
    if pr:
        out["pull_request"] = {}
    return out


def harvest(data, since="", until="2026-10-18T22:23:00Z", **kw):
    api = FakeApi(data, **kw)
    h = ih.Harvest(REPO, api)
    return h.harvest(since, until, now=NOW), api, h


def kinds(digest, kind):
    return [s for s in digest["signals"] if s["kind"] == kind]


TRIAGE = '<!-- factory-triage: {"state":"ready-to-plan","tier":"lite","estimate":{},"advisor":"none"} -->\nReady.'


class Clauses(unittest.TestCase):
    def test_grammar(self):
        self.assertEqual(ih.clauses("accept 1 3 · reject 2: not worth it · defer 4"),
                         [("accepted", [1, 3], ""), ("rejected", [2], "not worth it"), ("deferred", [4], "")])
        self.assertEqual(ih.clauses("Accepted 1, 3 and 4\nrejected 5 - noise"),
                         [("accepted", [1, 3, 4], ""), ("rejected", [5], "noise")])
        self.assertEqual(ih.clauses("**accept 2**; thanks"), [("accepted", [2], "")])

    def test_prose_is_not_a_decision(self):
        self.assertEqual(ih.clauses("I accept that 1 is odd"), [])
        self.assertEqual(ih.clauses("Looks good, will read later."), [])


class Marker(unittest.TestCase):
    def item(self, **kw):
        base = {"n": 1, "fp": "0123456789", "s": "factory-process", "r": "cd", "sev": "high", "t": "T", "p": "a/b", "e": ["x:1"]}
        base.update(kw)
        return base

    def test_round_trip_with_markup_in_text(self):
        state = {"v": 1, "week": "2026-W42", "since": "2026-10-11T00:00:00Z", "until": "2026-10-18T22:23:00Z", "cost": 3.5,
                 "items": [self.item(t="Close --> <!-- & stuff")]}
        text = ir.marker(state) + "\nbody"
        self.assertNotIn("-->", text.split("\n")[0][:-3])
        parsed = ih.report_marker(text)
        self.assertEqual(parsed["items"][0]["t"], "Close --> <!-- & stuff")
        self.assertEqual((parsed["week"], parsed["cost"], parsed["until"]), ("2026-W42", 3.5, "2026-10-18T22:23:00Z"))

    def test_items_stored_under_the_frameworks_old_name_read_as_z_sdlc(self):
        # Reports from before the rename (#58) store the framework section and route as cc-sdlc.
        parsed = ih.report_marker(ir.marker({"week": "2026-W41", "until": "2026-10-12T01:35:36Z",
                                             "items": [self.item(s="cc-sdlc", r="cc-sdlc"), self.item(n=2)]}))
        self.assertEqual([(i["s"], i["r"]) for i in parsed["items"]], [("z-sdlc", "z-sdlc"), ("factory-process", "cd")])

    def test_bad_items_and_markers(self):
        good, bad = self.item(), self.item(n=2, fp="nothex!!!!")
        parsed = ih.report_marker(ir.marker({"week": "2026-W42", "until": "x", "items": [good, bad]}))
        self.assertEqual([i["n"] for i in parsed["items"]], [1])
        self.assertIsNone(parsed["until"])
        self.assertIsNone(ih.report_marker("text first\n" + ir.marker({"week": "2026-W42", "items": []})))
        self.assertIsNone(ih.report_marker("<!-- factory-improve: {not json} -->"))


class Window(unittest.TestCase):
    def reports(self, until):
        return [{"until": until}]

    def test_catch_up_from_the_last_report(self):
        h = ih.Harvest(REPO, FakeApi({}))
        since, until, source, capped = h.window("", "", self.reports("2026-10-04T22:23:00Z"), NOW)
        self.assertEqual((ih.stamp(since), source, capped), ("2026-10-04T22:23:00Z", "last-report", False))

    def test_default_week_and_cap(self):
        h = ih.Harvest(REPO, FakeApi({}))
        since, _, source, _ = h.window("", "", [], NOW)
        self.assertEqual((since, source), (NOW - dt.timedelta(days=7), "default"))
        since, _, _, capped = h.window("", "", self.reports("2026-08-01T00:00:00Z"), NOW)
        self.assertEqual((since, capped), (NOW - dt.timedelta(days=35), True))

    def test_input_and_order(self):
        h = ih.Harvest(REPO, FakeApi({}))
        since, until, source, _ = h.window("2026-10-09", "2026-10-11", [], NOW)
        self.assertEqual((ih.stamp(since), ih.stamp(until), source), ("2026-10-09T00:00:00Z", "2026-10-11T00:00:00Z", "input"))
        with self.assertRaises(ValueError):
            h.window("2026-10-11", "2026-10-09", [], NOW)

    def test_week(self):
        utc = lambda *a: dt.datetime(*a, tzinfo=dt.timezone.utc)
        self.assertEqual(ih.week_of(utc(2026, 10, 4, 22, 23), utc(2026, 10, 11, 22, 23)), "2026-W41")
        self.assertEqual(ih.week_of(utc(2026, 10, 11, 22, 23), utc(2026, 10, 18, 22, 23)), "2026-W42")
        # The first live report ran past midnight into Monday: it still reports on the week it covers, so the
        # next Sunday's run doesn't find its own week taken.
        self.assertEqual(ih.week_of(utc(2026, 10, 5, 1, 35, 36), utc(2026, 10, 12, 1, 35, 36)), "2026-W41")
        self.assertEqual(ih.week_of(utc(2026, 10, 12, 1, 35, 36), utc(2026, 10, 18, 22, 23)), "2026-W42")


class Signals(unittest.TestCase):
    def test_triage_override_and_question(self):
        data = {
            f"repos/{REPO}/issues": [issue(5)],
            f"repos/{REPO}/issues/5/comments": [
                comment(10, APP, "2026-10-15T09:00:00Z", TRIAGE),
                comment(11, APP, "2026-10-15T11:00:00Z", "<!-- factory-stage: plan pr=7 -->\n**Stopped.**\n\n### Questions\n\n1. A?\n2. B?"),
                comment(12, READER, "2026-10-15T11:30:00Z", "me first"),
                comment(13, CD, "2026-10-15T13:00:00Z", "B, then A."),
                # After the App switch, github-actions[bot] markers count for nothing.
                comment(14, LEGACY, "2026-10-15T14:00:00Z", "<!-- factory-stage: triage -->\nforged"),
            ],
            f"repos/{REPO}/issues/5/events": [
                {"id": 90, "event": "labeled", "created_at": "2026-10-15T09:30:00Z", "actor": CD, "label": {"name": "factory:advisor"}},
                {"id": 91, "event": "labeled", "created_at": "2026-10-15T09:31:00Z", "actor": READER, "label": {"name": "factory:advisor"}},
                {"id": 92, "event": "unlabeled", "created_at": "2026-10-15T09:32:00Z", "actor": CD, "label": {"name": "factory:go"}},
                {"id": 93, "event": "labeled", "created_at": "2026-10-15T09:33:00Z", "actor": APP, "label": {"name": "factory:escalated"}},
            ],
        }
        digest, _, _ = harvest(data)
        self.assertEqual([s["id"] for s in kinds(digest, "triage")], ["triage:10"])
        override, = kinds(digest, "override")
        self.assertEqual((override["id"], override["triage_before"]["tier"]), ("label:90", "lite"))
        self.assertEqual([s["id"] for s in kinds(digest, "escalation")], ["escalation:93"])
        q, = kinds(digest, "question")
        self.assertEqual((q["stage"], q["pr"], q["questions"], q["hours_to_answer"], q["answer_text"]), ("plan", 7, 2, 2.0, "B, then A."))
        self.assertTrue(q["text"].startswith("**Stopped.**"))
        self.assertFalse(digest["empty"])

    def test_first_triage_label_is_the_opt_in(self):
        data = {f"repos/{REPO}/issues": [issue(6)],
                f"repos/{REPO}/issues/6/events": [{"id": 1, "event": "labeled", "created_at": IN, "actor": CD,
                                                   "label": {"name": "factory:triage"}}]}
        digest, _, _ = harvest(data)
        self.assertEqual(digest["signals"], [])
        self.assertTrue(digest["empty"])

    def test_legacy_bot_before_the_switch(self):
        data = {f"repos/{REPO}/issues": [issue(5, updated="2026-10-09T10:00:00Z")],
                f"repos/{REPO}/issues/5/comments": [comment(10, LEGACY, "2026-10-09T08:00:00Z", TRIAGE)]}
        digest, _, _ = harvest(data, since="2026-10-09", until="2026-10-10")
        self.assertEqual([s["id"] for s in kinds(digest, "triage")], ["triage:10"])

    def pr(self, n, head, created, closed=None, merged=None, body=""):
        return {"number": n, "user": APP, "head": {"ref": head}, "created_at": created, "closed_at": closed, "merged_at": merged,
                "body": body, "html_url": f"https://github.com/{REPO}/pull/{n}"}

    def test_pr_outcomes_reviews_and_revisions(self):
        pulls = [self.pr(20, "factory/9-impl", "2026-10-13T10:00:00Z", "2026-10-13T12:00:00Z"),
                 self.pr(21, "factory/9-impl", "2026-10-14T10:00:00Z", "2026-10-16T12:00:00Z", "2026-10-16T12:00:00Z",
                         "- **Models and cost:** claude-sonnet-5-5; $4.20 at API rates; 30 turns"),
                 self.pr(22, "factory/8-impl", "2026-10-13T10:00:00Z", "2026-10-13T20:00:00Z"),
                 self.pr(23, "factory/8-impl-opus", "2026-10-13T10:05:00Z", "2026-10-13T20:00:00Z", "2026-10-13T20:00:00Z"),
                 self.pr(24, "factory/7-plan", "2026-10-13T10:00:00Z", "2026-10-14T10:00:00Z")]
        data = {f"repos/{REPO}/issues": [issue(p["number"], pr=True) for p in pulls],
                f"repos/{REPO}/pulls": pulls,
                f"repos/{REPO}/pulls/21/reviews": [
                    {"id": 70, "user": CD, "state": "CHANGES_REQUESTED", "submitted_at": "2026-10-15T09:00:00Z", "body": "Fix X.",
                     "html_url": f"https://github.com/{REPO}/pull/21#r70"},
                    {"id": 71, "user": READER, "state": "CHANGES_REQUESTED", "submitted_at": "2026-10-15T09:10:00Z", "body": "No."}],
                f"repos/{REPO}/pulls/21/comments": [{"pull_request_review_id": 70, "path": "a.py", "body": "here"}],
                f"repos/{REPO}/issues/21/comments": [comment(
                    80, APP, "2026-10-15T10:00:00Z",
                    "<!-- factory-revise: 1 -->\n\n**Revision 1 of 3:** x\n\n### What you asked for\n\n"
                    "1. **Fix X**: Done. ok\n2. **Fix Y**: Declined. out of scope\n3. **Fix Z**: Needs your call. which?\n")],
                f"repos/{REPO}/issues/24/comments": [comment(81, CD, "2026-10-14T09:00:00Z", "Wrong approach; plan the cache first.")]}
        for p in pulls:
            data[f"repos/{REPO}/pulls/{p['number']}"] = p
        digest, _, _ = harvest(data)
        outcomes = {s["pr"]: s["outcome"] for s in kinds(digest, "pr-outcome")}
        self.assertEqual(outcomes, {20: "replaced", 21: "merged", 22: "comparison", 23: "merged", 24: "rejected"})
        rejected, = [s for s in kinds(digest, "pr-outcome") if s["pr"] == 24]
        self.assertEqual((rejected["text"], rejected["stage"], rejected["issue"]), ("Wrong approach; plan the cache first.", "plan", 7))
        merged, = [s for s in kinds(digest, "pr-outcome") if s["pr"] == 21]
        self.assertEqual((merged["cost"], merged["turns"], merged["revisions"], merged["changes_requested"]), (4.2, 30, 1, 1))
        review, = kinds(digest, "review")
        self.assertEqual((review["id"], review["inline_comments"], review["state"]), ("review:70", 1, "changes_requested"))
        self.assertIn("[a.py] here", review["text"])
        revision, = kinds(digest, "revision")
        self.assertEqual(revision["answers"], {"done": 1, "declined": 1, "needs_your_call": 1})
        self.assertEqual(revision["text"], "out of scope\nwhich?")

    def test_follow_ups_reactions_failures_commits(self):
        data = {
            f"repos/{REPO}/issues": [issue(30)],
            f"repos/{REPO}/issues/30/comments": [comment(
                40, APP, IN, "**Follow-ups from PR #33:**\n\n- #35 (F1): filed, triage started\n\nUnchecked at merge, so not filed: F2, F4.",
                reactions={"total_count": 2})],
            f"repos/{REPO}/issues/comments/40/reactions": [
                {"id": 1, "content": "-1", "user": CD, "created_at": IN}, {"id": 2, "content": "+1", "user": READER, "created_at": IN}],
            f"repos/{REPO}/actions/runs": [
                {"id": 500, "run_attempt": 2, "path": ".github/workflows/factory-plan.yml", "conclusion": "failure", "created_at": IN,
                 "display_title": "factory-plan #30", "event": "workflow_dispatch", "html_url": f"https://github.com/{REPO}/actions/runs/500"},
                {"id": 501, "path": ".github/workflows/factory-plan.yml", "conclusion": "skipped", "created_at": IN},
                {"id": 502, "path": ".github/workflows/ci.yml", "conclusion": "failure", "created_at": IN},
                {"id": 503, "path": ".github/workflows/factory-triage.yml", "conclusion": "success", "created_at": IN}],
            f"repos/{REPO}/actions/runs/500/attempts/2/jobs": [
                {"name": "plan", "conclusion": "failure", "steps": [{"name": "Plan", "conclusion": "failure"}, {"name": "x", "conclusion": "success"}]},
                {"name": "claim", "conclusion": "success", "steps": []}],
            f"repos/{REPO}/commits": [{"sha": "a" * 40, "html_url": f"https://github.com/{REPO}/commit/aaa",
                                       "commit": {"message": "fix(factory): x\n\nbody", "committer": {"date": IN}}},
                                      {"sha": "b" * 40, "commit": {"message": "feat(web): y", "committer": {"date": IN}}}],
            f"repos/{REPO}/commits/{'a' * 40}": {"files": [{"filename": ".github/factory/a.py"}, {"filename": "web/x.ts"}]},
            f"repos/{REPO}/commits/{'b' * 40}": {"files": [{"filename": "web/x.ts"}]},
        }
        digest, _, _ = harvest(data)
        f, = kinds(digest, "follow-ups")
        self.assertEqual((f["pr"], f["filed"], f["unchecked"]), (33, 1, ["F2", "F4"]))
        self.assertEqual([(r["id"], r["content"]) for r in kinds(digest, "reaction")], [("reaction:1", "-1")])
        failure, = kinds(digest, "failure")
        self.assertEqual((failure["id"], failure["issue"], failure["failing"]), ("failure:500:2", 30, [{"job": "plan", "steps": ["Plan"]}]))
        self.assertEqual(digest["runs"], {"factory-plan": {"failure": 1}, "factory-triage": {"success": 1}})
        commit, = kinds(digest, "commit")
        self.assertEqual((commit["id"], commit["files"], commit["text"]), ("commit:" + "a" * 12, [".github/factory/a.py"], "fix(factory): x"))

    def test_commits_alone_are_an_empty_window(self):
        data = {f"repos/{REPO}/commits": [{"sha": "a" * 40, "commit": {"message": "x", "committer": {"date": IN}}}],
                f"repos/{REPO}/commits/{'a' * 40}": {"files": [{"filename": ".claude/x"}]}}
        digest, _, _ = harvest(data)
        self.assertEqual(digest["counts"], {"commit": 1})
        self.assertTrue(digest["empty"])


class Trust(unittest.TestCase):
    def test_not_a_collaborator_is_a_plain_no(self):
        h = ih.Harvest(REPO, FakeApi({}, perms={}))
        self.assertFalse(h.is_cd(CD))
        self.assertEqual(h.trust_errors, 0)

    def test_a_failed_check_is_counted(self):
        h = ih.Harvest(REPO, FakeApi({}, perms={"cd": "error"}))
        self.assertFalse(h.is_cd(CD))
        self.assertEqual(h.trust_errors, 1)

    def test_bots_and_cached(self):
        api = FakeApi({})
        h = ih.Harvest(REPO, api)
        self.assertFalse(h.is_cd(APP))
        self.assertTrue(h.is_cd(CD) and h.is_cd(CD))
        self.assertEqual(sum("/collaborators/" in c for c in api.calls), 1)
        self.assertTrue(ih.Harvest.is_factory({"user": APP, "created_at": IN}))
        self.assertFalse(ih.Harvest.is_factory({"user": LEGACY, "created_at": IN}))
        self.assertFalse(ih.Harvest.is_factory({"user": {**APP, "type": "User"}, "created_at": IN}))


class Ledger(unittest.TestCase):
    def report(self, n, week, until, items, cost=None):
        return issue(n, user=APP, body=ir.marker({"v": 1, "week": week, "until": until, "cost": cost, "items": items}) + "\nbody")

    def item(self, n, fp, **kw):
        base = {"n": n, "fp": fp, "s": "factory-process", "r": "cd", "sev": "medium", "t": f"T{n}", "p": "a", "e": [f"x:{n}"]}
        base.update(kw)
        return base

    def test_decisions_and_window(self):
        data = {
            f"repos/{REPO}/issues": [
                self.report(50, "2026-W40", "2026-10-04T22:23:00Z", [self.item(1, "a" * 10), self.item(2, "b" * 10), self.item(3, "c" * 10)]),
                self.report(60, "2026-W41", "2026-10-11T22:23:00Z", [self.item(1, "b" * 10, e=["x:9"]), self.item(2, "d" * 10)], cost=7.5),
                # Not the App's: never a report.
                issue(70, user=CD, body=ir.marker({"week": "2026-W41", "items": [self.item(1, "e" * 10)]}))],
            f"repos/{REPO}/issues/50/comments": [comment(1, CD, "2026-10-05T10:00:00Z", "accept 1 · reject 2: no"),
                                                 comment(2, READER, "2026-10-05T11:00:00Z", "reject 1")],
            f"repos/{REPO}/issues/60/comments": [comment(3, CD, "2026-10-12T10:00:00Z", "defer 1: after D11")],
        }
        digest, _, _ = harvest(data)
        ledger = {e["fingerprint"]: e for e in digest["ledger"]}
        self.assertEqual(set(ledger), {"a" * 10, "b" * 10, "c" * 10, "d" * 10})
        self.assertEqual(ledger["a" * 10]["status"], "accepted")
        self.assertEqual((ledger["b" * 10]["status"], ledger["b" * 10]["reason"]), ("deferred", "after D11"))
        self.assertEqual((ledger["b" * 10]["evidence"], ledger["b" * 10]["last_report"]), (["x:2", "x:9"], 60))
        self.assertEqual(ledger["c" * 10]["status"], "open")
        self.assertEqual(digest["window"]["since"], "2026-10-11T22:23:00Z")
        self.assertEqual(digest["previous_report"]["number"], 60)
        self.assertEqual(digest["previous_report"]["cost"], 7.5)
        decision, = kinds(digest, "decision")
        self.assertEqual((decision["fingerprint"], decision["status"], decision["report"]), ("b" * 10, "deferred", 60))


class Metrics(unittest.TestCase):
    def zip(self, record):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("metrics.json", json.dumps(record))
        return buf.getvalue()

    def test_records(self):
        rec = {"v": 1, "stage": "plan", "run_id": 5, "run_attempt": 1, "cost": 3.0, "text": "agent words"}
        arts = [{"id": 1, "created_at": IN, "expired": False}, {"id": 2, "created_at": IN, "expired": False},
                {"id": 3, "created_at": "2026-09-01T00:00:00Z", "expired": False}, {"id": 4, "created_at": IN, "expired": True},
                {"id": 5, "created_at": IN, "expired": False}]
        raw = {f"repos/{REPO}/actions/artifacts/{i}/zip": self.zip(rec) for i in (1, 2, 3, 4)}
        raw[f"repos/{REPO}/actions/artifacts/5/zip"] = b"not a zip"
        digest, _, _ = harvest({f"repos/{REPO}/actions/artifacts": arts}, raw=raw)
        self.assertEqual(len(digest["metrics"]), 1)
        self.assertNotIn("text", digest["metrics"][0])
        self.assertEqual(digest["metrics"][0]["cost"], 3.0)
        self.assertFalse(digest["empty"])


if __name__ == "__main__":
    unittest.main()
