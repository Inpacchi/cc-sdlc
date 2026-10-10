# Handoff: catch deliverables that depend on unplanned or unshipped prerequisites

**Date:** 2026-10-09
**From:** the software-factory session (cc-sdlc + quantile)
**For:** a fresh cc-sdlc session
**Status:** problem agreed with CD; nothing built

## What happened (quantile D11)

- **2026-09-30:** a feasibility audit counted 11 phases for D11. CD split it into **D11a → D11b → D11c** (quantile commit `314c747`). D11a (interval unification) was marked lite and already had a design from an earlier post-mortem (`scratchpad/adr08_interval_unification_design.md`). It was treated as "designed", so it never got a spec or plan.
- **2026-10-01:** the D11b and D11c specs were approved. D11c was written early on purpose: its graduation bar had to be pre-registered before D11b ships.
- **2026-10-02:** the D11b plan was reviewed over 3 rounds. It gates explicitly on D11a ("Gate G-D11a" blocks its Phase 6 and the final candidate run).
- **2026-10-06/07:** D12 took priority. D11a was never picked back up.
- **2026-10-09:** CD found D11b planned and waiting for approval while its prerequisite D11a sat in Draft, with no spec, no plan and no code. CD asked how D11b got planned first.

**Diagnosis:** planning D11b before D11a was fine, because D11a blocks D11b's execution, not its planning. The failure was that D11a dropped out of sight. Dependencies between deliverables live only in prose: catalog row text, the split commit message, and the D11b plan's gate. No skill reads them, so nothing surfaced that a planned deliverable depended on an unplanned one.

## The rule to add

When a deliverable depends on another, the dependency is recorded where tools can read it, and the framework surfaces three things:
1. **Blocked:** a deliverable whose prerequisite is unplanned or unshipped.
2. **Execution risk:** a deliverable about to start execution (or whose blocked phase is about to start) while a prerequisite isn't done.
3. **Forgotten work:** a prerequisite that no active work is moving forward.

## What to build (suggested; the receiving session decides)

1. **Record dependencies in a structured form.**
   - **Option A:** a `Depends on` column in the deliverable catalog (`docs/_index.md`, template in `[sdlc-root]/templates/`), listing IDs: `D11a`, optionally `D11a (blocks Phase 6)`.
   - **Option B:** a `depends_on:` frontmatter field in specs and plans.
   - **Recommendation:** the catalog column. It's the single source of truth for IDs and statuses, and `sdlc-status` already reads it.
   - **Who fills it:** the split step in `sdlc-plan`'s Feasibility Gate, and any spec or plan that names a gate on another deliverable.
2. **Check it in the skills that would have caught D11:**
   - **`sdlc-status`:** list blocked deliverables, and prerequisites that nothing active is moving forward.
   - **`sdlc-plan` / `sdlc-lite-plan`, at registration and at plan approval:** if a prerequisite has no plan, say so in the plan and the completion report, and offer to plan the prerequisite next. In a headless run, put it in the result's `notes`, and in the PR description's review focus.
   - **`sdlc-execute` / `sdlc-lite-execute`, at load:** if a prerequisite isn't Complete, stop before any phase it gates (headless: `needs-input`). Phases that don't depend on it may proceed when the plan says so, as D11b's does.
   - **`sdlc-plan`'s split step:** for each split-off deliverable that "already has a design", register it with a plan, or leave an explicit next action, so it isn't left as Draft-with-a-design.
3. **Audit:** `sdlc-compliance-auditor` flags catalog rows with a dependency on a missing ID, cycles, and Draft prerequisites of Ready or In Progress deliverables.
4. **Migration:** add the catalog column through `sdlc-migrate`, with an empty default. Existing projects back-fill it by hand, or from a one-time scan of plan and spec text for "depends on" or "Gate G-Dnn" phrases, proposed for CD to confirm.

## Constraints

- **cc-sdlc `CLAUDE.md` applies:** directive = framework change, changelog entry in the same step, consistency checks, `[sdlc-root]` paths, and the manifest kept in sync.
- **Release type:** a new catalog column that projects write is a new data schema, so a **minor** bump by `CLAUDE.md` § Versioning. It's purely additive, with a back-fill default. Don't cut a tag without CD's request.
- **The software factory reads the catalog too.** quantile's plan stage reserves IDs from `docs/_index.md` (`.github/workflows/factory-plan.yml`, claim job). A new column mustn't break its `Next ID` and row parsing (`^\| *\[?D[0-9]+`).
- **Keep it light.** One column and a few checks, not a dependency-graph engine.

## Open questions for CD

1. Catalog column (recommended) or document frontmatter?
2. Should `execute` hard-stop on an unshipped prerequisite, or only warn? The recommendation is to stop before gated phases only.
3. Should quantile's existing D11 rows be back-filled as part of this work (D11b depends on D11a; D11c on D11b), or by hand?
