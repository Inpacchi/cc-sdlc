---
type: handoff
slug: software-factory
created: 2026-10-07
status: pending
trigger: deferred-work
recommended_next_skill: direct-dispatch
source_session_summary: "Two sessions (software-factory-take-1 and take-2) evaluated running cc-sdlc as an issue-driven agent factory on CD's Max plan and Linux PC. CD settled every setup decision; this hands off phases 0-1 (runner, then triage) to fresh sessions."
active_deliverable: null
related_files:
  - docs/current_work/ideas/software-factory_design.md
  - process/production-gates.md
  - docs/current_work/ideas/review-loop-unification_handoff.md
  - docs/current_work/ideas/review-loop-unification_consult-record.md
  - process/github-checkpoints.md
  - process/headless-mode.md
  - process/review-fix-loop.md
  - CLAUDE-SDLC.md
  - skills/sdlc-manage-github/SKILL.md
  - ~/Projects/quantile/.sdlc-manifest.json
---

# Handoff: Software factory

## Current state and next steps (2026-10-10): read this first

The factory runs in `endless-galaxy-studios/quantile` on self-hosted runners on pop-os. **Phases 0–3 are built and proven live.** The rest of this file is history (phases 0–3 as they happened) plus the design rules. The quantile side's operating manual is `.github/factory/README.md` there: the stage contract, Follow-ups, Revise, Services, labels.

### What's built (quantile `main`; every stage has run live)

- **Triage:** tier (direct, lite, full), estimate, and Fable-advisor choice (`factory:advisor`).
- **Implement:** direct fixes, finishing small related fixes as declared add-ons.
- **Plan:**
  - lite;
  - full: discovery, then a spec PR, then a plan from the merged spec;
  - **split** when the work exceeds the phase cap: a split PR, then part issues filed as sub-issues with Depends on, each held for `factory:go`.
- **Execute:** `/sdlc-lite-execute` or `/sdlc-execute` on a merged plan.
- **Revise:** code PRs, 3 revisions, through a Request-changes review or the `factory:revise` label.
- **Follow-ups:** an executed plan's PR lists up to 10 as a checklist. On merge they're filed as issues, triaged, then held for `factory:go`. Direct fixes and a follow-up's own follow-ups file nothing.
- **SDLC hygiene is agent-writable:** discipline parking lots, knowledge YAMLs (except `agent-context-map.yaml` and the agent-governing files) and the SDLC changelog. PRs name every such file.
- **PR descriptions** follow `[sdlc-root]/templates/pr_description_template.md`, rendered by the guard. An over-long brief gets a resume-and-rewrite step instead of failing the run.
- **Services:** `services.json` plus credential slots `FACTORY_SVC_1..4`. The sandbox masks every slot, and the proxy injects a value only on that service's domains. Every entry needs `read_only: true`. MCP attach is deferred. Planning stages only. Proven in the smoke run with a stand-in service.
- **Hardening found this session:**
  - the guard refuses agent and gate configuration at any depth;
  - owner-less CODEOWNERS lines unown only the exact files they name;
  - the policy check rejects apostrophes in schemas;
  - planning agents get the full git history;
  - the planning database proxy starts clean and reports its errors.

### In flight right now

- **The full-tier test (D14, issue #34), not to be executed:**
  - #34's split PR #45 merged, which filed parts #46–#49 (D14a–d).
  - **D14b (#47)** was released. Its spec run is 38032179372. Two earlier runs died on bugs, both fixed: the brief limit, and the database proxy.
- **Next for D14b:** open the spec PR. CD merges it, which tests advancing to the plan. Then **close the plan PR without merging**, so nothing executes.
- **Then clean up:** close or mark D14/D14a–d as a test in the catalog (`docs/_index.md`), and close #34 and #46–#49.

### Next steps, in order

1. **Finish the full-tier test** (above), including the reply-and-resume path if discovery asks a question.
2. **The improve loop (phase 4):** build it in a fresh session from § Next build below. CD's decisions are in it: Sunday 22:23 UTC, report only, a substantial actionable report covering everything.
3. **The production runner (gap 1): unowned; redesign needed.** Start from CD's decision (§ Gaps) and the reusable parts of `software-factory-gaps_design.md`: gates between plan phases (a CD step with a checklist, report-back fields and rollback), pinning the approved plan by its blob hash, and the `factory:handoff` state. Its gap 1 sections are otherwise superseded. Cover the security boundary: keys, which steps, how approval binds to one step without replay, audit, rollback, and the approval surface (CD prefers one long-standing PR with gates as steps, not a PR per approval). Cross-check with Fable and Codex, and design only until CD approves. Then fold the result into § Gaps and delete the gaps doc. The session that wrote the first design, cc-sdlc-52, is no longer running.
4. **Revise for plan and spec PRs:** a doc-revise path on the planning tier, 5 revisions. Not built: today, changes to a plan or spec PR mean closing it and re-running.
5. **Next services work,** from research into how other factories do it (Stripe, Uber, Snap, Shopify, Tessl and Claude Code keep credentials in a broker or proxy; Warp and HumanLayer put them in the agent's environment):
   - **CLIs:** installed in a setup step that has no secrets (Codex's pattern), or baked into the job image.
   - **Tokens:** CLIs run with masked, read-only tokens (`SENTRY_AUTH_TOKEN=$FACTORY_SVC_n sentry-cli …`).
   - **Methods:** limit read-only services to GET and HEAD if the sandbox supports it.
   - **MCP:** later, through one gateway that holds the credentials. Projects pick from a catalog CD approved, with tools off by default and allowlisted per tool (Copilot's, Tessl's and Uber's patterns).
   - **Avoid:** real secrets in the agent's environment, and sharing the host's logged-in CLIs.
6. **Shared scripts:** extract the prepare, publish and report logic duplicated across the stage workflows.
7. **Small items:**
   - switch `create-github-app-token`'s deprecated `app-id` to `client-id`;
   - smoke after `ubuntu-latest` moves to Ubuntu 26 (2026-10-19);
   - a Redis version floor for the Lua CVE;
   - wire the `extractMessage` `node --test` suite into CI (needs `web/package.json`, which is CD's);
   - **revise has the hole Codex found in continue mode:** `factory-revise.yml` refuses only agent configuration on the PR branch, then runs `pip install` and `npm ci` from it. Apply the owned-path refusal continue mode now has (`factory-implement.yml`, gates branch);
   - cc-sdlc: the `completion-report` mirror source in `process/writing-for-cd.md` still says "Deferred" where both execute skills say "Add-ons" and "Follow-ups" (drift since 2026-10-09). Update the source and re-copy it.

### Parked or deferred by CD

- **Moving cc-sdlc into the org** ("after"). Then the improve loop can file framework proposals there, decision A3(b).
- **#33's follow-ups (#35–#44):** held. #42 needs CD's two `max_spread` answers; #44 waits on D11b.
- **D11 (D11a/b/c):** set aside. D11b's plan touches production: to run it through the factory, it needs re-planning with gates (D4), and its snapshot proofs stay CD gates until the catalog grows.
- **Deliverables registered outside the factory:** CD handles this separately.
- **Runner 1's migration:** CD runs `sudo bash ~/factory-setup/setup.sh` on pop-os.
- **Neuroloom factory memory:** optional, exploratory (Phase 5 below).

### Other sessions

- **cc-sdlc-52** (App identity, splitting, the first gap 1 design) has ended.
- **cc-sdlc-de** built the gap 1 redesign (next step 3).
- **cc-sdlc-89** did the PR-description standard, the writing-for-CD port, and the cc-sdlc history rewrite (force-pushed; old SHAs map in its messages).
- **When working in quantile:** fetch before pushing, and build in a worktree off `origin/main`. Other sessions push there.

## Next build: the weekly improve loop (phase 4)

The brief for the session that builds it. It's self-contained, and CD's decisions are recorded. Also read `software-factory_design.md` (D1–D3) and, in quantile, `.github/factory/README.md` and the factory workflows. Services, the other half of the original design, is built: see quantile's README § Services.

### What the loop is for

Once a week, read the factory's own GitHub record of what CD did to its output, and turn that into a **report CD acts on**: concrete improvements, each with its evidence, or an explicit statement that nothing needs action. The factory learns from CD's corrections instead of repeating them.

### CD's decisions (2026-10-10)

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

### Build outline (adjust after reading the design)

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

### Constraints

- **cc-sdlc `CLAUDE.md` applies** (directive = framework change, changelog entry, consistency checks), and so do the quantile factory rules:
  - agents hold no write credential;
  - writer jobs are hosted and use the factory-writer environment;
  - factory PRs never merge by bypass;
  - build in a worktree off `origin/main`, and fetch before pushing, because other sessions push there;
  - keep `.github/factory/*.schema.json` free of apostrophes (the policy check enforces it).
- **Other sessions:** check ListAgents before starting. Whoever takes the production-runner redesign (gap 1) works in the same factory files, so coordinate through SendMessage.

### Open questions for CD (ask before building the affected part)

1. **The report's home:** a new issue each week (recommended, linked to the previous one), or one long-lived pinned issue updated weekly?
2. **Should the report also notify CD elsewhere,** such as an email or a push notification, or is the GitHub issue enough?

### Design (cross-checked by Fable and Codex, 2026-10-10)

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

### Cross-check corrections (apply these over the design above)

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

## The approach in one paragraph

- **Execution:** run Claude Code's own GitHub Action (`anthropics/claude-code-action`) on a self-hosted runner on CD's PC. Authenticate it with a `claude setup-token` OAuth token so usage bills to the Max plan.
- **Control plane:** GitHub issues and `factory:*` labels are the state machine.
- **Stage logic:** cc-sdlc skills do the work at each stage.
- **Source of the pattern:** Warp's `cloud-factory-demo` (MIT), with its six stages and the split between a read-only agent and a separate job that writes. Its workflow files are not reused, because they are bound to Warp's own runner and `WARP_API_KEY`.
- **Merging:** the factory never merges. CD reviews every PR.
- **Capacity:** the Max usage window is the real ceiling, so throughput is kept deliberately low.

## Decisions (CD-approved)

| # | Decision | Session |
|---|---|---|
| F1 | **Runtime:** `claude-code-action` on a self-hosted runner on the 10980XE PC, authenticated with `CLAUDE_CODE_OAUTH_TOKEN` (Max). No Warp Oz, Cursor or Copilot. | take-1, confirmed take-2 |
| F2 | **Pilot repo:** `endless-galaxy-studios/quantile`: private, in an org (GitHub plan: enterprise), local checkout `~/Projects/quantile`. | take-1, updated take-2 |
| F3 | **Runner registration:** org-level runner in a runner group restricted to `quantile`. One runner instance for the pilot. | take-2 |
| F4 | **Isolation:** a fresh Docker container per job. | take-1 |
| F5 | **Intake:** GitHub issues. **Opt-in:** triage runs only when CD adds `factory:triage`. Provenance-created issues and the existing backlog are never auto-triaged. | take-1 + take-2 |
| F6 | **What runs on its own:** triage, and `factory:ready-for-dispatch` fixes up to a draft PR. **Every plan, lite or full, stops** for CD's approval, which CD gives by merging the document PR (F17). There is no "lite runs through" lane. Nothing ever merges on its own. | take-1, reaffirmed take-2 |
| F7 | **Resuming after a question:** restart from the issue thread plus the committed docs, not by resuming the session. This fits containers, which keep no session history. | take-1 |
| F8 | **Getting CD's attention:** GitHub notifications (web and mobile) first. Slack later via GitHub's own Slack app, with nothing to build. | take-1 |
| F9 | **Local model:** not now. | take-1 |
| F10 | **Labels:** every factory label is prefixed `factory:`. A single waiting-on-CD label, `factory:needs-input`; the question comment records which stage to restart. | take-2 |
| F11 | **Deliverable IDs (plan tier, phase 3):** before branching, the run claims the next D-number in a small commit pushed straight to `main`, serialized by a concurrency group. Direct-tier fixes take no ID, as small work doesn't today. | take-2 |
| F12 | **No API-key overflow lane.** Leave usage credits off, so spending cannot pass the plan. | take-1, reaffirmed take-2 |
| F13 | **Incubate, then promote.** Build the triage skill and workflows in quantile first, then move them into an opt-in cc-sdlc `factory` bundle once proven. **Exception:** the headless rule (phase 2) is a cc-sdlc framework change from the start. | take-1 |
| F14 | **Runner PC = quantile production box.** The Pop!_OS machine also runs quantile's production stack. Job containers must be firewalled from the host's production Postgres and Redis **before any job runs**. | take-2 |
| F15 | **Revise stage.** CD's review on a factory PR is acted on, on the **same branch** (the PR updates; no new PR).<br>**Trigger:** submitting a review with **"Request changes"**. One run handles every comment in that review.<br>**Only path:** there is no `@claude` shortcut. "Request changes" is the only way to ask for a revision.<br>**Each run:** applies the changes, runs the bounded review loop on the new changes only, returns its replies as structured output plus a patch artifact; a writer job pushes the patch with the App token (so CI re-runs) and posts the replies with `GITHUB_TOKEN` (stage contract: quantile `.github/factory/README.md`).<br>**Scope-changing comments:** the run stops with `factory:needs-input`, or sends the issue back to `factory:ready-to-plan`, rather than improvising.<br>**Spec or plan PRs:** the stage revises the document. For plans, it follows the existing plan re-review rule: reviewers re-run only if the change alters the scope. Approval is CD merging the PR (F17).<br>**Built in:** phase 2, and reused in phase 3. | take-2 |
| F16 | **Revision limits, then escalate.** **Code PRs** get at most **3** "Request changes" revise runs. **Spec and plan PRs** get at most **5**, because up-front alignment is where iteration pays off.<br>**On the next request after the limit:** no run starts. The PR gets `factory:escalated` and a comment that lists the rounds, the comments still unresolved, and the options: take it over, send the issue back to `factory:ready-to-plan`, or close it. **On a spec or plan PR, it also offers continuing in an interactive `sdlc-plan` session on that branch**, since a document that needs a sixth round usually needs a conversation.<br>**Counting:** every "Request changes" review counts. Revise runs keep the normal 3-round review cap *inside* each run, separate from this per-PR limit. | take-2 |
| F17 | **Approval = CD merges the document PR.** This replaces the `factory:spec-approved` label from take-1.<br>**Full tier:** spec PR → CD merges → plan PR → CD merges → execution → code PR.<br>**Lite tier:** plan PR → CD merges → execution → code PR.<br>**Why merge works:** each stage is its own PR with its own revision count, the approved document lands on `main` before any code is written, and the factory still never merges.<br>**Doc PRs open ready for review, not as drafts,** because GitHub can't merge a draft. Code PRs stay drafts.<br>**Closing a doc PR without merging** stops the item; nothing further runs. | take-2 |
| F18 | **The full-tier spec stage asks questions.** It runs a discovery conversation before drafting the spec, as `sdlc-plan` does interactively today, and back-and-forth is expected. Questions go to the issue through `factory:needs-input`, and CD's reply restarts the spec stage.<br>**Lite tier** asks only when it must.<br>**Question rounds are not revisions:** they don't count toward F16's limits, and each round waits for CD.<br>**Pacing (decided):** one question per run, as `sdlc-plan`'s rule requires. Each run posts and updates a running "discovery notes" comment on the issue, so the next run reads it instead of redoing the research.<br>**Next to explore:** persistent planning sessions (see § Exploration). | take-2 |
| F19 | **Planning sees real data through a snapshot, never production.** Spec and plan runs restore a periodic snapshot of quantile's database into their own Postgres.<br>**Production stays off-limits** to every factory job (F14 holds). No live read-only access, no replica exception.<br>**Not yet decided:** which tables, scrubbing, and refresh cadence (see Open questions). | take-2 |
| F20 | **The factory's conversation lives on GitHub.** Every question, answer, review and escalation goes through issue and PR comments, so the phase 4 improve loop and CD can see all of it.<br>**Persistent sessions too:** any persistent planning session must take its questions and CD's replies through GitHub, not through the Claude app or claude.ai. This rules out a cloud session whose Q&A lives only in claude.ai (option B in § Exploration). | take-2 |
| F21 | **State names:** `ready-for-dispatch` (was `ready-direct`) and `ready-to-plan` (was `ready-plan`), with labels `factory:ready-for-dispatch` and `factory:ready-to-plan`. Tier values stay `direct`, `lite` and `full`. | phase 1 session |
| F22 | **Factory decisions live in cc-sdlc, not in project ADRs.** The factory is meant for many projects, so its rules are framework rules: drafted in `software-factory_design.md` while incubating, then promoted into the `factory` bundle's process doc, which installs into each project. Projects keep only operating notes (`.github/factory/README.md`). | phase 1 session |

**Superseded by what was built:** F7 (planning runs resume the saved session; restarts still re-read the thread), F11 (IDs are reserved by an App marker comment, not a commit to `main`), F19 (planning reads production read-only through a pgbouncer proxy, design rule D3, not a snapshot), and F6's "every plan stops" now also covers split PRs. The rest stand.


### Label set (F10)

| Label | Set by | Meaning |
|---|---|---|
| `factory:triage` | CD | Opt-in: run triage on this issue. The apply step removes it. |
| `factory:ready-for-dispatch` | triage | Small and clear. Implement, review, then open a draft PR (phase 2). |
| `factory:ready-to-plan` | triage | Needs a plan. The triage comment names the tier (lite or full). The run stops at a plan/spec PR (phase 3). |
| `factory:needs-input` | any stage | Waiting on CD. The question comment carries `<!-- factory-stage: <stage> -->`. CD's reply comment restarts that stage. |
| `factory:wait` | triage | Doesn't fit now. The comment says what would change that. |
| `factory:review-capped` | execute | The 3-round review cap was hit. A draft PR is parked with an open-findings table (phase 2+). |
| `factory:advisor` | triage or CD | A property, not a state (2026-10-09): planning (plan, later spec) gets a Fable advisor. Triage sets it when the plan turns on judgment and clears it otherwise; a label CD added always stands. State sweeps leave it alone. Implement and execute never use an advisor. |
| `factory:follow-up` | follow-up filer | A property (2026-10-10): filed from a merged plan's checklist. Triage runs, then holds; the App's provenance marker, not the label, decides the hold. |
| `factory:go` | CD | Releases a held issue (a follow-up or a split part): starts its triaged stage once, then removes itself. Needs write access. |
| `factory:revise` | CD | On a factory code PR: revise it from the review comments since the last revision (works on any PR; a Request-changes review also triggers revise on PRs opened after 2026-10-10). |
| `factory:escalated` | revise workflow | The PR had 3 revise runs and CD requested changes again. No more automatic runs; CD decides (F16). |
| `factory:gate` | execute | The issue's execution is stopped before a production gate (D4). Its PR's gate run waits for CD's approval in environment `factory-production`. |
| `factory:gate-retry` | CD | On an execution PR: build a fresh gate request (the next attempt) and start its gate run, after a failed, rejected or refused gate or a stale request. |

## Gaps (open)

**Gaps found 2026-10-09 (CD: record now, build later).**
- **Plans that touch production.** quantile's D11b plan restores a pinned production database snapshot (on the NAS), deploys, and restarts services on pop-os. The strict tier has no production path by design (D2), and the planning tier reads production read-only through one proxied database login (D3). Nothing can execute a plan with production steps. Needs a decision:
  - a production-capable execution tier, with its own boundary and CD approval per step;
  - or a rule that such plans split into factory-executable phases and CD-run deploy and proof steps, with the plan template marking which is which;
  - or both.

  **CD's decision (2026-10-10): build a production-capable runner.** It works without CD's hands, CD approves each production step, and there's no new PR per approval.

  **Built (2026-10-10), not yet live: design rule D4.** Cross-checked with a Fable advisor and Codex (`gpt-6-astra`, max effort). Codex's review found 2 critical and 10 major problems in the first draft, all folded in.
  - **Plans** put production work in gates between phases (cc-sdlc `process/production-gates.md`). A gate names operations from quantile's reviewed catalog, or is a CD gate (CD runs its runbook). Execution reviews and commits before each gate, then stops (`awaiting-approval`).
  - **One execution PR per deliverable.** Later segments push to it, fast-forward only. A deploy ships the PR's head, so production can run ahead of `main` until CD merges with a merge commit.
  - **Approval is GitHub's deployment review** of each gate's run (environment `factory-production`), not a label (CD's choice after the cross-check). Labels and comments can be edited by any writer, and a label can't say which request it approves.
  - **A root broker runs the gate,** reached over a socket only the runner user can open. It re-derives the request from the plan on `main`, checks CD's approval with GitHub, runs only catalog operations, keeps a ledger so nothing runs twice, and signs its result.
  - **The cc-sdlc gaps design doc is deleted.** Its content is in D4 and in git history (`63c8d2e`).
- **Splitting deliverables.** When planning hits the phase cap, `sdlc-plan`'s feasibility gate proposes a split (D11 became D11a → D11b → D11c). The factory handles one deliverable per issue and can't split:
  - it has no step to mint sibling IDs and file their issues;
  - it doesn't record which split part depends on which (see `[sdlc-root]/process/deliverable_lifecycle.md` § Dependencies);
  - it doesn't run each part through the stages.

  Today it would stop with `needs-input` and leave the split to CD.
- **Deliverables registered outside the factory** (started interactively, like D11a and D11c) can't be planned by the factory: triage skips them, and the plan stage's claim would mint a new ID. A temporary bridge was built and then reverted on 2026-10-09. If it's needed again, reuse the catalog's ID for the issue and read an approved spec from the catalog row.

## Later and optional

**Phase 5 (optional, exploratory): factory memory through Neuroloom (CD, 2026-10-09).** Not committed work: explore first, after the lite path runs end to end. The open questions below (workspace access, server-side tag enforcement, whether memory beats parking lots plus the improve loop at all) decide whether this phase happens.
- **Why:** job containers are ephemeral, so nothing a factory agent learns survives the run except what lands in a reviewed PR. File-based agent memory doesn't fit:
  - **Git:** `.claude/agent-memory/` is gitignored by cc-sdlc rule (`CLAUDE-SDLC.md`: "Agent memories are not git-tracked"). Persisting it would mean tracking it in factory PRs.
  - **Auto-load:** the first 200 lines of `MEMORY.md` load into every future agent's system prompt, CD's local sessions included.
  - **The factory blocks it anyway:** Edit/Write deny `**/.claude/**`, and CODEOWNERS owns `.claude/`.
  - **Discipline parking lots** are the reviewed channel for lessons today (unowned in CODEOWNERS on 2026-10-09).
- **Shape:** give the factory's agent jobs the Neuroloom MCP server (`memory_search`, `memory_store`, `memory_rate`) as factory memory.
  - **Credential:** HTTP MCP like Context7, with the API key in the MCP config held by the main process. Sandboxed Bash never sees it.
  - **Policy:** `workflow_policy.py` allows it as a second server. The key goes in a GitHub secret, scoped to the factory environments.
  - **Leave the knowledge layer alone at first:** no full neuroloom-sdlc-plugin install in quantile. That rewrites the skills' knowledge routing and changes CD's local sessions too; it's a separate decision.
- **The design point: writes land unreviewed.** `memory_store` bypasses the PR gate, and factory runs read issue text and, on the planning tier, the open internet. A poisoned or wrong memory would surface in later runs, and in CD's sessions if they share a workspace. Pick one:
  - a **dedicated factory API key** (Neuroloom resolves the workspace from the key), which keeps factory memories out of CD's workspace. Open: can the factory also get read-only access to CD's curated workspace?
  - the **same workspace with quarantined writes:** every factory write is tagged (`source:factory`, `unreviewed`), CD's searches filter those tags out, and entries are promoted after review. The tag has to be enforced server-side, not left to the agent.
- **Promotion:** reviewed factory memories flow into the knowledge stores or CD's workspace, through `sdlc-reflect` or the phase 4 improve loop. `memory_rate` feedback from runs helps rank what to promote.
- **Threat model:** `memory_store` is an outbound text channel. Planning runs read production data, so aggregates could reach Neuroloom. Add it to D3 beside WebSearch and Context7.

## Open questions

- **Product direction for triage:** add `vision.md` and `roadmap.md` to quantile, or keep relying on the README and the catalog?

## Out of scope

- Local model work (F9).
- Vendor tools (Warp Oz, Cursor, Copilot, HumanLayer) and Slack or Linear integration.
- Moving other projects onto the runners. That's a later rollout, after the improve loop and the production runner.

## History

Phases 0–3 as they happened (runner setup, calibration, the credential-free Bash spike, the implement, plan, revise, follow-up, split and services stages, and every live run and fix) are in git: `git log -p -- docs/current_work/ideas/software-factory_handoff.md`, and the full text before this trim is at commit `a74eb60`. The original evaluation and market scan is `software-factory_evaluation.md` at commit `f838ad7`.
