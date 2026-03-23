# Coding Discipline

**Status**: Active — foundational testability architecture codified
**Knowledge store**: `knowledge/testing/testing-paradigm.yaml` (code structure for testability)

## Scope

Implementation patterns, conventions, tech debt management, code review, refactoring strategies.

## Code Structure for Testability

The most impactful coding discipline is structural: **separate I/O from logic**. This is the Functional Core, Imperative Shell pattern. See `knowledge/testing/testing-paradigm.yaml` for the full treatment.

**The rule:** If a function does both I/O (database, filesystem, API calls) and logic (transforms, validation, business rules), split it. The logic half becomes trivially unit-testable with no mocks. The I/O half is thin enough for integration tests against real systems.

**The smell:** If you need a mock to test a function, the function is doing too much. Restructure the code, don't add a mock.

**When planning and reviewing code, apply this lens:**
- Does this function read from a database AND process the result? → Split it.
- Does this API handler validate input AND call an external service? → Split it.
- Does this component fetch data AND render a complex UI? → Separate the data-fetching wrapper from the pure renderer.

This applies during plan review (architects check for I/O-logic entanglement) and code review (reviewers flag functions that mix concerns).

## Parking Lot

*Add coding insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Testability is a code quality concern.** Promoted → `knowledge/coding/code-quality-principles.yaml` (testability_as_code_quality section)

- **Validation gaps found via test data design.** [NEEDS VALIDATION] Designing boundary test cases often reveals missing or incomplete validation in the implementation (e.g., no numeric range validation, no string length limits). These are coding concerns surfaced by the testing discipline. The architect decides whether to fix or accept.

- **Reusable patterns belong in a shared library.** [DEFERRED] When a pattern solves a recurring problem (e.g., a hook pattern for React StrictMode double-mount, or a slot replacement pattern for a UI library), document it as a coding pattern for the shared library — not buried in a single component file. *Reason: generic advice, not actionable until a project builds a patterns library.*

- **Mocking is a code smell.** Promoted → `knowledge/coding/code-quality-principles.yaml` (mocking_stance section)

### Code Assertion Without Verification (Anti-Pattern)

Promoted → `process/collaboration_model.md` (CC Anti-Patterns section, "Code assertion without verification" bullet)
