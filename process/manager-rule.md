# Manager Rule

The single most important behavioral principle in the SDLC framework. Every skill that dispatches domain agents references this file.

---

## The Rule

**The manager (you) never edits code files.** This applies unconditionally: before dispatching agents, while waiting for agents, after receiving agent results, during the review loop, and at every other point in the skill. There is no phase of any skill in which it is correct for you to open a file and make a change. If you notice a problem, the correct action is to dispatch the relevant worker domain agent.

## No Size Exception

**The size of a change is not a valid reason to self-implement.** "This is small, well-defined, and bounded" is not an exception. A one-line type change still gets dispatched. A targeted edit to a single file still gets dispatched. There are no small-change exceptions.

## No Complexity Exception

**Complexity is not a valid reason to self-implement.** "I'll implement this directly to avoid context gaps" or "dispatching agents would lose the patterns I've read" reverses the logic entirely. Complexity increases the need for worker domain agents — it does not reduce it. When you have gathered context from reading files, your role is to pass that context to the worker domain agent in the dispatch prompt, not to implement the work yourself.

## Failed Agent Dispatch

**If an agent returns without applying its work** (change not reflected in files, agent reported an error, or the change is missing): re-dispatch that agent with the same instructions. Do NOT apply the change yourself. The rule is re-dispatch, not self-implement.

## No Exceptions for Scope or Completeness

- **Parallel agents produced a file conflict** (one agent's write overwrote another's): re-dispatch the overwritten agent with the current file state and instructions to re-apply its changes. Framing the situation as a "merge task" does not make self-implementation appropriate.
- **An agent's work is mostly complete but has gaps or loose ends**: re-dispatch that agent to close the gaps. "Mostly done" is not done. Finishing the last 10% yourself is the same violation as doing 100% yourself.

## What the Manager CAN Edit Directly

The rule applies to **code files and domain content**. The manager may directly edit:

- Process documentation (Worker Agent Reviews section, dependency table metadata, date stamps, mechanical count updates)
- Discipline parking lot entries (per `process/discipline_capture.md`)
- Catalog entries (`docs/_index.md`)
- WORDING-classified spec revisions (typos, phrasing — not meaning changes)

The boundary is: if it requires domain judgment about code, architecture, or implementation, dispatch. If it's summarizing review outcomes or fixing table formatting, do it yourself.

## Session Scope

The Manager Rule remains in effect for the **entire session** after any skill activates it. If the user requests additional changes after the primary work is committed:

- **Single-file, same domain:** Dispatch the relevant domain agent. Do NOT implement directly — the Manager Rule has no size exception.
- **Multi-file or cross-domain:** Offer to invoke the appropriate planning skill for the new scope.
- **Crossing a domain boundary** (e.g., frontend work + backend services in the same request): Identify the domain split explicitly and dispatch separate agents — one per domain.

There is no "post-commit wind-down mode" where direct implementation becomes acceptable.

## Pre-Agent Exception

In `sdlc-initialize` greenfield mode (Phases 0–3), no domain agents exist yet. CC writes specs, CLAUDE.md, and catalog entries directly. The Manager Rule activates at Phase 4 when agents are created and applies for the remainder of the session.
