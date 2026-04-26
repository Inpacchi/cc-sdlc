# cc-sdlc

A reusable Software Development Lifecycle (SDLC) framework for AI-assisted development projects using Claude Code.

## What This Is

cc-sdlc is a lightweight process framework for projects that use Claude Code (CC) as a primary development tool. It defines how work flows from idea to archive, how humans and AI agents collaborate, and how project knowledge is captured and reused across sessions.

The framework is designed to be adopted incrementally — start with the core process, add skills and agents as your workflow matures.

## What's Included

| Directory      | Contents                                                                                                                           |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `process/`     | Workflow documentation (overview, lifecycle, collaboration model, ad hoc reconciliation, compliance audit, chronicle organization) |
| `templates/`   | Document templates for specs, plans, results, prompts, and audits                                                                  |
| `examples/`    | Filled-out examples of spec, plan, and result documents                                                                            |
| `disciplines/` | Persistent "parking lots" for capturing cross-project insights by discipline                                                       |
| `knowledge/`   | Structured YAML knowledge stores — patterns, methodologies, test strategies                                                        |
| `playbooks/`   | Recipes for recurring task types (add your own as patterns emerge)                                                                 |
| `skills/`      | Claude Code skills for SDLC workflow automation                                                                                    |
| `agents/`      | Agent definitions — `AGENT_SUGGESTIONS.md` catalog and framework subagents                                                          |
| `skeleton/`    | Directory structure manifest for project initialization                                                                            |
| `plugins/`     | Plugin setup guides (context7 required, LSP recommended)                                                                           |

## Quick Start

### 1. Initialize a Project

```bash
# One command — downloads the bootstrap file
curl -fsSL https://raw.githubusercontent.com/Inpacchi/cc-sdlc/master/BOOTSTRAP.md -o .claude/BOOTSTRAP.md
```

Open your project in Claude Code and say:

> "Bootstrap SDLC"

That's it. Claude Code reads the bootstrap file, clones the framework, installs everything, and walks you through setup.

The `sdlc-initialize` skill auto-detects whether this is a greenfield project or a retrofit (existing code/docs), then handles: file installation, CLAUDE.md authoring, agent creation, knowledge wiring, and verification.

### 2. Use the Process

Once initialized, the core workflow is:

```
Idea → Spec (CD approves) → Plan (reviewed) → Execute → Review → Result → Chronicle
```

**SDLC commands you'll use regularly:**

| Trigger                             | What Happens                                                                      |
| ----------------------------------- | --------------------------------------------------------------------------------- |
| "Let's build X" / "New feature"     | Invokes `sdlc-plan` — spec + plan                                                 |
| "Execute the plan"                  | Invokes `sdlc-execute` — implement + review + result                              |
| "Let's catalog our ad hoc work"     | Invokes `sdlc-reconcile` — reconciles untracked commits                           |
| "Let's organize the chronicles"     | Invokes `sdlc-archive` — moves completed work to archive                          |
| `/sdlc-audit`                       | Compliance audit — deliverable integrity, knowledge health, migration correctness |
| `/sdlc-audit improve <session>`     | Improvement audit — analyze sessions/commits for process improvements             |
| "Make a playbook from that session" | Invokes `sdlc-playbook-generate` — session-to-playbook extraction                 |

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
Not everything needs a full spec → plan → result cycle. **SDLC-Lite** registers a deliverable ID (tier: lite) and produces a plan and result doc — no spec. **Direct dispatch** skips the plan entirely — CD steers in real-time, agents do the work. Reconcile untracked work periodically with `sdlc-reconcile`.

## Knowledge Layer

The framework includes a two-tier knowledge layer:

```
Disciplines (parking lots + triage markers) → Knowledge YAMLs / Skills (structured patterns + automation)
```

- `disciplines/` — Persistent files for capturing insights per domain as they emerge. Entries are triaged with markers (`[READY TO PROMOTE]`, `[NEEDS VALIDATION]`, `[DEFERRED]`) and promoted directly to knowledge or skills when validated.
- `knowledge/` — Structured YAML patterns that agents load at runtime via `agent-context-map.yaml`
- `skills/` — Automation that queries the knowledge layer before dispatching agents

This layer starts mostly empty and fills in as your project accumulates insights. Planning and execution skills prompt for discipline capture at natural checkpoints.

## Plugins

### Required
- **context7** — Live library/framework documentation lookups. Prevents stale API knowledge from training data. See `plugins/context7-setup.md`.

## Upstream

This framework is maintained at [github.com/Inpacchi/cc-sdlc](https://github.com/Inpacchi/cc-sdlc).

Knowledge YAMLs and discipline files were seeded from a cross-project reference implementation. They are intentionally generic — project-specific content belongs in your project's `docs/` and `CLAUDE.md`.
