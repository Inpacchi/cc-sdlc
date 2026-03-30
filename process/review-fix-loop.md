# Review-Fix Loop

The core validation pattern that determines when work is done. Every execution skill references this file for the post-completion review cycle.

---

## Overview

After all implementation work completes, dispatch ALL relevant domain agents to review. Collect findings, classify them, fix them, and re-review until every agent reports clean. This loop is mandatory and has no shortcuts.

## Step A: Dispatch ALL Review Agents

Use the plan's agent assignment table (or the original review's agent list) as the starting set — do not re-evaluate relevance from scratch. Add agents if new domains surfaced during implementation; do not remove agents from the list. Dispatch **every single one** — not a subset.

**Review agents report findings only. They do NOT fix anything.** Fixes are dispatched in Step C after the manager classifies each finding. An agent that fixes inline during review has bypassed the triage gate — that is a process failure, not a shortcut.

Before dispatching, output this checklist:

```
Review round N — dispatching:
- [ ] agent-name-1
- [ ] agent-name-2
- [ ] agent-name-3
```

Every box must have a corresponding agent dispatch. If the number of dispatched agents doesn't match the checklist count, **stop and fix before proceeding**.

## Step B: Collect Findings

Wait for ALL agents to return. For each agent, record:
- Agent name
- Findings (or "no issues")

Output a findings table:

```
Review round N results:
| Agent | Findings | Severity |
|-------|----------|----------|
| agent-1 | specific finding | critical/major/minor |
| agent-2 | no issues | — |
```

**If any agent has findings → go to Step C.**
**If ALL agents report no issues → output "Review loop complete — all agents clean." and exit the loop.**

"Clean" means zero findings. Not "findings I consider pre-existing." Not "only minor suggestions." Zero.

## Step C: Triage + Fix

Classify each finding using the finding classification protocol per `process/finding-classification.md`.

Dispatch the most relevant domain agent to fix each FIX finding — this is often the agent who found it, but may be a different agent with deeper expertise in the affected file. If multiple findings need fixes, dispatch all of them before re-reviewing.

For anything that isn't a FIX, state what you don't know:
```
**Unknown**: [specific thing you haven't verified]
```

## Step D: Re-Review (Mandatory)

After ALL fixes from Step C are applied, **return to Step A**. Before dispatching, check whether any fixes introduced new domains not covered by the existing agent list. If yes, add the relevant agent(s) to the checklist for this round. Then dispatch ALL agents — not just the ones who found issues. Fixes can introduce new problems in other domains.

**This loop repeats until Step B shows ALL agents reporting no issues.** There is no shortcut. Do not claim the loop is closed without a clean round.

## 3-Strike Rule

If the same agent reports the same finding category in 3 consecutive review rounds — regardless of what was changed between rounds — stop iterating. Output:

1. The finding text
2. The agent dispatched to fix it
3. What each attempt returned
4. Your hypothesis for why attempts are failing

Then invoke `AskUserQuestion` to escalate to CD — do not type the escalation as conversational text. Save progress in a partial result doc if applicable.

## Skill-Specific Variations

| Skill | Agent Source | Notes |
|-------|------------|-------|
| `sdlc-execute` | Plan's agent assignment table | Full review with result doc output |
| `sdlc-lite-execute` | Plan's agent assignment table | Same loop, no result doc |
| `sdlc-review-fix` | Original `/sdlc-review-commit` agent list | Loop starts after initial fix dispatch |
