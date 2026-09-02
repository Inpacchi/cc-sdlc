## GitHub Checkpoints

**Activation gate:** skip this entire section unless `[sdlc-root]/process/github-checkpoints.md` exists and its config block says `enabled: true`.

This skill owns **CP-11** and **CP-11b** — not two checkpoints in sequence, but the two branches of a single decision: an issue already exists for this work, or it does not.

**Read `[sdlc-root]/process/github-checkpoints.md` before firing either.** That document is the policy: what each checkpoint says, where it moves the card, the comment templates, the column roles/names/ranks, the floor rule, the never-block invariant, the SHA-pinned link policy, commit conventions, terminology, content prohibitions, and the failure classes. None of it is restated here. The mechanics — the exact `gh`/`git` calls — are the named recipes in `sdlc-manage-github` § SDLC Checkpoint Recipes; call them by name rather than assembling commands.

Two operating rules govern both: a checkpoint **never** blocks, stalls, or aborts the step it sits inside (on failure: `log-miss`, one-line notice, continue), and the **comment posts before any Status write**. The `registered` column is the only Status this skill ever writes, and only at CP-11b on accept.

Both checkpoints fire **after the handoff doc is written and before the surfacing message**. Both are ⎘ checkpoints: they commit and push the handoff doc via `commit-and-push-artifact` first, then link it SHA-pinned. A workspace path is not a link — a reader on GitHub cannot open `docs/current_work/ideas/…`.

**Branch on whether a deliverable issue exists** (the handoff doc's `active_deliverable:` frontmatter):

| `active_deliverable:` | Checkpoint | Why |
|---|---|---|
| `Dnn` | **CP-11** | The deliverable was registered at CP-1, so an issue already exists and already carries the narrative |
| `null` | **CP-11b** | No D-number has been minted, so no `Dnn` join key exists and no deliverable issue can |

**Any optional-commit question elsewhere in this skill is superseded for the handoff doc** whenever either checkpoint fires — `commit-and-push-artifact` has already committed and pushed it. Do not ask again; state in the surfacing message that the doc is committed.

### CP-11 — an existing deliverable's session is parked

Comment on the deliverable's issue: why the session stopped, what remains, and the SHA-pinned handoff doc link.

> **CP-11 writes NO Status and creates NO issue.** Parking is not a board transition. The work did not advance, and under the floor rule it cannot retreat — it simply stopped, and the narrative *is* the checkpoint. Call no Status recipe here.

### CP-11b — parked work with no issue: an offer, never an assumption

`sdlc-manage-github`'s checkpoint carve-out lets SDLC checkpoints act without per-call confirmation. **CP-11b is one of the two deliberate exceptions to that posture** (driving-repo selection rule 4 is the other): it creates something org-visible for work that has not earned a D-number, so CD decides.

1. **Offer** issue creation via `AskUserQuestion`. On decline: nothing happens, and nothing is recorded as a miss — a declined offer is a decision, not a failure.
2. On accept: `commit-and-push-artifact` for the handoff doc (first cycle), then `create-or-link` (`mode: parked`) — title `Parked: <short description>`, body per the CP-11b template with the SHA-pinned handoff-doc link.
3. **Universal label only — and the default issue type (`Task`) when types are configured** — both applied on the create call itself, never a follow-up edit. Parked work has no scoped file set yet, so conditional labels are not classifiable here; label/type classification and the sprawl hazard are owned by the policy doc's § Labels and § Issue Types.
4. **Board add at `registered`** — idempotent, handled inside `create-or-link` (skipped in issues-only mode).
5. **Write `github_issue: <repo>#N` into the handoff doc's frontmatter**, then call `commit-and-push-artifact` a second time to land it. The recipe is idempotent, so the second call is cheap and cannot produce an empty commit. **This write is the entire point of CP-11b:** it is the seam the promotion path reads at CP-1, where `create-or-link` links and *retitles* this same issue to `Dnn — <Deliverable Name>` instead of creating a second one. Skip it and the issue is orphaned — the work crystallizes later into a fresh issue while this one sits at `registered` forever.

> **The two commit-and-push cycles are deliberate, and CP-11b is the second documented exemption from the ordinary ≤4 git-operation cap** — **≤8 happy path, ≤10 worst case**, per `github-checkpoints.md` § Call Budgets, where CP-1's `gh`-call exemption is the only other one. The ordering cannot be collapsed into one cycle: the issue body links the handoff doc **SHA-pinned**, so the doc must be pushed *before* the issue exists — and the issue number written in step 5 does not exist until that create returns. **Do not "optimize" this into a single commit** — doing so either publishes a workspace path in the issue body or drops the `github_issue:` seam entirely.
