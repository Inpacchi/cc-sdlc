---
name: sdlc-enrich-agent
description: >
  Systematically extract relevant patterns from external sources (subagent
  definitions, articles, docs, frameworks) and integrate them into an existing
  agent. Uses a 6-dimension analytical framework to catch direct, adjacent,
  and reframed patterns that surface-level scanning misses.
  Use when you have external sources that may contain patterns worth integrating into an existing agent.
  Triggers on "enrich this agent", "extract patterns from these sources for
  [agent]", "what can we learn from these for [agent]", "/sdlc-enrich-agent".
  Supports a bulk mode for fanning sources across multiple agents or applying
  many sources (including repo collections of subagents) to one agent —
  triggers on "enrich all agents", "evaluate all our subagents against these",
  "bulk enrich", or when sources are GitHub repo trees / directories of
  subagent files.
  Do NOT use for creating new agents from scratch — use sdlc-create-agent.
  Do NOT use for reviewing agent convention compliance — use sdlc-review.
  Do NOT use for extracting SDLC process improvements or convention suggestions from sources — use sdlc-review analyze mode.
  Do NOT use for ingesting knowledge into SDLC discipline stores — use sdlc-ingest.
---

# Agent Enrichment

Extract all relevant patterns from external sources and integrate them into an existing agent's definition. The skill's value is catching non-obvious patterns that surface-level domain matching misses — techniques from adjacent fields, reframed concepts, and operational patterns that apply when viewed through the agent's actual problem domain.

**Arguments — single-agent mode:** `<agent-name> <source1> [source2] [source3] ...` — the target agent file and one or more source URLs or file paths to analyze.

**Arguments — bulk mode:** one of:
- `bulk <source1> [source2] ...` — enrich every agent in `.claude/agents/` against the given sources
- `bulk <agent1>,<agent2>,... <source1> [source2] ...` — enrich a comma-separated subset of agents
- `<agent-name> <collection-source1> ...` — single target against source collections; auto-detected when any source is a GitHub repo tree URL or a directory path containing multiple subagent files

## Modes

**Single-agent mode** (default): one target agent, direct sources. Follow Steps 1–7.

**Bulk mode**: fans either many sources to one target or sources to many targets. Uses a two-phase structure — a cheap main-thread relevance mapping pass followed by parallel dispatched enrichment. See the **Bulk Mode** section after Red Flags. Phase 2 of bulk mode delegates Steps 1–7 to dispatched subagents; do not re-run Steps 1–7 in the main thread when bulk mode is active.

## Preconditions

- The target agent file(s) must exist at `.claude/agents/<agent-name>.md` (created via `sdlc-create-agent` or manually)
- At least one source must be provided (URL or file path)
- If the target agent file lacks a clear scope statement or domain expertise line, flag this to the user before proceeding — the analytical lens depends on understanding the agent's domain
- **Bulk mode**: all target agent files must already exist; if `bulk` is invoked with no explicit target list, confirm the discovered agent list with the user before starting Phase 1 (some agents may be deliberately scoped to reject external patterns)

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

## Bulk Mode

Bulk mode handles two cases with the same two-phase structure: (a) many external items fanned out to one target agent, and (b) many external items fanned out to many target agents. The goal is to preserve the analytical rigor of Steps 1–7 while making the fan-out tractable — a naive approach either drops sources prematurely (to keep the work small) or burns fetch budget reading every source against every target.

### Bulk Phase 1 — Relevance Mapping (main thread, cheap)

Goal: produce a table that assigns each external item to the set of target agents whose domain *remotely applies*, so Phase 2 has a bounded, justified source list per target.

1. **Inventory the external items.** For each source:
   - **GitHub repo tree URLs** (e.g., `.../tree/main/agents`): use the GitHub tree API for a structured listing (`gh api repos/OWNER/REPO/git/trees/BRANCH?recursive=1 --jq '.tree[] | select(.path | endswith(".md"))'`), or a single WebFetch on the tree page — do not WebFetch each file yet
   - **Directory paths**: glob all `.md` files
   - **Single sources** (one article, one agent file): treat as a single item — no inventory needed

   Capture each item's name, category (if visible in the taxonomy), and a one-line description inferred from filename, frontmatter, or the first line of content. The goal is a cheap categorization pass, not full reads.

   **The inventory must come from an actual source listing, not training-data recall.** "Do not WebFetch each file" is not a license to generate item names from memory of what the repo probably contains. If you catch yourself writing out items without a concrete listing (API response, glob result, tree page) to point at, stop and fetch the listing. Phase 1's value collapses the moment the map is built on assumed contents — the user may approve a table that references items that don't exist, and Phase 2 fails to fetch them.

2. **List target agents.** Enumerate `.claude/agents/*.md`. For each, record the agent name and a short domain hint pulled from the `description` frontmatter line or the first scope paragraph.

3. **Build the relevance mapping table.** For each target agent, list every external item whose domain *remotely applies* — directly, adjacently, or when reframed. Apply generous inclusion:
   - Include anything that plausibly touches the target's domain. The cost of reading an irrelevant source in Phase 2 is one extraction pass that produces zero patterns; the cost of skipping a source is losing every pattern it would have yielded, permanently.
   - When in doubt, include. It is always better to dispatch with a source that proves irrelevant than to skip one that would have yielded a pattern.
   - This is a categorization pass against names and one-liners, not a content analysis. Do not WebFetch items at this stage.

4. **Present the table for approval.** Format:
   ```
   | target agent | relevant external items (count) |
   ```
   Include a summary footer with totals (items, targets, assignments) and a breakdown of items assigned to zero targets (surface these explicitly — the user may want to force-include them against a specific agent, or confirm dismissal). The user reviews and edits the table before Phase 2 runs.

### Bulk Phase 2 — Parallel Enrichment (dispatched subagents)

Goal: run Steps 1–7 of the single-agent workflow against each target agent, in parallel, with the relevance map narrowing the source list per target. The main thread does not do extraction in bulk mode — it orchestrates.

1. **Batch the work.** Group target agents into batches of **3–4** for parallel dispatch. Batch size balances throughput against WebFetch rate limits and against the cognitive cost of aggregating reports. Do not exceed 4 per batch.

2. **Dispatch each target as a general-purpose Agent.** For each target in the batch, launch `Agent` with `subagent_type=general-purpose`. The prompt is self-contained and must include:
   - The absolute target agent file path
   - The approved list of external items for this target (from Phase 1 — specific URLs or file paths, not "items about X")
   - The full 6-dimension analytical lens — either inlined verbatim (simple; right for small fan-outs ≤5 targets), or written once to a shared brief file (e.g., `/tmp/enrich_agent_brief.md`) with the file path referenced in each dispatched prompt (right for larger fan-outs — avoids inlining the same ~2KB lens into every prompt). Dispatched agents do not have access to this skill file; they must either read the lens inline in the prompt or Read the brief file as their first action.
   - **A path-discovery fallback instruction.** Tell the subagent: if a provided source URL returns 404, fall back to `gh api repos/OWNER/REPO/contents/PATH` (or walk the tree) to discover the actual path before giving up on the source. External repos routinely use nested layouts (e.g., `plugins/<category>/agents/<name>.md`) or non-standard filenames (e.g., `architect-review.md` instead of the expected `architect-reviewer.md`). Phase 1's inventory may have produced URLs based on the top-level tree that don't resolve without layout discovery.
   - **A project-anchors section.** List project-specific technologies, libraries, data stores, module conventions, and architectural rules that this project uses (e.g., `GameAdapter`, `Firestore publicDeckIndex`, Zustand selector pattern, `.mts` NodeNext, Data Pipeline Integrity rule). This anchoring is what lets subagents recognize when an adjacent-domain or reframed pattern applies *specifically to this project* rather than in the abstract — extraction yield drops sharply when the dispatched agent has no project-specific hooks to map patterns onto. Pull these anchors from `CLAUDE.md`, the target agent's existing body, or a `[sdlc-root]/knowledge/` file; do not invent them.
   - Explicit instructions to execute Steps 1–7 of the single-agent enrichment workflow
   - Direction to **edit the target file directly** — do not return a plan for human review. The plan was Phase 1; the user already approved which sources apply to this target.
   - A concise report format for the response: counts by extraction mode (direct/adjacent/reframed), top 3 patterns integrated, any sources that failed to fetch (distinguishing 404-then-discovered from genuinely-missing), and the sections updated

3. **Run batches sequentially; items within a batch in parallel.** Send all 3–4 Agent tool calls for a batch in a single message. Wait for the batch to complete before dispatching the next. Do not fan out all targets at once — rate limits and report volume both suffer. Within each batch, follow `[sdlc-root]/process/parallel-dispatch-monitoring.md` — read every subagent's output before starting the next batch, and apply the 3-strike rule if a subagent fails repeatedly.

4. **Handle write-back failures (staging fallback).** Dispatched subagents sometimes have Edit permission denied on target files even when the user granted Edit to the main thread — tool permissions do not always inherit across the Agent boundary. If a subagent reports that it completed analysis but could not write:

   - **Do not re-dispatch.** The analysis work (pattern extraction, dismissal defense, integration plan) represents 20–50 minutes of real effort per target. Re-dispatching throws it away.
   - **Resume via SendMessage.** Send a follow-up to the stuck subagent instructing it to emit the full enriched file content as a text message. The main thread then applies the write using its own Edit/Write tools.
   - **Preserve frontmatter bytes.** YAML frontmatter can use inconsistent escape styles across files (`\n` vs `\\n`, quoted vs. unquoted multiline). When main-thread-writing from a subagent's output, have the subagent emit only the enriched body; Read the original file to capture the exact frontmatter bytes; merge with a simple concatenation (e.g., `head -N original + blank line + body`) rather than re-serializing through a YAML library.
   - **Test permissions with one target before full dispatch.** When running a large bulk pass (10+ targets), dispatch the first batch of 1–2 first and verify writes landed before firing subsequent batches — catches the permission issue early instead of after eight batches of staging cleanup.

5. **Aggregate batch reports.** After all batches finish, present a per-target summary: patterns added by extraction mode, sources that failed to fetch, and any targets where the dispatched subagent reported unusually low yield (flag those for manual review — the Phase 1 map may have over-assigned, or the agent's lens may be too narrow for these sources).

6. **Check for description drift.** Enrichment can grow a target's body substantially (3,000+ added lines across 30 agents is typical for a large bulk run). Afterward, scan each enriched agent for description drift: does the frontmatter `description` line still accurately summarize what the body now covers? Common signal: the body adopts new disciplines (e.g., ADRs, SemVer, deprecation windows) that the description doesn't mention. Flag drifted agents for manual description updates — do not rewrite descriptions automatically, because the user's intent for scope is the authority, not the extraction yield.

### Bulk Mode: Single Target with Source Collections

When bulk mode is triggered by one target agent plus repo-tree or directory sources (case (a)), Phase 1 collapses to a single-row table ("which items from the collections are remotely relevant to *this one* agent?") and Phase 2 can run in the main thread (one target, so no parallelism needed). The generous-inclusion lens and the mandatory presentation-for-approval step still apply — do not skip Phase 1 and feed the full collection into Steps 1–7, because the collection will contain dozens of items most of which don't apply, and the lens's "read the full source" instruction will blow out the context.

### Bulk Mode Red Flags

| Thought | Reality |
|---------|---------|
| "These two target agents are similar, I can reuse extraction results" | No. Each agent's lens is different — the same source yields different patterns through different dimensional questions. Dispatch separately. |
| "I'll skip Phase 1 and let each dispatched subagent decide relevance" | You pay full WebFetch cost for every source on every target, and lose the user's ability to sanity-check assignments before dispatch. Phase 1 is cheap and narrows Phase 2 dramatically. |
| "This external item clearly doesn't match any target agent" | Apply generous inclusion. Check every target's domain once before dismissing. It is always better to over-assign and have the extraction pass produce zero patterns than to skip a source permanently. |
| "I'll run all 15 agents in one big parallel batch" | Respect the 3–4 batch size. Larger batches hit rate limits, and aggregated reports from 15 parallel agents become un-reviewable in practice. |
| "Phase 2 subagents should return plans, not edit" | No. The plan was the Phase 1 relevance map, which the user already approved. Phase 2 subagents extract and edit. Returning plans for each of N agents is not reviewable in practice — trust the lens. |
| "The dispatched agent's prompt is too long if I inline all 6 dimensions" | For small fan-outs (≤5 targets), inline verbatim — a terse prompt produces a terse extraction. For larger fan-outs, write the lens to a shared brief file once and reference the path; do NOT trim the lens to save tokens. Lens fidelity is what makes the skill's output valuable. |
| "I'll dispatch in Phase 2 even for a single-target bulk" | If there's one target, run Steps 1–7 in the main thread after Phase 1 narrows the sources. Dispatch overhead isn't justified without parallelism. |
| "I'll just list what's probably in this repo from memory for Phase 1" | No. The inventory must point at an actual listing (tree API response, glob result, WebFetch of the tree page). Memory-generated inventories yield relevance tables that reference items that don't exist; Phase 2 then fails to fetch them and you've wasted the user's approval step. |
| "A Phase 2 subagent's Edit failed, I'll re-dispatch it" | No. Resume the stuck subagent via `SendMessage` and have it emit the enriched body as text; the main thread applies the write. Re-dispatching throws away 20–50 minutes of analysis per target. |
| "I'll rewrite the frontmatter descriptions for agents whose bodies grew" | No. Flag description drift for the user; don't auto-rewrite. The description encodes user intent for scope, which is authoritative over whatever the extraction pass grew the body into. |
| "This source URL 404'd, I'll skip it" | Not yet. External repos use nested layouts (`plugins/<category>/agents/...`) and non-standard filenames — the Phase 1 inventory may have produced a URL the top-level tree doesn't resolve. Fall back to `gh api repos/.../contents/PATH` or a tree walk to discover the actual path. Only skip after discovery also fails. |
| "I'll dispatch the lens alone and let subagents anchor patterns to whatever" | Extraction yield collapses when subagents have no project-specific hooks. Include a project-anchors section in the dispatch prompt (specific libraries, data stores, module conventions, architectural rules) pulled from `CLAUDE.md` or existing agent bodies. Do not invent anchors. |

## Integration

- **Depends on:** A target agent file must exist (created via `sdlc-create-agent` or manually)
- **Feeds into:** Updated agent definitions with richer domain knowledge; may surface knowledge store gaps for `sdlc-ingest`
- **Uses:** WebFetch (for URL sources), Read (for file sources), Edit (for agent file updates), the target agent file, source material
- **Complements:** `sdlc-create-agent` (creates the agent this skill enriches), `sdlc-review` (reviews conventions; this skill enriches content), `sdlc-ingest` (ingests into knowledge stores; this skill enriches agent definitions)
- **Does NOT replace:** `sdlc-review analyze` mode (which extracts process improvements, not agent enrichment), `sdlc-ingest` (which targets discipline knowledge stores, not agent files)
- **DRY notes:** `sdlc-review analyze` also reads external sources, but its output is process improvements and skill/agent convention suggestions. This skill's output is direct agent file content updates. No overlap in output; possible overlap in input sources.
