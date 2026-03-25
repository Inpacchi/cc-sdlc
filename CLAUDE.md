# CC-SDLC — Claude Code SDLC Toolkit

This is the **source repository** for the cc-sdlc framework. It contains SDLC skills, agents, knowledge stores, and compliance tooling that get installed into target projects via `setup.sh`.

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `skills/` | SDLC skill definitions (installed to target's `.claude/skills/`) |
| `agents/` | Agent definitions (installed to target's `.claude/agents/`) |
| `process/` | Workflow documentation (installed to target's `ops/sdlc/process/`) |
| `templates/` | Document templates (installed to target's `ops/sdlc/templates/`) |
| `knowledge/` | Domain knowledge stores (installed to target's `ops/sdlc/knowledge/`) |
| `disciplines/` | Discipline parking lots (installed to target's `ops/sdlc/disciplines/`) |
| `plugins/` | Required/optional plugin setup guides (installed to target's `ops/sdlc/plugins/`) |
| `skeleton/` | `manifest.json` — canonical directory structure and file list |
| `CLAUDE-SDLC.md` | Drop-in CLAUDE.md addition for target projects |
| `skills/sdlc-migrate/` | Skill for content-aware framework updates to existing projects |
| `setup.sh` | Installation script |

## Plugin Dependencies

| Plugin | Status | Purpose |
|--------|--------|---------|
| **context7** | Required | Live library/framework documentation lookups — prevents stale API knowledge |
| **LSP** (language-specific) | Highly recommended | Type-aware code intelligence — go-to-definition, find-references, hover, diagnostics |

See `plugins/README.md` for details and `plugins/*-setup.md` for installation instructions.

## When Editing This Repo

- Changes to skills, agents, and process docs affect all downstream projects on next migration
- Test changes by running `setup.sh` against a scratch directory
- The `skeleton/manifest.json` is the source of truth for what gets installed — keep it in sync
- CLAUDE-SDLC.md is the drop-in that target projects add to their CLAUDE.md — it must be self-contained
- **Changelog rule:** When you change any process file (skills, agents, process docs, CLAUDE-SDLC.md, disciplines, knowledge), update `process/sdlc_changelog.md` **immediately in the same step** — not as a follow-up. If the user has to ask for the changelog update, it was already too late.
