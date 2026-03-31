---
title: "Tessl Engineering Blog Reference"
created: 2026-03-30
tags: [ai-native-development, spec-driven-development, agent-skills, context-engineering, process-improvement]
source: https://tessl.io/blog/
---

# Tessl Engineering Blog Reference

## About Tessl

Tessl is an AI-native development startup founded by Guy Podjarny (formerly founder of Snyk), backed by $125M in funding (Index Ventures, Accel). The company builds tools for spec-driven development (SDD) — structured specification writing that guides AI coding agents to produce reliable, deterministic output. Their products include the Tessl Framework (enforces plan → spec → build workflow), the Spec Registry (10,000+ versioned API usage specs), and the Skill-Optimizer (evaluation pipeline for agent skills).

Tessl's editorial voice is led by Patrick Debois (DevOps pioneer) and Guy Podjarny, with contributions from Jennifer Sand and Paul Duvall. The blog publishes 3-5 articles per month, spanning from mid-2024 through present (March 2026).

## Why Tessl Matters to This Framework

Tessl's blog is the single richest external source for grounding an SDLC framework's AI-native development practices. Specific overlaps:

- **Process Improvement:** Comprehensive coverage of spec-driven development methodology, skill lifecycle management, evaluation frameworks, and maturity models
- **Testing:** Novel testing paradigms for AI-generated code — system invariants, spec-driven QA, behavioral compliance testing
- **Coding:** Context engineering patterns, skill authoring best practices, Claude Code-specific workflow guidance
- **Skill Governance:** The skills lifecycle model (build → evaluate → distribute → optimize) directly parallels how this framework manages its own skill artifacts

**Important caveat:** Tessl has a clear commercial interest in SDD adoption. Quantitative claims (35% API improvement, 15%→99% behavioral compliance, 67%→94% skill performance) are internally consistent and methodologically described but are Tessl-produced measurements using Tessl tooling. Treat as directionally credible pending independent replication.

## Blog URL

https://tessl.io/blog/

---

## Tier 1: Directly Applicable (34 articles)

Articles that map directly to active framework disciplines or knowledge areas with extractable process guidance.

### Theme: Spec-Driven Development Methodology

1. **[Spec-Driven Development: 10 Things You Need to Know About Specs](https://tessl.io/blog/spec-driven-development-10-things-you-need-to-know-about-specs/)**
   Comprehensive taxonomy of SDD: spec types (functional, agent identity, task, knowledge), context window constraints, registries analogous to npm/PyPI, strangler pattern for legacy modernization.
   *Domains: Process Improvement, Coding*

2. **[From Vibe Coding to Spec-Driven Development](https://tessl.io/blog/from-vibe-coding-to-spec-driven-development/)**
   Three-phase workflow: PRD → technical spec → task decomposition. Evidence: "1 iteration with structure ≈ 8 iterations without."
   *Domains: Process Improvement*

3. **[Why Code Alone Isn't Enough: The Case for Code Specification](https://tessl.io/blog/from-code-centric-to-spec-centric/)**
   Argues specs should replace code as primary artifact. Testing validates spec adherence, not code quality. Autonomous maintenance and multi-implementation flexibility as downstream benefits.
   *Domains: Process Improvement, Testing*

4. **[The Most Valuable Developer Skill in 2025? Writing Code Specifications](https://tessl.io/blog/the-most-valuable-developer-skill-in-2025-writing-code-specifications/)**
   Professional case for centering developer training on specification writing. References OpenAI's model spec as practical example.
   *Domains: Process Improvement, Coding*

5. **[Taming AI Coding Agents with Specifications — What the Experts Say](https://tessl.io/blog/taming-agents-with-specifications-what-the-experts-say/)**
   Three-level maturity framework: spec-assisted (claude.md files) → spec-driven (specs drive changes) → spec-centric (code becomes disposable). Critical tension between determinism and adaptability noted.
   *Domains: Process Improvement*

6. **[From Vibe Coding to Vibe Planning](https://tessl.io/blog/from-vibe-coding-to-vibe-planning/)**
   Read-only exploration phase producing specs before coding. Introduces "meta-prompting" for consistency. Workflow: plan → spec → build.
   *Domains: Process Improvement*

7. **[How Tessl's Products Pioneer Spec-Driven Development](https://tessl.io/blog/how-tessls-products-pioneer-spec-driven-development/)**
   Plans/Specs/Tests triad as long-term product memory. Framework enforces process discipline; Registry prevents hallucination via curated knowledge.
   *Domains: Process Improvement*

8. **[Spec-Driven Development with Claude Code](https://tessl.io/blog/spec-driven-dev-with-claude-code/)**
   Claude Code-specific workflow: maintain spec.md, use /clear and /compact for context management, embed "think very hard" triggers for complex reasoning.
   *Domains: Process Improvement, Coding*

### Theme: AI-Native Development Patterns

9. **[The 4 Patterns of AI-Native Dev — Overview](https://tessl.io/blog/the-4-patterns-of-ai-native-dev-overview/)**
   Four role shifts: producer→manager, implementation→intent, delivery→discovery, content→knowledge. Affects all roles, not just developers.
   *Domains: Process Improvement*

10. **[Charting Your AI-Native Journey](https://tessl.io/blog/charting-your-ai-native-journey/)**
    Two-axis maturity model: Change (workflow disruption) vs. Trust (reliability requirements). Four quadrants for AI adoption. Anchor in vision, execute from low-change/low-trust.
    *Domains: Process Improvement, Product Research*

11. **[AI Development Patterns: What Actually Works](https://tessl.io/blog/ai-development-patterns-what-actually-works/)**
    Three pattern categories from 30+ repos: foundation (rules-as-code), development (spec-driven TDD: spec→tests→code), operations (policy-as-code, security scanning). AI-driven traceability.
    *Domains: Process Improvement, Testing, Deployment*

### Theme: Skill Lifecycle & Evaluation

12. **[Announcing Skills on Tessl: The Package Manager for Agent Skills](https://tessl.io/blog/skills-are-software-and-they-need-a-lifecycle-introducing-skills-on-tessl/)**
    Skills as versioned software with four-stage lifecycle: build → evaluate → distribute → optimize. Review evals (structural) and task evals (behavioral). Version pinning via tessl.json.
    *Domains: Process Improvement, Coding*

13. **[Introducing Task Evals: Measure Whether Your Skills Actually Work](https://tessl.io/blog/introducing-task-evals-measure-whether-your-skills-actually-work/)**
    A/B skill testing with LLM judge scoring. Addresses silent drift where model updates cause skills to stop working. Write → evaluate → inspect → refine loop.
    *Domains: Process Improvement, Testing*

14. **[Stop Guessing Whether Your Skill Works: Skill-Optimizer](https://tessl.io/blog/stop-guessing-whether-your-skill-works-skill-optimizer-measures-and-improves-it/)**
    Four-dimension scoring: completeness, actionability, conciseness, robustness. Improved Fastify skill from 67% to 94%. Identifies regressions where instructions confuse rather than help.
    *Domains: Process Improvement, Testing*

15. **[Three Context Eval Methodologies at Tessl](https://tessl.io/blog/three-context-eval-methodologies/)**
    Evaluation ladder: Skill Review (structural linting) → Task Evals (isolated behavioral testing) → Repo Evals (grounded in real repository commits).
    *Domains: Process Improvement, Testing*

16. **[Do Agent Skills Actually Help? A Controlled Experiment](https://tessl.io/blog/do-agent-skills-actually-help-a-controlled-experiment/)**
    Controlled experiment (n=30): baseline 53%, official skills 73%, custom skills 80%. When activated: 96% success; when not: 0%. Initial activation rate ~10% until trigger descriptions refined.
    *Domains: Process Improvement, Testing*

17. **[A Proposed Evaluation Framework for Coding Agents](https://tessl.io/blog/proposed-evaluation-framework-for-coding-agents/)**
    ~270 libraries, points-based rubric. Tiles delivered ~35% relative improvement over baseline; ~50% for post-2022 libraries. Metrics: accuracy, execution time, agent turns.
    *Domains: Process Improvement, Coding*

18. **[Your AGENTS.md File Isn't the Problem. Your Lack of Evals Is.](https://tessl.io/blog/your-agentsmd-file-isnt-the-problem-your-lack-of-evals-is/)**
    Unvalidated context is useless or harmful. ElevenLabs and Cisco skills achieved 1.79x improvement through validated context. The problem is absent feedback loops, not context files.
    *Domains: Process Improvement*

### Theme: Behavioral Compliance & Context Engineering

19. **[Our AI Is the Bright Kid with No Manners, Part 1](https://tessl.io/blog/our-ai-is-the-bright-kid-with-no-manners-part-1/)**
    Agent scored 15% behavioral compliance despite correct code. Solution: three-layer architecture — Scripture (on-demand skills), Commandments (always-loaded rules), Rituals (deterministic bash scripts). Improved from 15% to 99%.
    *Domains: Process Improvement, Coding*

20. **[Our AI Is the Bright Kid with No Manners, Part 2](https://tessl.io/blog/our-ai-is-the-bright-kid-with-no-manners-part-2/)**
    Open-book evals masked weaknesses (93% → 15% when made realistic). Core principle: "every behavior that CAN be deterministic SHOULD be deterministic." 19 deterministic scripts, 2.8k token always-on rules.
    *Domains: Process Improvement, Testing*

21. **[Context-Aware Development in Kiro](https://tessl.io/blog/context-aware-development-in-kiro-from-hallucination-to-production/)**
    Three-layer context strategy: MCP servers (authoritative docs) + agent steering files (project memory) + specs (complex features). Working Python code in 15 minutes.
    *Domains: Process Improvement, Coding*

22. **[Making Claude Good at Go Using Context Engineering with Tessl](https://tessl.io/blog/making-claude-good-at-go-using-context-engineering-with-tessl/)**
    Curated documentation tiles, steering rules, project-level AGENTS.md/CLAUDE.md. 100% vs 92% baseline, 1.6x faster, 3x lower cost.
    *Domains: Process Improvement, Coding*

23. **[Stop Prompt Hacking](https://tessl.io/blog/stop-prompt-hacking/)**
    Prompt phrasing variations produce no measurable difference in modern models. Replace one-off prompt cleverness with durable skills and structured context. "Context is the product surface now."
    *Domains: Process Improvement, Coding*

### Theme: Agent Standards & Architecture

24. **[Agents.md: An Open Standard for AI Coding Agents](https://tessl.io/blog/the-rise-of-agents-md-an-open-standard-and-single-source-of-truth-for-ai-coding-agents/)**
    Vendor-neutral Markdown standard. Supported by GitHub Copilot, OpenAI, Google, Cursor. Hierarchical placement per repository/subdirectory.
    *Domains: Process Improvement, Coding*

25. **[From Prompts to AGENTS.md: What Survives Across Thousands of Runs](https://tessl.io/blog/from-prompts-to-agents-md-what-survives-across-thousands-of-runs/)**
    Persistent memory structures — not clever prompts — survive. Hierarchical AGENTS.md, meta-learning loops, multi-agent cooperation. Analysis of 40,000+ GitHub repositories.
    *Domains: Process Improvement*

26. **[Agent Prompts Need a Registry](https://tessl.io/blog/agent-prompts-need-a-registry/)**
    Three inadequate approaches (git submodules, agent-specific repos, package managers). Registry needs: vendor-agnostic, semantic versioning, familiar CLI.
    *Domains: Process Improvement*

27. **[I Invented a Three-Tier Stack for AI Agents](https://tessl.io/blog/i-invented-a-three-tier-stack-for-ai-agents-and-im-not-apologizing/)**
    Library (reusable code) / ASI-Agentic Skill Interface (teaches agents) / Policy (user rules). Independent versioning, public Library+ASI with private Policy.
    *Domains: Architecture, Process Improvement*

28. **[Claude's Agent Skills Let You Customize AI for Your Workflows](https://tessl.io/blog/anthropic-gives-claude-code-contextual-intelligence-with-agent-skills/)**
    Three skill scopes (project, personal, plugin), progressive disclosure via YAML frontmatter, token efficiency. Skills transform Claude from generic assistant to "programmable coworker."
    *Domains: Process Improvement, Coding*

### Theme: Practical Workflows & Code Quality

29. **[Level Up Claude Code: 14 Techniques Our Engineers Actually Use](https://tessl.io/blog/level-up-claude-code-14-techniques-our-engineers-actually-use/)**
    Plan-first mode, context tiles, CLAUDE.md as project memory, GitHub MCP, custom commands, skills, sub-agents, hooks, git worktrees, YOLO mode, session resumption, security review.
    *Domains: Coding, Process Improvement*

30. **[Best Agent Skills for AI Code Review: 8 Evaluated Skills](https://tessl.io/blog/best-agent-skills-for-ai-code-review-8-evaluated-skills-for-dev-workflows/)**
    Four-dimension scoring matrix: Review, Validation, Implementation, Activation. Top: secondsky (88% review, 100% impl) and Sentry (86%, 82% activation).
    *Domains: Testing, Coding*

31. **[Testing and Securing AI-Generated Code with Cursor](https://tessl.io/blog/testing-and-securing-ai-generated-code-with-cursor/)**
    Front-loaded security guardrails at generation time. Rules: no fakes/mocks/stubs unless external deps, parameterized queries, auth validation. Module-level memory files.
    *Domains: Testing, Coding, Deployment*

32. **[Beyond Tests: What to Verify in AI-Generated Code](https://tessl.io/blog/beyond-tests-what-to-verify-in-ai-generated-code/)**
    Three invariant levels: universal (concurrency safety), system (cross-service transaction atomicity), feature (workflow preconditions/postconditions). Verification > testing.
    *Domains: Testing*

33. **[How Amazon's Q CLI and Kiro Can Turn Specs into Automated QA](https://tessl.io/blog/how-amazon-s-q-cli-and-kiro-can-turn-specs-into-automated-qa/)**
    Spec-to-QA pipeline: specs as validation blueprint, Playwright MCP, structured pass/fail/partial reports. Human control emphasized.
    *Domains: Testing, Process Improvement*

34. **[The Tessl Registry Now Has Security Scores, Powered by Snyk](https://tessl.io/blog/the-tessl-registry-now-has-security-scores-powered-by-snyk/)**
    Skill security scanning: prompt injection (36% of skills affected), malware, credential mishandling, toxic flows. Three-signal evaluation: quality + impact + security.
    *Domains: Process Improvement, Testing*

---

## Tier 2: Adjacent & Valuable (11 articles)

Transferable patterns and ecosystem context that strengthen framework decisions.

1. **[2025 Year in Review: From Vibe Coding to Viable Code](https://tessl.io/blog/a-year-in-review-from-vibe-coding-to-viable-code/)**
   Defining shifts of 2025: agent autonomy, structure replacing spontaneity after production DB deletion, MCP adoption (8M downloads) with security vulnerabilities.
   *Domains: Process Improvement, Deployment*

2. **[Amazon Probes Surge in Outages Linked to AI Coding Tools](https://tessl.io/blog/a-high-blast-radius-amazon-probes-surge-in-outages-linked-to-ai-coding-tools/)**
   Kiro deleted and recreated entire infrastructure env (13-hour disruption). Response: senior engineer approval for AI-assisted changes.
   *Domains: Deployment, Process Improvement*

3. **[Stack Overflow's 2025 Report: Trends on AI-Native Development](https://tessl.io/blog/what-happened-devs-appear-to-use-ai-more-and-believe-it-less/)**
   84% AI adoption, 33% trust (down from 43%). 69% of agent users report productivity gains; 19% of experienced devs report slower productivity.
   *Domains: Process Improvement, Product Research*

4. **[Context-Bench: Benchmarking AI's Context Engineering Proficiency](https://tessl.io/blog/context-bench-benchmarking-ais-context-engineering-proficiency/)**
   Claude Sonnet 4.5 leads at ~74% completion. GPT-5 cheaper per token but higher total cost. Model selection data for framework users.
   *Domains: Process Improvement, Coding*

5. **[A Look at Spec Kit — GitHub's Spec-Driven Development Toolkit](https://tessl.io/blog/a-look-at-spec-kit-githubs-spec-driven-software-development-toolkit/)**
   GitHub's .specify/ directory with spec.md, plan.md, tasks/. Confirms cross-industry convergence on plan/spec/task pattern.
   *Domains: Process Improvement*

6. **[AWS Backs Spec-Driven Dev with Kiro](https://tessl.io/blog/from-vibe-coding-to-viable-code-aws-dives-into-spec-driven-ai-software-development-with-kiro/)**
   Amazon internal SDD practices productized. Agent hooks, steering files.
   *Domains: Process Improvement*

7. **[Kiro Spec-Driven Development Platform Hits Prime Time](https://tessl.io/blog/kiro-spec-driven-development-platform-hits-prime-time-with-cli-support-in-tow/)**
   Property-based testing from specs. "Spec correctness" metric. CLI-first spec development.
   *Domains: Testing, Process Improvement*

8. **[Kilo Code: An Open-Source AI Coding Agent](https://tessl.io/blog/inside-kilo-code-an-open-source-ai-coding-agent-with-plans-to-reshape-software-development/)**
   Open-source coding agent: multi-file refactoring, multi-agent orchestration, model-agnostic.
   *Domains: Coding*

9. **[As AI Coding Agents Take Flight, What Does This Mean for Jobs?](https://tessl.io/blog/as-ai-coding-agents-take-flight-what-does-this-mean-for-software-development-jobs/)**
   Role transformation: developers shift toward review, architecture, specification.
   *Domains: Process Improvement*

10. **[OpenClaw for Dummies](https://tessl.io/blog/openclaw-for-dummies/)**
    Minimum viable OpenClaw agent: workspace/instructions/tools/runs. "Start simple, make reliable, make clever last."
    *Domains: Process Improvement, Architecture*

11. **[How Anthropic Is Turning Claude into an Always-On Agent](https://tessl.io/blog/how-anthropic-is-turning-claude-into-an-always-on-agent-and-what-it-learned-from-openclaw/)**
    Persistent, multi-platform Claude agents. Lessons from OpenClaw architecture.
    *Domains: Architecture, Process Improvement*

---

## Tier 3: Good to Know (16 articles)

Background knowledge, company news, tool landscape, and events.

1. [Tessl Launches Spec-Driven Framework and Registry](https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry/) — Product launch announcement
2. [Announcing Tessl's Products to Unlock the Power of Agents](https://tessl.io/blog/announcing-tessls-products-to-unlock-the-power-of-agents/) — Earlier product announcement
3. [Announcing Our Series A](https://tessl.io/blog/announcing-our-series-a-for-ai-native-software-development/) — $125M funding ($25M seed + $100M Series A)
4. [Announcing Tessl, the AI Native Development Startup](https://tessl.io/blog/announcing-tessl-the-ai-native-development-startup/) — Founding announcement
5. [Announcing AI Native Dev Con](https://tessl.io/blog/announcing-ai-native-dev-con-supercharge-development-today-and-reimagine-it-for-tomorrow/) — Conference announcement
6. [AI Native Devcon: NYC](https://tessl.io/blog/ai-native-devcon-the-event-for-spec-driven-ai-software-development-in-nyc/) — Event details
7. [GitHub to Use Copilot Interaction Data for Training](https://tessl.io/blog/github-to-use-copilot-interaction-data-for-training-by-default/) — Privacy/policy news
8. [Anthropic Tests 'Auto Dream' for Claude Code Memory](https://tessl.io/blog/anthropic-tests-auto-dream-to-clean-up-claudes-memory/) — Experimental feature
9. [Claude Code Gets 'Auto Mode'](https://tessl.io/blog/claude-code-gets-auto-mode-to-cut-approval-fatigue/) — Feature news
10. [With Composer 2, Cursor Targets Longer Tasks](https://tessl.io/blog/with-composer-2-cursor-targets-longer-coding-tasks-with-lower-pricing/) — Tool update
11. [The Best Open-Source Model for Agentic Coding? Devstral](https://tessl.io/blog/devstral/) — Model release
12. [When OpenAI Goes Open Source: Codex CLI](https://tessl.io/blog/open-ai-codex-cli/) — Tool release
13. [Ollama Helps Claude Code Run Locally](https://tessl.io/blog/ollama-paves-a-path-for-claude-code-to-run-locally-on-open-weight-models/) — Tooling
14. [Claude Code Visibility Shift Sparks New Open-Source Tool](https://tessl.io/blog/claude-code-hid-file-access-data-a-new-open-source-observability-tool-emerged/) — Community tooling
15. [Anthropic Open-Sources Its Internal Code-Simplifier Agent](https://tessl.io/blog/anthropic-open-sources-its-internal-code-simplifier-agent/) — Tool release
16. [GitHub Brings Claude and Codex Agents into Copilot](https://tessl.io/blog/github-brings-claude-and-codex-agents-directly-into-copilot/) — Integration news

---

## Key Takeaways

1. **Spec-driven development is the convergence point.** Tessl, AWS (Kiro), GitHub (Spec Kit), and independent practitioners all converge on plan → spec → build as the foundational AI-native workflow. This is not one company's opinion — it's an emerging industry pattern.

2. **Skills need a lifecycle, not just authoring.** The build → evaluate → distribute → optimize loop with progressive evaluation (review evals → task evals → repo evals) is the most complete skill governance model available. Skills without evaluation provide minimal or negative value.

3. **Activation design is as important as skill content.** A skill achieving 96% success when activated scored 0% when not activated — and initial activation rate was only ~10%. Trigger engineering in YAML frontmatter and skill descriptions is not optional.

4. **The deterministic-first principle reduces variance.** Any agent behavior that CAN be deterministic (file scanning, policy fetching, pattern matching) SHOULD use scripts rather than LLM judgment. The Scripture/Commandments/Rituals three-layer architecture is the most proven implementation of this principle.

5. **Evaluation contamination is a hidden risk.** Open-book evaluations (giving agents all necessary files inline) mask true weaknesses. Realistic evals dropped one agent's score from 93% to 15%. All framework skill evaluations should simulate real-world discovery conditions.

6. **Unvalidated context is harmful, not neutral.** LLM-generated context files showed -3% improvement; validated skills showed +20-27%. The quality gate matters more than the quantity of context.

7. **System invariants fill a testing gap.** Traditional tests miss concurrency safety, cross-service transaction atomicity, and workflow precondition integrity. The three invariant levels (universal, system, feature) address AI-generated code's system-level failure modes.

8. **Prompt engineering is dead; context engineering is the replacement.** Phrasing variations produce no measurable difference. Durable systems (skills, structured context, canonical components) are the new product surface.

## Gaps

Tessl's blog provides **no substantive coverage** of:

- **Architecture** — No system design, API design, or architectural pattern guidance (only conceptual agent architecture)
- **Design (UX/UI)** — Zero coverage across all discovery methods
- **Data Modeling** — No schema patterns, data structures, or model health content
- **Business Analysis** — Requirements/stakeholder management only appears as SDD sub-topics
- **Product Research** — One tangential Stack Overflow survey analysis; no methodology content
- **Deployment** — Limited to one Amazon outage news report; no CI/CD or infrastructure pattern guidance

**Better sources for gap domains:** Look to Spotify, Netflix, Stripe, and Airbnb engineering blogs for Architecture and Deployment. Look to Material Design, GOV.UK Design System, and Shopify Polaris for Design. Look to dbt Labs and Mode Analytics for Data Modeling.
