---
name: sdlc-review-code
description: >
  Review code changes with domain agents — checks for overengineering, unnecessary code, DRY violations,
  and architecture adherence. Target auto-detects from arguments: no argument reviews uncommitted changes,
  a commit ref reviews that commit, a range reviews the range.
  Use when code changes need review — works on uncommitted changes, specific commits, or commit ranges.
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

**Knowledge routing:** After selecting agents, consult `[sdlc-root]/knowledge/agent-context-map.yaml` for each selected agent's entry. Include their mapped knowledge files in the dispatch prompt so agents receive domain context alongside the diff. Read `[sdlc-root]/knowledge/coding/code-quality-principles.yaml` and include it in every `code-reviewer` dispatch — it is the code-reviewer's primary quality reference and applies to every review.

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

**Pre-dispatch — CLAUDE.md Alignment Lens**

The diff may invalidate documented project knowledge. Ask `code-reviewer` to compare the diff against the project's CLAUDE.md (root + any module-/package-level CLAUDE.md whose tree the diff touches):

> **CLAUDE.md alignment check:** For each file changed in this diff, check whether the project's CLAUDE.md (or a CLAUDE.md in the file's package) makes claims that the diff invalidates — file paths that moved or were deleted, conventions that changed, build/test/lint commands that no longer work, dependencies that were swapped or removed, or architecture statements that no longer describe the codebase. Cite the CLAUDE.md line that needs updating and the diff change that invalidated it. Flag stale documentation as `minor` with category `claude-md-staleness`. Escalate to `major` only when the staleness would actively misdirect a future agent (e.g., wrong build command, removed module still listed as canonical).

This is a documentation-correctness check, not a "should we add more documentation" prompt. Do not flag CLAUDE.md for missing context the diff *could* be added to — only for content the diff *invalidates*.

**Pre-dispatch — Commit Message Quality Lens**

The commit message is part of the deliverable — it is the primary record of *why* a change was made. Ask `code-reviewer` to assess the commit message alongside the code:

> **Commit message check:** Verify the subject line uses conventional-commits format (`type(scope): imperative verb`), stays under ~72 characters, and describes the *what* at a summary level. Verify the body explains the *why* — not just what the code does (the diff shows that), but what reasoning led to this approach. Flag a missing body on any commit that introduces a non-trivial design choice as `minor` with category `commit-quality`. Flag a subject line that describes implementation mechanics rather than intent (e.g., "add variable X" vs. "prevent tenant ID from leaking into log output") as `minor`.

Dispatch ALL listed agents in parallel. Each agent receives the full diff and is asked to review using the lenses defined in `[sdlc-root]/process/review-lenses.md` (all lenses apply to code review — see applicability table) plus the pre-dispatch test-quality and commit-message lenses above. Each agent reviews through their domain expertise but applies all applicable lenses. Read `[sdlc-root]/knowledge/architecture/agent-orchestration-patterns.yaml` and use the dispatch template from § dispatch_prompt_templates: objective = "Review {target} through your {domain} lens"; owned files = "Read-only — do not modify files"; acceptance criteria = "Return structured findings per the finding format below with severity and category"; out-of-scope = "Do not fix issues — report only. Do not duplicate the {other-agent} lens."

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
| 1 | specific finding | agent-name | critical/major/minor | overengineering/type-safety/security/contract/DRY/architecture/correctness/test-quality/commit-quality/claude-md-staleness |
| 2 | ... | ... | ... | ... |

### Overengineering Summary

[If any overengineering or unnecessary code was found, summarize the pattern here — e.g., "3 helper functions wrap single operations", "error handling added for impossible states". If none found, say "No overengineering detected."]

### CLAUDE.md Drift

[If any `claude-md-staleness` findings exist, list which CLAUDE.md file(s) and section(s) the diff invalidates and the line(s) that need updating. Authors miss documentation updates by default — surface this as a cross-cutting concern alongside Overengineering. Omit this section entirely when no drift was flagged.]

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

### 6. Log Recurring Patterns

After presenting the report, scan findings for patterns that recur across files or represent a general class of mistake. If any pattern qualifies, log it to the **recurring patterns file** at `docs/reviews/recurring-patterns.yaml`.

**Step 6a. Read the log.** If `docs/reviews/recurring-patterns.yaml` exists, read it. If it doesn't exist, create it with the seed structure:

```yaml
# Recurring review patterns — clustered by agent judgment.
# sdlc-audit Dimension 6l scans this file for threshold breaches.
patterns: []
```

**Step 6b. Match or create clusters.** For each pattern worth capturing from this review:

1. Read existing cluster slugs and descriptions in the file.
2. Use judgment: does this pattern match an existing cluster? Same root cause class, same lens, same kind of mistake — even if the specific file or manifestation differs.
3. **If match found:** append a new occurrence entry to that cluster.
4. **If no match:** create a new cluster with a descriptive slug, description, lens category, and the first occurrence.

**Step 6c. Write the log.** Write the updated YAML file. The diff will appear as an uncommitted change the user can inspect before committing.

**Cluster entry format:**

```yaml
patterns:
  - slug: {kebab-case-identifier}
    description: "{one-line description of the recurring pattern}"
    lens: {security|correctness|architecture|DRY|type-safety|overengineering|test-quality|contract}
    first_seen: YYYY-MM-DD
    occurrences:
      - date: YYYY-MM-DD
        commit: {short-sha}
        manifestation: "{what specifically was found in this review}"
        files: [{path/to/affected/file}]
    promoted: false
```

**Step 6d. Surface in the report.** After logging, add a section to the report output:

```markdown
### Patterns Worth Capturing

| Pattern | Occurrences | Status |
|---------|-------------|--------|
| {slug} — {description} | {N} (first: {date}, latest: this review) | {new / recurring / at threshold} |

[If no patterns identified, omit this section.]
```

Mark patterns "at threshold" when they reach 3+ occurrences — these are candidates for knowledge-store promotion via `sdlc-audit`.

**Slug consistency:** The file itself is the slug registry. Reading existing slugs and descriptions before writing is sufficient for agent judgment to reuse the right slug. When uncertain whether a finding matches an existing cluster, prefer creating a new cluster — false splits are easier to merge than false merges are to untangle.

Do NOT ingest into the knowledge store from within this skill. Do NOT create parking-lot entries. The pattern log feeds `sdlc-audit` Dimension 6l, which handles promotion recommendations.

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
| "The diff doesn't add docs, so no CLAUDE.md issue" | The CLAUDE.md alignment lens checks for *invalidated* claims, not missing ones. A path rename, dropped command, or deleted module that CLAUDE.md still references is a finding regardless of whether the diff adds documentation. |
| "CLAUDE.md feels out of date in general — flag it" | The lens is scoped to claims the *current diff* invalidates. Out-of-date content unrelated to this diff is for `claude-md-improver` audits, not commit-scoped review. |

## Integration
- **Feeds into:** `sdlc-review-fix` (if findings need fixing)
- **Siblings:** `sdlc-team-review-fix` (same lenses + inter-agent debate + persistent team fix lifecycle — higher cost, use for high-stakes changes)
- **Shared reference:** Agent selection in `[sdlc-root]/process/agent-selection.yaml`, lenses in `[sdlc-root]/process/review-lenses.md`
- **Knowledge routing:** `[sdlc-root]/knowledge/agent-context-map.yaml` (dispatch-time injection), `[sdlc-root]/knowledge/coding/code-quality-principles.yaml` (code-reviewer primary), `[sdlc-root]/knowledge/architecture/agent-orchestration-patterns.yaml` (dispatch template)
