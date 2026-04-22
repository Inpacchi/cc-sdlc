# Framework Compliance Audit Methodology

Full methodology for cc-sdlc framework source repo compliance auditing. Covers all 9 audit dimensions, report format, severity levels, and guiding principles.

## Audit Methodology Sequence

1. **Manifest Scan**: Read `skeleton/manifest.json` — build complete inventory of declared source files
2. **Disk Scan**: Glob all tracked directories and compare against manifest entries
3. **Cross-Reference Check**: Verify skills have CLAUDE-SDLC.md commands, agents are in manifest, knowledge files are wired
4. **Stale Reference Scan**: Grep for old/removed names across the codebase
5. **Changelog Freshness**: Compare `process/sdlc_changelog.md` against recent commits modifying process files
6. **Knowledge Store Scan**: Audit YAML structure, README files, `spec_relevant` fields, conventions
7. **Discipline Health Scan**: Check parking lot entries, triage markers, cross-discipline flow
8. **Skill/Agent Convention Scan**: Verify frontmatter format, required sections, anti-triggers, tools lists
9. **Setup.sh Verification**: Verify installation script handles all manifest files correctly
10. **Report Generation**: Produce structured inline report
11. **Interactive Triage**: Present promotion candidates from disciplines for triage decisions

## Dimension 1: Manifest Completeness

Compare every file on disk against `skeleton/manifest.json` and vice versa.

**Tracked directories:**
- `skills/` — Skill definitions (each skill is a directory with `SKILL.md` and optional `references/`)
- `agents/` — Agent definition files (`.md`)
- `knowledge/` — Knowledge store YAML files organized by discipline
- `process/` — Workflow and process documentation
- `templates/` — Document templates
- `disciplines/` — Discipline parking lot files
- `plugins/` — Plugin setup guides
- `playbooks/` — Playbook files

**What to check:**
- Every file in these directories on disk has a corresponding entry in `skeleton/manifest.json` `source_files`
- Every entry in `skeleton/manifest.json` `source_files` resolves to an actual file on disk
- No phantom entries (manifest references files that don't exist)
- No untracked files (files on disk not in manifest)

**How to validate:**
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('skeleton/manifest.json'))"
```
Then glob `skills/*/SKILL.md`, `skills/*/references/*.md`, `agents/*.md`, `knowledge/**/*.yaml`, `knowledge/**/*.d2`, `process/*.md`, `templates/*.md`, `disciplines/*.md`, `plugins/*.md`, `playbooks/*.md` and cross-reference against manifest `source_files` entries.

## Dimension 2: Cross-Reference Consistency

Verify that framework components are properly cross-referenced across key files.

**Skills → CLAUDE-SDLC.md:**
- Every user-invokable skill in `skeleton/manifest.json` → `source_files.skills` should have a corresponding command entry in `CLAUDE-SDLC.md`
- The command name in CLAUDE-SDLC.md should match the skill directory name
- Skills that are internal-only (not user-invokable) are exempt

**Agents → Manifest:**
- Every agent file in `agents/` should be listed in `skeleton/manifest.json` → `source_files.agents`

**Knowledge → Agent Context Map:**
- New knowledge files should be wired in `knowledge/agent-context-map.yaml` to relevant agent roles
- Check `knowledge/agent-context-map.yaml` for:
  - All mapped file paths resolve to actual files
  - Knowledge YAML files not referenced by any agent (potential gaps)
  - Agents referenced in mappings that don't have corresponding agent files

**Skills/Agents → sdlc-initialize:**
- New skills and agents should be referenced in `skills/sdlc-initialize/` where relevant

**Skills/Agents → sdlc-migrate:**
- New files should be handled in `skills/sdlc-migrate/` migration strategy (direct copy in section 2.1, context-map wiring in section 3.3)

## Dimension 3: Stale Reference Scan

Grep across the entire codebase for references to old, removed, or renamed concepts.

**Known stale references to check:**
- `plugin-dev:agent-development` (replaced by `sdlc-create-agent`)
- Any recently renamed or removed skill names
- Any recently renamed or removed agent names
- References to old directory structures or file paths

**Scope:** All `.md` and `.yaml` files in tracked directories. Exclude `process/sdlc_changelog.md` (changelog entries legitimately reference old names).

**Method:** Maintain a list of known renames/removals (check recent changelog entries for renames). Grep for each old name. Report any hits outside the changelog.

## Dimension 4: Changelog Freshness

Compare `process/sdlc_changelog.md` against recent git history to verify process changes are documented.

**What to check:**
- Recent commits that modify files in `skills/`, `agents/`, `process/`, `disciplines/`, `knowledge/`, `CLAUDE-SDLC.md` — do they have corresponding changelog entries?
- Changelog entries reference actual changes (not phantom entries)
- Entries are dated and describe the change meaningfully

**Method:**
```bash
git log --oneline --since="30 days ago" -- skills/ agents/ process/ disciplines/ knowledge/ CLAUDE-SDLC.md templates/ plugins/ playbooks/
```
Cross-reference commit subjects against changelog entries. Flag process-modifying commits without changelog coverage.

## Dimension 5: Knowledge Store Conventions

Audit knowledge store YAML files for structural consistency and convention adherence.

**Directory structure:** `knowledge/<discipline>/` with YAML files and optional `README.md`

**YAML conventions to check:**
- Files have proper YAML frontmatter/structure
- Required metadata fields present (varies by knowledge type)
- `spec_relevant` field present where applicable
- Consistent key naming across files in the same discipline
- No orphaned YAML files (not wired in context map — overlaps with Dimension 2)

**README completeness:**
- Each knowledge discipline directory should have a `README.md` explaining scope and contents
- README should list all YAML files in the directory with brief descriptions
- README should indicate which agents consume this knowledge

**Diagram files:** Check `.d2` files for syntax validity if present.

## Dimension 6: Discipline Health

### 6a. Discipline Parking Lots (`disciplines/`)

Check each discipline file:

| File | Discipline |
|------|-----------|
| `architecture.md` | System design, component boundaries, integration patterns |
| `business-analysis.md` | Requirements, domain modeling, stakeholder needs |
| `coding.md` | Implementation patterns, conventions, tech debt |
| `data-modeling.md` | Data architecture, schema design |
| `deployment.md` | CI/CD, infrastructure, release management |
| `design.md` | UI/UX, visual design, interaction patterns |
| `process-improvement.md` | Meta-discipline: improving the SDLC itself |
| `product-research.md` | Market, users, competitive landscape |
| `testing.md` | Test strategy, automation, knowledge layers |

**What to check:**
- Are parking lots being written to between audits? (git blame / last-modified)
- Do entries have triage markers (`[READY TO PROMOTE]`, `[NEEDS VALIDATION]`, `[DEFERRED]`)?
- Are cross-discipline insights flowing? (entry in one discipline references another)
- Is there a healthy pipeline from parking lot to knowledge store?

### 6b. Triage Status

**Triage authority matrix:**

| Transition | Authority | When |
|-----------|-----------|------|
| unmarked → `[NEEDS VALIDATION]` | Auto-apply (step 7) | Unmarked for >=2 audit cycles |
| `[NEEDS VALIDATION]` → `[DEFERRED]` | Auto-apply (step 7) | Unvalidated >=3 cycles AND discipline dormant |
| Any → `[READY TO PROMOTE]` | User decision (step 11) | Proposed with evidence during interactive triage |
| `[READY TO PROMOTE]` → Promoted | User decision (step 11) | Actual knowledge file creation during interactive triage |

**Step 7 auto-triage:** Scan entries, apply qualifying low-risk transitions, log actions in report. Collect promotion candidates for step 11.

### 6c. Knowledge-to-Skill Wiring

Two ownership tiers:
1. **Agent-owned (domain):** Agent definitions include Knowledge Context section directing them to `knowledge/agent-context-map.yaml`
2. **Skill-owned (cross-domain):** Skills inject knowledge from other agents' mappings when dispatching into cross-domain contexts

**Check:** Agent definitions have self-lookup sections, skills don't redundantly inject same-agent knowledge, cross-domain injection exists where needed.

### 6d. Discipline Usage Audit

Five usage signals per discipline:

| Signal | Active | Warning | Dead |
|--------|--------|---------|------|
| Parking lot activity | Entries added between audits | Only during audits | No entries since last audit |
| Knowledge consumption | Mapped agents reference knowledge files | Mapped but unused | No mapping |
| Promotion flow | Entries triaged and promoted | Added but not triaged | Static |
| Cross-discipline feed | Receives insights from other domains | Isolated | N/A |
| Growth since seeding | Knowledge files added or expanded | Unchanged since initial seed | N/A |

Report as table with interpretation (healthy / formalized-but-dead / alive-but-unformalized / dead).

## Dimension 7: Skill Convention Compliance

Audit every skill in `skills/` for convention adherence.

**Frontmatter format:**
- Uses YAML frontmatter with `---` delimiters
- `name:` field present and matches directory name
- `description:` uses folded scalar (`>`) for multi-line
- Description includes trigger phrases ("Triggers on...")
- Description includes anti-triggers ("Do NOT use for...")

**Required sections:**
- Title heading matching skill purpose
- Workflow or methodology section
- Red Flags table (common mistakes to avoid)
- Integration section (dispatches, complements, feeds into, uses)

**Content quality:**
- Skill references correct agent names (not stale)
- File paths in skill match source repo structure (not child project paths)
- Skill workflow steps are actionable and clear

## Dimension 8: Agent Convention Compliance

Audit every agent in `agents/` for convention adherence.

**Frontmatter format:**
- Uses YAML frontmatter with `---` delimiters
- `name:` field present
- `description:` includes when-to-use guidance with examples
- `model:` field present (e.g., `sonnet`, `opus`)
- `tools:` field lists required tools
- `color:` field present

**Content quality:**
- Agent has clear role description
- Methodology or approach section present
- Agent references correct file paths for the source repo
- Agent doesn't reference child-project-only concepts (deliverables, catalog, chronicle)

## Dimension 9: Setup.sh Correctness

Verify the installation script handles all framework files correctly.

**What to check:**
- `setup.sh` copies all files listed in `skeleton/manifest.json`
- Skills install to target's `.claude/skills/` (not `ops/sdlc/skills/`)
- Agents install to target's `.claude/agents/` (not `ops/sdlc/agents/`)
- Knowledge, process, templates, disciplines, plugins, playbooks install to target's `ops/sdlc/<type>/`
- New files added to manifest are handled by setup.sh's copy logic
- setup.sh creates all directories listed in manifest's `directories` array

**Method:** Read `setup.sh` and trace its copy logic. Compare against manifest entries. Flag any manifest file that wouldn't be copied by the current script logic.

## Step 11: Interactive Triage

After presenting the audit report, run an interactive triage session for all promotion candidates identified during the audit (from Dimension 6 parking lot entries).

### Triage Workflow

**11a. Collect candidates.** During step 7, build a candidate list. Each candidate needs:
- The entry text (verbatim from parking lot)
- Source location (discipline file + line)
- Evidence (why it's promotion-worthy: recurrence, deliverable references, validation status)
- Suggested target (which knowledge store file it would go into — existing or new)

**11b. Present candidates grouped by discipline.** Use interactive prompts to present candidates in batches (one discipline at a time):

```
TRIAGE: [Discipline Name] — N candidates

1. "[entry text]"
   Source: disciplines/coding.md
   Evidence: Referenced in multiple sessions. Consistent pattern.
   Suggested target: knowledge/coding/typescript-patterns.yaml → new item under "Error Handling"

For each: (P)romote, (D)efer, (S)kip
```

**11c. Apply decisions.**

- **Promote:** Create or update the target knowledge store YAML file with the new entry. Mark the parking lot entry as `Promoted → [target file path] ([date])`.
- **Defer:** Update the parking lot entry marker to `[DEFERRED]` with reason appended.
- **Skip:** Leave the entry unchanged — it stays at its current marker for next audit cycle.

**11d. Report triage results.** Include triage outcomes in the report:

```markdown
### Triage Results
| # | Entry | Decision | Target |
|---|-------|----------|--------|
| 1 | [summary] | Promoted | knowledge/coding/typescript-patterns.yaml |
| 2 | [summary] | Deferred — not validated yet | — |
| 3 | [summary] | Skipped | — |

Promoted: N | Deferred: N | Skipped: N
```

### When to Skip Triage

- **No candidates:** If no promotion candidates found, skip step 11 entirely.
- **User declines:** If user says "skip triage" or "not now," respect that. Note "Triage deferred by user" in the report.

## Report Format

```markdown
## Framework Compliance Audit — [Date]

### Summary
- Compliance score: X/10
- Verdict: [HEALTHY / NEEDS ATTENTION / CRITICAL]
- Top issues: [brief list]

### Dimension 1: Manifest Completeness
- Files on disk not in manifest: [list or none]
- Manifest entries without files: [list or none]

### Dimension 2: Cross-Reference Consistency
- Skills without CLAUDE-SDLC.md commands: [list or none]
- Agents not in manifest: [list or none]
- Knowledge files not in context map: [list or none]
- Missing sdlc-initialize references: [list or none]
- Missing sdlc-migrate handling: [list or none]

### Dimension 3: Stale References
- [list of stale reference findings or "None found"]

### Dimension 4: Changelog Freshness
- Process commits without changelog entries: [list or none]
- Changelog coverage: X/Y recent process commits documented

### Dimension 5: Knowledge Store Conventions
- YAML structure issues: [list or none]
- Missing READMEs: [list or none]
- Missing spec_relevant fields: [list or none]

### Dimension 6: Discipline Health
#### Parking Lot Status
[per-file status, triage markers, cross-discipline flow]

#### Discipline Usage Audit
| Discipline | Parking Lot | Knowledge | Promotion | Cross-Feed | Status |
|-----------|-------------|-----------|-----------|------------|--------|

#### Knowledge-to-Skill Wiring
[wiring status, gaps]

### Dimension 7: Skill Convention Compliance
[per-skill findings — frontmatter, sections, content quality]

### Dimension 8: Agent Convention Compliance
[per-agent findings — frontmatter, content, paths]

### Dimension 9: Setup.sh Correctness
- Unhandled manifest files: [list or none]
- Path mapping issues: [list or none]
- Missing directory creation: [list or none]

### Triage Results
| # | Entry | Decision | Target |
|---|-------|----------|--------|
[triage outcomes — omit section if no candidates or triage skipped]

Promoted: N | Deferred: N | Skipped: N

### Recommendations
[prioritized action items]
```

## Severity Levels

- **Critical**: Manifest entries pointing to nonexistent files, setup.sh not copying required files, skills referencing deleted agents, CLAUDE-SDLC.md missing commands for active skills
- **Warning**: Stale references outside changelog, process commits without changelog entries, knowledge files not wired in context map, skills missing required sections, agents with incorrect paths
- **Info**: Minor naming inconsistencies, optional improvements, unmarked parking lot entries. Note: promotion candidates are handled interactively in step 11 (triage), not reported as INFO findings.

## Guiding Principles

- **Read before asserting.** Never claim a file exists or doesn't without checking.
- **Substance over ceremony.** Flag missing conventions only when the gap creates real risk.
- **Proportional recommendations.** Small gaps get small fixes.
- **Context-aware.** This is a framework source repo — audit the framework's own health, not child project concepts.
- **Toolbox, not recipe.** Empty parking lots aren't failures if the discipline hasn't been needed. Only flag staleness when the discipline IS being exercised but the knowledge layer isn't participating.
- **Source of truth mindset.** Changes here propagate to all child projects — accuracy matters more than speed.
