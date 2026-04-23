# CLAUDE-SDLC.md

This file is a **drop-in addition** for your project's `CLAUDE.md`. Copy the relevant sections into your existing CLAUDE.md — do not replace it.

---

## SDLC Process

This project follows a lightweight SDLC framework. Reference material lives in the SDLC directory (`ops/sdlc/` by default, or `.claude/sdlc/` for projects using Neuroloom integration).

The SDLC defines what artifacts a deliverable requires; two skills define how CC produces them:
- `sdlc-plan` — spec + plan (domain agents write and review)
- `sdlc-execute` — implement + review + commit (domain agents execute and review)

### Roles
- **CD (Claude Director):** Human — sets direction, approves specs, makes product decisions
- **CC (Claude Code):** The entire agent system — specs, plans, implements, reviews via domain-agent-driven skills

### Deliverable Workflow
Idea → (optional: `sdlc-idea` for exploration) → Spec (CD approves) → Plan (reviewed) → Execute → Review → Result → Chronicle

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

### Three Tiers of Work

| Tier | When | What Happens |
|------|------|-------------|
| **Idea Exploration** (`sdlc-idea`) | The user has a thought or direction but isn't ready to commit to requirements | Idea brief (optional), saved to `docs/current_work/ideas/` |
| **Full SDLC** (`sdlc-plan` → `sdlc-execute`) | New features, architectural changes, new integrations, new subsystems | Deliverable ID, spec, plan, result doc, chronicle |
| **SDLC-Lite** (`sdlc-lite-plan` → `sdlc-lite-execute`) | Work complex enough to benefit from a reviewed plan up front, but doesn't need a spec | Deliverable ID (tier: lite), plan file, result doc, agent review, catalog entry |
| **Direct dispatch** (no skill) | CD is steering in real-time — describing goals, testing results, giving feedback | Agents do the work, CC orchestrates, CD drives iteration |

**Choosing a tier:** If the user isn't sure what they want yet → `sdlc-idea`. If the work benefits from a **plan artifact that survives context clears** → SDLC or SDLC-Lite. If the user is actively steering and iterating in conversation → direct dispatch.

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

**STOP and invoke `sdlc-idea` when:**

- The user has a vague idea, question, or direction they want to explore ("what if we...", "I'm thinking about...", "could we...")
- The user describes a problem without proposing a solution and wants to think it through
- Multiple viable approaches exist and the user hasn't chosen — exploration before commitment

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

### Process Changelog
When you make changes to SDLC process files (skills, agents, process docs, CLAUDE-SDLC.md, disciplines, knowledge), update the process changelog (`[sdlc-root]/process/sdlc_changelog.md`) **immediately after the change, in the same step**. Do not defer changelog updates to a later step, a separate commit, or a future session. Every process decision change — new rules, classification changes, workflow adjustments, guard additions — must have a changelog entry written before moving on to other work. The changelog captures *why* process changes were made — context that git log alone doesn't preserve. Don't backdate entries for changes made in prior sessions.

### Key References
- `[sdlc-root]/process/overview.md` — Full workflow
- `[sdlc-root]/process/commands.md` — All SDLC commands and skills
- `[sdlc-root]/templates/` — Document templates (spec, plan, result, concept index)
- `docs/_index.md` — Deliverable catalog

> **Note:** `[sdlc-root]` is `ops/sdlc/` by default, or `.claude/sdlc/` for projects using Neuroloom integration. The actual path is recorded in `.sdlc-manifest.json` under `sdlc_root`.

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

| Task | Use | Not |
|------|-----|-----|
| Find where a symbol is defined | LSP `goToDefinition` | Grep for the name |
| Find all call sites of a function | LSP `findReferences` | Grep for the name (misses renames and aliased imports) |
| Get the type signature of a function/variable | LSP `hover` | Read the file and infer |
| Find implementations of an interface method | LSP `goToImplementation` | Grep for method name |
| Trace what a function calls / who calls it | LSP `outgoingCalls` / `incomingCalls` | Manually following imports |
| List all symbols in a file | LSP `documentSymbol` | Reading the entire file |
| Search for a string literal or comment | Grep | LSP |
| Search non-code files (JSON, YAML, md) | Grep | LSP |
| Find a file by name pattern | Glob | LSP |

**If LSP returns an error or empty result:** Fall back to Grep + Read. Do not retry LSP in a loop.

See `[sdlc-root]/plugins/lsp-setup.md` for setup.

---

## Debugging Escalation Rule

If you have spent 3 or more rounds of read/search/grep investigating a bug without identifying the root cause, stop self-investigating and dispatch `debug-specialist` with your findings so far. Pass what you've ruled out, the open hypotheses, and the relevant file paths. Do not continue accumulating context yourself — that context belongs in the agent's dispatch prompt.

---

## Agent Conventions

- **Agent memories are not git-tracked** — `.claude/agent-memory/` is a private scratchpad for per-agent session continuity. Reusable learnings should flow through `knowledge_feedback` in agent handoffs → discipline capture → knowledge stores. See the "Surfacing Learnings to the SDLC" section in the agent template.
- **Agent frontmatter: single-line descriptions only** — The `description` field in `.claude/agents/*.md` must be a double-quoted single-line YAML string using `\\n` (double-backslash n) for newlines. A single `\n` in YAML double-quoted strings is interpreted as a real newline character and silently breaks Claude Code's frontmatter parser.

## Commit Completeness Rule

Every commit must include **all** artifacts produced during the work — not just application code. Before staging, scan for modifications in all of these categories:

| Category | Paths | When present |
|----------|-------|--------------|
| Application code & tests | Project-specific | Always |
| Discipline parking lot entries | `[sdlc-root]/disciplines/*.md` | When discipline capture adds entries |
| Knowledge store updates | `[sdlc-root]/knowledge/*.md` | When domain knowledge is added or corrected |
| SDLC process changelog | `[sdlc-root]/process/sdlc_changelog.md` | When process files change |
| Result docs & catalog | `docs/current_work/results/`, `docs/_index.md` | During full SDLC execution |

**Never split SDLC documentation into a separate follow-up commit.** The documentation is part of the work, not a chore after the work. If `git status` shows unstaged SDLC files after staging application code, something was missed.

---

## Commit Message Format

**Subject line:** Keep under ~72 characters. Use the conventional-commits prefix style: `feat(scope): ...`, `fix(scope): ...`, `chore(scope): ...`, `docs(scope): ...`, `refactor(scope): ...`. Scope is the package or domain (`api`, `web`, `auth`, `sdlc`, etc.). Imperative mood — "add feature" not "added feature."

**Body wrapping:** Do **not** hard-wrap body text at 72 characters. Write natural sentences and let the viewer reflow. One blank line between paragraphs. The 50/72 convention existed for 80-column terminals and mailing-list patch workflows; neither governs how this repo's commits are read. Hard-wraps in the middle of a clause create awkward breakpoints in GitHub's commit view (where most reading happens) and don't help `git log` more than natural breaks would.

**Intentional line breaks are fine** when they serve meaning — bullet lists, grouped clauses, or separating a trailing footer like `Co-Authored-By:`. What's out is mechanical wrapping at column 72.

**Structure:** Subject line, blank line, paragraph-form body explaining the *why*. Bullet lists only when the content is genuinely enumerable (a list of behaviors, a list of affected files) — not as a default format. Close with any `Co-Authored-By:` trailer on its own line.

