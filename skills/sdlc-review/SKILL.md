---
name: sdlc-review
description: >
  Review or analyze SDLC skills and agents. Two modes: review mode dispatches the sdlc-reviewer
  subagent to check a skill or agent file against cc-sdlc conventions. Analyze mode takes any
  external source (agent definitions, articles, docs, code patterns) and compares against
  existing cc-sdlc agents/skills to identify improvements or new candidates.
  Knowledge store candidates route to /sdlc-ingest.
  Triggers on "review this skill", "review this agent", "check skill quality", "check agent quality",
  "/sdlc-review", "analyze these", "incorporate from these", "compare against our agents",
  "what can we learn from this", "see if there's anything useful".
  Do NOT use for creating new skills or agents — use sdlc-develop-skill or sdlc-create-agent.
  Do NOT use for bulk knowledge import — use sdlc-ingest.
---

# SDLC Review

Review existing skills/agents for convention compliance, or analyze external sources for improvements to incorporate.

**Argument:** `$ARGUMENTS` (file path for review mode, or source description for analyze mode)

## Mode Resolution

Parse `$ARGUMENTS` to determine mode:

| Invocation | Mode |
|-----------|------|
| `/sdlc-review path/to/SKILL.md` | Review |
| `/sdlc-review path/to/agent.md` | Review |
| `/sdlc-review` (no args, skill/agent in recent context) | Review (infer target from conversation) |
| `/sdlc-review analyze <source>` | Analyze |
| "analyze these agent definitions" | Analyze |
| "what can we learn from this" | Analyze |

When ambiguous, ask the user.

## Review Mode

### Steps

#### 1. Resolve Target

Identify the skill or agent file to review. If a path is provided, use it. If not, check conversation context for a recently created or discussed file.

If no target can be identified:

> No review target found. Provide a file path: `/sdlc-review path/to/file.md`

#### 2. Dispatch Reviewer

Dispatch the `sdlc-reviewer` subagent with the target file path. The subagent detects the file type (skill vs agent), runs the appropriate checklist, and returns structured findings.

#### 3. Present Findings

Present the reviewer's findings directly. If critical or major issues exist, offer to fix them:

> **{N} findings** ({critical} critical, {major} major, {minor} minor)
>
> Want me to fix these issues?

For minor-only findings, present and move on — no fix offer unless the user requests it.

## Analyze Mode

### Steps

#### 1. Gather Source Material

Accept any external source relevant to a domain:
- **Pasted content** — agent definitions, skill files, articles, documentation
- **File paths** — local files to read
- **URLs** — fetch and read via WebFetch

Read the source material completely before proceeding.

#### 2. Map to Existing Agents/Skills

Read the existing cc-sdlc agents and skills:
- Scan `.claude/agents/` for agent files
- Scan `.claude/skills/` for skill directories
- Consult `[sdlc-root]/knowledge/agent-context-map.yaml` for knowledge wiring

For each concept in the source material, determine:
- Does an existing agent/skill already cover this domain?
- Does the source add value beyond what we already have?

#### 3. Categorize Findings

Sort findings into categories:

**Improvements to existing agents/skills:**
- New principles or workflow steps worth adding
- Anti-rationalization entries we're missing
- Review lenses or verification checks to incorporate
- Scope refinements or boundary clarifications

**New agent/skill candidates:**
- Domains the source covers that no existing agent/skill handles
- Only flag if the domain is relevant to the project

**Knowledge store / discipline candidates:**
- Patterns, methodologies, or domain knowledge worth codifying
- Route these to `/sdlc-ingest` — do NOT create knowledge files inline

#### 4. Present Analysis

```
ANALYZE REPORT
═══════════════════════════════════════

Source: [description of what was analyzed]

IMPROVEMENTS TO EXISTING
| # | Target | What to Add | Why |
|---|--------|-------------|-----|
| 1 | .claude/agents/{name}.md | [specific addition] | [rationale] |
| 2 | .claude/skills/{name}/SKILL.md | [specific addition] | [rationale] |

NEW CANDIDATES
| # | Proposed Name | Type | Domain | Rationale |
|---|--------------|------|--------|-----------|
| 1 | {name} | agent/skill | [domain] | [why it's needed] |

KNOWLEDGE CANDIDATES (route to /sdlc-ingest)
| # | Content | Target Store/Discipline |
|---|---------|----------------------|
| 1 | [pattern/methodology] | [where it should go] |
```

#### 5. Apply (on approval)

When the user approves specific improvements:
- **Existing agent/skill edits** — apply directly
- **New agents** — offer to invoke `/sdlc-create-agent`
- **New skills** — offer to invoke `/sdlc-develop-skill`
- **Knowledge candidates** — remind user to run `/sdlc-ingest` with the identified content

Update `[sdlc-root]/process/sdlc_changelog.md` for any process changes applied.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The source has a lot of good stuff, adopt everything" | Evaluate each finding against what already exists. Most external content overlaps with existing conventions. |
| "I'll create knowledge files directly during analyze" | Knowledge candidates route to `/sdlc-ingest`. That skill handles validation, placement, and tagging. |
| "The external agent definition is better than ours, replace it" | Compare specific elements, not wholesale. Our agents have project-specific context that generic definitions lack. |
| "Review mode found no issues, the skill is perfect" | A clean review means convention compliance, not quality. The skill might follow all conventions and still be poorly designed. |
| "I'll skip reading existing agents during analyze" | Without knowing what we already have, you can't identify what's new or improved. |
| "The source is from a trusted project, no need to validate" | Every suggestion gets evaluated against our conventions regardless of source. |

## Integration

- **Uses:** `sdlc-reviewer` subagent (review mode), WebFetch (analyze mode URLs), existing agents/skills (comparison baseline)
- **Feeds into:** Direct edits (improvements), `sdlc-create-agent` / `sdlc-develop-skill` (new candidates), `sdlc-ingest` (knowledge candidates)
- **Complements:** `sdlc-develop-skill` and `sdlc-create-agent` (creation triggers review; review can trigger creation)
- **Does NOT replace:** `sdlc-audit` (audits project-wide compliance; this reviews individual files and external sources)
