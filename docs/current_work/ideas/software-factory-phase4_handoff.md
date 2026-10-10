# Handoff: build the factory's weekly improve loop (phase 4)

**Date:** 2026-10-10
**From:** the software-factory session (cc-sdlc + quantile)
**For:** a fresh session
**Status:** design cross-checked by Fable and Codex; CD's decisions recorded below; nothing built

## Read first

1. `docs/current_work/ideas/software-factory-phase4-services_design.md`, **Part A** and **Cross-check results**. It's the design and its review corrections. Part B (services) is already built.
2. `docs/current_work/ideas/software-factory_design.md`, D1–D3, the factory's rules, and `software-factory_handoff.md` for how the factory got here.
3. In `endless-galaxy-studios/quantile`:
   - `.github/factory/README.md` (stage contract, Follow-ups, Revise, Services);
   - `.github/workflows/factory-*.yml`;
   - `.github/factory/implement_guard.py`, `follow_ups.py`, `workflow_policy.py`.

## What the loop is for

Once a week, read the factory's own GitHub record of what CD did to its output, and turn that into a **report CD acts on**: concrete improvements, each with its evidence, or an explicit statement that nothing needs action. The factory learns from CD's corrections instead of repeating them.

## CD's decisions (2026-10-10)

1. **Cadence:** weekly on **Sunday**, cron `23 22 * * 0`. That's 22:23 UTC: 18:23 Eastern in summer, 17:23 in winter (cron is UTC). It runs off the hour because GitHub delays or drops schedules near the top of the hour. Add manual dispatch with a window, and catch-up from the last successful harvest so a missed run loses nothing. CD may adjust the time.
2. **Report only** to start. The weekly run posts a report issue and changes nothing. Hygiene PRs (knowledge YAMLs, discipline parking lots, the changelog) come in a later step, after a dedicated `improve` guard stage exists. Skills, agents, process docs and anything code-owned stay CD-applied.
3. **The report must be substantial and actionable:**
   - **Every item is actionable:** what to change, where (file, workflow, skill, setting), why (evidence links), and the expected effect. Or the report says plainly that **nothing needs action this week**. Never filler, never observations with no recommendation.
   - **It advises on everything,** not only skills. At minimum it covers these sections, each one either with items or "nothing to action":
     - **Factory process:** stage flow, triage calibration (tier and advisor choices CD overrode), the revise and follow-up mechanics, holds and releases, failure patterns, cost and turns by stage.
     - **SDLC content:** skills, agents, process docs, templates, discipline parking lots, knowledge stores (stale, contradicted or missing entries).
     - **The framework (cc-sdlc):** problems whose fix belongs upstream, for example a headless rule, a skill every project shares or a template. These go in a "For cc-sdlc" section CD carries upstream until cc-sdlc moves into the org (then they can be filed there).
     - **Factory infrastructure:** workflows, guards, policy check, runners, images, smoke coverage, the security boundary.
     - **The project itself, where the evidence points there:** recurring code areas that cause rework, missing tests, docs gaps.
   - **Ranked:** the top items first, with severity. The rest stay in the body, grouped by section. Cap the number of action items so the report stays readable (the design suggests five headline items), but never drop one silently; list overflow briefly.
   - **Tracked across weeks:** each proposal has a stable fingerprint. New evidence is appended to an existing proposal, which isn't re-proposed. Status is recorded as accepted, rejected or deferred, so CD isn't shown the same item every week.
4. **Data:** metrics are recorded at the source. Each stage run emits an allowlisted record (stage, status, cost, turns, models, failing step), retained for at least 30 days. No full transcripts are kept. Missing metrics read as unknown, not zero.
5. **Per project** for now (quantile); copied on rollout.
6. **Build it in this new session.**

## Build outline (adjust after reading the design)

1. **Metrics at the source.** Every stage's agent job, plus triage, uploads a small allowlisted metrics record (or writes it where the harvester can read it for 30 days or more). The PR body's agent record already carries cost and turns, which is a fallback source.
2. **Harvest:** `factory-improve.yml`, a hosted job with a read-only token, plus `improve_harvest.py`, deterministic and unit-tested. It builds a JSON digest of the window's signals with links (the design's Signals table, as corrected):
   - CD's review and revise outcomes;
   - questions asked and answered;
   - triage overrides;
   - follow-up pruning, from the filer's "Unchecked at merge" line;
   - closed-unmerged PRs (told apart from close-and-replan and comparison runs);
   - failures, from Actions metadata;
   - metrics.

   **Trust:** CD's pinned identity or a repository permission check, never `author_association: MEMBER`. Factory content is recognized by bot ID plus marker grammar. Quoted text is untrusted data, capped.
3. **Analyze:** an agent job on the strict tier, Opus, with no write credential. It runs `sdlc-audit` improvement mode headless, with the digest as input, and returns proposals in a schema: section, target, change, evidence IDs, severity, fingerprint, route.
   - **This is a cc-sdlc change.** Add a "factory digest" input and a headless contract to `skills/sdlc-audit/SKILL.md` and its methodology reference: return proposals, end with `awaiting-approval`, never apply anything. It needs a changelog entry and a port to quantile. Check that `sdlc-audit` carries the headless stop-rule mirror block.
4. **Report:** a hosted writer job using the App token, issues-only. It renders the report issue deterministically from the schema (no agent free text in structure; every quoted string through the guard's `escape()` and `literal()`), with evidence validated against the harvested IDs. It's idempotent per week, and dispositions are kept, for example in a marker on the report issue or in a small state file.
5. **Policy, tests, README, changelog,** and runner group 4 if the analyze job runs self-hosted. Then a smoke-style dry run over a past window. The 2026-10-09/10 history is rich: #30's three plan runs, #33's revise, #34's split, the follow-up filing and holds.

## Constraints

- **cc-sdlc `CLAUDE.md` applies** (directive = framework change, changelog entry, consistency checks), and so do the quantile factory rules:
  - agents hold no write credential;
  - writer jobs are hosted and use the factory-writer environment;
  - factory PRs never merge by bypass;
  - build in a worktree off `origin/main`, and fetch before pushing, because other sessions push there;
  - keep `.github/factory/*.schema.json` free of apostrophes (the policy check enforces it).
- **Other live sessions:** cc-sdlc-52 owns the production-runner redesign (gap 1). Coordinate through SendMessage if you touch the same files.

## Open questions for CD (ask before building the affected part)

1. **The report's home:** a new issue each week (recommended, linked to the previous one), or one long-lived pinned issue updated weekly?
2. **Should the report also notify CD elsewhere,** such as an email or a push notification, or is the GitHub issue enough?
