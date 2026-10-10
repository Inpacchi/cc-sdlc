# Handoff: build the factory's weekly improve loop (phase 4)

**Date:** 2026-10-10
**From:** the software-factory session (cc-sdlc + quantile)
**For:** a fresh session
**Status:** design cross-checked by Fable and Codex; CD's decisions recorded below; nothing built

## Read first

1. **The design** and its review corrections, both below (§ Design, § Cross-check corrections). This file is self-contained. Services, the design's other half, is built; see quantile's `.github/factory/README.md` § Services.
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

## Design (cross-checked by Fable and Codex, 2026-10-10)

### Goal

Once a week, turn what CD did to the factory's output into concrete proposals that make the next run better. The factory then learns from CD's reviews instead of repeating mistakes CD already corrected.

### Signals (what CD's actions say)

Job containers discard session transcripts (F4), so the loop reads the factory's **GitHub record**. All of it is already structured by markers and labels:

| Signal | Source | What it tells |
|---|---|---|
| Revision requests and their outcomes | CD's Request-changes reviews and inline comments on factory PRs; revise comments (`factory-revise: N`) with done, declined or needs-your-call | What the agents got wrong the first time; what they refused |
| Revision count, escalations | the `factory-revise` markers; `factory:escalated` and `factory:review-capped` | Where review caps bite |
| PRs closed without merging | factory PRs, state closed and not merged | Rejected work and the reason CD gave |
| Questions asked | `needs-input` comments (stage markers) and CD's replies | Gaps in issue context or in the skills; questions the thread already answered |
| Triage overrides | CD adding or removing `factory:advisor`, re-adding `factory:triage`, a manual `tier` on a dispatched plan | Where triage's judgment is off |
| Follow-up pruning | items CD unchecked at merge (the PR body as merged versus as opened) | What the agents over-propose |
| Failures | `report-failure` comments; failed runs with their failing step | Brittle steps, recurring environment problems |
| Run statistics | the transcripts' `result` records (cost, turns, models, permission denials), read while the 7-day artifacts last, **as numbers only** | Cost trends, stages that struggle |
| Reactions | 👍/👎 that CD puts on factory comments | Lightweight quality signal |

**Trust:** only content authored by maintainers (OWNER, MEMBER, COLLABORATOR, not bots) and the factory App's own markers is harvested. Agent text in transcripts is never read as text, only counted. The digest is data.

### Shape

1. **Harvest** (`factory-improve.yml`, a hosted job, read-only token, deterministic code `improve_harvest.py`)
   - **Trigger:** weekly cron, plus manual dispatch with a window.
   - **Output:** a JSON digest of the window's signals, grouped by stage and by factory PR or issue, with links. It's uploaded as an artifact, and the run summary gets the counts.
2. **Analyze** (an agent job on the strict tier, Opus, no write credential)
   - It runs `sdlc-audit`'s improvement mode headless, with the digest as a new input type ("factory digest").
   - It reads the skills, process docs and knowledge the signals point at.
   - It returns proposals in a schema: target file, change type, the evidence (links to the signals), severity, and a **route**.
3. **Route** (hosted writer jobs). Each proposal goes where its target can be changed:
   - **Project SDLC hygiene** (`ops/sdlc/knowledge/**/*.yaml` except the agent-governing files, `ops/sdlc/disciplines/*.md`, the changelog): committed by the agent in the analyze job, published as an **improvement PR** through the guard like any other factory PR. CD reviews and merges.
   - **Project skills, agents, process docs, CODEOWNERS paths:** the guard refuses agent commits to `.claude/` and owned paths, by design. These are listed as **proposals** in the weekly report issue, each with a ready-to-apply patch. CD applies them, or asks an interactive session to.
   - **Framework-level** (the problem is in cc-sdlc itself, for example a headless rule or a skill every project shares): listed in the report under "For cc-sdlc", with the evidence. See decision A3 for how they reach cc-sdlc.
4. **The report**: one issue per week, "Factory improvement report YYYY-WW", posted by the App. It has a summary (counts, cost trend, top three problems), the proposals by route, and links to the improvement PR and the digest. No proposal is applied without CD.

### Guard rails

- The loop never edits `.claude/`, `CLAUDE.md`, workflows or CODEOWNERS. Agent-config refusal stays absolute.
- One run a week, one improvement PR at most. A proposal repeated across weeks is linked, not re-proposed (it's keyed by target and evidence).
- An empty window posts nothing.
- The analysis cites signals by link. A proposal without evidence is dropped by the guard.

### Decisions for CD (Part A)

- **A1. Cadence:** weekly cron (Monday) plus manual dispatch? *Rec: yes.*
- **A2. What the loop may change by itself:** hygiene via an improvement PR, and everything else as proposals? *Rec: yes.* Skills stay CD-applied.
- **A3. Framework-level proposals:**
  - **(a)** listed in the report for CD to carry to cc-sdlc. *Recommended to start.*
  - **(b)** install the factory App on `Inpacchi/cc-sdlc` (a personal repo, outside the org installation) and file issues there.
  - **(c)** open a handoff file in cc-sdlc via PR (needs (b) too).
- **A4. Transcripts:** count-only statistics from the 7-day artifacts? *Rec: yes.* The alternative, mounting `~/.claude/projects` to a volume to keep full transcripts, keeps agent text around and widens what the loop reads.
- **A5. Where the loop lives:** in each project's `.github/` (quantile now; copied on rollout)? *Rec: yes for now.* A shared reusable workflow is blocked by the policy check's no-reusable-workflow rule, and is part of the shared-scripts item.

## Cross-check corrections (apply these over the design above)

**Part A changes before building:**
1. **Report-only first** (Codex). The weekly run posts the report issue only. Hygiene improvement PRs come after a dedicated guard stage, `improve`, with its own schema, an exact allowlist (knowledge YAMLs except governing files, discipline parking lots, the changelog), a renderer, and evidence IDs validated against the harvest. The report issue is created before any PR that refs it (Fable).
2. **Metrics at the source** (Codex, Fable). Each stage run emits an allowlisted metrics record (stage, status, cost, turns, models, failing step), retained for at least 30 days, instead of a weekly scrape of 7-day transcript artifacts that races the expiry. Missing means unknown, not zero. Cost and turns can also be read from PR bodies' agent records today.
3. **Trust** (Codex):
   - "maintainer" means CD's pinned identity, or a repository permission check, not `author_association: MEMBER`;
   - factory content is recognized by bot ID plus marker grammar;
   - all quoted text stays untrusted, with inputs capped and reports rendered deterministically;
   - failures are read from Actions metadata.
4. **Snapshots** (Codex, Fable):
   - follow-up pruning comes from the filer's summary comment ("Unchecked at merge, so not filed");
   - manual tier selections are recorded at dispatch, since the workflow-run API doesn't expose inputs;
   - close-and-replan and comparison runs are distinguished from rejection.
5. **Durable dispositions** (Codex). Each proposal gets a stable fingerprint, new evidence is appended, and a status is recorded (accepted, rejected, deferred). Report creation is idempotent.
6. **cc-sdlc change** (Fable). `sdlc-audit` improvement mode gains a "factory digest" input and a headless contract (proposals returned, `awaiting-approval`, never applied), with a changelog entry and a port to projects.
7. **Cadence** (Codex). Monday, not on the hour, with manual bounded windows, and catch-up from the last successful harvest (GitHub cron can be delayed or dropped).

**Decisions, revised:** A1 yes (with catch-up); A2 report-only first; A3 (a) for now, (b) after the repo moves into the org; A4 metrics at the source, 30 days; A5 per-project.
