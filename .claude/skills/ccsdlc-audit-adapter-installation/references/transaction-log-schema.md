# Transaction Log Schema

The adapter plugin writes `.sdlc-transaction-log` in the target project root during `/sdlc-initialize`, `/sdlc-migrate`, and `/sdlc-port` runs. Each line is a JSON object recording a single event.

This skill verifies the log's completeness for the most recent run — mandatory events must be present, event data must be self-consistent, and no silent gate bypasses may have occurred. Use this reference to interpret log contents.

## Event catalog

### Gate events

Emitted as each plugin-defined gate evaluates.

```json
{"ts": "ISO-8601", "run_id": "<op>-<hash>", "event": "gate", "gate": "<gate-name>", "result": "approved|rejected|cancelled"}
```

Gates expected in a migration run:
- `preflight` — environment check
- `changelog_review` — CD reviewed the cc-sdlc changelog since last version
- `change_manifest_preview` — CD approved the preview of files that will change

A `rejected` or `cancelled` result at any gate should halt the run. The absence of `run_complete` later in the log corroborates this.

### Contract change detection

```json
{"ts": "...", "run_id": "...", "event": "contract_change_detected", "version": "vX.Y.Z", "resolution": "<description>"}
```

Emitted when stage 2.2a spots `[contract-change]` tags in the cc-sdlc changelog between versions. `resolution` describes how the plugin handled it (e.g., `pattern_mapping_already_updated_in_plugin_0.3.5`). If `resolution` indicates the plugin didn't have rules for the new contract, expect Pattern Mapping gaps in the audit.

### Checkpoint

```json
{"ts": "...", "run_id": "...", "event": "checkpoint", "name": "point_of_no_return"}
```

Emitted when the run transitions from read-only stages (1–3) to mutation (stage 4). Any `run_complete` event must post-date this.

### Stage completion

```json
{"ts": "...", "run_id": "...", "event": "stage_complete", "stage": "<stage-id>", "...stage-specific fields"}
```

Stages:
- `4.1_knowledge_seed` — knowledge layer upserted; `created`, `updated`, `errors` counts
- `4.2_content_merge` — operational files written; should appear once per run
- `4.3_claude_md_check` — CLAUDE.md compatibility evaluated; `guarded_renames` count
- `4.4_manifest_update` — `.sdlc-manifest.json` written; `version`, `installed_files` count

Missing `stage_complete` events without a corresponding `gate` rejection means the run halted mid-stage — the installation is in an undefined state.

### Per-file merge events (MANDATORY in stage 4.2 per plugin 0.3.6+)

Emitted immediately after each file is written. One event per file.

```json
{
  "ts": "...",
  "run_id": "...",
  "event": "file_merged",
  "stage": "4.2",
  "file": "<install-path>",
  "subtype": "mcp_new_file|mcp_backfilled|mcp_preserved|exempt_verbatim",
  "mcp_before": <int>,
  "mcp_after": <int>,
  "headings_preserved": ["<heading>", ...],
  "headings_fuzzy_matched": [{"tier": 2|3|4, "project": "...", "upstream": "..."}],
  "rules_fired": ["<rule-label>", ...]
}
```

Subtypes:
- `mcp_new_file` — file didn't exist in project; wrote transformed upstream content
- `mcp_backfilled` — file existed but had no MCP; wrote transformed upstream content
- `mcp_preserved` — file had MCP; merged transformed upstream + project's preserved sections
- `exempt_verbatim` — file is on the exempt list; copied upstream verbatim with no rule evaluation

**Audit implications:**
- Count of `file_merged` events must match count of operational files in the change manifest
- Files on the exempt list must have `subtype: "exempt_verbatim"` — any other subtype on an exempt file is a plugin defect
- `headings_fuzzy_matched` entries indicate the §4.2.0 fuzzy heading matcher fired; surface these in the audit report so the user knows where heading drift happened

### MCP retention audit summary (MANDATORY per plugin 0.3.6+)

One event per run. Aggregates stage 4.2's MCP-bearing file outcomes.

```json
{
  "ts": "...",
  "run_id": "...",
  "event": "mcp_retention_audit_complete",
  "stage": "4.2-gate",
  "mcp_before": <int>,
  "mcp_after": <int>,
  "net_delta": <int>,
  "files_scanned": <int>,
  "regressions": <int>,
  "legitimate_drops": <int>,
  "drops_detail": "<comma-separated>",
  "audit_result": "PASS|FAIL"
}
```

**Audit implications:**
- Missing event = plugin ran stage 4.2 without running its own internal audit. Major telemetry regression; the migration cannot be trusted to have evaluated its own output.
- `audit_result: "FAIL"` means the plugin itself halted; verify the target state against the halt message
- `regressions > 0` should have halted the run. If `run_complete` still appears after, the halt was bypassed — plugin bug.
- `net_delta < 0` with `regressions: 0` means all drops were legitimate upstream removals — check `drops_detail` against cc-sdlc changelog for matching upstream changes

### Structural content-loss audit (MANDATORY per plugin 0.3.6+)

Introduced alongside MCP retention. Catches content dropped without MCP changes.

```json
{
  "ts": "...",
  "run_id": "...",
  "event": "structural_audit_complete",
  "stage": "4.2-gate",
  "files_scanned": <int>,
  "regressions": <int>,
  "legitimate_drops": <int>,
  "drops_detail": "<per-file summaries>",
  "audit_result": "PASS|FAIL"
}
```

**Audit implications:**
- Missing event = plugin is pre-0.3.6 or didn't run this audit. For pre-0.3.6 installations, manually run the Step 5 structural check against the post-merge files.
- If present with `regressions > 0` and the run still completed, content-merge dropped upstream content — a plugin defect the audit must surface.

### Transformation warnings

```json
{"ts": "...", "run_id": "...", "event": "transformation_warning", "file": "<path>", "line": <int>, "phrase": "<the unmatched phrase>", "reason": "<why>"}
```

Emitted when the transformer encountered a standard-phrase-adjacent pattern not in Pattern Mapping. These are Pattern Mapping gaps — a correct adapter should have zero warnings post-release. Every warning is itself a finding.

### Run completion

```json
{"ts": "...", "run_id": "...", "event": "run_complete", "from_version": "...", "to_version": "...", "stages_complete": [1, 2, 3, 4, 5], "knowledge_layer": "...", "operational_layer": "..."}
```

Emitted only after the pre-run_complete assertion (Stage 5.0 telemetry assertion in plugin 0.3.6+) passes. Presence of this event means the plugin itself considered the run successful. Absence means the run halted or crashed — the installation is in an undefined state and must be restored via `git checkout -- .claude/` before re-running.

## Completeness check (the audit's job)

For the most recent `run_id` in the log, assert:

1. All expected gates are `approved`
2. `checkpoint: point_of_no_return` exists
3. Every stage_complete from 4.1 through 4.4 exists
4. Count of `file_merged` events == count of files in change manifest (can be approximated by counting upstream files that differ from project's pre-migration state)
5. Files on the exempt list all have `file_merged` events with `subtype: "exempt_verbatim"`
6. Exactly one `mcp_retention_audit_complete` with `audit_result: "PASS"` (plugin 0.3.6+)
7. Exactly one `structural_audit_complete` with `audit_result: "PASS"` (plugin 0.3.6+)
8. Zero `transformation_warning` events without resolution (either resolved in a later event or absent because the plugin's Pattern Mapping had the rule)
9. `run_complete` event present

Failures on any of these are findings. Report each specifically — "no file_merged events found for run migrate-f01a70" is more actionable than "transaction log incomplete."

## Pre-0.3.6 installations

Plugin versions before 0.3.6 didn't emit `exempt_verbatim` subtypes, `structural_audit_complete` events, or pre-run_complete assertions. If the plugin_version in the manifest is < 0.3.6, relax checks 5 and 7 — their absence is expected, not a defect. Continue to surface the fact that the plugin is old in the report, since the user may want to re-migrate against current plugin to benefit from the audit gates.
