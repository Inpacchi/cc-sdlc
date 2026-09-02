## GitHub Provenance Reconciliation (Dimension 10)

**Activation gate:** this dimension exists only where the `github-provenance` bundle is installed. If `[sdlc-root]/process/github-checkpoints.md` does not exist, or its config block says `enabled: false`, report "Dimension 10 — not applicable, convention not installed/not configured" in coverage and produce no findings. When active, this project runs **ten** dimensions, not nine — a report claiming nine has silently dropped this one; state Dimension 10's result explicitly in coverage, and apply the additional self-verification checks at the end of this section.

**Read `[sdlc-root]/process/github-checkpoints.md` first.** It is the policy: the config block (org, repos, board, column roles/names/ranks, labels, reconciliation cutoff), catalog-wins, the never-reopen rule, and the miss-log's fast-path-not-gate role. The read-side `gh` mechanics and the name-then-resolve discipline live in `.claude/skills/sdlc-manage-github/SKILL.md`. Neither is restated here.

**Read-only, without exception.** This dimension issues read `gh` calls only. It never writes a Status, never creates or closes an issue, never edits `docs/_index.md`. Per § Catalog Wins, the catalog is canonical and the board is its projection: drift is *detected and reported*, and a human decides.

NEVER-WRITE: the `staged` column is the ceiling of SDLC board tracking; the config block's `never_write` columns (defaults: `Ready for Production Deploy` and `Deployed`) belong to whoever runs the production deploy pipeline. A card in one sits **above** every floor computed below and is never reported as drift.

**Issues-only mode** (`board.default: none`): run classes 1 and 2 only (10f); skip board enumeration (10c) and class 3 entirely, and say so in coverage.

### 10a. Inputs — gather all three before comparing anything

1. **Issues**, across every repo in the config block's `repos.driving` list — **open and closed**:

   ```bash
   gh issue list --repo <org>/<repo> --state all \
     --json number,title,state,url,labels --limit 500
   ```

   Filter **in memory** for titles matching a `Dnn` prefix: `^D[0-9]+[a-z]?\s*(—|-|:|\s)`. A bare substring test is not sufficient — `D4` substring-matches `D41` and `D400`. Titles with **no** `Dnn` prefix (`Parked: …`, `Idea: …`) are deliberately outside this join: pre-deliverable work has no catalog row to join against. Do not report them as orphans.

   **Pagination discipline (applies to every enumeration in this dimension — issues, board items, labels):** the `--limit` values here are per-call caps, not scope declarations. When a listing returns exactly its limit, page to completion before comparing anything — a silently truncated enumeration narrows the join and suppresses real drift.

2. **Catalog rows** — every deliverable row in `docs/_index.md`, across both the active and the completed/archived tables. Capture the ID cell **verbatim**, including whether it is a markdown link and where that link points.

3. **Board items** — from every board in scope, per 10c. Skipped in issues-only mode.

### 10b. Scope gate — cutoff D-number, not link-cell

Read the **reconciliation cutoff D-number** from the policy doc's config block. Read it from the document; do not hardcode a copy here, and do not invent one. **If the config carries no cutoff, that absence is itself a `major` finding** — report it and run the dimension over nothing rather than guessing a boundary.

- Deliverable ID **below** the cutoff → pre-convention, **entirely out of scope**. No findings of any class, in either direction.
- Deliverable ID **at or above** the cutoff → **in scope regardless of the ID cell's format.**

**The linked ID cell is a fast path, never the gate.** A linked cell resolves the issue in one hop and skips the title search. An **unlinked** in-scope row falls through to a title-prefix search across all driving repos, and reports **missing-issue** if nothing is found.

> Gating scope on link-format alone would make a post-cutoff deliverable whose CP-1 *failed* invisible **by definition** — and a deliverable with no issue is the primary drift class this dimension exists to catch. A failed CP-1 leaves exactly a plain-text ID cell, so a link-cell gate would blind the detector to its own most important case. Never reintroduce it.

### 10c. Multi-board enumeration — never hardcode a board

Do not assume the default board is the only one. Build the board set **from the data**: the distinct `github_board:` values found in **in-scope artifact frontmatter**, plus any board named in an in-scope catalog row's free text (catalog rows carry no `github_board:` field, only prose mentions — read them as prose), plus the default board from the config block. Resolve each board's project number via `gh project list --owner <org> --format json`.

For each board in the set, resolve its status field **by column name** — never by ID, never across boards:

```bash
gh project field-list <project-number> --owner <org> --format json
gh project item-list  <project-number> --owner <org> --format json --limit 200
```

**A board whose status options do not match the configured column names is reported as "board unconfigured"** — a `major` finding naming the board, what it has, and what is missing. It is **not** a silent pass. Items on an unconfigured board are **exempt from below-floor drift** — you cannot compare ranks against columns that do not exist — but their missing-issue and orphan-issue checks still run normally.

### 10d. The join

Key on the D-number.

- **Sub-deliverables join their parent row.** Strip the trailing letter suffix: a `D41a` issue joins the **`D41`** catalog row. Sub-deliverables have no row of their own, so several issues legitimately join one row — that is not a duplicate finding.
- Each in-scope catalog row resolves to zero or more issues (fast path via the linked cell, else title-prefix search across the driving repos), and each issue resolves to zero or one board item per board in scope.

### 10e. Status parsing — compound cells

Catalog Status cells are compound free text: `In Progress (Phases 1-6 done…)`, `Complete — D41a/D41b/D41c all Complete`.

**Parse by prefix-matching the first canonical token** — take everything before the first ` (` or ` — ` and match it against the declared catalog vocabulary: `Draft`, `Ready`, `In Progress`, `Validated`, NEVER-WRITE: `Deployed` (the *catalog status* of that name, which gets no board write at all — distinct from any board column sharing the name), `Complete`, `Archived`.

**If no canonical token matches, report the row as `unparseable` (`minor`) — never guess a status.** A guessed status silently produces or suppresses a below-floor finding, which is worse than admitting the cell cannot be read. A non-canonical token that recurs across rows is additionally flagged once per audit as vocabulary drift (`info`), with a proposed floor treatment, so CD can normalize the rows or extend the vocabulary.

**Catalog status → board floor** (roles and ranks from the policy doc's config block — read them there; this table only states the mapping):

| Catalog status | Board floor (role) | Default rank |
|---|---|---|
| Draft | `registered` | 1 |
| Ready | `spec-approved` | 2 |
| In Progress | `executing` | 3 |
| Validated | `validated` | 5 |
| NEVER-WRITE: `Deployed` (catalog status), Complete, Archived | none — the SDLC writes no Status for these; the issue is closed at CP-10 | — |

The `stakeholder-blocked` column (rank 4) is a stakeholder-block state, not a catalog status. A card sitting there satisfies the floor for anything at rank 3 or below.

### 10f. The three drift classes

| # | Class | Test | Severity |
|---|---|---|---|
| 1 | **Deliverable with no issue** | In-scope catalog row; fast path finds no link and the title-prefix search across all driving repos finds nothing | `major` |
| 2 | **Issue with no catalog row** | `Dnn`-prefixed issue whose D-number (suffix stripped) is at or above the cutoff and matches no catalog row | `major` |
| 3 | **Board Status below floor** | `rank(board column) < rank(floor(catalog status))`, on a configured board | `major` when two or more ranks below; `minor` at one |

**A card *above* its floor is never drift.** The board has two writers, and the SDLC never moves a card backward or corrects a human's forward move.

### 10g. States that are not drift — check these before flagging class 3

- **Validated with a pending archive-time checklist.** A deliverable that reached Validated but has not yet been archived will **always** show catalog rank above board rank, because CP-8 and CP-9 may be archive-session work. Exempt it when the catalog status parses to `Validated` **and** the result doc carries an archive-time checklist section (match `Archive-Time Checklist`, case-insensitive) that has not been executed. Stated generally on purpose — it covers every future validated-but-unarchived row, not any one deliverable.
- **Items on an unconfigured board** (10c) — exempt from class 3 only.
- **Pre-cutoff IDs** (10b) — exempt from every class.
- **A closed issue whose catalog status is Complete or Archived** — no board floor applies; CP-10 closed it and wrote no Status.

### 10h. Taxonomy parity check — labels, types, verdicts

For each driving repo:

```bash
gh label list --repo <org>/<repo> --json name --limit 200
```

**The repo's label set must equal exactly the config block's label set** (universal + conditional + human). Both directions are drift:

- **A missing label is drift (`minor`)** — not tolerated as a silently empty label filter; a filter that returns nothing looks identical to a filter that matched nothing, and the difference matters.
- **An extra label is drift (`minor`)** — the REST create call silently auto-creates unknown labels, so a typo in a checkpoint create becomes a repo label nobody decided on. This check is the designated detector for that sprawl. (Exception: GitHub's default labels the project chose to keep — flag once as `info` for CD to prune or add to the config block.)

**When `issue_types` is configured: open issues with no issue type are drift (`minor`)** — `create-or-link` sets the type on the create call, and GitHub silently drops `type` for callers without push access (200 response, nothing in the miss-log), so this check is the only detector for that failure mode. Closed pre-cutoff issues are out of scope.

**When `board.human_fields` declares a column-scoped field** (e.g. a Test Verdict cleared when a card leaves the `staged` column): a non-empty value on a card outside that field's column is drift (`minor`) — a stale verdict misdescribes the card's state. **Read-only: report it, never clear it — the field is human-owned.**

### 10i. Log-independence — the property that makes this dimension trustworthy

You **may** read `[sdlc-root]/.local/github-checkpoint-misses.jsonl` to prioritize where you look first. You **must** produce **identical findings** whether that file is present, empty, absent, or **wrong** — carrying entries for drift live GitHub does not show, or omitting drift it does.

Concretely: never report a finding sourced from a log entry you did not confirm against live GitHub, and never suppress a live-state finding because the log does not mention it. **If the log's contents change your conclusions, the design has failed and the finding is invalid.** Live GitHub state is the only source of truth; the log is a hint about search order and nothing more.

### 10j. Reporting

Fold Dimension 10 findings into the standard findings table with `Dimension: GitHub Provenance`. Evidence discipline applies unchanged — every finding cites the catalog line number, the issue URL, and the board item's current Status column name. Report "board unconfigured", `unparseable`, and any vocabulary-drift note explicitly even when no drift is found; a clean run states "no drift across N in-scope deliverables, M issues, K boards" rather than omitting the dimension.

**Additional self-verification checks when this dimension is active:**

- Dimension 10 scanned and explicitly reported (ten dimensions, not nine)
- Scope gate applied by **cutoff D-number**, never by ID-cell link format
- Every board in scope enumerated, and each one's configuration state stated (including any "board unconfigured"); or issues-only mode declared
- The Validated-with-pending-archive-checklist exemption applied **before** any class-3 finding was raised
