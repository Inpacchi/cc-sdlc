## GitHub Checkpoints

**Activation gate:** skip this entire section unless `[sdlc-root]/process/github-checkpoints.md` exists and its config block says `enabled: true`.

This skill owns **CP-10** and **CP-12**, the **parked-issue closure path**, the **archive-time checklist executor**, and a read-only **drift-detection hook** (which points at the audit skill's GitHub Provenance Reconciliation dimension rather than carrying its own copy of the join).

**Read `[sdlc-root]/process/github-checkpoints.md` before firing any of them.** That document is the policy: what each checkpoint says, where it moves the card, the comment templates, the column roles/names/ranks, the floor rule, the never-block invariant, the SHA-pinned link policy, commit conventions, terminology, content prohibitions, and the failure classes. None of it is restated here. The mechanics — the exact `gh`/`git` calls — are the named recipes in `sdlc-manage-github` § SDLC Checkpoint Recipes; call them by name rather than assembling commands.

Two operating rules govern everything below: a checkpoint **never** blocks, stalls, or aborts the step it sits inside (on failure: `log-miss`, one-line notice, continue — the archive still completes), and the **comment posts before any Status write**. The `staged` column is the ceiling of SDLC board tracking; NEVER-WRITE: the config block's `never_write` columns (defaults: `Ready for Production Deploy` and `Deployed`) belong to whoever runs the production deploy pipeline, and nothing in this file may target either.

**Firing points:**

| When | Checkpoint | What |
|---|---|---|
| During reconciliation, per reconciled commit cluster | **CP-12** | Retroactive issue for direct-dispatch work that just earned a D-number |
| After the archive commit is pushed | **CP-10, part 1** | Closing comment with main-branch chronicle links; **issue stays open** |
| After part 1's link verification | **CP-10, part 2** | Close the issue as completed |

### CP-10 — chronicled and closed, in two parts

**Part 1 fires only after the archive commit has been pushed.** CP-10's closing comment links the **final chronicle locations as main-branch URLs**, and a main-branch URL to a file that has not reached `origin` yet is a 404. Push first (the archive commit, or `commit-and-push-artifact` scoped to the moved files and `docs/_index.md`), then comment: a short closing summary of what was built and what changed as a result, followed by those main-branch links.

> **CP-10 is the one checkpoint in the entire map that does not SHA-pin, and this is deliberate — do not "fix" it.** Every other artifact link in the thread is pinned to the commit it described, precisely so it survives this move. CP-10's job is the opposite: it answers "where does this live *now*", which only a main-branch URL can answer. Between the pinned history and the main-branch closing links, a reader gets both the frozen record and the current home.

**Part 2 is idempotent against an issue that's already closed.** Board-native automation (e.g. GitHub's "Auto-close issue" Projects v2 workflow) may have closed the issue when a human moved the card into a terminal column. Check state before closing (`gh issue view <N> --json state`); if already `CLOSED`, skip the close call and post the summary comment only — never treat "already closed" as an error, and never reopen to re-close.

### Archive-time checklist executor

Some deliverables reach **Validated** carrying lifecycle checkpoints that could not honestly have fired during execution — a process deliverable never lands a staging deploy, and nothing can archive itself while its own artifacts are still under review. Those checkpoints are recorded as a **pending archive-time checklist** in the deliverable's result doc, and **this skill is where they get executed.** A deferred checkpoint with no executor is a promise nobody keeps.

**Execution.** Run the rows in the order the doc states. Do not reorder, do not skip, do not batch. For the standard shape that order is: **CP-8 → simulated CP-9 → CP-10 part 1 → post-move link verification → CP-10 part 2.**

- **CP-9 is simulated** for deliverables that never see a staging deploy. Invoke `resolve-and-write-status` **directly** against the `staged` column, accompanied by a comment that **says plainly it is a verification simulation of the checkpoint's Status write, not a real staging event.** Never let a simulated transition read as a genuine deploy narrative — a reader who cannot tell the difference has been misled by the provenance log, which is worse than a gap in it.

**Verify each row before proceeding to the next.** A row that fails stops the *checklist*, not the archive: report the failure, leave the issue **open** (CP-10 part 2 does not run), finish the file move and the catalog update, and leave the deliverable at Validated rather than marking it Complete. The never-block invariant governs the checkpoint; it does not license closing a thread whose verification did not pass.

### CP-12 — retroactive issues for reconciled direct-dispatch work

Fires when reconciliation assigns a retroactive D-number to direct-dispatch work. One consolidated comment per the CP-12 template: what the work was, which commits carried it, what it changed. Status → `staged` (terminal only). Close if the work is complete.

> **Never replay or fabricate checkpoint history.** The temptation is to backfill a plausible CP-1…CP-8 sequence so the thread "looks normal." Do not. This work genuinely had no spec approval, no plan review, and no phase narration — inventing them turns the provenance log into fiction and destroys the one thing it is for. A retroactive thread has exactly one entry because the work produced exactly one entry's worth of narrative, and the comment says so in its opening line.

### Parked-issue closure

A `Parked:` issue (created at CP-11b, carrying **no** `Dnn` prefix) whose handoff doc is being resolved, archived, or deleted **without ever having been crystallized into a deliverable** is closed as **not planned**, with a comment saying the work was parked and never picked up, and pointing at the handoff doc's chronicle location.

**Do not apply this to a handoff that graduated.** A crystallized handoff's issue was *retitled* at CP-1 and now carries a `Dnn` prefix — it belongs to that deliverable and closes at CP-10 as **completed**, not as *not planned*. Check the current title, not the frontmatter's age.
