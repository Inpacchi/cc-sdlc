# Postmortem: [Incident Title]

<!-- Source: Google SRE Book, Introduction (sre.google/sre-book/introduction/) — blame-free postmortem culture.
     CS146S Wk 9: Incident response and DevOps.
     Resolve AI, "Top 5 Benefits" — evidence-based collaboration with real-time documentation. -->

**Date:** YYYY-MM-DD
**Severity:** SEV-N
**Duration:** HH:MM (from detection to resolution)
**Author:** [Name]
**Status:** Draft | Reviewed | Action Items Tracked

---

## Summary

*One paragraph: what happened, who was affected, how it was resolved.*

---

## Timeline

*All times in UTC (or project-local timezone).*

| Time | Event |
|------|-------|
| HH:MM | First alert / report received |
| HH:MM | Incident classified as SEV-N |
| HH:MM | Investigation began |
| HH:MM | Root cause identified |
| HH:MM | Mitigation applied |
| HH:MM | Full resolution confirmed |

---

## Impact

- **Users affected:** [count or percentage]
- **Duration of user-visible impact:** [time]
- **Data loss:** [none / description]
- **Revenue impact:** [none / estimate]

---

## Root Cause

*What was the technical root cause? Be specific — "a bug" is not a root cause.*

---

## Contributing Factors

*What conditions made this incident possible, harder to detect, or harder to fix?*

1. [Factor 1 — e.g., "No integration test covering this code path"]
2. [Factor 2 — e.g., "Alert threshold was set too high to catch gradual degradation"]
3. [Factor 3 — e.g., "Recent deploy changed X without updating Y"]

---

## Detection

- **How was the incident detected?** [monitoring alert / user report / internal discovery]
- **Time to detect:** [from incident start to first alert]
- **Could detection have been faster?** [yes/no — if yes, what would help]

---

## Response

- **What worked well in the response?**
  - [e.g., "Runbook for this service was accurate and up to date"]
  - [e.g., "Rollback was fast because deploy pipeline supports one-click revert"]

- **What could be improved?**
  - [e.g., "Took 20 minutes to find the right log query"]
  - [e.g., "No clear escalation path for this service"]

---

## Action Items

*Every action item must have an owner and a target date. If it's worth listing, it's worth tracking.*

| # | Action | Owner | Target Date | Deliverable ID |
|---|--------|-------|-------------|----------------|
| 1 | [Specific action] | [Name] | YYYY-MM-DD | [DNN or backlog] |
| 2 | [Specific action] | [Name] | YYYY-MM-DD | [DNN or backlog] |
| 3 | [Specific action] | [Name] | YYYY-MM-DD | [DNN or backlog] |

---

## Lessons Learned

*What did this incident teach us that we didn't know before? Focus on systemic insights, not "don't do the bad thing again."*
