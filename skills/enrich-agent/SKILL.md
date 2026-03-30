---
name: sdlc-enrich-agent
description: >
  Systematically extract relevant patterns from external sources (subagent
  definitions, articles, docs, frameworks) and integrate them into an existing
  agent. Uses a 6-dimension analytical framework to catch direct, adjacent,
  and reframed patterns that surface-level scanning misses.
  Triggers on "enrich this agent", "extract patterns from these sources for
  [agent]", "what can we learn from these for [agent]", "/sdlc-enrich-agent".
  Do NOT use for creating new agents from scratch — use sdlc-create-agent.
  Do NOT use for reviewing agent convention compliance — use sdlc-review.
  Do NOT use for extracting SDLC process improvements or convention suggestions from sources — use sdlc-review analyze mode.
  Do NOT use for ingesting knowledge into SDLC discipline stores — use sdlc-ingest.
---

# Agent Enrichment

Extract all relevant patterns from external sources and integrate them into an existing agent's definition. The skill's value is catching non-obvious patterns that surface-level domain matching misses — techniques from adjacent fields, reframed concepts, and operational patterns that apply when viewed through the agent's actual problem domain.

**Argument:** `<agent-name> <source1> [source2] [source3] ...` — the target agent file and one or more source URLs or file paths to analyze.

## Preconditions

- The target agent file must exist at `.claude/agents/<agent-name>.md` (created via `sdlc-create-agent` or manually)
- At least one source must be provided (URL or file path)
- If the target agent file lacks a clear scope statement or domain expertise line, flag this to the user before proceeding — the analytical lens depends on understanding the agent's domain

## Steps

### 1. Build the Analytical Lens

Read the target agent file. Before reading any source material, decompose the agent's domain into specific analytical questions across six dimensions. These questions are the lens — every source gets read through them.

**Dimension 1 — Core Operations:** What does this agent actually do?
- What are the agent's primary verbs? (design, evaluate, implement, diagnose, monitor, etc.)
- What decisions does this agent make? What trade-offs does it navigate?
- What does this agent produce? (code, configurations, reports, evaluations)

**Dimension 2 — Failure Modes:** What can go wrong in this domain?
- What are the silent failures? (things that break without obvious errors)
- What degrades gradually rather than breaking suddenly?
- What happens when the agent's assumptions are wrong?
- What are the known blind spots in this domain?

**Dimension 3 — Adjacent Domain Knowledge:** What does this agent need to *understand* from neighboring domains?
- What does this agent need to know about other agents' domains to do its own job? (Not to do their work, but to make good requests, write correct queries, avoid conflicts)
- What database/infrastructure/platform knowledge shapes the agent's decisions?
- What upstream inputs does this agent depend on? What downstream consumers use its output?

**Dimension 4 — Operational Lifecycle:** How are changes in this domain shipped and maintained?
- How should changes be deployed? (incremental vs. big-bang, with/without monitoring)
- What does rollback look like? Can changes be safely reverted?
- What maintenance patterns apply? (periodic re-evaluation, cache invalidation, data freshness)

**Dimension 5 — Diagnostic Toolkit:** How does this agent measure success?
- What are the primary metrics? What secondary/proxy metrics exist?
- What observability does this domain need beyond the obvious metrics?
- How does this agent detect that something is wrong before users notice?
- What does a "health check" look like for this domain?

**Dimension 6 — Input/Output Quality:** What quality requirements exist for what this agent consumes and produces?
- What happens when inputs are stale, incomplete, or biased?
- How does the agent validate its own outputs?
- What data quality discipline applies to this agent's artifacts?

**Output of this step:** A filled-in question set specific to the target agent. Write these out explicitly — they are the analytical lens for all subsequent source reading.

### 2. Fetch and Read Sources

Fetch all provided sources (URLs via WebFetch, file paths via Read). For each source, read the full content — do not skim or summarize prematurely. Capture the complete set of patterns, techniques, principles, and operational guidance before filtering.

- **URLs**: Use WebFetch. If a fetch fails (404, timeout, auth-required), report which source failed and continue with remaining sources. Do not silently skip.
- **File paths**: Use Read. If the file doesn't exist, report and continue.
- **Long sources** (articles, full documentation): Read in full. The analytical lens from Step 1 does the filtering — pre-summarizing a source before applying the lens defeats the purpose, because you don't yet know which details will match which dimension.
- **Multiple sources**: Fetch all sources before beginning extraction (Step 3). Having the full landscape in view helps identify cross-source patterns.

### 3. Extract Through the Lens

For each source, work through every dimension's questions systematically. For each question, ask: **"Does this source contain anything — directly, adjacently, or when reframed — that answers this question for the target agent?"**

The three extraction modes:

**Direct:** The source describes a technique that maps 1:1 to the agent's domain. Example: a database-optimizer's "query plan analysis" directly applies to a search-engineer that writes ranking queries.

**Adjacent:** The source describes a technique from a neighboring domain that the agent needs to *understand* to do its own job well. Example: a postgres-pro's "GIN index behavior" isn't the search-engineer's responsibility to implement, but the search-engineer needs to understand it to write queries that use GIN indexes correctly.

**Reframed:** The source describes a technique using different terminology or in a different context, but the underlying pattern applies when translated to the agent's domain. Example: an SEO specialist's "keyword intent classification" is about web search, but the underlying pattern — classifying query intent to select a ranking strategy — applies to any search system.

For each extracted pattern, record:
- **Pattern name** — concise label
- **Source** — which source it came from
- **Extraction mode** — direct, adjacent, or reframed
- **Dimension** — which analytical dimension it answers
- **How it applies** — specific, concrete description of how this pattern maps to the target agent's domain
- **Where it goes** — which section of the agent file it belongs in (scope, principles, workflow, anti-rationalization, checklist, handoff fields, memory guidance)

### 4. Defend Each Dismissal

After extracting patterns, review what you did NOT extract from each source. For each dismissed element, write a one-line justification. This is not optional — it forces examination of every dismissal.

The five dismissal failure modes to guard against:

| Failure mode | What it looks like | Counter-question |
|---|---|---|
| **Surface-level domain mismatch** | "That's a web/SEO/marketing thing" | Strip the domain label — does the underlying technique apply? |
| **Adjacent domain blindness** | "That belongs to [other agent]" | Does the target agent need to *understand* this to do its own job? |
| **Premature satisfaction** | Took one pattern from a source, stopped looking | Did you check every dimension against this source? |
| **Metric tunnel vision** | Only found patterns matching existing metric types | Are there diagnostic, observability, or operational patterns you missed? |
| **Implementation vs. understanding** | "We don't need to implement that" | Does the agent need to understand this concept even if another agent implements it? |

If any dismissal justification matches one of these failure modes, re-examine it.

### 5. Compile the Integration Plan

Group extracted patterns by target section in the agent file:

| Agent section | Patterns to integrate |
|---|---|
| Domain expertise line | New technologies, techniques, or knowledge areas |
| Core Principles | New principle sections or additions to existing sections |
| Workflow | New or modified workflow steps |
| Anti-rationalization table | New entries for shortcuts the agent might take |
| Self-verification checklist | New quality checks |
| Communication protocol / handoff fields | New handoff data the agent should report |
| Memory guidance | New categories of information worth persisting |

Present the full integration plan to the user with the pattern table from step 3. Include the total count and a breakdown by extraction mode (direct/adjacent/reframed) so the user can see the analytical coverage.

### 6. Apply Changes

After user approval, edit the agent file. For each section:
- Add new content that integrates naturally with existing content — don't create an "additions from enrichment" ghetto
- Preserve the agent's existing voice and structure
- If a new Core Principles subsection is warranted (3+ related patterns), create one with a descriptive heading
- Update the domain expertise line if new knowledge areas were identified
- If the anti-rationalization table grows unwieldy, merge entries that address the same root rationalization pattern — but never drop entries to hit an arbitrary count
- If the self-verification checklist grows beyond 6 items, look for items that can be consolidated — but never drop a check that catches a distinct failure mode

### 7. Verify Completeness

After applying changes, do a final read of the updated agent file. Verify:
- [ ] Every extracted pattern from the integration plan appears in the agent file
- [ ] No existing content was accidentally removed or contradicted
- [ ] New content is specific and actionable, not generic platitudes
- [ ] The agent file still reads coherently as a whole — not like a patchwork of additions

## Red Flags

| Thought | Reality |
|---------|---------|
| "This source isn't relevant, I'll skip it entirely" | Read it through all 6 dimensions first. The user provided it for a reason, and surface-level domain mismatch is the #1 failure mode. |
| "I found 2-3 good patterns from this source, that's enough" | Premature satisfaction. Check every dimension against the source before moving on. |
| "That technique belongs to another agent, not this one" | Does the target agent need to *understand* it? Adjacent domain knowledge is a legitimate enrichment category. |
| "That's just a different word for something we already have" | Is it though? Or does the different framing reveal an angle your existing content misses? Check the specific wording. |
| "I'll skip the dismissal defense step, I was thorough" | The dismissal defense exists specifically because you feel thorough when you're not. It's mandatory. |
| "This pattern is too generic to be useful" | Make it specific. "Validate data quality" is generic. "Check eval set for stale relevance labels that no longer match the memory corpus" is actionable. The pattern might be generic — your job is to make the application specific. |
| "I'll add everything and let the user sort it out" | Quality over quantity. Every pattern in the integration plan must have a concrete "how it applies" — if you can't articulate it, don't include it. |
| "The agent file is getting too long, I'll skip some" | If the agent file is over-growing, consolidate — don't drop patterns. Merge related principles, tighten wording, combine checklist items. |

## Integration

- **Depends on:** A target agent file must exist (created via `sdlc-create-agent` or manually)
- **Feeds into:** Updated agent definitions with richer domain knowledge; may surface knowledge store gaps for `sdlc-ingest`
- **Uses:** WebFetch (for URL sources), Read (for file sources), Edit (for agent file updates), the target agent file, source material
- **Complements:** `sdlc-create-agent` (creates the agent this skill enriches), `sdlc-review` (reviews conventions; this skill enriches content), `sdlc-ingest` (ingests into knowledge stores; this skill enriches agent definitions)
- **Does NOT replace:** `sdlc-review analyze` mode (which extracts process improvements, not agent enrichment), `sdlc-ingest` (which targets discipline knowledge stores, not agent files)
- **DRY notes:** `sdlc-review analyze` also reads external sources, but its output is process improvements and skill/agent convention suggestions. This skill's output is direct agent file content updates. No overlap in output; possible overlap in input sources.
