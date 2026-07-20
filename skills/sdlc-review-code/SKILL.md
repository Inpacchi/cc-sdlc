---
name: sdlc-review-code
description: >
  Review code changes with domain agents — checks for overengineering, unnecessary code, DRY violations,
  and architecture adherence. Target auto-detects from arguments: no argument reviews uncommitted changes,
  a commit ref reviews that commit, a range reviews the range.
  Use when code changes need review — works on uncommitted changes, specific commits, or commit ranges.
  Triggers on "review this commit", "review HEAD", "review the last commit", "code review",
  "review uncommitted changes", "check my diff", "review before committing", "diff review",
  "review working tree", "look at my changes", "/sdlc-review-code",
  "fix review findings", "fix the review", "address the findings", "fix all findings".
  Do NOT use for reviewing skill/agent files — dispatch the sdlc-reviewer subagent directly.
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
- [ ] software-architect (always)
- [ ] frontend-developer (touches frontend components)
- [ ] performance-engineer (new store selectors)

Not dispatching:
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

**Pre-dispatch — Architecture Guardrail Lens**

The software-architect runs on every review as the structural counterpart to code-reviewer. Where code-reviewer catches micro issues (DRY, correctness, naming, overengineering at the expression level), software-architect catches macro drift that compounds across changes. Include this instruction in `software-architect`'s dispatch prompt:

> **Architecture guardrail check:** Review this diff for structural health, not code quality (code-reviewer handles that). Specifically:
> - **Boundary violations:** Are responsibilities leaking across module or package boundaries? Imports flowing the wrong direction? Features reaching into each other's internals?
> - **Pattern drift:** Does new code silently introduce a second way to do something the codebase already has a pattern for? If so, flag which existing pattern it diverges from.
> - **Extraction signals:** Are any files, functions, or components growing beyond a single responsibility? Would this change be the right time to extract, or is it premature?
> - **Abstraction fitness:** Are new or existing abstractions earning their complexity? Flag wrappers that pass through without transforming, or indirection that serves exactly one consumer.
> - **Scope discipline:** Does the diff stay within its stated intent, or does it quietly expand into adjacent concerns that should be separate changes?
> - **Dependency health:** Are new dependencies (imports, packages) justified? Do they create coupling that will make future changes harder?
>
> Flag boundary violations and pattern drift as `major` with category `architecture`. Flag extraction signals and scope observations as `minor` with category `architecture`. Escalate to `critical` only when the structural issue would force a rewrite if left to compound (e.g., circular dependency between packages).

This lens complements, not duplicates, the Standard lens's "Architecture adherence" bullet — that bullet checks convention conformance; this lens checks whether the codebase structure is staying healthy over time.

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
| 1 | specific finding | agent-name | critical/major/minor | overengineering/type-safety/security/contract/DRY/architecture/correctness/test-quality/commit-quality/claude-md-staleness/adr-drift |
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

### 5. Fix Gate

After presenting the report, offer to fix:

> **{N} findings** ({critical} critical, {major} major, {minor} minor)
>
> Fix these findings?

If the user declines, stop here. If the user accepts, proceed to Step 5a.

### 5a. Fix Findings

**You are the manager.** The canonical rule is in `[sdlc-root]/process/manager-rule.md`. The critical guardrails are inlined here so that skipping the read does not skip the behavior:

**Economics-qualifying fixes — you may self-apply** when ALL are true per the Manager Rule's Delegation Economics Exception: (1) delegation would cost more than the fix itself — in tokens or main-context growth; (2) small and bounded — a few edit sites, no new abstractions; (3) no design judgment — mechanical or following a citable existing pattern; (4) no new context needed — you can decide HOW from what is already in your window. Trivial fixes always qualify: typos, missing imports, unused variables, obvious type annotations, missing `key` props. Every self-applied fix goes through the review loop in Step 5b — self-applied is never self-approved.

**Non-qualifying fixes — dispatch domain agents.** If you need to read surrounding code to decide HOW to fix, it does not qualify. Group non-trivial findings by the most relevant domain agent. Consult `[sdlc-root]/knowledge/architecture/agent-orchestration-patterns.yaml` for dispatch discipline (AOP1, AOP9). When dispatching 2+ fixers in parallel, follow `[sdlc-root]/process/parallel-dispatch-monitoring.md`. Each agent receives: the specific findings assigned to them, the original diff, cross-domain knowledge files from the finding agent (when fixer differs from finder, consult `[sdlc-root]/knowledge/agent-context-map.yaml`), and instruction to make the minimal change that addresses each finding.

**If an agent returns without applying its fix, re-dispatch with a revised prompt.** Only a remaining gap that itself passes the economics test may be closed directly (with review).

**Guard modification is in-scope.** If a finding matches a cluster in `docs/reviews/recurring-patterns.yaml` that has (or plainly warrants) a mechanized guard, the fix is two-part: fix the instance AND update or create the guard (lint rule, drift test, CI check) so the next instance is caught mechanically. See `[sdlc-root]/process/guardrail-lifecycle.md` § "Guard Modification Is In-Scope in Review Loops". Guard edits go through the same review loop as any other fix.

**Self-check before proceeding:** Count findings you self-fixed under the economics test. Count findings dispatched to agents. The two numbers must equal the total finding count. If any finding is neither self-fixed nor dispatched, stop — you missed one.

After all fixes (self-applied and agent-applied), verify the project builds.

### 5b. Review-Fix Loop

**This loop is mandatory — whether fixes were self-applied or agent-applied.** No shortcuts, no skipping, no claiming it ran without a clean review round.

The full protocol is in `[sdlc-root]/process/review-fix-loop.md`. The critical mechanics are inlined here:

1. **Verification gate** — tests, type checks, and lint must pass before dispatching reviewers. Fix failures first.
2. **Dispatch ALL review agents** from the original review (Step 3) as **subagents** — separate context windows, not inline. Context separation prevents confirmation bias: a reviewer in the same context that wrote the fix is biased toward approving it.
3. **Collect findings.** If ALL agents report zero findings → loop exits clean. Zero means zero — not "only minor," not "only pre-existing."
4. **Classify each finding** per `[sdlc-root]/process/finding-classification.md`: FIX, INVESTIGATE, DECIDE, PRE-EXISTING.
5. **Fix classified findings** — dispatch agents for non-trivial, self-fix trivial (same rules as Step 5a).
6. **Return to step 2 — mandatory.** Dispatch ALL agents again, not just the ones who found issues. Fixes can introduce new problems in other domains.

The loop repeats until step 3 shows all agents clean. **Do not claim the loop exited clean without a review round that produced zero findings.**

**3-strike rule:** If the same finding recurs across 3 consecutive rounds, stop iterating and escalate to the user via `AskUserQuestion`.

**External Review Gate (optional):** After the internal loop is clean and before commit, if `[sdlc-root]/external-review.sh` exists and is executable, run the External Review Gate — a cross-vendor (Codex / local LLM) independent second opinion. Its findings re-enter Step 5b's triage; the external model never fixes. State any data egress to CD first. Full protocol: `[sdlc-root]/process/external-review-gate.md` (also `[sdlc-root]/process/review-fix-loop.md` Step E). Skip silently if the wrapper is absent.

### 5c. Summary and Commit

When the loop exits clean, present:

```markdown
## Fix Summary

{N} original findings fixed | {M} review rounds | Build: passing

Key feedback incorporated:
- [agent-name] specific feedback that was incorporated
```

> All fixes applied, review loop clean, build passes. Want me to commit?

Do NOT commit automatically — wait for user confirmation.

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

Two optional fields appear on clusters after audit-triage promotions — do not remove them when appending occurrences: `knowledge_entry` (path to the promoted knowledge file, set with `promoted: true`) and `mechanized_guard` (the lint rule / drift test / CI check that now catches the pattern — schema and lifecycle in `[sdlc-root]/process/guardrail-lifecycle.md`).

**Step 6d. Surface in the report.** After logging, add a section to the report output:

```markdown
### Patterns Worth Capturing

| Pattern | Occurrences | Status |
|---------|-------------|--------|
| {slug} — {description} | {N} (first: {date}, latest: this review) | {new / recurring / at threshold} |

[If no patterns identified, omit this section.]
```

Mark patterns "at threshold" when they reach 3+ occurrences — these are candidates for knowledge-store promotion and/or mechanized-guard promotion via `sdlc-audit` (see `[sdlc-root]/process/guardrail-lifecycle.md`). If a new occurrence lands on a cluster that already has a `mechanized_guard`, say so explicitly in the Status column ("recurred despite guard") — that is a guard-effectiveness signal `sdlc-audit` Dimension 6n needs.

**Slug consistency:** The file itself is the slug registry. Reading existing slugs and descriptions before writing is sufficient for agent judgment to reuse the right slug. When uncertain whether a finding matches an existing cluster, prefer creating a new cluster — false splits are easier to merge than false merges are to untangle.

Do NOT ingest into the knowledge store from within this skill. Do NOT create parking-lot entries. The pattern log feeds `sdlc-audit` Dimension 6l, which handles promotion recommendations.

### 7. HTML Review Artifact (opt-in)

After completing the review report, ask CD whether they want an HTML render of it for reading/sharing — don't render unprompted. If CD declines, the markdown report stands as the deliverable and you skip the rest of this step.

If CD accepts, render it as a self-contained HTML file: read the design system from `[sdlc-root]/templates/html-design-system.html` and apply **review** document-type defaults from `[sdlc-root]/process/html-rendering.md`.

Write to: `docs/reviews/{target_slug}_review.html` (e.g., `docs/reviews/HEAD_review.html`, `docs/reviews/abc1234_review.html`, `docs/reviews/uncommitted_review.html`).

The HTML review should include:
- Header with target description, date, and overall finding counts
- File risk map (table with per-file change stats and severity dots)
- Annotated diffs with inline margin comments for each finding (use diff viewer + callout components)
- Overengineering summary section
- CLAUDE.md drift section (if applicable)
- Agent coverage summary
- Findings detail with severity-coded badges
- Recurring patterns section (if any identified)

This is the artifact CD uses for review — it replaces scrolling through terminal output. If `docs/reviews/` doesn't exist, create it.

### 8. Session Learning Capture

Code reviews surface cross-discipline insights — gotchas, anti-patterns, cross-domain friction, and knowledge gaps that go beyond the specific diff. Step 6 captures recurring *patterns* to `recurring-patterns.yaml`, but discipline-level insights (e.g., a testing paradigm gap, an architecture anti-pattern, a DX friction point) belong in parking lots.

If this review surfaced non-obvious learnings beyond the findings themselves, suggest:

> This review surfaced insights that may be worth capturing to discipline parking lots. Consider running `/sdlc-reflect` to surface them.

Skip the suggestion if the review was routine with no cross-cutting insights.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, skip some lenses" | Small diffs produce the subtlest bugs |
| "Just do a quick glance, we're about to commit" | Quick glances miss type safety and contract issues. Run the full workflow. |
| "Agent fixed the issue during review" | Report only during review — fixes go through the fix gate (Step 5) |
| "I'll start fixing without asking" | Always present the fix gate. The user decides whether to fix. |
| "This is just a refactor, no review needed" | Refactors need architecture and DRY lens review |
| "Skip Tier 2, it's a small commit" | Read the diff content. Small commits introduce new patterns more often than expected. |
| "software-architect will catch what code-reviewer catches" | They have non-overlapping scopes. code-reviewer handles micro (DRY, correctness, naming). software-architect handles macro (boundaries, dependency direction, pattern drift). Neither substitutes for the other. |
| "This agent overlaps with another, skip it" | Agents review different concerns. `performance-engineer` and `frontend-developer` both review component code but catch different issues. |
| "No security concerns in this diff" | Check the boundaries lens anyway. User input flows through surprising paths. |
| "Two agents flagged the same line, merge them" | Same line, same issue — merge and credit both. Same line, different issues — keep separate and tag `co-located`. Merging by location erases real findings. |
| "One agent called it critical, that settles it" | Severity is calibrated after collection, not inherited from the loudest agent. Apply the impact x likelihood criteria before finalizing the severity label. |
| "An agent recommended refactoring the whole module while reviewing" | Scope creep in a finding. A finding must name a specific problem and a surgical fix. If the fix requires rewriting code outside the commit's scope, flag the specific issue and note the broader refactor as a separate tracking issue — not a required fix in this review. |
| "The agent phrased every finding as a command" | Findings on uncertain issues should be questions. Findings on confirmed issues should be declarative. Using command form for a speculation inflates the author's cognitive load. |
| "The diff doesn't add docs, so no CLAUDE.md issue" | The CLAUDE.md alignment lens checks for *invalidated* claims, not missing ones. A path rename, dropped command, or deleted module that CLAUDE.md still references is a finding regardless of whether the diff adds documentation. |
| "CLAUDE.md feels out of date in general — flag it" | The lens is scoped to claims the *current diff* invalidates. Out-of-date content unrelated to this diff is for `claude-md-improver` audits, not commit-scoped review. |

## Integration
- **Feeds into:** `docs/reviews/recurring-patterns.yaml` (pattern log for `sdlc-audit` Dimension 6 promotion), `sdlc-reflect` (suggests it when cross-discipline insights surface beyond the findings themselves)
- **Uses:** `[sdlc-root]/process/agent-selection.yaml` (agent dispatch), `[sdlc-root]/process/review-lenses.md` (review lenses), `[sdlc-root]/process/review-fix-loop.md` (fix loop), `[sdlc-root]/process/guardrail-lifecycle.md` (mechanized-guard schema and in-scope rule), `[sdlc-root]/knowledge/agent-context-map.yaml` (dispatch-time injection), `[sdlc-root]/knowledge/coding/code-quality-principles.yaml` (code-reviewer primary)
- **Complements:** `sdlc-execute` (development phase before review), `sdlc-audit` (promotes recurring patterns to knowledge store)
- **Does NOT replace:** Quality gates in `sdlc-develop-skill` / `sdlc-develop-agent` (those are author-facing convention checks, not diff-facing code review)
