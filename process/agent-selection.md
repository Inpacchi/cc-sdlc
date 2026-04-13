# Agent Selection & Lenses

Shared reference for all skills that dispatch domain agents by file scope (`review-diff`, `review-commit`, `review-team`, `sdlc-tests-create`, `sdlc-plan`, `sdlc-create-agent`, `sdlc-initialize`). Defines which domain agents to dispatch and which analytical lenses they apply. Each skill specifies which lenses are relevant to its context — see the Lenses section.

## Agent Selection

Agent selection has two tiers. Tier 1 agents are domain specialists — dispatch them when the work involves their domain. Tier 2 agents cover structural and architectural concerns and are only dispatched when the work introduces new patterns or boundaries.

### Tier 1: Domain Agents (dispatch when the work involves their domain)

Select based on which files, systems, or domains the work touches:

- `code-reviewer` — **always included** regardless of scope. Covers overengineering, DRY, correctness, and codebase conventions.
- `frontend-developer` — when the work involves frontend source files. Covers component patterns, state management, component decomposition, and memo boundaries.
- `backend-developer` — when the work involves backend source files. Covers API patterns, server conventions, route structure, and schema design.
- `performance-engineer` — when the work involves components, state stores, memoization, search queries, or database queries. Covers re-render chains, selector patterns, query efficiency, and bundle impact. Do NOT skip because `frontend-developer` is also dispatched — they cover different concerns.
- `data-architect` — when the work involves database migrations, models, indexes, database queries, or schema-affecting code. Covers schema design, migration safety, index strategy, and query optimization.
- `ui-ux-designer` — when the work involves UI components with visual/interaction changes (not just logic refactors). Covers layout, interaction patterns, design system adherence, accessibility, and UX.
- `security-engineer` — when the work involves auth, API key handling, secrets, access control, or user input processing. Covers auth patterns, input validation, secrets management, and access control.
- `sdet` — when the work involves test files, test config, test fixtures, or test utilities. Also when the work modifies API contracts, route paths, or component selectors that existing tests may depend on. Covers test quality, flake prevention, deterministic assertions, and test architecture.
- `build-engineer` — when the work involves build configuration: `tsconfig*.json`, `vite.config.*`, workspace config, `package.json`, CI workflow files, or deploy config. Covers dependency management, build pipeline, and package boundaries.
- `accessibility-auditor` — when the work involves interactive UI components with visual or interaction changes: new buttons, modals, drawers, filter controls, icon-only controls, or any component using `aria-*` attributes or focus management. Do NOT dispatch for logic-only refactors or backend changes.
- `domain-integration-engineer` — when the work involves domain adapter files, domain models, codecs, or domain-specific logic.
- `realtime-systems-engineer` — when the work involves real-time event handling, WebSocket code, pub/sub logic, or any file that subscribes to real-time state feeds.
- `data-engineer` — when the work involves data pipelines, ETL, background processing, scrapers, or batch jobs.
- `ml-engineer` — when the work involves model configuration, training scripts, evaluation benchmark runners, or inference pipelines.
- `devops-engineer` — when the work involves Dockerfile, docker-compose, deployment config, health check scripts, CI/CD workflows, or environment variable configuration.
- `systems-engineer` — when the work involves inter-service communication, worker coordination, or cross-service communication patterns.
- `payment-engineer` — when the work involves payment integration, billing models, subscription services, webhook handlers, or checkout endpoints.
- `legal-advisor` — when the work involves privacy policies, terms of service, cookie consent, licensing decisions, or regulatory compliance documentation (GDPR, CCPA, HIPAA).
- `security-auditor` — when the work involves security assessments, vulnerability analysis, threat modeling, DevSecOps review, or compliance control implementations (SOC 2, PCI DSS, ISO 27001, OWASP). Does NOT implement fixes (that's `security-engineer`).

*Customize this list for your project. Remove agents not relevant to your stack. Add project-specific agents with their file-scope triggers and technology stacks. Use `/sdlc-create-agent` to create new agents.*

### Tier 2: Structural Agents (dispatch when warranted)

These agents cover higher-level design decisions. They add value when the work makes structural choices, but duplicate Tier 1 coverage when it doesn't.

- `software-architect` — dispatch ONLY when the work does one or more of:
  - Introduces new directory boundaries or moves files between directories
  - Creates new abstraction layers (new context providers, new store patterns, new shared hooks)
  - Changes how packages depend on each other
  - Introduces a pattern that doesn't exist elsewhere in the codebase
  - Modifies a domain adapter interface or registry

  Do NOT dispatch for: routine additions that follow existing patterns, store selectors, style changes, bug fixes, or work where `code-reviewer` and `frontend-developer`/`backend-developer` already cover architecture adherence.

- `refactor-engineer` — dispatch ONLY when the work does one or more of:
  - Moves files between directories or renames exports with consumer updates
  - Extracts new shared modules, hooks, or utilities from inline code
  - Converts between state management patterns
  - Restructures domain adapter abstraction boundaries
  - Performs significant code reorganization beyond renaming

  Do NOT dispatch for: new feature additions, bug fixes, style changes, or changes that add code without restructuring existing code.

### Personal-Level Agents (Fallback)

Generic, stack-agnostic agents at `~/.claude/agents/`. Use when the work extends beyond project-scoped expertise.

| Agent | Use Case |
|-------|----------|
| `prompt-engineer` | LLM prompt design, optimization, and evaluation for production systems |
| `refactoring-specialist` | Restructuring complex or duplicated code while preserving behavior |
| `search-specialist` | Advanced search strategies, query optimization, targeted info retrieval |
| `seo-specialist` | Technical SEO audits, keyword strategy, search rankings improvement |
| `competitive-analyst` | Competitor analysis, benchmarking, competitive positioning strategy |
| `market-researcher` | Market analysis, consumer behavior, opportunity sizing, market entry |
| `research-analyst` | Multi-source research synthesis, trend identification, detailed reporting |
| `trend-analyst` | Emerging patterns, industry shift prediction, future scenario planning |

### Selection Process

After identifying the scope of work (changed files, plan phases, or coverage map):

1. Always add `code-reviewer`
2. Add Tier 1 agents based on which domains the work touches
3. Assess whether any Tier 2 triggers apply based on the nature of the work
4. For each Tier 2 agent, briefly note WHY it's included or excluded in your checklist

## Lenses

Lenses are the perspectives agents apply when analyzing code. Each consuming skill specifies which lenses are relevant to its context:

| Skill Context | Applicable Lenses |
|--------------|-------------------|
| Code review (`review-commit`, `review-diff`, `review-team`) | All lenses |
| Test gap analysis (`sdlc-tests-create`) | Coverage, security at boundaries, contract safety, performance, data integrity, standard |
| Agent/skill creation (`sdlc-create-agent`, `sdlc-initialize`) | Standard only |

### Primary lens — overengineering and unnecessary code (review only)
- Abstractions that serve only one call site
- Helper functions or utilities for one-time operations
- Configuration or options that could just be hardcoded
- Error handling for scenarios that can't happen in context
- Feature flags, backward-compatibility shims, or future-proofing for hypothetical requirements
- Added types, interfaces, or enums that aren't needed yet
- Comments explaining obvious code
- Defensive checks that duplicate what the framework already guarantees

### Type safety lens (review only)
- `as` type casts that bypass the compiler instead of fixing the underlying type
- `any` types that erase safety (especially in function parameters or return types)
- `!` non-null assertions that hide potential undefined values
- Optional chaining (`?.`) that silently swallows undefined instead of failing at a clear boundary — particularly in data paths where undefined means a real bug, not an expected absence

### Security at boundaries lens
- User-supplied strings rendered without sanitization
- Raw HTML injection via escape hatches in components that render external data
- Database writes that accept user input without validating shape or size
- URL construction from user input without encoding
- Parser inputs that could contain injection payloads

### Contract safety lens
- Changes to shared types in shared packages — did all consumers get updated?
- State store shape changes — are all selectors and subscribers still reading valid paths?
- Enum additions or removals — are switch/case handlers and maps exhaustive?
- Function signature changes in shared utilities — are all call sites passing the right arguments?

### Performance lens
- N+1 queries — loading related objects in a loop instead of eager loading or joining
- Missing pagination on list endpoints — unbounded result sets that grow with data
- Unnecessary re-renders from unstable references, inline object literals in props, or missing memoization
- Database queries missing indexes on filtered/sorted columns, especially in hot paths
- Unbounded loops or recursive calls without depth limits
- Large payloads returned when only a subset of fields is needed

### Data integrity lens
- Missing database constraints that allow invalid state (e.g., nullable FK that should be required, missing unique constraint on a business key)
- Race conditions in concurrent writes — two requests modifying the same row without optimistic locking or serializable isolation
- Transaction boundary violations — work split across multiple commits where partial failure leaves inconsistent state
- Orphaned records — deletes or status changes that leave related rows pointing to nothing
- Enum/status values stored as strings without validation — any string can be written, not just valid states

### Coverage lens (test gap analysis)
- End-to-end workflows that cross function boundaries — is the full chain tested, or just individual pieces?
- State machine transitions — are all valid status changes exercised, including edge cases (recovery, reactivation, out-of-order events)?
- Error handling paths that affect user-visible behavior — do tests cover what happens when external services fail, input is invalid, or preconditions aren't met?
- Integration points — are external API calls, DB transactions, and job queue interactions tested with realistic mocks or real systems?
- Auth and permission boundaries — are role guards, JWT-only requirements, and IDOR prevention tested at the endpoint level?

### Standard lens — always applied
- DRY violations (duplicated logic that should be shared)
- Architecture adherence (domain adapter pattern, state management conventions, import rules, file conventions per CLAUDE.md)
- Correctness (logic errors, off-by-one, missing edge cases)
- Naming and consistency with codebase conventions
