# Knowledge Provenance Log

Append-only record of where knowledge entered the SDLC knowledge layer. Enables staleness tracing, audit lineage, and prepared handoffs between research and ingestion.

**Conventions:**
- Entries in reverse-chronological order (newest first)
- IDs are sequential per date: `prov-YYYY-MM-DD-NNN`
- Conditional fields (`files-created`, `files-updated`, `rule-count`, `ingested-by`) only required when `status: ingested`
- Optional fields (`tier-1-count`, `tier-2-count`) used by `research-external` for research entries
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

(No entries yet.)
