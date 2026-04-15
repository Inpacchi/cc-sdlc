# Multi-Agent Debate Protocol

Defines how team-based review skills resolve conflicting findings between domain agents. Grounded in multi-agent debate research — citations at the end.

This protocol uses the **organic broadcast + architect tiebreaker** model. There are no formal debate rounds. Reviewers broadcast findings, challenge or agree organically, and the architect breaks ties in real-time. For message format and envelope structure, see `[sdlc-root]/process/team-communication-protocol.md`.

## Design Principles

1. **Independent review is the primary value driver.** Most gains attributed to debate are actually attributable to ensembling — agents reviewing independently without seeing each other's work (Du et al. 2023, "Should We Be Going MAD?" ICLR Blog 2025).
2. **Debate resolves conflicts, not consensus.** The goal is not agreement — it's evidence-based resolution of contradictions.
3. **Judge-managed adaptive breaking outperforms fixed rounds.** The architect decides when evidence is sufficient, rather than running a fixed number of rounds (Liang et al. EMNLP 2024).
4. **Organic convergence over structured rounds.** No Round 1/Round 2 structure. Reviewers challenge or agree naturally. The architect breaks ties immediately when they arise. This converges faster and avoids the conformity pressure that accumulates over multiple forced rounds.

## Review Phase — Broadcast and Converge

Reviewers work independently but send findings to the architect AND to reviewers whose domain overlaps (direct messages, not broadcast). Claude Code docs warn "broadcast: use sparingly, as costs scale with team size." Direct messages to relevant reviewers + architect avoids inflating every teammate's context with every finding. The architect can broadcast selectively when cross-domain input is needed.

When a reviewer finds an issue:
1. Send the finding (FINDING message) to the architect AND domain-relevant reviewers
2. Other reviewers who receive the finding can:
   - **CHALLENGE** it with counter-evidence (direct message to finder + architect)
   - **Agree** — confirms severity, increases confidence
   - **Ignore** — outside their domain, no response required
3. The architect receives every finding and every challenge/agreement
4. The architect creates a task for the finding via TaskCreate (see `team-communication-protocol.md` for task schema)

This preserves the independent-review value (research: most gains from ensembling, ICLR Blog 2025) while enabling organic conflict resolution.

## Architect as Real-Time Tiebreaker

When two reviewers disagree (CHALLENGE exchange), the architect reads both positions and breaks the tie immediately:

| Situation | Architect Action |
|-----------|-----------------|
| Evidence clearly favors one side | Resolve in favor of the supported position, cite evidence |
| Both sides have merit | Merge into a nuanced finding that captures both concerns |
| Both sides speculative | Classify as INVESTIGATE or DECIDE (user resolves) |
| Same finding, different severity | Calibrate — use higher severity, note the disagreement |

**Research basis:** "Judge-managed adaptive breaking outperforms fixed-round approaches" (Liang et al. EMNLP 2024). The architect's judgment is final for reviewer-reviewer disputes. If the architect is genuinely uncertain — DECIDE classification (user resolves).

## Anti-Conformity Safeguard

The architect tracks which reviewers originally held which positions. If a reviewer flips position after seeing a challenge, the architect:

1. Notes the flip explicitly
2. Evaluates whether the original position had merit
3. If the flip looks like social pressure rather than genuine evidence-based reconsideration, retains the original finding with a note

**Research:** LLMs exhibit conformity bias — initially correct agents update toward incorrect majorities under social pressure (FREE-MAD, arXiv:2509.11035).

## Deduplication (Architect, Continuous)

The architect deduplicates as findings arrive:

| Situation | Dedup Rule |
|-----------|-----------|
| Multiple reviewers find the same issue | Merge into one finding, cite all agents, mark high confidence |
| Same file+line, different categories | Separate findings — different concerns deserve separate tracking |
| Overlapping findings with different scopes | Merge if root cause is the same; keep separate if different fixes needed |

## Fix Phase — Fixer-Reviewer-Architect Collaboration

During the fix phase, debate continues organically between fixers and reviewers:

1. **Fixer disagrees with a finding** — CHALLENGE to the reviewer who found it
   - Reviewer responds with evidence (one exchange)
   - If unresolved — ESCALATION to architect who breaks the tie
2. **Fixer requests validation** — REVIEW_REQUEST to a reviewer
   - Reviewer steers with guidance (STEER messages)
3. **Architect monitors** — receives all FIX_COMPLETE and resolution confirmations, maintains the shared task list

## Convergence Criteria

### Review Phase Ends When:
- All reviewers idle (TeammateIdle notifications)
- All outstanding challenges resolved by architect
- The shared task list is stable (no new findings arriving)

### Fix Phase Ends When:
- All FIX findings in the shared task list show "completed" (reviewer-validated)

### 3-Strike Rule:
- If a fixer and reviewer cycle 3 times on the same finding without converging
- Architect breaks the tie
- If still stuck — escalate to user via AskUserQuestion

## Architect Prompt Template

```
You are the team's software architect, serving as mediator and master list builder.

DURING REVIEW:
- Receive all FINDING messages from reviewers
- Create a task for each finding via TaskCreate with metadata (severity, file, line, found_by, classification)
- When you see CHALLENGE messages between reviewers:
  - Read both positions
  - Break the tie immediately -- cite specific evidence
  - Update the task metadata with your resolution rationale
- Merge duplicate findings (same file+line), cite all agents
- Track position flips (conformity bias safeguard)
- When all reviewers are idle and all challenges resolved:
  - Classify each finding: FIX / INVESTIGATE / DECIDE / PRE-EXISTING
  - Present DECIDE items to the lead for user escalation
  - Signal "review complete"

DURING FIX:
- Assign FIX findings to fixer teammates (FIX_REQUEST)
- Receive ESCALATION messages from fixer-reviewer disagreements -- break ties
- Monitor FIX_COMPLETE and reviewer confirmations -- mark tasks completed via TaskUpdate
- Sequence same-file fixes via task dependencies (addBlockedBy)
- Check TaskList periodically -- when all FIX tasks show "completed" -> signal "fix complete"
```

## Research Citations

These citations document why specific design choices were made. They are included for future reference when evaluating whether to modify this protocol.

1. **Du et al. (2023)** — "Improving Factuality and Reasoning in Language Models through Multiagent Debate." Established that multi-agent debate improves LLM output quality.

2. **Liang et al. (2024)** — "Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate" (EMNLP 2024). Introduced MAD (Multi-Agent Debate) with judge-managed adaptive breaking. Key finding: judge-managed adaptive breaking outperforms fixed-round approaches.

3. **"Should We Be Going MAD?" (2025)** — ICLR Blog post analyzing debate literature. Key finding: "most gains attributed to debate are actually attributable to ensembling" — independent review is the primary value driver, not the debate itself.

4. **FREE-MAD (2025)** — arXiv:2509.11035. Demonstrated conformity bias in LLM debate: initially correct agents update toward incorrect majorities. Introduced the anti-conformity safeguard pattern.

5. **"Voting or Consensus? A Study of Multi-LLM Agent Debate Strategies" (2025)** — ACL 2025. Key finding: additional debate rounds beyond 2-3 often decrease performance by causing problem drift or error propagation through conformity pressure.

6. **"Can LLM Agents Really Debate?" (2025)** — arXiv:2511.07784. Analyzed actual debate dynamics in multi-agent LLM systems.

7. **S2-MAD (2025)** — arXiv:2502.04790. Structured approaches to multi-agent debate with improved convergence properties.
