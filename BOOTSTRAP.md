# SDLC Bootstrap Instructions

**For Claude Code:** Follow these instructions when a user asks to implement this SDLC process in their project.

---

## Phase 1: Discovery

### 1.1 Identify Existing Documentation

Scan the project for documentation:

```bash
# Check for existing docs directory
ls -la docs/ 2>/dev/null || echo "No docs/ directory"

# Find markdown files
find . -name "*.md" -type f | head -50

# Check for common doc patterns
ls -la {docs,documentation,doc,specs,design}/ 2>/dev/null
```

### 1.2 Categorize Existing Artifacts

For each document found, classify it:

| Category | Indicators |
|----------|------------|
| **Spec** | "Specification", "Design", requirements, API definitions |
| **Planning** | "Instructions", "How to", implementation steps |
| **Result** | "COMPLETE", "DONE", completion records |
| **Roadmap** | Future plans, phases, milestones |
| **Reference** | API docs, architecture overview, README |
| **Issue** | "BLOCKED", problems, open questions |

### 1.3 Identify Concepts

Group related documents into logical concepts:
- What domains/features does this project cover?
- Are there natural groupings (e.g., "authentication", "data model", "UI")?
- What would someone ask about? ("How does X work?")

---

## Phase 2: Proposal

### 2.1 Create Categorization Table

Present findings to the user:

```markdown
## Existing Documentation Analysis

### Documents Found: N files

### Proposed Categorization

| File | Current Location | Type | Proposed Concept |
|------|------------------|------|------------------|
| auth_spec.md | docs/ | Spec | 01_authentication |
| api_design.md | design/ | Spec | 02_api |
| ... | ... | ... | ... |

### Proposed Concepts

| # | Concept | Description | Files |
|---|---------|-------------|-------|
| 01 | authentication | User auth, sessions, tokens | 3 |
| 02 | api | REST endpoints, schemas | 5 |
| ... | ... | ... | ... |

### Recommended Actions

1. Create SDLC directory structure
2. Move/copy existing docs to appropriate locations
3. Create _index.md for each concept
4. Add templates for future work
```

### 2.2 Get User Approval

Ask: "Does this categorization look correct? Any adjustments before I create the structure?"

---

## Phase 3: Implementation

### 3.1 Create Directory Structure

Read `skeleton/manifest.json` from the cc-sdlc package to get the canonical directory list. Create each directory:

```bash
mkdir -p docs/current_work/{specs,planning,results,issues,audits,sdlc-lite}
mkdir -p docs/chronicle
mkdir -p docs/testing/{specs,knowledge}
```

### 3.2 Create Project-Specific Concepts

For each identified concept:

```bash
mkdir -p docs/chronicle/concept_name/{specs,planning,results}
```

### 3.3 Create Index Files

For each concept, create `docs/chronicle/concept_name/_index.md`:

```markdown
# NN_concept_name

## Overview
[One paragraph describing this concept]

## Deliverables
[Table of specs, planning docs, results]

## Common Tasks
[How to do common things in this area]

## Key Decisions
[Important architectural choices]
```

### 3.4 Copy Templates

Copy from the cc-sdlc `templates/` directory to `docs/templates/` in the project.

### 3.5 Move Existing Documents

For each categorized document:
- Copy to appropriate chronicle location
- Or move to `current_work/` if still active

### 3.6 Create `docs/_index.md`

This is the deliverable catalog — the single source of truth for all deliverable IDs and their statuses.

```markdown
# Project Deliverable Catalog

| ID | Name | Status | Location |
|----|------|--------|----------|
| D1 | [First deliverable] | Complete | chronicle/[concept]/results/ |
```

If existing work predates the SDLC, backfill entries for substantial completed work.

### 3.7 Create/Update CLAUDE.md

**IMPORTANT: Do NOT overwrite existing CLAUDE.md files.**

For projects with existing CLAUDE.md:
1. Read the existing file completely
2. Preserve all existing content (project purpose, stack, APIs, conventions)
3. **Add** the SDLC compliance section (see below) if not present
4. **Add** references to docs/current_work/ and chronicle locations if not present

For projects without CLAUDE.md:
- Create a minimal CLAUDE.md with project-specific content
- Add the SDLC compliance section below

The goal is to **augment**, not replace.

**Add this SDLC compliance section:**

```markdown
## SDLC Process

This project follows a lightweight SDLC framework. Reference material lives in `ops/sdlc/`.

### Deliverable Workflow
Idea → Spec (CD approves) → Plan (reviewed) → Execute → Review → Result → Chronicle

### Deliverable Tracking
- **IDs:** Sequential: D1, D2, ... Dnn (never reused)
- **Catalog:** `docs/_index.md`
- **Active work:** `docs/current_work/`
- **Archived work:** `docs/chronicle/`

### When to Use Full Process vs. SDLC-Lite vs. Direct Dispatch
- **Full SDLC (deliverable ID):** New features, architectural changes, new integrations, new subsystems
- **SDLC-Lite:** Complex enough to benefit from a reviewed plan, but doesn't need full tracking
- **Direct dispatch:** CD steers in real-time — agents do the work, no plan file needed

### Commands
| Command | Action |
|---------|--------|
| "Let's catalog our ad hoc work" | Reconcile untracked commits |
| "Let's organize the chronicles" | Archive completed work |
| "Let's run an SDLC compliance audit" | Audit spec coverage and catalog integrity |
```

### 3.8 Create or Update Domain Agents

If the project doesn't have domain agents yet, create them now. If agents exist, verify they follow the current template structure.

1. Review `agents/AGENT_SUGGESTIONS.md` for recommended roles matching your project type
2. **MANDATORY: Invoke the `/plugin-dev:agent-development` skill for each agent.** Do NOT write agent files directly — the skill handles frontmatter validation, description formatting with `<example>` blocks, system prompt scaffolding, and ensures compliance with the template structure. Writing agent files by hand bypasses these quality gates.
3. The skill will produce agents following `agents/AGENT_TEMPLATE.md`: scope ownership, Knowledge Context section, Communication Protocol, Core Principles, Workflow, Anti-Rationalization Table, Self-Verification Checklist, and Persistent Agent Memory
4. Verify every agent includes the `## Knowledge Context` section that directs it to self-lookup from `agent-context-map.yaml`

### 3.9 Wire Up Agent-to-Knowledge Context Map

The knowledge layer (`ops/sdlc/knowledge/`) ships with an `agent-context-map.yaml` that maps generic role names (e.g., `architect`, `sdet`, `backend-developer`) to knowledge files. Update this file to use the project's **actual agent filenames** from `.claude/agents/`.

1. Read `ops/sdlc/knowledge/agent-context-map.yaml`
2. List the project's agents: `ls .claude/agents/*.md`
3. For each mapping entry:
   - Rename generic roles to match the project's agent filenames (e.g., `architect` → `software-architect`)
   - Remove mappings for roles that have no corresponding agent
   - Add mappings for project-specific agents not in the generic list (e.g., `fullstack-engineer`, `taste-intelligence-engineer`)
4. Keep the knowledge file paths unchanged — the YAML files are cross-project

Agents self-lookup their mapped knowledge files via a `## Knowledge Context` section in their definition, so the role names must match exactly. Skills also consult this map for cross-domain knowledge injection when dispatching agents into contexts outside their primary domain.

---

## Phase 4: Verification

### 4.1 Structure Check

```bash
# Verify directory structure
find docs/ -type d | sort

# Count files by location
echo "Specs: $(ls docs/current_work/specs/*.md 2>/dev/null | wc -l)"
echo "Concepts: $(ls -d docs/chronicle/*/ 2>/dev/null | wc -l)"
```

### 4.2 Index Completeness

Verify each concept has `_index.md`:

```bash
for dir in docs/chronicle/*/; do
  [ -f "$dir/_index.md" ] || echo "Missing index: $dir"
done
```

### 4.3 Deliverable Catalog Check

Verify `docs/_index.md` exists and has the correct format.

### 4.4 Report to User

```markdown
## SDLC Implementation Complete

### Structure Created
- current_work/: specs, planning, results, issues, audits, sdlc-lite
- chronicle/: N concepts with indexes
- templates/: M templates copied
- docs/_index.md: deliverable catalog initialized
- agent-context-map.yaml: wired to N project agents

### Next Steps
1. Review the concept indexes for accuracy
2. Start using deliverable IDs (D1, D2, ...) for new work
3. Install required plugin: **context7** — see ops/sdlc/plugins/context7-setup.md
4. Install LSP plugin for your language(s) (highly recommended) — see ops/sdlc/plugins/lsp-setup.md
   - Optional: oberskills (prompt engineering + web research) — see ops/sdlc/plugins/oberskills-setup.md
5. Run an SDLC compliance audit: "Let's run an SDLC compliance audit"
6. See ops/sdlc/process/overview.md for workflow details
```

---

## Artifact Type Reference

### Spec (`docs/current_work/specs/`)
**Purpose:** Define WHAT to build
**Naming:** `dNN_feature_name_spec.md`
**Contains:** Problem statement, requirements, design/approach, success criteria

### Planning (`docs/current_work/planning/`)
**Purpose:** Define HOW to build it
**Naming:** `dNN_feature_name_plan.md`
**Contains:** Step-by-step implementation guide, files to modify, test approach

### Result (`docs/current_work/results/`)
**Purpose:** Record completion
**Naming:** `dNN_feature_name_result.md`
**Contains:** What was implemented, files changed, test results, deviations from spec

### Issue (`docs/current_work/issues/`)
**Purpose:** Track blockers
**Naming:** `dNN_feature_name_BLOCKED.md`
**Contains:** What's blocked, why, what's needed to unblock, workarounds

---

## Notes for CC

1. **Always propose before acting** — Show the user the categorization and get approval
2. **Preserve existing structure** — Don't delete or move without confirmation
3. **Create indexes thoughtfully** — They're the primary navigation tool
4. **Adapt to project size** — Small projects may not need all concepts
5. **Document decisions** — Record why things are organized the way they are
6. **Install skills** — After bootstrapping, ask if the user wants the SDLC skills installed in `.claude/skills/`
7. **Install required plugins** — Remind the user to install context7 (required) and optionally oberskills (see `ops/sdlc/plugins/README.md`)
