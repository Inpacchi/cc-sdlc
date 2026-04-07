# Observability Discipline

<!-- Source: CS146S Wk 9 topics (Monitoring and observability for AI systems, Automated incident response).
     Google SRE Book, Introduction (sre.google/sre-book/introduction/):
       - Monitoring outputs: alerts (immediate action), tickets (days), logging (diagnostic only)
       - "Monitoring should never require a human to interpret any part of the alerting domain"
       - 50% cap on operational work; rest must be engineering/automation
     Resolve AI, "Top 5 Benefits of Agentic AI in On-call Engineering" (resolve.ai/blog/Top-5-Benefits):
       - Specialized agents collaborating: one for logs, another for metrics
       - Dynamic knowledge retention over static runbooks
     Extended from existing cc-sdlc deployment-patterns.yaml and debugging-methodology.yaml. -->

**Status**: Active — foundational patterns established

## Scope

Instrumentation, structured logging, metrics, tracing, alerting design, monitoring as a review concern. Covers what to observe, how to observe it, and how to act on observations.

## Core Principles

### Observability vs Monitoring

Monitoring tells you *when* something is wrong (alerts on known failure modes). Observability tells you *why* something is wrong (the ability to ask arbitrary questions about system behavior from the outside). Both are required but serve different purposes.

- **Monitoring** = predefined queries against known metrics (CPU > 90%, error rate > 1%)
- **Observability** = ad-hoc investigation using logs, traces, and metrics to diagnose novel failures

### The Three Pillars

| Pillar | Purpose | When to Use |
|--------|---------|-------------|
| **Logs** | Record discrete events with context | Debugging, audit trails, error investigation |
| **Metrics** | Track quantitative measurements over time | Capacity planning, SLO tracking, alerting |
| **Traces** | Follow a request across service boundaries | Latency diagnosis, dependency mapping, bottleneck identification |

Each pillar answers different questions. Logs answer "what happened?" Metrics answer "how much/how often?" Traces answer "where did time go?"

## Structured Logging

### Rules

- **Always use structured formats (JSON).** Human-readable logs are unsearchable at scale. Structured logs are both human-readable (with tooling) and machine-queryable.
- **Include correlation IDs.** Every request should carry a unique ID that appears in all log entries for that request. This is the primary mechanism for tracing a request through multiple services or components.
- **Log at the right level.** Log levels are a contract with your future self about what's worth reading.

| Level | When | Examples |
|-------|------|----------|
| **ERROR** | Something failed and needs human attention | Unhandled exception, external service down, data corruption |
| **WARN** | Something unexpected but handled | Retry succeeded, rate limit approaching, deprecated API used |
| **INFO** | Significant business events | User created, payment processed, deployment completed |
| **DEBUG** | Developer-useful detail, off in production | SQL queries, cache hits/misses, intermediate calculation values |

- **Never log PII at INFO or above.** Debug logs may include PII in development but must be stripped in production. See `knowledge/architecture/security-review-taxonomy.yaml` Domain 6 (Data Privacy).
- **Never log secrets at any level.** Tokens, passwords, API keys — redact before logging.
- **Include context, not just the event.** Bad: `"Payment failed"`. Good: `{"event": "payment_failed", "user_id": "u_123", "amount": 4999, "currency": "usd", "error": "card_declined", "provider": "stripe"}`.

### Anti-Patterns

- Logging entire request/response bodies (PII risk, storage cost, noise)
- Using string interpolation instead of structured fields
- Logging in hot loops (performance impact)
- Log-and-throw (logging an error then rethrowing it produces duplicate entries)

## Metrics Design

### What to Measure

The RED method for services:
- **Rate** — requests per second
- **Errors** — failed requests per second
- **Duration** — response time distribution (p50, p95, p99)

The USE method for resources:
- **Utilization** — percentage of resource capacity in use
- **Saturation** — work queued because resource is busy
- **Errors** — error count for this resource

### Alerting Design

- **Alert on symptoms, not causes.** Alert on "users can't log in" (symptom), not "CPU at 90%" (cause). CPU at 90% might be fine; users unable to log in never is.
- **Monitoring should never require a human to interpret the alerting domain** (Google SRE). If an alert fires and the responder's first step is "figure out if this is real," the alert is misconfigured. Three valid monitoring outputs: alerts (immediate human action), tickets (action within days), logging (diagnostic records, reviewed only when prompted).
- **Every alert must have a runbook.** If you don't know what to do when it fires, the alert is premature. Prepared runbooks yield ~3x improvement in MTTR vs improvisation.
- **Tune thresholds from data, not intuition.** Collect baseline metrics before setting alert thresholds. Alert fatigue from false positives trains responders to ignore real alerts.
- **Use severity levels consistently.** Page for user-impacting issues only. Everything else goes to a dashboard or non-urgent channel.

### SLO-Based Alerting

Define Service Level Objectives (SLOs) first, then alert on error budget burn rate:
- **SLI** (Service Level Indicator): the metric being measured (e.g., "proportion of requests completing in < 200ms")
- **SLO** (Service Level Objective): the target (e.g., "99.5% of requests complete in < 200ms over 30 days")
- **Error budget**: 100% - SLO = allowed failure (e.g., 0.5% of requests can be slow)
- **Burn rate alert**: alert when error budget is being consumed faster than sustainable

## Observability as a Review Concern

When reviewing code that touches request handling, data mutations, or external integrations, review agents should check:

- [ ] Are significant operations logged with structured context?
- [ ] Do new API endpoints emit RED metrics?
- [ ] Are error paths logged with enough context to diagnose without a reproducer?
- [ ] Do external service calls include timeout handling and failure logging?
- [ ] Are correlation IDs propagated across async boundaries?

This is not a separate review pass — it's part of what the code-reviewer and backend-developer agents check during the standard review-fix loop.

## Parking Lot

*Add observability insights here as they emerge during work. Include date and source context.*
