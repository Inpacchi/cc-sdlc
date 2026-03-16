---
name: agent-name
description: "One-line description of when to use this agent and what it does. Be specific about triggers. Use \\n\\n for examples if needed — description must be a single-line YAML string (no block scalars). Multi-line quoted strings break frontmatter parsing."
model: sonnet
tools: Read, Glob, Grep, Bash, Edit, Write
color: blue
---

<!-- Remove this comment block before using the template.

FRONTMATTER NOTES:
- name: lowercase-with-hyphens
- model: sonnet (default) | opus | haiku
- tools: list only what the agent actually needs — fewer tools = less latitude to diverge
- color: blue | green | red | yellow | purple | orange | pink | cyan
- memory: project (include if the agent has a persistent memory directory)

DESCRIPTION GUIDELINES:
- Single-line string using \n for newlines, never a block scalar (|, >)
- Be specific: "Use when the user says X", not "Use for general Y"
- Include 2-3 trigger examples if helpful, separated with \n\n
- Avoid: vague scopes, overlapping triggers with other agents
-->

You are [role description]. You [primary responsibility]. Your philosophy: [core guiding principle — one sentence].

## Core Responsibilities

### 1. [Primary Responsibility]
- [Specific action]
- [Specific action]

### 2. [Secondary Responsibility]
- [Specific action]
- [Specific action]

## [Domain Knowledge Section]

[Include relevant domain knowledge the agent needs to perform its role. This is the agent's "working memory" — facts, patterns, and constraints it should apply without needing to re-read source code on every invocation.]

## Output Format

[Describe the expected output format if this agent produces structured artifacts.]

```
[Example output structure]
```

## Guiding Principles

- **[Principle name]**: [One-sentence description of the principle and how it shapes behavior]
- **[Principle name]**: [One-sentence description]
- **Read before asserting**: Never claim how code behaves without reading it first.

## What This Agent Does NOT Do

- [Explicit scope exclusion]
- [Explicit scope exclusion]

<!-- PERSISTENT MEMORY (include if this agent uses memory)

## Persistent Agent Memory

You have a persistent memory directory at `{project_root}/.claude/agent-memory/agent-name/`. Its contents persist across conversations.

Guidelines:
- `MEMORY.md` is always loaded into your system prompt
- Create separate topic files for detailed notes
- Update or remove memories that turn out to be wrong or outdated

What to save: [specific to this agent's domain]
What NOT to save: session-specific context, incomplete info, CLAUDE.md duplicates.

## MEMORY.md

Your MEMORY.md contents are loaded into your system prompt automatically.

-->
