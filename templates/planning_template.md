# DNN: Feature Name — Implementation Instructions

**Spec:** `dNN_feature_name_spec.md`
**Created:** YYYY-MM-DD

---

## Overview

[Brief summary of what will be implemented]

---

## Component Impact

| Component / Package | Changes |
|--------------------|---------|
| [name] | [What changes] |
| [name] | [What changes] |

## Interface / Adapter Changes

- [New methods, new fields, or "None — no interface changes"]

## Migration Required

- [ ] No migration needed
- [ ] Database migration: [describe]
- [ ] Storage migration: [describe]

---

## Prerequisites

- [ ] Prerequisite 1 is in place
- [ ] Prerequisite 2 is available

---

## Implementation Steps

### Step 1: [Name]

**Files:** `path/to/file.ext`

[Detailed instructions]

```language
// Code example or pattern to follow
```

### Step 2: [Name]

**Files:** `path/to/file.ext`

[Detailed instructions]

### Step 3: [Name]

[Continue as needed]

---

## Phase Dependencies

| Phase | Depends On | Agent | Can Parallel With |
|-------|-----------|-------|-------------------|
| 1 | — | [agent] | — |
| 2 | Phase 1 | [agent] | Phase 3 |

## Approach Comparison (Medium/Complex only)

| Approach | Description | Key Tradeoff | Selected? |
|----------|-------------|-------------|-----------|
| A: [name] | [2 sentences] | [tradeoff] | ✅ / ❌ + why |
| B: [name] | [2 sentences] | [tradeoff] | ✅ / ❌ + why |

## Agent Skill Loading

| Agent | Load These Skills |
|-------|------------------|
| [agent-name] | [skills to load, e.g., WebSearch if researching external patterns] |

---

## Testing Strategy

<!-- Consider tests-first: if acceptance criteria are clear, write tests as an early
     implementation phase so subsequent phases implement code to pass them. This is
     especially valuable when the spec defines precise expected behavior. -->

### Test Phase Ordering
- [ ] **Tests-first** — Tests written as Phase 1 (or early phase), implementation follows to pass them
- [ ] **Tests-after** — Implementation first, tests written after to verify behavior

### Manual Testing
1. [Test step 1]
2. [Test step 2]

### Automated Tests
- [ ] Unit tests in `path/to/tests`
- [ ] Integration tests in `path/to/tests`

---

## Verification Checklist

- [ ] All implementation steps complete
- [ ] Manual testing passes
- [ ] Automated tests pass
- [ ] No regressions introduced

---

## Spec Deviations

[List any intentional divergences from the spec. If the plan implements the spec exactly, write "None — plan matches spec." If the plan drops, adds, or modifies requirements, declare each deviation with a reason.]

- **[Deviation]**: [What changed from spec and why]

---

## Notes

[Any additional context, gotchas, or references]
