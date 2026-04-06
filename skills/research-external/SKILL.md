---
name: sdlc-research-external
description: >
  Research external knowledge sources (engineering blogs, conference talks, papers, documentation)
  to find content relevant to the project's technology domains. Dispatches research-analyst agents to
  discover, fetch, classify, and curate articles into tiered reference docs.
  Produces company profiles, article catalogs with URLs, and cross-cutting insight summaries.
  Triggers on "research [company] blog", "find articles from [source]", "what has [company] published",
  "look into [company] engineering", "curate [source] for us", "/sdlc-research-external".
  Do NOT use for ingesting content into SDLC knowledge stores — use sdlc-ingest.
  Do NOT use for exploring project-internal ideas — use sdlc-idea.
  Do NOT use for web searches about specific bugs or library APIs — use direct WebSearch or Context7.
---

# External Knowledge Research

Research external knowledge sources and curate articles relevant to the project's technology domains into tiered reference docs. The skill dispatches research-analyst agents to systematically discover content, then saves structured docs with company profiles, article catalogs, and relevance notes.

**Argument:** `$ARGUMENTS` (company name, blog URL, or topic area to research)

## When This Applies

Use this when the team wants to survey what a company or knowledge source has published that's relevant to the project's work. The hallmark is external discovery — finding and classifying content we haven't read yet.

Signs this skill is appropriate:
- "Research the [Company] engineering blog for things relevant to us"
- "What has [Company] published about [topic]?"
- "Find articles from [source] that relate to [project feature]"
- "Look into [Company]'s engineering blog"
- "Curate [source] for our team to read"
- The user wants a structured inventory of external knowledge, not a single answer

Signs this skill is NOT appropriate:
- Already have the content and want to extract rules into SDLC knowledge stores -> `sdlc-ingest`
- Exploring a project-internal idea -> `sdlc-idea`
- Looking up a specific API or library question -> Context7 or WebSearch directly
- Researching competitors for business strategy -> product research, not this skill

## Manager Rule

Read and follow `ops/sdlc/process/manager-rule.md`. The research-analyst agents do the fetching, reading, and classification. You orchestrate — you do not fetch articles yourself. If you notice a source needs more investigation, dispatch another agent — do not WebFetch it yourself.

## Workflow

```
SCOPE ──> DISCOVER ──> RESEARCH ──> CURATE ──> SAVE ──> PROVENANCE ──> REPORT
  (you)     (you)      (agents)     (you)     (agent)    (you)
                          │
                    ┌─────┴─────┐
                    │ parallel  │
                    │ dispatch  │
                    │ per source│
                    └───────────┘
              research-analyst x N
              (one per source, in parallel)
```

- **You** handle steps 1, 2, 4, 6, 7 (scoping, discovery, curation, provenance, reporting)
- **research-analyst agents** handle step 3 (fetching, reading, classifying articles)
- **general-purpose agent** handles step 5 (writing large docs)
- When multiple sources are researched, dispatch all research agents in a single parallel batch

### 1. Scope

Clarify with the user:
- **Source(s):** Which company/blog/source to research? Get the URL if possible.
- **Domains of interest:** All project domains, or focused on specific areas?
- **Depth:** Single source deep-dive, or broad survey across multiple sources?

**Domain classification lens:** Before dispatching agents, establish the project's technology domains. Check for:
1. Agent definitions in `.claude/agents/` — each agent's domain expertise line reveals a project domain
2. Knowledge stores in `ops/sdlc/knowledge/` — directory names and YAML files reveal domain areas
3. Discipline files in `ops/sdlc/disciplines/` — each discipline maps to a domain
4. User-provided list — the user may specify domains directly

Build a domain table (domain name + examples/keywords) and use it as the classification lens for all research. If no clear domain list emerges, ask the user to enumerate their project's key technology areas before proceeding.

### 2. Discover

Identify entry points for the source. Not all sources are structured the same way:

| Entry Point | How to Find It |
|-------------|----------------|
| RSS feed | `{url}/feed` or `{url}/rss` |
| Sitemap | `{url}/sitemap.xml` or `{url}/sitemap/sitemap.xml` |
| Homepage pagination | Scroll/paginate the main blog page |
| Tag/category pages | `{url}/tagged/{topic}` or `{url}/category/{topic}` |
| Web search | `site:{domain} {topic}` queries for each project domain |

**Important:** No single entry point gives complete coverage. Use at least 2-3 discovery methods per source. Medium-hosted blogs are especially incomplete via sitemap alone — supplement with web search.

**Filter noise:** Medium sitemaps include comment threads alongside real articles. Filter out short conversational slugs (e.g., "hi-vincent", "thanks-for-the-question").

### 3. Research

Dispatch `research-analyst` agent(s) for each source.

**Parallelism:** When researching multiple sources, dispatch one agent per source in a single parallel batch. Each agent works independently.

#### Dispatch Protocol (required context for every agent)

Every research-analyst dispatch prompt MUST include all of the following:

- [ ] **Source URL** and any discovery entry points found in step 2
- [ ] **Project's domain list** (from step 1) as the classification lens
- [ ] **Web search queries** — at minimum: `site:{domain} {topic}` for each relevant project domain
- [ ] **Discovery instructions** — which entry points to try (RSS, sitemap, tag pages, web search)
- [ ] **Output format:**
  - For each article: title, URL, 1-2 sentence summary, key technologies
  - Classify into three tiers:
    - **Tier 1: Directly Applicable** — maps to active or near-term project work
    - **Tier 2: Adjacent & Valuable** — transferable patterns, future reference
    - **Tier 3: Good to Know** — background knowledge, lower priority
  - Note gaps: project domains with no coverage from this source

Dispatch prompts describe WHAT to find and WHY it matters — the research methodology (which URLs to fetch, how to search) is the agent's domain.

### 4. Curate

When agent results return, curate into a reference doc:

**Required sections:**
1. **YAML frontmatter** — title, created date, tags
2. **About [Company]** — Who they are, what they do, scale/size context
3. **Why [Company] Matters to This Project** — Specific technology overlaps, what domains they cover that we care about
4. **Blog URL(s)**
5. **Tier 1 articles** — organized by theme, each with URL + 1-line project relevance note
6. **Tier 2 articles** — same format
7. **Tier 3 articles** — same format (can be condensed)
8. **Key Takeaways** — 5-8 numbered actionable insights specific to the project
9. **Gaps** — Project domains this source doesn't cover, with pointers to better sources

**Naming convention:** `{Company}-Engineering-Blog-Reference.md` (or `{Source}-Reference.md` for non-blog sources)

**Location:** Save to the project's research/reference directory. Check for existing conventions:
- `docs/current_work/research/` (if it exists)
- `docs/research/` or `docs/references/` (common alternatives)
- Ask the user if no convention exists

### 5. Save

1. Write the reference doc to the chosen location
2. If a master catalog exists (e.g., `Tech-Engineering-Blogs-Catalog.md`), update it:
   - Add the new source to the appropriate relevance tier
   - Link to the new reference doc
   - Include article count

### 6. Provenance

Append entries to the provenance log to create a prepared handoff for `sdlc-ingest`:

1. Read `knowledge/provenance_log.md` (or target project's `ops/sdlc/knowledge/provenance_log.md`) to determine the next `prov-YYYY-MM-DD-NNN` ID
2. Append one entry per researched source with:
   - `status: pending-review`
   - `source-type: reference-doc`
   - `source`: path to the saved reference doc from step 5
   - `source-url`: the source blog/site URL
   - `discipline`: primary discipline(s) the content maps to (from SCOPE domain classification)
   - `tier-1-count`: number of Tier 1 articles found
   - `tier-2-count`: number of Tier 2 articles found
   - `notes`: company/source name + brief relevance summary
3. Omit ingestion-specific fields (`files-created`, `files-updated`, `rule-count`, `ingested-by`) — those are populated when `sdlc-ingest` consumes the entry

### 7. Report

Present a summary to the user:
- Source researched
- Total articles found, breakdown by tier
- Top 3-5 most relevant articles with URLs
- Key gaps noted
- Doc location
- Provenance log entries created (IDs and status)

## Agent Selection

| Agent | When to Dispatch | Dispatch Count | What They Do |
|-------|-----------------|----------------|-------------|
| `research-analyst` | Step 3: for every source being researched | One per source, all in parallel | Fetches blog pages, runs web searches, reads articles, classifies by tier, returns structured findings |
| `general-purpose` | Step 5: when the curated doc exceeds ~200 lines | One per doc being saved | Writes the curated reference doc |

**When to use one agent vs. many:** If the user asks to research a single source (e.g., "research the Spotify blog"), dispatch one research-analyst. If multiple sources (e.g., "research all food delivery blogs"), dispatch one agent per source in a single parallel batch — never sequentially.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll fetch and classify the articles myself" | Dispatch research-analyst agents. You orchestrate, they research. |
| "The agent knows what our project does" | Agents start fresh — always include the project domain list and classification lens in the dispatch prompt. Without it, output is unclassified. |
| "The RSS feed has everything" | RSS feeds typically show only 6-10 recent posts. Always supplement with sitemap + web search. |
| "I'll save the raw agent output to the wiki" | Agent output needs curation — add company profile, organize by theme, add key takeaways. |
| "This source only has a few articles, no need for a reference doc" | Even 5-10 relevant articles deserve a structured doc. The structure is the value. |
| "I'll skip the company profile section" | The profile explains WHY the source matters to the project. Without it, future readers lack context. |
| "All articles from a similar company are Tier 1" | Classify rigorously. Infrastructure articles from a relevant company may still be Tier 2/3 if they don't map to active project work. |
| "I'll update the master catalog later" | Update the catalog in the same step as saving the reference doc. |
| "Medium-hosted blogs can be fully crawled via sitemap" | Medium sitemaps are incomplete and noisy (include comment threads). Always supplement with web search. |

## Integration

- **Depends on:** A research/reference directory in the project, project domain knowledge (from agent definitions, knowledge stores, or user input)
- **Feeds into:** `sdlc-ingest` (when the team wants to extract rules from discovered articles into SDLC knowledge stores). The provenance log (`knowledge/provenance_log.md`) is the prepared handoff mechanism — research creates `pending-review` entries, the user approves them to `approved-for-ingest`, and `sdlc-ingest` can consume approved entries directly via "ingest from provenance"
- **Uses:** `research-analyst` agent (primary), `general-purpose` agent (doc writing), WebFetch, WebSearch
- **Complements:** `sdlc-ingest` (this discovers, ingest absorbs), `sdlc-idea` (research may spark ideas)
- **Does NOT replace:** `sdlc-ingest` (that extracts rules into knowledge stores; this catalogs external articles), direct WebSearch (for specific one-off questions)
- **DRY notes:** This skill discovers and catalogs external content. `sdlc-ingest` takes content (potentially discovered by this skill) and extracts structured knowledge rules into SDLC disciplines. The boundary: this skill produces reference docs; `sdlc-ingest` produces knowledge YAML in `ops/sdlc/knowledge/`.
