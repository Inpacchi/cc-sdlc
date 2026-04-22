---
name: sdlc-resume
description: >
  Resume work on an active deliverable — loads context (spec, plan, prior results) and suggests
  the next action based on deliverable state.
  Triggers on "resume a deliverable", "pick up where we left off", "continue D[N]",
  "what's in progress", "resume work", "/sdlc-resume".
  Do NOT use for starting new deliverables — use sdlc-plan or sdlc-lite-plan.
  Do NOT use for project-wide status without resuming anything — use sdlc-status.
---

# SDLC Resume

Pick up where you left off on an active deliverable.

## Steps

1. **Scan `docs/current_work/`** for all deliverables by collecting unique deliverable IDs from filenames across `specs/`, `planning/`, `results/`, and `issues/`.

2. **Determine each deliverable's stage:**

   | Has Spec | Has Plan | Has Result | Has Issue | Stage |
   |----------|----------|------------|-----------|-------|
   | yes | no | no | no | **Spec written** |
   | yes | yes | no | no | **Plan ready** |
   | yes | yes | yes | no | **Complete** |
   | any | any | any | yes | **Blocked** |

3. **Present numbered list and ask the user to pick one:**

```
Active deliverables:

1. D1 — User Authentication [Complete]
2. D2 — Search Integration [Plan ready]
3. (blocked) D3 — Example Feature [Blocked: reason]

Which deliverable do you want to resume? (number)
```

   Use the AskUserQuestion tool to get their selection.

4. **Load context for the selected deliverable.** Read the most advanced artifact:
   - If result exists -> read the result file
   - Else if plan exists -> read the plan file
   - Else if spec exists -> read the spec file
   - If an issue file exists -> also read it

5. **Suggest the next action based on stage:**

   | Stage | Suggested Action |
   |-------|-----------------|
   | Spec written | "Spec needs CD approval, then planning. To start planning, say: **invoke sdlc-plan**" |
   | Plan ready | "Plan is approved and ready. To execute, say: **Execute the plan at docs/current_work/planning/dNN_name_plan.md**" |
   | Complete | "Work is done. To archive, say: **Let's organize the chronicles**" |
   | Blocked | "This deliverable is blocked. Here's the issue:" then show the issue content |

Present the loaded artifact summary (title, key sections) and the suggested action. Let the user decide what to do next.

## Integration
- **Depends on:** `docs/current_work/` (scans for in-progress deliverables), `docs/_index.md` (catalog)
- **Routes to:** `sdlc-plan` (if spec/plan stage), `sdlc-execute` (if plan approved), `sdlc-archive` (if complete)

## Red Flags

| Thought | Reality |
|---------|---------|
| "Just pick the most recent deliverable" | Present the list and let the user choose. They know what they want to resume. |
| "Skip reading the artifact, I remember the context" | Always read the most advanced artifact. Prior conversation context may be stale or compressed. |
| "The stage is obvious, skip the assessment" | Cross-reference which artifacts exist. A missing plan file changes the suggested action. |

## Failure Guards
- If `docs/current_work/` is empty or missing, tell the user and suggest `sdlc-plan` or `sdlc-status`
- If stage shows "Complete", remind the user that archiving is still pending via `sdlc-archive`
