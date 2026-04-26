# PROJECT-SECTION Marker Review: Finding Types and Detection

This reference defines the classification scheme and detection rules for PROJECT-SECTION content review during migration (§2.1d).

## Finding Type Classification

| Upstream Change | Project Marker Status | Finding Type | Recommendation |
|-----------------|----------------------|--------------|----------------|
| Section unchanged | Any | `OK` | Re-inject as-is |
| Section updated (minor) | Content still valid | `OK` | Re-inject as-is |
| Section updated (significant) | Content may be stale | `REVIEW` | Present to user — content may need updating |
| Section restructured | Block position unclear | `REVIEW` | Present to user — may need repositioning |
| Section removed | Block orphaned | `ORPHAN` | Present to user — content has no home |
| New patterns added nearby | Could benefit project | `OPPORTUNITY` | Present to user — may want to adopt |
| Project content contradicts upstream | Conflict detected | `CONFLICT` | Present to user — resolve contradiction |

## User Decision Prompt

For each extracted `PROJECT-SECTION` block with a non-`OK` finding, present:

```
PROJECT-SECTION CONTENT REVIEW
══════════════════════════════

Found [N] marked blocks that may need attention:

┌─ [file path] ─────────────────────────────────────
│ Label: [marker label]
│ Section: [heading]
│ Finding: [REVIEW | ORPHAN | OPPORTUNITY | CONFLICT]
│
│ Upstream change:
│   [brief description of what changed in upstream]
│
│ Project content:
│   [first 3-5 lines of marked block, truncated if long]
│
│ Recommendation:
│   [specific suggestion based on finding type]
└────────────────────────────────────────────────────

[Repeat for each finding]

For each finding, choose:
1. Keep as-is — re-inject project content unchanged
2. Update — [opens content for manual edit, then re-inject]
3. Remove — discard this marked block, adopt upstream
4. Merge — combine project additions with upstream changes

Enter choices (e.g., "1:keep, 2:update, 3:remove" or "all:keep"):
```

## User Decision Application

- `keep` — re-inject block verbatim after upstream copy
- `update` — user edits the block content, then re-inject
- `remove` — do not re-inject; block is discarded
- `merge` — combine project content with upstream changes (present merged result for confirmation)

## Decision Logging

```
PROJECT-SECTION review decisions:
- [file]#[label]: kept (upstream section unchanged)
- [file]#[label]: kept (user chose to preserve despite upstream changes)
- [file]#[label]: updated (user modified content to align with upstream)
- [file]#[label]: removed (user adopted upstream version)
- [file]#[label]: merged (combined project + upstream)
```

## Finding Type Detection Rules

| Type | Detection | User Prompt |
|------|-----------|-------------|
| `REVIEW` | Upstream section diff > 20% changed lines, or key patterns added/removed | "Upstream significantly updated this section. Your marked content may reference outdated patterns or miss improvements." |
| `ORPHAN` | Upstream removed the heading entirely | "The section this content lived under no longer exists. Consider: moving to a new location, removing if obsolete, or keeping at file end." |
| `OPPORTUNITY` | Upstream added new content within 10 lines of marker position | "Upstream added new guidance near your marked content. Review whether to incorporate or reference it." |
| `CONFLICT` | Project content contains patterns explicitly superseded in upstream changelog | "Your marked content uses [pattern] which upstream replaced with [new pattern]. Consider updating." |

## When to Skip Review

- If `source_version` is unknown (first migration after legacy install), skip review — no baseline to compare against
- If the block label starts with `deviation-` (wrapped by previous migration), always flag for review — these are temporary preservations that should be re-evaluated
- If the block is < 7 days old (parse date from label), skip review — too recent to be stale
