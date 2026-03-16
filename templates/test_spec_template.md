# Test: {Feature Name}

**Deliverable:** D{NN} (or "Ad hoc")
**Tags:** @smoke | @regression | @real-time | @multi-client | @visual | @a11y | @performance | @resilience
**Created:** YYYY-MM-DD

---

## Context

[What feature, what page, what scope. One paragraph max. Include the route or entry point, key component names, and relevant state layers so the test author can locate code quickly.]

---

## Prerequisites

[What must be true before any scenario runs. Each prerequisite is a checkable assertion, not prose.]

- [ ] [Frontend service] running at `[frontend-url]` (verify: `GET /` returns 200)
- [ ] [API service] running at `[api-url]` (verify: `GET /health` returns 200)
- [ ] Authenticated via [auth system] (storageState or equivalent loaded)
- [ ] [Seed data requirements — what must exist in the database before tests run]

---

## Acceptance Criteria

[What "done" looks like. Sourced from the upstream spec (if deliverable) or the feature description (if ad hoc). Bulleted, each one verifiable.]

- Criterion 1
- Criterion 2

---

## Risk Areas

[Concerns from architect notes, planning docs, prior test runs, or known gotchas. Each entry: what might go wrong, why, and what to probe. Reference relevant entries from `ops/sdlc/knowledge/testing/gotchas.yaml`.]

| Risk | Source | Gotcha ID | What to probe |
|------|--------|-----------|---------------|
| [Risk description] | [Spec, plan, code review, or prior test] | [gotcha ID or —] | [Specific test action] |

---

## Scenarios

[Test cases. Ordered by priority: happy path → persistence → multi-client → errors → edge cases.]

### Scenario: {Name}

**Steps**:
1. [Action — references element roles/labels, not coordinates]
2. [Action]

**Verify**:
- [ ] [Concrete, checkable assertion]
- [ ] [Assertion — persist-verify for mutations: action → navigate away → return → confirm]

**Testability**:
- [Selector strategy notes — what's stable, what's fragile]
- [DEBT: any testability issues found — missing test IDs, missing aria-labels]

---

## Test Data

[Include subsections as relevant to the feature. Omit subsections that don't apply.]

### Seed Data

[What exists before tests run. Table format.]

| Field | Value | Notes |
|-------|-------|-------|
| [field] | [value] | [why this data exists] |

### Valid Inputs

[Happy path data for create/update scenarios.]

| Case | [Field 1] | [Field 2] | Expected result |
|------|-----------|-----------|-----------------|
| [case name] | [value] | [value] | [outcome] |

### Boundary & Edge Cases

| Case | Input | Boundary tested | Expected behavior |
|------|-------|-----------------|-------------------|
| [case name] | [input] | [what limit] | [accept/reject + why] |

### Search/Filter Cases

[For features using search or client-side filtering.]

| Search/Filter | Should match | Expected count | Why |
|--------------|-------------|----------------|-----|
| [term or filter value] | [matching items] | [N] | [match reason] |

---

## Multi-Client Scenarios

[Only for @real-time/@multi-client features. Describe producer/consumer relationship.]

### Scenario: {Real-Time Feature Name}

**Setup**:
- Client A: [context and URL]
- Client B: [context and URL]
- Both connected to [real-time transport]

**Steps**:
1. [Client A action]
2. [Wait for propagation]

**Verify**:
- [ ] [Client B reflects change]
- [ ] [Message/event conforms to expected contract]

**Contract**:
```
Expected message/event:
  type: [action type]
  payload: { field: type, ... }
```

---

## Resilience Scenarios

[Only for @resilience features. Follow the Chaos Hypothesis Framework.]

### Scenario: {Failure Mode}

**Chaos Experiment:**
- **Steady state:** [What "healthy" looks like — assert before fault injection]
- **Hypothesis:** [When X fails, the UI does Y — not blank screen]
- **Blast radius:** [What's affected, what's NOT affected]
- **Rollback:** [How to restore normal behavior in the test]

**Steps**:
1. Assert steady state
2. Inject fault: [network intercept / offline / service stop / etc.]
3. Assert degraded state
4. Remove fault
5. Assert recovery to steady state

---

## Testability Debt

[Items found during exploration where the code should be more testable.]

| Item | Location | Current state | Proposed fix |
|------|----------|---------------|-------------|
| [what's fragile] | [file:component] | [current selector strategy] | [what to add — test ID, aria-label, etc.] |

---

## Knowledge References

[Pointers to knowledge layers the test author should read before executing. Prevents re-learning.]

- **Gotchas**: `ops/sdlc/knowledge/testing/gotchas.yaml` — [relevant IDs]
- **Components**: `ops/sdlc/knowledge/testing/component-catalog.yaml` — [relevant entries]
- **Timing**: `ops/sdlc/knowledge/testing/timing-defaults.yaml` — [relevant profiles]
- **Tools**: `ops/sdlc/knowledge/testing/tool-patterns.yaml` — [relevant patterns]
