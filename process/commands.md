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
| "Let's catalog our ad hoc work" | Invokes `sdlc-reconcile` — reconciles untracked ad hoc commits back into the deliverable catalog |
| "Let's organize the chronicles" | Invokes `sdlc-archive` — archive completed deliverables from `current_work/` to `chronicle/` |
| "Let's update the SDLC" | Propose process improvement. See `[sdlc-root]/process/sdlc_changelog.md` |
| "Migrate my SDLC framework" | Invokes `sdlc-migrate` — apply cc-sdlc upstream updates while preserving project customizations |

## Status & Navigation

| Command | Action |
|---------|--------|
| `/sdlc-status` | Show active deliverables, blocked items, and recent archives |
| `/sdlc-resume` | Resume work on an active deliverable — loads context and suggests next action |
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
| `/sdlc-research-external` | Research external knowledge sources (blogs, talks, papers) and curate tiered reference docs |

## Skill & Agent Development

| Command | Action |
|---------|--------|
| `/sdlc-develop-skill` | Create or modify SDLC skills with convention enforcement, migration-aware wrapping, and quality gate |
| `/sdlc-create-agent` | Create a new domain agent with frontmatter validation and knowledge wiring |
| `/sdlc-review` | Review a skill/agent for convention compliance, or analyze external sources for improvements |
| `/sdlc-enrich-agent` | Extract patterns from external sources and integrate them into an existing agent definition |

## Code Review

| Command | Action |
|---------|--------|
| `/sdlc-review-code` | Review code with domain agents. No argument reviews uncommitted changes; a commit ref or range reviews that target. |
| `/sdlc-review-fix` | Review-fix loop — fixes the findings from the most recent `/sdlc-review-code` |
| `/sdlc-team-review-fix` | Unified team review + fix lifecycle with persistent teammates. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |

## Design (optional bundle)

Installed only when CD opts into the `design` bundle during `/sdlc-initialize`.

| Command | Action |
|---------|--------|
| `/sdlc-design-consult` | Consult domain design agents on UX, visual design, or interaction patterns |
| `/sdlc-design-brand-asset` | Generate specs for visual brand assets — dimensions, colors, positioning, AI image prompts |

## Cross-Platform

| Command | Action |
|---------|--------|
| `/sdlc-port-opencode` | Adapt existing cc-sdlc installation for OpenCode — creates `.opencode/` structure, `AGENTS.md`, adapted agents/skills, and `opencode.json` alongside the Claude Code setup |

## Testing

| Command | Action |
|---------|--------|
| `/sdlc-tests-create` | Generate test suites — domain experts identify gaps, SDET implements |
| `/sdlc-tests-run` | Automated test-fix loop — run tests, classify failures, dispatch agents to fix, repeat until green |
