---
type: decision-record
status: active             # active | superseded | expired
decided: YYYY-MM-DD
decider: cd                # cd | role-name (e.g., software-architect, chief-product-officer) | joint
triggered_by: ""           # D-number, DR-number, idea brief, external signal, or ad hoc
depends_on: []             # [DR-1, D-59] or empty
informs: []                # [D-61, DR-5] or empty
---

# DR-NN: [Decision Title]

**Status:** Active | Superseded by DR-XX | Expired
**Decided:** YYYY-MM-DD
**Decider:** CD / role-name / joint
**Triggered by:** D-number, DR-number, idea brief, external signal, or ad hoc

## Context

[What forced this decision — problem statement, constraints, scope. Future readers cannot reconstruct rationale without this.]

## Decision Drivers

[The specific criteria the decision was scored against — must-haves vs nice-to-haves]

## Decision

[One paragraph: what was decided]

## Alternatives Considered

[What else was on the table and why it lost. At least two options; "do nothing" is valid when reversibility is asymmetric.]

## Rationale

[Why this option won — the "why" that's worth preserving]

## Consequences

**Positive:**
- [Expected benefit]

**Negative:**
- [Honest cost or tradeoff]

**Risks:**
- [Risk — mitigation]

## Assumptions (unvalidated)

[What has to be true for this decision to be correct]

## Implementation Notes

[Links to migrations, fitness functions, observed metrics. Fill in as the decision is implemented.]

## Expiration / Revisit Conditions

[When to re-evaluate — market triggers, time bounds, metric thresholds, library version changes, scale crossings]

## References

- **Depends on:** D-XX (planning artifact), DR-YY (prior decision)
- **Informs:** D-ZZ (planned feature), DR-WW (downstream decision)
