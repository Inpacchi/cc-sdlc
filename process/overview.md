# SDLC Process Overview

## The Flow

```
Idea → Spec → Planning → Implementation → Validation → Deploy → Result → Chronicle
```

### 1. Idea
A feature, fix, or improvement is identified. Assign a deliverable ID: **D1, D2, ... Dnn**

### 2. Spec
Create `docs/current_work/specs/dNN_name_spec.md`
- Define the problem
- Specify requirements
- Design the approach
- Set success criteria

### 3. Planning
Create `docs/current_work/planning/dNN_name_plan.md`
- Step-by-step implementation guide
- Specific files and functions to modify
- API signatures and patterns to follow

### 4. Implementation
CC (or human) executes the work:
- Follow the planning document
- Create/modify code
- Run tests

### 5. Validation (stage gate)
A deliverable is not deployable until it passes validation. Validation follows the **5-phase hybrid testing workflow**:

| Phase | Tool | Output |
|-------|------|--------|
| **1. Explore** | Browser testing tool | Exploratory testing — verify features work, discover issues |
| **2. Specify** | CC | Test specs in markdown format (`docs/testing/specs/dNN_name.spec.md`) |
| **3. Generate** | CC / Test Agents | Executable test files in your test directory |
| **4. Execute** | Test CLI | Deterministic test run — all tests must pass |
| **5. Heal** | CC / Healer Agent | Auto-repair failing tests when UI changes (future runs) |

**Minimum bar:** Phases 1-4 must complete with all tests passing before proceeding to Deploy. Phase 5 applies to subsequent runs when existing tests break due to new changes.

**Knowledge capture:** Each validation cycle updates project-specific testing knowledge. Cross-project knowledge updates go to your SDLC knowledge store (`ops/sdlc/knowledge/testing/`).

**When to skip phases:** Ad hoc work (bug fixes, UI tweaks <30 min) may skip Phases 2-4 if Phase 1 (exploratory) provides sufficient confidence. Document the rationale in the result doc.

### 6. Deploy (stage gate)
Deployment is gated by validation:
- **Prerequisite:** All tests pass (Phase 4 green)
- **Action:** Deploy to staging/production per project deployment docs
- **Verification:** Post-deploy smoke test (health checks, auth, key endpoints)
- **Parallel option:** CD may authorize early deployment for human review while tests run in parallel, but the deliverable is not marked Complete until both gates pass

A deliverable deployed without passing validation remains **In Progress**, not Complete.

### 7. Result
Create `docs/current_work/results/dNN_name_result.md`
- What was implemented
- Files changed
- Test outcomes
- Deploy verification
- Any deviations

### 8. Chronicle
Periodically move completed work to `docs/chronicle/`, organized by concept (domain/feature area). Chronological ordering is tracked by the deliverable catalog and git history.

---

## Roles

### CD (Claude Director / Human)
- Defines what to build (specs)
- Reviews proposals and results
- Makes architectural decisions
- Guides priority and scope

### CC (Claude Code)
- Proposes approaches
- Implements features
- Asks clarifying questions
- Documents completion

---

## Working Locations

### `current_work/`
Active deliverables in progress:
```
current_work/
├── specs/           # What to build
├── planning/        # How to build it
├── results/         # Completion records
└── issues/          # Blocked items
```

### `chronicle/`
Completed work organized by concept:
```
chronicle/
├── authentication/
│   ├── _index.md    # Navigation and context
│   ├── specs/
│   ├── planning/
│   └── results/
├── data_model/
└── ...
```

---

## Deliverable IDs

- Sequential across entire project: D1, D2, D3, ...
- Never reused, even if work is abandoned
- Used in filenames: `d42_memory_formation_spec.md`
- Referenced in commits: "feat: implement D42 memory formation"

---

## File Suffix Convention

All documentation files carry a type suffix so that a file's purpose is self-evident regardless of where it lives.

| Type | Suffix | Example |
|------|--------|---------|
| Specification | `_spec.md` | `d42_memory_formation_spec.md` |
| Planning/Instructions | `_plan.md` | `d42_memory_formation_plan.md` |
| Result | `_result.md` | `d42_memory_formation_result.md` |
| Issue/blocker | `_BLOCKED.md` | `d42_memory_formation_BLOCKED.md` |

**Why this matters:**
1. **Context-free identification** — A file named `tpv_research_spec.md` is unambiguously a spec in a directory listing, git log, grep result, or cross-agent chat
2. **Multi-agent workflows** — When CD and multiple CC instances share file references, the suffix eliminates "which file do you mean?"
3. **Search and automation** — `find . -name "*_result.md"` finds all results; `*_spec.md` finds all specs
4. **Directory structure is additive** — The directory (`specs/`, `planning/`) still provides organization, but the suffix ensures the file is self-describing even without it

---

## When to Chronicle

Archive completed work when:
- A logical milestone is reached
- `current_work/` is getting cluttered (>20 active items)
- Starting a new phase of work
- Context refresh is needed

See `chronicle_organization.md` for detailed process.

---

## Tester Knowledge Capture

When a tester agent (human or AI) completes a test pass, the test results document should include a **Navigation & Learnings** section that captures reusable knowledge:

### Required Sections in Test Results

**Navigation Paths** — How to reach each test area:
- Exact URLs, click sequences, scroll directions needed
- UI quirks (e.g., "must scroll right to see Actions column")
- Which icons/buttons to click and where they are

**Lessons Learned** — What future testers should know:
- Common gotchas encountered during testing
- Data prerequisites (e.g., "need at least one assigned user to test unassign")
- Timing issues (e.g., "wait for toast to dismiss before re-opening flyout")
- Environment-specific notes (e.g., "dev has no email data populated")

**Why this matters:** Testing the same UI areas repeatedly is expensive. Captured navigation paths let future test runs skip the discovery phase and go straight to verification. This compounds — each test pass makes the next one faster and more thorough.

---

## Updating This Process

When the team discovers process improvements, gaps, or new conventions during real work:

**Trigger:** Say **"Let's update the SDLC"**

CC will:
- Read the current SDLC changelog at `process/sdlc_changelog.md`
- Discuss the proposed addition or change
- Update the relevant canonical files
- Append to the changelog with date, description, and rationale
- Wait for approval before committing

The changelog serves as a living record of how the process evolves through use. Not every change needs a formal proposal — often the best improvements emerge from noticing friction during real work.

See `process/sdlc_changelog.md` for the change history.

---

## Key Principles

1. **Specs before code** — Define what before implementing how
2. **Explicit over implicit** — Document decisions and rationale
3. **Centralized by concept** — Related work belongs together
4. **Indexes for navigation** — `_index.md` enables targeted context loading
5. **Archives preserve memory** — Chronicles are long-term project memory
6. **Process accommodates reality** — Ad hoc work is legitimate; reconcile periodically
7. **Capture testing knowledge** — Tester navigation paths and learnings compound across runs
8. **Validation before deployment** — Tests must pass before code ships
9. **Deploy is a process step** — Not an afterthought; gated by validation, verified by smoke tests

## Tooling Integration

### oberskills Plugin

Quality gates for agent dispatch, prompt engineering, writing, and research. Invoked automatically by the planning and execution skills when the plugin is installed.

| Skill | Integrated Into | Purpose |
|-------|----------------|---------|
| oberagent | Planning + Execution (agent dispatch) | Validates agent prompts before dispatch |
| oberprompt | oberagent (auto-invoked) | Constraint budget and prompt quality |
| oberweb | Planning (research phase) | Multi-dimensional web research |

See `ops/sdlc/optional/oberskills-setup.md` for installation instructions.

### CHECKER/APPLIER Pattern

Both planning and execution skills support dual modes:
- **APPLIER** (default): Creates new artifacts — full workflow
- **CHECKER**: Audits existing artifacts against criteria — structured review

### PRE-GATE / POST-GATE

Execution phases are gated:
- **PRE-GATE**: Verify dependencies satisfied, prepare dispatch prompt
- **POST-GATE**: Verify build passes, check file changes match plan, document deviations

---

## Ad Hoc Work

Not everything needs the full Spec → Planning → Result flow.

**Legitimate ad hoc work:**
- Bug fixes and CC corrections
- UI tweaks (move a button, adjust spacing)
- Missed requirements discovered during implementation
- Quick iterations based on feedback

**When to go ad hoc:**
- Work is small (<30 min)
- It's a correction, not a new feature
- Full spec would be overhead

**Reconciliation:** Periodically say **"Let's catalog our ad hoc work"** to:
- Review what was done since last formal deliverable
- Update specs if requirements changed
- Create lightweight completion records if needed
- Resume formal process cleanly

See `ad_hoc_reconciliation.md` for the full process.

---

## Compliance Auditing

Periodically verify the project follows SDLC standards:

**Trigger:** Say **"Let's run an SDLC compliance audit"**

CC will:
- Check CLAUDE.md for compliance section and commands
- Verify all file references are valid
- Confirm `_index.md` coverage in concept chronicles
- Check templates and current_work hygiene
- Produce a proposal with gaps, severity ratings, and recommended fixes
- Wait for approval before making changes

See `compliance_audit.md` for the full process.
