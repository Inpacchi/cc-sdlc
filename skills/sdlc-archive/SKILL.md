---
name: sdlc-archive
description: >
  Archive completed deliverables and resolved idea briefs from `docs/current_work/` to
  `docs/chronicle/`. Only deliverables in the Complete state are eligible — verify `**Status:**`
  marker before moving. Idea briefs, bug reports, handoffs, and lite deliverables are also handled.
  Use when a deliverable is complete or an idea brief is resolved and needs to move from active work to the chronicle.
  Triggers on "let's organize the chronicles", "archive completed deliverables",
  "move to chronicle", "archive deliverable", "/sdlc-archive".
  Do NOT use for deliverables still In Progress or Validated — they stay in current_work until Complete.
  Do NOT use for restructuring or deleting chronicle entries — archive is one-way.
---

# Archive Completed Deliverables

Move completed work from `docs/current_work/` to `docs/chronicle/`. Follows the process defined in `[sdlc-root]/process/chronicle_organization.md`. Only deliverables in the **Complete** state (per `[sdlc-root]/process/deliverable_lifecycle.md`) are eligible for archival — verify the `**Status:**` marker before proceeding. Idea briefs, bug reports, handoffs, and lite deliverables are also handled.

## Steps

### 1. Comprehensive Inventory

Perform a single exhaustive scan across ALL artifact types in `docs/current_work/`. Do not split this into multiple passes — scan everything at once.

#### Artifact types to scan:

| Type | Location pattern | What makes it complete |
|------|-----------------|----------------------|
| **Full deliverable** | `docs/current_work/{specs,planning,results}/dNN_*` | Has spec + plan + result files |
| **Lite deliverable** | `docs/current_work/sdlc-lite/dNN_*_result.md` | Result file exists |
| **Idea brief** | `docs/current_work/ideas/*_idea-brief.md` | Any state (triage in step 3) |
| **Bug report** | `docs/current_work/ideas/*_bug-report.md` | Any state (triage in step 3) |
| **Handoff** | `docs/current_work/ideas/*_handoff.md` | Any state (triage in step 3) |
| **Ad hoc result** | `docs/current_work/results/adhoc_*` | Result file exists |

For EACH artifact found:
1. Read its content and frontmatter (status field, problem statement, outcome)
2. Check its entry in `docs/_index.md` — record the catalog status for cross-checking in step 2

If a type yields zero results for a given pattern, also try broader globs (e.g., `docs/current_work/ideas/*bug*`, `docs/current_work/ideas/*handoff*`) to catch naming variations.

### 2. Git History Verification

**Mandatory.** Do not skip this step or defer it to the user.

For every artifact found in step 1:

1. **Verify implementation commits exist:**
   ```bash
   git log --oneline --grep="DNN" --grep="dNN" -i
   ```
   Also search for the artifact's topic keywords if the ID search yields nothing.

2. **Cross-check catalog status against reality:**
   - Catalog says "In Progress" but result file exists → flag as **catalog inconsistency** (fix in step 6)
   - Catalog says "Complete" but no result file → flag as **premature status** (skip archival)
   - No catalog entry but artifact exists → flag as **missing catalog entry**

3. **Graduation detection for idea briefs:**
   - First check frontmatter `status: graduated` / `status: abandoned` / `status: active`
   - If no explicit status, search git log for commits whose messages reference the brief's topic, concept name, or recommended next steps
   - If a deliverable exists whose spec traces to the brief (shared concept, matching problem description), mark as graduated even without frontmatter

Record all findings — they feed directly into step 3 classification.

### 3. Classification

For each artifact, classify using this priority order: **frontmatter status → git history evidence → content analysis**.

| Classification | Criteria | Action |
|---------------|----------|--------|
| **Archive (deliverable)** | Complete full or lite deliverable with implementation commits | Move to concept chronicle |
| **Archive (graduated idea)** | Idea brief that led to a deliverable (linked by topic/ID) | Archive alongside the deliverable's concept |
| **Archive (resolved idea)** | Idea brief whose question was answered without needing a deliverable | Archive into best-fit concept chronicle |
| **Archive (resolved bug)** | Bug report that was fixed (commits exist, issue closed) | Archive into relevant concept chronicle |
| **Delete** | Stale bug reports with no follow-up, duplicate artifacts, resolved handoffs that have been fully acted on | Remove entirely |
| **Skip** | Active, recent, or in-progress work | Leave in place |

### 4. Single Approval Gate

**This is the ONLY AskUserQuestion in the entire flow.** Present one comprehensive table covering all artifact types and all proposed actions:

```
Archive & cleanup plan:

| Item | Type | Status Evidence | Target Concept | Action |
|------|------|----------------|----------------|--------|
| D12 — Auth Tokens | full deliverable | spec+plan+result, 8 commits | auth | Archive |
| D15 — Cache Layer | lite deliverable | result exists, 3 commits | performance | Archive |
| caching_idea-brief | idea (graduated → D15) | topic match to D15 | performance | Archive with D15 |
| notification_idea-brief | idea (resolved) | question answered in D12 result | auth | Archive |
| stale_bug-report | bug report | fixed in commit abc123 | — | Delete |
| api_handoff | handoff | fully acted on | — | Delete |
| D18 — New Feature | full deliverable | no result file yet | — | Skip |
```

If catalog inconsistencies were found in step 2, append a **Catalog Fixes** section:

```
Catalog fixes needed:

| Item | Current Status | Actual Status | Fix |
|------|---------------|---------------|-----|
| D14 | In Progress | Complete (result exists) | Update to Complete |
| D19 | — | Active (spec exists) | Add missing entry |
```

Use AskUserQuestion to confirm. If the user adjusts mappings or actions, apply their changes.

### 5. Archive Deliverables

For each approved deliverable (both full AND lite):

1. **Create concept directory** if it doesn't exist:
   ```
   docs/chronicle/{concept_name}/specs/
   docs/chronicle/{concept_name}/planning/
   docs/chronicle/{concept_name}/results/
   ```

2. **Copy files** to the concept chronicle:
   - Full deliverables: `docs/current_work/{type}/` → `docs/chronicle/{concept_name}/{type}/`
   - Lite deliverables: `docs/current_work/sdlc-lite/dNN_*_result.md` → `docs/chronicle/{concept_name}/results/`
   - If a lite deliverable has an associated plan or spec in `docs/current_work/sdlc-lite/`, copy those to the matching subdirectory

3. **Update or create `_index.md`** in the concept directory with:
   - Overview of the concept
   - Deliverables table listing all files with purpose and dependencies
   - Key decisions from the spec/result

4. **Remove archived files** from `docs/current_work/`

5. **Update `docs/_index.md`**:
   - Move the deliverable row from "Active Work" to "Completed & Archived"
   - Update its status to "Archived"
   - Add a link to the concept chronicle

### 6. Fix Catalog Inconsistencies

Apply all approved catalog fixes from the table in step 4:
- Update status markers in `docs/_index.md` to match reality
- Add missing catalog entries
- Correct any stale status fields

### 7. Archive Idea Briefs & Resolved Artifacts

For each approved idea brief, bug report, or handoff marked for archival:

1. **Create `ideas/` subdirectory** in the target concept chronicle if it doesn't exist:
   ```
   docs/chronicle/{concept_name}/ideas/
   ```

2. **Copy the file** from `docs/current_work/ideas/` to `docs/chronicle/{concept_name}/ideas/`

3. **Update `_index.md`** in the concept directory — add an "Exploration History" section (if not already present):
   ```markdown
   ## Exploration History

   | Brief | Seed | Outcome | Date |
   |-------|------|---------|------|
   | [filename.md] | [original seed from brief] | Graduated → DNN / Resolved / Abandoned | [explored date] |
   ```

4. **Remove the file** from `docs/current_work/ideas/`

### 8. Delete Approved Artifacts

Remove all artifacts marked for deletion in step 4. This includes stale bug reports, resolved handoffs, and duplicates.

### 9. Knowledge Hygiene

Archival is a natural triage checkpoint for parking lot entries generated during the work being archived. This is NOT discipline capture (no new insights are generated) — it closes the loop on entries that were captured during the original work sessions.

#### 9a. Scan Related Parking Lot Entries

For each deliverable being archived, read `[sdlc-root]/disciplines/*.md` and find parking lot entries tagged with that deliverable's ID (e.g., `[D05 — phase 2]`, `[D05 — planning]`).

For each idea brief being archived, scan for entries tagged with its context (e.g., `[idea: caching]`).

Collect all entries that are still marked `[NEEDS VALIDATION]`.

#### 9b. Check Idea Brief Insight Coverage

For each idea brief being archived, read its "Key Insights from Exploration" section. For each insight listed, check whether a corresponding parking lot entry exists.

Flag any insight that appears significant and reusable but has no parking lot entry.

#### 9c. Present Triage Table (only if needed)

**Skip this entire sub-step if no `[NEEDS VALIDATION]` entries exist AND all idea brief insights have coverage.** Do not use AskUserQuestion — apply reasonable defaults instead:

- Entries clearly validated by the archived work → promote to `[READY TO PROMOTE]`
- Entries not yet proven → mark `[DEFERRED]`
- Missing insight entries → capture with `[NEEDS VALIDATION]`

If more than 3 entries require judgment calls, present a brief summary and use AskUserQuestion. Otherwise, apply defaults and report what was done.

### 10. Clean Up Issues

If a deliverable had an associated issue file in `docs/current_work/issues/` and the deliverable is now archived, remove the issue file too.

### 11. Verify

List the archived files in their new locations and confirm nothing was left behind in `docs/current_work/` that should have been moved.

### 12. Commit

Commit with message format: `docs: archive DXX-DYY into chronicles`

Include artifact types in the message when relevant:
- `docs: archive DXX-DYY + idea briefs into chronicles`
- `docs: archive DXX-DYY + lite deliverables + idea briefs, fix catalog`

Ask for confirmation before committing.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Archive everything, skip categorization" | Each deliverable needs correct concept mapping. Wrong categorization breaks chronicle discoverability. |
| "This deliverable is obviously complete, skip the check" | Run git log verification. Catalog status lies — commits don't. |
| "I'll pick the concept category myself" | Present the table and use AskUserQuestion. The user decides categorization. |
| "This idea brief is old, just delete it" | Old briefs still contain exploration context. Archive them — don't discard. The thinking is valuable even if the idea was abandoned. |
| "I should run full discipline capture during archival" | Archival is housekeeping, not creative work. Knowledge hygiene triages existing entries — it does not generate new ones. |
| "No parking lot entries to triage, skip step 9" | Still check idea brief insights for missing coverage (step 9b). But if both 9a and 9b are clean, skip the triage table — don't fabricate work. |
| "I'll ask the user at each step" | ONE AskUserQuestion in step 4. After approval, execute autonomously. Knowledge hygiene gets a second gate only if >3 ambiguous entries exist. |
| "Lite deliverables go through the same path as full" | Lite deliverables may only have a result file — don't fail on missing spec/plan. Archive what exists. |
| "Bug reports should always be archived" | Stale, duplicate, or fully-resolved bug reports can be deleted. Only archive bugs with valuable diagnostic context. |

## Integration
- **Depends on:** `docs/current_work/` (source of completed deliverables, lite deliverables, idea briefs, bug reports, handoffs), `docs/_index.md` (catalog), `[sdlc-root]/disciplines/*.md` (parking lot entries for knowledge hygiene)
- **Fed by:** `sdlc-status` (identifies archivable work), `sdlc-reconcile` (catalogs ad hoc work first), `sdlc-idea` (produces idea briefs)
- **Updates:** `docs/_index.md`, `docs/chronicle/`, `[sdlc-root]/disciplines/*.md` (triage markers)
