---
name: sdlc-archive
description: Archive completed deliverables and resolved idea briefs from current_work/ to chronicle/. Use when: "Let's organize the chronicles", "archive completed deliverables", "move to chronicle", "archive deliverable"
---

# Archive Completed Deliverables

Move completed work from `docs/current_work/` to `docs/chronicle/`. Follows the process defined in `ops/sdlc/process/chronicle_organization.md`. Only deliverables in the **Complete** state (per `ops/sdlc/process/deliverable_lifecycle.md`) are eligible for archival — verify the `**Status:**` marker before proceeding. Idea briefs that have graduated to deliverables or been abandoned are also archived.

## Steps

### 1. Inventory Deliverables

Scan `docs/current_work/` across all subdirectories (specs, planning, results). Identify deliverables that are **Complete** — meaning they have a spec, plan, AND result file.

Skip any deliverable that:
- Is missing a result file (still in progress)
- Has a matching issue file in `issues/` (blocked)

### 2. Inventory Idea Briefs

Scan `docs/current_work/ideas/` for idea brief files. For each brief, classify its state:

Idea briefs have YAML frontmatter with a `status` field. Check frontmatter first, then fall back to content-based detection:

| State | How to detect | Action |
|-------|--------------|--------|
| **Graduated** | Frontmatter `status: graduated`, OR a deliverable exists whose spec traces to this idea (shared concept, matching problem description, or the brief's "Recommended Next Step" was followed) | Archive alongside the deliverable's concept chronicle |
| **Abandoned/Stale** | Frontmatter `status: abandoned`, OR no deliverable emerged and the brief is old (check git log for creation date — >30 days with no follow-up activity) OR the user confirms it's dead | Archive into the best-fit concept chronicle |
| **Still active** | Frontmatter `status: active`, OR user is actively exploring, or the brief is recent with no deliverable yet | Skip — leave in `current_work/ideas/` |

If classification is ambiguous, include the brief in the categorization table (Step 3) and let the user decide.

### 3. Categorize

**Gate:** Do not proceed to step 4 without explicit user approval via AskUserQuestion.

For each complete deliverable, determine which concept chronicle it belongs to by reading the spec's problem statement and the existing concepts in `docs/chronicle/`.

For each archivable idea brief, determine which concept chronicle it best fits by reading the brief's problem understanding and direction.

Present a combined categorization table and ask for approval:

```
Ready to archive:

| Item | Type | Target Concept | Action |
|------|------|---------------|--------|
| D1 — User Authentication | deliverable | auth | Extend existing |
| D2 — Search Integration | deliverable | search | Extend existing |
| caching_idea-brief | idea (graduated → D2) | search | Archive with D2 |
| notification_idea-brief | idea (abandoned) | messaging | New concept |

Proceed? (yes / adjust)
```

Use AskUserQuestion to confirm. If the user adjusts mappings, apply their changes.

### 4. Archive Deliverables

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

### 5. Archive Idea Briefs

For each approved idea brief:

1. **Create `ideas/` subdirectory** in the target concept chronicle if it doesn't exist:
   ```
   docs/chronicle/{concept_name}/ideas/
   ```

2. **Copy the brief** from `docs/current_work/ideas/` to `docs/chronicle/{concept_name}/ideas/`

3. **Update `_index.md`** in the concept directory — add an "Exploration History" section (if not already present) with a table for idea briefs:
   ```markdown
   ## Exploration History

   | Brief | Seed | Outcome | Date |
   |-------|------|---------|------|
   | [filename.md] | [original seed from brief] | Graduated → DNN / Abandoned | [explored date] |
   ```

   This section sits below the Deliverables table and above Common Tasks. It is separate from the deliverables table — idea briefs are context, not deliverables.

4. **Remove the brief** from `docs/current_work/ideas/`

### 6. Knowledge Hygiene

Archival is a natural triage checkpoint for parking lot entries generated during the work being archived. This is NOT discipline capture (no new insights are generated) — it closes the loop on entries that were captured during the original work sessions.

#### 6a. Scan Related Parking Lot Entries

For each deliverable being archived, scan `ops/sdlc/disciplines/*.md` for parking lot entries tagged with that deliverable's ID (e.g., `[D05 — phase 2]`, `[D05 — planning]`).

For each idea brief being archived, scan for entries tagged with its context (e.g., `[idea: caching]`).

Collect all entries that are still marked `[NEEDS VALIDATION]`.

#### 6b. Check Idea Brief Insight Coverage

For each idea brief being archived, read its "Key Insights from Exploration" section. For each insight listed, check whether a corresponding parking lot entry exists (the `sdlc-idea` skill runs discipline capture at crystallization, but coverage may be incomplete).

Flag any insight that appears significant and reusable but has no parking lot entry.

#### 6c. Present Triage Table

If any entries need triage or insights lack coverage, present a table:

```
Knowledge hygiene — entries related to archived work:

| # | Entry/Insight | Source | Current State | Suggested Action |
|---|--------------|--------|---------------|-----------------|
| 1 | React StrictMode double-mount gotcha | [D05 — phase 2] coding | [NEEDS VALIDATION] | Promote to knowledge |
| 2 | Queue retry needs idempotency keys | [idea: notifications] architecture | [NEEDS VALIDATION] | Defer — not yet proven |
| 3 | Auth token refresh race condition | D07 idea brief insight | No parking lot entry | Capture to coding |

Actions: promote / defer / discard / capture (for missing entries)
```

Use AskUserQuestion to confirm. Apply the user's decisions:
- **Promote** → Change marker to `[READY TO PROMOTE]`
- **Defer** → Change marker to `[DEFERRED]` with reason
- **Discard** → Remove the entry
- **Capture** → Write a new parking lot entry with `[NEEDS VALIDATION]` marker

**Skip this step entirely** if no `[NEEDS VALIDATION]` entries exist for the archived work and all idea brief insights have coverage. Do not fabricate triage work.

### 7. Clean Up Issues

If a deliverable had an associated issue file in `docs/current_work/issues/` and the deliverable is now archived, remove the issue file too.

### 8. Verify

List the archived files in their new locations and confirm nothing was left behind in `docs/current_work/`.

### 9. Commit

Commit with message: `docs: archive DXX-DYY into chronicles`

If idea briefs were archived, include them: `docs: archive DXX-DYY + idea briefs into chronicles`

Ask for confirmation before committing.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Archive everything, skip categorization" | Each deliverable needs correct concept mapping. Wrong categorization breaks chronicle discoverability. |
| "This deliverable is obviously complete, skip the check" | Verify spec + plan + result all exist. Missing artifacts mean in-progress work. |
| "I'll pick the concept category myself" | Present the table and use AskUserQuestion. The user decides categorization. |
| "This idea brief is old, just delete it" | Old briefs still contain exploration context. Archive them — don't discard. The thinking is valuable even if the idea was abandoned. |
| "I should run full discipline capture during archival" | Archival is housekeeping, not creative work. Knowledge hygiene triages existing entries — it does not generate new ones. |
| "No parking lot entries to triage, skip step 6" | Still check idea brief insights for missing coverage (step 6b). But if both 6a and 6b are clean, skip the triage table — don't fabricate work. |

## Integration
- **Depends on:** `docs/current_work/` (source of completed deliverables and idea briefs), `docs/_index.md` (catalog), `ops/sdlc/disciplines/*.md` (parking lot entries for knowledge hygiene)
- **Fed by:** `sdlc-status` (identifies archivable work), `sdlc-reconcile` (catalogs ad hoc work first), `sdlc-idea` (produces idea briefs)
- **Updates:** `docs/_index.md`, `docs/chronicle/`, `ops/sdlc/disciplines/*.md` (triage markers)
