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

## Workflow Design Rationale

The plan→execute workflow is structured around context window management. These principles explain *why* the workflow works the way it does — not just what it does.

### Context Clearing Between Phases

Each phase (spec, plan, execute) should start with a fresh context window. LLM performance degrades as the context fills with tool outputs, file reads, and conversation history. Clearing between phases ensures execution happens with only the approved plan as input, not accumulated noise from the planning process. The plan file is the compaction artifact — it compresses all research and decisions into a document that a fresh context can act on immediately.

### Domain Agents as Context Isolation

Dispatching work to domain agents is a context management strategy. Each agent gets a clean context window loaded with only the domain knowledge and files relevant to its task. A backend-developer agent doesn't load design knowledge, accessibility rules, or frontend component patterns — its context stays focused on backend concerns. This keeps each agent operating in a focused, high-signal context rather than a broad, noisy one. The domain scoping (specific files, specific knowledge, specific concerns) is what makes the isolation effective.

### On-Demand Research Over Static Documentation

The spec phase investigates the codebase live rather than relying on pre-written architectural documentation. Code is the source of truth; documentation drifts. On-demand research compresses the actual current state of the code into a spec — a snapshot of truth derived from the code itself, not a cached understanding that may be stale.

### Rigor Gradient

Match process overhead to task complexity. The trigger is complexity of decisions, not file count.

| Complexity | Approach |
|---|---|
| Trivial (config change, typo fix) | Direct implementation, no plan |
| Moderate (multi-step, cross-domain, non-obvious approach) | `sdlc-lite-plan` → `sdlc-lite-execute` |
| Significant (new feature, new integration, architectural change) | `sdlc-plan` → `sdlc-execute` |

A 2-file change touching real-time + database warrants a lite plan. A 10-file rename refactor might not. Judge by the complexity of the decisions involved.

### Plan Review as Mental Alignment

As AI-generated code throughput increases, plan review becomes the primary mechanism for maintaining shared understanding of how the codebase is evolving. CD reads plans to stay aligned on approach and intent. This is more efficient than reviewing hundreds of lines of generated code after the fact. Plans compress intent — a reviewer can assess correctness at the approach level before any code is written, catching architectural missteps that would be expensive to fix post-implementation.

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
- **Trajectory poisoning** — repeatedly correcting the agent in the same context window instead of starting fresh. After 2-3 corrections, the conversation trajectory becomes "CC does something wrong → CD corrects → CC does something wrong again." The LLM treats this trajectory as the expected pattern and continues producing errors. If the agent is off track after 2-3 corrections, clear the context and start a new session with better initial guidance rather than continuing to correct in a poisoned trajectory.

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
