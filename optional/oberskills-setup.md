# oberskills Plugin Setup

The `oberskills` plugin provides quality gates for agent dispatch, prompt engineering, and web research.

## What It Provides

| Skill | What It Does | Used By |
|-------|-------------|---------|
| `oberagent` | Validates agent prompts before dispatch. Enforces constraint budgets and prompt quality. | All skills that dispatch agents |
| `oberprompt` | Prompt engineering — fixes vague or flawed prompts. Auto-invoked by oberagent. | oberagent (auto) |
| `oberweb` | Multi-dimensional web research orchestrator. Runs parallel searches across different angles. | `design-consult`, `sdlc-planning` (research phase) |

## Installation

Install via Claude Code's plugin system. The plugin is available from the oberskills repository (check the upstream cc-sdlc README for the current installation method).

Once installed, the `[PLUGIN: oberagent]` and `[PLUGIN: oberweb]` markers in skills will activate.

## How oberagent Works

When a skill says:

```
[PLUGIN: oberagent] Before dispatching any agent, invoke oberagent first.
```

This means: before using the Task tool to dispatch a domain agent, invoke the `oberagent` skill. It will:

1. Review the dispatch prompt for quality issues (vague scope, missing context, unclear output format)
2. Apply the oberprompt quality gate to tighten the prompt
3. Return an improved prompt for use in the Task tool call

This prevents the failure mode where agents receive insufficiently-scoped prompts and produce unfocused or incorrect output.

## How oberweb Works

When a skill says:

```
[PLUGIN: oberweb] Invoke oberweb to research UI/UX patterns...
```

This means: invoke the `oberweb` skill with a research brief. It will:

1. Decompose the research question into parallel search angles
2. Dispatch sonnet agents to search and extract quality information
3. Synthesize findings into structured output

This provides richer research than a single web search.

## Degraded Mode (Without Plugin)

If oberskills is not installed:
- Skills will skip the `[PLUGIN: oberagent]` step and dispatch agents directly
- Skills will skip the `[PLUGIN: oberweb]` step and omit web research
- All other skill functionality remains intact

The quality of agent dispatch and research will be lower, but the workflow will complete.
