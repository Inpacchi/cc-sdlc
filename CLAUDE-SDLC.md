# CLAUDE-SDLC.md

This file is a **drop-in addition** for your project's `CLAUDE.md`. Copy the relevant sections into your existing CLAUDE.md — do not replace it.

---

## SDLC Process

This project follows a lightweight SDLC framework. Reference material lives in `ops/sdlc/`.

The SDLC defines what artifacts a deliverable requires; two skills define how CC produces them:
- `sdlc-plan` — spec + plan (domain agents write and review)
- `sdlc-execute` — implement + review + commit (domain agents execute and review)

### Roles
- **CD (Claude Director):** Human — sets direction, approves specs, makes product decisions
- **CC (Claude Code):** The entire agent system — specs, plans, implements, reviews via domain-agent-driven skills

### Deliverable Workflow
Idea → Spec (CD approves) → Plan (reviewed) → Execute → Review → Result → Chronicle

CC produces SDLC artifacts across two skills:
- **Spec** → `docs/current_work/specs/dNN_name_spec.md` (planning skill, CD must approve)
- **Plan** → `docs/current_work/planning/dNN_name_plan.md` (planning skill, agents review)
- **Result** → `docs/current_work/results/dNN_name_result.md` (execution skill, domain agents review)
- **Complete** → renamed to `dNN_name_COMPLETE.md`, archived to `docs/chronicle/`

### Deliverable Tracking
- **IDs:** Sequential: D1, D2, ... Dnn (never reused). Sub-deliverables use letter suffixes: D1a, D1b.
- **Assign an ID** when work is expected to touch more than one file or take more than 30 minutes.
- **Catalog:** `docs/_index.md`
- **Active work:** `docs/current_work/`
- **Archived work:** `docs/chronicle/`

### File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Spec | `dNN_name_spec.md` | `d1_auth_spec.md` |
| Plan | `dNN_name_plan.md` | `d1_auth_plan.md` |
| Result | `dNN_name_result.md` | `d1_auth_result.md` |
| Complete | `dNN_name_COMPLETE.md` | `d1_auth_COMPLETE.md` |
| Blocked | `dNN_name_BLOCKED.md` | `d1_auth_BLOCKED.md` |

### Three Tiers of Work

| Tier | When | What Happens |
|------|------|-------------|
| **Full SDLC** (`sdlc-plan` → `sdlc-execute`) | New features, architectural changes, new integrations, new subsystems | Deliverable ID, spec, plan, result doc, chronicle |
| **SDLC-Lite** (`sdlc-lite-plan` → `sdlc-lite-execute`) | Work complex enough to benefit from a reviewed plan up front, but doesn't warrant full tracking | Plan file, agent review, no deliverable tracking |
| **Direct dispatch** (no skill) | CD is steering in real-time — describing goals, testing results, giving feedback | Agents do the work, CC orchestrates, CD drives iteration |

**Choosing a tier:** The question is whether the work benefits from a **plan artifact that survives context clears**. If yes → SDLC or SDLC-Lite. If the user is actively steering and iterating in conversation → direct dispatch.

**Before touching any file:** If you identify non-trivial complexity (cross-domain, non-obvious approach, new subsystems), surface the scope and ask CD which tier to use. The user should never be in the position of catching a missed planning gate.

### Direct Dispatch Rules

Direct dispatch is not "no process" — it's process without a plan file. These rules apply whenever you're doing work without invoking a planning or execution skill:

**Agent-first, always.** Domain agents do the implementation and review work. You orchestrate. This is not optional just because there's no plan. If a domain agent exists for the work, dispatch them.

**State scope before dispatching.** Before your first agent dispatch, output a brief scope statement:
```
Scope: [what we're doing and why]
Agents: [who's doing the work]
```
This takes 10 seconds and prevents scope drift. It's not a plan — it's a one-time orientation.

**Pass full context to agents.** The dispatch prompt must include everything the agent needs: what to build/fix, which files are involved, relevant constraints, library versions (verify via Context7 when external APIs are involved), and any context from the user's feedback. Agents start fresh — they don't see the conversation.

**Iterate on CD feedback.** When the user tests and reports issues ("that didn't work", "why is this magenta?", screenshots), dispatch the relevant agent to fix — don't fix it yourself. Each round of feedback is a new dispatch with the user's observations as context.

**Review before committing.** When the user signals they're satisfied (or when you've completed a coherent unit of work), dispatch all relevant agents to review the full set of changes before committing. This is the same review-fix loop used in the execution skills — dispatch ALL relevant agents, collect findings, triage, fix, re-review until clean.

**Never self-implement.** The manager rule applies in direct dispatch exactly as it does in plan-based execution. "There's no plan so I'll just do it myself" is not valid. The absence of a plan changes what you produce (no artifact), not how you produce it (agents).

### When to Escalate to a Plan

If you're in direct dispatch and ANY of these become true, stop and ask CD about escalating to SDLC-Lite or full SDLC:

- The scope has grown beyond what was originally stated
- You're on your third dispatch round and the work isn't converging
- The changes would benefit from surviving a context clear (long-running, will continue next session)
- You're introducing new abstractions (components, hooks, stores, routes, types, events)

### Workflow Rules

**STOP and invoke `sdlc-plan` when ANY of the following is true:**

- The user asks to build a new feature, new integration, or new subsystem
- The work introduces new architectural patterns
- You are unsure whether something needs full tracking — default to asking, not implementing

**STOP and invoke `sdlc-lite-plan` when:**

- The work is complex enough to benefit from agent review of a plan before execution
- The work will likely span a context clear
- Multiple interacting changes where getting the approach wrong is costly

**Invoke `sdlc-execute` / `sdlc-lite-execute` only when:**
- An approved plan exists at the expected path
- The user explicitly says "execute the plan" or references a specific plan file

**When starting any session:** Check `docs/current_work/` for in-progress deliverables before accepting new work.

### The Failure Pattern (What Not To Do)

This is the exact sequence that bypasses process incorrectly:

1. User mentions improvements to a page or feature
2. Claude Code explores the codebase and reads relevant files
3. Claude Code identifies 4-6 files that need to change, new components needed, store interactions required
4. **Claude Code begins writing code itself instead of dispatching agents**
5. User has to interrupt: "should we make a plan?" or "use the agents"

Step 4 is wrong. After step 3, the correct action is to surface the scope assessment and ask which tier to use — or if the user is already steering, state scope and start dispatching agents.

### Compliance Auditing
Run `"Let's run an SDLC compliance audit"` periodically (~every 2-4 weeks or at each version bump). See `ops/sdlc/process/compliance_audit.md`.

### SDLC Commands

| Command | Action |
|---------|--------|
| "Let's catalog our ad hoc work" | Invokes the `sdlc-reconciliation` skill — reconciles untracked ad hoc commits back into the deliverable catalog |
| "Let's organize the chronicles" | Archive completed deliverables from `current_work/` to `chronicle/`. See `ops/sdlc/process/chronicle_organization.md` |
| "Let's run an SDLC compliance audit" | Audit spec coverage, chronicle freshness, index completeness. See `ops/sdlc/process/compliance_audit.md` |
| "Let's update the SDLC" | Propose process improvement. See `ops/sdlc/process/sdlc_changelog.md` |

### Key References
- `ops/sdlc/process/overview.md` — Full workflow
- `ops/sdlc/templates/` — Document templates (spec, plan, result, concept index)
- `docs/_index.md` — Deliverable catalog

---

## Verification Policy (Zero-Assumption Rule)

**Assumptions are forbidden.** Every claim about external behavior, API shape, library usage, or service configuration must be verified before acting on it. "I'm pretty sure" is not good enough — verify or disclose.

### External Libraries & Frameworks
- Before using any external library API, **verify it via Context7** (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`). Do not rely on training data for API signatures, parameter names, default behaviors, or version-specific features.
- Check the project's actual dependency version (package.json, lock files, etc.) before querying docs — version matters.
- If Context7 does not have docs for the library, say so and ask the user for a documentation source.

### Codebase Knowledge
- Before making claims about how this codebase works, **read the actual code**. Do not infer file structure, function signatures, or module behavior from naming conventions alone.
- When modifying code, always read the target file and its immediate dependencies first.

### External Services & APIs
- Do not assume endpoint shapes, authentication methods, rate limits, or response formats. Look up documentation via Context7 or web search, or ask the user.
- If an external API has changed between versions, verify the version in use before giving guidance.

### When You Don't Know
- **Say "I don't know" or "Let me verify that."** Do not fabricate an answer.
- If verification tools are unavailable or inconclusive, explicitly flag the uncertainty: "I wasn't able to verify this — here's my best understanding, but please confirm."
- Never present unverified information with confidence.

### Agent Dispatch Integration
When dispatching domain agents for phases that involve external library integration, include in the dispatch prompt:
1. The specific libraries involved and their versions (from the project's dependency files)
2. Instructions to use Context7 for API verification before writing integration code
3. A reminder that training-data knowledge of library APIs is not sufficient — live docs are required

---

## Use AskUserQuestion for All Questions

**Always use the `AskUserQuestion` tool when you need user input.** Do not type questions as conversational text. This includes:

- Design decisions and trade-offs
- Scope confirmation ("should we plan this, use SDLC-Lite, or direct dispatch?")
- Data accuracy questions ("should this be X or Y?")
- Clarification of ambiguous requirements
- Escalation when stuck (3-strike rule, blocked work)

**Why:** Conversational questions create pause points where the user has to type free-text responses like "do it", "yes", "continue", "go" to unblock execution. `AskUserQuestion` presents structured options, reduces friction, and makes the decision point explicit.

**Exception:** Status updates, findings tables, and informational output are not questions — those are plain text.

---

## Data Pipeline Integrity

**Data pipelines must never contain hallucinated or assumed values.** Every value in a seed script, scraper constant, allowlist, or configuration must be traceable to an official source — a rules document, an API response, an existing codebase constant, or a user decision.

**Required behavior:**
1. **Read from the defined source.** If the plan names an external source (GitHub repo, API, rules document), fetch from it. Do not infer, guess, or generate plausible-sounding values.
2. **Cross-reference codebase constants.** When the codebase already has values (e.g., adapter config, color maps), read those files and use the exact values — do not retype from memory.
3. **When a value cannot be sourced, use `AskUserQuestion`.** If no official source exists for a data point and it cannot be derived from the codebase, stop and ask the user. Do not fill the gap with a plausible guess.
4. **Coupled artifacts must read from each other.** When two files must agree (e.g., a consumer's allowlist must match a producer's canonical data), the later file must read the earlier file as its canonical reference — not independently derive the same values.

---

## Code Verification Rule

**Never assert how specific code behaves without reading it first.**

This applies to: flag names, function signatures, sync logic, config values, pipeline flow — anything implementation-specific.

The correct workflow is:

```
Read/Search → Reason → Assert
```

Not:

```
Assert (plausible) → Search to confirm → Correct when challenged
```

If you haven't read the relevant file, say so: *"Let me check"* — then check.

**Use LSP when available.** For type-system and call-graph questions, prefer LSP over Grep:
- `hover` for type signatures (don't read a file and infer the type)
- `goToDefinition` to navigate to source (don't Glob for the filename)
- `findReferences` for all callers (don't Grep for the function name — it misses renames and aliased imports)
- `goToImplementation` for interface implementations

Fall back to Grep for string literals, config keys, and non-code content (YAML, markdown). See `ops/sdlc/plugins/lsp-setup.md` for setup.

---

## Debugging Escalation Rule

If you have spent 3 or more rounds of read/search/grep investigating a bug without identifying the root cause, stop self-investigating and dispatch `debug-specialist` with your findings so far. Pass what you've ruled out, the open hypotheses, and the relevant file paths. Do not continue accumulating context yourself — that context belongs in the agent's dispatch prompt.

---

## Agent Conventions

- **Agent memories committed with code** — domain agent memory files (`.claude/agent-memory/`) are committed alongside the code changes they relate to. Update stale memories when fixes resolve documented issues.
- **Agent frontmatter: single-line descriptions only** — The `description` field in `.claude/agents/*.md` must be a single-line YAML string using `\n` for newlines. Multi-line quoted strings silently break Claude Code's frontmatter parser.

---

## Recommended Claude Code Settings

Add these to your project's `.claude/settings.json` (create if it doesn't exist):

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "mcp__context7__resolve-library-id",
      "mcp__context7__query-docs",
      "LSP"
    ]
  }
}
```

**What these do:**
- Pre-approve common git read operations so Claude Code can check status and history without prompting
- Pre-approve git staging and commit so the commit skill runs without interruption
- Pre-approve Context7 documentation lookups so verification happens without prompting (required by the Verification Policy)
- Pre-approve LSP operations so code intelligence happens without prompting (highly recommended — see `ops/sdlc/plugins/lsp-setup.md`)

**Optional additions** (tailor to your project's build tooling):

```json
{
  "permissions": {
    "allow": [
      "Bash(npm install)",
      "Bash(npm run build*)",
      "Bash(npm test*)",
      "Bash(npx playwright test*)"
    ]
  }
}
```

Adjust the build commands to match your package manager (`npm`, `pnpm`, `yarn`, `make`, etc.).

See [Claude Code settings documentation](https://docs.anthropic.com/en/docs/claude-code/settings) for the full settings reference.
