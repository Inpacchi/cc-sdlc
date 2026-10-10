# Design: factory gaps 1 and 2 (production-touching plans, splitting deliverables)

**Status:** gap 2 built (quantile `f5ef1a9`, cc-sdlc `68782df`). Gap 1 reversed by CD and awaiting redesign; the gap 1 sections below are the superseded first design, kept for reference. **Date:** 2026-10-09, updated 2026-10-10.
**Source:** `software-factory_handoff.md` § "Gaps found 2026-10-09", items 1 and 2. Item 3 (deliverables registered outside the factory) is CD's.
**Cross-checked** with Codex (read-only, against quantile `f5098bf`) and a Fable reviewer. Their main corrections are folded in below.

## CD's decisions (2026-10-09)

- **Gap 2 first; built.** CD accepted recommendations 5, 6 and 7:
  - merging the split PR approves it, and the parts then wait for `factory:go`;
  - parts reuse the parent's approved spec when the split names it;
  - the prerequisite-tracking column and checks are built together.

  The defaults stand: a part can't split again, and CD closes the parent by hand. Follow-ups per segment wait for gates.
- **Gap 1 reversed.** CD wants:
  - a **production-capable runner** that does production steps without CD's hands, with **per-step approval** through labels or tags;
  - **no new PR per approval:** one long-standing PR with the gates posted as steps and approved in place, or another mechanism. CD isn't settled on the PR mechanics.

  That replaces recommendation 1 ("plans mark them for CD to run") and the segment-per-PR flow below. A redesign comes next, with its security boundary: keys, which steps, approval binding, audit. The gate structure in plans (§ Gates) likely survives, with the factory running CD gates after approval instead of CD.
- The handoff (`software-factory_handoff.md`, gaps section) records the same decisions.

## Principle (first design; superseded for gap 1)

Plans mark the steps that need production. The factory stops at them, and CD runs them. No agent gets production or host access. One mechanism, **gates**, handles both CD steps and waits on other deliverables.

## Gates (framework, cc-sdlc)

1. **The plan templates (full and lite) gain gates between phases.**
   - `### Gate G<n> (CD): <title>`: a step only CD runs. Anything needing production data or host files, deploys, migrations on production, restarts, backup gates and observation windows.
   - `### Gate G<n> (prerequisite): <ID> Complete`: a wait on another deliverable.
   - **A CD gate has:**
     - preconditions;
     - a runbook as a checklist;
     - **required report-back fields**, whenever a later phase consumes CD's output (snapshot identity, hashes, timings);
     - rollback.
   - **Phases stay factory-only.** D11b's Phase 3 "code + Deploy step 1" becomes Phase 3 followed by Gate G1.
2. **Gates don't count toward the 7-phase cap.**
3. **The last item is always a factory phase** (records). It reads CD's report-backs from the issue and writes the result doc, so a plan that ends in a live window still has a closer that sets the catalog to Complete.
4. **The catalog gains a `Depends on` column** (IDs). This builds most of `prerequisite-tracking_handoff.md`:
   - sdlc-status lists blocked deliverables and forgotten prerequisites;
   - plan/execute check the column;
   - the split step writes it.
   - A dependency that blocks the whole deliverable is a prerequisite gate before Phase 1.
5. **Execute skills in headless mode stop before every gate** (CD, or an unmet prerequisite). Interactive runs show the CD gate's runbook and wait for the person.
6. **Release:** minor bump. It adds a template structure and a catalog column, both additive with defaults.

## Gap 1 in the factory (quantile)

1. **Triage:** the decision marker gains `production: true|false`. An issue that needs production is never `direct`; a direct issue that turns out to need it returns `rescope`.
2. **Plan stage:**
   - the plan result gains `gates`: `{id, kind, title, report_back[]}`. The guard checks it against the plan's gate headings.
   - the PR description's Review focus lists the CD gates and their runbooks. CD reviews the runbooks when approving the plan, because agent-written commands are untrusted until then.
3. **Approved plan pinned:** factory-advance records the merged plan's blob SHA. Every execution run refuses a plan whose blob changed without a new approved plan PR.
4. **Execution in segments:**
   - a run executes consecutive phases up to the next gate on branch `factory/<n>-impl-s<k>`, opens that segment's draft PR, and returns a new status `handoff`;
   - the report job posts a handoff record `<!-- factory-handoff: {"gate","plan","blob","pr","next_phase"} -->` plus the gate's checklist, and sets state label **`factory:handoff`**. factory-resume ignores it, so a casual reply restarts nothing.
   - restart state is the partial result doc and plan checkboxes in the merged segment PR (implement's schema has no `notes`).
5. **Continuing:** CD merges the segment PR, does the gate, posts the report-back if one is required, then adds `factory:go`. factory-release gains a handoff case. It:
   - reads the latest handoff record;
   - checks the segment PR is merged and required report-backs are present;
   - dispatches factory-implement with the plan, blob and next phase;
   - consumes the handoff (label swap), so a stale or duplicate `go` does nothing.

   For a prerequisite gate, `go` is accepted only if the prerequisite's catalog status is Complete.
6. **Failure:** if CD's gate fails (for example a deploy is rolled back), CD comments and either fixes forward and adds `go`, or re-plans (`factory:triage`). No automation in v1.
7. **Unchanged, for the record:** D3 already lets planning agents read production data, the non-personal columns only, while using the open web. D3 accepts that, bounded by data sensitivity. This design adds no production access.

## Gap 2 in the factory (quantile)

1. **The plan result gains status `split` with `parts`:** for each part a suffix, title, scope, tier, `depends_on` and rationale. A split can come from the spec run or the plan run.
2. **Split PR on `factory/<n>-split`** (docs only, its own advance job). It adds catalog rows for the parts (IDs: the parent's Dnn plus letters) with `Depends on`, sets the parent row's `Depends on` to its parts, and adds a short split record. The parent stays Draft; no new lifecycle status. **The merged catalog is the source of truth,** so CD can edit or redo the split before merging.
3. **On merge,** the advance job files part issues **idempotently**: a per-part marker on the parent, find-or-create, safe to re-run. Each part gets:
   - a sub-issue link to the parent;
   - a `factory-id` reservation marker;
   - a triage marker carrying its tier, plus `factory:ready-to-plan`;
   - held: it waits for `factory:go`.

   The parent's factory label is cleared last. CD closes the parent by hand.
4. **Claim job:** the reservation regex captures the letter suffix separately, so the numeric max (`sort -n`) stays right.
5. **Not in v1:**
   - splitting a part again (a too-big part stops with `needs-input`);
   - native `blocked_by` links (the catalog is the truth; they could mirror it later);
   - auto-dispatch when a prerequisite completes;
   - auto-closing the parent;
   - a production-capable tier;
   - a named-operations job.

## Open dependencies

- **A `full` part whose parent spec CD already approved** would re-run the spec stage unless the plan stage's mode chooser reads the catalog's Spec column. That is the same bridge as handoff item 3 (CD's).
- **Contract versioning (Codex):** the new statuses (`handoff`, `split`) and fields change the result contracts. They ship with end-to-end tests: guard unit tests, a smoke case per status, and a dry run on a test issue.

## Decisions for CD (as first asked; answered above)

1. Should an agent ever hold the keys to the production box (a new runner with per-step approval), or do plans mark those steps for you to run? **Recommended:** plans mark them.
2. When a plan reaches one of your steps, the factory stops, opens a PR for the work so far and posts your checklist. You merge, do the step, then add `factory:go`. **OK?**
3. Should your steps count toward the plan's 7-phase limit? **Recommended:** no.
4. When a plan says "Phase 6 waits on D11a": run Phases 1–5 and stop, or don't start until D11a is done? **Recommended:** run 1–5 and stop.
5. Splits: approve by merging a split PR that adds the parts to the catalog (you can edit them first). Then:
   - (a) parts wait for your `factory:go` before planning, or
   - (b) start planning on their own.

   **Recommended:** merge to approve, then (a).
6. When the parent already has an approved spec: parts reuse it, or each part gets its own spec run? **Recommended:** reuse it when the split PR names it. This overlaps the third gap.
7. Build the prerequisite-tracking handoff's catalog column and checks as part of this? **Recommended:** yes.

**Defaults unless CD says otherwise:**
- follow-ups are filed per segment PR;
- a part can't split again;
- the parent issue is closed by hand.
