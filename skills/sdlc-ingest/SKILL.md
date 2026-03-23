---
name: sdlc-ingest
description: >
  Bulk-import external knowledge into SDLC disciplines and knowledge stores. Analyzes curated
  content collections (transcripts, articles, documentation, design guides, architecture papers,
  postmortems) through a discipline lens and produces structured YAML knowledge files, parking
  lot entries, and playbook candidates. Follows the existing discipline lifecycle: extract →
  structure → place (validated rules to knowledge files, unvalidated insights to parking lots).
  Triggers on "ingest these", "analyze these transcripts", "import knowledge from", "extract
  patterns from", "bulk import", "learn from these", "what can we adopt from", "process these
  for the SDLC", "add to our knowledge from", "distill these into knowledge".
  Do NOT use for single-file reads or ad-hoc research — use direct reads or oberweb.
  Do NOT use for exploring ideas — use sdlc-idea.
  Do NOT use for creating specs or plans — use sdlc-plan or sdlc-lite-plan.
---

# Knowledge Ingestion

Structured bulk import of external content into the SDLC knowledge layer. The goal is to extract actionable, testable rules from curated source material and place them correctly within disciplines and knowledge stores — following the existing discipline lifecycle rather than bypassing it.

**This skill produces knowledge artifacts. It does NOT produce specs, plans, or implementations.**

**Argument:** `$ARGUMENTS` (path to content directory or file list, plus optional target discipline hint)

## When This Applies

Use this when the user has a collection of curated external content they want to absorb into the project's SDLC knowledge. The hallmark is bulk external material — not codebase-derived insights (those come from discipline capture during normal work).

Signs this skill is appropriate:
- A directory of transcripts, articles, or documentation files
- "What can we adopt from these into our SDLC?"
- "Analyze these for patterns we should codify"
- Curated content from a known expert, conference, or authoritative source
- The user wants to accelerate knowledge store population beyond organic capture

Signs this skill is NOT appropriate:
- Single file or single insight → add directly to a discipline parking lot
- Codebase patterns → discipline capture protocol handles this organically
- The user wants to explore an idea → `sdlc-idea`
- The user wants competitive analysis → `/feature-compare` or product research tools

## Core Principles

**Extract rules, not summaries.** The output is testable, falsifiable rules with specific values — not prose summaries of what the source said. "Use non-linear easing" is a summary. "All animations must use non-linear easing (ease-in-out or spring); linear easing is forbidden except for progress bars" is a rule.

**Respect the discipline lifecycle.** Rules that are specific, testable, and broadly applicable go directly to knowledge YAML files. Insights that are promising but need project-specific validation go to discipline parking lots with `[NEEDS VALIDATION]`. Do not skip the triage step — bulk import is especially prone to importing plausible-sounding rules that don't survive contact with the actual codebase.

**Source attribution is mandatory.** Every extracted rule must trace back to its source file. This enables future re-evaluation when sources are updated or when rules prove wrong.

**Filter aggressively.** Not everything in external content belongs in the knowledge store. Workflow-specific advice ("view designs on your target device"), tool-specific tips ("use Figma's export settings"), and opinions without rationale get filtered out. The test: would an agent acting on this rule produce measurably better work?

**Deduplicate against existing knowledge.** Before creating new rules, read existing knowledge files in the target discipline. If a rule already exists, skip it or merge source attribution. If it conflicts, flag the conflict for CD resolution.

## Workflow

```
SURVEY → SCOPE → EXTRACT → STRUCTURE → PLACE → REPORT
```

The flow is sequential. Each step must complete before the next begins. The user confirms scope (step 2) before extraction begins.

## Steps

### 1. Survey the Content

Read the content source to understand what's there:

1. **Inventory** — list all files, formats, sizes. Count the total.
2. **Sample** — read 2-3 representative files to assess content quality and domain focus.
3. **Characterize** — describe the content in one sentence: who created it, what domain it covers, what type of knowledge it contains (principles, tutorials, case studies, reference docs).

Present the survey to the user:

```
SURVEY
Files: [count] [format] files in [path]
Domain: [what the content covers]
Character: [principles / tutorials / case studies / reference / mixed]
Sample: [1-sentence summary of 2-3 sampled files]
Quality signal: [high — expert with rationale / medium — practical tips / low — opinions without backing]
```

### 2. Scope the Ingestion

Before extracting anything, align with the user on:

1. **Target discipline(s)** — which discipline(s) will receive the knowledge. Usually 1-2; if the content spans many disciplines, pick the primary and note secondary captures.
2. **Existing knowledge audit** — read the target discipline's current state:
   - Discipline file (`ops/sdlc/disciplines/<name>.md`) — existing parking lot entries
   - Knowledge store (`ops/sdlc/knowledge/<name>/`) — existing YAML files and their rule IDs
   - Playbooks (`ops/sdlc/playbooks/`) — related playbooks that might need updating
3. **Extraction depth** — based on file count and user preference:
   - **Shallow** (>20 files): read all files but extract only high-confidence, broadly-applicable rules. Best for large collections where comprehensive extraction would exceed context limits.
   - **Deep** (<20 files): thorough extraction with nuance, including edge cases and conditional rules. Best for focused, high-quality source material.
4. **Project context** — if the user provides context about how the knowledge applies to their project, capture it. This enables project-specific application notes in the output.

Present the scope for confirmation:

```
SCOPE
Target discipline: [name]
Existing knowledge: [count] YAML files, [count] rules (highest ID: [X-NN])
Existing parking lot entries: [count] ([count] NEEDS VALIDATION)
Extraction depth: shallow | deep
Project context: [supplied context | none — rules will be generic]
```

Wait for user confirmation before proceeding. If the user adjusts scope, re-present.

### 3. Extract

Read all source files and extract knowledge through the discipline lens.

**For each source file, capture:**
- Actionable rules with specific, testable criteria
- Anti-patterns with "why it's wrong" rationale
- Patterns that apply to specific component types or situations
- Gotchas that agents would not derive from codebase reading alone

**Filtering criteria — include if:**
- The rule has a specific, testable assertion (numbers, constraints, conditions)
- An agent acting on it would produce measurably better work
- It generalizes beyond the specific example in the source
- It includes rationale (not just "do this" but "do this because...")

**Filtering criteria — exclude if:**
- It's tool-specific workflow advice (Figma settings, IDE shortcuts)
- It's an opinion without rationale or evidence
- It's obvious to any competent practitioner in the domain
- It duplicates an existing rule in the knowledge store
- It's too context-specific to generalize

**For large collections (shallow mode):** Process files in batches. After each batch, check for theme saturation — if the same rules keep appearing, note the redundancy and move on. Not every file needs full extraction.

**Track extraction metadata:**
- Rules extracted per source file
- Rules filtered out (with brief reason)
- Cross-references between files (multiple sources validating the same rule)

### 4. Structure

Organize extracted rules into structured YAML files following the conventions of the target knowledge store.

**File organization:**
- Group rules by theme/category into files. Each file should be a coherent topic (e.g., `visual-design-rules.yaml`, `interaction-animation-patterns.yaml`).
- If the target discipline already has YAML files, add rules to existing files where they fit. Only create new files for genuinely new categories.
- Continue existing rule ID sequences (e.g., if `visual-design-rules.yaml` ends at V16, new rules start at V17).

**Rule format (follow existing conventions in the target knowledge store):**
Each rule should include:
- **ID** — sequential within its file (e.g., V17, I8, C15)
- **Name** — descriptive, 3-8 words
- **Rule statement** — the testable assertion
- **Rationale** — why this rule exists (the "because")
- **Checklist item** — a yes/no question for code review (e.g., "Does the heading use tightened letter-spacing?")
- **Source** — the source file identifier
- **Guideline/Anti-pattern entries** — specifics of what to do or not do

**If the discipline doesn't have YAML conventions yet:**
Follow the general pattern from `knowledge/architecture/*.yaml` or `knowledge/testing/*.yaml`:
```yaml
rule_id: XX
name: rule-name
description: |
  The testable rule statement.
rationale: |
  Why this matters.
checklist:
  - "Question framed for code review"
source: source-file-identifier
```

**Project-specific application notes (optional):**
If the user provided project context in step 2, add application notes to rules where the generic rule maps to specific product surfaces, components, or patterns. These are informational — they help agents apply generic rules in context.

### 5. Place

Route each output to its correct destination:

| Output Type | Destination | Criteria |
|-------------|-------------|----------|
| Validated, testable rules | `ops/sdlc/knowledge/<discipline>/<file>.yaml` | Specific, testable, broadly applicable, has rationale |
| Promising but unvalidated insights | `ops/sdlc/disciplines/<name>.md` parking lot | Needs project-specific validation, or too context-dependent to codify as a rule |
| Cross-discipline insights | Adjacent discipline's parking lot | Belongs to a different discipline than the primary target |
| Playbook candidates | Noted in report (not auto-created) | Enough related rules emerged to warrant a review checklist |

**Parking lot entry format:**

```
### [Category Name] ([date], source: [source description])

*Bulk import from [source characterization]. Rules promoted to knowledge store; parking lot entries below are principles that need validation against [project]'s specific context before full adoption.*

- **[Insight title].** [NEEDS VALIDATION] [Description]. *[Project relevance note if applicable].* (Source: `[source-file-id]`)
```

**Knowledge file placement:**
- Write new YAML files or append to existing ones
- Update the knowledge store's `README.md` to list new files
- If new files are created, add them to the README's structure listing and "Knowledge Categories" table

**Playbook updates:**
- If a related playbook exists, check whether new rules should be added to its checklist
- If enough rules cluster around a specific task type to warrant a new playbook, note it in the report but do not auto-create — propose the playbook structure for CD approval

### 6. Report

Present a structured summary of what was ingested:

```
INGESTION REPORT
═══════════════════════════════════════════════════════════════

Source: [count] files from [path]
Target discipline: [name]
Extraction depth: shallow | deep

KNOWLEDGE FILES
  Created: [list of new YAML files with rule count]
  Updated: [list of existing files with new rule count]
  Total new rules: [count]

PARKING LOT
  New entries: [count] ([count] NEEDS VALIDATION)
  Cross-discipline entries: [count] (in [discipline names])

PLAYBOOK
  Updated: [playbook name — added N checklist items] | none
  Proposed: [new playbook name and reason] | none

FILTERING
  Rules extracted: [count]
  Rules filtered: [count] (tool-specific: N, opinion-only: N, duplicates: N, too-specific: N)

GAPS IDENTIFIED
  [List areas where the source material was thin or where the discipline needs more depth]

SOURCE COVERAGE
  [count]/[total] files produced extractable rules
  Top contributors: [files that yielded the most rules]
  No-yield files: [files that produced nothing useful, with brief reason]
```

### 7. Changelog Update

Update `ops/sdlc/process/sdlc_changelog.md` with the ingestion event:

```markdown
## [date]: Knowledge Ingestion — [discipline name]

**Origin:** Bulk ingestion from [source description]

**What happened:** [count] [content type] files analyzed for [discipline] knowledge.

**Changes made:**

1. **`knowledge/[discipline]/[file].yaml`** — [created/updated] with [count] new rules ([ID range])
2. **`disciplines/[name].md`** — [count] new parking lot entries added
3. **`knowledge/[discipline]/README.md`** — updated structure listing
[4. **`playbooks/[name].md`** — updated checklist with [count] new items (if applicable)]

**Rationale:** External knowledge accelerates discipline maturity beyond organic capture. Source material was [quality assessment] — [brief justification for the import].
```

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll summarize the content" | Extract rules, not summaries. Summaries aren't actionable in code review. |
| "Everything in here is useful" | Filter aggressively. Most external content doesn't meet the testability bar. |
| "I'll put everything directly in knowledge YAML" | Unvalidated insights go to the parking lot. Only testable, broadly-applicable rules go to YAML. |
| "I'll skip reading existing knowledge" | Deduplication is mandatory. Don't create rules that already exist. |
| "The source didn't provide rationale, but the rule is good" | If you can supply the rationale from domain knowledge, do so. If not, it goes to the parking lot as [NEEDS VALIDATION]. |
| "I'll create a playbook automatically" | Propose playbooks for CD approval. Don't auto-create — they need validation against the project's actual task patterns. |
| "I'll skip source attribution" | Every rule traces to a source. No exceptions. |
| "This content spans 5 disciplines" | Pick the primary discipline. Secondary captures go to adjacent parking lots. Don't try to populate 5 knowledge stores in one session. |
| "I'll read all 50 files in detail" | Use shallow mode for large collections. Theme saturation means diminishing returns after ~15-20 files in most domains. |
| "I'll create new YAML conventions for this discipline" | Follow existing conventions in the target knowledge store. If none exist, follow the patterns from the most mature stores (architecture, testing). |

## Integration

- **Feeds into:** discipline parking lot triage, knowledge store maturation, playbook creation
- **Uses:** file reading, existing knowledge stores (for deduplication), discipline files (for parking lot placement)
- **Complements:** discipline capture protocol (organic, per-session) — this skill handles bulk external import
- **Does NOT replace:** organic discipline capture. Work-session insights still flow through the capture protocol in skills like sdlc-execute and sdlc-idea. Ingestion accelerates knowledge store population from curated external sources.
- **Downstream:** after ingestion, the compliance auditor can assess freshness and coverage of the new knowledge entries during its regular audit cycle
