# Discipline Capture Protocol

A lightweight step for capturing cross-discipline insights during active work. Skills reference this file instead of duplicating the protocol.

## When This Runs

After substantive work completes — post-execution, post-planning, post-exploration, post-design. Each skill specifies its own trigger point.

## What to Look For

Scan the work just completed for insights that are:

- **Reusable** — applies beyond this specific deliverable
- **Non-obvious** — not something an agent would derive from reading the codebase
- **Cross-discipline** — belongs to a discipline other than the primary work (e.g., a testing gotcha discovered during implementation, an architecture boundary issue surfaced during planning)

Common signals:

| Source | Example |
|--------|---------|
| Agent review finding | "Agent flagged a pattern that applies to all API endpoints, not just this one" |
| Discovery during research | "Context7 revealed a library gotcha not in our knowledge store" |
| Execution friction | "This approach required 3 re-dispatches because the data flow wasn't documented" |
| Cross-domain surprise | "Backend agent needed design knowledge to implement this correctly" |

## How to Capture

Append each insight to the relevant `ops/sdlc/disciplines/*.md` parking lot under the `## Parking Lot` heading:

```
- **[date] [context]**: [insight]. [triage marker]
```

**Context formats by skill:**
- Execution: `[DNN — phase N]`
- Planning: `[DNN — planning]`
- Idea exploration: `[idea: {slug}]`
- Design consultation: `[design-consult: {slug}]`

**Triage markers:**
- `[NEEDS VALIDATION]` — default for newly captured insights
- `[READY TO PROMOTE]` — use only if you're confident the insight is validated, reusable, and stable
- `[DEFERRED]` — acknowledged but not a priority (include reason)

## Rules

- **Skip if nothing surfaced.** Do not fabricate entries. Empty is fine — discipline capture is pulled, not pushed.
- **<2 minutes.** This is a scan, not a research project. If the insight is obvious, write it. If it requires investigation, note the question and move on.
- **One insight per bullet.** Keep entries atomic so they can be triaged independently.
- **The orchestrator writes these directly.** This is process documentation, not domain content — the Manager Rule does not apply. Do not dispatch an agent to write a parking lot entry.
