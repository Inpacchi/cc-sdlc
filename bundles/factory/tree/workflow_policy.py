"""Check every workflow against the factory's binding rules (D1 stage contract, D2 credential
boundary). Run by ci.yml on every PR and push to main.

Usage: python3 workflow_policy.py <workflows-dir> [<factory-dir>]
       (factory-dir defaults to <workflows-dir>/../factory, where the *-tools.args files live)

This is a drift check, not the security boundary. It catches a workflow edit that weakens an
agent job by mistake. A workflow is a program (expressions, $GITHUB_ENV writes, other actions), so
no static check is complete against someone editing workflows on purpose. The boundary is
CODEOWNERS review of .github/ (enforced by the main ruleset), the Claude App having no `workflows`
permission, and the runtime sandbox probe (factory-smoke). The factory's design rules say what
this leaves open (z-sdlc process/factory.md, D2).

Allowlists, not blocklists:
- Runners: only exact GitHub-hosted labels count as hosted. Any other job needs a container whose
  only options are the factory seccomp profile and systempaths=unconfined, with no volumes, no
  service containers, no docker:// steps and no docker CLI.
- Actions: `uses: ./...` (unscanned local actions) and any action naming claude other than
  `anthropics/claude-code-action@` are refused.
- Agent steps (`anthropics/claude-code-action@`): only allowlisted inputs. claude_code_oauth_token is
  the OAuth secret, github_token the job's own token, settings a frozen settings file. claude_args
  is parsed the way the action parses it: each flag at most once, from an allowlist, with its value
  checked; printable ASCII only (the action splits words on a non-breaking space, shlex doesn't);
  exactly one ${{ env.FACTORY_TOOL_ARGS }}; --model a literal model ID or a choice input of model
  IDs; --setting-sources user or user,project, and project only with a checkout pinned to the
  default branch.
- Agent jobs: exactly one checkout, of this repository into the workspace, without persisted
  credentials, and `git remote remove origin` before the agent step (the action would write the
  job token into origin's URL).
- Bash: a tool policy that grants Bash (or sets no --tools, which grants every tool) needs the
  sandbox: a frozen --settings file also passed as the settings input, CLAUDE_CODE_SUBPROCESS_ENV_SCRUB
  set to 1, and the factory container options.
- Agent jobs: an explicit read-only permissions block; the tool policy set only by
  `tr ... < .github/factory/*-tools.args`; no env (workflow, job or agent step) that sets
  FACTORY_TOOL_ARGS, an Anthropic variable or a token, or references any secret but CONTEXT7_API_KEY.
- The OAuth secret appears only as an agent step's claude_code_oauth_token, or in the step env of
  a run step in an agent job (the probes and scans that compare against it).
- The factory App's key appears only as the private-key input of actions/create-github-app-token,
  in a job on a GitHub-hosted runner that uses the writer environment and runs no agent.
- No run step starts Claude Code or the Agent SDK directly.
- Agent jobs set CLAUDE_CODE_DISABLE_BACKGROUND_TASKS: "1" (headless runs dispatch in the foreground).
- Runner tiers (design rule D3): only the planning workflows (PLANNING_WORKFLOWS) run on the
  planning runners, and their agent jobs must; only jobs there may use the planning
  environment, which holds the read-only database password.
- Production tier (design rule D4): only factory-gate.yml's `execute` job runs on the production
  runner. It runs on the host with no container (it only talks to the root broker's socket), so the
  container rule doesn't apply; instead it has the production environment (CD's approval), exactly
  read-only permissions, no `uses:` steps, no secrets and no agent. The production environment is
  for that job only (CD gates run through it too). factory-gate.yml has no agent job.
"""

import json
import pathlib
import re
import shlex
import sys

import yaml

ACTION = "anthropics/claude-code-action@"
HOSTED = {
    "ubuntu-latest", "ubuntu-24.04", "ubuntu-22.04", "ubuntu-24.04-arm", "ubuntu-22.04-arm",
    "windows-latest", "windows-2025", "windows-2022", "macos-latest", "macos-15", "macos-14",
}
ALLOWED_OPTIONS = {
    ("--security-opt", "seccomp=/etc/factory-runner/seccomp-bwrap.json"),
    ("--security-opt", "systempaths=unconfined"),
}
OAUTH = "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"
OAUTH_REF = re.compile(r"secrets\.CLAUDE_CODE_OAUTH_TOKEN")
APP_KEY = "${{ secrets.FACTORY_APP_PRIVATE_KEY }}"
APP_KEY_REF = re.compile(r"secrets\.FACTORY_APP_PRIVATE_KEY")
APP_TOKEN_ACTION = "actions/create-github-app-token@"
JOB_TOKENS = {"${{ github.token }}", "${{ secrets.GITHUB_TOKEN }}"}
DEFAULT_BRANCH_REFS = {"${{ github.event.repository.default_branch }}", "main"}
AGENT_INPUTS = {"claude_code_oauth_token", "github_token", "prompt", "claude_args", "settings", "allowed_bots",
                "classify_inline_comments", "bot_name", "bot_id"}
SETTINGS_INPUT = re.compile(r"^\$\{\{ env\.CHECKS \}\}/[\w.-]+\.settings\.json$")
REMOVE_REMOTE = re.compile(r"^\s*git remote remove origin\s*$", re.M)
TOOL_ARGS_SETTER = re.compile(r"FACTORY_TOOL_ARGS=\$\(tr '\\n' ' ' < \.github/factory/[\w-]+-tools\.args\)")
TOOL_ARGS_FILE = re.compile(r"\.github/factory/([\w-]+-tools\.args)")
EXPR = re.compile(r"\$\{\{.*?\}\}")
HEADLESS = "SDLC headless mode: no person is present."
# One directory level is allowed (the brief rewrite resumes from its own), never `..`.
RESUME_FILE = re.compile(r"^\$\{\{ env\.CHECKS \}\}/(?:[\w-][\w.-]*/)?[\w.-]+\.jsonl$")
PRINTABLE = re.compile(r"^[\x20-\x7e\t\n]*$")
MODEL_ID = re.compile(r"^claude-[a-z0-9.-]+$")
MODEL_INPUT = re.compile(r"^\$\{\{ inputs\.model(?: \|\| '(claude-[a-z0-9.-]+)')? \}\}$")
# claude_args flags an agent step may set, with a check for each value (None: takes no value).
# --model is checked separately (it depends on the workflow's inputs).
FLAGS = {
    "model": lambda v: True,
    "json-schema": lambda v: True,
    "mcp-config": lambda v: True,
    "strict-mcp-config": None,
    "setting-sources": lambda v: v in ("user", "user,project"),
    "permission-mode": lambda v: v == "auto",
    "permission-prompts": lambda v: v == "none",
    "max-turns": lambda v: v.isdigit(),
    "settings": lambda v: bool(SETTINGS_INPUT.match(v)),
    # The headless declaration (process/headless-mode.md), verbatim.
    "append-system-prompt": lambda v: v == HEADLESS,
    # A literal advisor, or the one the workflow chose from its choice input.
    "advisor": lambda v: v in ("opus", "fable", "${{ env.FACTORY_ADVISOR }}"),
    "effort": lambda v: v in ("low", "medium", "high", "xhigh", "max"),
    # Resume a saved session: only a file in the frozen checks directory.
    "resume": lambda v: bool(RESUME_FILE.match(v)),
}
ENV_NAME = re.compile(r"TOKEN|^ANTHROPIC_|^CLAUDE_CODE_OAUTH|^FACTORY_TOOL_ARGS$|_PAT$|PRIVATE_KEY", re.I)
DIRECT_CLAUDE = re.compile(r"@anthropic-ai/|claude-agent-sdk|(^|[\s;&|(/])claude(\s|$)", re.M)


SERVICE_SLOTS = {f"FACTORY_SVC_{n}" for n in range(1, 5)}
SERVICES_RUN = re.compile(r"python3 -I \.github/factory/services\.py \.github/factory/services\.json ")
PLANNING_WORKFLOWS = {"factory-plan.yml", "factory-spec.yml", "factory-revise-doc.yml"}
PRODUCTION_WORKFLOW = "factory-gate.yml"
PRODUCTION_JOBS = {"execute": "runner"}
PRODUCTION_PERMISSIONS = {"actions": "read", "contents": "read", "issues": "read", "pull-requests": "read"}
SECRET_REF = re.compile(r"secrets\.|secrets\[|toJSON\(\s*secrets", re.I)

# The project's runner labels and environment names (factory.json in the factory directory; configure()).
PLANNING_LABEL = PRODUCTION_LABEL = WRITER_ENVIRONMENT = PLANNING_ENVIRONMENT = PRODUCTION_ENVIRONMENT = None


def configure(factory_dir):
    """Read the runner labels and environment names this project's workflows were rendered with."""
    global PLANNING_LABEL, PRODUCTION_LABEL, WRITER_ENVIRONMENT, PLANNING_ENVIRONMENT, PRODUCTION_ENVIRONMENT
    config = json.loads((pathlib.Path(factory_dir) / "factory.json").read_text())
    PLANNING_LABEL, PRODUCTION_LABEL = config["runners"]["planning"], config["runners"]["production"]
    environments = config["environments"]
    WRITER_ENVIRONMENT, PLANNING_ENVIRONMENT = environments["writer"], environments["planning"]
    PRODUCTION_ENVIRONMENT = environments["production"]


def environment_name(job):
    environment = job.get("environment")
    return environment.get("name") if isinstance(environment, dict) else environment


def production_failures(workflow_name, name, job, is_agent_job):
    """The production tier (design rule D4): one containerless job, behind CD's approval, that can only
    hand the run to the broker."""
    labels = job.get("runs-on", [])
    labels = [labels] if isinstance(labels, str) else labels if isinstance(labels, list) else []
    on_prod = PRODUCTION_LABEL in labels
    environment = environment_name(job)
    failures = []
    if workflow_name == PRODUCTION_WORKFLOW and is_agent_job:
        failures.append(f"{name}: {PRODUCTION_WORKFLOW} may not run an agent")
    if on_prod:
        if workflow_name != PRODUCTION_WORKFLOW or PRODUCTION_JOBS.get(name) != "runner":
            failures.append(f"{name}: only {PRODUCTION_WORKFLOW}'s execute job may run on {PRODUCTION_LABEL} runners")
        if job.get("container") or job.get("services"):
            failures.append(f"{name}: the production job runs no container or service")
        if environment != PRODUCTION_ENVIRONMENT:
            failures.append(f"{name}: the production job needs the {PRODUCTION_ENVIRONMENT} environment (CD's approval)")
        if job.get("permissions") != PRODUCTION_PERMISSIONS:
            failures.append(f"{name}: the production job's permissions must be exactly {PRODUCTION_PERMISSIONS}")
        for step in job.get("steps") or []:
            if "uses" in step or set(step) - {"name", "id", "env", "run", "shell", "if", "timeout-minutes"}:
                failures.append(f"{name}: the production job runs only plain run steps")
        if SECRET_REF.search(str(job)):
            failures.append(f"{name}: the production job references a secret")
    if environment == PRODUCTION_ENVIRONMENT:
        kind = PRODUCTION_JOBS.get(name) if workflow_name == PRODUCTION_WORKFLOW else None
        if kind is None or (kind == "runner") != on_prod or (kind == "hosted" and not hosted(job.get("runs-on", []))):
            failures.append(f"{name}: the {PRODUCTION_ENVIRONMENT} environment is for {PRODUCTION_WORKFLOW}'s gate jobs only")
        if kind == "hosted" and (job.get("permissions") != {} or SECRET_REF.search(str(job))
                                 or any("uses" in s for s in job.get("steps") or [])):
            failures.append(f"{name}: the CD-gate job has no permissions, secrets or actions")
    return failures


def tier_failures(workflow_name, name, job, is_agent_job):
    """Planning runners and their environment belong to the planning workflows only (D3 rule 1)."""
    labels = job.get("runs-on", [])
    labels = [labels] if isinstance(labels, str) else labels if isinstance(labels, list) else []
    on_planning = PLANNING_LABEL in labels
    environment = job.get("environment")
    environment = environment.get("name") if isinstance(environment, dict) else environment
    failures = []
    if on_planning and workflow_name not in PLANNING_WORKFLOWS:
        failures.append(f"{name}: only the planning workflows may run on {PLANNING_LABEL} runners")
    if workflow_name in PLANNING_WORKFLOWS and is_agent_job and not on_planning:
        failures.append(f"{name}: a planning agent job must run on {PLANNING_LABEL} runners")
    if environment == PLANNING_ENVIRONMENT and not on_planning:
        failures.append(f"{name}: the {PLANNING_ENVIRONMENT} environment is for planning-tier jobs only")
    return failures


def hosted(runs_on):
    labels = [runs_on] if isinstance(runs_on, str) else runs_on
    return isinstance(labels, list) and bool(labels) and all(l in HOSTED for l in labels)


def container_failures(name, job):
    failures = []
    if not job.get("container"):
        failures.append(f"{name}: runs off GitHub-hosted runners without a container")
    if job.get("services"):
        failures.append(f"{name}: runs service containers off GitHub-hosted runners")
    container = job.get("container")
    if isinstance(container, dict):
        if container.get("volumes"):
            failures.append(f"{name}: container mounts volumes")
        try:
            tokens = shlex.split(str(container.get("options", "")))
        except ValueError:
            tokens = []
            failures.append(f"{name}: container options don't parse")
        while tokens:
            if tuple(tokens[:2]) in ALLOWED_OPTIONS:
                tokens = tokens[2:]
            else:
                failures.append(f"{name}: container option not allowed: {tokens[0]}")
                tokens = tokens[1:]
    for step in job.get("steps") or []:
        if str(step.get("uses", "")).startswith("docker://"):
            failures.append(f"{name}: docker:// step off GitHub-hosted runners")
        if re.search(r"(^|[\s;&|(])docker\s", str(step.get("run", "")), re.M):
            failures.append(f"{name}: runs the docker CLI off GitHub-hosted runners")
    return failures


def claude_words(args):
    """claude_args as shell words, with each ${{ }} expression kept whole (raises ValueError)."""
    exprs = EXPR.findall(args)
    placeholder = {f"__expr{i}__": e for i, e in enumerate(exprs)}
    text = args
    for key, expr in placeholder.items():
        text = text.replace(expr, key, 1)
    words = shlex.split(text)
    for key, expr in placeholder.items():
        words = [w.replace(key, expr) for w in words]
    return words


def model_failures(label, value, model_input):
    """--model: a literal model ID, or the workflow's model input when it's a choice of model IDs."""
    if MODEL_ID.match(value):
        return []
    match = MODEL_INPUT.match(value)
    if not match:
        return [f"{label}: --model must be a model ID or ${{{{ inputs.model }}}}: {value}"]
    options = (model_input or {}).get("options") if isinstance(model_input, dict) else None
    if (model_input or {}).get("type") != "choice" or not options or not all(MODEL_ID.match(str(o)) for o in options):
        return [f"{label}: --model takes inputs.model, which must be a choice input of model IDs"]
    return []


def claude_args_failures(label, args, pinned, model_input):
    """Parse claude_args like the action does (shell words, '--flag value'), refuse anything off the list."""
    failures = []
    if not PRINTABLE.match(args):
        return [f"{label}: claude_args has a character outside printable ASCII"]
    if "#" in args:
        return [f"{label}: '#' in claude_args (the action parses it as a shell comment)"]
    if EXPR.findall(args).count("${{ env.FACTORY_TOOL_ARGS }}") != 1:
        failures.append(f"{label}: claude_args needs exactly one ${{{{ env.FACTORY_TOOL_ARGS }}}}")
    try:
        words = claude_words(args)
    except ValueError:
        return failures + [f"{label}: claude_args don't parse"]
    seen = set()
    i = 0
    while i < len(words):
        word = words[i]
        i += 1
        if word == "${{ env.FACTORY_TOOL_ARGS }}":
            continue
        if not word.startswith("--") or "=" in word:
            failures.append(f"{label}: unexpected claude_args word: {word}")
            continue
        flag = word[2:]
        if flag not in FLAGS:
            failures.append(f"{label}: claude_args flag not allowed: --{flag}")
            continue
        if flag in seen:
            failures.append(f"{label}: --{flag} given twice")
        seen.add(flag)
        check = FLAGS[flag]
        if check is None:
            continue
        if i >= len(words) or words[i].startswith("--"):
            failures.append(f"{label}: --{flag} has no value")
            continue
        value = words[i]
        i += 1
        if flag == "model":
            failures += model_failures(label, value, model_input)
        elif not check(value):
            failures.append(f"{label}: --{flag} value not allowed: {value}")
        if flag == "setting-sources" and "project" in value.split(",") and not pinned:
            failures.append(f"{label}: loads project settings without a checkout pinned to the default branch")
    for flag in ("strict-mcp-config", "setting-sources"):
        if flag not in seen:
            failures.append(f"{label}: no --{flag}")
    return failures


def grants_bash(text):
    """Whether a tool policy grants Bash: named in --tools or --allowedTools, or no --tools at all."""
    words = shlex.split(text)
    if "--tools" not in words:
        return True
    current = None
    for word in words:
        if word.startswith("--"):
            current = word
        elif current in ("--tools", "--allowedTools"):
            if any(t == "Bash" or t.startswith("Bash(") for t in re.split(r"[,\s]+", word)):
                return True
    return False


def tool_args_failures(name, setters, factory_dir):
    """Read the *-tools.args files the job's setters name. Returns (failures, grants Bash)."""
    failures, bash = [], False
    for file in sorted({f for s in setters for f in TOOL_ARGS_FILE.findall(str(s["run"]))}):
        path = factory_dir / file
        try:
            text = path.read_text()
        except OSError:
            failures.append(f"{name}: tool policy {file} not found in {factory_dir}")
            continue
        if not PRINTABLE.match(text):
            failures.append(f"{name}: tool policy {file} has a character outside printable ASCII")
            continue
        try:
            bash = grants_bash(text) or bash
        except ValueError:
            failures.append(f"{name}: tool policy {file} doesn't parse")
    return failures, bash


def checkout_failures(name, steps):
    """Exactly one checkout, of this repository into the workspace, credentials not persisted.
    Returns (failures, pinned to the default branch)."""
    checkouts = [s for s in steps if str(s.get("uses", "")).startswith("actions/checkout@")]
    if len(checkouts) != 1:
        return [f"{name}: agent job needs exactly one checkout (has {len(checkouts)})"], False
    with_ = checkouts[0].get("with") or {}
    failures = [f"{name}: agent job checkout sets {k}" for k in ("repository", "path") if k in with_]
    if str(with_.get("persist-credentials", "")).strip().lower() != "false":
        failures.append(f"{name}: agent job checkout must set persist-credentials: false")
    return failures, str(with_.get("ref", "")).strip() in DEFAULT_BRANCH_REFS


def sandbox_failures(name, job, workflow_env, agent_steps):
    """A Bash-granting tool policy runs only inside the factory's proven sandbox setup."""
    failures = []
    scrub = {**workflow_env, **(job.get("env") or {})}.get("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB")
    if str(scrub) != "1":
        failures.append(f"{name}: grants Bash without CLAUDE_CODE_SUBPROCESS_ENV_SCRUB: \"1\"")
    container = job.get("container")
    options = []
    if isinstance(container, dict):
        try:
            words = shlex.split(str(container.get("options", "")))
            options = list(zip(words[::2], words[1::2]))
        except ValueError:
            pass
    if not ALLOWED_OPTIONS <= set(options):
        failures.append(f"{name}: grants Bash outside a container with the factory seccomp and systempaths options")
    for step in agent_steps:
        label = f"{name} / {step.get('name', step.get('id', 'claude-code-action'))}"
        with_ = step.get("with") or {}
        settings = str(with_.get("settings", "")).strip()
        try:
            words = claude_words(str(with_.get("claude_args", "")))
        except ValueError:
            words = []
        flag = words[words.index("--settings") + 1] if "--settings" in words[:-1] else None
        if not settings or flag != settings:
            failures.append(f"{label}: grants Bash without the same frozen file as --settings and the settings input")
    return failures


def agent_failures(name, job, workflow_env, model_input, factory_dir, workflow_name=""):
    failures = []
    steps = job.get("steps") or []
    perms = job.get("permissions")
    if not isinstance(perms, dict):
        failures.append(f"{name}: agent job needs an explicit permissions block")
    elif any(v not in ("read", "none") for v in perms.values()):
        failures.append(f"{name}: agent job grants a write permission")
    checkout, pinned = checkout_failures(name, steps)
    failures += checkout

    setters = [s for s in steps if "FACTORY_TOOL_ARGS=" in str(s.get("run", ""))]
    if not setters or any(len(re.findall(r"FACTORY_TOOL_ARGS=", str(s["run"])))
                          != len(TOOL_ARGS_SETTER.findall(str(s["run"]))) for s in setters):
        failures.append(f"{name}: FACTORY_TOOL_ARGS must be set only from .github/factory/*-tools.args")
    policy, bash = tool_args_failures(name, setters, factory_dir)
    failures += policy
    agent_steps = [s for s in steps if str(s.get("uses", "")).startswith(ACTION)]
    # The action writes the job token into origin's URL, where the agent can read it.
    first_agent = next(i for i, s in enumerate(steps) if str(s.get("uses", "")).startswith(ACTION))
    if not any(REMOVE_REMOTE.search(str(s.get("run", ""))) for s in steps[:first_agent]):
        failures.append(f"{name}: agent job must run `git remote remove origin` before the agent step")
    if bash:
        failures += sandbox_failures(name, job, workflow_env, agent_steps)

    envs = [("workflow", workflow_env), ("job", job.get("env") or {})]
    envs += [(s.get("name", "agent step"), s.get("env") or {}) for s in steps if str(s.get("uses", "")).startswith(ACTION)]
    # Service credential slots (README § Services) may reach a planning agent step, each exactly its
    # own secret, when the job builds its sandbox settings with services.py, which masks all four.
    builds_services = any(SERVICES_RUN.search(str(s.get("run", ""))) for s in steps[:first_agent])
    for where, env in envs:
        for key, value in env.items():
            if (key in SERVICE_SLOTS and str(value).strip() == f"${{{{ secrets.{key} }}}}"
                    and where not in ("workflow", "job") and workflow_name in PLANNING_WORKFLOWS and builds_services):
                continue
            refs = set(re.findall(r"secrets\.(\w+)", str(value)))
            if ENV_NAME.search(key) or refs - {"CONTEXT7_API_KEY"}:
                failures.append(f"{name}: {where} env {key} reaches the agent")

    for step in steps:
        if not str(step.get("uses", "")).startswith(ACTION):
            continue
        label = f"{name} / {step.get('name', step.get('id', 'claude-code-action'))}"
        with_ = step.get("with") or {}
        failures += [f"{label}: input not allowed: {k}" for k in sorted(set(with_) - AGENT_INPUTS)]
        if str(with_.get("claude_code_oauth_token", "")).strip() != OAUTH:
            failures.append(f"{label}: claude_code_oauth_token must be {OAUTH}")
        if str(with_.get("github_token", "")).strip() not in JOB_TOKENS:
            failures.append(f"{label}: github_token must be the job's own read-only token")
        if "settings" in with_ and not SETTINGS_INPUT.match(str(with_["settings"]).strip()):
            failures.append(f"{label}: settings must be a frozen file under ${{{{ env.CHECKS }}}}")
        failures += claude_args_failures(label, str(with_.get("claude_args", "")), pinned, model_input)
    return failures


def oauth_failures(name, job, workflow_env, is_agent_job):
    """The OAuth secret: an agent step's input, or a run step's env inside an agent job. Nowhere else."""
    failures = []
    if OAUTH_REF.search(str(workflow_env)) or OAUTH_REF.search(str(job.get("env") or "")):
        failures.append(f"{name}: OAuth token in workflow or job env")
    for step in job.get("steps") or []:
        label = f"{name} / {step.get('name', step.get('uses', 'step'))}"
        rest = {k: v for k, v in step.items() if k not in ("with", "env")}
        if OAUTH_REF.search(str(rest)):
            failures.append(f"{label}: OAuth token outside an input or env")
        is_agent = str(step.get("uses", "")).startswith(ACTION)
        with_ = dict(step.get("with") or {})
        if is_agent:
            with_.pop("claude_code_oauth_token", None)
        if OAUTH_REF.search(str(with_)):
            failures.append(f"{label}: OAuth token passed as an input")
        if OAUTH_REF.search(str(step.get("env") or "")) and not (is_agent_job and "run" in step):
            failures.append(f"{label}: OAuth token in env outside an agent job's run step")
    return failures


def app_key_failures(name, job, workflow_env, is_agent_job):
    """The App key: create-github-app-token's private-key, in a hosted writer-environment job with no agent."""
    failures = []
    if APP_KEY_REF.search(str(workflow_env)) or APP_KEY_REF.search(str(job.get("env") or "")):
        failures.append(f"{name}: App key in workflow or job env")
    users = []
    for step in job.get("steps") or []:
        label = f"{name} / {step.get('name', step.get('uses', 'step'))}"
        with_ = dict(step.get("with") or {})
        is_minter = str(step.get("uses", "")).startswith(APP_TOKEN_ACTION)
        if is_minter and str(with_.get("private-key", "")).strip() == APP_KEY:
            with_.pop("private-key")
            users.append(label)
        rest = {k: v for k, v in step.items() if k != "with"}
        if APP_KEY_REF.search(str(rest)) or APP_KEY_REF.search(str(with_)):
            failures.append(f"{label}: App key outside create-github-app-token's private-key")
    if users:
        environment = job.get("environment")
        if isinstance(environment, dict):
            environment = environment.get("name")
        if environment != WRITER_ENVIRONMENT:
            failures.append(f"{name}: App key in a job outside the {WRITER_ENVIRONMENT} environment")
        if not hosted(job.get("runs-on", [])):
            failures.append(f"{name}: App key on a self-hosted runner")
        if is_agent_job:
            failures.append(f"{name}: App key in an agent job")
    return failures


def job_failures(name, job, workflow_env, model_input, factory_dir, workflow_name=""):
    failures = []
    steps = job.get("steps") or []
    runs_on = job.get("runs-on", [])
    on_prod = PRODUCTION_LABEL in ([runs_on] if isinstance(runs_on, str) else runs_on if isinstance(runs_on, list) else [])
    if not hosted(runs_on) and not on_prod:
        failures += container_failures(name, job)
    for step in steps:
        uses = str(step.get("uses", ""))
        if uses.startswith("./"):
            failures.append(f"{name}: local action {uses} isn't scanned")
        elif "claude" in uses.lower() and not uses.startswith(ACTION):
            failures.append(f"{name}: Claude action other than {ACTION}: {uses}")
        if DIRECT_CLAUDE.search(str(step.get("run", ""))):
            failures.append(f"{name} / {step.get('name', 'run')}: runs Claude Code outside the action")
    is_agent_job = any(str(s.get("uses", "")).startswith(ACTION) for s in steps)
    failures += tier_failures(workflow_name, name, job, is_agent_job)
    failures += production_failures(workflow_name, name, job, is_agent_job)
    if is_agent_job and str({**workflow_env, **(job.get("env") or {})}.get("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS")) != "1":
        # Headless mode: the run ends with the orchestrator's turn, so a background agent's work is lost.
        failures.append(f"{name}: agent job without CLAUDE_CODE_DISABLE_BACKGROUND_TASKS: \"1\"")
    if is_agent_job:
        failures += agent_failures(name, job, workflow_env, model_input, factory_dir, workflow_name)
    failures += oauth_failures(name, job, workflow_env, is_agent_job)
    failures += app_key_failures(name, job, workflow_env, is_agent_job)
    return failures


def main():
    root = pathlib.Path(sys.argv[1])
    factory_dir = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else root.parent / "factory"
    configure(factory_dir)
    paths = sorted([*root.glob("*.yml"), *root.glob("*.yaml")])
    failures = []
    for path in paths:
        workflow = yaml.safe_load(path.read_text()) or {}
        workflow_env = workflow.get("env") or {}
        # YAML 1.1 reads a bare `on` key as the boolean True.
        triggers = workflow.get("on") or workflow.get(True) or {}
        dispatch = triggers.get("workflow_dispatch") if isinstance(triggers, dict) else None
        model_input = ((dispatch or {}).get("inputs") or {}).get("model")
        for name, job in (workflow.get("jobs") or {}).items():
            failures += [f"{path}: {f}" for f in job_failures(name, job, workflow_env, model_input, factory_dir, path.name)]
    # claude_args wraps each result schema in single quotes: one apostrophe breaks every run of that stage.
    for schema in sorted(factory_dir.glob("*.schema.json")):
        if "'" in schema.read_text():
            failures.append(f"{schema}: contains a single quote (claude_args wraps schemas in single quotes)")
    # The services the planning stages may use: a malformed entry would fail every planning run.
    services_file = factory_dir / "services.json"
    if services_file.exists():
        sys.path.insert(0, str(factory_dir))
        import services  # noqa: E402 (the factory directory's own module)
        try:
            services.load(services_file)
        except services.Invalid as e:
            failures.append(f"{services_file}: {e}")
    for f in failures:
        print(f"::error::{f}")
    print(f"workflow policy: {len(paths)} workflows, {len(failures)} violations")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
