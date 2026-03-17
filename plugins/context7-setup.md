# Context7 MCP Setup

The `context7` MCP server provides up-to-date library and framework documentation lookups via the Context7 API.

## What It Provides

| Tool | What It Does | Used By |
|------|-------------|---------|
| `mcp__context7__resolve-library-id` | Resolves a library name to a Context7 library ID | All skills that touch external dependencies |
| `mcp__context7__query-docs` | Queries library documentation by resolved ID | All skills that touch external dependencies |

## Why It's Required

Claude's training data goes stale. API signatures change, parameters get renamed, defaults shift between versions. Without live documentation lookup, Claude will confidently use outdated or incorrect library APIs — and the code will look plausible but break at runtime.

Context7 closes this gap by providing real-time documentation for the libraries your project actually uses. Every SDLC skill that dispatches agents to write or review code must have access to accurate library documentation.

## Installation

### Option 1: Claude Code Plugin (Recommended)

Install via Claude Code's plugin system:

```
/install-plugin context7@claude-plugins-official
```

This installs Context7 as a managed plugin with automatic updates.

### Option 2: Project-Level MCP Configuration

Add to your project's `.mcp.json`:

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```

### Option 3: Global MCP Configuration

Add to `~/.claude/mcp.json` to enable Context7 across all projects:

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```

## Verification

After installation, verify the tools are available by asking Claude Code:

```
What MCP tools do you have access to?
```

You should see `mcp__context7__resolve-library-id` and `mcp__context7__query-docs` in the list.

## How It's Used in the SDLC

The CLAUDE-SDLC.md file includes a **Verification Policy** that requires:

1. Before using any external library API → resolve via Context7, then query docs
2. Before asserting version-specific behavior → check the version in use, then query Context7 for that version's docs
3. If Context7 doesn't have docs for a library → disclose the gap and ask the user for a documentation source

This policy applies to all domain agents dispatched by SDLC skills. Agent dispatch prompts should include verification instructions when the phase involves external library integration.
