---
type: handoff
slug: adr-amendment-vs-supersession-gate
created: 2026-10-03
status: pending
trigger: issue
recommended_next_skill: sdlc-lite-plan
source_session_summary: "D152 (Neuroscape) execution: two planning-time ADR amendments were appended to ADR-18 and ADR-27 in place, contradicting adr-practice.md; CD ordered them moved to new ADRs (ADR-35, ADR-36; 32-34 were taken)"
active_deliverable: D152
related_files:
  - .claude/sdlc/process/adr-practice.md
  - .claude/skills/sdlc-plan/SKILL.md
  - .claude/skills/sdlc-lite-plan/SKILL.md
  - docs/architecture/decisions/adr-30_content-hash-shadow-transition-rollout.md
  - docs/architecture/decisions/adr-26_collection-finish-bucket-key-and-staged-rollout.md
  - docs/architecture/decisions/adr-01_composable-query-syntax-compilation.md
  - docs/architecture/decisions/adr-18_pricing-spine-source-keyed-artifact-and-cache-retention.md
  - docs/architecture/decisions/adr-27_per-printing-market-grain-digimon-gundam.md
---

# Handoff: cc-sdlc lets "new constraint" ADR edits ship as in-place amendments

> **Origin:** written in the Sleeved repo (`endless-galaxy-studios/sleeved`, deliverable D152) and moved here on 2026-10-03. All `related_files` and file:line references in this document are relative to the **Sleeved** repo, not cc-sdlc; the cc-sdlc files they correspond to are `process/adr-practice.md`, `skills/sdlc-plan/SKILL.md`, `skills/sdlc-lite-plan/SKILL.md` and the ADR template.

**Audience:** the cc-sdlc maintainers (upstream `Inpacchi/cc-sdlc`, installed here at sdlc_version 1.7.0 per
`.sdlc-manifest.json`). This file is written so that a session in the cc-sdlc repo can act on it without the D152
conversation.

## Why this is a handoff

During D152 (Sleeved's fifth TCG, Neuroscape), the plan's reviewers wrote two "D152 Amendment" sections and appended
them to the bottom of two existing, Accepted ADRs (ADR-18 and ADR-27), each headed `(PROPOSED)` with its own
approval checklist. They went through several review rounds and were nearly accepted in that form. Only when CD was
asked to tick the CD-acceptance box did the checklist's own wording surface the conflict: the amendments add new
constraints, which `adr-practice.md` says is a narrative edit that requires a **superseding ADR**, never an in-place
edit. CD ordered both moved into new ADRs (ADR-35, ADR-36; CD's answer named ADR-32/ADR-33, but those numbers and
ADR-34 are claimed by the unmerged D162/D162c/D162a work). The source session was executing D152 Phase 5; it should
not also own the cc-sdlc process fix.

The failure is process-level, not a one-off: nothing in the planning or review flow stopped the appended form, and the
repo already contains earlier appended amendments (see Evidence), so the pattern had precedent that looked legitimate.

## What needs to happen

Make it hard to ship an in-place ADR amendment that the immutability rule forbids. Candidate changes, for the receiving
session to scope and choose among:

1. **Gate at plan time.** `sdlc-plan` / `sdlc-lite-plan` have an ADR-CONTEXT step that only READS active ADRs
   (they cite `adr-practice.md` for "the full three-function model (READ / PRODUCE / RESPECT)"). Add a PRODUCE-time
   check: when a spec or plan proposes to change, extend or add constraints to an existing ADR, the plan must name a
   new ADR number and `Supersedes:` / partial-supersession frontmatter, not an "Amendment" section.
2. **Make the rule's exception mechanical.** `adr-practice.md` allows only two in-place edits (placeholder corrections
   and rendering updates) and says "Everything else ... adding new constraints ... requires a superseding ADR. When in
   doubt, supersede." Provide a one-line decision test and a partial-supersession template (the repo's ADR-23 /
   ADR-19 are good structural precedents) so the compliant path is the easy path.
3. **Review roster / audit check.** Add a check to plan review and to `sdlc-audit` that flags a heading matching
   `## .*(Amendment|Addendum)` appended to an ADR whose body adds or removes constraints, and flags any ADR section whose
   status line says "(PROPOSED)" inside an Accepted ADR.
4. **Rename the checklist item.** The approval checklist said "the trailer form", which is a label that hid the
   real question (append in place vs new superseding ADR). Use plain wording in the ADR template's approval checklist.
5. **Decide what "Amendment trailer" means.** `adr-practice.md` mentions an `## Amendment` trailer only for the two
   narrow exceptions, yet the repo's own amendments use the word for substantive additions. Clarify or retire the
   term so it cannot be read as permission.

## Evidence

- **The rule:** `.claude/sdlc/process/adr-practice.md:14-16` ("ADRs are append-only facts ... you write a new ADR that
  `Supersedes` the prior one"); `:84-92` ("Amendments vs. Supersessions": two narrow exceptions; "adding new
  constraints, or removing existing constraints — is a narrative edit and requires a superseding ADR. When in doubt,
  supersede."); `:37` and the Contradiction Handling section ("Never edit the prior ADR in place.").
- **Skills that cite the practice but only for context:** `.claude/skills/sdlc-plan/SKILL.md:308` and
  `.claude/skills/sdlc-lite-plan/SKILL.md:205` ("See `[sdlc-root]/process/adr-practice.md` for conventions,
  immutability rules, and the full three-function model (READ / PRODUCE / RESPECT)"); the step they describe
  (ADR-CONTEXT) reads `_index.md` and passes active ADRs to agents as constraints.
- **Prior appended amendments in this repo** (verified by grep and `git log -S`): ADR-30 `## D160b Amendment`
  (`adr-30_...md:284`, added 2026-09-28 in commit 9c91ff7cb, text says "Append-only. Nothing above this heading has been
  edited. Where this amendment and the text above disagree, this amendment wins."); ADR-26 `## ADR-25 Amendment` (`:109`)
  and `## ADR-28 Amendment` (`:148`), added 2026-09-09 in commit 95957b956; ADR-01 `## D76 Addendum` (`:188`, 2026-06-20,
  commit 910997f13); ADR-18's own earlier `## Decision 4 — ADR-16 Enforce-Mode Amendment` (`:102`). Proper
  supersessions also exist (ADR-19 over ADR-16, ADR-23 over part of ADR-14, ADR-10 by ADR-13), so both mechanisms are in use.
- **The D152 case:** `docs/architecture/decisions/adr-18_...md` from the heading `## D152 Amendment — The store Source Key,
  Store-Only Market Participation, and the Printing-Grain Price Rule (PROPOSED)` (about line 287) and `adr-27_...md`
  from `## D152 Amendment — A Third printingGrain Kind (declaredSet) ...` (about line 420). Their checklists carried the
  item "CD acceptance — including ... the trailer form". D152 plan: `docs/current_work/planning/d152_neuroscape_integration_plan.md`,
  addendum "2026-10-02/03 Phase 4 close-out and Phase 5 decisions". ADR-30 also carries a pending
  `## D152 Amendment` (`adr-30_...md:726`), already on `main` before CD's decision.
- **CD's decision (2026-10-03, chat):** after being shown the precedent and the rule, CD chose "new ADR" for both
  (named ADR-32/ADR-33 in chat; filed as ADR-35 from the ADR-18 amendment and ADR-36 from the ADR-27 amendment,
  because 32-34 were already claimed), and asked for this handoff. The appended sections have since been removed
  from ADR-18 and ADR-27; the line numbers above describe the pre-move state.
- **Observation (CD, in their own words):** "has any other ADR been modified as such? would this be the first time we
  modify ADRs?" — the precedent existed, which is why the pattern did not look wrong during review.
- **Related findings:** the source session's own question to CD mislabelled the item as a "commit-trailer form";
  the real question was append-versus-supersede. The checklist wording invited that misreading.

## Recommended next step

Open a new session in the cc-sdlc repo and run: **`/sdlc-lite-plan`** with this file as the seed.

Reasoning: the change spans the planning skills, the review roster, `sdlc-audit` and the ADR template, and the first
move (where the gate lives) is worth a reviewed plan before editing framework files. If the maintainers prefer to
explore whether the rule itself should change (e.g. allow a defined amendment form), start with `/sdlc-idea` instead.

## Open questions

- Is the rule right as written, or are partial, additive amendments (like ADR-30's D160b Amendment, which declares
  itself append-only and says it wins on conflict) a legitimate third form the framework should define and constrain?
  If so, `adr-practice.md` should say so; today the rule and the repo practice disagree.
- Should the existing appended amendments (ADR-01, ADR-26, ADR-30, ADR-18 Decision 4) be retro-fitted, grandfathered,
  or flagged by the new audit check as known exceptions?
- Where does the gate belong: plan time (cheapest), review roster, execution commit gate, or all three? The execution
  skills already scan for ADR crystallization signals (`sdlc-execute/SKILL.md:422`, `sdlc-lite-execute/SKILL.md:368`);
  do they also need a "did this edit an Accepted ADR in place?" check?
- Do the planning agents (here, `software-architect` and `data-engineer`) load `adr-practice.md` at all when writing
  ADR text, or only the skills do? This session did not verify it; the receiving session should.

## Out of scope (do NOT pursue)

- Do not rewrite or move Sleeved's existing ADRs from the cc-sdlc session; the Sleeved repo's D152 session is already
  moving its two amendments into ADR-35 and ADR-36.
- Do not change how supersession ADRs are numbered or indexed; only the decision to create one is in question.
- Do not widen this into a general ADR-quality review; the failure here is the in-place-edit path only.
