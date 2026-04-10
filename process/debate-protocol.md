# Multi-Agent Debate Protocol

Defines how the `review-team` skill resolves conflicting findings between domain agents. Grounded in multi-agent debate research — citations at the end.

## Design Principles

1. **Independent review is the primary value driver.** Most gains attributed to debate are actually attributable to ensembling — agents reviewing independently without seeing each other's work (Du et al. 2023, "Should We Be Going MAD?" ICLR Blog 2025).
2. **Debate resolves conflicts, not consensus.** The goal is not agreement — it's evidence-based resolution of contradictions.
3. **Fewer rounds is better.** Additional rounds beyond 2-3 decrease performance through conformity pressure and problem drift (FREE-MAD, "Voting or Consensus?" ACL 2025).
4. **Judge-managed adaptive breaking outperforms fixed rounds.** The lead decides when evidence is sufficient, rather than always running a fixed number of rounds (Liang et al. EMNLP 2024).

## Protocol Phases

### Phase 1 — Independent Review

All teammates review the diff in parallel with **no inter-agent communication**. This preserves confirmation-bias prevention — each agent forms an independent opinion before seeing others' findings.

Each teammate posts findings as task completions with these required fields:
- `file` — path and line range
- `finding` — what the issue is
- `severity` — critical / major / minor
- `category` — overengineering / type-safety / security / contract / DRY / architecture / correctness
- `evidence` — specific code or guarantee that supports the finding
- `recommendation` — what should change

### Phase 2 — Conflict Detection

The software-architect subagent scans all Phase 1 findings for conflicts:

| Conflict type | Detection rule |
|---------------|---------------|
| Contradictory assessment | Same file+line range, opposite conclusions (e.g., "remove this" vs "this is correct") |
| Severity disagreement | Same issue identified by multiple agents, different severity ratings |
| Contradictory recommendation | Different agents recommend incompatible changes to the same code |

Non-conflicting findings pass through directly to synthesis.

### Phase 3 — Round 1: Targeted Exchange

For each detected conflict, the lead creates debate tasks for the conflicting agents:

- Each agent receives: the other agent's finding + evidence
- Each agent posts **one response**: agree, disagree with evidence, or propose compromise
- Responses must cite specific code, type guarantees, or framework behavior — not general reasoning

### Phase 4 — Lead Judgment (Adaptive Break)

The software-architect subagent reads both Round 1 positions for each conflict:

- **If evidence clearly resolves the conflict** → mark as resolved, use the supported finding (early termination)
- **If not resolvable from Round 1 evidence** → formulate a specific question for Round 2, explaining what evidence would resolve it

This is the adaptive break point. Research shows judge-managed adaptive breaking outperforms fixed-round approaches (Liang et al. EMNLP 2024).

### Phase 5 — Round 2: Conditional Rebuttal

Only fires for conflicts not resolved in Round 1. For each:

- Each conflicting agent gets: the lead's specific question + the other agent's Round 1 response
- Each posts **one response** — no further rounds

### Phase 6 — Escalation

If a conflict remains unresolved after Round 2:

- Classify the finding as `DECIDE` — user must resolve
- Present both positions with their evidence
- Do NOT pick a winner without evidence — that's conformity, not judgment

## Anti-Conformity Safeguard

When an agent changes position between rounds (flips from "this is a bug" to "actually it's fine", or vice versa), the lead must:

1. Flag the flip explicitly in the synthesis report
2. Evaluate whether the original position had merit
3. If the flip looks like social pressure rather than genuine evidence-based reconsideration, retain the original finding with a note

Research: LLMs exhibit conformity bias — initially correct agents update toward incorrect majorities under social pressure (FREE-MAD, arXiv:2509.11035).

## Synthesis Rules

After debate completes, the architect produces the final report:

| Situation | Synthesis rule |
|-----------|---------------|
| Same finding from multiple agents | One finding, cite all agents (higher confidence) |
| Severity disagreement (resolved) | Use the converged severity |
| Severity disagreement (unresolved) | Use higher severity, note the disagreement |
| Contradictory assessment (resolved) | Use the finding supported by evidence |
| Contradictory assessment (unresolved) | Present both with `DECIDE` classification |
| Agent flipped position | Note the flip, evaluate if original had merit |

The output format matches `review-diff` and `review-commit` findings tables so that `review-fix` works unchanged.

## Research Citations

These citations document why specific design choices were made. They are included for future reference when evaluating whether to modify this protocol.

1. **Du et al. (2023)** — "Improving Factuality and Reasoning in Language Models through Multiagent Debate." Established that multi-agent debate improves LLM output quality.

2. **Liang et al. (2024)** — "Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate" (EMNLP 2024). Introduced MAD (Multi-Agent Debate) with judge-managed adaptive breaking. Key finding: judge-managed adaptive breaking outperforms fixed-round approaches.

3. **"Should We Be Going MAD?" (2025)** — ICLR Blog post analyzing debate literature. Key finding: "most gains attributed to debate are actually attributable to ensembling" — independent review is the primary value driver, not the debate itself.

4. **FREE-MAD (2025)** — arXiv:2509.11035. Demonstrated conformity bias in LLM debate: initially correct agents update toward incorrect majorities. Introduced the anti-conformity safeguard pattern.

5. **"Voting or Consensus? A Study of Multi-LLM Agent Debate Strategies" (2025)** — ACL 2025. Key finding: additional debate rounds beyond 2-3 often decrease performance by causing problem drift or error propagation through conformity pressure. Validates the 2-round maximum.
