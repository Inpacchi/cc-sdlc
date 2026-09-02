## GitHub Checkpoints

**Activation gate:** skip this entire section unless `[sdlc-root]/process/github-checkpoints.md` exists and its config block says `enabled: true`.

This skill owns **CP-1**, **CP-2**, **CP-3**, and the conditional **CP-S1/CP-S2** pair.

**Read `[sdlc-root]/process/github-checkpoints.md` before firing any of them.** That document is the policy: what each checkpoint says, where it moves the card, the comment templates, the column roles/names/ranks, the floor rule, the never-block invariant, SHA-pinned link policy, commit conventions, terminology, content prohibitions, and the failure classes. None of it is restated here. The mechanics — the exact `gh`/`git` calls — are the named recipes in `sdlc-manage-github` § SDLC Checkpoint Recipes; call them by name rather than assembling commands.

Two operating rules govern every checkpoint below: a checkpoint **never** blocks, stalls, or aborts the step it sits inside (on failure: `log-miss`, one-line notice, continue), and the **comment posts before any Status write**.

### CP-1 — deliverable registration

Fires immediately after the catalog row is written and the D-number is claimed.

**The four-part persistence set — all four, or registration is half-done:**

1. **Issue created or linked** via `create-or-link` (`mode: registration`). **Promotion path first:** if this work originated from a handoff doc, read that doc's `github_issue:` frontmatter; when it names an issue, **link and retitle** it to `Dnn — <Deliverable Name>` rather than creating a second issue.
2. **Board add at the `registered` column** — idempotent, handled inside `create-or-link`. Just call it.
3. **`github_issue: <repo>#N` written into the spec's frontmatter** (the deliverable's first artifact). **`github_board:` is captured the same way** whenever this deliverable targets a board other than the configured default.
4. **Catalog ID cell written as a link** — `[Dnn](https://<host>/<org>/<repo>/issues/N)` in `docs/_index.md`. This write is what makes the documented catalog convention actually happen; skip it and the convention is inert.

**Also at CP-1:**

- **Driving-repo selection** — resolve per § Repo Selection in the policy doc, applying those rules in order. **Never guess**; rule 4 there asks rather than guessing.
- **Sub-deliverable linking.** Registering a sub-deliverable (`D41a`, not `D41`) creates its **own** issue and links it to the parent's via `link-sub-issue`. Sub-deliverables never share the parent's thread.
- **Labels, applied on the create call itself**, never a follow-up edit — classification per § Labels in the policy doc, which also owns the unknown-label fallback.
- **Call budget.** CP-1 carries a documented exemption from the ordinary per-checkpoint cap — see § Call Budgets in the policy doc.

CP-1 commits and pushes before commenting (`commit-and-push-artifact`), then links SHA-pinned. **Pathspec: `docs/_index.md`, plus the deliverable's idea brief when one exists** — the CP-1 body links that brief as Background, and idea briefs routinely sit uncommitted, so leaving one out of the pathspec publishes CP-1's most common background link as a dead workspace path.

### CP-2 — spec approved

Fires the moment CD approves the spec. Commit and push the spec via `commit-and-push-artifact`, comment what is being built and why plus what is explicitly out of scope, link the spec **as approved at this checkpoint** (SHA-pinned), then Status → `spec-approved` via `resolve-and-write-status`.

### CP-3 — plan approved after agent review

Fires once the plan review loop is clean, before execution is handed off. Commit and push the plan, then comment the approach, the phase list, what review surfaced, and whether the external-review gate participated. Link the plan SHA-pinned (and the plan-review findings doc when one exists).

> **Editor's note — CP-3 is comment-only and writes NO Status. Do not "fix" this.** CP-3 sits between CP-2 (which writes `spec-approved`) and CP-4 (which writes `executing`), and the fact that both neighbours write is exactly why someone will eventually assume this one does too. Call no Status recipe here.

### CP-S1 / CP-S2 — conditional, position-independent

These are **not** sequential steps. They are a branch available at **any** point in this skill's flow — a decision owed by any configured stakeholder role can block while the spec is being drafted just as easily as during plan review.

- **CP-S1** fires when the deliverable becomes blocked on a decision owed by a stakeholder role listed in the policy doc's config block — because CD did not resolve it or explicitly deferred it. Status → `stakeholder-blocked`.
- **CP-S2** fires when that stakeholder answers and work resumes. Status → `executing`. This is the system's only backward write, guarded by an exact-match precondition — `resolve-and-write-status` implements the guard, so pass its `is_cp_s2` flag and let the recipe decide rather than checking the current column yourself.

The `stakeholder-blocked` column means **awaiting stakeholder feedback**, and nothing else. Nothing internal to the SDLC ever writes it.
