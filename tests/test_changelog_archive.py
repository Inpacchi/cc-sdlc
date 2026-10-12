"""Tests for skills/sdlc-archive/scripts/changelog_archive.py. Run: python3 -m unittest discover -s tests"""
import datetime as dt
import importlib.util
import io
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/sdlc-archive/scripts/changelog_archive.py"
spec = importlib.util.spec_from_file_location("changelog_archive", SCRIPT)
ca = importlib.util.module_from_spec(spec)
sys.modules["changelog_archive"] = ca  # dataclasses look the module up
spec.loader.exec_module(ca)

HEADER = """# SDLC Process Changelog

A living record of how the process evolves.

---

## Example Entry

```
## YYYY-MM-DD: [Brief Title]
```

---

"""


def entry(day, title, body="Body.", sep=True):
    text = f"## {day}: {title}\n\n**Changes made:**\n\n1. {body}\n"
    return text + ("\n---\n\n" if sep else "")


def release_keys(content):
    """release.yml's parser: the entry keys it would see in one file."""
    keys = set()
    for block in re.split(r"\n---\n", content):
        m = re.match(r"\s*## (\d{4}-\d{2}-\d{2}):\s*(.*)", block.strip())
        if m:
            keys.add(f"{m.group(1)}: {m.group(2).strip()}")
    return keys


def run(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = ca.main([str(a) for a in argv])
    return code, out.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.log = self.dir / "sdlc_changelog.md"

    def write(self, *entries):
        text = HEADER + "".join(entries)
        self.log.write_text(text, encoding="utf-8")
        return text

    def all_bodies(self):
        _, entries, archives = ca.read_all(self.log)
        return ca.bodies(entries, archives)


class SplitTests(Base):
    def test_lossless(self):
        text = HEADER + entry("2026-10-01", "A") + entry("2026-09-01", "B", sep=False)
        header, entries = ca.split(text)
        self.assertEqual(header + "".join(e.text for e in entries), text)
        self.assertEqual([e.date.isoformat() for e in entries], ["2026-10-01", "2026-09-01"])

    def test_heading_inside_fence_is_not_an_entry(self):
        fenced = "## 2026-10-02: Fenced\n\n```markdown\n## 2026-01-01: Not an entry\n```\n\n---\n\n"
        _, entries = ca.split(HEADER + fenced + entry("2026-09-01", "B"))
        self.assertEqual(len(entries), 2)

    def test_fence_with_info_string_does_not_close(self):
        text = HEADER + "## 2026-10-02: X\n\n```\n```python\n## 2026-01-01: still fenced\n```\n\n---\n\n"
        _, entries = ca.split(text + entry("2026-09-01", "B"))
        self.assertEqual(len(entries), 2)

    def test_unclosed_fence_is_an_error(self):
        with self.assertRaises(ca.ChangelogError):
            ca.split(HEADER + "## 2026-10-02: X\n\n```\nno close\n")

    def test_invalid_date_is_an_error(self):
        with self.assertRaises(ca.ChangelogError):
            ca.split(HEADER + "## 2026-13-02: X\n")

    def test_real_changelog_is_lossless(self):
        for path in [ROOT / "process/sdlc_changelog.md", *sorted((ROOT / "process/changelog-archive").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            header, entries = ca.split(text, str(path))
            self.assertEqual(header + "".join(e.text for e in entries), text, path)


class ArchiveTests(Base):
    TODAY = "2026-10-11"  # Q4: the previous quarter is Q3, so Q2 and older move

    def fill(self):
        pad = "x" * 2000
        return self.write(
            entry("2026-10-05", "Q4 entry", pad),
            entry("2026-08-01", "Q3 entry", pad),
            entry("2026-05-02", "Q2 newer", pad),
            entry("2026-05-09", "Q2 out of order", pad),
            entry("2026-04-01", "Q2 oldest", pad),
            entry("2025-12-30", "2025 Q4", pad, sep=False),
        )

    def test_moves_quarters_older_than_the_previous_one(self):
        original = self.fill()
        before = self.all_bodies()
        code, out = run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        self.assertEqual(code, 0, out)
        live = self.log.read_text()
        self.assertIn("Q4 entry", live)
        self.assertIn("Q3 entry", live)
        self.assertNotIn("Q2 oldest", live)
        q2 = (self.dir / "changelog-archive/2026-Q2.md").read_text()
        # Original relative order, unsorted.
        self.assertLess(q2.index("Q2 newer"), q2.index("Q2 out of order"))
        self.assertLess(q2.index("Q2 out of order"), q2.index("Q2 oldest"))
        self.assertTrue((self.dir / "changelog-archive/2025-Q4.md").exists())
        self.assertEqual(self.all_bodies(), before)
        # release.yml sees the same entries across the live file and the archives.
        keys = set()
        for p in [self.log, *(self.dir / "changelog-archive").glob("*.md")]:
            keys |= release_keys(p.read_text())
        self.assertEqual(keys, release_keys(original))
        self.assertEqual(live.count(ca.POINTER_MARK), 1)

    def test_missing_separators_stay_missing(self):
        pad = "x" * 2000
        original = self.write(
            entry("2026-10-05", "Q4 a", pad, sep=False),
            entry("2026-10-04", "Q4 b, no separator above", pad),
            entry("2026-04-01", "Q2 no separator", pad, sep=False),
            entry("2026-03-01", "Q1", pad, sep=False),
        )
        run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        live = self.log.read_text()
        # release.yml must not see an old entry as new in the live file.
        self.assertLessEqual(release_keys(live), release_keys(original))
        self.assertIn(entry("2026-10-05", "Q4 a", pad, sep=False) + "## 2026-10-04", live)
        _, entries = ca.split((self.dir / "changelog-archive/2026-Q2.md").read_text())
        self.assertEqual(len(entries), 1)

    def test_keeps_file_modes(self):
        self.fill()
        self.log.chmod(0o644)
        run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        self.assertEqual(self.log.stat().st_mode & 0o777, 0o644)
        q2 = self.dir / "changelog-archive/2026-Q2.md"
        self.assertTrue(q2.stat().st_mode & 0o044, "archive files are readable beyond the owner")

    def test_under_threshold_moves_nothing(self):
        text = self.fill()
        code, out = run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "500")
        self.assertEqual(code, 0)
        self.assertIn("under the 500 KB threshold", out)
        self.assertEqual(self.log.read_text(), text)
        self.assertFalse((self.dir / "changelog-archive").exists())

    def test_dry_run_writes_nothing(self):
        text = self.fill()
        code, out = run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("Would move", out)
        self.assertEqual(self.log.read_text(), text)
        self.assertFalse((self.dir / "changelog-archive").exists())

    def test_second_run_is_a_no_op(self):
        self.fill()
        run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        live = self.log.read_text()
        q2 = (self.dir / "changelog-archive/2026-Q2.md").read_text()
        code, out = run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        self.assertEqual(code, 0)
        self.assertIn("nothing is older than the previous quarter", out)
        self.assertEqual(self.log.read_text(), live)
        self.assertEqual((self.dir / "changelog-archive/2026-Q2.md").read_text(), q2)

    def test_pointer_stays_single_across_quarters(self):
        self.fill()
        run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        run("archive", self.log, "--today", "2027-04-01", "--threshold-kb", "1")
        live = self.log.read_text()
        self.assertEqual(live.count(ca.POINTER_MARK), 1)
        self.assertNotIn("\n\n\n", live.split("## ")[0])

    def test_merges_into_an_existing_archive_file(self):
        self.fill()
        run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        before = self.all_bodies()
        # A late entry backdated into an archived quarter.
        text = self.log.read_text().replace("## 2026-10-05", entry("2026-06-30", "Late Q2", "y" * 2000) + "## 2026-10-05", 1)
        self.log.write_text(text)
        code, out = run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        self.assertEqual(code, 0, out)
        q2 = (self.dir / "changelog-archive/2026-Q2.md").read_text()
        self.assertLess(q2.index("Late Q2"), q2.index("Q2 newer"))
        after = self.all_bodies()
        self.assertEqual(sum(after.values()), sum(before.values()) + 1)

    def test_duplicates_refuse(self):
        self.fill()
        run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        q2 = (self.dir / "changelog-archive/2026-Q2.md").read_text()
        _, q2_entries = ca.split(q2)
        self.log.write_text(self.log.read_text() + "\n---\n\n" + q2_entries[0].text)
        code, _ = run("archive", self.log, "--today", self.TODAY, "--threshold-kb", "1")
        self.assertEqual(code, 2)

    def test_wrong_quarter_in_archive_refuses(self):
        self.fill()
        folder = self.dir / "changelog-archive"
        folder.mkdir()
        (folder / "2026-Q1.md").write_text(ca.archive_header("2026-Q1") + entry("2026-05-01", "Misfiled", sep=False))
        code, _ = run("check", self.log, "--today", self.TODAY)
        self.assertEqual(code, 2)


class UpstreamCopyTests(Base):
    TODAY = "2026-10-11"

    def setUp(self):
        super().setUp()
        self.upstream = self.dir / "upstream.md"
        # z-sdlc's live file and an archive file, concatenated as sdlc-migrate pipes them.
        self.upstream.write_text(
            HEADER + entry("2026-10-03", "Upstream Q4") + entry("2026-08-01", "Upstream Q3", sep=False)
            + "\n" + ca.archive_header("2026-Q2") + entry("2026-05-01", "Upstream Q2", sep=False)
        )

    def fill(self):
        return self.write(
            entry("2026-10-06", "Own Q4"),
            entry("2026-10-03", "Upstream Q4", "copied body"),
            entry("2026-08-02", "Own Q3"),
            entry("2026-08-01", "Upstream Q3", "copied body"),
            entry("2026-05-01", "Upstream Q2", "copied body", sep=False),
        )

    def test_copies_move_whatever_their_quarter_and_the_size(self):
        self.fill()
        before = self.all_bodies()
        code, out = run("archive", self.log, "--upstream", self.upstream, "--today", self.TODAY, "--threshold-kb", "500")
        self.assertEqual(code, 0, out)
        self.assertIn("3 of the moved entries were copied from z-sdlc", out)
        live = self.log.read_text()
        self.assertIn("Own Q4", live)
        self.assertIn("Own Q3", live)
        self.assertNotIn("Upstream", live.split(ca.POINTER_MARK)[1])
        for quarter in ("2026-Q4", "2026-Q3", "2026-Q2"):
            self.assertTrue((self.dir / f"changelog-archive/{quarter}.md").exists(), quarter)
        self.assertEqual(self.all_bodies(), before)

    def test_own_entries_still_need_the_threshold(self):
        self.write(entry("2026-10-06", "Own Q4"), entry("2026-01-02", "Own Q1", sep=False))
        code, out = run("archive", self.log, "--upstream", self.upstream, "--today", self.TODAY, "--threshold-kb", "500")
        self.assertEqual(code, 0)
        self.assertIn("no entry copied from z-sdlc", out)
        self.assertIn("Own Q1", self.log.read_text())

    def test_upstream_from_stdin(self):
        self.fill()
        import sys as _sys
        old = _sys.stdin
        _sys.stdin = io.StringIO(self.upstream.read_text())
        try:
            code, out = run("archive", self.log, "--upstream", "-", "--today", self.TODAY, "--threshold-kb", "500")
        finally:
            _sys.stdin = old
        self.assertEqual(code, 0, out)
        self.assertNotIn("Upstream Q4", self.log.read_text())

    def test_empty_upstream_refuses(self):
        self.fill()
        empty = self.dir / "empty.md"
        empty.write_text("")
        self.assertEqual(run("archive", self.log, "--upstream", empty, "--today", self.TODAY)[0], 2)


class CheckTests(Base):
    def test_fails_only_when_over_threshold_with_something_to_move(self):
        self.write(entry("2026-10-05", "Q4", "x" * 3000), entry("2026-01-05", "Q1", "x" * 3000, sep=False))
        self.assertEqual(run("check", self.log, "--today", "2026-10-11", "--threshold-kb", "1")[0], 1)
        self.assertEqual(run("check", self.log, "--today", "2026-10-11", "--threshold-kb", "100")[0], 0)
        # Over the threshold but nothing older than the previous quarter: passes.
        self.assertEqual(run("check", self.log, "--today", "2026-04-11", "--threshold-kb", "1")[0], 0)

    def test_cutoff(self):
        self.assertEqual(ca.cutoff(dt.date(2026, 10, 11)), dt.date(2026, 7, 1))
        self.assertEqual(ca.cutoff(dt.date(2027, 1, 1)), dt.date(2026, 10, 1))
        self.assertEqual(ca.cutoff(dt.date(2026, 3, 31)), dt.date(2025, 10, 1))


class InitTests(Base):
    def test_header_and_one_install_entry(self):
        source = self.dir / "source.md"
        source.write_text(ca.with_pointer(HEADER) + entry("2026-10-05", "Upstream", sep=False))
        target = self.dir / "project" / "sdlc_changelog.md"
        code, _ = run("init", source, target, "--version", "v2.0.0", "--today", "2026-10-11")
        self.assertEqual(code, 0)
        text = target.read_text()
        self.assertNotIn("Upstream", text)
        self.assertNotIn(ca.POINTER_MARK, text)
        _, entries = ca.split(text)
        self.assertEqual(len(entries), 1)
        self.assertIn("Installed z-sdlc v2.0.0", entries[0].text)
        self.assertEqual(run("init", source, target, "--version", "v2.0.0")[0], 2)

    def test_refuses_a_source_without_header(self):
        source = self.dir / "empty.md"
        source.write_text("")
        target = self.dir / "new.md"
        self.assertEqual(run("init", source, target, "--version", "v2.0.0")[0], 2)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
