# Improvement Audit Methodology

Detailed patterns for extracting SDLC process improvements from sessions and commits. The goal is to identify how the SDLC itself should evolve — not whether it was followed (that's compliance), but whether it's good enough.

## The Self-Improvement Loop

```
Session work → Improvement audit → Process changes → Better session work
```

Every session is data. Friction, corrections, missing knowledge, and process bypasses are signals that the SDLC has gaps. The improvement audit reads those signals and proposes targeted changes.

## Extraction from Sessions

### Process Friction Signals

Scan the conversation for moments where the SDLC process either helped or hindered:

**Skill invocation patterns:**
- Was a skill invoked? Which one? Did it fit the task?
- Was a skill NOT invoked when it should have been? (User did work that matches a skill's trigger but didn't use it)
- Was a skill invoked but abandoned mid-workflow? (Skill didn't fit)
- Were multiple skills considered before choosing one? (Ambiguous trigger conditions)

**Workflow mismatch:**
- Did the skill's phase structure match the actual work? (Steps skipped, steps added, steps reordered)
- Were there phases in the work that no skill covers?
- Did the user have to interrupt the skill workflow to handle something unexpected?

**Agent dispatch issues:**
- Were agents dispatched that weren't useful? (Wrong agent for the task)
- Were agents missing from dispatch that should have been included?
- Did agent dispatches lack necessary context? (Agent had to re-discover what the skill should have provided)
- Were agents re-dispatched with corrected prompts? (Context quality issue)

**Decision point gaps:**
- Were there decisions where the user had to make a call with no guidance from the process?
- Were there decisions where the SDLC gave guidance but it was wrong or outdated?
- Were there decisions that come up every time for this task type? (Playbook candidate)

### Knowledge Gap Signals

**External lookups that should be internal:**
- Context7 queries for information that should be in knowledge stores
- Web searches for patterns the project uses regularly
- User providing information that should be documented ("The Railway config needs X")
- Assistant reading external docs that could be distilled into knowledge YAML

**Agent context deficiencies:**
- Agent produced incorrect output due to missing domain knowledge
- Agent had to be told something that a knowledge file should have provided
- Agent re-discovered a pattern that was already in a parking lot but not promoted
- Agent's work contradicted an existing knowledge rule (rule not loaded or not applicable)

**Discipline parking lot candidates:**
- Insights that emerged during the session that are reusable
- Patterns that were discovered by reading code that should be formalized
- Cross-discipline observations (testing session reveals coding pattern)

### Skill Deficiency Signals

**Phase-level issues:**
- A skill's workflow has a phase that consistently produces incomplete results
- A skill's workflow is missing a phase that the work always requires
- A skill's phase ordering doesn't match the natural order of the work

**Template/output issues:**
- Skill produces an artifact that doesn't match what's actually needed
- Artifact sections are consistently skipped or marked N/A
- Artifact is missing sections that the work always requires

**Trigger issues:**
- Skill triggers on queries it shouldn't handle
- Skill doesn't trigger on queries it should handle
- Multiple skills could trigger — ambiguous boundaries

### Structural Gap Signals

- Task types repeated without playbooks
- Disciplines exercised without parking lots
- Agent roles not in the context map
- Process docs that contradict each other
- CLAUDE-SDLC.md out of sync with actual skill behavior

## Extraction from Commits

When working from commits without a session:

### Commit Pattern Analysis

| Pattern | Signal | Improvement Target |
|---------|--------|--------------------|
| `fix:` after `feat:` on same files | Correction — feature had a gap | Playbook gotcha, or skill phase ordering |
| Config-only commits after implementation | Infrastructure setup missed initially | Skill should include setup phase earlier |
| Same file edited 3+ times in sequence | Iterative correction | Knowledge gap — pattern not codified |
| Revert commits | Approach was wrong | Decision point needs better guidance |
| Migration commits after implementation | Database setup out of order | Playbook ordering, or skill phase ordering |
| Large commits without `d<N>:` prefix | Untracked substantial work | Process awareness gap |
| Commits touching knowledge/discipline files | Process learning happened | Check if the learning was also captured in changelog |

### Diff Analysis

For significant commits, read the full diff:
- **New files created:** Do they represent new patterns that should be in knowledge stores?
- **Config files modified:** Are these configurations documented anywhere? Should they be?
- **Test files added/modified:** Do they reveal testing patterns not in the testing knowledge store?
- **Dependency changes:** Were version bumps or new packages added mid-stream? (Setup gap)

### Cross-referencing with Playbooks

If the commits match an existing playbook's task type:
1. Read the playbook
2. Map the commit sequence to the playbook's phases
3. Identify: were all playbook phases represented in commits? Were there commits for work NOT in the playbook?
4. If gaps exist, propose playbook updates

## Categorization Framework

Every finding gets categorized for actionability:

### Category: Process Friction

**Improvement types:**
- Skill workflow modification (add/remove/reorder phases)
- Skill trigger refinement (broader or narrower matching)
- New skill proposal (task type has no skill)
- Process doc update (guidance missing or wrong)

**Severity:**
- **High:** Friction that caused errors, wasted significant time, or forced process bypass
- **Medium:** Friction that slowed work noticeably but didn't cause errors
- **Low:** Minor friction, opportunity for smoother workflow

### Category: Knowledge Gap

**Improvement types:**
- Knowledge YAML addition (new file or new rules in existing file)
- Discipline parking lot entry (insight not yet validated)
- Agent context map update (wire knowledge to the right agents)
- Playbook knowledge context update (add files to playbook's context list)

**Severity:**
- **High:** Missing knowledge caused incorrect output or significant rework
- **Medium:** Missing knowledge required manual lookup but work completed correctly
- **Low:** Knowledge exists elsewhere but isn't surfaced at the right time

### Category: Skill Deficiency

**Improvement types:**
- Phase addition/modification/removal
- Agent recommendation update
- Template section update
- Gate condition change

**Severity:**
- **High:** Skill produced wrong output or missed critical steps
- **Medium:** Skill workflow needed manual adjustment to fit the task
- **Low:** Skill worked but could be smoother

### Category: Structural Gap

**Improvement types:**
- New playbook proposal
- New discipline proposal
- Context map addition
- Process doc creation/update

**Severity:**
- **High:** Missing structure caused process failure or significant confusion
- **Medium:** Missing structure required workaround
- **Low:** Missing structure is a nice-to-have for future work

## Proposing Changes

Each proposal must include:

1. **Target:** Specific file and section to modify
2. **Change type:** Add / Modify / Remove
3. **Description:** What to change and why
4. **Evidence:** Where in the session/commits this gap was observed
5. **Severity:** High / Medium / Low
6. **Draft change:** For skill/process modifications, include the actual text to add or modify. For knowledge additions, include a YAML skeleton.

### Proposal Quality Bar

- **Specific:** "Add env-var verification phase to sdlc-execute after PRE-GATE" not "improve the execution skill"
- **Evidenced:** "In session X, the Railway SIGNING_SECRET was missing because the skill doesn't check env vars before deploy" not "env vars are important"
- **Proportional:** Don't propose skill rewrites for single-session friction. Don't propose parking lot entries for established patterns.
- **Non-duplicative:** Check existing knowledge stores and parking lots before proposing additions

## Applying Changes

When the user approves proposals:

1. **Skills:** Edit SKILL.md directly. For phase additions, place in the workflow where the analysis showed it was needed. Update the workflow diagram if present.
2. **Knowledge stores:** Create or update YAML files. Follow existing conventions in the target store. Set `spec_relevant: false` for new files (safe default).
3. **Discipline parking lots:** Add entries with `[NEEDS VALIDATION]` marker, dated, with source reference.
4. **Process docs:** Edit directly. Ensure changelog entry is written in the same step.
5. **Playbooks:** For updates to existing playbooks, edit directly and update `last_validated`. For new playbook proposals, note for `sdlc-playbook-generate` — don't auto-create.
6. **Context map:** Add agent-to-knowledge mappings. Verify the mapped files exist.

**Migration protection:** When applying fixes to framework files (process docs and skills), determine whether the fix is project-specific or a framework correction (see `[sdlc-root]/process/project-section-markers.md` for the full convention):

- **Framework correction** (e.g., fixing a typo in a framework-defined phase, correcting a gate condition) — apply directly, no markers needed. These should flow back upstream.
- **Project-specific fix to process/skill files** (e.g., adding a project-specific phase to a skill) — wrap in `PROJECT-SECTION` markers:

```html
<!-- PROJECT-SECTION-START: audit-improve-YYYY-MM-DD-description -->
... project-specific fix content ...
<!-- PROJECT-SECTION-END: audit-improve-YYYY-MM-DD-description -->
```

**No markers needed for project-specific files:** Knowledge YAML files, discipline parking lot entries, and agent-context-map.yaml are project-owned — they're not overwritten during framework migrations, so no markers are required.

**Always update `[sdlc-root]/process/sdlc_changelog.md`** for every process change. This is a hard rule — changelog entries are written in the same step as the change, not deferred.
