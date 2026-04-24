---
name: sdlc-debug-incident
description: >
  Required workflow for any production incident (OOM, service down, elevated error rate,
  data issue, security event) — creates a live investigation doc during active response and
  transforms it into the canonical postmortem after remediation is scoped. Two phases
  auto-detected by doc state: TRIAGE captures hypotheses, timestamped findings, and
  dispatched domain agents in real time; CLOSEOUT restructures the messy doc into the
  project's postmortem template (timeline, root cause, action items) once remediation
  deliverables exist.
  Triggers on "incident", "production incident", "OOM", "service is down", "we had an outage",
  "production issue", "investigate the outage", "postmortem", "incident report",
  "document the incident", "/sdlc-debug-incident".
  Do NOT use for pure debugging without user-visible service impact — dispatch the
  debug-specialist agent directly.
  Do NOT use for writing the remediation plan itself — use sdlc-plan or sdlc-lite-plan once
  TRIAGE identifies candidate deliverables.
  Do NOT use for proactive systemic audits without a triggering incident — use sdlc-audit.
  Do NOT use for generating playbooks from a resolved incident — use sdlc-playbook-generate.
---

# SDLC Debug Incident

Orchestrates the full incident lifecycle: live investigation during active response, then structured postmortem closeout after remediation is scoped. The investigation doc is the single source of truth the whole way through — it starts messy and gets cleaned up, rather than being rewritten from scratch. One skill, two phases, auto-detected.

**Argument:** `$ARGUMENTS` (optional — `triage`, `closeout`, or empty for auto-detect; see Mode Resolution below)

## Modes

| Mode | Purpose | Output |
|------|---------|--------|
| **TRIAGE** | Active investigation — capture hypotheses, findings, dispatched agents, emerging remediation | Live doc at `docs/current_work/incidents/incident_YYYY-MM-DD_slug.md` |
| **CLOSEOUT** | Transform the triage doc into the canonical postmortem; link action items to deliverables | Same file, restructured to match `[sdlc-root]/templates/postmortem_template.md`; candidate for eventual archival |

## Mode Resolution

Parse `$ARGUMENTS` and the working tree to pick a mode:

| Invocation | Condition | Mode |
|------------|-----------|------|
| `/sdlc-debug-incident triage` | Explicit | TRIAGE |
| `/sdlc-debug-incident closeout` | Explicit | CLOSEOUT |
| `/sdlc-debug-incident` (no args) | No incident doc exists for today, or most recent incident doc has `status: triage-active` | TRIAGE |
| `/sdlc-debug-incident` (no args) | Most recent incident doc has `status: remediation-scoped` and all linked deliverables are `Complete` | CLOSEOUT |
| `/sdlc-debug-incident` (no args) | Most recent incident doc has `status: remediation-scoped` but linked deliverables are still in-flight | Ask the user: "Remediation deliverables are still in flight. Run CLOSEOUT now (partial) or wait until all deliverables complete?" |

When the user asks for a specific incident ("close out last week's OOM"), accept either a date (`2026-04-20`) or a slug (`api_oom`) as a second argument and resolve the matching file under `docs/current_work/incidents/`.

---

## Manager Rule and Collaboration

Read and follow `[sdlc-root]/process/manager-rule.md`. It applies unconditionally for the entire session. You orchestrate; domain agents investigate. Never self-investigate past a single layer of code reading — if the root cause isn't obvious after one read of the suspected file, dispatch a domain agent. The incident doc is *your* artifact; the investigation work is the agents'.

Ask-user gates in this skill (the Mode Resolution ambiguity prompt, the T6 escalation after three unconverging dispatch rounds, the C1 partial-closeout choice) follow `[sdlc-root]/process/collaboration_model.md` — use `AskUserQuestion` for structured decisions, not free-text prompts.

Status transitions on the incident doc (`triage-active` → `remediation-scoped` → `complete` / `partial`) and on linked deliverables follow the state machine in `[sdlc-root]/process/deliverable_lifecycle.md`. Do not invent custom states.

## Agent Dispatch Protocol

Every agent dispatched during TRIAGE must receive:

1. **The symptom** — what the user sees or what the monitoring reported. Exact error messages, latency numbers, service IDs, timestamps.
2. **The classification so far** — what's been ruled in and what's been ruled out.
3. **The domain lens** — what this specific agent should look at (not the whole system).
4. **Output format** — a structured finding: observation / impact / suggested next step.
5. **Return budget** — "under 600 words." Agents default to verbose; incidents need density.

Dispatch prompts describe *what to investigate and why*. Agents decide *how*. Do not tell an agent what the root cause is — let them find it independently and converge. Parallel independent investigations are more valuable than one agent being given the answer.

---

## Agent Selection

Pick 3–5 agents per incident based on the symptom. Over-dispatch (10 agents for a small bug) wastes cycles; under-dispatch (1 agent for a multi-domain issue) misses cross-cutting causes.

**Use `[sdlc-root]/process/agent-selection.yaml` as the source of truth for which agent covers which domain.** That file lists the project's actual agents, their dispatch triggers, and their domain coverage — incident triage uses the same role-to-domain mapping as planning and review.

**Default starting point:** `debug-specialist` is the universal entry point when the root cause is unclear — it does structured root cause analysis and narrows the domain. Once the domain is clearer, dispatch the specialist.

**Selection process:**

1. Identify the symptom domain(s) from `agent-selection.yaml`'s `dispatch_when` triggers (e.g., latency → performance-engineer; auth → security-engineer; DB → data-architect; deploy/container → devops-engineer; frontend render → frontend-developer; build/CI → build-engineer; data pipeline → data-engineer; ML/inference → ml-engineer; cross-service → systems-engineer).
2. Always include `debug-specialist` for ambiguous cases.
3. Always include `code-reviewer` if you suspect a recent change introduced the issue.
4. Add `security-auditor` (not `security-engineer`) if the incident is a suspected breach, IDOR, or data exposure — the auditor assesses, the engineer fixes.
5. For ML/retrieval quality regressions, pair `ml-engineer` with whichever evaluation specialist your project has (often `sdet`).

---

## TRIAGE Mode

### Workflow

```
CAPTURE SYMPTOM → CLASSIFY SEVERITY → CREATE/OPEN DOC → SELECT AGENTS → DISPATCH IN PARALLEL → LOG FINDINGS → IDENTIFY CAUSE → RECOMMEND DELIVERABLES → HANDOFF
```

### Steps

### T1. Capture the Symptom

Ask the user (or accept from the invocation context):

- What is observed? (error message, behavior, metric)
- What is the scope? (one user, one tenant, all users, one service)
- When did it start? (if known)
- What changed recently? (last deploy, config change, env var update)

Follow `[sdlc-root]/process/incident_response.md` for severity classification (SEV-1 to SEV-4). Err higher when uncertain — downgrading is cheaper than under-responding.

### T2. Create or Open the Incident Doc

Path: `docs/current_work/incidents/incident_YYYY-MM-DD_{slug}.md`. If the directory does not exist, create it. The `{slug}` is a 2–4 word identifier of the incident (e.g., `api_oom`, `auth_session_leak`, `search_quality_drop`).

If a doc for today already exists for the same slug, open it and continue — do not create duplicates. If the symptom is distinct from an existing doc for today (different service, different symptom), use a disambiguating slug.

Scaffold the doc with the TRIAGE template:

```markdown
---
type: incident
severity: SEV-{N}  # or SEV-?  if still assessing
date: YYYY-MM-DD
service: {service-name}  # e.g., "api", "worker", "frontend"
status: triage-active
started_at: YYYY-MM-DDTHH:MM:SSZ  # best-available estimate of incident start
detected_at: YYYY-MM-DDTHH:MM:SSZ  # when someone noticed
author: CC
related_deliverables: []  # filled in as deliverables get created
---

# Incident — {Title}

## Symptom
- Observed: {what}
- Scope: {who is affected}
- First seen: {time, if known}
- Recent changes: {deploys, env vars, merges in the last N hours}

## Hypotheses (live — add, don't delete)
- [ ] H1: {description}  — proposed {timestamp}
- [ ] H2: {description}  — proposed {timestamp}

## Ruled Out (preserve, don't delete)
- {hypothesis}  — ruled out by {evidence}, {timestamp}

## Findings Log (timestamped, append-only)
- {timestamp} — {finding from agent/investigation}

## Dispatched Agents
| Agent | Dispatched | Returned | Key finding |
|-------|------------|----------|-------------|

## Candidate Remediation
- {item}  — likely deliverable: D{NN} or backlog

## Open Questions
- {question}
```

### T3. Select Agents

Use `[sdlc-root]/process/agent-selection.yaml` to map symptom → specialist. Start with `debug-specialist` + 2–4 domain specialists from the matching `dispatch_when` triggers. State the selection explicitly in the doc under "Dispatched Agents" before dispatching.

### T4. Dispatch in Parallel

Dispatch all selected agents in a single message with multiple tool calls so they run concurrently. Each prompt must follow the Agent Dispatch Protocol. Wait for all to return before synthesis.

### T5. Log Findings

As each agent returns, append a timestamped entry to the Findings Log. Update the Hypotheses section: move anything confirmed to a "leading hypothesis" position, move anything falsified to Ruled Out with the evidence that falsified it.

**Do not delete hypotheses**, even wrong ones. The ruled-out list is future-you's context for the next similar incident.

### T6. Converge or Re-Dispatch

Ask: has at least one hypothesis been confirmed to the point we can scope remediation?

- **Yes** — proceed to T7.
- **No, but we have a narrower domain** — dispatch additional specialists focused on the narrowed area. Loop T4-T6.
- **No, and we've looped 3+ times without convergence** — STOP. Escalate to the user: "Triage has run three rounds without a converging hypothesis. I recommend pausing to add telemetry or log a larger observation window, then resuming." Do not accumulate agents indefinitely.

### T7. Identify Root Cause + Contributing Factors

Write the `Root Cause` section inline in the doc. Distinguish:

- **Proximate cause** — the single thing that broke. Example: "Memory allocator grew to 15 GB under concurrent fan-out."
- **Contributing factors** — conditions that made the proximate cause possible, harder to detect, or harder to fix. Example: "no concurrency cap on the worker, no RSS watchdog, upstream dependency slowness extended request duration."

Root cause is rarely a single event. Be thorough on contributing factors — they drive the action items.

### T8. Recommend Deliverables

Translate the root cause + contributing factors into remediation candidates. For each, state:

- What the deliverable would address
- Estimated tier (lite, full, housekeeping)
- Which existing in-flight deliverables already cover it (if any)

Update the doc frontmatter:

```yaml
status: remediation-scoped
related_deliverables: [D{NN}, D{NN+1}]  # use placeholders if not yet created
```

### T9. Handoff

STOP. The incident doc now has enough to drive remediation, but **this skill does not write plans**.

Output to the user:

1. Summary of root cause and contributing factors
2. Recommended deliverables with tier
3. Explicit handoff: "Run `sdlc-lite-plan` for D{NN} and `sdlc-plan` for D{NN+1} when you're ready. Re-run `/sdlc-debug-incident closeout` once remediation is merged."

Do not invoke `sdlc-plan` or `sdlc-lite-plan` from inside this skill. Keep the boundary sharp — planning is a separate skill with its own dispatch and review loop.

---

## CLOSEOUT Mode

### Workflow

```
DETECT DELIVERABLES → EXTRACT TIMELINE → RESTRUCTURE TO POSTMORTEM → FILL WHAT-WENT-WELL/POORLY → MAP ACTION ITEMS → PRESERVE HYPOTHESIS LOG → REVIEW → (OPTIONAL) ARCHIVE
```

### Steps

### C1. Detect Remediation Deliverables

Read the incident doc's `related_deliverables` frontmatter. Verify each in `docs/_index.md`:

- All `Complete` — proceed.
- Some `In Progress` or `Planning` — ask the user whether to proceed with a partial closeout (valid — "what we know so far") or wait for all to complete. Partial closeout is allowed; label the postmortem's `status` as `partial` in that case.

### C2. Extract Timeline

Walk the Findings Log. Each timestamped entry is a timeline row. Map to the postmortem template's Timeline section:

| Time | Event |
|------|-------|
| HH:MM UTC | {Finding log entry → event} |

Enrich with:

- The `started_at` and `detected_at` from frontmatter as the first two rows
- Deployment / config-change events (cross-reference `git log` against the window)
- Resolution timestamp (when the remediation was deployed or the mitigation was applied)

### C3. Restructure to Postmortem

Load `[sdlc-root]/templates/postmortem_template.md`. Keep the incident doc in place; restructure its body to match the template sections:

- **Summary** — one paragraph synthesizing what happened and how it was resolved.
- **Timeline** — from C2.
- **Impact** — users affected, duration, data loss (none / specific), revenue (usually none pre-launch).
- **Root Cause** — lifted from the TRIAGE doc's Root Cause section, cleaned up.
- **Contributing Factors** — lifted from TRIAGE, numbered.
- **Detection** — how detected, time to detect, could it have been faster.
- **Response** — what worked (as paragraphs) + what could be improved (as paragraphs).
- **Action Items** — table mapping each item to its Deliverable ID. Every row must have a `Deliverable ID` column value — either `D{NN}`, `housekeeping`, or `backlog`.
- **Lessons Learned** — systemic insights, not "don't do the bad thing again." 5-8 items.

### C4. Preserve Hypothesis Log as Appendix

Do NOT delete the Hypotheses, Ruled Out, or Dispatched Agents sections from TRIAGE. Move them to an `## Appendix: Investigation Log` at the end. That content is the reusable learning — future you on a similar incident will mine it.

### C5. Update Frontmatter

```yaml
status: complete  # or 'partial' if some deliverables are still in-flight
resolved_at: YYYY-MM-DDTHH:MM:SSZ
peak_impact: {concise description — e.g., "~20 GB RSS, 14-minute eval blockage"}
```

### C6. Self-Review

Dispatch `code-reviewer` on the final postmortem with the following lens:

- Every action item has an owner and a deliverable ID
- Root cause is specific, not vague ("a bug" is not a root cause per `[sdlc-root]/process/incident_response.md`)
- Contributing factors are distinct from root cause
- No blame assignment — focus is on systems, not people
- Lessons learned are generalizable — they would help on *a different* incident

Apply findings before marking closeout complete.

### C7. Link from Catalog and Deliverables

For each deliverable in `related_deliverables`:

- Add a line to the deliverable's result doc: `**Triggered by:** [incident YYYY-MM-DD](../../current_work/incidents/incident_YYYY-MM-DD_{slug}.md)`
- Optionally add a row for the incident in `docs/_index.md` under a new `## Incidents` section if the project adopts that convention (propose to user — this is a project-level choice).

### C8. Handoff to Archival

STOP. Do not auto-archive. Archival to `docs/chronicle/{concept}/` happens later, when the user invokes `sdlc-archive` and the incident's related deliverables have all completed and themselves been archived.

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll investigate this myself — no need to dispatch" | Manager Rule applies here exactly as in planning. Dispatch `debug-specialist` + specialists. |
| "I'll skip the incident doc — the incident is small" | Even small incidents have reusable lessons. Small incidents → small docs, but there's no floor at which the doc becomes pointless. |
| "I'll name the root cause during T1 from the symptom alone" | Root cause is a conclusion, not a hypothesis. Log it as H1, verify, then move to Root Cause. Premature convergence ends investigation. |
| "I'll delete ruled-out hypotheses to keep the doc clean" | Preserve them. The next engineer investigating a similar symptom wants to see what you checked and why it wasn't that. Ruled-out is signal, not noise. |
| "I'll write the remediation plan inside the closeout" | Out of scope. Hand off to `sdlc-plan` or `sdlc-lite-plan`. Incident skill identifies deliverables; planning skills write them. |
| "I'll auto-run closeout as soon as triage identifies a cause" | No. Closeout requires remediation deliverables to exist. Without them, "Action Items" is empty, which is the useless part of a postmortem. Wait. |
| "I'll merge the triage log into the timeline and delete it" | The hypothesis log becomes the Appendix. Timeline is distinct — it's the ordered public-facing narrative, the appendix is the investigator's scratch pad preserved. |
| "I'll dispatch 8 agents to be thorough" | Over-dispatch dilutes signal. 3-5 with clear domain lenses outperforms 8 with overlapping scope. |
| "I'll use a different template — the project's is too long" | Use `[sdlc-root]/templates/postmortem_template.md` verbatim. Consistency across incidents makes the chronicle searchable. |
| "The kernel OOM-killed us, so there's nothing to investigate — just restart" | SIGKILL leaves no trace, but the conditions that led to the kill are everywhere else: traffic patterns, resource curves, config state. Run TRIAGE. |
| "This is the same as last month's incident, copy-paste the old doc" | New doc, reference the old one. A fresh investigation might find that the cause is different even if the symptom matches. Copying hides regressions in root-cause understanding. |
| "I'll hardcode the agent matrix in this skill" | No — the matrix lives in `agent-selection.yaml` so it stays consistent with planning and review. If a project adds a new domain agent, it shows up in incident triage automatically. |

---

## Integration

- **Depends on:** An observable incident signal — user report, alert, or visible service degradation. Does not run speculatively.
- **Feeds into:** `sdlc-lite-plan` and `sdlc-plan` for remediation deliverables. `sdlc-archive` eventually, when all related deliverables complete.
- **Uses:** `debug-specialist` agent (primary diagnostic during TRIAGE), domain specialists per `[sdlc-root]/process/agent-selection.yaml`, `code-reviewer` for CLOSEOUT review, and project observability tooling (whatever your stack uses) via the corresponding MCPs or CLI access.
- **Complements:** `sdlc-audit` (proactive systemic review — different trigger, different purpose), `sdlc-review-code` (code-level review), `sdlc-playbook-generate` (turns a resolved incident + its remediation into a reusable playbook — runs AFTER CLOSEOUT).
- **Does NOT replace:**
  - The `debug-specialist` agent itself, which can still be dispatched directly for non-incident debugging (e.g., a failing test).
  - `sdlc-plan` / `sdlc-lite-plan`, which own remediation planning. This skill hands off to them.
  - `sdlc-audit` (proactive, curiosity-driven, no triggering incident).
- **DRY notes:** This skill does not duplicate `[sdlc-root]/process/incident_response.md` — it references the process doc for severity classification, triage workflow principles, and postmortem timeline conventions. This skill is the *executable orchestration* of that process. The postmortem template at `[sdlc-root]/templates/postmortem_template.md` is also referenced rather than reinvented; CLOSEOUT's output conforms to it.

---

## Additional Resources

- `[sdlc-root]/process/incident_response.md` — severity classification (SEV-1 to SEV-4), triage workflow, postmortem principles, deliverable lifecycle connection. Read before TRIAGE if you haven't recently.
- `[sdlc-root]/templates/postmortem_template.md` — the canonical postmortem structure. CLOSEOUT output conforms to this template.
- `[sdlc-root]/process/agent-selection.yaml` — domain-to-agent mapping used during T3. Single source of truth shared with planning and review skills.
- `[sdlc-root]/knowledge/architecture/debugging-methodology.yaml` — structured investigation methodology. The `debug-specialist` agent uses this; TRIAGE prompts should reference it when dispatching.
- `[sdlc-root]/process/manager-rule.md` — required reading. You orchestrate; agents investigate.
- `[sdlc-root]/process/collaboration_model.md` — ask-user gates in this skill follow this doc.
- `[sdlc-root]/process/deliverable_lifecycle.md` — canonical state transitions for deliverables and the incident doc itself.
- `[sdlc-root]/process/finding-classification.md` — when incident TRIAGE produces findings, classify them per this doc (FIX / DECIDE / PRE-EXISTING).
