---
name: sdlc-review-diff
description: >
  Review all uncommitted changes in the working tree with domain agents — same lenses as sdlc-review-commit
  but targets the working tree before committing. Triggers on "review uncommitted changes", "check my diff",
  "review before committing", "diff review", "review working tree", "look at my changes".
  Do NOT use for committed code — use sdlc-review-commit for that.
---

# Review Uncommitted Changes

Review all uncommitted changes (staged + unstaged) with relevant domain agents. Same review lenses as `/sdlc-review-commit` but targets the working tree diff instead of a commit.

## Steps

### 1. Gather the Diff

Run `git diff HEAD --stat` to get the list of changed files and a summary. Then run `git diff HEAD` to get the full diff.

If there are no changes, tell the user and stop:

> No uncommitted changes to review.

Also run `git status -s` to check for untracked files. If untracked files exist that look like new source files (not build artifacts, .env, or node_modules), warn:

> Note: {N} untracked files not included in the diff — `git add` them first if they should be reviewed.

### 2. Identify Relevant Domain Agents

Follow the agent selection process in `[sdlc-root]/process/agent-selection.md`. That document defines:
- Tier 1 (domain agents) — always dispatch when the work involves their domain
- Tier 2 (structural agents) — dispatch only when warranted
- The 4-step selection process

### 3. Dispatch Review Agents

Output a checklist before dispatching:

```
Reviewing uncommitted changes
Files changed: N

Dispatching reviewers:
- [ ] code-reviewer (always)
- [ ] frontend-developer (touches frontend components)
- [ ] performance-engineer (new store selectors)

Not dispatching:
- software-architect — follows existing pattern, no new abstractions
- ui-ux-designer — logic-only changes, no visual modifications
```

Dispatch ALL listed agents in parallel. Each agent receives the full diff and is asked to review using the lenses defined in `[sdlc-root]/process/agent-selection.md` § Lenses (all lenses apply to code review — see applicability table). Each agent reviews through their domain expertise but applies all applicable lenses.

### 4. Collect and Present Findings

Collect all findings. Present them in a single structured report:

```markdown
## Diff Review: uncommitted changes

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
> Run `/sdlc-review-fix` to fix all findings, or commit first and run `/sdlc-review-commit` for a post-commit review.

Do NOT fix anything in this skill. Do NOT offer partial fix options. The review skill only reviews — `/sdlc-review-fix` handles all fixes.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, skip some lenses" | Small diffs produce the subtlest bugs |
| "Just do a quick glance, we're about to commit" | Quick glances miss type safety and contract issues. Run the full workflow. |
| "Agent fixed the issue during review" | Report only — fixes go through `sdlc-review-fix` |
| "This is just a refactor, no review needed" | Refactors need architecture and DRY lens review |
| "Skip Tier 2, it's obviously not architectural" | Read the diff content first. Routine-looking changes introduce new patterns more often than expected. |

## Integration
- **Depends on:** None (operates on uncommitted working tree changes)
- **Feeds into:** `sdlc-review-fix` (if findings need fixing)
- **Siblings:** `sdlc-review-commit` (same lenses, targets commits), `sdlc-review-team` (same lenses, adds inter-agent debate)
- **Shared reference:** Agent selection and lenses live in `[sdlc-root]/process/agent-selection.md`
