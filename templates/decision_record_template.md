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

## Decision

[One paragraph: what was decided]

## Alternatives Considered

[What else was on the table and why it lost]

## Rationale

[Why this option won — the "why" that's worth preserving]

## Assumptions (unvalidated)

[What has to be true for this decision to be correct]

## Expiration / Revisit Conditions

[When to re-evaluate — market triggers, time bounds, metric thresholds, library version changes, scale crossings]

## References

- **Depends on:** D-XX (planning artifact), DR-YY (prior decision)
- **Informs:** D-ZZ (planned feature), DR-WW (downstream decision)
