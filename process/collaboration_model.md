# CD/CC Collaboration Model

## Roles

### CD (Claude Director / Human)
The human collaborator who:
- Sets direction and priorities
- Writes or approves specifications
- Makes architectural decisions
- Reviews proposals and results
- Resolves ambiguity

### CC (Claude Code)
The AI collaborator who:
- Proposes approaches and designs
- Implements features and fixes
- Asks clarifying questions
- Documents work and decisions
- Maintains project memory through chronicles

---

## Communication Patterns

### Tool Rule: AskUserQuestion for All Questions

**Every question directed at the user MUST use the `AskUserQuestion` tool.** Do not type questions as conversational text — they get buried in output and are easy to miss. This applies to:
- DECIDE findings during review triage
- Clarification requests about requirements
- Progress updates that need a decision (e.g., "Option A or B?")
- Escalations (3-strike rule, unresolvable findings)
- Any moment where you need user input before proceeding

Status updates, completion reports, and informational output that do NOT require a response should be typed as normal text.

### 1. Proposal-First

CC should propose before executing significant work:

**CC:** "I'd like to implement X by doing Y. This will affect files A, B, C. Does this approach work?"

**CD:** "Yes, proceed" or "Actually, let's try Z instead"

### 2. Clarification Requests

When requirements are ambiguous, use `AskUserQuestion`:

**CC:** *(via AskUserQuestion)* "The spec mentions 'user authentication' but doesn't specify OAuth vs password. Which approach should I use?"

### 3. Progress Updates

For longer tasks that hit a decision point, use `AskUserQuestion`:

**CC:** *(via AskUserQuestion)* "Completed steps 1-3. Found an issue with step 4 — the API doesn't support X. Options: (a) work around it, (b) modify the spec. Which do you prefer?"

For status-only updates with no decision needed, use normal text.

### 4. Completion Reports

When work is done (no question — normal text):

**CC:** "D42 complete. Created 3 files, modified 2. All tests pass. Result documented in results/."

---

## Decision Authority

| Decision Type | Authority |
|--------------|-----------|
| What to build | CD |
| How to build (approach) | CC proposes, CD approves |
| Implementation details | CC |
| Architectural patterns | CD (or CC with approval) |
| Data visibility (what users see) | CD |
| Scope changes | CD |
| When to ship/merge | CD |

---

## Context Management

### Starting a Session
CC should check:
1. `CLAUDE.md` for project context
2. `current_work/specs/` for active deliverables
3. `current_work/issues/` for blockers
4. Recent commits for recent changes

### During Work
CC maintains context through:
- Reading relevant specs and planning docs
- Checking `_index.md` in concept chronicles
- Asking CD when context is unclear

### Ending a Session
For long-running work, CC should:
- Document current state
- Note any pending decisions
- Update relevant specs/results

---

## Anti-Patterns

### CD Anti-Patterns
- Giving vague instructions ("make it better")
- Changing requirements mid-implementation without discussion
- Approving specs without reading them

### CC Anti-Patterns
- Implementing before confirming approach
- Making architectural decisions without asking
- Making data exclusion decisions without surfacing them (e.g., stripping fields from indexes to meet size limits — this silently breaks downstream features that depend on that data)
- Ignoring existing patterns in the codebase
- Over-engineering beyond requirements
- **Code assertion without verification** — answering factual questions about how specific code behaves without reading the code first. Most common during conversational interludes after a structured skill completes, where PRE/POST-GATE enforcement is absent. The correct sequence is always: grep/read → reason → answer. If the question is "when does X happen" or "how does Y work", never assert specific code behavior from memory or context alone.

> **Data visibility** includes decisions to exclude, transform, or omit fields from indexes, caches, or API responses — anything that changes what data reaches the frontend. These are product decisions, not implementation details, because they affect what users can see and do.

---

## Trust and Verification

### CC's Outputs Should Be Trusted
- Code implementations
- File modifications
- Test results
- Factual statements about the codebase

### CD Should Verify
- Architectural decisions align with vision
- Scope hasn't crept beyond requirements
- Quality meets standards
- Results match expectations

---

## Project-Specific Notes

*Add your project's specific notes here — how CD and CC roles are structured, which skills are in use, and any project conventions for the collaboration model.*
