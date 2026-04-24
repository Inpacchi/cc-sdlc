# Review Lenses

Analytical perspectives that agents apply when reviewing code. Each consuming skill specifies which lenses are relevant to its context.

## Lens Applicability by Skill

| Skill Context | Applicable Lenses |
|--------------|-------------------|
| Code review (`sdlc-review-code`, `team-review-fix`) | All lenses |
| Test gap analysis (`sdlc-tests-create`) | Coverage, security at boundaries, contract safety, performance, data integrity, standard |
| Agent/skill creation (`sdlc-create-agent`, `sdlc-initialize`) | Standard only |

---

## Primary Lens — Overengineering and Unnecessary Code (review only)

- Abstractions that serve only one call site
- Helper functions or utilities for one-time operations
- Configuration or options that could just be hardcoded
- Error handling for scenarios that can't happen in context
- Feature flags, backward-compatibility shims, or future-proofing for hypothetical requirements
- Added types, interfaces, or enums that aren't needed yet
- Comments explaining obvious code
- Defensive checks that duplicate what the framework already guarantees

## Type Safety Lens (review only)

- `as` type casts that bypass the compiler instead of fixing the underlying type
- `any` types that erase safety (especially in function parameters or return types)
- `!` non-null assertions that hide potential undefined values
- Optional chaining (`?.`) that silently swallows undefined instead of failing at a clear boundary — particularly in data paths where undefined means a real bug, not an expected absence

## Security at Boundaries Lens

- User-supplied strings rendered without sanitization
- Raw HTML injection via escape hatches in components that render external data
- Database writes that accept user input without validating shape or size
- URL construction from user input without encoding
- Parser inputs that could contain injection payloads

## Contract Safety Lens

- Changes to shared types in shared packages — did all consumers get updated?
- State store shape changes — are all selectors and subscribers still reading valid paths?
- Enum additions or removals — are switch/case handlers and maps exhaustive?
- Function signature changes in shared utilities — are all call sites passing the right arguments?

## Performance Lens

- N+1 queries — loading related objects in a loop instead of eager loading or joining
- Missing pagination on list endpoints — unbounded result sets that grow with data
- Unnecessary re-renders from unstable references, inline object literals in props, or missing memoization
- Database queries missing indexes on filtered/sorted columns, especially in hot paths
- Unbounded loops or recursive calls without depth limits
- Large payloads returned when only a subset of fields is needed

## Data Integrity Lens

- Missing database constraints that allow invalid state (e.g., nullable FK that should be required, missing unique constraint on a business key)
- Race conditions in concurrent writes — two requests modifying the same row without optimistic locking or serializable isolation
- Transaction boundary violations — work split across multiple commits where partial failure leaves inconsistent state
- Orphaned records — deletes or status changes that leave related rows pointing to nothing
- Enum/status values stored as strings without validation — any string can be written, not just valid states

## Coverage Lens (test gap analysis)

- End-to-end workflows that cross function boundaries — is the full chain tested, or just individual pieces?
- State machine transitions — are all valid status changes exercised, including edge cases (recovery, reactivation, out-of-order events)?
- Error handling paths that affect user-visible behavior — do tests cover what happens when external services fail, input is invalid, or preconditions aren't met?
- Integration points — are external API calls, DB transactions, and job queue interactions tested with realistic mocks or real systems?
- Auth and permission boundaries — are role guards, JWT-only requirements, and IDOR prevention tested at the endpoint level?

## Standard Lens — Always Applied

- DRY violations (duplicated logic that should be shared)
- Architecture adherence (domain adapter pattern, state management conventions, import rules, file conventions per CLAUDE.md)
- Correctness (logic errors, off-by-one, missing edge cases)
- Naming and consistency with codebase conventions
