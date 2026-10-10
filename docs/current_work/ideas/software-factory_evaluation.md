---
type: research
slug: software-factory
created: 2026-10-07
status: superseded-by-handoff
recommended_next_skill: direct-dispatch
related_files:
  - docs/current_work/ideas/software-factory_handoff.md
  - docs/current_work/ideas/review-loop-unification_handoff.md
  - docs/current_work/ideas/review-loop-unification_consult-record.md
  - process/github-checkpoints.md
  - process/review-fix-loop.md
  - CLAUDE-SDLC.md
---

# Software factory: adapt cc-sdlc or adopt a tool?

> **Superseded for decisions.** This document is kept as the research and comparison record: sources, talk syntheses, tool comparison and the Claude-native primitives table. Its recommendations were reconciled with the software-factory-take-1 session and CD's later answers. Where the two differ, [`software-factory_handoff.md`](software-factory_handoff.md) wins. Positions in this document that the handoff reverses:
> - The lite tier runs without an approval stop. **Reversed:** every plan stops for CD's approval, given by merging the doc PR (handoff F6/F17).
> - Labels such as `factory:implement` and `factory:needs-human`. **Replaced:** the handoff's `factory:*` label set.
> - Keep an API-key fallback lane. **Reversed:** no API lane, usage credits off.
> - Open questions 1, 3 and 4. **Answered:** pilot on `endless-galaxy-studios/quantile`, intake through GitHub issues, incubate in quantile and then promote to a cc-sdlc bundle.

This evaluation continues the "software factory" thread that the review-loop-unification handoff parked. The goal is to go from "Zellij tabs plus hand-started agents" to filing issues that agents pick up. Each agent decides whether to plan or implement directly, asks CD when blocked, and opens a PR.

Hard constraints:
- **Claude Max subscription** for model usage.
- **CD's own server** as the runner.
- **GitHub Actions** preferred, alternatives open.

Facts below were checked against primary sources on 2026-10-07 unless marked *(unverified)*.

## Bottom line

1. **Adopt Warp's factory pattern, not Warp's runtime.** The `cloud-factory-demo` stages map one-to-one onto cc-sdlc: triage, then spec or implement, then review, then a daily improve loop, with labels as state and a read-only agent paired with a separate write job. Every workflow in that repo is tied to `oz-agent-action` plus a `WARP_API_KEY`, so its files are not reusable. Its skills and shape are.
2. **Build it on Claude-native pieces.** The only path that meets all three constraints is `anthropics/claude-code-action@v1`, authenticated with a `claude setup-token` OAuth token, on a self-hosted Actions runner, triggered by issue labels.
3. **cc-sdlc already covers the lower two-thirds of Zach Lloyd's factory diagram.** It has agent configuration (skills, agents, permissions) and the data plane (knowledge stores, disciplines, playbooks). The missing parts are the control plane (intake, routing, triggers, a board) and headless execution.
4. **The real scaling limit is the Max usage window, not the server.** A factory does not add model capacity. It shares the same 5-hour and weekly limits as interactive work. What it scales is CD's attention as dispatcher.

## What the sources say

### Zach Lloyd (Warp): "Software engineering is becoming factory engineering"
- **The loop:** idea, triage, spec (if hard), implement, review (agent, then human), verify (computer use), ship, monitor, then back to the top.
- **Where humans step in:** spec review, code review and product review.
- **Triage:** if the issue is easy and unambiguous, implement it. If it is hard, write a product spec plus a tech spec.
- **What a factory needs:**
  - Automations.
  - Context and skills.
  - Human touchpoints for when things get stuck.
  - Self-improvement loops. Example: observer agents watch how humans correct the review agent and update its skill.
- **Primitives** (from his slide):
  - Control plane: agent configuration, orchestration, administration.
  - Execution: hosting, multi-harness, multi-agent.
  - Data plane: artifacts, memory, knowledge, rules, skills.
- **Build or buy:** most organizations should not build a factory that scales. The domain tuning (are these the right skills for my product?) is still their own engineering work.

### Dex Horthy (HumanLayer): "Harness engineering is not enough / why software factories fail"
- **Warning:** lights-out factories, where nobody reads the code, fail. Models are RL-trained on "the tests pass" and cannot be rewarded for maintainability, because the cost of bad design shows up months later.
- **Measured fallout:** review quality fell and incidents rose after teams adopted agents.
- **His own experience:** codebases degrade within 3 to 6 months.
- **Remedy:** turn the lights back on.
  - Align up front: product review, then architecture, then program design (types, signatures, call graphs), then vertical slices.
  - Small work still goes straight to the agent.
  - About 30 minutes of alignment saves hours of review.
  - "If you're drowning in PRs, you have too many bad PRs."

### Dru Knox (Tessl): "Harness engineering: how to build a software factory"
- **Three metrics, in order:** autonomy (how often humans correct the agent), then automation (how much humans review before trusting), with quality held constant and then raised.
- **Three loops:**
  - Inner: cheap checks before the PR.
  - Outer: expensive checks once the PR is up.
  - Meta: reads agent logs, PR comments and issues, and feeds fixes back into the other two.
- **Build order:**
  1. **Control plane first.** Move all work onto legible surfaces (issue, then headless agent in a sandbox, then PR, then human comments) so the signals are saved.
  2. **Agent enablement.** Give agents CLI/API access, logs and an execution environment. "Worse than you think."
  3. **Improvement loops:** repo sweeps, playbooks, automated repeated tasks.
- **Track:** manual takeovers, human PR comments, and PRs started without a human.

### HumanLayer (product, from humanlayer.com and its docs)
- **What it is:** a multiplayer agent IDE plus cloud.
- **Workflow tiers:** Oneshot, RPI Outline, and full PRD+TDD. "Use the shortest path that controls the main risk." This is the same idea as cc-sdlc's tiers.
- **Agents and billing:** it runs Claude Code, Codex or Copilot with BYOK ("plug in your existing subscriptions or API keys").
- **Remote daemons** run on your own Linux host (systemd), which fits.
- **Automations** (`humanlayer automation run` in GitHub Actions, on cron, `workflow_dispatch` or `issue_comment`) are documented with `ANTHROPIC_API_KEY`.
- **GitHub issue to task is manual:** you click "Create Task" in the desktop app.
- **Price:** Pro is $100/user/month for remote daemons and multi-repo.
- **Fit:** a cockpit for reviewing specs and plans, not an unattended factory.

### 12-factor agents (HumanLayer)
The factors that matter here:
- **#5 Unify execution state and business state.** The issue and the repo are the state.
- **#6 Launch/pause/resume.**
- **#7 Contact humans with tool calls.** A question is a comment plus a label.
- **#8 Own your control flow.** Deterministic workflows, with the LLM at decision points.
- **#10 Small, focused agents.**
- **#11 Trigger from anywhere.**
- **#12 Stateless reducer.**

### `warpdotdev-demos/cloud-factory-demo` (MIT)
- **Stages:** six skills (triage, spec, implementation, verify-behavior, review-pr, improve-review-pr) plus five workflows.
- **Readiness labels:** Ready to implement, Ready to spec, Needs info, Wait to implement.
- **Steering docs:** `vision.md` and `roadmap.md` give triage product direction.
- **Read-only agent, separate write job:** the triage agent has `issues: read` and returns JSON. A separate `apply` job with `issues: write` sets the label and comment.
- **Daily improve loop:** it scores human reactions to review comments as validated, corrected or refined, and opens a PR that updates the review skill.
- **Stated as portable:** "replace the trigger mechanism, runtime, and platform-specific instructions while keeping the skill boundaries and handoff contracts intact."

## The deciding constraint: the Max subscription

**Terms** ([legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance)):
- Subscription OAuth is for "ordinary use of Claude Code and other native Anthropic applications". "Advertised usage limits for Pro and Max plans assume ordinary, individual usage."
- Third parties may not route requests through Pro or Max credentials.
- A user signing into the **unmodified Claude Code binary** with their own subscription is allowed.

**The documented path:** the GitHub Actions docs support `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` on Pro, Max, Team and Enterprise. They warn that the token is tied to one person's subscription.

**Usage:** `claude -p`, the Agent SDK and the Action all draw from subscription limits. The separate Agent SDK credit pool announced for June 2026 is paused ([support article](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)). The same article says: "Teams running shared production automation should use Claude Platform with an API key."

**CD's own numbers** (from the review-loop consult record, last 30 days):
- About $16.3k of usage at API rates.
- Subagents were two-thirds of it.
- Review loops were the largest single share.

**What follows:**
- Any tool billed per token or in vendor credits costs too much at this volume.
- A factory on Max competes with interactive work for the same window. When the limit hits, routines are "rejected until your usage window resets", and Action runs fail.
- A 24/7, high-volume factory on one Max seat is the scenario the "ordinary, individual usage" line is about. Anthropic "may enforce without prior notice".
- Keep an API-key fallback lane ready.

## What Claude Code gives a Max user natively

| Primitive | On Max? | Runs where | Triggers | Factory role |
|---|---|---|---|---|
| `claude-code-action@v1` + OAuth token | Yes | **Any Actions runner, including self-hosted** (runner-agnostic; docs silent on self-hosted specifics) | Any GitHub event. Inputs `label_trigger`, `assignee_trigger`, `trigger_phrase` (`@claude`), `track_progress`. `prompt: "/skill-name"` runs a repo `.claude/skills/` skill | **Main execution lane** |
| Routines (`/schedule`) | Yes | Anthropic cloud. Self-hosted environments are **Team/Enterprise only** | Schedule (at most hourly), API `/fire`, GitHub **PR and release events only (no issues)** | Scheduled meta loop or maintenance sweeps |
| Claude Code in Slack (earlier version) | Yes, in workspaces not connected to Claude Tag | Anthropic cloud session | `@Claude` in a channel; posts progress, then "Create PR" | Phone or Slack quick asks; bypasses the issue state machine |
| Claude Tag (Slack) | **No** (Team/Enterprise) | | | |
| Remote Control | Yes | Your machine | You, from web or mobile | Steer a live session on the server from your phone |
| Channels (Telegram/Discord/iMessage) | Yes | Your machine (open session) | Inbound message | Two-way chat with a long-running local session |
| Self-hosted environments | **No** (Team/Enterprise beta) | Your runners | | Would be ideal; not available on Max |

## The "adopt" options

| Option | Fits Max? | Own server? | Verdict |
|---|---|---|---|
| **Warp Oz** | No. The Claude Code harness takes Anthropic API or Bedrock keys plus Warp credits | Self-hosting is Enterprise-only | Take the pattern, skip the runtime |
| **Cursor automations / cloud agents** | No. Cursor's own agent loop and billing | Self-hosted pools move tool execution only; the loop stays in Cursor's cloud | Closest managed match, wrong billing |
| **GitHub Copilot coding agent** | No. It can pick a Claude agent but bills GitHub AI Credits | ARC scale sets, Ubuntu x64 | Simplest "assign issue, get PR", but not Max |
| **HumanLayer** | Interactive: yes (your login on your daemon). Automation: documented with an API key | Yes (remote daemon) | A cockpit for alignment; overlaps cc-sdlc plan/spec; manual issue import |
| **Tessl** | n/a (governance layer) | n/a | cc-sdlc plus `sdlc-migrate` already acts as the skills registry |
| **OpenHands** (OSS, MIT, mature) | Only by driving the stock `claude` binary *(inference)* | Yes | The only credible OSS board UI if one is wanted |
| Vibe Kanban, Claude Squad, Sculptor, Conductor | | | Shut down, interactive-only, or experimental |

Sources: the market-scan agent, 2026-10-07. Warp, Cursor and Copilot pricing are partly from secondary sources.

## Recommended architecture

```text
 Control plane: GitHub
   Issues + factory labels = state machine (12-factor #5)
   One cross-repo Projects v2 board = factory floor view
   Reusable workflows (workflow_call) in one central repo;
   each project gets a ~15-line caller stub (installed as a cc-sdlc bundle)
        |
        v  issues.opened / issues.labeled / issue_comment / pull_request
 Execution: self-hosted runner on CD's server
   runs-on: [self-hosted, factory]
   anthropics/claude-code-action@v1, claude_code_oauth_token (Max)
   prompt: "/sdlc-triage" | "/sdlc-lite-plan" ... (installed skills)
   Budgets outside the prompt: --max-turns, timeout-minutes,
   concurrency per issue, 1-2 runner slots total
        |
        v
 Data plane: cc-sdlc, already exists
   skills, agents, knowledge stores, disciplines, playbooks,
   docs/current_work artifacts committed on the PR branch
```

### Flow

| Event | Workflow | Agent does | Writes |
|---|---|---|---|
| Issue opened (or `factory` label added) | triage | `/sdlc-triage`, read-only. Returns JSON with tier, label and comment | Apply job sets **one** label: `factory:implement`, `factory:spec`, `factory:needs-info` or `factory:parked` |
| `factory:implement` | implement-lite | `sdlc-lite-plan` then `sdlc-lite-execute` in one run. The plan is committed for after-the-fact review | Draft PR, `Closes #N` |
| `factory:spec` | spec | `sdlc-plan` up to the spec | **Specs PR** (the approval surface, replacing `ExitPlanMode`) |
| Specs PR merged, or `factory:spec-approved` | implement-full | `sdlc-execute` against the approved spec | Draft PR |
| Agent is blocked | (any) | Posts the question as a comment and adds `factory:needs-human` (12-factor #7), then exits cleanly | |
| CD comments on a `needs-human` issue | resume | Re-runs the stage recorded in a hidden marker in the question comment (12-factor #12) | |
| PR opened | review | `sdlc-review-code` | PR review |
| Review cap hit | (execute) | Parks: draft PR, open-findings table, `factory:review-capped` | |
| Weekly schedule | improve | Harvests human PR comments, takeovers and `needs-human` reasons; proposes skill or knowledge updates (`sdlc-audit` improvement mode) | Skill-update PR |

**The factory never merges.** Human PR review stays mandatory (Dex's warning). The spec path gives the up-front alignment he argues for.

### Human in the loop on Max
- **Primary:** issue and PR comments. GitHub mobile push covers the phone.
- **Slack, optional:** subscribe the GitHub Slack app to `+label:"factory:needs-human"` for notifications.
- **Quick tasks from Slack, optional:** Claude Code in Slack (Max, cloud-run).
- **Manual override:** `@claude` in any comment, using the action's interactive mode.

### Multi-project
- One runner pool serves every repo **if the repos live in a GitHub organization** (runner groups). On a personal account, register one runner per repo; several runner services on one box is fine.
- Reusable workflows plus cc-sdlc bundle install and migrate mean a new project needs no new infrastructure. Add the bundle, labels and secret.

### Safety
- **Private repos only.** A self-hosted runner on a public repo lets anyone's PR run code on the server.
- **Isolate the runner:** an unprivileged user, ideally a container or VM, ephemeral runners.
- **Omit `github_token`** so the action authenticates as the Claude GitHub App. Commits made with the default `GITHUB_TOKEN` do not trigger CI.
- **Pilot early.** The docs are silent on the action on self-hosted runners, and rough edges have been reported *(unverified)*.
- **Check the label chain first.** Three things can break triage, then apply label, then `issues.labeled`, then the implement run:
  - GitHub does not start workflows from events caused by the default `GITHUB_TOKEN`.
  - The action rejects bot actors unless `allowed_bots` names them.
  - Warp's demo apply job uses `${{ github.token }}`, so verify the chain fires before copying it.
  - **Fix:** apply state labels with the Claude GitHub App token or a PAT, and list that actor in `allowed_bots`.
- **Triage output capture.** The read-only-agent-plus-apply-job split depends on reading the triage JSON from the action's outputs. Check what `claude-code-action` exposes before committing to it. The fallback is to let the triage job set the label itself with the App token.

### Not picked: a hand-rolled `claude -p` daemon on the server
It is allowed (unmodified binary, your own login). But it would re-implement what Actions already gives you: queueing, retries, logs, permissions and secrets. Keep it as the fallback if Actions gets in the way.

## What cc-sdlc would need (candidate deliverable: an opt-in `factory` bundle)

The Explore pass found the framework has never run headless and has these gaps (line numbers as of 2026-10-07):

1. **No triage skill.** Today the tier is chosen by asking CD (`CLAUDE-SDLC.md:46`), and `sdlc-manage-github` stops at lookup (`sdlc-manage-github/SKILL.md:154-159`).
   - Needed: a read-only `sdlc-triage` that emits structured JSON.
   - Its rubric already exists in the validity, correctness and effort estimation model (`CLAUDE-SDLC.md:48-57`).
   - Add per-project `vision.md` and `roadmap.md` (or their equivalents) so triage has product direction.
2. **Headless contract for interactive gates.** One process doc (`headless-mode.md`), plus a mirrored line in each skill. Gates to cover:
   - The global `AskUserQuestion` rule (`CLAUDE-SDLC.md:174-184`).
   - The spec approval gate (`sdlc-plan:396-398`).
   - `EnterPlanMode`/`ExitPlanMode` (`sdlc-plan:646-667`, `sdlc-lite-plan:375-395`).
   - Phase triage SKIP and REVISE_PLAN (`sdlc-execute:185`, `sdlc-lite-execute:161`).
   - The review-cap escalation (`review-fix-loop.md:231`).
   - In headless mode each one becomes: comment, label, write state, exit 0.
3. **Park at the review cap.** Both outside reviewers recommended it, and the review-loop handoff deferred it to "the factory work". It means a draft PR, the open-findings table, a `review-capped` label, and CP-11.
4. **Deliverable ID collisions.** The Next-ID counter in `docs/_index.md` is one shared file, so parallel branches will collide. Use the issue number as the ID, or allocate at merge.
5. **Labels as state.** The github-provenance labels are categories, and the state lives in the Projects v2 Status field (`github-checkpoints.md:88-93, :335`). Actions can trigger on `issues.labeled` but not on Status changes. Factory labels have to carry the trigger state, with Status as a mirror. CP-S1 (`stakeholder-blocked`) and CP-S2 (resume) are the existing hooks for `needs-human`.
6. **Budgets outside prompts:** `--max-turns`, `timeout-minutes`, and per-run dispatch limits in the checkpoints config. The consult record asks for these.
7. **Meta-loop evidence.** Improvement-mode audits read session JSONL under `~/.claude/projects`. Headless sessions would leave theirs on the server *(where the action writes them is unverified)*. Either run the improve loop on the server or harvest PR comments instead, as Warp's `improve-review-pr` does.

8. **Tool permissions in automation mode.** With a `prompt` input, the action grants no shell or GitHub API access unless `--allowedTools` or a `settings` permissions rule allows it. A skill invocation gets only what its `allowed-tools` frontmatter grants.
   - **None of the 27 cc-sdlc skills declare `allowed-tools`.**
   - The bundle needs a factory `settings` file passed from the reusable workflow. It must cover file edits, `gh`, git, test commands and the Agent tool for subagent dispatch.
   - The alternative is per-skill `allowed-tools` frontmatter.

**Versioning:** a new opt-in bundle is additive, so it is a **minor** bump under the repo's versioning rules.

## Suggested first slice

Start narrow. Dex's warning and the cost data (review loops are the largest share) both point that way.

1. One private repo, one runner, the action with the OAuth token. **Triage only**, read-only, posting a label and a comment. Run it on about 20 real issues and grade its calls.
2. Add the `factory:implement` path (lite tier) producing a draft PR. Add the `needs-human` resume loop.
3. Add the spec path (specs PR as the approval surface).
4. Add the weekly improve loop.

Track:
- Manual takeovers.
- Human comments per factory PR.
- Share of PRs started without CD.
- Usage-window hits.

Zellij plus interactive direct dispatch stays in use; the factory handles the queue.

## Open questions for CD
- Do the target repos live in a GitHub organization (one shared runner pool) or on a personal account (one runner per repo)?
- Is a separate API-key lane acceptable for overflow, or is Max a hard ceiling?
- Is GitHub Issues the intake, or is Linear in play? Linear changes the trigger layer, not the rest.
- Build the `factory` bundle inside cc-sdlc, or as a separate factory repo that cc-sdlc installs from?
