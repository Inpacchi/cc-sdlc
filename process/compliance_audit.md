# SDLC Compliance Audit

## Purpose

A compliance audit compares a project's current documentation structure and practices against the SDLC framework standards. It identifies gaps, stale references, and missing artifacts — then proposes fixes for user approval.

**When to run:**
- After bootstrapping the SDLC into an existing project
- Periodically (monthly or at major milestones) as a health check
- When onboarding a new team member or agent who notices inconsistencies
- After a large chronicle organization pass

**Trigger:** Say **"Let's run an SDLC compliance audit"**

---

## What Gets Audited

| Area | What to Check | Standard |
|------|---------------|----------|
| CLAUDE.md | Has SDLC compliance section and commands table | `~/src/ops/sdlc/skeleton/CLAUDE.md` |
| CLAUDE.md references | All file paths point to existing files | No broken links |
| `_index.md` coverage | Every concept chronicle has an index | 100% coverage |
| Templates | Project has all SDLC templates | 5 templates from `~/src/ops/sdlc/templates/` |
| current_work hygiene | No completed deliverables lingering | Specs/results archived after chronicle org |
| Directory structure | Standard directories exist | `current_work/{specs,planning,results,issues}` |
| Concept registry | Chronicle organization guide is current | All concepts listed |

---

## Audit Process

### Phase 1: Discovery

Gather facts without making changes.

**1.1 Check CLAUDE.md**

```bash
# Read the file
cat CLAUDE.md
```

Verify:
- [ ] SDLC Process Compliance section exists
- [ ] SDLC Commands table exists with all standard commands
- [ ] All file path references point to existing files
- [ ] Key references section includes SDLC process docs

**1.2 Check directory structure**

```bash
# Standard directories
ls docs/current_work/{specs,planning,results,issues}

# Chronicle structure
ls -d docs/chronicle/*/

# Templates
ls docs/templates/
```

**1.3 Check _index.md coverage**

```bash
# List concepts without indexes
for dir in docs/chronicle/*/; do
  [ -f "$dir/_index.md" ] || echo "Missing: $dir"
done
```

**1.4 Check for stale current_work**

```bash
# Completed results still in current_work
ls docs/current_work/results/*result.md

# Cross-reference with chronicles — are these already archived?
```

**1.5 Check templates**

Compare project templates against SDLC standard:
```bash
ls docs/templates/
# Expected: spec_template.md, planning_template.md, cc_prompt_template.md,
#           stepwise_result_template.md, concept_index_template.md
```

### Phase 2: Categorize Findings

For each gap found, classify:

| Severity | Meaning | Action |
|----------|---------|--------|
| **High** | CC behavior affected — may skip process or miss context | Fix immediately |
| **Medium** | Navigation or discoverability impaired | Fix in this pass |
| **Low** | Cosmetic or minor inconvenience | Fix if time permits |
| **Info** | Non-standard but acceptable | Document, no action needed |

### Phase 3: Create Proposal

Write a compliance proposal using the template at `~/src/ops/sdlc/templates/compliance_audit_template.md`.

**Key sections:**
- Summary table of all gaps with severity
- Detailed description of each gap with proposed fix
- Decision points requiring user input
- Recommended implementation order
- Non-standard items that are acceptable (informational)

### Phase 4: Walk Through Gaps One by One

Present each gap to the user individually for approval. This keeps decisions focused and avoids overwhelming the user with the full proposal at once.

**For each gap:**
1. State the gap title and severity
2. Summarize the recommendation concisely
3. Ask for approval (or present options if a decision is needed)
4. Implement immediately on approval
5. Update the summary table's Resolution column

**Resolution tracking markers:**

| Marker | Meaning |
|--------|---------|
| `--` | Not yet reviewed |
| `APPROVED` | User approved the proposed fix |
| `DECIDED` | User chose between options |
| `DONE` | Fix implemented |
| `SKIPPED` | User chose no action |

Update the Resolution column in the summary table as each gap is addressed. This provides a live progress view within the proposal document itself.

**Decision points to surface:**
- Any gap where multiple fix approaches exist
- Non-standard directories: keep, consolidate, or restructure?
- Any proposed changes that affect existing workflows

### Phase 5: Implement

After approval, implement fixes in this order (or immediately per gap if using the one-by-one approach):

1. **CLAUDE.md updates** — Highest impact, enables all other SDLC features
2. **Template copies** — Quick win, no risk
3. **_index.md creation** — Requires reading concept contents
4. **Stale reference fixes** — Path updates
5. **current_work cleanup** — Archive or remove completed items
6. **Prompt cleanup** — Per user's chosen approach

### Phase 6: Verify and Commit

Re-run the discovery checks to confirm all gaps are resolved.

```bash
git add docs/
git commit -m "docs: SDLC compliance audit fixes"
```

---

## Standard Checklist

Use this as a quick pass/fail checklist:

- [ ] CLAUDE.md has SDLC Process Compliance section
- [ ] CLAUDE.md has SDLC Commands table with all commands
- [ ] All CLAUDE.md file references resolve to existing files
- [ ] All concept chronicles have `_index.md`
- [ ] `docs/templates/` has all 5 standard templates
- [ ] `current_work/` contains only active (non-chronicled) work
- [ ] No orphaned prompts for completed deliverables
- [ ] Standard directory structure exists
- [ ] Concept registry (if maintained) is up to date

---

## Anti-Patterns

### Don't
- Run the audit and implement fixes without showing the proposal
- Treat non-standard directories as violations (the SDLC is additive)
- Delete files during the audit — only the implementation phase changes files
- Audit during active development — wait for a natural pause

### Do
- Present findings objectively with severity ratings
- Let the user decide on ambiguous items
- Document accepted deviations as "informational" findings
- Run the full checklist even if the project "looks fine"
