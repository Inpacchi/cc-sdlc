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

**Knowledge store:** `[sdlc-root]/knowledge/architecture/` (see inventory below)

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
| `pipeline-design-patterns.yaml` | ETL, data pipeline, background processing patterns | [architect], [data-engineer] |
| `api-design-methodology.yaml` | REST API design, route conventions | [architect], [backend-developer] |
| `deployment-patterns.yaml` | CI/CD, hosting deploy patterns | [architect], [backend-developer], [build-engineer] |
| `agent-communication-protocol.yaml` | Cross-agent structured output format | All agents |
| `knowledge-management-methodology.yaml` | Knowledge store organization patterns | [architect], compliance auditor |
| `debugging-methodology.yaml` | Root cause analysis, investigation workflow | [debug-specialist], [code-reviewer] |
| `investigation-report-format.yaml` | Structured investigation output format | [debug-specialist], [code-reviewer] |
| `error-cascade-methodology.yaml` | Error propagation tracing, failure chains | [debug-specialist], [performance-engineer] |
| `security-review-taxonomy.yaml` | Security assessment categories, OWASP mapping | [security-engineer], [code-reviewer] |
| `payment-state-machine.yaml` | Payment flow states, gateway integration | [payment-engineer] |
| `ml-system-design.yaml` | ML inference pipelines, model lifecycle | [ml-architect] |
| `prompt-engineering-patterns.yaml` | LLM prompt design, evaluation patterns | [ml-architect] |
| `domain-boundary-gotchas.yaml` | Cross-domain work patterns, orchestrator signals | [architect], [code-reviewer] |
| `token-economics.yaml` | Context window constraints on AI-assisted workflows | [architect] |
| `database-optimization-methodology.yaml` | Query optimization, index strategy | [data-engineer], [backend-developer] |

## Parking Lot

*Add architectural insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Layer 0 (upstream SDLC context) is an architectural function.** Promoted → `[sdlc-root]/knowledge/architecture/domain-boundary-gotchas.yaml` (architect-feeds-testing-risk-areas entry)

- **Two-tier knowledge architecture.** Promoted → `[sdlc-root]/knowledge/architecture/knowledge-management-methodology.yaml` (two_tier_architecture section)

- **Token economics as an architectural constraint.** Promoted → `[sdlc-root]/knowledge/architecture/token-economics.yaml`

### External Ingestion — 2026-04-22 (Generic patterns from production systems)

- **Async concurrency: pass a session/connection factory, never a shared session.** [NEEDS VALIDATION] In any async runtime (Python asyncio, Node.js, Go), passing a single shared database session/connection to multiple concurrent tasks produces silent corruption — the tasks interleave their statements on one connection. Pass a `session_factory` (callable returning a fresh session) instead, and have each task open its own. The same applies to HTTP clients with connection state, transaction handles, and any resource that has implicit per-call state. Document this in any architecture doc that introduces concurrent task fan-out.

- **Advisory lock + connection pooling release locks silently.** [NEEDS VALIDATION] Database advisory locks (Postgres `pg_advisory_lock`, MySQL `GET_LOCK`, etc.) are scoped to the connection that acquired them. When the connection is returned to a pool mid-job, the lock releases — but the application code thinks it still holds the lock. Either pin the connection for the duration of the locked work, or use a different coordination primitive (Redis lock, distributed lock service). Same hazard exists with `SET LOCAL` Postgres settings, prepared statements, and any session-level state.

- **Lazy initialization needs a short-circuit for tests.** [NEEDS VALIDATION] Service-level "initialize on first request" patterns (resolving config, loading models, opening connections) require an `_initialized` flag and a way to short-circuit it in tests. Otherwise tests inherit production initialization paths (network calls, filesystem reads, expensive setup) that make them slow and flaky. The pattern: `get_or_init()` checks the flag; `reset_for_tests()` clears it. Test setup calls reset before each scenario.

- **"Metadata-only" flags don't gate behavior — until they do.** [NEEDS VALIDATION] When a schema field or config flag is labeled "metadata only" (e.g., `is_bidirectional`, `is_legacy`, `display_only`), readers assume it has no behavioral effect — but downstream code often branches on it. Document the actual enforcement point: which functions read this field, what they do with it, and whether the "metadata only" label is accurate. If behavior depends on a flag, the flag is not metadata.
