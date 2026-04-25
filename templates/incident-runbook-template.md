# Playbook: Incident — [Symptom Class Name]

**Last validated:** YYYY-MM-DD
**Validation triggers:**
- [Condition that would make this runbook stale, e.g., "observability stack changes"]
- [Another trigger, e.g., "deploy mechanism replaced"]

---

## When to use

Use this playbook during TRIAGE phase of `sdlc-debug-incident` when the symptom is [description of the symptom class].

Signs this playbook applies:
- [Observable signal 1, e.g., "monitoring shows error-rate spike on the API"]
- [Observable signal 2, e.g., "service is running but emitting 5xx"]

Distinct from: [name other playbooks that cover similar-but-different symptoms and how to tell them apart].

---

## Recommended Agents

| Agent | Role | Required? |
|-------|------|-----------|
| `debug-specialist` | Lead investigator; runs diagnostic queries, narrows hypothesis | Yes |
| `backend-developer` | Investigates code-path-specific failures | If failure concentrates on a specific endpoint or service path |
| `devops-engineer` | Investigates deploy correlation and infrastructure-level causes | If broad failure or recent deploy |
| `data-architect` | Investigates if connection state or query failures appear in snapshot | If database involvement suspected |

---

## Knowledge Context

When dispatching agents, include:
- `[sdlc-root]/knowledge/architecture/debugging-methodology.yaml` — investigation techniques
- `[sdlc-root]/knowledge/architecture/error-cascade-methodology.yaml` — retry amplification, error classification
- [Add other relevant knowledge files for this incident class]

---

## First response (non-destructive)

These steps take 3–5 minutes. They preserve evidence and narrow the hypothesis space before agent dispatch. All steps are read-only — they produce data, they don't change state.

1. **[Diagnostic step 1].** [Description of what to check, what tool to use, and what the result means.]
   - [Expected result for "this playbook applies" vs. "escalate to different playbook"]

2. **[Diagnostic step 2].** [Description.]

3. **[Diagnostic step 3].** [Description.]

4. **Log the snapshot in the Findings Log** of the incident doc before proceeding to T3 (agent selection).

---

## Severity / escalation

| Condition | Severity |
|-----------|----------|
| [Most severe manifestation] | SEV-1 |
| [Major feature path broken] | SEV-2 |
| [Isolated or partial impact] | SEV-3 |

---

## Rollback path

[Describe the fastest mitigation path for this incident class. When is rollback the right lever? When is it not? What prerequisites must be true before rolling back?]

---

## Key decisions to surface

- **[Decision 1]** — [What tradeoff this decision involves and how the answer affects the investigation path.]
- **[Decision 2]** — [Description.]
- **[Decision 3]** — [Description.]

---

## Reference incidents

[Links to prior postmortems that used this runbook. Update as incidents are closed out and archived.]

- (none yet — this section will populate as incidents using this runbook are closed out)
