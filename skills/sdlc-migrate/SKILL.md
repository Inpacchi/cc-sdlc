---
name: sdlc-migrate
description: >
  Migrate a project's cc-sdlc framework to the latest version — content-aware updates that preserve
  project-specific customizations (parking lots, agent names, build commands, maturity tracker) while
  updating framework sections (skills, knowledge, process docs, agents) to match the current cc-sdlc.
  Triggers on "migrate my SDLC", "update the SDLC", "migrate SDLC framework", "update SDLC framework",
  "upgrade SDLC", "sync SDLC with upstream".
  Do NOT use for first-time installation — use sdlc-initialize.
  Do NOT use when neither ops/sdlc/ nor .claude/sdlc/ exists — use sdlc-initialize.
---

# SDLC Migrate

Apply cc-sdlc upstream updates to a project while preserving project-specific customizations. Unlike the initial installation (which copies files and skips modified ones), this skill is **content-aware** — it understands which sections are framework-level vs project-customized and updates them independently.

**Argument:** `$ARGUMENTS` (optional — local path to a cc-sdlc clone. If omitted, resolve via `.sdlc-manifest.json` → `source_repo`, or ask user.)

## Source Repo Access Rule

**All reads from the cc-sdlc source repo MUST use git commands**, not filesystem reads. This ensures you're reading committed state, not the working tree.

- Read a file: `git -C [cc-sdlc-path] show HEAD:<path>`
- List files: `git -C [cc-sdlc-path] ls-tree -r --name-only HEAD`
- Diff since version: `git -C [cc-sdlc-path] diff [source_version]..HEAD`

Never use `cat`, `cp`, `ls`, or direct file reads against `[cc-sdlc-path]`. The source repo may have uncommitted work in progress.

### Safe File Extraction (CRITICAL)

**Never use direct shell redirection** to extract files: `git show HEAD:<path> > file` is UNSAFE because shell redirection truncates the target file *before* `git show` runs. If `git show` fails for any reason (path doesn't exist, clone was cleaned up, permission error), the target file is left empty — destroying the project's content.

**Safe pattern — verify before overwriting:**
```bash
# Extract to temp, verify content exists, then move
CONTENT=$(git -C [cc-sdlc-path] show HEAD:<path> 2>/dev/null) || {
  echo "ERROR: git show failed for <path> — file NOT overwritten"
  return 1  # or continue to next file
}
if [ -z "$CONTENT" ]; then
  echo "ERROR: <path> has empty content in source — file NOT overwritten"
  return 1
fi
echo "$CONTENT" > [project-path]/[target]
```

**Alternative — use git archive for batch extraction:**
```bash
# Extract specific files to a temp directory, then move
git -C [cc-sdlc-path] archive HEAD:<dir> | tar -x -C /tmp/extract/
# Verify each file before copying to project
```

**Why this matters:** During migration, a single silent `git show` failure can destroy dozens of project files. The neuroloom migration bug (2026-04-15) emptied 8 knowledge READMEs because `git show` produced no output after the temp clone was cleaned up — the shell redirect created empty files over the project's content.

## Pre-Flight Check

Before starting, verify this is a migration (not initialization):

If neither `ops/sdlc/` nor `.claude/sdlc/` exists → tell user to run `sdlc-initialize` instead and stop.

**Step 1 — Resolve cc-sdlc source to a local path** (in priority order):
1. `$ARGUMENTS` — if the user passed a local clone path, verify with `git -C [path] rev-parse HEAD`
2. `.sdlc-manifest.json` → `source_repo` field (git remote URL) — **clone it immediately:**
   ```bash
   git clone --depth=1 [source_repo] /tmp/cc-sdlc-migrate
   ```
   This is safe and expected — it's a shallow clone of the user's own repo. Use `/tmp/cc-sdlc-migrate` as `[cc-sdlc-path]` for all subsequent phases. Clean up with `rm -rf /tmp/cc-sdlc-migrate` after migration completes.
3. If neither is available, ask the user.

**Step 2 — Detect project structure:**

The cc-sdlc source uses canonical paths (`knowledge/`, `disciplines/`, `process/`). Projects install these to different locations. Detect the project's structure before applying any changes.

| Signal | Detection | Result |
|--------|-----------|--------|
| **SDLC directory** | `[ -d ops/sdlc ]` vs `[ -d .claude/sdlc ]` | Set `[sdlc-root]` to whichever exists (if both exist, prefer `ops/sdlc` and warn user) |
| **Neuroloom integration** | `[ -d neuroloom-sdlc-plugin ]` OR `[ -d neuroloom-claude-plugin ]` OR `grep -q "neuroloom" .claude/settings.json` OR manifest has `neuroloom_integration: true` | Set `[has-neuroloom]` flag |

```bash
# Detect SDLC root
if [ -d ops/sdlc ] && [ -d .claude/sdlc ]; then
  SDLC_ROOT="ops/sdlc"
  echo "WARNING: Both ops/sdlc and .claude/sdlc exist. Using ops/sdlc. Consider consolidating."
elif [ -d ops/sdlc ]; then
  SDLC_ROOT="ops/sdlc"
elif [ -d .claude/sdlc ]; then
  SDLC_ROOT=".claude/sdlc"
else
  echo "No SDLC directory found — use sdlc-initialize"
  exit 1
fi

# Detect Neuroloom integration
HAS_NEUROLOOM=false
[ -d neuroloom-sdlc-plugin ] && HAS_NEUROLOOM=true
[ -d neuroloom-claude-plugin ] && HAS_NEUROLOOM=true
grep -q '"neuroloom"' .claude/settings.json 2>/dev/null && HAS_NEUROLOOM=true
jq -e '.neuroloom_integration == true' .sdlc-manifest.json 2>/dev/null && HAS_NEUROLOOM=true
```

**Step 3 — Report assessment:**

```
MIGRATION ASSESSMENT
SDLC root: [sdlc-root] (ops/sdlc or .claude/sdlc)
Neuroloom integration: [yes/no]
Has .sdlc-manifest.json: [yes/no]
Has .claude/agents/: [yes/no]
Has .claude/skills/: [yes/no]
cc-sdlc source: [local path or "cloned from [URL] to /tmp/cc-sdlc-migrate"]
cc-sdlc HEAD: [commit hash from git -C [cc-sdlc-path] rev-parse HEAD]
```

---

## Path Transformation Rules

Throughout this migration, apply these transformations when copying or merging content:

### Source → Project Path Mapping

| cc-sdlc Source Path | Project Path |
|---------------------|--------------|
| `knowledge/` | `[sdlc-root]/knowledge/` |
| `disciplines/` | `[sdlc-root]/disciplines/` |
| `process/` | `[sdlc-root]/process/` |
| `templates/*.md` | `[sdlc-root]/templates/*.md` |
| `playbooks/` | `[sdlc-root]/playbooks/` |
| `examples/` | `[sdlc-root]/examples/` |
| `agents/` | `.claude/agents/` (always — Claude Code requires this location) |
| `skills/` | `.claude/skills/` (always — Claude Code requires this location) |

**Not installed to child projects:**
- `templates/optional/` — Conditional CLAUDE.md appendices (e.g., `data-pipeline-integrity.md`). Read from cc-sdlc source during initialization when needed, not installed.
- `CLAUDE-SDLC.md` — Content is merged into the project's `CLAUDE.md` during initialization. No separate file is maintained.

### Project-Specific Files (Never Overwrite)

Some files in the cc-sdlc source are **templates** that become project-specific after initialization. These must NOT be direct-copied during migration:

| File | Reason |
|------|--------|
| `process/agent-selection.yaml` | Project's agent roster and dispatch rules — contains project-specific agent names |
| `knowledge/agent-context-map.yaml` | Project's agent-to-knowledge mappings — already protected in §3.3 |
| `knowledge/provenance_log.md` | Project's knowledge provenance records — append-only log of ingestions and research handoffs |

Framework files may contain canonical agent names (e.g., `frontend-developer`) in examples. These are illustrative — they don't affect dispatch behavior. The project's actual agents in `.claude/agents/` and `agent-context-map.yaml` define what gets dispatched.

### Neuroloom-Aware Content Transformation

When `[has-neuroloom]` is true, **preserve MCP tool calls** in framework content. The cc-sdlc source uses file path references (generic), but Neuroloom projects use MCP tools for knowledge access.

#### Pattern Mapping

| cc-sdlc Generic Pattern | Neuroloom Pattern (preserve if present) |
|-------------------------|----------------------------------------|
| `consult [sdlc-root]/knowledge/agent-context-map.yaml` | `memory_search(query="[agent-name] domain-specific patterns...", tags=["sdlc:knowledge"])` |
| `Read [sdlc-root]/knowledge/architecture/agent-communication-protocol.yaml` | `memory_search(query="agent communication protocol...", tags=["sdlc:knowledge", "sdlc:domain:architecture"])` |
| `Append to [sdlc-root]/disciplines/*.md` | `memory_store(tags=["sdlc:discipline:{name}", "sdlc:parking-lot"])` |
| `knowledge stores ([sdlc-root]/knowledge/)` | `Neuroloom knowledge store (via memory_store)` |
| `[sdlc-root]/knowledge/testing/` | `memory_store with tags ["sdlc:knowledge", "sdlc:domain:testing"]` |
| `look up agent's mapped files from agent-context-map.yaml` | `memory_search(query="{agent-name} domain patterns", tags=["sdlc:knowledge"])` |

#### Files Containing These Patterns

These framework files contain knowledge access patterns that differ between generic cc-sdlc and Neuroloom:

| File | Section | Pattern Type |
|------|---------|--------------|
| `agents/AGENT_TEMPLATE.md` | `## Knowledge Context` | Agent knowledge retrieval |
| `agents/AGENT_TEMPLATE.md` | `## Communication Protocol` | Protocol retrieval |
| `agents/AGENT_TEMPLATE.md` | "Surfacing Learnings" | Knowledge store reference |
| `agents/sdlc-compliance-auditor.md` | Methodology reference | Knowledge retrieval |
| `agents/sdlc-reviewer.md` | Agent wiring checklist | Knowledge wiring validation |
| `process/discipline_capture.md` | Agent knowledge lookup | Knowledge retrieval |
| `process/discipline_capture.md` | "How to Capture" | Discipline store |
| `process/overview.md` | Knowledge capture | Knowledge store |

#### Content-Merge Rules for Neuroloom Projects

1. **Detection heuristic:** Before merging any file listed above, scan the project's current version for `memory_search(` or `memory_store(`. If present, the project uses Neuroloom integration.

2. **Section-level preservation:** When merging a file with Neuroloom patterns:
   - Identify sections containing MCP tool calls (usually delimited by `##` headings)
   - Extract the project's MCP-based version of those sections
   - Apply upstream framework updates to sections WITHOUT MCP calls
   - Re-inject the project's MCP-based sections verbatim
   - Log: `Neuroloom pattern preserved: [file] § [section]`

3. **Per-file detection for partial Neuroloom:** Even when `[has-neuroloom]` is true at the project level, apply detection at file level before merging. Scan the project's current version of each file in the "Files Containing These Patterns" table for `memory_search(` or `memory_store(`. If present, apply content-merge preservation for that file. If absent, direct-copy is safe. This handles projects that migrated to Neuroloom piecemeal — some files may have MCP patterns while others still use file paths.

4. **Reviewer checklist transformation:** The `sdlc-reviewer.md` contains checklists that validate knowledge wiring. For Neuroloom projects:
   - Preserve: `Knowledge Context section includes a memory_search call`
   - Don't overwrite with: `Knowledge Context section references agent-context-map.yaml`

5. **Agent template sections:** The `AGENT_TEMPLATE.md` drives new agent creation. For Neuroloom projects:
   - Preserve: `call memory_search(query="[agent-name] domain-specific patterns...`
   - Don't overwrite with: `consult [sdlc-root]/knowledge/agent-context-map.yaml`

**Why this matters:** Neuroloom projects store SDLC knowledge in the Neuroloom memory graph, accessed via MCP tools. Overwriting these with file path references breaks:
- Semantic search (queries by meaning, not file membership)
- Cross-domain discovery (relevant knowledge from unexpected domains)
- Context injection (Neuroloom plugin injects memories into agent context)

The migration must preserve whichever pattern the project uses.

---

## Phase 1: Detect What Changed

### 1.1 Identify Source Version

Read the project's `.sdlc-manifest.json` to get:
- `source_repo` — the git remote URL for the cc-sdlc repo (used to clone if no local path given)
- `source_version` — the commit hash from the last install/migration

Then check what changed in cc-sdlc since that commit (using git, not filesystem):

```bash
git -C [cc-sdlc-path] log --oneline [source_version]..HEAD
git -C [cc-sdlc-path] diff --name-only [source_version]..HEAD
```

If `source_version` is `"unknown"` or missing, treat this as a **full migration** — compare all framework files against the project. Do not stop or ask the user — a full migration is the correct fallback.

### 1.2 Changelog Review Gate

**Before categorizing or applying anything**, read the changelog entries since the project's source version.

Read `process/sdlc_changelog.md` from the cc-sdlc source repo (via `git -C [cc-sdlc-path] show HEAD:process/sdlc_changelog.md`), stopping when you reach entries older than the project's `source_version` date. This is the migration's release notes — it surfaces:

- **Breaking changes** — renamed concepts, moved files, added structural markers, changed conventions
- **New capabilities** — new knowledge files, new disciplines, new agent roles the project may want
- **Human-judgment items** — changes where the project team should decide (e.g., "do you want the new BA discipline wired to an agent?")

**Gate rule:** If any changelog entry describes a breaking change or convention rename, note it for the CLAUDE-SDLC.md compatibility check in §4.3a. If any entry describes a new capability that requires project-team input (new agent roles, new discipline areas), flag it for user review before applying.

Present a brief migration summary to the user via `AskUserQuestion`:

```
Migration summary: [source_version] → [HEAD]
- N commits, M changelog entries
- Breaking changes: [list or "none"]
- New capabilities: [list or "none"]
- Items needing your input: [list or "none"]
Proceed with migration?
```

**Gate:** Wait for user confirmation before continuing to Phase 2.

### 1.3 Categorize Changes

Group the changed cc-sdlc files by migration strategy:

| File Type | Location | Strategy |
|-----------|----------|----------|
| **Skills** | `skills/*/SKILL.md` | Content-merge: update framework sections, preserve project customizations |
| **Agent template** | `agents/AGENT_TEMPLATE.md` | Direct copy (no project customizations) |
| **Agent suggestions** | `agents/AGENT_SUGGESTIONS.md` | Direct copy (no project customizations) |
| **Audit skill** | `skills/sdlc-audit/SKILL.md` + `references/` | Content-merge: update audit methodology, preserve project-specific additions |
| **Knowledge YAMLs** | `knowledge/**/*.yaml` | Key-level merge: add new upstream keys, preserve project additions (§2.1b). Check for moved/deleted files (§2.1a) |
| **Process docs** | `process/*.md` | Direct copy (framework-level) |
| **Disciplines** | `disciplines/*.md` | Content-merge: update framework guidance, preserve project parking lot entries |
| **Context map** | `knowledge/agent-context-map.yaml` | Never overwrite — project has its own agent names. Update paths for moved/deleted files (§3.3) |
| **Provenance log** | `knowledge/provenance_log.md` | Never overwrite — project's append-only ingestion/research records |
| **Project agents** | Project `.claude/agents/*.md` | Targeted section updates (see Phase 3) |
| **CLAUDE-SDLC.md** | `CLAUDE-SDLC.md` | Content-merge into project's `CLAUDE.md` (§2.1e). No separate file. |
| **Templates** | `templates/*.md` | Direct copy (framework-level). Skip `templates/optional/` (source-only). |

---

## PROJECT-SECTION Marker Convention

Read and follow `[sdlc-root]/process/project-section-markers.md` — the canonical definition of the marker convention. It defines the syntax (Markdown and YAML), label format, rules, and validation. Producing skills that add markers to process/skill files (`sdlc-create-agent`, `sdlc-develop-skill`, `sdlc-audit` improvement mode) reference that document. Note: markers are only for process docs and skill files — knowledge files, discipline files, and agent-context-map are project-specific and don't need markers.

This migration skill is responsible for **consuming** markers: extracting, preserving, and re-injecting marked blocks during framework updates. Existing project content that lacks markers is detected by the deviation detection step (§2.1c).

---

## Phase 2: Apply Framework Updates

### 2.1 Direct Copy Files

For files with no project customizations, copy directly from cc-sdlc to the project's `[sdlc-root]/` directory:

- `process/*.md` (framework process docs — `agent-selection.yaml` is NOT copied; it's project-specific, see "Project-Specific Files")
- `knowledge/**/*.yaml` (but NOT `agent-context-map.yaml`) — **Neuroloom projects:** skip this; knowledge files are stored in the memory graph and updated via the Neuroloom plugin's migrate skill
- `knowledge/README.md` (to `[sdlc-root]/knowledge/`) — NOT `knowledge/provenance_log.md`; that's project-specific (see "Project-Specific Files")
- `README.md` (to `[sdlc-root]/`)
- `agents/AGENT_TEMPLATE.md`, `agents/AGENT_SUGGESTIONS.md` → `.claude/agents/` — **Neuroloom projects:** apply content-merge rules from "Neuroloom-Aware Content Transformation" section above; these files contain Knowledge Context patterns that differ between generic and Neuroloom projects
- `agents/sdlc-reviewer.md`, `agents/sdlc-compliance-auditor.md` → `.claude/agents/` — **Neuroloom projects:** apply content-merge rules; these contain knowledge wiring validation patterns. (Framework subagents must be in `.claude/agents/` for Claude Code to dispatch them, not just `[sdlc-root]/agents/`)
- `playbooks/*.md` (unless the project has written its own playbooks — check git blame)
- `examples/*.md`
- `templates/*.md` (to `[sdlc-root]/templates/`)

**Not direct-copied:**
- `templates/optional/` — Conditional CLAUDE.md appendices. Read from cc-sdlc source during initialization when needed, not installed.
- `CLAUDE-SDLC.md` — See §2.1e for CLAUDE-SDLC.md handling (merge into CLAUDE.md, not a separate file).

**All reads from the cc-sdlc source repo must use git commands** (e.g., `git -C [cc-sdlc-path] show HEAD:path/to/file`), not filesystem reads. This ensures you're reading committed state, not working tree.

**PROJECT-SECTION preservation with content review (mandatory for all direct-copy files):**

Before overwriting any file:
1. Scan the project's current version for `PROJECT-SECTION-START` / `PROJECT-SECTION-END` marker pairs
2. Extract each marked block along with its label and the heading it appears under (nearest `#`/`##`/`###` above)
3. **Review each marked block against upstream changes** (see §2.1d below)
4. After copying the upstream file, re-inject each block at its original heading position (unless user chose to update/remove during review)
5. If the heading no longer exists in the upstream file, append the block at the end of the file with a warning comment: `<!-- MIGRATION WARNING: heading "[heading]" no longer exists in upstream — block preserved at end of file -->`
6. Log all re-injected blocks and review decisions in the migration report

### 2.1d PROJECT-SECTION Content Review

Markers preserve project content, but that content can become stale, conflicting, or improvable as upstream evolves. Before blindly re-injecting, review each marked block against upstream changes.

**For each extracted `PROJECT-SECTION` block:**

1. **Identify the surrounding context:**
   - Which section heading is it under?
   - What was the upstream content in that section at `source_version`?
   - What is the upstream content in that section at `HEAD`?

2. **Detect upstream changes to the same area:**
   ```bash
   # Get the section content at old version
   git -C [cc-sdlc-path] show [source_version]:<path> | ... extract section ...
   
   # Get the section content at new version
   git -C [cc-sdlc-path] show HEAD:<path> | ... extract section ...
   
   # Compare
   diff <(old_section) <(new_section)
   ```

3. **Classify the marker review finding:**

   | Upstream Change | Project Marker Status | Finding Type | Recommendation |
   |-----------------|----------------------|--------------|----------------|
   | Section unchanged | Any | `OK` | Re-inject as-is |
   | Section updated (minor) | Content still valid | `OK` | Re-inject as-is |
   | Section updated (significant) | Content may be stale | `REVIEW` | Present to user — content may need updating |
   | Section restructured | Block position unclear | `REVIEW` | Present to user — may need repositioning |
   | Section removed | Block orphaned | `ORPHAN` | Present to user — content has no home |
   | New patterns added nearby | Could benefit project | `OPPORTUNITY` | Present to user — may want to adopt |
   | Project content contradicts upstream | Conflict detected | `CONFLICT` | Present to user — resolve contradiction |

4. **Build the review findings list** — collect all non-`OK` findings across all files

5. **Present findings to user via `AskUserQuestion`:**

   ```
   PROJECT-SECTION CONTENT REVIEW
   ══════════════════════════════
   
   Found [N] marked blocks that may need attention:
   
   ┌─ [file path] ─────────────────────────────────
   │ Label: [marker label]
   │ Section: [heading]
   │ Finding: [REVIEW | ORPHAN | OPPORTUNITY | CONFLICT]
   │
   │ Upstream change:
   │   [brief description of what changed in upstream]
   │
   │ Project content:
   │   [first 3-5 lines of marked block, truncated if long]
   │
   │ Recommendation:
   │   [specific suggestion based on finding type]
   └────────────────────────────────────────────────
   
   [Repeat for each finding]
   
   For each finding, choose:
   1. Keep as-is — re-inject project content unchanged
   2. Update — [opens content for manual edit, then re-inject]
   3. Remove — discard this marked block, adopt upstream
   4. Merge — combine project additions with upstream changes
   
   Enter choices (e.g., "1:keep, 2:update, 3:remove" or "all:keep"):
   ```

6. **Apply user decisions:**
   - `keep` → re-inject block verbatim after upstream copy
   - `update` → user edits the block content, then re-inject
   - `remove` → do not re-inject; block is discarded
   - `merge` → combine project content with upstream changes (present merged result for confirmation)

7. **Log all decisions in migration report:**
   ```
   PROJECT-SECTION review decisions:
   - [file]#[label]: kept (upstream section unchanged)
   - [file]#[label]: kept (user chose to preserve despite upstream changes)
   - [file]#[label]: updated (user modified content to align with upstream)
   - [file]#[label]: removed (user adopted upstream version)
   - [file]#[label]: merged (combined project + upstream)
   ```

**Finding type details:**

| Type | Detection | User Prompt |
|------|-----------|-------------|
| `REVIEW` | Upstream section diff > 20% changed lines, or key patterns added/removed | "Upstream significantly updated this section. Your marked content may reference outdated patterns or miss improvements." |
| `ORPHAN` | Upstream removed the heading entirely | "The section this content lived under no longer exists. Consider: moving to a new location, removing if obsolete, or keeping at file end." |
| `OPPORTUNITY` | Upstream added new content within 10 lines of marker position | "Upstream added new guidance near your marked content. Review whether to incorporate or reference it." |
| `CONFLICT` | Project content contains patterns explicitly superseded in upstream changelog | "Your marked content uses [pattern] which upstream replaced with [new pattern]. Consider updating." |

**When to skip review:**

- If `source_version` is unknown (first migration after legacy install), skip review — no baseline to compare against
- If the block label starts with `deviation-` (wrapped by previous migration), always flag for review — these are temporary preservations that should be re-evaluated
- If the block is < 7 days old (parse date from label), skip review — too recent to be stale

**Why this matters:** Markers protect project content from being overwritten, but they don't protect it from becoming stale. A discipline capture from 6 months ago may reference patterns that upstream has since improved. An agent wiring entry may use outdated dispatcher logic. Blind re-injection preserves content but also preserves technical debt. This review step ensures markers serve their purpose (preserving project work) without becoming a mechanism for accumulating outdated customizations.

**Ensure `.claude/agent-memory/` is gitignored.** Agent memories are not source-controlled — check the project's `.gitignore` for the entry. If missing, append:

```
# Agent memory — private scratchpad, not source-controlled
# Reusable learnings flow through knowledge_feedback → discipline capture → knowledge stores
.claude/agent-memory/
```

If the project was previously committing agent memory files, note this in the migration report. The files can remain in the working tree but should not be committed going forward. If agent memory files are currently tracked by git, unstage them:

```bash
git rm -r --cached .claude/agent-memory/ 2>/dev/null
```

### 2.1a Remove Deleted and Moved Files

Check the cc-sdlc changelog for files that were **deleted, moved, or renamed** since the project's `source_version`. These require explicit cleanup in the downstream project — direct copy only adds files, it doesn't remove stale ones.

**Process:**

1. From the diff in Phase 1.1, identify any files that were deleted or moved:
   ```bash
   git -C [cc-sdlc-path] diff --name-status [source_version]..HEAD | grep -E '^[DR]'
   ```

2. For each deleted file: remove it from the downstream project's `[sdlc-root]/` directory.

3. For each moved/renamed file: the new location was already copied in §2.1. Remove the old location. Then check whether the project's `agent-context-map.yaml` references the old path — if so, update the path (see §3.3).

4. **Scan agent memory files for stale paths (if they exist locally).** Agent memory files (`.claude/agent-memory/*.md`) are not git-tracked but may exist locally and contain hardcoded knowledge file paths that bypass the context map. For each deleted or moved file path, grep agent memories:
   ```bash
   grep -rl "old/path/to/file.yaml" .claude/agent-memory/ 2>/dev/null
   ```
   Update any matches to the new path, or remove references to deleted files.

5. Log all removals and path fixes so the migration report (Phase 4.6) includes them.

6. **Clean up legacy files no longer installed to child projects:**
   
   - **Standalone CLAUDE-SDLC.md:** If `[sdlc-root]/CLAUDE-SDLC.md` exists as a separate file, verify its content is already in `CLAUDE.md` (via §2.1e), then remove it:
     ```bash
     rm [sdlc-root]/CLAUDE-SDLC.md
     ```
   
   Log any removals in the migration report.

**Why this matters:** Without cleanup, downstream projects accumulate orphan files. Worse, if a file was moved (e.g., `knowledge/architecture/foo.yaml` → `knowledge/coding/foo.yaml`), agents mapped to the old path load a stale copy while the updated version sits unwired at the new path. Agent memories are a second source of path references that §3.3 (context map) doesn't cover — they must be scanned separately.

### 2.1b Knowledge YAML Key-Level Merge

Knowledge YAML files contain domain patterns that projects naturally extend with project-specific additions. Unlike framework logic files, knowledge is additive — projects add their own patterns alongside upstream patterns. Direct-copy would destroy these additions.

**Merge strategy:**

- **New upstream keys** → add to project file
- **Existing project keys** → preserve project version (may be intentionally customized)
- **Project-only keys** → preserved automatically (no markers needed)
- **`spec_relevant` field** → special handling (see below)

**Process for each knowledge YAML:**

1. **New file (doesn't exist in project):** Copy from upstream as-is.

2. **Existing file:** Perform key-level merge:
   ```
   For each top-level key in upstream:
     If key doesn't exist in project → add it
     If key exists in project → keep project version, flag if upstream differs
   Project-only keys → keep (these are project additions)
   ```

3. **`spec_relevant` handling:**
   - Project `true` + upstream `false` → keep project's `true` (project override)
   - Project `false` + upstream `true` → keep project's `false`, flag for review:
     ```
     Knowledge spec_relevant upstream upgrade: [file] — upstream now marks as spec-relevant. Review whether to adopt.
     ```
   - Missing in project → copy from upstream

4. **Flag merge conflicts** in migration report when upstream updated a key the project also has:
   ```
   Knowledge merge conflicts (review recommended):
   - [file]: upstream updated `[key]`, project version kept
   ```
   This ensures projects are aware of upstream improvements without silently overwriting their customizations.

**First migration introducing `spec_relevant`:** If no knowledge file in the project has `spec_relevant` at all (the field didn't exist before this migration), all files will receive `spec_relevant: false` from upstream. After Phase 4 completes, prompt CD to review which stores should be tagged `true` for this project — same walkthrough as `sdlc-initialize` Phase 6d:

1. List all knowledge YAMLs grouped by discipline with their `name` and `description`
2. Mark commonly spec-relevant stores with `*` (see `knowledge/README.md` § "spec_relevant Field" for examples)
3. CD selects which to tag `true`; update the files
4. If CD skips, all files stay `false` and `sdlc-plan` filtering remains dormant (backward compatible)

**Why merge-only:** Knowledge YAMLs capture domain patterns — both framework patterns (upstream) and project-specific patterns (local additions like custom enum mappings, project conventions, incident learnings). Direct-copy destroys project knowledge; key-level merge preserves both sources.

### 2.1c Deviation Detection

Before direct-copying any file, detect whether the project has made custom changes outside existing `PROJECT-SECTION` markers:

**Process:**

1. Read the project's current version of the file
2. Read the previous upstream version (at `source_version` commit): `git -C [cc-sdlc-path] show [source_version]:<path>`
3. Diff the project's version against the previous upstream version
4. Identify changes that are:
   - **Inside markers** — already protected, will be preserved automatically (§2.1 marker preservation)
   - **Outside markers** — project customizations that will be lost on overwrite

5. If the project modified content outside existing markers, present the customizations via `AskUserQuestion`:

```
DEVIATION DETECTED: [file path]

The project has customized this framework file outside of any PROJECT-SECTION markers.
These changes will be lost when the upstream version is copied.

Customized sections:
  [heading or line range]: [brief description of what changed]
  [heading or line range]: [brief description of what changed]

Options:
1. Wrap customizations in markers — preserve this and future migrations
2. Overwrite — accept upstream version, discard customizations
3. Skip — don't update this file
```

6. If the user chooses option 1: wrap each customized section in `<!-- PROJECT-SECTION-START: deviation-YYYY-MM-DD-label -->` markers before applying the upstream copy, then proceed with marker-preserving copy
7. If option 2: direct copy as normal
8. If option 3: skip this file, log in migration report

**Why this matters:** Without deviation detection, `sdlc-migrate` silently destroys intentional project-specific changes. Users invest time customizing business suite content, discipline captures, and agent wiring — a migration that discards that work without warning erodes trust in the framework.

### 2.1e CLAUDE-SDLC.md Merge

**CLAUDE-SDLC.md is not maintained as a separate file in child projects.** Its content lives directly in the project's `CLAUDE.md`. During migration, update the SDLC sections in `CLAUDE.md` rather than copying a separate file.

**Process:**

1. **Read the upstream CLAUDE-SDLC.md** content via git:
   ```bash
   git -C [cc-sdlc-path] show HEAD:CLAUDE-SDLC.md
   ```

2. **Identify the SDLC section boundaries** in the project's `CLAUDE.md`:
   - Look for markers like `# CC-SDLC` or the characteristic SDLC headings (`## SDLC Skills`, `## Knowledge Stores`, etc.)
   - If the project uses `<!-- SDLC-START -->` / `<!-- SDLC-END -->` markers, use those as boundaries

3. **Compare and update:**
   - Diff the project's SDLC sections against the upstream CLAUDE-SDLC.md
   - Apply framework updates (new skills, changed workflow rules, updated paths)
   - Preserve project-specific customizations within the SDLC sections (custom agent names, project-specific instructions)

4. **Clean up stale separate file:** If `[sdlc-root]/CLAUDE-SDLC.md` exists as a separate file (legacy from older installations), delete it after verifying its content is already in `CLAUDE.md`:
   ```bash
   rm [sdlc-root]/CLAUDE-SDLC.md
   ```

**Why this matters:** Maintaining CLAUDE-SDLC.md as a separate file creates confusion — users must remember to read two files, and updates to the separate file don't automatically propagate to what Claude Code actually sees. Merging into CLAUDE.md keeps everything in one place.

### 2.2 Content-Merge: Skills

Skills have two layers:
1. **Framework structure** — dispatch patterns, gate logic, manager rules, cross-domain injection
2. **Project customizations** — build commands, agent names, project-specific examples, tech stack references

**Migration process for each skill:**

1. Read the cc-sdlc source version of the skill
2. Read the project's version of the skill
3. Identify framework-level changes (new sections, updated dispatch logic, added/removed gates)
4. Apply those changes while preserving:
   - Project-specific build commands (e.g., `pnpm build` vs `[build command]`)
   - Project-specific agent names in tables and examples
   - Project-specific examples and terminology
   - Project-specific health check URLs and test commands
   - `[PLUGIN: ...]` guards that have been resolved to direct invocations

**Verbatim rule:** Framework content must be copied verbatim from the cc-sdlc source — do not summarize, rephrase, condense, or rewrite in your own words. The source text is the canonical version. When merging, replace the project's framework sections with the exact cc-sdlc text, then re-apply project-specific values (build commands, agent names, etc.) into the appropriate placeholders. If a framework section contains `[build command]` or similar placeholders, substitute the project's actual values — but do not rephrase the surrounding framework text.

**Key rule:** If a section exists in cc-sdlc but not in the project, add it. If a section was removed from cc-sdlc, remove it from the project. If a section was modified in cc-sdlc, update the framework logic while keeping project-specific values.

**PROJECT-SECTION preservation with review:** If `PROJECT-SECTION` blocks exist within a skill being content-merged, apply the §2.1d content review process. Present findings to user before re-injection. These blocks contain project-specific content (e.g., dispatcher table entries added by `sdlc-create-agent`, custom modifications from `sdlc-develop-skill`) that survive migration — but may need updating if upstream changed the surrounding framework patterns.

### 2.3 Content-Merge: Disciplines

Discipline files have:
1. **Framework structure** — status line, knowledge store reference, summary, mutation verification rules, level definitions (in process-improvement.md only)
2. **Project additions** — parking lot entries (with triage markers), active questions, project context sections
3. **Project-assessed data** — the Process Maturity Tracker in `process-improvement.md` (levels reflect the downstream project's state, not the source repo's)

**Migration process:**
1. Update framework sections to match cc-sdlc — **verbatim, not rephrased**
2. Preserve all parking lot entries with their triage markers (these are project-specific knowledge)
3. Preserve active questions
4. Preserve project context sections (added by `sdlc-initialize` Phase 7)
5. Add any new seeded insights from cc-sdlc that the project doesn't have — but do NOT overwrite triage markers on existing entries (the project may have triaged differently than the source repo)
6. **Preserve project parking lot entries.** Discipline parking lot entries are project-specific — they don't have PROJECT-SECTION markers because discipline files are not overwritten during migration. Simply preserve all entries with their triage markers.
7. **Preserve the Process Maturity Tracker table as-is.** The tracker is delimited by `<!-- PROJECT-TRACKER-START -->` and `<!-- PROJECT-TRACKER-END -->` markers. Everything between these markers (including the table and last-updated note) reflects the project's assessed levels — never overwrite it. Update the framework sections *outside* the markers (level definitions, assessment procedure) to match cc-sdlc. If the downstream file lacks these markers, treat the entire `### Process Maturity Tracker` section through the next heading as project data and preserve it.

### 2.4 Content-Merge: Audit Skill

The `sdlc-audit` skill has framework audit methodology in `SKILL.md` and `references/` that must stay current:

1. Read the cc-sdlc source versions of all audit skill files
2. Read the project's versions
3. Update SKILL.md workflow, modes, and reference pointers — **verbatim from cc-sdlc source, not rephrased**
4. Update `references/compliance-methodology.md` audit dimensions and report format
5. Update `references/improvement-methodology.md` extraction patterns and categorization
6. Update `references/session-reading.md` JSONL format reference
7. Preserve any project-specific audit dimensions or improvement categories added by the project

**Migration note:** The `sdlc-compliance-auditor` agent has been restored as a subagent dispatched by `sdlc-audit`. If the project has an old version, update it to the current version. If the project removed it during a prior migration, re-install it.

### 2.5 Content-Merge Verification Gate

**Before proceeding to agent updates**, verify the content-merge results from §2.2–2.4 didn't corrupt project data. This catches merge errors before they propagate into agent wiring.

**Quick checks (< 2 minutes):**

1. **Tracker integrity** — read `[sdlc-root]/disciplines/process-improvement.md` and verify:
   - `<!-- PROJECT-TRACKER-START -->` / `<!-- PROJECT-TRACKER-END -->` markers are present
   - The table between markers contains the project's levels (not the cc-sdlc source repo's levels)
   - Level definitions outside the markers were updated to match cc-sdlc

2. **Parking lot preservation** — spot-check 2 discipline files:
   - Project-specific entries (dates, deliverable references) are still present
   - Triage markers (`[NEEDS VALIDATION]`, `[DEFERRED]`, `Promoted →`) were not overwritten
   - New seeded insights from cc-sdlc were added without disturbing existing entries

3. **Skill customization preservation** — spot-check 1 skill:
   - Project-specific build commands, agent names, and examples are intact
   - Framework sections were updated (compare against cc-sdlc source)

4. **Audit skill** — verify all reference files were updated and any project-specific audit dimensions preserved

**Gate rule:** If any check fails, fix the merge before continuing. Do not proceed to Phase 3 with corrupted content — agent wiring decisions depend on accurate discipline and knowledge state.

---

## Phase 3: Update Project Agents

Project agents are NOT framework files — they're project-specific. But some sections come from the framework template and should be updated when the template changes.

### 3.1 Identify Template-Derived Sections

These sections originate from the framework and should be updated across all project agents:

| Section | Source | Update Rule |
|---------|--------|-------------|
| `## Knowledge Context` | AGENT_TEMPLATE | Must exist in every agent. If missing, add it. If present, update to match template wording. |
| `## Communication Protocol` | AGENT_TEMPLATE | Update the canonical protocol reference. Preserve domain-specific handoff fields. |
| Memory section header/guidelines | AGENT_TEMPLATE | Update generic guidelines and "Surfacing Learnings to the SDLC" section. Preserve domain-specific "what to save" content. |

### 3.2 Apply Template Updates

For each agent in `.claude/agents/`:
1. Check if `## Knowledge Context` section exists — add if missing
2. Verify Communication Protocol references the correct source:
   - **Non-Neuroloom projects:** correct YAML path (`[sdlc-root]/knowledge/agent-communication-protocol.yaml`)
   - **Neuroloom projects:** `memory_search` with appropriate `sdlc:knowledge` tags
3. Verify memory section guidelines match the latest template
4. Do NOT touch: scope ownership, core principles, workflow, anti-rationalization tables, self-verification checklists, domain-specific content

### 3.3 Update Agent-Context-Map (if needed)

**Skip this section if `[has-neuroloom]` is true.** Neuroloom projects do not use `agent-context-map.yaml` — agents load context via `memory_search` with `sdlc:knowledge` tags. Knowledge wiring changes are handled by the Neuroloom plugin's own migrate skill.

**For non-Neuroloom projects:**

The agent-context-map is **never overwritten** because projects have their own agent names. But it must be updated for four scenarios:

**New knowledge files added to existing roles:** If cc-sdlc added new YAML files that are relevant to existing agents:
1. Read the project's `agent-context-map.yaml`
2. Read the cc-sdlc source's `agent-context-map.yaml` for the new mappings
3. Add new file paths to the project's existing agent entries (matching by role, not by exact name)

**New role entries:** If cc-sdlc added an entirely new role section to the agent-context-map (e.g., `business-analyst`):
1. Read the project's `agent-context-map.yaml`
2. Check if the project has an agent that matches the new role (by role name or responsibility — e.g., the project may use `ba-agent` instead of `business-analyst`)
3. If a matching agent exists: add the new role section using the project's agent name, with the cc-sdlc knowledge file paths
4. If no matching agent exists: add the role section as-is (the project can customize or remove it later)
5. Note the addition in the migration report so the project team can review the wiring

**Moved/renamed knowledge files:** If cc-sdlc moved a file from one directory to another (identified in §2.1a):
1. Search the project's `agent-context-map.yaml` for the old path
2. Replace with the new path
3. Verify the new path exists on disk

**Removed knowledge files:** If cc-sdlc deleted a knowledge file:
1. Search the project's `agent-context-map.yaml` for references to the deleted file
2. Remove those references
3. Note the removal in the migration report

Never remove project-specific mappings that aren't in the cc-sdlc source — those were added during initialization or by the project team.

### 3.4 Downstream Impact Analysis

New or updated knowledge files and process docs may conflict with or improve the child project's existing artifacts — skills, agents, discipline entries, and knowledge overrides. This step identifies those impacts so the project team can decide what to act on.

**When to run:** Only when the migration includes new or substantively changed knowledge files, discipline insights, or process docs (identified in §1.2/§1.3). Skip if the migration is purely structural (file moves, template updates, manifest changes).

**What to scan in the child project:**

| Child Artifact | Where | What to Check Against New Knowledge |
|----------------|-------|-------------------------------------|
| Skill descriptions | `.claude/skills/*/SKILL.md` frontmatter | Activation framing rules — flag advisory descriptions ("best practices", "guidance for") that should use mandatory framing |
| Skill bodies | `.claude/skills/*/SKILL.md` content | AVOID example safety — flag unguarded anti-pattern examples missing the correct-pattern pairing |
| Skill bodies | `.claude/skills/*/SKILL.md` content | Deterministic-first — flag procedural instructions (file scanning, API calls, pattern matching) that could be scripts |
| Agent definitions | `.claude/agents/*.md` | New knowledge wiring — do any agents work in domains covered by newly added knowledge files but aren't wired to them? |
| Discipline parking lots | `[sdlc-root]/disciplines/*.md` | Stale entries — do any `[NEEDS VALIDATION]` entries now have evidence from newly landed knowledge? |
| Project knowledge | `[sdlc-root]/knowledge/**/*.yaml` | Contradictions — do any project-specific knowledge rules conflict with newly landed upstream rules? |

**Process:**

1. **Read the changelog entries being applied** (from §1.2) to identify which new knowledge files and process changes are landing. Extract the key principles, rules, and patterns from each.

2. **Scan child skills:**
   - Glob `.claude/skills/*/SKILL.md`
   - For each skill, read the frontmatter `description` field and check activation framing
   - For each skill, grep for AVOID/DON'T/NEVER patterns without an adjacent correct-pattern ("Instead do", "DO this")
   - For each skill, grep for procedural instructions that describe step-by-step API calls, file reads, or pattern matching that could be a script
   - **Do not modify skills.** Collect findings.

3. **Scan child agents:**
   - Glob `.claude/agents/*.md` (excluding framework agents: `sdlc-reviewer.md`, `sdlc-compliance-auditor.md`, `AGENT_TEMPLATE.md`, `AGENT_SUGGESTIONS.md`)
   - For each agent, read its domain expertise description
   - Cross-reference against newly added knowledge files — if a new knowledge file covers a domain the agent works in but isn't in the agent's `## Knowledge Context` section, flag it
   - **Do not modify agents.** Collect findings.

4. **Scan discipline parking lots:**
   - Read each `[sdlc-root]/disciplines/*.md` parking lot
   - For each `[NEEDS VALIDATION]` entry, check if newly landed knowledge provides evidence that would change the triage marker (promote to knowledge, or mark as validated)
   - **Do not modify entries.** Collect findings.

5. **Scan project knowledge:**
   - Read each `[sdlc-root]/knowledge/**/*.yaml` that the project has customized (use `git diff HEAD -- [sdlc-root]/knowledge/` to identify project-modified files)
   - Compare project-added rules against newly landed upstream rules for contradictions
   - **Do not modify files.** Collect findings.

**Present findings via `AskUserQuestion`:**

```
DOWNSTREAM IMPACT ANALYSIS
═══════════════════════════════════════════════════════════════

New knowledge landing this migration:
  [list of new/changed knowledge files and their key principles]

SKILL FINDINGS ([count] skills scanned)
  Activation framing:
    [skill-name] — description uses advisory framing: "[current text]"
      → Suggest: "[mandatory reframing]"
  AVOID examples:
    [skill-name] — line N has unguarded anti-pattern
      → Suggest: pair with correct pattern
  Deterministic candidates:
    [skill-name] — §N describes procedural [API call/file scan] inline
      → Suggest: extract to scripts/ for consistency

AGENT FINDINGS ([count] agents scanned)
  Missing knowledge wiring:
    [agent-name] — works in [domain] but not wired to new [knowledge-file]
      → Suggest: add to agent-context-map.yaml

PARKING LOT FINDINGS
  Evidence available:
    [discipline] — "[entry title]" marked [NEEDS VALIDATION], new knowledge
    in [file] provides supporting evidence
      → Suggest: promote or update triage marker

KNOWLEDGE CONFLICTS
  [file] rule [id] conflicts with upstream [file] rule [id]: [description]
    → Suggest: reconcile — project rule may need updating

No findings in a category? Omit that category entirely.
Apply any of these? (list numbers, "all", or "skip")
```

**Gate rule:** User chooses which findings to apply. For each approved finding:
- Skill description reframing → edit the skill's frontmatter
- AVOID example fixes → edit the skill body
- Agent knowledge wiring → edit `agent-context-map.yaml`
- Parking lot triage updates → edit the discipline file
- Knowledge conflict resolution → edit the project knowledge file

Log all applied changes in the migration report (§4.6). Log all skipped findings too — they serve as tech debt awareness.

**Why this matters:** Without this step, new knowledge lands in `[sdlc-root]/knowledge/` but the project's existing skills and agents continue operating with stale assumptions. The knowledge is available but not applied. This step closes the gap between "framework updated" and "project benefits from the update."

---

## Phase 4: Verification

### 4.1 File Path Integrity

**For non-Neuroloom projects** (file-based knowledge layer):

```bash
# Verify all agent-context-map paths resolve
for path in $(grep -E '^\s+- ' [sdlc-root]/knowledge/agent-context-map.yaml | sed 's/.*- //'); do
  [ -f "$path" ] || echo "BROKEN: $path"
done
```

**For Neuroloom projects** (memory-based knowledge layer):

Skip this check — `agent-context-map.yaml` does not exist. Agents access knowledge via `memory_search` with appropriate `sdlc:knowledge` tags instead. Knowledge integrity is verified by the Neuroloom plugin's compliance checks.

### 4.2 Agent Consistency

```bash
# Verify all agents have Knowledge Context section
for agent in .claude/agents/*.md; do
  grep -q '## Knowledge Context' "$agent" || echo "MISSING Knowledge Context: $agent"
done
```

### 4.3 Skill Verification

Spot-check 2-3 skills to confirm:
- Framework sections updated correctly
- Project customizations preserved
- No orphaned references to removed framework features

### 4.3a CLAUDE-SDLC.md Compatibility Check

The project's `CLAUDE.md` contains CLAUDE-SDLC.md content — skill names, process file paths, conventions, and workflow rules. If the migration renamed a skill, changed a convention, or modified a path, the project's CLAUDE.md will have stale references.

**Check for:**

1. **Skill name references (guarded renames)** — verify all skill names mentioned in CLAUDE.md (`sdlc-plan`, `sdlc-execute`, `sdlc-lite-plan`, `sdlc-lite-execute`, `sdlc-idea`, `sdlc-initialize`, `sdlc-reconcile`, `sdlc-review-diff`, `sdlc-review-commit`, `sdlc-review-fix`, `sdlc-develop-skill`, `sdlc-create-agent`, `sdlc-review`) still match the actual skill directory names in `.claude/skills/`. Check for renamed skills: `diff-review` → `sdlc-review-diff`, `commit-review` → `sdlc-review-commit`, `commit-fix` → `sdlc-review-fix`, `sdlc-create-skill` → `sdlc-develop-skill`

   **Guarded rename rule:** Before renaming any skill reference in the project's CLAUDE.md or other files:
   1. Build the project's actual skill inventory: `ls .claude/skills/`
   2. Only rename if the target skill directory exists in the project
   3. If the target doesn't exist (e.g., the project hasn't received the new skill yet), log a warning instead of renaming:
      ```
      GUARDED RENAME SKIPPED: [old-name] → [new-name] — target directory does not exist in project
      ```
   This prevents renaming references to skills that don't exist in the project, which causes silent process failures.

2. **Process file paths** — verify paths like `[sdlc-root]/process/overview.md`, `[sdlc-root]/process/sdlc_changelog.md`, `[sdlc-root]/process/compliance_audit.md` still exist

3. **Convention changes** — if the changelog (§1.2) flagged breaking convention changes (renamed concepts, changed workflow rules), check whether the project's CLAUDE.md still uses the old terminology

4. **New sections in CLAUDE-SDLC.md** — compare the project's CLAUDE.md SDLC sections against the current `CLAUDE-SDLC.md` source. If new sections were added (e.g., new workflow rules, new verification policies), they should be merged into the project's CLAUDE.md

5. **Optional sections** — some SDLC sections are conditionally included based on project characteristics. Check if the project should have optional sections it doesn't currently have:

   | Optional Section | Detection Signals | Template |
   |-----------------|-------------------|----------|
   | Data Pipeline Integrity | `seeds/`, `scrapers/`, `etl/`, `pipelines/` dirs; `*seed*.{ts,js,py}`, `*scrape*.{ts,js,py}` files; allowlist/blocklist files | `templates/optional/data-pipeline-integrity.md` |
   
   If signals are detected but the section is missing from the project's CLAUDE.md, ask CD whether to add it.

**Gate rule:** If the project's CLAUDE.md references a renamed skill or removed path, fix it. Stale CLAUDE.md content causes silent process failures — Claude Code follows the instructions but they point nowhere.

### 4.4 Post-Migration Compliance Audit

**MANDATORY — do not skip.** Dispatch the `sdlc-compliance-auditor` subagent directly to verify migration integrity. Do not ask the user to invoke `/sdlc-audit` separately — dispatch the subagent yourself as part of this skill's execution.

**Dispatch prompt for the subagent:**

> Run a compliance audit focused on migration integrity. Check all 9 dimensions, with special attention to:
> - Dimension 7 (Migration Integrity): All framework files match the cc-sdlc source at [new commit hash]
> - No orphaned files from previous versions remain
> - Agent-context-map paths all resolve (skip for Neuroloom projects — they use memory_search instead)
> - Content-merge preserved project data (tracker levels, parking lot entries, skill customizations)
> - For Neuroloom projects: MCP tool calls (memory_search, memory_store) were preserved, not overwritten with file paths
> - CLAUDE-SDLC.md references in CLAUDE.md are valid
> - `agents/sdlc-compliance-auditor.md` is present and current
>
> **Context:** This audit runs immediately after migration applied changes. Uncommitted files in the working tree are expected — the user has not committed yet. Do NOT flag uncommitted migration files as findings.
> **Project type:** [non-Neuroloom | Neuroloom] (detected in pre-flight)

Present the subagent's findings to the user before proceeding to §4.5.

If the audit returns findings:
- **Critical/Major:** Fix before continuing. Re-dispatch the auditor after fixes.
- **Minor/Info:** Log in the migration report, continue to §4.5.

### 4.5 Update Manifest

After migration, update `.sdlc-manifest.json`:

1. **Update `source_version`** to the current cc-sdlc commit hash
2. **Add missing fields** if the manifest predates this migration:
   - `sdlc_root`: set to `[sdlc-root]` detected in pre-flight
   - `neuroloom_integration`: set to `[has-neuroloom]` detected in pre-flight

```bash
# Read existing manifest
MANIFEST=$(cat .sdlc-manifest.json)

# Update source_version
MANIFEST=$(echo "$MANIFEST" | jq --arg v "$(git -C [cc-sdlc-path] rev-parse HEAD)" '.source_version = $v')

# Add sdlc_root if missing
if ! echo "$MANIFEST" | jq -e '.sdlc_root' >/dev/null 2>&1; then
  MANIFEST=$(echo "$MANIFEST" | jq --arg r "$SDLC_ROOT" '.sdlc_root = $r')
fi

# Add neuroloom_integration if missing
if ! echo "$MANIFEST" | jq -e '.neuroloom_integration' >/dev/null 2>&1; then
  MANIFEST=$(echo "$MANIFEST" | jq --argjson n "$HAS_NEUROLOOM" '.neuroloom_integration = $n')
fi

echo "$MANIFEST" > .sdlc-manifest.json
```

### 4.6 Report to User

```markdown
## SDLC Migration Complete

### Source Version
- Previous: [old commit hash]
- Current: [new commit hash]

### Changes Applied
- Agent memory gitignored: yes/already present
- Previously tracked agent memories unstaged: yes/no/not applicable
- Skills updated: N (framework sections merged, project customizations preserved)
- Knowledge files added: N [list new files from upstream]
- Knowledge files merged: N (new upstream keys added, project additions preserved)
- Knowledge merge conflicts: N [list files where upstream updated a key the project also has — review recommended]
- Knowledge spec_relevant overrides preserved: N [list files where project `true` was kept]
- Knowledge spec_relevant upstream upgrades: N [list files where upstream is now `true` — review recommended]
- Knowledge files removed (moved/deleted in source): N [list old paths]
- New agent roles added to context-map: N [list roles]
- Process docs updated: N (direct copy, excluding agent-selection.yaml)
- Templates updated: N (direct copy, excluding templates/optional/)
- Agent template updated: yes/no
- Agents updated: N (Knowledge Context / Communication Protocol sections)
- Agent-context-map paths updated: N (moved/removed file paths corrected)
- Auditor updated: yes/no
- CLAUDE-SDLC.md merged into CLAUDE.md: yes/no/not needed

### Legacy Cleanup
- Standalone CLAUDE-SDLC.md removed: yes/no/not present

### PROJECT-SECTION Content Review (§2.1d)
- Marked blocks found: N
- Reviewed (non-OK findings): N
- Decisions:
  - Kept as-is: N (list labels)
  - Updated by user: N (list labels)
  - Removed: N (list labels)
  - Merged: N (list labels)
- Blocks skipped (too recent or no baseline): N

### Preserved
- Project-specific skill customizations (build commands, agent names, examples)
- Discipline parking lot entries and triage markers
- Process Maturity Tracker (project-assessed levels, not source repo levels)
- Agent-context-map agent names and project-specific mappings
- Project agent domain content (scope, principles, workflow, anti-rationalization)
- Knowledge file project additions (project-specific keys preserved via key-level merge)
- Knowledge file `spec_relevant` project overrides (true values preserved)

### Downstream Impact Analysis (§3.4)
- Skills scanned: N
- Agents scanned: N
- Findings: N (applied: N, skipped: N)
- Applied: [list changes made]
- Skipped: [list findings deferred — serves as tech debt awareness]

### Gates Passed
- §1.2 Changelog review: user confirmed migration summary
- §2.5 Content-merge verification: tracker intact, parking lots preserved, skills spot-checked
- §3.4 Downstream impact: user reviewed findings
- §4.3a CLAUDE-SDLC.md compatibility: no stale references / [list fixes]

### Verification
- All agent-context-map paths resolve: yes/no (N/A for Neuroloom projects — they use memory_search)
- All agents have Knowledge Context: yes/no
- Spot-check passed: yes/no
- Post-migration audit: passed/findings fixed (auditor dispatched automatically in §4.4)

### Neuroloom Integration (if applicable)
- Project type: [non-Neuroloom | Neuroloom]
- Files with MCP patterns preserved: [list files where memory_search/memory_store calls were kept]
- Sections skipped for Neuroloom: §3.3 (context map), §4.1 (path integrity)
- Knowledge files: [skipped — Neuroloom stores in memory graph | copied]

### Next Steps
1. Commit the migration
```

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just copy all files from cc-sdlc" | Content-merge exists for a reason — direct copy overwrites project customizations |
| "The project's agent names match cc-sdlc's" | They almost never do. Always read the project's context-map, not the source's |
| "I'll copy agent-selection.yaml with the other process files" | `agent-selection.yaml` is project-specific — it contains the project's agent roster, not the framework's. Never overwrite it. |
| "I'll skip the changelog review" | Breaking changes and new capabilities need user input before applying |
| "The tracker levels look right, I'll overwrite them" | The source repo's tracker reflects the source repo's levels, not this project's |
| "I'll rephrase the framework sections to be clearer" | Verbatim rule. Copy exactly from cc-sdlc. Do not rephrase. |
| "I'll remove this agent mapping that cc-sdlc doesn't have" | Project-specific mappings are intentional. Never remove them. |
| "No files were deleted, so §2.1a doesn't apply" | Always check. Moved files appear as add+delete pairs, not renames. |
| "I'll just read the file from the cc-sdlc directory" | Use `git -C [path] show HEAD:file` — never raw filesystem reads. The repo may have uncommitted WIP. |
| "I'll use `git show HEAD:path > file` to extract" | UNSAFE. Shell redirect truncates the target before git show runs. If git show fails, the target becomes an empty file. See "Safe File Extraction" in Source Repo Access Rule. |
| "New knowledge files are installed, so the project benefits automatically" | Knowledge in [sdlc-root]/ is available but not applied until skills and agents are updated to use it. §3.4 closes this gap. |
| "This file has no PROJECT-SECTION markers, so I'll just overwrite it" | Run deviation detection (§2.1c) first — the project may have customized framework content that should be wrapped in markers before overwriting. |
| "I'll rename all skill references to match upstream" | Guarded renames (§4.3a) — only rename if the target skill exists in the project. Renaming to a nonexistent skill causes silent process failures. |
| "I'll auto-fix all the downstream impact findings" | Present findings to the user. They choose what to apply — some findings may not suit the project's context. |
| "This project uses file paths for knowledge access, same as cc-sdlc" | Check for Neuroloom integration first. Projects with `memory_search`/`memory_store` calls use MCP tools, not file paths. Preserve the integration pattern during content-merge — don't overwrite MCP calls with file references. |
| "The SDLC is in `ops/sdlc/`" | Not always. Some projects use `.claude/sdlc/`. Detect the actual structure in pre-flight and use `[sdlc-root]` throughout. |
| "PROJECT-SECTION markers mean this content is protected, just re-inject it" | Markers preserve content from being overwritten, but they don't prevent staleness. Review marked content against upstream changes (§2.1d) — a 6-month-old custom skill phase may reference outdated patterns. |
| "I'll skip the marker review for old blocks" | Old blocks are the most likely to be stale. The skip threshold is for recent blocks (< 7 days) that can't have drifted yet. |
| "The user chose 'keep' last time, so keep all markers this time" | Each migration is a fresh review. Upstream may have changed differently this time. Don't cache decisions across migrations. |

## Integration

- **Feeds into:** `sdlc-audit` skill (post-migration compliance audit)
- **Depends on:** cc-sdlc source repo (reads via git), `.sdlc-manifest.json` (version tracking)
- **Uses:** `AskUserQuestion` (changelog review gate, user confirmation)
- **Related:** `sdlc-initialize` (first-time setup — use that, not this, for new projects)

## Migration vs Initialization

| Concern | Initialization (`sdlc-initialize`) | Migration (`sdlc-migrate`) |
|---------|-------------------------------------|----------------------------|
| When | First install | Framework update |
| Agent creation | Creates new agents from scratch | Updates template-derived sections in existing agents |
| Skills | Copies from cc-sdlc | Merges framework changes into project-customized skills |
| Context map | Wires generic roles to project agents | Adds new knowledge file mappings only |
| Disciplines | Copies templates | Preserves parking lot entries, updates framework sections |
| Destructive? | No (creates new) | No (merges, never overwrites project content) |
