# ADR Practice

Shared reference for Architecture Decision Record (ADR) conventions. Linked from planning, execution, and review skills so the language stays in sync. Edit here once; all skills pick up the changes on their next invocation.

## What an ADR is

An ADR captures a single significant architectural decision: the context that forced the choice, the options considered, the option taken, and the rationale. ADRs are durable constraints that agents must respect.

- **Home:** `docs/architecture/decisions/adr-NN_{slug}.md`
- **Template:** `[sdlc-root]/templates/decision_record_template.md`
- **Catalog:** `docs/architecture/decisions/_index.md`
- **Owner:** The architect role drafts; affected domain agents review; CD approves. Other agents read and respect active ADRs.

## Immutability

ADRs are append-only facts. Once Active, you do **not** edit a prior ADR to reflect a newer choice — you write a new ADR that `Supersedes` the prior one and link both directions via frontmatter. This preserves the reasoning chain: someone later can reconstruct *why* the old decision was made and what changed.

## Crystallization Signals

An ADR is warranted when work introduces any of:

- A new service boundary (new container in the C4 sense, or a new arrow between existing containers)
- A new external library or framework (or replaces an existing one)
- A new data-model shape (new table, relationship type, or invariant)
- A new dependency edge (A now calls B where it didn't before), or an existing edge reversed
- A new protocol surface (new API endpoint family, new event stream, new MCP tool signature)
- A new fitness function (CI check, lint rule, import-boundary enforcement)
- A configuration safety default that encodes a decision (flipping a lenient default to strict for durability)
- A codified defensive pattern (new base class, middleware, guard, or invariant enforcement that encodes a learned failure-mode response)

If none of these apply, the work is conformance to existing ADRs — note that explicitly in the result doc (`Architectural decisions: none — conforms to existing ADRs`) rather than producing a new ADR.

## Contradiction Handling

If proposed or in-flight work appears to contradict an active ADR, surface the conflict rather than silently resolving it. Contradictions are CD's to resolve, with three paths:

1. **Supersede** — write a new ADR with `Supersedes: ADR-N` in frontmatter; the old ADR's status becomes `Superseded by ADR-M`. Ship the supersession ADR in the same commit as the code that relies on the new decision.
2. **Conform** — revise the approach to match the active ADR.
3. **Reject** — if neither supersession nor conformance is acceptable, the deliverable itself needs to change.

Never edit the prior ADR in place. Never merge work that contradicts an active ADR without also merging the supersession ADR in the same commit.

## Three Functions

ADRs integrate into SDLC skills via three functions. All three are skip-if-absent: if `docs/architecture/decisions/` does not exist in the project, the step is a no-op.

### READ — discovered as constraints

Planning skills (`sdlc-plan`, `sdlc-lite-plan`) scan `docs/architecture/decisions/_index.md` during discovery, list active ADRs relevant to the work's domain, and include them in agent dispatch prompts as technical constraints. This prevents agents from re-litigating decided questions.

### PRODUCE — drafted when crystallized

Execution skills (`sdlc-execute`, `sdlc-lite-execute`) run an architecture-decision check at the result-doc step. If the work crystallized a new architectural choice (see signals above), they dispatch the architect agent to draft the ADR before marking the deliverable complete. The ADR is committed with the code that crystallized it — same commit.

Incident skills (`sdlc-debug-incident`) run the same check at postmortem closeout — remediations that changed architecture produce an ADR with the postmortem cited as `triggered_by`.

### RESPECT — enforced at review

Review skills (`sdlc-review-code`) apply an ADR-drift lens: for each active ADR relevant to the changed files, verify the change does not violate the ADR's decision. Drift gets flagged as `major` with category `adr-drift`. Intentional supersessions require a matching supersession ADR staged in the same diff; missing supersession is itself an `adr-drift` finding.

## Lightweight Variants

For decisions that warrant a record but do not need the full template structure:

**Y-Statement format** — single paragraph:
> In the context of *<problem>*, facing *<constraint>*, we decided for *<option>* and against *<alternatives>*, to achieve *<benefit>*, accepting that *<cost>*.

**Lightweight ADR** — Status, Date, Context (1-3 sentences), Decision, Consequences (Good/Bad/Mitigations).

Both variants live in the same `docs/architecture/decisions/` directory with the same numbering.

## Negative Constraints: "What This ADR Forbids / Does NOT Decide"

Any ADR that decides "X uses pattern Y" should also explicitly document "X must NOT do Z" — the negative constraints prevent future agents from drifting toward the wrong shape. This applies especially to ADRs drafted alongside specs/plans, where the decision is partially implemented and partially deferred.

An ADR without negative constraints is aspirational — it describes what was chosen but not what was excluded. Future agents reading the ADR may reasonably implement approaches that the original decision intended to prevent, because the prevention was implicit rather than stated.

Add a subsection titled **"What This ADR Does NOT Decide"** or **"What This ADR Forbids"** (or both) covering:

1. **Deferred scope** — aspects the ADR intentionally leaves open for future decisions. Name them explicitly so future work knows where the seam is, rather than assuming the ADR covers everything.
2. **Architectural prohibitions** — patterns or access paths that the decision structurally prevents. These are candidates for fitness functions (CI assertions, lint rules, import boundary tests) that enforce the prohibition automatically.
3. **Phase boundaries** — if the ADR covers a multi-phase implementation, state what is NOT in Phase 1 and where the seam is. This prevents Phase 2 work from choosing an incompatible shape.

## Amendments vs. Supersessions

ADR immutability has two narrow exceptions that do not require a superseding ADR. Both require an `## Amendment` trailer at the bottom of the ADR documenting what changed and why it is not a supersession.

**Placeholder corrections** — a fact written into the Decision section turned out wrong before any consumer depended on it (e.g., a URL placeholder for an unbuilt repo, a version number for an unreleased dependency). The decision itself is unchanged; a detail that was always intended to have a specific value is corrected to that value. The amendment trailer cites the correction and confirms no consumer depended on the placeholder.

**Rendering updates** — diagram syntax, formatting, or rendering directives that change how the ADR displays without changing what it decides (e.g., updating Mermaid syntax for a new renderer version). The amendment trailer cites the rendering change.

Everything else — including rewording the Decision section to say something substantively different, adding new constraints, or removing existing constraints — is a narrative edit and requires a superseding ADR. When in doubt, supersede. The cost of an unnecessary supersession ADR is one extra file; the cost of a misclassified in-place edit is a broken reasoning chain.

## Directory Conventions

- **Numbering:** ADR-1, ADR-2, ... sequential, never reused
- **File naming:** `adr-NN_short_name.md` (lowercase, zero-padded two-digit number, underscores)
- **Statuses:** Active | Superseded by ADR-XX | Expired
- **Catalog:** `docs/architecture/decisions/_index.md` — live index with status, revisit schedule, cross-references
- **Template:** shared with business DRs — `[sdlc-root]/templates/decision_record_template.md`
