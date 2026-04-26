# Path Transformation Rules

Throughout this migration, apply these transformations when copying or merging content.

## Source → Project Path Mapping

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

## Project-Specific Files (Never Overwrite)

Some files in the cc-sdlc source are **templates** that become project-specific after initialization. These must NOT be direct-copied during migration:

| File | Reason |
|------|--------|
| `process/agent-selection.yaml` | Project's agent roster and dispatch rules — contains project-specific agent names |
| `knowledge/agent-context-map.yaml` | Project's agent-to-knowledge mappings — already protected in §3.3 |
| `knowledge/provenance_log.md` | Project's knowledge provenance records — append-only log of ingestions and research handoffs |

Framework files may contain canonical agent names (e.g., `frontend-developer`) in examples. These are illustrative — they don't affect dispatch behavior. The project's actual agents in `.claude/agents/` and `agent-context-map.yaml` define what gets dispatched.
