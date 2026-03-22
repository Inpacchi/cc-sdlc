# Process Improvement Discipline

**Status**: Parking lot — meta-discipline for improving the SDLC itself

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
- **Maturity is not ceremony.** Moving from CMMI Level 1 to Level 2 means the process is *documented and repeatable when invoked*, not that it's always invoked.

This principle is the governor on all other process improvement. If an improvement makes things heavier without making them better, it's wrong.

## Parking Lot

*Add process improvement insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **CMMI maturity progression as roadmap.** Level 1 (ad hoc) → Level 2 (managed, documented) → Level 3 (standardized across projects) → Level 4 (measured) → Level 5 (self-improving). Build Level 2 with the architecture to support 3-5. Each level is earned by demonstrating it works at the current level.

- **Disciplines → Skills progression.** Each discipline parking lot is raw material for a future Claude Code skill. The pattern: parking lot insight → `[READY TO PROMOTE]` triage → knowledge YAML → skill definition → skill suite. Each discipline follows the same path at its own pace.

- **The self-improving loop generalizes.** A layered knowledge store with a capture-accumulate-feed-forward cycle applies to every discipline. Design knowledge, architecture knowledge, BA knowledge all benefit from the same structure. Consider a generic "discipline knowledge store" template.

- **Cross-discipline remediation flow.** One discipline captures factual observations → knowledge store → another discipline polls at planning boundaries → triages into backlog. Example: tester captures testability gaps → architect polls at planning boundaries → triages into backlog. The same flow applies to any discipline pair.

- **Disciplines-as-skills orchestration.** When individual discipline skills exist, the SDLC becomes an orchestrator that invokes discipline skills at appropriate phases with appropriate intensity.

### Process Maturity Tracker

| Discipline | Starting Level | Next Level Target |
|-----------|----------------|-------------------|
| Testing | 1 (Initial) | 2 — document patterns, knowledge store, spec format |
| Design | 1 (Initial) | 2 — document patterns from component library |
| Coding | 1 (Initial) | 2 — formalize coding patterns library |
| Architecture | 1 (Initial) | 2 — formalize architecture decision records |
| Business Analysis | 1 (Initial) | 2 — structured requirements templates |
| Product Research | 1 (Initial) | 1 — capture initial questions |
| Deployment | 1 (Initial) | 2 — generalize across projects |
| Process Improvement | 2 (Managed) | 3 — self-improving via discipline feedback |

*Update this tracker as disciplines mature on each project that adopts this framework.*
