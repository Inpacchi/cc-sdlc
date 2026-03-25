---
name: sdlc-initialize
description: >
  Bootstrap a new project with the cc-sdlc framework — determines whether this is a greenfield or retrofit
  initialization, then walks through the full setup: ideation, spec drafting, skeleton installation, CLAUDE.md
  authoring, deliverable catalog, domain agent creation, knowledge seeding, discipline initialization, and
  verification. This is the single entry point for any project adopting cc-sdlc.
  Triggers on "initialize sdlc", "bootstrap sdlc", "set up sdlc", "sdlc init", "initialize this project",
  "bootstrap this project", "set up the SDLC", "I want to use cc-sdlc", "integrate sdlc",
  "I'd like to bootstrap the SDLC process in this project".
  Do NOT use for resuming existing SDLC work — use sdlc-resume.
  Do NOT use for creating a single deliverable — use sdlc-plan.
  Do NOT use when SDLC is already initialized (ops/sdlc/ exists and is populated) — use sdlc-status instead.
---

# SDLC Initialize

Orchestrate the full initialization of cc-sdlc in a project. This skill detects the project state, selects the right initialization mode, and walks through each phase with CD approval at key gates.

**This skill sets up the framework. It does NOT create deliverables beyond the founding spec.** After initialization, hand off to `sdlc-plan` or `sdlc-lite-plan` for the first piece of implementation work.

**Argument:** `$ARGUMENTS` (optional — cc-sdlc source path, or project description for greenfield)

## Pre-Agent Reality

In greenfield mode, **no domain agents exist until Phase 4.** This means:

- Phases 0–3 are a direct conversation between CD and CC. There is no one to dispatch.
- The Manager Rule does not apply until agents exist. CC writes the spec, CLAUDE.md, and catalog entries directly.
- The Manager Rule activates at Phase 4 and applies for the remainder of the skill and the full session.

This is the only SDLC skill where CC does domain work directly. The justification is structural: you cannot dispatch agents that haven't been created yet.

## Mode Detection

Before starting, determine which mode applies:

```
INITIALIZATION ASSESSMENT
Project directory: [path]
Has existing code: [yes/no — check for src/, lib/, app/, or language-specific indicators]
Has existing docs: [yes/no — check for docs/, README.md beyond boilerplate, specs, design docs]
Has ops/sdlc/: [yes/no]
Has .claude/skills/: [yes/no]
Has .sdlc-manifest.json: [yes/no]
Has spec in docs/current_work/specs/: [yes/no — check for d*_spec.md files]
Has agents in .claude/agents/ (beyond template): [yes/no]
```

| State | Mode | Entry Point |
|-------|------|-------------|
| `ops/sdlc/` exists and populated, agents exist | **Already initialized** | Report status, suggest `sdlc-status` |
| No code, no docs (or only boilerplate), no spec | **Greenfield — fresh** | Phase 0 (ideation + spec) |
| Spec exists in `docs/current_work/specs/`, but no agents | **Greenfield — resume** | Phase 1 (skeleton, then agents) |
| `ops/sdlc/` exists, spec exists, but no agents | **Greenfield — resume (post-skeleton)** | Phase 4 (agents) |
| Has code and/or docs, no `ops/sdlc/` | **Retrofit** | Phase R1 (discovery) |
| `.sdlc-manifest.json` exists but `ops/sdlc/` is incomplete | **Repair** | Phase 1 (re-run setup.sh) |

Present the assessment and mode selection to CD via `AskUserQuestion`:

> Based on what I see, this is a **[mode]** initialization. Does that match your intent, or should I adjust?

**Resume detection:** If the skill was previously invoked and interrupted (e.g., CD ideated in a prior session), the mode detection picks up from wherever it left off. A spec without agents means "ideation is done, continue from scaffolding." A skeleton without agents means "scaffolding is done, continue from agent creation." This makes re-invocation seamless.

---

## Greenfield Mode

For new projects with no existing code. CD and CC define the project together before the scaffold is installed.

### Phase 0: Ideation and Spec

This is a direct conversation between CD and CC. No agents exist yet — CC does the work.

The goal is to produce a D1 spec that establishes the project's identity, tech stack, and structure. Without this, agents, knowledge, and disciplines are impossible to meaningfully create.

#### 0a. If a spec already exists

Read it. Verify it establishes at minimum:
- Problem statement — what you're building and why
- Technology stack — languages, frameworks, databases, infrastructure
- Repository structure — monorepo packages or directory layout

If all three are present, summarize and ask CD: "This spec covers the foundations. Ready to proceed with SDLC scaffolding, or do you want to refine it first?"

If critical sections are missing, note what's missing and ask CD whether to flesh it out now or proceed as-is.

Skip to Phase 1.

#### 0b. If no spec exists — Ideation

Tell CD:

> This is a greenfield project. Before I set up the SDLC framework, we need to define what we're building. Tell me about your project — what problem are you solving, who is it for, and what's your initial vision?

Then enter the ideation loop. The principles here are borrowed from `sdlc-idea` but streamlined for initialization:

**Ground in what you can observe.** Before asking follow-up questions, check:
- Does the repo have any files that hint at direction (package.json, requirements.txt, Cargo.toml)?
- Is there a README with any project description?
- Are there any prior art references in the repo?

**Ask one question at a time.** Do not batch questions. Let each answer inform the next. Use `AskUserQuestion` for every question — no conversational text questions.

**Question priorities for initialization** (these establish what the spec needs):

| Priority | Question Area | Why It Matters |
|----------|--------------|----------------|
| 1 | **Problem + audience** | What are we building and who is it for? |
| 2 | **Technology stack** | Languages, frameworks, databases — determines agents and knowledge |
| 3 | **Repository structure** | Monorepo vs single package, directory layout — determines agent scope |
| 4 | **Deployment target** | Where it runs — determines infrastructure agents and knowledge |
| 5 | **Data model** (if applicable) | Key entities — determines data-modeling knowledge |
| 6 | **Business model** (if applicable) | Monetization, auth model — determines business-analysis discipline |
| 7 | **Non-functional requirements** | Performance bar, security model, compliance needs |

**You do NOT need to ask all of these.** CD may cover several in their initial description. Ask only what's missing. If CD gives a comprehensive description, you may only need 1–2 follow-up questions.

**When CD describes a problem without a solution:** Help them think through the solution space. Sketch 2–3 high-level approaches (not implementations — directional shapes) and let CD pick. This is exploratory, not prescriptive.

**When CD knows exactly what they want:** Don't over-question. If the problem, stack, and structure are clear, move to spec drafting.

**There is no minimum question count.** The goal is a spec with enough content to create agents and seed knowledge. Some projects need 10 minutes of conversation; others need an hour.

#### 0c. Draft the Spec

When enough is understood, draft a D1 spec. CC writes this directly (no agents exist yet).

Use the spec template at `ops/sdlc/templates/spec_template.md` as the structural guide. For initialization, the spec must cover at minimum:

```markdown
# D1: [Project Name] — Spec

**Deliverable:** D1
**Name:** [Project Name]
**Status:** Draft
**Date:** [today]

---

## Problem Statement
[What this project solves and why it matters — from ideation conversation]

## Technology Stack
[Languages, frameworks, databases, infrastructure — specific versions where known]

## Repository Structure
[Directory layout with purpose annotations]

## Requirements
### Functional Requirements
[Key features — numbered FR-1, FR-2, etc.]

### Non-Functional Requirements
[Performance, deployment, security — numbered NFR-1, NFR-2, etc.]

## Data Model (if applicable)
[Key entities and relationships]

## Dependencies
[External services, libraries, infrastructure]

## Success Criteria
[What "done" looks like for D1]

## Open Questions
[Unknowns to resolve during planning]
```

**The spec does not need to be exhaustive.** It needs to be sufficient to:
1. Create domain agents with meaningful stack-specific system prompts
2. Seed knowledge stores with relevant technology patterns
3. Seed disciplines with project context
4. Write a CLAUDE.md with accurate project instructions

More detail is better, but don't block on completeness. Open questions are expected.

#### 0d. CD Approves the Spec

Present the full spec to CD. Use `AskUserQuestion`:

> Here's the D1 spec. Review it and let me know:
> 1. Approved as-is — proceed to scaffolding
> 2. Changes needed — tell me what to adjust
> 3. Need more exploration — let's keep ideating

If CD requests changes, make them directly (no agents to dispatch) and re-present.

**Gate:** CD must approve (option 1) before Phase 1.

### Phase 1: Install the Skeleton

**1a. Locate cc-sdlc source.**

Check in order:
1. `$ARGUMENTS` for an explicit path
2. Common locations: `~/Projects/cc-sdlc`, `~/cc-sdlc`, `../cc-sdlc`
3. Ask CD for the path via `AskUserQuestion`

Verify the source by checking for `skeleton/manifest.json` and `setup.sh`.

**If setup.sh was already run** (`.sdlc-manifest.json` exists and `ops/sdlc/` is populated): Skip to Phase 1c (verify). Do not re-run.

**1b. Run setup.sh.**

```bash
/path/to/cc-sdlc/setup.sh /path/to/this-project
```

Report the output to CD. If any files were skipped (already exist), note them.

**1c. Verify installation.**

Validate against `skeleton/manifest.json` source_files — every file listed must exist at its target path. Report any missing files.

```
SKELETON CHECK
Directories created: [count]
Files installed: [count]
Files skipped: [count]
.sdlc-manifest.json: [exists/missing]

Required directories:
[ ] docs/current_work/audits/
[ ] ops/sdlc/playbooks/
[ ] ops/sdlc/plugins/
[ ] ops/sdlc/examples/

Required files (commonly missed):
[ ] ops/sdlc/knowledge/README.md
[ ] ops/sdlc/knowledge/architecture/README.md
[ ] ops/sdlc/knowledge/data-modeling/README.md
[ ] ops/sdlc/knowledge/design/README.md
[ ] ops/sdlc/knowledge/product-research/README.md
[ ] ops/sdlc/knowledge/testing/README.md
[ ] .claude/skills/sdlc-migrate/SKILL.md
[ ] .claude/agents/AGENT_TEMPLATE.md
[ ] .claude/agents/AGENT_SUGGESTIONS.md
[ ] .claude/skills/sdlc-audit/SKILL.md
[ ] ops/sdlc/plugins/README.md
[ ] ops/sdlc/plugins/context7-setup.md
[ ] ops/sdlc/plugins/lsp-setup.md
```

If any are missing, re-run `setup.sh` with `--force` or copy them manually. Do not proceed to Phase 2 with missing files.

### Phase 1d: Ensure `.claude/agent-memory/` is gitignored

Agent memory files are a private per-agent scratchpad and must not be git-tracked. Valuable learnings flow through `knowledge_feedback` → discipline capture → knowledge stores instead.

Check the project's `.gitignore` for `.claude/agent-memory/`. If the entry is missing, append it:

```
# Agent memory — private scratchpad, not source-controlled
# Reusable learnings flow through knowledge_feedback → discipline capture → knowledge stores
.claude/agent-memory/
```

If `.gitignore` doesn't exist, create it with this entry (plus any standard entries for the project's language/framework).

### Phase 2: Write CLAUDE.md

CC writes CLAUDE.md directly (agents don't exist yet). Use the spec as the source of truth.

**If CLAUDE.md already exists:** Read it. Preserve all existing content. Add the SDLC process section if not present.

**If CLAUDE.md does not exist:** Author it from scratch.

**Required sections for greenfield CLAUDE.md:**

1. **Project header** — name, one-paragraph description
2. **Repository layout** — directory tree with purpose annotations (from spec)
3. **Technology stack** — per-package if monorepo (from spec)
4. **Coding standards** — per-language conventions
   - If multi-language: document the boundary conventions (e.g., snake_case API, camelCase frontend)
5. **SDLC process section** — read `ops/sdlc/CLAUDE-SDLC.md` (installed by setup.sh) and copy the full content, adapted for this project
6. **Verification policy** — zero-assumption rule, Context7 for external libs, read code before asserting
7. **Agent dispatch conventions** — agent-first, never self-implement, manager rule

**Gate:** Present the drafted CLAUDE.md to CD. Use `AskUserQuestion`: "CLAUDE.md is ready for review. Any changes before I save it?"

### Phase 3: Register D1 in the Catalog

1. Read `docs/_index.md` (installed by setup.sh with the template)
2. Register the project's founding deliverable as D1
3. Set status to `Draft` with a link to the spec
4. Increment "Next ID" to D2
5. Save the spec to `docs/current_work/specs/d1_name_spec.md` if it isn't there already

This is mechanical — CC does this directly.

### Phase 4: Create Domain Agents

This is the highest-effort phase. Agents must be customized for the project's actual stack.

**From this phase forward, the Manager Rule activates.** Agents created in this phase will be dispatched for work in subsequent phases.

**4a. Determine agent roster.**

Based on the spec's technology stack, propose a set of domain agents:

| Project Type | Typical Count | Core Roles |
|-------------|--------------|------------|
| Single-framework web app | 4–6 | frontend, backend, code-reviewer, sdet |
| Full-stack with separate API | 6–8 | + db-engineer, devops, debug-specialist |
| Multi-package monorepo | 8–12 | + per-package specialists, architect, security |
| CLI / library | 3–5 | core-engineer, code-reviewer, sdet |

Present the proposed roster to CD via `AskUserQuestion`:

> Based on the spec, I recommend these domain agents: [list with one-line domain descriptions]. Add, remove, or adjust?

**4b. Create each agent.**

**MANDATORY: Invoke `/sdlc-create-agent` for each agent.** Do NOT write agent files directly. The skill handles:
- Frontmatter validation (name format, description with `<example>` blocks)
- System prompt scaffolding (Knowledge Context, Communication Protocol, Anti-Rationalization Table)
- Template compliance (AGENT_TEMPLATE.md structure)

**Creation order:**
1. Roles dispatched most often first (usually backend + frontend + code-reviewer)
2. Specialized roles (db-engineer, security, performance)
3. Cross-cutting roles (architect, sdet)

The `sdlc-audit` skill is already installed by setup.sh — do not recreate it as an agent.

**Pass stack context to the agent creation skill.** Each agent's system prompt must reference the project's actual technologies, not generic placeholders. Include in the creation prompt:
- Which packages/directories the agent owns
- Which frameworks/libraries the agent should know
- Key file paths and conventions from the spec

**4c. Report progress.**

After each agent is created, report to CD: "Created [agent-name] — [domain coverage]." After all agents are created, list the full roster.

**4d. Spec-vs-roster reconciliation.**

Before moving to Phase 5, compare the created agent roster against any agent roles mentioned in the spec (e.g., FR requirements that reference "domain agents" or list specific roles). If the spec lists agents that were not created, or agents were created that the spec doesn't mention:

```
ROSTER RECONCILIATION
Spec-listed roles:    [list from spec FRs/NFRs]
Created agents:       [list from .claude/agents/]
Match:                [yes / deviations listed below]
Deviations:
  - [role] — [not created / created but not in spec] — [reason]
```

Present deviations to CD. This prevents the neuroloom-bootstrap gap where spec-listed agents were silently dropped without a deviation record.

### Phase 5: Wire the Agent-Context Map

1. Read `ops/sdlc/knowledge/agent-context-map.yaml`
2. List the agents just created: `ls .claude/agents/*.md`
3. For each mapping entry:
   - Rename generic roles to match the project's actual agent filenames
   - Remove mappings for roles that have no corresponding agent
   - Add mappings for project-specific agents not in the generic list
4. Save the updated map

This is mechanical — the orchestrator does this directly. The agent filenames must match exactly for self-discovery to work.

### Phase 6: Seed Knowledge Stores

**Now that agents exist, dispatch them for knowledge work.**

**6a. Assess knowledge store relevance.**

Read every YAML file in `ops/sdlc/knowledge/` (installed by setup.sh). Each file has a `project_applicability` block:

```yaml
project_applicability:
  relevant_when: "condition describing when this store applies"
  action_if_irrelevant: keep | customize | remove
```

For each file, compare its `relevant_when` condition against the D1 spec (tech stack, domain, architecture). Classify each as:

- **Keep** — condition matches the project, or `action_if_irrelevant: keep` (always relevant)
- **Customize** — condition doesn't match but the file has a useful structure; replace content with project-appropriate equivalents (e.g., swap MUI DataGrid patterns for your component library)
- **Remove** — condition doesn't match and the content isn't adaptable

Present the assessment to CD:

```
KNOWLEDGE RELEVANCE ASSESSMENT
Based on the D1 spec, here is how each knowledge store maps to this project:

Keep (always relevant or matches spec):
  [x] debugging-methodology — Always relevant
  [x] security-review-taxonomy — Always relevant
  [x] agent-communication-protocol — Governs cc-sdlc agents
  [x] typescript-patterns — Project uses TypeScript
  ...

Customize (useful structure, replace content for your stack):
  [~] testing/tool-patterns — Currently Playwright CLI; replace with [your test tool]
  [~] testing/timing-defaults — Currently React/MUI; replace with [your components]
  [~] testing/component-catalog — Currently MUI DataGrid; replace with [your components]
  ...

Remove (not applicable to this project):
  [ ] payment-state-machine — No payment features in spec
  [ ] ml-system-design — No ML/AI model training in spec
  [ ] pipeline-design-patterns — No ETL/batch pipelines in spec
  ...
```

Use `AskUserQuestion` to let CD confirm. CD may override any classification (e.g., "keep payments — we'll add Stripe in Q2").

**Actions after CD confirms:**
- **Keep** files: no changes needed
- **Customize** files: note them for Phase 6c (agent will rewrite content for the project's stack)
- **Remove** files: delete them from `ops/sdlc/knowledge/` and remove their entries from `agent-context-map.yaml`

**6b. Identify stack-specific knowledge gaps.**

For each major technology in the spec's stack, ask: "What would an agent need to know that isn't obvious from the documentation?" Categories:

- **Gotchas** — things that look right but break
- **Patterns** — the project's preferred way of doing common things
- **Boundaries** — where one technology meets another

**6c. Create stack-specific knowledge files.**

Dispatch the `software-architect` agent (or nearest equivalent) to draft knowledge YAML files for the project's stack-specific technologies. Each file follows the cc-sdlc knowledge format:

```yaml
id: technology-patterns
name: Technology Patterns
description: One-line description
last_updated: YYYY-MM-DD
content:
  - category: Category Name
    items:
      - name: Pattern Name
        description: What this is
        details: Why it matters and how to apply it
```

**Verify via Context7** before writing knowledge files that reference external library APIs. Do not seed knowledge with training-data assumptions about library behavior.

Present the list of knowledge files to CD. This is informational, not a gate — CD can adjust later.

**6d. Tag spec-relevant knowledge stores.**

Walk through all installed knowledge YAML files and identify which should inform spec writing for this project. Present the list grouped by discipline:

```
SPEC-RELEVANCE TAGGING
Which knowledge stores should inform spec writing for this project?
(Stores marked with * are commonly spec-relevant)

Architecture:
  [ ] api-design-methodology — API design patterns
  [ ] backend-capability-assessment — Backend assessment rubric
  [*] security-review-taxonomy — Security posture is a spec-level concern
  ...
Data Modeling:
  [*] people-and-organizations — Party/role data model patterns
  [*] meta-framework — Universal data modeling framework
  ...
Design:
  [*] ux-modeling-methodology — UX interaction modeling
  [*] accessibility-testability-principles — Accessibility rules
  ...
Product Research:
  [*] product-methodology — Product methodology shapes feature scoping
  ...
Testing:
  [*] testing-paradigm — Test type selection (always loaded at spec time by sdlc-plan)
  ...
```

CD selects which stores to mark as `spec_relevant: true`. Update the selected files' `spec_relevant` field from `false` to `true`.

**Guidance:** Tag at least 2-3 files, or leave all as `false` for full loading. Tagging only one file may produce under-informed specs. See `knowledge/README.md` § "spec_relevant Field" for semantics.

**If CD skips this step:** All files stay `false` and `sdlc-plan` spec-time filtering remains dormant — all mapped files load at spec time (backward-compatible behavior). CD can tag stores later by asking the orchestrator to "review spec-relevance tags."

### Phase 7: Seed Discipline Parking Lots

Read each of the 9 discipline files in `ops/sdlc/disciplines/`. For each, add a "## Project Context" section with 3–5 bullets specific to this project's stack and domain.

Dispatch the `software-architect` agent to produce the seed content for all 9 disciplines in one pass, given the spec as input. The agent returns the seed content; the orchestrator appends it to each file.

| Discipline | Seed Focus |
|-----------|-----------|
| architecture | Repo layout, service boundaries, API-first vs monolith |
| coding | Per-language conventions, cross-language boundaries |
| testing | Test suites per package, isolation challenges, mocking stance |
| design | Theme direction, component library, brand constraints |
| data-modeling | ORM/query patterns, migration safety, special column types |
| deployment | Target platform, service topology, local dev stack |
| business-analysis | Revenue model, multi-tenancy, auth strategy |
| product-research | Market context, competitive landscape, ecosystem position |
| process-improvement | Note: "First project from cc-sdlc — capture friction for upstream" |

### Phase 8: Seed Testing Knowledge

Dispatch the `sdet` agent (or nearest equivalent) to produce `ops/sdlc/knowledge/testing/gotchas.yaml` entries specific to the project's technology stack. For each major technology, the agent should identify:

- Test isolation challenges
- Mocking pitfalls
- Async/timing issues
- Environment-specific gotchas (dev vs CI vs prod)

**Verify gotchas via Context7** for any claims about library-specific test behavior.

If `gotchas.yaml` already has upstream content, append project-specific entries — do not overwrite.

### Phase 9: Verify Plugin Readiness

Check whether required plugins are installed:

**context7 (required):**
```bash
grep -r "context7" ~/.claude/settings.json ~/.claude/settings.local.json .claude/settings.json .claude/settings.local.json 2>/dev/null
```

If not found, tell CD:
> context7 is required for library verification. See `ops/sdlc/plugins/context7-setup.md` for installation.

**LSP (highly recommended):**
Check for language-appropriate LSP plugin based on the spec's technology stack.


### Phase 9a: Assess Initial Maturity Levels

Read the maturity level definitions in `ops/sdlc/disciplines/process-improvement.md` (§ Process Maturity Levels). For each of the 9 disciplines, assess the initial level based on what was just set up:

**Level 1 (Initial)** — parking lot file exists with at least one entry but no knowledge store directory for this discipline.

**Level 2 (Managed)** — knowledge store directory exists with at least one validated YAML file AND the agent-context-map wires those files to relevant agents AND parking lot has been seeded.

For most fresh installations, the assessment is straightforward:
- Disciplines that received knowledge seeding in Phases 6-8 AND have entries in `agent-context-map.yaml` → Level 2
- Disciplines with only parking lot seeding from Phase 7 → Level 1

Update the Process Maturity Tracker table in `ops/sdlc/disciplines/process-improvement.md` with the assessed levels and evidence. The tracker was copied from the cc-sdlc source with source-repo levels — it must be adjusted to reflect this project's actual state.

This is a quick assessment (2-3 minutes total), not a gate. Present the tracker to CD as informational.

### Phase 10: Final Verification

Run through the verification checklist:

```
INITIALIZATION COMPLETE — VERIFICATION

Skeleton & Infrastructure:
[ ] Spec: D1 spec exists in docs/current_work/specs/
[ ] Skeleton: setup.sh completed, .sdlc-manifest.json present
[ ] All upstream READMEs copied (knowledge/README.md, knowledge/*/README.md)
[ ] All scaffold directories exist: playbooks/, plugins/, examples/, docs/current_work/audits/
[ ] .gitignore: `.claude/agent-memory/` entry present
[ ] CLAUDE.md: exists with all required sections
[ ] Catalog: docs/_index.md has D1 registered

Agents:
[ ] All agents created via /sdlc-create-agent — confirmed
    Created: [list all agents]
[ ] Spec-vs-roster reconciliation complete — all spec-listed roles created or deviation logged
[ ] AGENT_TEMPLATE.md and AGENT_SUGGESTIONS.md present in .claude/agents/
[ ] Context map: agent-context-map.yaml wired to actual agent filenames
[ ] All knowledge files mapped in agent-context-map.yaml (no unmapped YAMLs)

Knowledge & Disciplines:
[ ] Knowledge: upstream carried + stack-specific seeded
    Stack-specific files: [list]
[ ] Disciplines: all 9 initialized with project context
[ ] Testing: gotchas.yaml seeded with stack-specific entries
[ ] Maturity tracker: updated with project-assessed levels (not source-repo levels)

Plugins:
[ ] context7: [installed / NOT INSTALLED]
[ ] LSP: [installed / not applicable / NOT INSTALLED]
```

Present the checklist to CD. If any items failed, note them and suggest remediation.

**Suggest next step:**

> SDLC initialization is complete. To start your first piece of implementation work:
>
> - **New feature or major work:** invoke `sdlc-plan`
> - **Quick task with a plan:** invoke `sdlc-lite-plan`
> - **Run a health check:** "Let's run an SDLC compliance audit"

---

## Retrofit Mode

For existing projects with code and documentation that need cc-sdlc integrated.

### Phase R1: Discovery

1. Scan the project for existing documentation (markdown files, docs/, design/, specs/)
2. Categorize each document:

| Category | Indicators |
|----------|------------|
| **Spec** | "Specification", "Design", requirements, API definitions |
| **Planning** | "Instructions", "How to", implementation steps |
| **Result** | "COMPLETE", "DONE", completion records |
| **Roadmap** | Future plans, phases, milestones |
| **Reference** | API docs, architecture overview, README |
| **Issue** | "BLOCKED", problems, open questions |

3. Group related documents into logical concepts (domains/features)
4. Check for existing agents in `.claude/agents/`

### Phase R2: Proposal

1. Present categorization table to CD (files found, proposed type, proposed concept)
2. Propose concept groupings for the chronicle
3. Propose which existing docs map to which SDLC artifact types
4. Get CD approval via `AskUserQuestion` before acting

**Gate:** CD must approve the proposal before Phase R3.

### Phase R3: Implementation

1. Run `setup.sh` (same as Greenfield Phase 1)
2. Augment existing CLAUDE.md with SDLC process section (do NOT overwrite)
3. Create concept directories in `docs/chronicle/` based on approved proposal
4. Move/copy existing docs to appropriate locations
5. Backfill `docs/_index.md` with entries for substantial completed work
6. Create domain agents (same as Greenfield Phase 4 — via `/sdlc-create-agent`)
7. Wire agent-context map (same as Greenfield Phase 5)
8. Seed knowledge and disciplines (same as Greenfield Phases 6–8, informed by existing codebase patterns)
9. Assess initial maturity levels (same as Greenfield Phase 9a)

### Phase R4: Verification

Same as Greenfield Phase 10, plus:

```
[ ] Existing documents categorized and moved to SDLC locations
[ ] Chronicle concept directories created with _index.md files
[ ] Deliverable catalog backfilled with completed work
[ ] Existing CLAUDE.md augmented (not replaced)
```

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll skip ideation and go straight to scaffolding" | Agents and knowledge seeded without stack context are generic and unhelpful. Define the project first. |
| "I should dispatch an agent for the spec" | No agents exist yet in greenfield. CC writes the spec directly. This is the one exception to the Manager Rule. |
| "The user described the project, I have enough to create agents" | You have enough to create agents when you have an approved spec with tech stack and repo structure. Not before. |
| "I'll write the agent files directly — the skill is slow" | `/sdlc-create-agent` validates frontmatter, descriptions, and template compliance. Hand-written agents skip these gates. |
| "The context map ships with reasonable defaults" | The defaults use generic role names. If they don't match your agent filenames, self-discovery is broken. |
| "Disciplines can be seeded later" | A few bullets now costs 2 minutes; discovering the gap mid-execution costs a review round. |
| "Context7 is optional for now" | Without it, agents will hallucinate library APIs from training data. Install it before any agent work begins. |
| "I'll overwrite their existing CLAUDE.md with a fresh one" | In retrofit mode, ALWAYS augment. Existing project instructions are authoritative. |
| "The project only needs 2 agents" | Even small projects benefit from code-reviewer + sdet separation. The minimum viable set is 3 (implementer + reviewer + tester). |
| "I'll seed knowledge from training data" | Verify all library/framework claims via Context7 before writing knowledge files. Training data goes stale. |
| "Setup.sh failed, I'll create the directories manually" | Fix the setup.sh failure. Manual creation misses files and skips version tracking. |
| "Manager Rule applies from the start" | In greenfield Phases 0–3, no agents exist. CC works directly. Manager Rule activates at Phase 4. |
| "I'll batch all the ideation questions" | One question at a time via AskUserQuestion. Batched questions get shallow answers. |

## Integration

- **Feeds into:** `sdlc-plan` (first deliverable), `sdlc-lite-plan` (first lightweight task), `sdlc-status` (health check)
- **Uses:** `/sdlc-create-agent` (agent creation), Context7 (knowledge verification), `AskUserQuestion` (CD gates)
- **Produces:** Fully initialized SDLC framework with project-specific agents, knowledge, and disciplines
- **Borrows from:** `sdlc-idea` (ideation principles for Phase 0), spec template (Phase 0c structure)
