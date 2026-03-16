# oberskills Plugin Setup

The `oberskills` plugin provides quality gates for agent dispatch, prompt engineering, and web research.

## What It Provides

| Skill | What It Does | Used By |
|-------|-------------|---------|
| `oberagent` | Validates agent prompts before dispatch. Selects correct `subagent_type` and model tier. Enforces constraint budgets and prompt quality. | **All SDLC skills** (mandatory) |
| `oberprompt` | Prompt engineering — fixes vague or flawed prompts. Auto-invoked by oberagent. | oberagent (auto) |
| `oberweb` | Multi-dimensional web research orchestrator. Runs parallel searches across different angles. | `design-consult`, `sdlc-planning` (research phase) |

## Installation

Install via Claude Code's plugin system. The plugin is available from the oberskills repository (check the upstream cc-sdlc README for the current installation method).

**oberagent is a required dependency for the SDLC workflow.** All SDLC skills invoke oberagent before every agent dispatch. Without it, agent dispatches may use incorrect `subagent_type` values (e.g., falling back to `general-purpose` instead of `frontend-developer`) and skip prompt quality validation.

## How oberagent Works

Every SDLC skill contains this instruction:

```
Before dispatching ANY agent, invoke the `oberagent` skill.
```

This means: before using the Agent tool to dispatch a domain agent, invoke the `oberagent` skill. It will:

1. Review the dispatch prompt for quality issues (vague scope, missing context, unclear output format)
2. Select the correct `subagent_type` — matching project-level agent names from `.claude/agents/`
3. Assign the appropriate model tier (haiku/sonnet/opus) based on task complexity
4. Apply the oberprompt quality gate to tighten the prompt
5. Return an improved prompt ready for the Agent tool call

This prevents two failure modes:
- **Wrong agent type**: Without oberagent, the model may not pass the correct `subagent_type` (e.g., `frontend-developer`) because it only sees built-in agent types in the Agent tool description
- **Poor prompts**: Insufficiently-scoped prompts produce unfocused or incorrect agent output

## How oberweb Works

When a skill says:

```
Invoke oberweb to research UI/UX patterns...
```

This means: invoke the `oberweb` skill with a research brief. It will:

1. Decompose the research question into parallel search angles
2. Dispatch sonnet agents to search and extract quality information
3. Synthesize findings into structured output

This provides richer research than a single web search.
