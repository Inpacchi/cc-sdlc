---
name: sdlc-execute
description: >
  Execute an approved implementation plan. The plan must already exist at
  docs/current_work/planning/dNN_name_plan.md — written and reviewed by worker domain agents via
  sdlc-plan. Loads the plan, executes phases using worker domain agents, reviews all completed work
  with worker domain agents, fixes all findings, and commits.
  Triggers on "execute the plan", "implement the plan", or references to an existing plan file.
  Do NOT use without a plan — if no plan exists, use sdlc-plan first.
  Do NOT use for lite deliverables — those use sdlc-lite-execute.
  Do NOT use for auditing completed work against a plan — use CHECKER mode (this skill supports both).
---

# SDLC Execution

## Overview

This skill executes an approved plan that was produced by `sdlc-plan`. Worker domain agents implement the phases, review the result, and fix findings. You are the manager — you dispatch worker agents, track phase completion, and ensure reviews pass before the task is done.

**Precondition:** A reviewed and approved plan must exist before this skill runs. If no plan exists, stop and use `sdlc-plan` first.

## Mode Selection

| User Intent | Mode | Entry Point |
|-------------|------|-------------|
| "Execute the plan", "implement the plan" | **APPLIER** | Step 0 (full execution workflow) |
| "Audit implementation", "review against plan", "check completed work" | **CHECKER** | Audit Workflow below |
| Unclear | Ask: "Are you executing new work, or auditing completed work?" | — |

### CHECKER Mode: Audit Completed Work Against Plan

When auditing already-implemented work (not executing new work):

1. Load the plan from `docs/current_work/planning/dNN_name_plan.md`
2. Scan changed files (git diff or file list from result doc)
3. Dispatch ALL relevant worker domain agents to audit:
   - Completeness: did all plan phases get implemented?
   - Correctness: does the implementation match the plan's intent?
   - Deviation: are there changes NOT in the plan? Are they justified?
4. Present structured findings to CD
5. If fixes needed: dispatch agents to fix, re-audit

**CHECKER mode ends after step 5. APPLIER mode below governs all execution work.**

## Step 0: Load the Plan

Load the plan from `docs/current_work/planning/dNN_name_plan.md` — this plan has been reviewed and approved.

**Read the plan file only.** Do not pre-read implementation files, existing components, or codebase patterns before dispatch. The plan file is sufficient context for the manager. Worker domain agents read the files relevant to their own phases when they execute. Pre-reading implementation files and accumulating context is not management — it is the first step toward self-implementation.

Extract:
1. **Phases and their dependencies** — what runs in parallel vs. what sequences
2. **Agent assignments** — which worker domain agent owns each phase/task
3. **Relevant worker domain agents** — the full list for post-execution review

If the plan file doesn't exist or can't be found, **stop immediately** and tell the user:

> No approved plan found. Run `sdlc-plan` first to create and review the plan.

Do NOT write a plan yourself. Do NOT proceed without one.

## The Process

```dot
digraph execution {
    rankdir=TB;

    "0. Load approved plan" [shape=box];
    "Plan exists?" [shape=diamond];
    "STOP — run planning skill first" [shape=doublecircle, color=red];

    subgraph cluster_phase_loop {
        label="1. Per-Phase Loop (repeat for each phase/wave)";
        style=dashed;

        "1a. PRE-GATE\n- Pattern Reuse Gate\n- Phase triage: BUILD / SKIP / REVISE_PLAN\n- Verify dependencies complete" [shape=box, style=bold, color=blue];
        "1b. DISPATCH worker domain agent(s)\nper plan assignment\n(you do NOT implement)" [shape=box];
        "1c. POST-GATE\n- [build command]\n- Files match plan?\n- Flag deviations to CD" [shape=box, style=bold, color=blue];
    }

    "All phases complete?" [shape=diamond];
    "2a. Output checklist of ALL agents\nDispatch ALL of them" [shape=box];
    "2b. Collect findings table\nfrom ALL agents" [shape=box];
    "Any findings?" [shape=diamond];
    "2c. Triage + Fix all findings\n(finding agent fixes it)" [shape=box];
    "2d. Return to 2a\n(re-review ALL agents)" [shape=box, style=bold];
    "3. Write Worker Agent Reviews\n-> results doc" [shape=box];
    "4. Verify + commit" [shape=box];
    "Task complete" [shape=doublecircle];

    "0. Load approved plan" -> "Plan exists?";
    "Plan exists?" -> "STOP — run planning skill first" [label="no"];
    "Plan exists?" -> "1a. PRE-GATE\n- Pattern Reuse Gate\n- Phase triage: BUILD / SKIP / REVISE_PLAN\n- Verify dependencies complete" [label="yes"];
    "1a. PRE-GATE\n- Pattern Reuse Gate\n- Phase triage: BUILD / SKIP / REVISE_PLAN\n- Verify dependencies complete" -> "1b. DISPATCH worker domain agent(s)\nper plan assignment\n(you do NOT implement)";
    "1b. DISPATCH worker domain agent(s)\nper plan assignment\n(you do NOT implement)" -> "1c. POST-GATE\n- [build command]\n- Files match plan?\n- Flag deviations to CD";
    "1c. POST-GATE\n- [build command]\n- Files match plan?\n- Flag deviations to CD" -> "All phases complete?";
    "All phases complete?" -> "1a. PRE-GATE\n- Pattern Reuse Gate\n- Phase triage: BUILD / SKIP / REVISE_PLAN\n- Verify dependencies complete" [label="no — next phase/wave"];
    "All phases complete?" -> "REVIEW-GATE\n(mandatory — no pause)" [label="yes"];
    "REVIEW-GATE\n(mandatory — no pause)" [shape=box, style=bold, color=red];
    "REVIEW-GATE\n(mandatory — no pause)" -> "2a. Output checklist of ALL agents\nDispatch ALL of them";
    "2a. Output checklist of ALL agents\nDispatch ALL of them" -> "2b. Collect findings table\nfrom ALL agents";
    "2b. Collect findings table\nfrom ALL agents" -> "Any findings?";
    "Any findings?" -> "2c. Triage + Fix all findings\n(finding agent fixes it)" [label="yes"];
    "2c. Triage + Fix all findings\n(finding agent fixes it)" -> "2d. Return to 2a\n(re-review ALL agents)";
    "2d. Return to 2a\n(re-review ALL agents)" -> "2a. Output checklist of ALL agents\nDispatch ALL of them";
    "Any findings?" -> "3. Write Worker Agent Reviews\n-> results doc" [label="no — ALL agents clean"];
    "3. Write Worker Agent Reviews\n-> results doc" -> "4. Verify + commit";
    "4. Verify + commit" -> "Task complete";
}
```

## Collaboration Model

Read `ops/sdlc/process/collaboration_model.md` for the CD/CC role definitions, communication patterns (AskUserQuestion rule), decision authority table, and anti-patterns. All questions to the user must use `AskUserQuestion`. All anti-patterns in that doc apply during execution.

## Deliverable Lifecycle

Follow the state machine in `ops/sdlc/process/deliverable_lifecycle.md`. Update the `**Status:**` marker in the spec file as the deliverable transitions through states: In Progress (at phase start), Validated (after review loop passes), Deployed (after deployment verification, if applicable), Complete (after final commit). Use the defined status markers — do not invent custom states.

## Manager Rule

Read and follow `ops/sdlc/process/manager-rule.md` — the canonical definition of this rule. It applies unconditionally for the entire session.

## Phase Details

### 1. Execute Phases

Follow the plan's phase structure. For each phase:

**PRE-GATE** — you cannot dispatch the phase agent until this block appears in your response:

```
PRE-GATE Phase [N] — [phase name]
Pattern search: [what you searched for] → [found / not found / following pattern at path/to/file.ts] (use LSP goToImplementation/findReferences for interface implementations and call sites; Grep for text patterns)
Triage: BUILD | SKIP | REVISE_PLAN
If SKIP or REVISE_PLAN: [reason — stop and wait for CD confirmation before proceeding]
Dependencies: [phase N complete | none required]
Data sources: [ALL external sources from the plan for this phase — URLs, repos, APIs, documents | "codebase only"]
Expected counts: [any counts stated in the plan — "14 trigger prefixes", "11 counter types" | none]
Design Decisions: [list binding decisions from the plan that apply to this phase | none]
Agent: [agent-name]
```

For **BUILD**: proceed to dispatch. For **SKIP** or **REVISE_PLAN**: stop and wait for explicit CD confirmation before continuing. Document SKIPs in the result doc under 'Skipped Phases'. Do not self-modify the approved plan.

**File-Conflict Gate (parallel phases only):** Before dispatching two or more phases simultaneously, list every file each phase will modify. If any file appears in more than one phase, those phases MUST run sequentially — dispatch the first phase, wait for POST-GATE to pass, then dispatch the second. Do not rely on the plan's dependency table alone; verify file overlap yourself.

**Data Source Extraction (mandatory):** Read the plan's phase description and extract EVERY data source mentioned — external repos, APIs, URLs, documents, AND codebase files. List them all in the PRE-GATE block. If the plan says data comes from an external source, the dispatch prompt MUST tell the agent to fetch from that source. Omitting an external data source from the dispatch prompt causes agents to hallucinate values instead of reading from the defined source.

**EXECUTE**: Dispatch assigned agent(s) per plan. Never narrate readiness ("Ready to dispatch") and pause for confirmation; the plan is already approved. The dispatch prompt must include:
1. **The phase's full context from the plan** — outcome, constraints, acceptance criteria, AND any implementation guidance the planning agent included (approach hints, key functions, file relationships, migration notes, data flow context). The plan is the agent's primary briefing document — pass through everything relevant to this phase. Do not summarize or omit plan details; the executing agent benefits from the planning agent's full reasoning.
2. **All data sources** from the PRE-GATE extraction — external sources get explicit fetch instructions. For data extraction tasks, tell the agent to read ALL relevant pages from the source, extract ALL entries exhaustively, and cross-check the final count.
3. **Expected counts** from the plan — the agent can self-check its output
4. **Binding Design Decisions** that constrain this phase's implementation
5. **Prior phase artifacts** — when this phase depends on a completed phase that produced data artifacts (seed scripts, config files, type definitions), the dispatch prompt must tell the agent to read those files as the canonical reference. Agents that produce coupled artifacts will fabricate their own values if not told where the canonical data lives.
6. **Library verification instructions** — when the phase involves external library/framework APIs, tell the agent to verify API usage via Context7 (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`) before writing integration code. Include the library names and versions from the project's dependency files. Agents must not rely on training data for API signatures, parameter names, or default behaviors.
Dispatch independent phases in parallel using multiple Agent tool calls in a single message. If you find yourself editing files directly instead of dispatching an agent, stop — that violates the Manager Rule.

**Cross-domain knowledge injection:** When a phase requires an agent to work in a context outside its primary domain, consult `ops/sdlc/knowledge/agent-context-map.yaml` for the other domain's agent and include those knowledge files in the dispatch prompt. Use judgment — only inject when the agent is genuinely crossing into unfamiliar territory (e.g., a backend agent implementing a feature that depends on real-time patterns, a frontend agent touching data layer code). Do not inject for routine single-domain work.

**POST-GATE** — a phase is NOT complete until this block appears in your response:

```
POST-GATE Phase [N] — [phase name]
Build: pass | fail (command: [build command] — see project CLAUDE.md)
Planned files: [list from plan]
Actual files: [list from git diff / agent report]
Deviations: [none | list of extra files with reason — logged, included in result doc]
```

- **Stale diagnostic dismissal (anti-pattern):** Do not dismiss build warnings or diagnostics as "stale" or "LSP catching intermediate state." Every warning is potentially real. If a build tool reports an unused variable, type error, or import issue, dispatch the phase agent to verify and fix — do not reason the warning away yourself. Warnings dismissed as stale in one round reliably resurface as real findings in the next review round.

**File deviation check (mandatory):**
1. List every file the plan specifies for this phase (created or modified)
2. List every file the agent actually created or modified (from the git diff or agent report)
3. Compare the two lists. Any file in list 2 that is NOT in list 1 is a deviation — regardless of whether the agent describes it as "related", "fixing the same pattern", or "obviously necessary"
4. If any deviation exists: log the deviation (file name and reason) and continue execution. Include all deviations in the result doc's Deviations section. Do not stop for approval — but do not silently absorb them either; they must be visible in the final report.

- **Phase bleeding check:** If an agent returns work that covers scope belonging to a subsequent phase (within plan-listed files): (1) output a one-line note to CD identifying which phase was anticipated, (2) in the subsequent phase's dispatch prompt, include a summary of what the earlier agent already implemented and instruct the agent to verify completeness and implement only what remains. If the bleeding substantially changes a subsequent phase (e.g., makes it a verify-only pass), flag to CD rather than silently absorbing. Document any skipped or substantially reduced phases in the result doc under 'Skipped Phases'.

- **Re-dispatch within the same phase (partial completion):** If an agent returns work that is incomplete (missed a component, left TODOs, partially implemented scope), re-dispatch that agent with a PRE-GATE block labeled `Phase [N] re-dispatch — [brief reason]`. The PRE-GATE documents what was missed and why the re-dispatch occurred. Omitting the PRE-GATE for re-dispatches creates untracked sub-phases that can cause drift between the plan and the implementation.

- **Stub audit (mandatory):** After each phase completes, grep the plan-specified files for stub indicators: `TODO`, `FIXME`, `NotImplementedError`, `not yet implemented`, `placeholder`, `raise NotImplementedError`, `pass` as a lone function body, hardcoded return values on functions the plan specified as real implementations (e.g., `return True`, `return []`, `return None` where the plan requires actual logic).
  - **Intermediate phases:** Log any stubs found as tracked items. Include them in the next phase's dispatch prompt so the implementing agent knows they exist and must be filled. This is expected — phased execution legitimately stubs things in early phases that get filled later.
  - **Final phase (or single-phase plans):** Stubs are defects. Re-dispatch the phase agent with a PRE-GATE block listing every stub found, requiring real implementation. Do not proceed to the review-fix loop with known stubs — they will pass code review because they are syntactically valid code. A stub that builds clean is the hardest defect to catch in review; catch it here instead.

- **Data audit (mandatory for phases that produce data artifacts):** If this phase created or modified a seed script, scraper, allowlist, or any file containing data values (not just code logic), verify the data against its authoritative source before marking the phase complete. For each data category: check the count matches the plan's expected count, confirm no fabricated entries exist, and confirm no entries are missing. If any value cannot be traced to a source, flag it via `AskUserQuestion`. Code review catches code quality — the data audit catches data accuracy. These are separate concerns.

Do not start dependent phases until the dependency's POST-GATE clears.

```
Phase 1: Data schema + shared types (independent)
Phase 2: Backend endpoints (depends on Phase 1)
Phase 3: UI components (depends on Phase 1, NOT Phase 2)

-> Phase 1 runs first (PRE-GATE → EXECUTE → POST-GATE)
-> Phase 2 and Phase 3 run in parallel (both only depend on Phase 1)
```

### 2. Completion Review

**MANDATORY — NO PAUSE.** When the last phase's POST-GATE clears, proceed directly to the review loop. A brief phase summary is fine, but do not stop and wait for user input — no "what's next?", no "ready to review?", no waiting for confirmation. The plan already defines the review agents — emit the REVIEW-GATE block and dispatch them in the same response. Phase completion is a waypoint, not a stopping point.

You must emit this block before dispatching review agents:

```
REVIEW-GATE — entering completion review
Phases completed: [list phase numbers]
Review agents (from plan): [list all agent names]
Dispatching: [count] agents
```

After ALL phases are done, run the **Review-Fix Loop** per `ops/sdlc/process/review-fix-loop.md`. **Start with Step 0 (Verification Gate):** run tests, type checks, linting, and any configured SAST tooling BEFORE dispatching review agents. Fix any verification failures first — do not ask reviewers to evaluate code that doesn't build, doesn't pass tests, or has known tool-detected issues. Agent source: the plan's agent assignment table. Classifications: use all five per `ops/sdlc/process/finding-classification.md` (FIX, PLAN, INVESTIGATE, DECIDE, PRE-EXISTING).

**Plan contract briefing (mandatory):** When dispatching review agents in the loop, each agent's prompt must include the plan's specification for the phases they are reviewing — specifically: the expected behavior, acceptance criteria, and implementation approach from the plan. Reviewers check "does the implementation match what was specified?" in addition to "is the code well-written?" A well-structured stub passes code quality review but fails plan compliance review. Without the plan contract, reviewers can only assess code quality — they cannot detect whether the agent delivered what was actually asked for.

This loop is mandatory and repeats until every agent reports clean. When the loop exits cleanly, output "Review loop complete — all agents clean. Proceeding to Worker Agent Reviews." then go to step 3.

### 3. Worker Agent Reviews Output

Every execution MUST end with a Worker Agent Reviews section. This step is only reached when step 2b shows ALL agents reporting no issues. Save as: `docs/current_work/results/dNN_name_result.md`

```markdown
## Worker Agent Reviews

Key feedback incorporated:

- [agent-name] specific, concrete feedback that was incorporated or addressed
- [agent-name] another specific feedback point with actionable detail
- [agent-name] what they caught during review and how it was resolved
```

**Rules:**
- Bracket the agent's exact name: `[frontend-developer]`, `[software-architect]`, etc.
- Each bullet is specific and concrete — not generic praise
- Include feedback from the completion review (step 2)
- Omit agents that found no issues (don't write "[agent] no issues found")
- This section is **mandatory** — the task cannot be marked complete without it

### 3a. Discipline Capture

Run the discipline capture protocol per `ops/sdlc/process/discipline_capture.md`. Context format: `[DNN — phase N]`. This includes structured gap detection (using the review-fix triage table and agent dispatch data from this session) followed by the freeform insight scan.

### 3b. Per-Phase Commits (Mandatory)

After each phase's POST-GATE clears, commit the phase's work before starting the next phase:

1. Stage **all** files created or modified by the phase's agent(s) — this includes:
   - Application code and test files
   - Discipline parking lot entries (`ops/sdlc/disciplines/*.md`) if discipline capture added entries
2. Commit with the cc-sdlc format: `feat[DNN](phase-N): [phase name] — [brief description]`
3. Do NOT wait until all phases are complete to commit

This ensures each phase is independently reviewable, bisectable, and revertable. A single monolithic commit at the end defeats the purpose of phased execution.

**Exception:** If two phases run in parallel and both pass their POST-GATEs, they may share a single commit if the files don't overlap. Document which phases are included.

### 4. Final Verify, Commit, and Mark Complete

Before claiming the work is done:

1. Run the full build (`[build command]` — see project CLAUDE.md)
2. Confirm build passes with zero errors
3. Review the git diff for unintended changes (should be minimal — most work committed per-phase)
4. Stage any remaining modified files — **all categories, not just application code:**
   - Result doc (`docs/current_work/results/dNN_*_result.md`)
   - Catalog updates (`docs/_index.md`)
   - Discipline parking lot entries (`ops/sdlc/disciplines/*.md`)
   - Knowledge store updates (`ops/sdlc/knowledge/*.md`)
   - Process changelog (`ops/sdlc/process/sdlc_changelog.md`) if updated
   - Review fixes from the review loop
5. Commit using the cc-sdlc commit format:
   ```
   {type}[{deliverable_id}]({scope}): {description}

   {optional body — brief summary of what was changed and why}

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```
   **Types:** `feat` (new feature), `fix` (bug fix), `refactor` (restructure, no behavior change), `docs` (documentation only), `test` (adding/updating tests), `chore` (build, config, tooling, dependencies), `style` (formatting, no logic change), `perf` (performance improvement), `ci` (CI/CD changes), `sdlc` (SDLC process, skills, agents, or framework changes)
   **Example:** `feat[D-042](auth): add session refresh endpoint`
6. Present the full commit to the user:

```
Commit: {short-sha}

{full commit message — title, body, and footers as written}

Files changed:
- {file path}
- {file path}
```

7. **Deployment guide (if applicable):** If the work touches infrastructure that requires manual deployment steps beyond an automatic CI/CD deploy (e.g., Cloud Functions, search index config, database indexes/rules, environment variables), present a concise deployment guide to the user. Include: deploy commands in order, any backfill/migration steps, and post-deploy verification checks. Skip this step for changes that deploy automatically.
8. Update `docs/_index.md` — change the deliverable's status from "In Progress" to "Complete" in the Active Work table
9. If on a feature branch, push and create a PR

### Session Handoff

The Manager Rule remains in effect per `ops/sdlc/process/manager-rule.md` — see the Session Scope section.

## Agent Selection Reference

The plan identifies which agents are relevant. If you need to add agents not listed in the plan (e.g., a security concern surfaces during implementation), refer to the full agent tables in the `sdlc-plan` skill's Agent Selection section.

- **Project-level agents**: `.claude/agents/` (project root)
- **Personal-level agents**: `~/.claude/agents/`

## SDLC Integration

This skill produces the third SDLC artifact:

| Artifact | Saved To | Step |
|----------|----------|------|
| Result | `docs/current_work/results/dNN_name_result.md` | 3 |

The spec and plan were produced by `sdlc-plan`.

When the deliverable is complete, the "Let's organize the chronicles" command moves artifacts from `current_work/` to `docs/chronicle/{concept}/` and updates `docs/_index.md`.

## Red Flags

| Thought | Reality |
|---------|---------|
| "There's no plan, I'll wing it" | Stop. Use `sdlc-plan` first. |
| "I'll implement this part myself" | If a worker domain agent exists for it, dispatch them. See Manager Rule. |
| "This phase is small and well-defined, I'll do it directly" | Size is not an exception. Dispatch the agent. |
| "I'll implement directly to avoid context gaps from dispatching" | Complexity increases the need for agents, not decreases it. Pass the context you have to the agent in the dispatch prompt. |
| "I pre-read 8 files so now I have complete context and can implement" | Pre-reading is the first step toward self-implementation. Read the plan file; let agents read the implementation files they need. |
| "I'll just merge the conflict / fix the loose ends myself" | Parallel conflict or partial completion is still an agent task. Re-dispatch the affected agent. |
| "Findings are minor, ship it" | Minor findings compound. Worker domain agents fix them. |
| "I dispatched most of the agents" / "Re-review is overkill" | ALL means ALL. Count the checklist. Count the dispatches. Re-review after every fix round. |
| "I'll skip the PRE-GATE / POST-GATE" | The mandatory output blocks exist because these were skipped in 100% of early executions. Emit the block. |
| "One more iteration and I'll get it" | Three failed attempts means the hypothesis is wrong. Escalate with documented attempts. |
| "This only touches the frontend" | Check. Features rarely affect one layer. If it changes data shape or API contract, backend must review too. |
| "I know a better way to do this" | Search first. If a pattern exists, follow it. Consistency beats cleverness. |
| "I'll fix it without triaging first" | Classify the problem (2c) before attempting a fix. Wrong classification wastes iterations. |
| "This finding is about code I didn't modify in that file" | If the file is in the plan's Files list, the finding is in scope. File presence is the test, not function-level diff. |
| "The review loop finished cleanly" | Output the exit announcement before proceeding. Silent state transitions cause drift. |
| "Build passes, fixes are done — moving on" | Build-pass is step 4, not the review loop exit. After ANY fix round, return to 2a and dispatch ALL agents. Only exit when 2b shows all agents clean. Two audits caught this same skip. |
| "All phases complete — here's a summary" *(then waits for user input)* | Summaries are fine — stopping is not. Emit the summary, then REVIEW-GATE and dispatch review agents in the same response. The plan defines the review agents; no user input is needed to proceed. |
| "I noted the file deviation but didn't log it" | Deviations don't require approval, but they MUST be logged in the POST-GATE output and included in the result doc's Deviations section. Silent absorption defeats traceability. |
| "This is a fix dispatch, not a phase dispatch" | Fix dispatches follow the same protocol as phase dispatches. |
| "Phase 2's agent did Phase 3's work — I'll skip Phase 3" | Note the overlap to CD. Dispatch Phase 3 to verify completeness and implement what remains. |
| "Data sources: read from these codebase files" (plan also mentions external source) | If the plan says data comes from an external source AND codebase files, the dispatch prompt must include BOTH. Listing only codebase files causes agents to hallucinate values for the external-source categories. |
| "This phase produces a scraper/consumer that should align with the seed/config from Phase N" | Tell the agent to READ the Phase N output file for canonical values. Agents will fabricate their own allowlists if not pointed at the canonical source. |
| "The plan is committed, this is just a small follow-up" | Manager Rule applies for the full session. Dispatch the domain agent. |
| "The user asked about the server code — I'll just fix it while I'm here" | Domain crossing. Dispatch the relevant domain agent for that scope. Read domain boundaries in agent definitions. |

## Integration

- **Feeds into:** `sdlc-tests-run` (post-commit test verification), `sdlc-archive` (when deliverable is complete)
- **Uses:** worker domain agents (implementation + review), `sdlc-plan` output (the plan file), `ops/sdlc/process/manager-rule.md`, `ops/sdlc/process/collaboration_model.md`
- **Complements:** `sdlc-lite-execute` (handles lite deliverables), `sdlc-audit` (can audit execution quality post-hoc)
- **Does NOT replace:** `sdlc-plan` (plan must exist before execution), `sdlc-tests-run` (separate test verification step)