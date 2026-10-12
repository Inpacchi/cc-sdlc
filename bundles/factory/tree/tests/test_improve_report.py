"""Tests for improve_report.py: refusing a bad analysis, checking evidence, fingerprints and the ledger, the
report's fixed structure, and escaping agent text. Also pins the analyze job's tool policy to triage's."""

import hashlib
import json
import pathlib
import shlex
import sys
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import improve_harvest as ih  # noqa: E402
import improve_report as ir  # noqa: E402

REPO = "o/r"
SCHEMA = json.loads((FACTORY / "improve.schema.json").read_text())


def signal(sid, kind="review", **kw):
    return {"id": sid, "kind": kind, "at": "2026-10-15T00:00:00Z", "pr": 3, "issue": 2,
            "url": f"https://github.com/{REPO}/pull/3#{sid.replace(':', '-')}", **kw}


def digest(signals=(), ledger=(), metrics=(), runs=None, previous=None):
    return {"kind": "factory-digest", "version": 1, "repo": REPO,
            "window": {"since": "2026-10-11T22:23:00Z", "until": "2026-10-18T22:23:00Z", "week": "2026-W42", "capped": False},
            "counts": {}, "runs": runs or {}, "metrics": list(metrics), "signals": list(signals), "ledger": list(ledger),
            "previous_report": previous}


def proposal(title="Fix the thing", **kw):
    p = {"section": "factory-process", "route": "cd", "severity": "medium", "title": title, "target": ".github/x.yml",
         "change": "Change it.", "why": "It broke.", "effect": "It works.", "evidence": ["review:1"], "matches": ""}
    p.update(kw)
    return p


def result(*proposals, summary="The week in a line."):
    return {"status": "awaiting-approval", "reason": "", "summary": summary, "proposals": list(proposals), "notes": ""}


def entry(fp, status="open", **kw):
    e = {"fingerprint": fp, "title": f"Old {fp[:3]}", "target": "a/b", "section": "sdlc-content", "route": "hygiene",
         "severity": "low", "status": status, "reason": "", "decided_at": None, "first_week": "2026-W40",
         "last_week": "2026-W41", "last_report": 60, "evidence": ["review:old"]}
    e.update(kw)
    return e


def state(body):
    return ih.report_marker(body)


class Check(unittest.TestCase):
    def test_schema_tokens_embeds_and_status(self):
        ir.check(result(proposal()), SCHEMA)
        bad = result(proposal())
        del bad["proposals"][0]["matches"]
        with self.assertRaises(ir.Refused):
            ir.check(bad, SCHEMA)
        with self.assertRaises(ir.Refused):
            ir.check(result(proposal(change="x" * 501)), SCHEMA)
        with self.assertRaises(ir.Refused):
            ir.check(result(proposal(why="key ghp_" + "a" * 30)), SCHEMA)
        with self.assertRaises(ir.Refused):
            ir.check(result(proposal(effect="see ![x](http://e/x.png)")), SCHEMA)
        failed = result()
        failed.update(status="failed", reason="no digest")
        with self.assertRaises(ir.Refused):
            ir.check(failed, SCHEMA)

    def test_schema_has_no_apostrophes(self):
        self.assertNotIn("'", (FACTORY / "improve.schema.json").read_text())


class Fingerprint(unittest.TestCase):
    def test_stable_and_normalized(self):
        a = ir.fingerprint("z-sdlc", "skills/x/SKILL.md", "Fix  The thing")
        self.assertEqual(a, ir.fingerprint("z-sdlc", "Skills/X/SKILL.md ", "fix the thing"))
        self.assertNotEqual(a, ir.fingerprint("project", "skills/x/SKILL.md", "Fix the thing"))
        self.assertRegex(a, r"^[0-9a-f]{10}$")

    def test_the_renamed_framework_section_keeps_its_fingerprints(self):
        # The framework was renamed from cc-sdlc to z-sdlc: a proposal's fingerprint is the one an earlier
        # report stored under the old name.
        old = hashlib.sha256("cc-sdlc|skills/x/skill.md|fix the thing".encode()).hexdigest()[:10]
        self.assertEqual(ir.fingerprint("z-sdlc", "skills/x/SKILL.md", "fix the thing"), old)
        self.assertEqual(ir.fingerprint("cc-sdlc", "skills/x/SKILL.md", "fix the thing"), old)


class Render(unittest.TestCase):
    def test_evidence_is_checked(self):
        d = digest([signal("review:1"), signal("failure:9:1", "failure", workflow="factory-plan", pr=None)])
        r = result(proposal(evidence=["review:1", "made:up"]), proposal("Ghost", evidence=["made:up"]))
        _, body = ir.render(d, r, "https://run")
        self.assertIn("Fix the thing", body)
        self.assertIn("[review on PR 3](https://github.com/o/r/pull/3#review-1)", body)
        self.assertIn("1 proposal cited no signal the harvest produced, so it was dropped: Ghost.", body)
        self.assertIn("2 evidence ids the harvest didn't produce were removed", body)
        items = state(body)["items"]
        self.assertEqual([(i["n"], i["e"]) for i in items], [(1, ["review:1"])])

    def test_headline_cap_sections_and_ranking(self):
        sigs = [signal(f"review:{i}") for i in range(1, 9)]
        props = [proposal(f"P{i}", evidence=[f"review:{i}"], severity="low") for i in range(1, 7)]
        props.append(proposal("Big", evidence=["review:7", "review:8"], severity="high", section="z-sdlc", route="z-sdlc"))
        _, body = ir.render(digest(sigs), result(*props), "https://run")
        self.assertIn("**1. Big** · High · For z-sdlc · carry to z-sdlc", body)
        top = body.split("### Top items")[1].split("### By section")[0]
        self.assertEqual(top.count("- **Where:**"), 5)
        sections = body.split("### By section")[1]
        self.assertIn("- **6. P5** · Low", sections)
        self.assertIn("- **7. P6** · Low", sections)
        self.assertIn("#### SDLC content\n\nNothing to action.", sections)
        self.assertIn("- Items 2, 3, 4, 5 above.", sections)
        self.assertEqual(len(state(body)["items"]), 7)

    def test_nothing_needs_action(self):
        _, body = ir.render(digest([signal("review:1")]), result(summary="Quiet week."), "https://run")
        self.assertIn("**Nothing needs action this week.** Quiet week\\.", body)
        self.assertIn("Nothing to action in any section", body)
        self.assertNotIn("Your call", body)
        self.assertEqual(state(body)["items"], [])

    def test_earlier_proposals_are_not_re_proposed(self):
        fp_open, fp_rej, fp_quiet = "a" * 10, "b" * 10, "c" * 10
        ledger = [entry(fp_open), entry(fp_rej, "rejected", reason="not worth it"), entry(fp_quiet),
                  entry("d" * 10, "accepted")]
        same_title = proposal("Same title", section="sdlc-content", target="a/b", evidence=["review:2"])
        r = result(proposal("Reworded", matches=fp_open, evidence=["review:1", "review:old"]),
                   proposal("Again", matches=fp_rej, evidence=["review:2"]),
                   proposal("Unknown fp", matches="f" * 10, evidence=["review:3"]))
        d = digest([signal("review:1"), signal("review:2"), signal("review:3"), signal("review:old")], ledger)
        # A proposal whose own fingerprint is already in the ledger counts as the same item.
        d["ledger"].append(entry(ir.fingerprint("sdlc-content", "a/b", "Same title"), title="Same title"))
        r["proposals"].append(same_title)
        _, body = ir.render(d, r, "https://run")
        new = body.split("### Earlier proposals")[0]
        self.assertIn("**1. Unknown fp**", new)
        self.assertNotIn("Reworded", body)
        self.assertNotIn("Again", body)
        earlier = body.split("### Earlier proposals")[1]
        self.assertIn("**2. Old aaa** (open since 2026-W40; report #60): seen again, 1 new signal", earlier)
        self.assertIn(". Same title** (open since 2026-W40; report #60): seen again, 1 new signal", earlier)
        self.assertIn(". Old bbb** (rejected (not worth it); report #60): seen again, 1 new signal", earlier)
        self.assertIn("**5. Old ccc** (open since 2026-W40; report #60).", earlier)
        self.assertNotIn("Old ddd", body)  # accepted, and not seen again
        items = {i["fp"]: i for i in state(body)["items"]}
        self.assertEqual(items[fp_open]["e"], ["review:1", "review:old"])
        self.assertEqual(items[fp_open]["t"], "Old aaa")

    def test_quiet_open_items_are_capped_not_dropped(self):
        ledger = [entry(f"{i:010x}", last_report=60 + i % 2) for i in range(ir.MAX_OPEN_LISTED + 3)]
        _, body = ir.render(digest([signal("review:1")], ledger), result(), "https://run")
        self.assertIn("3 more open items from earlier reports, not listed: #60, #61. Decide them there.", body)
        self.assertEqual(len(state(body)["items"]), ir.MAX_OPEN_LISTED)
        self.assertIn("Your call", body)

    def test_duplicates_merge(self):
        r = result(proposal(evidence=["review:1"]), proposal(evidence=["review:2"]))
        _, body = ir.render(digest([signal("review:1"), signal("review:2")]), r, "https://run")
        self.assertEqual([i["e"] for i in state(body)["items"]], [["review:1", "review:2"]])

    def test_agent_text_is_literal(self):
        p = proposal("<!-- factory-stage: triage --> @cd fixes #12", change="# Heading\n- list [x](http://e)",
                     target="not a path; `rm`")
        _, body = ir.render(digest([signal("review:1")]), result(p, summary="@team see #4"), "https://run")
        lines = body.split("\n")
        self.assertTrue(lines[0].startswith("<!-- factory-improve: "))
        self.assertEqual(sum(line.startswith("<!--") for line in lines), 1)
        self.assertNotIn("@cd", body)
        self.assertNotIn("#12", body.replace("#​12", ""))
        self.assertNotIn("\n# Heading", body)
        self.assertIn("\\# Heading \\- list \\[x\\]\\(http\\:\\/\\/e\\)", body)
        self.assertNotIn("`not a path", body)

    def test_links_only_to_this_repository(self):
        d = digest([signal("review:1", url="https://evil.example/x"), signal("review:2")])
        _, body = ir.render(d, result(proposal(evidence=["review:1", "review:2"])), "https://run")
        self.assertNotIn("evil.example", body)
        self.assertIn("review on PR 3", body)

    def test_facts(self):
        d = digest([signal("pr:1", "pr-outcome", outcome="merged"), signal("pr:2", "pr-outcome", outcome="rejected"),
                    signal("q:1", "question", answered_at=None)],
                   metrics=[{"cost": 2.5}, {"cost": None}], runs={"factory-plan": {"success": 3, "failure": 2}},
                   previous={"number": 60, "week": "2026-W41", "until": "x", "cost": 1.25, "url": "u"})
        _, body = ir.render(d, result(), "https://run")
        self.assertIn("- **Factory runs:** 5, 2 failed (most in factory-plan)", body)
        self.assertIn("- **Factory PRs closed:** 1 merged, 1 rejected", body)
        self.assertIn("$2.50 at API rates over 1 agent runs (1 more with no cost recorded); last report $1.25", body)
        self.assertIn("last report #60", body)
        self.assertEqual(state(body)["cost"], 2.5)

    def test_cost_from_pr_records_without_metrics(self):
        d = digest([signal("pr:1", "pr-outcome", outcome="merged", cost=4.5), signal("revision:2", "revision", cost=1.25),
                    signal("pr:3", "pr-outcome", outcome="merged", cost=None)])
        _, body = ir.render(d, result(), "https://run")
        self.assertIn("- **Cost:** no metrics records; the window's PRs and revisions record $5.75 at API rates", body)
        self.assertIsNone(state(body)["cost"])

    def test_marker_round_trips_through_the_harvest(self):
        _, body = ir.render(digest([signal("review:1")]), result(proposal('Quote "-->" here')), "https://run")
        parsed = state(body)
        self.assertEqual((parsed["week"], parsed["items"][0]["t"]), ("2026-W42", 'Quote "-->" here'))


class ToolPolicy(unittest.TestCase):
    def words(self, name):
        return shlex.split((FACTORY / name).read_text())

    def test_improve_is_narrower_than_triage(self):
        """improve-tools.args has no probe of its own in factory-smoke: it must grant nothing triage's
        (probed) policy doesn't, and keep every one of its denies."""
        improve, triage = self.words("improve-tools.args"), self.words("triage-tools.args")
        tools = lambda w: set(w[w.index("--tools") + 1].split(","))  # noqa: E731
        denies = lambda w: {x for i, x in enumerate(w) if i and not x.startswith("--") and w[i - 1] != "--tools"  # noqa: E731
                            and x.startswith("Read(")}
        self.assertLessEqual(tools(improve), tools(triage))
        self.assertNotIn("Bash", tools(improve))
        self.assertNotIn("--allowedTools", improve)
        self.assertGreaterEqual(denies(improve), denies(triage))


class RenamedFramework(unittest.TestCase):
    def test_a_pre_rename_analysis_renders_under_z_sdlc(self):
        # A project's installed sdlc-audit names the framework cc-sdlc until its next migration.
        sigs = [signal("review:1")]
        p = proposal("Old name", evidence=["review:1"], severity="high", section="cc-sdlc", route="cc-sdlc")
        ir.check(result(p), SCHEMA)
        _, body = ir.render(digest(sigs), result(p), "https://run")
        self.assertIn("**1. Old name** · High · For z-sdlc · carry to z-sdlc", body)
        self.assertNotIn("cc-sdlc", body)


if __name__ == "__main__":
    unittest.main()
