# SDLC Commands Reference

Quick reference for all SDLC skills and commands. Slash commands (`/sdlc-*`) are auto-discoverable — type `/` in Claude Code to see available skills. Natural-language triggers require knowing the phrase.

## Core SDLC Workflow

The standard deliverable lifecycle: **ideation → plan → execute**. Most work flows through these skills.

| Command | Action |
|---------|--------|
| `/sdlc-idea` or "I have an idea" | Invokes `sdlc-idea` — open-ended exploration for seeds that aren't ready to plan yet; produces an idea brief |
| "Let's build X" / "Plan deliverable DNN" | Invokes `sdlc-plan` — full planning lifecycle (spec + plan with domain-agent review) for non-trivial work |
| "Execute the plan at ..." | Invokes `sdlc-execute` — executes an approved plan; worker agents implement, review, and fix |
| "Quick plan for X" / small tweak | Invokes `sdlc-lite-plan` — lightweight plan for same-session 1–3 file changes |
| "Execute the lite plan" | Invokes `sdlc-lite-execute` — executes a lite plan with the same review-fix loop |

## Lifecycle Commands

| Command | Action |
|---------|--------|
| "Initialize SDLC in this project" | Invokes `sdlc-initialize` — detects greenfield vs retrofit, walks through full framework setup |
| "Let's organize the chronicles" | Invokes `sdlc-archive` — archive completed deliverables from `current_work/` to `chronicle/`, reconciles untracked ad hoc work first |
| "Let's update the SDLC" | Propose process improvement. See `[sdlc-root]/process/sdlc_changelog.md` |
| "Migrate my SDLC framework" | Invokes `sdlc-migrate` — apply cc-sdlc upstream updates while preserving project customizations |

## Status & Navigation

| Command | Action |
|---------|--------|
| `/sdlc-status` | Show active deliverables, blocked items, and recent archives |
| `/sdlc-handoff` or "create a handoff" | Invokes `sdlc-handoff` — capture the current session as a self-contained handoff doc at `docs/current_work/ideas/{slug}_handoff.md` for another session to pick up via `sdlc-idea`, `sdlc-lite-plan`, `sdlc-plan`, or `sdlc-debug-incident` |
| `/sdlc-reflect` or "capture learnings" | Invokes `sdlc-reflect` — surface session learnings into discipline parking lots after direct-dispatch or ad-hoc work sessions |

## Auditing

| Command | Action |
|---------|--------|
| `/sdlc-audit` | Compliance audit — deliverable integrity, knowledge layer health, migration correctness |
| `/sdlc-audit improve` | Improvement audit — analyze current session or past session/commits for process gaps |

## Incidents & Reference Docs

| Command | Action |
|---------|--------|
| `/sdlc-debug-incident` | Two-phase incident workflow — TRIAGE during active response, CLOSEOUT to postmortem after remediation. Auto-detects mode from incident doc state. |
| `/sdlc-create-reference-doc` | Create an internal developer-facing reference doc (event schemas, API surfaces, pipeline stage inventories). Author + review quorum + code-reviewer through review-fix loop. Writes to `docs/reference/{category}/`. |

## Knowledge & Content

| Command | Action |
|---------|--------|
| "Ingest these transcripts/articles" | Invokes `sdlc-ingest` — bulk-import external knowledge into disciplines and knowledge stores |
| "Make a playbook from this" | Invokes `sdlc-playbook-generate` — generate a structured playbook from the current session context or a past session's conversation and commits |
| `/sdlc-research` | Research external knowledge sources (blogs, talks, papers) and curate tiered reference docs |

## Skill & Agent Development

| Command | Action |
|---------|--------|
| `/sdlc-develop-skill` | Create or modify SDLC skills with convention enforcement, migration-aware wrapping, and quality gate |
| `/sdlc-develop-agent` | Create a new domain agent with frontmatter validation and knowledge wiring |
| `/sdlc-develop-agent enrich <agent> <sources>` | Extract patterns from external sources and integrate them into an existing agent definition |

## Code Review

| Command | Action |
|---------|--------|
| `/sdlc-review-code` | Review code with domain agents. No argument reviews uncommitted changes; a commit ref or range reviews that target. |

## Design (optional bundle)

Installed only when CD opts into the `design` bundle during `/sdlc-initialize`.

| Command | Action |
|---------|--------|
| `/sdlc-design-consult` | Consult domain design agents on UX, visual design, or interaction patterns |

## Cross-Platform

| Command | Action |
|---------|--------|
| `/sdlc-port-opencode` | Adapt existing cc-sdlc installation for OpenCode — creates `.opencode/agents/`, `AGENTS.md`, and `opencode.json` (incl. local model endpoint) alongside the Claude Code setup; skills and `[sdlc-root]` content are shared, not copied (OpenCode reads `.claude/skills/` directly) |

## Rendering

| Command | Action |
|---------|--------|
| `/sdlc-render` | Render a markdown deliverable as a self-contained HTML file. Interactive scoping for audience (multi-select), purpose, and emphasis. Offered (opt-in) after skills write deliverables — CD chooses whether to render. |

## Testing

| Command | Action |
|---------|--------|
| `/sdlc-tests-create` | Generate test suites — domain experts identify gaps, SDET implements |
| `/sdlc-tests-run` | Automated test-fix loop — run tests, classify failures, dispatch agents to fix, repeat until green |
