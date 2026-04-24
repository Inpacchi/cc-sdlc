# Input Quality Gates

Phase-transition gates that score artifact quality before downstream consumption. These catch structural deficiencies early — before agents invest tokens planning from weak research or executing from weak plans.

These are **soft gates**: the orchestrator scores and presents results; the human reviews and decides whether to proceed, revise, or override. They do not block phase advancement automatically.

## Design Principles

1. **Gates validate structure, not correctness** — a passing score means the artifact is well-formed enough for the next phase to consume reliably. Agent review and human judgment own correctness.
2. **AI scores, human reviews** — the orchestrator performs mechanical scoring using the rubric anchors below. The human reviews the score and the artifact before deciding to proceed.
3. **Skip for trivial scope** — single-file changes, config-only work, and SIMPLE complexity (per DISCOVERY-GATE) do not warrant input quality gates. Apply to MEDIUM and COMPLEX work only.

## FAR Gate (Discovery → Spec)

Validates that discovery findings are grounded in evidence before they inform spec writing. Applied in `sdlc-plan` after DISCOVERY-GATE passes (MEDIUM/COMPLEX only), before spec-writing agent dispatch.

Score each discovery finding on three dimensions (0–5):

| Dimension | What It Measures | Threshold |
|-----------|-----------------|-----------|
| **Factual** | Grounded in codebase evidence (file refs, code citations), not assumption? | ≥ 4 |
| **Actionable** | Informs a concrete design or implementation decision? | ≥ 3 |
| **Relevant** | Pertains to the deliverable's stated scope? | ≥ 3 |

### Scoring Anchors

**Factual:**
- 2 — Indirect (mentioned in docs, not verified in code)
- 3 — Provisional (partial code reference, plausible but unconfirmed)
- 4 — Corroborated (verified via grep/LSP, call graph checked)
- 5 — Strongly verified (multiple methods, exact file:line references)

**Actionable:**
- 2 — Directional but vague (hypothesis exists, unclear next step)
- 3 — Concrete next step (specific file/function identified)
- 4 — Clear path (small change scope, risk noted)
- 5 — Immediate (validation path obvious)

**Relevant:**
- 2 — Adjacent (related area, not blocking)
- 3 — On-theme (affects acceptance criteria)
- 4 — Core (blocks the deliverable, within scope)
- 5 — Critical path (unblocks the primary objective)

### Pass Criteria

All three per-dimension thresholds met: F ≥ 4, A ≥ 3, R ≥ 3.

### On Failure

Flag low-scoring findings with their scores. Recommended actions:
- F < 4: re-search codebase, verify with grep/LSP before proceeding
- A < 3: clarify how the finding informs a decision, or discard
- R < 3: set aside — may be useful later but should not drive spec scope

The human decides whether to re-research, discard, or proceed with acknowledged gaps.

## FACTS Gate (Plan → Review)

Validates that a plan's phases are well-formed before agents review them. Applied in `sdlc-plan` after plan is written (before plan review) and in `sdlc-lite-plan` after plan is written (before plan review).

Score each phase on five dimensions (0–5):

| Dimension | What It Measures | Floor |
|-----------|-----------------|-------|
| **Feasible** | Implementable with available tools, APIs, and patterns? | — |
| **Atomic** | Single, independently completable unit of work? | — |
| **Clear** | Would a different agent interpret this the same way? | ≥ 3 |
| **Testable** | Concrete way to verify completion? | ≥ 3 |
| **Scoped** | Stays within stated boundaries? | — |

### Scoring Anchors

**Feasible:**
- 2 — Requires significant investigation or unavailable tooling
- 3 — Achievable with available tools, minor investigation needed
- 4 — Straightforward with known patterns
- 5 — Configuration-only or trivial change

**Atomic:**
- 2 — Spans multiple systems, unclear boundaries
- 3 — Single responsibility, 2–5 file changes
- 4 — Focused unit, clear start and end
- 5 — Indivisible, single file change

**Clear:**
- 2 — Ambiguous, multiple interpretations possible
- 3 — Intent understood, minor clarification might be needed
- 4 — Unambiguous, execution path obvious
- 5 — Step-by-step, no interpretation required

**Testable:**
- 2 — Verification requires subjective judgment
- 3 — Clear pass/fail criteria, may need manual verification
- 4 — Automated test can verify
- 5 — Existing test infrastructure covers this

**Scoped:**
- 2 — Touches adjacent systems, scope creep likely
- 3 — Focused with clear boundaries
- 4 — Well-bounded, out-of-scope items listed
- 5 — Minimal surface area, self-contained

### Pass Criteria

Mean ≥ 3.0 across all five dimensions, AND C ≥ 3, AND T ≥ 3.

The per-dimension floors on Clarity and Testability prevent ambiguous or unverifiable phases from being averaged away by high scores elsewhere.

### On Failure

Recommended actions based on score range:
- C < 3 or T < 3 on any phase: revise that phase for clarity or testability
- Mean 2.5–2.9: revise low-scoring phases, re-score
- Mean < 2.5: plan likely needs restructuring

The human decides whether to revise, proceed with caveats, or restructure.

### Lite Plan Notes

Lite plans use the same FACTS dimensions and thresholds. Code snippets in lite plans (encouraged by the template) count as Clarity evidence — a phase with concrete signatures or diffs scores higher on C than prose-only descriptions.

## Output Format

Both gates produce a compact scoring block appended to the orchestrator's output:

```
── FAR Gate ──────────────────────────────
Finding 1: [summary]     F:4  A:3  R:4  → PASS
Finding 2: [summary]     F:3  A:3  R:4  → FAIL (F<4)
Finding 3: [summary]     F:5  A:4  R:5  → PASS
──────────────────────────────────────────
```

```
── FACTS Gate ────────────────────────────
Phase 1: [name]  F:4  A:3  C:4  T:3  S:4  Mean:3.60 → PASS
Phase 2: [name]  F:3  A:3  C:2  T:3  S:3  Mean:2.80 → FAIL (C<3)
Phase 3: [name]  F:4  A:4  C:4  T:4  S:3  Mean:3.80 → PASS
──────────────────────────────────────────
Overall Mean: 3.40  |  Floors: C≥3 ✗ (Phase 2)  T≥3 ✓
```

## What These Gates Do NOT Catch

- **Correctness** — a plan can score well on FACTS while describing the wrong approach. Agent review and human judgment own correctness.
- **Architecture fitness** — whether the approach fits the system is a domain judgment. Tier 2 agent dispatch (software-architect) catches this.
- **The plan-reading illusion** — plans that read coherently but contain flawed assumptions pass FACTS. FACTS is necessary but not sufficient.

## Research Basis

- Robinson, `patrob/rpi-strategy` (2025) — formalized FAR/FACTS numeric rubrics within the RPI methodology
- Horthy / HumanLayer (2024) — originated the qualitative FAR/FACTS criteria
- Horthy, "Everything We Got Wrong About RPI" (2025) — documented the plan-reading illusion as the primary limitation of plan quality scoring
- mmanzini/rpi-methodology (2025) — acknowledged absence of empirical validation for thresholds; no inter-rater reliability testing exists
- Per-dimension floors on C and T: this framework's addition, addressing the documented mean-only threshold flaw where ambiguous or unverifiable tasks get averaged away
