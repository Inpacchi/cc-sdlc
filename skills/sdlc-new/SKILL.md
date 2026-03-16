---
name: sdlc-new
description: Start a new deliverable — assigns ID, creates catalog entry, invokes planning. Use when: "start a new deliverable", "new feature", "register a deliverable", "create deliverable", "new D-number"
---

# Start New Deliverable

Handles the bookkeeping for a new deliverable, then hands off to the planning skill.

## Steps

1. **Read `docs/_index.md`** to find the next deliverable ID (listed in the header as "Next ID: **DNN**").

2. **Ask the user for a deliverable name** using AskUserQuestion:
   > Starting deliverable **DNN**. What's the name? (e.g., "User Authentication", "Payment Integration")

3. **Create the catalog entry.** Edit `docs/_index.md` to:
   - Add a new row to the Active Work table with the ID, name, and status "Draft"
   - Increment the "Next ID" counter in the header

   Example row:
   ```
   | D3 | Tournament Bracket System | Draft | | | |
   ```

4. **Confirm and hand off:**
   > Deliverable **DNN — Name** is registered. Invoking planning.

   Then invoke the `sdlc-planning` skill to begin the spec and plan workflow. Pass the deliverable ID and name as context.

Do NOT create any spec, plan, or result files — the planning skill handles artifact creation.

## Integration
- **Depends on:** `docs/_index.md` (next ID counter)
- **Feeds into:** `sdlc-planning` (invoked after catalog entry is created)
- **Do NOT:** Create spec, plan, or result files — `sdlc-planning` handles that

## Red Flags

| Thought | Reality |
|---------|---------|
| "Skip the catalog entry, just start planning" | The catalog entry is the source of truth for deliverable IDs. Skipping it causes ID collisions. |
| "I'll create the spec file too, save a step" | Spec creation belongs to `sdlc-planning`. This skill does bookkeeping only. |

## Failure Guards
- If `docs/_index.md` is missing or the Next ID field is absent, stop and alert the user
- Do NOT create spec, plan, or result files — `sdlc-planning` handles that
