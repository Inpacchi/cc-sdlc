---
name: sdlc-reconcile
description: >
  Reconcile untracked ad hoc work back into the SDLC process. Trigger when the user says
  "Let's catalog our ad hoc work", "Let's catch up the docs", "What have we done since D[last]?",
  "Let's rejoin the process", "Reconcile our recent work", or any similar phrase indicating
  they want to bring informal commits back into the tracked process. Do NOT trigger for
  compliance audits — those use the sdlc-compliance-auditor agent.
---

# SDLC Reconciliation

Read `ops/sdlc/process/ad_hoc_reconciliation.md` and follow it exactly.

The process has 5 phases:
1. **Discovery** — identify the boundary (last formal commit), list ad hoc commits, categorize each
2. **Reconciliation** — for each commit, pick the right resolution: absorb into parent / lightweight record / batch polish deliverable / skip
3. **Spec Maintenance** — identify any specs that need updating based on what was learned
4. **Git State** — ensure clean state before resuming
5. **Path Forward** — ask the user what comes next (formal process / continue ad hoc / chronicle and pause)

Do not skip the categorization step. Every commit gets classified before a resolution is chosen.

## Cleanup

After reconciliation is complete, check `docs/current_work/sdlc-lite/completed/` for archived plan files. Apply this logic automatically — no need to ask:

- **Delete** if the work was absorbed into a deliverable, batched into a polish deliverable, or classified as trivial
- **Keep** if the plan documents a non-obvious approach decision that isn't captured in a spec, result doc, or commit message — it stays until the next chronicle pass

## Red Flags

| Thought | Reality |
|---------|---------|
| "Mark all of these as trivial" | Each commit must be individually categorized. Bulk classification hides substantial work. |
| "Skip categorization, just assign deliverable IDs" | Categorization determines the right resolution. Wrong category leads to wrong resolution. |
| "These are all related, batch them into one deliverable" | Related commits may still warrant separate resolutions. Categorize individually first. |
| "Skip spec maintenance, the specs are fine" | Ad hoc work often reveals spec gaps. Check every spec that touches the same domain. |

## Failure Guards
- If `ops/sdlc/process/ad_hoc_reconciliation.md` does not exist, stop and alert the user
- If `docs/_index.md` is missing or the Next ID field is absent, stop and alert the user
- Do NOT bulk-classify commits as trivial — each commit must be individually categorized

## Integration
- **Depends on:** `ops/sdlc/process/ad_hoc_reconciliation.md` (process definition), `docs/_index.md` (catalog + next ID)
- **Fed by:** `sdlc-status` (user sees untracked work and decides to reconcile)
- **Feeds into:** `sdlc-plan` (if reconciliation surfaces work needing a deliverable), `sdlc-archive` (if reconciled deliverables are complete)
