# Deliverable Lifecycle

## States

```
[Draft] → [Ready] → [In Progress] → [Validated] → [Deployed] → [Complete] → [Archived]
                 ↘ [Blocked] ↗
```

### Draft
Spec exists but is incomplete or under review.
- File: `dNN_name_spec.md`
- Status marker in file: `**Status:** Draft`

### Ready
Spec is approved and has planning/instructions.
- Files: spec + planning + optional prompt
- Status marker: `**Status:** Ready`

### In Progress
Implementation is underway.
- CC is actively working on it
- Status marker: `**Status:** In Progress`

### Blocked
Work cannot proceed.
- File: `dNN_name_BLOCKED.md` in `issues/`
- Contains: what's blocked, why, what's needed

### Validated
Implementation passes all testing gates.
- Phase 1 (exploratory testing): all scenarios pass
- Phases 2-3 (test specs + test generation): test files created
- Phase 4 (test execution): all tests green
- Testing knowledge updated
- Status marker: `**Status:** Validated`

### Deployed
Code is live in staging/production and verified.
- Deployment completed per project deployment docs
- Post-deploy smoke tests pass (health checks, auth, key endpoints)
- Seed data verified if applicable
- Status marker: `**Status:** Deployed`

**Note:** CD may authorize early deployment for human review while tests run in parallel. In this case, the deliverable moves to Deployed before Validated, but cannot move to Complete until both gates pass.

### Complete
Implementation is finished, validated, and deployed.
- File: `dNN_name_result.md` in `results/`
- Includes: test results, deploy verification
- Status marker: `**Status:** Complete`

### Archived
Moved to chronicles for long-term reference.
- Files moved to `chronicle/` under the appropriate concept
- Removed from `current_work/`

---

## Transitions

### Draft → Ready
- Spec is reviewed and approved
- Planning document is written
- Optional: CC prompt is prepared

### Ready → In Progress
- CC begins implementation
- Or: human begins implementation

### In Progress → Validated
- Code compiles clean
- Exploratory testing passes (Phase 1)
- Test specs written (Phase 2)
- Tests generated and passing (Phases 3-4)
- Testing knowledge files updated

### Validated → Deployed
- Prerequisite: Validated state reached (all tests green)
- Code deployed to target environment
- Post-deploy smoke tests pass

### Deployed → Complete
- Both Validated and Deployed states confirmed
- Result document created with full test + deploy outcomes

### In Progress → Blocked
- Obstacle encountered
- Issue document created
- Work pauses until resolved

### Blocked → In Progress
- Blocker resolved
- Issue document updated or removed
- Work resumes

### Complete → Archived
- Periodic chronicle organization
- Files moved to appropriate concept/step
- `_index.md` updated

---

## File Naming

| State | File Pattern |
|-------|--------------|
| Draft/Ready | `dNN_name_spec.md` |
| Planning | `dNN_name_plan.md` |
| Complete | `dNN_name_result.md` |
| Blocked | `dNN_name_BLOCKED.md` |

---

## Status Markers

Every spec should have a status block at the top:

```markdown
# DNN: Feature Name — Specification

**Status:** Draft | Ready | In Progress | Complete
**Created:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**Depends On:** D1, D5 (if any)
```
