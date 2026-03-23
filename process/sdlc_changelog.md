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

1. **`agents/sdlc-compliance-auditor.md` §6a** — Added "Maturity level verification" sub-section: auditor reads the formal level definitions in `process-improvement.md`, checks each discipline's claimed level against evidence criteria (Level 1: parking lot exists; Level 2: knowledge store + agent wiring + triage pass; Level 3: used on 2+ projects), flags unsupported claims and potential regressions.

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

2. **`disciplines/README.md`** — Added "Creating a New Discipline" section with: when to create (3 conditions: recurring capability, no existing home, distinct agent role), minimum viable discipline (4 items: discipline file, tracker entry, manifest entry, hump chart row), full lifecycle flowchart (from observation to Level 3 and optional skill), and 3 anti-patterns to avoid (premature creation, unnecessary ownership, high-intensity hump chart).

3. **`knowledge/README.md`** — Replaced 3-line "Adding a New Discipline" with "Adding a Knowledge Store for a Discipline" — 8-step procedure that references the canonical lifecycle in `disciplines/README.md`. Clarifies that a knowledge store is a Level 2 artifact, not a Level 1 starting point.

**Rationale:** The discipline system had a chicken-and-egg gap: disciplines existed but there was no documented way to create one or assess its maturity. Without a creation lifecycle, new disciplines would either be created too eagerly (speculative process overhead) or never created at all (insights forced into ill-fitting existing disciplines). Without an assessment procedure, the maturity tracker is a snapshot that drifts from reality. Both additions close loops that the triage pass revealed were open.

---

## 2026-03-22: Formalize Process Maturity Level Definitions

**Origin:** During the discipline triage session, the maturity tracker in `process-improvement.md` used Level 1/2/3 labels but the level definitions were only sketched in a `[DEFERRED]` parking lot entry. The compliance auditor checks "Is the CMMI maturity tracker current?" but has no formal criteria for what each level means.

**What happened:** The tracker was updated during the triage pass (six disciplines upgraded from Level 1 to Level 2 based on actual knowledge store evidence), but the level definitions themselves were implicit. "Level 2 (Managed)" meant whatever the reader assumed it meant. This made tracker updates subjective and auditor checks unverifiable.

**Changes made:**

1. **`disciplines/process-improvement.md`** — Added "Process Maturity Levels" section with formal definitions for Levels 1-5. Each level includes: description of what it looks like, evidence required to claim the level, and transition trigger to the next level. Also includes 5 progression rules (per-discipline assessment, evidence-based, regression possible, not all disciplines need Level 5, auditor verifies claims).

2. **`disciplines/process-improvement.md`** — CMMI parking lot entry changed from `[DEFERRED]` to `Promoted →` since the formal definitions now supersede the sketch. Status updated from "Parking lot" to "Active".

**Rationale:** Maturity levels without definitions are aspirational labels, not assessment criteria. Formalizing what "Level 2" means (knowledge store + agent wiring + triage pass) makes the tracker verifiable: the compliance auditor can check evidence against criteria rather than asking "does this feel like Level 2?" The definitions are calibrated to this framework's "toolbox not recipe" principle — Level 2 doesn't mean "always invoked", it means "documented and repeatable when invoked."

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

2. **`process/review-fix-loop.md`** (new) — Canonical definition of the review-fix loop (Steps A-D). Covers: dispatch all agents, collect findings, triage + fix, re-review, 3-strike rule, and skill-specific variations table. Referenced by sdlc-execute, sdlc-lite-execute, and commit-fix.

3. **`process/finding-classification.md`** (new) — Unified finding classification taxonomy. Defines all 5 categories (FIX, PLAN, INVESTIGATE, DECIDE, PRE-EXISTING) with a table showing which subset each skill context uses. Resolves the consistency bug where different skills had different category counts. Also covers: misclassification guard, PRE-EXISTING qualification rules, severity levels, and FIX failure escalation.

4. **Skills updated to reference process docs:**
   - Manager Rule: sdlc-execute, sdlc-lite-execute, sdlc-plan, sdlc-lite-plan, commit-fix (replaced ~100 lines each with 1-line reference)
   - Review-Fix Loop: sdlc-execute, sdlc-lite-execute, commit-fix (replaced ~200 lines each with 3-line reference)
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
3. **`plugins/README.md`** — Three-tier plugin hierarchy: Required (context7), Highly Recommended (LSP), Optional (oberskills, design-for-ai)
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
16. **Skill renames** — ad-hoc-planning → sdlc-lite-plan, ad-hoc-execution → sdlc-lite-execute, sdlc-planning → sdlc-plan, sdlc-execution → sdlc-execute, sdlc-new merged into sdlc-plan Step 0, ad-hoc-review → diff-review

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
