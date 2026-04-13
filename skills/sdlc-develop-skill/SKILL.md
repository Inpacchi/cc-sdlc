---
name: sdlc-develop-skill
description: >
  Create or modify SDLC skills following cc-sdlc conventions. Two modes: CREATE mode walks through
  purpose definition, skill type selection (orchestration, utility, exploration, domain-specific),
  frontmatter generation with trigger phrases and anti-triggers, type-appropriate body scaffolding,
  Red Flags table, Integration section, and registration in manifest.json and CLAUDE-SDLC.md.
  MODIFY mode reads an existing skill, identifies changes, auto-wraps custom content in
  PROJECT-SECTION markers, and warns if changes target framework sections that will be overwritten
  on next migration. Enforces single-line YAML descriptions, verb-first naming, manager-rule
  references for agent-dispatching skills, and mandatory sections. Dispatches sdlc-reviewer for
  quality gate.
  Triggers on "create a new skill", "new skill", "add a skill", "scaffold a skill",
  "I need a skill for", "make a skill", "modify a skill", "update a skill", "customize a skill",
  "/sdlc-develop-skill".
  Do NOT use for creating agents — use sdlc-create-agent.
---

# Skill Development

Create or modify SDLC skills following cc-sdlc conventions. Scaffold new skills with convention enforcement, or safely modify existing skills with migration-aware wrapping.

**Argument:** `$ARGUMENTS` (what the skill should do, or which existing skill to modify)

## Mode Selection

| User Intent | Mode | Entry Point |
|-------------|------|-------------|
| "Create a new skill", "scaffold a skill", "I need a skill for X" | **CREATE** | Step 1 (full creation workflow) |
| "Modify a skill", "update a skill", "customize a skill", "add a phase to X" | **MODIFY** | Modify Workflow below |
| Unclear | Ask: "Are you creating a new skill or modifying an existing one?" | — |

---

## CREATE Mode

### Steps

### 1. Purpose Definition

Clarify with the user:
- **What does this skill do?** (one sentence)
- **What skill type?**
  - **Orchestration** — dispatches domain agents, has agent selection criteria, review loops (e.g., sdlc-plan, sdlc-execute, sdlc-review-commit)
  - **Utility** — step-by-step procedure, may or may not dispatch agents (e.g., sdlc-archive, sdlc-reconcile, sdlc-ingest)
  - **Exploration** — open-ended flow, no hard gates, user-directed iteration (e.g., sdlc-idea, sdlc-design-consult)
  - **Domain-specific** — focused on a specific technical domain (e.g., sdlc-tests-create, sdlc-tests-run)
- **What triggers this skill?** (natural language phrases users would say)
- **What should NOT trigger this skill?** (anti-triggers — which existing skills handle adjacent concerns)

### 2. Name Generation

Generate a name following conventions:
- Format: `lowercase-with-hyphens`, 2-4 words
- Verb-first preferred (e.g., `sdlc-review-commit`, not `commit-review`)
- Must not conflict with existing skills

Read `skeleton/manifest.json` → `source_files.skills` to list existing skill names. Present the proposed name and confirm.

### 3. Frontmatter Generation

**CRITICAL:** The `description` field MUST use `>` (folded scalar) for readability. Multi-line quoted strings and block scalars (`|`) break Claude Code's frontmatter parser in some contexts.

The description MUST include:
- What the skill does (1-2 sentences)
- Explicit trigger phrases (`Triggers on "phrase1", "phrase2", ...`)
- Anti-triggers (`Do NOT use for X — use Y.`)

**Activation framing rule:** Use imperative/mandatory language in descriptions and trigger phrases. Advisory framing ("Best practices for X", "Guidance on X") causes agents to skip the skill — empirically measured at ~10% activation rate. Mandatory framing ("Rules that MUST be followed when working on X", "Required steps for X") achieves 57-83% activation. The description is the primary signal agents use to decide whether to invoke the skill — treat it as a trigger, not a summary. (Evidence: Tessl controlled experiment, 30 trials per configuration — `knowledge/coding/context-engineering-patterns.yaml`, activation_engineering section.)

Template:

```yaml
---
name: {name}
description: >
  {What it does — 1-2 sentences}.
  Triggers on "{phrase1}", "{phrase2}", "{phrase3}", "/{name}".
  Do NOT use for {anti-trigger1} — use {alternative1}.
  Do NOT use for {anti-trigger2} — use {alternative2}.
---
```

### 4. Body Scaffolding

Generate the skill body based on type. All types share common requirements; each type adds specific sections.

#### All Types (required sections)

- **Title** — `# {Skill Title}` with 1-2 sentence summary
- **Argument** — `**Argument:** $ARGUMENTS (description)` if the skill accepts input
- **Steps** — numbered steps with `### N. Step Name` headers
- **Red Flags** — `## Red Flags` table (see step 6)
- **Integration** — `## Integration` section (see step 7)

#### Orchestration Skills (additional requirements)

- **Workflow diagram** — `STEP → STEP → STEP` showing the flow
- **Manager Rule** — `## Manager Rule` section: "Read and follow `ops/sdlc/process/manager-rule.md`."
- **Agent Dispatch Protocol** — "Dispatch prompts must describe WHAT/WHY — implementation HOW is the agent's domain."
- **Agent Selection Criteria** — table or tiered list showing which agents to dispatch and when
- **Review lenses** — what each reviewing agent checks for
- **Review-Fix Loop** — reference to `ops/sdlc/process/review-fix-loop.md` if the skill has iterative review

#### Utility Skills (additional requirements)

- **Preconditions** — what must exist before the skill runs
- **Output format** — what artifacts the skill produces and where they go
- **Validation criteria** — how to verify each step succeeded

#### Exploration Skills (additional requirements)

- **Workflow diagram** — non-linear, with iteration loops
- **Core Principles** — what guides the exploration
- **Iterate section** — user controls the loop, with soft prompts after N rounds
- **Optional output format** — exploration may or may not produce artifacts

### 5. Bundled Resources

Determine if the skill needs reference files:
- **references/** — detailed methodology, checklists, or domain-specific content that would bloat SKILL.md (target SKILL.md body at 1,500-3,000 words; overflow goes to references)
- **scripts/** — executable utilities the skill runs repeatedly

If references are needed, create a `## Additional Resources` section at the end of SKILL.md listing each file with a description.

### 6. Red Flags Table

Generate 6-10 red flags specific to this skill. Format:

```markdown
## Red Flags

| Thought | Reality |
|---------|---------|
| "[Common mistake]" | [Why it's wrong and what to do instead] |
```

Include universal red flags relevant to the skill type:
- Orchestration: "I'll implement this myself instead of dispatching" / "The agent has context from earlier"
- All types: "I'll skip the changelog update" / "This skill doesn't need anti-triggers"

**AVOID example warning:** If the skill includes "don't do this" anti-pattern examples, frame them carefully. Tessl found that AVOID examples in skills caused regressions — the agent followed the bad example rather than the instruction. Always pair anti-patterns with the correct pattern immediately after: "DO NOT do this: [bad]. Instead do this: [good]." Never show an anti-pattern without its replacement. (Evidence: Tessl Skill-Optimizer, hooks.md regression in database-plugin-architecture scenario — `knowledge/testing/ai-generated-code-verification.yaml`, eval_contamination section.)

### 7. Integration Section

Generate:

```markdown
## Integration

- **Depends on:** [what must exist before this skill runs]
- **Feeds into:** [what skills consume this skill's output]
- **Uses:** [tools, agents, knowledge files this skill uses]
- **Complements:** [sibling skills]
- **Does NOT replace:** [similar-sounding skills that handle different concerns]
- **DRY notes:** [if this skill overlaps with existing skills, document the boundary]
```

### 8. Write and Register

1. Write the skill file to `skills/{name}/SKILL.md`
2. Add `"skills/{name}/SKILL.md"` to `skeleton/manifest.json` → `source_files.skills`
3. Add a command row to `CLAUDE-SDLC.md` if the skill is user-invokable
4. Add a changelog entry to `process/sdlc_changelog.md`

### 9. Quality Gate

Dispatch the `sdlc-reviewer` subagent on the created skill file. Present its findings. Fix any convention violations before finalizing.

---

## MODIFY Mode

Safely modify an existing skill with migration-aware wrapping. This mode reads the skill, identifies what the user wants to change, determines whether the change is framework-level or project-specific, and applies appropriate protection.

### Modify Workflow

### M1. Read and Analyze

1. Read the existing skill's `SKILL.md`
2. All skills in `.claude/skills/` are framework-installed from cc-sdlc — direct edits to framework sections will be overwritten on next `sdlc-migrate`
3. Warn the user accordingly before making changes

### M2. Classify the Change

Determine whether the user's requested change targets:

| Target | Classification | Action |
|--------|---------------|--------|
| Framework section (gates, workflow, dispatch protocol) | **Framework change** | Warn: "This section is framework-owned and will be overwritten on next migration. Consider proposing this upstream instead." |
| Project-specific addition (new phase, custom agent wiring, domain-specific step) | **Project addition** | Auto-wrap in `PROJECT-SECTION` markers |
| Existing `PROJECT-SECTION` block | **Project update** | Edit within existing markers |

### M3. Apply with Protection

For **project additions** to framework skills:

1. Identify the insertion point (which section/heading the new content belongs under)
2. Wrap the new content in markers:

```html
<!-- PROJECT-SECTION-START: modify-YYYY-MM-DD-description -->
... new project-specific content ...
<!-- PROJECT-SECTION-END: modify-YYYY-MM-DD-description -->
```

3. Apply the edit
4. Confirm to the user that the content is migration-protected

For **framework changes**: present the warning and offer alternatives:
- Propose the change upstream (edit the cc-sdlc source repo)
- Apply anyway with markers (will be preserved but may conflict with upstream changes)
- Apply without markers (will be overwritten on next migration — user accepts this)

### M4. Quality Gate

Dispatch the `sdlc-reviewer` subagent on the modified skill file. Present its findings.

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "The description can span multiple YAML lines with quotes" | Use `>` folded scalar. Other multi-line formats can break Claude Code's frontmatter parser. |
| "This skill doesn't need anti-triggers" | Every skill needs anti-triggers to prevent overlap with siblings. |
| "Red flags are optional for utility skills" | Every skill type needs a Red Flags table. No exceptions. |
| "I'll skip the Integration section — this skill is standalone" | No skill is standalone. Every skill feeds into or complements others. |
| "The name should describe the noun first" | Verb-first naming: `sdlc-review-commit`, not `commit-review`. |
| "I'll register it later" | Registration (manifest, CLAUDE-SDLC.md, changelog) happens in the same step as creation. |
| "This orchestration skill doesn't need the Manager Rule" | If it dispatches agents, it MUST reference manager-rule.md. |
| "I'll write the skill directly without this scaffolding" | Hand-written skills skip convention validation. Use this skill. |
| "SKILL.md can be as long as needed" | Target 1,500-3,000 words for SKILL.md body. Move detailed content to references/. |
| "I'll edit a framework skill directly without markers" | Framework sections are overwritten on migration. Use MODIFY mode to auto-wrap project-specific additions. |
| "The user wants to modify a skill, I'll just edit it" | Check if it's a framework skill first. If so, classify the change and apply appropriate protection. |

## Integration

- **Feeds into:** The created/modified skill becomes part of the SDLC skill library
- **Uses:** `skeleton/manifest.json` (registration), `CLAUDE-SDLC.md` (command table), `sdlc-reviewer` (quality gate), existing skills (as reference patterns)
- **Complements:** `sdlc-create-agent` (agents vs skills), `sdlc-review` (review existing skills)
- **Does NOT replace:** Direct editing of project-owned skills (this adds convention enforcement and migration protection)
