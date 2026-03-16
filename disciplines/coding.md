# Coding Discipline

**Status**: Parking lot — capturing ideas as they emerge from other work

## Scope

Implementation patterns, conventions, tech debt management, code review, refactoring strategies.

## Parking Lot

*Add coding insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Testability is a code quality concern.** When the testing agent has to use coordinate-based clicks or fragile DOM selectors, the code should change — not just the test. Testability debt items (missing data-testid, no aria-labels, timing-dependent state) are code quality items, triaged by the architect at planning boundaries.

- **Validation gaps found via test data design.** Designing boundary test cases often reveals missing or incomplete validation in the implementation (e.g., no numeric range validation, no string length limits). These are coding concerns surfaced by the testing discipline. The architect decides whether to fix or accept.

- **Reusable patterns belong in a shared library.** When a pattern solves a recurring problem (e.g., a hook pattern for React StrictMode double-mount, or a slot replacement pattern for a UI library), document it as a coding pattern for the shared library — not buried in a single component file.
