# oberskills Plugin Setup

The `oberskills` plugin provides prompt engineering and web research utilities.

## What It Provides

| Skill | What It Does | Used By |
|-------|-------------|---------|
| `oberprompt` | Prompt engineering — fixes vague or flawed prompts. | Ad hoc prompt improvement |
| `oberweb` | Multi-dimensional web research orchestrator. Runs parallel searches across different angles. | `design-consult`, `sdlc-plan` (research phase) |

## Installation

Install via Claude Code's plugin system. The plugin is available from the oberskills repository (check the upstream cc-sdlc README for the current installation method).

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
