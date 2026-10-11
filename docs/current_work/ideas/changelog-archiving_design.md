---
type: design-draft
slug: changelog-archiving
created: 2026-10-11
status: built (2026-10-11), not released
related_files:
  - process/sdlc_changelog.md
  - skills/sdlc-migrate/SKILL.md
  - skills/sdlc-archive/SKILL.md
  - .github/workflows/release.yml
  - skeleton/manifest.json
---

# Archiving the Process Changelog (draft)

CD decided (2026-10-11) that the process changelog gets archived. This draft says how. Nothing here is built except the first fix below.

## What exists

- **cc-sdlc's changelog** is 659 KB, 249 entries since March 2026. Nothing archives it.
- **Every project's changelog is a copy of cc-sdlc's history plus its own entries.** `sdlc-initialize` installs `process/sdlc_changelog.md` from the source, so a project starts with the framework's whole history and adds its own on top (one project: 758 KB, all 199 cc-sdlc entries from March to May, and 54 of its own; two others about 600 KB each).
- **Who reads it:**
  - `sdlc-migrate` §1.2 reads cc-sdlc's changelog *from the source repo* at the target tag, back to the project's version: the migration's release notes.
  - `release.yml` builds release notes from the entries present now but not at the previous tag.
  - Adapters never transform it (`process/adapter-lifecycle-protocol.md`, the adapter audit's exempt-file list): it quotes canonical phrases as history.
  - The software factory's guard caps each file a stage may write at 200 KB; quantile's changelog is over it, so b1bf1d2 added an exception (an over-cap file may grow by the patch cap).
- **Fixed already (c8dd38d, ported to quantile):** migration treated the project's changelog as a framework file to copy. Drift detection raised a hard three-way prompt over it on every migration, and an install without drift data would have had its own entries copied over. It's now on the never-overwrite list, and each migration prepends one entry recording itself.

## Proposed shape

1. **A project's changelog is project-only going forward.** New installs start with the file's header and one install entry, not the framework's history. The framework's history stays in cc-sdlc, where migration already reads it.
2. **Archive files:** `[sdlc-root]/process/changelog-archive/YYYY-Qn.md`, one per calendar quarter, each holding that quarter's entries verbatim, newest first, under a one-line header. The live file keeps a pointer line under its header.
3. **When:** when the live file passes about 150 KB, every whole quarter older than the previous one moves to its archive file. Entries are never edited after they move.
4. **Who:** a deterministic script (checks over prose), not an agent: split by `## YYYY-MM-DD:` headings, write the quarter files, rewrite the live file, verify that the entries across all the files equal the entries before. `sdlc-archive` runs it in projects, and a framework-dev skill or a CI check runs it in cc-sdlc.
5. **Readers:**
   - `sdlc-migrate` §1.2 also reads the archive files at the target tag when the project's version is older than the live file's oldest entry.
   - `release.yml` is unaffected: it takes entries that are in the current file but weren't at the previous tag, and archiving only moves old ones. A check proves it.
   - Adapters: the archive files get the same no-transform exemption, with the paired change in `neuroloom-sdlc-plugin`.
6. **The manifest:** cc-sdlc's own archive files are history, not something to install, so they stay out of `source_files`, and the manifest comment says so. The consistency check's `process/*.md` glob doesn't descend into the subdirectory, so the archive needs no exception there.
7. **Existing installs:** `sdlc-migrate` archives the project's old entries on its next run, without asking (framework copies included: they're the history the project lived through). CD chose automatic over opt-in, so this is a non-optional `contract_changes.yaml` entry and a **major** release.

**The payoff beyond size** was meant to be quantile's changelog dropping under the guard's 200 KB cap, so the over-cap exception in `implement_guard.py` (b1bf1d2) could go. Built as decided, it doesn't: see § Built.

## CD's decisions (2026-10-11)

1. **Project changelogs are project-only going forward:** new installs don't copy cc-sdlc's history.
2. **By quarter:** `[sdlc-root]/process/changelog-archive/YYYY-Qn.md`; when the live file passes about 150 KB, every whole quarter older than the previous one moves out.
3. **A script** does it: `sdlc-archive` runs it in projects, and cc-sdlc's CI checks it.
4. **Existing installs are archived automatically** by their next migration, not offered. That makes the release major.
5. **Copied cc-sdlc entries leave existing installs whatever their quarter** (decided after seeing the incubating project's numbers, § Built). Migration passes cc-sdlc's changelog and archive at the target tag; an entry whose dated heading matches one there moves to the project's archive, whatever its date and the file's size.

## Built (2026-10-11)

As decided, in the changelog entry "Changelog archiving: project-only changelogs, quarterly archive files" and contract 0017. Not released: the next tag is major, and no tag is cut until the history rewrite (handoff § Parked).

- **cc-sdlc's own changelog:** 644 KB → 171 KB (46 entries, Q3–Q4); Q1–Q2 (203 entries) are in `process/changelog-archive/`. It stays over 150 KB until 2027-01-01, when Q3 becomes archivable; the CI check then fails with the command to run.
- **`release.yml` unchanged.** 15 old entries have no `---` before the next; the script keeps them byte for byte, so the release parser sees no old entry as new. Gap: an entry added after a tag but dated into an already archived quarter would miss that release's notes.
- **Porting this commit by path rewrite:** port everything except `process/sdlc_changelog.md` and `process/changelog-archive/`. Its diff deletes 4,000 lines of cc-sdlc's changelog and adds cc-sdlc's archive; applied to a project, that would delete the project's own entries and install cc-sdlc's history. Instead, run `changelog_archive.py archive --upstream` on the project's own changelog, with cc-sdlc's changelog and archive (as `sdlc-migrate` §4.5c does). Later ports add a short port entry to the project's changelog, not a copy of cc-sdlc's.
- **Quantile, when it takes this (by port, or its next migration):** by quarter alone its changelog would have gone from 735 KB to about 265 KB, still over the factory guard's 200 KB cap, because Q3–Q4 held 96 KB of entries copied from cc-sdlc. With decision 5 it goes to **133 KB**: 235 copied entries move to the archive and its 55 own entries stay (checked on a copy, 2026-10-11). The guard's over-cap exception (b1bf1d2) can then go.

