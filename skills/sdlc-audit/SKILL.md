---
name: sdlc-audit
description: >
  Unified SDLC auditing skill with two modes: compliance and improvement. Compliance mode audits
  project structure, deliverable integrity, knowledge layer health, and migration correctness.
  Improvement mode analyzes sessions and/or commits to identify process gaps, missing knowledge,
  and skill modifications that would improve the SDLC itself. Both modes can run against the current
  session or be fed a previous session or commit range. Triggers on "sdlc audit", "audit the sdlc",
  "run an sdlc audit", "compliance audit", "audit this session", "audit for improvements",
  "what can we improve about the process", "sdlc health check", "check sdlc compliance",
  "audit these commits", "process improvement audit".
  Do NOT use for generating playbooks from sessions — use sdlc-playbook-generate.
  Do NOT use for bulk knowledge import — use sdlc-ingest.
---

# SDLC Audit

Unified auditing for both structural compliance and process improvement. Two modes, flexible inputs.

**Argument:** `$ARGUMENTS` (mode + optional source — see Input Resolution below)

## Modes

| Mode | Purpose | Output |
|------|---------|--------|
| **Compliance** | Verify SDLC structure, deliverables, knowledge layer, migration integrity | Findings table + audit artifact at `docs/current_work/audits/` |
| **Improve** | Identify process gaps, missing knowledge, skill/workflow modifications | Improvement proposals targeting skills, process docs, knowledge stores, disciplines |

## Input Resolution

Parse `$ARGUMENTS` to determine mode and source:

| Invocation | Mode | Source |
|-----------|------|--------|
| `/sdlc-audit` (no args) | Compliance | Current project state |
| `/sdlc-audit compliance` | Compliance | Current project state |
| `/sdlc-audit compliance <session>` | Compliance | Specific session — did it follow process? |
| `/sdlc-audit compliance <commit(s)>` | Compliance | Specific commits — do they have proper artifacts? |
| `/sdlc-audit improve` | Improve | Current session |
| `/sdlc-audit improve <session>` | Improve | Past session |
| `/sdlc-audit improve <commit(s)>` | Improve | Specific commits |
| `/sdlc-audit improve <session> <commit(s)>` | Improve | Session + commits combined |

**Identifying sessions vs commits in arguments:**
- Session identifiers: UUIDs, quoted names, or search terms (resolved against JSONL files)
- Commit identifiers: 7+ char hex strings, commit ranges (`abc123..def456`), or branch names
- When ambiguous, ask the user

**Session location:** Session JSONL files live in `~/.claude/projects/<project-dir-hash>/`. Locate by scanning for matching content or session ID. See `references/session-reading.md` for JSONL structure.

## Compliance Mode

Verify the project's SDLC health across 9 audit dimensions. Full methodology in `references/compliance-methodology.md`.

### Workflow

```
DISPATCH AUDITOR → REPORT → TRIAGE → FIX
```

**Dispatch the `sdlc-compliance-auditor` subagent** to perform the 9-dimension scan. The subagent reads the methodology, scans all dimensions, and returns structured findings with a score and promotion candidates. This skill then handles the interactive triage and fix phases.

### Audit Dimensions (summary)

1. **Deliverable catalog integrity** — `docs/_index.md` matches reality
2. **Artifact traceability** — spec → plan → result chains complete
3. **Untracked work detection** — git commits without deliverable tracking
4. **Knowledge freshness** — CLAUDE.md, agent memories, docs current
5. **Process health indicators** — tracked vs untracked ratio, archive freshness, changelog coverage
6. **Knowledge layer health** — disciplines, knowledge stores, triage status, wiring, playbooks, usage
7. **Migration integrity** — manifest version, file completeness, content-merge correctness
8. **Agent memory pattern mining** — recurring findings worth promoting
9. **Recommendation follow-through** — previous audit recommendations acted on?

### Compliance with Session/Commit Input

When fed a session or commits (not just current state):
- **Session input:** Read the conversation and verify SDLC process was followed — were skills invoked? Were deliverable IDs assigned? Were specs written before execution?
- **Commit input:** Check whether commits have corresponding deliverable artifacts. Cross-reference commit messages against `docs/_index.md`. Flag substantial multi-file changes without tracking.

### Output

Produce audit artifact at `docs/current_work/audits/sdlc_audit_YYYY-MM-DD.md` using the report format in `references/compliance-methodology.md`. Present findings to user in the standardized format from CLAUDE-SDLC.md (score/10, verdict, findings table).

### Interactive Triage Phase

After presenting the audit report, if any parking lot entries are promotion candidates (from Dimensions 6c and 8), run an interactive triage session. See `references/compliance-methodology.md` step 11 for the full workflow.

The triage phase presents candidates grouped by discipline and asks CD to decide on each: promote to knowledge store, defer (with reason), or leave as-is. Promotions are applied immediately — the audit creates or updates the target knowledge store file and marks the parking lot entry as `Promoted → [target file]`.

## Improvement Mode

Analyze sessions and/or commits to identify how the SDLC itself should evolve. Full methodology in `references/improvement-methodology.md`.

### Workflow

```
LOCATE → EXTRACT → CATEGORIZE → PROPOSE → (optional) APPLY → CHANGELOG
```

### What to Look For

**Process friction** — moments where the SDLC process slowed the work down, was bypassed, or didn't have guidance for the situation:
- Skills invoked but not helpful (wrong workflow for the task)
- Skills not invoked when they should have been
- Manual steps that should be automated in a skill
- Decision points where the process offered no guidance

**Knowledge gaps** — information that was needed but didn't exist in the knowledge layer:
- External docs consulted that should be in knowledge stores
- Patterns discovered during work that should be codified
- Gotchas encountered that no knowledge file warned about
- Agent dispatches that lacked necessary context

**Skill deficiencies** — specific skill behaviors that produced suboptimal results:
- Steps in a skill workflow that were skipped or done out of order
- Missing phases that the work required
- Agent recommendations in skills that were wrong for the task
- Template sections that didn't fit the actual output needed

**Structural gaps** — missing infrastructure in the SDLC:
- Task types that have no playbook but should
- Disciplines being exercised without a parking lot
- Agent roles that aren't mapped in the context map
- Process docs that contradict each other or are outdated

### Improvement with Commit Input

When fed commits (without a session):
- Read commit messages and diffs for process signals
- Look for patterns: commits that fix previous commits (correction signal), config-only commits after feature commits (setup gap), multiple small commits to the same file (iteration signal)
- Cross-reference against existing playbooks — does the commit pattern match a playbook? If so, were the playbook's steps followed?
- Check whether the commits produced or updated SDLC artifacts (specs, plans, results)

### Output

Present categorized improvement proposals:

```
IMPROVEMENT AUDIT REPORT
═══════════════════════════════════════════════════════════════

Source: [session ID / commit range / current session]
Analyzed: [message count] messages, [commit count] commits

PROCESS FRICTION
  [numbered list of friction points with severity]

KNOWLEDGE GAPS
  [numbered list with target discipline/store]

SKILL DEFICIENCIES
  [numbered list with target skill and proposed change]

STRUCTURAL GAPS
  [numbered list with proposed addition]

PROPOSED CHANGES
| # | Target | Change Type | Description | Severity |
|---|--------|-------------|-------------|----------|
| 1 | skills/sdlc-execute/SKILL.md | Modify | Add env-var checklist phase | High |
| 2 | knowledge/architecture/ | Add | Railway deployment patterns | Medium |
| 3 | disciplines/deployment.md | Add entry | Service dependency ordering | Low |
```

### Applying Improvements

When the user approves proposals, apply changes directly:
- Skill modifications → edit the SKILL.md
- Knowledge additions → create/update YAML files
- Discipline entries → add to parking lot with `[NEEDS VALIDATION]`
- Process doc updates → edit the relevant process file
- New playbook proposals → note for `sdlc-playbook-generate` (don't auto-create)

Update `ops/sdlc/process/sdlc_changelog.md` for every process change applied.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The process looks fine, no improvements needed" | Every session has friction. Look harder at correction signals and mid-stream discoveries. |
| "I'll fix everything without asking" | Present proposals first. The user decides what to change. |
| "This is just a compliance audit with extra steps" | Compliance checks structure. Improvement analyzes behavior. Different inputs, different outputs. |
| "I'll propose sweeping process changes" | Proportional recommendations. Small friction gets small fixes. |
| "The session didn't follow SDLC, that's a compliance failure" | For improvement mode, process bypass is a signal, not a failure. Ask: why was it bypassed? That's the improvement. |

## Integration

- **Dispatches:** `sdlc-compliance-auditor` subagent (compliance mode 9-dimension scan)
- **Complements:** `sdlc-playbook-generate` (playbooks capture "how to repeat"; this captures "how to improve")
- **Feeds into:** skill modifications, knowledge store updates, discipline parking lots, process doc changes
- **Uses:** session JSONL, git history, all SDLC project artifacts, existing knowledge layer

## Additional Resources

### Reference Files

- **`references/compliance-methodology.md`** — Full 9-dimension compliance audit methodology, report format, severity levels, guiding principles (migrated from sdlc-compliance-auditor agent)
- **`references/improvement-methodology.md`** — Detailed patterns for extracting process improvements from sessions and commits
- **`references/session-reading.md`** — JSONL message type reference and extraction patterns for reading Claude Code session files
