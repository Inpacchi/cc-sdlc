# Adapter Defect Catalog

Known defect patterns that appear in adapter-produced installations. Each entry includes:
- The exact grep pattern to detect it
- What causes it
- A concrete example from production audits
- Where the fix lives (plugin / upstream / both)

## Table of contents

1. [Transformer output bugs](#1-transformer-output-bugs) — malformed strings that shouldn't exist in any correct installation
2. [Pattern Mapping coverage gaps](#2-pattern-mapping-coverage-gaps) — canonical phrases that weren't transformed
3. [Exempt-file violations](#3-exempt-file-violations) — files in the allowlist that got transformed anyway
4. [Structural content loss](#4-structural-content-loss) — upstream content dropped during merge
5. [Version-drift false positives](#5-version-drift-false-positives) — hunks that look like defects but aren't

---

## 1. Transformer output bugs

These are malformed outputs — no correct installation should contain them. Each hit is a standalone finding.

### 1.1 Double-paren splice

**Grep:** `((discipline memories\|((memory graph\|((the agent knowledge graph\|((via memory_store`

**Cause:** A bare-path rule (replacement itself contains `(...)`) fired inside an existing `(...)` context, producing `((replacement) original-tail)`.

**Example from `migrate-f01a70`:**
```
Input:  Discipline parking lot entries (`[sdlc-root]/disciplines/*.md`)
Output: Discipline parking lot entries ((discipline memories, tagged sdlc:discipline:*) *.md`)
```

**Fix location:** plugin. The plugin's Pattern Mapping rule ordering (full-parenthetical → label → table-cell → bare-path) prevents this when enforced. If double-parens appear, the matcher is picking bare-path rules when parenthetical-whole rules exist.

### 1.2 Orphan glob debris

**Grep:** `\*\.md\`)\|\) \*\.md)\|\`\*\.md\`\)`

**Cause:** Same as 1.1 — the replacement consumed the opening `(` of the pattern but not the trailing `*.md)`, leaving orphaned suffix.

**Example:** visible inside the double-paren output above (`*.md\`)` trailing).

**Fix location:** plugin. Rule ordering fix resolves both 1.1 and 1.2.

### 1.3 Read of write API

**Grep:** `Read memory_store\|Read memory_search`

**Cause:** A capture-target rule (whose replacement begins with `memory_store with tags [...]`) fired inside a `Read ...` instruction context. Capture-target rules describe WRITE destinations; they should never transform a read.

**Example from `migrate-f01a70`:**
```
Input:  Read `[sdlc-root]/knowledge/architecture/agent-communication-protocol.yaml` for the handoff schema.
Output: Read memory_store with tags ["sdlc:knowledge", "sdlc:domain:architecture"] for the handoff schema.
```

`Read memory_store` is semantically impossible — `memory_store` is the write API. Correct transformation uses `Call memory_search(query="...", tags=[...])`.

**Fix location:** plugin. The plugin's "Capture-target rules must NEVER fire in `Read ...` contexts" guard prevents this when enforced.

### 1.4 Greedy-swallow capture

**Grep:** context-dependent — look for `memory_search(query="...(e\|query="...\| [X]\|query=".*[.;,]`

**Cause:** A wildcard capture (`[X]`, `<name>`, `<purpose>`) consumed past its intended terminator, swallowing a following parenthetical, comma, or sentence boundary.

**Example from `migrate-f01a70`:**
```
Input:  read `[sdlc-root]/disciplines/*.md` and find parking lot entries tagged with that deliverable's ID (e.g., [D05 — phase 2], [D05 — planning]).
Output: memory_search(query="parking lot entries tagged with that deliverable's ID (e", tags=["sdlc:discipline:*"]) g., [D05 — phase 2], [D05 — planning]).
```

The `[X]` capture stopped at arbitrary position `(e` and leaked the rest as orphan text.

**Fix location:** plugin. Match rule #6 (non-greedy with explicit terminators: `(`, `)`, `[`, `]`, `,`, `.`, `;`, `: `, EOL) prevents this.

### 1.5 Fenced-block corruption

**Grep:** find `memory_search(` or `memory_store(` inside `^\`\`\`` blocks that aren't ```bash (MCP calls in `bash`/`jsonl` fences are legitimate transaction log examples).

**Cause:** Transformer didn't honor fenced-block exemption, mangled example YAML/JSON with transformation, breaking syntax.

**Example from `migrate-f01a70`:** `sdlc-ingest.md:271-273` had ```yaml with `[sdlc-root]/knowledge/design/component-patterns.yaml` transformed into nested-quoted `memory_search(...)` producing syntactically invalid YAML.

**Fix location:** plugin. Fenced-block hard exclusion prevents this.

### 1.6 Integration-section corruption

**Grep:** `\*\*(Uses|Depends on|Updates|Feeds into|Complements|Downstream):\*\*.*memory_(search|store)`

**Cause:** Transformer didn't honor Integration-section exemption. Transforms `**Uses:** [sdlc-root]/knowledge/agent-context-map.yaml (for wiring)` into nonsense with double-paren.

**Fix location:** plugin. Integration-section hard exclusion prevents this.

---

## 2. Pattern Mapping coverage gaps

Canonical phrases stayed untransformed. The rule either doesn't exist in the plugin's Pattern Mapping or exists but didn't match due to context.

### 2.1 Leak grep (general)

```bash
grep -rn '\[sdlc-root\]/\(knowledge\|disciplines\)/' <target>/.claude/ 2>/dev/null \
  | grep -vE 'sdlc_changelog|knowledge-routing|sdlc-reviewer\.md|sdlc-compliance-auditor\.md|CLAUDE-SDLC\.md|provenance_log\.md'
```

Each hit needs per-line classification (see `classification-framework.md`).

### 2.2 Known untransformed idioms (Pattern Mapping gap candidates)

- ``- Knowledge store updates (`[sdlc-root]/knowledge/*.md`)`` — label-parenthetical with backticks
- ``- Files from the same discipline (e.g., `[sdlc-root]/knowledge/<discipline>/`)`` — `(e.g., ...)` variant
- Table cells with `[sdlc-root]/knowledge/...` in non-first column
- ``knowledge stores (`[sdlc-root]/knowledge/`)`` mid-sentence (e.g., `AGENT_TEMPLATE.md:134` pre-fix)
- `Cross-project knowledge updates append to [sdlc-root]/knowledge/testing/` — rule exists, didn't fire

### 2.3 Mid-sentence lowercase verb

**Example:** `For each deliverable being archived, read [sdlc-root]/disciplines/*.md and find parking lot entries...`

Rule pattern `Read [sdlc-root]/disciplines/*.md and find [X]` should match case-insensitively regardless of sentence position (plugin match rule #1). Hits here indicate the matcher anchors on sentence-start capitalization.

**Fix location:** plugin.

---

## 3. Exempt-file violations

These files must be copied verbatim from cc-sdlc source — zero transformation. A transformation-shaped hunk in any of these files is a defect.

**Exempt files (Neuroloom):**
- `process/knowledge-routing.md` — the phrasing contract itself
- `process/sdlc_changelog.md` — historical record
- `agents/sdlc-reviewer.md` — reviewer's phrases-to-detect list
- `agents/sdlc-compliance-auditor.md` — auditor's validation criteria
- `CLAUDE-SDLC.md` — framework documentation
- `knowledge/provenance_log.md` — project append-only file (treated like changelog)

**Detection:** diff each exempt file against cc-sdlc source. Any hunk = defect. Exception: `agents/sdlc-compliance-auditor.md` has a documented adapter customization around methodology path reference (see specific rules in `classification-framework.md`).

**Example from `migrate-f01a70`:** `agents/sdlc-reviewer.md:82-86` had the forbidden-phrases checklist transformed into Neuroloom forms, destroying the validation criteria the reviewer exists to enforce.

**Fix location:** plugin. Hard-gate enforcement (post-0.3.6) prevents this by routing exempt files through a verbatim-copy path with zero rule evaluation.

---

## 4. Structural content loss

These don't show in MCP counts or leak greps. They show as heading / table row / numbered step count drops between cc-sdlc source and target.

**Detection:**
```bash
# For each file diffed:
comm -23 <(grep -cE '^#{1,6} ' source.md) <(grep -cE '^#{1,6} ' target.md)
# ...similar for tables and numbered steps
```

If target count < source count without a matching project customization, it's a content-merge bug.

**Examples from `migrate-f01a70`:**
- `sdlc-develop-skill.md:224-234` — 12-row Red Flags table replaced with duplicate of an earlier prose section
- `sdlc-plan.md:240-254` — 5-step "Library verification (MANDATORY)" procedure deleted; 4-step "Spec-time knowledge filtering" replaced with 3-step stub
- `sdlc-review.md:49-59` — "Dispatch Reviewer" step body replaced with duplicate of a later section

**Fix location:** plugin. The Structural Content-Loss Audit (plugin §4.2-gate, post-0.3.6) catches this when enforced.

---

## 5. Version-drift false positives

Not defects — but they look like defects at first glance. Rule them out before classifying anything else.

### 5.1 Target cc-sdlc version < current cc-sdlc version

If `.sdlc-manifest.json` shows `source_version` earlier than the current cc-sdlc repo, differences against current source may just be legitimate upstream changes the target hasn't migrated to yet. A v1.1.1 target diffed against current v1.2.3 source will show all v1.2.1-v1.2.3 upstream edits as "deviations."

**What to do:** always surface target version vs current version in the report headline. Interpret diffs in that context. If the user wants a same-version audit, have them re-migrate to current first.

### 5.2 Target customizations inside PROJECT-SECTION markers

Content between `<!-- PROJECT-SECTION-START: label -->` and `<!-- PROJECT-SECTION-END: label -->` is explicitly preserved across migrations and is project-specific by design. Diffs inside these blocks are never defects.

### 5.3 Preserved MCP sections (project-authored MCP)

Sections with `memory_search(query="<domain-specific>", tags=[...])` calls that weren't plugin-generated (i.e., the project added them during `/sdlc-port` or manually) are preserved verbatim by the plugin's §4.2.0 gate. Diffs in these sections are project customizations, not defects.

**Detection heuristic:** a preserved MCP section has query strings referencing project-specific domain terms (e.g., `"debugging methodology investigation root cause"` in a project's debug-specialist agent), not the generic terms the plugin's Pattern Mapping emits.

### 5.4 Sleeved-specific path corrections

In the 2026-04-22 audit, sleeved's `agents/sdlc-compliance-auditor.md:13` had a MORE CORRECT methodology path than upstream (sleeved had `.claude/skills/sdlc-audit/references/compliance-methodology.md`; upstream had the broken `[sdlc-root]/knowledge/compliance-methodology.md`). When sleeved fixes an upstream bug, that's an upstream finding, not a plugin one.
