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
