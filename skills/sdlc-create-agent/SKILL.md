---
name: sdlc-create-agent
description: >
  Create a new domain agent following cc-sdlc conventions. Walks through domain definition,
  frontmatter generation (single-line description with example blocks, model selection,
  tools list, color, memory setting), body scaffolding (scope, knowledge context,
  communication protocol, core principles, workflow, anti-rationalization table,
  self-verification checklist, persistent memory section), agent-context-map update,
  registration, and wiring into dispatching skills ([sdlc-root]/process/agent-selection.yaml for all review skills,
  sdlc-plan, sdlc-lite-plan). Dispatches sdlc-reviewer for quality gate.
  Use when the project needs a new domain agent that doesn't exist yet.
  Triggers on "create a new agent", "new agent", "add an agent", "scaffold an agent",
  "I need an agent for", "make an agent", "/sdlc-create-agent".
  Do NOT use for creating skills — use sdlc-develop-skill.
  Do NOT use for modifying existing agents — edit directly.
---

# Agent Creation

Create a new domain agent that follows cc-sdlc conventions. Scaffold the complete agent file, validate conventions, wire up knowledge context, register, and quality-gate with the reviewer subagent.

**Argument:** `$ARGUMENTS` (what domain the agent owns)

## Reference

Read `.claude/agents/AGENT_TEMPLATE.md` before proceeding — it is the canonical structural pattern with full frontmatter reference.

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

**description:** Follow the exact format from AGENT_TEMPLATE.md line 3. Include realistic scenarios in example blocks.

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

Generate each section following AGENT_TEMPLATE.md structure:

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
Include the standard memory section from AGENT_TEMPLATE.md:
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
   This single entry covers all review skills (`sdlc-review-code`, `team-review-fix`)

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

Dispatch the `sdlc-reviewer` subagent on the created agent file. Present its findings. Fix any convention violations before finalizing.

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

## Integration

- **Feeds into:** The created agent becomes available for dispatch by orchestration skills
- **Modifies:** `[sdlc-root]/process/agent-selection.yaml` (tier1 reviewers + infrastructure_domains), `sdlc-plan` (agent table) — see Step 6
- **Uses:** `.claude/agents/AGENT_TEMPLATE.md` (structural reference), `[sdlc-root]/knowledge/agent-context-map.yaml` (knowledge wiring), `.claude/agents/AGENT_SUGGESTIONS.md` (reusable patterns), `sdlc-reviewer` (quality gate), existing agents (conflict checking)
- **Complements:** `sdlc-develop-skill` (skills vs agents), `sdlc-review` (review existing agents)
- **Does NOT replace:** Direct editing of existing agents (this creates new ones only)
