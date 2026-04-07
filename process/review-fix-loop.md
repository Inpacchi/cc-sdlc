# Review-Fix Loop

The core validation pattern that determines when work is done. Every execution skill references this file for the post-completion review cycle.

---

## Overview

After all implementation work completes, verify that evidence exists (tests pass, linters clean), then dispatch ALL relevant domain agents to review in isolated contexts. Collect findings, classify them, fix them, and re-review until every agent reports clean. This loop is mandatory and has no shortcuts.

## Step 0: Verification Gate (before agent review)

<!-- Source: Claude Code Best Practices (code.claude.com/docs/en/best-practices) — "Give Claude a way to verify its work."
     CS146S Wk 6: AI Testing and Security — SAST/DAST integration, Isaac Evans (CEO Semgrep).
     Semgrep blog: Agent-based vuln detection has ~85% false positive rate — tool verification first.
     Google AutoCommenter paper (AIware '24): AI review comments on unchanged code waste attention — scope to changed files.
     Reddit "How we vibe code at a FAANG": "Always write tests first" — tests before implementation, agent builds to pass. -->

Before dispatching any review agent, confirm that machine-verifiable evidence exists and passes. Agent review without verification is opinion — it catches style and design issues but cannot reliably catch functional bugs (agent-based vulnerability detection has a measured ~85% false positive rate). Verification catches functional bugs but cannot catch design issues. Both are required; verification comes first because it's cheaper and objective.

**Required checks (run all that apply):**

1. **Tests exist and pass** — If the plan or spec defines acceptance criteria, corresponding tests must exist. Run the test suite. If tests fail, fix them before entering the review loop — do not ask reviewers to evaluate broken code.
2. **Type checking passes** — If the project has a type system (TypeScript, mypy, etc.), run the type checker. Type errors are not review findings; they are build failures.
3. **Linter passes** — If the project has linting configured, run it. Lint violations are not review findings; they are automated checks that should pass before human review.
4. **Security scanning passes** — If SAST tooling is configured (Semgrep, ESLint security plugins), run it. Tool-detected vulnerabilities are machine-verified findings with higher confidence than agent opinions.

**Output the verification summary before proceeding:**

```
Verification gate:
- Tests: ✓ passed (47/47) | ✗ 3 failures — fix before review
- Types: ✓ clean | ✗ 2 errors — fix before review
- Lint: ✓ clean | ✗ warnings only (proceeding)
- SAST: ✓ clean | ○ not configured
```

**If any required check fails, fix it before proceeding to Step A.** Do not enter the review loop with known failures — this wastes agent context on problems that tooling already identified.

**If no tests exist for the implemented functionality:** This is itself a finding. Note it in the verification summary and flag it to CD before proceeding. The absence of tests means the review loop has no objective ground truth — agent opinions will be the only quality signal, which is insufficient for production code.

## Step A: Dispatch ALL Review Agents

Use the plan's agent assignment table (or the original review's agent list) as the starting set — do not re-evaluate relevance from scratch. Add agents if new domains surfaced during implementation; do not remove agents from the list. Dispatch **every single one** — not a subset.

**Review agents report findings only. They do NOT fix anything.** Fixes are dispatched in Step C after the manager classifies each finding. An agent that fixes inline during review has bypassed the triage gate — that is a process failure, not a shortcut.

<!-- Source: Claude Code Best Practices (code.claude.com/docs/en/best-practices) — Writer/Reviewer pattern with separate sessions.
     CS146S Wk 4: Human-agent collaboration patterns.
     Medium/OutsightAI, "Peeking Under the Hood of Claude Code": Sub-agents spawn with narrower context
       and no todo-list reminders — separate context prevents cognitive drift in specialized sub-tasks. -->

**Context separation rule:** Review agents MUST be dispatched as subagents (separate context windows), not inline in the orchestrator's context. This is not optional — it exists to prevent confirmation bias. An agent reviewing code in the same context that wrote it has access to the implementation rationale, the failed approaches, and the conversation history. This biases it toward approving the code because it "understands why" decisions were made. A reviewer in a fresh context sees only the code and the spec — it evaluates what was built, not why it was built that way. This mirrors the principle that code review should evaluate the artifact, not the author's intent.

**Plan contract injection (when available):** When the review-fix loop is invoked from an execution skill (`sdlc-execute`, `sdlc-lite-execute`), the plan document is available. Each reviewer's dispatch prompt must include the plan's specification for the work they are reviewing — expected behavior, acceptance criteria, and implementation approach. This enables **plan compliance review**: reviewers check "does the implementation match what was specified?" alongside standard code quality checks. Without the plan contract, a well-structured stub that builds clean will pass review — the reviewer has no way to know the plan required a real implementation.

Before dispatching, output this checklist:

```
Review round N — dispatching:
- [ ] agent-name-1
- [ ] agent-name-2
- [ ] agent-name-3
```

Every box must have a corresponding agent dispatch. If the number of dispatched agents doesn't match the checklist count, **stop and fix before proceeding**.

## Step B: Collect Findings

Wait for ALL agents to return. For each agent, record:
- Agent name
- Findings (or "no issues")

Output a findings table:

```
Review round N results:
| Agent | Findings | Severity |
|-------|----------|----------|
| agent-1 | specific finding | critical/major/minor |
| agent-2 | no issues | — |
```

**If any agent has findings → go to Step C.**
**If ALL agents report no issues → output "Review loop complete — all agents clean." and exit the loop.**

"Clean" means zero findings. Not "findings I consider pre-existing." Not "only minor suggestions." Zero.

## Step C: Triage + Fix

Classify each finding using the finding classification protocol per `process/finding-classification.md`.

**Security finding calibration:** Agent-based security review has a measured ~85% false positive rate (Semgrep 2025 study). Security agent findings that are not corroborated by tool output (Step 0 SAST results) should be scrutinized more carefully than findings from code-reviewer or architect agents. If a security finding seems plausible but uncertain, classify it as INVESTIGATE rather than FIX — verify it with a targeted tool scan or manual inspection before committing a fix that may be unnecessary.

Dispatch the most relevant domain agent to fix each FIX finding — this is often the agent who found it, but may be a different agent with deeper expertise in the affected file. If multiple findings need fixes, dispatch all of them before re-reviewing.

For anything that isn't a FIX, state what you don't know:
```
**Unknown**: [specific thing you haven't verified]
```

## Step D: Re-Review (Mandatory)

After ALL fixes from Step C are applied, **return to Step A**. Before dispatching, check whether any fixes introduced new domains not covered by the existing agent list. If yes, add the relevant agent(s) to the checklist for this round. Then dispatch ALL agents — not just the ones who found issues. Fixes can introduce new problems in other domains.

**This loop repeats until Step B shows ALL agents reporting no issues.** There is no shortcut. Do not claim the loop is closed without a clean round.

## 3-Strike Rule

If the same agent reports the same finding category in 3 consecutive review rounds — regardless of what was changed between rounds — stop iterating. Output:

1. The finding text
2. The agent dispatched to fix it
3. What each attempt returned
4. Your hypothesis for why attempts are failing

Then invoke `AskUserQuestion` to escalate to CD — do not type the escalation as conversational text. Save progress in a partial result doc if applicable.

## Skill-Specific Variations

| Skill | Agent Source | Notes |
|-------|------------|-------|
| `sdlc-execute` | Plan's agent assignment table | Full review with result doc output |
| `sdlc-lite-execute` | Plan's agent assignment table | Same loop, result doc saved to sdlc-lite/ |
| `sdlc-review-fix` | Original `/sdlc-review-commit` agent list | Loop starts after initial fix dispatch |
