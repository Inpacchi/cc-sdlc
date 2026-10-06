## GitHub Checkpoints

**Activation gate:** skip this entire section unless `[sdlc-root]/process/github-checkpoints.md` exists and its config block says `enabled: true`.

This skill owns **CP-4, CP-5, CP-6, CP-7, CP-8, CP-9**, and the conditional **CP-S1/CP-S2** pair.

**Read `[sdlc-root]/process/github-checkpoints.md` before firing any of them.** That document is the policy: what each checkpoint says, where it moves the card, the comment templates, the column roles/names/ranks, the floor rule, the never-block invariant, SHA-pinned link policy, commit conventions, terminology, content prohibitions, and the failure classes. None of it is restated here. The mechanics — the exact `gh`/`git` calls — are the named recipes in `sdlc-manage-github` § SDLC Checkpoint Recipes; call them by name rather than assembling commands.

Two operating rules govern every checkpoint below: a checkpoint **never** blocks, stalls, or aborts the step it sits inside (on failure: `log-miss`, one-line notice, continue), and the **comment posts before any Status write**. Only **CP-8** pays git cost in this skill — every other checkpoint here links commits and pull requests that are already pushed, or links nothing.

### CP-4 — execution begins

Fires once the phase plan is emitted and before the first phase dispatches. Comment what is starting, in what order, and which agents are dispatched. Status → `executing` via `resolve-and-write-status`.

### CP-5 — a phase completes

Fires when a phase's POST-GATE clears. Comment-only — no Status write; the card stays at `executing`. Comment what that phase produced, in plain language, plus anything that changed relative to the plan.

**Threshold:** CP-5 is **required only when the deliverable has three or more phases**, and optional below that. A two-phase deliverable that skips it has not missed a checkpoint — the threshold exists so short runs do not become noisy.

### CP-6 — the internal review-fix loop begins

Fires when the REVIEW-GATE block is emitted and review agents are dispatched. Comment what is under review, the reviewer roster, and whether the external-review gate is participating.

> **CP-6 writes NO Status. The card stays at `executing`.** This is the single most likely thing in the whole checkpoint map to get wrong from memory, so state it plainly: the `stakeholder-blocked` column means **awaiting stakeholder feedback** — someone outside the session owes us a decision — and it does **not** mean "under internal agent review." The internal review-fix loop is the SDLC doing its own work; nobody is waiting on anyone. CP-6 must never call a Status recipe. If a card sits at `stakeholder-blocked` and no stakeholder owes a decision, that column's signal is dead.

### CP-S1 / CP-S2 — conditional, position-independent

These are **not** sequential steps. They are a branch available at **any** point during execution — a decision owed by any configured stakeholder role can block between two phases just as easily as during the review loop.

- **CP-S1** fires when the deliverable becomes blocked on a decision owed by a stakeholder role listed in the policy doc's config block — because CD did not resolve it or explicitly deferred it. Status → `stakeholder-blocked`.
- **CP-S2** fires when that stakeholder answers and work resumes. Status → `executing`. This is the system's only backward write, guarded by an exact-match precondition — `resolve-and-write-status` implements the guard, so pass its `is_cp_s2` flag and let the recipe decide rather than checking the current column yourself.

### CP-7 — review loop exited, work committed

Fires after the review-fix loop meets its exit bar (no critical or major findings open) and the work is committed. Comment-only — no Status write. Comment what shipped in plain language, the commit SHAs and any pull-request links, and any deviation from the plan and why. The commits are already pushed, so this checkpoint pays no git cost.

### CP-8 — result doc written, catalog moves to Validated

Fires once the result doc is written and the catalog row moves to Validated. Commit and push the result doc (and the catalog row) via `commit-and-push-artifact`, comment the outcome, the verification evidence, the deviations, and the known follow-ups with a SHA-pinned link to the result doc, then Status → `validated` via `resolve-and-write-status`.

### CP-9 — the staging deploy lands

Fires when the **staging** (pre-production) deploy carrying this deliverable lands — which may be after the Completion Report, in this session or a later one. Comment-only on artifacts (nothing new is committed): what is now testable, what reviewers should focus on, and what users will notice if it goes further. Status → `staged`. Projects whose config maps `staged` to `null` (no staging stage) never fire CP-9 live — `sdlc-archive`'s archive-time checklist handles the simulated variant.

**CP-9 is the ceiling of SDLC board tracking.** Nothing in this skill may write a Status past the `staged` column. NEVER-WRITE: the columns in the config block's `never_write` list (defaults: `Ready for Production Deploy` and `Deployed`) belong to whoever runs the production deploy pipeline, and no checkpoint, recipe, or step in this file may target one as a Status write. This is an ownership boundary, not a preference: the SDLC does not run the production deploy pipeline and does not get to narrate it. The enforcement is not policy-only — `resolve-and-write-status` refuses every `never_write` column outright, before the floor rule is even evaluated, regardless of caller. Note that the catalog status vocabulary includes a `Deployed` NEVER-WRITE: state that shares the default column 8's name; that is the *catalog* state, it gets no board write at all, and this line is tagged for the same grep reason (see `github-checkpoints.md` § The Never-Write Columns on `NEVER-WRITE:` as a line-tag).
