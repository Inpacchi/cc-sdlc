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
  - docs/current_work/ideas/software-factory_evaluation.md
  - docs/current_work/ideas/software-factory_design.md
  - docs/current_work/ideas/review-loop-unification_handoff.md
  - docs/current_work/ideas/review-loop-unification_consult-record.md
  - process/github-checkpoints.md
  - process/headless-mode.md
  - process/review-fix-loop.md
  - CLAUDE-SDLC.md
  - skills/sdlc-manage-github/SKILL.md
  - ~/Projects/quantile/.sdlc-manifest.json
---

# Handoff: Software factory, phases 0-1 (runner, then triage)

## Why this is a handoff

The **software-factory-take-1** session (2026-10-06) evaluated the factory idea and measured CD's usage. It spun off the review-loop work, which landed as `44d6cc0`. CD then made the setup decisions.

The **software-factory-take-2** session (2026-10-07):
- re-did the research from primary sources, including the three AI Engineer talks, the Warp demo repo and HumanLayer;
- reconciled its findings with take-1;
- had CD settle the remaining questions.

The research and comparison live in `software-factory_evaluation.md`. **This handoff supersedes that document's recommendations wherever they differ.**

When this handoff was written nothing was built. Progress since then is recorded in the Phase 0 and Phase 1 progress sections below.

The work splits across machines and repos:
- **Phase 0** runs on CD's Linux PC.
- **Phase 1** is built in `endless-galaxy-studios/quantile` (formerly `Inpacchi/crypto-tracker`).
- **Later**, proven pieces move into an opt-in cc-sdlc `factory` bundle.

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

### Label set (F10)

| Label | Set by | Meaning |
|---|---|---|
| `factory:triage` | CD | Opt-in: run triage on this issue. The apply step removes it. |
| `factory:ready-for-dispatch` | triage | Small and clear. Implement, review, then open a draft PR (phase 2). |
| `factory:ready-to-plan` | triage | Needs a plan. The triage comment names the tier (lite or full). The run stops at a plan/spec PR (phase 3). |
| `factory:needs-input` | any stage | Waiting on CD. The question comment carries `<!-- factory-stage: <stage> -->`. CD's reply comment restarts that stage. |
| `factory:wait` | triage | Doesn't fit now. The comment says what would change that. |
| `factory:review-capped` | execute | The 3-round review cap was hit. A draft PR is parked with an open-findings table (phase 2+). |
| `factory:escalated` | revise workflow | The PR had 3 revise runs and CD requested changes again. No more automatic runs; CD decides (F16). |

## What needs to happen

### Phase 0 progress (2026-10-07, driven from the Mac over `ssh pop-os`)

Files written in `~/Projects/quantile` (uncommitted, awaiting CD): `.github/factory/{host/setup.sh, Dockerfile, smoke_check.py, README.md}`, `.github/workflows/{factory-image,factory-smoke}.yml`, `.github/actionlint.yaml`. `setup.sh` is staged at `pop-os:/mnt/workbench/factory-setup/`.

- **Done:** host survey (step 1); the seven `factory:*` labels (step 10); the action pinned to v1.0.244 = `58985842b834ed26087302ba27d07bc24ca8697a`, which hard-codes Claude Code `2.1.292` in `src/entrypoints/run.ts` (step 6); `sdlc-migrate` to v1.9.0 (step 11, commit `472bcc7`, local and unpushed).
- **Decided on the host:** **rootless Docker** for `factory-runner`. Rootful would put a root-equivalent user next to about ten production and personal containers (portainer, stash, qbittorrent and others, all listening on `0.0.0.0`).
- **Firewall:** a firewall by **socket owner (uid)**, not `DOCKER-USER`. It's an nftables table `inet factory_runner` that rejects `factory-runner` traffic to host-local, RFC 1918, CGNAT, link-local and ULA addresses, allowing DNS only. It runs as its own unit with no `flush ruleset`, because ufw is active.
- **Home directory:** `factory-runner`'s home is `/mnt/workbench/factory-runner`, because `/` is 91% full.
- **Runner facts verified in its source (v2.338.0):**
  - Job containers always get the host's `/var/run/docker.sock` mounted. Under rootless Docker, container root is `factory-runner`, which is not in the `docker` group, so the socket is unusable. The smoke test asserts this.
  - `container:` images are always pulled, so the image lives on GHCR (`ghcr.io/endless-galaxy-studios/factory-job`), built on `ubuntu-latest`.
  - `ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER=true` is set. **Phase 1 consequence:** the triage `apply` and failure jobs cannot run on this runner, so they go on `ubuntu-latest`.
- **Action and CLI facts verified:**
  - The init event carries `skills`, `agents` and `mcp_servers`, so the smoke check asserts runtime facts in one pass.
  - The action passes the full `process.env` to the CLI, so job-level `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` reaches it.
  - The action defaults to `settingSources: user, project, local`.
  - Context7 connects without an API key.
  - `--permission-mode auto` is honored in a clean environment.
- **Phase 0 COMPLETE (2026-10-07).**
  - **Repo and image:** quantile `main` is at `47e5be2`, and `factory-image` pushed `ghcr.io/endless-galaxy-studios/factory-job`.
  - **Host setup:** `setup.sh` ran twice. In the isolation test, every probe was blocked: the host and LAN addresses on all ports, plus the host `docker.sock` (PermissionError). The internet stayed reachable.
  - **Runner:** org runner group `factory-quantile` (id 4) is limited to quantile. Runner `pop-os-factory` is online with the labels `self-hosted, Linux, X64, factory`.
  - **Secret:** `CLAUDE_CODE_OAUTH_TOKEN` is a repo secret. CD regenerated the token after the first one was exposed in a session transcript.
  - **Smoke run 37643211247 is green.**
    - Isolation probes passed inside the job container.
    - Claude Code 2.1.292 on `claude-sonnet-5-5`; permission mode `auto`; `apiKeySource: none` (Max OAuth).
    - 26/26 repo skills and 12/12 agents loaded, and Context7 connected. Context7 answered `/django/django`.
    - 3 turns, **$0.16 at API rates**.
- **Open question resolved:** the action runs correctly with `github_token: GITHUB_TOKEN` under `contents: read, packages: read` and without `id-token: write`.
- **Admin `gh` lives on the PC.** The `admin:org` scope was granted to `gh` on pop-os, not on the Mac.
- **Next:** Phase 1 in `~/Projects/quantile`.

### Calibration graded by CD (2026-10-08): COMPLETE

**Method:** CD blind-triaged all 15 issues, compared against the models' calls, and set final labels.

**Agreement with CD's final labels:**

| | Majority call matched | Note |
|---|---|---|
| Sonnet 5.5 | 13/15 | |
| Haiku 5.5 | 8/15 | |
| CD's own blind calls | 11/15 | All four changes followed code findings |

**Rubric changes** (quantile `38a7ec4`):
- collisions need concrete overlap;
- duplicates of an active deliverable get `wait` plus a suggestion to close;
- parked-issue split-outs route normally;
- bundled items with different blockers get a split suggestion;
- a premise the code contradicts gets a question, or the small remaining gap is dispatched;
- additive API/schema changes are lite; breaking ones are full. This also refines `CLAUDE.md`'s tier table.

**Kept:** financial formulas never dispatch; API changes go through a plan.

**Re-measured on Sonnet** (3 runs × 15):

| | Before | After |
|---|---|---|
| Runs matching CD | 34/45 | 42/45 |
| Consistent across runs | 8/15 | 13/15 |

The one remaining miss is a test-case flaw: c15's comment names an element that doesn't exist.

Raw grades: session scratchpad `triage/grades.json`.

### Phase 2 spike: credential-free agent Bash (2026-10-08)

Ran on the real runner with temporary quantile workflow `factory-spike.yml`: rootless Docker, the pinned action, and the real Max OAuth token.

**Result: works.** The setup is:
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`;
- bubblewrap in the job container;
- container `options: --security-opt seccomp=unconfined --security-opt systempaths=unconfined`.

**Evidence:**
- **Control** (the same probe script, run unsandboxed): it sees the token in the environment and in 3 processes' `/proc/*/environ` (len 108, matching hash).
- **Agent Bash:**
  - `env: empty`;
  - no process holds the token value;
  - its own PID namespace (`bwrap` is PID 1, 6 processes in total);
  - neither the token nor its hash appears in the transcript.
- **With Docker's default container security:** bubblewrap can't create namespaces, so every Bash call fails. Claude Code fails closed: Bash is unusable, and it doesn't leak.
- **The auto-mode classifier** declined to run commands that read token variables directly. That's an extra layer, but not one to rely on.

**Spike v2 (2026-10-08) — DONE; spike workflow removed, runner group restored (quantile `e9520ac`):**

| Agent Bash | Scrub only | Scrub + network sandbox |
|---|---|---|
| Max OAuth token | not visible | not visible |
| Job GitHub token (`GH_TOKEN`, `GITHUB_TOKEN`) | visible (by design) | visible (by design) |
| Process namespace | isolated, 6 processes | isolated, 6 processes |
| pypi.org, registry.npmjs.org | reachable | reachable |
| example.com, api.github.com | reachable | **blocked** |

- **The control** (unsandboxed, with the real tokens set) saw both tokens in the environment and in process environments, so the probe works.
- **Narrow seccomp works.** The profile is Docker's default plus `unshare`, `clone`, `setns`, `mount`, `umount2`, `pivot_root`, `mount_setattr`, `open_tree` and `move_mount`. It is kept at quantile `.github/factory/host/seccomp-bwrap.json`; a temporary copy is at `pop-os:/mnt/workbench/factory-seccomp/`.
- **`systempaths=unconfined` is still required** (bubblewrap mounts its own `/proc`). Under rootless Docker the unmasked kernel files stay unreadable to the unprivileged host user.
- **`.git/config`** held no token (`persist-credentials: false`).
- **The job GitHub token** is passed to Claude on purpose by the action (`GH_TOKEN`/`GITHUB_TOKEN` for `gh`), and the scrub leaves it alone. Under the network sandbox, Bash can't reach GitHub. The phase 2 agent job holds a read-only token that expires with the job. Optional hardening: try `sandbox.credentials` (not yet tested).

**Design rules (D1, D2): `software-factory_design.md`.** First drafted as quantile ADR-21/22 (`6d58c6c`); CD undid that commit because the rules are generic (F22).
- **D1:** the stage contract. Labels hold state, dispatch advances, writer jobs write, and one posting identity makes markers unforgeable.
- **D2:** the agent credential boundary. Every agent step runs under a tool-policy file, and Bash stages need the scrub, bubblewrap, a mandatory network sandbox, the narrow seccomp profile, and a smoke probe before use.

A software-architect review of the drafts found 4 majors. The main one: `factory-smoke`'s Claude step ran with no tool policy. The fix (it now loads `triage-tools.args`) plus apply's estimate-value validation are re-committed in quantile `42925c0` without the ADRs.

**Phase 2 agent-job recipe (built and proven, 2026-10-08; quantile `59b695b`..`e2b1e7f`):**
- **Image and host:** `bubblewrap` and `socat` are in the job image (`sha256:3ad5551…`), and `setup.sh` installs the seccomp profile at `/etc/factory-runner/seccomp-bwrap.json` (CD ran it).
- **Container `options`:** `--security-opt seccomp=/etc/factory-runner/seccomp-bwrap.json --security-opt systempaths=unconfined`.
- **Job env:** `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`.
- **Sandbox settings:** `.github/factory/bash-sandbox.settings.json`. Copy it out of the workspace, then pass it with `--settings` and as the action's `settings` input. Add `--strict-mcp-config`. Widen `allowedDomains` per stage only.
- **After the agent:** run only frozen code, with `/usr/local/bin/python3 -I` and git hooks off.
- **Gate:** `factory-smoke`'s `bash-sandbox` job must pass. It did on run 37841112243. Sandboxed Bash sees no credential, including the GitHub token, which closes the spike's "visible by design" gap.
- **CI:** a `workflow-policy` job checks every workflow against D1/D2. It's a drift check, not a security control (D2 rule 6, CD's decision after review round 4). The boundary is CODEOWNERS plus the ruleset, the App without `workflows`, and the runtime probe. Its known gaps are in D2 § Leaves open.
- **Implement-stage design item:** run every agent job through one reusable `factory-agent.yml` with a frozen runtime pre-agent check (D2 § Leaves open). Also add `--append-system-prompt` to the policy's `claude_args` allowlist when stages start declaring headless mode.
- **Rules:** D2 in `software-factory_design.md` carries the full set.

### Phase 3 lite path (2026-10-09): built, pushed, first live run on #30

Design rule D3 (the planning tier) is in `software-factory_design.md`. Built in quantile (`c998c3c`, then the App-identity switch from a parallel session, `9bffba1`..`1f44269`):

- **Planning tier:** `factory-planner` user, label `factory-plan`, runners `pop-os-planner-1`/`-2`, 10 GiB cap, a firewall exception for tcp 5432 to the host only. Runner group 4 lists `factory-plan.yml`.
- **Production data:** the `factory_reader` role (SELECT on 36 tables, read-only, 60 s statement timeout, 4 connections). `auth_user`, `django_session` and `django_admin_log` are excluded. `db-access.json` plus `db_access_check.py` in CI flag unreviewed sensitive-looking columns. pgbouncer on the job container's loopback (6432) holds the password from the `factory-planning` environment; the agent never sees it.
- **Workflows:**
  - `factory-plan.yml`: a claim job reserves the ID (`<!-- factory-id: Dnn -->`). The plan job runs `/sdlc-lite-plan` with Opus and a Fable advisor at `--effort high`, with open internet (`WebFetch(domain:*)`). Publish opens a ready-for-review plan PR (docs/ only, `Refs #n`). A question saves the session as an artifact, and the reply resumes it.
  - `factory-advance.yml`: merging `factory/<n>-plan` dispatches `factory-implement` with `plan=`, which runs `/sdlc-lite-execute` and publishes as the execute stage.
  - Triage dispatches plan for lite `ready-to-plan`.
- **Guards:** `implement_guard.py` takes a stage argument (doc stages publish `awaiting-approval` or `escalated`). The workflow policy keeps planning runners and the `factory-planning` environment to the planning workflows.
- **Smoke (run 37899281812, all 7 jobs green):**
  - Resume across containers works, including structured output.
  - Credential masking works under the env scrub. The sandbox saw `fake_value_…` placeholders, and httpbin received the real values, for both a credential-shaped and a plain variable name. So future services (`services.json`, Sentry) can use mask-and-inject instead of MCP servers.
  - The earlier mask "failure" was the probe model declining to run an inline command, not the mechanism. Probes now run frozen scripts.
- **Next:** finish the first lite run (#30 → plan PR → CD merges → execute → draft PR). Then the revise stage (F15/F16), the full-tier spec stage (resume plus discovery notes), and `services.json` once a Sentry token exists.

### Phase 2 implement stage (2026-10-08/09): pushed, smoke green, first live run on #12

- **Live fixes after the review rounds (quantile `d2a4eb5`..`34f683a`, all on `main`):** `git_guard.sh` with fixture-repo CI tests and a workflow-policy rule that agent jobs remove the git remote (`d2a4eb5`); the image with Postgres 16 and Redis pinned at `sha256:0db6b7c4…` (`f667d53`). Then four smoke runs taught four things:
  1. The Linux sandbox blocks creating any Unix socket (its seccomp helper is built in), so the services can't be reached over sockets (run 37874241000).
  2. `allowAllUnixSockets` drops that helper, and with it the nested PID namespace and clean environment: sandboxed Bash read the job's GitHub token from `/proc/1/environ` and could reach Claude Code's own sockets (run 37874841855). Rejected. The services moved to the container's loopback, reached through the sandbox's HTTP proxy with `localhost` allowed and a read-only forwarder, `/opt/factory/with-test-services` (`bafc82d`).
  3. Inside the sandbox `HTTP_PROXY` carries a per-session credential (`7090f05`).
  4. After an agent run `.git/commondir` holds `.` and `actions/checkout` leaves `config.worktree` (`sparseCheckout = false`): both inert, now logged and removed by the guard (`34f683a`).
- **Smoke run 37877737492: all green** (smoke, bash-sandbox, implement-tools). Runner group 4 now admits `factory-implement.yml` (CD approved; `admin:org` scope added to CD's `gh`).
- **First live runs:** issue #12 (the `/app`-hard-coded import-boundary tests), triaged `ready-for-dispatch` (direct, high/high/light) by run 37877766976.
  - Implement run 37878253736 failed: the orchestrator dispatched `sdet` in the background and its turn ended first. The skill now requires foreground dispatch; the leftover-sandbox check now ignores zombies (quantile `8c54e57`).
  - Implement run 37878603427 succeeded: **draft PR #13** by `z-software-factory[bot]` (one commit, +8/−1 in the test file), CI green including `ci-ok`. 13 turns, $1.37 at API rates, Sonnet with no advisor, zero orchestrator edits, two review rounds (`sdet`, `code-reviewer`, `software-architect`). It ran only that test file, not the full suite (CI did).
- **Auto-start on (quantile `05ed5e8`):** triage's apply job now dispatches implement for `ready-for-dispatch` (F6).
- **Next:** CD reviews PR #13; after it merges, remove the `/app` symlink from the implement job. Compare `advisor: opus` / `fable` on the next similar issues against this baseline.

### Phase 2 implement stage (2026-10-08/09): built and reviewed

- **Quantile commits (local):** `85a375d` (Postgres 16 and Redis in the job image), `eed2423` (the stage), `1d4e3ee`, `d699058`, `2ff6ab2` (review rounds 1–3). Review: 3 rounds × 4 reviewers (code, architecture, infra/security, sdlc conventions). Round 3 found one critical, a round-2 regression in the services environment check that would have failed every run; fixed in `2ff6ab2` and verified by running it (clean, leak and blanked cases), but not re-reviewed: the cap.
- **Shape:** `factory-implement.yml` runs `/sdlc-implement` (new project skill) on the factory runner with sandboxed Bash (no network), the repo's agents, and Postgres/Redis on Unix sockets started by `test-services.sh`. A `publish` job (`ubuntu-latest`, `factory-writer` environment) checks the bundle with `implement_guard.py` and pushes `factory/<n>-impl` as a draft PR with the `z-software-factory` App token; a `report` job comments and labels with `GITHUB_TOKEN`. Statuses: `done`, `escalated` (review cap, a decision for CD, or a test that won't pass: draft PR + `factory:review-capped`), `needs-input`, `rescope` (back to triage: a `<!-- factory-stage: triage from=implement -->` comment that triage reads as evidence, not as one of its question rounds), `failed`. Resume has an `implement` case.
- **CD's decisions (2026-10-08):** orchestrator `claude-sonnet-5-5`, effort medium; the agents keep their frontmatter models; an `advisor` input `none` / `opus` / `fable` (Fable is included on the factory account), `none` first as the baseline, the run summary counts advisor calls and orchestrator edits. No factory label after a `done` draft PR opens (an `escalated` one gets `factory:review-capped`). No auto-start after triage until a manual run succeeds. `/app` symlink for the 8 tests that hard-code it (fixing the test is a good first factory issue). Codex and a Fable subagent were consulted on the model setup: both favored a Sonnet orchestrator over Opus; they split on starting with the advisor, hence the baseline-then-compare plan.
- **Verified locally:** the full suite against the socket-only services: 3044 passed, 1 skipped. The services lockdown refuses superuser login, `COPY TO PROGRAM`, `MIGRATE`, `REPLICAOF`, protected config; the env check catches a leaked variable. Guard unit tests: 16.
- **Rollout (README § Operating notes):** push the image commit → `factory-image` builds → bump the digest in every factory workflow → `factory-smoke` green (`bash-sandbox`'s `unixsock` lines and the new `implement-tools` job) → add `factory-implement.yml` to runner group 4 (org-admin API, CD approves) → first live run on a small triaged issue (dispatch, or remove and re-add the label).
- **Deviations:** `outbound` is a list of strings, listed in the PR body (CD: list, don't apply). The revise stage isn't built; the PR footer says so.
- **Open minors:** Redis Lua CVE patch floor for the image (EVAL must stay: channels-redis uses it); no CI test with fixture repos for the Package step's `.git` checks; a `workflow_policy.py` rule that agent jobs remove the remote; WebSearch and Context7 queries are outbound text the agent writes (CD to decide); a sandbox `denyWrite` for `CLAUDE.md`; whether the advisor's `server_tool_use` shape matches the summary's count (check on the first `opus` run); whether `--append-system-prompt` reaches the CLI through the action's extraArgs (the skill and `--permission-prompts none` cover it if not).

### Headless rule progress (2026-10-08): committed (`2df932e`), ported to quantile (`c23aaae`)

This is the phase 2 prerequisite. Changelog entry: `process/sdlc_changelog.md` § 2026-10-08. It was reviewed in rounds: each had `sdlc-reviewer` passes plus a cross-framework check, and all majors are fixed.

- **The rule:** `process/headless-mode.md`.
  - **Detection:**
    - The primary signal is a line starting `SDLC headless mode:` in the caller's prompt or appended system prompt.
    - The fallback is that no ask-the-user tool can be used: none is available or loadable, or a call to it is denied without an answer (`--permission-prompts none`).
    - A subagent is never headless itself. The orchestrator tells each subagent the run is headless, so the limits bind it.
  - **Stops:**
    - `needs-input`: a question the next step depends on.
    - `escalated`: a bounded loop ran out (review cap, a FIX that failed twice, external-gate rounds). A twice-failed FIX is not reclassified.
    - `awaiting-approval`: a spec, a plan, or a full action plan is ready. The run never calls `EnterPlanMode`/`ExitPlanMode`.
    - `failed` with a `reason`: a precondition the caller must fix.
  - **No stop:**
    - Soft gates (FAR, FACTS) continue on a pass.
    - Non-blocking questions (PRE-EXISTING, minor PLAN findings) are listed under `deferred`. A critical or major PLAN finding stops.
    - Optional offers take the no path.
    - Local commits proceed.
    - Questions the prompt or thread already answers are not gates.
  - **No side effect outside the working tree** unless the caller's prompt names it. Reads are fine. That covers push, PR, comment, label, publish, external send and live-system change. Skipped actions are listed under `outbound`.
  - **github-provenance checkpoints** (`process/github-checkpoints.md` § Headless Runs): the run still does each checkpoint's local half. When the issue is known, that is the `github_issue:` frontmatter and the catalog link; for the ⎘ checkpoints, a local artifact commit. Its GitHub half goes under `outbound` as a rendered entry: issue, title and labels for a new issue, the full comment, Status target with rank and `write_if`, close, and the SHAs to push. A `ranks` item rides inside `outbound`.
  - **Ending:** the run ends its turn normally; the status carries the outcome. With `--json-schema`, the caller's schema is the contract. Otherwise the result is a `## Headless Result` block: status, stage, reason, questions, findings, documents, deferred, notes, skipped, outbound.
  - **Restart, not resume.** `sdlc-plan`, `sdlc-lite-plan`, `sdlc-execute` and `sdlc-lite-execute` each have a **Headless restart** paragraph in step 0. It skips finished work, never re-registers the deliverable, and keeps the review round and frozen roster. In `sdlc-plan`, an approved spec → 3d.
- **Mirrored in all 27 skills:** the `headless-stop-rule` MIRROR block.
- **Gate-site lines:** in `sdlc-plan`, `sdlc-lite-plan`, `sdlc-execute`, `sdlc-lite-execute`, `review-fix-loop.md`, `html-rendering.md`, `external-review-gate.md`, `github-checkpoints.md` and the six checkpoint-firing github-provenance fragments. `CLAUDE-SDLC.md` carries a paragraph.
- **What phase 2 needs to do with it:**
  - **Declare headless.** Every factory agent step adds `--append-system-prompt "SDLC headless mode: no person is present."` to `claude_args`. Triage already gets the fallback through `--permission-prompts none`; the declaration makes it explicit.
  - **Shape each stage's `--json-schema`.** It carries:
    - a status field: `done | needs-input | awaiting-approval | escalated | failed`;
    - `questions`;
    - `deferred`;
    - `notes`, which the writer job posts as the running discovery-notes comment (F18);
    - `outbound`;
    - for `awaiting-approval`, the document path or the full action plan.
  - **The writer job applies `outbound` checkpoint entries** in the documented order: push the linked commits unchanged → find (by `Dnn` prefix), create (with the comment as the body) or retitle the issue → board add → comment (skipped when the issue was just created with it as body) → read Status and write only if `write_if` holds → close.
    - Pass the issue number in every stage prompt, so the run writes the issue links itself.
    - The writer job searches for an existing `Dnn` issue before creating one. For Status it uses the `ranks` item inside `outbound`: an empty Status is rank 0, a current column missing from `ranks` means skip the write, and the target is written only if `write_if` holds. It holds CP-10 until the moved files are on `main` (the links resolve), whatever the merge method, and skips a close when an earlier entry for the same issue failed.
    - Ship the implement agent's commits as a `git bundle`, not a patch. A bundle keeps the SHAs that checkpoint comments link; a re-applied patch rewrites them and the links 404. This settles the "patch or `git bundle`" choice above.
    - Board (Projects v2) writes probably need a token with organization-projects access. `GITHUB_TOKEN` likely can't write org project boards. Verify before relying on it; if so, the App token needs that permission, or Status writes stay off and the issue comments carry the trail.
    - The stage schema's `outbound` field must hold objects, not just strings.
  - **The factory owns the label mapping:**
    - `escalated` at the review cap → draft PR + `factory:review-capped`;
    - `awaiting-approval` → open the doc PR;
    - `failed` → the failure comment.
  - **Restart prompts** name the stage and the deliverable, and carry CD's answer or the approval (for example, the merged spec PR). That lets `sdlc-plan`'s Headless restart pick up at the right step.
  - **Quantile has it (2026-10-08):** committed upstream as `2df932e` and ported directly into quantile as `c23aaae`, with no migration and no release. CD will ship the factory features upstream as a new **major** version; quantile's `.sdlc-manifest.json` records the port under `ported_commits`, with `source_version` still v1.9.0.
  - **Promotion:** when `sdlc-triage` moves to cc-sdlc, it carries the mirrored block like every other skill.
- **Not done here:** parking at the review cap (draft PR plus `factory:review-capped`), labels, markers and writer jobs. Those stay with the factory, per F13.
- **Open design item:** the plan → execute hop has no unchanged-since-approval guard for the plan. `sdlc-plan` records the spec's content hash so a restart can check the spec, but `sdlc-execute` step 0 doesn't check the plan against what CD approved. In the factory, merging the plan PR fixes the content on `main`, so this matters only for callers without that step. Decide it in `process/headless-mode.md`'s approval-gate row.

### Phase 1 progress (2026-10-07): COMPLETE except CD's calibration grading

- **Live tests on quantile:** test issues #8, #9 and #10 got `ready-for-dispatch`, `ready-to-plan` (lite) and `needs-input` as expected.
- **Resume:** the first live resume failed because `gh workflow run` needs `--ref` without `contents` access; fixed in `66f0117`. The rollback restored the label and posted the failure comment. The retry worked end to end:
  - CD's reply started resume, which swapped the label to `factory:triage` and dispatched triage;
  - triage re-ran with the thread, read the earlier answers, and labelled the issue `wait` (overlaps D11, owned by D11c/#7).
- **Test issues** are closed as not planned.
- **Done-when status:**
  - the three issues got the expected labels;
  - the agent provably cannot write: by job permissions, and by the smoke tool-policy probe;
  - a `needs-input` reply restarts triage;
  - the agreement rate comes from the 15-case calibration: Sonnet matched 10 of 15 and all 5 others were evidence-backed. CD grades the calls.

- **Shipped:** quantile `f624ec5`, plus three smoke-scan fixes up to `7346052`.
- **Host:** `setup.sh` was re-run, and the kernel now enforces the caps: the user slice gets 12 GiB soft and 16 GiB hard memory, 12 CPUs and 4,096 tasks; the runner service gets 2 GiB and 512 tasks.
- **Runner group:** group 4 is restricted to `factory-smoke.yml` and `factory-triage.yml` on `main`.
- **Smoke run 37676930447: green.**
  - Isolation holds.
  - 26/26 skills and 12/12 agents loaded, and Context7 connected.
  - Tool-policy probe: Read on `/proc`, `.git`, `/__w/_temp` and `/github` was denied; a repo read and Context7 were allowed; no Bash, write or WebFetch tools were available.
  - Exact-value credential scan: neither the job's OAuth token nor its GitHub token is readable by the agent.
- **Usage measured after setup and 4 smoke runs:** the user slice peaked at 3.2 GiB and 189 tasks; the runner service peaked at 205 MiB.
- **Remaining:**
  - the three live test issues and the resume reply (needs CD's approval);
  - CD grades the 15 Sonnet calibration calls.

- **Built in quantile (uncommitted while under review):**
  - `.claude/skills/sdlc-triage/SKILL.md`
  - `.github/factory/triage.schema.json`
  - `.github/workflows/factory-triage.yml` and `factory-resume.yml`
  - stage contract in `.github/factory/README.md`
  - `setup.sh` cgroup caps. These are not yet applied on the host: CD re-runs `setup.sh`.
- **Decided this session:**
  - Triage model is **Sonnet** (CD). It is a `workflow_dispatch` input for A/B runs.
  - **No `vision.md`/`roadmap.md`**: triage reads CLAUDE.md's goals, stage and phase sections, plus the catalog.
  - **Resume chains through `workflow_dispatch`**, the one event `GITHUB_TOKEN` may trigger, so no App token or PAT is needed.
  - The triage agent runs with **`--tools Read,Grep,Glob`**: no Bash, web or write tools.
  - The issue is **pre-fetched to a file**.
  - **Writer jobs run on `ubuntu-latest`.**
  - The job image is **pinned by digest**.
  - **Invariant:** comments, labels and markers are posted only with `GITHUB_TOKEN`. The App token only pushes and opens PRs.
  - **Triage tool policy (CD, 2026-10-07)**, single source quantile `.github/factory/triage-tools.args`, probed by `factory-smoke`:
    - **Tools:** Read, Grep, Glob, WebSearch and Context7, pre-approved because auto mode can't prompt.
    - **Denied reads:** `/proc`, `/dev`, `.git` and the runner's mounts. The deny rules also bind Grep and Glob.
    - **Not given:** Bash, write tools and WebFetch.
    - **Why WebFetch was dropped:** CD noted that Context7 covers docs. Context7 indexes the Kalshi, Coinbase Advanced Trade and Binance Spot API docs, and WebFetch was the one channel injected text could use to send repo content to an arbitrary URL.
    - **When Bash returns:** once phase 2 proves credential-scrubbed Bash (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` or the Claude Code sandbox) inside rootless Docker.
- **Stage contract, adopted (architect review, option A):**
  - Agents never write to GitHub. Writer jobs using `GITHUB_TOKEN` post every comment and label, so every factory comment is by `github-actions[bot]`.
  - Markers form a block of consecutive lines at the top of a factory comment. The stage marker `<!-- factory-stage: <stage> [k=v ...] -->` comes first, then the machine-readable `<!-- factory-triage: {state,tier,estimate} -->`.
  - Questions always go on the issue.
- **The handoff's pilot plan doesn't fit quantile.** It has six open issues, all deliverables or parked, so the "~20 real issues" pilot is replaced by:
  - a 15-case synthetic calibration set, run locally on Sonnet and Haiku and graded by CD;
  - three live GitHub test issues.
- **Review:** three rounds with `sdlc-reviewer`, `code-reviewer`, `software-architect` and `infra-engineer`. The last three ran as general-purpose agents working from quantile's agent files. No critical or major findings remain open.
- **Open minors at the cap:**
  - deduplicating an identical repeat question round;
  - a CD reply that lands mid-run isn't seen;
  - cancelled runs post no comment;
  - the round limit is enforced by the skill, not mechanically by apply.
- **Calibration, run locally on 15 synthetic cases with CI's flags:**
  - **Sonnet:** matched the expected label on 10 of 15. Each of the 5 others was evidence-backed. $0.136 per issue, 6.8 turns.
  - **Haiku:** called `ready-for-dispatch` on a cross-container API change, and two of its runs produced no usable structured output. $0.126 per issue, 13.7 turns.
  - **Decision:** Sonnet stays.
  - CD still grades the Sonnet calls.
- **Haiku 5.5 rerun** (Haiku 5.5 was released 2026-10-07; three runs × 15 cases on the current skill, for both models):
  - **Sonnet 5.5:** 45/45 acceptable calls; the same state across all three runs on 11/15 cases; $0.083 per issue.
  - **Haiku 5.5:** 41/45 acceptable calls; consistent on 9/15; $0.006 per issue. Its misses invented collisions to justify `wait` (c09, c13).
  - Neither made a wrong `ready-for-dispatch` call.
  - **Sonnet stays.** Models are pinned by full ID (quantile `f612c5f`; smoke run 37711284994 is green on `claude-sonnet-5-5`).
  - **Rubric soft spots, where both models flip between runs:**
    - whether a deliverable's plan merely listing a file counts as a collision (c01);
    - the lite/full tier boundary (c06, c12, c13).

    CD's grading should settle both.
- **Deferred to phase 2** (from the four-agent review):
  1. A CLAUDE.md factory exception for deliverable IDs. `ready-for-dispatch` allows a handful of files, while § Deliverable Tracking says more than one file gets an ID (F11 says direct-tier takes none).
  2. **Chain by dispatch; writer jobs push.** Now written into the phase 2 requirements below (dispatch chain; pushes and PRs from a writer job with an App token; agents never post). The rules (item 3) are in `software-factory_design.md` § D1.
  3. ~~An ADR: "labels are state, dispatch advances, writer jobs write".~~ Done as design rule D1 (F22).
  4. Extract the duplicated MCP-config step into a composite action or script.
  5. Upload `issue-context.json` and the result as artifacts for phase 4.
  6. Move quantile-specific triggers into a project policy file before promoting to cc-sdlc.
  7. Bake Claude Code into the image (`path_to_claude_code_executable`).
  8. Restrict the runner group to selected workflows on `main`, after merge.
  9. Add `.factory/` to quantile's `.gitignore`. The triage fetch step writes `issue-context.json` there, and a phase 2 implement run committing from the workspace would pick it up.

### Phase 0: runner on the PC (a session running on the Linux box)

Work through these in order. The isolation steps come before any job runs (F14).

1. **Survey the host.**
   - Confirm the OS (Pop!_OS expected).
   - List the production compose services and their bound ports, especially Postgres and Redis.
   - Read quantile issue #3 ("Parked: pop-os hardening — ignore-file gaps, exposed DB/cache ports, dev compose in prod").
2. **Create a runner account.** A dedicated `factory-runner` Linux user with no sudo, no personal SSH keys and no cloud credentials.
   - **Caution:** membership in the `docker` group is root-equivalent on the host. Use **rootless Docker** (or Podman) for this user, so a job container cannot reach the host's Docker or production containers.
3. **Isolate the network.**
   - Job containers get a dedicated Docker network.
   - Block that subnet from the host's production ports, using iptables or nftables rules (the `DOCKER-USER` chain for rootful Docker; for rootless, verify how egress to host ports is blocked).
   - Verify from inside a test container that `nc -z <host> 5432` and `6379` fail.
   - Fixing issue #3's exposed ports is separate work, but it overlaps.
4. **Register the runner.**
   - Create an org-level runner group in `endless-galaxy-studios`, restricted to the `quantile` repo.
   - Register one runner with the labels `self-hosted, linux, factory`.
   - Run it as a service under `factory-runner`.
5. **Build the job image.** It holds:
   - Python and Node versions matching quantile;
   - `gh` and `jq`;
   - a Context7 MCP config, passed via `--mcp-config`. The framework requires Context7 for library docs.

   For Postgres and Redis, tests use GitHub **service containers** next to the job container. No Docker-in-Docker, and no host Docker socket.
6. **Pin the versions.** Pin `anthropics/claude-code-action` to a specific release commit SHA, not `@v1`, which moves.
   - **Why it matters:** the docs say `--bare` "will become the default for `-p`". Bare mode skips skills, agents and CLAUDE.md, and never reads OAuth credentials, so a silent default flip would remove the framework *and* break Max auth.
   - **How the pin works:** the action runs `bun install --production` against its own committed `bun.lock`, which pins `@anthropic-ai/claude-agent-sdk`. So a SHA pin should also pin the Claude Code runtime. Confirm the version in the smoke run's init event.
   - `path_to_claude_code_executable` is the explicit alternative: it points at a binary pinned in the image. The action's docs warn against older versions.
   - Upgrade on purpose, and re-run the smoke test each time.
7. **Store the secret.** CD runs `claude setup-token` and stores the result as a **repo** secret `CLAUDE_CODE_OAUTH_TOKEN` on `quantile`. It should not be an org secret, because the token is tied to CD's subscription.
8. **Set the environment.** Set `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` well above the 10-minute default, with the job's `timeout-minutes` as the backstop. Without it, `-p` runs stop waiting on background subagents after 10 idle minutes and drop their results, and cc-sdlc dispatches background agents constantly.
9. **Smoke workflow** (`workflow_dispatch`). It runs the action and **fails** when any of the items below is missing.
   - **How to check:** assert on the init event in the action's `execution_file`, which lists tools, MCP servers and plugins, and possibly skills and agents. That is a fact from the runtime. Fall back to asking Claude to list what loaded only for whatever the init event doesn't carry, since that is self-report.
   - **Items:**
     - the `sdlc-*` skills;
     - the `.claude/agents` definitions (still unverified that the action loads them; this run settles it);
     - Context7.
   - **Cost:** it writes `total_cost_usd` (from the JSON output or the `execution_file`) to the job summary.
10. **Create the labels.** Add the seven `factory:*` labels from the table to quantile.
11. **Optional:** run `sdlc-migrate` on quantile, v1.8.0 → v1.9.0 or later. This picks up the bounded review loops (`44d6cc0`) and the `sdlc-render` → `sdlc-explain` rename. It is required before phase 2, and fine to do now.

**Done when:**
- The smoke workflow is green on the PC runner.
- The skills, agents and Context7 are confirmed loaded.
- A cost figure is reported.
- The container-to-host production-port test fails as intended.

### Phase 1: triage only (built in quantile)

1. **Triage skill** at `quantile/.claude/skills/sdlc-triage/SKILL.md`. Use the final name so promotion into cc-sdlc needs no rename.
   - It is **read-only**: it inspects the issue, the comments, related issues, the codebase and the catalog, and writes nothing.
   - **Rubric:** cc-sdlc's tier definitions and the validity/correctness/effort estimation model (`CLAUDE-SDLC.md:35-57`). Warp's triage skill (`cloud-factory-demo/.agents/skills/triage/SKILL.md`) is a good shape reference: "choose the more cautious state when between states."
   - **Output:** structured JSON enforced with `--json-schema`, read from the action's `structured_output` output:
     ```json
     {"state": "ready-for-dispatch|ready-to-plan|needs-input|wait",
      "estimate": {"validity": "...", "correctness": "...", "effort": "..."},
      "tier": "direct|lite|full|null",
      "comment": "reporter-facing markdown: decision, evidence, next step",
      "questions": ["only when state = needs-input"]}
     ```
   - **Product direction:** quantile has no `vision.md` or `roadmap.md`. Decide whether to add short ones, as triage reads them in Warp's demo, or to have triage rely on the README and the catalog.
2. **Workflow `factory-triage.yml`** with **two jobs**, as in Warp's demo.
   - **Why two jobs:** Actions permissions are set per job, not per step. A read-only agent job therefore can't contain a step that writes labels.
   - **Trigger:** `on: issues: [labeled]`, filtered to `factory:triage`.
   - **`triage` job.**
     - Runner and limits:
       - `runs-on: [self-hosted, factory]` with the phase 0 job `container:`;
       - `permissions: contents: read, issues: read`;
       - `timeout-minutes` (start at 30);
       - `concurrency: factory-issue-${{ github.event.issue.number }}`.
     - Action inputs:
       - `prompt: "/sdlc-triage <issue URL>"`;
       - `claude_code_oauth_token`;
       - `github_token: ${{ secrets.GITHUB_TOKEN }}`. This keeps the agent read-only; when it's omitted, the action uses the Claude App token, which can write.
       - `claude_args` with `--json-schema …`, `--permission-mode auto`, `--permission-prompts none`, `--max-turns`, `--mcp-config <context7>`.
     - Why the permission flags matter: in automation mode the action grants no shell or GitHub tools by default, and none of the 27 cc-sdlc skills declare `allowed-tools`. `--permission-mode auto` has a classifier review actions instead. `--permission-prompts none` removes `AskUserQuestion`.
     - Expose the action's `structured_output` as a job `outputs:` value, and write `total_cost_usd` to the job summary.
   - **`apply` job.**
     - Setup: `needs: triage`; `permissions: issues: write`; no container needed.
     - Steps: parse the output, remove `factory:triage`, add `factory:<state>`, post the comment.
     - For `needs-input`, put `<!-- factory-stage: triage -->` in the question comment.
     - Token: its own `GITHUB_TOKEN`, in every phase. Writer jobs post all comments, labels and markers with it; stages chain by `workflow_dispatch`, not by label events (see the dispatch-chain note).
   - **Failure path** (`if: failure()`, its own small job with `issues: write`): comment on the issue that triage failed, link the run, and leave `factory:triage` in place so a re-run is one click. This covers Max-window exhaustion mid-run, which would otherwise fail silently.
3. **Resume workflow `factory-resume.yml`** (phase 1b; the same mechanism every later stage reuses).
   - **Trigger:** `on: issue_comment: [created]`.
   - **Run only when:** the target is an issue, not a PR (`!github.event.issue.pull_request`, since `issue_comment` also fires on PR comments); the issue carries `factory:needs-input`; the commenter has write access; and the commenter is not a bot.
   - **Action:** read the `factory-stage` marker from the most recent factory question comment and re-run that stage, which in phase 1 is always triage, with the whole thread as context (F7).
4. **Pilot.** Create three test issues: a small bug, a feature that needs a spec, and a deliberately vague request. Expected labels: `ready-for-dispatch`, `ready-to-plan` and `needs-input`.
   - Then run triage on about 20 real issues and **grade each call** (agree or disagree, with the reason).
   - Do not use the open D11/D12 deliverable issues (#2, #4-#7) as triage tests. They are already-planned work.

**Done when:**
- All three test issues get the expected labels.
- The agent provably cannot write to the issue.
- A `needs-input` reply restarts triage.
- The ~20-issue agreement rate is recorded.

**Usage controls** (F12 plus the Max ceiling):
- One runner instance.
- A `concurrency` group per issue.
- `--max-turns` and `timeout-minutes` on every job.
- Usage credits off.
- Consider `--model` Sonnet for triage to stretch the Max window. CD's call.

## Requirements for later phases (recorded so they aren't lost; not in this handoff's scope)

**Phase 2: `factory:ready-for-dispatch` → implement → review → draft PR.** Prerequisites:
- **Headless rule (cc-sdlc framework change, F13). DONE: cc-sdlc `2df932e`, ported to quantile `c23aaae`; see § Headless rule progress.** One process doc plus a line mirrored in each skill, never only a pointer (the 2026-05-19 lesson). In headless mode, every interactive gate becomes: return the question(s) as structured output and exit 0; the stage's writer job posts the question comment with the stage marker and adds `factory:needs-input`. Agents never post. The gates are:
  - the global `AskUserQuestion` rule (`CLAUDE-SDLC.md:174-184`);
  - the spec approval gate (`sdlc-plan:396-398`);
  - `EnterPlanMode`/`ExitPlanMode` (`sdlc-plan:646-667`, `sdlc-lite-plan:375-395`);
  - phase triage SKIP/REVISE (`sdlc-execute:185`, `sdlc-lite-execute:161`);
  - the review-cap escalation (`review-fix-loop.md:231`).
- **Park at the review cap.** Open a draft PR with the open-findings table and `factory:review-capped`, then park via CP-11/CP-11b. Both outside reviewers recommended this in the review-loop consult, and that handoff deferred it to "the factory work".
- **Dispatch chain (replaces the label chain).** Labels applied with the default `GITHUB_TOKEN` do not start workflows, but `workflow_dispatch` does. So labels record state, and a writer job advances a stage with `gh workflow run factory-<stage>.yml -f issue_number=N` (`actions: write`). Phase 1's resume already works this way, with `allowed_bots: github-actions` on the agent step. Each stage workflow can also keep `issues: labeled` so CD can trigger it by hand. No App token or PAT is needed to chain.
- **Pushes and PRs come from a writer job, never the agent.** The implement agent keeps a read-only `github_token`, commits locally and uploads a patch or `git bundle` artifact (so artifact upload is a phase 2 prerequisite). A writer job on `ubuntu-latest`, in the `factory-writer` environment, mints an installation token for the factory's own app, **Z Software Factory** (`actions/create-github-app-token` with `vars.FACTORY_APP_ID` and `secrets.FACTORY_APP_PRIVATE_KEY`), pushes `factory/<n>-impl` and opens the draft PR. Using the App means the PR author isn't CD, so CD can request changes, and that any CI runs on its pushes (pushes with `GITHUB_TOKEN` trigger nothing). Quantile CI exists as of 2026-10-08 (`.github/workflows/ci.yml`, PR #11): the `make verify` gates on GitHub-hosted runners, with `ci-ok` as the aggregate check. **The writer job must reject patches that touch the gate's own config or the agents' configuration:** every path in quantile's `.github/CODEOWNERS`, which includes `.github/**`, `.claude/**`, `CLAUDE.md`, `.mcp.json`, `api/pytest.ini`, any `conftest.py`, `api/requirements.txt`, `web/package.json`, `web/package-lock.json`, the Dockerfiles and the `Makefile`. Read the list from CODEOWNERS on `main`, not from the patch's branch. The `.claude/` paths matter beyond CI: a later stage that checks out the factory branch with `--setting-sources user,project` would load that branch's settings, and their `env` applies outside the sandbox. CI calls eslint, tsc and vite directly, but a PR can still disable tests through pytest config or a conftest hook (CI review, major). CD decided (2026-10-08): the `main` ruleset (id 24746399) requires `ci-ok` plus code-owner review of the gate's own config (`.github/CODEOWNERS`), dismisses stale approvals and requires approval of the last push; admins bypass for CD's direct pushes, and factory PRs never merge by bypass. CI also builds every image, runs pytest and `makemigrations --check` inside the api image, and the model directory is `ML_MODEL_DIR`. Open (minor): pytest trusts only its exit code, so add a `--junitxml` test-count floor if the writer job's path check proves insufficient. The App has no `workflows` permission, so a patch touching `.github/workflows/` can't be pushed. Invariant: comments, labels and markers are posted only with `GITHUB_TOKEN`; the App token only pushes and opens PRs. **Done (2026-10-08):** created `z-software-factory` (App ID 5244270; Contents and Pull requests read/write, Metadata read; no webhook), installed it on all org repositories (CD: the factory rolls out to the other repos), and set up the `factory-writer` environment (deployment branch `main` only) with `FACTORY_APP_ID` and `FACTORY_APP_PRIVATE_KEY`. Anthropic's `claude` app can't fill this role: it has `workflows: write` and only Anthropic holds its key. **Writer jobs mint for their own repository only** (`actions/create-github-app-token` without `owner`/`repositories`, which scopes the token to the current repo). Each repo that adopts the factory gets its own `factory-writer` environment, limited to its default branch, holding a copy of the key. A leaked key can write to every repo the app is installed on, so if one repo's key is compromised, revoke it in the app settings and rotate it everywhere.
- **quantile migrated to cc-sdlc v1.9.0 or later.**
- **Revise stage (F15, F16).** Mechanics:
  - **Spotting factory PRs:** factory branches are named `factory/<issue#>-spec`, `factory/<issue#>-plan` and `factory/<issue#>-impl` (named by the writer job's push; the agent never pushes). The revise workflow filters on the `factory/` prefix, so your own PRs never trigger it. The suffix tells it which limit applies: 5 for `-spec`/`-plan`, 3 for `-impl`.
  - **Trigger:** `on: pull_request_review: [submitted]`, filtered to `review.state == 'changes_requested'`, a `factory/` head branch, and a reviewer with write access who is not a bot.
  - **Counting revisions:** each revise run posts a hidden marker comment (`<!-- factory-revise: N -->`). The workflow counts those markers before starting. When the PR's limit is reached (3 for code, 5 for spec/plan), it applies `factory:escalated` and posts the escalation comment instead of running (F16). Counting is mechanical and stateless; no counter file.
  - **Who opens factory PRs:** the writer job, **as `z-software-factory[bot]`, not under CD's identity**. GitHub doesn't let an author approve or request changes on their own PR. If PRs were opened as CD, the "Request changes" trigger would be unavailable to CD.
  - **Verify first:** whether GitHub allows a "Request changes" review on a **draft** PR. This only matters for code PRs, since doc PRs open ready for review (F17). If it doesn't, use a `factory:revise` label as the trigger for code PRs instead.
  - **No `@claude` workflow.** Don't install the action's interactive `@claude` workflow. "Request changes" is the only revision path, so every revision is counted (F15).

**Phase 3: `factory:ready-to-plan` → (full tier: spec stage with questions → spec PR → CD merges) → plan PR → CD merges → execute → draft code PR.**
- **Triggers:** merging a `factory/<issue#>-spec` PR starts the plan stage. Merging a `factory/<issue#>-plan` PR starts execution. Both use `on: pull_request: [closed]` filtered to `merged == true` and the branch suffix. The merge is done by CD, so the actor is human and `allowed_bots` doesn't apply.
- **Spec stage (F18):** the discovery questions go to the issue through `factory:needs-input`, and each reply restarts the spec stage. The receiving session must keep each restarted run cheap, for example by posting a running "discovery notes" comment that later runs read, so they don't redo the codebase research. This is 12-factor's stateless reducer: the thread is the state.
- **The revise stage (F15/F16)** covers all three PRs: spec, plan, then code. Doc PRs get 5 revisions, the code PR 3.
- **Data snapshot (F19).** Production must never be reachable from a job container. Suggested shape:
  - **Producer:** a host-level scheduled job, outside the factory containers, under its own Linux user with a **read-only** database role. It dumps the agreed tables and applies the agreed scrubbing.
  - **Storage:** it writes the dump to a snapshot directory on the host.
  - **Use:** spec and plan jobs mount that directory **read-only** and restore the dump into their Postgres service container. The firewall stays as it is: data flows one way, through a file.
  - **Stamp:** the snapshot date goes into the discovery notes, so specs say how fresh their data facts are.
- The ID claim on `main` (F11) happens before the first branch (spec for full, plan for lite). With a concurrency group, the receiving session decides whether claims serialize per repo or per org.
- Merging the doc PRs replaces `ExitPlanMode` and the spec approval gate as the approval surfaces.

**Phase 4: weekly improve loop.**
- Containers discard session transcripts (F4), so the loop harvests **human PR review comments, reactions and `needs-input` reasons**, as Warp's `improve-review-pr` does, rather than session JSONL. The alternative is mounting `~/.claude/projects` to a volume.
- It proposes skill and knowledge updates through `sdlc-audit` improvement mode or `sdlc-reflect`.
- It could run as a Claude Code Routine (Max OK, schedule trigger, runs in Anthropic's cloud) or as a scheduled workflow on the runner.

### Exploration: persistent planning sessions (before phase 3; CD asked to explore, nothing decided)

**The problem.** F18's discovery is one question per run, and each run starts cold in a fresh container. A full-tier spec takes 2-6+ question rounds, so the planning session forgets everything between your replies. Discovery notes soften this; a persistent session would remove it.

**Facts checked 2026-10-07:**
- **Cloud sessions:** "If Claude asks a question and the session sits idle, you can still answer when you come back, up to environment expiry, and the session continues from your answer." Reopening an expired session restores the conversation history; only running background work is lost.
- **Follow-ups from the CLI:** `claude -p "<message>" --cloud <session-id>` queues a message into an existing cloud session from any machine "logged in with `claude auth login`", including CI scripts.
- **Routines** can start a cloud session from an Action step (the API `/fire` endpoint, a per-routine bearer token, with the issue text in `text`).
- **Projects** (Pro/Max beta) show threads under **Waiting on you**, with desktop-only notifications.
- **The Action** exposes `session_id`. `--resume` accepts a session ID or the absolute path to a session's `.jsonl` transcript.

| Option | How it works | For | Against |
|---|---|---|---|
| **A. Resume on the runner** | Each spec run saves its transcript as an Actions artifact, keyed by the issue. Your reply triggers a new container that downloads it and runs `--resume <transcript path>` with your answer. Q&A stays on the GitHub issue. | Full memory, everything stays on your PC and GitHub, and container isolation (F4) is kept. | Each resume re-sends the whole conversation. After an idle hour the prompt cache has expired, so the context is rewritten at full price (take-1 measured about $1.1k a month of these). Whether the Action accepts `--resume` in `claude_args` is unverified. |
| **B. Cloud planning session** | `factory:ready-to-plan` (full tier) fires a Routine. Its cloud session runs `sdlc-plan` discovery, asks you questions natively, and waits for days if needed. You answer in the Claude app or on claude.ai/code. It opens the spec PR when done. | Truly persistent and native to the product. Uses your Max plan. Planning only reads code and writes docs, so it doesn't need your PC or its databases. | The Q&A lives in claude.ai instead of on the issue, so it's less visible to the phase 4 improve loop unless the session posts a summary. Context7 must be a claude.ai connector. Routines' `/fire` is a research preview. Mobile notifications when a session waits are unverified. |
| **B+ Cloud session plus an issue bridge** | Option B, plus a workflow that relays your issue replies into the session with `claude -p "<reply>" --cloud <session-id>`. The session mirrors its questions onto the issue. | Persistent memory *and* the Q&A stays on GitHub. | Needs a full `claude auth login` on the runner. The setup-token OAuth token "can only make model requests", so it probably can't send to cloud sessions. That puts a long-lived credential on the production box. Unverified. |
| C. Long-lived local session + Remote Control | The factory starts `claude --remote-control` outside the containers, and you answer from your phone. | Local and persistent. | Runs outside the job container on the production box, needs a full login, and pauses when the PC sleeps. Not recommended. |
| D. Hold the Actions job open | The job waits until your reply arrives. | Simple. | Blocks the single runner for hours, and the cache expires anyway. Not recommended. |

**What planning needs beyond reading code** (CD's concern, 2026-10-07): internet, scratch code and proofs of concept, and sometimes real data. Facts checked for B (cloud-environments docs):
- **The VM:** Ubuntu 24.04 with Docker and docker compose, PostgreSQL 16 and Redis 7 pre-installed (not running until started). Setup scripts run as root (`apt install` works) and are cached when they finish in about 5 minutes.
- **Network access:** None, Trusted (allowlist), Custom or **Full**.
- **Idle behavior:** an idle VM pauses with its files saved. If the VM is later reclaimed, the conversation survives but scratch files don't, so anything worth keeping gets committed to the planning branch.
- **Secrets:** on Pro/Max, "API credentials" attach a key (for example Kalshi) to matching requests without the session seeing it.
- **Comparison:** internet, scratch code and POCs work in B *and* on the runner. What B can't reach is anything on CD's network, including quantile's databases.
- **The same holds for the runner, by design:** F14 firewalls job containers from production, and secrets stay out of jobs. **Real-data access for planning is therefore a separate decision, whichever option is chosen:**
  - no data access: plan from code and schema, and ask CD for data facts;
  - a **data snapshot** loaded into the planning session's own Postgres. This works for A and B, as of the snapshot date.
  - live read-only access to a replica. This is only reasonable from the runner, as a narrow firewall exception, and it weakens F14.

**CD's decisions narrow this.**
- Real data comes from a **snapshot** (F19).
- The Q&A must live on **GitHub** (F20). That rules out **plain B**.

**Leading candidate: A (resume on the runner).**
- Questions and replies are native issue comments through `factory:needs-input` and the resume workflow, with nothing to relay.
- Runs happen where everything else runs.
- The snapshot can be mounted read-only into the job container.
- No extra credential is needed on the production box.

**Fallback: B+** (cloud session plus an issue bridge), if A fails verification. B+ needs the session to mirror its questions to the issue *and* a relay that forwards CD's issue replies into it. That means a full `claude auth login` on the runner. Replies made in the Claude app would also bypass the loop, so the rule would be to reply only on GitHub.

**If both fail:** F18's baseline of a fresh run with discovery notes per question already satisfies F19 and F20.

**Verify before choosing:**
1. A routine-fired session can ask with `AskUserQuestion` and wait.
2. How you get notified on your phone when it waits.
3. Whether the setup token can send `--cloud` follow-ups (decides B+).
4. Whether the Action honors `--resume` in `claude_args` (decides A).
5. Cost per round of A against fresh runs with discovery notes, measured on 2-3 real specs.

**Promotion (F13).** Once phases 0-2 work, move the triage skill, workflow templates (as reusable `workflow_call` workflows with per-repo caller stubs), label set and headless rule into an opt-in cc-sdlc `factory` bundle with github-provenance as a prerequisite. A new opt-in bundle is a **minor** version bump.

## Evidence

- **Research and comparison:**
  - `docs/current_work/ideas/software-factory_evaluation.md` (talk syntheses, the Claude-native primitives table, tool comparison, sources).
  - The take-1 session transcript: `~/.claude/projects/-Users-yovarniyearwood-Projects-cc-sdlc/8cac0907-4638-4c81-a191-75b29d6ec007.jsonl`.
- **Usage data** (take-1, 30 days, at API rates):
  - Totals: about $16.3k total; subagents 67%; 95% of it is context re-reads.
  - Per item: `sdlc-plan` about $106 and `sdlc-execute` about $155 per session; lite about $97 plan plus about $77 execute; direct dispatch median about $15.
- **Facts verified 2026-10-07 against code.claude.com:**
  - The action accepts `claude_code_oauth_token` (Pro/Max).
  - Action inputs include `label_trigger`, `allowed_bots`, `github_token`, `path_to_claude_code_executable`.
  - Action outputs include `structured_output` (with `--json-schema`), `github_token`, `session_id`, `execution_file`.
  - The `--bare` default flip is announced, and bare mode skips OAuth.
  - Background-subagent wait: 10-minute default, set by `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`.
  - `--permission-prompts none` removes `AskUserQuestion`.
  - `--output-format json` includes `total_cost_usd`.
  - Routines' GitHub triggers are PR and release only. Self-hosted environments and Claude Tag are Team/Enterprise only.
  - Max limits assume "ordinary, individual usage" (legal-and-compliance).
- **quantile state (2026-10-07):**
  - Private; owner `endless-galaxy-studios`.
  - cc-sdlc v1.8.0 installed, with the `design` and `github-provenance` bundles; still has `sdlc-render`.
  - No `.github/` directory.
  - Open issues: #2-#7, all `sdlc`-labelled deliverables, plus #3, the parked pop-os hardening.
- **Framework gaps:** the Explore pass in take-2 lists them with line numbers (summarized in the phase 2 prerequisites above).

## Recommended next step

1. Open a session **on the Linux PC** and work through **Phase 0** by direct dispatch, using this file as the checklist. It is infrastructure with a settled approach.
2. Then open a session in `~/Projects/quantile` for **Phase 1**. It is Light-to-Moderate: one skill and two workflows. Direct dispatch fits. Use `sdlc-lite-plan` if the receiving session judges the skill-plus-workflow coupling worth a reviewed plan.

## Open questions (for the receiving sessions)

- **Snapshot scope (F19), for CD before phase 3:**
  - Which tables go in. Market and price data probably do. Anything holding account, position or balance data, or credentials, needs a decision.
  - What gets scrubbed.
  - Refresh cadence: nightly or weekly.
  - Size limits. A subset may be needed if the database is large.


- ~~**Triage model**~~ Resolved: Sonnet (CD, 2026-10-07); the calibration compares Haiku.
- **Product direction for triage:** add `vision.md` and `roadmap.md` to quantile, or rely on the README and the catalog?
- **Rootless Docker** versus rootful Docker with `DOCKER-USER` rules: decide on the host, after the phase 0 survey.
- ~~**Read-only token for the action**~~ Resolved in phase 0 (smoke run 37643211247). confirm the action runs correctly with `github_token: GITHUB_TOKEN` (`issues: read`) and without `id-token: write`. If not, enforce read-only through the agent's tool permissions instead.

## Out of scope (do NOT pursue)

- Phases 2-4 builds, and any cc-sdlc framework edit. The phase 2 headless rule gets its own session in this repo, following `CLAUDE.md` (changelog, consistency checks, `sdlc-reviewer`).
- Local model work (F9).
- Slack integration, Linear, Claude Code Projects, Routines, and any vendor tools (Warp Oz, Cursor, Copilot, HumanLayer).
- Fixing quantile issue #3 beyond the port isolation the runner needs.
- Moving other projects onto the runner.
