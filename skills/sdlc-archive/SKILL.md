---
name: sdlc-archive
description: Archive completed deliverables from current_work/ to chronicle/. Use when: "Let's organize the chronicles", "archive completed deliverables", "move to chronicle", "archive deliverable"
---

# Archive Completed Deliverables

Move completed work from `docs/current_work/` to `docs/chronicle/`. Follows the process defined in `ops/sdlc/process/chronicle_organization.md`. Only deliverables in the **Complete** state (per `ops/sdlc/process/deliverable_lifecycle.md`) are eligible for archival — verify the `**Status:**` marker before proceeding.

## Steps

### 1. Inventory

Scan `docs/current_work/` across all subdirectories (specs, planning, results). Identify deliverables that are **Complete** — meaning they have a spec, plan, AND result file.

Skip any deliverable that:
- Is missing a result file (still in progress)
- Has a matching issue file in `issues/` (blocked)

### 2. Categorize

**Gate:** Do not proceed to step 3 without explicit user approval via AskUserQuestion.

For each complete deliverable, determine which concept chronicle it belongs to by reading the spec's problem statement and the existing concepts in `docs/chronicle/`.

Present a categorization table and ask for approval:

```
Ready to archive:

| Deliverable | Target Concept | Action |
|-------------|---------------|--------|
| D1 — User Authentication | auth | Extend existing |
| D2 — Search Integration | search | Extend existing |

Proceed? (yes / adjust)
```

Use AskUserQuestion to confirm. If the user adjusts mappings, apply their changes.

### 3. Archive

For each approved deliverable:

1. **Create concept directory** if it doesn't exist:
   ```
   docs/chronicle/{concept_name}/specs/
   docs/chronicle/{concept_name}/planning/
   docs/chronicle/{concept_name}/results/
   ```

2. **Copy files** from `docs/current_work/{type}/` to `docs/chronicle/{concept_name}/{type}/`

3. **Update or create `_index.md`** in the concept directory with:
   - Overview of the concept
   - Deliverables table listing all files with purpose and dependencies
   - Key decisions from the spec/result

4. **Remove archived files** from `docs/current_work/`

5. **Update `docs/_index.md`**:
   - Move the deliverable row from "Active Work" to "Completed & Archived"
   - Update its status to "Archived"
   - Add a link to the concept chronicle

### 4. Clean up issues

If a deliverable had an associated issue file in `docs/current_work/issues/` and the deliverable is now archived, remove the issue file too.

### 5. Verify

List the archived files in their new locations and confirm nothing was left behind in `docs/current_work/`.

### 6. Commit

Commit with message: `docs: archive DXX-DYY into chronicles`

Ask for confirmation before committing.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Archive everything, skip categorization" | Each deliverable needs correct concept mapping. Wrong categorization breaks chronicle discoverability. |
| "This deliverable is obviously complete, skip the check" | Verify spec + plan + result all exist. Missing artifacts mean in-progress work. |
| "I'll pick the concept category myself" | Present the table and use AskUserQuestion. The user decides categorization. |

## Integration
- **Depends on:** `docs/current_work/` (source of completed deliverables), `docs/_index.md` (catalog)
- **Fed by:** `sdlc-status` (identifies archivable work), `sdlc-reconcile` (catalogs ad hoc work first)
- **Updates:** `docs/_index.md`, `docs/chronicle/`
