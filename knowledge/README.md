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
- `.claude/skills/commit-review/SKILL.md`
- `.claude/skills/diff-review/SKILL.md`
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
