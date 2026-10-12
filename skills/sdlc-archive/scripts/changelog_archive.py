#!/usr/bin/env python3
"""Archive old entries of an SDLC process changelog, one file per quarter.

Usage:
  changelog_archive.py archive CHANGELOG [--upstream FILE|-] [--today YYYY-MM-DD] [--threshold-kb 150] [--dry-run]
  changelog_archive.py check   CHANGELOG [--today YYYY-MM-DD] [--threshold-kb 150]
  changelog_archive.py init    SOURCE_CHANGELOG|- TARGET --version vX.Y.Z [--today YYYY-MM-DD]

archive: when CHANGELOG is over the threshold, every entry dated before the
  previous calendar quarter moves, unedited and in its original order, to
  changelog-archive/YYYY-Qn.md beside it. With --upstream (z-sdlc's changelog
  and archive files, concatenated; `-` reads stdin), entries copied from
  z-sdlc move too, whatever their date and the file's size: an entry is a
  copy when its `## YYYY-MM-DD: Title` line matches one upstream. The live
  file keeps a pointer line. Nothing is written unless the entries across
  all the files are the same before and after.
check: moves nothing. Exits 1 when archive would move something (the file
  is over the threshold and holds a quarter older than the previous one), and
  2 when the files don't parse, an archive file holds another quarter's
  entry, or an entry appears twice.
init: writes a new project's changelog: SOURCE's header and one install
  entry, none of SOURCE's entries. SOURCE `-` reads stdin (pipe it from
  `git show`). Refuses an existing TARGET.

Entries start at `## YYYY-MM-DD: Title` lines outside code fences.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ARCHIVE_DIR = "changelog-archive"
THRESHOLD_KB = 150
HEADING = re.compile(r"^## (\d{4})-(\d{2})-(\d{2}):")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SEPARATOR = re.compile(r"\n[ \t]*-{3,}[ \t]*\s*\Z")
POINTER_MARK = "<!-- changelog-archive-pointer -->"
POINTER = (
    f"{POINTER_MARK}\n> Older entries are in `{ARCHIVE_DIR}/`, one file per quarter, "
    "moved there unedited once this file passed about 150 KB."
)


class ChangelogError(Exception):
    pass


@dataclass
class Entry:
    date: dt.date
    text: str  # verbatim, including any trailing separator

    @property
    def quarter(self) -> str:
        return f"{self.date.year}-Q{(self.date.month - 1) // 3 + 1}"

    @property
    def body(self) -> str:
        """The entry without its trailing separator: what must never change."""
        return SEPARATOR.sub("", self.text.rstrip()).rstrip()


def split(text: str, name: str = "changelog") -> tuple[str, list[Entry]]:
    """Split into (header, entries). header + every entry's text == text."""
    lines = text.splitlines(keepends=True)
    fence: str | None = None
    starts: list[tuple[int, dt.date]] = []
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if m:
            mark = m.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not line.strip()[len(mark):]:
                fence = None
            continue
        if fence is None:
            h = HEADING.match(line)
            if h:
                try:
                    day = dt.date(int(h.group(1)), int(h.group(2)), int(h.group(3)))
                except ValueError:
                    raise ChangelogError(f"{name}:{i + 1}: invalid date in {line.strip()!r}")
                starts.append((i, day))
    if fence is not None:
        raise ChangelogError(f"{name}: a code fence ({fence}) is never closed")
    if not starts:
        return text, []
    header = "".join(lines[: starts[0][0]])
    bounds = [s for s, _ in starts] + [len(lines)]
    entries = [Entry(day, "".join(lines[bounds[k] : bounds[k + 1]])) for k, (_, day) in enumerate(starts)]
    return header, entries


def join(header: str, entries: list[Entry]) -> str:
    """Rebuild a file from entries, each byte for byte (a missing separator stays missing,
    so release.yml's parser sees no entry as new), except that the last loses any
    trailing separator."""
    out = header
    for k, e in enumerate(entries):
        if k == len(entries) - 1:
            out += e.body + "\n"
        else:
            out += e.text if e.text.endswith("\n") else e.text + "\n\n"
    return out if entries else out.rstrip() + "\n"


def without_pointer(header: str) -> str:
    """The header with the archive pointer (and the blank line after it) removed."""
    lines = header.splitlines(keepends=True)
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip() == POINTER_MARK:
            i += 2
            if i < len(lines) and not lines[i].strip():
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def with_pointer(header: str) -> str:
    """The live file's header with exactly one, current pointer to the archive."""
    if POINTER in header and header.count(POINTER_MARK) == 1:
        return header
    kept = without_pointer(header).splitlines(keepends=True)
    # After the title's first paragraph; at the top if there is no title.
    at = 0
    for i, line in enumerate(kept):
        if line.startswith("# "):
            at = i + 1
            while at < len(kept) and not kept[at].strip():
                at += 1
            while at < len(kept) and kept[at].strip():
                at += 1
            break
    block = ("\n" if at and kept[at - 1].strip() else "") + POINTER + "\n"
    if at < len(kept) and kept[at].strip():
        block += "\n"
    return "".join(kept[:at]) + block + "".join(kept[at:])


def archive_header(quarter: str) -> str:
    year, q = quarter.split("-")
    return (
        f"# SDLC Process Changelog: {year} {q} (archived)\n\n"
        f"Entries from {year} {q}, moved here unedited from `../sdlc_changelog.md`. Newest first.\n\n"
        "---\n\n"
    )


def cutoff(today: dt.date) -> dt.date:
    """The first day of the previous quarter: older entries are archivable."""
    first_month = 3 * ((today.month - 1) // 3) + 1
    month, year = first_month - 3, today.year
    if month < 1:
        month, year = month + 12, year - 1
    return dt.date(year, month, 1)


def archive_files(changelog: Path) -> dict[str, Path]:
    folder = changelog.parent / ARCHIVE_DIR
    if not folder.is_dir():
        return {}
    found = {}
    for p in sorted(folder.glob("*.md")):
        if not re.fullmatch(r"\d{4}-Q[1-4]", p.stem):
            raise ChangelogError(f"{p}: archive files are named YYYY-Qn.md")
        found[p.stem] = p
    return found


def read_all(changelog: Path) -> tuple[str, list[Entry], dict[str, tuple[str, list[Entry]]]]:
    header, entries = split(changelog.read_text(encoding="utf-8"), str(changelog))
    archives = {}
    for quarter, p in archive_files(changelog).items():
        a_header, a_entries = split(p.read_text(encoding="utf-8"), str(p))
        for e in a_entries:
            if e.quarter != quarter:
                raise ChangelogError(f"{p}: holds an entry from {e.quarter}: {e.body.splitlines()[0]}")
        archives[quarter] = (a_header, a_entries)
    return header, entries, archives


def bodies(entries: list[Entry], archives: dict[str, tuple[str, list[Entry]]]) -> Counter:
    c = Counter(e.body for e in entries)
    for _, a_entries in archives.values():
        c.update(e.body for e in a_entries)
    return c


def duplicates(c: Counter) -> list[str]:
    return [b.splitlines()[0] for b, n in c.items() if n > 1]


def heading(e: Entry) -> str:
    return e.text.split("\n", 1)[0].strip()


def upstream_headings(text: str) -> set[str]:
    """The `## YYYY-MM-DD: Title` lines of z-sdlc's changelog and archive files."""
    return {heading(e) for e in split(text, "upstream")[1]}


def plan(changelog: Path, today: dt.date, threshold_kb: int, upstream: set[str] | None = None):
    """What archive would do: (moving entries by quarter, copies among them, reason if nothing)."""
    size = changelog.stat().st_size
    header, entries, archives = read_all(changelog)
    dup = duplicates(bodies(entries, archives))
    if dup:
        raise ChangelogError(f"entries appear twice across the changelog and its archive: {dup[:3]}")
    copies = {id(e) for e in entries if upstream and heading(e) in upstream}
    over = size > threshold_kb * 1024
    limit = cutoff(today)
    moving: dict[str, list[Entry]] = {}
    for e in entries:
        if id(e) in copies or (over and e.date < limit):
            moving.setdefault(e.quarter, []).append(e)
    if not moving:
        why = (
            f"{size // 1024} KB, but nothing is older than the previous quarter (before {limit})"
            if over
            else f"{size // 1024} KB, under the {threshold_kb} KB threshold"
        )
        if upstream is not None:
            why += "; no entry copied from z-sdlc"
        return header, entries, archives, {}, 0, why
    return header, entries, archives, moving, len(copies), ""


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        mode = path.stat().st_mode & 0o777
    else:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def cmd_archive(changelog: Path, today: dt.date, threshold_kb: int, dry_run: bool, upstream: set[str] | None = None) -> int:
    header, entries, archives, moving, n_copies, why = plan(changelog, today, threshold_kb, upstream)
    if not moving:
        print(f"Nothing to archive: {why}.")
        return 0
    before = bodies(entries, archives)
    moved_ids = {id(e) for group in moving.values() for e in group}
    kept = [e for e in entries if id(e) not in moved_ids]
    new_live = join(with_pointer(header), kept)
    new_archives = {}
    for quarter, group in moving.items():
        a_header, a_entries = archives.get(quarter, (archive_header(quarter), []))
        new_archives[quarter] = join(a_header, group + a_entries)

    # Verify in memory before writing anything.
    _, check_live = split(new_live, "new changelog")
    check_archives = dict(archives)
    for quarter, text in new_archives.items():
        check_archives[quarter] = split(text, f"new {quarter}")
    if bodies(check_live, check_archives) != before:
        raise ChangelogError("the archived files would not hold exactly the original entries; nothing written")

    folder = changelog.parent / ARCHIVE_DIR
    for quarter, group in sorted(moving.items()):
        print(f"{'Would move' if dry_run else 'Moved'} {len(group)} entries to {folder / (quarter + '.md')}")
    size_after = len(new_live.encode("utf-8"))
    if upstream is not None:
        print(f"{n_copies} of the moved entries were copied from z-sdlc")
    print(f"{changelog}: {changelog.stat().st_size // 1024} KB -> {size_after // 1024} KB, {len(kept)} entries kept")
    if dry_run:
        return 0
    for quarter, text in new_archives.items():
        atomic_write(folder / f"{quarter}.md", text)
    atomic_write(changelog, new_live)

    # Verify what landed on disk.
    _, entries_after, archives_after = read_all(changelog)
    if bodies(entries_after, archives_after) != before:
        raise ChangelogError("the files on disk don't hold exactly the original entries; restore them from git")
    return 0


def cmd_check(changelog: Path, today: dt.date, threshold_kb: int) -> int:
    _, entries, archives, moving, _, why = plan(changelog, today, threshold_kb)
    if moving:
        counts = ", ".join(f"{q} ({len(g)})" for q, g in sorted(moving.items()))
        print(
            f"{changelog} is over {threshold_kb} KB and holds entries to archive: {counts}.\n"
            f"Run: python3 {Path(__file__).as_posix()} archive {changelog}"
        )
        return 1
    held = sum(len(a) for _, a in archives.values())
    print(f"OK: {len(entries)} live entries, {held} archived; {why}.")
    return 0


def cmd_init(source: Path, target: Path, version: str, today: dt.date) -> int:
    if target.exists():
        raise ChangelogError(f"{target} exists; init writes only a new changelog")
    text = sys.stdin.read() if str(source) == "-" else source.read_text(encoding="utf-8")
    header, _ = split(text, str(source))
    if not header.lstrip().startswith("# "):
        raise ChangelogError(f"{source}: no changelog header (a `# ` title) before the first entry")
    header = without_pointer(header).rstrip()
    if not header.endswith("---"):
        header += "\n\n---"
    entry = (
        f"## {today.isoformat()}: Installed z-sdlc {version}\n\n"
        "**Origin:** `sdlc-initialize`.\n\n"
        f"**What happened:** the framework was installed at {version}. Its own history is the "
        "z-sdlc repository's changelog; this file records this project's process changes from here on, "
        "and each migration adds an entry.\n\n"
        "**Changes made:**\n\n"
        f"1. Installed z-sdlc {version}.\n"
    )
    atomic_write(target, header + "\n\n" + entry)
    print(f"Wrote {target}: the header and one install entry.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("archive", "check"):
        p = sub.add_parser(name)
        p.add_argument("changelog", type=Path)
        p.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
        p.add_argument("--threshold-kb", type=int, default=THRESHOLD_KB)
        if name == "archive":
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--upstream", help="z-sdlc's changelog and archive files, concatenated; - for stdin")
    p = sub.add_parser("init")
    p.add_argument("source", type=Path)
    p.add_argument("target", type=Path)
    p.add_argument("--version", required=True)
    p.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    args = parser.parse_args(argv)
    try:
        if args.command == "archive":
            upstream = None
            if args.upstream:
                text = sys.stdin.read() if args.upstream == "-" else Path(args.upstream).read_text(encoding="utf-8")
                upstream = upstream_headings(text)
                if not upstream:
                    raise ChangelogError("--upstream holds no changelog entries")
            return cmd_archive(args.changelog, args.today, args.threshold_kb, args.dry_run, upstream)
        if args.command == "check":
            return cmd_check(args.changelog, args.today, args.threshold_kb)
        return cmd_init(args.source, args.target, args.version, args.today)
    except (ChangelogError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
