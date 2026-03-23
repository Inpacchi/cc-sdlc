---
name: sdlc-tests-create
description: >
  Generate integration and E2E test suites for completed work by dispatching the SDET agent.
  Analyzes scope (SDLC plan, SDLC-Lite plan, specific commit, or unstaged changes), designs test
  cases covering happy paths, edge cases, and error scenarios, implements them, then hands off
  to sdlc-tests-run for the red-green fix cycle.
  Trigger when someone says "create tests", "write tests", "generate test suite",
  "create test suite", "test this work", "write tests for this", or after completing
  a deliverable or SDLC-Lite execution.
  Do NOT use for running or fixing existing tests — use sdlc-tests-run for that.
---

# Create Test Suite

Dispatch the SDET agent to design and implement tests for completed work. You are the manager — you identify what was built, gather scope context, and dispatch. The SDET agent decides test cases, writes the tests, and verifies they compile. Then hand off to `sdlc-tests-run`.

## Manager Rule

**You never write test code.** The SDET agent designs test cases, implements tests, and fixes test compilation issues. If you notice a gap in test coverage, dispatch SDET to address it. Do not write test files, fixtures, or helpers yourself.

## Step 0: Identify Scope

Determine what work needs tests. If the user didn't specify, ask:

```
What work should I create tests for?

1. The current SDLC deliverable plan (docs/current_work/planning/)
2. The current SDLC-Lite plan (docs/current_work/sdlc-lite/)
3. A specific commit (provide SHA or "HEAD")
4. Unstaged changes in the working tree
```

Use `AskUserQuestion` — do not type this as conversational text.

**Also ask:** "Any specific test cases you want included?" Accept the user's suggestions and pass them to the SDET agent in the dispatch prompt.

If the user already specified scope and test cases (or said none), skip the questions.

### Scope Resolution

| Source | How to gather context |
|--------|----------------------|
| SDLC plan | Read `docs/current_work/planning/dNN_name_plan.md` — extract phases, files, acceptance criteria |
| SDLC-Lite plan | Read `docs/current_work/sdlc-lite/dNN_{slug}_plan.md` — extract phases, files, acceptance criteria |
| Specific commit | Run `git show --stat {sha}` + `git diff {sha}~1 {sha}` — extract changed files and diff |
| Unstaged changes | Run `git diff` + `git diff --cached` — extract changed files and diff |

Extract from the scope:
1. **Changed files** — what was created or modified
2. **Packages affected** — which packages or layers
3. **User-facing behavior** — what a user would interact with
4. **Acceptance criteria** — from plan if available, otherwise infer from the diff

## Step 1: Dispatch SDET to Design and Implement

Dispatch `sdet` with a single prompt that covers both design and implementation.

**Cross-domain knowledge injection:** The SDET is testing code written by domain agents (frontend, backend, etc.). Consult `ops/sdlc/knowledge/agent-context-map.yaml` for the agents who built the feature being tested and include their domain knowledge files in the SDET's dispatch prompt. This helps the SDET understand domain patterns, data flows, and known gotchas in the code under test.

The dispatch prompt must include:
- The scope context gathered in step 0 (changed files, packages, acceptance criteria)
- Any user-suggested test cases
- Cross-domain knowledge file paths from the feature's domain agents
- **Library verification instructions** (when tests involve external library APIs — test frameworks, assertion libraries, mocking tools): verify API usage via Context7 (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`) before writing tests. Include the test framework name and version from the project's dependency files.
- These instructions:

```
Design and implement tests for the following completed work.

SCOPE:
[paste scope context]

USER-REQUESTED TEST CASES:
[paste user suggestions, or "None specified"]

GUIDELINES:
- Apply the testing paradigm from ops/sdlc/knowledge/testing/testing-paradigm.yaml:
  - Unit test pure logic (transforms, validators, parsers) — no mocks needed
  - Integration test I/O boundaries (DB queries, API calls) — hit real systems
  - E2E test critical user flows — small, curated suite
  - If a function mixes I/O and logic, flag it as a testability issue — don't mock around it
- Design test cases from a real user's perspective — what would a user do?
- Cover: happy paths, edge cases, error scenarios. Use your judgment on which
  edge cases matter.
- Tests live in the [test directory per project CLAUDE.md]. Follow existing conventions
  in the test config and existing test files.
- Use existing fixtures and helpers where applicable.
- Check for existing tests that already cover this area — avoid duplication.
- Read the source files under test before writing selectors or assertions.
- Verify the tests compile by running the test list command for your framework.
```

**Do not constrain the SDET agent's test case selection.** The agent has domain expertise in what to test. Your role is to provide complete scope context, not prescribe test cases (except for user-requested ones).

## Step 2: Verify and Hand Off

After SDET returns:

1. **Check that test files were created** — verify via `git diff --stat` or agent report
2. **Run a compilation check** — run the test list command for your framework on the new test files to confirm they parse
3. **Invoke `sdlc-tests-run`** — hand off to the sdlc-tests-run skill targeting the newly created test files

```
Test suite created. Handing off to sdlc-tests-run to run and fix.
Target: tests/{path-to-new-tests}
```

If compilation check fails, re-dispatch SDET with the error output. Do not fix test code yourself.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll write a quick test myself" | SDET writes all test code. Manager Rule. |
| "I'll specify exactly which test cases to write" | Provide scope context, not test prescriptions. SDET has domain expertise. |
| "Skip sdlc-tests-run, the tests already pass" | sdlc-tests-run catches what a single run misses. Always hand off. |
| "Let me ask if they want to run sdlc-tests-run" | Step 2 says invoke sdlc-tests-run, not ask about it. Hand off automatically. |
| "The scope is obvious, skip step 0" | Ask if not specified. Wrong scope = wrong tests. |
| "Unit tests are enough for this" | Default to integration/E2E. Unit tests only where they genuinely fit. |
| "I'll fix the compilation error, it's one line" | Re-dispatch SDET. Size is not an exception. |

## Integration

- **sdlc-tests-run** — Receives the created tests and runs the red-green fix cycle
- **sdlc-execute** — Can be invoked after execution completes to generate tests for the deliverable
- **sdlc-lite-execute** — Same — invoke after SDLC-Lite work to generate tests
