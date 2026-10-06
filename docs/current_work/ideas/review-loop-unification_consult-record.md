---
type: reference
slug: review-loop-unification
created: 2026-10-06
related_handoff: docs/current_work/ideas/review-loop-unification_handoff.md
---

# Consult record: review-loop changes (Fable + Codex GPT-6-Astra)

Raw rulings from the two independent reviewers consulted on 2026-10-06, kept so the implementing session can read the reasoning behind the decisions in the handoff. Both reviewers received the same brief (section 1) plus a later correction (section 2); neither saw the other's answer. Fable ran as a Claude subagent and received the Q4b correction as a mid-run message, so it answered Q4b with its own Q1–Q4 reasoning already in context; Codex ran as `codex exec -m gpt-6-astra --config model_reasoning_effort=ultra --sandbox read-only` in this repo, with Q4b answered in a separate second run that saw the brief plus the correction but not its own earlier answers. File links were converted to repo-relative paths. **These are inputs, not decisions** — CD's decisions are in the handoff and override anything here (notably: no reviewer reuse, no lighter lite tier, Fable's mechanical re-review trigger).

## 1. Brief sent to both reviewers

### Consultation brief: cc-sdlc review-fix loop changes

You are an independent reviewer. You are being asked to **adjudicate** four proposed changes to the review-fix loop of the cc-sdlc framework: rule on each, and disagree where the evidence warrants. That includes disagreeing with the framework owner's stated preferences, which are listed below so you can test them, not defer to them. A verdict of "the status quo is better" is a valid answer.

#### Context

cc-sdlc is a Claude Code process framework (skills, subagent definitions, process docs) installed into the owner's software projects. The repository is your working directory. In it, an orchestrator session dispatches domain-specialist subagents to write plans, implement phases, and review code. Every review dispatch starts a fresh subagent with its own context window, and each one reads its own knowledge files.

Two constraints shape the answer:

1. **Cost is usage limits and wall-clock time, not dollars.** The owner is on a flat-rate Claude subscription. Dollar figures below are API-rate equivalents, used only as a unit of measure. Spending them means hitting the plan's 5-hour and weekly usage limits sooner, and waiting longer for loops to finish.
2. **These loops will soon run unattended.** The owner plans to run the same skills headlessly from GitHub issues on a self-hosted runner, with nobody watching a terminal. A loop with no termination guarantee would burn usage limits unobserved.

#### Evidence (last 30 days of the owner's real sessions)

**Measured** from local transcript token counts:
- 4,775 subagent conversations cost about $10.9k at API rates, two-thirds of total usage of about $16.3k.
- 95% of all cost is re-reading context: prompt-cache reads and writes. Output is 5%.
- A typical subagent starts at about 43k tokens of context and grows to about 150k over about 24 requests.
- Cache rewrites after an idle gap of more than 1 hour cost about $1.1k.

**Heuristic.** These figures come from classifying each subagent's dispatch description with regular expressions, so treat them as approximate:
- **Spend by purpose:**

  | Purpose | Dispatches | Cost (API rate) |
  |---|---|---|
  | Review and re-review | about 3,008 | about $5.1k |
  | Implement / fix | about 734 | about $2.8k |
  | Other (many are "verify" / "confirm" rounds) | about 836 | about $2.5k |
  | Plan / research | about 197 | about $0.5k |

- **Review checkpoints:** across 97 multi-reviewer checkpoints, the roster size had a median of 7, a 90th percentile of 12, and a maximum of 15.
- **Labelled review rounds** reached as high as round 23. Reviewer dispatches by round:

  | Rounds | Dispatches |
  |---|---|
  | 3-5 | 469 |
  | 6-10 | 224 |
  | 11 and later | 183 |

- **Findings never fall off.** In every round bucket, about 60-75% of reviewers report at least one finding, including after round 10. The median checkpoint had 75% of its reviewers report findings.
- **Severity is unclear.** A keyword check for critical/major severity was noisy because it matched negations such as "no blockers," so it is inconclusive.
- **Spot check.** Eight late-round reviewer reports (rounds 7-20) were read by hand. Nearly every finding was self-described as minor, for example a 1px spacing issue, runbook wording, or a small test gap.

**Not established:**
- Whether first-round findings are distinct from one another or duplicated across reviewers.
- What share of findings were real defects rather than noise.
- Whether the full-roster re-reviews caught regressions that a narrower re-review would have missed.

#### Current rules (read the files; do not rely on this summary)

- `process/review-fix-loop.md`:
  - :76-80 says dispatch ALL review agents and "do not remove agents from the list."
  - :87 is the context-separation rule: fresh-context reviewers exist to prevent confirmation bias.
  - :119-123 says exit only when every agent reports zero findings: "Not 'only minor suggestions.' Zero."
  - :140-144 says re-review is mandatory after any fix, by ALL agents, "not just the ones who found issues."
  - :177 is the 3-strike rule, which applies to the same finding category only. There is no round cap.
- `skills/sdlc-execute/SKILL.md` around :355-364, and its red-flags table at :601 ("Re-review is overkill" → "ALL means ALL").
- `skills/sdlc-lite-execute/SKILL.md` :509: "Skip re-review, the fixes were small" is listed as a red flag.
- `skills/sdlc-review-code/SKILL.md` :224 (groups fixes by agent), :367 ("The diff is small, skip some lenses" is a red flag), :372.
- `skills/sdlc-plan/SKILL.md` :170-182 (selection rule "When in doubt, include"), :560-595 (plan review).
  - **Note the asymmetry.** Plan review stops when "All agents report no critical or major findings. Minor findings may be acknowledged without a fix." Plan re-review fires only on mechanical triggers: a critical FIX, a changed file list, or a changed phase or agent. When it does fire, it still dispatches the full roster.
- `knowledge/architecture/agent-orchestration-patterns.yaml` AOP5, "Right-size the agent group." It gives a 1/2/3/4-5 group-size table, says "Beyond 5... split," and names as an anti-pattern "Dispatching the same set of reviewers for trivial diffs and architectural changes alike." Only the plan skills cite it; the execution skills and the review loop do not.
- `process/finding-classification.md`, `process/manager-rule.md` (the delegation economics exception), and `process/external-review-gate.md` (the external reviewer is capped at 2 rounds and skips trivial or docs-only diffs).
- History in `process/sdlc_changelog.md`:
  - The 2026-04-14 entry records an audit where review-fix "spawned 17 fresh agents instead of reusing teammates (63% of total token cost)." A team-based review-fix skill with agent reuse was added in response.
  - The 2026-05-12 entry removed that skill as "underused."

#### The four questions

##### Q1. Re-review scope after fixes
**Proposal:** after a fix round, re-dispatch only the reviewers who raised findings, plus the reviewers whose domains own the files the fix touched. Bring back the full roster when a fix reaches new files or domains, or changes behavior beyond the finding's scope.
**Owner's concern:** fixes change code, and the other reviewers' lenses may catch problems the fix introduced. The owner leans toward keeping the full-roster re-review.

##### Q2. Exit bar, and whether to cap rounds
**Proposal:** exit when no critical or major findings remain, matching plan review. Batch the remaining minor findings into one fix pass that only the raising reviewer checks, or record them as acknowledged.
**Separate question:** should there be a round cap, for example escalating to the human after round 3, and what should happen at the cap when the loop runs unattended (park the run with a label, open the PR with an open-findings list, or something else)?
**Owner's position:** agrees with the exit-bar change. Unsure whether a round cap is wise.

##### Q3. Reusing reviewers across rounds
**Proposal under consideration:** continue the same reviewer subagent across rounds (Claude Code can resume a subagent with its context intact) instead of starting a fresh one each round. Its knowledge files and earlier analysis would stay loaded, and each round would add only the fix delta.
**Cuts both ways:**
- For it: no re-reading of knowledge files each round; the reviewer remembers what it flagged and why.
- Against it:
  - The context-separation rule at review-fix-loop.md:87 exists to prevent confirmation bias, and a reused reviewer may shift into "verify my own finding was fixed" mode.
  - Cache economics only favour reuse when rounds are less than about 1 hour apart. After that, the resumed context is rewritten at the 2x cache-write price.
  - Reuse was tried in a different form (team-review-fix) and later removed.

##### Q4. First-round roster size
**Proposal:** size the first-round roster to the change, as AOP5 already prescribes, instead of "when in doubt, include" plus always-on reviewers. Remove the red flags that forbid trimming for small diffs.
**Owner's concern:** prefers the larger roster for its breadth of perspectives.

#### What to return

For each of Q1-Q4:
1. **Verdict:** agree / agree with modification / disagree.
2. **Reasoning:** steelman the owner's stated concern before ruling.
3. **Failure modes** of the proposal AND of the status quo.
4. **Exact rule wording** you would put in the framework, in two to four sentences.
5. **Evidence** that would change your mind, and a cheap way to collect it.

Then:
- Anything the four questions missed that matters more. For example: duplicate findings across reviewers, how the orchestrator triages minor findings, a per-run budget for headless mode, or differences between the lite and full tiers.
- One line on whether these changes should land together or be staged.

Read the cited files yourself before ruling. Keep the response under about 1,200 words. Do not edit any files.

## 2. Correction sent mid-run (Q4b)

### Correction to Q4 of the review-loop consultation brief

The brief's Q4 ("First-round roster size") misread the owner's fourth question. Keep your Q4 answer on general roster sizing; it is still useful context. Add a separate ruling, **Q4b**, on the question the owner actually asked.

#### Q4b. Should the lite tier use a lighter review than the full tier?

**Current state.** The two tiers differ only in their artifacts:
- `sdlc-lite-plan` and `sdlc-lite-execute` drop the spec and cap plans at 4 phases.
- Their review rules are identical to the full tier's:
  - the same roster selection ("When in doubt, include", plus the always-on code-reviewer and software-architect)
  - the same full-roster re-review after every fix
  - the same exit at zero findings, minor ones included
- As a result, a lite deliverable produces about as many subagent dispatches as a full one: roughly 22-45 by the process's own arithmetic, at a typical roster of 5-7.

**When the lite tier applies.** `CLAUDE-SDLC.md` § Three Tiers of Work says the lite tier is for work "complex enough to benefit from a reviewed plan up front, but doesn't need a spec."

**Proposal under consideration.** Give the lite tier a smaller review roster and/or a lighter loop than the full tier. For example:
- a capped roster sized by AOP5
- the "no critical/major" exit bar
- scoped re-review

so that the lite tier is lighter in review effort, not only in artifacts.

**Owner's position.** Not sure. Leans toward keeping the larger roster for breadth of perspective.

**Files to read.**
- `skills/sdlc-lite-plan/SKILL.md`: the roster selection near :82 and :126, and the plan review around :250-312.
- `skills/sdlc-lite-execute/SKILL.md`: the review section and the red flag at :509.
- `CLAUDE-SDLC.md`: the tier table.

**Return format.** Answer Q4b in the same five-part format as Q1-Q4:
1. verdict
2. reasoning, steelmanning the owner's concern
3. failure modes of both the proposal and the status quo
4. exact rule wording
5. evidence that would change your mind

Also say whether your Q1-Q3 answers change for lite-tier work.

## 3. Codex (GPT-6-Astra, ultra): Q1–Q4

**Q1. Re-review scope after fixes**

1. **Verdict: agree with modification.**
2. **Reasoning:** The owner’s concern is valid: a frontend fix can break accessibility or performance without touching another file. [AOP2 explicitly partitions review by concern, not file ownership](knowledge/architecture/agent-orchestration-patterns.yaml:62). Nevertheless, repeating every lens for demonstrably bounded fixes spends scarce capacity without established marginal benefit. Permit narrowing based on affected concerns, with conservative fallbacks.
3. **Failure modes:** Proposal: incomplete impact mapping excludes the reviewer who would catch a regression. Status quo: repeated broad searches generate unrelated findings, extra fixes, and further regression opportunities.
4. **Exact rule wording:** “After each fix batch, rerun applicable verification and identify affected concerns, contracts, and dependencies. For bounded, low-risk fixes, re-dispatch raising reviewers, affected specialists, and a reviewer assigned cross-cutting regression checks; these roles may overlap. Dispatch the full selected roster, adding specialists as needed, when fixes reach new files or domains, change behavior beyond the finding, involve high-risk paths, or have uncertain effects. Reviewers inspect current code and the fix delta, including possible regressions beyond the original finding.”
5. **Evidence:** Frequent confirmed regressions found uniquely by excluded reviewers would reverse this preference. Cheap check: select a hypothetical narrowed roster for 20 historical fix diffs *before* reading their subsequent reviewer reports, then classify what it would have missed.

**Q2. Exit bar and round cap**

1. **Verdict: agree with modification; add a mandatory cap.**
2. **Reasoning:** The owner reasonably accepts diminishing returns on polish, while worrying that an arbitrary cap interrupts legitimate repairs. However, a cap should stop automation, not certify unfinished work. The [existing three-strike rule](process/review-fix-loop.md:177) cannot stop an endless sequence of different findings. Eight late reports suggest churn but do not establish that all late findings are harmless.
3. **Failure modes:** Proposal: severity downgrading conceals defects; “one minor pass” introduces an unchecked regression; caps park recoverable work. Status quo: no termination guarantee, plus mandatory human questions that cannot be answered unattended.
4. **Exact rule wording:** “Complete review only when final-revision verification passes and no critical/major findings or potentially blocking unresolved investigations or decisions remain. Record minors under an explicitly authorized acknowledgment policy, or batch them into one fix pass reviewed under the same risk-based scope rules. Allow at most three internal review rounds, including the initial round and external-gate re-entry, within a finite run budget. If completion criteria remain unmet at a limit, preserve the revision, verification evidence, and open findings, create or update a draft PR marked `needs-human`, and stop without declaring validation or automatically retrying.”
5. **Evidence:** Frequent productive blocker resolution just beyond round three would justify a higher configured cap. Manually grade a random sample of late-round reports and link each confirmed blocker to its discovery and resolution rounds; do not use severity keywords alone.

**Q3. Reusing reviewers**

1. **Verdict: agree with modification.**
2. **Reasoning:** The strongest objection is anchoring: a returning reviewer may validate its requested fix instead of seeking new defects. But [the separation rule](process/review-fix-loop.md:87) principally separates writer history from reviewer history; reviewer continuity does not inherently violate it. The [April audit](process/sdlc_changelog.md:2799) supports investigating reuse; [“underused” removal](process/sdlc_changelog.md:1167) is not evidence that reuse reduced quality.
3. **Failure modes:** Proposal: anchoring, stale file knowledge, accidentally resuming a fixer, and growing cached context. Status quo: repeated knowledge loading and rediscovery. Resumption adds a delta to history, but processing that accumulated history is not free; cold rewrites can erase savings.
4. **Exact rule wording:** “Resume a reviewer only when that context has never written the implementation or its fixes. Supply the current revision, fix delta, and acceptance criteria, requiring inspection of current code and a regression search beyond previous findings. Use fresh independent review for materially expanded or high-risk changes. Start fresh when measured context size and cache behavior make resumption less economical.”
5. **Evidence:** More confirmed regression misses, or no usage/time savings, would reject reuse. Compare fresh and resumed reviewers on five sampled re-reviews of identical revisions, withholding each other’s findings; record cache reads/writes, total input, latency, and confirmed defects.

**Q4. First-round roster size**

1. **Verdict: agree with modification.**
2. **Reasoning:** The owner’s breadth argument is strongest when specialists detect different failure classes; shared files do not imply redundant expertise. But breadth requires a concrete coverage argument. [AOP5](knowledge/architecture/agent-orchestration-patterns.yaml:162) contradicts indiscriminate inclusion, and the current data does not establish the unique contribution of large rosters. Its numerical table is a heuristic, not a demonstrated optimum.
3. **Failure modes:** Proposal: equating small diffs with low risk, replacing necessary specialists with an overloaded generalist, or enforcing five reviewers as a hard ceiling. Status quo: overlapping concerns, conflicting fixes, consolidation overload, and multiplying unnecessary dispatches across rounds.
4. **Exact rule wording:** “Select the smallest independent reviewer roster covering the change’s concrete risks, and state each reviewer’s distinct contribution. Use AOP5’s sizes as starting points, allowing documented exceptions for required specialist coverage. Retain applicable security, data-integrity, accessibility, and contract expertise regardless of diff length. Replace blanket anti-trimming rules and unconditional assignments with explicit coverage triggers; reassess coverage when actual implementation differs from the plan.”
5. **Evidence:** Repeated unique major findings from reviewers the proposed policy excludes would justify broader defaults. First map existing first-round findings to proposed coverage, deduplicate and validate them, then occasionally shadow omitted specialists.

**What matters more**

- **Repair severity and disposition first.** [Finding classification](process/finding-classification.md:79) calls scope/file changes “critical”; [code review](skills/sdlc-review-code/SKILL.md:141) uses impact and likelihood. Separate scope change from defect severity. Severity must also remain visible for unresolved investigations. Explicitly reconcile minor acknowledgment with [the prohibition on unilateral FIX acceptance](process/manager-rule.md:77).
- **Make triage shared and durable.** Use stable finding IDs, duplicate links, evidence-backed rejection, and recorded acknowledgments. Code review already has deduplication; the central loop should inherit it. Reconsider [whole-file scope qualification](process/finding-classification.md:47), which can turn a small change into unrelated cleanup.
- **Enforce budgets outside prompts.** The runner needs timeouts and finite dispatch/usage limits covering verification repairs, investigations, external review, and retries. Lite should reduce ceremony and ordinary roster size, while retaining the same blocker standard and risk escalation.

**Staging:** Land consistent triage, termination, and Q2 together; then pilot Q4, Q1, and Q3 separately so changes in quality and usage remain attributable.

## 4. Codex (GPT-6-Astra, ultra): Q4b

1. **Verdict — agree with modification.** Lite should normally receive a smaller, risk-based review roster and a bounded loop. Treat roster sizes as defaults with justified exceptions, not hard ceilings that exclude necessary expertise.

2. **Reasoning.** The owner’s strongest argument is that independent lenses catch interactions the planner missed; lacking a spec can increase ambiguity. The [tier table](CLAUDE-SDLC.md:35) defines lite by its planning needs, not by low defect risk. Nevertheless, breadth should mean coverage of distinct risks, not automatic headcount; [AOP5](knowledge/architecture/agent-orchestration-patterns.yaml:162) supports that distinction.

   The correction overstates current uniformity: [lite plan review](skills/sdlc-lite-plan/SKILL.md:310) already permits acknowledged minors and conditionally triggers re-review. [Lite execution](skills/sdlc-lite-execute/SKILL.md:288) requires zero findings and full-roster re-review after fixes. Extending the planning exit principle to execution is reasonable.

3. **Failure modes.** The proposal can miss cross-domain regressions, encourage severity downgrading, or let “lite” disguise risky work. The status quo consumes usage and time on repeated context loading and minor-finding churn, without guaranteeing termination. Neither roster breadth nor the supplied finding counts establish unique defect-detection value.

   Also, [classification rules](process/finding-classification.md:17) assign severity only to FIX findings: unresolved investigations and decisions must not disappear through a severity-only exit test.

4. **Exact rule wording.**

   > For lite plan and code review, default to two or three independent reviewers covering general correctness and the relevant domains; record each reviewer’s distinct contribution, make architect participation risk-triggered, and expand when coverage requires it. Preserve applicable verification gates, and permit completion only when critical/major defects and unresolved blocking investigations or decisions are cleared, with remaining minor findings explicitly recorded as accepted under the minor-acceptance policy. After code fixes, re-review with the raising reviewers and affected-domain reviewers, rerun applicable verification, and restore the full roster plus newly relevant specialists when changes introduce new files, domains, or behavior beyond the finding’s scope. Allow at most three review rounds per checkpoint, including rounds caused by external findings, within a preset run-wide dispatch/time budget; exhaustion with unresolved work parks the run as needing human attention, preserves findings, and blocks automatic completion.

   The minor-acceptance policy must explicitly reconcile the existing prohibition on unilateral FIX closure.

5. **Evidence that would change my mind.** Repeated, unique, confirmed major defects caught by omitted lenses would justify broader defaults. Cheaply audit a small sample of frozen lite diffs with an additional independent lens; track missed defects, duplicates, usage, and elapsed time. The supplied measurements are not tier-stratified.

**Q1–Q3 for lite:** No fundamental change: favor scoped re-review with expansion triggers; a nonblocking-minor exit with a hard termination boundary; and conditional reuse of read-only reviewers. Reuse must preserve separation from implementation/fixing and include regression review beyond checking the original finding. Lite alone warrants no weaker independence standard.

## 5. Fable: Q1–Q4b

I have everything needed; nothing further depends on another read. One finding from that last check matters for Q2: the framework has no unattended-run handling anywhere except a note in `knowledge/architecture/model-tier-strategy.yaml:329` that only the mechanical review-fix loop could ever run headless. The hooks that exist are CP-11/CP-11b parking and the `labels.conditional` block in `process/github-checkpoints.md`.

### Ruling on the review-fix loop changes

Files read: `process/review-fix-loop.md`, `finding-classification.md`, `manager-rule.md`, `external-review-gate.md`, `debate-protocol.md`, `github-checkpoints.md`, `agent-selection.yaml`; `skills/sdlc-execute`, `sdlc-lite-execute`, `sdlc-review-code`, `sdlc-plan`, `sdlc-lite-plan`; AOP5, MTS4; `CLAUDE-SDLC.md` tier table; changelog 2026-04-14/04-26/05-12.

**One finding that governs everything below:** the status quo has no termination guarantee. The 3-strike rule (`review-fix-loop.md:179`) fires only on the *same category*; a loop that surfaces a different minor each round never trips it, and the "zero means zero" bar (:121) plus reviewers who report findings 60–75% of the time in every round is a recipe for round 23. The exit bar, not roster scope, is the first-order cost driver.

#### Q1. Re-review scope

**Verdict:** agree with modification.

**Reasoning.** The owner's concern is valid and the brief's own "not established" list admits nobody has measured it. But the proposal's unit is wrong: `sdlc-review-code:77` says reviewers divide by *concern*, not by file, and forbids excluding an agent because another "covers it." "Reviewers whose domains own the touched files" cannot be computed from the lens model. The trigger must also be mechanical: plan review already forbids reasoning about whether a revision "changed the approach" (`sdlc-plan`), and execution runs on Sonnet/medium (`CLAUDE-SDLC.md:259`). The mechanical inputs available are the severity of fixes applied and the touched-file set; the always-on pair (code-reviewer + software-architect, `agent-selection.yaml:325`) is a regression net already on every roster.

| Proposal fails when | Status quo fails when |
|---|---|
| A minor fix silently changes a contract another lens would catch; orchestrator misjudges "beyond scope" | Roster × rounds multiplies: 7 reviewers × 10 rounds for findings that are 1px spacing; headless burns limits unobserved |

**Rule (`review-fix-loop.md` Step D):** "After a fix round, re-dispatch the full roster if any applied fix was major or critical, or if the fixers' reported touched-file set extends beyond the files named in the findings. Otherwise re-dispatch the raising reviewers plus code-reviewer and software-architect, scoped to the fix diff. This test is mechanical: read the Severity column and compare file sets; do not reason about relevance."

**Evidence:** in 20 full-roster re-review rounds, count major+ findings raised by reviewers who neither raised a finding the prior round nor are the always-on pair. Above ~10% of rounds, keep full roster. The classified transcripts already carry per-agent, per-round findings.

#### Q2. Exit bar and round cap

**Verdict:** agree, with two prerequisites; add a cap.

**Reasoning.** As written the proposal is blocked by two existing rules. (1) The execution loop has no severity definition: `finding-classification.md:81-85` is planning-shaped ("adds or removes files"), and the impact×likelihood calibration lives only in `sdlc-review-code:143-153`. A severity-keyed exit bar without it invites inflation (reviewers mark major to force fixes) and deflation (orchestrator marks minor to exit). (2) `manager-rule.md` § No Unilateral Finding Demotion forbids closing FIX findings at any severity without CD; "record as acknowledged" needs the plan-review hook ("acknowledged — document the decision") extended to execution, with visibility, not closure.

| Proposal fails when | Status quo fails when |
|---|---|
| Severity gaming; minors accrete invisibly | No termination; "verify/confirm" rounds ($2.5k) outside the written loop; unattended runs hang on `AskUserQuestion` nobody answers |

**Rule (`review-fix-loop.md` Step B/D; `finding-classification.md`):** "Import the review-code calibration and dedup tables; execution severity is impact × likelihood. The loop exits when no critical or major FIX findings remain. Remaining minors get one batched fix pass re-reviewed by the raisers plus code-reviewer; any still open are listed in the result doc's Open Minor Findings table, not closed. Round cap: after three review rounds, stop. Attended: escalate via `AskUserQuestion` with the open-findings table. Unattended: write the result doc, open the PR as draft with the table in its body, apply the project's configured conditional label (e.g. `review-capped`), park via CP-11/CP-11b. Never merge at the cap. Headless runs also carry a per-run dispatch and wall-clock budget in the checkpoints config block, with the same stop behavior."

**Evidence:** for 20 post-change loops, tag any later defect (CD iteration, external gate, bug) that traces to an acknowledged minor. Above ~1 in 10 deliverables, tighten the bar.

#### Q3. Reviewer reuse

**Verdict:** disagree, with one narrow allowance.

**Reasoning.** The brief overstates the history: team-review-fix was removed as "underused" (changelog 2026-05-12), not failed. The real evidence is elsewhere. Debate-protocol's Retraction Discipline exists because reviewers judging from memory instead of re-reading at HEAD is a known failure; a resumed reviewer is that failure by construction. Economically it inverts: contexts grow 43k→150k, so a resumed reviewer gets *more* expensive per round and hits compaction, which drops the knowledge files reuse was meant to preserve. Q1 and Q2 remove most of the rounds reuse would save.

| Proposal fails when | Status quo fails when |
|---|---|
| Reviewer verifies its own finding rather than the artifact; >1h gaps pay 2× cache writes | Each round re-reads knowledge files cold |

**Rule (`review-fix-loop.md:87`):** "Every review round uses fresh subagents. A reviewer may be resumed only to verify that a single minor finding it raised is resolved, within the same session; that verification is not a review round. Re-review dispatches include the fix diff and the prior findings table, and state that a clean report is an expected outcome."

**Evidence:** on 10 deliverables, run resumed and fresh reviewers on the same round-2 delta; compare regressions caught.

#### Q4. First-round roster

**Verdict:** agree with modification.

**Reasoning.** "A 2-minute review that finds nothing costs less than a missed issue" (`sdlc-plan:172`) is contradicted by the data: reviewers find something 60–75% of the time, so the marginal reviewer costs dispatch × rounds *plus* the fix and re-review it induces. Median 7, p90 12, max 15 against AOP5's "beyond 5, split." Separate lenses (free prompt content; the :367 red flag is about lenses and stands) from agents (not free). Keep breadth; cap it.

| Proposal fails when | Status quo fails when |
|---|---|
| Cross-layer bug missed by a 3-agent roster ("features rarely affect one layer") | Duplicated findings, overlapping fixes, consolidation loss (AOP5 rationale) |

**Rule (`sdlc-plan`/`sdlc-lite-plan` Selection Rule, `agent-selection.yaml`):** "The roster is the always-on pair plus one reviewer per domain whose files or concerns the plan touches. Beyond five, each additional agent needs a one-sentence statement of what it uniquely contributes (AOP5). High-risk domains (MTS4) always get their specialist. 'When in doubt, include' applies to domain coverage, not headcount."

**Evidence:** apply review-code's dedup table to 20 first-round checkpoints; if reviewers beyond the fifth contribute unique major+ findings in >20% of checkpoints, keep the large roster.

#### Q4b. Lighter review for the lite tier

**Verdict:** disagree with a tier-specific lighter loop; the tier should get lighter via Q1/Q2/Q4 applied uniformly.

**Reasoning.** The owner's instinct is right for a reason the proposal misses: lite drops the spec, so execution review in lite is the *only* contract check, not a redundant one. The axis that should drive review effort is risk and change size, which the framework already has (MTS4, AOP5), not tier, which is chosen by artifact need (`CLAUDE-SDLC.md:41`). A lighter lite loop creates a review-dodging incentive in tier selection that nothing defends against. Lite's 4-phase cap and smaller file set already yield smaller rosters under AOP5 and fewer rounds under a severity exit bar; that is where its lightness should come from.

| Proposal fails when | Status quo fails when |
|---|---|
| High-risk work classified lite to escape review; no spec to backstop | 22–45 dispatches per lite deliverable pushes CD toward direct dispatch, which has no plan artifact at all |

**Rule (`CLAUDE-SDLC.md` tier table; both lite skills):** "Review effort scales with change size and risk, not tier. Lite and full run the same loop, exit bar, re-review scoping, and cap. Lite-tier work in an MTS4 high-risk domain is reviewed at full strength."

**Evidence:** after Q1/Q2/Q4 land, if lite dispatch counts remain within 20% of full for comparable file counts, revisit a lite-specific cap.

**Q1–Q3 for lite:** unchanged. The cap and scoped re-review are the lite tier's win; no separate rule.

#### What the questions missed

1. **No dedup step in the execution loop.** review-code has one (:130-140); `review-fix-loop.md` has none, so overlapping minors become overlapping fix dispatches. Prerequisite for Q2.
2. **The $2.5k verify/confirm bucket** is outside the written loop. Make the fixer's return contract report touched files and tests run; that kills standalone verify dispatches and supplies Q1's mechanical file-set input.
3. **Reviewer prompt framing.** A reviewer asked for findings produces findings. Scope re-review prompts to the delta and say a clean report is expected.
4. **Headless budget** independent of round count, since rounds vary 3–15 agents.

**Staging:** land calibration import, dedup, exit bar, cap, and unattended parking together (coupled; minor bump). Instrument for ~20 loops, then land Q1 and Q4, which is where the owner's regression and breadth concerns and the "not established" items sit. Do not land Q3.
