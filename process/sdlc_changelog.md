# SDLC Process Changelog

A living record of how the process evolves through real use. Each entry captures what changed, why, and where the change originated.

<!-- changelog-archive-pointer -->
> Older entries are in `changelog-archive/`, one file per quarter, moved there unedited once this file passed about 150 KB.

---

## Format

Each entry contains:
- **Date** — when the change was made
- **Origin** — what prompted the change (a session, audit finding, or observed friction)
- **What happened** — context leading to the change
- **Changes made** — numbered list of specific file changes
- **Rationale** — why the change improves the process

---

## Example Entry

```
## YYYY-MM-DD: [Brief Title]

**Origin:** [What prompted this — e.g., D7 planning session compliance audit, upstream sync]

**What happened:** [Context — what was observed, what problem was found]

**Changes made:**

1. **`[file path]`** — [what changed and why]
2. **`[file path]`** — [what changed and why]

**Rationale:** [Why this improves the process — the insight that led to the change]
```

---

## 2026-10-12: Debut the factory bundle: the software factory, promoted from quantile

**Origin:** the factory's rollout (`docs/current_work/ideas/software-factory_rollout-design.md`). The software factory incubated in quantile (F13): issue-driven agent stages from triage to a draft PR, on self-hosted runners, with CD approving every plan, merge and production step. Steps 1-3 made it installable: shared scripts, workflows rendered from a per-repository `factory.json`, and the `python-node` stack profile. Step 4 moves it into z-sdlc as an opt-in bundle, with its design rules promoted to a process doc (F22); step 5 adds the GitHub setup. CD decided (2026-10-12) that quantile keeps incubating it and z-sdlc imports it, and that a fix found in a project that installed the bundle goes straight into z-sdlc.

**What happened:** before the release, the bundle met quantile's live runs. D17, the first live rollback gate, found that the deploy check refused the factory's own job image under `.github/`. Moving the guard tests upstream found that a project without a production tier could publish no plan. Renaming the org's runner groups showed that a runner-group API update can empty a group's repository list. Smoke's stand-in service, httpbin.org, failed it for an afternoon. Each is fixed here.

**Changes made:**

1. **`bundles/factory/tree/`** — the factory's code as quantile has it (83 files): the scripts, guards, schemas, tool policies, sandbox settings, workflow templates, `render.py`, `workflow_policy.py`, the `python-node` profile, `bootstrap.py` and the tests. Installed at `.github/factory/` and refreshed on every migration. The guard tests use a sample CODEOWNERS and operations catalog, so they ship upstream; the publish guards treat a missing catalog as no production tier. `bootstrap.py` checks a repository's GitHub setup against Enablement and, with `--apply`, creates the labels, environments and runner-group entries (secrets, the App, CODEOWNERS and the ruleset stay report-only). Smoke's injection probes call `factory.json`'s `smoke.echo_host` instead of httpbin.org.
2. **`bundles/factory/seed/`** — what becomes the project's, written once where absent: `factory.json` (Endless Galaxy's shared defaults, including `smoke.echo_host`; the `stack` block is set per project), `planning.json`, `services.json`, `triage-policy.md`, a short `README.md`, and `tests/test_codeowners.py` (the project's CODEOWNERS against the guard). Not in the bundle: quantile's production tier (the broker, its operations and their tests), its host setup and its Django-specific database access list.
3. **`skills/sdlc-triage`, `skills/sdlc-implement`, `skills/sdlc-revise`** — the stage skills, made generic. Project specifics moved to the project's `.github/factory/triage-policy.md`; the App's login comes from `factory.json`, and commands and test services from the stack profile. An `sdlc-reviewer` pass found 7 major and 15 minor findings; two minors are left as follow-ups (the thread-reading rules repeated across the three skills, and where the sandbox paragraphs sit).
4. **`process/factory.md`** — D1-D5's rules, forbids, costs and revisit-when, the label set and Enablement. D4 rule 13: no infrastructure pattern applies under `.github/`, whatever a file there is called. D4 rule 16: without a production tier a plan has no gates, CD's included. Enablement names the shared runner group `factory-pool` and the per-project `factory-pool-<project>-prod`, gives the runner-group API's rule, and points steps 2 to 8 at `bootstrap.py`.
5. **`skeleton/manifest.json`** — `bundles.factory`; bundles may now carry `tree`, `seed`, `render` and `requires` (`skeleton/contract_changes.yaml` 0019; the debut is 0020). `sdlc-initialize` and `sdlc-migrate` install trees and absent seeds, run the render, hash tree files (never seeds) and offer an adopt path to a project that already has the tree. `process/path-mappings.md`, `process/commands.md`, `review-fix-loop.md`'s mirror table and `headless-mode.md`'s gate sites cover them.

**Proof:** installed into quantile, the bundle changes nothing and the workflow policy passes. Installed into an empty project with an Enablement-shaped CODEOWNERS, all 17 workflows render, the policy passes and every test passes (`zsdlc-import-factory --prove`). Quantile's live runs exercised the rest: smoke (all eight jobs, on the new echo host), a rollback gate that ended `rolled-back` as designed, and the generic triage and implement skills on a throwaway issue.

**Adapter action:** none; the bundle's files are code and settings, not knowledge-layer references (treat `bundles/factory/` like scripts).

**Rationale:** the factory is meant for every project (F22). Steps 1-3 left its project-specific values in a settings file and a stack profile, so the rest ships as one upstream copy. Release type: minor on its own (an opt-in bundle debut and additive manifest fields).

---

## 2026-10-12: Adapter fields and the improve route take the z-sdlc name [contract-change]

**Origin:** the rename to z-sdlc (entry below) left three names that other repositories store: two adapter fields and the improve loop's route value.

**What changed:**
- `process/adapter-lifecycle-protocol.md`, `process/knowledge-routing.md`, `sdlc-initialize`, `sdlc-migrate`: adapters mark themselves with `zsdlc_adapter` and declare `supported_zsdlc_version`. The pre-rename keys `ccsdlc_adapter` and `supported_ccsdlc_version` stay readable, and a migration that refreshes a project's adapter entry writes the new key and drops the old one.
- `sdlc-audit` improvement mode: the framework route and section are `z-sdlc`; factories and reports from before the rename call them `cc-sdlc`, and the two are the same route.
- `skeleton/contract_changes.yaml` 0018 records it.

**Adapter action:** declare `zsdlc_adapter` and `supported_zsdlc_version` (neuroloom-sdlc-plugin does as of this change). A factory that stores the route (quantile's improve loop) accepts both values in its schema and ledger.

**Rationale:** Every reader accepts both names, so an adapter or ledger written before the rename keeps working, and nothing has to change in lockstep. Release type: major, with contract 0017 in the same release.

---

## 2026-10-12: The framework is called z-sdlc everywhere

**Origin:** CD (2026-10-12): every cc-sdlc reference becomes z-sdlc. The `sdlc-*` skill and file names and "SDLC" stay.

**What changed:**
- Every skill, agent, process doc, template, knowledge file, bootstrap file and design doc names the framework z-sdlc (Z-SDLC in titles).
- The temporary clone paths are `/tmp/z-sdlc-bootstrap`, `/tmp/z-sdlc-lite-bootstrap` and `/tmp/z-sdlc-migrate`, and the source placeholder is `[z-sdlc-path]`. `sdlc-initialize` also accepts `/tmp/cc-sdlc-bootstrap` from a BOOTSTRAP.md copied before the rename, and looks for a local copy under both names.
- The framework-development skills are `zsdlc-audit`, `zsdlc-audit-adapter-installation`, `zsdlc-create-skill`, `zsdlc-ingest` and `zsdlc-research`.
- Unchanged on purpose: this changelog's past entries and the changelog archive (`archive --upstream` matches a project's copied entries by their dated headings, so those must stay as written), past `contract_changes.yaml` entries (append-only), and the old repository URL in `sdlc-migrate`'s `source_repo` rewrite. The adapter fields and the improve loop's route value are renamed in the next entry, with compatibility.

**Rationale:** One name for the framework in everything it installs. Projects get the new text at their next migration (direct copies). Release type: patch.

---

## 2026-10-12: The framework moved to endless-galaxy-studios/z-sdlc

**Origin:** CD moved the repository from `Inpacchi/cc-sdlc` into the Endless Galaxy Studios organization and renamed it `z-sdlc` for branding. The `sdlc-*` names inside stay.

**What changed:**
- `BOOTSTRAP.md`, `BOOTSTRAP-LITE.md`, `README.md` and the `.sdlc-manifest.json` template point at `https://github.com/endless-galaxy-studios/z-sdlc`, for cloning and for the raw bootstrap file.
- `skills/sdlc-initialize`: clones from the new URL, and looks for a local copy under the new name first (`~/Projects/z-sdlc`, `~/z-sdlc`, `../z-sdlc`), then the old one.
- `skills/sdlc-migrate` § 4.5 step 1a: a project whose `source_repo` names `github.com/Inpacchi/cc-sdlc` (HTTPS or SSH) gets it rewritten to the same form at the new home. Any other value, such as a fork or a local path, is left alone.

**Rationale:** GitHub redirects the old URL, but only until something takes the old name, and every install's manifest still names it. Migration fixes each project's record, so no project has to be edited by hand. A migration runs the project's installed `sdlc-migrate`, so the rewrite happens at the first migration after one installs this version; the redirect covers the time between. Release type: patch.

---

## 2026-10-11: Changelog archiving: project-only changelogs, quarterly archive files

**Origin:** CD decided the process changelog gets archived (2026-10-11) and chose all four parts of `docs/current_work/ideas/changelog-archiving_design.md`. [contract-change] (adapter exemption list; contract 0017)

**What happened:** cc-sdlc's changelog was 644 KB and nothing archived it. Every project's changelog started as a copy of it, so projects carried the framework's whole history plus their own (quantile 735 KB). CD chose: project changelogs hold only their own entries from now on; old entries move by calendar quarter once the file passes about 150 KB; a script does it; and existing installs are archived by their next migration without asking, which makes the release major. Then, seeing that quantile would keep 96 KB of copied cc-sdlc entries from July on: existing installs move every copied cc-sdlc entry out, whatever its quarter.

**Changes made:**

1. **`skills/sdlc-archive/scripts/changelog_archive.py`** (new; the first script shipped in a skill) — `archive` moves every entry dated before the previous quarter to `changelog-archive/YYYY-Qn.md` when the file is over the threshold, byte for byte and in its order, adds one pointer line, and writes nothing unless every entry is present exactly once across the files before and after. `check` fails when there's something to move and names the command. With `--upstream` (cc-sdlc's changelog and archive files), entries copied from cc-sdlc move too, whatever their date and the file's size; a copy is an entry whose `## YYYY-MM-DD: Title` line matches one upstream. `init` writes a new project's changelog: the header and one install entry. Splits on `## YYYY-MM-DD:` headings outside code fences. Tests: `tests/test_changelog_archive.py`.
2. **`process/changelog-archive/2026-Q1.md`, `2026-Q2.md`** (new) — cc-sdlc's own 203 entries from March to June, moved unedited. The live file is 171 KB with 46 entries (Q3 and Q4): over 150 KB, with nothing older than the previous quarter, so it stays until January. 15 old entries have no `---` before the next one; kept that way, so `release.yml` sees no old entry as new.
3. **`skills/sdlc-initialize/SKILL.md`** — Phase 1b writes the changelog with `init` from the source at `HEAD` instead of copying it; the archive is never installed; the changelog stays out of `installed_files`.
4. **`skills/sdlc-migrate/SKILL.md`** — §1.2 reads cc-sdlc's archive at the target tag when the project's version predates the live file; §1.3 rows for skill scripts (direct copy) and the archive (not installed, never overwritten); §2.1 copies `process/*.md` top level only and copies skill scripts; §2.1a ignores archive paths; new §4.5c runs `archive --upstream` (cc-sdlc's changelog and archive at the target tag) on the project's changelog every migration, automatically, so copied cc-sdlc entries leave and old quarters follow; back-fills skip never-overwrite files; the report lists what moved.
5. **`skills/sdlc-archive/SKILL.md`** — the inventory runs a dry run, the approval table gets a changelog row, step 8a runs it, and a red flag forbids moving entries by hand.
6. **`process/path-mappings.md`**, **`process/README.md`**, **`process/adapter-lifecycle-protocol.md`**, **`agents/sdlc-compliance-auditor.md`** — the archive is project-owned, never overwritten, never installed from cc-sdlc, and exempt from adapter transformation and the phrasing scan.
7. **`skeleton/manifest.json`** (the script listed; a not-installed note), **`skeleton/contract_changes.yaml`** (0017, `type: other`), **`CLAUDE.md`** (the consistency glob covers `skills/*/scripts/*.py`), **`.github/workflows/changelog.yml`** (new: the tests and `check`, on change and each quarter's first day; it never archives by itself), **`.claude/skills/ccsdlc-audit*`** (exempt lists; a project's changelog no longer holds cc-sdlc's entries).
8. **Paired adapter change:** `neuroloom-sdlc-plugin` `ddcc382` exempts `process/changelog-archive/*.md` in the transformer, the pattern rules, the post-operation audit and `sdlc-port`'s remapping.

**Rationale:** the framework's history belongs to cc-sdlc, where migration already reads it; a project's changelog is its own record. Moving whole quarters unedited keeps every entry findable by date, and a script that proves nothing was lost is safer than an agent copying 600 KB by hand. `release.yml` needs no change: it takes entries present now but not at the previous tag, and archiving only moves old ones. The one gap: an entry added after a tag and backdated into an already archived quarter would miss that release's notes.

---

## 2026-10-11: Migration never overwrites a project's changelog

**Origin:** sizing the changelog for archiving (CD asked for it to be archived, 2026-10-11). Every project's changelog turned out to be a full copy of cc-sdlc's history plus its own entries (quantile: all 199 cc-sdlc entries from March to May, and 54 entries of its own).

**What happened:** `sdlc-migrate` treated `process/sdlc_changelog.md` like any other process doc: a direct copy from upstream. Drift detection caught the project's edits, so on a tracked install every migration raised a hard three-way prompt over a file every project edits by design; on an install from before `installed_files`, the first migration had no drift data and would have copied over the project's own entries.

**Changes made:**

1. **`process/path-mappings.md`** — `process/sdlc_changelog.md` joins the Project-Specific Files (Never Overwrite) list.
2. **`skills/sdlc-migrate/SKILL.md`** — the changelog is excluded from direct copies (§1.3's table, §2.1's Step 0 and list); drift detection skips every never-overwrite file, since their edits are expected; new §4.5b prepends one entry recording the migration (version, the upstream entries applied, the project's decisions) instead of copying upstream entries; § Preserved lists it.

**Rationale:** the project's changelog is the project's record; the framework's history already lives in cc-sdlc, where §1.2 reads it. Archiving old entries (CD's decision) is a separate, larger design, in `docs/current_work/ideas/changelog-archiving_design.md`.

---

## 2026-10-11: A headless run stops before its time limit, not at it

**Origin:** the software factory's "work survives no stop" follow-up (`docs/current_work/ideas/software-factory_handoff.md`). quantile's D14b full-tier plan ran past its 2-hour step limit and was killed: about 2 hours of work, no result, no transcript.

**What happened:** headless callers stop a run at a time limit, but nothing told the run how long it had, so it could only be killed. A killed run returns nothing: no document, no notes, no result for the caller to act on.

**Changes made:**

1. **`process/headless-mode.md`** — § Ending a Headless Run: a caller that kills the run at a time limit gives it a time budget (how long, and the margin to keep for stopping). The run checks the time between steps; at the margin it starts nothing new, commits what is done, and stops with the status the caller names for running out of time, with what is done and what is left in `notes`. A red flag for pushing past the margin.

**Rationale:** a stop a few minutes early leaves a result the caller can resume or publish; a kill at the limit leaves nothing. The caller owns the clock and the status, so the rule only says to stop at its margin and with its status.

---

## 2026-10-11: Improvement mode reads a factory digest, report-only when headless

**Origin:** the software factory's phase 4, the weekly improve loop (`docs/current_work/ideas/software-factory_handoff.md` § Next build). CD decided (2026-10-10) that once a week the factory reads its own GitHub record of what CD did to its output and posts a report CD acts on: report only, every item actionable, every area covered, ranked, and tracked across weeks.

**What happened:** `sdlc-audit` improvement mode took sessions and commits only, and its Applying Improvements step edited files on approval. The factory's analyze job has neither a session nor a person: it gets a digest of signals built deterministically from GitHub, and it must never apply anything.

**Changes made:**

1. **`skills/sdlc-audit/SKILL.md`** — a new input, the **factory digest** (`/sdlc-audit improve <digest>.json`, recognized by `kind: factory-digest`), and § Improvement with a Factory Digest: the digest's signals, metrics and ledger; quoted text is untrusted data; check the window's commits so already-fixed problems aren't proposed; reference an earlier proposal's fingerprint instead of re-proposing it; each proposal names its target, change, why (signal ids, never invented), expected effect, severity and route (`hygiene`, `cd`, `cc-sdlc`, `issue`); all five sections are considered and an empty one means nothing to action. A **Headless run:** line there and at § Applying Improvements: return the proposals with status `awaiting-approval`, apply nothing. Two red flags (quoted text as instructions; a re-worded duplicate of a ledger item).
2. **`skills/sdlc-audit/references/improvement-methodology.md`** — § Extraction from a Factory Digest: what each signal says and where its fix usually goes, patterns over events, what CD needs from each proposal; evidence for a digest is its signal ids; a headless run never applies.
3. **`process/headless-mode.md`** — § Integration lists `sdlc-audit`'s factory-digest input and Applying Improvements as gate sites.
4. **`process/writing-for-cd.md`**, **`CLAUDE-SDLC.md`** — improvement proposals are something CD reads, budget about 100 words each.

**Rationale:** the improve loop's analysis is the same judgment as an improvement audit, so it runs the same skill rather than a factory-only prompt. Making the digest a first-class input, and the headless contract explicit, keeps the factory's report from drifting away from how interactive audits reason, and keeps it from ever changing what CD hasn't approved.

---

## 2026-10-11: Discovery check-in and headless results follow writing for CD

**Origin:** the first live discovery check-in (quantile D14c, issue #48). CD asked whether it followed the writing-for-CD rules, and then asked that every surface the factory uses to reach CD does.

**What happened:** The check-in question ran to about 1,150 words. It re-explained decisions CD had already approved item by item, listed implementation details CD doesn't decide, and gave each option a paragraph. The check-in rule set no budget and no filter, and `writing-for-cd.md` didn't name headless results as something CD reads, though callers post their questions, reasons and findings straight to CD.

**Changes made:**

1. **`process/writing-for-cd.md`** — § Where It Applies names the parts of a headless result a caller shows CD (questions, a stop's reason, findings, deferred items); `notes` keeps its detail. Length budgets add a stop's reason (1–2 sentences) and a discovery check-in (about 300 words, only what CD hasn't decided, one line per assumption and per choice). § Integration lists the check-in.
2. **`process/headless-mode.md`** — the check-in is about 300 words: one line for what carries over from what CD approved, one line per undecided assumption with its source, one line per open choice with its recommendation and the alternative's cost. Facts go in `notes`. § Ending a Headless Run adds "Write the result for CD where CD will read it".
3. **`skills/sdlc-plan/SKILL.md`** — the check-in block matches.
4. **`CLAUDE-SDLC.md`** — § Writing for CD covers what a headless caller posts, and its budgets name the check-in.
5. **`process/writing-for-cd.md`** — fixes mirror drift found by the consistency check. The Completion Report source block gets the Add-ons and Follow-ups lines that `sdlc-execute` and `sdlc-lite-execute` gained with add-ons (2026-10-09), so source and copies match again.

**Rationale:** a check-in CD can't read in a minute gets skimmed, which defeats the point of asking. Headless results are the factory's main voice to CD, so they get the same budget as everything else CD reads.

---

## 2026-10-10: Discovery check-in — a headless spec run can confirm its basis with CD before writing

**Origin:** the software factory's full-tier test (quantile D14b, issue #47), and CD's direction to have the spec stage ask its discovery questions.

**What happened:** Three D14b spec runs reached discovery. One stopped with a real question (live's late 5m bars break the parity bar under Rule C). The other two settled all of discovery from D11b's records, never asked, and wrote specs that didn't address that problem. The headless DISCOVERY-GATE counts questions the records already answer, so a run with rich history never stops. That drifts from the factory's decision (F18) that the full-tier spec stage has a discovery conversation with CD.

**Changes made:**

1. **`process/headless-mode.md`** — § The Rule adds the **discovery check-in**, a caller option and the one exception to "ask what blocks the next step, and no more". When the caller's prompt asks for one, `sdlc-plan` stops once with `needs-input`, after the DISCOVERY-GATE and FAR gate pass and before the spec is written. The stop carries one question, "is this the right basis for the spec?", listing the assumptions with their sources and the open choices with recommendations. It is not a batch, and it happens once per deliverable. The answered-question red flag names the exception, and § Integration lists the new gate site.
2. **`skills/sdlc-plan/SKILL.md`** — a **Discovery check-in** block as the last step before step 2, with its **Headless run:** line. The DISCOVERY-GATE's no-batching rule says the check-in isn't a batch. **Headless restart** gains a bullet (CD answered the check-in → apply it, start at step 2, never repeat it), and `notes` record whether it was asked and what CD answered.

**Rationale:** confirming the assumptions costs CD one reply, while a wrong assumption found later costs a whole spec run. It's opt-in, so callers that don't want the stop keep today's behavior. This is new contract surface (a caller option in the headless contract), so it's a minor bump when CD cuts a release.

---

## 2026-10-10: Production gates — fixes from the convention review

**Origin:** an `sdlc-reviewer` pass over the production-gates change (the entry below), the same day.

**What happened:** The new gate text left four gaps: lite execution still said it commits once; the review loop before a gate ended with step 2's hand-off to step 3, which would skip the rest of the plan; a plan with production work inside a phase (D11b's shape) had no stop at execution; and the interactive gate put a runbook and a question in one turn.

**Changes made:**

1. **`skills/sdlc-execute/SKILL.md`, `skills/sdlc-lite-execute/SKILL.md`** — the review before a gate emits its own REVIEW-GATE line and proceeds to the gate, not to step 3 (past the cap at CD's direction, with the open findings recorded); every loop's open minors and feedback go in the result doc; the gate is presented as a completed message before the question, and the report-back values are asked once it's done; a phase holding production work is triaged REVISE_PLAN and never dispatched; gate rows are never dispatched; the review after a gate starts at round 1. Lite: the per-gate commit uses step 4's format, and the "commits once" lines say so.
2. **`process/production-gates.md`** — no phase after a gate starts before it's done; approving a deploy gate authorizes deploying before Validated, and the deliverable stays In Progress; typed parameters defined; push the branch before a gate whose steps use `${head}`.
3. **`process/headless-mode.md`** — `production-gates.md` § At a Gate joins the gate-site list; the approval row says the next run receives the gate's result.
4. **`skills/sdlc-lite-plan/SKILL.md`, `skills/sdlc-plan/SKILL.md`** — reviewers check each gate in both; "catalog patterns".
5. **`templates/planning_template.md`** — the example gate sits between Step 2 and Step 3, matching its "After: Step 2".

**Rationale:** each gap would have shown up the first time a plan reached a gate: an execution ending early after the pre-gate review, or an older plan's deploy dispatched to an agent.

---

## 2026-10-10: Production gates — production work happens only in gates between phases

**Origin:** the software factory's gap 1 (`docs/current_work/ideas/software-factory_handoff.md` § Gaps). quantile D11b's plan mixed a deploy into a phase ("Phase 3: code + Deploy step 1"), so nothing running plans unattended could tell which steps needed production. CD decided the factory gets a production-capable runner with per-step approval; the framework half is the plan structure every project uses, with or without a runner. Cross-checked with a Fable advisor and Codex (`gpt-6-astra`, max effort).

**What happened:** Plans had no place for production work. It sat inside phases, where an execute run would either do it (a live-system change no headless run may make) or skip it silently. Execution's review loop also ran only after the last phase, so a deploy in the middle of a plan would have shipped unreviewed code.

**Changes made:**

1. **`process/production-gates.md`** (new) — what a gate is (production work between phases, done by CD or the project's production runner after CD approves, never by an agent); the gate section (runbook, report-back fields, rollback, optional `gate-ops` block); gates don't count toward the phase limit; the last item is a phase; a review loop and commit before every gate; interactive and headless behavior at a gate and after it; the optional operations catalog with its placeholders and two approvals.
2. **`templates/planning_template.md`, `templates/sdlc_lite_plan_template.md`** — a gate section between phases and gate rows in the Phase Dependencies table.
3. **`templates/result_template.md`, `templates/sdlc_lite_result_template.md`** — a Gates section: outcome, when, done by, report-back values.
4. **`skills/sdlc-plan/SKILL.md`, `skills/sdlc-lite-plan/SKILL.md`** — production work goes in gates; gates don't count toward the 7- or 4-phase limit; reviewers check runbook, rollback and report-back; the Approval Brief lists every gate. A red flag each.
5. **`skills/sdlc-execute/SKILL.md`, `skills/sdlc-lite-execute/SKILL.md`** — before a gate: the review loop over the work since the last gate, then a commit (lite commits once per gate). At a gate: interactive shows CD the gate; headless stops with `awaiting-approval`, the gate named in `stage` (and a `gate` field when the caller's schema has one). The headless restart after a gate records its result or stops with `needs-input`. The completion review covers the work after the last gate. Three red flags each.
6. **`process/headless-mode.md`** — a production gate is an approval gate whose action plan is the gate's steps; the execute skills' gate-site entries name it.
7. **`skeleton/manifest.json`, `process/README.md`** — the new process doc.

**Rationale:** Production work is the riskiest part of a plan and the one part an agent must never do on its own. Giving it a fixed place makes it visible at plan approval, approvable at the moment it happens, reversible by a stated rollback, and reviewable before it ships. The same structure serves a project where CD runs every gate by hand and one where a production runner does it after CD's approval. Release: minor (a new template structure and process convention, additive).

---

## 2026-10-09: Dependencies between deliverables, and splitting a deliverable

**Origin:** quantile D11. D11 split into D11a → D11b → D11c, but the split and the dependencies lived only in prose, so D11a dropped out of sight while D11b was planned against it (`docs/current_work/ideas/prerequisite-tracking_handoff.md`). The software factory also needed a split it could act on (`software-factory-gaps_design.md`, gap 2). CD approved building both together, cross-checked with Codex and Fable.

**What changed:**
- **Catalog:** a `Depends on` column in the deliverable catalog (`skeleton/manifest.json` template, `skills/sdlc-initialize` seed), with a Notes bullet on its format.
- **`process/deliverable_lifecycle.md`:**
  - **§ Dependencies:** where dependencies are recorded (the catalog column; a deliverable ID in a plan's Phase Dependencies row gates that phase), who fills them, and what checks them.
  - **§ Splitting a Deliverable:** split records, part rows, the parent as umbrella, one level only.
- **`templates/split_record_template.md` (new):** the document CD approves for a split. Its parts table carries name, tier, dependencies, a reused spec and scope.
- **`templates/planning_template.md`, `templates/sdlc_lite_plan_template.md`:** a phase's Depends On may name a deliverable.
- **`skills/sdlc-plan`:**
  - a § Splitting a Deliverable procedure (propose parts, write the split record, register the parts, approval; headless stops with `awaiting-approval` and the split record);
  - the Feasibility Gate and the phase limit point to it;
  - registration fills `Depends on`, and existing deliverables report unplanned prerequisites.
- **`skills/sdlc-lite-plan`:** uses an existing ID (a split part) instead of claiming one, fills `Depends on`, and reports unplanned prerequisites.
- **`skills/sdlc-execute`, `skills/sdlc-lite-execute`:** at load, run only phases no unfinished prerequisite gates. Interactive runs ask CD whether to continue; headless runs stop with `needs-input`.
- **`skills/sdlc-status`:** shows deliverables waiting on a prerequisite, split parents, and a **Forgotten Prerequisites** section.
- **`skills/sdlc-audit/references/compliance-methodology.md`, `agents/sdlc-compliance-auditor.md`:** flag missing IDs, cycles, Draft prerequisites of active work, and split parents without a split record.
- **`process/headless-mode.md`:** split approval is an approval gate, and the execute prerequisite stop is listed in § Integration.
- **`skeleton/contract_changes.yaml` and `skills/sdlc-migrate` §4.5a:** a new `catalog_column_added` entry type, and entry 0016, which back-fills `—` into existing catalogs.

**Release:** minor. New contract surface (a catalog column projects write, a new template and a new entry type), purely additive with a back-fill default.

**Rationale:** A dependency no tool reads is a dependency nobody sees. One column plus a few checks surfaces the three failures that bit D11: blocked work, execution starting before a prerequisite is done, and a prerequisite nobody is moving forward. A split record gives CD one document to approve, and gives the factory something it can act on.

---

## 2026-10-09: Add-ons finish small follow-ups; Follow-Up Items become issue-ready

**Origin:** CD, after the software factory's first executed plan (quantile D13) deferred two stale knowledge entries and left its follow-ups in the result doc. CD's direction: SDLC hygiene is part of the work, a quick follow-up is finished in the PR as an add-on, and anything else becomes its own issue and goes through triage. Cross-checked with Fable and Codex.

**What changed:**
- `skills/sdlc-lite-execute` and `skills/sdlc-execute`: an **Add-ons and follow-ups** rule.
  - **Add-ons:** small, no new decision, inside the touched area, dispatched and verified like planned work, listed in the result doc.
  - **SDLC hygiene:** knowledge entries or parking-lot notes the change makes wrong are corrected in the same deliverable.
  - **Everything else is a Follow-Up Item:** F-numbered, an issue-ready title, why not now. Nothing is dropped silently.
  - The PR body example's Scope gains Add-ons and Follow-ups lines.
- `templates/sdlc_lite_result_template.md` and `templates/result_template.md`: a new **Add-ons Beyond the Plan** section, and **Follow-Up Items** in a parseable checklist format (`- [ ] **F1: title**: what _Not now: why_`).
- `templates/pr_description_template.md`: Scope's Deferred line becomes Add-ons and Follow-ups. Follow-ups are a checklist CD can prune before merging.

**Rationale:** Follow-ups that live only in a result doc are forgotten, and tiny ones aren't worth an issue each. Finishing small ones in the PR and making the rest issue-ready lets a project (the factory does) file them automatically.

---

## 2026-10-09: Codex calls can't hang on stdin

**Origin:** A direct `codex exec` consult run from a background shell sat idle for 35 minutes. It printed "Reading additional input from stdin..." and waited for an end-of-file the open, empty pipe never sent.

**What changed:**
- `process/external-review-gate.md`: direct `codex exec` calls (no piped payload) end with `< /dev/null`, and the Task-Based Model Selection example shows it. The wrapper bullets list the new time limit and the stdin refusal.
- `templates/external-review.sh.template` and `templates/external-review-knowledge.sh.template`: refuse to run without piped stdin, and bound the codex call with `CODEX_TIMEOUT_SECS` (default 1800) through a portable `perl` alarm. A stall now skips the gate with a message instead of hanging.

**Rationale:** The wrappers always pipe a payload, so they were safe in normal use, but nothing stopped a background or ad-hoc call from waiting forever, and a stalled model call had no bound at all.

---

## 2026-10-09: Writing for CD — plain, short output in every session

**Origin:** CD, after the PR description standard landed: "I regularly find that I tune out because the agent is just so verbose and it just becomes information overload." CD wanted the PR's readability in every interactive SDLC session, and asked whether this belongs in the framework or in an installed output style.

**What happened:** Most of the overload was written into the skills themselves. Plan approval pasted the whole plan into plan mode (quantile's D13 plan is 12,020 words). The completion report's change list was required to be "exhaustive". Gate checklists and review rosters printed in full every time. An output style can't override that, and the docs confirm it doesn't reach dispatched agents. Only one style can be active, and CD already uses personal ones (Architect Mentor, and ELI5 Finance Mentor in quantile). So the fix goes in the framework, and personal styles stay a teaching layer on top. Mid-change, CD also dropped plan mode: "I generally close a session and start a new one to execute the plan."

**Changes made:**

1. **`process/writing-for-cd.md`** (new) — The standard for anything CD reads.
   - **Rules:** lead with what CD needs, plain language, say each thing once, evidence over claims, say where you're unsure, don't invent, keep to the budget.
   - **Length budgets:** status updates 1–2 sentences, end-of-turn summaries about 150 words, approval briefs about 450, completion reports about 500.
   - **Status blocks:** one line on the happy path, and a plain sentence before any findings table.
   - **Approval Briefs:** shown verbatim, then the path, in a message that ends the turn. CD's reply is the approval: the one approval asked without `AskUserQuestion`, now stated in `CLAUDE-SDLC.md` and `process/collaboration_model.md` too.
   - **Two mirrored blocks:** the Approval Brief procedure (`approval-brief`) and the Completion Report (`completion-report`). The procedure: the writing agent fills the brief's `###` headings with `Edit`, naming every decision CD approves; a fresh reader checks it; the manager counts its words. Both blocks are registered in § Mirrored Blocks and `process/project-section-markers.md`.
   - **Soft gates (a behavior change):** a FAR or FACTS gate that passes now prints one line and the run continues, where before every soft gate waited for CD. A failing one still waits (also in `process/input-quality-gates.md`). To restore the pause, revert that sentence in the two plan skills and the gates doc.
2. **`CLAUDE-SDLC.md`** — new § Writing for CD for every session. Key References lists the doc.
3. **Approval Briefs** — `templates/spec_template.md`, `planning_template.md` and `sdlc_lite_plan_template.md` gain a `## Approval Brief` section at the top.
   - `sdlc-plan` gains step 2a (spec brief) and step 5b (plan brief); `sdlc-lite-plan` gains step 4a. Each carries the `approval-brief` block; the process diagrams gain the new nodes, and the headless restart paths cover a plan change request.
   - Spec approval (step 3) shows the brief, the path and "To approve, reply approved" as a message of its own, and takes CD's reply as the answer. SPEC-REVISION re-runs step 2a after a scope change or pivot.
   - The lite plan's Definition of Done gains a seventh item for the brief.
4. **Plan mode removed** — `sdlc-plan` step 6 and `sdlc-lite-plan` step 5 are now "Present the Approval Brief".
   - The plan file is read, the brief is pasted verbatim, then the path and "start a new session and say: Execute the plan at …".
   - Approval is CD starting execution in a new session. `EnterPlanMode`/`ExitPlanMode` and the execution-prompt text are gone, from the skills and from `process/headless-mode.md` and `process/html-rendering.md` too.
   - The Read-then-paste rule against summarizing stays.
5. **Completion report** (`sdlc-execute`, `sdlc-lite-execute` step 5) — now the `completion-report` block:
   - the code variant of the PR template, with the same sections in the same order, bold labels for the terminal, What was built in place of What you're approving, What you need to do first and Commits last;
   - explicit always-present and left-out-when-empty sections;
   - critical or major findings CD directed past the cap shown under Review focus;
   - Scope integrity drawn from the deviation log and a diff of test and CI paths;
   - about 500 words, with the exhaustive file list kept in the result doc;
   - "Present the full commit" folded into the Commits line;
   - a PR opened from the report's sections in the template's PR form, after the fresh-reader check.
6. **One-line status blocks:**
   - pass lines for VERIFICATION-GATE (keeping the resolved library ID and how infrastructure was checked) and DISCOVERY-GATE;
   - FAR and FACTS pass lines (also in `process/input-quality-gates.md`);
   - REVIEW-GATE as one line, without repeating the roster;
   - review rosters and plan revision dispatches as one line instead of checkbox lists, in `process/review-fix-loop.md` Step A and both plan skills. The count-must-match rule now counts names.
7. **`process/finding-classification.md`** — one plain sentence before the Classification Table.
8. **`templates/pr_description_template.md`** — the general rules now live in the writing standard. A plan or spec PR's description is the document's Approval Brief. `process/headless-mode.md` fills a caller's PR fields from the brief.
9. **`process/collaboration_model.md`** § Completion Reports, and `sdlc-lite-execute`'s description — updated to match.
10. **`skeleton/manifest.json`** — lists `process/writing-for-cd.md`.

11. **Quality gate** — `sdlc-reviewer` ran on the four skills in two parallel passes and found 0 critical, 7 major and about 35 minor findings and nits. All majors were fixed:
   - the brief's heading level (it must stay `###`, or the word count and the shown brief break);
   - the `sdlc-plan` diagram;
   - the report's empty-section rules;
   - the PR/report shape and order;
   - open critical findings in the report;
   - the duplicated report and brief procedure, now mirrored blocks.

   Most minors were fixed too: stale "checklist" wording, restart paths, the approval exception, the FAR metric, the VERIFICATION-GATE one-liner, and the red flags. Not fixed, because they predate this change: skill size, `sdlc-plan`'s Integration labels, `sdlc-review-code`'s own dispatch checklist, and the diagrams' missing step 5 node in the execute skills.

**Rationale:** CD approves and steers from what the agent shows, and a wall of text gets skimmed: an approval CD couldn't follow isn't an approval. The documents agents work from keep their detail; only what CD reads gets shorter and plainer. Briefs come from the document's author and are checked by a fresh reader, so the manager never paraphrases, which was the reason for the old verbatim-paste rule. Release type: minor (a new cross-skill convention and new skill steps).

---

## 2026-10-09: A reviewable PR description standard

**Origin:** `docs/current_work/ideas/pr-description-standard_handoff.md`. The software factory opened its first plan PR (quantile #31, the D13 plan for issue #30). CD couldn't approve it: "It doesn't really feel right for me to read and approve something that I don't understand."

**What happened:** The plan is written for the executing agent: exact functions, file lines, test fixtures. That is the right content for the agent's contract and the wrong document for CD's approval, and the PR body inherited the same voice. Every PR that asks CD to approve agent-written work has this problem, interactive or factory-made. cc-sdlc had no PR-description guidance at all.

**Changes made:**

1. **`templates/pr_description_template.md`** (new) — The standard, with a plan/spec variant and a code variant.
   - **Fixed sections, in order:** The problem; What changes for users; What you're approving (numbered decisions, each with the alternative it rejects, plus any scope beyond the issue); Scope (tackled, not tackled, deferred); Risk (tier, top risks, undo); Review focus; How it will be verified; How it works (the approach and why it is shaped that way); Learn the change (files in reading order with their roles, and concepts); then a collapsed agent record. Each section has a word share.
   - **Code variant:** How it was verified shows results, not intent. It adds Scope integrity and Deviations from the approved plan (omitted for a direct fix). Open critical or major findings go under Review focus, in plan PRs too.
   - **Rules:** plain language, with code names only where they help CD find or check something. About 450 words above the agent record for a plan, 500 for code. Say each thing once. Evidence over claims. Don't invent: an empty list is fine. Line-level explanation stays in code comments. Headless fields are plain sentences, because the caller renders the formatting.
   - **Fresh-reader check before opening:** a reader given only the description and the plan or diff must be able to explain the change, and every statement must match its source.
   - **Risk tiers:** high, medium and low, decided by what valid use gets and whether a revert undoes it, with the highest fitting tier winning. Each project lists its always-high areas in its own `PROJECT-SECTION` block.
   - **Examples:** a complete plan PR from quantile #30 (D13), and the code-only sections for the same change.
2. **`CLAUDE-SDLC.md`** — new § Pull Request Description: every PR that asks CD to approve agent-written work follows the template, whether a person or the factory opens it. Key References names the template.
3. **`process/headless-mode.md`** § Ending a Headless Run — when a caller's schema has PR-description fields, fill them per the template, never pasted from the plan. Integration lists the template.
4. **`skills/sdlc-plan`, `skills/sdlc-lite-plan`** (Output) — when the spec or plan is approved through a PR, its description follows the plan variant. The plan file is unchanged.
5. **`skills/sdlc-execute`** step 4 item 8 and **`skills/sdlc-lite-execute`** step 4 — a PR carrying the work follows the code variant: deviations come from the result doc, and verification shows the build and test results.
6. **`skeleton/manifest.json`** — lists the template. `sdlc-migrate` §2.1 already direct-copies every manifest-listed template and preserves `PROJECT-SECTION` blocks, so it needs no change.

**Rationale:** CD approves through the PR and, as CD put it, reviewing PRs "is going to be the predominant way in which I look at the code in the first place." So the PR has to say for sure what is being approved, why, at what risk and with what proof, and leave CD understanding the codebase better. The research behind the sections is in the handoff: Google's CL descriptions and Bacchelli & Bird on the why; Willison, Osmani and Phabricator test plans on evidence; Osmani, Atlassian and Kubernetes on review focus; Spotify Honk and GitHub's agent-PR guide on scope integrity; the Rust RFC guide-level explanation and PEP "How to Teach This" on learning. CD overrode Google's "explanations belong in code comments" for the approach-level "How it works". Line-level explanation still goes in comments. A Codex cross-check (gpt-6.1-sol) before building shaped four choices: one file map rather than separate read-order and key-file lists, a fresh-reader check, "don't invent" for lists that can be empty, and risk tiers by reversibility. Release type: minor (a new cross-skill convention).

---

## 2026-10-09: Headless runs dispatch agents in the foreground

**Origin:** The software factory's first live lite-plan run (quantile #30) ended after 4 minutes. The Agent tool launched the plan writer in the background by default. The orchestrator ended its turn to wait for it, and the run closed with the plan unwritten.

**What changed:**
- `process/headless-mode.md` § Ending a Headless Run: every agent is dispatched in the foreground, and the run waits for its result. Callers switch background launches off in the runtime (`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`). Added a Red Flags row.

**Rationale:** A headless run ends with the orchestrator's turn. This was already a rule in the factory's `sdlc-implement` skill; every headless skill that dispatches agents needs it.

---

## 2026-10-08: Headless mode — the rule for running skills with no person present

**Origin:** Software-factory handoff (`docs/current_work/ideas/software-factory_handoff.md`), phase 2 prerequisite "Headless rule". Decision F13 made it a cc-sdlc framework change from the start, ahead of the opt-in `factory` bundle. Phases 0–1 now run `/sdlc-triage` unattended on a self-hosted runner in quantile, and phase 2 will run implementation skills the same way.

**What happened:** Every skill assumed CD was present. Questions went through `AskUserQuestion`, spec approval waited for CD, plan approval went through `EnterPlanMode`/`ExitPlanMode`, phase triage SKIP/REVISE_PLAN waited for confirmation, and the review-loop round cap escalated through `AskUserQuestion`. Under `claude -p` with `--permission-prompts none`, `AskUserQuestion` does not exist, and nothing said what a skill should do instead. The likely failure was guessing past a gate or approving its own work to keep going. The framework had never defined a headless run (the evaluation's Explore pass: "the framework has never run headless").

**Changes made:**

1. **`process/headless-mode.md`** (new) — The rule.
   - **Detection:** a line starting `SDLC headless mode:` in the caller's prompt or appended system prompt (primary). The phrase quoted in the rule, `CLAUDE.md` or a skill doesn't count. Fallback: no ask-the-user tool can be used — neither `AskUserQuestion` nor the harness's equivalent (OpenCode's `question`) is available or loadable, or a call to it is denied without an answer. A deferred tool counts as available.
   - **Subagents:** a dispatched subagent is never headless itself. In a headless run the orchestrator says so in every dispatch prompt, so the limits bind the subagent.
   - **The rule:** every point that needs CD stops the run, and nothing is guessed, defaulted, self-approved or skipped. Seven kinds of point:
     - a question the next step depends on → `needs-input`;
     - a bounded loop that ran out without meeting its bar (review round cap, a FIX that failed twice — not reclassified headless: the run stops and CD decides where it goes — the External Review Gate's fix-round limit, debug-incident T6, the tests-run round limit) → `escalated`;
     - an approval gate (spec, plan mode, or an action plan such as `sdlc-archive`'s archive set or `sdlc-migrate`'s change plan) → save it and stop with `awaiting-approval`. An action plan goes in the result in full, never call `EnterPlanMode`/`ExitPlanMode`, and the next run executes exactly what was approved or stops again;
     - a soft gate (FAR, FACTS) → continue on a pass, stop with `needs-input` on a fail;
     - a question the next step doesn't depend on (PRE-EXISTING findings, minor PLAN findings) → list it under `deferred` and continue. A critical or major PLAN finding stops, because deferring it needs CD (manager rule);
     - an optional offer → take the no path and list it under `skipped`;
     - confirmation of local, reversible work (committing the skill's own output, even when framed as optional) → proceed.
   - **Answered questions are not gates:** a question the prompt or thread already answers doesn't stop the run. Skill pacing rules still hold, and work done before the stop stays.
   - **Outward actions go to the caller:** no side effect outside the working tree. That rules out push, PRs, comments, labels, publishing, messages, external sends and live-system changes, and github-provenance checkpoint writes (their local half still runs, and their GitHub half becomes a rendered `outbound` entry). Reads from anywhere are fine (Context7, web search, `gh` reads, an upstream fetch), and writes to the project's configured knowledge backend count as local. The External Review Gate runs only against a local model or a durably authorized hosted provider. Each skipped action is listed under `outbound`, unless the caller's prompt names it.
   - **Ending:** a stop is a result, so the run ends its turn normally. The run can't set its own exit code, so the status carries the outcome. `failed` with a `reason` is for a precondition the caller must fix.
   - **Result format:** a skill's own closing report comes first and the result last. With `--json-schema`, the caller's schema is the contract; any field it lacks (`notes`, `deferred`, `skipped`, `outbound`) goes into the stage's saved document under `## Headless Result`. Otherwise the run ends with a `## Headless Result` block: status, stage, reason, questions, findings, documents, deferred, notes, skipped, outbound.
   - **Restart, not resume.** A skill whose restart from step 1 would repeat a side effect or lose counted state carries a **Headless restart** paragraph in its entry step. It skips work already done, never registers the deliverable twice, and keeps counting completed phases, review rounds and the frozen roster.
   - **Kept out of core:** factory specifics (labels, markers, writer jobs, approval by merging the doc PR).
2. **Every skill in `skills/`** (27) — Carries the `headless-stop-rule` mirrored block verbatim, inside `MIRROR` markers.
   - **Placement:** directly after the `**AskUserQuestion mandate:**` paragraph where a skill has one (`sdlc-plan`, `sdlc-lite-plan`, `sdlc-execute`, `sdlc-lite-execute`, `sdlc-tests-create`, `sdlc-create-reference-doc`, `sdlc-debug-incident`). Otherwise, before the first `##` section.
   - **Coverage:** every skill carries it, including skills that never ask anything, so choosing consumers takes no judgment. Project skills may carry it too.
   - **How it was done:** copied by script from the source. The audit's drift check reports no drift across all 33 mirrored copies: 27 headless and 6 review-loop.
   - This follows the 2026-05-19 lesson that a pointer alone gets skipped.
3. **Gate-site lines** (outside the mirrored block):
   - **`sdlc-plan`:**
     - step 0 **Headless restart**: skip registration and finished steps, and never mint a second D-number. Spec approval → set Ready and start at 3d, or stop again if the spec changed since. Spec feedback → the SPEC-REVISION block in step 3. A discovery answer → the DISCOVERY-GATE in step 1. DECIDE answers, a FACTS decision or an escalated review → step 5 at the recorded round with the frozen roster. `notes` carry the D-number, complexity, worktree, agent list, prior context and ADR constraints, playbook match, review round, roster and open findings.
     - DISCOVERY-GATE: answered questions count toward the minimum; on a FAIL, stop with the single most blocking question.
     - FAR and FACTS: continue on a pass, stop on a fail.
     - step 3 spec hard gate: `awaiting-approval`.
     - step 6: skip 6a–6c and stop with `awaiting-approval`. "Follow these sub-steps in exact order" is now labelled **Interactive run**, as is the step's opening line.
     - Output section and a red flag.
   - **`sdlc-lite-plan`:** step 0 **Headless restart** (never a second ID or plan file; resume at FACTS or review with the recorded round and roster), step 5 (the same as step 6), FACTS (pass = every phase meets the thresholds), the summary line, the Output section, and a red flag.
   - **`sdlc-execute` and `sdlc-lite-execute`:**
     - step 0: no plan → `failed` with the reason. A **Headless restart** paragraph reads the plan, partial result doc and notes, skips completed phases, and continues the review round count with the frozen roster.
     - PRE-GATE "Triage ≠ BUILD": stop with `needs-input`, giving the phase, SKIP or REVISE_PLAN, and the reason.
     - Completion Report: the Headless Result follows it as the last output.
     - `sdlc-execute` step 4: no push or PR, both listed under `outbound`.
   - **`sdlc-handoff`:** step 7 commits the handoff locally without asking (when the project commits SDLC docs), never pushes; the "Always ask" red flag is scoped to interactive runs.
4. **`process/review-fix-loop.md`** § Round Cap — New headless bullet:
   - at the cap with a critical or major finding open, save the partial result doc and stop with `escalated`;
   - DECIDE and unresolved INVESTIGATE findings stop with `needs-input`;
   - a FIX that fails twice is not reclassified and stops with `escalated`;
   - PRE-EXISTING and minor PLAN findings go under `deferred`, and a critical or major PLAN finding stops with `needs-input`.

   It sits outside the `MIRROR-SOURCE` blocks, so the six review-loop copies are unchanged. The Step C "FIX failure escalation" line and the § Round Cap closing line, plus **`process/finding-classification.md`** § FIX Failure Escalation, say a headless run stops with `escalated` instead of reclassifying.
5. **`process/html-rendering.md`** § Post-Skill Offer — Headless runs take the no path and list the offer under `skipped`.
6. **`process/external-review-gate.md`** § Data egress — In a headless run without durable authorization, hosted-model runs are skipped and listed under `skipped`. A local model or a durably authorized provider runs as usual. The opening list of sanctioned reasons to skip a configured reviewer now includes this one.
7. **`process/github-checkpoints.md`** — New § Headless Runs. The run never writes to GitHub itself, and each checkpoint splits in two:
   - **Local half (still done):** when the issue is known (named in the caller's prompt, or already recorded in an earlier artifact's frontmatter or the catalog's linked ID cell), CP-1 writes `github_issue:` (and `github_board:`) into the first artifact's frontmatter and the catalog ID cell as a link. The ⎘ checkpoints commit their artifact locally under § Commit Conventions, without pushing.
   - **GitHub half (handed to the caller):** each checkpoint, and `sdlc-archive`'s parked-issue closure, adds a rendered entry to `outbound` in firing order. The fields are `checkpoint`, `deliverable`, `issue` (or `new <repo>` for CP-1 or CP-12), `title`, `labels`, `type`, `parent`, `board`, `board_add`, the whole rendered `comment`, `status` (column name and rank, or `—`), `write_if` (the floor rule, or CP-S2's exact match), `close` (`completed` or `not planned`, set only when the skill's closing conditions hold), `needs_push` (the commits the links need, and the branch), and `note`. A `ranks` item travels inside `outbound`: it includes the `never_write` columns above every SDLC rank, an empty Status is rank 0, and an unmapped column means skip the write, so a caller can never move a card backward.
   - **Caller order:**
     - **Push** the linked commits unchanged. A `git bundle` keeps the SHAs; a re-applied patch breaks the links, but the comment still posts. CP-10 waits until the moved files are on the default branch, by any merge method.
     - **Find or create the issue:** search open and closed issues for the `Dnn` title prefix and link a match before creating; create with title, labels, type and the comment as body in one call, then link the parent sub-issue. Under rule 4, `issue: new` carries candidate repos in `note`, and the caller waits for CD to name one.
     - **Board add, then comment** (skipped when the comment was the new issue's body).
     - **Status:** write only if `write_if` holds, using `ranks`.
     - **Close last:** skip it if the issue is already closed or an earlier entry for the same issue failed; CP-10 waits until the moved files are on the default branch, by any merge method, and closes only after its main-branch links resolve. The `sdlc-archive` fragment's checklist executor gains a headless line: its GitHub rows are earlier entries for the same issue.
   - **Missing links are caught up:** any later headless run whose prompt names the issue writes missing links before its own work, including a restart that skips registration and a lite deliverable's first execute run. The rule lives in the six fragments' activation lines, not in core skill text, so projects without the bundle never see it.
   - A handed-off checkpoint is not a failure: no miss-log entry and no notice; reconciliation sees the gap if the caller drops it. CP-11b never fires headless. The caller may hand checkpoint writes to the run; if it does, CP-11b's offer takes the no path and repo selection rule 4 skips that one checkpoint (listed under `outbound`) rather than stopping the SDLC step, so the never-block invariant holds.
   - **`bundles/github-provenance/fragments/{sdlc-plan,sdlc-lite-plan,sdlc-execute,sdlc-lite-execute,sdlc-handoff,sdlc-archive}.md`:** the activation gate line says that in a headless run each checkpoint does only its local half and hands its GitHub half to the caller as a rendered `outbound` entry, unless the caller hands checkpoints to the run.
   - The first draft simply skipped checkpoints and listed only the CP id and D-number. CD asked for the two changes above, because the factory's writer job doesn't know the checkpoint recipes, so the provenance trail would have gone dark for every headless run. A review of the split found five majors, all fixed before landing: the `ranks` map omitted `never_write` columns (a backward write over the deploy pipeline), creation skipped the `Dnn` duplicate search, nothing wrote the CP-1 links once a caller created the issue, the entry lacked `type`, `board` and `parent`, and CP-10's main-branch links and close were unguarded. Round 2 found no majors; its seven minors were fixed and re-reviewed. Round 3 (the cap) found no critical or major findings, and its four wording minors were applied after the cap without re-review.
8. **`CLAUDE-SDLC.md`** § Use AskUserQuestion for All Questions — A self-contained headless paragraph, matching the mirrored block: detection, subagents, stop and end normally, never guess or self-approve, deferred questions, no path on offers, no actions outside the working tree unless the caller names them, answered questions aren't gates. It points at the process doc.
9. **`process/project-section-markers.md`** § MIRROR Markers — Lists the headless stop rule as a user. New rule 6: prose never spells a live marker. A source doc describes its markers with `{id}`, and a skill never writes the copy-marker form with a file name. The drift check matches marker text, and both forms produced false drift while this change was drafted:
   - `headless-mode.md`'s own Markers paragraph made all 27 copies report drift;
   - `sdlc-develop-skill`'s authoring bullet made that skill report drift.
10. **`skills/sdlc-develop-skill/SKILL.md`**, **`.claude/skills/ccsdlc-create-skill/SKILL.md`** — All-types required sections now include the headless stop-rule block: its marker label form, placement and scope, the fact that no mirror-table row is needed, when a gate gets its own **Headless run:** line (its stop needs stating at the gate: status, payload, a skipped step, or an outward action), and a **Headless restart** paragraph for skills that can be restarted. In a target project the § Integration list is upstream-owned, so `sdlc-develop-skill` proposes the entry upstream instead of editing it. `sdlc-develop-skill` also:
    - CREATE step 1.5 (item 4) and MODIFY M1.5 exempt `MIRROR` blocks from extraction. Without the exemption, its DRY audit would recommend reducing the now-universal block to a pointer.
    - M2 gains a "Inside a `MIRROR` block → source-doc change" row: propose the change upstream, never edit the copy.
    - New red flag: "never asks anything, so the headless block is noise".
11. **`process/skill-agent-review.md`** § Required Sections — Mirrored blocks: the headless stop rule in every skill, and the review-loop block in loop-bearing skills.
12. **`agents/sdlc-reviewer.md`** (`.claude/agents` is a symlink to `../agents`) — The mirrored-block drift check names `headless-mode.md` § Mirrored Stop Rule (which lists every skill) beside the review-loop table.
13. **`.claude/skills/ccsdlc-audit/references/compliance-methodology.md`** — Dimension 10 check 5 names both mirror sources and adds a one-line completeness check: `grep -L 'MIRROR-START: headless-mode.md#headless-stop-rule' skills/*/SKILL.md` must print nothing.
14. **`process/README.md`**, **`skeleton/manifest.json`** — `headless-mode.md` registered: a Shared Behavioral Protocols row, and an entry in `source_files.process`.

**Review:** round 1 ran three `sdlc-reviewer` passes (`sdlc-plan`; `sdlc-lite-plan` + `sdlc-develop-skill`; the two execute skills) and one cross-framework consistency review. There were no critical findings. All majors were fixed:
- the skip-vs-"do not skip any sub-step" contradiction;
- no restart entry in `sdlc-plan`;
- the DISCOVERY-GATE unanswerable headless;
- the lite-execute line citing a triage table lite never produces;
- OpenCode's ask tool tripping the fallback;
- an outward-action ban too narrow, missing live-system changes, egress and subagents;
- no `failed` status;
- unsaved action plans approved by question.

Round 2 (three fresh reviewers) confirmed every round-1 fix and found three new majors, now fixed: (1) a twice-failed FIX had three different outcomes across the docs, one of which let a critical finding be deferred; (2) `sdlc-lite-plan` had no restart entry, so a restarted run would mint a second D-number; (3) both execute skills had no restart entry, so a restarted run could redo finished phases and reset the review round count. Round-2 minors were fixed in the same pass: the `failed` status was added to the mirrored block, reads were allowed explicitly, schema fallback now covers every field, the commit-confirmation rule was settled, the external gate's sanctioned-skip list was updated, the gate-line criterion was stated once, and the § Integration list was completed. Round 3 (two fresh reviewers, the cap) found no critical or major findings. Its ten minors were applied after the cap and checked mechanically, not re-reviewed: twice-failed-FIX qualifiers in `review-fix-loop.md` and `finding-classification.md`; the restart-paragraph scope narrowed to skills whose restart from step 1 would repeat a side effect or lose counted state; `sdlc-plan` records the spec's content hash for the unchanged-since-approval check and splits the FAR, FACTS and review restart cases; `sdlc-lite-execute` restart notes reflect its single step-4 commit; `sdlc-handoff` step 7 commits locally headless. Known open item: the plan → execute hop has no unchanged-since-approval guard for the plan (a design question for the approval row). Pre-existing findings were left alone. These include `sdlc-plan`'s Integration structure, skill length, the `§3c` references, sibling drift between the execute skills, bare paths in `sdlc-develop-skill`, and the Manager Rule copies.

**Not changed:**
- The `code-review-mechanics` and `plan-review-mechanics` blocks still say "escalate to CD via `AskUserQuestion`". The mirrored stop rule and the § Round Cap bullet cover headless runs, and editing those blocks would mean re-copying them into six skills.
- Parking a draft PR at the review cap with `factory:review-capped`, the labels, the markers, the writer-job split and the per-stage output schemas are factory concerns. They stay in quantile until the `factory` bundle.
- No `contract_changes.yaml` entry: the new process doc is a direct copy and the rest are in-place edits, so no migration behavior is needed.
- Neuroloom: no new knowledge-layer references, so this is not a contract change.

**Versioning:** a new cross-skill process convention, so this is a **minor** bump at the next release. No tag was cut.

**Rationale:** The factory is the first caller, but the gap is general. Any unattended run (CI, a scheduled job, `claude -p`) reaches the same gates. Stopping cleanly with a structured result does three things:
- keeps CD's decisions with CD;
- lets a caller tell "needs CD" from "broke";
- gives the next cold run what it needs to continue.

The rule sits in core with a mirrored line in every skill, not only a pointer, because pointer-only guardrails have been skipped before.

---

## 2026-10-06: Unify and bound the review loops — one severity scale, mechanical re-review, critical/major exit bar, 3-round cap

**Origin:** A software-factory and cost evaluation session measured 30 days of Claude Code usage (local transcript token counts to 2026-10-06, priced at API list rates — on the Max plan this is usage limits and waiting time, not dollars). About $16.3k equivalent in total; subagents were 67% (~$10.9k) and 95% of all cost was re-reading context. Review and re-review were ~3,008 of 4,775 subagent dispatches and ~$5.1k — 47% of subagent cost. Median review checkpoint roster 7 reviewers (p90 12, max 15); rounds labelled up to 23 (469 dispatches in rounds 3–5, 224 in rounds 6–10, 183 in round 11+); 60–75% of reviewers reported findings in every round bucket, and hand-sampled late-round reports were nearly all self-described minor. Fable and Codex (GPT-6-Astra, `ultra`) ruled independently on proposed changes (consult record: `docs/current_work/ideas/review-loop-unification_consult-record.md`); CD decided D1–D14 (`docs/current_work/ideas/review-loop-unification_handoff.md`).

**What happened:** The loop had no termination guarantee. The exit bar was zero findings with minors included; the 3-strike rule only fired when the *same* finding category repeated, so a loop surfacing a different minor each round never stopped. Every fix sent the whole roster back ("not just the ones who found issues"), rosters never shrank ("do not remove agents", "When in doubt, include"), and AOP5 right-sizing was cited only by the plan skills. There was also no single severity definition: `finding-classification.md` was planning-shaped (critical = "changes the approach"), the impact × likelihood calibration and the dedup table lived only in `sdlc-review-code`, and `sdlc-create-reference-doc` used its own CRITICAL/HIGH/MEDIUM/LOW scale. History: the 2026-04-14 audit attributed 63% of token cost to review-fix; 2026-05-12 removed `team-review-fix` as underused; 2026-05-19 ("Inline Critical Guardrails Lost in Skill Consolidation") restored inline loop steps after a pointer-only consolidation let `sdlc-review-code` skip the loop and falsely claim it clean — which is why this change keeps the loop steps inline as verbatim mirrored blocks instead of reducing skills to pointers.

**Changes made:**

1. **`process/finding-classification.md`** — Now owns the shared definitions for every review loop. § Severity Levels replaced: impact × likelihood scale (critical = certain/very likely data loss, breach, or complete failure; major = significant, likely to manifest; minor = partial/workaround/cosmetic) moved from `sdlc-review-code`, with a per-context reading of "impact" (software / implementation-as-written / reader). New § Severity Calibration (calibrate before labelling; never a lever for exiting a loop). New § Scope-Change Marker — a `Scope change` yes/no column in the planning-context Classification Table (fix changes the approach, adds/removes files, or changes a phase/agent assignment); plan re-review trigger (1) reads it (D9, D12). New § Finding Deduplication — the four-row merge table moved from `sdlc-review-code` Step 4, applied before classification everywhere. New § Open Minor Findings — table shape, where it lives per context (result doc / Fix Summary / plan file / commit message), only CD closes entries. Context table: stale "Post-commit fix (review-fix)" row retitled to code review fix (`sdlc-review-code`, direct dispatch); reference-doc row added. Kept: FIX Failure Escalation (fails twice → INVESTIGATE/PLAN) and Low-Severity In-Scope Findings (Planning Context).
2. **`process/manager-rule.md`** — § No Unilateral Finding Demotion: listing open minor FIX findings at loop exit, visible to CD, is permitted and not demotion; closing them still requires CD; downgrading severity to meet the exit bar is demotion.
3. **`process/review-fix-loop.md`** — Now owns the loop for every review context. Overview rewritten. Step A: the "do not remove agents… dispatch every single one" rule replaced by the first-round roster rule (code-reviewer + software-architect plus one reviewer per touched domain; "when in doubt" covers domains, not headcount; beyond five each extra agent states what it uniquely adds, AOP5; MTS4 high-risk domains always get their specialist; lenses are never trimmed). Context-separation rule kept, plus **fresh reviewers every round — no reuse** and what re-review prompts carry (prior findings table, fix diff, read current code, look for regressions, a clean report is acceptable). Step B: "Zero means zero" replaced by § Exit Bar. Step C: dedup → calibrate → classify; fix critical and major each round, minors accumulate for one batched pass; a non-mutating **pre-fix snapshot** — a tree hash written through a throwaway copy of the index (`GIT_INDEX_FILE=<tmp> git add -A && git write-tree`), taken again after the fixes — feeds the file-set comparison and the fix diff (verified in a scratch repo: the real index and working tree are untouched, and edits to untracked files are caught; `git stash create` was tried first and rejected because it omits untracked files, so fixes to newly created code or docs would be invisible); FIX failure escalation cross-referenced. Step D: "dispatch ALL agents — not just the ones who found issues" replaced by the mechanical rule (re-run the verification gate; full roster if any applied fix was critical/major or touched files go beyond the findings' files, otherwise raisers + code-reviewer + software-architect scoped to the fix diff; new domain adds its reviewer). Step E: external findings deduplicated and calibrated with internal ones; every internal round they re-open counts toward the cap; the gate's own 2-round cap kept, whichever limit hits first. New § Exit Bar (no critical/major open, no INVESTIGATE/DECIDE unresolved, minors have had their batched pass) and § Round Cap (3 rounds, every round counts; escalate via `AskUserQuestion` with the open-findings table when critical/major remain; exit with Open Minor Findings when only minors remain) — **replaces the 3-strike rule**. New § Plan Review (no verification gate; one revision dispatch per round; re-review fires on the scope-change marker, Files-list change, or phase/agent change — exactly today's cases — and always dispatches the full step-1 roster; an unreviewable round-3 revision escalates). New § Mirrored Critical-Steps Blocks with the two source blocks (`code-review-mechanics`, `plan-review-mechanics`) and the consumer table. § Skill-Specific Variations rebuilt as a per-context table (execution, review-code — whose Step 3 dispatch is round 1 — direct dispatch, plan review, reference-doc review); the stale `sdlc-review-fix` row removed; lite and full run the identical loop.
4. **`process/project-section-markers.md`** — New § MIRROR Markers: `MIRROR-SOURCE-START/END: {id}` in the source doc, `MIRROR-START/END: {doc}.md#{id}` in skills; byte-identical content; exempt from DRY extraction; not migration markers (`sdlc-migrate` matches only the literal `PROJECT-SECTION-*` / `BUNDLE-SECTION-*` names, so mirror blocks pass through as upstream content). Validation section: `sdlc-reviewer` checks mirror blocks against their source.
5. **`skills/sdlc-execute/SKILL.md`, `skills/sdlc-lite-execute/SKILL.md`** — Inlined loop steps replaced by the mirrored code-review block; Step 0.5, self-applied-fix note, Triage output format, plan contract briefing, and the External Review Gate paragraph kept outside it. Exit announcement now "Review loop complete — no critical or major findings open (N open minor findings listed)"; step 3 is reached under the exit bar; open minors go to the result doc. Flow diagrams redrawn (fresh reviewers per round, dedup/calibrate/classify, cap and escalation branch). Red flags: "ALL means ALL" → "Re-review is mandatory; its roster comes from the mechanical trigger, never judgment"; "Skip re-review, the fixes were small" (lite) rewritten the same way; "One more iteration" now cites the cap; "Build passes" updated; new flags for downgrading severity to exit, claiming clean at the cap, resuming a reviewer, and skipping the verification re-run. No lite-specific rules.
6. **`skills/sdlc-review-code/SKILL.md`** — Step 3 gains the roster-size rule and states its dispatch is review round 1. Step 4's dedup and calibration tables moved to `finding-classification.md`; a short inline step keeps the critical behavior (merge same-location duplicates keeping the highest severity; calibrate before labelling). Report Framing Discipline kept. Fix gate: critical/major first, minors batched. Step 5a self-check counts the findings being fixed this round and records the pre-fix snapshot. Step 5b replaced with the mirrored code-review block (5a's manager-rule guardrails stay inline). Fix Summary shows rounds of 3 and the Open Minor Findings table. Red flags :367 (lenses) and :372 (Tier 2) kept — Tier 2 wording now says a touched-domain Tier 2 agent stays; new flags for headcount padding, judgment-scoped re-review, and claiming clean at the cap.
7. **`skills/sdlc-plan/SKILL.md`, `skills/sdlc-lite-plan/SKILL.md`** — Selection Rule: "When in doubt, include" replaced by coverage-not-headcount wording with AOP5 as a rule (beyond five, a one-sentence unique-contribution statement) and MTS4 specialists; the existing `Consult [sdlc-root]/knowledge/architecture/agent-orchestration-patterns.yaml` lines kept (phrasing contract). Plan review: mirrored plan-review block added; classification now dedups, calibrates on the shared scale, and fills the `Scope change` column; re-review trigger (1) reads `Scope change` instead of `Severity = critical` (triggers (2) and (3) unchanged, full step-1 roster unchanged, no narrow re-review, no re-review for non-scope fixes); revision checklist counts minors and scope-change findings; stopping condition is the exit bar with an Open Minor Findings table appended to the plan; external reviewer's 2-round cap sits inside the 3-round loop cap. Lite-plan flow diagram redrawn to show the trigger and cap. New red flags on severity-vs-scope triggers, the cap, reviewer reuse, and headcount padding.
8. **`skills/sdlc-create-reference-doc/SKILL.md`** — CRITICAL/HIGH/MEDIUM/LOW reviewer format and the "no CRITICAL, HIGH, or MEDIUM" exit replaced by the shared critical/major/minor scale (read as impact on a reader) and the exit bar, used as-is. § 5 Fix Loop carries the mirrored code-review block; the step 4 dispatch is round 1; the standing reviewer for narrow re-review is `code-reviewer` (on every quorum). Open minors are listed in the commit body (commit template updated). Flow diagram and red flags updated.
9. **`process/agent-selection.yaml`** — Selection Process step 7: coverage, not headcount; AOP5 beyond five; MTS4 specialists; lenses are not headcount.
10. **`knowledge/architecture/agent-orchestration-patterns.yaml`** — AOP5: note that review rosters apply it through the Step A roster rule, using the one-sentence test rather than splitting the round. No rule change.
11. **`process/external-review-gate.md`** — Severity vocabulary points at `finding-classification.md`; external findings are deduplicated and calibrated with internal ones; the 2-round gate cap is reconciled with the 3-round loop cap (both apply, whichever first; gate re-entries consume loop rounds) for execution and plan review; the plan-review rubric now defines the three severities for the external model. **`templates/external-review.sh.template`** default-format line defines them too.
12. **`CLAUDE-SDLC.md`** — Direct Dispatch "Review before committing": "dispatch ALL relevant agents… re-review until clean" replaced by a pointer to the loop plus the one-line roster / re-review / exit / cap summary (self-contained for target CLAUDE.md files). Escalation list mentions the review-loop round cap.
13. **`process/README.md`** — `review-fix-loop.md` and `finding-classification.md` rows describe what each now owns; consumer counts corrected to 7.
14. **`templates/result_template.md`, `templates/sdlc_lite_result_template.md`** — New Open Minor Findings section.
15. **`process/discipline_capture.md`, `process/collaboration_model.md`, `process/github-checkpoints.md`, `bundles/github-provenance/fragments/{sdlc-execute,sdlc-lite-execute,sdlc-plan}.md`** — Stale "review-fix" skill row retitled to `sdlc-review-code`; escalations mention the round cap; CP-7 / plan checkpoint wording "loop clean" → "meets its exit bar".
16. **`agents/sdlc-reviewer.md`** (hardlinked to `.claude/agents/sdlc-reviewer.md`) — § Cross-skill DRY: `MIRROR` blocks are exempt from extraction recommendations; new mirrored-block drift check (copy must match the source exactly; a listed consumer with no copy is major).
17. **`.claude/skills/ccsdlc-audit/references/compliance-methodology.md`** — Dimension 10 check 5: mirrored-block drift, with a BSD-safe shell check (verified against all six copies and against a deliberately drifted copy); scoping rule exempting `MIRROR` blocks from extraction recommendations.

18. **Quality gate** — `sdlc-reviewer` dispatched in three parallel passes (execute pair, review-code + reference-doc, plan pair); 0 critical, 10 major, 20 minor, 10 nit in total. The plan pass walked trigger (1)–(3) before and after and confirmed plan re-review fires in exactly the same cases. Applied: the snapshot mechanism change above (reference-doc pass: the doc is a new untracked file); `sdlc-review-code` now emits the Classification Table before fixing (FIX / INVESTIGATE / DECIDE / PRE-EXISTING), runs the full verification gate after fix rounds, and moves a parenthetical `agent-context-map.yaml` instruction into its own sentence (phrasing contract); reference-doc minors get the batched pass before being listed, classification and External-Gate-not-applicable notes added, diagram gains the cap/escalation branch; execute skills' descriptions and round-1 roster now include the standing pair, every round emits the Step A checklist, Step E paragraph carries the gate cap and never-block rule, a round-cap escalation outcome rule, CHECKER-mode re-audits follow the loop rules, Open Minor Findings wired into § 3 / result-doc lists, lite/full red flags aligned, and stale step references fixed (2c→2b, 3c→3d, 3d→3e, 3b→3c, "L143"); plan block now records the pre-revision Files list and phase/agent assignments before the revision dispatch and defines the roster as the round-1 dispatch checklist; `sdlc-plan` diagram gains the re-review/cap loop; lite-plan diagram no longer lets a minors-only round skip the writer; plan checklists say "round N of 3"; `manager-rule.md` allowed-edits list covers the Open Minor Findings table; `sdlc-lite-plan` points at `agent-selection.yaml`; `sdlc-plan` bare `playbooks/README.md` path fixed; Integration/Uses lists include the two process docs. Mirror drift check re-run after every source edit: all six copies identical. Not applied (pre-existing, out of scope): skill body length and the `sdlc-plan` Integration section shape. The gate then ran the new loop on itself. Round 2 sent the full roster, because round 1 had major fixes, and found 0 critical/major and 14 minors. Those 14 went into one batched pass: escalation-outcome wording; `review-fix-loop.md` step qualifiers; CHECKER round counting; lite description; red-flag merge and parity; the `sdlc-plan` diagram gate; AGENT-RECONFIRM limited to round 1; "round-1 roster" naming; review-code's pre-round-1 gate exemption; the Tool Rule link; the per-round checklist; and the `sdlc-reviewer` unresolvable-source rule. The batch also covered `sdlc-develop-skill` and `ccsdlc-create-skill` (item 19). Round 3 sent the narrow roster, since every touched file was named in a finding, and found 0 critical/major, 4 minors and 2 nits. The loop exited at the cap, and these were listed as **Open Minor Findings** for CD. CD then directed fixing all four before the v1.9.0 tag was redone; each row says how it was resolved:

| # | Finding | Location | Why still open |
|---|---------|----------|----------------|
| 1 | When CD directs proceeding past the round cap with majors open, the step 3 precondition and the "Review loop complete — no critical or major findings open" announcement would be false. The skills should say to skip the announcement and record the open findings and CD's direction in the result doc. | `sdlc-execute` / `sdlc-lite-execute` § 2 escalation paragraph | **Resolved:** the escalation paragraph now skips the announcement and records the open findings and CD's direction; step 3's precondition admits the CD-directed path |
| 2 | The `sdlc-plan` diagram's re-review edge loops back to node 5, whose label still says "AGENT-RECONFIRM". Prose says reconfirm is round 1 only. | `sdlc-plan` flow diagram | **Resolved:** node relabelled "AGENT-RECONFIRM (round 1 only) … re-review: frozen roster, no reconfirm" |
| 3 | `sdlc-plan` CHECKER-mode re-audit has no Classification/`Scope change` table, roster, or escalate-at-cap rule. Its trigger is not mechanically evaluable. | `sdlc-plan` CHECKER step 6 | **Resolved:** plan audits classify with the `Scope change` column and record Files/phase-agent state first; re-audits use the full round-1 roster; the cap escalates via `AskUserQuestion` |
| 4 | `sdlc-plan` does not say to re-emit the "Plan review round N of 3" checklist each round. `sdlc-lite-plan` says "copy it". | `sdlc-plan` § 5 Re-review | **Resolved:** both plan skills re-emit the checklist each round with N updated |

A narrow `sdlc-reviewer` check of these fixes found three more minors, all applied. `review-fix-loop.md` § Round Cap now owns the CD-directed-proceed rule: the still-open critical and major findings go in the Open Minor Findings table with their real severity and CD's direction, and `finding-classification.md` and both result templates say so. The plan checklist re-emit drops the external reviewer once its 2-round cap is spent. `sdlc-plan` CHECKER audits deduplicate and calibrate before classifying. Nits: the four skills that quoted a shortened Step A checklist header now quote it verbatim. The "step-1 list" sentence in `sdlc-lite-plan` is kept, because it is correct as a contrast with the dispatched set.

19. **`skills/sdlc-develop-skill/SKILL.md`, `.claude/skills/ccsdlc-create-skill/SKILL.md`** — The orchestration-skill requirement "Review-Fix Loop — reference to review-fix-loop.md" prescribed exactly the pointer-only form this change forbids; it now requires carrying the matching mirrored block verbatim and registering the skill in the mirror table.

**Deliberately kept:** "When in doubt, include" in `sdlc-develop-agent/references/enrichment-methodology.md` (external-content relevance mapping, not reviewer selection) and the other "3-strike" rules (`sdlc-tests-run` test failures, `parallel-dispatch-monitoring.md` dispatch failures, `debate-protocol.md`, `team-communication-protocol.md`, `debugging-methodology.yaml`, AOP debugging checks) are different rules about stuck hypotheses and failed dispatches, not the review loop. Not implemented (raised in the consult, not decided by CD): fixer return contract, stable finding IDs across rounds, whole-file PRE-EXISTING scope qualification, and headless parking/budgets at the cap. No manifest or `contract_changes.yaml` change — no files added, removed, or renamed. Neuroloom `pattern-mapping-rules.md` has no transformation for any changed phrase (`finding-classification`, `review-fix-loop`, severity); new knowledge references use the canonical `Read [sdlc-root]/knowledge/...` form outside parentheses — not a contract change.

**Rationale:** Termination comes from the exit bar and the cap, not from roster trimming alone: the critical/major bar plus three rounds bounds every loop, the mechanical re-review rule (Fable's version — execution reviews run on Sonnet, so no judgment-based scoping) stops whole-roster re-reviews after minor, file-local fixes, and visible Open Minor Findings keep the looser bar honest. One severity scale and one dedup step are prerequisites — a severity-keyed exit bar without shared calibration invites inflation and deflation. Reviewer reuse (D4) and a lighter lite tier (D6) were considered and rejected. Estimated effect ~$1.5–2.5k API-equivalent per month, mostly from rounds 2+ — an estimate, not a measurement. Versioning: **minor** bump (CD decision, 2026-10-06) — the mirrored-block convention and the shared loop contract are new process conventions with no forced migration behavior.

---

## 2026-09-22: sdlc-render becomes sdlc-explain — big pictures, few words `[contract-change]`

**Origin:** CD brought in Thariq Shihipar's (Claude Code team) published practice with artifacts: "use big pictures and few words" typed several times a day, inline SVG in artifacts, artifacts as explainers, "one picture + a hard limit beats three paragraphs of vibe", "show me the diff, not the essay — agents drown in prose", Claude is too verbose by default, and the `/eli5 <topic>` plugin (`anthropics/claude-plugins-community`, `eli5@claude-community`) used for "how does this module work", "why did we make this tradeoff", "what caused this incident". CD asked to fold this into `sdlc-render`, whether render / walkthru / eli5 should be combined, then clarified: the render was built as the reading aid for specs and plans, `sdlc-walkthru` has overtaken that, so the render no longer needs to be faithful — it needs to explain, the way eli5 does. Then: rename it to `sdlc-explain`, and remove any rules and documentation the change makes unnecessary.

**What happened:** A first cut kept three skills (faithful render, walkthrough, a new explainer) sharing one doctrine. CD's clarification collapsed that: with the comprehensive read owned by the walkthrough, a faithful render and an explainer of the same deliverable are the same artifact with different fidelity — and the lossy one is the one people read. So the render *is* the explainer. Merged, renamed, and everything built for the faithful-render era removed: the verbatim content rule, the four-question audience/purpose/emphasis scoping, audience-variant profiles, the per-section slide layout with review checkboxes, tab auto-generation, filter chips, the component-by-component document-type profiles, and the Content Review Deck component in the design system.

**Changes made:**

1. **`skills/sdlc-render/` → `skills/sdlc-explain/SKILL.md`** — Renamed and rewritten as the eli5 explainer. Subject resolution table (deliverable → catalog and document type; module → code; tradeoff → specs/ADRs/knowledge layer/changelog; incident → incident doc and fixing commits), verify-before-draw under the Code Verification Rule with a sources footer, the "one thing" discipline (≤12-word title), storyboard budgets (3–8 pictures, 12 for a many-phase plan; ≤40 words per picture; ≤30 × pictures total, binding; zero paragraphs), a beat → picture-type table, open decisions always get a picture, inline-SVG-only drawing rules, one picture per screen, jargon glossed inside the picture. Post-skill mode uses the document type's storyboard with no Q&A; manual mode has no scoping Q&A either — the only question is a disambiguation. Deliverable explainers still live beside their markdown (staleness conventions unchanged); question explainers go to `docs/current_work/explainers/`. Twelve Red Flags; four validation criteria. Triggers keep `/sdlc-render` and "render the spec/plan" so muscle memory still lands, and add `/eli5`, "eli5", "explain like I'm 5", and explainer-shaped questions.
2. **`process/html-rendering.md`** — Rewritten. Philosophy now says HTML explains, it does not transcribe. New § "Visual Doctrine: Big Pictures, Few Words" (seven rules, credited to Thariq's practice). "Two Categories" are now explainers and exploration artifacts, with a table relating them to the walkthrough. § Post-Skill Offer keeps the opt-in, precedes-approval, and walkthrough-as-peer rules and the skill → storyboard table. § Document-Type Storyboards replaces the component-by-component profiles: one row per type with its default beats. Removed: Layout Modes, Review Checkboxes, Tab Auto-Generation, Filter Chips, Audience Variants, Manual Render scoping, and the verbatim content rules. Staleness and sharing kept, trimmed.
3. **Ten post-write offer points** (`sdlc-plan` ×2, `sdlc-lite-plan`, `sdlc-execute`, `sdlc-lite-execute`, `sdlc-idea`, `sdlc-handoff`, `sdlc-audit`, `sdlc-create-reference-doc`, `sdlc-debug-incident`; `sdlc-review-code`'s two-line variant) — Each carried a near-verbatim paragraph re-describing how to render. Replaced with one line: offer an explainer (`sdlc-explain`, named storyboard) or a walkthrough, never unprompted, mechanics in the process doc. "Render precedes approval" wording in `sdlc-plan` / `sdlc-lite-plan` (steps and Red Flags) now says explainer.
4. **`skills/sdlc-walkthru/SKILL.md`** — Step 4 routes by shape of the question: *see* one mechanism → `sdlc-explain`; *manipulate* it → an exploration artifact. Description, Complements, Does NOT replace, and Red Flags reference the explainer instead of the render.
5. **`templates/html-design-system.html`** — Removed the Content Review Deck (section 21): its CSS, print rules, TOC entry, demo markup, and the localStorage review-state script. The presentation Slide Deck (section 20) stays — it is the explainer's optional one-picture-per-screen stepper. Footer attribution updated.
6. **`CLAUDE-SDLC.md`** — The post-write rule now offers explainer or walkthrough, and a second paragraph states the visual doctrine and `/eli5`.
7. **`process/commands.md`** — `/sdlc-render` row replaced by `/sdlc-explain <subject>` / `/eli5 <subject>`; walkthru row calls it the explainer's peer.
8. **`skeleton/manifest.json`** — `skills/sdlc-render/SKILL.md` → `skills/sdlc-explain/SKILL.md`.
9. **`skeleton/contract_changes.yaml`** — Entry `0015`, `rename_skill` `sdlc-render` → `sdlc-explain`, with notes on the offer-paragraph rewrite and the design-system removal.
10. **Quality gate** — `sdlc-reviewer` dispatched on the rewritten skill, then across the whole change set (three parallel passes on the two rendering skills, the ten lifecycle skills, and the process-doc wiring). Second round applied: a leftover "Render precedes approval" paragraph deleted from `sdlc-plan`; `sdlc-review-code` and `sdlc-audit` codebase-health mode now offer the walkthrough alongside the explainer; the stale "tabs and collapsibles only" clause in `sdlc-idea` / `sdlc-plan` exploration-artifact provisions replaced with the explainer's static, stepper-only rule; one missed "render" noun in `sdlc-walkthru`; `§ Post-Skill Offer` casing normalized across all pointers; two Key References descriptions in `CLAUDE-SDLC.md`. First round on the skill (4 minor findings, all applied): "render" as a noun replaced by "explainer" throughout the body (the `/sdlc-render` and "render the spec/plan" triggers stay, deliberately); a garbled § Sharing cross-reference fixed; the Visual Doctrine section trimmed to a pointer so it matches the DRY-notes claim; the Code Verification Rule no longer re-described inline.

**Rationale:** Prose is where the human in the loop becomes the bottleneck; a picture with a hard limit is how they stay in the loop without reading everything. Once the walkthrough owns "nothing load-bearing omitted", a second HTML view that also tries to keep everything is dead weight — and the machinery built to make a faithful render reviewable (slide decks, review checkboxes, audience scoping) is dead weight with it. The community plugin's three-line prompt is preserved as the skill's spine; cc-sdlc adds grounding (verify before draw, cite sources, always draw the open decisions) so that a lossy picture is never a false one. Versioning: a skill rename is a breaking contract change → **major** bump when CD next tags.

---

## 2026-09-02: sdlc-reviewer quality-gate fixes for the two new skills

**Origin:** `sdlc-reviewer` dispatched on both skills added today (`sdlc-manage-github`, `sdlc-walkthru`) per the new-skill quality gate. Eight findings total; six applied, two declined with rationale.

**Changes made:**

1. **`skills/sdlc-manage-github/SKILL.md`** — 8 bare `github-checkpoints.md` references expanded to `[sdlc-root]/process/github-checkpoints.md` (path-variable rule); recipe headers renamed `### Recipe N:` to disambiguate from the Steps numbering; Integration gains the board-roles-vs-catalog-statuses relationship (roles are a deliberate per-project taxonomy; the catalog stays canonical) and documents why the recipes stay inline rather than in `references/` (an extra read-hop is skippable indirection under the directive-inlining convention — declining the extraction suggestion).
2. **`skills/sdlc-walkthru/SKILL.md`** — `AskUserQuestion` gate question now cites `[sdlc-root]/process/collaboration_model.md` § Tool Rule; the Code Verification Rule citation names its home (project CLAUDE.md); the Manager Rule section names the dispatch mechanism. Declined: renaming `walkthru` → `walkthrough` — the contraction matches the trigger phrases and the originating project's installed skill name, which keeps migration continuity.

**Rationale:** The quality gate exists precisely for ported content — both declined findings are deliberate design choices now documented in place, so the next reviewer reads a decision instead of re-flagging a gap.

---

## 2026-09-02: Adopt sdlc-walkthru from paire-appetit — guided artifact walkthroughs as the render's peer

**Origin:** paire-appetit built `sdlc-walkthru` as a comprehension-first alternative to the HTML render: an SDLC artifact delivered as a paced, part-by-part guided tour — CD paces with "next", questions are answered against verified code, and feedback is classified and dispatched to revision agents mid-flight. Its first use surfaced three material spec corrections a static read had missed. Fully generic apart from two project references, so it upstreams as a core skill (not a bundle — no external dependencies).

**Changes made:**

1. **`skills/sdlc-walkthru/SKILL.md`** — New core skill, ported near-verbatim: preflight segmentation by story (4–7 parts, chaptered past ~8), the pacing contract, part-delivery rules (≤350 words, lead with the claim, one part per turn), verify-then-answer for questions, feedback classification via the invoking skill's revision protocol (SPEC-REVISION et al.), wrap-up-before-gate. Generalized: the project-specific principles reference now consults `[sdlc-root]/knowledge/agent-context-map.yaml`; paire's terminology example dropped.
2. **`process/html-rendering.md`** — § Post-skill render offer: the walkthrough is the render's peer at every offer point — skills offer both consumption modes; whichever CD picks resolves before any approval question. (This closes the follow-up paire's own Integration note recorded as not-yet-done.)
3. **`CLAUDE-SDLC.md`** — Post-write render-offer paragraph updated to offer the walkthrough alongside the render.
4. **`skeleton/manifest.json`** — `skills/sdlc-walkthru/SKILL.md` added to `source_files.skills`.
5. **`process/commands.md`** — `/sdlc-walkthru` row.

**Rationale:** A document's job is durability; a decision-maker's job is judgment. The walkthrough serves the approval gates the render already serves, with a different consumption mode — and it demonstrably surfaces corrections a static read misses. New installs get it via the normal file copy; existing installs receive it on next migration as an ordinary new framework skill.

---

## 2026-09-02: Unbuilt-Capability Rule, launch-recipe skill convention, additive-contract versioning

**Origin:** Three adoptions from reviewing paire-appetit's recent evolution alongside this session's own decisions. (1) Paire's newest CLAUDE.md rule (their commit of 2026-09-02): a session investigated only the exposed application layer, concluded a leadership-requested capability "does not exist," and cut the language unilaterally — when the underlying data actually supported building it. (2) Paire's project-local `verify` skill — a build/launch recipe with accumulated environment gotchas — is a pattern worth naming upstream even though its content is project-specific. (3) CD decision on versioning for this release.

**Changes made:**

1. **`CLAUDE-SDLC.md`** — New § Unbuilt-Capability Rule: Ask, Don't Silently Cut (generalized from paire's). "Not found in the codebase" is a reason to ask, never to unilaterally cut or soften a stakeholder's request: check the underlying data (not just the application layer), ask via `AskUserQuestion` with what exists vs. what would need building, and never present a cut as a fait accompli — doubly so for leadership requests, whose phrasing may be deliberately illustrative.
2. **`process/verify-command.md`** — New § Companion: the Project Launch-Recipe Skill: the convention of a project-local `.claude/skills/verify/` skill capturing launch commands, end-to-end drive instructions, and accumulated environment gotchas; seeded on first rediscovery, grown per gotcha. The framework defines the convention; the content stays project-specific.
3. **`CLAUDE.md`** (source repo) — Versioning refinement (CD decision, 2026-09-02): purely additive `contract_changes.yaml` entries — opt-in bundle debuts, manifest field additions with back-fill defaults — are **minor**, not major; major is reserved for entries that force behavior change on existing installs.

**Rationale:** (1) is a judgment-boundary rule that generalizes cleanly: codebase absence ≠ infeasibility, and the requester owns the call. (2) names a pattern the built-in `run` behavior already looks for, so projects stop rediscovering their own launch procedure. (3) keeps major bumps meaningful — a convention no project is forced to adopt should not signal breakage.

---

## 2026-09-02: Debut github-provenance bundle (upstreamed from paire-appetit D52)

**Origin:** paire-appetit built a full GitHub provenance convention as their D52 — every tracked deliverable narrated into a GitHub issue via lifecycle checkpoints (CP-1…CP-12 + CP-S1/S2), with Projects v2 board tracking under a forward-only floor rule, a never-block invariant, SHA-pinned artifact links, and a read-only reconciliation audit dimension. It was live-verified against real boards (their Phase 6), which among other things discovered that GitHub accepts a wrong board's option ID silently — making name-then-resolve-per-session the only guard against silent mis-writes. This entry generalizes and upstreams the whole convention as an opt-in bundle. Design cross-checked via the external review gate (Codex, 18 findings triaged): config survives migration via a PROJECT-SECTION-wrapped config block, "configured" is machine-defined (`enabled: true` set last in Enablement), issues-only mode (`board: none`) supported, label provisioning and preflight in Enablement, predecessor detection at the migrate offer.

**Changes made:**

1. **`process/github-checkpoints.md`** — New policy doc (bundle-delivered). Owns the checkpoint map, column **roles** (`registered`/`spec-approved`/`executing`/`stakeholder-blocked`/`validated`/`staged`) mapped to per-project names/ranks in a `PROJECT-SECTION`-wrapped config block, the floor rule + CP-S2 exact-match exception, never-block + miss-log, catalog-wins + reconciliation cutoff, never-reopen, repo selection (single-repo first), labels (universal + project-defined conditionals), pre-deliverable `Parked:` promotion path, SHA-pinned links, commit conventions, call budgets with two exemptions, terminology + content prohibitions (config-extensible), all comment templates, failure classes, checkpoint confirmation carve-out, and the six recipe names. § Activation defines the two-stage gate (installed + `enabled: true`); § Enablement is the guided setup (preflight, board column verification, label provisioning, miss-log gitignore, cutoff, `enabled: true` last).
2. **`skills/sdlc-manage-github/SKILL.md`** — New skill (bundle-delivered). Interactive `gh` procedures for Projects v2 boards/issues (the github MCP tools 404 on board items), plus § SDLC Checkpoint Recipes: `create-or-link` (idempotent by `Dnn` prefix, `registration`/`parked` modes, promotion path, idempotent board add), `resolve-and-write-status` (role→name→ID per session, floor rule, CP-S2 flag, NEVER-WRITE hard guard, no-op in issues-only mode), `link-sub-issue`, `commit-and-push-artifact` (pathspec-only, rebase-once, SHA re-capture), `log-miss` (atomic JSONL append), shared failure-class→action lookup, and the verified cross-board option-ID hazard note.
3. **`bundles/github-provenance/fragments/*.md`** — Eight fragments injected as `BUNDLE-SECTION` blocks: checkpoint ownership sections for `sdlc-plan` (CP-1/2/3, S-pair), `sdlc-lite-plan` (CP-1/3, S-pair — no spec gate), `sdlc-execute` (CP-4–9, S-pair), `sdlc-lite-execute` (CP-4/5/7/8, S-pair — no CP-6/9), `sdlc-handoff` (CP-11/11b), `sdlc-archive` (CP-10 two-part, CP-12, parked closure, archive-time checklist executor); a Dimension 10 dispatch hook for `sdlc-audit`; and the full § GitHub Provenance Reconciliation (10a–10j) for `sdlc-compliance-auditor`. Every fragment opens with the activation gate and inlines the DIRECTIVE-level rules (never-block, comment-before-Status, the CP-3/CP-6 trap notes) while reading DATA (templates, ranks) from the policy doc.
4. **`skeleton/manifest.json`** — `bundles.github-provenance` registered with `skills`, `process`, and `fragments`.
5. **`skeleton/contract_changes.yaml`** — Entry 0014 (`bundle_debut`) with predecessor-detection notes for hand-rolled installs (paire-appetit itself: adopt-preserving-config, retire hand-wrapped equivalents on their next migration); bundle_debut type comment updated for the extended shape.
6. **`process/commands.md`** — `/sdlc-manage-github` row (marked as bundle-delivered).
7. **`CLAUDE.md`** (source repo) — `bundles/` row in the structure table; consistency-check globs and manifest comparison extended to bundle entries.
8. **Post-D52 refinement sync** — paire evolved the convention after the initial port was drafted (their commits of 2026-08-14…24, pulled mid-session); all four refinements are folded in: closed label taxonomy with the **silent label auto-creation** hazard (the REST create never fails on an unknown label — replaces the obsolete unknown-label retry fallback), § Issue Types (`Bug`/`Feature`/`Task` set on the same REST create call, `gh issue create` has no type flag; type silently dropped without push access → audit is the detector), § Board Fields: Ownership (human-owned fields incl. the Test Verdict example, the assignees convention, and the deliberate absence of estimate fields), the follow-up-issues-start-at-`registered` rule (with the originating project's 17-misfiled-issues incident), the completion-lives-in-comments rule (policy + skill + Red Flags — bodies go stale; CP-9–12 outcomes are comments), the full-read-before-classify triage rule, audit 10h upgraded from label presence to **taxonomy parity** (extra labels are drift; untyped open issues; stale column-scoped verdicts, report-only), and paire's create-or-link step-numbering fix ("skip to step 4 — step 3 is creation-only").
9. **External implementation review fixes (Codex, second pass — on the diff, not the plan)** — bundle-detection fallback restricted to skill paths so a hand-rolled `github-checkpoints.md` routes through §4.7 predecessor detection instead of being auto-marked installed; fragment injection extended to the content-merge flow (§2.2–§2.4 — most fragment targets are content-merged skills, not direct-copied files) in both `sdlc-migrate` and the marker doc; `installed_files` drift baselines explicitly include bundle-installed files (initialize + migrate back-fill); `create-or-link` step 4 now explicitly writes the `registered` option after a fresh board add (a new item is otherwise column-less) and states the comment-before-Status ordering on the link path; mechanical cautions added for `content.repository` shape and pagination-at-the-limit (recipe + audit dimension); the audit-skill fragment states outright that "all 9 dimensions" language is superseded when the dimension is active.

**Rationale:** The provenance layer makes SDLC work legible to people who will never open the markdown vault, without the issue ever becoming a second source of truth — the catalog stays canonical, the board is a projection corrected forward-only, and a checkpoint can never stall the work it narrates. Shipping it as a fragment-carrying bundle keeps core skills clean for the majority of projects that will not enable it, while adopters get the full DIRECTIVE-inlined sections and every future policy improvement on migration. The role indirection (`registered`…`staged`) keeps the checkpoint map stable across projects whose boards name columns differently, and `board: none` gives issue-only projects the narrative without Projects v2.

---

## 2026-09-02: Bundle fragment injection (BUNDLE-SECTION) and bundle process files

**Origin:** Upstream adoption of paire-appetit's GitHub provenance convention (their D52). The convention needs ~40–50-line checkpoint sections inside six core lifecycle skills plus an auditor dimension — content that must not ship as dormant dead weight to projects that decline the bundle, and must not freeze at install time the way hand-wrapped `PROJECT-SECTION` blocks do. Design cross-checked via the external review gate (Codex), which drove the idempotency, ordering, offline-validation, and predecessor-detection requirements. This is Phase 1 (mechanism); the `github-provenance` bundle itself is Phase 2.

**Changes made:**

1. **`process/project-section-markers.md`** — New § BUNDLE-SECTION Markers: upstream-owned sibling of `PROJECT-SECTION`. Labels namespaced `bundle/fragment`; declared in `manifest.bundles.<name>.fragments` (fragment source file → target framework file); injection is strip-then-append (idempotent), alphabetical bundle order, no nesting; hand-edits inside markers are lost on migration by design; presence must match `installed_bundles`/`bundle_fragments`; injection counts as a file write for adapter `post-file-write`. Installer ordering rule: copy files → inject fragments → record in manifest last (crash under-claims, re-run repairs). Direct-copy flow and Validation sections updated to match.
2. **`skeleton/manifest.json`** — `bundles._comment` documents the extended schema: optional `process` and `fragments` fields alongside `skills`. (Also normalized a stray-indent directory entry.)
3. **`skills/sdlc-initialize/SKILL.md`** — Phase 1b bundle offer lists process docs and fragment targets; effective install set includes bundle `process` files; fragment injection step after all copies; `installed_bundles`/`bundle_fragments` written only after files + fragments land; Enablement-section offer for bundles that need per-project configuration. Manifest schema example and field docs gain `bundle_fragments`.
4. **`skills/sdlc-migrate/SKILL.md`** — §2.0a: effective process list, file-existence fallback covers bundle process paths, fragments-are-refreshed rule. §2.1 marker preservation: new step 7 injects current fragments from source at `[target_tag]` after PROJECT-SECTION re-injection. §4.5: new step 4a maintains `bundle_fragments` (add injected, drop upstream-removed). §4.7: offer lists process/fragment surface; predecessor detection for bundles whose `process` paths already exist in the project (adopt-preserving-config vs. skip); accept path copies process files, injects fragments, records manifest entries last, offers Enablement.
5. **`agents/sdlc-compliance-auditor.md`** — Dimension 7 marker validation extended: `BUNDLE-SECTION` pairing, orphaned-bundle-content check against `installed_bundles`, partial-install check against `bundle_fragments`, nesting with `PROJECT-SECTION` is critical.
6. **`skeleton/contract_changes.yaml`** — Entry 0013 (`manifest_field_added`, `bundle_fragments`, default `{}`) documenting the schema extension and the adapter posture.

**Rationale:** Bundles could previously carry only whole skills, so any bundle needing hooks inside core framework files had two bad options: dormant sections shipped to everyone (recurring context cost in every downstream invocation, forever) or project-local `PROJECT-SECTION` blocks (frozen at install, silently staling as upstream evolves — the exact failure paire's hand-wrapped Dimension 10 block exhibits). Fragment injection gives bundles a third path: core files stay clean upstream, hooks exist only where the bundle is installed, and hooks refresh from source on every migration because migration overwrites with a clean upstream copy and re-appends the current fragment — no merging, ever. The mechanism is general-purpose: any future bundle (testing infrastructure, incident extensions) rides the same rails.

---

## 2026-07-21: 6n guard check verifies effective enforcement, not presence; versioning convention recorded

**Origin:** Sleeved D121 field report (via inter-session, evidence in Sleeved ADR-15 and the D121 result doc): their `zustand-selector-missing-useshallow` guard shipped with the rule set to `off` behind a stale justification comment — both 6n's "guard exists" check and their local wiring script read it as fully wired, because presence-in-config was checked but not effective enforcement. Related sub-gap: conditional-registration wrappers (`plugin.rules["x"] ? {...} : {}`) defeat text-grep wiring checks the same way. Caught only by a completion review. Sleeved correctly declined a local patch (framework owns check design) and fed it upstream.

**Changes made:**

1. **`process/guardrail-lifecycle.md`** — Freshness check 1 renamed "Guard exists and enforces": parse effective severity (`off` = CRITICAL, same as missing; `warn` = WARNING unless `notes` documents advisory intent), evaluate conditional registration for runtime collapse, skipped tests and continue-on-error CI steps count as not enforcing, known-bad-sample fallback when static reading is inconclusive. `location` spec and new Red Flag ("presence ≠ enforcement") updated to match.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — 6n check 1 extended identically.
3. **`CLAUDE.md`** — Versioning convention recorded (CD decision, v1.7.0/v1.7.1): minor for new contract surface (new cross-skill contracts, command surface, downstream data schema); patch for iterations, fixes, and check strengthening within existing contracts.

**Rationale:** The first field deployment of 6n produced a guard that passed the freshness check while enforcing nothing — the exact failure 6n exists to catch. One fix (read effective enforcement from config semantics, not string presence) closes both the severity blind spot and the conditional-wrapper gap.

---

## 2026-07-20: Review-time mechanization-threshold trigger in sdlc-review-code

**Origin:** Sleeved D121 (CD-approved, via inter-session): per-review pattern logging and audit-cadence triage were only connected by the next audit happening to run — a cluster could cross the mechanization threshold and sit unproposed for weeks.

**Changes made:**

1. **`skills/sdlc-review-code/SKILL.md`** — Step 6d: when logging brings a `promoted: false`, non-guarded cluster to 3+ occurrences within Dimension 6l's 30-day window (6l's threshold definition reused verbatim, not redefined), emit "Pattern {slug} crossed the mechanization threshold ({N} occurrences) — run `/sdlc-audit` to triage mechanization." Skips `mechanization_assessed: excluded` clusters. Nudge only — no triage or field-writing from within the review skill.

**Rationale:** Threshold crossings now surface in the same review that causes them, while the decision itself stays at audit triage where CD gates it.

---

## 2026-07-20: Guardrail exclusion marker — "assessed, deliberately not mechanized, do not re-propose"

**Origin:** Inter-session report from Sleeved's D121 reconciliation against the just-landed `guardrail-lifecycle.md` — first downstream contact with the contract found a gap: a cluster clearing the 3+ threshold whose manifestations are heterogeneous (would need a semantic allowlist that doesn't exist). CD chose exclusion, but the contract had no way to record it, so 6l and reflect would re-propose every cycle and CD would re-dismiss forever.

**What happened:** Sleeved adopted local fields `mechanization_assessed: excluded` + `mechanization_reason`; upstream adopts the same names verbatim so the local data becomes canonical on next migration.

**Changes made:**

1. **`process/guardrail-lifecycle.md`** — New § "Assessed and Excluded — Do Not Re-Propose": field schema, semantics (set only at triage; exclude ≠ defer; guards only — knowledge promotion unaffected; reversible at triage; new occurrences accumulate info-tier but never auto-reopen). Red Flag row for the re-propose nag.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — 6l.1 validates the fields; 6l.2 skips excluded clusters from guard-candidate output, lists them info-tier with reasons; output format shows the excluded section; triage note distinguishes decline-with-exclusion from defer.
3. **`skills/sdlc-reflect/SKILL.md`** — Step 4b skips excluded clusters.
4. **`skills/sdlc-review-code/SKILL.md`** — Step 6 optional-fields note covers the exclusion fields (don't strip them when appending occurrences).

**Rationale:** A promotion pipeline that cannot record "no, and stop asking" trains CD to ignore its proposals. Exclusion keeps the decision durable, audit-visible (info-tier listing, never hidden), and reversible — without turning every dismissal into a permanent burial. Additive only; no reference-pattern changes, no `[contract-change]`.

---

## 2026-07-20: Guardrail lifecycle, KEEP-IN-SYNC lens, codebase-health audit mode, verify-command convention (Sleeved upstream contributions)

**Origin:** Cross-repo handoff from Sleeved (`docs/current_work/ideas/cc-sdlc-upstream-contributions_handoff.md`, sourced from Sleeved's 2026-07-17 repo-wide quality audit). Four framework-shaped improvements identified downstream that would be clobbered by `sdlc-migrate` if implemented there.

**What happened:** Sleeved's `recurring-patterns.yaml` accumulated ~40 pattern clusters, several recurring for months because nothing converts a recurring pattern into a mechanized guard (lint rule, drift test, CI check) — and nothing re-evaluates guards once created. Separately: the `manually-synced-parallel-copies-drift` pattern hit 5 occurrences (copies diverging in the very commit adding the "keep in sync" comment); the audit's product-substrate sweeps proved a generic recipe worth a first-class audit mode; and the top agent-ergonomics gap was the absence of a discoverable one-shot verify command.

**Changes made:**

1. **`process/guardrail-lifecycle.md`** (new) — The cross-skill guardrail contract: LOG → THRESHOLD → PROMOTE → ENFORCE → RE-EVALUATE → MODIFY/RETIRE. Defines the `mechanized_guard` field on recurring-pattern clusters, mechanizability criteria (textual/structural/behavioral signatures), guard-freshness checks, the guard-modification-in-scope rule, and enforcement floors. Framework defines the loop; projects supply the actual rules/tests.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — 6l extended: validates optional `knowledge_entry`/`mechanized_guard` fields, flags guard-promotion candidates (mechanizable patterns at threshold) alongside knowledge-promotion candidates; triage promotion note covers the guard path. New **6n Mechanized Guard Freshness**: guard-exists, recurred-despite-guard, suppression-growth, never-fired checks.
3. **`skills/sdlc-audit/SKILL.md`** — Four modes (was three): new **Codebase Health mode** auditing the product substrate via three parallel read-only sweeps (test/CI activation, agentic ergonomics, observability blind spots) with SCOPE → SWEEP → SYNTHESIZE → ROUTE workflow; report to `docs/current_work/audits/`, gaps route to handoffs/plans/parking lots, never fixed in-mode. Dimension 6 summary, triage section (guard promotions + 6n findings), Red Flags, Integration, and frontmatter triggers updated.
4. **`skills/sdlc-audit/references/codebase-health.md`** (new) — Full health-mode methodology: dispatch discipline, the three sweep prompts, report format, merged top-gap ranking (cap 10), routing rules, recurring-pattern cross-referencing.
5. **`skills/sdlc-review-code/SKILL.md`** — Step 6 documents the post-promotion `knowledge_entry`/`mechanized_guard` fields and flags "recurred despite guard" in the patterns table; Step 5a adds the two-part guard-modification-in-scope rule; Integration references the lifecycle doc.
6. **`process/review-fix-loop.md`** — Step C: FIX findings matching a guarded (or plainly guardable) recurring-pattern cluster get two-part fixes — instance + guard — consumed by all execution skills.
7. **`skills/sdlc-reflect/SKILL.md`** — New Step 4b: session-scoped recurring-pattern guard scan (reuses 6l thresholds, no redefinition) proposing guard promotions and flagging recurred-despite-guard; report section, Red Flag ("reflect proposes, triage decides"), Integration updated.
8. **`process/review-lenses.md`** — Contract Safety Lens: manually-synced parallel copies bullet — a KEEP-IN-SYNC comment is itself a defect; require single source of truth or a drift-detection test; grep-based CI floor sanctioned.
9. **`process/verify-command.md`** (new) — The one-shot root `verify` command convention: chains the gates CI runs, documented in CLAUDE.md, invoked by the review-fix loop's verification gate.
10. **`skills/sdlc-initialize/SKILL.md`** — New Phase 9b: check for the verify command, offer scaffolding (chain what exists, report gaps, don't invent tooling); Phase 10 checklist line added.
11. **`agents/sdlc-compliance-auditor.md`** — Dimension 6 summary mentions 6l recurrence and 6n guard freshness.
12. **`process/commands.md`** — `/sdlc-audit health [scope]` row.
13. **`skeleton/manifest.json`** — Added `process/guardrail-lifecycle.md`, `process/verify-command.md`, `skills/sdlc-audit/references/codebase-health.md`.

**Rationale:** Review-pattern logging existed (review-code Step 6) and knowledge promotion existed (audit 6l), but the loop dead-ended at "agents were told" — nothing made the *machine* catch a recurring pattern, and nothing watched guards after creation. This closes the loop end-to-end with explicit ownership: review-code logs, reflect and 6l propose, CD decides at triage, projects implement, 6n re-evaluates, review loops maintain. The KEEP-IN-SYNC lens and verify-command convention are the two cheapest universal wins from Sleeved's evidence; the health mode generalizes an audit recipe already validated against a real repo. No knowledge-layer reference patterns were changed — all new references use canonical phrasing, so no `[contract-change]` tag is needed.

---

## 2026-07-19: Frontier once-over made unconditional for all promotion candidates

**Origin:** CD directive — promotion candidates should never be validated by shipped-deliverable evidence alone; every candidate must be reviewed by a frontier-tier agent (Codex external wrapper at xhigh, or Fable subagent) before reaching CD.

**What happened:** The Promotion Verification Gate had a skip path: a single well-evidenced entry (direct deliverable evidence, batch < 3) bypassed the judge panel entirely and went straight to CD. That entry never received any independent model review — inconsistent with the gate's own rationale, since deliverable recurrence proves a pattern was used, not that its embedded factual claims are true, and the compounding risk of a wrongly promoted entry applies equally to skip-path entries.

**Changes made:**

1. **`process/discipline_capture.md`** — Skip path narrowed: single well-evidenced entries may skip the screening panel (steps 2–4) but not the frontier once-over (step 5); the neutral payload is built for them and the once-over verdict accompanies the CD presentation. Step 5 restated as unconditional for every promotion candidate, including screening-skip entries.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — §6c evidence-production note and step 11a gate description updated to match: the once-over is unconditional; deliverable evidence alone never carries a candidate to CD without an independent frontier-tier fact-check.

**Rationale:** The once-over machinery already exists and runs as a single batch dispatch, so extending it to skip-path entries costs almost nothing while closing the only route by which a promotion candidate could become knowledge-store precedent with zero independent model review. Frontier budget stays concentrated at promotion time, where the risk asymmetry justifies it — parking-lot triage of non-candidates remains cheap.

---

## 2026-07-18: Standard external-review wrapper templates; drop "different model family" from model-facing prompts

**Origin:** CD follow-up to the 2026-07-17 planning integration: "we don't need to say 'from a different model family'. also, we can adopt a standard template from ~/Projects/neuroloom."

**What happened:** The gate doc's example wrappers were toy inline sketches, while the Neuroloom installation had a production-hardened wrapper pair (stdin passthrough to dodge ARG_MAX, `-o` final-message capture so codex noise never reaches the findings contract, `--sandbox read-only --ephemeral`, stderr egress disclosure, mktemp/trap cleanup, and empty-output-is-failure handling in the knowledge judge). The planning payload rubrics also told the external model it was "from a different model family" — unnecessary framing in model-facing text (the cross-family rationale belongs in the docs, not the prompt).

**Changes made:**

1. **`templates/external-review.sh.template`** (new) — Codex-backed standard wrapper adopted from the Neuroloom installation, with the embedded prompt generalized to payload-neutral: it defers to the payload's rubric header for artifact, task, and output format, so the one wrapper serves diff review, plan review, and approach consults.
2. **`templates/external-review-knowledge.sh.template`** (new) — Neuroloom's knowledge-judgment wrapper adopted as-is (paths converted to `[sdlc-root]`), including its contract difference: empty stdout exits non-zero so the Promotion Verification Gate falls back to an internal subagent judge.
3. **`process/external-review-gate.md`** — "Example wrappers" replaced by "Standard template": documents the shipped template, its operational details, and enable-by-copy instructions; the local-Ollama variant stays as the sensitive-codebase alternative. Wrapper-contract bullet updated from "cc-sdlc ships no default wrapper" to the template + copy/chmod stance. Knowledge-judgment section's inline example replaced with a pointer to its template. Removed "from a different model family" from the Codex example prompt and both planning payload rubrics.
4. **`skeleton/manifest.json`** — Both templates added to `source_files.templates`; `_templates_note` updated (non-.md template files install too; `*.sh.template` files are inert until a project copies and chmods them — the gate activates on the executable copy, never the template).
5. **`skills/sdlc-migrate/SKILL.md`** — Template copy rules widened from `templates/*.md` to all manifest-listed template files, with an explicit guard: never copy a `*.sh.template` onto the executable wrapper path, and never overwrite a project's enabled `external-review*.sh` (project-authored).
6. **`process/path-mappings.md`** — `templates/*.md` row generalized to manifest-listed template files.
7. **`CLAUDE-SDLC.md`** — Gate paragraph now names the shipped templates and the copy + chmod enable path.

**Rationale:** A production-tested wrapper encodes half a dozen non-obvious operational lessons; shipping it as a template means the next project enables the gate in one copy instead of rediscovering ARG_MAX limits and codex stdout noise. Keeping templates inert (`.sh.template`, non-executable, in `templates/`) preserves the gate's activation semantics — presence of the executable wrapper remains the project's explicit egress opt-in. And prompts sent to the external model should carry task instructions, not meta-commentary about the ensemble's composition.

---

## 2026-07-17: External reviewer becomes a first-class planning participant

**Origin:** CD directive — "integrate our external reviewer into planning as well. It should be more of a first-class resident in the SDLC if it is configured… deliberation between models is much stronger when they're of different families."

**What happened:** The External Review Gate participated only at execution time (post-internal-loop diff review) and knowledge promotion. Planning — where decisions are structural and cross-family disagreement is most valuable — had no external participation. The gate was also framed as "opt-in per run," leaving configured projects under-using a capability they had already paid to set up.

**Changes made:**

1. **`process/external-review-gate.md`** — Reframed intro as a lifecycle-wide participant with a three-point integration table (planning / execution / knowledge promotion). Added a "First-class once configured" presence policy: enabling is opt-in via wrapper presence, but once configured, participation is the default at every integration point, with named skip conditions the only sanctioned skips. Added § Planning Integration defining (1) the approach deliberation consult (payload, `RECOMMEND \| <approach> \| reason` output line, advisory-only, frontier/`xhigh`) and (2) the plan review ensemble member (spec+plan payload, `SEVERITY \| artifact § section \| finding` output, same classification table, `[external:<model>]` attribution, 2-round cap, mid-tier/`high` default). Generalized the wrapper contract so the payload rubric header owns task framing and output format (wrapper is transport; old-contract wrappers keep working via the default format); updated both example wrappers to be payload-neutral. Updated "When to run it" with per-point skip conditions and the planning invocation sites.
2. **`skills/sdlc-plan/SKILL.md`** — Step 3d: added `External consult:` line to the APPROACH-DECISION block and the external deliberation consult procedure (run before selecting when approaches are compared; on disagreement present both positions to CD via AskUserQuestion). Step 5: external reviewer added to the review dispatch checklist and roster (same round as domain agents), findings attributed `[external:<model>]` in the classification table, re-review participation capped at 2 rounds, Domain Agent Reviews attribution rule extended. Two new Red Flags rows (external reviewer is not code-review-only; disagreement is signal, not authority — neither defer nor ignore). Integration section links the gate doc.
3. **`skills/sdlc-lite-plan/SKILL.md`** — Step 3: external reviewer joins the review roster when configured (plan-only payload, mid-tier/`high`, `[external:<model>]` attribution, 2-round cap, never blocks on availability). Worker Agent Reviews attribution rule extended; new Red Flags row; Integration section links the gate doc.
4. **`process/debate-protocol.md`** — § Cross-Vendor External Reviewer updated: first-class once configured; final pass at execution time, but *alongside* the internal roster at planning time (plan review is a single ensemble round, not a fix loop — independence is maximized by parallel review).
5. **`CLAUDE-SDLC.md`** — "Optional external review gate" paragraph retitled "External review gate — first-class when configured" and extended to name the planning integration points.

**Rationale:** The value of an external reviewer comes from vendor-level independence — a different training distribution fails on different edge cases. That independence pays most where decisions are structural and cheapest to change: planning. Reviewing a plan costs a fraction of reviewing a diff, and a caught phasing or approach error avoids the 10x cost of unwinding it during execution. Making participation default-on when configured (instead of per-run discretionary) converts an occasional second opinion into genuine cross-family deliberation, while the advisory-only + same-triage + 2-round-cap constraints keep the Manager Rule and anti-conformity safeguards intact.

---

## 2026-07-13: sdlc-audit Deep Verify — opt-in retroactive knowledge content verification (§6m)

**Origin:** ChronoCore handoff (`sdlc-audit-deep-verify-mode_handoff.md`), sibling to the promotion-verification-gate handoff. After two worked runs of the multi-judge pattern (18-entry promotion batch, then a 674-entry full-store retroactive sweep that found 45 real defects — ~1 in 15 entries — in content unreviewed since ingestion), CD asked where the retroactive version should live upstream. Decision: an opt-in `sdlc-audit` mode — not the default run (an order of magnitude costlier than the file-read/grep dimensions), not a standalone skill (audit already owns provenance reading, the §6c authority matrix, and the step 11 triage flow the findings feed).

**What happened:** The Promotion Verification Gate covers content entering the store, but nothing re-verified content already inside — entries predating the gate, drifted since ingestion, or contradicting the code they describe (worked example: an entry claiming all four effect classes route through a pipeline that its own `pipeline:` field showed handles two). The ChronoCore sweep also had to invent tooling mid-session (a comment-preserving YAML entry remover, because `yaml.safe_dump()` round-trips destroy hand-authored `# =====` banners) that should ship with the mode, not be re-derived per project.

**Changes made:**

1. **`skills/sdlc-audit/references/deep-verify.md`** (new) — Full mode spec: opt-in-by-name activation (mirrors the external-review-gate's disabled-by-default shape); orchestrator-run, never the `sdlc-compliance-auditor` subagent (needs `AskUserQuestion`, judge dispatches, egress disclosure); mandatory pre-flight `AskUserQuestion` with cost estimate, egress disclosure, and scope selection (full / domain / stale-only via §6h / incremental since last `audit-sweep` provenance entry); claims-vs-reference content scoping with ambiguous files flagged to CD, never silently decided; judge mechanics by reference to the Promotion Verification Gate with `KEEP|DEMOTE` verdicts (screening tier, fact-check lens, frontier tie-breaks, once-over of the keep-bound slate); embedded reusable scripts (payload extraction + comment-preserving entry removal); demotion mechanics; provenance logging; red flags.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — New §6m dimension (explicitly excluded from the default sweep and from the auditor subagent's scan; sequence note added after step 11 list). §6c authority matrix gains a demotion row: Promoted/`[READY TO PROMOTE]` → `[NEEDS VALIDATION]` is CD decision (step 11), proposed with multi-judge DEMOTE verdicts, **batch-level approval per discipline acceptable** with factual-error dissents and splits listed individually — resolving the handoff's open question on demotion authority (CD-gated, but at batch granularity; per-entry adjudication at 45-demotion scale is the same failure mode the tie-break judge exists to prevent). Step 11 intro gains Deep Verify as a third candidate source; step 11c gains the Demote path (comment-preserving removal, parking-lot restoration with judges' reasoning, `Promoted →` ledger pointer fixes, `last_updated` bump, one provenance entry per sweep).
3. **`skills/sdlc-audit/SKILL.md`** — Three-mode frontmatter with deep-verify trigger phrases ("deep audit", "deep verify", "verify the knowledge store", "full content sweep"); modes table and Input Resolution rows (`/sdlc-audit deep-verify [scope]`) with an explicit "never activates implicitly" rule; new Deep Verify Mode section (workflow summary + non-negotiable gates, details in the reference file); Integration and Reference Files updated; red-flag row against opportunistic deep-verifying during a compliance audit.
4. **`knowledge/provenance_log.md`** — `source-type` enum gains `audit-sweep`; conventions note that sweep entries record scope/judge-config/counts and serve as the incremental-scope boundary marker.
5. **`process/commands.md`** — `/sdlc-audit deep-verify [scope]` command row.
6. **`skeleton/manifest.json`** — `skills/sdlc-audit/references/deep-verify.md` added to `source_files.skills`.
7. **`agents/sdlc-compliance-auditor.md`** — Explicit exception under "Full coverage": §6m is opt-in and orchestrator-run; the auditor never executes it and reports it as "opt-in, not run" in coverage rather than as a gap.

**Rationale:** The ~1-in-15 defect rate in never-reverified content justifies the capability existing; the two-hour/dozens-of-dispatches cost profile justifies it never running by default — the handoff's own answer to "should full-store re-verification be scheduled?" is "no: available, opt-in, on the project's cadence." Routing findings through the existing step 11 triage instead of a parallel flow keeps one authority model (the §6c matrix) governing every marker transition in both directions. The judge mechanics are referenced from the gate rather than duplicated, so the two-tier/fact-check/once-over refinements land in one place. Not a `[contract-change]`: no knowledge-layer reference phrasing changed.

---

## 2026-07-13: Promotion gate — two-tier judging (screen cheap, escalate splits), mandatory fact-checking lens, frontier once-over

**Origin:** Retroactive gate run over ChronoCore's 674 already-promoted knowledge entries: 540 unanimous PROMOTE, 12 unanimous DEMOTE, **122 splits** — far too many for one-by-one CD adjudication. Sampling showed the splits were signal, not noise: Codex was fact-checking specific claims embedded in entries (PostgreSQL lock-escalation semantics, `REINDEX CONCURRENTLY` locking, OCI image-signing order, stale DORA thresholds, a 4xx-retry rule contradicting its own 429 guidance) while the Fable judge evaluated "is this a recognized general pattern?" and passed them. CD directives: run the initial external-judge pass at a low/mid tier with medium/high reasoning, elevate model and/or effort for tie-breaks, and add a final high-model once-over to verify the lower tiers got it right.

**What happened:** The gate as first shipped ran everything at the frontier tier (`xhigh`) and escalated every split to CD with full reasoning — a design that worked at prototype scale (18 entries, 5 splits) and collapses at batch scale (674 entries, 122 splits). The retro also exposed a judge-instruction gap: nothing required judges to verify embedded factual claims, so a pattern-recognition lens could PROMOTE entries containing checkable errors.

**Changes made:**

1. **`process/discipline_capture.md`** — Gate step 2 becomes the **screening tier**: external judge at a balanced/mid-tier `CODEX_MODEL` with `CODEX_REASONING_EFFORT=high`; subagent judge at `model: "opus"`. Step 4's split handling becomes **escalate model/effort, not CD**: one fresh frontier-tier tie-break judge (frontier `CODEX_MODEL` at `xhigh`, else `model: "fable"` subagent), blind to the split, same fact-checking instructions; the 2–1 majority applies with dissent recorded. New requirement in step 2: every judge's instructions must demand fact-checking of specific claims (numeric thresholds, version-sensitive benchmarks, protocol/API semantics, internal consistency) — a recognized pattern containing a false specific claim is a DEMOTE. New flag rule: a 2–1 PROMOTE overriding a factual-error dissent is flagged prominently to CD rather than buried by the majority. New step 5: **frontier once-over** — the full promote-bound slate (unanimous and tie-broken PROMOTEs) gets one final frontier-tier judgment as a single batch dispatch, blind to earlier verdicts, before CD presentation; its DEMOTEs are frontier dissents flagged to CD, never silently applied or discarded. Demote-bound entries are not re-reviewed — the risk is asymmetric (a wrong promotion compounds; a wrong hold-back waits a cycle).
2. **`process/external-review-gate.md`** — § Task-Based Model Selection effort guidance rewritten as "screen cheap, escalate splits" (frontier tier reserved for tie-breaks, the final once-over, and high-risk diffs); Knowledge-Judgment Wrapper section documents the tiers; example knowledge-judge wrapper default effort `xhigh` → `high` and its prompt gains the fact-checking instruction.
3. **`skills/sdlc-audit/references/compliance-methodology.md`** — §6c evidence-production note and step 11a updated to the tie-break flow (splits resolved by frontier-tier judge, factual-error dissents flagged to CD) plus the final frontier once-over before 11b, instead of per-split CD escalation.

**Rationale:** Two empirical lessons from the first at-scale run. (1) Split volume grows with batch size, so the human can't be the tie-breaker — but a frontier-tier judge can be, while CD keeps batch-level authority and gets the high-value splits (factual-error dissents) surfaced instead of all 122. (2) The most valuable verdicts came from fact-checking embedded claims, not recognizing patterns — so that lens is now a required judge instruction rather than an accident of which vendor's model happened to apply it. Screening at mid-tier/high is the cost floor that makes 674-entry batches feasible; the retro showed unanimity is the common case (82%), so frontier capacity is only spent where it pays: the ~18% that split, plus one batch-level once-over that backstops the screening tier on everything about to enter a knowledge store.

---

## 2026-07-13: Task-based model selection for Codex-backed external-review wrappers

**Origin:** CD directive in a cc-sdlc source session: when Codex is configured as an external reviewer, allow the orchestrator to choose model and reasoning effort per task (`codex -m <model> --config model_reasoning_effort="xhigh"`), resolving current model names at runtime from https://developers.openai.com/api/docs/models.

**What happened:** The wrapper contract gave the wrapper sole ownership of model choice, so every external review ran at the wrapper's single hardcoded configuration regardless of stakes — a docs-only diff and a knowledge-promotion verdict got the same model and effort.

**Changes made:**

1. **`process/external-review-gate.md`** — New "Task-Based Model Selection" section: Codex-backed wrappers pass through optional `CODEX_MODEL` / `CODEX_REASONING_EFFORT` env vars set by the invoking skill at the call site; wrapper defaults apply when unset. Model names must be resolved at runtime from OpenAI's model catalog (WebFetch https://developers.openai.com/api/docs/models), never recalled from training data — if the catalog can't be fetched, leave `CODEX_MODEL` unset rather than guess. Effort guidance: top-tier model at `xhigh` for high-stakes single-shot judgments (promotion verdicts, auth/payments/migrations/concurrency diffs), `medium` for routine second opinions. Wrapper-contract bullet updated (wrapper provides the *default* model, honors the passthrough); both Codex example wrappers updated — diff reviewer defaults effort to `medium`, knowledge judge to `xhigh`. Egress disclosure now names the actual model used.
2. **`CLAUDE-SDLC.md`** — External review paragraph mentions the env-var convention and the runtime model-resolution rule.

**Rationale:** External review quality should scale with task stakes, and the framework shouldn't embed model names that rot — OpenAI's catalog changes faster than this repo. Env-var passthrough keeps the wrapper contract intact (project still owns endpoint, egress policy, and defaults) while letting the orchestrator escalate a high-stakes judgment to a frontier model at maximum effort without editing the wrapper.

---

## 2026-07-13: Promotion Verification Gate — multi-judge evidence before knowledge promotion

**Origin:** ChronoCore handoff (`promotion-verification-gate_handoff.md`). In a ChronoCore session, 18 `[NEEDS VALIDATION]` parking-lot entries were bulk-promoted on the orchestrator's own judgment, violating the §6c authority matrix ("Proposed with evidence during interactive triage"). A retrofitted 3-judge review (self + Codex + Fable subagent) demoted 10 of the 18 — empirical proof that single-agent self-certification fails at exactly this transition. CD asked for the gate to be formalized upstream. Design was reviewed by two independent judges (Codex via `codex exec`, plus this session's own analysis) before implementation; both agreed with three amendments adopted below.

**What happened:** Promotion to a knowledge store had a CD-only authority rule but no defined evidence-production mechanism — step 11a said candidates need "evidence" without saying how it gets produced, so orchestrators substituted their own reasoning. Worse, `sdlc-archive` step 9c instructed applying `[READY TO PROMOTE]` as a silent "reasonable default," directly contradicting the §6c matrix.

**Changes made:**

1. **`process/discipline_capture.md`** — New "Promotion Verification Gate" section before the Promotion Workflow: neutral no-verdict evidence payload; two independent non-orchestrator judges (external `external-review-knowledge.sh` wrapper if configured, high-tier Fable/Opus subagent always, second subagent as fallback); `N | PROMOTE|DEMOTE | justification` verdict format; the orchestrator does not vote or break ties; unanimous-PROMOTE goes to CD as verified, unanimous-DEMOTE is not proposed, splits escalate to CD with each judge's full reasoning. Proportionality rule: full gate required for batches of 3+ entries or any weakly-evidenced entry; a single well-evidenced entry may present its evidence directly (lighter path replaces the judges, never the CD decision). Rules section's audit-triage carve-out now points at the gate as how CD's decision gets evidence.
2. **`process/external-review-gate.md`** — New "Knowledge-Judgment Wrapper" section: parallel convention `[sdlc-root]/external-review-knowledge.sh` (separate wrapper, not a mode flag — different artifact, different contract), stdin = neutral payload, stdout = `N | PROMOTE|DEMOTE | justification`, non-zero exit falls back to a second internal subagent, same egress rules, with a Codex example wrapper.
3. **`skills/sdlc-audit/references/compliance-methodology.md`** — §6c gains an "Evidence production" note wiring the matrix's evidence requirement to the gate; step 11a specifies when to run the gate before 11b and how verdicts map to the candidate list (unanimous-DEMOTE drops the candidate with dissent appended to the parking-lot entry).
4. **`skills/sdlc-archive/SKILL.md`** — Step 9c no longer applies `[READY TO PROMOTE]` as a silent default (that contradicted the §6c CD-only rule): validated entries are flagged as promotion candidates in the triage table for CD, or annotated `(promotion candidate — [date])` if the table is skipped. Added an explicit note that archival identifies candidates but does not adjudicate — the gate runs at promotion time (audit step 11), keeping archival fast by design.
5. **`CLAUDE-SDLC.md`** — External review gate paragraph mentions the parallel knowledge-judgment wrapper.

**Rationale:** A knowledge store entry is precedent every future agent reads, so a bad promotion compounds — and the ChronoCore data shows self-certification approves bad promotions at a >50% rate. The gate's key design points came from the prototype and the two-judge design review: judges must reason from a shared verdict-free payload (independence), the orchestrator must not tie-break (it is the actor being checked — "self + one subagent" is one independent opinion, not a majority), split votes need full reasoning surfaced (a bare tally hid the "adjacent entry ≠ corroboration" distinction that caught most bad promotions), and the gate is scoped to batches/weak evidence so it stays a followed rule rather than skipped ceremony. Not a `[contract-change]`: no knowledge-layer reference phrasing changed.

---

## 2026-07-11: sdlc-reflect prunes agent memories session-scoped

**Origin:** CD directives in a cc-sdlc source session: "sdlc-reflect should attempt to prune agent memories," followed by "part of the reflect process should be figuring out if those entries warrant being entered into the parking lots."

**What happened:** Agent memory hygiene existed only as sdlc-audit Dimension 8b — a project-wide sweep that runs at audit cadence. Between audits, memories invalidated by ongoing work (stale claims, drifted duplicate values, MEMORY.md files creeping toward the 200-line/25KB load cap) accumulated with no lighter-weight cleanup point. sdlc-reflect already closes out ad-hoc sessions and surveys the session's diff, making it the natural place for a session-scoped prune.

**Changes made:**

1. **`skills/sdlc-reflect/SKILL.md`** — Added Step 5 "Prune Agent Memories" (Report renumbered to Step 6): session-scoped prune covering agents dispatched this session and memories whose claims the session's diff invalidated. Reuses the Dimension 8b check definitions (contradicts-code, duplicate/drifted values, size-cap split, orphaned directory), gates prunes behind a confirmation prompt, requires source verification before deleting, and treats pruning as best-effort — parking lot capture remains the primary deliverable. Step 5 also runs a promotion check before any deletion: memory entries passing the Step 2 filters (reusable, non-obvious, actionable) — whether pruned or kept — are routed to discipline parking lots with context `[memory: {agent-name}]`, marked `[NEEDS VALIDATION]`. Frontmatter description, preconditions, report template, Red Flags, and Integration/DRY notes updated; added anti-trigger routing project-wide sweeps to sdlc-audit.
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — Dimension 8b note: sdlc-reflect applies the same checks session-scoped between audits and opportunistically routes generalizable memory entries to parking lots (lower bar than 8a's 2+-agent recurrence, same triage cycle); the audit remains the project-wide sweep and shouldn't be skipped on the assumption that reflect kept things clean.
3. **`CLAUDE-SDLC.md`** — Extended the post-session sdlc-reflect suggestion to mention the memory prune.

**Rationale:** Stale agent memories are a correctness risk (an agent trusting an invalidated claim is worse than one with no memory), and the session that invalidated a memory is the cheapest moment to catch it — the diff is already in hand. Pruning without a promotion check would silently discard insight: a memory invalidated by a change often documents why the old approach failed, which is exactly the kind of gotcha/anti-pattern signal the parking lots exist to catch. Scoping reflect's prune to the session keeps it fast and keeps the division of labor clean: reflect handles incremental hygiene and opportunistic capture, audit handles the exhaustive sweep and recurrence-based mining.

---

## 2026-07-09: Render precedes approval — never in sequence with the approval gate

**Origin:** CD directive in a cc-sdlc source session: "render should never happen in sequence with approval — it should precursor approval if the user chooses."

**What happened:** The post-skill render offer existed as a post-write step, but nothing constrained its position relative to approval gates. In practice this allowed the render offer to be bundled into the approval question, or the render to happen after approval as a follow-up — defeating the render's purpose as a review aid for the approval read. Worse, `html-rendering.md`'s re-render-on-plan-revision rule said "the HTML should reflect the approved plan," which reads as an instruction to render *after* approval.

**Changes made:**

1. **`process/html-rendering.md`** — Added "Render precedes approval — never in sequence with it" rule to the post-skill render offer section: the render offer is its own interaction, fully resolved (declined, or accepted with HTML delivered) before approval is requested; never bundled into the approval question, never rendered post-approval. Reworded the re-render-on-plan-revision rule: re-render after the final revision and *before* presenting for approval — CD approves what they see rendered.
2. **`CLAUDE-SDLC.md`** — Appended the sequencing rule to the post-deliverable render-offer paragraph.
3. **`skills/sdlc-plan/SKILL.md`** — Spec render offer (step 2) now states it must resolve before the step-3 approval gate. Step 6 (Prompt for Execution) gained a "Render precedes approval" pre-step: re-render the final revised plan before entering plan mode. Added two Red Flags rows (post-approval render offer; bundling render offer with approval question).
4. **`skills/sdlc-lite-plan/SKILL.md`** — Step 5 (Enter Plan Mode) gained the same "Render precedes approval" pre-step. Added a Red Flags row.

**Rationale:** The HTML render exists to give CD a better reading surface for the decision they're about to make. Sequencing it with or after the approval gate makes it decorative — the decision is already made by the time the render arrives. Fixing the sequencing at the process-doc level and at each approval gate ensures CD reviews the rendered artifact (if they opt in) before being asked to approve.

---

## 2026-07-09: Agent-memory hygiene — MEMORY.md cap enforcement, topic-file protocol, archive path fixups

**Origin:** Upstream handoff from a ChronoCore session that manually pruned `.claude/agent-memory/` (16 dirs, ~50 files) after severe drift — one `MEMORY.md` had reached 2628 lines, others contained content actively contradicting current code, duplicated tuned values with drifted numbers, and an orphaned predecessor-role directory. Web research confirmed Claude Code loads only the first **200 lines / 25KB** of `MEMORY.md` into the agent's system prompt (`MAX_ENTRYPOINT_LINES`), silently truncating the rest — and since entries append at the bottom, the *newest* notes are the ones dropped. The framework already named topic files as the remedy but only as a bare one-line suggestion with no size trigger, naming convention, or index framing, and nothing enforced the cap.

**Changes made:**

1. **`templates/agent-template.md`** — rewrote the Persistent Agent Memory guidelines into a real protocol: MEMORY.md-as-index framing, the 200-line/25KB cap with the "newest entries truncated" explanation, a split trigger (~180 lines), a topic-file naming/location convention (`.claude/agent-memory/{agent-name}/{topic}.md`, kebab-case, linked with one-line pointers), and explicit "replace drifted values, don't duplicate" guidance. Removed the redundant trailing `## MEMORY.md` section (its content is now covered above).
2. **`skills/sdlc-audit/references/compliance-methodology.md`** — split Dimension 8 into **8a Pattern mining** (promotion signal, unchanged) and **8b Hygiene** (new fix signal): size-cap violation (Major, MEMORY.md only — topic files uncapped), contradicts-current-code, internal duplication, orphaned directory. States the read-only auditor reports with file+line and the orchestrator applies fixes.
3. **`skills/sdlc-audit/SKILL.md`** — added a **Memory hygiene triage** to Step 3 folded into the existing prune `AskUserQuestion` batch (no second gate); routed fixes to Step 4's orchestrator (has Write), resolving the read-only-domain-agent limitation without needing write-capable domain agents. Updated the Dimension 8 summary line.
4. **`agents/sdlc-compliance-auditor.md`** — updated Dimension 8 summary to name 8a/8b; extended the Major severity class to include over-cap and code-contradicting `MEMORY.md`.
5. **`skills/sdlc-archive/SKILL.md`** — added **Step 9d Agent Memory Path Fixups (mechanical only)**: scoped strictly to the archived deliverable(s) and to rewriting `docs/current_work/...` → `docs/chronicle/...` paths this operation just broke. Explicitly defers all judgment-based pruning to audit Dimension 8b; folds any task-log deletions into the Step 9c triage table (with a defined fallback when 9c is skipped).
6. **`CLAUDE-SDLC.md`** — added the MEMORY.md cap + topic-file index pattern to the agent-memory bullet so target projects see the rule in their merged CLAUDE.md.

**Rationale:** Detection of agent-memory drift already existed (Dimension 8 flagged stale/contradicting memories) but there was no *fix loop* and no *prevention* — findings were flagged and nothing acted. The split here is deliberate: the template is the prevention layer (agents split before they hit the cap), archive Step 9d is the incremental mechanical cleanup (fix only what an archive itself breaks), and audit Dimension 8b is the periodic judgment-based sweep. The over-cap flag is a correctness issue, not cosmetic — an agent over 200 lines is silently running on a memory it can't fully see. Adapter phrasing contract checked: `.claude/agent-memory/` is the private scratchpad, distinct from the knowledge layer the neuroloom adapter transforms, so no `[contract-change]` and no paired plugin edit.

---

## 2026-07-09: sdlc-execute — plan size is not a confirmation trigger

**Origin:** Observed in a target-project execution session (D105, 7-phase plan). After emitting the Phase plan table, the executor paused and asked an `AskUserQuestion` about "execution scope" (full run vs. backend-only vs. Phase 1 only) — a checkpoint the skill never sanctions. The question's "Full sequential execution" wording also contradicted the parallelism the Phase plan itself declared.

**What happened:** The skill already forbids pausing for confirmation at dispatch time ("the plan is already approved") and treats post-summary stopping as a red flag, but nothing addressed the specific failure shape: plan *size* triggering an invented pre-execution scope checkpoint right after the Phase plan emission.

**Changes made:**

1. **`skills/sdlc-execute/SKILL.md`** — added an explicit rule after the Phase plan emission instructions: proceed directly to the first wave's PRE-GATE in the same response; plan size is not a confirmation trigger; a scope question re-litigates the `sdlc-plan` approval. Added a matching Red Flags row ("This plan is very large — I should confirm scope before starting").

**Rationale:** Approved plans are executed, not re-negotiated. Large plans pattern-match to a generic "confirm before a long autonomous run" instinct; the skill now names and blocks that instinct at the exact point it fired.

## 2026-07-08: Planning orchestrator is Fable OR Opus (CD's choice, not prescribed)

**Origin:** CD directive — "fable or opus should be the planning agent depending on what the user wants." The just-added cheat-sheet leaned toward Fable as the planning default; CD clarified it is a choice between the two top-tier models.

**Changes made:**

1. **`knowledge/architecture/model-tier-strategy.yaml`** — MTS6 reworded: run planning on a top-tier model, Fable OR Opus at CD's discretion (choose by task, quota, preference; e.g. Fable flagship vs Opus 4.8 1M-context), explicitly "the framework does not prescribe one; the load-bearing split is planning-premium vs execution-Sonnet." Checklist item updated to match.
2. **`CLAUDE-SDLC.md`** — session cheat-sheet: planning Model cell now "Fable **or** Opus (CD's choice)"; added a "Planning model is your call" note; alias block now offers both `ccplan` (Fable) and `ccplan-opus` (Opus).

**Downstream:** Documentation — propagates on next migration.

**Rationale:** Both models are premium and interchangeable for the planning seat; prescribing Fable would over-constrain a preference/quota decision. What actually matters is that planning runs premium and execution runs Sonnet — not which premium.

## 2026-07-08: Session model/effort cheat-sheet + launch-alias recipe in CLAUDE-SDLC

**Origin:** CD found switching the session model and effort by hand every time they change between planning and execution painful, and asked for an easier way. Claude Code session-config mechanics were verified against current docs via a claude-code-guide subagent.

**What happened:** MTS6 said "plan on Fable/high, execute on Sonnet/medium" but nothing told CD *how* to apply that without friction. Added a CD-facing session cheat-sheet with the lowest-friction mechanism (launch aliases that set both dials at once).

**Changes made:**

1. **`CLAUDE-SDLC.md`** — new "Session Model & Effort (your orchestrator seat)" subsection: a plan-vs-execution model/effort table, the `ccplan`/`ccexec` launch-alias recipe (`claude --model fable --effort high` / `--model sonnet --effort medium`), and the verified mechanics — both are launch flags; switching model mid-session can reset effort (re-check `/effort` after `/model`); `settings.json` persists `effortLevel` but not `model`; no named profiles; SessionStart hooks can't drive `/model`. Distinguished the session dial from the per-agent frontmatter tiers.

**Verified mechanics (Claude Code docs):** `--model` and `--effort` are launch flags (effort values low/medium/high/xhigh/max); `settings.json` supports `model` and a persisting `effortLevel` field, but `model` does not hot-reload; `/model` and `/effort` switch mid-session; no named-profile mechanism exists.

**Downstream:** Documentation — propagates on next migration. Closes the loop between the MTS6 rule and its day-to-day application.

**Rationale:** A tier rule nobody can apply frictionlessly gets ignored. The alias recipe makes the plan-wide/execute-narrow split a one-word launch choice, so the guidance actually gets followed.

## 2026-07-08: AI/ML domain provisioning rule (function coverage, not agent count)

**Origin:** CD asked whether an AI-adjacent domain always warrants a dedicated ai-architect + ai-engineer duo.

**What happened:** Refined G5. The precise requirement is that two opus-tier FUNCTIONS are covered — AI system design/judgment, and AI-aware correctness review — not that two named agents always exist. Whether to dedicate a pair depends on how central AI is to the product.

**Changes made:**

1. **`knowledge/architecture/model-tier-strategy.yaml`** — added an `ai_ml_provisioning` block under `assignment_rules`: principle (two functions, not two agents; a single opus ai-architect can fill both design + escalated review); a core/feature/incidental decision (dedicate the duo only when AI is the core value prop; for a feature, inject the AI review lenses into the existing opus software-architect + code-reviewer; incidental gets generic agents + a security reviewer); and a "provision by function coverage, not agent count; right-size per AOP5" rule. Added an "AI/ML architect + reviewer" row (opus/high) to `archetype_table` and cross-linked it from G5.

**Downstream:** Documentation/rule change — propagates on next migration.

**Rationale:** "Always a duo" would over-provision feature-level and incidental AI usage (roster bloat, violates AOP5/M4) while under-specifying what actually matters — the two opus functions. Framing it as function coverage lets a project satisfy G5 with existing opus reviewers when AI is peripheral, and dedicate specialists only when AI is central (avoiding generalist-masking). paire-appetit's organic llm-engineer + taste-intelligence-engineer split is the reference for the core case.

## 2026-07-08: Consolidated model/effort assignment rules + field survey of 5 installs

**Origin:** CD asked (1) what rules govern setting `model` and `effort` on agents, including AI/ML agents, and (2) to evaluate the sub-agents actually installed across sleeved, ChronoCore, paire-appetit, endlessgalaxystudios, and neuroloom to see whether real usage warrants additional rules.

**What happened:** The tier rules existed but were scattered across MTS1–MTS7 and the AGENT_SUGGESTIONS note — not a followable procedure. A survey of 113 installed agents validated the ladder and surfaced three additions: a both-axes reviewer invariant, a project-level baseline pattern, and the finding that `effort` is unset on 113/113 agents (a migration backfill, not just a go-forward default).

**Changes made:**

1. **`knowledge/architecture/model-tier-strategy.yaml`** — added an `assignment_rules` block: axes definition; model rules M1–M4; effort rules E1–E4; guardrails G1–G5 (G5 = AI/ML correctness is not evidence-checkable, so the correctness review escalates to opus/high regardless of implementation tier, and a passing run is never verification); `reviewer_invariant` (reviewer ≥ implementer on the model-OR-effort axis); `project_baseline` (raise the whole project's implementer model for systematically-hard domains, then differentiate reviewers by effort); `archetype_table` (keyed by role archetype, not agent name); and `survey_2026_07` recording the field evaluation and its consequences.
2. **`skills/sdlc-develop-agent/SKILL.md`** — pointed the frontmatter step at `assignment_rules` as the authoritative procedure for both `model` and `effort`, emphasizing archetype-keying.

**Survey findings (recorded in the YAML):** effort unset on all 113 agents; `code-reviewer` sonnet in 3/5 (violates the opus-reviewer default); security-review agents inconsistent (opus vs sonnet); deep-debugging split opus/sonnet; AI/ML implementers sonnet with non-escalated reviewers (confirms the G5 gap); ChronoCore runs implementers at opus wholesale (the project_baseline pattern); role names drift across projects (rules must key on archetype).

**Downstream:** Documentation/rule change — propagates to child projects on next migration. The installed agents in the five surveyed projects were NOT edited (out of scope — the ask was rules, not fixes); backfilling their model/effort per these rules is a separate migration/audit action a future session can trigger. A future sdlc-audit dimension could flag violations automatically.

**Rationale:** Real-world installs showed the rules were needed (broad inconsistency) and surfaced patterns pure theory missed — especially that when a hard-domain project runs everything at opus, effort becomes the ONLY remaining reviewer-differentiation lever, which is the strongest argument for treating effort as first-class rather than optional.

## 2026-07-08: Record tier-override decision (structural over per-call/Workflow)

**Origin:** CD follow-up in the same session — after verifying that per-dispatch model/effort override is reliable only in Workflow scripts (not interactive Task dispatch), CD asked whether the manual override was worth the effort or whether designating general-tier reviewer agents suffices, and whether Workflows could cover spec/plan reviews as well as implementation review loops.

**What happened:** Decided to keep the structural approach (MTS7 — dedicated opus review-only agents) and NOT adopt per-call override or a Workflow orchestration rewrite. Reasoning: the opus cross-cutting reviewers already carry the highest-value lenses; escalating each domain agent's own review adds only modest depth at large architectural cost; Workflows fit only the mechanical implementation review loop (spec/plan review are human-gated and cannot run headless); and interactive per-dispatch override is a tracked Claude Code feature (GitHub #62211/#64033) that could make a Workflow rewrite obsolete if it ships.

**Changes made:**

1. **`knowledge/architecture/model-tier-strategy.yaml`** — added a `tier_override_decision` record after MTS7 capturing the question, decision, rationale, and explicit `revisit_if` triggers (per-dispatch override becoming documented; evidence that sonnet domain review misses defects the opus reviewers don't catch).

**Downstream:** Documentation-only; propagates on next migration. No behavior change — records why the current structure was chosen so a future migration does not re-litigate it.

**Rationale:** The decision hinges on facts that will age (Claude Code's dispatch capabilities, the #62211/#64033 roadmap). Recording the triggers that would flip the decision keeps the choice auditable and cheap to revisit rather than re-deriving it from scratch later.

## 2026-07-08: Agent-tier structure decisions + External Review Gate

**Origin:** CD design session following the model-tier-strategy ingestion (below). CD asked three questions: (1A) split subagents into reviewer/implementer roles or genericize into stage-based roles (spec/plan/code reviewer)? (1B) how does a dispatching agent override a subagent's hardcoded model — is it even possible? (2) how can cc-sdlc use one LLM as planner/orchestrator and another (Codex or a local LLM) as implementer/reviewer, at minimum for an extra external review phase? Claude Code mechanics were verified via a claude-code-guide subagent against current docs before answering.

**What happened:** CD decided: (1) keep domain + reviewer hybrid — no stage-generic roles; (2) wire tiers explicitly (domain writers=sonnet, review-only agents=opus, recon=effort:low); (3) build an External Review Gate via Bash CLI. Verified mechanics that shaped the design: subagent model resolves in order `CLAUDE_CODE_SUBAGENT_MODEL` env → per-invocation param → frontmatter → inherit, but per-invocation model/effort override is only reliable in Workflow scripts, not interactive Task dispatch; `effort:` frontmatter (low|medium|high|xhigh|max) is stable and overrides session effort; external models integrate via MCP-wrapped tool, Bash CLI, or the existing OpenCode local-serving path.

**Changes made:**

1. **`knowledge/architecture/model-tier-strategy.yaml`** — added MTS7: realize the reviewer/implementer tier gap through the write/review agent split (reviewer-only agents at opus), NOT through stage-generic roles or unreliable interactive dispatch override. Unifies decisions 1A and 1B — the tier gap is achieved structurally because cc-sdlc already separates reviewer agents from writer agents.
2. **`agents/AGENT_SUGGESTIONS.md`** — added a "Model & effort defaults" note to the intro; added `Suggested model: opus` to code-reviewer, security-auditor, and software-architect (the cross-cutting review-only layer).
3. **`process/agent-selection.yaml`** — tier1 header comment codifying: review is a mode not a role; review-only agents carry the escalated (opus) tier; recon agents effort:low; do not add stage-generic reviewer roles.
4. **`process/external-review-gate.md`** (new) — canonical spec for the opt-in cross-vendor review gate: runs after the internal loop converges, activated by an executable `[sdlc-root]/external-review.sh` wrapper (stdin=rubric+context+diff, stdout=`SEVERITY | file:line | finding`), findings re-enter triage, external model never fixes, hard data-egress rules (never send secrets; prefer local models; state egress to CD; confirm before first hosted run), 2-round cap, anti-conformity handling. Includes local (Ollama) and hosted (Codex) example wrappers.
5. **`process/review-fix-loop.md`** — added Step E (External Review Gate) between the clean internal loop and commit.
6. **`process/debate-protocol.md`** — added "Cross-Vendor External Reviewer" section framing the external model as the most-independent ensemble member (Design Principle 1), subordinate to internal review, weighted for higher false positives.
7. **`skills/sdlc-review-code/SKILL.md`, `skills/sdlc-execute/SKILL.md`, `skills/sdlc-lite-execute/SKILL.md`** — added the optional External Review Gate step after each internal review loop.
8. **`CLAUDE-SDLC.md`** — Direct Dispatch Rules: added the optional external review gate with the egress caveat.
9. **`skeleton/manifest.json`** — registered `process/external-review-gate.md`.

**Downstream:** Child projects receive MTS7, the new process doc, and the skill/doc wiring on next migration (`process/*.md` glob already covers the new doc in sdlc-migrate §2.1). The gate ships disabled — projects opt in by adding an executable `external-review.sh`; cc-sdlc ships no default wrapper because model choice and egress policy are project decisions. No contract-phrase changes.

**Rationale:** CD's planner/implementer-split goal is served two ways. Within Claude Code: keep domain agents, make the existing reviewer layer the higher tier (MTS7) so reviewer≥implementer holds without depending on dispatch-override that only workflows support. Across vendors: the External Review Gate adds a genuinely independent reviewer (different vendor/architecture = different blind spots), which debate-protocol identifies as the highest-value ensemble addition — while keeping it subordinate to cc-sdlc's own review loop and the Manager Rule (external model reviews; domain agents fix). Stage-generic roles were rejected because they strip knowledge routing, duplicate the skill's own stage orchestration, and shrink ensemble diversity.

## 2026-07-08: Manager Rule — replace trivial-fix exception with Delegation Economics Exception

**Origin:** CD directive, same session as the model-tier-strategy ingestion below. The initial ingestion deliberately rejected the community "do the work directly when delegation would cost more" boundary; CD reviewed that call and reversed it: "I don't mind the manager doing changes if they're trivial or small or more cost efficient, but they should always be reviewed. The goal is to keep main context small."

**What happened:** The Manager Rule's trivial-fix exception (mechanical + single-site + self-evident) was the only permitted self-implementation. CD adopted a broader economic boundary: the manager may self-apply when delegation costs more than the change itself — monetarily (dispatch overhead re-loading context the manager already holds) or in main-context growth — with review as the non-negotiable backstop.

**Changes made:**

1. **`process/manager-rule.md`** — "The Rule" reframed from "never edits code files" to "dispatches by default; direct implementation only under the Delegation Economics Exception; never self-approves." Trivial Fix Exception replaced by the Delegation Economics Exception (4 conditions: small and bounded; no design judgment; context-neutral — no paging in code to decide HOW; reviewed). Trivial fixes always qualify. Hard boundaries kept regardless of economics: specs/plans stay agent-written (except WORDING), architectural/product decisions stay with agents/CD, high-risk domains allow only trivial-class fixes with MTS4 risk-escalated review. "No Size Exception" section removed (superseded); new "Mandatory Review of Manager-Applied Changes" section (self-applied ≠ self-approved; batch small changes into one review dispatch). "No Complexity Exception" retained. Failed-dispatch rule softened: re-dispatch with revised prompt first; a remaining gap that itself passes the economics test may be closed directly with review. Scope/completeness bullets updated to the same test (merge reconciliation still always dispatches — it's judgment). Session Scope single-file rule now applies the economics test.
2. **`skills/sdlc-plan/SKILL.md`, `skills/sdlc-lite-plan/SKILL.md`, `skills/sdlc-execute/SKILL.md`, `skills/sdlc-lite-execute/SKILL.md`** — inlined Manager Rule summaries updated to the economics exception + revised failed-dispatch rule; execute skills' review-loop fix triage now uses the economics test (self-applied fixes re-enter the next review round); lite-execute red flag updated.
3. **`skills/sdlc-review-code/SKILL.md`** — Step 5a fix triage rewritten around the economics test (trivial fixes always qualify); self-check wording updated; Step 5b review loop unchanged and remains mandatory for self-applied fixes.
4. **`skills/sdlc-create-reference-doc/SKILL.md`** — fix-loop triage aligned to the economics test.
4a. **`skills/sdlc-tests-run/SKILL.md`** — Manager Rule section updated: economics-qualifying fixes may be self-applied, verified by re-running tests, and reviewed; diagnosis-requiring fixes still dispatch.
5. **`CLAUDE-SDLC.md`** — Direct Dispatch Rules: "Never self-implement" → "Dispatch-first, with an economics exception" (review mandatory); "Iterate on CD feedback" allows economics-qualifying self-fixes with review.
6. **`process/overview.md`** — direct-dispatch description updated.
7. **`BOOTSTRAP-LITE.md`** — Manager Rule summary updated (complexity exception still absent; economics exception added with mandatory review).
8. **`knowledge/architecture/model-tier-strategy.yaml`** — "Relationship to the Manager Rule" preamble rewritten (exception adopted; economics never buys skipped review or absorbed design judgment); MTS1 anti-pattern retargeted at skipping review rather than at self-implementation per se.
9. **`knowledge/provenance_log.md`** — prov-2026-07-08-001 note amended to record the same-session adoption (branch not yet merged; note corrected rather than appended to avoid misleading future readers).

**Rationale:** The original rule optimized for role purity; CD optimizes for context economy. A dispatch that forces an agent to re-load context the manager already holds costs more tokens than the change, and reading the agent's handoff can grow main context more than typing the fix would. The redesigned exception keeps the two failure modes the old rule guarded against — scope creep via "small" changes and unreviewed manager output — behind explicit conditions: acquiring new context to self-implement disqualifies (that cost is the point of the rule), design judgment disqualifies, and review is unconditional. Self-applied is never self-approved.

## 2026-07-08: Framework Ingestion — Model & Effort Tier Strategy

**Origin:** Bulk ingestion via `ccsdlc-ingest` from community sources: three r/ClaudeAI thread screenshots (per-subagent `effort:` frontmatter; Fable-coordinates/Opus-verifies/Sonnet-executes/Haiku-scouts workflow splits; SDD with a top-tier coordinator), a community "fable-chief-agent" skill, and the DataCamp spec-driven development tutorial. CD specifically asked to explore Fable/Opus as the research/planning tier with Sonnet agents implementing.

**What happened:** The framework already assigned models per-agent (sonnet default, opus for design decisions, haiku for retrieval) and already enforced judgment/labor separation via the Manager Rule, but had no codified doctrine for WHY tiers map to work types, no effort-as-a-lever guidance, no risk-escalated-review rule, and no session-level guidance that planning should run on the top tier. The community sources supplied exactly that doctrine.

**Changes made:**

1. **`knowledge/architecture/model-tier-strategy.yaml`** — created with 6 rules (MTS1–MTS6): concentrate judgment at the top tier / delegate evidence-checkable work down; the tier ladder (top-tier orchestrator → opus hard delegated reasoning + high-risk review → sonnet default worker → haiku recon); effort as an independent per-role lever; reviewer tier ≥ implementer tier for high-risk domains; stack-difficulty tier adjustment; plan-wide-on-premium / execute-narrow-on-cheap session tiering. Includes an explicit "Relationship to the Manager Rule" preamble rejecting the community delegation-economics escape hatch.
2. **`templates/agent-template.md`** — frontmatter reference: added optional `effort:` field (low|medium|high|xhigh|max, with harness-version caveat); model guidance now covers the high-risk-review role for opus and points to the tier strategy file.
3. **`skills/sdlc-develop-agent/SKILL.md`** — frontmatter generation step: expanded `model:` guidance and added `effort:` field guidance with tier-strategy pointer.
4. **`agents/sdlc-reviewer.md`** — agent frontmatter checklist: validates optional `effort:` values.
5. **`skills/sdlc-plan/SKILL.md`** / **`skills/sdlc-lite-plan/SKILL.md`** — Agent Dispatch Protocol: read the tier strategy; planning sessions run on the highest-tier model available (MTS1/MTS6), recon goes cheap, high-risk phases get escalated reviewer tiers (MTS4).
6. **`skills/sdlc-execute/SKILL.md`** — EXECUTE dispatch protocol: MTS4 (reviewer ≥ implementer tier on high-risk) and MTS5 (escalate a thrashing worker instead of a third re-dispatch).
7. **`knowledge/agent-context-map.yaml`** — wired the new file to the architect role.
8. **`knowledge/architecture/README.md`** — structure listing updated.
9. **`CLAUDE-SDLC.md`** — Agent Conventions: new bullet on pre-assigned model/effort tiers and running planning sessions on the top tier.
10. **`disciplines/architecture.md`** — inventory table row + 3 `[NEEDS VALIDATION]` parking lot entries (effort-frontmatter support matrix, Sonnet-on-Rust thrash reports, per-phase Model/Effort column in the planning template).
11. **`knowledge/provenance_log.md`** — first provenance entry (prov-2026-07-08-001) recording sources and ingestion.
12. **`skeleton/manifest.json`** — added the new knowledge file.

**Skill candidates proposed:** none — the material is doctrine (knowledge + template/skill wiring), not a workflow warranting a new skill. The pasted fable-chief-agent skill was NOT adopted as a skill: its judgment/labor split is now knowledge, and its "do the work directly when delegation costs more" boundary conflicts with the Manager Rule, which stays authoritative.

**Downstream:** Child projects receive the new knowledge file, template fields, and skill guidance on next migration. No renames or contract-phrase changes — all new references use canonical phrasings, so no `[contract-change]` tag and no `skeleton/contract_changes.yaml` entry needed.

**Rationale:** CD's proposed split — Fable/Opus researching and planning, Sonnet implementing — is exactly the architecture the SDLC already enforces structurally (Manager Rule separates judgment from labor; agent frontmatter carries worker tiers). What was missing was the explicit doctrine making that split *deliberate*: run planning where judgment concentrates on the strongest model, keep workers cheap, and escalate only the review tier — not the implementation tier — when risk demands it. The DataCamp SDD material validated the existing spec → plan → execute gate structure without requiring changes.

## 2026-07-07: Agent-description example economy (drop `<commentary>`, tier example count, mandatory Do-NOT-use)

**Origin:** Upstream handoff from ChronoCore (`upstream-agent-description-economy_handoff.md`). ChronoCore measured that Claude Code injects every agent's full `description` frontmatter into every session's system prompt regardless of whether the agent is ever spawned — a permanent per-session tax, unlike the agent body (loaded only on spawn). ChronoCore's 16 agents, authored to the prior convention (4 `<example>` blocks each, every example with `<commentary>`), totaled ~44.5k characters (~11k tokens) of description payload per session. ChronoCore applied a local trim (~18-20k chars, ~5-6k tokens saved) and handed the convention change upstream since the framework's template/skill/reviewer — not the projects — was the driver.

**What happened:** The prior convention (agent-template.md, sdlc-develop-agent, sdlc-reviewer) mandated 2-4 `<example>` blocks per agent description, each with a `<commentary>` annotation restating why the routing is correct. Review of the trimmed ChronoCore agents found `<commentary>` blocks invariably restate the scope sentence or Do-NOT-use boundary already present in the same description (pure redundancy), and examples 3-4 invariably restate example 1's pattern with a different noun. The routing value concentrates in one typical-use example plus, for agents with a confusable sibling, one "seam" example distinguishing the two.

**Changes made:**

1. **`templates/agent-template.md`** — Description example rewritten to 1 `<example>` block (no `<commentary>`) plus a mandatory `Do NOT use for: X — use Y instead` boundary sentence. Comment-block frontmatter reference rewritten: explains the per-session token-tax mechanic, the confusability-tiering rule (1 example / 2 examples, never 3-4), the `<commentary>` drop, and the boundary sentence's promotion to mandatory.
2. **`skills/sdlc-develop-agent/SKILL.md`** — CREATE mode Step 2 (Frontmatter Generation) adds an explicit example-count-tiering procedure (detect confusable sibling via the Step 1 domain-overlap scan → 1 or 2 examples, never 3-4, no `<commentary>`, mandatory boundary sentence). Red Flags table entry on example blocks updated to the tiered rule. New Red Flags entry warns ENRICH mode against re-inflating a description's example count or reintroducing `<commentary>` when a source suggests a "great new scenario" — ENRICH enriches the body, not the description.
3. **`agents/sdlc-reviewer.md`** and **`process/skill-agent-review.md`** — Reviewer checklist updated in both: 1-2 examples tiered by confusability (3+ is Major), `<commentary>` blocks inside descriptions are Major, missing Do-NOT-use boundary sentence is Major (graduated from recommended to required — it's now the primary overlap-resolution mechanism once examples are capped at 2). "Do NOT use" section discipline broadened to cover both the body scope statement AND the description boundary sentence. Example-quality check extended: a 2nd example that isn't a genuine seam (just another typical-use case) is also Major.
4. **`agents/sdlc-reviewer.md`** and **`agents/sdlc-compliance-auditor.md`** — Dogfooded the new convention on the two framework agents installed into every target project. Both had 3 examples with `<commentary>` (pre-trim). Trimmed to 2 examples each (typical-use + a reciprocal seam example distinguishing single-file convention review from project-wide compliance auditing) with `<commentary>` dropped and a Do-NOT-use sentence naming the other agent.
5. **`skills/sdlc-migrate/SKILL.md`** — §3.1 (Identify Template-Derived Sections): added a clarifying note that the frontmatter `description` field is project/author-owned and is NEVER auto-updated by template changes — settles the handoff's open question explicitly rather than leaving it implicit. §3.4 (Downstream Impact Analysis): added an "Agent descriptions" scan row, a scan-step bullet, a findings-block example, and a gate-rule line so migration offers (but never auto-applies) a description trim to existing downstream agents that violate the new convention.

**Rationale:** The convention was the cost driver, not the individual projects — every agent scaffolded via `sdlc-develop-agent` inherited the 4-example-plus-commentary shape by default. Fixing it at the template/skill/reviewer level means future generated and migrated agents are born lean, and `sdlc-migrate` won't regress a project's already-trimmed descriptions back to the fat framework default (the field was never template-derived to begin with — §3.1 now says so explicitly instead of leaving it to be discovered by re-reading the migration code). Dogfooding the trim on `sdlc-reviewer`/`sdlc-compliance-auditor` themselves avoids the framework shipping two examples of the exact violation its own reviewer now flags in downstream agents.

---

## 2026-07-04: Route sdlc-handoff deferred work on effort, not artifact size

**Origin:** Downstream-project feedback. A session filed mechanical metadata backfill (a known, repeatable transform over ~76 production records) as "Deferred work — non-trivial" and got routed to `sdlc-lite-plan` when direct dispatch was correct. Root cause: the word "non-trivial" in the Step 3 routing table invited a *size/volume* reading, while the rest of that table keys on *approach*.

**Changes made:**

1. **`skills/sdlc-handoff/SKILL.md`** (Step 3 table) — Re-keyed the two "Deferred work" rows and the isolated-Issue row on **effort** (coordination cycles) instead of size. Added a criterion sentence above the table pointing at `collaboration_model.md` § Estimation Model: a known repeatable transform over N items is Light effort regardless of item count or production-write surface → direct dispatch. Preserved blast-radius/reversibility as an explicit plan trigger ("costly or hard to reverse") so high-volume irreversible writes still route to a plan. Encoded the escalation default in the Light-effort deferred row (default to direct dispatch; receiver escalates only if a real unknown surfaces).
2. **`skills/sdlc-handoff/SKILL.md`** (Red Flags) — Added an entry capturing the exact miscalibration: "It touches many records / writes to production, so it's non-trivial → plan it" → volume and write-surface aren't effort.

**Rationale:** Aligns the skill with the framework's existing Estimation Model, which already defines Effort as coordination cycles ("not wall-clock time") and explicitly lists cross-domain handoffs and verification depth — exactly the levers that make high-blast-radius work plan-worthy. Reusing the Effort vocabulary fixes the size-proxy miscalibration without minting a competing "approach clarity" axis, and keeps the fix from over-rotating into "scale never warrants a plan."
