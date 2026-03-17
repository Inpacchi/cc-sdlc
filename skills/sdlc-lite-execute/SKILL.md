---
name: sdlc-lite-execute
description: >
  Execute a lightweight plan that was produced by sdlc-lite-plan. Worker domain agents implement the phases,
  review the completed work, and fix findings. No SDLC artifacts are created — no result doc, no deliverable tracking.
  Trigger when someone says "execute the lite plan", "go ahead with the plan", "start the lite work",
  or after sdlc-lite-plan has produced a reviewed plan and the user confirms execution via the plan mode prompt.
  The plan file lives at docs/current_work/sdlc-lite/{slug}_plan.md — load it from there.
  Do NOT use for full SDLC deliverables — those use sdlc-execute.
  Do NOT use without a plan — if no plan file exists, use sdlc-lite-plan first.
---

# SDLC-Lite Execution

This skill executes a plan produced by `sdlc-lite-plan`. Worker domain agents implement the phases, review the result, and fix findings. You are the manager — dispatch agents, track completion, and run the review loop until clean.

**Precondition:** A reviewed plan must exist at `docs/current_work/sdlc-lite/{slug}_plan.md`. If no plan file exists, stop and use `sdlc-lite-plan` first.

## The Process

```dot
digraph sdlc_lite_execution {
    rankdir=TB;

    "0. Load plan from\ndocs/current_work/sdlc-lite/" [shape=box];
    "Plan file exists?" [shape=diamond];
    "STOP — run sdlc-lite-plan first" [shape=doublecircle, color=red];

    subgraph cluster_phase_loop {
        label="1. Per-Phase Loop";
        style=dashed;

        "1a. PRE-GATE\n- Pattern Reuse Gate\n- Verify dependencies complete" [shape=box, style=bold, color=blue];
        "1b. DISPATCH worker domain agent(s)\nper plan assignment" [shape=box];
        "1c. POST-GATE\n- [build command]\n- Files match plan?" [shape=box, style=bold, color=blue];
    }

    "All phases complete?" [shape=diamond];
    "2a. Dispatch ALL relevant agents\nfor review" [shape=box];
    "2b. Collect findings" [shape=box];
    "Any findings?" [shape=diamond];
    "2c. Triage + Fix\n(finding agent fixes)" [shape=box];
    "2d. Return to 2a\n(re-review ALL agents)" [shape=box, style=bold];
    "3. Output Worker Agent Reviews" [shape=box];
    "4. Verify + commit + clean up" [shape=doublecircle];

    "0. Load plan from\ndocs/current_work/sdlc-lite/" -> "Plan file exists?";
    "Plan file exists?" -> "STOP — run sdlc-lite-plan first" [label="no"];
    "Plan file exists?" -> "1a. PRE-GATE\n- Pattern Reuse Gate\n- Verify dependencies complete" [label="yes"];
    "1a. PRE-GATE\n- Pattern Reuse Gate\n- Verify dependencies complete" -> "1b. DISPATCH worker domain agent(s)\nper plan assignment";
    "1b. DISPATCH worker domain agent(s)\nper plan assignment" -> "1c. POST-GATE\n- [build command]\n- Files match plan?";
    "1c. POST-GATE\n- [build command]\n- Files match plan?" -> "All phases complete?";
    "All phases complete?" -> "1a. PRE-GATE\n- Pattern Reuse Gate\n- Verify dependencies complete" [label="no — next phase"];
    "All phases complete?" -> "2a. Dispatch ALL relevant agents\nfor review" [label="yes"];
    "2a. Dispatch ALL relevant agents\nfor review" -> "2b. Collect findings";
    "2b. Collect findings" -> "Any findings?";
    "Any findings?" -> "2c. Triage + Fix\n(finding agent fixes)" [label="yes"];
    "2c. Triage + Fix\n(finding agent fixes)" -> "2d. Return to 2a\n(re-review ALL agents)";
    "2d. Return to 2a\n(re-review ALL agents)" -> "2a. Dispatch ALL relevant agents\nfor review";
    "Any findings?" -> "3. Output Worker Agent Reviews" [label="no — all clean"];
    "3. Output Worker Agent Reviews" -> "4. Verify + commit + clean up";
}
```

## Step Details

### Manager Rule

**The manager (you) never edits code files.** This applies unconditionally: before dispatching agents, while waiting for agents, after receiving agent results, during the review loop, and at every other point in this skill. There is no phase of this skill — not Phase 1, not any phase — in which it is correct for you to open a file and make a change. If you notice a problem, the correct action is to dispatch the relevant worker domain agent.

**The size of a change is not a valid reason to self-implement.** "This is small, well-defined, and bounded" is not an exception. A one-line type change still gets dispatched. A targeted edit to a single file still gets dispatched. There are no small-change exceptions.

**Complexity is not a valid reason to self-implement.** "I'll implement this directly to avoid context gaps" or "dispatching agents would lose the patterns I've read" reverses the logic entirely. Complexity increases the need for worker domain agents — it does not reduce it. When you have gathered context from reading files, your role is to pass that context to the worker domain agent in the dispatch prompt, not to implement the work yourself.

**If an agent returns without applying its work** (change not reflected in files, agent reported an error, or the change is missing): re-dispatch that agent with the same instructions. Do NOT apply the change yourself. The rule is re-dispatch, not self-implement.

This rule has no exceptions for scope or completeness. Specifically:

- **Parallel agents produced a file conflict** (one agent's write overwrote another's): re-dispatch the overwritten agent with the current file state and instructions to re-apply its changes. Framing the situation as a "merge task" does not make self-implementation appropriate.
- **An agent's work is mostly complete but has gaps or loose ends**: re-dispatch that agent to close the gaps. "Mostly done" is not done. Finishing the last 10% yourself is the same violation as doing 100% yourself.

### Agent Dispatch Protocol

Dispatch prompts must pass through all relevant context from the plan — outcomes, constraints, acceptance criteria, and any implementation guidance the planning agent included. Never narrate readiness ("Ready to dispatch") and wait for user confirmation. The plan is already approved; execution means continuous forward motion.

### 0. Load the Plan

Read the SDLC-Lite plan file from `docs/current_work/sdlc-lite/`. If multiple plan files exist, check conversation context or ask the user which plan to execute.

**Read the plan file only.** Do not pre-read implementation files, existing components, or codebase patterns before dispatch. The plan file is sufficient context for the manager. Worker domain agents read the files relevant to their own phases when they execute. Pre-reading implementation files and accumulating context is not management — it is the first step toward self-implementation.

Extract from the plan:
1. **Phases and dependencies** — what runs in parallel vs. sequences
2. **Agent assignments** — which worker domain agent owns each phase
3. **Relevant agents** — the full list for post-execution review

If no plan file exists, stop:

> No SDLC-Lite plan found at `docs/current_work/sdlc-lite/`. Use `sdlc-lite-plan` first.

### 1. Execute Phases

Follow the plan's phase structure. For each phase:

**PRE-GATE** — you cannot dispatch the phase agent until this block appears in your response:

```
PRE-GATE Phase [N] — [phase name]
Pattern search: [what you searched for] → [found / not found / following pattern at path/to/file.ts]
Dependencies: [phase N complete | none required]
File-conflict check: [parallel only — list files per phase, confirm no overlap | N/A — sequential]
Data sources: [ALL external sources from the plan for this phase — URLs, repos, APIs, documents | "codebase only"]
Expected counts: [any counts stated in the plan — "14 trigger prefixes", "11 counter types" | none]
Design Decisions: [list binding decisions from the plan that apply to this phase | none]
Agent: [agent-name]
```

- **Pattern Reuse Gate:** Search the codebase for existing implementations of what this phase builds. Use LSP `goToImplementation` for interface methods and `findReferences` for hooks/utilities. Use Grep for text patterns in configuration or documentation. If a pattern exists, follow it — consistency over preference.
- Verify all dependency phases are complete
- **File-Conflict Gate (parallel phases only):** Before dispatching two or more phases simultaneously, list every file each phase will modify. If any file appears in more than one phase, those phases MUST run sequentially — dispatch the first phase, wait for POST-GATE to pass, then dispatch the second. Do not rely on the plan's dependency table alone; verify file overlap yourself.
- **Data Source Extraction (mandatory):** Read the plan's phase description and extract EVERY data source mentioned — external repos, APIs, URLs, documents, AND codebase files. List them all in the PRE-GATE block. If the plan says data comes from an external source, the dispatch prompt MUST tell the agent to fetch from that source. Omitting an external data source from the dispatch prompt causes agents to hallucinate values instead of reading from the defined source.
**DISPATCH:** List the agent and phase description before dispatching. Every listed agent must have a corresponding dispatch. If you find yourself editing files directly instead of dispatching an agent, stop — that violates the Manager Rule.

**EXECUTE:** Dispatch the assigned agent(s). The dispatch prompt must include:
1. **The phase's full context from the plan** — outcome, constraints, acceptance criteria, AND any implementation guidance the planning agent included (approach hints, key functions, file relationships, migration notes, data flow context). The plan is the agent's primary briefing document — pass through everything relevant to this phase. Do not summarize or omit plan details; the executing agent benefits from the planning agent's full reasoning.
2. **All data sources** from the PRE-GATE extraction — external sources get explicit fetch instructions. For data extraction tasks, tell the agent to read ALL relevant pages from the source, extract ALL entries exhaustively, and cross-check the final count.
3. **Expected counts** from the plan — the agent can self-check its output
4. **Binding Design Decisions** that constrain this phase's implementation
5. **Prior phase artifacts** — when this phase depends on a completed phase that produced data artifacts (seed scripts, config files, type definitions), the dispatch prompt must tell the agent to read those files as the canonical reference. Agents that produce coupled artifacts will fabricate their own values if not told where the canonical data lives.
6. **Library verification instructions** — when the phase involves external library/framework APIs, tell the agent to verify API usage via Context7 (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`) before writing integration code. Include the library names and versions from the project's dependency files. Agents must not rely on training data for API signatures, parameter names, or default behaviors.
For independent phases, dispatch in parallel using multiple Agent tool calls in a single message.

**Cross-domain knowledge injection:** When a phase requires an agent to work in a context outside its primary domain, consult `ops/sdlc/knowledge/agent-context-map.yaml` for the other domain's agent and include those knowledge files in the dispatch prompt. Use judgment — only inject when the agent is genuinely crossing into unfamiliar territory. Do not inject for routine single-domain work.

**POST-GATE:**
- Verify build passes: `[build command]` — see project CLAUDE.md
- **File deviation check (mandatory):**
  1. List every file the plan specifies for this phase (created or modified)
  2. List every file the agent actually created or modified (from the git diff or agent report)
  3. Compare the two lists. Any file in list 2 that is NOT in list 1 is a deviation — regardless of whether the agent describes it as "related", "fixing the same pattern", or "obviously necessary"
  4. If any deviation exists: stop, report the extra files to the user, and wait for explicit approval before starting the next phase. Do not proceed on your own judgment that the extra work was warranted.

- **Phase bleeding check:** If an agent returns work that covers scope belonging to a subsequent phase (within plan-listed files): (1) output a one-line note to the user identifying which phase was anticipated, (2) in the subsequent phase's dispatch prompt, include a summary of what the earlier agent already implemented and instruct the agent to verify completeness and implement only what remains. If the bleeding substantially changes a subsequent phase (e.g., makes it a verify-only pass), flag to the user rather than silently absorbing.

- **Data audit (mandatory for phases that produce data artifacts):** If this phase created or modified a seed script, scraper, allowlist, or any file containing data values (not just code logic), verify the data against its authoritative source before marking the phase complete. For each data category: check the count matches the plan's expected count, confirm no fabricated entries exist, and confirm no entries are missing. If any value cannot be traced to a source, flag it via `AskUserQuestion`. Code review catches code quality — the data audit catches data accuracy. These are separate concerns.

A phase is NOT complete until POST-GATE passes.

### 2. Completion Review Loop

After ALL phases are done, run the review-fix loop. This is mandatory and repeats until every agent reports clean.

#### 2a. Dispatch ALL Review Agents

List every relevant worker domain agent from the plan. Dispatch ALL of them — not a subset. Include `code-reviewer` if it was listed as relevant during planning.

**Review agents report findings only. They do NOT fix anything.** Fixes are dispatched in step 2c after the manager classifies each finding. An agent that fixes inline during review has bypassed the triage gate — that is a process failure, not a shortcut.

#### 2b. Collect Findings

Wait for all agents to return. Output a findings table:

```
Review round N results:
| Agent | Findings | Severity |
|-------|----------|----------|
| agent-1 | specific finding | critical/major/minor |
| agent-2 | no issues | — |
```

**All agents clean → output "Review loop complete — all agents clean. Proceeding to Worker Agent Reviews." then go to step 3.**
**Any findings → go to 2c.**

#### 2c. Triage + Fix

Classify each finding individually — no blanket dismissals. Every finding gets a classification and rationale.

| Classification | When | Action |
|---------------|------|--------|
| **FIX** | Confident in diagnosis and fix | Dispatch the most relevant domain agent to fix it |
| **INVESTIGATE** | Need more info | Dispatch relevant agent to diagnose |
| **DECIDE** | Trade-off or business decision | Invoke the `AskUserQuestion` tool with the finding description and options. Do not type the question as conversational text. Block until the user answers. |
| **PRE-EXISTING** | Finding exists in code this work did not touch | No action — cite the file and explain why it's out of scope |

**Use only these four classifications.** If a finding doesn't fit, use DECIDE.

**PRE-EXISTING** qualifies ONLY if the finding's file is not in the plan's Files list AND was not created or modified by an agent during execution. If the file appears in the Files list, or if an agent touched it during this execution, any finding about that file is in scope — regardless of whether the finding is about the specific function the plan modifies.

Dispatch the most relevant domain agent to fix each finding — this is often the agent who found it, but may be a different agent with deeper expertise in the affected file. Dispatch all FIX agents before re-reviewing.

#### 2d. Re-Review (Mandatory)

After fixes, return to 2a and dispatch ALL agents again — not just the ones who found issues. Fixes can introduce new problems in other domains.

**3-strike rule:** Same finding category 3 times in a row — stop iterating. Output: (1) the finding text, (2) the agent dispatched to fix it, (3) what each attempt returned, (4) your hypothesis for why attempts are failing. Then invoke `AskUserQuestion` to escalate — do not type the escalation as conversational text.

### 3. Worker Agent Reviews

Every SDLC-Lite execution ends with this section, presented in conversation. This step is only reached when 2b shows ALL agents reporting no issues.

```markdown
## Worker Agent Reviews

Key feedback incorporated:

- [agent-name] specific, concrete feedback that was incorporated
- [agent-name] another specific feedback point with actionable detail
```

**Rules:**
- Bracket the agent's exact name: `[frontend-developer]`, `[software-architect]`, etc.
- Each bullet is specific and concrete — not "code looks good" but "input validation on SubmitForm correctly rejects empty values — prevents silent failures on form submission"
- Omit agents that found no issues
- This section is mandatory — the work is not done without it

### 4. Verify, Commit, and Clean Up

1. Run `[build command]` — confirm zero errors (see project CLAUDE.md)
2. Review the git diff for unintended changes
3. Stage all modified files (application code + any new files created by agents)
4. Commit with conventional commit format (see project CLAUDE.md):
   ```
   {type}[({scope})]: {description}

   {optional body — brief summary of what was changed and why}

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```
5. **Deployment guide (if applicable):** If the work touches infrastructure that requires manual deployment steps beyond an automatic CI/CD deploy (e.g., Cloud Functions, search index config, database indexes/rules, environment variables), present a concise deployment guide to the user. Include: deploy commands in order, any backfill/migration steps, and post-deploy verification checks. Skip this step for changes that deploy automatically.
6. Move the plan file to `docs/current_work/sdlc-lite/completed/` — preserves the "why this approach" context for reconciliation
7. Present the full commit to the user:

```
Commit: {short-sha}

{full commit message — title, body, and footers as written}

Files changed:
- {file path}
- {file path}
```

## What This Skill Does NOT Do

- **No SDLC artifacts.** No result doc, no deliverable tracking, no catalog entry.

## Red Flags

| Thought | Reality |
|---------|---------|
| "There's no plan, I'll wing it" | Stop. Use `sdlc-lite-plan` first. |
| "I'll implement this myself" | If a domain agent exists for it, dispatch them. |
| "This phase is small and well-defined, I'll do it directly" | Size is not an exception. Dispatch the agent. |
| "I'll implement directly to avoid context gaps from dispatching" | Complexity increases the need for agents, not decreases it. Pass the context you have to the agent in the dispatch prompt. |
| "I pre-read 8 files so now I have complete context and can implement" | Pre-reading is the first step toward self-implementation. Read the plan file; let agents read the implementation files they need. |
| "Skip re-review, the fixes were small" | Small fixes cause new bugs. 2d says return to 2a. |
| "I'll skip the review loop, everything looks clean" | The review loop catches what confidence misses. Run it. |
| "I dispatched most of the agents" | ALL means ALL. Count the checklist. Count the dispatches. Match. |
| "One more iteration and I'll get it" | Three failed attempts = wrong hypothesis. Escalate to user. |
| "I'll just merge the conflict / fix the loose ends myself" | Parallel conflict or partial completion is still an agent failure. Re-dispatch the affected agent. |
| "This finding is about code I didn't modify in that file" | If the file is in the plan's Files list, the finding is in scope. File presence is the test, not function-level diff. |
| "The review loop finished cleanly" | Output the exit announcement before proceeding. Silent state transitions cause drift. |
| "Build passes, fixes are done — moving on" | Build-pass is step 4, not the review loop exit. After ANY fix round, return to 2a and dispatch ALL agents. Only exit when 2b shows all agents clean. Two audits caught this same skip. |
| "I noted the file deviation but it's reasonable, proceeding" | POST-GATE says "wait for explicit approval." Noting a deviation is not the same as getting approval. Stop and ask — even if the extra file is obviously necessary. |
| "Ready to dispatch" / "Let me dispatch now" | Never narrate readiness — just dispatch. The plan is already approved. |
| "Phase 2's agent did Phase 3's work — I'll skip Phase 3" | Note the overlap to the user. Dispatch Phase 3 to verify completeness and implement what remains. |
| "Data sources: read from these codebase files" (plan also mentions external source) | If the plan says data comes from an external source AND codebase files, the dispatch prompt must include BOTH. Listing only codebase files causes agents to hallucinate values for the external-source categories. |
| "This phase produces a scraper/consumer that should align with the seed/config from Phase N" | Tell the agent to READ the Phase N output file for canonical values. Agents will fabricate their own allowlists if not pointed at the canonical source. |

## Integration

- **sdlc-lite-plan** — The prerequisite skill that produces the plan file
- **sdlc-execute** — Use instead when executing SDLC deliverable plans
- **test-loop** — If the plan included test files, run after commit to verify tests pass and fix failures automatically
