# Process Documentation

Workflow rules, behavioral protocols, and process definitions. Skills reference these files instead of duplicating shared logic.

## Files

### Workflow
| File | Purpose |
|------|---------|
| `overview.md` | The full SDLC flow: Idea → Spec → Plan → Execute → Validate → Deploy → Result → Chronicle |
| `deliverable_lifecycle.md` | State machine for deliverables (Draft → In Progress → Validated → Deployed → Complete → Archived) |
| `collaboration_model.md` | How CD (human) and CC (agent system) interact — roles, responsibilities, communication patterns |
| `chronicle_organization.md` | How and when to archive completed work from `current_work/` to `chronicle/` |
| `ad_hoc_reconciliation.md` | Sweeping untracked ad hoc commits back into the deliverable catalog |
| `compliance_audit.md` | What the compliance audit checks and how to run one |

### Shared Behavioral Protocols
| File | Referenced By | Purpose |
|------|-------------|---------|
| `manager-rule.md` | 5+ skills | The orchestrator never writes code — dispatch agents. No size or complexity exceptions. |
| `review-fix-loop.md` | 7 skills | The loop for every review context (code, plan, reference doc): roster rule → verify → dedup/calibrate/classify → fix critical+major → mechanical re-review → exit when no critical/major remain, 3-round cap. Owns the two mirrored critical-steps blocks |
| `finding-classification.md` | 7 skills | FIX / PLAN / INVESTIGATE / DECIDE / PRE-EXISTING taxonomy with per-skill subsets; owns the one severity scale (impact × likelihood) and calibration, the deduplication table, the planning scope-change marker, and Open Minor Findings |
| `discipline_capture.md` | 6 skills | Lightweight protocol for capturing cross-discipline insights during active work |

### Meta
| File | Purpose |
|------|---------|
| `sdlc_changelog.md` | Living record of process changes — what changed, why, and where the change originated |
