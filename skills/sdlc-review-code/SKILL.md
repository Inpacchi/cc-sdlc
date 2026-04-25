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

**Scope Discipline — Before Dispatching**

Each domain agent reviews through their own lens — they do not divide the diff by file, they divide it by concern. Two agents can legitimately flag different issues at the same line (e.g., `backend-developer` catches a missing filter; `code-reviewer` catches an unhandled exception at the same location). This is correct and expected. Do NOT pre-deduplicate by excluding an agent because another agent "will cover it."

What agents should NOT do is overlap on *concern*: if `code-reviewer` is already reviewing security boundaries, do not also ask another agent to perform a full security review. Set scope explicitly in dispatch prompts using constraint language: "Review through your [X] lens. Security boundary review is handled by code-reviewer — flag anything that interacts with it, but do not duplicate that lens."

The output of this discipline: each agent's report covers its own non-overlapping concern slice. Overlap in *location* (same file:line) is fine and will be handled at collection time. Overlap in *concern* inflates the finding list with duplicates and creates conflicting recommendations that the author cannot resolve.

**Pre-dispatch — Test Quality Lens**

Beyond "what is NOT tested" (absence analysis), agents must also assess the quality of tests that *are* present. Include this instruction in each relevant agent's dispatch prompt:

> **Test quality check:** For each new or modified test in this commit, verify:
> - Tests assert observable behavior, not internal state or implementation details. A test that checks `component.state.counter == 1` instead of checking what the user sees is testing the implementation, not the contract — it will break on any internal refactor even when behavior is preserved.
> - Test names describe the scenario and expected outcome, not the method under test. `test_item_not_returned_for_wrong_tenant` is a test document. `test_item_query` is a label.
> - Tests are deterministic and order-independent. Any test that relies on external state, prior test data, or wall-clock time without explicit setup/teardown is a latent flake.

Flag behavior-testing violations as `minor` with category `test-quality`. Flag determinism issues as `major` — flaky tests erode the signal value of the entire suite.

**Pre-dispatch — Commit Message Quality Lens**

The commit message is part of the deliverable — it is the primary record of *why* a change was made. Ask `code-reviewer` to assess the commit message alongside the code:

> **Commit message check:** Verify the subject line uses conventional-commits format (`type(scope): imperative verb`), stays under ~72 characters, and describes the *what* at a summary level. Verify the body explains the *why* — not just what the code does (the diff shows that), but what reasoning led to this approach. Flag a missing body on any commit that introduces a non-trivial design choice as `minor` with category `commit-quality`. Flag a subject line that describes implementation mechanics rather than intent (e.g., "add variable X" vs. "prevent tenant ID from leaking into log output") as `minor`.

Dispatch ALL listed agents in parallel. Each agent receives the full diff and is asked to review using the lenses defined in `[sdlc-root]/process/review-lenses.md` (all lenses apply to code review — see applicability table) plus the pre-dispatch test-quality and commit-message lenses above. Each agent reviews through their domain expertise but applies all applicable lenses.

### 4. Collect and Present Findings

Collect all findings. Present them in a single structured report.

**Finding Deduplication — Before Building the Report**

When multiple domain agents flag issues at the same location, apply these merge rules:

| Situation | Action |
|-----------|--------|
| Same `file:line`, same underlying issue | Merge into one finding. Credit all agents. Keep the more detailed description. Use the highest severity among them. |
| Same `file:line`, different issues | Keep as separate findings. Tag both as `co-located` in the Category column so the author knows they are distinct concerns at the same spot. |
| Same issue, different locations | Keep separate. Cross-reference: "See also: Finding #N (same pattern at `other/file.py:88`)". |
| Same location, conflicting fix recommendations | Keep merged but include both recommendations with agent attribution: "agent-A recommends X; agent-B recommends Y." Do not silently choose one. |

**Severity Calibration — Before Assigning Labels**

Severity is a function of **impact x likelihood**, not reviewer alarm level. Before finalizing severity on any finding, apply these calibration rules to prevent a single agent inflating the report:

| Severity | Criteria |
|----------|----------|
| `critical` | Certain or very likely data loss, security breach, or complete failure |
| `major` | Significant functionality impact, likely to manifest |
| `minor` | Partial impact, workaround exists, or cosmetic |

A finding escalated by one agent to `critical` that would calibrate as `major` by the above criteria should be downgraded. Note the rationale in the finding detail: "Calibrated from agent-reported critical to major: impact is significant but not certain data loss under normal conditions."

The calibration step protects the author from alert fatigue: a report where everything is `critical` is a report that gets ignored.

**Report Framing Discipline — Before Writing Finding Details**

The structured findings report is read by a developer who will act on it. How findings are phrased affects whether they produce action or defensiveness. Apply these framing rules when writing the Details section:

- Prefix non-blocking findings explicitly: `nit:` signals "this is stylistic, not blocking." Authors should be able to skip nits without guilt. If it does not get a `nit:` prefix, it is assumed to require action.
- Use question form for uncertain findings — where the issue depends on context the agent may not have: "What happens to active sessions when this migration rolls back?" is better than asserting "This migration will corrupt sessions" when that outcome is conditional.
- Use declarative form for confirmed issues: "This query runs without a tenant filter — results will include other tenants' data."

| Framing form | When to use |
|--------------|-------------|
| `nit:` prefix | Non-blocking stylistic preference; author may ignore |
| Question form | Uncertain finding; outcome depends on context not in the diff |
| Declarative form | Confirmed issue with a clear fix |

```markdown
## Code Review: {target description}

{commit subject if applicable}
{N} files changed | Reviewed by {N} domain agents

### Findings

| # | Finding | Agent | Severity | Category |
|---|---------|-------|----------|----------|
| 1 | specific finding | agent-name | critical/major/minor | overengineering/type-safety/security/contract/DRY/architecture/correctness/test-quality/commit-quality |
| 2 | ... | ... | ... | ... |

### Overengineering Summary

[If any overengineering or unnecessary code was found, summarize the pattern here — e.g., "3 helper functions wrap single operations", "error handling added for impossible states". If none found, say "No overengineering detected."]

### Details

#### Finding 1: [title]
**Agent:** [agent-name] | **Severity:** [level] | **Category:** [category]
**File:** [path:line]
[Concrete description of the issue and what should change]

### Agent Coverage Summary

| Agent | Critical | Major | Minor | Total |
|-------|----------|-------|-------|-------|
| code-reviewer | 0 | 0 | 0 | 0 |
| {agent-name} | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** |

*(Fill in actual counts. Rows = agents dispatched; columns = calibrated severity after deduplication.)*
```

### 5. Next Steps

After presenting the report:

> **{N} findings** ({critical} critical, {major} major, {minor} minor)
>
> Run `/sdlc-review-fix` to fix all findings.

If the target was uncommitted changes, also include:

> Or commit first and run `/sdlc-review-code HEAD` for a post-commit review.

Do NOT fix anything in this skill. Do NOT offer partial fix options. The review skill only reviews — `/sdlc-review-fix` handles all fixes.

### 6. Extract Reusable Patterns (Optional but Encouraged)

After presenting the report, scan findings for patterns that recur across files or represent a general class of mistake the codebase has seen before. If any pattern qualifies, note it at the bottom of the report:

```markdown
### Patterns Worth Capturing

[If one or more findings represent a recurring class of issue, list them here for knowledge-store capture. Examples: "tenant filter missing on 3 query sites — candidate for knowledge store entry", "lazy relationship accessed outside async context (2nd occurrence this sprint)". If no recurring patterns identified, omit this section.]
```

This is the knowledge-sharing function of review. A one-off finding is a fix. A finding that recurs across commits is a gap in the team's shared understanding — it belongs in `[sdlc-root]/knowledge/` as a documented anti-pattern, not in every individual review as a repeated finding. Flag it here; use `sdlc-ingest` to formalize it into the knowledge store.

Do NOT ingest directly from within this skill — surface the pattern and let the user decide whether it warrants a knowledge-store entry.

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
| "Two agents flagged the same line, merge them" | Same line, same issue — merge and credit both. Same line, different issues — keep separate and tag `co-located`. Merging by location erases real findings. |
| "One agent called it critical, that settles it" | Severity is calibrated after collection, not inherited from the loudest agent. Apply the impact x likelihood criteria before finalizing the severity label. |
| "An agent recommended refactoring the whole module while reviewing" | Scope creep in a finding. A finding must name a specific problem and a surgical fix. If the fix requires rewriting code outside the commit's scope, flag the specific issue and note the broader refactor as a separate tracking issue — not a required fix in this review. |
| "The agent phrased every finding as a command" | Findings on uncertain issues should be questions. Findings on confirmed issues should be declarative. Using command form for a speculation inflates the author's cognitive load. |

## Integration
- **Feeds into:** `sdlc-review-fix` (if findings need fixing)
- **Siblings:** `sdlc-team-review-fix` (same lenses + inter-agent debate + persistent team fix lifecycle — higher cost, use for high-stakes changes)
- **Shared reference:** Agent selection in `[sdlc-root]/process/agent-selection.yaml`, lenses in `[sdlc-root]/process/review-lenses.md`
