---
name: sdlc-reflect
description: >
  Surface learnings from the current work session into SDLC discipline parking lots. Reviews
  recent work (commits, changes, conversation context), identifies reusable insights and
  cross-discipline patterns, categorizes them by discipline, and writes them as triage-ready
  parking lot entries. This is the standalone version of the discipline capture protocol —
  use it after any work session where formal SDLC skills were not invoked.
  Triggers on "/sdlc-reflect", "capture learnings", "what did I learn", "surface insights",
  "session retrospective", "reflect on this session", "feed back to SDLC".
  Do NOT use for bulk external knowledge import — use sdlc-ingest.
  Do NOT use for exploring ideas — use sdlc-idea.
  Do NOT use for formal post-mortems — use sdlc-debug-incident closeout.
  Do NOT use during or after sdlc-execute or sdlc-plan — those skills run discipline capture automatically.
---

# SDLC Reflect — Session Learning Capture

Surface learnings from a work session into discipline parking lots. The goal is to capture reusable, non-obvious insights that emerged during work — especially sessions where formal SDLC skills were not invoked and discipline capture didn't run automatically.

**Argument:** `$ARGUMENTS` (optional — description of what to focus the reflection on, or "all" for a full session scan)

## When This Applies

Use after any work session where you did substantive work but didn't go through `sdlc-plan` / `sdlc-execute` (which have built-in discipline capture). Common scenarios:

- Direct dispatch sessions — CD was steering, agents were doing work, no plan artifact
- Bug fix sessions — diagnosed and fixed an issue without a deliverable
- Exploratory coding — prototyped something, learned things, didn't use `sdlc-idea`
- Refactoring sessions — restructured code, discovered patterns or anti-patterns
- Integration work — wired up external services, hit gotchas worth recording

Signs this skill is NOT appropriate:
- You just finished `sdlc-execute` or `sdlc-plan` — those already ran discipline capture
- You want to import external articles/transcripts — use `sdlc-ingest`
- You want to explore an idea — use `sdlc-idea`
- Nothing non-obvious happened — skip it, don't fabricate entries

## Preconditions

- At least one substantive work action in the current session (commits, file edits, agent dispatches, research)
- Discipline parking lot files exist at `[sdlc-root]/disciplines/`

## Steps

### 1. Survey the Session

Review what happened in this session to build a picture of the work done:

1. **Recent commits** — run `git log --oneline -20` and `git diff HEAD~5 --stat` (adjust range to cover the session's work)
2. **Uncommitted changes** — run `git status` and `git diff --stat` for work in progress
3. **Conversation context** — what agents were dispatched, what problems were solved, what friction was encountered

Present a brief session summary:

```
SESSION SUMMARY
Work: [1-2 sentence description of what was done]
Files touched: [count] ([key areas])
Agents dispatched: [list] | none (manual work)
Duration signal: [commit count and time span]
```

### 2. Identify Learnings

Scan the session for insights across two dimensions.

**Structured detection** — signals from `[sdlc-root]/process/discipline_capture.md` applicable in standalone mode. The full protocol defines seven signal types; two (`UNMAPPED_KNOWLEDGE`, `STALE_KNOWLEDGE`) require agent handoff data (`knowledge_feedback.loaded`) that isn't available in standalone sessions. The five session-inferrable signals:

| Signal | What to look for |
|--------|-----------------|
| `MISSING_KNOWLEDGE` | A problem was solved that no knowledge file covers — would a future agent benefit from having this documented? |
| `CROSS_DOMAIN_FRICTION` | Work required expertise outside the primary domain — did a backend change need design knowledge, or vice versa? |
| `RESURFACING_PATTERN` | Did you fix something you've fixed before, or see the same issue in multiple places? |
| `GOTCHA_DISCOVERED` | Did a library, API, or framework behave unexpectedly? |
| `ANTI_PATTERN_HIT` | Did you refactor away from a pattern that was causing problems? |

**Freeform scan** — beyond the structured signals, ask:

- What would I tell a colleague starting similar work tomorrow?
- What assumption turned out to be wrong?
- What took longer than expected, and why?
- What pattern emerged that applies beyond this specific task?

**Filtering criteria — include if:**
- Reusable beyond this specific task
- Non-obvious — an agent wouldn't derive it from reading the codebase
- Actionable — it changes how future work should be done

**Filtering criteria — exclude if:**
- Obvious to any competent practitioner
- Specific to this exact task with no generalizable lesson
- Already captured in an existing knowledge file or discipline entry

### 3. Categorize by Discipline

Map each identified learning to its target discipline. Read `[sdlc-root]/disciplines/README.md` for the full discipline list if needed.

| Discipline | Typical learnings |
|-----------|-------------------|
| `coding` | Implementation patterns, refactoring insights, language gotchas, testability lessons |
| `architecture` | System design discoveries, integration patterns, boundary issues, performance insights |
| `testing` | Test strategy insights, coverage gaps, flaky test patterns, tool gotchas |
| `design` | UI/UX patterns, accessibility discoveries, component interaction issues |
| `data-modeling` | Schema insights, migration patterns, query optimization discoveries |
| `deployment` | CI/CD friction, infrastructure gotchas, release process learnings |
| `observability` | Monitoring gaps, debugging workflow improvements, logging patterns |
| `business-analysis` | Requirements clarifications, domain model insights, stakeholder feedback patterns |
| `product-research` | User behavior observations, competitive insights, feature viability signals |
| `process-improvement` | SDLC friction, workflow improvements, tool integration insights |
| `dx` | Developer experience friction, documentation gaps, onboarding obstacles |

Present the categorized learnings for confirmation:

```
LEARNINGS
─────────────────────────────────────────────
[N] learnings identified across [N] disciplines

  coding (2):
    1. [Brief description of learning]
    2. [Brief description of learning]

  architecture (1):
    1. [Brief description of learning]

Write to parking lots? (y / adjust / skip)
```

Wait for confirmation. The user may adjust categorization, remove entries, or add ones you missed.

### 4. Write to Parking Lots

For each confirmed learning, append to the target discipline file under `## Parking Lot`.

**Entry format:**

```
- **[date] [context]**: [insight]. [NEEDS VALIDATION]
```

**Context format:** `[session: {brief-slug}]` — e.g., `[session: fix-auth-race-condition]`, `[session: refactor-payment-flow]`.

For auto-detected structured gaps, use the GAP format adapted from `[sdlc-root]/process/discipline_capture.md`:

```
- **[date] [session: {slug}]**: [GAP:{type}] {description}. [NEEDS VALIDATION]
```

The canonical GAP format includes `Source: {agent} finding` — omitted here because sdlc-reflect infers gaps from git history and conversation context, not from agent handoffs.

**Rules:**
- Default triage marker is `[NEEDS VALIDATION]` — do not mark as `[READY TO PROMOTE]` unless the learning has been validated through repeated use
- One insight per bullet — keep entries atomic for independent triage
- Include enough context that the entry is useful without the conversation history
- Write directly — the Manager Rule does not apply to parking lot entries (per `[sdlc-root]/process/discipline_capture.md`)

### 5. Report

Present what was captured:

```
REFLECT REPORT
═══════════════════════════════════════════════════════════════

Session: [brief description]

ENTRIES WRITTEN
  [discipline]: [count] entries
  [discipline]: [count] entries
  Total: [count] entries across [count] disciplines

SAMPLE ENTRIES
  - [discipline]: [first entry text, truncated]
  - [discipline]: [first entry text, truncated]

SKIPPED
  [count] potential insights filtered (obvious: N, task-specific: N, already-captured: N)

NEXT STEPS
  - Entries are marked [NEEDS VALIDATION] — they'll be triaged during the next sdlc-audit cycle
  - [If any entry looks ready to promote]: Consider promoting [entry] to [target knowledge file] after further validation
```

## Red Flags

| Thought | Reality |
|---------|---------|
| "Nothing happened worth capturing" | If the session involved substantive work, run the structured detection signals before concluding there's nothing. But if genuinely nothing non-obvious surfaced, that's fine — skip it. |
| "I'll mark these as READY TO PROMOTE" | Default is NEEDS VALIDATION. A single session's learning hasn't been validated through repeated use. |
| "I'll dispatch an agent to write the parking lot entries" | The orchestrator writes parking lot entries directly — Manager Rule does not apply to process documentation. |
| "I'll also update the knowledge YAML files" | Reflect captures raw insights to parking lots. Promotion to knowledge stores is a separate triage step (sdlc-audit or manual). |
| "This belongs in the knowledge store, not a parking lot" | Parking lot is the landing zone. Even high-confidence insights start here. The triage cycle promotes what's validated. |
| "I'll skip the user confirmation step" | Always present categorized learnings before writing. The user may disagree with categorization or want to adjust. |
| "I should run this after every session" | Only when substantive work happened AND formal skills didn't already capture. Most direct-dispatch or bug-fix sessions are good candidates. |
| "I'll create a new discipline for this learning" | Route to the closest existing discipline. New disciplines require the criteria in `[sdlc-root]/disciplines/README.md` § "Creating a New Discipline". |

## Integration

- **Depends on:** Substantive work in the current session; discipline parking lot files at `[sdlc-root]/disciplines/`
- **Feeds into:** Discipline triage cycle (sdlc-audit scans parking lots for threshold breaches and untriaged entries)
- **Uses:** `git log`, `git diff`, `git status` (session survey); `[sdlc-root]/disciplines/*.md` (write targets); `[sdlc-root]/process/discipline_capture.md` (structured gap detection methodology)
- **Complements:** Built-in discipline capture in sdlc-execute, sdlc-plan, sdlc-idea (those run automatically; this is for sessions without those skills)
- **Does NOT replace:** sdlc-ingest (bulk external knowledge import), sdlc-audit improvement mode (systematic process gap analysis), built-in discipline capture steps in execution/planning skills
- **DRY notes:** Structured detection uses five of seven signals from `[sdlc-root]/process/discipline_capture.md` — standalone mode omits `UNMAPPED_KNOWLEDGE` and `STALE_KNOWLEDGE` (require agent handoff data). GAP entry format omits `Source: {agent} finding` (documented in Step 4). The difference: discipline_capture.md runs embedded within other skills with full triage table and agent handoff data; sdlc-reflect runs standalone and infers from git history and conversation context.
