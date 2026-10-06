---
type: handoff
slug: review-loop-unification
created: 2026-10-06
status: pending
trigger: deferred-work
recommended_next_skill: direct-dispatch
source_session_summary: "A software-factory and cost evaluation session measured 30 days of Claude Code usage. Subagents were two-thirds of it and review loops the largest single share. Fable and Codex (GPT-6-Astra) were consulted on changes to the review loops, and CD decided the changes below. The edits are deferred to a fresh session."
active_deliverable: null
related_files:
  - docs/current_work/ideas/review-loop-unification_consult-record.md
  - process/review-fix-loop.md
  - process/finding-classification.md
  - process/manager-rule.md
  - process/external-review-gate.md
  - process/agent-selection.yaml
  - process/README.md
  - skills/sdlc-execute/SKILL.md
  - skills/sdlc-lite-execute/SKILL.md
  - skills/sdlc-review-code/SKILL.md
  - skills/sdlc-plan/SKILL.md
  - skills/sdlc-lite-plan/SKILL.md
  - skills/sdlc-create-reference-doc/SKILL.md
  - CLAUDE-SDLC.md
  - knowledge/architecture/agent-orchestration-patterns.yaml
  - knowledge/architecture/model-tier-strategy.yaml
  - agents/sdlc-reviewer.md
  - .claude/skills/ccsdlc-audit/references/compliance-methodology.md
  - process/project-section-markers.md
---

# Handoff: Unify and bound the framework's review loops

## Why this is a handoff
This session started as an evaluation of "software factory" tooling: running agents from GitHub issues. Measuring the cost of the work showed that the framework's review loops are the biggest driver of subagent usage, and that their design keeps them from converging. CD reviewed the evidence, had Fable and Codex (GPT-6-Astra at `ultra` effort) rule on the proposed changes independently, and made the decisions recorded below. CD asked for a fresh session to make the edits.

**This repo uses direct dispatch, not `sdlc-plan`.** Follow `CLAUDE.md`:
- Update `process/sdlc_changelog.md` in the same step as each change.
- Run the mandatory consistency checks before presenting the summary.
- Use the `sdlc-reviewer` quality gate on every changed skill.

The line numbers below were correct on 2026-10-06. Re-read each file before editing.

## Decisions (CD-approved)

CD's instruction on scope was that review-code and every review loop, planning or execution, "should all pull from the same place **if possible**", and that if doing so "would pose a problem, I'd rather just keep it the way that it is right now." That safety condition governs D7, D8, and D9 together, not only the mirroring. If any part cannot be unified without the regressions listed under Guardrails, leave that part as it is and tell CD.

| # | Decision | Rule to implement |
|---|---|---|
| D1 | **Re-review scope is mechanical (Fable's rule).** Judgment-based scoping (Codex's version) was rejected because execution reviews run on Sonnet. | After a fix round, **re-run the verification gate** (tests, type checks, lint, configured static analysis). Then re-dispatch the **full roster** if (a) any applied fix was `critical` or `major`, or (b) the fix's touched files (`git diff --name-only` against the pre-fix state) go beyond the files named in the findings. Otherwise, re-dispatch **only the reviewers who raised findings, plus code-reviewer and software-architect**, scoped to the fix diff. "This test is mechanical: read the Severity column and compare file sets; do not reason about relevance." Keep the existing rule that a fix touching a new domain adds that domain's agent. |
| D2 | **Exit bar: no critical or major findings remain.** This replaces "zero findings, minor ones included." | The loop exits when no `critical` or `major` FIX findings remain **and** no INVESTIGATE or DECIDE findings are unresolved (those must still be resolved, as today). Each round fixes `critical` and `major` findings only. Minors accumulate and get **one batched fix pass once no critical or major findings remain**, re-reviewed under D1 (CD chose this order). Minors still open after that go into an **Open Minor Findings** table: in the result doc, the plan, the final report, or the commit for reference docs. They are never silently closed. |
| D3 | **Three-round cap.** | At most 3 review rounds per loop: the first round plus up to 2 re-reviews. **Every round counts**, including the re-review after the minor batch pass and rounds started when external-gate findings re-open the loop (CD-confirmed). In an interactive session, if `critical` or `major` findings are still open at the cap, stop, escalate to CD via `AskUserQuestion` with the open-findings table, and never claim the loop is clean. If only minors remain at the cap, exit with the Open Minor Findings table. The cap **replaces the 3-strike rule**. Keep "FIX fails twice → reclassify" in finding-classification.md. |
| D4 | **No reviewer reuse.** CD weighed Codex's conditional reuse and decided against it: after D1 and D3 there is little left to save, it adds orchestrator bookkeeping, and the main benefit is available another way. | Every review round uses **fresh** subagents. Re-review prompts include the previous round's findings table and the fix diff. They require reading the current code (not memory) and looking for regressions beyond the prior findings. They state that a clean report is an expected, acceptable outcome. |
| D5 | **Roster: "When in doubt, include" covers domains, not headcount.** | The roster is code-reviewer and software-architect (always dispatched) plus one reviewer for each domain whose files or concerns the change touches. Beyond five reviewers, each extra agent needs a one-sentence statement of what it uniquely adds (AOP5). High-risk domains (MTS4) always get their specialist regardless of diff size. Review **lenses** are prompt content and are not trimmed for small diffs. |
| D6 | **No lighter lite tier.** | Lite and full tiers run the identical loop. Do **not** add lite-specific review rules. Lite work naturally gets smaller rosters under D5 and fewer rounds under D2 and D3. |
| D7 | **One severity scale and one deduplication step, used by every review loop.** | Adopt `sdlc-review-code`'s impact × likelihood severity scale and its calibration rule, plus its deduplication table, as the single definitions. They live in `process/finding-classification.md` and apply to code, plan, and reference-doc reviews. |
| D8 | **Single source, without the skip regression.** All review loops pull from the same place, but each skill keeps its inline critical steps. | Definitions live once in process docs. Each skill keeps a short block of the critical steps, **identical word for word** to a source section in `review-fix-loop.md`. A mechanical check fails if any copy drifts. **Never reduce a skill to a bare "read and follow [file]" pointer.** That is the failure recorded in the changelog entry "2026-05-19: Inline Critical Guardrails Lost in Skill Consolidation", where `sdlc-review-code` skipped the loop and falsely claimed it was clean. If this cannot be done safely, CD prefers keeping the current structure. |
| D9 | **Plan review re-reviews exactly when it does today.** | Moving to the D7 severity scale must not change when plan re-review fires. Today's trigger (1), "any FIX finding has Severity = `critical`", really means "the fix changes the approach". Replace it with a separate **scope-change marker** on FIX findings: the fix changes the approach, adds or removes files, or changes a phase or agent assignment. Triggers (2) and (3) are unchanged. **D1's narrow re-review does not apply to plan review.** When plan re-review fires, it always dispatches the full step-1 roster, as today. When it doesn't fire, there is no re-review, as today. The plan loop adopts D2's exit bar (it already uses it), D3's cap, D4, D5, and D7. |
| D10 | **Reference-doc review uses the shared bar as-is.** CD accepted a slightly looser bar. | The CRITICAL/HIGH/MEDIUM/LOW scale goes. Reference-doc findings use critical/major/minor, and the loop exits under D2. Some of today's MEDIUM findings become minor and are listed in the commit instead of fixed. |
| D11 | **Reference-doc standing reviewers are the skill's own.** | In D1's narrow re-review for reference docs, use whichever reviewers `sdlc-create-reference-doc` always dispatches. If it has none, use the author's reviewer plus code-reviewer. |
| D12 | **Scope-change marker is a table column.** | A `Scope change` yes/no column in the Classification Table, in planning context only. Plan re-review trigger (1) reads this column. |
| D13 | **Two mirrored blocks.** | One code-review block (execute, lite-execute, review-code, create-reference-doc) and one plan-review block (plan, lite-plan). Other context differences go in the variations table. |
| D14 | **Plan review does no re-review for fixes that don't change scope**, as today. | CD confirmed keeping today's behavior. Plan re-review triggers are the same "fix spread" cases where D1 would call the full roster anyway. Applying D1 unchanged would *add* full-roster re-reviews after every major plan fix. No narrow raiser check for plans. |

## Change list by file

### 1. `process/finding-classification.md`: owns severity, scope marker, deduplication, and open minors
- **Severity.** Replace § "Severity Levels (FIX Findings Only)" (around :81-85, currently planning-shaped: critical = "changes the approach, adds or removes files…") with the impact × likelihood table and calibration rule from `skills/sdlc-review-code/SKILL.md` around :141-153:

  | Severity | Meaning |
  |---|---|
  | critical | Certain or very likely data loss, security breach, or complete failure |
  | major | Significant functionality impact, likely to manifest |
  | minor | Partial impact, a workaround exists, or cosmetic |

  Downgrade inflated severities and record why. State that the scale applies to every review context. Add a short note on how each context reads "impact": for a plan, the impact on the implementation if executed as written; for a reference doc, the impact on a reader. Reference docs use the shared bar as-is (see D10).
- **Scope-change marker (D9).** A new subsection defining the marker for planning-context FIX findings. It is a **`Scope change` yes/no column in the Classification Table, in planning context only** (D12).
- **Deduplication.** A new section holding the four-row merge table moved from `sdlc-review-code` Step 4 (around :129-138): same `file:line` and same issue; same `file:line` with different issues; same issue at different locations; conflicting fixes. It applies **before classification** in every loop.
- **Open Minor Findings.** A new section (D2) with the table shape, where it lives in each context, and the rule that CD closes entries, not the orchestrator.
- **Keep:** "FIX Failure Escalation" (fails twice → INVESTIGATE or PLAN) and "Low-Severity In-Scope Findings (Planning Context)".

### 2. `process/review-fix-loop.md`: owns the loop for every review context
- **Step A** (:76-80): replace "do not remove agents… dispatch every single one" with the D5 roster rule for the first round. Re-review rosters come from D1.
- **Context-separation rule** (:87): keep, and add D4 (fresh subagents every round, plus what re-review prompts carry).
- **Step B exit** (:119-123): replace "Zero means zero" with the D2 exit bar, including the unresolved INVESTIGATE/DECIDE guard.
- **Step C:** dedup first (point to the finding-classification section), then calibrate, then classify. Then fix critical and major; minors follow D2's batched pass.
- **Step D** (:140-144): replace "dispatch ALL agents — not just the ones who found issues" with D1, including the verification-gate re-run.
- **Step E** (external gate, :146-171): external findings are deduplicated and calibrated with internal ones. An external FIX that re-opens the internal loop counts toward the D3 cap.
- **§ 3-Strike Rule** (:177): replace with the D3 round cap and cap behavior.
- **§ Skill-Specific Variations** (:205+): turn this into the per-context table:
  - code review (execute, lite-execute, review-code, direct-dispatch "review before committing")
  - plan review (plan, lite-plan: D9 triggers, no verification gate)
  - reference-doc review (no build gate, its own reviewer set)
- **Remove the stale `sdlc-review-fix` row** (:211). That skill no longer exists.
- **Add the mirror source sections (D8, D13).** Write **two** compact critical-steps blocks that skills copy verbatim: a **code-review block**, used by execute, lite-execute, review-code, and create-reference-doc, and a **plan-review block**, used by plan and lite-plan. Everything else that differs by context goes in the variations table.

### 3. Skills: swap their own copies of the loop for the mirrored block
- **`skills/sdlc-execute/SKILL.md`:**
  - Replace the inlined loop steps (:355-372) with the mirrored code-review block.
  - Update "Review loop complete — all agents clean" and "repeats until every agent reports clean" to the D2 wording.
  - Keep the Triage output format, the plan contract briefing, and Step E.
  - Red flags: change :601 ("Re-review is overkill" → "ALL means ALL") to "Re-review is mandatory; its roster comes from the mechanical trigger, never judgment."
  - Add red flags for: downgrading severity to exit the loop; claiming clean at the cap; resuming a reviewer to save tokens; skipping the verification re-run after fixes.
- **`skills/sdlc-lite-execute/SKILL.md`:** the same changes at :288-300 and the red flag at :509 ("Skip re-review, the fixes were small"). **No lite-specific rules (D6).**
- **`skills/sdlc-review-code/SKILL.md`:**
  - Step 4 (around :127-153): deduplication and severity calibration move to finding-classification.md. Leave a short inline step that names both and keeps the critical behavior (merge same-location duplicates and keep the highest severity; calibrate before labelling). This must stay inline: it is the kind of directive that gets skipped as a pointer (D8).
  - Keep the Report Framing Discipline (it is specific to review-code).
  - Step 5b (:236-250): replace with the mirrored code-review block. Keep Step 5a's manager-rule guardrails inline.
  - Red flags :367 ("The diff is small, skip some lenses") and :372 ("Skip Tier 2…") **stay**. Lenses are prompt content, and a Tier-2 agent whose domain the diff touches stays under D5. Check that their wording does not contradict D5.
- **`skills/sdlc-plan/SKILL.md`:**
  - Selection rule (:170-182): change "When in doubt, include" (:172) to D5's coverage-not-headcount wording, and wire AOP5 in as rule rather than "consult".
  - Plan review (:560-595): adopt D7 severity and dedup. Replace re-review trigger (1) at :591 with the D9 scope-change marker. Keep the stopping condition at :595, now pointing at D2's Open Minor Findings. Add the D3 cap and D4.
- **`skills/sdlc-lite-plan/SKILL.md`:** the same changes at :82 (selection), :126 (AOP5), :295 (classify), :310 (trigger 1), :312 (re-review dispatch), and :314 (stopping condition).
- **`skills/sdlc-create-reference-doc/SKILL.md` § 5 Fix Loop** (:152-162):
  - Replace the CRITICAL/HIGH/MEDIUM/LOW scale and its exit condition at :161 with D7 and D2.
  - Apply D1, D3, and D4. In D1's narrow re-review, the skill's **own standing reviewers** replace code-reviewer and software-architect: whichever reviewers it always dispatches, or, if it has none, the author's reviewer plus code-reviewer (D11).
  - Use the **shared severity bar as-is** (D10). Some of today's MEDIUM findings become minor and go to the Open Minor Findings list, which for reference docs is recorded in the commit message, as LOW deferrals are today.

### 4. Other docs
- **`process/manager-rule.md` § No Unilateral Finding Demotion** (:77): add that listing minor FIX findings as open at loop exit, visible to CD, is permitted and is not demotion. Closing them still requires CD.
- **`process/external-review-gate.md`:**
  - Point its `critical|major|minor` vocabulary (:123, :293) at the finding-classification definitions.
  - Say external findings are deduplicated and calibrated alongside internal ones.
  - Reconcile its 2-round external cap with the D3 loop cap.
- **`CLAUDE-SDLC.md` § Direct Dispatch Rules, "Review before committing"** (:76): replace "dispatch ALL relevant agents… re-review until clean" with a pointer to the loop plus the one-line D1, D2, and D3 summary. CLAUDE-SDLC.md is merged into target projects' CLAUDE.md, so keep it self-contained.
- **`process/README.md`:** update the `finding-classification.md` row to reflect that it now owns severity, deduplication, and open minors.
- **`knowledge/architecture/agent-orchestration-patterns.yaml` AOP5** (:162-199): no rule change needed. Optionally note that review rosters apply it through D5.

### 5. Drift check for the mirrored blocks (D8)
- Define a marker pair for the mirrored blocks.
  - Check `process/project-section-markers.md` and how `sdlc-migrate` and `sdlc-initialize` parse `PROJECT-SECTION` and `BUNDLE-SECTION` markers, so the new marker cannot collide with them or be mangled during migration.
  - The marker should name its source section, e.g. `review-fix-loop.md#code-review-mechanics`.
- **`.claude/skills/ccsdlc-audit/references/compliance-methodology.md` Dimension 10 (Cross-Skill DRY, :271):**
  - Exempt marked blocks from "extract it" recommendations.
  - Add a check that each marked block matches its source section exactly; any difference is a finding.
- **`agents/sdlc-reviewer.md` § Cross-skill DRY (:115):** the same exemption and exact-match check. This file is hardlinked to `.claude/agents/sdlc-reviewer.md` (same inode), so edit one path only.

### 6. Bookkeeping
- **Changelog:** a `process/sdlc_changelog.md` entry written with the changes, not afterwards. It must:
  - Explain the origin (the data and the consult).
  - Reference the 2026-04-14, 2026-05-12, and 2026-05-19 entries.
  - List every file changed.
- **Manifest:** no new files are expected, so `skeleton/manifest.json` should not change. If a new file is added, list it. No rename, so no `contract_changes.yaml` entry is expected.
- **Neuroloom adapter:** confirm none of the changed wording is a phrasing-contract phrase. Grep `~/Projects/neuroloom/neuroloom-sdlc-plugin/references/pattern-mapping-rules.md` for "finding-classification", "review-fix-loop", and "severity". It is expected to be clean; if not, tag the changelog entry `[contract-change]`.
- **Version:** CD decides minor or patch at tag time. The mirror-block convention is arguably a new process convention, which would make it minor. Do not tag.

## Guardrails (regression safety)
- **Never leave a skill with only a pointer for loop steps** (D8, the 2026-05-19 lesson).
- **Plan re-review must fire in exactly today's cases** (D9). Check this by walking the three triggers before and after the change.
- **INVESTIGATE and DECIDE findings still block exit** under the new bar.
- **Do not add** reviewer reuse (D4), lite-specific review rules (D6), or unattended/headless behavior at the cap. Headless parking and per-run budgets belong to the future factory work; see "Raised but not decided".
- **Stale-phrase scan.** After the edits, grep `skills/`, `process/`, `agents/`, and `CLAUDE-SDLC.md` for each of the following. Only changelog hits should remain, unless a hit is deliberately kept and you can say why.
  - "Zero means zero"
  - "ALL means ALL"
  - "Dispatch ALL agents again"
  - "not just the ones who found issues"
  - "3-strike"
  - "until every agent reports clean"
  - "all agents clean"
  - "When in doubt, include"
  - "CRITICAL, HIGH, or MEDIUM"
  - "Severity = `critical`"
  - "sdlc-review-fix"

## Acceptance walkthrough (run this on paper before finishing)
1. **Round 1** has a roster of 6 under D5. Findings: 2 reviewers report the same `file:line` issue (dedup merges them into one major), 2 minors in different files, and 1 INVESTIGATE.
2. **The major is fixed**, touching only its own file. Verification re-runs. A major was fixed, so **round 2 is the full roster** (D1). Round 2 reports nothing critical or major, and the INVESTIGATE has been resolved.
3. **The two minors get one batched pass** touching only their two files. Verification re-runs. **Round 3 is only the raising reviewers plus code-reviewer and software-architect** (D1). One minor remains open, and the loop has reached the cap.
4. **Exit** with the Open Minor Findings table, since there are no critical or major findings.

**Variant:** if round 3 still had a major, stop at the cap and escalate to CD with the open-findings table. Never claim clean.

**Plan-review variant:** a FIX marked scope-change triggers re-review exactly as `Severity = critical` does today.

## Evidence (why these changes)

**Measured** from local Claude Code transcript token counts, 30 days to 2026-10-06, priced at API list rates. On the Max plan this translates to usage limits and waiting time, not dollars.
- Total spend was about $16.3k equivalent. Subagents were 67% (about $10.9k), and 95% of all cost was re-reading context.
- There were 4,775 subagents. A typical one started at about 43k tokens and grew to about 150k.

**Heuristic**, classified from dispatch descriptions:
- **Reviews dominate.** Review and re-review accounted for about 3,008 dispatches and about $5.1k, which is 47% of subagent cost.
- **Rosters are large.** Across 97 checkpoints, the median review checkpoint had 7 reviewers; one in ten had 12 or more, and the largest had 15.
- **Loops run long.** Rounds were labelled up to **23**. There were 469 dispatches in rounds 3–5, 224 in rounds 6–10, and 183 in round 11 or later.
- **Findings never stop.** In every round bucket, 60–75% of reviewers reported findings. The late-round reports sampled by hand were nearly all self-described minor.
- **Design arithmetic** (Explore mapping): a full deliverable prescribes about 24–46 subagent dispatches, and a lite one about 22–45, because lite has identical review rules.

**Root causes in the process** (verified against the files):
- The roster never shrinks: "do not remove agents" and "When in doubt, include".
- Every fix sends the whole roster back: "not just the ones who found issues".
- The exit bar is zero findings, minors included, with no round cap. The 3-strike rule only fires when the *same* finding repeats.
- Every round starts fresh reviewers, each reloading 9–15 knowledge files.
- AOP5 right-sizing is cited only by the plan skills.

**History:**
- 2026-04-14: review-fix accounted for 63% of token cost in an audit.
- 2026-05-12: team-review-fix was removed as underused.
- 2026-05-19: inline guardrails were restored after a pointer-only consolidation caused a skipped loop.

**Consult** (full text in `review-loop-unification_consult-record.md`):
- **Both reviewers agreed on:** the exit bar plus a 3-round cap; narrowed re-review; coverage-based rosters; and three prerequisites (one severity scale, deduplication, visible minors).
- **They split** on reviewer reuse and on a lighter lite tier. CD decided against both (D4, D6).
- **Re-review scoping:** CD picked Fable's mechanical version over Codex's judgment version (D1).

**Estimated effect:** roughly $1.5–2.5k of API-equivalent spend per month, mostly from rounds 2 and later. This is an estimate, not a measurement.

## Recommended next step
Open a fresh session in this repo and work by **direct dispatch** in this order:
1. `finding-classification.md` and the `manager-rule.md` line (§1, §4).
2. `review-fix-loop.md`, including the mirror source blocks (§2).
3. Mirror the blocks into the six skills and update red flags, plan triggers, and selection rules (§3).
4. `CLAUDE-SDLC.md`, `external-review-gate.md`, and `process/README.md` (§4).
5. The drift check in `ccsdlc-audit` and `sdlc-reviewer` (§5).
6. Run the acceptance walkthrough, the stale-phrase scan, the `sdlc-reviewer` quality gate on every changed skill, and the `CLAUDE.md` consistency checks.

Write the changelog entry alongside the edits, not at the end.

## Resolved questions (CD answered 2026-10-06, before the handoff)
All open questions are settled; the next session can start editing. The answers are folded into D2, D3, and D10-D14:
- **Reference-doc strictness:** use the shared bar as-is (D10). This was *not* the recommended default; CD accepted the looser bar.
- **Reference-doc standing reviewers:** the skill's own set (D11).
- **What counts toward the cap:** everything, including the minor-pass re-review and external-gate re-entry (D3).
- **Scope-change marker:** a table column, planning context only (D12).
- **Mirrored blocks:** two, code review and plan review (D13).
- **When minors get fixed:** batched once no critical or major findings remain (D2).
- **Plan review for fixes that don't change scope:** keep today's behavior, no re-review (D14).

## Raised but not decided (do NOT implement without CD)
- **Fixer return contract** (Fable): fixers report the files they touched and the tests they ran, to remove standalone "verify/confirm" dispatches (about $2.5k a month of "other"). D1's `git diff` input already covers the file part.
- **Stable finding IDs, duplicate links, and evidence-backed rejection across rounds** (Codex).
- **Reconsider whole-file scope qualification** in `finding-classification.md` (:47), which can turn a small change into unrelated cleanup (Codex).
- **Headless/unattended behavior:** parking at the cap (draft PR plus a `needs-human`/`review-capped` label through the github-provenance CP-11 hooks), and per-run dispatch and time budgets enforced by the runner. Both reviewers recommended these. They belong to the separate software-factory work, which does not exist yet.

## Out of scope (do NOT pursue)
- The software-factory build itself (GitHub Actions or a self-hosted runner, an issue-triage skill, headless mode). It was discussed this session but not started.
- Changes to execution-phase dispatches, planning spec/plan writers, or agent definitions.
- Session-length and context-handoff rules. Long sessions above 200k tokens were the largest cost driver in the main thread, but that is separate work.
