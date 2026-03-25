---
name: review-fix
description: >
  Fix all findings from the most recent /review-commit — dispatches worker domain agents to fix,
  then runs the review-fix loop until all agents report clean. Triggers on "fix review findings",
  "fix the review", "/review-fix", "address the findings", "fix all findings".
  Do NOT use without a prior /review-commit or /review-diff in this conversation.
---

# Fix Review Findings

Fix ALL findings from the most recent `/review-commit` — every critical, major, and minor issue. No filtering, no skipping by severity. Then run the review-fix loop (same as `sdlc-execute` step 2) until every agent reports clean.

## Precondition

A `/review-commit` must have been run in this conversation. If no review findings exist in the conversation context, stop:

> No review findings in this conversation. Run `/review-commit` first.

## Steps

### Manager Rule

Read and follow `ops/sdlc/process/manager-rule.md` — the canonical definition of this rule.

### 1. Load Findings

Read the review report from the current conversation. Extract each finding's description, file path, agent, severity, and category. Also extract the full list of relevant agents from the review (both those with findings and those without).

### Agent Dispatch Protocol

Dispatch prompts must describe WHAT/WHY — implementation HOW is the agent's domain. Every dispatch must include sufficient context for the agent to work autonomously.

### 2. Group by Agent and Dispatch Fixes

Group findings by the most relevant domain agent to fix them — this is often the agent who found the issue, but may be a different agent with deeper expertise in the affected file. **You do NOT fix findings yourself — you dispatch the relevant worker domain agent.**

Output the fix plan with a dispatch checklist:

```
Fixing {N} findings from review of {short-sha}:

Dispatching fixes:
- [ ] frontend-developer: 3 findings (1 major, 2 minor)
- [ ] code-reviewer: 2 findings (1 critical, 1 minor)
- [ ] performance-engineer: 1 finding (1 major)
```

**Every checkbox must have a corresponding agent dispatch.** Count the checkboxes. Count the dispatches. They must match. If you find yourself editing files directly instead of dispatching an agent, stop — that violates this command.

**Cross-domain knowledge injection:** When the fixing agent differs from the agent that found the issue, the fixer may lack context about the reviewer's domain. Consult `ops/sdlc/knowledge/agent-context-map.yaml` for the *finding* agent's entry and include relevant knowledge files in the *fixing* agent's dispatch prompt. For example, if `performance-engineer` found a re-render issue and `frontend-developer` is fixing it, include the performance engineer's knowledge files so the fixer understands the performance constraints.

Each agent receives:
- The specific findings assigned to them (description, file, line, category)
- The original diff for context
- Cross-domain knowledge files from the finding agent (when fixer ≠ finder)
- Instruction to make the minimal change that addresses each finding — no drive-by refactors, no scope expansion
- **Library verification instructions** (when the fix involves external library APIs): verify API usage via Context7 (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`) before writing the fix. Do not rely on training data for API signatures or behaviors.

Agents with no dependency between their fixes run in parallel.

After all agents complete, verify the project builds successfully (`[build command]` — see project CLAUDE.md) before proceeding to the review loop.

**If an agent returns without applying its fix** (fix not reflected in the file, agent reported an error, or the change is missing): re-dispatch that agent with the same instructions. Do NOT apply the fix yourself. The rule is re-dispatch, not self-fix.

### 3. Review-Fix Loop

Fixes can introduce new issues. Run the **Review-Fix Loop** per `ops/sdlc/process/review-fix-loop.md`. Agent source: the original `/review-commit` agent list. Classifications: FIX, INVESTIGATE, DECIDE, PRE-EXISTING per `ops/sdlc/process/finding-classification.md` (no PLAN — commit fixes are scoped to the current diff).

When the loop exits cleanly, go to step 4.

### 4. Worker Agent Reviews

This step is only reached when 3b shows ALL agents reporting no issues.

Present the summary:

```markdown
## Fix Summary

{N} original findings fixed | {M} review rounds | Build: passing

## Worker Agent Reviews

Key feedback incorporated:

- [agent-name] specific, concrete feedback that was incorporated
- [agent-name] another specific feedback point with actionable detail
```

**Rules:**
- Bracket the agent's exact name: `[frontend-developer]`, `[software-architect]`, etc.
- Each bullet is specific and concrete — not generic praise
- Include feedback from both the initial fixes and the review loop
- Omit agents that found no issues across all rounds

### 5. Offer Commit

> All fixes applied, review loop clean, build passes. Want me to commit these changes?

Do NOT commit automatically — wait for the user to confirm.

## Integration
- **Depends on:** `review-commit` or `review-diff` (must run first to produce findings)
- **Sibling:** `sdlc-lite-execute` (similar review-fix loop pattern)
