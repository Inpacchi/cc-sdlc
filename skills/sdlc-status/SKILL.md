---
name: sdlc-status
description: >
  Show project SDLC status — active deliverables, blocked items, and recent archives.
  Read-only: scans catalog and current_work/, makes no changes.
  Use when you need a quick read-only overview of active deliverables and project state.
  Triggers on "SDLC status", "show project status", "what are we working on",
  "deliverable dashboard", "show deliverables", "/sdlc-status".
  Do NOT use for compliance or health audits — use sdlc-audit.
---

# SDLC Status Dashboard

Scan the project's SDLC artifacts and present a status summary. This is read-only — take no actions, modify no files.

<!-- MIRROR-START: headless-mode.md#headless-stop-rule -->
**Headless runs (no person present).** This run is headless if the caller's prompt or appended system prompt has a line starting `SDLC headless mode:`, or if no ask-the-user tool (`AskUserQuestion`, or the harness's equivalent such as OpenCode's `question`) can be used — none is available or loadable, or a call to it is denied without an answer. A dispatched subagent is never headless itself; in a headless run the orchestrator tells each subagent so, and the limits below bind it too. In a headless run, every point in this skill that asks CD something the next step depends on, waits for CD's approval, or escalates to CD **stops the run there**: save the work so far, return the questions, the document or action plan awaiting approval, or the open-findings table as the run's result (in the caller's output schema if it passed one), and end the turn normally — a stop is a result, not an error. A missing precondition the caller must fix ends the run with status `failed` and the reason. Never guess an answer, take a default for a decision CD owns, approve your own work, or skip the gate. List questions the next step does not depend on in the result instead of stopping. Take the no path on optional offers. Cause no side effect outside the working tree — no push, post, comment, label, publish, external send, or live-system change — unless the caller's prompt names it; list those actions in the result. Reads are fine. A question the prompt or thread already answers is not a gate. Full rule and result format: `[sdlc-root]/process/headless-mode.md`.
<!-- MIRROR-END: headless-mode.md#headless-stop-rule -->

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
**{N} active, {N} blocked, {N} ready to execute.** Next ID: D__.

## Active Deliverables

| ID | Name | Stage | Next Action |
|----|------|-------|-------------|
| D1 | ... | Complete | Archive via "Let's organize the chronicles" |
| D2 | ... | Plan ready | Execute via sdlc-execute |

## Blocked Items ({N})

- [issue filename]: brief description from first line

## Recent Archives ({N})

- concept-name: brief description
```

Do NOT suggest or take any follow-up actions beyond what appears in the Next Action column. Present the status.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll suggest archiving while showing status" | This skill is read-only. Present the data. Do not take or suggest actions. |
| "I'll fix the catalog while I'm reading it" | Display only. If the catalog has issues, the user decides what to do about them. |

## Integration
- **Depends on:** `docs/_index.md`, `docs/current_work/` (reads current state)
- **Display only:** Do NOT invoke any other skill from here
