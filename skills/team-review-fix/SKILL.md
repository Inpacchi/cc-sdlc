---
name: sdlc-team-review-fix
description: >
  Unified team-powered review and fix lifecycle. Domain agents review any target (commit, diff,
  files, directory), debate findings organically with an architect mediator, then fix all findings
  using persistent teammates — no fresh agent spawning. Loops review-fix rounds until clean
  within one persistent team.
  Use when code changes need a deep team-powered review with persistent agents that debate and fix findings in-session.
  Triggers on "team review", "deep review", "review and fix with team", "/team-review-fix",
  "team review this commit", "team review these files".
  Do NOT use for quick reviews — use sdlc-review-code.
  Do NOT use without CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1.
---

# Team Review & Fix

Review any target with a persistent agent team, resolve conflicts through organic debate with an architect mediator, and fix all findings using the same team. No fresh agent spawning between phases. The team stays alive through all rounds and is cleaned up at the end.

**Cost:** 3-6x more tokens than `sdlc-review-code` + `sdlc-review-fix`. The team model earns its keep on ~30% of work (coordinated multi-file commits, cross-package contract-drift, mid-execution scope escalation). The other ~70% would be equally well served by subagent dispatch. Use the decision tree below.

### When to Use This vs Subagent Dispatch

Use `/team-review-fix` when **two or more** of these are true:

| Signal | Why it needs a team |
|--------|-------------------|
| **Partner-facing or production-critical** | Wrong fix direction is expensive; real-time reviewer validation prevents regressions landing |
| **Multiple package boundaries in scope** | Contract-drift findings (codec ↔ route ↔ schema ↔ docs) require holding multiple surfaces simultaneously — single-domain subagents miss these |
| **Coordinated multi-file commits needed** | The apiKey cluster pattern: 7 tasks landing as ONE commit while preserving security invariants. Subagents fragment this into separate commits with regression risk between them |
| **Cross-fixer file overlap expected** | Two fixers touching the same file need sequencing via `addBlockedBy`. Subagents collide silently |
| **Scope escalation likely** | Work that may surface PRE-DELIVERABLE-SPLIT findings or mid-execution DECIDE pivots that reshape downstream tasks |

Use `sdlc-review-code` + `sdlc-review-fix` (subagent dispatch) when:
- Bug-fix sweep with well-understood patterns
- Independent per-file changes (docs content, individual test creation, style fixes)
- Single-package work where findings don't cross domain boundaries
- Speed matters more than finding accuracy

**Evidence (3 sessions):** The team model caught contract-drift findings (12 of 25 critical/major in the 2026-04-26 session) that single-domain subagents would have missed. The apiKey coordinated commit and Grand Archive 3-way independent confirmation are the strongest examples. But ~70% of individual findings and fixes had no debate value and would have been cheaper as subagents.

**Argument:** `$ARGUMENTS` (optional — commit ref, file paths, directory, or description of what to review)

## Steps

### Step 0: Environment Gate

Check that agent teams are enabled:

```bash
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
```

If not set to `1`, tell the user and stop:

> Agent teams require the experimental feature flag. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in your environment and restart Claude Code.

### Step 1: Resolve Review Target

Parse the `$ARGUMENTS` to determine what to review:

| Argument | Target | How to Gather |
|----------|--------|---------------|
| No argument | Uncommitted changes | `git diff HEAD` (staged + unstaged) |
| Commit ref (e.g., `HEAD`, `abc1234`) | That commit | `git show {ref}` |
| Commit range (e.g., `abc..def`) | Range diff | `git diff {range}` |
| File path(s) | Those files in full | Read each file |
| Directory | All source files in directory | Read all non-binary, non-generated files |
| Description | User-described scope | Identify files from description, confirm with user |

Validate the target has reviewable content. If empty, tell the user and stop.

For uncommitted changes, also run `git status -s` to check for untracked files. Warn about untracked source files as in `sdlc-review-code`.

### Step 2: Select Teammates

Follow `[sdlc-root]/process/agent-selection.yaml` for dispatch rules:

1. Always add `code-reviewer`
2. Add Tier 1 agents based on file paths in the target
3. Read target content for Tier 2 triggers
4. Note WHY each Tier 2 agent is included or excluded

**Determine REVIEWER teammates** — domain agents who will review through their lenses.

**Fixers are NOT spawned yet.** Which fixers are needed depends on what the review finds. Spawning fixers upfront wastes tokens on idle teammates that may never be needed (e.g., if the review finds no issues, or findings cluster in one domain). Fixers are identified and spawned in Step 6a after the review converges.

**Validate each reviewer agent type has required tools:** Bash, Read, Grep minimum. If an agent definition restricts tools below this threshold, warn and either adjust or exclude with explanation. This prevents silent failures (audit: accessibility-auditor spawned as read-only, couldn't run git show, failed silently).

Output a dispatch checklist with cost estimate:

```
Team review-fix: {target description}
Files in scope: N

REVIEWERS:
- [ ] reviewer-code-reviewer (always)
- [ ] reviewer-frontend-developer (touches React components)
- [ ] reviewer-performance-engineer (new store selectors)

MEDIATOR:
- [ ] architect-software-architect (mediator + master list builder)

FIXERS: determined after review converges (Step 6a)

Not dispatching:
- software-architect (as reviewer) -- follows existing pattern, no new abstractions
- ui-ux-designer -- logic-only changes, no visual modifications

Estimated cost: ~{N} review teammates x target size = {estimate} tokens
```

### Step 3: Create Team, Spawn Reviewers + Architect

Create the agent team. The main session is the team lead — it manages lifecycle mechanics only (create, spawn, message routing, shutdown, cleanup). The lead does NOT make review judgments, does NOT classify findings, does NOT assign fixes. That is the architect's job.

**Spawn order matters:**

1. **Architect FIRST** — `architect-software-architect`. It needs to be listening before reviewers start sending findings. The architect receives:
   - Target content (diff, files, or commit)
   - The architect prompt template from `[sdlc-root]/process/debate-protocol.md`
   - Instruction to build the master findings list progressively as findings arrive
   - Reference to `[sdlc-root]/process/team-communication-protocol.md` for message format
   - Reference to `[sdlc-root]/process/finding-classification.md` for classification rules (no PLAN — use PRE-DELIVERABLE-SPLIT for scope escalation)

2. **All REVIEWERS in parallel** — each reviewer receives:
   - Target content
   - Review lenses from `[sdlc-root]/process/review-lenses.md` (all lenses apply)
   - Relevant knowledge context — consult `[sdlc-root]/knowledge/agent-context-map.yaml` for their role's mapped files and include them
   - Instructions to send findings as FINDING messages (per `team-communication-protocol.md`) to the architect AND domain-relevant reviewers
   - The message envelope format
   - **Explicit routing instruction** (mandatory — audit 2026-04-17 showed 4/7 reviewers emitted findings as plain text instead):
     ```
     ROUTING (critical): Send each finding via the SendMessage tool with
     to: "architect-software-architect". Plain-text output from your turns is
     ONLY visible to the team-lead, NOT to the architect. If you emit a finding
     as plain text, the architect will not create a task for it and it will be
     lost. For every FINDING you produce, call SendMessage exactly once with:
       to: "architect-software-architect"
       summary: <short subject>
       message: <envelope body with from/to/file/line/severity/category/body>
     If you have no findings in your domain, SendMessage "standing by, no findings"
     to the architect. Do not go idle silently.
     ```
   - **Read-only constraint** (mandatory — audit 2026-04-17 caught 2 reviewers editing files):
     ```
     CONSTRAINT: You are READ-ONLY during Phase 1. Do NOT call Edit, Write,
     NotebookEdit, or any mutation tool on any repo file. Fixes happen in Phase 2
     via dedicated fixer teammates spawned after review converges. If you spot a
     trivial fix, resist — report it as a FINDING and let a fixer own it.
     Violations will be reverted and re-queued for Phase 2.
     ```
   - **Retraction discipline** (mandatory — audit 2026-04-17 caught multiple stale-view retractions):
     ```
     RETRACTION DISCIPLINE: Before retracting a finding you previously submitted,
     re-read the target file at CURRENT HEAD (not from memory or cached context).
     The file state may differ from your initial read. If the finding no longer
     applies at HEAD, state explicitly "Re-verified at HEAD; finding obsolete".
     If the finding still applies, submit CHALLENGE with evidence instead of
     retracting.
     ```

**Fixers are NOT spawned here.** They are spawned on-demand in Step 6a after the review converges and FIX findings are identified. This avoids wasting tokens on idle teammates when no fixes are needed or when findings cluster in fewer domains than anticipated.

Name all teammates with role prefix: `architect-{name}`, `reviewer-{name}`, `fixer-{name}`.

### Step 4: PHASE 1 — Review + Organic Debate

All reviewers work in parallel, reviewing the target through their domain lenses.

When a reviewer finds an issue:
1. Send FINDING message to the architect AND reviewers whose domain overlaps (direct messages, not broadcast to all)
2. Other reviewers who receive the finding can:
   - **CHALLENGE** with counter-evidence (direct message to finder + architect)
   - **Agree** — confirms severity, increases confidence
   - **Ignore** — outside their domain, no response required
3. The architect receives every finding and every challenge/agreement
4. The architect creates a task for the finding via TaskCreate with structured metadata:
   - If no challenges: status "confirmed", task pending
   - If challenged: architect reads both positions, breaks the tie immediately
   - If multiple reviewers independently find the same thing: merge, cite all, high confidence
5. **Architect ACKs each finding** — after TaskCreate, the architect sends an ACK message back to the finder containing the task ID. This gives reviewers confirmation their finding landed and gives the team-lead a way to detect routing failures.

Positive findings (things done well) are tagged and preserved but excluded from the fix pipeline.

**Fast-fail routing check (team-lead enforcement):** Before the architect signals "review complete", the team-lead verifies each reviewer has either:
- At least one ACK'd finding from the architect, OR
- An explicit "standing by, no findings" message to the architect

If a reviewer went idle without any architect interaction, the team-lead prods that reviewer to re-emit findings via SendMessage. Do NOT allow the architect to signal convergence with silent reviewers — audit 2026-04-17 showed this caused premature convergence with ~40% of findings missing.

**Convergence:** The architect signals "review complete" when:
- All reviewers have gone idle (TeammateIdle notifications)
- Every reviewer has at least one architect interaction (ACK'd finding or "no findings" message)
- All outstanding challenges have been resolved
- The master findings list in the shared task list is stable

The architect classifies each finding: **FIX / INVESTIGATE / DECIDE / PRE-EXISTING / PRE-DELIVERABLE-SPLIT** (per `[sdlc-root]/process/finding-classification.md` — no PLAN classification in this skill).

Present DECIDE items to user via AskUserQuestion. Block until answered.

### Step 5: Architect Presents Findings Summary

The lead requests the findings summary from the architect and outputs:

```markdown
## Team Review: {target description}

{N} files reviewed | {N} reviewers | {N} findings

### Findings

| # | Task ID | Finding | Reviewer(s) | Severity | Category | Classification |
|---|---------|---------|-------------|----------|----------|----------------|
| 1 | 3 | specific finding | reviewer-code-reviewer | major | correctness | FIX |
| 2 | 5 | ... | reviewer-security-engineer, reviewer-code-reviewer | critical | security | FIX |

### Debate Summary

- {N} findings total, {N} challenged, {N} resolved by architect, {N} escalated to DECIDE
- [For each resolved challenge: one-line summary with rationale]

### Positive Findings

- [Things done well, preserved from reviewer feedback]
```

This is the handoff point from review to fix.

### Step 6: PHASE 2 — Collaborative Fix

Fixers and reviewers work together in real-time. Fixers implement while reviewers steer and validate continuously. This eliminates discrete review-fix rounds and produces already-reviewed code.

#### 6a. Determine and Spawn Fixers, Then Assign Fixes

**Spawn fixers now** — not before. The architect analyzes the confirmed FIX findings to determine which fixer domains are actually needed. Only spawn fixers for domains that have findings to fix.

For each required fixer domain:
1. Spawn `fixer-{name}` as a new teammate with role prefix
2. Validate required tools (Bash, Read, Grep, Edit minimum for fixers)
3. Each fixer receives: target content for reference, the message envelope format, cross-domain knowledge files relevant to their domain, and the **fixer discipline prompt** below. Consult `[sdlc-root]/knowledge/agent-context-map.yaml` for the fixer's mapped files.

```
TASK ID DISCIPLINE (mandatory — audit 2026-04-17 caught a fixer creating
10 duplicate task IDs):
Use the ORIGINAL task IDs from the architect's FIX_REQUEST. Do NOT call
TaskCreate to "track your work" — the architect owns the master list.
Update task status via TaskUpdate on the original task:
  - in_progress when you start
  - completed when FIX_COMPLETE is accepted by reviewers

PRE-FIX_COMPLETE CHECKLIST (mandatory — audit 2026-04-17 caught a fixer
shipping lint errors to the verification gate):
Before sending FIX_COMPLETE, you MUST verify:
  1. Tests that exercise the changed code pass (project test command)
  2. Linter passes on files you touched (project lint command)
  3. Type checker passes on files you touched (project typecheck command)
If any fail, fix them BEFORE sending FIX_COMPLETE. Do not push cleanup
work downstream to the verification gate.

Include the verification commands and their output in your FIX_COMPLETE
message body so reviewers can audit the pre-flight checks.

CONTEXT-BUDGET DISCIPLINE (mandatory — audit 2026-04-26 produced one
corrupted commit from silent context exhaustion):
Before tackling any non-trivial task (multiple file edits, coordinated
multi-task commit, or cross-package change), assess your context budget.
If you are above ~50% consumption AND the task is non-trivial:
  1. Self-flag to the architect: "Approaching context limit (~N%);
     requesting handoff before tackling task X."
  2. Wait for architect's decision — you may proceed if approved, or
     stand down if they spawn a successor.
  3. If proceeding: land the most coordinated single commit you can
     complete cleanly, then send FIX_COMPLETE for what landed and a
     "context-handoff-needed" message for what remains.
NEVER start a multi-task coordinated edit past ~75% context consumption
without explicit architect approval. NEVER leave a file in a partially-
edited state — if your output truncates mid-edit, the next fixer inherits
the corruption.
```

**When multiple reviewers found the same issue:** The architect assigns the fix to ONE fixer (the most relevant domain), but records ALL reviewers who found it in the task metadata (`found_by` field). The fixer sends FIX_COMPLETE to ALL reviewers who found the issue — each reviewer who surfaced the finding validates the fix from their domain perspective.

The architect then assigns FIX findings to fixer teammates via FIX_REQUEST messages. Each fixer receives:
- Task ID, description, file, line, evidence from review
- The list of all reviewers who found the issue (for FIX_COMPLETE routing)
- Cross-domain knowledge files from the finding agent(s) when fixer differs from finder — consult `[sdlc-root]/knowledge/agent-context-map.yaml` for the finder's mapped files
- **Library verification instructions** (when the fix involves external library APIs): verify API usage via Context7 (`mcp__context7__resolve-library-id` then `mcp__context7__query-docs`) before writing the fix

The architect sets task owner to fixer name, status to in_progress. All independent fixers are dispatched in parallel.

**Cross-fixer coordination (critical):** Before assigning, the architect checks task metadata for file overlap. If two fixers need the same file, sequence them via task dependencies — fixer B waits for fixer A to complete.

#### 6b. Collaborative Loop (per fixer)

For each finding the fixer works on:

1. Fixer reads the code, plans the fix
2. **If fixer disagrees** with the finding — CHALLENGE to the reviewer who found it
   - Reviewer responds with evidence (one exchange)
   - If unresolved — ESCALATION to architect who breaks the tie
3. Fixer implements the fix
4. Fixer sends FIX_COMPLETE to ALL reviewers listed in the task's `found_by` field
   - Message includes: what changed, which files, rationale
   - Each reviewer validates from their domain perspective (e.g., code-reviewer checks correctness, security-engineer checks the fix doesn't introduce a new vulnerability)
5. **Reviewers validate in real-time**
   - If all agree the fix is good — architect marks task as completed
   - If needs adjustment — reviewer sends STEER with specific guidance
   - Fixer adjusts, sends another FIX_COMPLETE
   - If fixer and reviewer disagree on fix approach — ESCALATION to architect
6. Fixer can REVIEW_REQUEST to any other reviewer for cross-domain input
   - e.g., fixer asks performance-engineer "will this fix impact render perf?"

#### 6c. Convergence

- Each finding converges individually (fixer + reviewer agree = resolved)
- No global "re-review round" — findings resolve as they're fixed
- Architect monitors task list: when all FIX tasks show "completed" — done
- **3-strike rule:** if a fixer and reviewer cycle 3 times on the same finding without converging, architect breaks it. If still stuck — escalate to user via AskUserQuestion

#### 6d. Cross-Fixer Coordination

- Architect MUST check task metadata for file overlap before assigning fixes
- If two fixers need the same file — architect sequences them via task dependencies (task B depends on task A completing)
- Fixer A finishes and sends FIX_COMPLETE — architect assigns fixer B with instruction to read the CURRENT file state
- Fixers can SendMessage each other for coordination ("I'm changing the import structure in this file, heads up")
- If a fixer discovers they need to touch a file owned by another fixer — message the architect, who coordinates the sequencing

### Step 6e: Verification Gate

After all findings are resolved, run verification per `[sdlc-root]/process/review-fix-loop.md` Step 0:

1. **Tests** — run the test suite
2. **Type checking** — run the type checker if applicable
3. **Linter** — run linter if configured
4. **SAST** — run security scanning if configured

Output the verification summary:

```
Verification gate:
- Tests: (pass/fail status)
- Types: (pass/fail status)
- Lint: (pass/fail status)
- SAST: (pass/fail status)
```

If verification fails — architect assigns failures to relevant fixers. Loop until verification passes.

This is a single pass — the collaborative fix phase already produced reviewer-validated code, so this gate catches only integration-level issues (type errors from cross-file changes, test regressions, etc.).

**User-away graceful degradation:** If no user message has been received in ~30 minutes and fixer activity is ongoing, shift to low-cadence observation — acknowledge fixer activity briefly (one short sentence per landing wave, not per FIX_COMPLETE), do not request architect status reports more often than every 30 minutes, let the team self-organize via the architect. Resume normal cadence when the user returns. Goal: minimize token spend during user-absent phases.

### Step 7: Final Report

```markdown
## Team Review-Fix Report: {target description}

### Protocol Compliance

Status legend: ✓ clean | ~ required intervention | ! violation

| Step | Status | Notes |
|------|--------|-------|
| Environment gate | ✓ | |
| Target resolution | ✓ | |
| Cost gate (user-confirmed dispatch) | ✓ | {N reviewers dispatched, N dropped by user} |
| Teammate selection + validation | ✓ | |
| Team creation + architect-first spawn | ✓ | |
| Inter-agent finding routing (reviewers use SendMessage, not plain text) | ✓/~/! | {note any reviewers who required re-emission prods} |
| Reviewer read-only discipline (no Edit/Write in Phase 1) | ✓/! | {note any violations caught and reverted} |
| Reviewer retraction discipline (re-read at HEAD before retracting) | ✓ | {N challenges resolved via R6} |
| Architect ACKs every finding | ✓ | |
| Challenges resolved by architect (no premature convergence) | ✓ | {N challenges, N escalated} |
| DECIDE items surfaced via AskUserQuestion | ✓ | {N items, N scope-narrowed} |
| Fixer spawn deferred until after review convergence | ✓ | |
| Fixer context-budget discipline (self-flag at ~50%, no silent exhaustion) | ✓/~/! | {note any respawns, handoffs, or corrupted commits} |
| Fixer task-ID discipline (no duplicate TaskCreate) | ✓/~ | {note any consolidations} |
| Fixer pre-FIX_COMPLETE checklist (tests + lint + types) | ✓/~ | {note any issues caught by verification gate} |
| Cross-fixer sequencing via addBlockedBy | ✓ | |
| Reviewer real-time validation | ✓ | |
| Architect termination tracking (no stale routing) | ✓/~ | {note any messages sent to terminated teammates} |
| Architect liveness poll (no soft-dead inference) | ✓/~ | {note any unresponsive teammates misclassified} |
| Architect status-sync cadence (master-list lag <5 min) | ✓/~ | {note any duplicate assignments from lag} |
| PRE-DELIVERABLE-SPLIT items filed | ✓ | {N items, D-numbers assigned} |
| Verification gate (tests, typecheck, lint, SAST) | ✓ | |
| User-away degradation (if applicable) | ✓/N/A | {note if low-cadence mode activated} |
| Team shutdown (all teammates terminated via shutdown_request) | Pending | |
| TeamDelete success (no missed fixers) | Pending | |

**Orchestration interventions:** {count}. If >5, flag as "high-friction" — investigate the protocol gap.

### Future Deliverables

| D-Number | Finding | Scope | Options Preserved |
|----------|---------|-------|-------------------|
| {D-N} | {finding description} | {why it exceeds this cycle} | {candidate approaches} |

### Finding Summary

| Metric | Count |
|--------|-------|
| Total findings | N |
| Challenged | N |
| Resolved by architect | N |
| Fixed | N |
| Escalated to user | N |

### Positive Findings

- [Things done well, from reviewer feedback]

### Worker Agent Reviews

Key feedback incorporated:
- [reviewer-name] specific, concrete feedback that was incorporated
- [fixer-name] specific implementation approach that worked well

### Final Task List State

| Task ID | Finding | Owner | Status |
|---------|---------|-------|--------|
| 3 | Missing group class | fixer-frontend-developer | completed |
| 5 | XSS in user input | fixer-backend-developer | completed |
```

### Step 8: Graceful Team Shutdown + Cleanup

Per Claude Code docs: "Always use the lead to clean up. Teammates should not run cleanup." And: TeamDelete "checks for active teammates and fails if any are still running, so shut them down first."

**Shutdown sequence:**

1. Request the architect's terminated-teammates list and cross-reference against the full spawn log. Any teammate NOT on the terminated list AND not explicitly in the current shutdown batch must be accounted for — do NOT assume "soft-dead" teammates are actually gone.
2. Lead sends shutdown request to each non-terminated teammate individually
   - Teammates can reject with explanation — handle rejections
   - Include any "UNRESPONSIVE" teammates the architect flagged during liveness polls
3. Wait for all teammates to confirm shutdown via `teammate_terminated` system messages
   - Note: "teammates finish their current request or tool call before shutting down, which can take time"
4. Only after ALL teammates are confirmed terminated (via system messages, not via silence) — TeamDelete
4. TeamDelete removes team config and task list automatically
5. Offer to commit changes:

> All fixes applied, verification passing, team cleaned up. Want me to commit these changes?

Do NOT commit automatically — wait for the user to confirm.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, use sdlc-review-code instead" | Small diffs are fine for team-review-fix if the changes are high-stakes |
| "Skip debate, agents agree" | The architect decides if debate is needed. Let the protocol run. |
| "Agent teams aren't enabled, I'll simulate with subagents" | No. Subagent dispatch is `sdlc-review-code` + `sdlc-review-fix`. This skill requires real agent teams for inter-agent communication. |
| "Just fix it myself instead of dispatching a fixer" | Manager rule. Fixers fix. You orchestrate. |
| "Spawn a fresh agent for this fix" | Use the existing fixer teammate via SendMessage. That's the whole point of persistent teammates. |
| "Spawn all fixers upfront so they're ready" | Fixers spawn in Step 6a after review converges. Spawning upfront wastes tokens on idle teammates that may never be needed. |
| "One reviewer found nothing, shut them down early" | They may be needed to validate fixes or provide cross-domain input during the fix phase. Keep all teammates alive until Step 8. |
| "Too many teammates, this is expensive" | The skill surfaces cost estimates in Step 2. The user decides whether to proceed. No artificial cap. |
| "Reviewer and fixer keep disagreeing, add more rounds" | 3-strike rule. Architect breaks it, then escalate to user. Don't let it loop. |
| "Skip verification, the reviewers already validated" | Reviewers validate individual fixes. Verification catches integration-level issues (type errors from cross-file changes, test regressions). Both are required. |
| "Reviewer output looks like a finding, architect will pick it up" | No. Plain-text reviewer output is only visible to the team-lead. Reviewers MUST call SendMessage with `to: "architect-software-architect"`. If you see a reviewer emit a finding as plain text, prod them to re-emit via SendMessage. |
| "Reviewer spotted a one-line fix, let them edit it" | No. Reviewers are read-only during Phase 1. Revert the edit and re-queue as a FINDING for Phase 2. Ratifying the edit normalizes the violation. |
| "Fixer created new task IDs to track subtasks" | Architect owns the master task list. Fixers use TaskUpdate on the original task ID, not TaskCreate. Consolidate duplicates and send the fixer a process note. |
| "Fixer said FIX_COMPLETE, just run verification" | Check that the fixer ran lint + typecheck + tests on touched files before FIX_COMPLETE. The pre-flight checklist prevents verification-gate ping-pong. |
| "Architect signaled convergence, we're good" | Verify every reviewer has at least one architect interaction (ACK'd finding or "standing by"). Silent reviewers may have emitted findings as plain text that never reached the architect. |
| "Fixer went silent, they're probably done" | Do NOT infer termination from silence. Check for a teammate_terminated system message. If none, send a shutdown_request to elicit a response. Soft-dead fixers cause TeamDelete failures. |
| "Fixer can handle one more big task before context runs out" | If the fixer is past ~50% context consumption and the task is non-trivial, they must self-flag. One corrupted commit from silent exhaustion costs more than a respawn. |
| "This finding is too big but let's just make it a FIX" | If it needs a CD UX decision, introduces a new subsystem, or requires full planning — it's PRE-DELIVERABLE-SPLIT. File with all options preserved and a D-number. |

## Integration

- **Depends on:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` environment variable
- **Does NOT replace:** `sdlc-review-code`, `sdlc-review-fix` — those remain as lighter-weight subagent alternatives
- **Replaces:** `sdlc-review-team` (unified review+fix lifecycle within a single agent team)
- **Shared references:**
  - Agent selection: `[sdlc-root]/process/agent-selection.yaml`
  - Review lenses: `[sdlc-root]/process/review-lenses.md`
  - Debate protocol: `[sdlc-root]/process/debate-protocol.md`
  - Communication protocol: `[sdlc-root]/process/team-communication-protocol.md`
  - Finding classification: `[sdlc-root]/process/finding-classification.md`
  - Review-fix loop (verification gate): `[sdlc-root]/process/review-fix-loop.md`
  - Manager rule: `[sdlc-root]/process/manager-rule.md`
  - Agent knowledge context: `[sdlc-root]/knowledge/agent-context-map.yaml`
