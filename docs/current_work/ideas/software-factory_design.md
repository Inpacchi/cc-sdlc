---
type: design-draft
slug: software-factory
created: 2026-10-08
status: draft
related_files:
  - docs/current_work/ideas/software-factory_handoff.md
  - docs/current_work/ideas/software-factory_evaluation.md
  - process/headless-mode.md
---

# Software Factory: Design Rules (draft)

The binding rules for the factory, kept here while it incubates in quantile (F13). They are framework rules, not project architecture: every repo that adopts the factory inherits them. At promotion this draft becomes the `factory` bundle's process doc, which installs into each project's `[sdlc-root]/process/`.

Three decisions so far: **D1, the stage contract**, **D2, the credential boundary**, and **D3, the planning tier**. Each has the rules and what they forbid, what it leaves open, its unvalidated assumptions and the evidence for it. Where a rule can be a check instead of prose, prefer the check: the smoke probes already are, and a lint of agent-job permissions should be.

Both decided 2026-10-08 (CD), first drafted as quantile ADR-21/22 and moved here because they are generic.

---

## D1: Stage Contract (labels hold state, dispatch advances, writer jobs write)

### Context

The factory runs issue-driven agent stages (triage, then implement, revise, spec and plan) on a self-hosted runner. Three platform facts shape how stages connect:
- A label or comment written with a workflow's default `GITHUB_TOKEN` starts no new workflow run. `workflow_dispatch` and `repository_dispatch` are the exceptions.
- `claude-code-action` acts as the Claude GitHub App when `github_token` is unset. That token can comment, label and push.
- The resume workflow restarts the stage named in a hidden comment marker, so whoever can author that marker can steer the factory.

Letting stages post with different identities (App token, PAT) would silently break resume, and handing an agent a write token makes "the agent cannot write" a matter of prompt wording rather than permissions.

### Options considered

1. **Label events chain stages,** applied by a bot with an App token or PAT. Needs a write token wherever labels are applied, and markers would come from several identities.
2. **Agents write directly** as the App. Simplest to wire, but write access rests on instructions and prompt injection gets a write channel.
3. **Labels hold state, dispatch advances, writer jobs write (chosen).** The only option where every must-have holds by construction.

### Rules

1. **Labels hold state.** An issue carries at most one `factory:*` state label, set by CD or by writer jobs.
2. **Dispatch advances.** A stage starts by `workflow_dispatch` of `factory-<stage>.yml` with an `issue_number` input, sent from a writer job (`GITHUB_TOKEN`, `actions: write`). A stage workflow may also accept its label event, so CD can start it by hand.
3. **Agents hold no write credential.** An agent job's `github_token` is the job's read-only `GITHUB_TOKEN`, never unset. The agent returns structured output (from phase 2, also a patch or bundle artifact). A writer job on a GitHub-hosted runner validates it and acts on it.
4. **One identity for comments and markers.** Comments, labels and markers are posted only as the factory App (`z-software-factory[bot]`), with an issues-only App token each writer job mints in `factory-writer`. Pushes and PR creation use a separate contents and pull-requests App token, in a writer job that posts no markers. Dispatch alone uses `GITHUB_TOKEN`. Exceptions that show as `github-actions[bot]`: failure reports when the App token can't be made (they fall back so a broken key still gets reported) and `factory-advance`'s "plan approved" comment (a `pull_request` event can't use the `main`-only environment). Changed 2026-10-09 from "only with `GITHUB_TOKEN`": CD wanted one visible factory identity, and markers became harder to forge, since only default-branch jobs in `factory-writer` can mint the App's token, where any workflow with `issues: write` can post as `github-actions[bot]`. App-set labels start workflows, so rule 2's label events count only from a person (`sender.type != 'Bot'`, in the job condition and the concurrency group).
5. **Marker grammar.** Markers form a block of consecutive lines at the top of a factory comment:
   - **stage marker,** first when present: `<!-- factory-stage: <stage> [k=v ...] -->`, meaning "waiting on CD; a reply restarts `<stage>`";
   - **decision record:** `<!-- factory-triage: {...} -->`;
   - **deliverable reservation:** `<!-- factory-id: Dnn -->`, posted by the plan stage's claim job before planning starts (F11 without a push to `main`): the next ID is the highest of the catalog's Next ID, its rows and every earlier reservation, plus one, claimed one at a time across the repository;
   - **reserved:** `<!-- factory-revise: N -->`.

   Writer jobs escape `<!--` in agent text and validate every value they write into a marker. Resume reads the leading marker only from comments by the App's bot user, matched by ID (REST has returned its login in different case), and maps stages to workflows through an explicit allowlist. The claim job's reservation scan also counts `github-actions[bot]` reservations from before the switch.
6. **Resumable questions go on the issue.** A stage that pauses about a PR puts its question on the issue with `pr=<n>` in the marker. Non-resumable notices on a PR (such as F16's escalation) are allowed.

### Forbids

1. An agent job with `issues: write`, `pull-requests: write` or `contents: write`, or with `github_token` unset.
2. Chaining stages by label events applied with a bot token or PAT (a stage ignores labels a bot sets).
3. Posting a comment, label or marker with a PAT, with `GITHUB_TOKEN` (except the fallbacks in rule 4), or with the App's push token.
4. Reading a marker from anything but the leading block of a comment by the App's bot user, or dispatching a stage not on resume's allowlist.
5. Posting a stage marker or resumable question on a PR.
6. Using the App key outside `create-github-app-token`'s private-key input in a hosted `factory-writer` job with no agent (quantile's `workflow_policy.py` checks this).

### Costs

- Every stage costs a second job on GitHub-hosted minutes.
- Adding a stage takes three touches: its workflow, a `case` line in resume (the stage's workflow and in-flight label), and the runner group's selected-workflows list.
- Phase 2 pushes need artifact plumbing between agent and writer jobs.
- A reply posted while a stage runs restarts nothing (the label is already swapped); CD replies again after the stage comments.

### Leaves open

- Revise-stage counting (F15/F16) beyond reserving the marker.
- How full-tier spec discovery keeps context across question rounds (F18).
- Restricting which person may trigger a stage by label (bots already can't).

### Assumptions (unvalidated)

- ~~The Claude GitHub App is installed without the `workflows` permission.~~ Invalid: an app's owner sets its permissions, and Anthropic's `claude` app has `workflows: write` and a private key only Anthropic holds. Replaced (2026-10-08) by the factory's own app, **Z Software Factory** (`z-software-factory`, App ID 5244270): Contents and Pull requests read/write, Metadata read, nothing else, no webhook. Its ID and key live in quantile's `factory-writer` environment, deployable from `main` only.
- Only CD applies `factory:triage`. The label trigger doesn't check who applied it; acceptable while CD is the only maintainer.
- ~~No non-factory workflow posts issue comments as `github-actions[bot]`.~~ No longer needed (2026-10-09): markers are trusted only from the App. The App now also has Issues read/write.

### Revisit when

- A stage genuinely needs agent-side GitHub writes.
- GitHub changes which events `GITHUB_TOKEN` may trigger (resume would fail loudly: it restores `factory:needs-input` and comments).
- The factory runs across more than one repository.
- Phase 2's patch-artifact handoff proves too brittle.

### Evidence

Quantile issues #8–#10 (2026-10-07): all three triage outcomes, plus a live resume by dispatch with no PAT. `66f0117` fixed `gh workflow run` needing `--ref` without `contents` access.

---

## D2: Credential Boundary for Agent Jobs

### Context

Agent jobs run in rootless-Docker containers firewalled from the host and LAN; in the pilot the host is also quantile's production box.
- `claude-code-action` passes its whole environment to Claude Code, including `CLAUDE_CODE_OAUTH_TOKEN`, a long-lived credential for CD's Max plan.
- Agents read untrusted text (issues, search results, docs), so a prompt injection only needs a tool that can read the environment and a channel to send it.
- Triage needs no shell; phase 2's implement stage needs Bash to install dependencies and run tests.

### Options considered

1. **Never give agents Bash.** Safe, but rules out an implement stage that runs tests.
2. **Bash with default isolation, relying on auto mode's classifier.** The classifier declined token-reading commands in the spike, but it's a model judgment, not a boundary.
3. **Tool policy, credential scrub, bubblewrap PID namespace and network sandbox (chosen).**
4. **No agent-side credentials** (API proxy, VM per job). Out of scope for a single-runner Max-plan pilot.

### Rules

1. **Every agent step runs under a versioned tool-policy file,** loaded by the stage workflow and probed by `factory-smoke`. Triage (and smoke's agent steps) use `triage-tools.args`: Read, Grep, Glob, WebSearch and Context7; no Bash, write tools or WebFetch; Read denies on `/proc`, `/dev`, `.git` and the runner's mounts (which also bind Grep and Glob).
2. **A stage that grants Bash runs it sandboxed:**
   - `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, with `bubblewrap` and `socat` in the job image;
   - a sandbox settings file, copied out of the workspace before the agent starts and loaded twice: with `--settings` (which makes the sandbox admin-required, so the repository's own settings can't loosen it) and as the action's `settings` input (user scope, for the user-scope-only keys). It sets `sandbox.enabled`, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, the weaker-isolation switches off, `network.strictAllowlist: true` with `allowedDomains` limited to the registries that stage needs, `filesystem.denyRead` on the runner's mounts, `credentials.envVars` `deny` for every credential the job holds (the OAuth token, `GH_TOKEN`, `GITHUB_TOKEN`, the action's `OVERRIDE_GITHUB_TOKEN` and `DEFAULT_WORKFLOW_TOKEN`, `CONTEXT7_API_KEY`, the Actions runtime tokens), and `disableAllHooks: true`;
   - `--strict-mcp-config`, because the action forces `enableAllProjectMcpServers` and MCP servers run outside the sandbox;
   - an explicit `--setting-sources` that never includes `local`: `user` where the stage needs nothing from the repository, `user,project` where it needs the repository's skills and `CLAUDE.md`. In `-p` mode, project and local settings apply their `env` at startup (`LD_PRELOAD` and `NODE_OPTIONS` aren't filtered), so `project` is loaded only from a ref whose `.claude/`, `CLAUDE.md` and `.mcp.json` CD has reviewed: `main` (CODEOWNERS), or a factory branch whose patch the writer job refused to let touch them;
   - container `options`: the narrow seccomp profile (Docker's default plus `unshare`, `clone`, `setns`, `mount`, `umount2`, `pivot_root`, `mount_setattr`, `open_tree`, `move_mount`) and `--security-opt systempaths=unconfined`;
   - **file tools are outside the sandbox:** Read, Edit and Write run in the Claude Code process, which holds the token. The stage's tool policy denies Read on `/proc`, `/dev`, `/sys` and the runner's mounts, and Edit on system directories, runner state, `HOME`, temp and mount points, `.git`, `.github`, and `.claude/`, `CLAUDE.md` and `.mcp.json` at any depth (deny rules also match a symlink's target). Skill shell execution is off;
   - **a service the job starts outside the sandbox that sandboxed Bash can reach is part of the boundary** (quantile `1d4e3ee`). Test databases run outside the sandbox with open network, on the job container's loopback, reached through the sandbox's HTTP proxy with `localhost` as the only local entry in `allowedDomains` (quantile `bafc82d`). Never `allowAllUnixSockets`: it drops the sandbox's seccomp helper, whose nested PID namespace and clean environment hide bubblewrap's own environment, and smoke run 37874841855 showed sandboxed Bash then reads the job's GitHub token from `/proc/1/environ` (the env scrub leaves GitHub tokens in place) and reaches Claude Code's own Unix sockets. Each runs least-privileged (no Postgres superuser, so no `COPY ... TO PROGRAM`; Redis without `MIGRATE`, `REPLICAOF`, `MODULE`, `CONFIG` and the like), starts with an empty environment, and the start script checks all of it on every run;
   - `network.allowedDomains` empty for a stage that installs nothing (implement): a package registry that accepts publishes is a way out.
3. **Writer jobs refuse to post** token-shaped strings, images and embeds.
4. **After an agent step that can write the workspace, the job trusts nothing the agent could have touched.** Later steps in that job run only code copied out beforehand to places the sandbox can't write, call `python3 -I` by absolute path, and run git with hooks and fsmonitor disabled, only after checking that `.git` is a real directory that wasn't redirected (`commondir`, `alternates`), its hooks are unchanged and its config holds only allowlisted keys (read with `git config --file`, which follows no include), and the index holds no submodule; and never into a nested repository (`--ignore-submodules=all`): `git status` runs a staged submodule's own config, filters included, which a planted repository outside `.git/` can define (review round 2, reproduced). The sandbox leaves empty read-only placeholder files behind at protected paths it mounts over (`commondir`, `alternates`, `config.worktree`); the guard removes empty ones and refuses any with content. The job removes `origin` before the agent step, because the action writes the job token into its URL, and passes the factory's bot identity so the action's git setup commits as the factory. The job removes `.git` at the end, because `actions/checkout`'s post step runs git in the workspace. The commits themselves are judged by a writer job on a clean GitHub-hosted runner.
5. **The boundary is tested before it is relied on.** Every smoke run probes the tool policy and does an exact-value credential scan. Before any stage gets Bash, smoke carries that stage's sandbox probe (`factory-smoke` job `bash-sandbox`):
   - **An unsandboxed control** must find the tokens in its environment and in `/proc`, and a planted canary in plain and base64 files, which proves each detection path.
   - **From inside the sandbox,** the probe, frozen read-only before the agent runs, must find no credential by value (environment, every process's environment, token-like strings in readable files, raw or base64) and none by name. It must also find:
     - a PID namespace other than the control's;
     - unlistable runner mounts;
     - unwritable protected paths;
     - the allowed registries reachable through the proxy, every other host refused, and no route around the proxy.
   - **The assertion judges** only the output of the one expected command.

   Re-run smoke on every action, image or tool-policy change.
6. **Workflow edits are trusted only through review.** The boundary against a malicious workflow change is:
   - CODEOWNERS on `.github/`, `.claude/`, `CLAUDE.md`, `.mcp.json` and the test and build config, enforced by the `main` ruleset;
   - the factory's own GitHub App (Z Software Factory) has no `workflows` permission, so no factory token can push a workflow change. Its key is in the `factory-writer` environment, which only `main` can use, so a factory branch can't mint the token;
   - the runtime sandbox probe (rule 5).

   CI's `workflow-policy` check catches accidental drift from these rules on every PR. It is not a security control: a workflow is a program (expressions, `$GITHUB_ENV` writes, other actions), so a static check can't be complete against someone editing workflows on purpose. Its known gaps are under Leaves open.

### Forbids

1. Giving an agent WebFetch or any unscoped network path. (Context7 covers library and vendor docs; WebFetch was the one channel that let injected text choose the destination.)
2. Agent Bash without the sandbox, or with `failIfUnavailable: false` or `allowUnsandboxedCommands: true`.
3. Granting a stage Bash before smoke carries that stage's sandbox probe.
4. Granting Bash without `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`.
5. `--security-opt seccomp=unconfined`, `apparmor=unconfined`, `--privileged` or `--cap-add` on factory containers.
6. Giving the OAuth token to a non-agent job; giving any write-capable token to an agent job, or putting one in a file the agent can read.
7. Running an agent step without a tool-policy file, or changing a tool policy without re-running smoke.

### Costs

- `systempaths=unconfined` is required (bubblewrap mounts its own `/proc`).
- Sandboxed Bash gets no credential at all, so tools inside it can't authenticate (no `gh`, no private registries). A stage that needs one would use a `mask` entry, which needs TLS termination; not decided.
- Denying `/github` hides the job's `HOME` from Bash; Bash stages point pip and npm caches at the temp directory.
- WebSearch and Context7 queries still leave the job, to fixed services.
- The seccomp profile tracks Docker's default; re-check on Docker or bubblewrap upgrades.

### Leaves open

- Whether `CONTEXT7_API_KEY` reaches sandboxed Bash: it is denied by name, but quantile has no key set, so the probe hasn't exercised it.
- Hooks and settings in a non-`main` checkout (the revise stage checks out PR branches): `disableAllHooks` and admin-required sandboxing cover hooks and sandbox loosening; project skills and `CLAUDE.md` on a PR branch are still agent instructions from that branch.
- Ephemeral (JIT) runners, which would remove workspace carry-over between jobs.
- Each later stage's tool policy and registry allowlist (set per stage when built).
- **Gaps in the static workflow check** (rule 6; review round 4 of quantile `d4722b0`). Each needs a workflow edit CD reviews under CODEOWNERS:
  - `--json-schema` and `--mcp-config` values aren't shape-checked, and an `env.*` value written at runtime can carry extra flags.
  - Lines a step writes to `$GITHUB_ENV` or `$GITHUB_PATH` aren't checked (`ANTHROPIC_BASE_URL`, `NODE_OPTIONS`, `PATH`). `FACTORY_TOOL_ARGS` can also be set by a heredoc, extended after the `tr`, or read from a rewritten `.args` file.
  - Env keys are blocklisted, not allowlisted (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=0`, `HTTPS_PROXY`, `NODE_TLS_REJECT_UNAUTHORIZED`, `LD_PRELOAD` pass), and `secrets['X']` or `toJSON(secrets)` aren't caught.
  - Actions in agent jobs aren't allowlisted (`actions/github-script`, third-party wrappers).
  - A `git checkout` in a `run:` step after the pinned checkout isn't caught.
  - The direct-Claude pattern misses `import claude_agent_sdk` and `$(which claude)`.
  - **The structural answer**, a design item for the implement stage: every agent run goes through one reusable workflow (`factory-agent.yml`), with a frozen step right before the agent that checks the actual environment, arguments and tool policy at runtime. That leaves one file to review and covers what static analysis can't see.

### Assumptions

- None unvalidated from the spike. Both earlier assumptions are now tested on every smoke run: the control finds `/proc/kcore` unreadable and `/proc/sysrq-trigger` and `/proc/sys` unwritable under `systempaths=unconfined`, and sandboxed Bash can't list the runner's mounts.

### Revisit when

- Claude Code or the action changes credential handling or sandbox keys.
- A stage needs a non-HTTP network path (the sandbox proxy covers HTTP(S) only).
- The factory moves off a production host.

### Evidence

Spike v2 on the real runner with the real token (quantile `ba9ef80`..`e9520ac`, 2026-10-08): the unsandboxed control saw the OAuth token in the environment and process environments; sandboxed Bash saw neither and ran in its own PID namespace. The network sandbox allowed `pypi.org` and `registry.npmjs.org` and refused `example.com` and `api.github.com`. Under Docker's default seccomp, bubblewrap can't build a namespace and every Bash call fails closed. Details in the handoff's "Phase 2 spike" sections.

Permanent probe (quantile `8ea210f`..`e2b1e7f`, `factory-smoke` run 37841112243, 2026-10-08), passed on its second run:
- **The control** found both tokens in its environment and `/proc`, and the canary plain and base64.
- **Sandboxed Bash** found:
  - no credential by value or name;
  - its own PID namespace;
  - all four runner mounts unlistable;
  - `.git/hooks` and `.claude` settings unwritable;
  - pypi and npm reachable (200);
  - `example.com` and `api.github.com` refused by the proxy, and no-proxy, direct TCP and DNS all failing.

The first run failed only because Claude Code appends a `<sandbox_violations>` note after a command's output.

A security review before the run found that user-scope sandbox settings don't lock out repository settings, that the action passes the GitHub token under two more names (`OVERRIDE_GITHUB_TOKEN`, `DEFAULT_WORKFLOW_TOKEN`), and that it forces project MCP servers on. Rules 2 and 4 carry the fixes.

Four review rounds of the static workflow check (quantile `b233d33`..`d4722b0`, then the drift fixes) each closed what they found and the next round found more. Round 4 had no criticals but six majors, all bypasses needing a reviewed workflow edit. CD's decision (2026-10-08): stop hardening it as a security control, fix the findings that catch plausible mistakes, and record the rest (rule 6).

---

## D3: Planning Tier (spec and plan stages see real data and services)

### Context

Spec and plan stages make judgement calls that depend on how the system behaves in production: what the data looks like, which errors occur and where, what an external service returns. D2 keeps every agent job away from production and from credentials, which is right for stages that write and run code (implement, execute, revise), but leaves planning guessing or asking CD for facts the factory could look up. CD (2026-10-09): planning should be able to use whatever data and services make an efficient plan, the whole database apart from personal and secret data, relaxing the firewall where needed. This replaces F19's snapshot-only rule for planning.

### Options considered

1. **Ask CD for every data fact.** Keeps D2 unchanged; slow, and plans are only as good as the questions.
2. **A periodic scrubbed snapshot** (F19 as first written). No production path, but stale data, a table list to maintain, and no route to services such as Sentry.
3. **A separate planning tier with live read-only access (chosen).** Planning jobs run on their own runners, as their own Linux user, with a firewall exception for the production database only, a read-only database login that excludes personal and secret data, and services wired from a list with their credentials masked.

### Rules

1. **Two runner tiers.** Implement, execute and revise run on the strict tier (D2, unchanged: no production path). Spec and plan run only on the planning tier: runners under a separate Linux user (`factory-planner`), selected by their own runner label and group. A workflow can't move a code-writing stage onto planning runners without a CODEOWNERS-reviewed edit, and the workflow policy check refuses it.
2. **One firewall exception.** The planning user may reach the production database port on the host and nothing else on the host or LAN; the strict user's firewall is unchanged.
3. **The database login is read-only and excludes personal and secret data.** A dedicated role with `SELECT` only, granted per table and per column: everything except fields holding personal data (names, emails, phone numbers, addresses), credentials (password hashes, API keys, tokens, session data) and payment data. The exclusion list is generated from the models and reviewed by CD; a migration that adds a table or column re-runs the check, and anything new and sensitive-looking stays excluded until CD approves it. The role also has a statement timeout and a connection limit. The agent reaches it through a connection proxy outside the sandbox that holds the password; the agent never sees it.
4. **Services come from a reviewed list.** `.github/factory/services.yml` (CODEOWNERS) names each service: its domains, the GitHub secret with its credential, and how the credential attaches. The planning job turns the list into sandbox settings (`credentials.envVars` with `mode: mask`, `injectHosts` set to the service's domains, `network.tlsTerminate`) or into an MCP server entry. Sandboxed commands see a placeholder; the proxy substitutes the real value only on requests to that service. Adding a service is one entry plus one secret, with no workflow edit.
5. **Open internet for planning.** Planning's sandbox allows general web access for research. What leaks is bounded by what the tier can read: credentials are masked and go only to their own hosts, and the database login can't see personal or secret data.
6. **Planning never copies raw data into its documents.** Specs and plans state facts and aggregates (counts, ranges, distributions, examples with identifiers removed), not row dumps. The skill says so; the writer job's checks apply as for every stage.
7. **Planning still writes only documents.** Its output is a spec or plan PR; it never pushes code to run. Rules D1 and D2 otherwise hold unchanged (read-only GitHub token, writer jobs post, frozen code after the agent).

### Forbids

1. A code-writing stage (implement, execute, revise) on planning runners, or any planning runner, secret or exception reachable from the strict tier.
2. A database login with write rights, or one that can read an excluded table or column.
3. A service credential in the agent's environment unmasked, or masked without `injectHosts`.
4. Raw rows of production data in a spec, plan, PR or comment.

### Costs

- A second runner user, its own rootless Docker, firewall and runners on pop-os.
- The exclusion list must be maintained as models change (mechanical, but it needs CD's review for new sensitive fields).
- Planning can exfiltrate what it can read through the open web; the bound is the data's sensitivity, not the network.

### Leaves open

- Services without an HTTP API or an MCP server.
- Realtime protocols (masking is documented for HTTP(S); a WebSocket such as Ably realtime is unverified, so planning uses REST).
- Other repos' databases when the factory runs on more projects (one role per project database).

### Evidence

- Session resume across containers works through the action (quantile `39828cc`, smoke run 37895543752): a second job in a fresh container resumed the first job's session file with `--resume` and recalled its code word. The spec stage keeps its memory this way, with a discovery-notes comment as the fallback.
- Credential masking is documented for sandboxed commands (Claude Code sandboxing docs, § Mask credentials): honored from user, managed and `--settings` scopes.

---

## Promotion Notes

- **Project-specific values move to a per-repo policy file** (handoff deferred item 6): host, registry allowlists, vendor docs Context7 covers, plan triggers.
- **Checks over prose:** done in quantile as `.github/factory/workflow_policy.py`, a required part of CI's `ci-ok`. It is a drift check (D2 rule 6), working from allowlists:
  - **Off GitHub-hosted runners:** a job needs a container whose only options are the factory seccomp profile and `systempaths=unconfined`, with no volumes or services.
  - **Agent steps** need the tool-policy expression, `--strict-mcp-config`, explicit setting sources without `local`, no `#` in `claude_args`, and the job's own token. `claude_args` must be printable ASCII (the action splits words on a non-breaking space; Python's `shlex` doesn't). `--model` must be a literal model ID or a `choice` input of model IDs.
  - **Agent jobs** need an explicit read-only permissions block and exactly one checkout, of the repository itself, without persisted credentials.
  - **A tool policy that grants Bash,** or sets no `--tools`, needs the D2 rule 2 setup: the same frozen file as `--settings` and the `settings` input, the scrub, and the factory container options.
  - **No `run:` step** may start Claude Code directly.

  Promote it with the bundle.
