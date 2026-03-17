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

- **Testability is a code quality concern.** When the testing agent has to use coordinate-based clicks or fragile DOM selectors, the code should change — not just the test. Testability debt items (missing data-testid, no aria-labels, timing-dependent state) are code quality items, triaged by the architect at planning boundaries.

- **Validation gaps found via test data design.** Designing boundary test cases often reveals missing or incomplete validation in the implementation (e.g., no numeric range validation, no string length limits). These are coding concerns surfaced by the testing discipline. The architect decides whether to fix or accept.

- **Reusable patterns belong in a shared library.** When a pattern solves a recurring problem (e.g., a hook pattern for React StrictMode double-mount, or a slot replacement pattern for a UI library), document it as a coding pattern for the shared library — not buried in a single component file.

- **Mocking is a code smell.** If a unit test requires mocking an internal dependency, the code structure is wrong — not the test. Restructure to separate I/O from logic. Mocks are acceptable only for genuinely external third-party services you cannot control. See `knowledge/testing/testing-paradigm.yaml` for the full mocking stance.
