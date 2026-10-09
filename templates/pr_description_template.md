# Pull Request Description

The description of a pull request that asks CD to approve agent-written work. Write it for CD, who owns the project but didn't watch the work, not for the agent that executes it. The plan, spec and result documents stay the agent's contract and keep their detail. The PR is where CD decides, and for code it is usually where CD starts reading.

**Use it for:**
- **Plan and spec PRs** (the plan variant): a document for CD to approve, from `sdlc-plan`, `sdlc-lite-plan` or a factory plan stage.
- **Code PRs** (the code variant): from `sdlc-execute`, `sdlc-lite-execute`, direct dispatch, or a factory implement or execute stage.
- **Headless runs** whose output schema has PR-description fields: fill those fields per this template, one field per section (`[sdlc-root]/process/headless-mode.md` § Ending a Headless Run). The caller renders the headings and formatting, so write plain sentences with no markdown, except backticks around a file path or code name.

## Rules

The rules for anything CD reads come first: `[sdlc-root]/process/writing-for-cd.md`. Lead with what CD needs, use plain language, say each thing once, show evidence over claims, say where you're unsure, and don't invent. On top of those, a PR:

- **Tells CD, for sure:** the original problem, what changes for users, what CD is approving, what's tackled and what's left out, the risk, and how it will be (or was) verified.
- **Uses code names only where they help CD find or check something:** How it works, Learn the change, verification evidence and findings.
- **Keeps the fixed order and headings.** The sections below, in this order. Omit a section only where it says so, and add none. Detail that doesn't fit goes in the agent record or stays in the plan.
- **Fits about 450 words above the agent record** for a plan PR, about 500 for a code PR, with each section's share given below. If the change won't fit, it is probably too big for one PR. A PR has one purpose you can state in a sentence.
- **Gives each section one job.** The problem describes today; What changes for users describes afterwards; What you're approving names the choices; Scope names the boundaries; How it works explains the flow; Learn the change explains files and terms.
- **Puts the approach here and lines in code.** How it works explains the approach and how the pieces fit. Why a particular line exists goes in a comment beside it.
- **Leaves an empty list empty.** No Deferred, Deviations or Concepts is fine.

**A plan or spec PR's description is the document's Approval Brief** (`[sdlc-root]/process/writing-for-cd.md` § Approval Briefs), which already passed a fresh reader. For a code PR, **before opening it,** give a fresh reader only the description and the diff (in a skill run, a subagent dispatched in the foreground). It answers two questions. Could someone who didn't watch the work explain the problem, the change, the choices, the risks and the evidence from the description alone? Does every statement match the diff? Fix what it finds, then cut every sentence CD needs neither to approve the change nor to learn from it.

## Risk Tiers

The highest tier that fits wins.

| Tier | When |
|---|---|
| **High** | Money, data integrity (migrations, deletes, bulk writes), authentication and permissions, security; any effect a revert doesn't undo (data written or lost, messages sent, external calls); and the project's always-high areas |
| **Medium** | Changes what valid use gets (results, defaults, screens, API responses) or what the system stores, and a revert fully undoes it |
| **Low** | Valid use works exactly as before, nothing stored changes, and a revert fully undoes it: tests, docs, internal changes covered by tests, rejecting input that was never valid |

A project lists its always-high areas under this heading, inside its own `PROJECT-SECTION` block (`[sdlc-root]/process/project-section-markers.md`), so migrations keep them.

## Plan and Spec PR

Word shares in brackets.

```markdown
## The problem
[≤50] What prompted this, and the symptom a user sees, in 2–3 sentences.

## What changes for users
[≤30] - Each visible change, in the user's terms. Or: Nothing visible.

## What you're approving
[≤90] 1. **The decision.** Rather than the alternative it rejects, and why, in one clause.
Anything beyond what the issue asked for is a numbered decision here that says so.

## Scope
[≤40] - **Tackled:** what this does
- **Not tackled:** non-goals
- **Deferred:** each as a proposed follow-up issue (omit when none)

## Risk
[≤45] **Low | Medium | High**: why, in one clause, by the Risk Tiers table.
- The top 1–3 risks
- **Undo:** how to back it out

## Review focus
[≤40] - Where the author is least sure, and why
- What CD may not have thought of
- Any open critical or major review finding (escalated runs)

## How it will be verified
[≤35] - The tests and checks that will run, and what each proves
- What CD will be able to see or try

## How it works
[≤55] The approach at a high level, how the pieces fit, and why it is shaped this way when that isn't obvious. A spec explains only the approach it settles.

## Learn the change
[≤65] - **Files, in reading order:** `path` (new) — its role in this change. Read the file, or the plan's file list, before naming it.
- **Concepts:** **term** — a plain definition (0–3 of them)

<details><summary>Agent record</summary>

Review rounds and open minor findings, FACTS scores, models and cost, deferred notes from the run, and the path of the full plan or spec.

</details>
```

## Code PR

The same skeleton, with these changes:

- **What you're approving** names the behavior being merged. A decision needs a rejected alternative only where one was weighed.
- **Deviations from the approved plan** [≤30] follows What you're approving: what changed from the plan, and why. Omit it for a direct fix with no plan.
- **Scope integrity** [≤20] follows Scope: "No tests or CI checks weakened; touched only the planned files", or each exception with its reason.
- **How it was verified** [≤50] replaces How it will be verified. Results, not intent: the commands and their outcome, test counts, CI status, screenshots or video for a UI change, and any check that couldn't run.
- **Files, in reading order** name files in the diff.

## Example: Plan PR

From quantile #30. Everything above the agent record, about 450 words:

```markdown
## The problem
The market API ignores filter values it doesn't recognize. `?tradeable_only=ture`, a typo, quietly turns off the filter that keeps only contracts with a positive edge after fees, so a trader sees contracts they believe were filtered out.

## What changes for users
- A bad filter value returns a 400 error naming the filter and its allowed values.
- The web app sends only valid values, so its screens don't change.

## What you're approving
1. **Bad values become 400 errors on every filter the issue lists**, rather than silent fallbacks: financial screens fail loudly.
2. **True/false filters accept only `true` and `false`**, rather than also `1` and `0`, which mean true on one filter and false on another today.
3. **Also check `interval` on drift status, and both filters on performance history**, beyond the issue's list, so neighbouring endpoints follow one rule. Strike these if you prefer.
4. **Delete two lists of valid values that the shared parsers replace**, rather than keep copies that can drift.

## Scope
- **Tackled:** those filters, a written convention for new endpoints (ADR-20), tests for every endpoint.
- **Not tackled:** alert filters, pagination, request bodies, and which interval table is canonical (D11a).
- **Deferred:** the web app shows these errors as "Bad Request"; a one-line fix is proposed as a follow-up.

## Risk
**Medium**: a blank or space-padded value now gets real results instead of empty or wrong ones, and a bad value now fails.
- `?interval=15m` on predictions now errors instead of returning an empty list. Production has no 15m predictions.
- **Undo:** revert the merge; nothing stored changes.

## Review focus
- The reject-or-fallback table in the plan, row by row: it is the decision.
- A bad `interval` on a backtest detail page now gives 400 where it gave 404.

## How it will be verified
- Tests written first against today's endpoints fail, then pass after the change.
- One deliberate break in each parser makes its tests fail.
- The full API test suite passes.

## How it works
One shared set of parsers reads each filter, trims spaces, checks it against a fixed list of allowed values, and returns a 400 listing them. Each view calls its parsers before reading any data. An existing "asset not found" 404 keeps its place, so only the filter checks are new.

## Learn the change
- **Files, in reading order:** `api/market/views/query_params.py`: the parsers and the convention. `api/market/views/contract.py`: the trading filter that motivated this. `api/market/tests/test_query_params.py` (new): what each parser accepts.
- **Concepts:** **fee-adjusted edge**: expected profit on a contract after exchange fees. **Silent fallback**: using a default when a value isn't recognized, without telling the caller.
```

## Example: Code PR Sections

The sections that differ, for the same change after execution. The values are illustrative:

```markdown
## Deviations from the approved plan
- None.

## Scope integrity
No tests or CI checks weakened; touched only the 15 planned files.

## How it was verified
- `pytest -q api/market/tests`: 64 new tests failed before the change and pass after; 412 passed in all.
- Breaking `parse_bool` made 9 tests fail.
- CI: lint, type check and the API suite green on the PR.
- Not run: a browser check (no screen changed).
```
