# Exempt File List (Neuroloom)

Files the adapter must copy verbatim from cc-sdlc source — zero transformation applied. Any hunk in these files that shows transformation shape (MCP calls, metadata replacements, orphan debris, etc.) is a plugin defect.

This list mirrors the plugin's own "Transformation-Exempt Files" table in `neuroloom-sdlc-plugin/skills/sdlc-migrate/SKILL.md`. If the two lists drift, the plugin's list is authoritative for what the plugin *should* enforce; this list is what the audit *checks* was enforced. Drift between them is itself a finding.

## The list

| File | Install path | Why exempt | Permitted deviations |
|---|---|---|---|
| `process/knowledge-routing.md` | `.claude/sdlc/process/knowledge-routing.md` | Phrasing contract itself — documents canonical AND forbidden phrases. Transforming destroys the documentation. | None. Any hunk = defect. |
| `process/sdlc_changelog.md` | `.claude/sdlc/process/sdlc_changelog.md` | Historical record — entries quote canonical phrases as context. Transforming corrupts history. | None. Any hunk = defect. Missing upstream entries (diff shows source has a section sleeved doesn't) = content-loss defect. |
| `agents/sdlc-reviewer.md` | `.claude/agents/sdlc-reviewer.md` | Reviewer's checklist lists canonical phrases as validation criteria. Transforming removes the phrases it exists to detect. | Adapter MAY add a supplementary Phrasing Contract Validation section listing adapter-specific forms; contents outside that section must be verbatim. |
| `agents/sdlc-compliance-auditor.md` | `.claude/agents/sdlc-compliance-auditor.md` | Auditor's validation section lists canonical phrases as scan targets. | **Documented exception:** line ~116 section about PROJECT-SECTION scan may have `(resolve via .sdlc-manifest.json's sdlc_root field, or fall back to .claude/sdlc/)` in place of source's `(detected in methodology section above)` — this is a post-2026-04-22 adapter customization since the `**Path detection:**` block was dropped from the adapter version. Content outside that line must be verbatim. |
| `CLAUDE-SDLC.md` | (merged into target's `CLAUDE.md`, not a standalone file) | Framework documentation inserted into project's CLAUDE.md; contains canonical phrases as examples. | The adapter merges this into the project's existing CLAUDE.md rather than overwriting, so the section's content should be verbatim within the merged file. |
| `knowledge/provenance_log.md` | `.claude/sdlc/knowledge/provenance_log.md` | Project-specific append-only file; treated like changelog. The adapter should NEVER overwrite this. | None — should be completely absent from the diff (never touched by migration). |

## How to verify exempt-ness during audit

For each file in the list:

1. **Locate both copies:**
   - Source: `~/Projects/cc-sdlc/<source-path>`
   - Target: `<target-path>/<install-path>`

2. **Diff them:**
   ```bash
   diff -u ~/Projects/cc-sdlc/process/knowledge-routing.md <target>/.claude/sdlc/process/knowledge-routing.md
   ```

3. **Evaluate the diff:**
   - **No diff** → exempt-ness enforced correctly. ✓
   - **Only permitted-deviation hunks per the table above** → exempt-ness enforced correctly. ✓
   - **Any other diff** → exempt-file violation (plugin defect). Report per-hunk with what shape of transformation shows.

## Transaction log cross-check

The plugin emits `file_merged` events during stage 4.2. For each file on this exempt list, the event should have `subtype: "exempt_verbatim"` and `rules_fired: []`. Subtypes of `mcp_preserved`, `mcp_backfilled`, or `mcp_new_file` on an exempt file are telemetry evidence of exempt-ness NOT being enforced — even before diffing the content.

```bash
grep '"event":"file_merged"' <target>/.sdlc-transaction-log \
  | grep -E 'knowledge-routing\.md|sdlc_changelog\.md|sdlc-reviewer\.md|sdlc-compliance-auditor\.md|CLAUDE-SDLC\.md|provenance_log\.md' \
  | grep -v '"subtype":"exempt_verbatim"'
```

Any output is a finding — the plugin ran non-verbatim transformation on an exempt file.

## When sleeved version is MORE correct than source

Sometimes the adapter's verbatim copy would propagate an upstream bug. The `agents/sdlc-compliance-auditor.md:13` case (broken methodology path) is an example. In these cases:

1. Classify the diff as **upstream** (source has a bug)
2. Note that the adapter is currently violating exempt-ness in a way that happens to produce the correct outcome
3. After the upstream fix lands, the adapter should return to verbatim copying — the correction is no longer needed

Don't punish the adapter for the workaround, but track it — once source is fixed, the plugin should drop any special-case handling.

## Future adapters

Different adapters may have different exempt lists. When adding a new adapter, create `references/exempt-file-list-<adapter>.md` and update `SKILL.md` Step 1 to select the right file based on `<adapter-name>` parameter.
