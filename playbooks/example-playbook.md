# Playbook: [Task Type Name]

**Last validated:** YYYY-MM-DD
**Validation triggers:**
- [Condition that would make this playbook stale, e.g., "domain adapter interface changes"]
- [Another trigger, e.g., "new major version of a core dependency"]

---

## When to use

Use this playbook when: [1-2 sentence description of the task pattern this covers, e.g., "adding a new end-to-end feature that involves both a backend API change and a frontend UI change"].

Signs this playbook applies:
- [Signal 1, e.g., "the task requires changes to both the API layer and the UI layer"]
- [Signal 2, e.g., "the task introduces a new data model or extends an existing one"]

---

## Recommended Agents

| Agent | Role | Required? |
|-------|------|-----------|
| `software-architect` | Reviews design approach, flags architectural concerns | Yes |
| `backend-developer` | Implements API/backend changes | If backend changes |
| `frontend-developer` | Implements UI changes | If frontend changes |
| `database-architect` | Reviews schema changes | If data model changes |
| `security-engineer` | Reviews auth and input validation | If user-facing |
| `code-reviewer` | Final code quality check | Yes |

---

## Knowledge Context

Include these knowledge files when dispatching agents for this task type:

| File | When to include |
|------|----------------|
| `ops/sdlc/knowledge/architecture/backend-capability-assessment.yaml` | Always |
| `ops/sdlc/knowledge/architecture/api-design-methodology.yaml` | If adding new API endpoints |
| `ops/sdlc/knowledge/data-modeling/patterns/meta-framework.yaml` | If adding or changing data models |
| `ops/sdlc/knowledge/testing/tool-patterns.yaml` | For test planning phase |

---

## Typical Phases

### Phase 1: Design
- [ ] Define the data contract (request/response shapes, event types)
- [ ] Identify affected layers (database, API, UI, tests)
- [ ] Flag breaking changes

### Phase 2: Backend
- [ ] Implement data model changes (migrations, schema updates)
- [ ] Implement API endpoint(s)
- [ ] Add input validation
- [ ] Write unit tests for business logic

### Phase 3: Frontend
- [ ] Implement UI components
- [ ] Wire to API / state store
- [ ] Handle loading, error, and empty states

### Phase 4: Integration
- [ ] End-to-end test covering the happy path
- [ ] Error scenario test

---

## Reference Implementations

[Link to existing code in your project that implements this pattern well. Update when the reference moves.]

- `[path/to/reference-file]` — [what this demonstrates]

---

## Key Decisions to Surface

These decision points consistently arise for this task type. Surface them explicitly during spec review:

1. **[Decision 1]** — e.g., "Should this be synchronous or asynchronous?"
   - Synchronous: simpler, but blocks the request
   - Asynchronous: more complex, but better for long-running operations

2. **[Decision 2]** — e.g., "How should pagination be handled?"
   - Cursor-based: efficient for large datasets, harder to implement
   - Offset-based: simple, degrades at scale

3. **[Decision 3]** — [brief description of the tradeoff]

---

## Common Gotchas

- **[Gotcha 1]** — [What goes wrong and why. e.g., "Don't forget to update the OpenAPI spec when adding new endpoints — the CI validation step will fail otherwise."]
- **[Gotcha 2]** — [What goes wrong and why]

---

## Checklist Before Marking Complete

- [ ] All phases implemented and reviewed
- [ ] Tests passing
- [ ] Reference implementation updated if this is the new canonical example
- [ ] Playbook `last_validated` date updated if any patterns changed
