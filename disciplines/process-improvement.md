# Process Improvement Discipline

**Status**: Active — meta-discipline with formal maturity level definitions and tracker

## Scope

Improving the SDLC framework, process maturity, tooling evolution, skill development.

## Foundational Principles

### Toolbox, not recipe

The single most important principle governing all process improvement work. Both RUP and SAFe were considered heavy not because the authors intended them to be — both included "tailor the methodology" as a first activity — but because inexperienced practitioners treated them as prescriptions to follow from alpha to omega, and the ecosystems (tooling, certification, consulting) reinforced that behavior.

Our framework must function as a toolbox: helpful, available prescriptions for common needs, with no overhead that isn't needed or requested. This means:

- **Process is pulled, not pushed.** Teams reach for a discipline when they need it. Nobody mandates all disciplines for every project.
- **Ad hoc is legitimate.** Vibe coding, exploratory prototyping, and "just build it" are valid approaches. The process accommodates them (see ad hoc reconciliation) rather than fighting them.
- **Overhead earns its place.** Every process element must demonstrate value before it becomes standard. "We should have done X" is the trigger, not "the process says we must do X."
- **Skills inherit this principle.** When disciplines become Claude Code skills, each skill should be independently invocable and immediately useful — not part of a mandatory pipeline.
- **Maturity is not ceremony.** Level 2 means the process is *documented and repeatable when invoked*, not that it's always invoked. Discipline health is measured by usage, not by labels.

This principle is the governor on all other process improvement. If an improvement makes things heavier without making them better, it's wrong.

## Process Maturity Levels

Two levels describe whether a discipline has formalized its knowledge. Levels are earned by evidence, not declared by intent. Actual discipline health is measured by usage tracking (see the compliance auditor's §6g Discipline Usage Audit), not by levels alone.

### Level 1 — Initial

The discipline exists as a concept. Work happens in the discipline's domain, but it's ad hoc — driven by individual judgment in the moment, not by documented patterns or reusable knowledge.

**What it looks like:**
- Parking lot file exists with seeded or untriaged insights
- No knowledge store directory
- No methodology files, no structured patterns
- Quality of work in this discipline varies by session and depends on whoever is doing it

**Evidence required:** Parking lot file exists with at least one entry.

**Transition trigger to Level 2:** A pattern or methodology has been used successfully in 2+ real sessions and is stable enough to write down.

### Level 2 — Managed

The discipline has documented, reusable knowledge. Methodology exists, patterns are captured, and agents can consult structured files to produce consistent output. The discipline is *repeatable when invoked*.

**What it looks like:**
- Knowledge store directory with at least one structured YAML file
- Agent-context-map wires the knowledge to relevant agents
- Parking lot entries are being triaged (markers applied)
- Methodology or principles documented well enough that a new agent (or person) could follow them

**Evidence required:** Knowledge store with validated files + agent wiring + at least one triage pass on parking lot. *Exception: the process-improvement meta-discipline satisfies Level 2 via `process/` docs (changelog, discipline capture, maturity levels) rather than `knowledge/` YAML files — its "knowledge" is the process documentation itself.*

### Level Rules

1. **Levels are assessed per-discipline, not globally.** Testing can be Level 2 while deployment is Level 1.
2. **Evidence, not declaration.** A discipline is at the level its evidence supports. Saying "Level 2" without a knowledge store is incorrect.
3. **Levels can regress.** If knowledge files go stale (no updates in 90+ days in an active code area), the discipline is effectively operating at Level 1.
4. **Not all disciplines need Level 2.** Deployment at Level 1 may be perfectly sufficient if deploy complexity is low. The "toolbox not recipe" principle applies here too.
5. **The compliance auditor verifies level claims** via §6a (parking lots) and §6b (knowledge stores).

### Level Assessment

**When:** At triage passes, during compliance audits, after major knowledge changes (files created, promoted, moved, or deleted).

**How:**
1. Check the discipline's parking lot: exists? entries triaged? entries added between audits?
2. Check for knowledge store: directory exists? validated YAML files? agent-context-map wired?
3. If evidence satisfies Level 2 criteria but current level is 1 → upgrade. If Level 2 evidence is gone → downgrade.
4. Update the tracker below.

**Who:** CD confirms. Auditor verifies. CC proposes with evidence.

## Parking Lot

*Add process improvement insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **CMMI maturity progression as roadmap.** Promoted → Process Maturity Levels section above. Formal definitions for Levels 1-5 with evidence requirements and transition triggers.

- **Disciplines → Skills progression.** [DEFERRED] Each discipline parking lot is raw material for a future Claude Code skill. The pattern: parking lot insight → `[READY TO PROMOTE]` triage → knowledge YAML → skill definition → skill suite. Each discipline follows the same path at its own pace. *Reason: meta-observation already documented in README and discipline files.*

- **The self-improving loop generalizes.** [NEEDS VALIDATION] A layered knowledge store with a capture-accumulate-feed-forward cycle applies to every discipline. Design knowledge, architecture knowledge, BA knowledge all benefit from the same structure. Consider a generic "discipline knowledge store" template.

- **Cross-discipline remediation flow.** Promoted → `knowledge/architecture/knowledge-management-methodology.yaml` (cross_discipline_remediation section)

- **Disciplines-as-skills orchestration.** [DEFERRED] When individual discipline skills exist, the SDLC becomes an orchestrator that invokes discipline skills at appropriate phases with appropriate intensity. *Reason: future vision, no discipline skills exist yet.*

### Process Maturity Tracker

<!-- PROJECT-TRACKER-START: Do not overwrite during migration. These levels are project-assessed. -->
| Discipline | Level | Evidence |
|-----------|-------|----------|
| Testing | 2 | 7-file knowledge store, testing paradigm, gotchas, tool patterns |
| Design | 2 | 3-file knowledge store, UX modeling methodology, a11y-testability principles |
| Coding | 2 | 3-file knowledge store, code quality principles, TypeScript patterns |
| Architecture | 2 | 17-file knowledge store, comprehensive methodology coverage |
| Data Modeling | 2 | 5-file knowledge store, UDM patterns, assessment templates |
| Product Research | 2 | 5-file knowledge store, competitive analysis methodology, risk assessment |
| Business Analysis | 2 | 1-file knowledge store (requirements-feedback-loops.yaml), agent wiring, all 3 insights promoted |
| Deployment | 1 | Parking lot only, 4 seeded insights |
| Process Improvement | 2 | Changelog, discipline capture pipeline, maturity levels, process docs |

*Last updated: 2026-03-22. Actual discipline health is tracked by the compliance auditor's §6g Discipline Usage Audit, not by levels alone.*
<!-- PROJECT-TRACKER-END -->

