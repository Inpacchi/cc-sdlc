# Incident Response Process

<!-- Source: CS146S Wk 9: Monitoring and observability for AI systems, Automated incident response.
     Google SRE Book, Introduction (sre.google/sre-book/introduction/):
       - 50% cap on operational work; rest must be engineering/automation
       - Error budgets reframe outages as expected part of innovation
       - Playbooks yield ~3x MTTR improvement vs improvisation
       - ~70% of outages stem from system changes
       - Blame-free postmortem culture focusing on engineering solutions
     Resolve AI, "Top 5 Benefits of Agentic AI in On-call Engineering" (resolve.ai/blog/Top-5-Benefits):
       - Multi-agent approach: specialized agents for logs, metrics, code changes
       - Dynamic knowledge retention vs static runbooks that become obsolete
       - Consistent investigation workflows eliminate human troubleshooting variability
     Existing cc-sdlc debugging-methodology.yaml for investigation approach. -->

How to classify, triage, respond to, and learn from production incidents. Connects incidents back to the deliverable lifecycle so lessons feed forward into future planning.

---

## Incident Classification

| Severity | Definition | Response Time | Examples |
|----------|-----------|---------------|----------|
| **SEV-1** | Service down or data loss affecting all users | Immediate — all hands | Database corruption, auth system failure, payment processing down |
| **SEV-2** | Major feature broken or significant degradation | Within 1 hour | Search broken, API latency > 10x normal, partial data loss |
| **SEV-3** | Minor feature broken, workaround exists | Within 4 hours | UI rendering bug, non-critical integration failure, edge case crash |
| **SEV-4** | Cosmetic or low-impact issue | Next business day | Styling regression, minor copy error, non-user-facing log noise |

**Classification heuristic:** Severity is determined by *user impact scope* (how many users) x *user impact depth* (how broken is their experience). A bug affecting 100% of users but with an easy workaround may be SEV-3. A bug affecting 1% of users with no workaround and data loss is SEV-1.

**Change correlation:** Approximately 70% of outages stem from system changes (Google SRE). When classifying, immediately check: what changed recently? `git log`, deploy history, and config changes are the first investigative step, not the last.

---

## Triage Workflow

### 1. Detect

Incidents are detected through:
- **Automated monitoring** — alerts from observability tooling (error rate spikes, latency thresholds, health check failures)
- **User reports** — support tickets, social media, direct reports
- **Internal discovery** — team members notice issues during normal work

### 2. Classify

Assign severity using the table above. When uncertain, **classify higher** — it's cheaper to downgrade than to under-respond.

### 3. Communicate

| Audience | When | Channel |
|----------|------|---------|
| Responders | Immediately | Incident channel (Slack, Discord, etc.) |
| Stakeholders | SEV-1/2: within 15 min; SEV-3/4: within 1 hour | Status page or stakeholder channel |
| Users | SEV-1/2 with user-visible impact | Status page, in-app banner |

### 4. Investigate

Follow the debugging methodology in `[sdlc-root]/knowledge/architecture/debugging-methodology.yaml`:

1. **Reproduce** — Confirm the symptom. Get a consistent reproduction.
2. **Isolate** — Narrow the blast radius. What changed? When did it start? What's the scope?
3. **Identify root cause** — Read logs, traces, recent deploys. Use `git log` to find recent changes in the affected area.
4. **Fix or mitigate** — Apply the smallest change that resolves user impact. Mitigation (rollback, feature flag, redirect) is acceptable as a first response; root cause fix follows.

**Playbooks vs improvisation:** Prepared runbooks yield approximately 3x improvement in mean time to repair (MTTR) compared to improvising a response (Google SRE). If a service has no runbook, that is itself an action item from the postmortem.

### 5. Resolve

- Confirm user impact is resolved (not just "deploy succeeded")
- Update status page / communication channels
- Downgrade severity if mitigated but root cause fix is pending

---

## Postmortem Process

**Every SEV-1 and SEV-2 incident gets a postmortem.** SEV-3 incidents get a postmortem if they reveal a systemic issue. SEV-4 incidents do not require postmortems.

### Timeline

| Step | When | Owner |
|------|------|-------|
| Incident resolved | T+0 | Responder |
| Draft postmortem | Within 48 hours | Incident lead |
| Review postmortem | Within 1 week | Team |
| Action items tracked | After review | Relevant owners |

### Postmortem Principles

- **Blameless.** Postmortems analyze systems, not people. "Why did the system allow this?" not "Who did this?" An outage is an expected part of the process of innovation, not a failure to be punished (Google SRE error budget principle).
- **Actionable.** Every postmortem produces concrete action items with owners and deadlines. A postmortem without action items is a story, not a learning tool.
- **Connected.** Action items from postmortems should become deliverables (tracked in the deliverable catalog) or backlog items. If an action item isn't worth tracking, it isn't worth listing.
- **Honest about contributing factors.** Root cause is rarely a single event. Identify the chain: what happened, what made it possible, what made it hard to detect, what made it hard to fix.

### Postmortem Template

Use `[sdlc-root]/templates/postmortem_template.md` for the document structure.

### Connecting Incidents to the Deliverable Lifecycle

When a postmortem action item is significant enough to warrant planning:

1. Create a deliverable in `docs/_index.md` referencing the postmortem
2. Run `sdlc-plan` or `sdlc-lite-plan` with the postmortem findings as input
3. The spec should reference the postmortem and explain how the change prevents recurrence

This creates traceability: incident → postmortem → deliverable → implementation → result.

---

## Maintenance

Update this process when:
- Incident response reveals gaps in the triage workflow
- New communication channels or monitoring tools are adopted
- Severity definitions no longer match the project's scale or user base
