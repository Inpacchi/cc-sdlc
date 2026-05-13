---
name: sdlc-create-agent
description: >
  Create or enrich domain agents following cc-sdlc conventions. CREATE mode walks through
  domain definition, frontmatter, body scaffolding, context-map wiring, and registration.
  ENRICH mode extracts patterns from external sources (articles, agent definitions, docs)
  using a 6-dimension analytical framework and integrates them into an existing agent.
  Dispatches sdlc-reviewer for quality gate in both modes.
  Triggers on "create a new agent", "new agent", "add an agent", "scaffold an agent",
  "I need an agent for", "make an agent", "/sdlc-create-agent",
  "enrich this agent", "extract patterns for [agent]", "what can we learn from these
  for [agent]", "enrich all agents", "bulk enrich".
  Do NOT use for creating skills — use sdlc-develop-skill.
  Do NOT use for ingesting knowledge into discipline stores — use sdlc-ingest.
---

# Agent Creation & Enrichment

Create new domain agents or enrich existing ones with patterns from external sources.

**Argument:** `$ARGUMENTS` (domain for CREATE, or `enrich <agent> <sources>` for ENRICH)

## Mode Resolution

| Invocation | Mode |
|-----------|------|
| `/sdlc-create-agent <domain>` | CREATE |
| `/sdlc-create-agent` (no args) | CREATE (will ask for domain) |
| `/sdlc-create-agent enrich <agent> <sources>` | ENRICH |
| "enrich this agent with..." | ENRICH |
| "bulk enrich" / "enrich all agents" | ENRICH (bulk) |

---

## CREATE Mode

Create a new domain agent that follows cc-sdlc conventions. Scaffold the complete agent file, validate conventions, wire up knowledge context, register, and quality-gate with the reviewer subagent.

## Reference

Read `[sdlc-root]/templates/agent-template.md` before proceeding — it is the canonical structural pattern with full frontmatter reference.

## Steps

### 1. Domain Definition

Clarify with the user:
- **What domain does this agent own?** (directories, packages, concerns)
- **What are the explicit boundaries?** (what belongs to OTHER agents)
- **What cross-domain handoff patterns apply?**
- **What technologies/frameworks is this agent expert in?**

Read the `.claude/agents/` directory to identify existing agents and their domains. Verify no domain overlap with the proposed agent.

### 2. Frontmatter Generation

**CRITICAL:** The `description` field MUST be a double-quoted single-line string using `\\n` (double-backslash n) for newlines. In YAML double-quoted strings, a single `\n` is interpreted as a real newline character which breaks Claude Code's agent frontmatter parser. Always use `\\n` so the parsed string contains a literal `\n`. Block scalars (`|`, `>`) and multi-line quoted strings also break the parser.

The description MUST include:
- Triggering conditions ("Use this agent when...")
- 2-4 `<example>` blocks with Context/user/assistant/commentary structure
- Anti-triggers (when NOT to use this agent)

Generate each field:

**name:** `lowercase-with-hyphens`, 3-50 characters, starts and ends with alphanumeric. Check for conflicts with existing agents.

**description:** Follow the exact format from agent-template.md line 3. Include realistic scenarios in example blocks.

**model:**
- `sonnet` (default) — most agents
- `opus` — architectural decisions, complex trade-offs
- `haiku` — retrieval/search tasks only

**tools:** List ONLY what the agent actually needs. Common sets:
- Read-only analysis: `Read, Glob, Grep`
- Code generation: `Read, Write, Edit, Glob, Grep`
- Full engineering: `Read, Write, Edit, Bash, Glob, Grep`
- Research: `Read, Glob, Grep, WebFetch, WebSearch`

**color:** Choose the color that matches the agent's semantic category. Multiple agents CAN share a color if they belong to the same group — color indicates category, not uniqueness. Semantic groups:
- green: core product
- cyan: architecture + domain
- orange: infrastructure
- red: quality + debugging
- yellow: SDLC process
- blue: business intelligence
- purple: product + design
- pink: creative / external

**memory:** Set to `project` only if the agent needs session-to-session continuity. Omit if stateless.

Present the complete frontmatter for review before proceeding.

### 3. Body Scaffolding

Generate each section following agent-template.md structure:

#### 3a. Scope Statement
```
You own [scope]. You do not touch [boundaries]. [Cross-domain handoff pattern.]
Your domain expertise covers [technologies, frameworks, patterns].
```

#### 3b. Knowledge Context
```
## Knowledge Context

Before starting substantive work, consult `[sdlc-root]/knowledge/agent-context-map.yaml`
and find your entry. Read the mapped knowledge files — they contain reusable patterns,
anti-patterns, and domain-specific guidance relevant to your work.
```

#### 3c. Communication Protocol
Read `[sdlc-root]/knowledge/architecture/agent-communication-protocol.yaml` for the canonical protocol. Add domain-specific handoff fields.

#### 3d. Core Principles
Generate 2-4 concern areas with concrete principles. Each principle has a rationale. Principles are domain-specific, not generic platitudes.

#### 3e. Workflow
Generate 3-5 numbered steps. First step should always involve checking existing patterns before creating new ones.

#### 3f. Anti-Rationalization Table
Generate 5-8 entries in `| Thought | Reality |` format. Include:
- Domain-specific shortcuts the agent might take
- "This is a small change, I'll skip verification" → No size exception
- "I'll change files outside my scope" → Stay in scope, handoff

#### 3g. Self-Verification Checklist
Generate 4-6 domain-specific quality checks. Must include:
- "No changes outside this agent's owned scope"
- "Structured handoff emitted with modified files and follow-up items"

#### 3h. Persistent Agent Memory (if memory: project)
Include the standard memory section from agent-template.md:
- MEMORY.md guidelines (200-line limit)
- What to save / what NOT to save (domain-specific examples)
- Surfacing Learnings to the SDLC section

### 4. Agent Context Map Update

Update `[sdlc-root]/knowledge/agent-context-map.yaml` to add a new entry mapping the agent to relevant knowledge files:

```yaml
  {agent-name}:
    - [sdlc-root]/knowledge/{domain}/relevant-file.yaml
    - [sdlc-root]/knowledge/architecture/agent-communication-protocol.yaml
```

If no domain-specific knowledge files exist yet, map only the communication protocol and note that knowledge files should be added as the domain matures.

### 5. Write and Register

1. Write the agent file to `.claude/agents/{agent-name}.md`
2. Update `[sdlc-root]/knowledge/agent-context-map.yaml` with the mapping
3. Add a changelog entry to `[sdlc-root]/process/sdlc_changelog.md`

### 6. Wire Into Dispatching Skills

New agents are useless if the skills that select agents don't know about them. Determine which dispatching skills need updating based on the agent's role:

**Classify the agent:**

| Role type | Description | Files to update |
|-----------|-------------|-----------------|
| **Reviewer** | Reviews code for domain-specific issues | `[sdlc-root]/process/agent-selection.yaml` § `tiers.tier1` |
| **Builder/Planner** | Implements or plans work in a domain | `sdlc-plan` agent table |
| **Infrastructure specialist** | Owns a specific infrastructure domain | `[sdlc-root]/process/agent-selection.yaml` § `infrastructure_domains` |

Most agents are multiple types. A `db-engineer` is a reviewer (catches schema issues in diffs), a builder (plans migration work), AND an infrastructure specialist (owns the database domain). Apply all that fit.

**For each applicable role:**

1. **`[sdlc-root]/process/agent-selection.yaml` tier1 entry** — Add under `tiers.tier1`:
   ```yaml
   db-engineer:
     dispatch_when:
       - migration files
       - ORM models
       - schema definitions
     covers:
       - migration safety
       - index strategy
       - query patterns
   ```
   This single entry covers review skills (`sdlc-review-code`)

2. **`sdlc-plan` agent table** — Add a row with:
   - Agent name and domain description
   - Example: `` | `db-engineer` | Database schema, migrations, query optimization, index strategy | ``

3. **`[sdlc-root]/process/agent-selection.yaml` infrastructure_domains entry** — Add under `infrastructure_domains`:
   ```yaml
   database-storage:
     triggers:
       - Adds/modifies schema, migrations, or indexes?
       - Changes query patterns or storage paths?
     specialist: db-engineer
   ```
   This covers infrastructure checks in `sdlc-plan` and `sdlc-lite-plan`

**Migration protection:**
- `[sdlc-root]/process/agent-selection.yaml` — NO markers needed. This file is project-specific and never overwritten during migration.
- `sdlc-plan` agent table — YES, wrap additions in `PROJECT-SECTION` markers (framework file that gets overwritten):

```markdown
<!-- PROJECT-SECTION-START: agent-wiring-{agent-name} -->
| `{agent-name}` | {domain description} |
<!-- PROJECT-SECTION-END: agent-wiring-{agent-name} -->
```

Use `agent-wiring-{agent-name}` as the label. This tells `sdlc-migrate` that these dispatcher table entries are project-specific and must be preserved when upstream skill files are content-merged.

**Verify after wiring:**
- The agent name in skills matches the actual agent filename (minus `.md`)
- No duplicate entries (check if a generic placeholder already exists for this domain)
- If replacing a generic name (e.g., `database-architect` → `db-engineer`), update the existing entry rather than adding a duplicate

### 7. Quality Gate

Dispatch the `sdlc-reviewer` subagent on the created agent file. The reviewer checks against the conventions in `[sdlc-root]/process/skill-agent-review.md`. Present its findings. Fix any convention violations before finalizing.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The description can use block scalars (> or \|)" | Agent descriptions MUST be double-quoted single-line with `\\n` escapes (double-backslash). A single `\n` in YAML double-quoted strings becomes a real newline and breaks the parser. |
| "I'll give the agent all tools to be safe" | Fewer tools = less latitude to diverge. Only list what the agent actually needs. |
| "The example blocks are optional" | Examples are the primary trigger mechanism. Without them, Claude Code won't suggest this agent. 2-4 examples minimum. |
| "I don't need anti-rationalization entries" | Every agent rationalizes shortcuts. The table is mandatory. |
| "This agent doesn't need a knowledge context section" | Every agent should consult agent-context-map. Even if no files are mapped yet, the section establishes the pattern. |
| "I'll skip the self-verification checklist" | The checklist is the agent's last chance to catch mistakes before handoff. Mandatory. |
| "The scope statement can be vague" | Vague scope leads to domain overlap. Be explicit about what the agent owns AND does not touch. |
| "Memory should default to project" | Only set `memory: project` if the agent genuinely needs session-to-session continuity. Stateless is simpler. |
| "I'll pick a color that looks good" | Pick the color matching the agent's semantic category (green=product, cyan=architecture, etc.). Multiple agents sharing a color is fine if they're in the same group. |
| "I'll write the agent file directly" | Hand-written agents skip frontmatter validation and convention checks. Use this skill. |
| "I'll wire it into the skills later" | An agent that isn't in the dispatching skills won't get selected. Wire it now or it's invisible. |
| "This source is clearly relevant — extract everything" | Premature satisfaction. Check every dimension against the source. Most content won't apply when viewed through the agent's actual lens. |
| "I'll skip the dismissal defense — all patterns look good" | The defense exists because you feel thorough when you're not. It's mandatory in ENRICH mode. |
| "I'll apply enrichments directly without presenting a plan" | Always compile and present the integration plan first. The user decides what gets integrated. |

---

## ENRICH Mode

Extract patterns from external sources and integrate them into an existing agent. Full methodology in `references/enrichment-methodology.md`.

### Workflow

```
LENS → FETCH → EXTRACT → DEFEND DISMISSALS → PLAN → APPLY → REVIEW
```

1. **Build the analytical lens** — decompose the target agent's domain into questions across 6 dimensions (core operations, failure modes, adjacent knowledge, lifecycle, diagnostics, I/O quality)
2. **Fetch and read sources** — full content, no pre-summarizing
3. **Extract through the lens** — direct, adjacent, and reframed patterns
4. **Defend each dismissal** — guard against surface-level domain mismatch, adjacent blindness, premature satisfaction
5. **Compile integration plan** — group patterns by agent file section, present for approval
6. **Apply changes** — edit naturally into existing content, preserve voice
7. **Verify and review** — completeness check, then `sdlc-reviewer` quality gate

**Bulk mode** handles many sources across many agents via a two-phase structure: Phase 1 (cheap relevance mapping) → Phase 2 (parallel dispatched enrichment in batches of 3-4). See `references/enrichment-methodology.md` for full bulk workflow.

## Integration

- **Feeds into:** Created/enriched agents become available for dispatch by orchestration skills; enrichment may surface knowledge store gaps for `sdlc-ingest`
- **Modifies:** `[sdlc-root]/process/agent-selection.yaml` (tier1 reviewers + infrastructure_domains), `sdlc-plan` (agent table) — see CREATE Step 6
- **Uses:** `[sdlc-root]/templates/agent-template.md` (structural reference), `[sdlc-root]/knowledge/agent-context-map.yaml` (knowledge wiring), `sdlc-reviewer` (quality gate), existing agents (conflict checking), WebFetch (ENRICH mode URL sources)
- **Complements:** `sdlc-develop-skill` (skills vs agents), `sdlc-ingest` (ingests into knowledge stores; ENRICH mode enriches agent definitions)
- **Does NOT replace:** `sdlc-ingest` (which targets discipline knowledge stores, not agent files)

## Additional Resources

- **`references/enrichment-methodology.md`** — Full 6-dimension analytical framework, extraction modes, dismissal defense, bulk mode phases
