---
title: "{Human-readable title — 3-8 words}"
slug: "{lowercase-with-hyphens — matches filename}"
category: "{primary-domain — pick one matching your project's reference categories, e.g. api, frontend, database, observability, security, deploy, sdlc, cross-cutting}"
owner_agent: "{primary-maintainer-domain — e.g. backend-developer, devops-engineer}"
audience: ["coding-agent", "developer"]   # include "on-call" only if this doc supports incident response
status: "active"                            # draft | active | deprecated
last_verified_commit: "{short git sha of the commit that produced this doc}"
last_verified_date: "{YYYY-MM-DD}"
related_deliverables: ["D{NN}"]             # SDLC deliverable IDs this doc references
---

# {Title}

> **Audience:** {one sentence — who reads this and when}
> **Scope:** {one sentence — what's covered, what's out of scope}

## Summary

{2-4 sentences. State what the system is, what problem it solves, and the single most important thing a reader must know. Written for an agent that has never seen this code before.}

## Key Concepts

{Domain terms used in this doc, with plain-language definitions and concrete examples or analogies. Omit this section only if the doc uses no domain-specific jargon.}

- **{Term}** — {definition}. {Analogy or concrete example.}
- **{Term}** — {definition}. {Analogy or concrete example.}

## Reference

{The authoritative content. Whatever the doc is FOR — event schema, API surface, config matrix, pipeline stage list, etc. Prefer tables over prose for enumerable content.}

### {Sub-heading — e.g. "Event Schema", "Endpoints", "Stage Inventory"}

{content}

### {Sub-heading}

{content}

## Examples

{Working examples a reader can copy and adapt. Include at least one for every usage mode the reference describes.}

### {Example 1 title}

```{language}
{code or query}
```

{1-2 sentences explaining what this example does and when to use it.}

### {Example 2 title}

...

## Gotchas

{Known pitfalls, surprising behavior, and constraints that are not obvious from the code. Each entry: the trap, the fix or workaround, the source (review finding, incident, deliverable).}

- **{Gotcha name}.** {Description.} {Fix or workaround.} (Source: {D-number or incident or review finding.})
- **{Gotcha name}.** {Description.} {Fix or workaround.} (Source: {source.})

## Related Code

{Every anchor must be `path/relative/to/repo/root.ext:LINE` or `path:LINE-LINE`. File paths with no line numbers are not acceptable — agents use line numbers to navigate.}

- `{path/to/file.ext:LINE-LINE}` — {what's at this location}
- `{path/to/another_file.ext:LINE}` — {what's at this location}

## Related Docs

- [{Doc title}]({relative/path/to/doc.md}) — {one-sentence relationship}
- [{Deliverable N result}]({docs/current_work/.../result.md}) — {one-sentence relationship}

## Change Log

| Date | Commit | Change | Verified by |
|------|--------|--------|-------------|
| {YYYY-MM-DD} | {short sha} | Initial version | {author-agent + reviewing agents} |
