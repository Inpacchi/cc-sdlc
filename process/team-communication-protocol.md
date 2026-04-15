# Team Communication Protocol

Defines the inter-agent communication protocol for skills that use agent teams. Reusable by any team-based skill (e.g., `team-review-fix`, future `team-execute`).

---

## Message Envelope

All inter-agent messages use a hybrid format: structured routing fields for traceability, natural language body for reasoning. Research shows hybrid formats outperform both pure natural language (ChatDev: 2.25/5 executability) and over-structured schemas (rigid, overkill for reasoning). MetaGPT's structured documents achieved 3.75/5 executability — the gain comes from defined output formats, not machine-enforced schemas.

```
MESSAGE ENVELOPE:
{
  type: FINDING | CHALLENGE | FIX_REQUEST | FIX_COMPLETE | REVIEW_REQUEST |
        CLARIFICATION | ESCALATION | STATUS | STEER,
  from: "reviewer-security-engineer",
  to: "fixer-frontend-developer",
  task_id: "3",
  file: "src/components/GalleryCarousel.tsx",
  line: 42,
  severity: "major",
  body: "[natural language -- evidence, reasoning, code citations]"
}
```

**Enforcement:** Prompt-enforced (like MetaGPT), not schema-validated. Skill instructions tell agents to format messages this way. The structured fields (type, from, to, task_id) make communication auditable and traceable.

## Message Types

| Type | From | To | Purpose |
|------|------|----|---------|
| `FINDING` | Reviewer | Mediator + relevant reviewers | Initial finding from review phase |
| `CHALLENGE` | Reviewer or Fixer | Reviewer or Fixer + Mediator | Dispute a finding with counter-evidence |
| `FIX_REQUEST` | Mediator | Fixer | Assign a confirmed finding to fix, includes debate evidence |
| `FIX_COMPLETE` | Fixer | ALL reviewers in the task's `found_by` field | "I've fixed task #N, here's what I changed" — each reviewer validates from their domain |
| `REVIEW_REQUEST` | Fixer | Reviewer | "Can you check my fix for task #N in real-time?" |
| `CLARIFICATION` | Fixer or Reviewer | Reviewer or Fixer | "What exactly did you mean by X in task #N?" |
| `STEER` | Reviewer | Fixer | Real-time guidance while fixer is implementing |
| `ESCALATION` | Any | Mediator | Unresolved fixer-reviewer disagreement |
| `STATUS` | Any | Lead | Progress update |

## Findings Registry (Built-in Task List)

Findings are tracked as **tasks** in the shared task list — no custom file needed. The task system provides states, dependencies, file locking, ownership, and visibility to all teammates natively.

### Task Creation

The mediator (architect) creates finding tasks directly. Teammates CAN create tasks (TeamCreate docs: *"Teammates should: Create new tasks with TaskCreate when identifying additional work"*). Any agent can set/change ownership via TaskUpdate.

Each finding becomes a task with structured metadata:

```
TaskCreate({
  subject: "Missing group class breaks hover navigation",
  description: "File: src/components/GalleryCarousel.tsx:42\nCategory: correctness\n[full description with evidence]",
  metadata: {
    type: "finding",
    severity: "major",
    file: "src/components/GalleryCarousel.tsx",
    line: 42,
    category: "correctness",
    found_by: "reviewer-code-reviewer, reviewer-accessibility-auditor",
    classification: "FIX"
  }
})
```

### Status Flow (maps to built-in task states)

| Task State | Meaning |
|------------|---------|
| `pending` | Finding confirmed, awaiting fix assignment |
| `in_progress` | Fixer is working on it (owner set to fixer name) |
| `completed` | Fix applied and reviewer-validated |

**Finding IDs = task IDs.** The task system generates IDs automatically. Agents reference findings by task ID in messages (e.g., "Regarding task #3...").

### Same-File Sequencing (Task Dependencies)

Two teammates editing the same file leads to overwrites. The mediator sequences same-file fixes via task dependencies:

```
TaskUpdate({ taskId: "5", addBlockedBy: ["3"] })
// Task 5 (fixer B's fix) can't start until task 3 (fixer A's fix) completes
```

When fixer A finishes and sends FIX_COMPLETE, the mediator assigns fixer B with instruction to read the CURRENT file state.

## Fixer-Reviewer Collaborative Protocol

### During Fix Phase

1. **Fixer reads the code, plans the fix**
2. **If fixer disagrees with a finding** — CHALLENGE to the reviewer who found it
   - Reviewer responds with evidence (one exchange)
   - If unresolved — ESCALATION to mediator who breaks the tie
3. **Fixer implements the fix**
4. **Fixer sends FIX_COMPLETE** to ALL reviewers in the task's `found_by` field
   - Message includes: what changed, which files, rationale
   - Each reviewer validates from their domain perspective
5. **Reviewers validate in real-time** (respond with STEER or confirmation)
   - If all agree — mediator marks task as completed
   - If needs adjustment — reviewer sends STEER with specific guidance
   - Fixer adjusts, sends another FIX_COMPLETE
   - If fixer and reviewer disagree on the fix approach — ESCALATION to mediator
6. **Cross-domain consultation** — fixer can REVIEW_REQUEST to any other reviewer
   - e.g., fixer asks performance-engineer "will this fix impact render perf?"

### 3-Strike Rule

If a fixer and reviewer cycle 3 times on the same finding without converging:
1. Mediator breaks the tie
2. If still stuck after mediator intervention — escalate to user via AskUserQuestion

## Cross-Fixer Coordination

- Mediator MUST check task metadata for file overlap before assigning fixes
- If two fixers need the same file — mediator sequences them via task dependencies
- Fixers can SendMessage each other for coordination ("I'm changing the import structure in this file, heads up")
- If a fixer discovers they need to touch a file owned by another fixer — message the mediator, who coordinates the sequencing

## Escalation Path

```
Fixer <-> Reviewer     (one exchange)
    |
    v
Mediator                (breaks tie)
    |
    v
User (AskUserQuestion)  (final authority)
```

## Research Basis

- **MetaGPT vs ChatDev benchmark:** 67% executability improvement with structured documents over pure natural language
- **Google A2A protocol:** Structured routing with flexible body
- **Agent Communication Trilemma (arXiv:2504.16736):** Trade-off between expressiveness, structure, and overhead
- **"Why Do Multi-Agent LLM Systems Fail?" (arXiv:2503.13657):** Communication failures are a leading cause of multi-agent system breakdowns
