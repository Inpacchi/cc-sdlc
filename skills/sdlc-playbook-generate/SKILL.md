---
name: sdlc-playbook-generate
description: >
  Generate structured playbooks from previous session conversations and their associated git commits.
  Analyzes both what worked (the process to formalize) and what was missed (corrections, setup gotchas,
  environment gaps, service configuration that surfaced mid-execution). Produces playbooks following the
  project's existing playbook template format. Triggers on "make a playbook from", "analyze session",
  "generate playbook", "create playbook from session", "playbook from that session", "let's make a
  playbook for", "formalize that into a playbook", "turn that session into a playbook",
  "what did we learn from that session", "extract a playbook".
  Do NOT use for creating playbooks from scratch without session data — write those directly.
  Do NOT use for bulk knowledge import — use sdlc-ingest.
  Do NOT use for session resumption — use sdlc-resume.
---

# Playbook Generation from Session Analysis

Extract structured, reusable playbooks from completed session conversations and their git history. The goal is to capture both the **process that worked** (steps to formalize and repeat) and the **gap that didn't** (corrections, missed setup, environment surprises, configuration gotchas that only surfaced during execution).

**This skill produces a playbook artifact in `ops/sdlc/playbooks/`. It does NOT produce specs, plans, or implementations.**

**Argument:** `$ARGUMENTS` (session identifier — a name, search term, or session ID; plus optional playbook purpose/scope hint)

## When This Applies

Use this when the user has completed work in a previous session and wants to formalize the process into a repeatable playbook. The hallmark is retrospective analysis — the work is done, and now the user wants to capture what they learned.

Signs this skill is appropriate:
- "Let's make a playbook from the Slack bot session"
- "Analyze that session and create a playbook for integrations"
- The user just finished a non-trivial task and wants to prevent the same friction next time
- A session involved corrections mid-stream that indicate missing process knowledge

Signs this skill is NOT appropriate:
- Writing a playbook from scratch without session data → write directly using `playbooks/example-playbook.md` as template
- Importing knowledge from external content → `sdlc-ingest`
- Resuming an incomplete session → `sdlc-resume`

## Core Principles

**Two sources of truth, not one.** The conversation reveals what happened (intent, friction, corrections, discoveries). The git log reveals what was produced (code, config, migrations). Neither alone tells the full story. Cross-reference both.

**Friction is the signal.** The most valuable parts of a playbook are the steps that weren't obvious — the env var that was missing, the database migration that was forgotten, the service that needed restarting, the config that was wrong on first attempt. Scan for user corrections, re-dos, "oh wait" moments, and error-fix cycles.

**Formalize the happy path too.** The process that got you 90% there is the backbone of the playbook. Capture the step sequence, agent selection, and knowledge context that worked — the gap analysis layers on top of that foundation.

**Concrete over abstract.** Playbook steps reference specific files, specific env vars, specific service names. "Configure the database" is useless. "Add DATABASE_URL to Railway service env vars, run prisma migrate deploy, verify connection with prisma db pull" is a playbook.

**One playbook per task type.** A session might touch multiple concerns. The playbook covers the repeatable task pattern, not the specific session. Generalize the steps while preserving the specific gotchas.

## Workflow

```
LOCATE → CORRELATE → ANALYZE → DRAFT → PLACE → REPORT
```

Sequential. Each step must complete before the next. The user confirms scope (step 2) before deep analysis begins.

## Steps

### 1. Locate the Session

Find the target session conversation. Sessions are stored as JSONL files in the project's Claude directory:

```
~/.claude/projects/<project-dir-hash>/<session-id>.jsonl
```

**Resolution strategy:**
1. If the user provides a session name or search term, scan JSONL files for matching content (first user messages, topic keywords)
2. If the user provides a session ID, locate the file directly
3. If ambiguous, present candidates with timestamps and first user message for the user to pick

**Extract session metadata:**
- Session ID and timestamp range (first to last message)
- Project directory (from the JSONL path)
- Message count and approximate conversation length

Present the located session for confirmation before proceeding.

### 2. Correlate with Git History

Using the session's timestamp range, extract all git commits made during that session:

```bash
git log --after="<session_start>" --before="<session_end>" --format="%H %ai %s" --reverse
```

**Build the correlation map:**
- List all commits with their messages and timestamps
- For significant commits, read the diff summary (`git diff --stat <hash>~1 <hash>`)
- Identify files created, modified, and deleted during the session
- Note any commits that were amended or reverted (signals of correction)

**Present scope for confirmation:**

```
SESSION LOCATED
ID: [session-id]
Time span: [start] → [end] ([duration])
Messages: [count] user / [count] assistant
Commits: [count] commits touching [count] files
Key files: [top 5-8 files by change frequency]
Playbook target: [user's stated purpose, or inferred task type]
```

Wait for user confirmation. If the user adjusts the playbook scope or target, re-present.

### 3. Analyze

Read the session JSONL and extract structured insights. This is the core analytical step — see `references/analysis-methodology.md` for the detailed extraction patterns.

**Two-track analysis:**

**Track A — The Process (what worked):**
- Ordered sequence of steps taken (what was done and in what order)
- Agent selection and dispatch patterns
- Knowledge files and references consulted
- Decision points and the choices made
- Codebase patterns leveraged (existing code that informed the approach)

**Track B — The Gap (what was missed or corrected):**
- User corrections ("no, not that", "we also need to", "that's wrong")
- Error-fix cycles (something failed, had to debug and retry)
- Mid-stream discoveries ("oh, we also need to set up X")
- Environment/infrastructure setup that wasn't anticipated
- Configuration values that required trial and error
- Service dependencies that weren't obvious upfront
- Steps that were done out of order and had to be redone

**Cross-reference tracks:** For each gap item, identify where in the process sequence it should have appeared. This produces the corrected, complete process that the playbook will capture.

### 4. Draft the Playbook

Generate the playbook following the project's template format (`ops/sdlc/playbooks/example-playbook.md`). Read the template first to match the exact structure.

**Key sections to populate from analysis:**

| Template Section | Source |
|-----------------|--------|
| When to use | Generalized from the session's task type |
| Recommended Agents | From Track A agent dispatch patterns |
| Knowledge Context | From Track A knowledge files consulted |
| Typical Phases | From Track A process sequence, corrected by Track B ordering |
| Reference Implementations | From git history — key files created/modified |
| Key Decisions to Surface | From Track A decision points |
| Common Gotchas | From Track B — the core value of the analysis |
| Checklist Before Complete | From both tracks — the full corrected process |

**Gotchas section is critical.** Each gotcha must include:
- What went wrong or was missed
- Why it wasn't obvious (what assumption led to the gap)
- The concrete fix (specific env var, specific command, specific config)

**Generalize but preserve specifics.** The playbook is for the *task type*, not the specific session. But gotchas reference specific technical details — env var names, service configurations, file paths. These are the details that make the playbook actionable.

Present the draft to the user for review before writing.

### 5. Place

After user approval:

1. Write the playbook to `ops/sdlc/playbooks/<slug>.md`
2. Update `ops/sdlc/playbooks/README.md` — add entry to the "Available playbooks" table
3. Check if any existing knowledge stores should cross-reference the new playbook (note in report, don't auto-modify)

### 6. Report

```
PLAYBOOK GENERATION REPORT
═══════════════════════════════════════════════════════════════

Source session: [session-id] ([date range])
Commits analyzed: [count] ([count] files changed)
Playbook: ops/sdlc/playbooks/[slug].md

PROCESS CAPTURED
  Phases: [count]
  Steps: [count] total
  Agents: [list of agents referenced]
  Knowledge context: [list of knowledge files]

GAP ANALYSIS
  Corrections found: [count]
  Gotchas documented: [count]
  Setup steps added: [count] (not in original session flow)
  Ordering fixes: [count] (steps that should have come earlier)

CROSS-REFERENCES
  Related playbooks: [existing playbooks that overlap] | none
  Knowledge stores to update: [stores that could benefit] | none

SESSION COVERAGE
  Conversation messages analyzed: [count]/[total]
  Commits correlated: [count]/[total in range]
```

### 7. Changelog Update

Update `ops/sdlc/process/sdlc_changelog.md`:

```markdown
## [date]: Playbook Generated — [playbook name]

**Origin:** Session analysis of [session-id] ([brief description of the work])

**What happened:** Analyzed [duration] session with [N] commits to extract repeatable process and gap analysis for [task type].

**Changes made:**

1. **`playbooks/[slug].md`** — new playbook with [N] phases, [N] steps, [N] gotchas
2. **`playbooks/README.md`** — added to available playbooks index

**Rationale:** Formalizing session learnings into a playbook prevents repeated friction. [N] gotchas documented that would otherwise be rediscovered on the next [task type] integration.
```

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just summarize what happened" | Extract process steps and gotchas, not a narrative summary. |
| "The git log tells the whole story" | Git log shows what was committed. The conversation shows what was tried, failed, and corrected. Both are required. |
| "I'll skip the gap analysis, the process is clear" | The gap analysis IS the primary value. A playbook without gotchas is just a generic checklist. |
| "This gotcha is too specific to include" | Specific is good. "Set SLACK_SIGNING_SECRET in Railway" is more useful than "configure environment variables". |
| "I'll generalize away the details" | Generalize the task type, preserve the technical specifics. The env var names, the service configs, the file paths — those are what save time next run. |
| "I'll create the playbook without showing the draft" | Always present the draft for review. The user knows nuances the conversation didn't capture. |
| "The session was messy, I can't extract a clean process" | Messy sessions produce the best playbooks — the mess IS the gap analysis. |

## Integration

- **Feeds into:** Planning skills (`sdlc-plan`, `sdlc-lite-plan`) — playbooks pre-seed agent selection and knowledge context
- **Uses:** Session JSONL files, git log, existing playbook template, knowledge stores (for cross-referencing)
- **Complements:** `sdlc-ingest` imports external knowledge; this skill imports internal session knowledge
- **Downstream:** `/sdlc-audit` checks playbook freshness as part of knowledge layer health audits

## Additional Resources

### Reference Files

For detailed analysis patterns and extraction methodology:
- **`references/analysis-methodology.md`** — Detailed patterns for extracting process steps and gap signals from session conversations and git history
