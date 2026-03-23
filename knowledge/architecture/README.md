# Architecture Knowledge Store — Cross-Project

Knowledge for assessing backend capabilities and estimating the cost of adding infrastructure that unlocks feature scope. When competitive analysis identifies what's desirable and the product owner defines target scope, this knowledge guides an agent through understanding what the backend already supports and what it would take to close the gaps.

## Structure

```
knowledge/architecture/
├── README.md                                  ← This file
├── agent-communication-protocol.yaml         ← Cross-agent progress update and handoff protocol
├── api-design-methodology.yaml               ← REST maturity, versioning, webhooks, SDK strategy
├── backend-capability-assessment.yaml         ← Process an agent follows end-to-end
├── database-optimization-methodology.yaml     ← Query optimization, index strategy, bloat thresholds
├── debugging-methodology.yaml                 ← 6-phase RCA framework for cross-system investigation
├── deployment-patterns.yaml                   ← DORA metrics, GitOps, feature flags, supply chain
├── domain-boundary-gotchas.yaml               ← Cross-domain work patterns and orchestrator signals
├── error-cascade-methodology.yaml             ← Cascade failure taxonomy, forensic timelines
├── investigation-report-format.yaml           ← Structured output format for investigation agents
├── knowledge-management-methodology.yaml      ← Pattern taxonomy, validation, two-tier architecture
├── ml-system-design.yaml                      ← ML pipelines, confidence gates, active learning
├── payment-state-machine.yaml                 ← Payment FSM, audit trail, webhook idempotency
├── pipeline-design-patterns.yaml              ← Idempotent pipelines, content hashing, rollback
├── prompt-engineering-patterns.yaml           ← LLM prompt design, evaluation, token economics
├── security-review-taxonomy.yaml              ← 7-domain security review, OWASP mapping
└── technology-patterns.yaml                   ← Reusable patterns by concern (search, real-time, auth, etc.)
```

## How This Gets Used

1. Competitive analysis produces a scoped feature definition with open questions
2. The product owner picks a target scope
3. An agent loads the assessment methodology and examines the backend codebase
4. The technology patterns catalog helps identify what to look for in specific stacks
5. The agent produces a capability matrix and scope recommendation
6. The product owner adjusts scope based on cost/benefit reality

## Pipeline Position

```
/feature-compare  → what competitors do, scope questions
  ↓
/backend-assess   → what backend supports, cost to add    ← THIS
  ↓
/ux-model         → IA, wireframes, specs
  ↓
spec → plan → implement
```

## Relationship to Other Knowledge Stores

- **`knowledge/product-research/`** — produces the competitive scope that feeds into assessment
- **`knowledge/design/`** — consumes the assessment output to model realistic UX
- **`knowledge/data-modeling/`** — UDM patterns inform what data layer capabilities to expect

## Skill Trajectory

This knowledge feeds a future `/backend-assess` skill:
```
/backend-assess "cross-conversation search for chat"
/backend-assess "real-time notifications with WebSocket"
/backend-assess "full-text search with fuzzy matching"
```

## Maintenance

- Updated when backend assessments reveal new patterns worth generalizing
- Technology patterns grow as new stacks and infrastructure are encountered
- Assessment methodology refined based on what produces the most useful scope recommendations
