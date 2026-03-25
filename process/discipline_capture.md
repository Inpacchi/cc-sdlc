# Discipline Capture Protocol

A lightweight step for capturing cross-discipline insights during active work. Skills reference this file instead of duplicating the protocol.

## When This Runs

After substantive work completes — post-execution, post-planning, post-exploration, post-design. Each skill specifies its own trigger point.

## Structured Gap Detection

Before the freeform scan, run these comparisons using data already in context. These detect systematic gaps that are invisible to a vibes-based scan.

### Comparison 1: Knowledge loaded vs. needed

For each agent dispatched in this session, compare what knowledge was available against the FIX findings the agent produced. Ask: could a knowledge file have prevented this finding?

- **If `knowledge_feedback.loaded` is present** in the agent's handoff (see agent-communication-protocol.yaml), use it — this is the most accurate source of what the agent actually read.
- **Otherwise**, look up the agent's mapped files from `ops/sdlc/knowledge/agent-context-map.yaml`. If the lookup for multiple agents would exceed the time budget, skip this comparison and note "deferred to auditor."

**What to detect:**

| Signal | GAP Type | Example |
|--------|----------|---------|
| Finding could have been prevented by knowledge that doesn't exist | `MISSING_KNOWLEDGE` | Agent hit a React StrictMode gotcha not in any knowledge file |
| Knowledge exists but wasn't mapped to this agent | `UNMAPPED_KNOWLEDGE` | Agent needed testing patterns but only had architecture files mapped |
| Knowledge was mapped but agent still got it wrong | `STALE_KNOWLEDGE` | Gotcha file says "use X" but X no longer works in current version |

### Comparison 2: Cross-domain friction

When agents were dispatched into cross-domain contexts (e.g., a backend agent fixing a frontend issue), did they produce FIX findings in the foreign domain?

- **For skills with a review-fix loop** (sdlc-execute, sdlc-lite-execute, sdlc-plan, sdlc-lite-plan): check the triage table for FIX findings where the fixing agent worked outside its primary domain.
- **For sdlc-idea and design-consult** (no triage table): this is a judgment call — did the agent's output reveal it struggled with something outside its domain?

If yes → write a `CROSS_DOMAIN_FRICTION` GAP entry in the relevant discipline's parking lot.

### Comparison 3: Iteration cost

If the review-fix loop ran >2 rounds, did you observe a finding recurring across rounds?

**This is a judgment call**, not a mechanical count. The review-fix loop doesn't assign finding IDs across rounds. The orchestrator assesses "did this look like the same issue?" based on finding descriptions. Resurfacing findings suggest a pattern that isn't captured in any knowledge store.

If yes → write a `RESURFACING_PATTERN` GAP entry.

**Not applicable** to sdlc-idea and design-consult (no review-fix loop).

### Skill applicability

| Skill | Comparison #1 | Comparison #2 | Comparison #3 |
|-------|--------------|--------------|--------------|
| sdlc-execute, sdlc-lite-execute | Yes (full triage data) | Yes | Yes |
| sdlc-plan, sdlc-lite-plan | Yes (planning findings) | Yes | Yes (if >2 rounds) |
| sdlc-idea | Conditional (no triage table) | Yes (judgment-based) | No |
| design-consult | Conditional (no triage table) | Yes (judgment-based) | No |
| review-fix | Not applicable — commit-scoped findings are too narrow for discipline-level gap detection |
| sdlc-resume | Inherits from sdlc-execute's capture step |

### GAP entry format

Auto-detected gaps use a distinct format and are always marked `[NEEDS VALIDATION]`:

```
- **[date] [context]**: [GAP:{type}] {description}. Source: {agent} finding. [NEEDS VALIDATION]
```

Types: `MISSING_KNOWLEDGE`, `UNMAPPED_KNOWLEDGE`, `STALE_KNOWLEDGE`, `CROSS_DOMAIN_FRICTION`, `RESURFACING_PATTERN`

## Freeform Insight Scan

After structured gap detection, scan the work just completed for insights that are:

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
| Agent knowledge feedback | Agent's `knowledge_feedback.missing` describes a gap worth capturing |

## How to Capture

Append each insight or GAP entry to the relevant `ops/sdlc/disciplines/*.md` parking lot under the `## Parking Lot` heading:

```
- **[date] [context]**: [insight]. [triage marker]
```

**Context formats by skill:**
- Execution: `[DNN — phase N]`
- Planning: `[DNN — planning]`
- Idea exploration: `[idea: {slug}]`
- Design consultation: `[design-consult: {slug}]`

**Triage markers:**
- `[NEEDS VALIDATION]` — default for newly captured insights and all auto-detected GAP entries
- `[READY TO PROMOTE]` — use only if you're confident the insight is validated, reusable, and stable
- `[DEFERRED]` — acknowledged but not a priority (include reason)

## Rules

- **Skip if nothing surfaced.** Do not fabricate entries. Empty is fine — discipline capture is pulled, not pushed.
- **<3 minutes total.** Structured gap detection: ~30s. Freeform scan: ~2 minutes. If a structured comparison would exceed the time budget, skip it and note "deferred to auditor."
- **One insight per bullet.** Keep entries atomic so they can be triaged independently.
- **The orchestrator writes these directly.** This is process documentation, not domain content — the Manager Rule does not apply. Do not dispatch an agent to write a parking lot entry.
- **Audit triage carve-out.** The `sdlc-audit` skill (compliance mode) may apply low-risk triage markers (unmarked → `[NEEDS VALIDATION]`, `[NEEDS VALIDATION]` → `[DEFERRED]`) directly per its triage authority matrix in the compliance methodology §6c. High-risk transitions (any → `[READY TO PROMOTE]`, any → `Promoted →`) remain CD-only.
