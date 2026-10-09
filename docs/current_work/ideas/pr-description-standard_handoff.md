# Handoff: a reviewable PR description standard (plan PRs and code PRs)

**Date:** 2026-10-09
**From:** the software-factory phase 3 session (cc-sdlc + quantile)
**For:** a fresh session that builds it
**Status:** built 2026-10-09. cc-sdlc: `templates/pr_description_template.md` and its wiring (changelog entry "A reviewable PR description standard"). quantile: the port and the factory rendering (its changelog entry "PR descriptions written for CD"). Defaults taken for the open questions, for CD to confirm or change:
1. **Budget:** 450 words above the record for a plan, 500 for code. Each field has a length cap in the schema, which the CLI enforces at generation by re-prompting the agent (checked on Claude Code 2.1.292, which the factory's pinned action installs, and 2.1.295). The record shows the measured total; the guard refuses only past twice the target.
2. **Scale by tier:** one skeleton. A direct fix omits only Deviations, and a code decision needs a rejected alternative only where one was weighed.
3. **Read order:** no snippet-extraction mandate. Files are read before they're named, and the guard marks a key file that isn't in the repository as new or not found.
4. **Risk tiers:** defined in the template by what valid use gets and whether a revert undoes it, with the highest fitting tier winning. Quantile's always-high areas sit in a `PROJECT-SECTION` block in its copy.
5. **Interactive parity:** yes, through `CLAUDE-SDLC.md` § Pull Request Description.

## Why this exists

The software factory (see `software-factory_design.md` and `software-factory_handoff.md`) opened its first plan PR: quantile PR #31, the D13 plan for issue #30. CD reviewed it and couldn't approve it in good conscience. CD owns the project and knows the codebase, but the project was largely built through cc-sdlc, and the PR was verbose and full of terms CD didn't follow:

> "It doesn't really feel right for me to read and approve something that I don't understand."

The root cause is the audience. The plan document is written for the executing agent: exact functions, file lines, test fixtures. That's the right content for the agent's contract and the wrong document for CD's approval. The PR body (the plan's `summary` field, rendered by `implement_guard.py`) inherited the same voice.

This applies beyond the factory. Every cc-sdlc PR that asks CD to approve agent-written work has the same problem: interactive sessions, plan and spec PRs, and code PRs.

## What CD decided (2026-10-09)

1. **Plain language throughout, but plain language alone isn't enough.** Every PR tells CD, for sure:
   - what changes for users;
   - what CD is approving;
   - what the original problem was;
   - what is being tackled;
   - any risk;
   - how it will be (or was) verified;
   - what is deferred or left out.
2. **Learning perspective.** The PR should leave CD understanding the codebase better: key files, key concepts, and things CD may not have thought about.
3. **A high-level "how it works" section belongs in the PR.** CD **overrode** Google's guidance that explanations belong only in code comments: "as I review PRs, it is going to be the predominant way in which I look at the code in the first place." The PR gives the approach, how the pieces fit, and the order to read the files in. Line-level explanation still goes in code comments.
4. **Adopt what the research supports** (below): review focus, evidence over claims, a length budget, and scope integrity. CD "largely agrees" with the proposed template.
5. **Neuroloom, factory memory and other factory items are out of scope here.**

## Research synthesis (2026-10-09)

Two research passes ran. Most pages were read through a web summarizer, so **spot-check any quote or number before it goes into a framework doc.** Sources marked "snippet" were seen only in search results.

**Recurring elements, from strongest backing to weakest:**

| Element | Backing |
|---|---|
| **The why: what prompted the change** | Google eng-practices, "Writing good CL descriptions" (https://google.github.io/eng-practices/review/developer/cl-descriptions.html); Linux kernel "Describe your changes" (https://www.kernel.org/doc/html/latest/process/submitting-patches.html); Phabricator (https://secure.phabricator.com/book/phabflavor/article/writing_reviewable_code/); Chromium; GitHub (https://github.blog/developer-skills/github/how-to-write-the-perfect-pull-request); GitLab (https://docs.gitlab.com/development/code_review/); Kubernetes PR template. Bacchelli & Bird, Microsoft Research 2013: understanding the change is reviewers' main challenge, and "what instigated the change" is their top need. |
| **Proof of verification, not assertion** | Simon Willison, "Your job is to deliver code you have proven to work" (https://simonwillison.net/2025/Dec/18/code-proven-to-work): paste commands and output, or video. Addy Osmani's "PR contract" (https://addyo.substack.com/p/code-review-in-the-age-of-ai). Claude Code best practices (https://code.claude.com/docs/en/best-practices): show evidence rather than asserting success. Phabricator's required Test Plan (https://secure.phabricator.com/book/phabricator/article/differential_test_plans/). Spotify Honk part 3 (https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3): verifiers run before a PR opens. Warp's factory `implementation` skill (https://raw.githubusercontent.com/warpdotdev-demos/cloud-factory-demo/main/.agents/skills/implementation/SKILL.md): validation commands and results, run links, video and screenshots. |
| **Review focus: where to look, what the author is unsure of** | Osmani ("review focus", 1–2 areas). Atlassian (https://www.atlassian.com/blog/git/written-unwritten-guide-pull-requests): group files by concept, flag the main-bulk files. Kubernetes ("special notes for your reviewer"). Maciej Dziuba's software-factory gist (https://gist.github.com/Maciejdziuba/88890d7e0eeefa5a8738bbe9fd5e20b8): "decisions the agent is least confident about". Zurich study of 80k PRs (https://arxiv.org/html/2602.14611v1): asking for a specific feedback type correlated with 64–72% higher merge odds. |
| **Small, single-purpose changes** | Google small CLs (~100 lines; 1,000 is too large); GitLab (~200 lines); SmartBear/Cisco (200–400 lines per sitting, ≤60 minutes); GitHub's agent-PR guide (https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/): split when the purpose won't fit in one sentence; Codex tech lead (plan first, then about 6 right-sized PRs). |
| **Scope integrity: what wasn't touched, no tests or CI weakened** | Spotify's LLM judge compares diff to prompt and vetoes about a quarter of changes for scope creep (refactors, disabled flaky tests). GitHub's agent-PR guide: weakening CI is a blocker. |
| **User-visible impact** | Linux kernel; Kubernetes "user-facing change?" with a release note. |
| **Risk, non-goals, alternatives, unresolved questions** | Thin for code PRs, core to design-doc practice: Google design docs (https://www.industrialempathy.com/posts/design-docs-at-google/); Rust RFC template (https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md); PEP 1 (https://peps.python.org/pep-0001/); Uber RFCs via Pragmatic Engineer (https://blog.pragmaticengineer.com/rfcs-and-design-docs/); Oxide RFD 1; Nygard ADRs. A plan PR is a design approval, so these apply there. |
| **Learning** | Thinnest in PR guides, real elsewhere. Bacchelli & Bird: nearly every reviewer cited knowledge transfer as a motive; unfamiliar files were the stated reason reviewers couldn't follow a change. Rust RFC "guide-level explanation" ("teach it as if it already exists"); PEP "How to Teach This"; Willison's "linear walkthroughs" (snippet). |

**Two cautions that match CD's experience:**
- **Agents are verbose.** GitHub's agent-PR guide: "Agents love verbosity", so edit the body before requesting review. Birgitta Böckeler on spec-driven tools (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html): "I'd rather review code than all these markdown files." Willison also warns that agents write convincing descriptions you still have to check.
- **Plan approval doesn't replace code review.** Dex Horthy (Tessl podcast, https://tessl.io/podcast/124): HumanLayer's "trust the plan, skip the code" experiment left an unusable codebase after months. CD approves the plan **and** reviews the code PR.

## The agreed template

Fixed section order. Plain language; code identifiers appear only where they help CD find something (the "How it works" and "Learn" sections). **Everything above the collapsed agent record fits on about one screen.** No source gives a number; start with roughly 400–500 words above the fold, tune after a few real PRs, and enforce it mechanically.

### Plan (and spec) PR

1. **The problem.** What prompted this, and the symptom a user sees. 2–3 sentences.
2. **What changes for users.** Bullets, or "nothing visible".
3. **What you're approving.** Numbered decisions. Each says the choice and, in one clause, the alternative it rejects. Scope extensions beyond the issue are listed here explicitly.
4. **Scope.** What's tackled; what isn't (non-goals); deferred items as proposed follow-up issues.
5. **Risk.** Tier (low, medium, high), the top 1–3 risks, and how to undo it.
6. **Review focus.** Where the agent is least sure; what CD may not have thought of.
7. **How it will be verified.** The tests and checks, and what CD will be able to observe.
8. **How it works.** (CD's addition.) The approach at a high level, how the pieces fit, and the order to read the files in once the code exists.
9. **Learn the change.** Key files, each with its role in this change. 1–3 key concepts with plain definitions. Why the code is shaped that way, if it isn't obvious.
10. *(collapsed `<details>`)* **Agent record.** Review rounds, open findings, scores (FACTS), models and cost, and a link to the full plan document.

### Code PR

The same skeleton, with these changes:
- **Section 7 becomes "How it was verified": results, not intent.** Commands and output, test counts, CI status, screenshots or video for UI changes.
- **Add "Scope integrity":** "no tests or CI weakened; touched only the planned files", or the exceptions with reasons.
- **Add "Deviations from the approved plan"** (execute stage): what changed and why. Omit for direct fixes with no plan.
- **"What you're approving"** names the behavior being merged.

### For worked examples

Use #30 / PR #31. A plain-language rewrite of #31 was drafted in the originating session. Its content:
- **Problem:** URL filters on the market API silently ignore bad values, so a typo returns a different answer instead of an error.
- **Approving:**
  1. Bad values become 400 errors on 11 filters.
  2. Delete the unused `PredictionViewSet.VALID_INTERVALS`.
  3. Also validate `interval` on prediction views, beyond what the issue named, because valid horizons depend on the interval.
- **Edge case:** `?interval=15m` on predictions now errors instead of returning an empty list. Production has no 15m data.
- **Risk:** low; input checking only; a test per endpoint.

The full agent result is in factory-plan run 37953444977 (`plan-transcript` artifact, 7-day retention from 2026-10-09).

## What to build

**cc-sdlc (framework change: changelog entry and consistency checks per `CLAUDE.md`).**
1. **The standard.** A template for PR descriptions, likely `templates/pr_description_template.md` with plan and code variants. If it gets bigger, add a process doc. Add it to `skeleton/manifest.json`.
2. **Where it applies.**
   - Skills that produce documents for approval: `sdlc-lite-plan` and `sdlc-plan` (plan and spec), and the execute skills for code.
   - Interactive sessions that open PRs.
   - `process/headless-mode.md` § Headless Result: when the caller's schema has brief fields, fill them per the template.

   No PR-description guidance exists in cc-sdlc today. A grep of `skills/`, `process/`, `templates/` and `CLAUDE-SDLC.md` found nothing.
3. **The plan document is unchanged.** It stays the agent's contract. Only the approval surface changes.
4. **`sdlc-migrate`:** the new template is a direct copy (§2.1).
5. **Release type:** a new cross-skill convention is minor by `CLAUDE.md` § Versioning. Don't cut a tag without CD's request.

**quantile factory (`.github/factory/`, after cc-sdlc).**
1. **Structured fields, not free text.**
   - `plan.schema.json` gains a `brief` object with one field per section: problem, user changes, decisions (each with the rejected alternative), scope (tackled, not tackled, deferred), risk (tier, items, undo), review focus, verification, how it works, key files (path and role), concepts (name and meaning).
   - `implement.schema.json` gains the code-PR fields: verification results, scope integrity, plan deviations.
   - claude_args wraps schemas in single quotes, so the schemas must not contain any.
2. **The publish job renders the body.** `implement_guard.py` builds `pr-body.md` from the fields in the fixed order.
   - Agent text can't change the structure.
   - Keep `escape()` for markers, mentions and refs.
   - Cap the words per section and the total above the fold; refuse or truncate per the guard's existing patterns.
   - The agent record (review rounds, findings, FACTS, `orchestrator`, cost) goes in the collapsed section.
3. **Prompts.** The `factory-plan.yml` prompt and the execute prompt in `factory-implement.yml` point at the installed template. `sdlc-implement` (quantile `.claude/skills/`) gets the code-PR variant.
4. **Tests** in `.github/factory/tests/test_implement_guard.py` for rendering, caps and escaping.
5. **Keep the `workflow_policy.py` check green,** and update the README and the quantile changelog.

## Constraints and context for the receiving session

- **cc-sdlc `CLAUDE.md` rules apply:**
  - directives are framework changes;
  - changelog in the same step;
  - consistency checks before the summary;
  - `[sdlc-root]` paths in skills;
  - conventional commits.
- **Factory rules (D1, D2, D3 in `software-factory_design.md`):**
  - agents hold no write credential;
  - publish runs on a hosted runner;
  - factory PRs never merge by admin bypass;
  - code-owned paths are refused, except `ops/sdlc/disciplines/*.md`, which is unowned as of 2026-10-09.
- **Coordinate with another live session.** A second session (named cc-sdlc-52) also edits the factory. Coordinate via SendMessage if it's still running, and never overwrite `software-factory_design.md` wholesale.
- **State of #31.** PR #31 is still open, waiting on CD. Whether CD approves it as is or waits for a re-render under the new standard is CD's call. A re-run costs about an hour and about $50 API-equivalent on the factory account.
- **Repo state.** cc-sdlc has unpushed local commits from this work (software-factory design and handoff docs, the headless foreground-dispatch rule `2df932e`). quantile `main` is pushed.

## Open questions

1. **The above-the-fold budget.** Start at about 400–500 words? CD tunes it after a few PRs.
2. **Scale by tier?** Fowler's Ship/Show/Ask and the design-doc sources argue for lighter ceremony on small changes. Should direct-fix code PRs get a shorter variant, for example without "What you're approving" and "Learn"?
3. **Read order and depth in "How it works".** Should the agent cite real snippets extracted by command, in the style of Willison's linear walkthroughs, rather than paraphrase from memory? The research favors extraction for accuracy.
4. **Risk tier definitions.** What makes a change low, medium or high in quantile? Money, data integrity and auth are candidates for automatic high.
5. **Interactive parity.** Should cc-sdlc's interactive sessions render the same template when CD opens a PR by hand, or only the factory?
