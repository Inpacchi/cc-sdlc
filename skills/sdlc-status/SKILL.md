---
name: sdlc-status
description: >
  Show project SDLC status — active deliverables, blocked items, and recent archives.
  Read-only: scans catalog and current_work/, makes no changes.
  Triggers on "SDLC status", "show project status", "what are we working on",
  "deliverable dashboard", "show deliverables", "/sdlc-status".
  Do NOT use for resuming a specific deliverable — use sdlc-resume.
  Do NOT use for compliance or health audits — use sdlc-audit.
---

# SDLC Status Dashboard

Scan the project's SDLC artifacts and present a status summary. This is read-only — take no actions, modify no files.

## Steps

1. **Read `docs/_index.md`** to get the deliverable catalog and next ID.

2. **Scan `docs/current_work/`** subdirectories:
   - `specs/` — list all spec files
   - `planning/` — list all plan files
   - `results/` — list all result files
   - `issues/` — list all issue/blocker files

3. **Determine each deliverable's stage** by cross-referencing which artifacts exist:

   | Has Spec | Has Plan | Has Result | Stage |
   |----------|----------|------------|-------|
   | yes | no | no | **Spec written** — needs CD approval, then planning |
   | yes | yes | no | **Plan ready** — awaiting execution |
   | yes | yes | yes | **Complete** — ready to archive |

   If a matching issue file exists in `issues/`, mark it **Blocked** regardless of other artifacts.

4. **Scan recent chronicles** — list the 5 most recently modified `_index.md` files under `docs/chronicle/`.

5. **Present the dashboard:**

```
## Active Deliverables

| ID | Name | Stage | Next Action |
|----|------|-------|-------------|
| D1 | ... | Complete | Archive via "Let's organize the chronicles" |
| D2 | ... | Plan ready | Execute via sdlc-execute |

## Blocked Items

- [issue filename]: brief description from first line

## Recent Archives

- concept-name: brief description

## Stats

- Next deliverable ID: D__
- Active: N | Blocked: N | Complete (unarchived): N
```

Do NOT suggest or take any follow-up actions. Just present the status.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll suggest archiving while showing status" | This skill is read-only. Present the data. Do not take or suggest actions. |
| "I'll fix the catalog while I'm reading it" | Display only. If the catalog has issues, the user decides what to do about them. |

## Integration
- **Depends on:** `docs/_index.md`, `docs/current_work/` (reads current state)
- **Precedes:** `sdlc-resume` (user may want to resume after seeing status)
- **Display only:** Do NOT invoke any other skill from here
