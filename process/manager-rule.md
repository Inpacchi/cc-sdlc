# Manager Rule

The single most important behavioral principle in the SDLC framework. Every skill that dispatches domain agents references this file.

---

## The Rule

**The manager (you) dispatches domain agents by default — for all code, specs, plans, and domain content.** Direct implementation is permitted only under the Delegation Economics Exception below, and every manager-applied change must be reviewed by the relevant domain agent(s) before commit. The manager never self-approves. If a problem falls outside the exception's bounds, the correct action is to dispatch the relevant worker domain agent.

The rule is economic, not ceremonial: the manager's context window is the scarcest resource in the session, and delegation keeps it small. The exception exists for the cases where delegation is the more expensive path.

## Delegation Economics Exception

The manager may apply a change directly when delegation would cost more than the change itself — monetarily (dispatch overhead: the agent re-loading context the manager already holds, plus handoff) or in main-context growth. ALL conditions must hold:

1. **Small and bounded** — a few edit sites; no new abstractions (components, hooks, stores, routes, types, events); no cross-domain coordination
2. **No design judgment** — mechanical, or follows an established pattern the manager can cite. Competing approaches or tradeoffs disqualify.
3. **Context-neutral** — the manager can decide HOW from context already in the window. If deciding requires paging in surrounding code, dispatch — acquiring context in order to self-implement is exactly the cost this exception exists to avoid, and "I'll read the files first, then it's cheaper to do it myself" is the loophole that swallows the rule.
4. **Reviewed** — the change enters the same review loop as agent work before commit (see Mandatory Review below)

Trivial fixes always qualify: a typo in a string, a missing import, an unused variable, an obvious type annotation, a missing `key` prop.

**Boundaries that hold regardless of economics:**
- Specs, plans, and plan revisions stay agent-written (except WORDING-class edits, which were always orchestrator-editable)
- Architectural and product decisions stay with agents and CD
- High-risk domains (auth, payments, permissions, migrations, concurrency — per the infrastructure domains in `[sdlc-root]/process/agent-selection.yaml`) allow only trivial-class manager fixes, and their review uses the risk-escalated tier from `[sdlc-root]/knowledge/architecture/model-tier-strategy.yaml` (MTS4)

When the conditions are debatable, dispatch — the default is delegation.

## Mandatory Review of Manager-Applied Changes

**Self-applied is never self-approved.** Every change the manager applies under the exception is reviewed by the relevant domain agent(s) before commit — the same review loop agent work goes through. Batch multiple small manager changes into a single review dispatch to keep the economics favorable. If a reviewer finds that a self-applied change involved design judgment after all, the finding routes to a domain agent for the fix — do not defend the change; re-dispatch it.

## No Complexity Exception

**Complexity is not a valid reason to self-implement.** The economics exception covers small mechanical work only. "I'll implement this directly to avoid context gaps" or "dispatching agents would lose the patterns I've read" reverses the logic entirely. Complexity increases the need for worker domain agents — it does not reduce it. When you have gathered context from reading files, your role is to pass that context to the worker domain agent in the dispatch prompt, not to implement the work yourself.

## Failed Agent Dispatch

**If an agent returns without applying its work** (change not reflected in files, agent reported an error, or the change is missing): re-dispatch that agent with a revised prompt. Do NOT absorb the work yourself by default. If a re-dispatch also fails and the *remaining gap* passes the Delegation Economics Exception test, the manager may close it directly (with review) — re-dispatching a full agent to add one missed line costs more than the line. If the gap doesn't qualify, re-dispatch again or escalate to CD.

## No Exceptions for Scope or Completeness

- **Parallel agents produced a file conflict** (one agent's write overwrote another's): re-dispatch the overwritten agent with the current file state and instructions to re-apply its changes. Reconciling two agents' intents is judgment work — the economics exception does not apply to merges.
- **An agent's work is mostly complete but has gaps or loose ends**: apply the economics test to the gap itself. A genuinely small, mechanical gap (a missed rename, an unexported symbol) may be closed directly with review. A gap requiring design judgment or new context gets re-dispatched — finishing a meaningful fraction of the agent's work yourself is the same violation as doing all of it yourself.

## No Revert Without Authorization

**Never run `git checkout --`, `git restore`, `git stash`, or any working-tree-destructive command on files you did not create or modify in the current session.** The working tree may contain uncommitted changes from prior sessions or concurrent work by the user. A `git checkout --` on such a file destroys that work irreversibly — there is no undo.

When an agent modifies a file not in the plan:
1. Log the deviation in the POST-GATE output
2. Include it in the result doc
3. **Do not revert the file** — the agent may have had a legitimate reason, or the file may contain the user's concurrent work mixed with the agent's changes
4. If the deviation is concerning, ask the user via `AskUserQuestion` whether to revert, keep, or investigate

The only files safe to revert are files you (or your dispatched agents) created from scratch in the current session. For everything else, reverting requires explicit user authorization via `AskUserQuestion`.

## No Semantic Revert (Fix Must Preserve Intent)

**Fixing a bug in user-requested behavior by removing the behavior is not a fix — it is a revert disguised as one.** This applies whether the "revert" is a `git checkout`, a replacement with a static value, or a reimplementation that drops the requested functionality.

When behavior the user requested has a bug:
1. **Identify the root cause** — not the feature, but the interaction that makes it malfunction
2. **Fix the root cause while preserving the behavior** — debounce, guard, batch, defer, or restructure the implementation to keep what the user asked for
3. **If the behavior is genuinely impossible** given system constraints, say so explicitly: "This behavior conflicts with [X] because [Y]. The options are [A] or [B]." Then wait for direction.

**Never do any of these without explicit user authorization:**
- Replace a dynamic/computed value with a static one ("just use 40 instead of columns * 5")
- Remove a feature that has a bug ("the fix is to not do this")
- Simplify requested behavior to a subset that doesn't have the bug ("we'll do the easy version")
- Frame removal as pragmatism ("the pragmatic fix is to not tie it to X")

**The test:** After your fix, does the feature still do what the user originally asked for? If the answer is no, you have not fixed a bug — you have reverted a feature. Stop and ask.

## No Unilateral Finding Demotion

A FIX-classified finding cannot be reclassified, downgraded, or closed as "accepted risk" by the manager without CD approval. This applies to all severities but is mandatory for major and critical.

**Permitted reclassifications (with evidence):**

- **FIX → INVESTIGATE:** Additional investigation would materially change the fix approach. State the open question.
- **FIX → DECIDE:** The finding reveals a genuine trade-off between acceptable alternatives. Present the alternatives to CD.
- **FIX → PRE-EXISTING:** The affected code was not touched by this work (per `[sdlc-root]/process/finding-classification.md` § PRE-EXISTING Qualification).

**Not permitted without CD approval:**

- Converting a code fix to documented-risk annotations (inline comments, TODO markers, or "accepted risk" labels do not resolve a FIX finding)
- Deferring a major/critical finding to a follow-up without CD sign-off
- Reframing a recommended implementation as unnecessary for the current change

**Open minors at loop exit are not demotion.** A review loop exits when no critical or major FIX findings remain (`[sdlc-root]/process/review-fix-loop.md` § Exit Bar). Listing the minor FIX findings still open at that point in an **Open Minor Findings** table, visible to CD (`[sdlc-root]/process/finding-classification.md` § Open Minor Findings), is permitted and is not demotion. Closing an entry — marking it resolved, accepted, or won't-fix — still requires CD. Downgrading a finding's severity so the exit bar is met *is* demotion.

**Escalation procedure:** When the manager believes a finding should be accepted rather than fixed, present it to CD via `AskUserQuestion` with: the finding, the recommended fix, the rationale for acceptance, and the conditions that would change the assessment. Do not close the finding until CD responds.

## What the Manager CAN Edit Directly

The rule applies to **code files and domain content**. The manager may directly edit:

- Process documentation (Worker Agent Reviews / Domain Agent Reviews sections, the Open Minor Findings table appended after them, dependency table metadata, date stamps, mechanical count updates)
- Discipline parking lot entries (per `[sdlc-root]/process/discipline_capture.md`)
- Catalog entries (`docs/_index.md`)
- WORDING-classified spec revisions (typos, phrasing — not meaning changes)

The boundary is: if it requires domain judgment about code, architecture, or implementation, dispatch. If it's summarizing review outcomes or fixing table formatting, do it yourself. For code changes, the Delegation Economics Exception above governs — and it always ends in review.

## Session Scope

The Manager Rule remains in effect for the **entire session** after any skill activates it. If the user requests additional changes after the primary work is committed:

- **Single-file, same domain:** Apply the Delegation Economics Exception test. If the change qualifies (small, no design judgment, no new context needed), self-apply and route it through review; otherwise dispatch the relevant domain agent.
- **Multi-file or cross-domain:** Offer to invoke the appropriate planning skill for the new scope.
- **Crossing a domain boundary** (e.g., frontend work + backend services in the same request): Identify the domain split explicitly and dispatch separate agents — one per domain.

There is no "post-commit wind-down mode" where direct implementation becomes acceptable.

## Pre-Agent Exception

In `sdlc-initialize` greenfield mode (Phases 0–3), no domain agents exist yet. CC writes specs, CLAUDE.md, and catalog entries directly. The Manager Rule activates at Phase 4 when agents are created and applies for the remainder of the session.
