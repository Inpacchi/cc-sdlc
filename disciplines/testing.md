# Testing Discipline

**Status**: Active — codified in `[sdlc-root]/process/overview.md` (Validation phase) and `[sdlc-root]/process/deliverable_lifecycle.md` (Validated/Deployed states)
**Knowledge store**: `[sdlc-root]/knowledge/testing/` (cross-project), project `docs/testing/knowledge/` (project-specific)
**Domain agent**: `.claude/agents/sdet.md` — dispatched for E2E test writing, Playwright suites, WebSocket flow tests, test architecture, and flake diagnosis

## Summary

Hybrid browser testing approach combining an AI-assisted browser tool for SDLC-aware exploration with Playwright CLI for fast, deterministic execution. Self-improving knowledge loop (Layers 0-6) reduces token cost and improves test quality over time. Testability is a first-class code quality concern.

## Testing Paradigm — Code Structure & Test Type Selection

See `[sdlc-root]/knowledge/testing/testing-paradigm.yaml` for the full treatment. Key principles:

**Functional Core, Imperative Shell.** Separate I/O from logic. Pure functions (the core) are unit tested with no mocks. I/O wrappers (the shell) are integration tested against real systems. If you need a mock, the code is structured wrong.

**Test type selection by code layer:**

| Code Layer | Test Type | Mock? |
|------------|-----------|-------|
| Pure logic (transforms, validators, parsers) | Unit test | Never |
| I/O boundary (DB queries, API calls, file ops) | Integration test | Never — hit the real system |
| Wiring (handlers, controllers, main) | Integration or E2E | Rarely |
| User-facing flows | E2E (small, curated suite) | Never for your own services |

**Regression-first for bug fixes.** Write a test that reproduces the bug (red) before fixing it (green). A fix without a regression test is a bug that will return.

**When to write tests.** Not during prototyping (behavior is still being discovered). During implementation stabilization (unit tests for core logic). At feature complete (integration + E2E). At bug fix (regression test first, always).

## Mutation Verification — The Persistence Rule

Any test that validates a write operation (create, update, delete) MUST verify persistence, not just UI response. Optimistic UI updates and HTTP 200s are not proof that data was saved.

**Required sequence for mutation verification:**
1. **Perform** the write action (create, update, delete, link, unlink)
2. **Force state reset** — close the modal, navigate away, or reload the page. This discards all client-side state including optimistic updates, local cache, and component state.
3. **Return** to the same view via fresh navigation (reopen modal, revisit page)
4. **Confirm** the change persisted — the data must reflect the mutation from a fresh server round-trip

**What does NOT count as verification:**
- Seeing the UI update immediately after the action (optimistic update)
- A 200 status code in the network tab (the request succeeded but the backend may not have persisted)
- Console logs showing "success" (frontend interpretation, not server truth)
- The absence of an error (silent failures exist)

**What counts:**
- Server-round-tripped state: data loaded fresh from the API after a full state reset
- A subsequent GET request returning the mutated data
- Reopening the entity and seeing the change reflected

**Why this matters:**
This rule exists because of a real failure mode: a test agent declared a feature "fixed" because the UI updated after the action. The action triggered an optimistic removal from the local list, but the backend returned an auth error — the data was never actually changed. The next time the user opened the record, the "change" had reverted. The test passed, but the feature was broken.

**Shorthand for test specs:** "Persist-verify" or "round-trip verify" — meaning the test must prove the mutation survived a full client reset.

## Active Questions

*(Add per-project as testing matures)*

- Playwright Test Agents integration — CLI works, AI-assisted test generation patterns being evaluated
- Custom spec format — prototype done, needs iteration per project type
- Mobile test suite — confirm Playwright device emulation setup for each project

## Parking Lot

*Add testing insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Cross-discipline**: [DEFERRED] Testability debt remediation flow (tester captures → architect polls → backlog) generalizes to other debt types (design debt, architecture debt, documentation debt). *Reason: duplicate of process-improvement entry; not testing-specific.*

- **Skill readiness**: [DEFERRED] Test spec format sections map to skill input schema; knowledge layers map to skill context loading; scenarios map to skill execution instructions. *Reason: meta-observation about skill design, not testing knowledge.*

- **Element catalog needs an operations layer.** [NEEDS VALIDATION] The element catalog captures elements (nouns — how to find them) and locators (automation access paths). Advanced components (Gantt charts, Kanban boards) need an operations layer (verbs — how to interact): multi-step interaction sequences with choreography, coordinate math, settlement timing, and success verification. Each operation also carries a tool selection dimension (playwright-only for drag, browser tool for visual exploration, either for clicks). Build this when advanced components arrive; the element catalog structure is ready to host it.

- **CLI auto-generates idiomatic locator code.** [NEEDS VALIDATION] When using Playwright's interactive CLI, every command outputs the equivalent Playwright JS. The catalog should capture these directly as the canonical access path.

- **Mobile testing pipeline.** [NEEDS VALIDATION] Playwright's `devices` config (e.g., `devices['Pixel 7']`) enables mobile emulation. Auth fixtures must forward `contextOptions` through the context factory so device emulation (viewport, userAgent, hasTouch, isMobile) carries through. Use viewport-aware storageState cache keys (e.g., `_mobile` suffix for viewports < 768px) to prevent desktop/mobile auth state cross-contamination.

### External Ingestion — 2026-03-30 (Tessl Engineering Blog)

*Bulk import from Tessl Engineering Blog. See `docs/research/Tessl-Engineering-Blog-Reference.md` for full catalog.*

- **Eval contamination masks real weaknesses.** [NEEDS VALIDATION] Tessl discovered that auto-generated evaluation scenarios that included inline file content (CONTRIBUTING.md, AI_POLICY.md) produced 93% baseline scores. Reducing task descriptions to single-sentence prompts with no breadcrumbs dropped the baseline to 15%. The critical test: "Does the agent search for signals nobody highlighted?" — not "Does the agent follow rules when given explicitly?" When designing evals for framework skills, ensure the eval simulates real-world discovery conditions, not open-book conditions. (Source: Tessl "Our AI Is the Bright Kid with No Manners Part 2" — controlled evaluation across 4 demo repos, 7 scenarios)

- **Behavioral compliance is distinct from functional correctness.** [NEEDS VALIDATION] AI agents can produce correct code while failing 85% of behavioral requirements (contribution guidelines, changelog updates, AI disclosure, DCO sign-offs). Traditional test suites only check functional correctness. A separate behavioral compliance evaluation is needed for agent-assisted workflows — especially in OSS contribution, code review, and any context with process rules beyond "does the code work." Promoted to knowledge: `[sdlc-root]/knowledge/testing/ai-generated-code-verification.yaml` (behavioral_compliance section). (Source: Tessl "Our AI Is the Bright Kid with No Manners Part 1" — 15% behavioral compliance despite correct code)

### External Ingestion — 2026-04-22 (Generic test maintenance patterns)

- **Test name vs. scenario consistency.** [NEEDS VALIDATION] Tests whose names contradict their actual assertions are latent maintenance hazards — when a test fails, future engineers debug the named scenario (which was never tested) instead of the real one. Code review of test files should explicitly check that the `it(...)` / `test(...)` name describes what the assertions actually verify. Common drift sources: copy-paste test scaffolding, refactoring assertions without renaming the test, deliberately disabling part of a test without renaming.

- **Stub fixtures must match live API shape.** [NEEDS VALIDATION] When writing dict/JSON fixtures for tests that mock an API or service response, read the live schema (or production payload sample) before authoring the fixture. Hand-written fixtures drift from real shapes within weeks — a field gets renamed, a default changes, a wrapper object is added — and the tests pass against stale shapes while production code paths fail. The discipline: every fixture file has a comment with the source-of-truth path (`# Verified against api/schemas/user.py:42 on 2026-04-22`) and gets re-verified during the next test that touches the same surface.
