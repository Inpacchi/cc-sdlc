# SDLC Process Changelog

A living record of how the process evolves through real use. Each entry captures what changed, why, and where the change originated.

---

## Format

Each entry contains:
- **Date** — when the change was made
- **Origin** — what prompted the change (a session, audit finding, or observed friction)
- **What happened** — context leading to the change
- **Changes made** — numbered list of specific file changes
- **Rationale** — why the change improves the process

---

## Example Entry

```
## YYYY-MM-DD: [Brief Title]

**Origin:** [What prompted this — e.g., D7 planning session compliance audit, upstream sync]

**What happened:** [Context — what was observed, what problem was found]

**Changes made:**

1. **`[file path]`** — [what changed and why]
2. **`[file path]`** — [what changed and why]

**Rationale:** [Why this improves the process — the insight that led to the change]
```

---

## 2026-03-25: Add design knowledge stores validated across projects

**Origin:** Cross-project analysis of paire-appetit, sleeved, and neuroloom SDLC implementations. All three projects ingested the same UI/UX design transcripts via sdlc-ingest, producing identical generic knowledge files.

**What happened:** Analyzed knowledge stores across all three downstream projects to identify content validated in multiple projects that should be adopted into the base framework. Four design knowledge files were present in 2+ projects with identical generic content (no project-specific references).

**Changes made:**

1. **`knowledge/design/component-patterns.yaml`** (new) — UI component rules: icons, buttons, navigation, modals, inputs, cards, chips, footers, pricing. 27 rules covering sizing, styling, states, hierarchy. Source: UI/UX design video transcripts.
2. **`knowledge/design/interaction-animation.yaml`** (new) — Interactive states, micro-interactions, animation easing, motion design, loading states, progressive disclosure. Source: UI/UX design video transcripts.
3. **`knowledge/design/visual-design-rules.yaml`** (new) — Color theory (60-30-10 rule, OKLCH palettes), dark mode depth, shadows, gradients, semantic colors. 22 rules. Source: UI/UX design video transcripts.
4. **`knowledge/design/layout-principles.yaml`** (new) — Spacing grids, container reduction, zebra striping, grid strictness by context, whitespace-first separation. 17 rules. Source: UI/UX design video transcripts.
5. **`knowledge/design/README.md`** — Updated structure listing with all 4 new files
6. **`skeleton/manifest.json`** — Added all 4 files to source_files.knowledge

**Rationale:** These files are genuinely generic — they apply to any project with a UI. Validated across 3 independent projects (paire-appetit, sleeved, neuroloom) that all ingested them and found them useful. Shipping in base means new projects get them on initialization instead of needing to re-ingest.

---

## 2026-03-25: Add native skill/agent creation, review, and compliance auditor

**Origin:** CD decision to replace external plugin-dev:agent-development dependency with native SDLC skills and add review/analysis capabilities.

**What happened:** Agent creation previously depended on an external plugin (`plugin-dev:agent-development`). Skill creation had no formal scaffolding. Review of skill/agent quality was not standardized. The compliance auditor subagent (removed in a318519) is restored to be dispatched by sdlc-audit.

**Changes made:**

1. **`skills/sdlc-create-skill/SKILL.md`** (new) — Interactive skill for creating SDLC skills with convention enforcement. Covers purpose definition, skill typing, frontmatter, body scaffolding, red flags, integration, registration. Dispatches sdlc-reviewer as quality gate.
2. **`skills/sdlc-create-agent/SKILL.md`** (new) — Interactive skill for creating domain agents. Replaces plugin-dev:agent-development. Covers domain definition, frontmatter with example blocks, body scaffolding, context map wiring, registration. Dispatches sdlc-reviewer as quality gate.
3. **`skills/sdlc-review/SKILL.md`** (new) — Two modes: review (dispatches sdlc-reviewer on a file) and analyze (compares external sources against existing agents/skills, routes knowledge to sdlc-ingest).
4. **`agents/sdlc-reviewer.md`** (new) — Subagent that reviews skill or agent files against cc-sdlc conventions. Detects file type, applies type-appropriate checklist, returns structured findings.
5. **`agents/sdlc-compliance-auditor.md`** (restored) — Subagent that performs 9-dimension compliance scan. Returns structured findings — does not do triage or fixes. Dispatched by sdlc-audit.
6. **`skills/sdlc-audit/SKILL.md`** — Updated compliance mode to dispatch sdlc-compliance-auditor subagent instead of scanning inline. Updated Integration section.
7. **`agents/AGENT_SUGGESTIONS.md`** — Replaced plugin-dev:agent-development references with /sdlc-create-agent
8. **`skills/sdlc-initialize/SKILL.md`** — Replaced 5 plugin-dev:agent-development references with /sdlc-create-agent
9. **`skills/sdlc-plan/SKILL.md`** — Replaced plugin-dev:agent-development reference with /sdlc-create-agent
10. **`process/overview.md`** — Replaced plugin-dev:agent-development reference with /sdlc-create-agent
11. **`skeleton/manifest.json`** — Added 3 new skills and 2 new agents to source_files
12. **`CLAUDE-SDLC.md`** — Added commands for sdlc-create-skill, sdlc-create-agent, sdlc-review

**Rationale:** Removes external plugin dependency for agent creation. Adds skill creation scaffolding and quality review that didn't previously exist. Both creation skills enforce cc-sdlc conventions and dispatch sdlc-reviewer as a quality gate. Restoring the compliance auditor as a subagent allows sdlc-audit to dispatch it while keeping interactive triage in the skill.

---

## 2026-03-25: Remove oberskills plugin dependency

**Origin:** CD decision to remove the last external plugin providing skill logic. Context7 and LSP remain as MCP tool providers.

**What happened:** oberskills provided optional prompt engineering (oberprompt) and web research (oberweb) utilities. Skills that referenced oberweb all used soft "if available" patterns. Removing it simplifies the plugin surface — skills now use WebSearch directly when research is needed.

**Changes made:**

1. **`plugins/oberskills-setup.md`** — Deleted
2. **`plugins/README.md`** — Removed Optional section (oberskills was the only optional plugin)
3. **`CLAUDE.md`** — Removed oberskills from plugin dependencies table
4. **`README.md`** — Removed from directory description and Optional subsection
5. **`process/overview.md`** — Removed oberskills Plugin section from Tooling Integration
6. **`setup.sh`** — Removed oberskills install lines and optional plugins echo
7. **`setup.ps1`** — Removed oberskills install lines and optional plugins echo
8. **`skeleton/manifest.json`** — Removed plugins/oberskills-setup.md from source files
9. **`skills/design-consult/SKILL.md`** — Replaced oberweb with WebSearch
10. **`skills/sdlc-idea/SKILL.md`** — Replaced oberweb with WebSearch
11. **`skills/sdlc-plan/SKILL.md`** — Replaced oberweb with WebSearch
12. **`skills/sdlc-ingest/SKILL.md`** — Removed oberweb from anti-trigger
13. **`skills/sdlc-initialize/SKILL.md`** — Removed oberskills mention
14. **`templates/planning_template.md`** — Replaced oberweb example with WebSearch

**Rationale:** WebSearch is a native tool available to all agents. Routing through an external plugin skill added indirection without benefit. After this change, context7 and LSP are the only plugins — both provide tool capabilities (MCP), not skill logic.

---

## 2026-03-25: Remove design-for-ai plugin dependency

**Origin:** CD decision to remove the design-for-ai plugin from the framework.

**What happened:** The design-for-ai plugin was an optional dependency that enriched design-consult with Design for Hackers references. Removing it simplifies the plugin surface — design-consult now uses general design theory principles from agent knowledge instead of plugin-specific reference files.

**Changes made:**

1. **`plugins/design-for-ai-setup.md`** — Deleted
2. **`skills/design-consult/SKILL.md`** — Removed all `[PLUGIN: design-for-ai]` markers, plugin reference table, and plugin-specific dispatch instructions. Replaced with general design theory research approach.
3. **`plugins/README.md`** — Removed design-for-ai from optional plugins table and description
4. **`CLAUDE.md`** — Removed design-for-ai from plugin dependencies table
5. **`README.md`** — Removed design-for-ai from plugins section and directory description
6. **`skeleton/manifest.json`** — Emptied optional_plugins array
7. **`skills/sdlc-initialize/SKILL.md`** — Removed design-for-ai mention from optional plugins note
8. **`setup.sh`** — Removed `--with-optional` flag and design-for-ai install block
9. **`setup.ps1`** — Removed `-WithOptional` parameter and design-for-ai install block

**Rationale:** Reduces plugin surface area. Design theory grounding is maintained through agent knowledge rather than a separate plugin with reference files.

---

## 2026-03-25: Review skill renames — verb-first naming convention

**Origin:** CD naming convention change — review-related skills now use `review-` prefix for consistent verb-first naming.

**What happened:** The three review skills (`diff-review`, `commit-review`, `commit-fix`) used inconsistent naming: two were noun-verb and one was noun-noun. Renaming to `review-diff`, `review-commit`, `review-fix` aligns them under a common `review-` prefix.

**Changes made:**

1. **`skills/diff-review/` → `skills/review-diff/`** — Directory and skill name renamed
2. **`skills/commit-review/` → `skills/review-commit/`** — Directory and skill name renamed
3. **`skills/commit-fix/` → `skills/review-fix/`** — Directory and skill name renamed
4. **All cross-references updated** — skeleton/manifest.json, process/discipline_capture.md, process/review-fix-loop.md, process/finding-classification.md, skills/sdlc-tests-run, skills/design-consult, skills/sdlc-idea, knowledge/README.md, and historical changelog entries

**Rationale:** Verb-first naming (`review-*`) groups related skills visually in listings and makes the action clear from the prefix. All three skills are part of the review workflow and now share the `review-` namespace.

---

## 2026-03-24: Interactive Triage Phase in sdlc-audit

**Origin:** CD question about how to triage promotion candidates — the audit identified them but left triage as a separate manual step.

**What happened:** The audit surfaced parking lot entries and agent memory patterns as INFO findings with "promote at next triage," but there was no triage mechanism built into the audit workflow. CD had to remember to come back and triage separately, which meant it often didn't happen.

**Changes made:**

1. **`skills/sdlc-audit/SKILL.md`** — Added TRIAGE to the compliance workflow diagram. Added "Interactive Triage Phase" section explaining the post-report triage flow.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — Added step 11 (Interactive Triage) to the audit sequence. Full workflow: collect candidates from §6c and Dimension 8, present grouped by discipline via AskUserQuestion, apply CD decisions (promote/defer/skip), append triage results to audit artifact. Updated §6c triage authority matrix to reference step 11 for CD-only transitions. Added Triage Results section to report format template. Updated severity levels — promotion candidates handled in triage, no longer INFO findings.

**Rationale:** The audit already has the context and candidates loaded — making triage a separate step creates friction and drop-off. Inline triage during the audit keeps the pipeline flowing: audit identifies → CD decides → promotions applied → knowledge stores updated, all in one session.

---

## 2026-03-24: Agent Memories Not Git-Tracked; Knowledge Flows Through SDLC Pipeline

**Origin:** CD question about whether agent memories belong in git at all, following the commit completeness work.

**What happened:** Agent memories (`.claude/agent-memory/`) were being committed alongside code, but they're inherently a per-agent scratchpad — noisy, prone to merge conflicts, and redundant with the knowledge store pipeline. The valuable signal in agent memories should flow upward through `knowledge_feedback` → discipline capture → knowledge stores, not sideways into git.

**Changes made:**

1. **`agents/AGENT_TEMPLATE.md`** — Added "Surfacing Learnings to the SDLC" section to the Persistent Agent Memory block. Explains that memory is private/untracked, and teaches agents to use `knowledge_feedback` in handoffs and flag reusable patterns for discipline capture rather than hoarding them in memory.
2. **`CLAUDE-SDLC.md` (Agent Conventions)** — Flipped "agent memories committed with code" to "agent memories are not git-tracked" with a pointer to the knowledge flow pipeline.
3. **`CLAUDE-SDLC.md` (Commit Completeness Rule)** — Removed agent memory files from the commit category table.
4. **`skills/sdlc-execute/SKILL.md` (§3b, §4)** — Removed agent memory files from per-phase and final commit staging lists.
5. **`skills/sdlc-lite-execute/SKILL.md` (§4)** — Removed agent memory files from staging list.
6. **`skills/sdlc-initialize/SKILL.md`** — Added Phase 1d: ensure `.claude/agent-memory/` is in `.gitignore`. Added gitignore check to Phase 10 verification checklist.
7. **`skills/sdlc-migrate/SKILL.md`** — Added gitignore provisioning to §2.1 (with `git rm --cached` for previously tracked files). Updated §2.1a step 4 to note agent memories are local-only. Updated §3.1 table to include "Surfacing Learnings" section. Added gitignore status to migration report template.

**Rationale:** Agent memory is a scratchpad; knowledge stores are the canonical record. The framework already has the pipeline (agent discovers pattern → `knowledge_feedback` in handoff → discipline capture → parking lot → promotion to knowledge store). Committing raw memories short-circuits this pipeline and creates noise in git history. Making agents aware of the SDLC knowledge flow ensures valuable learnings still get captured — just through the right channel.

---

## 2026-03-24: Commit Completeness Rule — SDLC Artifacts Must Ship with Code

**Origin:** CD observation that commits consistently omit SDLC documentation, sometimes relegating them to separate follow-up commits.

**What happened:** The staging instructions in `sdlc-execute` and `sdlc-lite-execute` used vague language ("stage all modified files", "application code + any new files") that didn't enumerate SDLC artifact categories. This allowed discipline parking lot entries, knowledge store updates, and process changelog edits to fall through the cracks.

**Changes made:**

1. **`skills/sdlc-execute/SKILL.md` (§3b)** — Per-phase commit staging now explicitly lists discipline entries alongside application code.
2. **`skills/sdlc-execute/SKILL.md` (§4)** — Final commit staging expanded from a one-liner to an enumerated checklist covering result docs, catalog, discipline entries, knowledge stores, process changelog, and review fixes.
3. **`skills/sdlc-lite-execute/SKILL.md` (§4)** — Staging step rewritten to enumerate all artifact categories with a "not just application code" callout.
4. **`CLAUDE-SDLC.md`** — Added "Commit Completeness Rule" section with a category table and the explicit instruction: "Never split SDLC documentation into a separate follow-up commit."

**Rationale:** Documentation is part of the work, not a chore after the work. Splitting it into follow-up commits means it often gets forgotten entirely, creating drift between code state and process artifacts. Explicit enumeration removes ambiguity about what "all modified files" means.

---

## 2026-03-23: Add `project_applicability` Metadata to Knowledge Stores

**Origin:** CD review of whether knowledge stores shipped with cc-sdlc are universally applicable or project-specific. Some stores (payment-state-machine, ml-system-design, MUI-specific testing) are only relevant to certain project types.

**What happened:** Knowledge stores were installed wholesale during initialization with no structured way to assess which ones applied to the target project. Phase 6a of `sdlc-initialize` had a static list of "stack-agnostic" files, but no mechanism for CD to review and prune irrelevant stores.

**Changes made:**

1. **All `knowledge/**/*.yaml` files** — Added `project_applicability` block with `relevant_when` (condition string) and `action_if_irrelevant` (keep/customize/remove). Each file now self-describes when it applies.
2. **`skills/sdlc-initialize/SKILL.md` (Phase 6a)** — Replaced static file list with a structured relevance assessment that reads each file's `project_applicability`, compares against the D1 spec, and presents a keep/customize/remove table to CD for confirmation.
3. **`knowledge/README.md`** — Documented the new `project_applicability` field in the metadata table and added a dedicated section explaining the field, its sub-fields, and the three `action_if_irrelevant` values.

**Rationale:** Projects vary widely — a CLI tool doesn't need payment FSM patterns, and a Django project doesn't need MUI DataGrid test strategies. Embedding relevance conditions in the files themselves makes the assessment portable and auditable. The three-way action (keep/customize/remove) avoids the false binary of "keep everything" vs "delete aggressively" — some files have useful structures worth rewriting for a different stack.

---

## 2026-03-23: Replace `sdlc-compliance-auditor` Agent with Unified `sdlc-audit` Skill

**Origin:** CD identified that auditing should be a skill (invoked with `/sdlc-audit`) rather than an agent, and that the SDLC needed an improvement audit capability alongside compliance — analyzing sessions and commits for process gaps that feed into the self-improving knowledge base.

**What happened:** The compliance auditor agent was a capable but inconsistent interface — it was the only SDLC function that lived as an agent rather than a skill. The user's workflow of analyzing past sessions for SDLC improvements had no home. A unified `sdlc-audit` skill now handles both compliance auditing (migrated from the agent) and improvement auditing (new capability) with flexible input modes: current session, fed session, or fed commits.

**Changes made:**

1. **`skills/sdlc-audit/SKILL.md`** — New unified skill with two modes (compliance + improve) and flexible input resolution. Lean SKILL.md (~1,800 words) with references for detailed methodology.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — Full 9-dimension compliance methodology migrated from `agents/sdlc-compliance-auditor.md`. All audit logic preserved: catalog integrity, artifact traceability, untracked work, knowledge freshness, process health, knowledge layer (6a-6g), migration integrity, agent memory mining, recommendation follow-through.
3. **`skills/sdlc-audit/references/improvement-methodology.md`** — New improvement audit methodology: process friction signals, knowledge gap signals, skill deficiency signals, structural gap signals, commit pattern analysis, categorization framework, and change proposal format.
4. **`skills/sdlc-audit/references/session-reading.md`** — JSONL message type reference and extraction patterns shared by both modes.
5. **`skeleton/manifest.json`** — Added `sdlc-audit` to skills, removed `sdlc-compliance-auditor` from agents.
6. **`CLAUDE-SDLC.md`** — Replaced compliance auditing section and commands table entries with `/sdlc-audit` and `/sdlc-audit improve`.

**Retiring:** `agents/sdlc-compliance-auditor.md` — all functionality absorbed by the skill. The agent file remains in the source repo for reference but is no longer installed to target projects.

**Rationale:** Skills are the consistent interface for all SDLC functions. The improvement audit creates a self-improving loop: sessions produce data → improvement audit extracts signals → process changes are applied → future sessions benefit. Compliance and improvement share infrastructure (session reading, git correlation) but serve different purposes — compliance checks structure, improvement analyzes behavior.

---

## 2026-03-23: Add `sdlc-playbook-generate` Skill

**Origin:** CD identified that completed sessions contain valuable process knowledge that isn't being captured. Specific example: a Slack bot integration session leveraged existing codebase patterns (90% of the way) but missed nuances in database setup, Railway service configuration, and env variable management that only surfaced during execution. A playbook would have caught those gaps.

**What happened:** Created a new skill that analyzes previous session conversations (JSONL) and their correlated git commits to produce structured playbooks. The skill performs two-track analysis: Track A captures the process that worked (steps to formalize and repeat), Track B captures the gap (corrections, missed setup, environment surprises, configuration gotchas). The combined output fills the existing playbook template format.

**Changes made:**

1. **`skills/sdlc-playbook-generate/SKILL.md`** — New skill with LOCATE → CORRELATE → ANALYZE → DRAFT → PLACE → REPORT workflow. Reads session JSONL for conversation analysis, correlates with git log by timestamp range, extracts process steps and gap signals, produces playbook following project template.
2. **`skills/sdlc-playbook-generate/references/analysis-methodology.md`** — Detailed extraction patterns for reading session JSONL message types, identifying correction signals in user messages, analyzing git commit patterns, and mapping analysis output to playbook template sections.
3. **`skeleton/manifest.json`** — Added skill to source_files.skills list.
4. **`CLAUDE-SDLC.md`** — Added "Make a playbook from that session" to SDLC Commands table.

**Rationale:** Session conversations contain two categories of knowledge that git log alone cannot preserve: (1) the decision sequence and agent selection that produced the work, and (2) the corrections, missing steps, and environment gaps that only surfaced during execution. Formalizing both into playbooks prevents repeated friction on recurring task types. This complements `sdlc-ingest` (external knowledge import) by providing internal session knowledge import.

---

## 2026-03-23: Add `spec_relevant` Tagging to Knowledge Stores

**Origin:** D2 (User Accounts & Auth) spec audit for Neuroloom revealed that spec-writing agents lacked access to knowledge stores that would have improved the spec — specifically data modeling patterns, security taxonomy, and design system knowledge. All knowledge loaded identically at spec time and plan time with no differentiation.

**What happened:** Analysis showed that some knowledge stores shape *what* gets built (domain models, design methodology, security posture) while others shape *how* it gets built (code patterns, debugging, deployment). Loading implementation-detail stores at spec time wastes context budget without improving spec quality. A `spec_relevant` boolean field was designed to let `sdlc-plan` selectively filter knowledge at Step 2.

**Changes made:**

1. **`knowledge/**/*.yaml` (38 files)** — Added `spec_relevant: false` to all framework knowledge YAML files as a top-level metadata field. Default is `false` because spec-relevance is project-specific.
2. **`knowledge/README.md`** — Added "Knowledge File Metadata Fields" section documenting the `spec_relevant` field, its semantics (`true` = shapes what gets built, `false` = shapes how), opt-in filtering behavior, and examples of typically spec-relevant vs not-spec-relevant stores.
3. **`skills/sdlc-plan/SKILL.md`** — Added "Spec-time knowledge filtering (opt-in)" block to Step 2. When at least one file has `spec_relevant: true`, only `true`-tagged files load at spec time. If no files are tagged, all files load (backward compat). `testing-paradigm.yaml` always loads regardless of tag.
4. **`skills/sdlc-ingest/SKILL.md`** — Added `spec_relevant: false` to the YAML template in Step 4 (Structure). Added tagging guidance in Step 5 (Place). Added `SPEC RELEVANCE` section to the ingestion report template (Step 6).
5. **`skills/sdlc-migrate/SKILL.md`** — Changed knowledge YAML strategy from "direct copy" to "direct copy with `spec_relevant` preservation" (§2.1b). Added preservation protocol: project `true` overrides are restored after upstream copy; upstream `true` upgrades are surfaced in the migration report. Added first-migration tagging walkthrough for projects encountering the field for the first time.
6. **`skills/sdlc-initialize/SKILL.md`** — Added Phase 6d "Spec-Relevance Tagging" with CD walkthrough for tagging stores after knowledge seeding.

**Rationale:** Spec-level decisions (data model shape, security posture, design language) should be informed by project knowledge, but implementation-detail stores (code patterns, debugging, deployment) add noise at spec time without improving what-to-build decisions. Per-project tagging with opt-in filtering gives projects control without breaking existing behavior.

---

## 2026-03-23: Fix Migration Pre-Flight to Auto-Clone from `source_repo`

**Origin:** Even after adding `source_repo` to the manifest, the migrate skill still asked the user for a local path instead of cloning automatically.

**What happened:** The pre-flight instructions presented the clone step as a conditional afterthought ("If the manifest has a `source_repo` URL but no local clone path was given..."). The assessment template also showed `cc-sdlc source repo: [path]` implying a local path was required before reporting. Claude read this as "I need a local path first" and prompted the user instead of cloning.

**Changes made:**

1. **`skills/sdlc-migrate/SKILL.md` Pre-Flight Check** — Restructured into two explicit steps: Step 1 resolves the source (clone immediately if `source_repo` is a URL), Step 2 reports the assessment. The clone command is now presented as the default action for URL sources with explicit reassurance ("This is safe and expected"). Fixed `/tmp` path to use a static name instead of shell `$$` variable.

**Rationale:** Skill instructions must be unambiguous about what to do vs what to ask about. Presenting the clone as a conditional buried after the assessment template caused Claude to skip it and prompt instead.

---

## 2026-03-23: Add `source_repo` to Manifest and Fix Migration Source Resolution

**Origin:** User ran `/sdlc-migrate` from neuroloom and the skill couldn't locate the cc-sdlc source repo — it asked for the path, and the user had to decline because there was no way to auto-resolve it.

**What happened:** `setup.sh` wrote `source_version` (commit hash) to `.sdlc-manifest.json` but never wrote the source repo location. The migrate skill had no way to find the cc-sdlc repo without user input. Additionally, when `source_version` was `"unknown"`, the skill treated this as a blocker instead of falling back to a full migration.

**Changes made:**

1. **`setup.sh`** — Added `source_repo` field to the manifest, set to the git remote origin URL (not a local path — local paths break on different machines or when the repo moves).
2. **`skills/sdlc-migrate/SKILL.md` Pre-Flight Check** — Added explicit source resolution order: `$ARGUMENTS` (local path) → manifest `source_repo` (git URL, cloned to temp dir) → ask user.
3. **`skills/sdlc-migrate/SKILL.md` §1.1** — Clarified that `source_version: "unknown"` triggers a full migration (compare all files) instead of blocking.

**Rationale:** Migration should work without manual input when the manifest has enough information. The git remote URL is stable across machines and clones — unlike a local absolute path which breaks if the repo moves or the user is on a different machine.

---

## 2026-03-23: New Skill — sdlc-ingest (Bulk Knowledge Import)

**Origin:** Analysis of a real ingestion session on paire-appetit that processed 27 UI/UX video transcripts into design knowledge files. The session produced 50+ structured rules across 5 YAML files, 8 parking lot entries, and a playbook — revealing a repeatable, high-value workflow with no formal process.

**What happened:** Knowledge stores today grow organically from discipline capture during work sessions. Bulk import from curated external sources (transcripts, articles, documentation, architecture papers, postmortems) is a powerful accelerator but was done ad-hoc. The paire-appetit session demonstrated the full pattern: survey content → scope target discipline → extract testable rules → structure into YAML → place in knowledge files vs. parking lots → report coverage and gaps.

**Changes made:**

1. **`skills/sdlc-ingest/SKILL.md`** — New skill with 7-step workflow (Survey → Scope → Extract → Structure → Place → Report → Changelog). Enforces source attribution, deduplication against existing knowledge, aggressive filtering (rules must be testable), and the discipline lifecycle (validated → YAML, unvalidated → parking lot).
2. **`skeleton/manifest.json`** — Added `skills/sdlc-ingest/SKILL.md` to source_files.skills.

**Rationale:** The discipline lifecycle (parking lot → validate → promote → knowledge store) was designed for organic, per-session capture. Bulk external import is a distinct workflow that needs its own guardrails: deduplication, source attribution, filtering criteria, and structured output conventions. Formalizing it as a skill ensures consistent quality when teams accelerate knowledge store population from external sources.

---

## 2026-03-23: Scan Agent Memory Files for Stale Paths During Migration

**Origin:** Real migration discovered two stale knowledge file paths hardcoded in agent memory files — a path source that §2.1a didn't scan.

**What happened:** Agent memory files (`.claude/agent-memory/*.md`) can contain hardcoded paths to knowledge files (e.g., "read ops/sdlc/knowledge/architecture/foo.yaml for context"). These paths bypass the agent-context-map, so when §3.3 updates the map, the stale paths in memories remain. The migration completed successfully but left two broken references that agents would follow.

**Changes made:**

1. **`skills/sdlc-migrate/SKILL.md` §2.1a** — Added step 4: grep agent memory files for each deleted/moved path and fix matches. Agent memories are now scanned alongside the context map and skill files.

2. **`disciplines/process-improvement.md`** — Added parking lot entry documenting the gap and fix.

**Rationale:** Three places reference knowledge file paths: the context map (§3.3), skill files (§2.2), and agent memories. The migration scanned two of three. This completes the coverage.

---

## 2026-03-23: Rename Skills for Consistent sdlc- Prefix

**Origin:** CD requested skill name standardization. Three skills used inconsistent naming: `sdlc-reconciliation` (too long), `test-loop` (no prefix), `create-test-suite` (no prefix).

**What happened:** All other skills use the `sdlc-` prefix convention. These three predated the convention and were never renamed.

**Changes made:**

1. `sdlc-reconciliation` → `sdlc-reconcile` — directory, frontmatter name
2. `test-loop` → `sdlc-tests-run` — directory, frontmatter name, trigger phrases
3. `create-test-suite` → `sdlc-tests-create` — directory, frontmatter name, all internal references to `test-loop`

**Cross-references updated:** `sdlc-execute`, `sdlc-lite-execute`, `sdlc-archive`, `sdlc-migrate`, `CLAUDE-SDLC.md`, `README.md`, `skeleton/manifest.json`, `knowledge/README.md`, `sdlc-tests-create` (internal refs to test-loop), `sdlc-tests-run` (trigger phrases + "do not use" guidance).

**Migration note:** Old skill directories will be orphaned in downstream projects. The `sdlc-migrate` skill's §2.1a (deleted file detection) will clean them up. `setup.sh` will install the new directories automatically (new files are always installed).

---

## 2026-03-22: Convert MIGRATE.md to sdlc-migrate Skill

**Origin:** Same reasoning as BOOTSTRAP.md removal — a doc drifts, a skill is the canonical entry point. MIGRATE.md had a Phase 0 self-update workaround because the doc being followed was itself subject to the update. Converting to a skill eliminates the bootstrapping problem entirely — skills are always installed from the source repo.

**What happened:** MIGRATE.md was the last standalone instruction doc. BOOTSTRAP.md was already converted to `sdlc-initialize`. The migration flow had the same drift risk — and an additional self-referential problem where the migration instructions needed to update themselves before executing.

**Changes made:**

1. **`skills/sdlc-migrate/SKILL.md`** (new) — Full migration skill with frontmatter, trigger phrases, pre-flight check, and Red Flags table. Content from MIGRATE.md with Phase 0 (self-update) removed (unnecessary as a skill). Added pre-flight check to verify this is a migration not an initialization.
2. **`MIGRATE.md`** — Deleted.
3. **`setup.sh`** — Removed MIGRATE.md from copy list and required files. Updated manifest comment and user-facing messages.
4. **`skeleton/manifest.json`** — Removed MIGRATE.md from top_level. Added `skills/sdlc-migrate/SKILL.md` to skills list.
5. **`CLAUDE.md`** — Replaced MIGRATE.md entry with sdlc-migrate skill reference.
6. **`CLAUDE-SDLC.md`** — Updated "Migrate my SDLC framework" command to reference the skill.
7. **`agents/sdlc-compliance-auditor.md`** — Updated migration integrity reference from MIGRATE.md to sdlc-migrate skill.
8. **`skills/sdlc-initialize/SKILL.md`** — Updated skeleton check from MIGRATE.md to sdlc-migrate skill path.

**Rationale:** Skills are the canonical interface. They're installed from the source repo, so they're always current. They have frontmatter for trigger detection. They have Red Flags tables for anti-patterns. A standalone doc has none of this. With both BOOTSTRAP.md and MIGRATE.md converted to skills, all SDLC entry points are now skills — no orphan docs to drift.

---

## 2026-03-22: Remove BOOTSTRAP.md — sdlc-initialize Supersedes It

**Origin:** CD review of how existing repos get bootstrapped. BOOTSTRAP.md was a legacy manual reference that predated the `sdlc-initialize` skill.

**What happened:** BOOTSTRAP.md contained a manual Phase 1-4 walkthrough for initializing cc-sdlc in a project. The `sdlc-initialize` skill was built later and handles the same flow (greenfield + retrofit) with mode detection, CD approval gates, and structured phases. BOOTSTRAP.md was redundant — and worse, its retrofit instructions diverged from the skill's (the skill had been updated while BOOTSTRAP.md stayed stale).

**Changes made:**

1. **`BOOTSTRAP.md`** — Deleted.
2. **`skills/sdlc-initialize/SKILL.md`** — Inlined the retrofit discovery categorization table and proposal steps (previously referenced BOOTSTRAP.md Phase 1-2). Removed `BOOTSTRAP.md` from Integration references.
3. **`setup.sh`** — Removed BOOTSTRAP.md from required files check and copy list.
4. **`skeleton/manifest.json`** — Removed from source_files list and updated comment.
5. **`MIGRATE.md`** — Removed from categorization table (§1.3) and direct copy list (§2.1). Updated "Migration vs Bootstrap" to "Migration vs Initialization" referencing `sdlc-initialize`.
6. **`process/overview.md`** — Removed BOOTSTRAP.md reference, added note that retrofit mode is built into the skill.
7. **`CLAUDE.md`** — Replaced BOOTSTRAP.md entry with MIGRATE.md in project structure table.
8. **`README.md`** — Rewrote Quick Start to point to `sdlc-initialize` instead of BOOTSTRAP.md. Removed manual "Adopt the Skills" step (the skill handles it).

**Rationale:** One source of truth for initialization. When the skill and a reference doc cover the same ground, the doc drifts and becomes a liability. The skill is the canonical entry point; MIGRATE.md handles updates. No manual bootstrap doc needed.

---

## 2026-03-22: Add Phase 0 Self-Update to MIGRATE.md

**Origin:** CD identified that the migrator reads the project's (old) copy of MIGRATE.md, not the source repo's (current) copy. New gates and strategies added in this session would not take effect until one migration too late.

**What happened:** MIGRATE.md is listed in §2.1 as a direct-copy file — it gets overwritten during migration. But the migrator is already executing the old version's instructions. If the new version adds a gate (like §1.2 Changelog Review), that gate doesn't exist in the old instructions, so it's skipped. The fix arrives on disk during §2.1, but by then the migrator has already passed Phase 1 without the gate.

**Changes made:**

1. **`MIGRATE.md` Phase 0** (new) — Self-Update. Before doing anything, the migrator reads the cc-sdlc source repo's MIGRATE.md and copies it to the project. The rest of the migration then follows current instructions. Includes rationale for why this must be first.

**Rationale:** Classic bootstrapping problem. The instructions governing the update are themselves subject to the update. Phase 0 ensures the migrator always runs the latest instructions, not the previous version's. This is the same pattern as a package manager updating itself before updating packages.

---

## 2026-03-22: Add Migration Gates to MIGRATE.md

**Origin:** CD review of migration flow after fixing GAP-1 (new role entries) and RISK-1 (tracker markers). Identified that the migration was a single pass with all verification deferred to the end.

**What happened:** For small migrations, single-pass works. For large ones (5+ commits, new directories, structural marker additions), deferring all verification to Phase 4 puts too much trust in the final audit. Three gaps: (1) the migrator starts applying changes without reading the changelog — misses breaking changes and items needing user input, (2) content-merge errors aren't caught until Phase 4 — by which time agent wiring decisions may already be wrong, (3) CLAUDE-SDLC.md compatibility is never checked — renamed skills or changed conventions leave stale references in the project's CLAUDE.md.

**Changes made:**

1. **`MIGRATE.md` §1.2** (new) — Changelog Review Gate. Before categorizing or applying anything, the migrator reads all changelog entries since the project's source version. Surfaces breaking changes, new capabilities, and items needing user input. Presents a migration summary and waits for user confirmation before proceeding. Old §1.2 renumbered to §1.3.

2. **`MIGRATE.md` §2.5** (new) — Content-Merge Verification Gate. After applying framework updates (§2.1–2.4) but before touching project agents (Phase 3), the migrator spot-checks: tracker integrity (markers present, project levels preserved), parking lot preservation (triage markers intact), skill customization preservation, and auditor memory path. Catches merge corruption before it propagates into agent wiring.

3. **`MIGRATE.md` §4.3a** (new) — CLAUDE-SDLC.md Compatibility Check. Verifies that the project's CLAUDE.md still references valid skill names, process file paths, and conventions. Checks for new sections in CLAUDE-SDLC.md that should be merged. Flags stale references from renamed skills or changed conventions.

4. **`MIGRATE.md` §4.6** — Updated migration report format: added "New agent roles" and "CLAUDE-SDLC.md sections updated" to Changes Applied. Added "Gates Passed" section documenting §1.2, §2.5, and §4.3a gate results.

**Rationale:** Migration safety scales with gate count, not audit thoroughness. A single audit at the end catches errors but can't prevent them from compounding. Three lightweight gates (changelog read, merge spot-check, CLAUDE.md compatibility) add ~5 minutes to a migration and catch the three failure modes that compound: applying changes without context, propagating merge errors, and leaving stale CLAUDE.md references.

---

## 2026-03-22: Fix Migration Gaps — New Role Entries and Tracker Markers

**Origin:** Bootstrap/migrate verification agent identified two gaps in MIGRATE.md coverage after the parking lot promotion commit.

**What happened:** The parking lot promotion added a new `business-analyst` role to the agent-context-map. MIGRATE.md §3.3 only covered adding files to existing roles, moved files, and removed files — not adding entirely new role sections. Separately, the Process Maturity Tracker lacked structural markers, making it dependent on migrator judgment to avoid overwriting project-assessed levels.

**Changes made:**

1. **`MIGRATE.md` §3.3** — Added fourth scenario: "New role entries." When cc-sdlc adds a new role to the agent-context-map, the migrator checks if the downstream project has a matching agent (by role or responsibility), wires accordingly, and notes the addition in the migration report.

2. **`disciplines/process-improvement.md`** — Added `<!-- PROJECT-TRACKER-START -->` and `<!-- PROJECT-TRACKER-END -->` HTML comment markers around the Process Maturity Tracker table. These are machine-readable boundaries that prevent accidental overwrite during content-merge.

3. **`MIGRATE.md` §2.3 rule 6** — Updated to reference the structural markers. Migrators now look for the marker boundaries instead of relying on judgment. Includes fallback for downstream files that predate the markers.

**Rationale:** Migration safety requires mechanical precision, not judgment calls. The new role scenario was a genuine gap — BA knowledge files would be installed but never wired. The structural markers convert a "be careful here" instruction into a "stop at this boundary" instruction, which is more reliable for both human and AI migrators.

---

## 2026-03-22: Promote 4 Parking Lot Items Across Disciplines

**Origin:** CD-initiated triage of parking lot items across all disciplines.

**What happened:** Reviewed all 9 discipline parking lots for items mature enough to promote. Identified 4 items with strong evidence from actual framework usage: cross-discipline remediation flow (validated through 4 real instances), health check prerequisite pattern (validated through testing discipline's recipe), bidirectional acceptance criteria (validated through testing practice), and token economics (validated through daily framework usage). All 4 were `[NEEDS VALIDATION]`; all had cross-discipline evidence.

**Changes made:**

1. **`knowledge/architecture/knowledge-management-methodology.yaml`** — Added `cross_discipline_remediation` section documenting the generalized pattern (producer captures → parking lot → consumer polls → triage) with 4 validated instances, how-to-apply guidance, and anti-patterns. Promoted from `disciplines/process-improvement.md`.

2. **`knowledge/architecture/deployment-patterns.yaml`** — Added `pre_deploy_readiness_checks` section recontextualizing the testing discipline's health check recipe as a deployment gate (frontend, API, proxy, database checks). Promoted from `disciplines/deployment.md`.

3. **`knowledge/business-analysis/requirements-feedback-loops.yaml`** (new file) — BA's first knowledge store file. Three sections: bidirectional acceptance criteria flow, test data design as domain modeling, and domain validation of computed values. Promotes all 3 seeded insights from `disciplines/business-analysis.md`.

4. **`knowledge/business-analysis/README.md`** (new file) — Knowledge store README for BA discipline.

5. **`knowledge/architecture/token-economics.yaml`** (new file) — Context window constraints as architectural constraint. Four dimensions: knowledge retrieval, codebase scope, workflow accumulation, review depth. Promoted from `disciplines/architecture.md`.

6. **`knowledge/agent-context-map.yaml`** — Added `business-analyst` role mapping to `requirements-feedback-loops.yaml`. Added `token-economics.yaml` to `architect` mapping.

7. **`disciplines/process-improvement.md`** — Updated maturity tracker: BA upgraded from Level 1 to Level 2 (knowledge store + agent wiring + all insights promoted). Architecture file count updated to 17.

8. **`disciplines/*.md`** (4 files) — All promoted entries marked with `Promoted →` and target file references.

9. **`skeleton/manifest.json`** — Added `knowledge/business-analysis/` directory, `requirements-feedback-loops.yaml`, `README.md`, and `token-economics.yaml` to canonical file list.

**Rationale:** Parking lot triage keeps the discipline pipeline healthy. These 4 items had accumulated enough evidence through real framework usage to graduate from speculative insights to validated knowledge. The BA promotion is notable — it bootstraps BA from Level 1 to Level 2, leaving only Deployment at Level 1. The cross-discipline remediation flow promotion codifies a pattern that was already working implicitly across 4 discipline pairs.

---

## 2026-03-22: Implement Self-Improving Discipline Process (3 Phases)

**Origin:** CD requested a mechanism to make disciplines, knowledge stores, and skills self-improving — closing the feedback loop from "agent does work" to "knowledge improves" with minimal manual gates.

**What happened:** The discipline pipeline had manual gates at every step: CD notices a pattern → tells CC to capture it → triages at planning boundaries → approves promotion. Detection and capture were entirely vibes-based. Agents consumed knowledge silently with no feedback mechanism. The auditor surfaced triage items but never acted on them.

**Changes made (Phase 1 — Enhanced Discipline Capture):**

1. **`process/discipline_capture.md`** — Added "Structured Gap Detection" section before the existing freeform scan. Three comparisons: knowledge loaded vs. needed (conditional on Phase 2 data), cross-domain friction, and iteration cost (judgment-based). Added skill applicability table, GAP entry format with 5 types (`MISSING_KNOWLEDGE`, `UNMAPPED_KNOWLEDGE`, `STALE_KNOWLEDGE`, `CROSS_DOMAIN_FRICTION`, `RESURFACING_PATTERN`), updated time budget to <3min, and added auditor triage carve-out for Manager Rule.

2. **7 skill files updated** — sdlc-execute (step 3a), sdlc-lite-execute (step 3a), sdlc-plan (step 5a), sdlc-lite-plan (step 3a): one-line addition noting structured gap detection with triage/dispatch data. sdlc-idea (crystallize), design-consult (finalize): one-line addition noting only comparison #2 applies.

**Changes made (Phase 2 — Agent Knowledge Feedback):**

3. **`knowledge/architecture/agent-communication-protocol.yaml`** — Added `knowledge_feedback` section under handoff format. Four optional string array fields: `loaded`, `useful`, `not_relevant`, `missing`. Includes consumer documentation (discipline capture and compliance auditor).

4. **`agents/AGENT_TEMPLATE.md`** — One sentence added to Knowledge Context paragraph instructing agents to optionally include feedback in their handoff.

**Changes made (Phase 3 — Auditor Auto-Triage):**

5. **`agents/sdlc-compliance-auditor.md` §6c** — Added triage authority matrix (auditor auto-applies unmarked→[NEEDS VALIDATION] after ≥2 cycles, [NEEDS VALIDATION]→[DEFERRED] after ≥3 cycles; CD-only for [READY TO PROMOTE] and promotions). Added auto-triage logging format (conditional — emitted only when actions taken). Added promotion draft format with YAML skeleton. Added feedback-informed triage with matching confidence criteria.

6. **`agents/sdlc-compliance-auditor.md` §6g** — Added 5th usage signal: agent knowledge feedback aggregation from result docs.

**How the cycle closes:**
```
Agent work → knowledge_feedback in handoff → structured gap detection writes GAP entries →
parking lots accumulate → auditor auto-triages low-risk items + drafts promotions →
CD approves → knowledge YAML created → agent-context-map updated → agents load new knowledge →
agents report feedback → cycle continues
```

**Rationale:** Three mechanisms that compose into a feedback loop. Phase 1 (enhanced capture) detects gaps using data already in context. Phase 2 (agent feedback) provides the data source that makes Phase 1 most effective. Phase 3 (auto-triage) acts on accumulated data to keep parking lots curated. CD retains approval authority for all promotions — automation handles detection and curation only.

---

## 2026-03-22: Fix migration gaps for moved files, context-map paths, and maturity tracker

**Origin:** Tracing this session's changes through the migration path revealed three gaps: moved files leave orphans, agent-context-map path changes aren't handled, and the maturity tracker gets overwritten with source-repo levels.

**What happened:** We moved `typescript-patterns.yaml` and `risk-assessment-framework.yaml` to new directories. Migration's direct-copy strategy would create the new files but leave the old copies in place. The agent-context-map (marked "never overwrite") would keep pointing to the old paths. And the discipline content-merge would overwrite the downstream project's maturity tracker with the source repo's levels.

**Changes made:**

1. **`MIGRATE.md` §2.1a** (new) — "Remove Deleted and Moved Files." Uses `git diff --diff-filter=DR` to identify files that were deleted or moved in cc-sdlc, removes old copies from downstream, and updates agent-context-map paths. Includes rationale for why orphan files are dangerous (agents load stale copies).

2. **`MIGRATE.md` §3.3** — Expanded from "add new mappings" to handle three scenarios: new knowledge files, moved/renamed files (path replacement), and removed files (reference cleanup). Still preserves project-specific mappings.

3. **`MIGRATE.md` §2.3** — Updated discipline content-merge to explicitly preserve: parking lot triage markers (project may have triaged differently), project context sections (from sdlc-initialize Phase 7), and the Process Maturity Tracker table (project-assessed levels, not source repo levels).

4. **`MIGRATE.md` §1.2** — Updated categorization table: knowledge YAMLs note §2.1a check, context map notes §3.3 path updates.

5. **`MIGRATE.md` §4.6** — Updated migration report format to include file removals and context-map path changes.

**Rationale:** Migration must be safe for the changes it carries. Every session that moves, deletes, or reorganizes framework files creates a migration hazard if MIGRATE.md doesn't account for it. These three gaps (orphan files, stale map paths, tracker overwrite) would have caused silent failures in downstream projects — agents loading stale knowledge, levels that don't reflect reality, and growing file cruft.

---

## 2026-03-22: Wire sdlc-initialize to Maturity Level Assessment

**Origin:** Gap analysis of which skills reference the new process docs. Only `sdlc-initialize` had a real gap — it seeds disciplines and knowledge stores but doesn't assess or set initial maturity levels, meaning the tracker is copied from the source repo with source-repo levels rather than reflecting the downstream project's actual state.

**What happened:** After `setup.sh` copies the framework (including the maturity tracker), Phase 7 seeds discipline parking lots and Phases 6/8 seed knowledge stores. But the maturity tracker was never updated to reflect the downstream project's state — it still showed the source repo's levels. A fresh project with only parking lot seeding would claim Level 2 for disciplines it hadn't actually validated.

**Changes made:**

1. **`skills/sdlc-initialize/SKILL.md`** — Added Phase 9a (Assess Initial Maturity Levels) between plugin readiness and final verification. Reads the level definitions, assesses each discipline based on what was actually set up (knowledge store + agent wiring = Level 2; parking lot only = Level 1), and updates the tracker.

2. **`skills/sdlc-initialize/SKILL.md`** — Added maturity tracker verification to the Phase 10 checklist.

3. **`skills/sdlc-initialize/SKILL.md`** — Added maturity assessment as step 9 in retrofit mode.

**Rationale:** The maturity tracker must reflect the downstream project's reality, not the source repo's. A fresh installation inherits all knowledge files but hasn't validated them in the project's context. Phase 9a takes 2-3 minutes and ensures the tracker starts honest.

---

## 2026-03-22: Replace Level 3-5 with Discipline Usage Audit

**Origin:** During Level 3 verification design, realized that Level 3 ("validated on 2+ projects") is inherently unverifiable — it's a cross-project claim that no single-project auditor can check. Adaptations to knowledge files aren't failures (they're the two-tier architecture working), so file diffs can't distinguish "major revision" from "healthy adaptation." Levels 4-5 (Measured, Self-Improving) were aspirational targets no discipline was close to reaching.

**What happened:** CD concluded that levels beyond 2 add complexity without delivering auditable value. The real question isn't "what level is this discipline?" but "is this discipline being used?" — which is an observable, auditable signal.

**Changes made:**

1. **`disciplines/process-improvement.md`** — Removed Levels 3 (Standardized), 4 (Measured), and 5 (Self-Improving). Kept Levels 1 (Initial) and 2 (Managed) as the only maturity levels. Simplified Level Rules from 5 to 4. Simplified Level Assessment procedure. Updated maturity tracker: removed "Next Level Target" column, updated file counts to current reality. Added note that actual discipline health is measured by the usage audit, not levels alone.

2. **`agents/sdlc-compliance-auditor.md` §6g** (new) — Discipline Usage Audit. Four auditable signals per discipline:
   - **Parking lot activity**: Active (entries between audits from skill sessions) / Audit-only (entries only during audits) / Dormant (no entries since last audit)
   - **Knowledge consumption**: Consumed (mapped agents dispatched recently) / Wired but unused (mapped but agents not dispatched) / Unwired (no agent mapping)
   - **Promotion flow**: Flowing (entries being triaged and promoted) / Accumulating (added but not triaged) / Static (no movement)
   - **Cross-discipline feed**: Connected (receives insights from other disciplines' work) / Isolated (only receives from own domain)
   Includes interpretation guidance: healthy, formalized but dead, alive but unformalized, dead. Respects "toolbox not recipe" — dead disciplines are acceptable when not relevant to current work.

3. **`agents/sdlc-compliance-auditor.md` §6a** — Removed Level 3 claim verification. Added note that levels indicate formalization only; actual health is measured by §6g.

4. **`agents/sdlc-compliance-auditor.md`** — Updated audit methodology step 6 to reference §6a–6g (was §6a–6f). Added Discipline Usage Audit table to report format.

5. **`disciplines/README.md`** — Removed "Validate on 2nd project (Level 3)" from the discipline lifecycle flowchart.

**Rationale:** Two auditable levels (Initial, Managed) plus a usage audit is more useful than five levels where only two are verifiable. The usage audit answers "is this discipline alive?" with four observable signals that the auditor can check mechanically — no subjective judgment needed. A Level 2 discipline that's dormant is less healthy than a Level 1 discipline with active capture, and the usage audit surfaces this.

---

## 2026-03-22: Wire Compliance Auditor to Discipline Lifecycle and Maturity Verification

**Origin:** After formalizing maturity level definitions, level assessment procedure, and the new discipline lifecycle, the compliance auditor was not aware of any of them — it still checked "Is the CMMI maturity tracker current?" without criteria to verify claims against.

**What happened:** The auditor's §6a checked parking lot freshness and triage markers but had no mechanism to verify maturity level claims against evidence criteria, detect potential regressions, or identify when a new discipline should be created. The §6b inventory table was also stale (missing `coding/` entirely, wrong file counts for other directories).

**Changes made:**

1. **`agents/sdlc-compliance-auditor.md` §6a** — Added "Maturity level verification" sub-section: auditor reads the formal level definitions in `process-improvement.md`, checks each discipline's claimed level against evidence criteria (Level 1: parking lot exists; Level 2: knowledge store + agent wiring + triage pass), flags unsupported claims and potential regressions.

2. **`agents/sdlc-compliance-auditor.md` §6a** — Added "Missing discipline detection" sub-section: auditor scans for insights filed in wrong parking lots, checks for agent roles orphaned from the discipline structure, and surfaces potential new disciplines to CD using the 3-condition creation criteria from `disciplines/README.md`. Explicitly states: do not recommend new disciplines speculatively.

3. **`agents/sdlc-compliance-auditor.md` §6b** — Updated inventory table from stale 7-row version to current 6-directory layout with accurate file counts. Added note that counts change as knowledge is promoted.

4. **`agents/sdlc-compliance-auditor.md` §6a table** — Updated `process-improvement.md` description to reference maturity level definitions and assessment procedure.

5. **`agents/sdlc-compliance-auditor.md` report format** — Added maturity level verification and missing discipline signals to the Discipline Parking Lots report section.

**Rationale:** The compliance auditor is the enforcement mechanism for process health. Without awareness of the maturity level definitions, level assessment procedure, and discipline creation lifecycle, these processes exist on paper but aren't verified. The auditor now closes three loops: verifying level claims have evidence, detecting level regressions from stale knowledge, and identifying when the discipline structure itself needs to evolve.

---

## 2026-03-22: Add Level Assessment Procedure and New Discipline Lifecycle

**Origin:** During the maturity level formalization, two gaps were identified: (1) levels were defined but there was no procedure for when/how to assess them, and (2) there was no documented process for creating a new discipline — the current 9 were seeded at framework creation with no formal lifecycle.

**What happened:** The maturity tracker had level claims but no assessment procedure — making auditor verification subjective. And the `knowledge/README.md` had a 3-line "Adding a New Discipline" section that only covered adding a knowledge store, not creating the discipline itself.

**Changes made:**

1. **`disciplines/process-improvement.md`** — Added "Level Assessment Procedure" subsection after the progression rules. Covers: when to assess (triage passes, project adoption, audits, major knowledge changes), how to assess (5-step evidence check), who assesses (CD confirms, auditor verifies, CC proposes).

2. **`disciplines/README.md`** — Added "Creating a New Discipline" section with: when to create (3 conditions: recurring capability, no existing home, distinct agent role), minimum viable discipline (4 items: discipline file, tracker entry, manifest entry, hump chart row), full lifecycle flowchart (from observation through Level 2 and optional skill), and 3 anti-patterns to avoid (premature creation, unnecessary ownership, high-intensity hump chart).

3. **`knowledge/README.md`** — Replaced 3-line "Adding a New Discipline" with "Adding a Knowledge Store for a Discipline" — 8-step procedure that references the canonical lifecycle in `disciplines/README.md`. Clarifies that a knowledge store is a Level 2 artifact, not a Level 1 starting point.

**Rationale:** The discipline system had a chicken-and-egg gap: disciplines existed but there was no documented way to create one or assess its maturity. Without a creation lifecycle, new disciplines would either be created too eagerly (speculative process overhead) or never created at all (insights forced into ill-fitting existing disciplines). Without an assessment procedure, the maturity tracker is a snapshot that drifts from reality. Both additions close loops that the triage pass revealed were open.

---

## 2026-03-22: Formalize Process Maturity Level Definitions

**Origin:** During the discipline triage session, the maturity tracker in `process-improvement.md` used Level 1/2/3 labels but the level definitions were only sketched in a `[DEFERRED]` parking lot entry. The compliance auditor checks "Is the CMMI maturity tracker current?" but has no formal criteria for what each level means.

**What happened:** The tracker was updated during the triage pass (six disciplines upgraded from Level 1 to Level 2 based on actual knowledge store evidence), but the level definitions themselves were implicit. "Level 2 (Managed)" meant whatever the reader assumed it meant. This made tracker updates subjective and auditor checks unverifiable.

**Changes made:**

1. **`disciplines/process-improvement.md`** — Added "Process Maturity Levels" section with formal definitions for Levels 1 and 2. Each level includes: description of what it looks like and evidence required to claim it. Also includes 4 level rules (per-discipline assessment, evidence-based, regression possible, auditor verifies claims). Levels 3-5 were initially drafted but removed in the same session — see "Replace Level 3-5 with Discipline Usage Audit" entry above.

2. **`disciplines/process-improvement.md`** — CMMI parking lot entry changed from `[DEFERRED]` to `Promoted →` since the formal definitions now supersede the sketch. Status updated from "Parking lot" to "Active".

**Rationale:** Maturity levels without definitions are aspirational labels, not assessment criteria. Formalizing what "Level 2" means (knowledge store + agent wiring + triage pass) makes the tracker verifiable: the compliance auditor can check evidence against criteria rather than asking "does this feel like Level 2?" The definitions are calibrated to this framework's "toolbox not recipe" principle — Level 2 doesn't mean "always invoked", it means "documented and repeatable when invoked."

---

## 2026-03-22: Fix Compliance Audit Findings (W1, W2, I1-I4)

**Origin:** Follow-up fixes from the 2026-03-22 compliance audit (score 8.5/10).

**What happened:** Audit identified 2 warnings and 4 info items. W1: `domain-boundary-gotchas.yaml` was unmapped in the agent-context-map. W2: `coding.md` knowledge store header pointed to testing-paradigm.yaml instead of `knowledge/coding/`. I1-I3: stale README structure listings and missing inventory entries. I4: process-improvement Level 2 definitional ambiguity — the meta-discipline's "knowledge" is process docs, not YAML files.

**Changes made:**

1. **`knowledge/agent-context-map.yaml`** — Wired `domain-boundary-gotchas.yaml` to architect, code-reviewer, and sdlc-compliance-auditor.
2. **`disciplines/coding.md`** — Fixed knowledge store header to reference `knowledge/coding/`.
3. **`knowledge/testing/README.md`** — Added missing entries for testing-paradigm.yaml and advanced-test-patterns.yaml.
4. **`knowledge/data-modeling/README.md`** — Fixed assessment section placeholder to reference actual `model-health-check.yaml`.
5. **`disciplines/architecture.md`** — Added `domain-boundary-gotchas.yaml` to inventory table.
6. **`disciplines/process-improvement.md`** — Added exception clause to Level 2 evidence: the meta-discipline satisfies Level 2 via `process/` docs rather than `knowledge/` YAML files.

**Rationale:** Audit findings should be fixed promptly. W1 was the highest-impact fix — an unmapped knowledge file means agents never see it. I4 resolved a definitional edge case where the process-improvement discipline was unfairly penalized for not having YAML files when its "knowledge" is inherently process documentation.

---

## 2026-03-22: Reorganize Misplaced Knowledge Files + Stale README Fixes

**Origin:** Domain placement audit of all 44 knowledge files, checking whether each file is in the correct discipline directory.

**What happened:** Two files were found in the wrong domain directory. `typescript-patterns.yaml` (branded types, Result types, exhaustiveness) is about code structure patterns — a coding discipline concern, not system architecture. `risk-assessment-framework.yaml` (legal risk, compliance gaps, COPPA/BIPA) is a product/governance concern, not technical architecture. Additionally, several knowledge READMEs were stale — `architecture/README.md` listed only 2 files when 16 existed, and `product-research/README.md` listed only 2 when 4 existed.

**Changes made:**

1. **`typescript-patterns.yaml`** — Moved from `knowledge/architecture/` to `knowledge/coding/`. Updated `agent-context-map.yaml` (5 agent mappings), `skeleton/manifest.json`, `disciplines/architecture.md` (removed from inventory table), `knowledge/coding/README.md`.

2. **`risk-assessment-framework.yaml`** — Moved from `knowledge/architecture/` to `knowledge/product-research/`. Updated `agent-context-map.yaml` (2 agent mappings), `skeleton/manifest.json`, `disciplines/architecture.md` (removed from inventory table), `knowledge/product-research/README.md`.

3. **`knowledge/architecture/README.md`** — Updated structure listing from 2 files to all 16 current files with descriptions.

4. **`knowledge/product-research/README.md`** — Updated structure listing from 2 files to all 5 current files.

**Rationale:** Knowledge files should live in the discipline they serve, not the discipline that created them. TypeScript patterns are consumed by coders and reviewers for code structure decisions — the architect may have authored them, but the coding discipline owns them. Legal risk assessment is consumed by product owners and legal advisors for business decisions — the architect may assess technical risk, but compliance risk is a product governance concern.

---

## 2026-03-22: First Discipline Parking Lot Triage — Promote 6 Entries to Knowledge

**Origin:** CD-initiated triage of all discipline parking lots. No entries had been triaged since the parking lot system was formalized.

**What happened:** All 27 parking lot entries across 9 discipline files were reviewed for promotion readiness. Six entries were validated through real use across projects and promoted to knowledge stores or process docs. The remaining 21 were triaged as `[NEEDS VALIDATION]` (13) or `[DEFERRED]` (8). The process-improvement maturity tracker was updated to reflect actual levels — six disciplines now at Level 2 (Managed) with active knowledge stores, up from the stale "all Level 1" baseline.

**Changes made:**

1. **`knowledge/coding/` (new directory)** — First knowledge store for the coding discipline. Contains `README.md` and `code-quality-principles.yaml` (testability-as-code-quality, mocking stance, validation gap observations). Promoted from coding.md entries #1 and #4.

2. **`knowledge/design/accessibility-testability-principles.yaml` (new)** — Design-side view of the a11y-testability duality: unified concern principle and color-meaning rule. Promoted from design.md entries #1 and #3.

3. **`knowledge/testing/gotchas.yaml`** — Added `color-only-status-indicators` gotcha (testing-side split of design #1/#3). Cross-references the design knowledge file.

4. **`knowledge/architecture/domain-boundary-gotchas.yaml`** — Added `architect-feeds-testing-risk-areas` entry (Layer 0 as architectural function). Promoted from architecture.md entry #1.

5. **`knowledge/architecture/knowledge-management-methodology.yaml`** — Added `two_tier_architecture` section documenting the cross-project vs project-specific knowledge split. Promoted from architecture.md entry #2.

6. **`process/collaboration_model.md`** — Added "Code assertion without verification" to CC Anti-Patterns section. Promoted from coding.md entry #5 (orchestrator behavioral rule, not domain knowledge).

7. **`knowledge/agent-context-map.yaml`** — Wired new knowledge files: `code-quality-principles.yaml` to code-reviewer, backend-developer, frontend-developer; `accessibility-testability-principles.yaml` to ui-ux-designer, frontend-developer, accessibility-auditor.

8. **All 9 discipline parking lot files** — Applied triage markers (`[READY TO PROMOTE]`, `[NEEDS VALIDATION]`, `[DEFERRED]`) to all 27 entries. Promoted entries marked with `Promoted → [target file]`.

9. **`disciplines/process-improvement.md`** — Updated maturity tracker from stale "all Level 1" to current actual levels with evidence column. Six disciplines at Level 2, two at Level 1.

10. **`knowledge/README.md`** — Updated structure listing to include new `coding/` directory and `design/accessibility-testability-principles.yaml`.

11. **`knowledge/design/README.md`** — Updated structure listing to include new file.

12. **`skeleton/manifest.json`** — Added `ops/sdlc/knowledge/coding` directory and 3 new source files (`coding/README.md`, `coding/code-quality-principles.yaml`, `design/accessibility-testability-principles.yaml`).

**Rationale:** Discipline parking lots accumulate raw insights, but without triage they're just growing lists. This first triage pass establishes the baseline: what's validated and promotable vs. what needs more real-world use. The coding discipline crossing the threshold to its own knowledge store is significant — it's the sixth discipline to reach Level 2 (Managed). The a11y-testability split across design and testing knowledge stores demonstrates the cross-discipline knowledge flow working as designed.

---

## 2026-03-22: Extract Manager Rule, Review-Fix Loop, and Finding Classification to Process Docs

**Origin:** Duplication audit across skills identified ~1,500 lines of near-identical content copy-pasted across 8 skills with no canonical definition.

**What happened:** Three core behavioral patterns were duplicated across multiple skills with minor variations — including a consistency bug where finding classification used 5 categories in sdlc-execute but only 4 in other skills, and only 3 in planning skills. The duplication meant changes to these patterns required updating 4-8 files, and drift between copies was inevitable.

**Changes made:**

1. **`process/manager-rule.md`** (new) — Single source of truth for the Manager Rule. Covers: the rule itself, no-size exception, no-complexity exception, failed agent dispatch, scope exceptions, what the manager CAN edit, session scope, and the pre-agent exception for sdlc-initialize. Referenced by 8 skills.

2. **`process/review-fix-loop.md`** (new) — Canonical definition of the review-fix loop (Steps A-D). Covers: dispatch all agents, collect findings, triage + fix, re-review, 3-strike rule, and skill-specific variations table. Referenced by sdlc-execute, sdlc-lite-execute, and review-fix.

3. **`process/finding-classification.md`** (new) — Unified finding classification taxonomy. Defines all 5 categories (FIX, PLAN, INVESTIGATE, DECIDE, PRE-EXISTING) with a table showing which subset each skill context uses. Resolves the consistency bug where different skills had different category counts. Also covers: misclassification guard, PRE-EXISTING qualification rules, severity levels, and FIX failure escalation.

4. **Skills updated to reference process docs:**
   - Manager Rule: sdlc-execute, sdlc-lite-execute, sdlc-plan, sdlc-lite-plan, review-fix (replaced ~100 lines each with 1-line reference)
   - Review-Fix Loop: sdlc-execute, sdlc-lite-execute, review-fix (replaced ~200 lines each with 3-line reference)
   - Finding Classification: sdlc-plan, sdlc-lite-plan (replaced ~30 lines each with 3-line reference)
   - Session Handoff: sdlc-execute, sdlc-lite-execute, sdlc-plan, sdlc-lite-plan (replaced ~8 lines each with 1-line reference to manager-rule.md Session Scope)

5. **`skeleton/manifest.json`** — Added all 3 new process files to source_files.

**Rationale:** Single source of truth prevents drift. The finding classification bug (4 vs 5 categories) was a direct consequence of copy-paste — each skill independently evolved its classification set. Centralizing means one file to update when the process changes, and skills inherit the update automatically.

---

## 2026-03-22: Formalize Discipline Capture Pipeline and Remove improvement-ideas

**Origin:** CD review of the SDLC's discipline/improvement-ideas/knowledge architecture. Identified that disciplines were only being written to during compliance audits — defeating their purpose as a real-time capture mechanism. Also identified that `improvement-ideas/` was an unnecessary staging area that added overhead without adding value.

**What happened:** The intended pipeline was: discipline parking lot → improvement-ideas/ → knowledge/skill/process change. In practice, the middle step (improvement-ideas/) was never used — the directory was always empty. Meanwhile, the planning and execution skills had no discipline capture step, so parking lots only got written during audits (post-mortems) rather than during active work (real-time capture).

**Changes made:**

1. **`improvement-ideas/` removed as a concept** — deleted directory, removed from `skeleton/manifest.json`, `setup.sh`, `setup.ps1`, `README.md`, `sdlc-initialize`, and `sdlc-compliance-auditor`. The promotion pipeline is now: discipline parking lot → `[READY TO PROMOTE]` marker → CD approves → knowledge YAML or skill/process change.

2. **Inline triage markers added to discipline parking lots** — `disciplines/README.md` updated with `[READY TO PROMOTE]`, `[NEEDS VALIDATION]`, `[DEFERRED]` convention. Replaces the separate improvement-ideas folder with inline status tracking.

3. **Discipline capture steps added to 6 skills:**
   - `sdlc-execute` (step 3a, post-execution before commit)
   - `sdlc-lite-execute` (step 3a, post-execution before commit)
   - `sdlc-plan` (step 5a, after agent review before plan mode)
   - `sdlc-lite-plan` (step 3a, after agent review before save)
   - `sdlc-idea` (in Crystallize step, after exploration)
   - `design-consult` (in Finalize step, after design direction chosen)
   All capture steps are lightweight (<2 min), optional (skip if nothing surfaced), and use a consistent format: `- **[date] [context]**: [insight]. [triage marker]`

4. **Compliance auditor strengthened (§6a, §6c):**
   - §6a now checks discipline write dates *between* audits and flags if parking lots are only written during audits
   - §6c replaced: was improvement-ideas triage, now discipline triage status — scans for `[READY TO PROMOTE]` items and surfaces them to CD
   - Severity levels updated: "improvement ideas accumulating" → "[READY TO PROMOTE] items pending CD approval"
   - Knowledge layer description updated from 3-tier to 2-tier architecture

5. **`process/discipline_capture.md`** (new) — Single reference file defining the discipline capture protocol (what to look for, how to capture, triage markers, rules). All 6 skills point here with a one-liner instead of duplicating the protocol. Added to `skeleton/manifest.json`.

6. **Related docs updated:** `knowledge/README.md` (promotion flow), `disciplines/process-improvement.md` (disciplines→skills progression), `README.md` (knowledge layer section — 3-tier → 2-tier)

**Rationale:** Discipline parking lots are only valuable if they capture insights in real-time during active work — not as audit after-the-fact observations. By baking capture prompts into the skills that produce insights (execution, planning, exploration, design), the parking lots become a living knowledge feed. Removing improvement-ideas/ simplifies the pipeline from three stages to two while losing nothing — the triage markers serve the same purpose with less overhead.

---

## 2026-03-22: sdlc-idea Skill Refinements from Paire-Appetit Usage Review

**Origin:** Review of the sous-improvement-planning session in paire-appetit, which produced two idea briefs (Sous Autonomous Marketing Intelligence, Sous Unified Search Router) using the sdlc-idea skill.

**What happened:** Both briefs were high-quality exploration artifacts that correctly stayed at conceptual altitude and produced appropriate next-step recommendations. However, three gaps were identified: (1) the Seed field in both briefs contained refined restatements rather than the user's verbatim words; (2) the Sketches step was skipped in both briefs without explicit guidance that this is allowed; (3) codebase grounding discoveries were not captured in the brief — the Search Router brief mentioned one file path in passing, but neither brief had a dedicated section for what was found during grounding.

**Changes made:**

1. **`skills/sdlc-idea/SKILL.md`** Step 5 (Sketch Conceptual Approaches) — Added clarification that this step is expected but not mandatory. If exploration converges quickly on a single obvious direction (e.g., codebase architecture makes one approach clearly natural), skipping to Crystallize with a single Direction is fine. But when multiple viable approaches exist and the user hasn't chosen, sketches should be presented.
2. **`skills/sdlc-idea/SKILL.md`** Brief template, Seed field — Changed from "[original idea as stated by the user]" to "[original idea — use the user's actual words, not a cleaned-up restatement]" to make the verbatim expectation explicit.
3. **`skills/sdlc-idea/SKILL.md`** Brief template — Added new `### Codebase Context` section between Open Questions and Feasibility Notes. Captures key files, modules, and patterns discovered during grounding, making briefs more useful for the next session that picks them up.

**Rationale:** The brief is a record of exploration, not a polished proposal. The raw seed preserves the user's original framing (which may differ from the refined direction). Codebase context makes the brief self-contained — a future session can understand what was discovered without re-doing the grounding. Clarifying sketch optionality prevents false-negative quality assessments when convergence is genuinely fast.

---

## 2026-03-21: Post-Neuroloom Audit — Installation Completeness Fixes

**Origin:** Compliance audit of the neuroloom-execution-bootstrap (paire-appetit), the first greenfield project setup using cc-sdlc.

**What happened:** The audit revealed three categories of gaps: (1) `skeleton/manifest.json` was missing files that existed on disk (`AGENT_SUGGESTIONS.md`, `domain-boundary-gotchas.yaml`, `sdlc_lite_plan_template.md`, `MIGRATE.md`, entire `plugins/` section, `improvement-ideas/`), making completeness validation impossible; (2) `setup.sh` wasn't creating `improvement-ideas/`, `docs/current_work/audits/`, and lacked the `improvement-ideas/` directory on disk; (3) `sdlc-initialize` Phase 1c had a 4-line skeleton check that missed upstream READMEs, scaffold directories, and agent reference files; Phase 4 had no spec-vs-roster reconciliation step (spec-listed agents were silently dropped); Phase 10 verification didn't check for agent creation method, unmapped knowledge files, or scaffold completeness.

**Changes made:**

1. **`skeleton/manifest.json`** — Added 8 missing files to source_files: `MIGRATE.md` (top_level), `sdlc_lite_plan_template.md` (templates), `domain-boundary-gotchas.yaml` (knowledge), `AGENT_SUGGESTIONS.md` (agents). Added three new source_files sections: `plugins` (4 files), `optional_plugins` (1 file), `improvement_ideas` (1 file). Manifest now serves as the single source of truth for installation completeness validation.
2. **`setup.sh`** — Creates `improvement-ideas/` with `.gitkeep` even when the source directory is empty. Creates `docs/current_work/audits/` directory for audit output.
3. **`skills/sdlc-initialize/SKILL.md`** Phase 1c — Expanded skeleton check from 4 lines to a comprehensive checklist: validates against `manifest.json` source_files, checks all upstream READMEs, scaffold directories (`improvement-ideas/`, `playbooks/`, `plugins/`, `examples/`, `audits/`), agent reference files (`AGENT_TEMPLATE.md`, `AGENT_SUGGESTIONS.md`), and `MIGRATE.md`. Blocks Phase 2 if files are missing.
4. **`skills/sdlc-initialize/SKILL.md`** Phase 4d (new) — Added spec-vs-roster reconciliation step between agent creation and context map wiring. Compares created agents against spec-listed roles, surfaces deviations, and requires CD acknowledgment before proceeding.
5. **`skills/sdlc-initialize/SKILL.md`** Phase 10 — Expanded verification from 10 items to 16, organized into three groups (Skeleton & Infrastructure, Agents, Knowledge & Disciplines). Added: upstream README verification, scaffold directory check, agent creation method confirmation, spec-vs-roster reconciliation, agent reference file presence, unmapped knowledge file check.
6. **`improvement-ideas/`** (new) — Created directory with `.gitkeep` in cc-sdlc source.

**Rationale:** The manifest is the contract between `setup.sh` (what gets installed) and `sdlc-initialize` (what gets verified). When the manifest drifts from reality, both tools silently produce incomplete installations. Making the manifest exhaustive and using it as the verification source in Phase 1c closes the loop. The spec-vs-roster reconciliation prevents the specific failure mode from neuroloom where agents listed in the spec were never created and the deviation was never logged.

---

## 2026-03-21: New sdlc-initialize Skill + Initialization Playbook

**Origin:** Analysis of the neuroloom-spec-planning session (paire-appetit D4) — the first time cc-sdlc bootstrapped an entirely new repository from scratch.

**What happened:** BOOTSTRAP.md optimizes for retrofitting existing projects (discovery, categorization, document migration). The neuroloom session revealed a different workflow for greenfield projects: spec first, then scaffold, then agents/knowledge/disciplines. The ordering matters — agents and knowledge stores can't be meaningfully seeded without knowing the project's tech stack, domain, and architecture. A follow-up review identified a deeper issue: greenfield projects have no agents, so Phase 0 can't route to `sdlc-plan` or `sdlc-idea` (both dispatch agents that don't exist). Ideation and spec drafting must be an inline CD↔CC conversation until agents are created.

**Changes made:**

1. **`skills/sdlc-initialize/SKILL.md`** (new) — Executable skill that orchestrates full SDLC initialization. Auto-detects greenfield (fresh/resume), retrofit, repair, and already-initialized modes. Greenfield Phase 0 is an inline ideation and spec-drafting conversation between CD and CC — no agent dispatch (agents don't exist yet). Introduces a "Pre-Agent Reality" section: CC does domain work directly in Phases 0–3 (the sole exception to the Manager Rule), and the Manager Rule activates at Phase 4 when agents are created. Phase 0 includes Socratic questioning (one question at a time via AskUserQuestion), grounding in repo state, approach sketching, and spec drafting using the spec template. Resume detection allows re-invocation to pick up where it left off (spec exists → skip to Phase 1; skeleton exists → skip to Phase 4). Post-agent phases (6–8) dispatch agents for knowledge, disciplines, and testing gotchas. Retrofit mode follows BOOTSTRAP.md. Includes red flags table with 13 entries.
2. **`skeleton/manifest.json`** — Added `skills/sdlc-initialize/SKILL.md` to source files list.
3. **`CLAUDE-SDLC.md`** — Added "Initialize SDLC in this project" and "Migrate my SDLC framework" to SDLC Commands table.
4. **`process/overview.md`** — Added "Project Initialization" section before "Work Without Plans" with mode table and trigger.
5. **`setup.sh`** / **`setup.ps1`** — Simplified post-install message to a single step: "Initialize SDLC in this project." Removed `initial-prompt.md` from install list.
6. **`initial-prompt.md`** (removed) — All content absorbed into `sdlc-initialize` skill, CLAUDE-SDLC.md commands table, and setup script output. Migration prompt added to CLAUDE-SDLC.md before removal.

**Rationale:** The initialization workflow was previously split across `setup.sh` (automated skeleton), BOOTSTRAP.md (retrofit instructions for CC to follow), and tribal knowledge (greenfield ordering, knowledge seeding, discipline initialization). The neuroloom session revealed that greenfield initialization has a fundamentally different ordering requirement — spec before scaffold — and that the post-scaffold phases (agents, knowledge, disciplines, testing gotchas) were undocumented as an executable workflow. The critical insight from the follow-up: in greenfield, there are no agents to dispatch, so the entire SDLC skill suite (which assumes agents exist) is inaccessible until agents are created. Phase 0 must be a direct CD↔CC conversation — the only point in the SDLC where CC does domain work. The skill unifies both paths behind a single entry point with mode detection and resume support, making initialization a first-class SDLC operation.

---

## 2026-03-20: SDLC Compliance Audit — Six Process Improvements

**Origin:** SDLC compliance audit across multiple execution sessions identified gaps in session handoff, phase re-dispatch tracking, plan review clarity, stale knowledge files, missing domain-boundary guidance, and unverified code assertions.

**What happened:** An audit of execution sessions revealed six categories of process drift: (1) the Manager Rule was not explicitly enforced after commit/handoff, allowing post-skill direct implementation; (2) re-dispatches within the same phase lacked PRE-GATE documentation, creating untracked sub-phases; (3) the plan review step was ambiguous about whether the writing agent should review its own plan; (4) tui-patterns.yaml had stale responsive breakpoints from pre-D8 viewport work; (5) no knowledge file existed for recurring domain-boundary crossing patterns; (6) the orchestrator answered code-behavior questions without reading code during conversational interludes.

**Changes made:**

1. **`skills/sdlc-lite-execute/SKILL.md`** — Added Session Handoff section after Step 4: Manager Rule persists for the full session, single-file dispatches to domain agent, multi-file/cross-domain triggers re-planning. Added two Red Flag rows for post-commit and domain-crossing anti-patterns. Added re-dispatch PRE-GATE requirement in the Phase bleeding check section.
2. **`skills/sdlc-execute/SKILL.md`** — Same Session Handoff section (referencing `sdlc-plan`), same two Red Flag rows, same re-dispatch PRE-GATE requirement.
3. **`skills/sdlc-lite-plan/SKILL.md`** — Clarified writing-agent-in-review guidance in Step 3: writing agent may self-review but cross-domain reviewers provide higher marginal value; count-must-match applies to dispatched set.
4. **`knowledge/architecture/domain-boundary-gotchas.yaml`** (new) — Four gotcha patterns (TUI-triggers-server, frontend-triggers-API, feature-triggers-schema, conversational-drift-after-skill) with recognition signals for orchestrator self-checks.
5. **`disciplines/coding.md`** — Added "Code Assertion Without Verification" anti-pattern to the Parking Lot: orchestrator must read code before answering factual questions in all modes, not just structured phases.
6. **`mission-control: ops/sdlc/knowledge/design/tui-patterns.yaml`** — Updated responsive_breakpoints from 4-mode (too_narrow/vertical/collapsed/full) to 8-mode 2D width x height classification matching D8 viewport implementation. Updated last_updated to 2026-03-20.

**Rationale:** These changes close gaps that structured phases (PRE/POST-GATE) already prevent during execution but that reappear during session handoff, conversational interludes, and re-dispatches. The Session Handoff section makes the Manager Rule's persistence explicit. The re-dispatch PRE-GATE prevents untracked sub-phases. The domain-boundary knowledge file gives the orchestrator recognition signals before boundary crossings happen rather than after.

---

## 2026-03-20: Session Handoff for Planning Skills + Stale Diagnostic Dismissal Anti-Pattern

**Origin:** Process review identified that the Manager Rule's session persistence was enforced in execution skills but not in planning skills, and that build warnings were being dismissed as "stale" during POST-GATE checks.

**What happened:** Two gaps surfaced: (1) After sdlc-plan and sdlc-lite-plan enter plan mode, the session continues but had no explicit guidance preventing the orchestrator from implementing unrelated requests directly — the Session Handoff section existed in execution skills but not planning skills. (2) During POST-GATE checks, build warnings (unused variables, type errors, import issues) were being rationalized away as "stale LSP state" or "intermediate build artifacts" instead of being dispatched to agents for verification. These dismissed warnings reliably resurfaced as real findings in subsequent review rounds.

**Changes made:**

1. **`skills/sdlc-plan/SKILL.md`** — Added Session Handoff section after the plan mode step (Step 6). Manager Rule persists for the full session: single-file dispatches to domain agent, multi-file/cross-domain triggers appropriate planning skill, domain boundary crossings dispatch separate agents. Added two Red Flag rows for post-plan and domain-crossing anti-patterns.
2. **`skills/sdlc-lite-plan/SKILL.md`** — Added Session Handoff section after Step 5 (Enter Plan Mode) with same rules. Added one Red Flag row for post-plan direct implementation.
3. **`skills/sdlc-lite-execute/SKILL.md`** — Added "Stale diagnostic dismissal" anti-pattern bullet in POST-GATE section after build verification. Every warning is potentially real — dispatch the phase agent to verify rather than reasoning it away.
4. **`skills/sdlc-execute/SKILL.md`** — Same stale diagnostic dismissal bullet added to POST-GATE section.

**Rationale:** The Session Handoff gap in planning skills allowed a subtle violation: after the plan was produced, the orchestrator could treat unrelated requests as "outside the skill" and implement directly. Making the Manager Rule's persistence explicit in planning skills closes the same gap that was already closed in execution skills. The stale diagnostic dismissal rule prevents a specific rationalization pattern where the orchestrator uses "LSP lag" or "intermediate state" as justification for ignoring real build warnings — a pattern that wastes review rounds when the warnings turn out to be genuine.

---

## 2026-03-20: New Idea Exploration Skill

**Origin:** CD identified that the DISCOVERY-GATE in sdlc-plan is minimum-viable discovery gating spec writing — but there was no skill for open-ended, pre-commitment exploration of ideas that aren't ready to plan yet.

**What happened:** The discovery gate enforces "ask N questions before proceeding to spec." But many ideas need unbounded exploration — Socratic questioning, codebase grounding, conceptual sketching, and iterative refinement — before they're shaped enough to enter any planning track. This gap was filled by creating a standalone exploration skill.

**Changes made:**

1. **`skills/sdlc-idea/SKILL.md`** — New skill for open-ended idea exploration. Workflow: SEED → GROUND → QUESTION → RESEARCH → SKETCH → ITERATE → CRYSTALLIZE (optional). Produces an idea brief saved to `docs/current_work/ideas/`. Hands off to sdlc-plan, sdlc-lite-plan, or design-consult when the user is ready to commit.
2. **`skeleton/manifest.json`** — Added `skills/sdlc-idea/SKILL.md` to source files, added `docs/current_work/ideas/` directory and `.gitkeep` seed file.
3. **`CLAUDE-SDLC.md`** — Added Idea Exploration as a tier in the Three Tiers table. Updated workflow diagram to show optional `sdlc-idea` step. Added "Choosing a tier" guidance for vague ideas. Added workflow rule for when to invoke `sdlc-idea`.
4. **`process/overview.md`** — Updated flow diagram to include optional Explore step. Updated "Idea" phase description to reference `sdlc-idea`. Added Idea Exploration tier to the Work Without Plans table.
5. **`skills/design-consult/SKILL.md`** — Added cross-reference to `sdlc-idea` in Integration section — the two skills complement each other (conceptual vs. visual exploration).

**Rationale:** The existing DISCOVERY-GATE is a speed bump before spec writing — it ensures minimum discovery happened. But exploration and discovery are different activities. Exploration has no gate, no minimum, no mandatory output. It's about helping the user think through what they actually want before entering any commitment track. This skill fills the gap between "I have a thought" and "I'm ready to plan."

---

## 2026-03-20: Changelog Must Be Immediate, Not Deferred

**Origin:** Same session as AskUserQuestion enforcement — CD had to explicitly ask for the changelog update after the process change was already complete.

**What happened:** After updating 5 SDLC files with the AskUserQuestion enforcement rules, the changelog was not written until CD asked "update the SDLC changelog." The process already said to update the changelog "in the same session," but that was loose enough to allow deferral to a separate step or even a follow-up prompt.

**Changes made:**

1. **`CLAUDE-SDLC.md`** — Changed "in the same session" to "immediately after the change, in the same step." Added: every process decision change must have a changelog entry written before moving on to other work.
2. **`process/overview.md`** — Added timing rule: changelog entry must be written in the same step as the process change. Added: "If CD has to ask for the changelog update, it was already too late."

**Rationale:** "Same session" is too loose — it allows the changelog to be forgotten or deferred until the user notices. Making it "same step" ties the changelog to the action itself, not the session boundary.

---

## 2026-03-20: AskUserQuestion Enforcement for All User-Directed Questions

**Origin:** D8 planning session — CD noticed a product decision (quarter-panel layout interaction model) was typed as conversational text instead of using `AskUserQuestion`, making it easy to miss.

**What happened:** During D8 plan review, T1/C1 (quarter-panel layout) was a product decision with multiple alternatives but got classified as FIX. The planner then typed the question as conversational text instead of invoking `AskUserQuestion`. Root cause was twofold: (1) the FIX classification was too loose — it didn't require "clear resolution without user input", so product decisions slipped through; (2) no global rule mandated `AskUserQuestion` for all questions, only for DECIDE-classified findings.

**Changes made:**

1. **`process/collaboration_model.md`** — Added "Tool Rule: AskUserQuestion for All Questions" section at the top of Communication Patterns. Every question directed at the user must use `AskUserQuestion`; only status updates and completion reports use normal text. Updated examples to show `(via AskUserQuestion)` annotation.
2. **`skills/sdlc-lite-plan/SKILL.md`** — Tightened FIX to require "correct resolution is clear without user input". Broadened DECIDE to include "any finding where the resolution requires choosing between alternatives". Added misclassification guard: if you're about to type a question about a FIX finding, STOP and reclassify as DECIDE.
3. **`skills/sdlc-plan/SKILL.md`** — Same FIX/DECIDE tightening and misclassification guard.
4. **`skills/sdlc-execute/SKILL.md`** — Same FIX/DECIDE tightening and misclassification guard.
5. **`skills/sdlc-lite-execute/SKILL.md`** — Same FIX/DECIDE tightening and misclassification guard.

**Rationale:** The DECIDE → `AskUserQuestion` instruction was already present in all four skills but was easy to bypass through misclassification. The FIX/DECIDE boundary was ambiguous enough that product decisions could be classified as FIX, then asked conversationally. The misclassification guard is a self-check that catches the specific failure mode: "I classified this as FIX but I'm about to ask the user a question about it." The global rule in the collaboration model closes the broader gap — questions should never be conversational text regardless of which skill is running.

---

## 2026-03-17: Three-Tier Model, Testing Paradigm, and Plugin Overhaul

**Origin:** CD-driven session — frustration with rigid ad-hoc/SDLC binary, Claude's assumption-making on library APIs, and missing guidance on code structure for testability.

**What happened:** Five structural changes to the framework in a single session:

1. **Context7 became the only required plugin.** Claude's training data goes stale on library APIs. Context7 MCP provides live documentation lookups. Wired into all 7 agent-dispatching skills with verification instructions. oberskills demoted to optional (consistent with the oberagent removal in 5dcc5c4).

2. **Ad-hoc track renamed to SDLC-Lite.** "Ad hoc" now means untracked work generically. SDLC-Lite is the middle tier — registers a deliverable ID (tier: lite), produces a plan, no spec or result doc. Trigger changed from file count (3-6 files) to complexity — a 2-file cross-domain change warrants a plan, a 10-file rename might not.

3. **Three-tier model formalized.** Full SDLC → SDLC-Lite → Direct Dispatch. Direct Dispatch is the new third tier for when CD steers in real-time. Keeps agent-first rule and review-before-commit, but drops plan files and approval gates. Includes escalation triggers for when to upgrade to a plan.

4. **WHAT/WHY rule relaxed.** Plans now default to WHAT/WHY but planning agents may include implementation guidance (approach hints, key functions, file relationships) at their discretion. Removed the strict HOW compliance verification gate. Execution skills now pass full plan context to agents — no summarizing or omitting.

5. **Testing paradigm codified.** New knowledge file (`testing-paradigm.yaml`) based on grug-brain philosophy: separate I/O from logic (functional core/imperative shell), test type selection by code layer, mocking is a code smell, regression-first for bug fixes. Wired into create-test-suite, test-loop, and sdlc-plan.

**Changes made:**

1. **`plugins/context7-setup.md`** (new) — Setup guide for Context7 MCP with installation options
2. **`plugins/lsp-setup.md`** (new) — Setup guide for all 12 language-specific LSP plugins
3. **`plugins/README.md`** — Three-tier plugin hierarchy: Required (context7), Highly Recommended (LSP), Optional (oberskills)
4. **`knowledge/testing/testing-paradigm.yaml`** (new) — Functional core/imperative shell, test type selection, mocking stance, regression-first rule
5. **`CLAUDE-SDLC.md`** — Three-tier model, Direct Dispatch rules, Verification Policy (zero-assumption rule), LSP in Code Verification Rule, updated recommended settings
6. **`skills/sdlc-plan/SKILL.md`** — WHAT/WHY relaxation, Context7 verification, testing strategy references paradigm
7. **`skills/sdlc-lite-plan/SKILL.md`** — Same WHAT/WHY relaxation, complexity-based trigger
8. **`skills/sdlc-execute/SKILL.md`** — Full plan context passthrough in dispatch prompts
9. **`skills/sdlc-lite-execute/SKILL.md`** — Same context passthrough
10. **`skills/create-test-suite/SKILL.md`** — SDET dispatch references testing paradigm
11. **`skills/test-loop/SKILL.md`** — "Needs a mock" classified as code structure issue
12. **All 7 agent-dispatching skills** — Context7 verification instructions added
13. **`disciplines/coding.md`** — Promoted to active, testability architecture section
14. **`disciplines/testing.md`** — Testing paradigm summary with test type selection table
15. **`knowledge/agent-context-map.yaml`** — Testing paradigm mapped to sdet and code-reviewer
16. **Skill renames** — ad-hoc-planning → sdlc-lite-plan, ad-hoc-execution → sdlc-lite-execute, sdlc-planning → sdlc-plan, sdlc-execution → sdlc-execute, sdlc-new merged into sdlc-plan Step 0, ad-hoc-review → review-diff

**Rationale:** The old binary (SDLC vs ad hoc) didn't match how work actually happens. Most real sessions are CD-driven iteration with agents — not plan-driven execution. The three-tier model gives that pattern a name and rules. The WHAT/WHY relaxation stops throwing away useful planning context. Context7 and the testing paradigm address the two biggest quality gaps: stale API knowledge and untestable code structure.

---

## 2026-03-16: Post-Audit Process Improvements

**Origin:** Independent SDLC compliance audit of mission-control planning and execution sessions (02257258, db1105a9)

**What happened:** Two audit sessions (external + sdlc-compliance-auditor) identified structural gaps in the execution skill and result template that caused preventable issues during the mission-control D1 execution: a 40K-line monolithic commit instead of per-phase commits, a result document that shipped without verifying success criteria, and an auditor agent that couldn't write its own output artifacts.

**Changes made:**

1. **`agents/sdlc-compliance-auditor.md`** — Added Write and Edit tools. The auditor's contract requires producing artifacts at `docs/current_work/audits/` but it lacked the Write tool to do so autonomously.
2. **`skills/sdlc-execute/SKILL.md`** — Added Step 3a (Per-Phase Commits) between the review loop and final commit. Each phase's work must be committed after its POST-GATE clears, producing one commit per phase instead of one monolithic commit at the end.
3. **`templates/result_template.md`** — Added Success Criteria Verification table. Maps each SC from the spec to Pass/Partial/Deferred with evidence, making it impossible to ship a result document without closing the loop on the spec's stated success bar.

**Rationale:** These three changes fix the tooling rather than relying on the agent to remember rules. Per-phase commits are self-enforcing through the skill's step ordering. The SC verification table is self-enforcing through the template structure. The auditor's Write tool is a capability fix. All three reduce the likelihood of the same gaps recurring in future executions.
