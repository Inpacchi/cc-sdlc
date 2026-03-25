---
name: sdlc-migrate
description: >
  Migrate a project's cc-sdlc framework to the latest version — content-aware updates that preserve
  project-specific customizations (parking lots, agent names, build commands, maturity tracker) while
  updating framework sections (skills, knowledge, process docs, agents) to match the current cc-sdlc.
  Triggers on "migrate my SDLC", "update the SDLC", "migrate SDLC framework", "update SDLC framework",
  "upgrade SDLC", "sync SDLC with upstream".
  Do NOT use for first-time installation — use sdlc-initialize.
  Do NOT use when ops/sdlc/ does not exist — use sdlc-initialize.
---

# SDLC Migrate

Apply cc-sdlc upstream updates to a project while preserving project-specific customizations. Unlike `setup.sh` (which copies files and skips modified ones), this skill is **content-aware** — it understands which sections are framework-level vs project-customized and updates them independently.

**Argument:** `$ARGUMENTS` (optional — local path to a cc-sdlc clone. If omitted, resolve via `.sdlc-manifest.json` → `source_repo`, or ask user.)

## Source Repo Access Rule

**All reads from the cc-sdlc source repo MUST use git commands**, not filesystem reads. This ensures you're reading committed state, not the working tree.

- Read a file: `git -C [cc-sdlc-path] show HEAD:<path>`
- List files: `git -C [cc-sdlc-path] ls-tree -r --name-only HEAD`
- Extract a file to the project: `git -C [cc-sdlc-path] show HEAD:<path> > [project-path]/ops/sdlc/<path>`
- Diff since version: `git -C [cc-sdlc-path] diff [source_version]..HEAD`

Never use `cat`, `cp`, `ls`, or direct file reads against `[cc-sdlc-path]`. The source repo may have uncommitted work in progress.

## Pre-Flight Check

Before starting, verify this is a migration (not initialization):

If `ops/sdlc/` doesn't exist → tell user to run `sdlc-initialize` instead and stop.

**Step 1 — Resolve cc-sdlc source to a local path** (in priority order):
1. `$ARGUMENTS` — if the user passed a local clone path, verify with `git -C [path] rev-parse HEAD`
2. `.sdlc-manifest.json` → `source_repo` field (git remote URL) — **clone it immediately:**
   ```bash
   git clone --depth=1 [source_repo] /tmp/cc-sdlc-migrate
   ```
   This is safe and expected — it's a shallow clone of the user's own repo. Use `/tmp/cc-sdlc-migrate` as `[cc-sdlc-path]` for all subsequent phases. Clean up with `rm -rf /tmp/cc-sdlc-migrate` after migration completes.
3. If neither is available, ask the user.

**Step 2 — Report assessment:**

```
MIGRATION ASSESSMENT
Has ops/sdlc/: [yes/no]
Has .sdlc-manifest.json: [yes/no]
Has .claude/agents/: [yes/no]
Has .claude/skills/: [yes/no]
cc-sdlc source: [local path or "cloned from [URL] to /tmp/cc-sdlc-migrate"]
cc-sdlc HEAD: [commit hash from git -C [cc-sdlc-path] rev-parse HEAD]
```

---

## Phase 1: Detect What Changed

### 1.1 Identify Source Version

Read the project's `.sdlc-manifest.json` to get:
- `source_repo` — the git remote URL for the cc-sdlc repo (used to clone if no local path given)
- `source_version` — the commit hash from the last install/migration

Then check what changed in cc-sdlc since that commit (using git, not filesystem):

```bash
git -C [cc-sdlc-path] log --oneline [source_version]..HEAD
git -C [cc-sdlc-path] diff --name-only [source_version]..HEAD
```

If `source_version` is `"unknown"` or missing, treat this as a **full migration** — compare all framework files against the project. Do not stop or ask the user — a full migration is the correct fallback.

### 1.2 Changelog Review Gate

**Before categorizing or applying anything**, read the changelog entries since the project's source version.

Read `process/sdlc_changelog.md` from the cc-sdlc source repo (via `git -C [cc-sdlc-path] show HEAD:process/sdlc_changelog.md`), stopping when you reach entries older than the project's `source_version` date. This is the migration's release notes — it surfaces:

- **Breaking changes** — renamed concepts, moved files, added structural markers, changed conventions
- **New capabilities** — new knowledge files, new disciplines, new agent roles the project may want
- **Human-judgment items** — changes where the project team should decide (e.g., "do you want the new BA discipline wired to an agent?")

**Gate rule:** If any changelog entry describes a breaking change or convention rename, note it for the CLAUDE-SDLC.md compatibility check in §4.3a. If any entry describes a new capability that requires project-team input (new agent roles, new discipline areas), flag it for user review before applying.

Present a brief migration summary to the user via `AskUserQuestion`:

```
Migration summary: [source_version] → [HEAD]
- N commits, M changelog entries
- Breaking changes: [list or "none"]
- New capabilities: [list or "none"]
- Items needing your input: [list or "none"]
Proceed with migration?
```

**Gate:** Wait for user confirmation before continuing to Phase 2.

### 1.3 Categorize Changes

Group the changed cc-sdlc files by migration strategy:

| File Type | Location | Strategy |
|-----------|----------|----------|
| **Skills** | `skills/*/SKILL.md` | Content-merge: update framework sections, preserve project customizations |
| **Agent template** | `agents/AGENT_TEMPLATE.md` | Direct copy (no project customizations) |
| **Agent suggestions** | `agents/AGENT_SUGGESTIONS.md` | Direct copy (no project customizations) |
| **Audit skill** | `skills/sdlc-audit/SKILL.md` + `references/` | Content-merge: update audit methodology, preserve project-specific additions |
| **Knowledge YAMLs** | `knowledge/**/*.yaml` | Direct copy with `spec_relevant` preservation (§2.1b). Check for moved/deleted files (§2.1a) |
| **Process docs** | `process/*.md` | Direct copy (framework-level) |
| **Templates** | `templates/*.md` | Direct copy (framework-level) |
| **Disciplines** | `disciplines/*.md` | Content-merge: update framework guidance, preserve project parking lot entries |
| **Context map** | `knowledge/agent-context-map.yaml` | Never overwrite — project has its own agent names. Update paths for moved/deleted files (§3.3) |
| **Project agents** | Project `.claude/agents/*.md` | Targeted section updates (see Phase 3) |

---

## Phase 2: Apply Framework Updates

### 2.1 Direct Copy Files

For files with no project customizations, copy directly from cc-sdlc to the project's `ops/sdlc/` directory:

- `process/*.md`
- `templates/*.md`
- `knowledge/**/*.yaml` (but NOT `agent-context-map.yaml`)
- `README.md`, `CLAUDE-SDLC.md`
- `agents/AGENT_TEMPLATE.md`, `agents/AGENT_SUGGESTIONS.md`
- `playbooks/*.md` (unless the project has written its own playbooks — check git blame)
- `examples/*.md`

**All reads from the cc-sdlc source repo must use git commands** (e.g., `git -C [cc-sdlc-path] show HEAD:path/to/file`), not filesystem reads. This ensures you're reading committed state, not working tree.

**Ensure `.claude/agent-memory/` is gitignored.** Agent memories are not source-controlled — check the project's `.gitignore` for the entry. If missing, append:

```
# Agent memory — private scratchpad, not source-controlled
# Reusable learnings flow through knowledge_feedback → discipline capture → knowledge stores
.claude/agent-memory/
```

If the project was previously committing agent memory files, note this in the migration report. The files can remain in the working tree but should not be committed going forward. If agent memory files are currently tracked by git, unstage them:

```bash
git rm -r --cached .claude/agent-memory/ 2>/dev/null
```

### 2.1a Remove Deleted and Moved Files

Check the cc-sdlc changelog for files that were **deleted, moved, or renamed** since the project's `source_version`. These require explicit cleanup in the downstream project — direct copy only adds files, it doesn't remove stale ones.

**Process:**

1. From the diff in Phase 1.1, identify any files that were deleted or moved:
   ```bash
   git -C [cc-sdlc-path] diff --name-status [source_version]..HEAD | grep -E '^[DR]'
   ```

2. For each deleted file: remove it from the downstream project's `ops/sdlc/` directory.

3. For each moved/renamed file: the new location was already copied in §2.1. Remove the old location. Then check whether the project's `agent-context-map.yaml` references the old path — if so, update the path (see §3.3).

4. **Scan agent memory files for stale paths (if they exist locally).** Agent memory files (`.claude/agent-memory/*.md`) are not git-tracked but may exist locally and contain hardcoded knowledge file paths that bypass the context map. For each deleted or moved file path, grep agent memories:
   ```bash
   grep -rl "old/path/to/file.yaml" .claude/agent-memory/ 2>/dev/null
   ```
   Update any matches to the new path, or remove references to deleted files.

5. Log all removals and path fixes so the migration report (Phase 4.6) includes them.

**Why this matters:** Without cleanup, downstream projects accumulate orphan files. Worse, if a file was moved (e.g., `knowledge/architecture/foo.yaml` → `knowledge/coding/foo.yaml`), agents mapped to the old path load a stale copy while the updated version sits unwired at the new path. Agent memories are a second source of path references that §3.3 (context map) doesn't cover — they must be scanned separately.

### 2.1b Preserve `spec_relevant` Overrides

Knowledge YAML files are direct-copied from upstream (§2.1), but the project may have overridden `spec_relevant: false` → `spec_relevant: true` for project-specific reasons. This single-field merge preserves those overrides.

**Process for each knowledge YAML being copied:**

1. **Before overwriting**, read the project's current file and extract its `spec_relevant` value. If the file doesn't exist yet (new upstream file), skip — it will be copied with the upstream default.
2. **Copy the upstream file** (overwriting the project's version — all other content is framework-owned).
3. **Restore project override:** If the project's file had `spec_relevant: true` and the upstream file has `spec_relevant: false`, restore the project's `true` in the newly copied file.
4. **Surface upstream upgrades:** If the upstream file has `spec_relevant: true` and the project's file had `spec_relevant: false`, do NOT auto-adopt. Instead, flag it in the migration report:
   ```
   Knowledge spec_relevant upstream upgrade: [file] — upstream now marks as spec-relevant. Review whether to adopt.
   ```
   This ensures the project team is aware of upstream's signal without silently overriding their explicit `false`.

**First migration introducing `spec_relevant`:** If no knowledge file in the project has `spec_relevant` at all (the field didn't exist before this migration), all files will receive `spec_relevant: false` from upstream. After Phase 4 completes, prompt CD to review which stores should be tagged `true` for this project — same walkthrough as `sdlc-initialize` Phase 6d:

1. List all knowledge YAMLs grouped by discipline with their `name` and `description`
2. Mark commonly spec-relevant stores with `*` (see `knowledge/README.md` § "spec_relevant Field" for examples)
3. CD selects which to tag `true`; update the files
4. If CD skips, all files stay `false` and `sdlc-plan` filtering remains dormant (backward compatible)

### 2.2 Content-Merge: Skills

Skills have two layers:
1. **Framework structure** — dispatch patterns, gate logic, manager rules, cross-domain injection
2. **Project customizations** — build commands, agent names, project-specific examples, tech stack references

**Migration process for each skill:**

1. Read the cc-sdlc source version of the skill
2. Read the project's version of the skill
3. Identify framework-level changes (new sections, updated dispatch logic, added/removed gates)
4. Apply those changes while preserving:
   - Project-specific build commands (e.g., `pnpm build` vs `[build command]`)
   - Project-specific agent names in tables and examples
   - Project-specific examples and terminology
   - Project-specific health check URLs and test commands
   - `[PLUGIN: ...]` guards that have been resolved to direct invocations

**Verbatim rule:** Framework content must be copied verbatim from the cc-sdlc source — do not summarize, rephrase, condense, or rewrite in your own words. The source text is the canonical version. When merging, replace the project's framework sections with the exact cc-sdlc text, then re-apply project-specific values (build commands, agent names, etc.) into the appropriate placeholders. If a framework section contains `[build command]` or similar placeholders, substitute the project's actual values — but do not rephrase the surrounding framework text.

**Key rule:** If a section exists in cc-sdlc but not in the project, add it. If a section was removed from cc-sdlc, remove it from the project. If a section was modified in cc-sdlc, update the framework logic while keeping project-specific values.

### 2.3 Content-Merge: Disciplines

Discipline files have:
1. **Framework structure** — status line, knowledge store reference, summary, mutation verification rules, level definitions (in process-improvement.md only)
2. **Project additions** — parking lot entries (with triage markers), active questions, project context sections
3. **Project-assessed data** — the Process Maturity Tracker in `process-improvement.md` (levels reflect the downstream project's state, not the source repo's)

**Migration process:**
1. Update framework sections to match cc-sdlc — **verbatim, not rephrased**
2. Preserve all parking lot entries with their triage markers (these are project-specific knowledge)
3. Preserve active questions
4. Preserve project context sections (added by `sdlc-initialize` Phase 7)
5. Add any new seeded insights from cc-sdlc that the project doesn't have — but do NOT overwrite triage markers on existing entries (the project may have triaged differently than the source repo)
6. **Preserve the Process Maturity Tracker table as-is.** The tracker is delimited by `<!-- PROJECT-TRACKER-START -->` and `<!-- PROJECT-TRACKER-END -->` markers. Everything between these markers (including the table and last-updated note) reflects the project's assessed levels — never overwrite it. Update the framework sections *outside* the markers (level definitions, assessment procedure) to match cc-sdlc. If the downstream file lacks these markers, treat the entire `### Process Maturity Tracker` section through the next heading as project data and preserve it.

### 2.4 Content-Merge: Audit Skill

The `sdlc-audit` skill has framework audit methodology in `SKILL.md` and `references/` that must stay current:

1. Read the cc-sdlc source versions of all audit skill files
2. Read the project's versions
3. Update SKILL.md workflow, modes, and reference pointers — **verbatim from cc-sdlc source, not rephrased**
4. Update `references/compliance-methodology.md` audit dimensions and report format
5. Update `references/improvement-methodology.md` extraction patterns and categorization
6. Update `references/session-reading.md` JSONL format reference
7. Preserve any project-specific audit dimensions or improvement categories added by the project

**Migration note:** The `sdlc-compliance-auditor` agent has been restored as a subagent dispatched by `sdlc-audit`. If the project has an old version, update it to the current version. If the project removed it during a prior migration, re-install it.

### 2.5 Content-Merge Verification Gate

**Before proceeding to agent updates**, verify the content-merge results from §2.2–2.4 didn't corrupt project data. This catches merge errors before they propagate into agent wiring.

**Quick checks (< 2 minutes):**

1. **Tracker integrity** — read `disciplines/process-improvement.md` and verify:
   - `<!-- PROJECT-TRACKER-START -->` / `<!-- PROJECT-TRACKER-END -->` markers are present
   - The table between markers contains the project's levels (not the cc-sdlc source repo's levels)
   - Level definitions outside the markers were updated to match cc-sdlc

2. **Parking lot preservation** — spot-check 2 discipline files:
   - Project-specific entries (dates, deliverable references) are still present
   - Triage markers (`[NEEDS VALIDATION]`, `[DEFERRED]`, `Promoted →`) were not overwritten
   - New seeded insights from cc-sdlc were added without disturbing existing entries

3. **Skill customization preservation** — spot-check 1 skill:
   - Project-specific build commands, agent names, and examples are intact
   - Framework sections were updated (compare against cc-sdlc source)

4. **Audit skill** — verify all reference files were updated and any project-specific audit dimensions preserved

**Gate rule:** If any check fails, fix the merge before continuing. Do not proceed to Phase 3 with corrupted content — agent wiring decisions depend on accurate discipline and knowledge state.

---

## Phase 3: Update Project Agents

Project agents are NOT framework files — they're project-specific. But some sections come from the framework template and should be updated when the template changes.

### 3.1 Identify Template-Derived Sections

These sections originate from the framework and should be updated across all project agents:

| Section | Source | Update Rule |
|---------|--------|-------------|
| `## Knowledge Context` | AGENT_TEMPLATE | Must exist in every agent. If missing, add it. If present, update to match template wording. |
| `## Communication Protocol` | AGENT_TEMPLATE | Update the canonical protocol reference. Preserve domain-specific handoff fields. |
| Memory section header/guidelines | AGENT_TEMPLATE | Update generic guidelines and "Surfacing Learnings to the SDLC" section. Preserve domain-specific "what to save" content. |

### 3.2 Apply Template Updates

For each agent in `.claude/agents/`:
1. Check if `## Knowledge Context` section exists — add if missing
2. Verify Communication Protocol references the correct YAML path
3. Verify memory section guidelines match the latest template
4. Do NOT touch: scope ownership, core principles, workflow, anti-rationalization tables, self-verification checklists, domain-specific content

### 3.3 Update Agent-Context-Map (if needed)

The agent-context-map is **never overwritten** because projects have their own agent names. But it must be updated for four scenarios:

**New knowledge files added to existing roles:** If cc-sdlc added new YAML files that are relevant to existing agents:
1. Read the project's `agent-context-map.yaml`
2. Read the cc-sdlc source's `agent-context-map.yaml` for the new mappings
3. Add new file paths to the project's existing agent entries (matching by role, not by exact name)

**New role entries:** If cc-sdlc added an entirely new role section to the agent-context-map (e.g., `business-analyst`):
1. Read the project's `agent-context-map.yaml`
2. Check if the project has an agent that matches the new role (by role name or responsibility — e.g., the project may use `ba-agent` instead of `business-analyst`)
3. If a matching agent exists: add the new role section using the project's agent name, with the cc-sdlc knowledge file paths
4. If no matching agent exists: add the role section as-is (the project can customize or remove it later)
5. Note the addition in the migration report so the project team can review the wiring

**Moved/renamed knowledge files:** If cc-sdlc moved a file from one directory to another (identified in §2.1a):
1. Search the project's `agent-context-map.yaml` for the old path
2. Replace with the new path
3. Verify the new path exists on disk

**Removed knowledge files:** If cc-sdlc deleted a knowledge file:
1. Search the project's `agent-context-map.yaml` for references to the deleted file
2. Remove those references
3. Note the removal in the migration report

Never remove project-specific mappings that aren't in the cc-sdlc source — those were added during initialization or by the project team.

---

## Phase 4: Verification

### 4.1 File Path Integrity

```bash
# Verify all agent-context-map paths resolve
for path in $(grep -E '^\s+- ' ops/sdlc/knowledge/agent-context-map.yaml | sed 's/.*- //'); do
  [ -f "$path" ] || echo "BROKEN: $path"
done
```

### 4.2 Agent Consistency

```bash
# Verify all agents have Knowledge Context section
for agent in .claude/agents/*.md; do
  grep -q '## Knowledge Context' "$agent" || echo "MISSING Knowledge Context: $agent"
done
```

### 4.3 Skill Verification

Spot-check 2-3 skills to confirm:
- Framework sections updated correctly
- Project customizations preserved
- No orphaned references to removed framework features

### 4.3a CLAUDE-SDLC.md Compatibility Check

The project's `CLAUDE.md` contains CLAUDE-SDLC.md content — skill names, process file paths, conventions, and workflow rules. If the migration renamed a skill, changed a convention, or modified a path, the project's CLAUDE.md will have stale references.

**Check for:**

1. **Skill name references** — verify all skill names mentioned in CLAUDE.md (`sdlc-plan`, `sdlc-execute`, `sdlc-lite-plan`, `sdlc-lite-execute`, `sdlc-idea`, `sdlc-initialize`, `sdlc-reconcile`, `review-diff`, `review-commit`, `review-fix`, `sdlc-create-skill`, `sdlc-create-agent`, `sdlc-review`) still match the actual skill directory names in `ops/sdlc/skills/`. Check for renamed skills: `diff-review` → `review-diff`, `commit-review` → `review-commit`, `commit-fix` → `review-fix`

2. **Process file paths** — verify paths like `ops/sdlc/process/overview.md`, `ops/sdlc/process/sdlc_changelog.md`, `ops/sdlc/process/compliance_audit.md` still exist

3. **Convention changes** — if the changelog (§1.2) flagged breaking convention changes (renamed concepts, changed workflow rules), check whether the project's CLAUDE.md still uses the old terminology

4. **New sections in CLAUDE-SDLC.md** — compare the project's CLAUDE.md SDLC sections against the current `CLAUDE-SDLC.md` source. If new sections were added (e.g., new workflow rules, new verification policies), they should be merged into the project's CLAUDE.md

**Gate rule:** If the project's CLAUDE.md references a renamed skill or removed path, fix it. Stale CLAUDE.md content causes silent process failures — Claude Code follows the instructions but they point nowhere.

### 4.4 Post-Migration Audit

Run the `sdlc-audit` skill in compliance mode directly — do not ask the user to invoke it separately. The compliance methodology's Dimension 7 (Migration Integrity) checks manifest version, framework file completeness, content-merge correctness, and stale references to removed features.

**Run:** `/sdlc-audit compliance` with focus on migration integrity:
- All framework files match the cc-sdlc source at [new commit hash]
- No orphaned files from previous versions remain
- Agent-context-map paths all resolve
- Content-merge preserved project data (tracker levels, parking lot entries, skill customizations)
- CLAUDE-SDLC.md references in CLAUDE.md are valid
- `agents/sdlc-compliance-auditor.md` present and current (dispatched by sdlc-audit)

If the audit returns findings:
- **WARNING or higher:** Fix before continuing. Re-run the auditor after fixes.
- **INFO only:** Log in the migration report, continue to §4.5.

### 4.5 Update Manifest

After migration, update `.sdlc-manifest.json` with the new source version:

```bash
# Update source_version to the current cc-sdlc commit hash
```

### 4.6 Report to User

```markdown
## SDLC Migration Complete

### Source Version
- Previous: [old commit hash]
- Current: [new commit hash]

### Changes Applied
- Agent memory gitignored: yes/already present
- Previously tracked agent memories unstaged: yes/no/not applicable
- Skills updated: N (framework sections merged, project customizations preserved)
- Knowledge files added/updated: N (direct copy with spec_relevant preservation)
- Knowledge spec_relevant overrides preserved: N [list files where project `true` was restored]
- Knowledge spec_relevant upstream upgrades: N [list files where upstream is now `true` — review recommended]
- Knowledge files removed (moved/deleted in source): N [list old paths]
- New agent roles added to context-map: N [list roles]
- Process docs updated: N (direct copy)
- Agent template updated: yes/no
- Agents updated: N (Knowledge Context / Communication Protocol sections)
- Agent-context-map paths updated: N (moved/removed file paths corrected)
- Auditor updated: yes/no
- CLAUDE-SDLC.md sections updated in CLAUDE.md: yes/no/not needed

### Preserved
- Project-specific skill customizations (build commands, agent names, examples)
- Discipline parking lot entries and triage markers
- Process Maturity Tracker (project-assessed levels, not source repo levels)
- Agent-context-map agent names and project-specific mappings
- Project agent domain content (scope, principles, workflow, anti-rationalization)
- Knowledge file `spec_relevant` project overrides (true values restored after upstream copy)

### Gates Passed
- §1.2 Changelog review: user confirmed migration summary
- §2.5 Content-merge verification: tracker intact, parking lots preserved, skills spot-checked
- §4.3a CLAUDE-SDLC.md compatibility: no stale references / [list fixes]

### Verification
- All agent-context-map paths resolve: yes/no
- All agents have Knowledge Context: yes/no
- Spot-check passed: yes/no
- Post-migration audit: passed/findings fixed (auditor dispatched automatically in §4.4)

### Next Steps
1. Review the migration diff: `git diff`
2. Commit the migration
```

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just copy all files from cc-sdlc" | Content-merge exists for a reason — direct copy overwrites project customizations |
| "The project's agent names match cc-sdlc's" | They almost never do. Always read the project's context-map, not the source's |
| "I'll skip the changelog review" | Breaking changes and new capabilities need user input before applying |
| "The tracker levels look right, I'll overwrite them" | The source repo's tracker reflects the source repo's levels, not this project's |
| "I'll rephrase the framework sections to be clearer" | Verbatim rule. Copy exactly from cc-sdlc. Do not rephrase. |
| "I'll remove this agent mapping that cc-sdlc doesn't have" | Project-specific mappings are intentional. Never remove them. |
| "No files were deleted, so §2.1a doesn't apply" | Always check. Moved files appear as add+delete pairs, not renames. |
| "I'll just read the file from the cc-sdlc directory" | Use `git -C [path] show HEAD:file` — never raw filesystem reads. The repo may have uncommitted WIP. |

## Integration

- **Feeds into:** `sdlc-audit` skill (post-migration compliance audit)
- **Depends on:** cc-sdlc source repo (reads via git), `.sdlc-manifest.json` (version tracking)
- **Uses:** `AskUserQuestion` (changelog review gate, user confirmation)
- **Related:** `sdlc-initialize` (first-time setup — use that, not this, for new projects)

## Migration vs Initialization

| Concern | Initialization (`sdlc-initialize`) | Migration (`sdlc-migrate`) |
|---------|-------------------------------------|----------------------------|
| When | First install | Framework update |
| Agent creation | Creates new agents from scratch | Updates template-derived sections in existing agents |
| Skills | Copies from cc-sdlc | Merges framework changes into project-customized skills |
| Context map | Wires generic roles to project agents | Adds new knowledge file mappings only |
| Disciplines | Copies templates | Preserves parking lot entries, updates framework sections |
| Destructive? | No (creates new) | No (merges, never overwrites project content) |
