# CC-SDLC — Claude Code SDLC Toolkit

This is the **source repository** for the cc-sdlc framework. It contains SDLC skills, agents, knowledge stores, and compliance tooling that get installed into target projects via the `sdlc-initialize` skill.

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `skills/` | SDLC skill definitions (installed to target's `.claude/skills/`) |
| `agents/` | Agent definitions (installed to target's `.claude/agents/`) |
| `process/` | Workflow documentation (installed to target's `ops/sdlc/process/`) |
| `templates/` | Document templates (source-only — skills read from cc-sdlc when needed, not installed to targets) |
| `knowledge/` | Domain knowledge stores (installed to target's `ops/sdlc/knowledge/`) |
| `disciplines/` | Discipline parking lots (installed to target's `ops/sdlc/disciplines/`) |
| `plugins/` | Required/optional plugin setup guides (installed to target's `ops/sdlc/plugins/`) |
| `skeleton/` | `manifest.json` — canonical directory structure and file list |
| `CLAUDE-SDLC.md` | SDLC content merged into target project's CLAUDE.md during initialization (not a separate file) |
| `BOOTSTRAP.md` | One-file bootstrap — curl this, say "Bootstrap SDLC", framework installs itself |
| `skills/sdlc-migrate/` | Skill for content-aware framework updates to existing projects |
| `skills/sdlc-initialize/` | Installation skill — handles full framework setup from GitHub source |

## Skill/Agent Location Convention

| Location | Type | Runs in | Purpose |
|----------|------|---------|---------|
| `skills/`, `agents/` | Project skills/agents | Target projects only | Installed to target's `.claude/skills/` and `.claude/agents/` via `sdlc-initialize`. Never run in cc-sdlc source. |
| `.claude/skills/`, `.claude/agents/` | Framework development | cc-sdlc source only | Used to maintain the framework itself. Not installed to target projects. |

**Key implication:** Skills in `skills/` must not reference cc-sdlc source paths like `skeleton/manifest.json` or bare `agents/` — those don't exist in target projects. Use `[sdlc-root]/...` for SDLC content and `.claude/...` for installed skills/agents.

## Plugin Dependencies

| Plugin | Status | Purpose |
|--------|--------|---------|
| **context7** | Required | Live library/framework documentation lookups — prevents stale API knowledge |
| **LSP** (language-specific) | Highly recommended | Type-aware code intelligence — go-to-definition, find-references, hover, diagnostics |

See `plugins/README.md` for details and `plugins/*-setup.md` for installation instructions.

## When Editing This Repo

- Changes to skills, agents, and process docs affect all downstream projects on next migration
- Test changes by copying `skills/sdlc-initialize/` to a scratch project and invoking "Initialize SDLC"
- The `skeleton/manifest.json` is the source of truth for what gets installed — keep it in sync
- CLAUDE-SDLC.md is the drop-in that target projects add to their CLAUDE.md — it must be self-contained
- **Changelog rule:** When you change any process file (skills, agents, process docs, CLAUDE-SDLC.md, disciplines, knowledge), update `process/sdlc_changelog.md` **immediately in the same step** — not as a follow-up. If the user has to ask for the changelog update, it was already too late.
- **Path variable rule:** Skills, agents, and installed docs reference SDLC paths using `[sdlc-root]` — both directories (e.g., `[sdlc-root]/knowledge/`, `[sdlc-root]/disciplines/`) and specific files (e.g., `[sdlc-root]/knowledge/agent-context-map.yaml`, `[sdlc-root]/process/sdlc_changelog.md`). Never use bare paths like `knowledge/`, `disciplines/`, or `agent-context-map.yaml`. The `[sdlc-root]` placeholder resolves to the project's installed location (typically `ops/sdlc/`). Exception: `sdlc-migrate` and `sdlc-initialize` may use bare paths when documenting cc-sdlc source structure or in mapping tables showing source → target.
- **Consistency check rule:** After completing any batch of changes to this repo, run the following checks **before presenting the final summary to the user**. Do not wait to be asked.

### Commit Convention

Use conventional commits with scopes matching the content area:

| Type | Scope | Example |
|------|-------|---------|
| `feat` | `skills`, `agents`, `knowledge`, `process` | `feat(skills): add brand-asset skill` |
| `fix` | `skills`, `agents`, `knowledge`, `process` | `fix(agents): correct frontmatter escaping` |
| `refactor` | `skills`, `agents`, `knowledge`, `process` | `refactor(skills): overhaul archive skill` |
| `docs` | omit or specific area | `docs: update plugin setup guide` |
| `ci` | omit | `ci: add auto-release workflow` |
| `chore` | omit | `chore: update manifest` |

The scope tells you *what* changed; the type tells you *how* it changed.

### Consistency Checks (mandatory after process changes)

**1. Manifest completeness** — Every file on disk must be in `skeleton/manifest.json` and vice versa:
```bash
# Validate JSON
python3 -c "import json; json.load(open('skeleton/manifest.json'))"
```
- Glob `skills/*/SKILL.md`, `skills/*/references/*.md`, `agents/*.md`, `knowledge/**/*.yaml`, `knowledge/**/*.d2`, `process/*.md`, `templates/*.md`, `disciplines/*.md`, `plugins/*.md`, `playbooks/*.md`
- Compare against manifest `source_files` entries. Report any file on disk not in manifest, or manifest entry without a file.

**2. Stale reference scan** — Grep for old/removed names across the codebase:
- Any recently renamed/removed skills, agents, plugins, or concepts
- Only changelog entries should reference old names

**3. Cross-reference consistency:**
- New skills listed in `skeleton/manifest.json` → `source_files.skills`
- New skills have commands in `CLAUDE-SDLC.md` (if user-invokable)
- New agents listed in `skeleton/manifest.json` → `source_files.agents`
- New knowledge files wired in `knowledge/agent-context-map.yaml` to relevant roles
- `sdlc-initialize` references new skills/agents/knowledge where relevant
- `sdlc-migrate` handles new files in its migration strategy (§2.1 for direct copy, §3.3 for context-map wiring)

**4. Agent installation paths** — Framework subagents in `agents/` install to `.claude/agents/` (not `ops/sdlc/agents/`). Verify `sdlc-initialize` Phase 1 copies them correctly.

**5. Hard-coded path scan** — Grep skills and agents for bare SDLC paths that should use `[sdlc-root]`:
```bash
grep -r '`\(knowledge\|disciplines\|playbooks\|process\|templates\|plugins\)/[^R\[\*]' skills/ agents/
```
Ignore hits in `sdlc-migrate` and `sdlc-initialize` (source path documentation) and example output blocks. All other references to these directories should use `[sdlc-root]/...`.

If any check fails, fix it before committing. Do not present the summary until all checks pass.
