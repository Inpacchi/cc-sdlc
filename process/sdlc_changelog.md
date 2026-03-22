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
