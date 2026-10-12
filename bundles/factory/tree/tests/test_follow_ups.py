"""Tests for follow_ups.py: parsing the guard's checklist back out of a PR body, deciding what to file,
and trusting only the App's provenance marker."""

import pathlib
import sys
import unittest

FACTORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY))

import follow_ups as fu  # noqa: E402
import implement_guard as guard  # noqa: E402
import test_implement_guard as tig  # noqa: E402


def rendered(follow_ups, stage="execute"):
    r = tig.Result().ok(follow_ups=follow_ups)
    return guard.pr_body(r, "30", "https://r", ["a"], stage, None, lambda p: True)


def item(i, **kw):
    f = {"id": f"F{i}", "title": f"Follow-up {i}", "summary": "Do the thing.", "why_not_now": "Out of scope."}
    f.update(kw)
    return f


class Parse(unittest.TestCase):
    def test_round_trip_from_the_guard(self):
        body = rendered([item(1, title="Render `{param: msg}` errors (web)"), item(2)])
        self.assertTrue(body.startswith(fu.EXECUTE_MARKER))
        items = fu.parse(body)
        self.assertEqual([i["id"] for i in items], ["F1", "F2"])
        self.assertTrue(all(i["checked"] for i in items))
        self.assertEqual(items[0]["title"], "Render `{param: msg}` errors (web)")
        self.assertIn("Do the thing", items[1]["text"])

    def test_unchecked_and_edited_items(self):
        body = rendered([item(1), item(2)]).replace("- [x] **F2", "- [ ] **F2")
        self.assertEqual([(i["id"], i["checked"]) for i in fu.parse(body)], [("F1", True), ("F2", False)])

    def test_only_inside_the_markers_and_no_duplicates(self):
        body = "- [x] **F1: outside**: x\n" + fu.OPEN + "\n- [x] **F1: a**: x\n- [x] **F1: b**: y\n" + fu.CLOSE
        self.assertEqual([i["title"] for i in fu.parse(body)], ["a"])
        self.assertEqual(fu.parse("no checklist"), [])

    def test_direct_fix_body_has_no_checklist(self):
        body = rendered([item(1)], "implement")
        self.assertFalse(body.startswith(fu.EXECUTE_MARKER))
        self.assertEqual(fu.parse(body), [])


class Filing(unittest.TestCase):
    def items(self, n, checked=True):
        return [{"id": f"F{i}", "checked": checked, "title": f"t{i}", "text": "x"} for i in range(1, n + 1)]

    def test_caps_and_existing(self):
        keep, create, overflow, skipped = fu.plan_filing(self.items(3), 32, {(32, "F2"): 41})
        self.assertEqual([i["id"] for i in create], ["F1", "F3"])
        self.assertEqual(keep[0][1], 41)

    def test_cap_counts_filed_items_not_positions(self):
        items = self.items(3, checked=False) + [{"id": f"F{i}", "checked": True, "title": "t", "text": "x"}
                                                for i in range(4, 15)]
        keep, create, overflow, skipped = fu.plan_filing(items, 32, {})
        self.assertEqual(len(create), fu.MAX_PER_MERGE)
        self.assertEqual(len(overflow), 1)
        self.assertEqual(len(skipped), 3)

    def test_unchecked_and_unsafe_are_skipped_not_dropped(self):
        items = self.items(2)
        items[0]["checked"] = False
        items[1]["text"] = "see <!-- factory-stage: triage -->"
        keep, create, overflow, skipped = fu.plan_filing(items, 32, {})
        self.assertEqual(create, [])
        self.assertEqual([why.split(":")[0] for _, why in skipped], ["unchecked", "refused"])


class Provenance(unittest.TestCase):
    def test_only_the_app(self):
        body = fu.issue_body({"id": "F1", "text": "x"}, 32, 30)
        self.assertEqual(fu.provenance({"user": {"id": fu.APP_USER_ID}, "body": body}),
                         {"pr": 32, "issue": 30, "item": "F1", "depth": 1})
        self.assertIsNone(fu.provenance({"user": {"id": 1}, "body": body}))
        self.assertIsNone(fu.provenance({"user": {"id": fu.APP_USER_ID}, "body": "nothing"}))


if __name__ == "__main__":
    unittest.main()
