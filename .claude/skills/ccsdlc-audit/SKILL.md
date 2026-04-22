---
name: ccsdlc-audit
description: >
  Unified auditing skill for the cc-sdlc framework source repo with two modes: compliance and
  improvement. Compliance mode audits manifest completeness, cross-reference consistency, stale
  references, changelog freshness, knowledge store conventions, discipline health, skill/agent
  convention compliance, and setup.sh correctness. Improvement mode analyzes sessions and/or
  commits to identify framework gaps — skill deficiencies, knowledge store gaps, process doc
  issues, and structural problems. Both modes can run against the current session or be fed a
  previous session or commit range. Triggers on "sdlc audit", "audit the framework", "run a
  framework audit", "compliance audit", "audit this session", "audit for improvements",
  "what can we improve about the framework", "framework health check", "check framework health",
  "validate the framework", "check sdlc compliance", "audit these commits",
  "process improvement audit".
  Do NOT use for generating playbooks from sessions — use sdlc-playbook-generate.
  Do NOT use for bulk knowledge import — use sdlc-ingest.
---

# Framework Audit

Unified auditing for both structural compliance and process improvement of the cc-sdlc source repo. Two modes, flexible inputs.

**Argument:** `$ARGUMENTS` (mode + optional source — see Input Resolution below)

## Modes

| Mode | Purpose | Output |
|------|---------|--------|
| **Compliance** | Verify framework structure, manifest completeness, cross-references, conventions | Findings table + inline report |
| **Improve** | Identify framework gaps — skill deficiencies, knowledge store gaps, process doc issues | Improvement proposals targeting skills, process docs, knowledge stores, disciplines |

## Input Resolution

Parse `$ARGUMENTS` to determine mode and source:

| Invocation | Mode | Source |
|-----------|------|--------|
| `/ccsdlc-audit` (no args) | Compliance | Current framework state |
| `/ccsdlc-audit compliance` | Compliance | Current framework state |
| `/ccsdlc-audit compliance <session>` | Compliance | Specific session — did it follow framework conventions? |
| `/ccsdlc-audit compliance <commit(s)>` | Compliance | Specific commits — do they maintain framework consistency? |
| `/ccsdlc-audit improve` | Improve | Current session |
| `/ccsdlc-audit improve <session>` | Improve | Past session |
| `/ccsdlc-audit improve <commit(s)>` | Improve | Specific commits |
| `/ccsdlc-audit improve <session> <commit(s)>` | Improve | Session + commits combined |

**Identifying sessions vs commits in arguments:**
- Session identifiers: UUIDs, quoted names, or search terms (resolved against JSONL files)
- Commit identifiers: 7+ char hex strings, commit ranges (`abc123..def456`), or branch names
- When ambiguous, ask the user

**Session location:** Session JSONL files live in `~/.claude/projects/<project-dir-hash>/`. Locate by scanning for matching content or session ID. See `references/session-reading.md` for JSONL structure.

## Compliance Mode

Verify the framework's health across 9 audit dimensions. Full methodology in `references/compliance-methodology.md`.

### Workflow

```
DISPATCH AUDITOR → REPORT → TRIAGE → FIX
```

**Dispatch the `sdlc-compliance-auditor` subagent** to perform the 9-dimension scan. The subagent reads the methodology, scans all dimensions, and returns structured findings with a score. This skill then handles the interactive triage and fix phases.

### Audit Dimensions (summary)

1. **Manifest completeness** — Every file on disk in tracked directories is in `skeleton/manifest.json` and vice versa
2. **Cross-reference consistency** — Skills in manifest have CLAUDE-SDLC.md commands; agents in manifest; knowledge files wired in context map
3. **Stale reference scan** — Grep for old/removed skill/agent/concept names across the codebase
4. **Changelog freshness** — Process changes have corresponding entries in `process/sdlc_changelog.md`
5. **Knowledge store conventions** — YAML structure, README completeness, `spec_relevant` fields
6. **Discipline health** — Parking lot entries have triage markers, cross-discipline flow
7. **Skill convention compliance** — Frontmatter format (folded scalar descriptions), required sections, anti-triggers
8. **Agent convention compliance** — Proper frontmatter, tools lists, when-to-use descriptions
9. **Setup.sh correctness** — Installation script copies all manifest files, agent paths go to `.claude/agents/`

### Compliance with Session/Commit Input

When fed a session or commits (not just current state):
- **Session input:** Read the conversation and verify framework conventions were followed — were consistency checks run? Were changelogs updated? Were manifest entries added for new files?
- **Commit input:** Check whether commits maintain framework consistency. Cross-reference changes against manifest, CLAUDE-SDLC.md, and changelog. Flag process file changes without changelog entries.

### Output

Present findings to user in a structured format (score/10, verdict, findings table). No separate audit artifact file — this is the source repo, not a child project.

### Interactive Triage Phase

After presenting the audit report, if any discipline parking lot entries are promotion candidates (from Dimension 6), run an interactive triage session. See `references/compliance-methodology.md` step 11 for the full workflow.

The triage phase presents candidates grouped by discipline and asks the user to decide on each: promote to knowledge store, defer (with reason), or leave as-is. Promotions are applied immediately — the audit creates or updates the target knowledge store file and marks the parking lot entry as `Promoted -> [target file]`.

## Improvement Mode

Analyze sessions and/or commits to identify how the cc-sdlc framework itself should evolve. Full methodology in `references/improvement-methodology.md`.

### Workflow

```
LOCATE → EXTRACT → CATEGORIZE → PROPOSE → (optional) APPLY → CHANGELOG
```

### What to Look For

**Skill deficiencies** — specific skill behaviors that produced suboptimal results in child projects or this repo:
- Steps in a skill workflow that were skipped or done out of order
- Missing phases that the work required
- Agent recommendations in skills that were wrong for the task
- Template sections that didn't fit the actual output needed
- Trigger phrases that are too broad or too narrow

**Knowledge gaps** — information that was needed but didn't exist in the knowledge layer:
- Patterns discovered during framework development that should be codified
- Gotchas encountered that no knowledge file warned about
- Agent context map missing relevant knowledge file mappings
- Knowledge store YAML files missing important rules or patterns

**Process friction** — moments where the framework's own process slowed work down:
- Consistency checks that miss important validations
- Setup.sh not handling edge cases
- CLAUDE-SDLC.md guidance that doesn't match actual skill behavior
- Process docs that contradict each other or are outdated

**Structural gaps** — missing infrastructure in the framework:
- Task types that have no playbook but should
- Disciplines being exercised without a parking lot
- Agent roles that aren't mapped in the context map
- Missing skill types for common development workflows

### Improvement with Commit Input

When fed commits (without a session):
- Read commit messages and diffs for process signals
- Look for patterns: commits that fix previous commits (correction signal), multiple small commits to the same file (iteration signal)
- Check whether commits updated the changelog, manifest, and CLAUDE-SDLC.md when they should have
- Cross-reference against existing playbooks — does the commit pattern match a playbook?

### Output

Present categorized improvement proposals:

```
IMPROVEMENT AUDIT REPORT
═══════════════════════════════════════════════════════════════

Source: [session ID / commit range / current session]
Analyzed: [message count] messages, [commit count] commits

SKILL DEFICIENCIES
  [numbered list with target skill and proposed change]

KNOWLEDGE GAPS
  [numbered list with target discipline/store]

PROCESS FRICTION
  [numbered list of friction points with severity]

STRUCTURAL GAPS
  [numbered list with proposed addition]

PROPOSED CHANGES
| # | Target | Change Type | Description | Severity |
|---|--------|-------------|-------------|----------|
| 1 | skills/sdlc-execute/SKILL.md | Modify | Add env-var checklist phase | High |
| 2 | knowledge/architecture/ | Add | New deployment patterns file | Medium |
| 3 | disciplines/deployment.md | Add entry | Service dependency ordering | Low |
```

### Applying Improvements

When the user approves proposals, apply changes directly:
- Skill modifications → edit the SKILL.md in `skills/`
- Knowledge additions → create/update YAML files in `knowledge/`
- Discipline entries → add to parking lot in `disciplines/` with `[NEEDS VALIDATION]`
- Process doc updates → edit the relevant file in `process/`
- Agent modifications → edit the agent file in `agents/`
- New playbook proposals → note for `sdlc-playbook-generate` (don't auto-create)

Update `process/sdlc_changelog.md` for every process change applied.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The framework looks fine, no improvements needed" | Every session has friction. Look harder at correction signals and mid-stream discoveries. |
| "I'll fix everything without asking" | Present proposals first. The user decides what to change. |
| "This is just a compliance audit with extra steps" | Compliance checks structure. Improvement analyzes behavior. Different inputs, different outputs. |
| "I'll propose sweeping framework changes" | Proportional recommendations. Small friction gets small fixes. |
| "The session didn't follow conventions, that's a compliance failure" | For improvement mode, convention bypass is a signal, not a failure. Ask: why was it bypassed? That's the improvement. |

## Integration

- **Dispatches:** `sdlc-compliance-auditor` subagent (compliance mode 9-dimension scan)
- **Complements:** `sdlc-playbook-generate` (playbooks capture "how to repeat"; this captures "how to improve")
- **Feeds into:** skill modifications, knowledge store updates, discipline parking lots, process doc changes, manifest updates, CLAUDE-SDLC.md updates
- **Uses:** session JSONL, git history, all framework source files

## Additional Resources

### Reference Files

- **`references/compliance-methodology.md`** — Full 9-dimension framework compliance audit methodology, report format, severity levels, guiding principles
- **`references/improvement-methodology.md`** — Detailed patterns for extracting framework improvements from sessions and commits
- **`references/session-reading.md`** — JSONL message type reference and extraction patterns for reading Claude Code session files
