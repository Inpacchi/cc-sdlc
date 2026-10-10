# Software factory: the improve loop (phase 4) and services access (draft design)

**Date:** 2026-10-10
**Status:** draft for cross-check, then CD's decisions; nothing built
**Context:** `software-factory_design.md` (D1–D3), `software-factory_handoff.md` (Phase 4; services item). Live factory in `endless-galaxy-studios/quantile` (`.github/workflows/factory-*.yml`, `.github/factory/`).

## Part A: the improve loop

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

## Part B: services access (generic; proven with a stand-in service)

### Goal

Any project adopting the factory can let planning (and later other stages) use an external service by adding one entry and one secret, with no workflow edit. Quantile has no service yet. The mechanism is proven with a dummy service, the same way the credential-masking smoke test was (`factory-smoke` § credential-mask: placeholders in the sandbox, real values injected only on requests to the service's hosts).

### Shape

`.github/factory/services.json` (CODEOWNERS-owned):

```json
{"services": [
  {"name": "sentry", "stages": ["plan", "spec"], "domains": ["sentry.io", "*.sentry.io"],
   "secret": "FACTORY_SVC_SENTRY", "attach": {"env": "SENTRY_AUTH_TOKEN", "header": "Authorization: Bearer"}}
]}
```

- **The secret** is a GitHub secret in the stage's environment (`factory-planning` for planning stages). Its name must start with `FACTORY_SVC_`.
- **Sandbox wiring.** The prepare step builds the sandbox settings for the run from the entries allowed for this stage:
  - `credentials.envVars` with `mode: mask` and `injectHosts` set to the entry's domains;
  - the domains added to `network.allowedDomains`;
  - `tlsTerminate` on.

  Sandboxed commands see a placeholder; the proxy substitutes the real value only on requests to those hosts.
- **MCP attach (alternative).** An entry can instead declare an HTTP MCP server URL and a header, written into the MCP config held by the main process, as Context7 is. The sandbox never sees the key.

### The one hard part: reading secrets by name

GitHub expressions can't index secrets by a runtime name. Options:
- **(i)** `toJSON(secrets)` in the prepare step's env, filtered to the names services.json lists. That step briefly holds every secret in its environment, so the agent step must never inherit it. That holds if the value only goes into a file in `$CHECKS` (mode 600), and nothing is exported to `GITHUB_ENV`.
- **(ii)** A fixed set of slots (`FACTORY_SVC_1..4`) referenced literally in the workflow, with services.json mapping names to slots.
- **(iii)** One secret holding a JSON map of every service credential.

*Rec: (ii).* It keeps literal references (the policy check can verify them), never loads unrelated secrets, and four slots is plenty. (iii) is simpler but puts every credential in one place.

### Proof

A smoke job registers a stand-in service:
- domain `httpbin.org`, a dummy secret in a slot;
- an agent probe curls it;
- the assertions check:
  - the sandbox saw a placeholder;
  - httpbin received the real value;
  - a request to a host not in the entry did **not** get the real value;
  - a stage not listed in `stages` got no wiring at all.

Plus `workflow_policy.py` rules: services.json is valid, its domains are hosts (no bare `*`), and secrets match a known slot.

### Decisions for CD (Part B)

- **B1. Secret lookup:** slots (ii)? *Rec: yes.*
- **B2. Stages:** planning stages only at first? *Rec: yes.* Implement and execute stay offline; widening needs its own decision, since code stages write code that runs later.
- **B3. MCP attach:** supported in the same file? *Rec: yes*, for services that ship an MCP server.

## Cross-check results (2026-10-10: Fable and Codex gpt-6-astra)

**Part B was built** (quantile `621d395`, `488ec64`) with the four-slot design, planning stages only, and these review changes:
- every entry must declare `read_only: true` (masking limits destinations, not authority);
- MCP attach is deferred until it has its own proof (it runs outside the sandbox);
- a warning about echo endpoints;
- the policy allows slot secrets only in planning agent steps whose job runs `services.py`.

Codex also noted that GitHub *can* index secrets dynamically (`secrets[steps.x.outputs.name]`). Slots remain the auditable choice.

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
