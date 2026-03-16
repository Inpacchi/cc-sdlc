# Architecture Discipline

**Status**: Active — backend capability assessment

## Scope

System design, component boundaries, integration patterns, technology choices, cross-project patterns. Assessing what a backend currently supports and estimating the cost of adding capabilities that unlock desired feature scope.

## Backend Capability Assessment

**When to invoke:** After competitive analysis produces a scoped feature definition with open questions, and before UX modeling finalizes the design. The backend assessment bridges "what should we build?" with "what CAN we build?"

**What it produces:**
- Backend inventory summary (API surface, database, services, auth, existing patterns)
- Capability matrix mapping feature dimensions to support levels (Supported / Partial / New / Infrastructure)
- Cost estimates with T-shirt sizing and dependency chains
- Scope recommendation organized by effort tier (ship now, quick wins, significant investment, revisit later)

**How to use the output:** Map each effort tier back to the competitive analysis scoping questions. This gives the product owner cost-aware information to adjust scope decisions.

**Knowledge store:** `knowledge/architecture/` (see inventory below)

**Pipeline position:**
```
/feature-compare → scope questions → product owner picks target scope
  ↓
/backend-assess → capability matrix, cost estimates    ← THIS
  ↓
/ux-model → IA, wireframes, specs (informed by what's feasible)
  ↓
spec → plan → implement
```

## Knowledge Store Inventory

| File | Domain | Primary Consumers |
|------|--------|-------------------|
| `backend-capability-assessment.yaml` | Capability matrix, cost estimation | [architect] |
| `technology-patterns.yaml` | Stack-specific patterns | [architect], [backend-developer], [build-engineer] |
| `typescript-patterns.yaml` | TypeScript conventions, strict mode patterns | [architect], [frontend-developer], [code-reviewer] |
| `pipeline-design-patterns.yaml` | ETL, data pipeline, background processing patterns | [architect], [data-engineer] |
| `api-design-methodology.yaml` | REST API design, route conventions | [architect], [backend-developer] |
| `deployment-patterns.yaml` | CI/CD, hosting deploy patterns | [architect], [backend-developer], [build-engineer] |
| `agent-communication-protocol.yaml` | Cross-agent structured output format | All agents |
| `knowledge-management-methodology.yaml` | Knowledge store organization patterns | [architect], compliance auditor |
| `debugging-methodology.yaml` | Root cause analysis, investigation workflow | [debug-specialist], [code-reviewer] |
| `investigation-report-format.yaml` | Structured investigation output format | [debug-specialist], [code-reviewer] |
| `error-cascade-methodology.yaml` | Error propagation tracing, failure chains | [debug-specialist], [performance-engineer] |
| `security-review-taxonomy.yaml` | Security assessment categories, OWASP mapping | [security-engineer], [code-reviewer] |
| `risk-assessment-framework.yaml` | Risk scoring, mitigation planning | [architect] |
| `payment-state-machine.yaml` | Payment flow states, gateway integration | [payment-engineer] |
| `ml-system-design.yaml` | ML inference pipelines, model lifecycle | [ml-architect] |
| `prompt-engineering-patterns.yaml` | LLM prompt design, evaluation patterns | [ml-architect] |
| `database-optimization-methodology.yaml` | Query optimization, index strategy | [data-engineer], [backend-developer] |

## Parking Lot

*Add architectural insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Layer 0 (upstream SDLC context) is an architectural function.** The architect sees code being written and flags concerns (race conditions, state management bugs, fragile patterns) that are invisible from the UI. These become targeted test probes. Architecture should feed the testing discipline's risk area section.

- **Two-tier knowledge architecture.** Cross-project knowledge (framework patterns, general conventions) lives in `ops/sdlc/knowledge/`. Project-specific knowledge (routes, data, business logic) lives in the project. This pattern generalizes beyond testing to all disciplines.

- **Token economics as an architectural constraint.** In AI-assisted workflows, token budgets are real constraints. Architecture should consider what patterns are feasible within context budgets. Context window size affects feasibility of large-scale refactors.
