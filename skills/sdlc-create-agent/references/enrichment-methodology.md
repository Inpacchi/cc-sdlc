# Agent Enrichment Methodology

Detailed methodology for ENRICH mode of `sdlc-create-agent`. Extracts relevant patterns from external sources and integrates them into an existing agent using a 6-dimension analytical framework.

## Preconditions

- The target agent file must exist at `.claude/agents/<agent-name>.md`
- At least one source must be provided (URL or file path)
- If the target agent file lacks a clear scope statement, flag this before proceeding — the analytical lens depends on understanding the agent's domain

## Steps

### 1. Build the Analytical Lens

Read the target agent file. Decompose the agent's domain into specific analytical questions across six dimensions:

**Dimension 1 — Core Operations:** What does this agent actually do? Primary verbs, decisions, trade-offs, outputs.

**Dimension 2 — Failure Modes:** What can go wrong? Silent failures, gradual degradation, wrong assumptions, blind spots.

**Dimension 3 — Adjacent Domain Knowledge:** What does this agent need to *understand* from neighboring domains to do its own job well?

**Dimension 4 — Operational Lifecycle:** How are changes shipped and maintained? Deployment, rollback, maintenance patterns.

**Dimension 5 — Diagnostic Toolkit:** How does this agent measure success? Metrics, observability, health checks.

**Dimension 6 — Input/Output Quality:** What quality requirements exist? Stale/incomplete inputs, output validation, data quality.

Write the filled-in question set explicitly — it is the analytical lens for all source reading.

### 2. Fetch and Read Sources

Fetch all sources (URLs via WebFetch, file paths via Read). Read full content — do not skim. The analytical lens does the filtering. Multiple sources: fetch all before beginning extraction.

### 3. Extract Through the Lens

For each source, work through every dimension's questions: **"Does this source contain anything — directly, adjacently, or when reframed — that answers this question?"**

Three extraction modes:
- **Direct:** 1:1 technique mapping to the agent's domain
- **Adjacent:** Technique from a neighboring domain the agent needs to *understand*
- **Reframed:** Different terminology/context, but underlying pattern applies when translated

For each pattern, record: pattern name, source, extraction mode, dimension, how it applies, where it goes in the agent file.

### 4. Defend Each Dismissal

Review what was NOT extracted. Write a one-line justification for each dismissal.

Five failure modes to guard against:

| Failure mode | Counter-question |
|---|---|
| Surface-level domain mismatch | Strip the domain label — does the underlying technique apply? |
| Adjacent domain blindness | Does the target agent need to *understand* this? |
| Premature satisfaction | Did you check every dimension against this source? |
| Metric tunnel vision | Are there diagnostic/observability patterns you missed? |
| Implementation vs. understanding | Does the agent need to understand this even if another agent implements it? |

### 5. Compile the Integration Plan

Group patterns by target section: domain expertise line, core principles, workflow, anti-rationalization table, self-verification checklist, communication protocol, memory guidance.

Present the full plan with counts by extraction mode (direct/adjacent/reframed).

### 6. Apply Changes

After user approval, edit the agent file:
- Integrate naturally with existing content — no "additions from enrichment" ghetto
- Preserve the agent's existing voice and structure
- Create new principle subsections when 3+ related patterns warrant it
- Consolidate if tables or checklists grow unwieldy — but never drop entries that catch distinct failure modes

### 7. Verify and Review

After applying changes, verify:
- Every pattern from the integration plan appears in the agent file
- No existing content was accidentally removed or contradicted
- New content is specific and actionable, not generic platitudes
- The agent file reads coherently as a whole

Then dispatch the `sdlc-reviewer` subagent to check conventions per `[sdlc-root]/process/skill-agent-review.md`.

## Bulk Mode

Handles many sources fanned to one or many target agents via a two-phase structure.

### Phase 1 — Relevance Mapping (cheap)

1. **Inventory external items.** GitHub repo trees: use tree API for structured listing. Directories: glob `.md` files. Capture name, category, one-line description from filename/frontmatter. The inventory must come from an actual listing, not training-data recall.

2. **List target agents.** Enumerate `.claude/agents/*.md` with domain hints.

3. **Build relevance mapping table.** For each target, list external items whose domain remotely applies — directly, adjacently, or reframed. When in doubt, include.

4. **Present for approval.** Surface items assigned to zero targets explicitly.

### Phase 2 — Parallel Enrichment (dispatched)

1. **Batch targets** into groups of 3-4 for parallel dispatch.

2. **Dispatch each target as a general-purpose Agent.** The prompt must include: target file path, approved source list, full 6-dimension lens (inline or via shared brief file), path-discovery fallback instruction, project-anchors section (from CLAUDE.md, agent bodies, knowledge files), and instructions to execute Steps 1-7 and edit directly.

3. **Run batches sequentially; items within a batch in parallel.** Follow `[sdlc-root]/process/parallel-dispatch-monitoring.md`.

4. **Handle write-back failures.** If a subagent can't write: resume via SendMessage to emit enriched body, then apply via main thread's Edit/Write. Do not re-dispatch.

5. **Aggregate reports.** Per-target summary: patterns by extraction mode, failed fetches, low-yield targets.

6. **Check for description drift.** Flag agents whose body grew past what the frontmatter description covers.

### Single Target with Source Collections

Phase 1 collapses to a single-row table. Phase 2 runs in the main thread (no parallelism needed). Generous-inclusion and presentation-for-approval still apply.
