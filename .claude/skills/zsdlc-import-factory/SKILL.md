---
name: zsdlc-import-factory
description: >
  Import the software factory from its incubator, quantile, into z-sdlc's opt-in `factory` bundle
  (bundles/factory/). A script sorts quantile's .github/factory/ into bundle code, seeds and the
  project's own files, reports what changed since the last import, copies the bundle code, and
  proves the result by installing it into quantile and into an empty project. Fixes made in z-sdlc
  (a project's pilot finds them) are kept, never overwritten, and handed to quantile with
  --to-incubator, as are newer copies of the bundle's skills and process doc.
  Triggers on "import the factory", "import from quantile", "sync the factory bundle",
  "update the factory bundle", "is the factory bundle in sync", "/zsdlc-import-factory".
  Do NOT use for changing the bundle's skills or process/factory.md: edit those here, then copy
  them into quantile. Do NOT use for installing the bundle into a project: that is sdlc-initialize
  or sdlc-migrate.
---

# Import the Factory

CD decided (2026-10-12) that quantile incubates the software factory and z-sdlc imports it: the factory changes in quantile first, as it runs in production there, and z-sdlc's `factory` bundle is built from quantile's `.github/factory/`. Quantile never installs the bundle (it declines it when `sdlc-migrate` offers it). Two kinds of file go the other way: the stage skills (`skills/sdlc-triage`, `sdlc-implement`, `sdlc-revise`) and `process/factory.md` are z-sdlc's, and quantile keeps exact copies. And a fix found in a project that installed the bundle (the ChronoCore pilot first) goes straight into z-sdlc's bundle code (CD, 2026-10-12); this skill keeps it and copies it into quantile, so quantile's next change builds on it.

**Argument:** `$ARGUMENTS`: `<clone> [commit]`, a local clone of quantile (default `~/Projects/quantile`) and optionally a commit, which becomes `<clone> --commit <commit>`. Pass the same `--commit` on every step.

**Preconditions:** run from the z-sdlc root with `python3` and `git`; the quantile clone has the commit last imported (`import.json`'s `last_import`), so pull it first.

**Exit codes:** 0 when nothing needs a person; 1 when something does or the proof failed, which is the normal result of a report with work to do; 2 on a usage or setup error (an unknown commit, a missing clone, a broken `import.json`).

## Rules

`import.json`, beside this file, sorts every file under quantile's `.github/factory/`:

| Kind | Rule | On import |
|---|---|---|
| Excluded | `excluded` globs: the production tier (`production/`, `host/`, its tests) and quantile's Django-specific database access list | Never imported: per project |
| Seed | `seed` paths: `factory.json`, `planning.json`, `services.json`, `triage-policy.md`, `README.md`, `tests/test_codeowners.py` | Not copied. The bundle keeps its own generic version in `bundles/factory/seed/`; the report says when the bundle's version needs a matching change |
| Bundle code | Everything else | Compared three ways (quantile now, the bundle now, quantile at the last import): quantile's changes are copied into `bundles/factory/tree/`; z-sdlc's own changes are kept and go to quantile; a file changed on both sides is a conflict |

`free_settings` names JSON seed settings whose keys are the project's own data (`stack.env`'s variable names), which aren't compared. `specific` lists patterns of quantile-specific text the report flags when an import adds them. `last_import` is the quantile commit last imported; the script updates it.

## Workflow

### 1. Report

```bash
python3 .claude/skills/zsdlc-import-factory/scripts/import_factory.py ~/Projects/quantile
```

It reads quantile at a commit (`--commit`, default `HEAD`), never its working tree, so only committed work is imported. Check out and pull quantile's `main` first, or pass `--commit origin/main`. The report lists the bundle code added, changed and removed, quantile's commits touching the factory or the mirrored files since the last import, and what needs a person. Each item is tagged with what `--apply` does about it:

- **[fix first] A setting a JSON seed has in quantile but not in the bundle** (for example `smoke.echo_host` in `factory.json`): add it to the bundle's seed with Endless Galaxy's shared default. A project installing the bundle without it fails to render.
- **[fix first] Quantile changed its copy of z-sdlc's text:** port the change into z-sdlc (with a z-sdlc changelog entry), then copy it back.
- **[check, then --accept] A conflict:** bundle code changed in both quantile and z-sdlc since the last import. Merge z-sdlc's change into quantile's file and commit it there; then `--apply --accept` takes quantile's.
- **[check, then --accept] A text seed quantile changed since the last import:** decide whether the bundle's generic version needs the same change.
- **[check, then --accept] Quantile-specific text added to bundle code:** a path, host or name only quantile has. Make the code read it from `factory.json` (or the project's own file) in quantile, then import again; accept it only when the text is right for every project.
- **[for the incubator] z-sdlc is ahead** on bundle code (a fix made here, listed as `ahead`), a skill or the process doc: step 3 copies it into quantile. This never blocks an import, and an import never overwrites it.

### 2. Apply

```bash
python3 .claude/skills/zsdlc-import-factory/scripts/import_factory.py ~/Projects/quantile --apply
```

It writes the bundle code and records the commit in `import.json`, and later reports compare against that commit, so it refuses while a [fix first] item is open: recording the import would hide it. An added or removed bundle file, or a [check, then --accept] item, stops it too: check each (a new file must belong in every project's copy, not quantile's alone), then re-run with `--apply --accept`, or add a rule to `import.json` for a file.

### 3. Hand z-sdlc's changes to quantile

```bash
python3 .claude/skills/zsdlc-import-factory/scripts/import_factory.py ~/Projects/quantile --to-incubator
```

It writes what z-sdlc is ahead on (bundle code, skills, `process/factory.md`) into quantile's working tree, at the commit you imported, and refuses if quantile has uncommitted changes in those files. Commit them in quantile with a quantile changelog entry and let its CI pass; the next report shows them in sync.

### 4. Prove

```bash
python3 .claude/skills/zsdlc-import-factory/scripts/import_factory.py ~/Projects/quantile --prove
```

It installs the bundle as this import makes it, the way `sdlc-initialize` and `sdlc-migrate` would: quantile's bundle code at the commit, with z-sdlc's own changes kept, plus the bundle's seeds. It proves the import whether or not you've applied it yet. It installs into a clone of quantile at the commit (nothing may change but z-sdlc's own changes quantile hasn't taken yet, and the workflow policy must pass), and into an empty project with an Enablement-shaped CODEOWNERS (every template renders, the policy passes, every test passes). Every check must pass before you commit.

### 5. Record

Commit the bundle code, any seed changes and `import.json` together, with a `process/sdlc_changelog.md` entry that names the quantile commit range the script printed and what changed. Then run CLAUDE.md's consistency checks. Pushing and release tags stay CD's.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll copy the changed files over by hand" | The script also catches new and removed files, new seed settings and drifted copies. By hand, quantile's copy of `factory.md` fell a clause behind and the guard tests carried quantile's own CODEOWNERS into the bundle (`process/sdlc_changelog.md`, 2026-10-12). |
| "This new file is obviously generic, --accept" | Read it first. A file that hard-codes quantile's paths, hosts or names becomes every project's. |
| "Quantile's uncommitted fix should come along" | The script reads commits only. Commit it in quantile (CI green) first. |
| "The seed doesn't need the new setting, quantile has it" | The seed is what a new project starts from. Without the setting, its render fails. |
| "I'll fix the skill in quantile and import it" | The skills and `process/factory.md` are z-sdlc's. Change them here and copy them to quantile. |
| "The pilot found a bug; I'll fix it in quantile first" | Fix it straight in z-sdlc's bundle code (CD, 2026-10-12), then step 3 copies it to quantile. |
| "It's a conflict; --accept and move on" | --accept takes quantile's file. Merge z-sdlc's change into quantile first, or the fix is lost. |
| "The proof takes a minute, the report was clean" | The report compares files; only the proof shows the bundle installs and works. |

## Integration

- **Depends on:** a local clone of quantile; `skeleton/manifest.json` → `bundles.factory` (tree, seed, render, skills, process); `import.json`
- **Feeds into:** `bundles/factory/tree/`, `bundles/factory/seed/`, `process/sdlc_changelog.md`; `sdlc-migrate` then delivers the bundle to projects that installed it
- **Uses:** `.claude/skills/zsdlc-import-factory/scripts/import_factory.py`; its tests are `tests/test_import_factory.py` (`python3 -m unittest discover -s tests`)
- **Complements:** `sdlc-migrate`, which goes the other way: z-sdlc's changes into projects, the bundle included for projects that installed it
- **Does NOT replace:** `sdlc-initialize` or `sdlc-migrate`: they install the bundle into a project; this builds the bundle from quantile
