import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import catalog  # noqa: E402

CATALOG = """# Project Deliverable Catalog

**Next ID:** D35

## Active Deliverables

| ID | Name | Status | Depends on | Spec | Plan | Result |
|----|------|--------|------------|------|------|--------|
| [D34](https://github.com/o/r/issues/34) | Big thing | Draft | D34a, D34b | [spec](specs/d34_big_spec.md) | — | — |
| D34a | First part | Draft | — | — | — | — |
| D34b | Second part | Draft | `D34a` | — | — | — |

## Completed Deliverables

| ID | Name | Chronicle Location |
|----|------|-------------------|
| D1 | Old | `docs/chronicle/x/` |
"""

SPLIT = """# D34 Split: Big thing

## Parts

| Part | Name | Tier | Depends on | Spec | Scope |
|------|------|------|------------|------|-------|
| D34a | First part | lite | — | — | Unify the interval table. |
| D34b | Second part | Full | D34a | `docs/current_work/specs/d34_big_thing_spec.md` | The point-in-time join. |
"""


class Catalog(unittest.TestCase):
    def test_rows(self):
        rows = catalog.catalog_rows(CATALOG)
        self.assertEqual(list(rows), ["D34", "D34a", "D34b"])
        self.assertEqual(catalog.ids(rows["D34"]["Depends on"]), ["D34a", "D34b"])
        self.assertEqual(catalog.ids(rows["D34b"]["Depends on"]), ["D34a"])
        self.assertEqual(catalog.ids(rows["D34a"]["Depends on"]), [])

    def test_ids_refuses_a_typo(self):
        with self.assertRaises(ValueError):
            catalog.ids("D34a, 34b")

    def test_missing_table(self):
        with self.assertRaises(ValueError):
            catalog.catalog_rows("# nothing here\n")

    def test_ragged_row(self):
        with self.assertRaises(ValueError):
            catalog.catalog_rows(CATALOG.replace("| D34a | First part | Draft | — | — | — | — |", "| D34a | First part | Draft |"))


class Split(unittest.TestCase):
    def test_parts(self):
        parts = catalog.split_parts(SPLIT)
        self.assertEqual([p["part"] for p in parts], ["D34a", "D34b"])
        self.assertEqual(parts[1]["tier"], "full")
        self.assertEqual(parts[1]["depends_on"], ["D34a"])
        self.assertEqual(parts[1]["spec"], "docs/current_work/specs/d34_big_thing_spec.md")
        self.assertEqual(parts[0]["spec"], "")
        catalog.check_parts("D34", parts)

    def test_rules(self):
        parts = catalog.split_parts(SPLIT)
        bad = [
            ("D34a", parts),                                              # parent must be top-level
            ("D34", parts[:1]),                                           # at least two parts
            ("D34", [parts[1], parts[0]]),                                # out of order
            ("D34", [parts[0], dict(parts[1], tier="huge")]),
            ("D34", [dict(parts[0], depends_on=["D34b"]), parts[1]]),     # depends on a later part
            ("D34", [parts[0], dict(parts[1], depends_on=["D34"])]),      # on its parent
            ("D34", [dict(parts[0], spec="docs/current_work/specs/d34_big_thing_spec.md"), parts[1]]),  # lite + spec
            ("D34", [parts[0], dict(parts[1], spec="api/x.py")]),
            ("D34", [parts[0], dict(parts[1], scope=" ")]),
        ]
        for parent, ps in bad:
            with self.assertRaises(ValueError, msg=f"{parent} {ps}"):
                catalog.check_parts(parent, ps)

    def test_external_dependency_allowed(self):
        parts = catalog.split_parts(SPLIT)
        catalog.check_parts("D34", [dict(parts[0], depends_on=["D12"]), parts[1]])

    def test_wrong_columns(self):
        with self.assertRaises(ValueError):
            catalog.split_parts(SPLIT.replace("| Spec | Scope |", "| Scope | Spec |"))


if __name__ == "__main__":
    unittest.main()
