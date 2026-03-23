# SDLC Migration Instructions

**For Claude Code:** Follow these instructions when a user asks to update their project's SDLC framework to the latest cc-sdlc version. Unlike `setup.sh` (which copies files and skips modified ones), migration is **content-aware** — it understands which sections are framework-level vs project-customized and updates them independently.

**When to use:** After the cc-sdlc framework has been updated (new features, bug fixes, pattern changes) and projects need those changes without losing their project-specific customizations.

---

## Phase 1: Detect What Changed

### 1.1 Identify Source Version

Read the project's `.sdlc-manifest.json` to get the `source_version` (commit hash) from the last install/migration.

```bash
cat .sdlc-manifest.json | grep source_version
```

Then check what changed in cc-sdlc since that commit:

```bash
git -C [cc-sdlc-path] log --oneline [source_version]..HEAD
git -C [cc-sdlc-path] diff --name-only [source_version]..HEAD
```

If `source_version` is "unknown" or `.sdlc-manifest.json` doesn't exist, treat this as a full migration — compare all framework files.

### 1.2 Categorize Changes

Group the changed cc-sdlc files by migration strategy:

| File Type | Location | Strategy |
|-----------|----------|----------|
| **Skills** | `skills/*/SKILL.md` | Content-merge: update framework sections, preserve project customizations |
| **Agent template** | `agents/AGENT_TEMPLATE.md` | Direct copy (no project customizations) |
| **Agent suggestions** | `agents/AGENT_SUGGESTIONS.md` | Direct copy (no project customizations) |
| **Auditor agent** | `agents/sdlc-compliance-auditor.md` | Content-merge: update audit logic, preserve project-specific memory paths |
| **Knowledge YAMLs** | `knowledge/**/*.yaml` | Direct copy (cross-project, no customizations). Check for moved/deleted files (§2.1a) |
| **Process docs** | `process/*.md` | Direct copy (framework-level) |
| **Templates** | `templates/*.md` | Direct copy (framework-level) |
| **Disciplines** | `disciplines/*.md` | Content-merge: update framework guidance, preserve project parking lot entries |
| **Bootstrap/migration** | `BOOTSTRAP.md`, `MIGRATE.md` | Direct copy (framework-level) |
| **Context map** | `knowledge/agent-context-map.yaml` | Never overwrite — project has its own agent names. Update paths for moved/deleted files (§3.3) |
| **Project agents** | Project `.claude/agents/*.md` | Targeted section updates (see Phase 3) |

---

## Phase 2: Apply Framework Updates

### 2.1 Direct Copy Files

For files with no project customizations, copy directly from cc-sdlc to the project's `ops/sdlc/` directory:

- `process/*.md`
- `templates/*.md`
- `knowledge/**/*.yaml` (but NOT `agent-context-map.yaml`)
- `BOOTSTRAP.md`, `MIGRATE.md`, `README.md`, `CLAUDE-SDLC.md`
- `agents/AGENT_TEMPLATE.md`, `agents/AGENT_SUGGESTIONS.md`
- `playbooks/*.md` (unless the project has written its own playbooks — check git blame)
- `examples/*.md`

### 2.1a Remove Deleted and Moved Files

Check the cc-sdlc changelog (`process/sdlc_changelog.md`) for files that were **deleted, moved, or renamed** since the project's `source_version`. These require explicit cleanup in the downstream project — direct copy only adds files, it doesn't remove stale ones.

**Process:**

1. From the diff in Phase 1.1, identify any files that were deleted or moved (appear in `--diff-filter=D` or `--diff-filter=R`):
   ```bash
   git -C [cc-sdlc-path] diff --name-status [source_version]..HEAD | grep -E '^[DR]'
   ```

2. For each deleted file: remove it from the downstream project's `ops/sdlc/` directory.

3. For each moved/renamed file: the new location was already copied in §2.1. Remove the old location. Then check whether the project's `agent-context-map.yaml` references the old path — if so, update the path (see §3.3).

4. Log all removals so the migration report (Phase 4.6) includes them.

**Why this matters:** Without cleanup, downstream projects accumulate orphan files. Worse, if a file was moved (e.g., `knowledge/architecture/foo.yaml` → `knowledge/coding/foo.yaml`), agents mapped to the old path load a stale copy while the updated version sits unwired at the new path.

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

### 2.4 Content-Merge: Auditor Agent

The `sdlc-compliance-auditor.md` has framework audit logic that must stay current:

1. Read the cc-sdlc source version
2. Read the project's version
3. Update all numbered sections (Core Responsibilities 1-9, severity levels, guiding principles) — **verbatim from cc-sdlc source, not rephrased**
4. Preserve the project's agent memory path
5. Preserve any project-specific audit dimensions added by the project

---

## Phase 3: Update Project Agents

Project agents are NOT framework files — they're project-specific. But some sections come from the framework template and should be updated when the template changes.

### 3.1 Identify Template-Derived Sections

These sections originate from the framework and should be updated across all project agents:

| Section | Source | Update Rule |
|---------|--------|-------------|
| `## Knowledge Context` | AGENT_TEMPLATE | Must exist in every agent. If missing, add it. If present, update to match template wording. |
| `## Communication Protocol` | AGENT_TEMPLATE | Update the canonical protocol reference. Preserve domain-specific handoff fields. |
| Memory section header/guidelines | AGENT_TEMPLATE | Update generic guidelines. Preserve domain-specific "what to save" content. |

### 3.2 Apply Template Updates

For each agent in `.claude/agents/`:
1. Check if `## Knowledge Context` section exists — add if missing
2. Verify Communication Protocol references the correct YAML path
3. Verify memory section guidelines match the latest template
4. Do NOT touch: scope ownership, core principles, workflow, anti-rationalization tables, self-verification checklists, domain-specific content

### 3.3 Update Agent-Context-Map (if needed)

The agent-context-map is **never overwritten** because projects have their own agent names. But it must be updated for three scenarios:

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

Never remove project-specific mappings that aren't in the cc-sdlc source — those were added during bootstrap or by the project team.

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

### 4.4 Post-Migration Audit

Run the `sdlc-compliance-auditor` agent to verify migration integrity. The auditor's §7 (Migration Integrity) checks manifest version, framework file completeness, content-merge correctness, and stale references to removed features — exactly what needs validation after a migration.

```
"Let's run an SDLC compliance audit"
```

Fix any findings before committing the migration.

### 4.5 Update Manifest

After migration, update `.sdlc-manifest.json` with the new source version and file hashes:

```bash
# Re-run setup.sh in diff mode to regenerate the manifest
# Or manually update source_version to the current cc-sdlc commit hash
```

### 4.6 Report to User

```markdown
## SDLC Migration Complete

### Source Version
- Previous: [old commit hash]
- Current: [new commit hash]

### Changes Applied
- Skills updated: N (framework sections merged, project customizations preserved)
- Knowledge files added/updated: N (direct copy)
- Knowledge files removed (moved/deleted in source): N [list old paths]
- Process docs updated: N (direct copy)
- Agent template updated: yes/no
- Agents updated: N (Knowledge Context / Communication Protocol sections)
- Agent-context-map paths updated: N (moved/removed file paths corrected)
- Auditor updated: yes/no

### Preserved
- Project-specific skill customizations (build commands, agent names, examples)
- Discipline parking lot entries and triage markers
- Process Maturity Tracker (project-assessed levels, not source repo levels)
- Agent-context-map agent names and project-specific mappings
- Project agent domain content (scope, principles, workflow, anti-rationalization)

### Verification
- All agent-context-map paths resolve: yes/no
- All agents have Knowledge Context: yes/no
- Spot-check passed: yes/no
- Post-migration audit: passed/findings fixed

### Next Steps
1. Review the migration diff: `git diff`
2. Commit the migration
```

---

## Migration vs Bootstrap

| Concern | Bootstrap | Migration |
|---------|-----------|-----------|
| When | First install | Framework update |
| Agent creation | Creates new agents from scratch | Updates template-derived sections in existing agents |
| Skills | Copies from cc-sdlc | Merges framework changes into project-customized skills |
| Context map | Wires generic roles to project agents | Adds new knowledge file mappings only |
| Disciplines | Copies templates | Preserves parking lot entries, updates framework sections |
| Destructive? | No (creates new) | No (merges, never overwrites project content) |
