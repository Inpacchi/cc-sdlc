---
name: commit-review
description: >
  Review a commit with domain agents — checks for overengineering, unnecessary code, DRY violations,
  and architecture adherence. Triggers on "review this commit", "check commit", "review HEAD",
  "/commit-review", "review the last commit", "code review".
  Do NOT use for uncommitted changes — use diff-review for that.
---

# Review Commit

Review a commit (or range) with relevant domain agents. The review prioritizes catching overengineered solutions and unnecessary code alongside standard quality checks.

**Argument:** `$ARGUMENTS` (commit ref, default: HEAD)

## Steps

### 1. Resolve the Commit

Use the argument as the commit ref. If no argument is provided, default to `HEAD`.

Run `git show --stat {ref}` to get the list of changed files and a summary. Then run `git show {ref}` to get the full diff.

If the ref is invalid, tell the user and stop.

### 2. Identify Relevant Domain Agents

Agent selection has two tiers. Tier 1 agents review for overengineering, unnecessary code, DRY, and correctness — the core purpose of this command. Tier 2 agents cover structural and architectural concerns and are only dispatched when the diff warrants it.

#### Tier 1: Implementation Reviewers (always dispatch if files match)

These agents catch concrete code-level issues. Select based on files changed:

- `code-reviewer` — **always included** regardless of what changed. Covers overengineering, DRY, correctness, and codebase conventions.
- `frontend-developer` — if the diff touches frontend source files. Covers component patterns, state management, component decomposition, and memo boundaries.
- `backend-developer` — if the diff touches backend source files. Covers API patterns, server conventions, and route structure.
- `data-engineer` — if the diff touches data pipeline or cloud function files. Covers pipeline patterns, batch processing conventions, and data infrastructure.
- `performance-engineer` — if the diff modifies any component file, state store, or any file that imports from a state store or uses memoization primitives. Also if search queries or database queries are added or changed. Covers re-render chains, selector patterns, query efficiency, and bundle impact. Do NOT skip because `frontend-developer` is also dispatched — they review different concerns.
- `domain-integration-engineer` — if the diff touches domain adapter files, domain models, codecs, or domain-specific logic.
- `realtime-systems-engineer` — if the diff touches real-time event handling, WebSocket code, pub/sub logic, or any file that subscribes to real-time state feeds.
- `database-architect` — if the diff touches database rules, indexes, security rules, or schema-affecting code.
- `ui-ux-designer` — if the diff touches UI components with visual/interaction changes (not just logic refactors).
- `payment-engineer` — if the diff touches pricing or payment code.
- `security-engineer` — if the diff touches auth, security rules, secrets handling, or user input processing.
- `sdet` — if the diff touches test files (`*.spec.ts`, `tests/`), test config, test fixtures, or test utilities. Also if the diff modifies API contracts, route paths, or component selectors (`data-testid`) that existing tests may depend on. Covers test quality, flake prevention, deterministic assertions, and test architecture.
- `accessibility-auditor` — if the diff touches interactive UI components with visual or interaction changes: new buttons, modals, drawers, filter controls, icon-only controls, or any component using `aria-*` attributes or focus management. Do NOT dispatch for logic-only refactors or backend changes.
- `build-engineer` — if the diff touches build configuration files: `tsconfig*.json`, `vite.config.*`, workspace config, `package.json` (scripts, dependencies, exports fields), CI workflow files, or deploy config. Also if the diff adds a new package to the monorepo or changes module format conventions.

#### Tier 2: Structural Reviewers (dispatch only when warranted)

These agents review higher-level design decisions. They add value when the commit makes structural choices, but duplicate Tier 1 coverage when it doesn't.

- `software-architect` — dispatch ONLY when the diff does one or more of:
  - Introduces new directory boundaries or moves files between directories
  - Creates new abstraction layers (new context providers, new store patterns, new shared hooks)
  - Changes how packages depend on each other
  - Introduces a pattern that doesn't exist elsewhere in the codebase
  - Modifies a domain adapter interface or registry

  Do NOT dispatch for: routine additions that follow existing patterns, store selectors, style changes, bug fixes, or commits where `code-reviewer` and `frontend-developer`/`backend-developer` already cover architecture adherence.

- `refactor-engineer` — dispatch ONLY when the diff does one or more of:
  - Moves files between directories or renames exports with consumer updates
  - Extracts new shared modules, hooks, or utilities from inline code
  - Converts between state management patterns (e.g., local state ↔ shared store)
  - Restructures domain adapter abstraction boundaries
  - Performs significant code reorganization beyond renaming

  Do NOT dispatch for: new feature additions, bug fixes, style changes, or commits that add code without restructuring existing code.

#### Selection Process

After reading the diff:

1. Always add `code-reviewer`
2. Add Tier 1 agents based on file paths
3. Read the diff content (not just file paths) to determine if Tier 2 triggers apply
4. For each Tier 2 agent, briefly note WHY it's included or excluded in your checklist

### 3. Dispatch Review Agents

Output a checklist before dispatching:

```
Reviewing commit {short-sha}: {commit subject}
Files changed: N

Dispatching reviewers:
- [ ] code-reviewer (always)
- [ ] frontend-developer (touches frontend components)
- [ ] performance-engineer (new store selectors)

Not dispatching:
- software-architect — follows existing pattern, no new abstractions
- ui-ux-designer — logic-only changes, no visual modifications
```

Dispatch ALL listed agents in parallel. Each agent receives the full diff and is asked to review with this lens:

**Primary lens — overengineering and unnecessary code:**
- Abstractions that serve only one call site
- Helper functions or utilities for one-time operations
- Configuration or options that could just be hardcoded
- Error handling for scenarios that can't happen in context
- Feature flags, backward-compatibility shims, or future-proofing for hypothetical requirements
- Added types, interfaces, or enums that aren't needed yet
- Comments explaining obvious code
- Defensive checks that duplicate what the framework already guarantees

**Type safety lens:**
- `as` type casts that bypass the compiler instead of fixing the underlying type
- `any` types that erase safety (especially in function parameters or return types)
- `!` non-null assertions that hide potential undefined values
- Optional chaining (`?.`) that silently swallows undefined instead of failing at a clear boundary — particularly in data paths where undefined means a real bug, not an expected absence

**Security at boundaries lens:**
- User-supplied strings rendered without sanitization
- Raw HTML injection via escape hatches in components that render external data
- Database writes that accept user input without validating shape or size
- URL construction from user input without encoding
- Parser inputs that could contain injection payloads

**Contract safety lens:**
- Changes to shared types in shared packages — did all consumers get updated?
- State store shape changes — are all selectors and subscribers still reading valid paths?
- Enum additions or removals — are switch/case handlers and maps exhaustive?
- Function signature changes in shared utilities — are all call sites passing the right arguments?

**Standard lens — always applied:**
- DRY violations (duplicated logic that should be shared)
- Architecture adherence (domain adapter pattern, state management conventions, import rules, file conventions per CLAUDE.md)
- Correctness (logic errors, off-by-one, missing edge cases)
- Naming and consistency with codebase conventions

Each agent reviews through their domain expertise but applies all applicable lenses.

### 4. Collect and Present Findings

Collect all findings. Present them in a single structured report:

```markdown
## Commit Review: {short-sha}

**{commit subject}**
{N} files changed | Reviewed by {N} domain agents

### Findings

| # | Finding | Agent | Severity | Category |
|---|---------|-------|----------|----------|
| 1 | specific finding | agent-name | critical/major/minor | overengineering/type-safety/security/contract/DRY/architecture/correctness |
| 2 | ... | ... | ... | ... |

### Overengineering Summary

[If any overengineering or unnecessary code was found, summarize the pattern here — e.g., "3 helper functions wrap single operations", "error handling added for impossible states". If none found, say "No overengineering detected."]

### Details

#### Finding 1: [title]
**Agent:** [agent-name] | **Severity:** [level] | **Category:** [category]
**File:** [path:line]
[Concrete description of the issue and what should change]
```

### 5. Next Steps

After presenting the report:

> **{N} findings** ({critical} critical, {major} major, {minor} minor)
>
> Run `/commit-fix` to fix all findings.

Do NOT fix anything in this command. Do NOT offer partial fix options. The review command only reviews — `/commit-fix` handles all fixes.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, skip some lenses" | Small diffs produce the subtlest bugs |
| "Agent fixed the issue during review" | Report only — fixes go through `commit-fix` |
| "This is just a refactor, no review needed" | Refactors need architecture and DRY lens review |
| "Skip Tier 2, it's a small commit" | Read the diff content. Small commits introduce new patterns more often than expected. |
| "This agent overlaps with another, skip it" | Agents review different concerns. `performance-engineer` and `frontend-developer` both review component code but catch different issues. |
| "No security concerns in this diff" | Check the boundaries lens anyway. User input flows through surprising paths. |

## Integration
- **Feeds into:** `commit-fix` (if findings need fixing)
- **Sibling:** `diff-review` (same review lenses, targets working tree instead of commits)
- **DRY note:** Agent selection criteria and review lenses are duplicated with `diff-review`. If you update one, update the other.
