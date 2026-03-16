---
name: commit-fix
description: >
  Fix all findings from the most recent /commit-review — dispatches worker domain agents to fix,
  then runs the review-fix loop until all agents report clean. Triggers on "fix review findings",
  "fix the review", "/commit-fix", "address the findings", "fix all findings".
  Do NOT use without a prior /commit-review or /ad-hoc-review in this conversation.
---

# Fix Review Findings

Fix ALL findings from the most recent `/commit-review` — every critical, major, and minor issue. No filtering, no skipping by severity. Then run the review-fix loop (same as `sdlc-execution` step 2) until every agent reports clean.

## Precondition

A `/commit-review` must have been run in this conversation. If no review findings exist in the conversation context, stop:

> No review findings in this conversation. Run `/commit-review` first.

## Steps

### Manager Rule

**The manager (you) never edits code files.** This applies unconditionally: before dispatching agents, while waiting for agents, after receiving agent results, during triage, and during the review loop. There is no phase of this command in which it is correct for you to open a file and make a change. If you notice a problem — before dispatch, mid-loop, anywhere — the correct action is to dispatch the relevant agent. Noticing a problem yourself does not authorize you to fix it yourself.

### 1. Load Findings

Read the review report from the current conversation. Extract each finding's description, file path, agent, severity, and category. Also extract the full list of relevant agents from the review (both those with findings and those without).

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

Agents with no dependency between their fixes run in parallel.

After all agents complete, verify the project builds successfully (`[build command]` — see project CLAUDE.md) before proceeding to the review loop.

**If an agent returns without applying its fix** (fix not reflected in the file, agent reported an error, or the change is missing): re-dispatch that agent with the same instructions. Do NOT apply the fix yourself. The rule is re-dispatch, not self-fix.

### 3. Review-Fix Loop

Fixes can introduce new issues. Run the same review-fix loop defined in `sdlc-execution` (steps 2a-2d):

#### 3a. Dispatch ALL Review Agents

Re-dispatch ALL relevant agents from the original review — not just those who had findings.

**Review agents report findings only. They do NOT fix anything.** Fixes are dispatched in step 3c after the manager classifies each finding. An agent that fixes inline during review has bypassed the triage gate — that is a process failure, not a shortcut.

Output a checklist before dispatching:

```
Review round N — dispatching:
- [ ] code-reviewer
- [ ] frontend-developer
- [ ] performance-engineer
```

Every box must have a corresponding agent dispatch.

#### 3b. Collect Findings

Wait for all agents to return. Output a findings table:

```
Review round N results:
| Agent | Findings | Severity |
|-------|----------|----------|
| agent-1 | specific finding | critical/major/minor |
| agent-2 | no issues | — |
```

**All agents clean -> go to step 4.**
**Any findings -> go to 3c.**

"Clean" means zero findings. Not "findings I consider pre-existing." Not "only minor suggestions." Zero.

#### 3c. Triage + Fix

For each finding, classify individually in a table before acting — no narrative paragraphs, no blanket dismissals:

```
| # | Finding | Agent | Classification | Rationale |
|---|---------|-------|---------------|-----------|
| 1 | specific finding | agent-name | FIX / INVESTIGATE / DECIDE / PRE-EXISTING | why |
| 2 | ... | ... | ... | ... |
```

| Classification | When | Action |
|---------------|------|--------|
| **FIX** | Confident in diagnosis and fix | Dispatch the most relevant domain agent to fix it |
| **INVESTIGATE** | Need more info | Dispatch relevant agent to diagnose |
| **DECIDE** | Trade-off or business decision | Invoke the `AskUserQuestion` tool with the finding description and options. Do not type the question as conversational text. Block until the user answers. |
| **PRE-EXISTING** | Finding exists in code the fixes did not touch | No action — but must cite the file and explain why it's out of scope |

**These are the only valid classifications. Do not invent new ones (STALE, DUPLICATE, INTENTIONAL, or any other). If a finding does not fit one of the four above, classify it as DECIDE and present it to the user.**

**PRE-EXISTING rules:** A finding qualifies as pre-existing ONLY if the fix diff did not modify the code in question. If the fix moved, hoisted, or refactored the code — even without changing its logic — it is in scope and must be classified as FIX, INVESTIGATE, or DECIDE.

After classification, output a dispatch checklist before taking any action:

```
Round N triage — dispatching:
- [ ] agent-name: finding description (FIX)
- [ ] agent-name: finding description (FIX)
```

**Every FIX row in the table must have a corresponding checkbox. Count the FIX rows. Count the checkboxes. They must match. If you find yourself editing files directly instead of dispatching an agent, stop — that violates this command.**

**The size of a fix is not a valid reason to self-fix.** "This is a small change" or "this is targeted" is not an exception. A one-line fix still gets dispatched to the relevant domain agent. There are no small-fix exceptions.

Then: dispatch agents for all FIX findings, present DECIDE findings to user, re-review. PRE-EXISTING findings do not block the loop from completing.

#### 3d. Re-Review (Mandatory)

After fixes, return to 3a and dispatch ALL agents again — not just the ones who found issues. Fixes can introduce new problems in other domains.

**3-strike rule:** Same finding category 3 times in a row — stop iterating. Document what was tried and flag to the user.

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
- **Depends on:** `commit-review` or `ad-hoc-review` (must run first to produce findings)
- **Sibling:** `ad-hoc-execution` (similar review-fix loop pattern)
