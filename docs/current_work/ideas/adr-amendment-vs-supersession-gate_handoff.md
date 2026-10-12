---
type: handoff
slug: adr-amendment-vs-supersession-gate
created: 2026-10-03
status: pending
trigger: issue
recommended_next_skill: sdlc-lite-plan
source_session_summary: "A project's planning run appended two amendments that added constraints to Accepted ADRs, in place, contradicting adr-practice.md; CD had them moved into new, superseding ADRs"
active_deliverable: null
related_files:
  - process/adr-practice.md
  - skills/sdlc-plan/SKILL.md
  - skills/sdlc-lite-plan/SKILL.md
---

# Handoff: z-sdlc lets "new constraint" ADR edits ship as in-place amendments

## Why this is a handoff

In a project running z-sdlc, a plan's reviewers wrote two amendment sections and appended them to the bottom of two existing, Accepted ADRs, each headed `(PROPOSED)` with its own approval checklist. They went through several review rounds and were nearly accepted in that form. Only when CD was asked to tick the acceptance box did the checklist's own wording surface the conflict: the amendments added new constraints, which `adr-practice.md` calls a narrative edit that requires a **superseding ADR**, never an in-place edit. CD had both moved into new ADRs.

The failure is in the process, not a one-off: nothing in the planning or review flow stopped the appended form, and the project already had earlier appended amendments, so the pattern had precedent that looked legitimate.

## What needs to happen

Make it hard to ship an in-place ADR amendment that the immutability rule forbids. Candidate changes, for the receiving session to scope and choose among:

1. **Gate at plan time.** `sdlc-plan` and `sdlc-lite-plan` have an ADR-CONTEXT step that only reads active ADRs (they cite `adr-practice.md` for the READ / PRODUCE / RESPECT model). Add a PRODUCE-time check: when a spec or plan proposes to change, extend or add constraints to an existing ADR, the plan must name a new ADR and its `Supersedes:` (or partial-supersession) frontmatter, not an "Amendment" section.
2. **Make the rule's exception mechanical.** `adr-practice.md` allows only two in-place edits (placeholder corrections and rendering updates) and says everything else, adding constraints included, requires a superseding ADR: "When in doubt, supersede." Provide a one-line decision test and a partial-supersession template, so the compliant path is the easy one.
3. **A review and audit check.** Plan review and `sdlc-audit` flag a heading like `## ... Amendment` or `## ... Addendum` appended to an ADR whose body adds or removes constraints, and any section marked "(PROPOSED)" inside an Accepted ADR.
4. **Plain checklist wording.** The approval checklist's item for this was a label ("the trailer form") that hid the real question: append in place, or a new superseding ADR. The ADR approval checklist `adr-practice.md` describes should ask it plainly.
5. **Decide what "Amendment trailer" means.** `adr-practice.md` mentions an `## Amendment` trailer only for the two narrow exceptions, yet projects use the word for substantive additions. Clarify or retire the term so it can't be read as permission.

## Evidence

- **The rule:** `process/adr-practice.md`, the opening (ADRs are append-only; a newer choice is a new ADR that `Supersedes` the prior one), § Amendments vs. Supersessions (two narrow exceptions; adding or removing constraints requires a superseding ADR), and the Contradiction Handling section ("Never edit the prior ADR in place").
- **The skills cite the practice only for reading:** `skills/sdlc-plan/SKILL.md` and `skills/sdlc-lite-plan/SKILL.md` point at `adr-practice.md` for conventions; their ADR-CONTEXT step reads the ADR index and passes active ADRs to agents as constraints, and nothing checks what a plan writes into an ADR.
- **Precedent in the project:** several Accepted ADRs already carried appended "Amendment" or "Addendum" sections, one declaring itself append-only and saying it wins where it disagrees with the text above it, alongside proper supersessions. Both mechanisms were in use, which is why the appended form didn't look wrong in review.

## Recommended next step

Open a session in the z-sdlc repo and run **`/sdlc-lite-plan`** with this file as the seed. The change spans the planning skills, the review roster, `sdlc-audit` and `adr-practice.md`, and where the gate lives is worth a reviewed plan before editing framework files. If the rule itself should change (for example, to allow a defined, constrained amendment form), start with `/sdlc-idea` instead.

## Open questions

- Is the rule right as written, or are partial, additive amendments (append-only, declaring that they win on conflict) a legitimate third form the framework should define and constrain? Today the rule and some projects' practice disagree.
- Should a project's existing appended amendments be retrofitted, grandfathered, or flagged by the new check as known exceptions?
- Where does the gate belong: plan time (cheapest), the review roster, the execution commit gate, or all three? The execution skills already scan for ADR crystallization signals; do they also need a "did this edit an Accepted ADR in place?" check?
- Do the planning agents load `adr-practice.md` when they write ADR text, or only the skills do?

## Out of scope

- Changing how supersession ADRs are numbered or indexed; only the decision to create one is in question.
- A general ADR-quality review; the failure here is the in-place-edit path only.
