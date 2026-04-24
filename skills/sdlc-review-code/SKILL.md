---
name: sdlc-review-code
description: >
  Review code changes with domain agents — checks for overengineering, unnecessary code, DRY violations,
  and architecture adherence. Target auto-detects from arguments: no argument reviews uncommitted changes,
  a commit ref reviews that commit, a range reviews the range.
  Triggers on "review this commit", "review HEAD", "review the last commit", "code review",
  "review uncommitted changes", "check my diff", "review before committing", "diff review",
  "review working tree", "look at my changes", "/sdlc-review-code".
  Do NOT fix findings in this skill — use sdlc-review-fix for that.
  Do NOT use for reviewing skill/agent files — use sdlc-review for that.
---

# Review Code

Review code changes with relevant domain agents. Prioritizes catching overengineered solutions and unnecessary code alongside standard quality checks.

**Argument:** `$ARGUMENTS` (optional) — commit ref, commit range, or empty.

## Steps

### 1. Resolve Target

Parse `$ARGUMENTS` to determine what to review:

| Argument | Target | How to Gather |
|----------|--------|---------------|
| None | Uncommitted changes (staged + unstaged) | `git diff HEAD --stat`, `git diff HEAD`, `git status -s` |
| Commit ref (e.g., `HEAD`, `abc1234`) | That commit | `git show --stat {ref}`, `git show {ref}` |
| Commit range (e.g., `abc..def`, `HEAD~3..HEAD`) | Range diff | `git diff --stat {range}`, `git diff {range}` |

**Uncommitted mode — empty diff check:** If there are no uncommitted changes, stop:

> No uncommitted changes to review.

**Uncommitted mode — untracked files:** If `git status -s` shows untracked files that look like new source files (not build artifacts, `.env`, or `node_modules`), warn:

> Note: {N} untracked files not included in the diff — `git add` them first if they should be reviewed.

**Ref mode — invalid ref:** If the ref or range is invalid, tell the user and stop.

### 2. Identify Relevant Domain Agents

Follow `[sdlc-root]/process/agent-selection.yaml` for dispatch rules:
- Tier 1 (domain agents) — always dispatch when the work involves their domain
- Tier 2 (structural agents) — dispatch only when warranted
- Selection process at the end of the file

### 3. Dispatch Review Agents

Output a checklist before dispatching:

```
Reviewing {target description}
Files changed: N

Dispatching reviewers:
- [ ] code-reviewer (always)
- [ ] frontend-developer (touches frontend components)
- [ ] performance-engineer (new store selectors)

Not dispatching:
- software-architect — follows existing pattern, no new abstractions
- ui-ux-designer — logic-only changes, no visual modifications
```

Where `{target description}` is:
- `uncommitted changes` (no argument)
- `commit {short-sha}: {commit subject}` (commit ref)
- `range {range}: {N} commits` (commit range)

Dispatch ALL listed agents in parallel. Each agent receives the full diff and is asked to review using the lenses defined in `[sdlc-root]/process/review-lenses.md` (all lenses apply to code review — see applicability table). Each agent reviews through their domain expertise but applies all applicable lenses.

### 4. Collect and Present Findings

Collect all findings. Present them in a single structured report:

```markdown
## Code Review: {target description}

{commit subject if applicable}
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

If the target was uncommitted changes, also include:

> Or commit first and run `/sdlc-review-code HEAD` for a post-commit review.

Do NOT fix anything in this skill. Do NOT offer partial fix options. The review skill only reviews — `/sdlc-review-fix` handles all fixes.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, skip some lenses" | Small diffs produce the subtlest bugs |
| "Just do a quick glance, we're about to commit" | Quick glances miss type safety and contract issues. Run the full workflow. |
| "Agent fixed the issue during review" | Report only — fixes go through `sdlc-review-fix` |
| "This is just a refactor, no review needed" | Refactors need architecture and DRY lens review |
| "Skip Tier 2, it's a small commit" | Read the diff content. Small commits introduce new patterns more often than expected. |
| "This agent overlaps with another, skip it" | Agents review different concerns. `performance-engineer` and `frontend-developer` both review component code but catch different issues. |
| "No security concerns in this diff" | Check the boundaries lens anyway. User input flows through surprising paths. |

## Integration
- **Feeds into:** `sdlc-review-fix` (if findings need fixing)
- **Siblings:** `sdlc-team-review-fix` (same lenses + inter-agent debate + persistent team fix lifecycle — higher cost, use for high-stakes changes)
- **Shared reference:** Agent selection in `[sdlc-root]/process/agent-selection.yaml`, lenses in `[sdlc-root]/process/review-lenses.md`
