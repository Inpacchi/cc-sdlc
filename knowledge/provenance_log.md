# Knowledge Provenance Log

Append-only record of where knowledge entered the SDLC knowledge layer. Enables staleness tracing, audit lineage, and prepared handoffs between research and ingestion.

**Conventions:**
- Entries in reverse-chronological order (newest first)
- IDs are sequential per date: `prov-YYYY-MM-DD-NNN`
- Conditional fields (`files-created`, `files-updated`, `rule-count`, `ingested-by`) only required when `status: ingested`
- Optional fields (`tier-1-count`, `tier-2-count`) used by `sdlc-research` for research entries
- Status transitions: `pending-review` -> `approved-for-ingest` -> `ingested` (or `rejected` at any point)

## Entry Format

```markdown
## [YYYY-MM-DD] {source name} — {discipline}

- **id:** prov-YYYY-MM-DD-NNN
- **status:** pending-review | approved-for-ingest | ingested | rejected
- **source-type:** reference-doc | file | directory | url | manual
- **source:** {path or description}
- **source-url:** {URL if applicable}
- **discipline:** {target discipline}
- **files-created:** {paths, when status=ingested}
- **files-updated:** {paths, when status=ingested}
- **rule-count:** {N, when status=ingested}
- **ingested-by:** {skill name, when status=ingested}
- **notes:** {freeform}

---
```

## Log

## [2026-07-08] Community tiered-orchestration sources — architecture

- **id:** prov-2026-07-08-001
- **status:** ingested
- **source-type:** manual
- **source:** Three r/ClaudeAI thread screenshots (per-subagent effort frontmatter; Fable/Opus/Sonnet/Haiku workflow splits; SDD with top-tier coordinator), community "fable-chief-agent" skill text, DataCamp spec-driven development tutorial
- **source-url:** https://www.datacamp.com/tutorial/spec-driven-development-with-claude-code
- **discipline:** architecture
- **files-created:** knowledge/architecture/model-tier-strategy.yaml
- **files-updated:** templates/agent-template.md, skills/sdlc-develop-agent/SKILL.md, agents/sdlc-reviewer.md, skills/sdlc-plan/SKILL.md, skills/sdlc-lite-plan/SKILL.md, skills/sdlc-execute/SKILL.md, knowledge/agent-context-map.yaml, knowledge/architecture/README.md, CLAUDE-SDLC.md, disciplines/architecture.md
- **rule-count:** 6
- **ingested-by:** ccsdlc-ingest
- **notes:** DataCamp SDD workflow (spec → plan → implement with human gates) validated as already fully implemented by cc-sdlc — no structural change needed. The fable-chief-agent skill's delegation-economics boundary ("do work directly when delegation costs more") was initially deferred, then adopted by CD decision in the same session as the Manager Rule's Delegation Economics Exception (mandatory review retained; see changelog 2026-07-08 entries). Three unvalidated observations parked in disciplines/architecture.md.

---
