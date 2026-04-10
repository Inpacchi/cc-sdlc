---
name: sdlc-review-commit
description: >
  Review a commit with domain agents — checks for overengineering, unnecessary code, DRY violations,
  and architecture adherence. Triggers on "review this commit", "check commit", "review HEAD",
  "/sdlc-review-commit", "review the last commit", "code review".
  Do NOT use for uncommitted changes — use sdlc-review-diff for that.
---

# Review Commit

Review a commit (or range) with relevant domain agents. The review prioritizes catching overengineered solutions and unnecessary code alongside standard quality checks.

**Argument:** `$ARGUMENTS` (commit ref, default: HEAD)

## Steps

### 1. Resolve the Commit

Use the argument as the commit ref. If no argument is provided, default to `HEAD`.

Run `git show --stat {ref}` to get the list of changed files and a summary. Then run `git show {ref}` to get the full diff.

If the ref is invalid, tell the user and stop.

### 2. Identify Relevant Domain Agents

Follow the agent selection process in `ops/sdlc/process/review-agent-selection.md`. That document defines:
- Tier 1 (implementation reviewers) — always dispatch if files match
- Tier 2 (structural reviewers) — dispatch only when the diff warrants it
- The 4-step selection process

### 3. Dispatch Review Agents

Output a checklist before dispatching:

```
Reviewing commit {short-sha}: {commit subject}
Files changed: N

Dispatching reviewers:
- [ ] code-reviewer (always)
- [ ] frontend-developer (touches frontend components)
- [ ] performance-engineer (new store selectors)

Not dispatching:
- software-architect — follows existing pattern, no new abstractions
- ui-ux-designer — logic-only changes, no visual modifications
```

Dispatch ALL listed agents in parallel. Each agent receives the full diff and is asked to review using the lenses defined in `ops/sdlc/process/review-agent-selection.md` § Review Lenses (overengineering, type safety, security, contract safety, standard). Each agent reviews through their domain expertise but applies all applicable lenses.

### 4. Collect and Present Findings

Collect all findings. Present them in a single structured report:

```markdown
## Commit Review: {short-sha}

**{commit subject}**
{N} files changed | Reviewed by {N} domain agents

### Findings

| # | Finding | Agent | Severity | Category |
|---|---------|-------|----------|----------|
| 1 | specific finding | agent-name | critical/major/minor | overengineering/type-safety/security/contract/DRY/architecture/correctness |
| 2 | ... | ... | ... | ... |

### Overengineering Summary

[If any overengineering or unnecessary code was found, summarize the pattern here — e.g., "3 helper functions wrap single operations", "error handling added for impossible states". If none found, say "No overengineering detected."]

### Details

#### Finding 1: [title]
**Agent:** [agent-name] | **Severity:** [level] | **Category:** [category]
**File:** [path:line]
[Concrete description of the issue and what should change]
```

### 5. Next Steps

After presenting the report:

> **{N} findings** ({critical} critical, {major} major, {minor} minor)
>
> Run `/sdlc-review-fix` to fix all findings.

Do NOT fix anything in this command. Do NOT offer partial fix options. The review command only reviews — `/sdlc-review-fix` handles all fixes.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, skip some lenses" | Small diffs produce the subtlest bugs |
| "Agent fixed the issue during review" | Report only — fixes go through `sdlc-review-fix` |
| "This is just a refactor, no review needed" | Refactors need architecture and DRY lens review |
| "Skip Tier 2, it's a small commit" | Read the diff content. Small commits introduce new patterns more often than expected. |
| "This agent overlaps with another, skip it" | Agents review different concerns. `performance-engineer` and `frontend-developer` both review component code but catch different issues. |
| "No security concerns in this diff" | Check the boundaries lens anyway. User input flows through surprising paths. |

## Integration
- **Feeds into:** `sdlc-review-fix` (if findings need fixing)
- **Siblings:** `sdlc-review-diff` (same lenses, targets working tree), `sdlc-review-team` (same lenses, adds inter-agent debate)
- **Shared reference:** Agent selection and review lenses live in `ops/sdlc/process/review-agent-selection.md`
