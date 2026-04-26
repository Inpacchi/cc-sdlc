# DX Discipline — Parking Lot

**Status:** Active parking lot — knowledge store at `[sdlc-root]/knowledge/dx/`
**Scope:** Developer experience: documentation architecture, getting-started flows, internal doc authoring standards, changelog discipline, skill quality evaluation, and the end-to-end developer evaluation journey.

---

## Parking Lot

### Changelog Automation (2026-04-25, source: wshobson/agents — documentation-standards, documentation-generation)

*Core rules promoted to `developer-documentation-patterns.yaml` (DDP-01 through DDP-08).*

- **Automated changelog generation tooling.** [DEFERRED] The changelog-automation source covers six tools: standard-version, semantic-release, git-cliff, commitizen, husky/commitlint, and GitHub Actions workflows. Tool choice should be deferred to SDK kickoff. Evaluate commitizen for Python and semantic-release or git-cliff for TypeScript. (Source: `documentation-generation/skills/changelog-automation/SKILL.md`)

### Skill Quality Evaluation (2026-04-25, source: wshobson/agents — plugin-eval/evaluation-methodology)

*Core rules promoted to `skill-quality-rubrics.yaml` (SQR-01 through SQR-10).*

- **Static anti-pattern check as a pre-commit gate.** [NEEDS VALIDATION] SQR-07 describes five automatically detectable anti-patterns (OVER_CONSTRAINED, EMPTY_DESCRIPTION, MISSING_TRIGGER, BLOATED_SKILL, ORPHAN_REFERENCE). A lightweight script (or a rule in the SDLC audit skill) could check these against all SKILL.md files on every commit. Cost: ~1 hour to implement; value: catches structural issues before they accumulate. (Source: `plugin-eval/skills/evaluation-methodology/SKILL.md`)

- **Elo ranking concept for comparing skills.** [DEFERRED] The PluginEval framework includes an Elo/Bradley-Terry ranking system for comparing skills against a "gold corpus." Only relevant if the SDLC skill library grows large enough to need quality comparison across versions or variants. Revisit when the SDLC has 30+ skills. (Source: `plugin-eval/skills/evaluation-methodology/SKILL.md`)
