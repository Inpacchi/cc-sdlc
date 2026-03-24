# Compliance Audit Methodology

Full methodology for SDLC compliance auditing. Covers all 9 audit dimensions, report format, severity levels, and guiding principles. Migrated from the `sdlc-compliance-auditor` agent.

## Audit Methodology Sequence

1. **Catalog Scan**: Read `docs/_index.md` — build complete inventory of claimed deliverables and statuses
2. **Artifact Verification**: For each deliverable, verify expected files exist and naming follows conventions
3. **Orphan Detection**: List files in `docs/current_work/` and `docs/chronicle/` not accounted for in catalog
4. **Git Cross-Reference**: Check recent commits for untracked substantial work
5. **Freshness Check**: Assess CLAUDE.md files and memory files for accuracy
6. **Knowledge Layer Scan**: Audit disciplines, knowledge stores, triage status, wiring, context map, playbooks, usage
7. **Migration Integrity**: Verify manifest version, file completeness, content-merge, stale references
8. **Agent Memory Mining**: Scan agent memories for recurring patterns worth promoting
9. **Recommendation Follow-Through**: Check whether previous audit recommendations were acted on
10. **Report Generation**: Produce structured audit report at `docs/current_work/audits/sdlc_audit_YYYY-MM-DD.md`

## Dimension 1: Deliverable Catalog Integrity

- Read `docs/_index.md` for the full deliverable catalog
- Verify every listed deliverable has corresponding artifacts at expected locations
- Check for orphaned artifacts (files in `docs/current_work/` or `docs/chronicle/` not referenced in catalog)
- Validate deliverable ID sequencing (no gaps, no duplicates, sub-deliverables properly suffixed)
- Confirm status labels match actual artifact state (e.g., "complete" should have `_COMPLETE.md`)

## Dimension 2: Artifact Traceability

For each active deliverable, verify the expected artifact chain:
- Spec at `docs/current_work/specs/dNN_name_spec.md`
- Plan at `docs/current_work/planning/dNN_name_plan.md`
- Result at `docs/current_work/results/dNN_name_result.md`
- Completed deliverables archived to `docs/chronicle/` with `_COMPLETE.md` suffix
- Flag deliverables with missing intermediate artifacts (e.g., has result but no spec)

## Dimension 3: Untracked Work Detection

- Scan recent git history for commits touching multiple files without deliverable ID prefixes (`d<N>:`)
- Identify patterns suggesting substantial work done ad hoc when it should have been tracked
- Look for new components, modules, stores, routes, or types introduced without corresponding deliverables
- Cross-reference commit messages against the deliverable catalog

## Dimension 4: Knowledge Freshness

- Check `CLAUDE.md` files (root and per-package) for staleness indicators
- Verify agent memory files in `.claude/agent-memory/` reflect current codebase state
- Flag documented patterns or files that no longer exist
- Check that recent architectural decisions are captured somewhere persistent
- Verify `docs/_index.md` reflects current state of all deliverables

## Dimension 5: Process Health Indicators

- Ratio of tracked vs untracked multi-file changes
- Average artifact completeness per deliverable
- Chronicle freshness (how long completed work sits in `current_work/` before archiving)
- Spec approval coverage (deliverables that went through proper CD approval)
- **Changelog freshness** — compare `ops/sdlc/process/sdlc_changelog.md` against recent commits modifying SDLC process files. Flag process changes without changelog entries.

## Dimension 6: Knowledge Layer Health

### 6a. Discipline Parking Lots (`ops/sdlc/disciplines/`)

Check each discipline file:

| File | Discipline |
|------|-----------|
| `architecture.md` | System design, component boundaries, integration patterns |
| `business-analysis.md` | Requirements, domain modeling, stakeholder needs |
| `coding.md` | Implementation patterns, conventions, tech debt |
| `data-modeling.md` | Data architecture, schema design |
| `deployment.md` | CI/CD, infrastructure, release management |
| `design.md` | UI/UX, visual design, interaction patterns |
| `process-improvement.md` | Meta-discipline: improving the SDLC itself |
| `product-research.md` | Market, users, competitive landscape |
| `testing.md` | Test strategy, automation, knowledge layers |

**What to check:**
- Are parking lots being written to between audits? (git blame / last-modified)
- Do insights reference recent deliverables?
- Are entries added by execution/planning skills? (If only during audits, capture integration is broken)
- Are cross-discipline insights flowing?
- Do entries have triage markers (`[READY TO PROMOTE]`, `[NEEDS VALIDATION]`, `[DEFERRED]`)?

**Maturity level verification:**
- Read Process Maturity Tracker in `process-improvement.md`
- Level 1 claim: parking lot file exists with entries
- Level 2 claim: knowledge store directory with YAML files + agent-context-map wired + at least one triage pass
- Flag claims lacking supporting evidence

### 6b. Knowledge Stores (`ops/sdlc/knowledge/`)

| Directory | Purpose |
|-----------|---------|
| `architecture/` | System design, debugging, security, payments, ML, deployment |
| `business-analysis/` | Requirements feedback loops |
| `coding/` | Code quality, TypeScript patterns, testability |
| `data-modeling/` | UDM patterns, anti-patterns, assessment |
| `design/` | UX modeling, ASCII conventions, accessibility |
| `product-research/` | Competitive analysis, methodology, risk |
| `testing/` | Paradigm, gotchas, tool patterns, timing |

**Check:** staleness, relevance to current stack, consumption by skills/agents, growth since seeding, cross-project vs project-specific content.

### 6c. Discipline Triage Status

**Triage authority matrix:**

| Transition | Authority | Condition |
|-----------|-----------|-----------|
| unmarked → `[NEEDS VALIDATION]` | Auto-apply | Unmarked for ≥2 audit cycles |
| `[NEEDS VALIDATION]` → `[DEFERRED]` | Auto-apply | Unvalidated ≥3 cycles AND no agent feedback references it AND discipline dormant |
| Any → `[READY TO PROMOTE]` | CD only | Propose with evidence, CD confirms |
| `[READY TO PROMOTE]` → Promoted | CD only | Actual knowledge file creation |

Auto-triage: scan entries, apply qualifying transitions, log actions in report.

### 6d. Knowledge-to-Skill Wiring

Two ownership tiers:
1. **Agent-owned (domain):** Agent definitions include Knowledge Context section directing them to `agent-context-map.yaml`
2. **Skill-owned (cross-domain):** Skills inject knowledge from other agents' mappings when dispatching into cross-domain contexts

**Check:** agent definitions have self-lookup sections, skills don't redundantly inject same-agent knowledge, cross-domain injection exists where needed.

### 6e. Agent Context Map Integrity

Check `ops/sdlc/knowledge/agent-context-map.yaml`:
- All mapped file paths resolve to actual files
- Knowledge YAML files not referenced by any agent (gaps)
- Agents in skill tables without knowledge mapping
- Skills that should consult the map actually do

### 6f. Playbook Freshness

Check `ops/sdlc/playbooks/`:
- Each playbook has `last_validated` and `validation_triggers`
- Validation triggers fired since `last_validated`?
- All referenced file paths resolve
- README index consistent with actual files

### 6g. Discipline Usage Audit

Five usage signals per discipline:

| Signal | Active | Warning | Dead |
|--------|--------|---------|------|
| Parking lot activity | Entries added between audits from skills | Only during audits | No entries since last audit |
| Knowledge consumption | Mapped agents dispatched recently | Mapped but agents unused | No mapping |
| Promotion flow | Entries triaged and promoted | Added but not triaged | Static |
| Cross-discipline feed | Receives insights from other domains | Isolated | N/A |
| Agent feedback | Agents reporting on knowledge quality | Silent (gradual adoption ok) | N/A |

Report as table with interpretation (healthy / formalized-but-dead / alive-but-unformalized / dead).

## Dimension 7: Migration Integrity

- **7a. Manifest version:** Read `.sdlc-manifest.json`, compare `source_version` against current cc-sdlc. If >10 commits or >30 days behind, recommend migration.
- **7b. File completeness:** Compare installed files against `skeleton/manifest.json` source_files lists.
- **7c. Content-merge:** Verify framework sections current while project customizations preserved (skill gates, discipline entries, agent context map names).
- **7d. Removed features:** Search skills/agents for references to deprecated/removed framework features.

## Dimension 8: Agent Memory Pattern Mining

- Read each agent's `MEMORY.md` in `.claude/agent-memory/*/`
- Identify recurring themes across multiple agents or cycles
- Flag patterns that should be in `ops/sdlc/knowledge/` or `ops/sdlc/disciplines/` but aren't
- Check for stale memories contradicting current codebase

Promotion criteria: appears in 2+ agent memories independently, reusable pattern, saves future agents from rediscovery.

## Dimension 9: Recommendation Follow-Through

- Read previous audit artifacts in `docs/current_work/audits/`
- For each past recommendation: implemented, deferred with rationale, or ignored?
- Calculate follow-through rate: (acted-on + explicitly-deferred) / total
- Flag ignored recommendations without explanation

## Compliance with Session Input

When auditing a specific session for compliance:

1. Read the session JSONL (see `references/session-reading.md`)
2. Check whether SDLC skills were invoked when they should have been
3. Verify deliverable IDs were assigned for substantial work
4. Check whether specs were written before execution
5. Verify agent dispatch patterns match process requirements
6. Flag process bypasses with context (why was it bypassed?)

## Compliance with Commit Input

When auditing specific commits:

1. Read commit messages and diffs
2. Cross-reference against `docs/_index.md` — do commits map to tracked deliverables?
3. Flag multi-file changes without deliverable tracking
4. Check whether new components/modules/routes have corresponding specs
5. Verify commit message conventions

## Report Format

```markdown
## SDLC Compliance Audit — [Date]

### Summary
- Total deliverables: N
- Complete: N | Active: N | Blocked: N
- Knowledge layer wiring: connected | partially connected | disconnected
- Compliance score: X/10
- Top issues: [brief list]

### Catalog Integrity
[findings]

### Artifact Traceability
[per-deliverable status]

### Untracked Work
[commits/changes that should have been tracked]

### Knowledge Freshness
[stale docs, outdated memories]

### Knowledge Layer Health
#### Discipline Parking Lots
[per-file status, cross-discipline flow, maturity verification]

#### Discipline Usage Audit
| Discipline | Level | Parking Lot | Knowledge | Promotion | Cross-Feed |
|-----------|-------|-------------|-----------|-----------|------------|

#### Knowledge Stores
[per-directory status]

#### Discipline Triage Status
[markers, promotion recommendations]

#### Knowledge-to-Skill Wiring
[wiring status, gaps]

#### Agent Context Map
[path resolution, unmapped files]

#### Playbook Freshness
[per-playbook status]

### Migration Integrity
- Manifest version: [hash] ([age] behind)
- Framework completeness: N/N files
- Content-merge: [pass/issues]
- Stale references: [list or none]

### Agent Memory Patterns
[recurring findings worth promoting]

### Changelog Freshness
[entries vs process commits]

### Recommendation Follow-Through
[previous recommendations status]
- Follow-through rate: X%

### Recommendations
[prioritized action items]
```

## Severity Levels

- **Critical**: Missing specs for completed features, deliverable ID conflicts, catalog entries pointing to nonexistent files
- **Warning**: Incomplete artifact chains, stale docs, unarchived completed work, disconnected knowledge stores, dormant disciplines
- **Info**: Minor naming inconsistencies, optional improvements, unmarked parking lot entries, pending `[READY TO PROMOTE]` items

## Guiding Principles

- **Read before asserting.** Never claim a file exists or doesn't without checking.
- **Substance over ceremony.** Flag missing artifacts only when the gap creates real risk.
- **Proportional recommendations.** Small gaps get small fixes.
- **Honor the ad hoc exception.** Single-file fixes, config changes, typo corrections legitimately skip tracking.
- **Context-aware.** The SDLC is lightweight by design — small team or solo dev + AI.
- **Toolbox, not recipe.** Empty parking lots aren't failures if the discipline hasn't been needed. Only flag staleness when the discipline IS being exercised but knowledge layer isn't participating.

## Audit Artifact Lifecycle

- Output: `docs/current_work/audits/sdlc_audit_YYYY-MM-DD.md`
- Keep the last 5 audits; recommend deleting older ones
- Not deliverables — don't archive to chronicles
- Consumed by: this skill on subsequent runs (follow-through), planning skills (knowledge wiring gaps), the user (periodic health check)

## File Naming Conventions to Validate

| Type | Pattern | Example |
|------|---------|---------|
| Spec | `dNN_name_spec.md` | `d1_auth_spec.md` |
| Plan | `dNN_name_plan.md` | `d1_auth_plan.md` |
| Result | `dNN_name_result.md` | `d1_auth_result.md` |
| Complete | `dNN_name_COMPLETE.md` | `d1_auth_COMPLETE.md` |
| Blocked | `dNN_name_BLOCKED.md` | `d1_auth_BLOCKED.md` |
