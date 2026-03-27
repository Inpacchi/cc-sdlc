# Knowledge Stores — Cross-Project

Deep, structured knowledge organized by discipline. Each subdirectory contains patterns, anti-patterns, gotchas, and assessment rubrics that apply across all projects using the SDLC framework.

## Structure

```
knowledge/
├── README.md                  ← This file
├── agent-context-map.yaml     ← Maps agents to their knowledge files
├── architecture/              ← 16 files: system design, debugging, security, payments, ML, deployment
├── coding/                    ← Code quality principles, TypeScript patterns, testability, mocking stance
├── data-modeling/             ← UDM patterns, anti-patterns, assessment templates
├── design/                    ← UX modeling methodology, ASCII conventions, accessibility-testability
├── product-research/          ← Competitive analysis, data source evaluation, product methodology, risk assessment
└── testing/                   ← Tool patterns, component strategies, gotchas, timing, advanced patterns
```

Other disciplines (business-analysis, deployment, process-improvement) will add directories here as their knowledge matures beyond the parking-lot stage in `disciplines/`.

## Relationship to Other Directories

| Directory | Purpose |
|-----------|---------|
| `disciplines/` | Overviews — *what* each discipline covers, plus parking lot entries with triage markers (`[READY TO PROMOTE]`, `[NEEDS VALIDATION]`, `[DEFERRED]`) |
| `knowledge/` | Deep content — *how* to apply the discipline (patterns, rubrics, gotchas). Promoted from discipline parking lots when validated. |

## How This Gets Used

1. **Agent self-lookup** — `agent-context-map.yaml` maps each domain agent to the knowledge files it should read before working. Agents consult this map themselves via a `## Knowledge Context` section in their definition, ensuring they load domain knowledge regardless of how they're dispatched (via skill or directly).
2. **Cross-domain injection** — When skills dispatch an agent into a context outside its domain, the skill consults the map for the *other* domain's agent and injects those knowledge files. Skills do NOT redundantly inject an agent's own domain knowledge.
3. **Discipline overviews** — `disciplines/*.md` reference knowledge files for deep methodology details.
4. **Project-specific knowledge** lives in each project's docs (e.g., project `docs/testing/knowledge/`).

Cross-project knowledge accumulates here; project-specific knowledge stays local.

**Accelerating knowledge stores:** Beyond organic discipline capture, the `sdlc-ingest` skill enables bulk import of external content (transcripts, articles, documentation) directly into knowledge files and discipline parking lots.

## Knowledge File Metadata Fields

All knowledge YAML files share a common metadata header. While domain-specific content varies, these top-level fields are standardized:

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `id` | Yes | string | Unique identifier matching the filename (e.g., `api-design-methodology`) |
| `name` | Yes | string | Human-readable name |
| `description` | Yes | string | One-line summary of what this knowledge covers |
| `pattern` | Yes | enum | Content structure: `entries`, `gotchas`, `rules`, or `methodology`. See [Content Patterns](#content-patterns). |
| `category` | Yes | string | Parent discipline directory (e.g., `architecture`, `testing`, `design`) |
| `spec_relevant` | Yes | boolean | Whether this knowledge is loaded during spec writing. Default: `false`. |
| `project_applicability` | Yes | object | When this store is relevant and what to do if it isn't. See below. |
| `last_updated` | Yes | date | When the content was last modified |

### Content Patterns

All knowledge files use one of four canonical content patterns. These are closed — new files MUST use one. If none fits, propose a new pattern explicitly rather than inventing one ad hoc.

Optional extra fields are allowed in all patterns. Required fields must always be present.

#### `entries` — Guidance on practices

Use when: teaching how to do something well (principles, patterns, conventions).

Structure: Freeform. Named subsections as top-level keys, organized by domain. No wrapper key required — content structure follows the subject matter.

```yaml
# ... metadata header ...

testability_as_code_quality:
  principle: "Testability is a design signal"
  detail: |
    Code that is hard to test is usually hard to maintain...
  examples:
    - pattern: "Dependency injection over global state"
      code: |
        # inject dependencies explicitly
```

No required content fields — subsection structure is domain-specific.

Example file: `coding/code-quality-principles.yaml`

#### `gotchas` — Failure pattern catalogs

Use when: documenting things that go wrong (symptoms, causes, resolutions).

Structure: Items wrapped under a `gotchas:` key. Each item has 6 required fields.

**Required fields:** `id`, `severity`, `symptom`, `cause`, `resolution`, `prevention`

```yaml
# ... metadata header ...

gotchas:                              # wrapper key MUST be "gotchas:"
  - id: G01
    severity: high                    # critical | high | medium | low
    symptom: "Tests pass locally but fail in CI"
    cause: "Hardcoded paths or timezone assumptions"
    resolution: "Use relative paths and UTC timestamps"
    prevention: "Run tests in CI-like container locally"
    # optional extras: discovered, applies_to, name, source-specific attribution, etc.
```

Example file: `testing/gotchas.yaml`

#### `rules` — Checklists and validation criteria

Use when: defining criteria to check against (design rules, assessment rubrics).

Structure: Items wrapped under a `rules:` key. Each item has 5 required fields.

**Required fields:** `rule_id`, `name`, `description`, `rationale`, `checklist`

```yaml
# ... metadata header ...

rules:                                # wrapper key MUST be "rules:"
  - rule_id: V01
    name: "Visual hierarchy"
    description: "Every screen needs a clear focal point"
    rationale: "Users scan in predictable patterns..."
    checklist:
      - "Is there one dominant element per section?"
      - "Do size/weight/color create clear reading order?"
    # optional extras: anti_pattern, source, etc.
```

Example file: `design/visual-design-rules.yaml`

#### `methodology` — Domain frameworks and processes

Use when: describing a multi-phase process or framework with domain-specific structure.

Structure: Freeform. Multiple named sections following the methodology's natural breakdown. No wrapper key required — structure follows the domain, not a rigid template.

```yaml
# ... metadata header ...

rest_maturity_levels:
  level_0:
    description: "Single URI, single verb"
    when_acceptable: "Internal tools, prototypes"
  level_1:
    description: "Resources with URIs"
    # ...
```

No required content fields — section structure is domain-specific.

Example file: `architecture/api-design-methodology.yaml`

### `spec_relevant` Field

Controls whether a knowledge file is injected into agent dispatch prompts during **spec writing** (`sdlc-plan` Step 2) vs only during **plan writing and execution** (Steps 4+).

- `spec_relevant: true` — Knowledge that shapes **what** gets built: domain models, design methodologies, product research frameworks, security taxonomies, accessibility principles. Loaded at spec time AND plan/execution time.
- `spec_relevant: false` — Knowledge that shapes **how** it gets built: code patterns, debugging methodologies, test tooling, deployment patterns. Loaded only at plan/execution time.

**Default is `false`** in the cc-sdlc source repo because spec-relevance is project-specific. Projects override to `true` for stores that matter to their spec writing. The `sdlc-migrate` skill preserves project overrides when updating framework files.

**Opt-in filtering:** If no knowledge file in the project has `spec_relevant: true`, `sdlc-plan` loads ALL mapped files at spec time (current behavior preserved). Filtering only activates once at least one file is tagged `true`. Tag at least 2-3 files as spec-relevant, or leave all as `false` for full loading — tagging only one file may produce under-informed specs.

**Examples of typically spec-relevant stores:**
- `data-modeling/patterns/people-and-organizations.yaml` — domain model patterns shape entity design
- `design/ux-modeling-methodology.yaml` — UX methodology informs spec requirements
- `product-research/product-methodology.yaml` — product methodology shapes feature scoping
- `architecture/security-review-taxonomy.yaml` — security posture is a spec-level concern
- `testing/testing-paradigm.yaml` — testing strategy is explicitly referenced in spec Step 2

**Examples of typically NOT spec-relevant stores:**
- `architecture/debugging-methodology.yaml` — debugging is an execution-time concern
- `coding/typescript-patterns.yaml` — code patterns matter at implementation, not spec
- `testing/tool-patterns.yaml` — test tooling is plan/execution detail
- `architecture/deployment-patterns.yaml` — deployment is post-implementation

### `project_applicability` Field

Controls whether a knowledge store is relevant to a given project and what to do during initialization if it isn't. Used by `sdlc-initialize` Phase 6a to present a relevance assessment to CD.

```yaml
project_applicability:
  relevant_when: "Project uses TypeScript"
  action_if_irrelevant: remove
```

**Fields:**

| Sub-field | Type | Purpose |
|-----------|------|---------|
| `relevant_when` | string | Human-readable condition describing when this store applies. Starts with "Always relevant" for core stores, or describes a specific tech/domain condition. |
| `action_if_irrelevant` | enum | What to do if the condition doesn't match: `keep`, `customize`, or `remove`. |

**`action_if_irrelevant` values:**

- `keep` — Always retain this file regardless of project type. Used for cc-sdlc infrastructure files (agent protocols, debugging, testing paradigm) and universal methodologies.
- `customize` — The file's structure is useful but its content is stack-specific. During initialization, the agent rewrites the content for the project's actual stack (e.g., swap Playwright CLI patterns for Cypress patterns).
- `remove` — The file is not applicable. Delete it from the project's knowledge directory and remove its entry from `agent-context-map.yaml`.

**During initialization:** `sdlc-initialize` Phase 6a reads every knowledge file's `project_applicability`, compares against the D1 spec, and presents a table to CD with keep/customize/remove recommendations. CD confirms or overrides before any files are deleted.

## Setup: Wiring Agents to Knowledge

After installing cc-sdlc into a project, the agent-context-map references **generic role names** (e.g., `sdet`, `architect`, `backend-developer`). These must be updated to match your project's actual agent filenames.

### Step 1: Update `agent-context-map.yaml`

1. List your project's agents: `ls .claude/agents/*.md`
2. For each mapping entry in `agent-context-map.yaml`:
   - Rename generic roles to your agent names (e.g., `architect` → `software-architect`)
   - Remove mappings for roles you don't have
   - Add entries for project-specific agents not in the generic template
3. Keep the knowledge file paths unchanged — those are cross-project

### Step 2: Update skill dispatch references

Several skills dispatch agents by name using backtick-quoted identifiers. Search and replace these to match your agent names:

```bash
# Find all hardcoded agent dispatch names in skills
grep -r '`sdet`\|`architect`\|`backend-developer`\|`frontend-developer`' .claude/skills/
```

Key files that reference `sdet` (your testing agent name will differ):
- `.claude/skills/sdlc-tests-run/SKILL.md`
- `.claude/skills/sdlc-tests-create/SKILL.md`
- `.claude/skills/review-commit/SKILL.md`
- `.claude/skills/review-diff/SKILL.md`
- `.claude/skills/sdlc-plan/SKILL.md`

### Step 3: Update discipline references

Check `disciplines/*.md` for agent file paths and update to match:

```bash
grep -r '\.claude/agents/' disciplines/
```

### Step 4: Verify no orphaned references

```bash
# Check that every agent name in the context map has a corresponding file
for role in $(grep -E '^\s+\w' knowledge/agent-context-map.yaml | grep -v '#' | sed 's/://'); do
  [ -f ".claude/agents/${role}.md" ] || echo "Missing agent: $role"
done
```

**Why this matters:** Skills silently fail to dispatch the correct agent if the name doesn't match. The context map lookup returns nothing, so agents don't receive knowledge files. Both failures are silent — no errors, just degraded output quality.

## Adding a Knowledge Store for a Discipline

A knowledge store is created when a discipline reaches Level 2 (Managed) — meaning its parking lot has validated, promotable entries. See `disciplines/README.md` § "Creating a New Discipline" for the full lifecycle.

**Prerequisites:** The discipline file (`disciplines/<name>.md`) must already exist with triaged parking lot entries marked `[READY TO PROMOTE]`.

**Steps:**

1. Create `knowledge/<discipline-name>/` with a `README.md` describing the store's purpose, structure, and relationships
2. Promote `[READY TO PROMOTE]` entries from the parking lot to structured YAML files
3. Mark promoted parking lot entries with `Promoted → [target file]`
4. Update `agent-context-map.yaml` — wire the new knowledge files to relevant agent roles
5. Update the discipline file's status from "Parking lot" to "Active" and add a knowledge store reference
6. Update the Process Maturity Tracker in `disciplines/process-improvement.md` — upgrade to Level 2
7. Add the directory and files to `skeleton/manifest.json`
8. Update this README's structure listing
