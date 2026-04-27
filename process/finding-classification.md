# Finding Classification

The canonical taxonomy for classifying review findings. Every skill that triages findings references this file.

---

## Classification Table

Classify each finding individually in a table before acting — no narrative paragraphs, no blanket dismissals:

```
| # | Finding | Agent | Classification | Severity | Rationale |
|---|---------|-------|---------------|----------|-----------|
| 1 | specific finding | agent-name | FIX / PLAN / INVESTIGATE / DECIDE / PRE-EXISTING | critical/major/minor | why |
```

Severity applies only to FIX findings. Other classifications leave Severity blank.

## The Five Classifications

| Classification | When | Action |
|---------------|------|--------|
| **FIX** | Confident in diagnosis AND fix, AND the correct resolution is clear without user input | Dispatch the most relevant domain agent to fix it. In planning skills: include in revision dispatch. |
| **PLAN** | Systemic issue (many files, architecture change) that exceeds a single fix | Needs a sub-plan. Flag to CD. |
| **INVESTIGATE** | Need more information before classifying | Dispatch relevant agent to diagnose, then reclassify |
| **DECIDE** | Trade-off, product decision, or resolution requires choosing between alternatives the user should weigh in on | Invoke `AskUserQuestion` with the finding description and options. Do not type the question as conversational text. Block until CD answers. |
| **PRE-EXISTING** | Finding exists in code this work did not touch | No action — cite the file and explain why it's out of scope |
| **PRE-DELIVERABLE-SPLIT** | Real finding requiring action, but scope is too large or decision-heavy for the current cycle | File as a future-deliverable candidate (D-suffix) with all options preserved. In-cycle work may include foundational pieces; the heavy lift is deferred. |

**Use only these six classifications.** If a finding doesn't fit, use DECIDE.

## Which Classifications Apply Where

Not every skill uses all six. The superset is defined here; each skill uses the subset appropriate to its context.

| Skill Context | Available Classifications | Notes |
|--------------|-------------------------|-------|
| Execution (sdlc-execute, sdlc-lite-execute) | FIX, PLAN, INVESTIGATE, DECIDE, PRE-EXISTING, PRE-DELIVERABLE-SPLIT | Full set — execution can surface systemic issues |
| Team review-fix (team-review-fix) | FIX, INVESTIGATE, DECIDE, PRE-EXISTING, PRE-DELIVERABLE-SPLIT | No PLAN — but PRE-DELIVERABLE-SPLIT handles scope escalation |
| Post-commit fix (review-fix) | FIX, INVESTIGATE, DECIDE, PRE-EXISTING | No PLAN or PRE-DELIVERABLE-SPLIT — commit fixes are scoped to the current diff |
| Planning review (sdlc-plan, sdlc-lite-plan) | FIX, DECIDE, PRE-EXISTING | No PLAN, INVESTIGATE, or PRE-DELIVERABLE-SPLIT — planning triage is simpler |

## Rules

### Misclassification Guard
Before dispatching FIX findings, scan each one. If you are about to type a question to the user about a FIX finding, STOP — that finding is DECIDE, not FIX. Reclassify it and invoke `AskUserQuestion`. A FIX finding must have a clear corrective action that does not require choosing between alternatives.

### PRE-EXISTING Qualification
A finding qualifies as PRE-EXISTING **only if** the finding's file is not in the plan's Files list AND was not created or modified by an agent during this work. If the file appears in the Files list, or if an agent touched it during this execution, any finding about that file is in scope — regardless of whether the finding is about the specific function that was modified.

### No Invented Classifications
Do not invent new classification types (STALE, DUPLICATE, INTENTIONAL, WONTFIX, or any other). If a finding doesn't fit the six canonical classifications, it's DECIDE.

### PRE-DELIVERABLE-SPLIT Guidelines
Use when:
- The fix requires a CD UX decision the cycle doesn't have time to gather
- The fix introduces a new abstraction or subsystem (cross-package, schema-changing, service-introducing)
- The fix's scope expanded mid-execution beyond what was originally tasked
- The fix needs full SDLC planning (sdlc-plan or sdlc-lite-plan)

Do NOT use when:
- The fix is fully scoped but large — that's still FIX, just multi-task
- The fix needs CD input on direction but is otherwise scoped — that's DECIDE

Architect/team-lead responsibilities for PRE-DELIVERABLE-SPLIT:
1. Capture all candidate options (with architect-side preference if applicable)
2. Preserve evidence + context so the follow-up deliverable can resume without re-discovery
3. Note the finder + relevant reviewers in metadata so they can be looped into the follow-up
4. Surface in the final report under "Future Deliverables" with proposed D-number

### Low-Severity In-Scope Findings (Planning Context)
If a finding is in scope but has no actionable correction (e.g., purely informational, already consistent with the plan), classify it as FIX with a rationale of "acknowledged, no revision needed." It still gets a row in the table. Do not create a new classification for it.

### FIX Failure Escalation
If a FIX fails twice (agent dispatched, finding persists), reclassify as INVESTIGATE or PLAN. Do not keep dispatching the same fix.

## Severity Levels (FIX Findings Only)

| Severity | Meaning |
|----------|---------|
| **critical** | Changes the approach, adds or removes files, or changes a phase/agent assignment |
| **major** | In-scope quality issue that doesn't change scope |
| **minor** | Style, polish, or low-impact correction |
