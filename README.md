# cc-sdlc

A reusable Software Development Lifecycle (SDLC) framework for AI-assisted development projects using Claude Code.

## What This Is

cc-sdlc is a lightweight process framework for projects that use Claude Code (CC) as a primary development tool. It defines how work flows from idea to archive, how humans and AI agents collaborate, and how project knowledge is captured and reused across sessions.

The framework is designed to be adopted incrementally — start with the core process, add skills and agents as your workflow matures.

## What's Included

| Directory | Contents |
|-----------|----------|
| `process/` | Workflow documentation (overview, lifecycle, collaboration model, ad hoc reconciliation, compliance audit, chronicle organization) |
| `templates/` | Document templates for specs, plans, results, prompts, and audits |
| `examples/` | Filled-out examples of spec, plan, and result documents |
| `disciplines/` | Persistent "parking lots" for capturing cross-project insights by discipline |
| `knowledge/` | Structured YAML knowledge stores — patterns, methodologies, test strategies |
| `playbooks/` | Recipes for recurring task types (add your own as patterns emerge) |
| `skills/` | Claude Code skills for SDLC workflow automation |
| `agents/` | Agent definitions — `sdlc-compliance-auditor` + `AGENT_TEMPLATE.md` for adding your own |
| `skeleton/` | Directory structure manifest for bootstrapping new projects |
| `plugins/` | Plugin setup guides (context7 is required; oberskills, design-for-ai are optional) |
| `improvement-ideas/` | Design proposals for evolving the SDLC itself |

## Quick Start

### 1. Bootstrap a New Project

```bash
# Clone or copy cc-sdlc to your machine
git clone https://github.com/Inpacchi/cc-sdlc ~/src/ops/sdlc

# Or set it up as a pnpm/npm package — see skeleton/manifest.json
```

Open your project in Claude Code and say:

> "Let's implement the SDLC process from `~/src/ops/sdlc`"

CC will scan your existing documentation, propose a categorization, create the directory structure, and add the SDLC compliance section to your CLAUDE.md.

See `BOOTSTRAP.md` for the full CC initialization walkthrough.

### 2. Adopt the Skills

Copy the `skills/` directory into your project's `.claude/skills/` and the `agents/` directory into `.claude/agents/`. Add the `CLAUDE-SDLC.md` content to your project's `CLAUDE.md`.

### 3. Use the Process

Once bootstrapped, the core workflow is:

```
Idea → Spec (CD approves) → Plan (reviewed) → Execute → Review → Result → Chronicle
```

**SDLC commands you'll use regularly:**

| Trigger | What Happens |
|---------|-------------|
| "Let's build X" / "New feature" | Invokes `sdlc-plan` — spec + plan |
| "Execute the plan" | Invokes `sdlc-execute` — implement + review + result |
| "Let's catalog our ad hoc work" | Invokes `sdlc-reconciliation` — reconciles untracked commits |
| "Let's organize the chronicles" | Invokes `sdlc-archive` — moves completed work to archive |
| "Let's run an SDLC compliance audit" | Invokes `sdlc-compliance-auditor` agent |

## Core Concepts

### Deliverable IDs
Sequential identifiers (D1, D2, ... Dnn) that track work across the project lifetime. Never reused, even if work is abandoned.

### Current Work vs Chronicles
- `docs/current_work/` — Active deliverables
- `docs/chronicle/` — Completed work organized by concept (domain/feature area)

### Roles
- **CD (Claude Director):** The human — sets direction, approves specs, makes product decisions
- **CC (Claude Code):** The entire agent system — specs, plans, implements, reviews

### Three Tiers
Not everything needs a full spec → plan → result cycle. **SDLC-Lite** registers a deliverable ID (tier: lite) and produces a plan — no spec or result doc. **Direct dispatch** skips the plan entirely — CD steers in real-time, agents do the work. Reconcile untracked work periodically with `sdlc-reconciliation`.

## Knowledge Layer

The framework includes a three-tier knowledge layer:

```
Disciplines (parking lots) → Knowledge YAMLs (structured patterns) → Skills (automation)
```

- `disciplines/` — Persistent files for capturing insights per domain as they emerge
- `knowledge/` — Structured YAML patterns that skills load at runtime
- `skills/` — Automation that queries the knowledge layer before dispatching agents

This layer starts mostly empty and fills in as your project accumulates insights.

## Plugins

### Required
- **context7** — Live library/framework documentation lookups. Prevents stale API knowledge from training data. See `plugins/context7-setup.md`.

### Optional
- **oberskills** — Prompt engineering and web research utilities. See `plugins/oberskills-setup.md` for installation.
- **design-for-ai** — Design theory integration (`[PLUGIN: design-for-ai]`). Enriches `design-consult` skill with Design for Hackers principles. See `plugins/design-for-ai-setup.md`.

## Upstream

This framework is maintained at [github.com/Inpacchi/cc-sdlc](https://github.com/Inpacchi/cc-sdlc).

Knowledge YAMLs and discipline files were seeded from a cross-project reference implementation. They are intentionally generic — project-specific content belongs in your project's `docs/` and `CLAUDE.md`.
