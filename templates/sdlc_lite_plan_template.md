# SDLC-Lite Plan: [Title]

**Execute this plan using the `sdlc-lite-execute` skill.**

**Scope:** [1-2 sentences — what's changing and why]
**Files:** [List all files that will be created or modified]
**Agents:** [List assigned worker domain agents]

## Approval Brief

> For CD, who approves the plan from this section. Written last, after review, by the plan's author: the plan variant of `[sdlc-root]/templates/pr_description_template.md`, in about 450 words (`[sdlc-root]/process/writing-for-cd.md` § Approval Briefs). Every decision this plan leaves to CD appears under What you're approving. Execution follows the sections below, not this one.

### The problem
### What changes for users
### What you're approving
### Scope
### Risk
### Review focus
### How it will be verified
### How it works
### Learn the change

**Review:** [N] rounds; [K] open minor findings, listed at the end of this plan.

## Phase Dependencies

| Phase | Depends On | Agent | Can Parallel With |
|-------|-----------|-------|-------------------|
| 1     | —         | agent | —                 |
| 2     | Phase 1   | agent | Phase 3           |

Depends On may also name another deliverable (`Phase 5, D11a`): that phase waits until the deliverable is Complete. List the deliverable in the catalog row's `Depends on` too (`[sdlc-root]/process/deliverable_lifecycle.md` § Dependencies).

## Phases

### Phase 1: [Name]
**Agent:** [assigned agent]
**Outcome:** [What must be true when this phase is done]
**Why:** [Why it matters]
**Guidance:** [Optional — approach hints, key files/functions, non-obvious context that helps the executing agent]

### Phase 2: [Name]
...

## Spec Deviations

[List any intentional divergences from the spec. If the plan implements the spec exactly, write "None — plan matches spec." If the plan drops, adds, or modifies requirements, declare each deviation with a reason.]

- **[Deviation]**: [What changed from spec and why]

## Post-Execution Review
All completed work must be reviewed by all relevant worker domain agents.
All findings must be fixed by the most relevant domain agent.
Build must pass before work is considered done.
