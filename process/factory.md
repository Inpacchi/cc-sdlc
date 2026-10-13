# Software Factory

The `factory` bundle's rules: issue-driven agent stages that run unattended on self-hosted runners,
from triage to a draft PR, with CD approving every plan, every merge and every production step. These
are framework rules (F22): every project that installs the bundle inherits them, and project
decisions never override them. A project keeps only its settings and operating notes
(`.github/factory/factory.json`, `.github/factory/README.md`).

**What the bundle installs.**

| Where | What | Owner |
|---|---|---|
| `.github/factory/` | The scripts, guards, schemas, tool policies, sandbox settings, workflow templates, the renderer (`render.py`), the workflow policy check, the stack profiles, the setup tools (`bootstrap.py`, `create_app.py`, `host/setup.sh`), the echo service's source (`echo/`) and their tests | z-sdlc: refreshed by every migration |
| `.github/factory/factory.json`, `planning.json`, `services.json`, `triage-policy.md`, `README.md`, `host/host.conf`, and the tests of the project's CODEOWNERS | The project's settings, its runner host's settings, triage policy and notes | The project: seeded once, never overwritten |
| `.github/workflows/factory-*.yml` | The workflows, rendered from the templates with `factory.json` | Generated: re-rendered on every migration; CI refuses a hand edit |
| `.claude/skills/sdlc-triage`, `sdlc-implement`, `sdlc-revise` | The stages' skills. Headless only: the workflows run them, so they have no commands | z-sdlc |

Not installed: the production tier, its broker, operations catalog, runner and host setup (D4
rule 16). It is per project and per host (`[sdlc-root]/process/production-gates.md` covers gates in
plans).

**Names.** Runner labels, runner groups and environments are defaults in `factory.json`, shared by
every project in an organization; a project that changes them changes them there, and the workflows,
`workflow_policy.py`, `bootstrap.py` and the host setup follow. The App, the job image and the echo
service are the organization's own: the seed holds placeholders for them, which Enablement fills
(steps 3 to 5).

**Limits of this version.** The project's SDLC root must be `ops/sdlc` (the scripts and the gate
digest name it). The runners need Linux hosts (systemd, nftables, rootless Docker). The one stack
profile, `python-node`, is Django and Vite's: its `verify probe` runs `manage.py migrate --plan`, and
its `node` checks are eslint, `tsc -b` and the Vite build; another stack needs a profile of its own
(§ Stack Profiles). The plan and spec stages run with or without a database (`planning.json`, D3).

---

## D1: Stage Contract (labels hold state, dispatch advances, writer jobs write)

### Why

Agent stages connect through GitHub, and three platform facts shape how:
- A label or comment written with a workflow's default `GITHUB_TOKEN` starts no new workflow run. `workflow_dispatch` and `repository_dispatch` are the exceptions.
- `claude-code-action` acts as the Claude GitHub App when `github_token` is unset, and that token can comment, label and push.
- The resume workflow restarts the stage a hidden comment marker names, so whoever can write that marker can steer the factory.

Posting under several identities would silently break resume, and an agent holding a write token makes "the agent can't write" a matter of prompt wording instead of permissions.

**Options considered:**
1. **Label events chain the stages,** applied by a bot with an App token or a PAT. A write token is needed wherever labels are applied, and markers come from several identities.
2. **Agents write directly** as the App. Simplest to wire, but write access rests on instructions, and a prompt injection gets a write channel.
3. **Labels hold state, dispatch advances, writer jobs write (chosen).** The only option where every requirement holds by construction.

### Rules

1. **Labels hold state.** An issue carries at most one `factory:*` state label, set by CD or by writer jobs.
2. **Dispatch advances.** A stage starts by `workflow_dispatch` of `factory-<stage>.yml` with an `issue_number` input, sent from a writer job (`GITHUB_TOKEN`, `actions: write`). A stage workflow may also accept its label event, so CD can start it by hand.
3. **Agents hold no write credential.** An agent job's `github_token` is the job's read-only `GITHUB_TOKEN`, never unset. The agent returns structured output (from phase 2, also a patch or bundle artifact). A writer job on a GitHub-hosted runner validates it and acts on it.
4. **One identity for comments and markers.** Comments, labels and markers are posted only as the factory App (its bot user is `factory.json`'s `app.login`), with an issues-only App token each writer job mints in the writer environment. Pushes and PR creation use a separate contents and pull-requests App token, in a writer job that posts no markers. Dispatch alone uses `GITHUB_TOKEN`. Exceptions that show as `github-actions[bot]`: failure reports when the App token can't be made (they fall back so a broken key still gets reported) and `factory-advance`'s "plan approved" comment (a `pull_request` event can't use the `main`-only environment). One visible identity also makes markers harder to forge: only default-branch jobs in `factory-writer` can mint the App's token, where any workflow with `issues: write` can post as `github-actions[bot]`. App-set labels start workflows, so rule 2's label events count only from a person (`sender.type != 'Bot'`, in the job condition and the concurrency group).
5. **Marker grammar.** Markers form a block of consecutive lines at the top of a factory comment (D4's gate markers on execution PRs are display only, never trusted for anything):
   - **stage marker,** first when present: `<!-- factory-stage: <stage> [k=v ...] -->`, meaning "waiting on CD; a reply restarts `<stage>`";
   - **decision record:** `<!-- factory-triage: {...} -->`;
   - **deliverable reservation:** `<!-- factory-id: Dnn -->`, posted by the plan stage's claim job before planning starts (F11 without a push to `main`): the next ID is the highest of the catalog's Next ID, its rows and every earlier reservation, plus one, claimed one at a time across the repository;
   - **revision count:** `<!-- factory-revise: N -->`, one per revise run (F16: 3 per code PR, 5 per spec or plan PR, then `factory:escalated`).

   Writer jobs escape `<!--` in agent text and validate every value they write into a marker. Resume reads the leading marker only from comments by the App's bot user, matched by ID (REST has returned its login in different case), and maps stages to workflows through an explicit allowlist. The claim job's reservation scan also counts `github-actions[bot]` reservations from before the switch.
6. **Resumable questions go on the issue.** A stage that pauses about a PR puts its question on the issue with `pr=<n>` in the marker. Non-resumable notices on a PR (such as F16's escalation) are allowed.

### Forbids

1. An agent job with `issues: write`, `pull-requests: write` or `contents: write`, or with `github_token` unset.
2. Chaining stages by label events applied with a bot token or PAT (a stage ignores labels a bot sets).
3. Posting a comment, label or marker with a PAT, with `GITHUB_TOKEN` (except the fallbacks in rule 4), or with the App's push token.
4. Reading a marker from anything but the leading block of a comment by the App's bot user, or dispatching a stage not on resume's allowlist.
5. Posting a stage marker or resumable question on a PR.
6. Using the App key outside `create-github-app-token`'s private-key input in a hosted `factory-writer` job with no agent (`workflow_policy.py` checks this).

### Costs

- Every stage costs a second job on GitHub-hosted minutes.
- Adding a stage takes three touches: its workflow, a `case` line in resume (the stage's workflow and in-flight label), and the runner group's selected-workflows list.
- Phase 2 pushes need artifact plumbing between agent and writer jobs.
- A reply posted while a stage runs restarts nothing (the label is already swapped); CD replies again after the stage comments.

### Revisit when

- A stage genuinely needs agent-side GitHub writes.
- GitHub changes which events `GITHUB_TOKEN` may trigger (resume would fail loudly: it restores `factory:needs-input` and comments).
- The factory runs across more than one repository.
- Phase 2's patch-artifact handoff proves too brittle.

## D2: Credential Boundary for Agent Jobs

### Why

Agent jobs run on self-hosted runners, and a runner host may also run production. `claude-code-action` passes its whole environment to Claude Code, including `CLAUDE_CODE_OAUTH_TOKEN`, a long-lived credential for the owner's Claude plan. Agents read untrusted text (issues, search results, documentation), so a prompt injection needs only a tool that reads the environment and a way to send it out. Triage needs no shell; implement needs Bash to install dependencies and run tests.

**Options considered:**
1. **Never give agents Bash.** Safe, but rules out a stage that runs tests.
2. **Bash with default isolation, relying on auto mode's classifier.** It declined token-reading commands when tested, but a model's judgment is not a boundary.
3. **A tool policy, a credential scrub, a bubblewrap PID namespace and a network sandbox (chosen).**
4. **No agent-side credentials** (an API proxy, a VM per job). More infrastructure than a self-hosted factory needs to start; § Revisit when says when it would be worth it.

### Rules

1. **Every agent step runs under a versioned tool-policy file,** loaded by the stage workflow and probed by `factory-smoke`. Triage (and smoke's agent steps) use `triage-tools.args`: Read, Grep, Glob, WebSearch and Context7; no Bash, write tools or WebFetch; Read denies on `/proc`, `/dev`, `.git` and the runner's mounts (which also bind Grep and Glob).
2. **A stage that grants Bash runs it sandboxed:**
   - `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, with `bubblewrap` and `socat` in the job image;
   - a sandbox settings file, copied out of the workspace before the agent starts and loaded twice: with `--settings` (which makes the sandbox admin-required, so the repository's own settings can't loosen it) and as the action's `settings` input (user scope, for the user-scope-only keys). It sets `sandbox.enabled`, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, the weaker-isolation switches off, `network.strictAllowlist: true` with `allowedDomains` limited to the registries that stage needs, `filesystem.denyRead` on the runner's mounts, `credentials.envVars` `deny` for every credential the job holds (the OAuth token, `GH_TOKEN`, `GITHUB_TOKEN`, the action's `OVERRIDE_GITHUB_TOKEN` and `DEFAULT_WORKFLOW_TOKEN`, `CONTEXT7_API_KEY`, the Actions runtime tokens), and `disableAllHooks: true`;
   - `--strict-mcp-config`, because the action forces `enableAllProjectMcpServers` and MCP servers run outside the sandbox;
   - an explicit `--setting-sources` that never includes `local`: `user` where the stage needs nothing from the repository, `user,project` where it needs the repository's skills and `CLAUDE.md`. In `-p` mode, project and local settings apply their `env` at startup (`LD_PRELOAD` and `NODE_OPTIONS` aren't filtered), so `project` is loaded only from a ref whose `.claude/`, `CLAUDE.md` and `.mcp.json` CD has reviewed: `main` (CODEOWNERS), or a factory branch whose patch the writer job refused to let touch them;
   - container `options`: the narrow seccomp profile (Docker's default plus `unshare`, `clone`, `setns`, `mount`, `umount2`, `pivot_root`, `mount_setattr`, `open_tree`, `move_mount`) and `--security-opt systempaths=unconfined`;
   - **file tools are outside the sandbox:** Read, Edit and Write run in the Claude Code process, which holds the token. The stage's tool policy denies Read on `/proc`, `/dev`, `/sys` and the runner's mounts, and Edit on system directories, runner state, `HOME`, temp and mount points, `.git`, `.github`, and `.claude/`, `CLAUDE.md` and `.mcp.json` at any depth (deny rules also match a symlink's target). Skill shell execution is off;
   - **a service the job starts outside the sandbox that sandboxed Bash can reach is part of the boundary**. Test databases run outside the sandbox with open network, on the job container's loopback, reached through the sandbox's HTTP proxy with `localhost` as the only local entry in `allowedDomains`. Never `allowAllUnixSockets`: it drops the sandbox's seccomp helper, whose nested PID namespace and clean environment hide bubblewrap's own environment, and a smoke probe showed sandboxed Bash then reads the job's GitHub token from `/proc/1/environ` (the env scrub leaves GitHub tokens in place) and reaches Claude Code's own Unix sockets. Each runs least-privileged (no Postgres superuser, so no `COPY ... TO PROGRAM`; Redis without `MIGRATE`, `REPLICAOF`, `MODULE`, `CONFIG` and the like), starts with an empty environment, and the start script checks all of it on every run;
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
   - CODEOWNERS on `.github/`, `.claude/`, `CLAUDE.md`, `.mcp.json`, `[sdlc-root]/` and the test and build config, enforced by the `main` ruleset. The discipline parking lots (`[sdlc-root]/disciplines/*.md`) are the exception: an owner-less line unowns them so agents can add entries. The writer's guard follows GitHub's last-match-wins rule, and CD still sees each entry in the PR diff;
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

### Revisit when

- Claude Code or the action changes credential handling or sandbox keys.
- A stage needs a non-HTTP network path (the sandbox proxy covers HTTP(S) only).
- The factory moves off a production host.

## D3: Planning Tier (spec and plan stages see real data and services)

### Why

Spec and plan stages make judgment calls that depend on how the system behaves in production: what the data looks like, which errors occur and where, what an external service returns. D2 keeps every agent job away from production and credentials, which is right for the stages that write and run code, but it leaves planning guessing or asking CD for facts it could look up. So planning may use the data and services that make a better plan, the whole database apart from personal and secret data, and only to read.

**Options considered:**
1. **Ask CD for every fact.** Keeps D2 unchanged; slow, and plans are only as good as the questions.
2. **A periodic scrubbed snapshot.** No path to production, but stale data, a table list to maintain, and no route to services such as error trackers.
3. **A separate planning tier with live read-only access (chosen).** Planning jobs run on their own runners as their own user, with a firewall exception for the production database only, a read-only login that can't see personal or secret data, and services wired from a list with their credentials masked.

### Rules

1. **Two runner tiers.** Implement, execute and revise run on the strict tier (D2, unchanged: no production path). Spec and plan run only on the planning tier: runners under a separate Linux user (`factory-planner`), selected by their own runner label and group. A workflow can't move a code-writing stage onto planning runners without a CODEOWNERS-reviewed edit, and the workflow policy check refuses it.
2. **One firewall exception.** The planning user may reach the production database port on the host and nothing else on the host or LAN; the strict user's firewall is unchanged.
3. **The database login is read-only and excludes personal and secret data.** A dedicated role with `SELECT` only, granted per table and per column: everything except fields holding personal data (names, emails, phone numbers, addresses), credentials (password hashes, API keys, tokens, session data) and payment data. The exclusion list is generated from the models and reviewed by CD; a migration that adds a table or column re-runs the check, and anything new and sensitive-looking stays excluded until CD approves it. The role also has a statement timeout and a connection limit. The agent reaches it through a connection proxy outside the sandbox that holds the password; the agent never sees it.
4. **Services come from a reviewed list.** `.github/factory/services.json` (CODEOWNERS) names each service: its domains, the GitHub secret with its credential, and how the credential attaches. The planning job turns the list into sandbox settings (`credentials.envVars` with `mode: mask`, `injectHosts` set to the service's domains, `network.tlsTerminate`) or into an MCP server entry. Sandboxed commands see a placeholder; the proxy substitutes the real value only on requests to that service. Adding a service is one entry plus one secret, with no workflow edit.
5. **Open internet for planning.** Planning's sandbox allows general web access for research. What leaks is bounded by what the tier can read: credentials are masked and go only to their own hosts, and the database login can't see personal or secret data.
6. **Planning never copies raw data into its documents.** Specs and plans state facts and aggregates (counts, ranges, distributions, examples with identifiers removed), not row dumps. The skill says so; the writer job's checks apply as for every stage.
7. **Planning still writes only documents.** Its output is a spec or plan PR; it never pushes code to run. Rules D1 and D2 otherwise hold unchanged (read-only GitHub token, writer jobs post, frozen code after the agent).

### Forbids

1. A code-writing stage (implement, execute, revise) on planning runners, or any planning runner, secret or exception reachable from the strict tier.
2. A database login with write rights, or one that can read an excluded table or column.
3. A service credential in the agent's environment unmasked, or masked without `injectHosts`.
4. Raw rows of production data in a spec, plan, PR or comment.

### Costs

- A second runner user, its own rootless Docker, firewall and runners on the host.
- The exclusion list must be maintained as models change (mechanical, but it needs CD's review for new sensitive fields).
- Planning can exfiltrate what it can read through the open web; the bound is the data's sensitivity, not the network.

## D4: Production Tier (gates CD approves, run by a broker no agent can reach)

### Why

Some plans need production: deploys, migrations, restarts, backups, checks against a live system. D2 keeps agents away from production, and D3 lets planning read it, never change it. The factory needs a way to do production steps without CD's hands, with approval per step and without a new PR for each approval. Cross-checks rejected the first design, which trusted labels and App comments: any repository writer can edit or race those.

**Options considered:**
1. **Plans mark production steps for CD to run.** Safe, but every gate needs CD's hands and a PR for each segment.
2. **An agent with production access, approved per step.** An agent's judgment in production is what D2 exists to prevent, and a prompt injection would reach production.
3. **A deterministic broker runs reviewed operations after CD approves each gate (chosen).** No agent touches production, and the approval is GitHub's own deployment review, which nobody can edit or forge.

### Rules

1. **No agent in the production tier.** Agents plan gates and write code; a deterministic broker runs the gates. D2 and D3 hold unchanged.
2. **Production work happens only in gates** between phases (`[sdlc-root]/process/production-gates.md`). The plan's last item is a phase; the factory also needs a phase before the first gate.
3. **Operations come from a reviewed catalog** (`.github/factory/production/ops.json`, code-owned): kind, parameters and outputs with an anchored pattern each, timeout, required earlier operations, rollback-only operations. Outputs are typed values, never free text. Scripts are installed root-owned by CD's setup run, never loaded from a workspace.
4. **Two approvals.** Merging the plan approves what each gate may do; the plan guard refuses an unknown operation or a broken parameter. Approving the gate run approves doing it now, with the values filled in.
5. **Approval is GitHub's deployment review.** Each gate gets a run of `factory-gate.yml` whose title carries the request's digest; its job waits on environment `factory-production` (CD the required reviewer, `main` only). Labels and comments authorize nothing: `factory:gate-retry` only asks for a fresh run.
6. **The digest binds everything:** repository, issue, PR, gate, attempt, plan path and blob, PR head, the resolved steps and rollback, and a hash of the installed operations.
7. **The broker checks for itself** (root, socket-activated, one instance per request, reachable only by the runner user): the run is `factory-gate.yml` dispatched on `main`; an approver approved its deployment; the request it rebuilds from the plan blob on `main`, the PR head, its own ledger and its installed operations has the title's digest; the run is in progress; every earlier gate is done in its ledger, as the plan defines it now; production's deployed commit is the one it last recorded (after any gate, or a `baseline` CD records after changing production by hand); nothing is unfinished; the digest never started.
8. **Signed receipts, for every gate.** A CD gate goes through the broker too: it runs nothing and records CD's approval. The broker signs every result, bound to its PR, gate and digest, with a root-only ed25519 key. The hosted report job verifies it with the committed public key before posting it or continuing execution; an unverified result changes nothing, and nothing the factory acts on comes from an editable comment.
9. **Never twice, and never unknown.** The ledger records each step. A finished digest returns its stored receipt; an interrupted run blocks every gate until CD resolves it on the host.
10. **Keys.** The runner user has no sudo, no Docker group and the strict firewall, and holds only the job's read-only token. The broker runs operations as the operator user, with the host's credentials in place. The runner group takes only `factory-gate.yml` from `refs/heads/main`.
11. **Rollback is approved with the gate,** runs automatically when a step fails, and only for steps that got far enough to need it. Schema changes are expand-only.
12. **One gate at a time on the host,** never during the nightly backup (the broker holds its lock).
13. **Release model:** a deploy gate deploys the execution PR's head; production may run ahead of `main` until CD merges it with a merge commit. Deploys only fast-forward, and refuse infrastructure files (compose, Dockerfiles, `docker/`, dependencies, env files, the Makefile, units), which need a rebuild by hand; compose files and `docker/` are code-owned. `.github/` deploys like docs: no container reads it and the broker runs its installed copy, so factory commits don't force a hand catch-up before the next deploy. No infrastructure pattern applies under it, whatever a file there is called (a stack profile's job-image `Dockerfile` included).
14. **A restart never changes production's settings.** Before stopping anything, a deploy asks Compose, with a dry run in the broker's own environment, what restarting would do, and refuses unless every restarted service would stay running as it is. A recreate re-reads the environment, `.env`, ports and mounts, so production could come back with settings it wasn't started with. (Comparing `docker compose config --hash` with the containers' config-hash label doesn't work: they differ even right after `up` in the same environment.)
15. **Healthy after a restart means the restarted process.** The health wait needs evidence newer than the restart (for example, a worker heartbeat newer than the running worker's start), not just a passing health check: a stopped worker's last heartbeat outlives it, and both the container health check and the API's endpoint accept it.
16. **No production tier, no gates.** The tier (the broker, its operations catalog `production/ops.json`, its runner) is the project's own, and the bundle doesn't install it. Without it a plan can have no gates, CD's included, since every gate runs through the broker: the publish guards refuse such a plan and say why. Production steps then stay outside the factory, as CD's.

### Forbids

1. An agent on the production runner, or a production path, credential or runner reachable from an agent job.
2. An operation outside the installed catalog, or a parameter that breaks its pattern.
3. A gate run without an approver's environment approval, or a digest run twice.
4. A production runner job from any workflow but `factory-gate.yml` on `main`, with a container, a `uses:` step, a secret, or any permission beyond read.
5. Operation scripts loaded from a workspace; agent commits to compose files, Dockerfiles or `docker/`.
6. Posting or continuing on a gate result whose signature doesn't verify.

### Costs

- CD sets up an environment, a runner group, labels, the host (`setup-production.sh`) and commits the public key, once; and re-runs setup after any change to the operations.
- The operator user's credentials are in reach of the operation scripts: they are the boundary's weakest part, so they stay few, typed and reviewed.
- Production can run code that isn't on `main` while a deliverable is mid-gate, which blocks unrelated deploys until it merges.
- Unknown outcomes need CD on the host.

## D5: Improve Loop (the factory learns from what CD did to its output)

### Why

The factory repeats mistakes nobody tells it about, while CD's corrections already sit on GitHub: request-changes reviews, revisions, PRs closed unmerged, answers to questions, label overrides, follow-ups left unchecked at merge. Agent transcripts don't outlive their artifacts' retention.

**Options considered:**
1. **Read transcripts weekly.** Races their expiry, and keeps agent text around for the loop to read as text.
2. **An agent with write access files its own improvements.** The loop would change skills and workflows without review, and a prompt injection in a review comment would get a write channel.
3. **A deterministic harvest, a read-only analysis, a deterministic report (chosen).** Only the analysis is an agent, and it returns data that a writer renders.

### Rules

1. **Report only.** The loop posts one report issue a week and changes nothing. Hygiene PRs wait for a dedicated `improve` guard stage (exact allowlist, its own schema, evidence validated). Skills, agents, process docs and anything code-owned stay CD-applied.
2. **Metrics at the source.** Every agent job uploads an allowlisted record (stage, status, cost, turns, models, dispatch inputs, how a lost run ended) for at least 30 days. Never agent text. A missing value is unknown, not zero.
3. **The harvest is code, not an agent.** It runs on a hosted runner with a read-only token, gives every signal a stable id, and caps quoted text, which stays untrusted data.
4. **Trust.** CD is a person the repository lets push (a permission check), never `author_association`. Factory content counts only from the App's bot user, by ID, in the marker grammar. A failed permission check fails the harvest; it never silently drops CD's signals.
5. **The analysis holds no write credential and no shell.** It runs `sdlc-audit` improvement mode headless on the strict tier with Read, Grep and Glob only, and returns proposals in a schema: section, route, severity, target, change, why, effect, evidence ids, and the earlier proposal it matches.
6. **The writer owns the report's structure.** It renders from the schema, escapes every agent string, builds links from the digest only, removes evidence ids the harvest didn't produce, and drops a proposal left with none, saying so. It never drops one silently.
7. **Fingerprints are the writer's.** A new proposal's fingerprint is a hash of its section, target and title. The agent may only point at a fingerprint the ledger already holds. A renamed section keeps its fingerprints: the framework section is `z-sdlc` (formerly `cc-sdlc`), its fingerprints are still hashed under the old name, and readers accept both values.
8. **Durable decisions.** The ledger lives in the report issues (the App's marker) and CD's replies on them (`accept 1 3`, `reject 2: why`, `defer 4`). A proposal matching a decided or open one is shown as one line with its new evidence, never re-proposed.
9. **One report a week, and an empty week posts nothing.** A re-run never posts a second report for the same week. Catch-up starts from the last report's window, so a missed run loses nothing. A report's week is the ISO week its window's midpoint falls in, so a run that ends past midnight into Monday (a delayed schedule, or a run by hand) reports on the week it covers and doesn't take the next Sunday's.

### Forbids

1. A write credential, Bash or network tool in the analysis job.
2. Agent text in the report's structure (headings, links, numbering, the marker), or a link not built from the digest.
3. A fingerprint or evidence id the writer didn't produce or validate.
4. Transcripts as a data source, or agent text in a metrics record.

### Costs

- A weekly Opus run on the Max plan.
- The window's commits are harvested so the analysis can drop already-fixed problems; a busy week means a large digest.
- The analysis can't run code, so it can't measure; numbers come only from the harvest.

---

## Tiers in the factory

The factory routes by `CLAUDE.md` § Three Tiers of Work, with one rule of its own for API and schema
changes, which an unattended run can't negotiate with CD:

- **Additive** changes are **lite**: a new field on a response, a new nullable column, a new endpoint
  that changes nothing existing. Never direct: implement hands them back (`rescope`).
- **Breaking or reshaping** changes are **full**: renaming, removing or retyping fields, changing an
  endpoint's or message's shape, migrating existing data.

A project's `CLAUDE.md` can be stricter; it can't move either kind to direct.

## The stages' sandbox

What every code-writing stage's agent works inside (D2), stated once and mirrored into the skills
that run there:

<!-- MIRROR-SOURCE-START: factory-sandbox -->
- **Bash is sandboxed:** it can write only the workspace and the temp directory, and has no network. Dependencies are already installed; nothing can be installed.
- **No GitHub access:** no `gh`, no push. The issue is in the context file.
- **Off-limits paths:** edits to `.github/`, `.claude/`, `CLAUDE.md`, `.mcp.json` and `.git/` are denied, and the publish job rejects any commit touching a path in `.github/CODEOWNERS` (the project's test and build config, dependency manifests, `[sdlc-root]/` and the like). The SDLC hygiene files are the exception, and you may write them: the discipline parking lots (`[sdlc-root]/disciplines/*.md`) and the knowledge YAMLs (`[sdlc-root]/knowledge/`), except `[sdlc-root]/knowledge/agent-context-map.yaml` and the agent-governing files CODEOWNERS still lists. A knowledge entry the fix makes wrong is corrected in this PR. If the change needs one of them, stop (Edge Cases).
<!-- MIRROR-SOURCE-END: factory-sandbox -->

| Mirror | Copies |
|---|---|
| `factory-sandbox` | `sdlc-implement`, `sdlc-revise` |

---

## Labels

Every factory label. D1 rule 1: an issue carries at most one state label.

| Label | Set by | Meaning |
|---|---|---|
| `factory:triage` | CD | Opt-in: run triage on this issue. The apply step removes it. |
| `factory:ready-for-dispatch` | triage | Small and clear. Implement, review, then open a draft PR. |
| `factory:ready-to-plan` | triage | Needs a plan. The triage comment names the tier (lite or full). The run stops at a plan or spec PR. |
| `factory:needs-input` | any stage | Waiting on CD. The question comment carries `<!-- factory-stage: <stage> -->`. CD's reply comment restarts that stage. |
| `factory:wait` | triage | Doesn't fit now. The comment says what would change that. |
| `factory:review-capped` | execute | The review cap was hit. A draft PR is parked with an open-findings table. |
| `factory:advisor` | triage or CD | A property, not a state: planning gets an advisor. Triage sets it when the plan turns on judgment and clears it otherwise; a label CD added always stands. State sweeps leave it alone. |
| `factory:follow-up` | follow-up filer | A property: filed from a merged plan's checklist. Triage runs, then holds; the App's provenance marker, not the label, decides the hold. |
| `factory:go` | CD | Releases a held issue (a follow-up or a split part): starts its triaged stage once, then removes itself. Needs write access. |
| `factory:revise` | CD | On a factory PR: revise it from the review comments since the last revision. A Request-changes review does the same. |
| `factory:escalated` | revise workflows | The PR had its revise runs (3 for code, 5 for a spec or plan) and CD requested changes again. No more automatic runs; CD decides. |
| `factory:gate` | execute | The execution is stopped before a production gate (D4). Its PR's gate run waits for CD's approval in the production environment. |
| `factory:gate-retry` | CD | On an execution PR: build a fresh gate request and start its gate run, after a failed, rejected or refused gate or a stale request. |

---

## Stack Profiles

A stack profile is how the factory builds, installs and checks one kind of project:
`.github/factory/profiles/<name>/`, chosen by `factory.json`'s `stack.profile`. Every job runs in the
profile's image, and the stages run the profile's commands, never the project's own scripts, which an
agent could have edited. A profile has five files:

| File | Run by | Does |
|---|---|---|
| `Dockerfile` | `factory-image`, on a GitHub-hosted runner | The job image: the stack's toolchain and test services, plus what the factory's own steps use (the Bash sandbox's `bubblewrap` and `socat`, `jq`, `git`, `curl`, `unzip`, and `pgbouncer` for the planning tier). No project dependencies. |
| `install.sh <python-dir> <node-dir>` | The job, outside the sandbox, after secrets are out of the environment | Installs the project's dependencies: the implement sandbox has no network. |
| `test-services.sh <socket-dir> <database>` | The job, as root, before the agent | Starts throwaway test services on the job container's loopback, with logins that can't run code, and prints their settings for the project's env file. |
| `with-test-services <command>` | Commands inside the sandbox | Runs a command with the test services' ports reachable through the sandbox's proxy. |
| `verify [python\|node\|probe]` | The stages and smoke | The project's checks (tests, lint, type check, build); `probe` proves the toolchain and the test database work. Reads its directories from `verify.conf`. |

The interface is the first profile's shape: `agent_job.sh` passes `stack.python` and `stack.node` as
the project's two directories, and `verify` takes `python` and `node` areas. A profile for another
stack uses them for its own directories until the first such profile generalizes the stack block.
Start from a copy of `python-node`, keep its security properties (no superuser test login, services
started with an empty environment, nothing installed inside the sandbox), and prove it with
`factory-smoke`.

---

## Enablement

The bundle installs inert: nothing runs until a person adds `factory:triage` to an issue, and the
first run fails without the setup below, done in order. Steps 3 to 5 replace the seed's placeholders
in `factory.json`; after each settings change, run `python3 .github/factory/render.py` and commit the
settings and the workflows to `main`. `python3 .github/factory/bootstrap.py` checks steps 2 to 9 and
changes nothing; with `--apply` it does step 6, and only once the placeholders are gone. It reports,
and never sets, the secrets, the App's install, CODEOWNERS and the `main` ruleset, which stay CD's. It
needs an organization owner's `gh` login (`admin:org`) for the runner groups and the App.

1. **An organization; for a private repository, on GitHub Team or above.** The runners register to
   an organization runner group, which a personal account doesn't have. The credential boundary
   (D2) rests on environment secrets, environments deployable from `main` only and a ruleset
   requiring code-owner review, which a private repository has from Team up; the production tier's
   required reviewer (D4 rule 5) on a private repository needs GitHub Enterprise. Why an
   organization, not a repository's own runners: one pool of hardened runners serves every project,
   and the group's selected-workflows list keeps a project's other workflows off them.
2. **Settings.** In `.github/factory/factory.json`, the `stack` block: the profile, where the project
   keeps its Python and Node code, its env file, its test database name, and workspace paths its
   code reads. Write `triage-policy.md` (its direction, rules, containers, plan triggers and external
   sources). The planning tier (D3) is required; its database is optional. To give the plan and spec
   stages one, fill `planning.json` and create the read-only role it names (D3 rule 3); list services
   in `services.json` (D3 rule 4). Leave both empty for none.
3. **The job image.** Set `image.repository` to where the organization publishes it (for example
   `ghcr.io/<org>/factory-job`), render, and push to `main`: `factory-image` builds the profile's
   `Dockerfile` on a GitHub-hosted runner and publishes it (or run it by hand). Its run on the
   install's own push fails, publishing to the placeholder; this one is the first that counts. Copy the digest from
   its run summary into `image.digest` and render again. Every factory job runs in this image, pinned
   by its digest. Projects on the same profile can share one image: give each repository read
   access to the package.
4. **The echo service.** Smoke proves the sandbox's credential masking against a host that echoes
   each request's headers back. Deploy `.github/factory/echo/worker.js` as a Cloudflare Worker on a
   `workers.dev` address (for example `npx wrangler deploy .github/factory/echo/worker.js --name
   factory-echo --compatibility-date 2025-01-01`), or run `echo/server.py` on any host behind HTTPS,
   and set `smoke.echo_host` to its host name. It stores nothing, and receives only smoke's
   throwaway values; one serves the whole organization.
5. **The App.** `python3 .github/factory/create_app.py <organization>` creates the factory's GitHub
   App from its manifest (Contents, Issues and Pull requests read and write, Metadata read; no
   webhook, no `workflows` or `actions` permission), writes its bot user into `factory.json` and its
   private key to a new file only you can read. Install it on the repository from the link it
   prints. One App serves the whole organization: another project installs the same App and copies
   `app` into its own `factory.json`.
6. **`bootstrap.py --apply`.** Creates the labels (§ Labels); the environments, each deployable
   from `main` only: writer (`factory-writer`), planning (`factory-planning`) and, with the production
   tier, production (`factory-production`, CD the required reviewer); and the runner group
   (`factory-pool`) with this repository and its agent workflows, or adds them to it. With the
   production tier, `factory-gate.yml` goes to the project's own group instead
   (`factory-pool-<repository>-prod`, on the host that runs its production). Through the API, an
   update to a group replaces its selected-workflows list with the list it sends (an omitted list
   empties it), and one that sends `visibility` empties its repository list: send the whole workflow
   list and never `visibility` (`bootstrap.py` does).
7. **Secrets.** In `factory-writer`: secret `FACTORY_APP_PRIVATE_KEY` and variable
   `FACTORY_APP_CLIENT_ID` (the commands `create_app.py` printed; then delete the key file). In
   `factory-planning`: `FACTORY_DB_READER_PASSWORD` with a planning database, and `FACTORY_SVC_1`..`4`
   for services. Repository secrets: `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`; never an
   organization secret), and optionally `CONTEXT7_API_KEY`.
8. **The runner host.** A Linux host with systemd, nftables, `python3`, rootless Docker's extras
   (`docker-ce-rootless-extras`) and room for the runners' work and images. From a checkout of
   `main`, set the host's own settings in `.github/factory/host/host.conf`; then, for each tier, write a
   runner registration token (`gh api -X POST orgs/<org>/actions/runners/registration-token --jq
   .token`) to `.github/factory/host/reg-token` (mode 600) and run `sudo bash
   .github/factory/host/setup.sh` (the strict tier) or `sudo TIER=planning bash
   .github/factory/host/setup.sh` (the planning tier). It creates each tier's user, rootless Docker,
   firewall and runners, and registers no runner whose jobs can reach the host or the LAN. Put the
   host's own LAN and VPN addresses in `factory.json`'s `smoke.host_probes`, so smoke checks them
   too. One host serves the whole organization, and can serve other organizations too: each one
   after the first sets `RUNNER_INSTANCE` in its `host.conf` and gets its own users, firewall tables
   and services, isolated from the others' as from the host. Setup refuses runners registered to
   another organization, and a planning database port is only ever the organization's own.
9. **CODEOWNERS and the `main` ruleset** (D2 rule 6): code owners on `.github/`, `.claude/`,
   `CLAUDE.md` at any depth, `.mcp.json`, `[sdlc-root]/` and the test and build configuration, with
   owner-less lines last for the discipline parking lots, the knowledge YAMLs (except the
   agent-governing ones) and the SDLC changelog; code-owner review required on `main`. The seeded
   `tests/test_codeowners.py` checks the file against the guard; until it exists it fails, and its
   path lists are the project's to extend (its test and build configuration, its source paths).
10. **CI**, required on `main`: `python .github/factory/render.py --check`, then
    `python .github/factory/workflow_policy.py .github/workflows`, then
    `python -m unittest discover -s .github/factory/tests` (with PyYAML).
11. **Smoke.** Run `factory-smoke`; every job must pass before the first issue (D2 rule 5).
