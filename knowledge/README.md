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

1. **Agent dispatch** — `agent-context-map.yaml` maps each domain agent to the knowledge files it should read before working. Planning skills (`sdlc-planning`, `ad-hoc-planning`) consult this map when dispatching agents.
2. **Discipline overviews** — `disciplines/*.md` reference knowledge files for deep methodology details.
3. **Project-specific knowledge** lives in each project's docs (e.g., project `docs/testing/knowledge/`).

Cross-project knowledge accumulates here; project-specific knowledge stays local.

## Adding a New Discipline

1. Create `knowledge/<discipline-name>/` with a `README.md`
2. Add structured files (YAML preferred for AI-parseable content)
3. Update the discipline overview in `disciplines/<discipline-name>.md` to point here
