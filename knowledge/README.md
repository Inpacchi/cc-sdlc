# Knowledge Stores — Cross-Project

Deep, structured knowledge organized by discipline. Each subdirectory contains patterns, anti-patterns, gotchas, and assessment rubrics that apply across all projects using the SDLC framework.

## Structure

```
knowledge/
├── README.md                  ← This file
├── agent-context-map.yaml     ← Maps agents to their knowledge files
├── architecture/              ← 18 files: system design, debugging, security, payments, ML, deployment
├── data-modeling/             ← UDM patterns, anti-patterns, assessment templates
├── design/                    ← UX modeling methodology, ASCII conventions
├── product-research/          ← Competitive analysis, data source evaluation, product methodology
└── testing/                   ← Tool patterns, component strategies, gotchas, timing, advanced patterns
```

Other disciplines (coding, deployment, etc.) will add directories here as their knowledge matures beyond the parking-lot stage in `disciplines/`.

## Relationship to Other Directories

| Directory | Purpose |
|-----------|---------|
| `disciplines/` | Overviews — *what* each discipline covers, when to engage it |
| `knowledge/` | Deep content — *how* to apply the discipline (patterns, rubrics, gotchas) |

## How This Gets Used

1. **Agent self-lookup** — `agent-context-map.yaml` maps each domain agent to the knowledge files it should read before working. Agents consult this map themselves via a `## Knowledge Context` section in their definition, ensuring they load domain knowledge regardless of how they're dispatched (via skill or directly).
2. **Cross-domain injection** — When skills dispatch an agent into a context outside its domain, the skill consults the map for the *other* domain's agent and injects those knowledge files. Skills do NOT redundantly inject an agent's own domain knowledge.
3. **Discipline overviews** — `disciplines/*.md` reference knowledge files for deep methodology details.
4. **Project-specific knowledge** lives in each project's docs (e.g., project `docs/testing/knowledge/`).

Cross-project knowledge accumulates here; project-specific knowledge stays local.

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
- `.claude/skills/test-loop/SKILL.md`
- `.claude/skills/create-test-suite/SKILL.md`
- `.claude/skills/commit-review/SKILL.md`
- `.claude/skills/ad-hoc-review/SKILL.md`
- `.claude/skills/sdlc-planning/SKILL.md`

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

## Adding a New Discipline

1. Create `knowledge/<discipline-name>/` with a `README.md`
2. Add structured files (YAML preferred for AI-parseable content)
3. Update the discipline overview in `disciplines/<discipline-name>.md` to point here
