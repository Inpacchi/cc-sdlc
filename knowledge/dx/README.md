# DX Knowledge Store

**Discipline:** Developer Experience
**Consumers:** dx-engineer, technical writers
**Discipline parking lot:** `[sdlc-root]/disciplines/dx.md`

This knowledge store contains structured rules for developer-facing surfaces: documentation architecture, getting-started flows, internal doc authoring standards, changelog discipline, and skill quality evaluation.

---

## Knowledge Files

| File | Rule IDs | Topics |
|------|----------|--------|
| `developer-documentation-patterns.yaml` | DDP-01 – DDP-08 | Doc architecture, getting-started guides, code examples, API reference, internal doc authoring (HADS-derived), changelog discipline |
| `skill-quality-rubrics.yaml` | SQR-01 – SQR-10 | Skill quality evaluation: triggering accuracy, orchestration fitness, scope calibration, progressive disclosure, token efficiency, anti-pattern flags |

## ID Sequences

| File | Prefix | Current max | Next |
|------|--------|-------------|------|
| `developer-documentation-patterns.yaml` | DDP- | DDP-08 | DDP-09 |
| `skill-quality-rubrics.yaml` | SQR- | SQR-10 | SQR-11 |

## `spec_relevant` Status

All files in this knowledge store are `spec_relevant: false`. The DX knowledge
covers implementation conventions and quality standards rather than data model
or API contract details that feed directly into spec authoring.
