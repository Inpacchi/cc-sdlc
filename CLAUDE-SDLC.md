# CLAUDE-SDLC.md

This file is a **drop-in addition** for your project's `CLAUDE.md`. Copy the relevant sections into your existing CLAUDE.md — do not replace it.

---

## SDLC Process

This project follows a lightweight SDLC framework. Reference material lives in `ops/sdlc/`.

The SDLC defines what artifacts a deliverable requires; two skills define how CC produces them:
- `sdlc-planning` — spec + plan (domain agents write and review)
- `sdlc-execution` — implement + review + commit (domain agents execute and review)

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

### When to Use Full Process vs. Ad Hoc
- **Full process (deliverable ID + skill):** New features, architectural changes, new integrations, multi-package work
- **Ad hoc OK:** Bug fixes, UI tweaks, config changes, corrections (<30 min)
- **Before touching any file:** If your planned changes span more than one file, or introduce anything new (component, hook, store, route, type), stop. State the scope out loud and ask CD whether to track it.

### Workflow Rules

**STOP and invoke `sdlc-planning` when ANY of the following is true:**

- You have finished exploring the codebase and find yourself forming a plan to change more than one file
- The user asks to build, add, improve, or redesign any feature or page
- The work would touch multiple files, multiple packages, or introduce new components, hooks, stores, routes, types, or events
- You are about to spawn implementation agents
- You are unsure whether something is ad hoc or substantial — default to planning, not implementation

Note: these triggers fire on **your own intent to act**, not only on user keywords. If you explored code and concluded "I should implement X across files A, B, and C" — that is a planning trigger, regardless of what the user said.

**Invoke `sdlc-execution` only when:**
- An approved plan exists at `docs/current_work/planning/dNN_name_plan.md`
- The user explicitly says "execute the plan" or references a specific plan file

**You MUST use domain agents (not do the work yourself) when:**
- The task falls within a domain agent's expertise
- You are writing specs, plans, or reviewing code — dispatch the relevant agents
- The agent with domain expertise writes and reviews. You orchestrate.

**Ad hoc work (no skill invocation required):**
- Single-file bug fixes, config changes, dependency updates
- Work completable in under 30 minutes that does not introduce new abstractions

**When starting any session:** Check `docs/current_work/` for in-progress deliverables before accepting new work.

### The Failure Pattern (What Not To Do)

This is the exact sequence that bypasses SDLC tracking incorrectly:

1. User mentions improvements to a page or feature
2. Claude Code explores the codebase and reads relevant files
3. Claude Code identifies 4-6 files that need to change, new components needed, store interactions required
4. **Claude Code begins spawning implementation agents or writing code**
5. User has to interrupt: "should we make a plan?"

Step 4 is wrong. After step 3, the correct action is to surface the scope assessment and ask whether to plan or proceed ad hoc. The user should never be in the position of catching a missed planning gate.

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
      "Bash(git commit*)"
    ]
  }
}
```

**What these do:**
- Pre-approve common git read operations so Claude Code can check status and history without prompting
- Pre-approve git staging and commit so the commit skill runs without interruption

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
