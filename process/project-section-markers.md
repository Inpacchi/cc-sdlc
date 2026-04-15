# PROJECT-SECTION Markers

A convention for protecting project-specific content in **process and skill files** across migrations. Only applies to framework files that get overwritten during `sdlc-migrate`.

---

## When Markers Are Needed

Markers are required when adding project-specific content to **process docs** or **skill files** — these are framework files that `sdlc-migrate` overwrites from upstream.

| File Type | Needs Markers | Reason |
|-----------|---------------|--------|
| Process docs (`[sdlc-root]/process/*.md`) | Yes | Overwritten during migration |
| Skill files (`.claude/skills/*/SKILL.md`) | Yes | Overwritten during migration |
| Knowledge YAML (`[sdlc-root]/knowledge/**/*.yaml`) | No | Project-specific, not overwritten |
| Discipline parking lots (`[sdlc-root]/disciplines/*.md`) | No | Project-specific, not overwritten |
| Agent-context-map (`[sdlc-root]/knowledge/agent-context-map.yaml`) | No | Project-specific, not overwritten |

## Skills That Produce Marked Content

- `sdlc-develop-skill` (modify mode) — adds project-specific phases to framework skills
- `sdlc-audit` (improvement mode) — applies project-specific fixes to process docs
- `sdlc-migrate` — wraps detected customizations during migration (deviation detection)

---

## The Convention

Wrap project-specific content in paired markers that `sdlc-migrate` recognizes and preserves.

### Markdown Files

```html
<!-- PROJECT-SECTION-START: descriptive-label -->
... project content preserved across migrations ...
<!-- PROJECT-SECTION-END: descriptive-label -->
```

### YAML Files

```yaml
# PROJECT-SECTION-START: descriptive-label
... project content ...
# PROJECT-SECTION-END: descriptive-label
```

### Label Format

Labels must be descriptive and unique within the file. Use this pattern:

```
{origin}-{date}-{topic}
```

| Origin | When | Example Label |
|--------|------|---------------|
| `modify` | `sdlc-develop-skill` modifies a framework skill | `modify-2026-04-07-custom-gate` |
| `audit-improve` | `sdlc-audit` improvement mode applies a project-specific fix | `audit-improve-2026-04-07-env-check` |
| `deviation` | `sdlc-migrate` wraps detected customizations during migration | `deviation-2026-04-07-build-commands` |

---

## Rules

1. **Every START must have a matching END with the same label.** Orphaned markers are flagged by `sdlc-compliance-auditor` (Dimension 7).

2. **Labels must be unique within a file.** Duplicate labels cause ambiguity during extraction and re-injection.

3. **Markers must not nest.** A `PROJECT-SECTION-START` inside another `PROJECT-SECTION` block is malformed. Use separate, sequential blocks instead.

4. **Content inside markers is preserved verbatim.** `sdlc-migrate` does not modify, reformat, or merge content within markers — it extracts the block before overwriting and re-injects it afterward.

5. **Markers use the file's native comment syntax.** HTML comments (`<!-- -->`) for Markdown, hash comments (`#`) for YAML. Do not mix formats.

6. **Skills that produce project-specific content are responsible for adding markers at creation time.** This is a producing-skill obligation, not a migration-time responsibility. If content is created without markers, it can only be protected retroactively via deviation detection (§2.1c in `sdlc-migrate`).

---

## How Migration Uses Markers

### Direct Copy Files (§2.1)

1. Before overwriting, extract all `PROJECT-SECTION` blocks with their labels and heading context
2. **Review each block against upstream changes (§2.1d):**
   - Compare the upstream section at `source_version` vs `HEAD`
   - Classify: OK, REVIEW (significant changes), ORPHAN (section removed), OPPORTUNITY (new patterns), CONFLICT (contradicts upstream)
   - Present non-OK findings to user with options: keep, update, remove, merge
3. Copy the upstream file (overwriting the project's version)
4. Re-inject each block at its original heading position (unless user chose to update/remove)
5. If the heading no longer exists upstream, append at end with a warning comment

### Content-Merge Files (§2.2–2.4)

1. **Review marked blocks against upstream changes (§2.1d)** — same classification and user presentation
2. Framework sections outside markers are updated to match upstream
3. Markers are never moved, split, or merged automatically — but user can choose to update content during review

### Deviation Detection (§2.1c)

1. Before direct-copying, diff the project's version against the previous upstream version
2. If the project modified content outside existing markers, present the customizations
3. User can choose to: wrap in markers (preserve), overwrite (discard), or skip the file

---

## Validation

The `sdlc-compliance-auditor` validates marker integrity as part of Dimension 7 (Migration Integrity):

- Every `START` has a matching `END` with the same label
- No orphaned `END` without a `START`
- No mismatched labels between paired markers
- Correct comment syntax for the file type

The `sdlc-reviewer` recognizes markers when reviewing skills and agents:

- Does not flag content inside markers as convention violations
- Verifies markers are well-formed if present
- Flags malformed markers as minor findings

---

## What Markers Are NOT

- **Not a way to opt out of upstream changes.** Framework sections outside markers are still updated by migration. Markers protect additions, not overrides.
- **Not version control.** Markers don't track history — they mark boundaries. Use git for history.
- **Not a substitute for upstream contribution.** If a project-specific change would benefit all projects, propose it upstream rather than wrapping it in markers permanently.
- **Not a guarantee of permanent preservation.** Migration reviews marked content against upstream changes (§2.1d). If upstream significantly changed the surrounding context, the user is prompted to review — they may choose to update, merge, or remove the marked content. Markers protect from silent overwriting, not from becoming stale.
