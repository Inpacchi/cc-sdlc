# DNN Split: [Parent Name]

**Parent:** DNN — [name] ([link to the parent's spec, if any])
**Why it splits:** [1-3 plain sentences: what the Feasibility Gate found, or which phases pushed the plan past seven]
**Status:** Proposed | Approved

> CD approves the split here (in a pull request, by merging it). Edit the parts table before approving to change the split: the merged table is what gets registered. Process: `[sdlc-root]/process/deliverable_lifecycle.md` § Splitting a Deliverable.

## Parts

| Part | Name | Tier | Depends on | Spec | Scope |
|------|------|------|------------|------|-------|
| DNNa | [name] | lite | — | — | [what this part delivers, one or two sentences] |
| DNNb | [name] | full | DNNa | [path to the parent's approved spec this part reuses, or —] | [scope] |

- **Part:** the parent's ID plus a letter, in execution order.
- **Tier:** `lite` (`sdlc-lite-plan`) or `full` (`sdlc-plan`, spec then plan).
- **Depends on:** parts or other deliverables that must be Complete first, comma-separated, or `—`.
- **Spec:** a full-tier part may reuse an approved spec (usually the parent's) when it covers the part's scope. Its plan then covers only the part. `—` means the part gets its own spec.

## Order and next actions

[Which part goes first and why. Every part has a next action: planned next, or held until a named part is Complete.]

## What stays with the parent

[Anything the parent's spec covers that no part takes on, and why; or "nothing".]
