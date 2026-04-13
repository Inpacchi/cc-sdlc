---
name: sdlc-review-team
description: >
  Team-powered code review with inter-agent debate. Domain agents review independently, then a software-architect
  subagent mediates conflicts before presenting findings. Triggers on "team review", "review with debate",
  "deep review", "/review-team". Requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1.
  Do NOT use for routine reviews — use sdlc-review-diff or sdlc-review-commit for those.
---

# Team Review with Debate

Review code changes using an agent team where domain agents can challenge each other's findings before reporting. This produces higher-confidence findings than standard review skills by resolving contradictions that users would otherwise reconcile manually.

**Cost:** 2-4x more tokens than `review-diff` or `review-commit`. Use when finding accuracy matters more than speed — complex diffs, security-critical changes, architectural decisions.

**Argument:** `$ARGUMENTS` (optional commit ref — if omitted, reviews uncommitted changes)

## Steps

### 0. Environment Gate

Check that the agent teams feature is enabled:

```bash
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
```

If not set to `1`, tell the user and stop:

> Agent teams require the experimental feature flag. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in your environment and restart Claude Code.

### 1. Gather the Diff

If a commit ref argument is provided:
- Run `git show --stat {ref}` and `git show {ref}` to get the diff

If no argument (review uncommitted changes):
- Run `git diff HEAD --stat` and `git diff HEAD` to get the diff
- Run `git status -s` to check for untracked files. Warn about untracked source files as in `review-diff`

If there are no changes, tell the user and stop.

### 2. Select Teammates

Follow the agent selection process in `ops/sdlc/process/agent-selection.md`:

1. Always add `code-reviewer`
2. Add Tier 1 agents based on file paths
3. Read diff content for Tier 2 triggers
4. Note WHY each Tier 2 agent is included or excluded

**If >7 agents selected:** Warn the user with the count and estimated cost increase, then ask whether to proceed with the full team or trim. Do not silently reduce the team.

Output a dispatch checklist:

```
Team review: {uncommitted changes | commit short-sha: subject}
Files changed: N

Teammates:
- [ ] code-reviewer (always)
- [ ] frontend-developer (touches frontend components)
- [ ] performance-engineer (new store selectors)

Not dispatching:
- software-architect — follows existing pattern, no new abstractions

Debate protocol: up to 2 rounds for conflicts (see ops/sdlc/process/debate-protocol.md)
```

### 3. Create Team and Spawn Teammates

Create the agent team. The main session acts as team lead — it manages team lifecycle (create, spawn, wait, cleanup) but does NOT make review judgments.

Spawn each selected agent as a teammate. Each teammate receives:
- The full diff
- Review lenses from `ops/sdlc/process/agent-selection.md` § Lenses
- Relevant knowledge context from `ops/sdlc/knowledge/agent-context-map.yaml` for their role
- Instructions to post findings as task completions with required fields:
  - `file` — path and line range
  - `finding` — what the issue is
  - `severity` — critical / major / minor
  - `category` — overengineering / type-safety / security / contract / DRY / architecture / correctness
  - `evidence` — specific code or guarantee that supports the finding
  - `recommendation` — what should change

### 4. Phase 1 — Independent Review

All teammates review in parallel with no inter-agent communication. The lead waits for all teammates to finish.

This phase is identical to standard `review-diff` / `review-commit` behavior — the value of independent review is preserved.

### 5. Collect Findings

Gather all findings from all teammates. Do not filter or modify at this stage.

### 6. Phase 2 — Debate (Architect-Mediated)

Dispatch a `software-architect` subagent to run the debate protocol defined in `ops/sdlc/process/debate-protocol.md`. The architect receives:
- All Phase 1 findings from all teammates
- The full diff
- Teammate identities (which agent produced which finding)

The architect executes:

1. **Conflict detection** — scan for contradictory assessments, severity disagreements, and incompatible recommendations on the same code
2. **Round 1** — for each conflict, create debate tasks where each conflicting teammate sees the other's finding + evidence and responds once
3. **Adaptive break** — architect judges each Round 1 exchange. If evidence resolves it → resolved. If not → formulate a specific question for Round 2
4. **Round 2 (conditional)** — only for unresolved conflicts. Each teammate gets the architect's question + the other's Round 1 response. One response each.
5. **Escalation** — anything still unresolved → `DECIDE` classification (user resolves)
6. **Anti-conformity check** — flag any position flips, evaluate if original positions had merit
7. **Synthesis** — deduplicate, resolve, calibrate severity, produce final findings

If no conflicts are detected in Phase 1 findings, the architect skips debate and proceeds directly to synthesis (deduplication and severity calibration only).

### 7. Present Report and Clean Up

Clean up the agent team.

Present the architect's synthesized report in the standard findings format:

```markdown
## Team Review: {uncommitted changes | commit short-sha}

{N} files changed | Reviewed by {N} domain agents | {N} conflicts debated

### Findings

| # | Finding | Agent(s) | Severity | Category | Status |
|---|---------|----------|----------|----------|--------|
| 1 | specific finding | agent-name | critical/major/minor | category | confirmed/resolved/DECIDE |
| 2 | ... | ... | ... | ... | ... |

### Debate Summary

[If debates occurred:]
- {N} conflicts detected, {N} resolved in Round 1, {N} resolved in Round 2, {N} escalated to DECIDE
- [For each DECIDE finding: brief summary of both positions]

[If no debates:]
- No conflicting findings — all agents aligned

### Overengineering Summary

[Same as review-diff/review-commit]

### Details

#### Finding 1: [title]
**Agent(s):** [agent-name(s)] | **Severity:** [level] | **Category:** [category] | **Status:** [confirmed/resolved/DECIDE]
**File:** [path:line]
[Concrete description of the issue and what should change]
[If resolved via debate: "Resolved: [agent-a] and [agent-b] initially disagreed on [X]. Evidence from [winning-side] was decisive."]
[If DECIDE: "Unresolved: [agent-a] says [X], [agent-b] says [Y]. Both positions have merit — user should decide."]
```

### 8. Next Steps

After presenting the report:

> **{N} findings** ({critical} critical, {major} major, {minor} minor) — {N} confirmed, {N} resolved via debate, {N} need your decision (DECIDE)
>
> Run `/sdlc-review-fix` to fix all confirmed and resolved findings. DECIDE findings require your input first.

Do NOT fix anything in this skill. The review skill only reviews — `/sdlc-review-fix` handles all fixes.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The diff is small, use review-diff instead" | Small diffs are fine for review-team if the changes are high-stakes |
| "Skip debate, agents agree" | The architect decides if debate is needed. Let the protocol run. |
| "Agent teams aren't enabled, I'll simulate it with subagents" | No. Subagent dispatch is `review-diff`. This skill requires real agent teams for inter-agent communication. |
| "Round 2 keeps failing to resolve, add Round 3" | The protocol caps at 2 rounds. Additional rounds decrease quality through conformity pressure. Escalate to DECIDE. |
| "One agent flipped, just use the new position" | Check the anti-conformity safeguard. Flips from social pressure should retain the original finding. |
| "Too many agents, dispatch all 14" | Warn the user and ask whether to proceed or trim. Teams larger than 7 get expensive fast. |

## Integration
- **Depends on:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` environment variable
- **Feeds into:** `sdlc-review-fix` (if findings need fixing)
- **Siblings:** `sdlc-review-diff` (same lenses, no debate), `sdlc-review-commit` (same lenses, no debate)
- **Shared references:**
  - Agent selection and lenses: `ops/sdlc/process/agent-selection.md`
  - Debate protocol: `ops/sdlc/process/debate-protocol.md`
