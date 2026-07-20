# Codebase Health Mode — Methodology

Audits the product substrate: the codebase's ability to catch bugs before they ship and to be worked on safely by agents. Three parallel read-only sweeps, each returning **what exists / what's missing / top-5 gaps most likely to let bugs ship**. This mode never modifies files — findings route into handoffs, plans, or parking lots.

## Dispatch Discipline

- One read-only research agent per sweep, dispatched in parallel. Do NOT use `sdlc-compliance-auditor` (process-scoped) or domain worker agents (they carry fix instincts — this is inventory, not repair).
- Each agent receives: the sweep prompt below, the scope (whole repo or a path), and the instruction to return the structured sweep report — no fixes, no file edits, no opinions on priorities beyond the top-5 ranking rationale.
- Scoped runs (`/sdlc-audit health <path>`) pass the path to all three sweeps; sweep-name runs (`tests`, `ergonomics`, `observability`) dispatch only that sweep repo-wide.

## Sweep 1 — Test & CI Activation

> Inventory the project's automated verification and report where it is inactive or hollow. Read-only. Check:
>
> 1. **Test-to-source ratios per package** — count test files vs source files for each package/top-level module. Flag packages at or near zero.
> 2. **Suites that exist but never run** — cross-reference test directories against CI configuration (workflow files, pipeline configs, pre-commit hooks). A suite not wired into any gate is documentation, not protection.
> 3. **Gate coverage** — which of lint / typecheck / format / test run in CI, per package? Which packages lack the scripts entirely? Is there a single discoverable one-shot verify command at the root (see `[sdlc-root]/process/verify-command.md` convention — e.g., `npm run verify`, `make verify`, `./scripts/verify.sh`)?
> 4. **Runtime validation at trust boundaries** — where does external data enter (API handlers, webhooks, queue consumers, file imports, env config)? Which entry points parse/validate shape (schema validation, type guards) vs cast and hope?
>
> Return: what exists (inventory with counts), what's missing (per package), top-5 gaps most likely to let bugs ship, each with a one-sentence "why this one" rationale.

## Sweep 2 — Agentic Ergonomics

> Inventory how safely and efficiently an agent can work in this codebase. Read-only. Check:
>
> 1. **CLAUDE.md coverage and accuracy** — which packages have a CLAUDE.md? For each that exists, spot-check 3-5 claims against the code (paths exist? commands run? conventions still followed?). A wrong CLAUDE.md is worse than a missing one.
> 2. **Hot spots** — the largest files by line count and the most-churned files (git log frequency). Files that are both large and hot are where agent edits go wrong.
> 3. **Duplication and fork patterns** — parallel copies of logic, components, or config that must be manually kept in sync. Any "KEEP IN SYNC"-style comment is a defect marker (Contract Safety Lens, `[sdlc-root]/process/review-lenses.md`).
> 4. **Dead weight** — unreferenced files, commented-out blocks over ~20 lines, dependencies in the manifest that nothing imports.
> 5. **Script discoverability** — can an agent find how to build, test, and verify from the root README/CLAUDE.md/package manifest without spelunking? Is there a one-shot verify?
> 6. **Type-safety escape hatches** — count `any`, `@ts-ignore`, `eslint-disable`, unchecked casts (or the language's equivalents) and report where they cluster. Clusters mark the modules where the type system has been opted out of.
>
> Return: what exists, what's missing, top-5 gaps most likely to let bugs ship, each with a one-sentence "why this one" rationale.

## Sweep 3 — Observability Blind Spots

> Inventory the project's ability to notice its own failures. Read-only. Check:
>
> 1. **Error-reporting coverage per surface** — which runtime surfaces (web app, API, workers, scheduled jobs, CLIs) report errors to a tracking service or structured log, and which fail invisibly?
> 2. **Swallowed catches** — count catch blocks that neither rethrow, report, nor meaningfully handle (empty catch, `console.log` only, catch-and-return-default). Report where they cluster.
> 3. **Structured logging presence** — is there a logging convention (levels, correlation IDs, structured fields), or ad-hoc prints? Per surface.
> 4. **Scheduled-job failure alerting** — for each cron/scheduled/queue job: if it fails or silently stops running, what notices? "Nothing" is the finding.
> 5. **Silent fallbacks** — defaults that mask failure: empty-array returns on fetch errors, cached values served past expiry without flagging, feature code that no-ops when config is missing.
>
> Return: what exists, what's missing, top-5 gaps most likely to let bugs ship, each with a one-sentence "why this one" rationale.

## Report Format

Write to `docs/current_work/audits/codebase_health_YYYY-MM-DD.md`:

```markdown
# Codebase Health Audit — YYYY-MM-DD

Scope: {whole repo | path | single sweep}
Sweeps: {3/3 | which}

## Summary

| Sweep | Exists | Missing | Top gap |
|-------|--------|---------|---------|
| Test & CI activation | {one-line inventory} | {one-line} | {gap #1} |
| Agentic ergonomics | ... | ... | ... |
| Observability | ... | ... | ... |

## Top Gaps (merged, ranked)

| # | Gap | Sweep | Likely failure it permits | Suggested route |
|---|-----|-------|---------------------------|-----------------|
| 1 | {gap} | {sweep} | {what ships broken because of this} | handoff / plan / lite-plan / parking lot |

## Sweep Detail
{each sweep's full exists/missing/top-5 report}
```

Merged ranking: order by (likelihood a real bug ships undetected) × (blast radius when it does). Cap the merged list at 10 — a 30-item list is a backlog, not an audit.

## Routing Rules

- **Route, don't fix.** Present the merged top gaps; CD picks which become work. Accepted gaps go to `sdlc-handoff` (cross-session tracks), `sdlc-plan`/`sdlc-lite-plan` (work starting now), or discipline parking lots (insights needing validation).
- **Cross-reference recurring patterns.** If a gap matches a cluster in `docs/reviews/recurring-patterns.yaml`, cite the cluster slug in the report. A health gap corroborated by recurrence history is a guard-promotion signal — note it for the next compliance audit's 6l triage (`[sdlc-root]/process/guardrail-lifecycle.md`).
- **No silent scope caps.** If a sweep sampled (e.g., spot-checked 5 of 40 CLAUDE.md claims), the report says so — sampled coverage presented as full coverage is itself a health defect.
