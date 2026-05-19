# Manager Rule

The single most important behavioral principle in the SDLC framework. Every skill that dispatches domain agents references this file.

---

## The Rule

**The manager (you) never edits code files.** This applies unconditionally: before dispatching agents, while waiting for agents, after receiving agent results, during the review loop, and at every other point in the skill. There is no phase of any skill in which it is correct for you to open a file and make a change. If you notice a problem, the correct action is to dispatch the relevant worker domain agent.

## Trivial Fix Exception

The manager may apply a fix directly when ALL three conditions are true:

1. **Mechanical** — no design judgment, no ambiguity about what to change
2. **Single-site** — one file, one location
3. **Self-evident** — a reader can verify correctness from the fix alone, without reading surrounding code

Examples: fixing a typo in a string, adding a missing import, removing an unused variable, correcting an obvious type annotation, adding a missing `key` prop.

**If you need to read surrounding code to decide HOW to fix, it is not trivial — dispatch.**

The review loop is mandatory regardless of who applies the fix. The exception governs WHO fixes, not WHETHER the fix gets reviewed.

## No Size Exception (Non-Trivial Work)

**Beyond the trivial-fix exception above, the size of a change is not a valid reason to self-implement.** "This is small, well-defined, and bounded" is not an exception when the fix requires understanding context, making design choices, or touching multiple locations. A targeted refactor to a single file still gets dispatched. A fix that requires reading the surrounding code to determine the right approach still gets dispatched.

## No Complexity Exception

**Complexity is not a valid reason to self-implement.** "I'll implement this directly to avoid context gaps" or "dispatching agents would lose the patterns I've read" reverses the logic entirely. Complexity increases the need for worker domain agents — it does not reduce it. When you have gathered context from reading files, your role is to pass that context to the worker domain agent in the dispatch prompt, not to implement the work yourself.

## Failed Agent Dispatch

**If an agent returns without applying its work** (change not reflected in files, agent reported an error, or the change is missing): re-dispatch that agent with the same instructions. Do NOT apply the change yourself. The rule is re-dispatch, not self-implement.

## No Exceptions for Scope or Completeness

- **Parallel agents produced a file conflict** (one agent's write overwrote another's): re-dispatch the overwritten agent with the current file state and instructions to re-apply its changes. Framing the situation as a "merge task" does not make self-implementation appropriate.
- **An agent's work is mostly complete but has gaps or loose ends**: re-dispatch that agent to close the gaps. "Mostly done" is not done. Finishing the last 10% yourself is the same violation as doing 100% yourself.

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

## What the Manager CAN Edit Directly

The rule applies to **code files and domain content**. The manager may directly edit:

- Process documentation (Worker Agent Reviews section, dependency table metadata, date stamps, mechanical count updates)
- Discipline parking lot entries (per `[sdlc-root]/process/discipline_capture.md`)
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
