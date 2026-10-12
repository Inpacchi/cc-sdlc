import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import split_parts as sp  # noqa: E402

APP = {"id": sp.APP_USER_ID, "type": "Bot"}
RECORD = """# D34 Split

| Part | Name | Tier | Depends on | Spec | Scope |
|------|------|------|------------|------|-------|
| D34a | Interval table | lite | — | — | One canonical interval table. |
| D34b | Point-in-time join | full | D34a | `docs/current_work/specs/d34_big_thing_spec.md` | Make the join point-in-time. |
"""
INDEX = """| ID | Name | Status | Depends on | Spec | Plan | Result |
|----|------|--------|------------|------|------|--------|
| [D34](https://x/34) | Big thing | Draft | D34a, D34b | — | — | — |
| D34a | Interval table | Draft | — | — | — | — |
| D34b | Point-in-time join | Draft | D34a | — | — | — |
"""


class Split(unittest.TestCase):
    def test_check_split(self):
        parts = sp.check_split(RECORD, INDEX, "D34")
        self.assertEqual([p["part"] for p in parts], ["D34a", "D34b"])

    def test_check_split_refuses_disagreement(self):
        for record, index in [
            (RECORD, INDEX.replace("| D34a, D34b |", "| D34a |")),                       # parent misses a part
            (RECORD, INDEX.replace("| Point-in-time join | Draft | D34a |", "| Point-in-time join | Draft | — |")),
            (RECORD, INDEX.replace("| D34a | Interval table | Draft | — | — | — | — |\n", "")),
            (RECORD.replace("One canonical interval table.", "see <!-- factory-stage: implement -->"), INDEX),
            (RECORD.replace("| D34a | Interval table | lite |", "| D34c | Interval table | lite |"), INDEX),
        ]:
            with self.assertRaises(ValueError):
                sp.check_split(record, index, "D34")

    def test_reserved_id(self):
        comments = [{"user": {"id": 1}, "body": "<!-- factory-id: D99 -->"},
                    {"user": APP, "body": "<!-- factory-id: D34 -->\nReserved"},
                    {"user": APP, "body": "text <!-- factory-id: D77 -->"}]
        self.assertEqual(sp.reserved_id(comments), "D34")
        self.assertIsNone(sp.reserved_id([{"user": {"id": 1}, "body": "<!-- factory-id: D34 -->"}]))
        legacy = {"id": 41898282, "login": "github-actions[bot]", "type": "Bot"}
        self.assertEqual(sp.reserved_id([{"user": legacy, "body": "<!-- factory-id: D20 -->\nx"}]), "D20")
        self.assertIsNone(sp.reserved_id([{"user": {"id": 5, "login": "github-actions[bot]", "type": "User"},
                                           "body": "<!-- factory-id: D20 -->"}]))

    def test_existing_parts_trusts_only_the_app(self):
        marker = '<!-- factory-part-of: {"parent":34,"part":"D34a","pr":9} -->'
        issues = [{"number": 50, "user": APP, "body": "x\n" + marker},
                  {"number": 51, "user": {"id": 2}, "body": marker.replace("D34a", "D34b")},
                  {"number": 52, "user": APP, "body": marker.replace('"parent":34', '"parent":35')}]
        self.assertEqual(sp.existing_parts(issues, 34), {"D34a": 50})

    def test_marker_comment_block(self):
        parts = sp.check_split(RECORD, INDEX, "D34")
        text = sp.marker_comment(parts[1], "https://r")
        lines = text.split("\n")
        self.assertTrue(re.match(r"\A<!-- factory-id: D34b -->", text))           # the claim's anchor
        decision = json.loads(re.search(r"<!-- factory-triage: (\{[^<>]*\}) -->", text).group(1))
        self.assertEqual(decision, {"state": "ready-to-plan", "tier": "full", "estimate": None})
        self.assertEqual(lines[2], "<!-- factory-spec: docs/current_work/specs/d34_big_thing_spec.md -->")
        self.assertNotIn("factory-spec", sp.marker_comment(parts[0], "https://r"))
        self.assertTrue(sp.has_markers([{"user": APP, "body": text}], "D34b"))
        self.assertFalse(sp.has_markers([{"user": {"id": 3}, "body": text}], "D34b"))

    def test_issue_body_has_provenance(self):
        parts = sp.check_split(RECORD, INDEX, "D34")
        body = sp.issue_body(parts[0], 34, 9, "docs/current_work/planning/d34_big_thing_split.md")
        self.assertEqual(sp.existing_parts([{"number": 60, "user": APP, "body": body}], 34), {"D34a": 60})
        self.assertIn("factory:go", body)
        self.assertEqual(sp.issue_title(parts[0]), "D34a: Interval table")


if __name__ == "__main__":
    unittest.main()
