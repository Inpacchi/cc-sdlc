---
name: sdlc-render
description: >
  Render a markdown deliverable as a self-contained HTML file for human reading, review, and sharing.
  Uses the SDLC design system for visual consistency. Supports multiple audience variants from a
  single source file — engineer (always generated), plus leadership, design, or marketing on request.
  Triggers on "/sdlc-render", "render this as HTML", "make an HTML version", "generate HTML",
  "render the spec", "render the plan", "render the result".
  Do NOT use for creating interactive tools or playgrounds — those are bespoke and not deliverable renders.
  Do NOT use for editing markdown content — the MD file is the source of truth.
---

# HTML Rendering

Render a markdown deliverable to a self-contained HTML document using the SDLC design system. The markdown remains the source of truth; the HTML is a visual presentation layer for human consumption.

**Argument:** `$ARGUMENTS` — path to a markdown file, or a deliverable reference (e.g., "the spec", "D5 plan")

## When This Applies

Use this skill in two modes:

**Auto mode (post-skill):** After any skill writes a deliverable MD file to `docs/current_work/`, auto-render the engineer variant. No Q&A — use document-type defaults. This mode is triggered by the workflow rule in CLAUDE-SDLC.md, not by direct user invocation.

**Manual mode (user-invoked):** CD invokes `/sdlc-render <path>` or says "render this as HTML." Opens with interactive scoping before generating. Use when:
- CD wants audience variants beyond the default engineer version
- CD wants to customize emphasis or include specific elements
- CD wants to re-render with different framing
- The auto-rendered version needs refinement

Signs this skill is NOT appropriate:
- Creating an interactive tool, editor, or playground → build it directly, not through this skill
- Editing the markdown content → edit the MD file directly
- Generating documentation from scratch → use the appropriate template and planning skill

## Workflow

```
RESOLVE → (manual: SCOPE) → READ DESIGN SYSTEM → DETECT TYPE → GENERATE → WRITE → REPORT
```

### Step 1: Resolve Target

Identify the markdown file to render.

- If given a path, use it directly
- If given a deliverable reference ("the spec", "D5 plan"), resolve it via `docs/_index.md` and the `docs/current_work/` directory structure
- If ambiguous, ask CD to clarify which file

Verify the file exists and is a markdown file before proceeding.

### Step 2: Interactive Scoping (manual mode only)

Skip this step entirely in auto mode. In manual mode, ask CD the following questions to shape the output.

**Question 1 — Audience (multi-select):**

> Who needs an HTML version of this document? Engineer is always included.

| Option | What it produces |
|--------|-----------------|
| Engineer only | Default technical version (always generated) |
| + Leadership | Additional version with executive summary, impact metrics, and decisions up top; implementation details collapsed |
| + Design | Additional version with visual/UX emphasis; mockups, component specs, and interaction flows prominent |
| + Marketing | Additional version framed in user-facing language; benefit-oriented, internals omitted |
| + Other (specify) | Custom audience with CD-defined emphasis |

Each selected audience generates a separate HTML file.

**Question 2 — Purpose:**

> What will you use this for?

| Option | How it shapes the output |
|--------|--------------------------|
| Review & approval | Emphasis on completeness, decision points highlighted, open questions prominent |
| Share for awareness | Emphasis on readability, executive summary, key takeaways |
| Presentation | Larger type, fewer details, visual impact, one-screen sections |
| Reference / archive | Deep navigation, comprehensive detail, anchor links |

**Question 3 — Emphasis:**

> What should stand out most?

| Option | Effect |
|--------|--------|
| Visual clarity & diagrams | More SVG diagrams, architecture visuals, flowcharts |
| Data & metrics | Stat cards prominent, tables enhanced, before/after comparisons |
| Actionable items & decisions | Decision callouts, checklists, blockers highlighted |
| Comprehensive detail | All sections expanded, nothing collapsed, full technical depth |

**Question 4 — Specific requests (open-ended):**

> Any specific elements to include or emphasize? (e.g., "include the data flow diagram", "highlight the API changes", "keep it under one screen")

Use the answers to customize the HTML output. The scoping answers act as modifiers on top of the document-type defaults and audience profiles.

### Step 3: Read Design System

Read the design system from `[sdlc-root]/templates/html-design-system.html`.

Extract:
- All CSS custom properties (tokens)
- Component patterns and their HTML structure
- Layout patterns and responsive breakpoints
- SVG diagram conventions

The design system is the sole source of visual vocabulary. Do not invent new components or override tokens.

### Step 4: Detect Document Type

Determine the document type from the file's path and content structure:

| Path Pattern | Type | Default Profile |
|-------------|------|-----------------|
| `docs/current_work/specs/` | spec | Requirement cards, dependency diagrams, acceptance criteria |
| `docs/current_work/planning/` | plan | Timeline, phase tabs, code previews, agent dispatch table |
| `docs/current_work/results/` | result | Stat cards with deltas, diff summary, review findings |
| `docs/current_work/sdlc-lite/` + `_plan` | plan | Same as plan, lighter |
| `docs/current_work/sdlc-lite/` + `_result` | result | Same as result, lighter |
| `docs/current_work/ideas/` + `_idea-brief` | exploration | Comparison grid, option cards, tradeoff matrices |
| `docs/current_work/ideas/` + `_handoff` | handoff | Status banner, done/remaining columns, decision log |
| `docs/current_work/audits/` | report | Stat cards, finding severity rows, compliance tables |
| `docs/current_work/incidents/` | incident | Severity banner, timeline, root cause diagram, remediation checklist |
| `docs/reference/` | reference | Deep TOC, anchor links, code blocks, collapsible sections |

If the path doesn't match a known pattern, infer the type from the markdown structure (headings, content patterns) and default to the closest matching profile.

Consult `[sdlc-root]/process/html-rendering.md` for full document-type default profiles.

### Step 5: Generate HTML

For each audience variant (engineer always, plus any selected in scoping):

1. **Page structure:** Create a single-file HTML document with all CSS inline in a `<style>` block. No external dependencies.

2. **Header:** Document title (from first H1 or frontmatter), eyebrow label (document type), metadata row (deliverable ID, status, date, author if available).

3. **Table of contents:** Auto-generate for documents with 3+ sections. Use the `.toc` component from the design system.

4. **Content conversion:** Transform markdown content to semantic HTML using design system components:
   - Headings → serif section headings with section numbers
   - Lists → styled lists; checklists where appropriate
   - Tables → design system tables with hover states
   - Code blocks → `<pre><code>` with dark background
   - Blockquotes → callout boxes (infer severity from content)
   - Bold text in key positions → requirement cards, stat cards, or badges as appropriate
   - ASCII diagrams or flowchart descriptions → inline SVG using diagram conventions from design system

5. **Document-type components:** Add type-specific components based on the detected document type (see Step 4). These are structural additions that make the document type's key information visually prominent.

6. **Audience shaping:** For non-engineer variants, reshape the content:
   - **Leadership:** Move executive summary and decisions to the top. Collapse implementation details into `<details>` sections. Add stat cards for key metrics. Emphasize timeline and impact.
   - **Design:** Promote visual elements (mockups, component specs, screenshots). Add design-relevant callouts. Collapse technical implementation. Emphasize interaction and layout decisions.
   - **Marketing:** Reframe headings and descriptions in user-benefit language. Remove internal jargon. Omit implementation details entirely (don't collapse — remove). Focus on what the feature does for users, not how it works.

7. **Interactive elements:** Add where they improve navigation without requiring JavaScript beyond tab switching:
   - Collapsible `<details>` for lengthy sections
   - Tabs for multi-perspective content (phases, options, before/after)
   - Anchor links from TOC to sections
   - Tab switching script (from design system)

8. **Footer:** Auto-generated footer with generation timestamp and "Generated by sdlc-render" attribution.

### Step 6: Write Files

Write each HTML file alongside the source markdown:

```
{source_name}.html                   ← engineer (always)
{source_name}_leadership.html        ← if leadership audience selected
{source_name}_design.html            ← if design audience selected
{source_name}_marketing.html         ← if marketing audience selected
{source_name}_{custom}.html          ← if custom audience specified
```

### Step 7: Report

Output a summary of what was generated:

```
Rendered: docs/current_work/specs/d01_feature_spec.md

  → d01_feature_spec.html (engineer)
  → d01_feature_spec_leadership.html (leadership)

Open in browser: open docs/current_work/specs/d01_feature_spec.html
```

In auto mode, keep the report to a single line confirming the HTML was written.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll add a custom color that looks better here" | Use design system tokens only. Consistency across all rendered docs matters more than per-doc aesthetics. |
| "This doc doesn't fit any type, I'll skip type detection" | Infer the closest type. Every doc benefits from a structural profile even if imperfect. |
| "Leadership doesn't need the technical details at all" | Collapse, don't delete. Leadership variants should allow drilling into detail if they choose. Marketing is the exception — it omits internals. |
| "I'll add complex JavaScript for interactivity" | Keep JS minimal. Tabs and collapsibles only. This is a document, not an app. |
| "The markdown has errors, I'll fix them in the HTML" | Never silently fix source content. Flag issues to CD. The MD is the source of truth. |

## Integration

- **Depends on:** `[sdlc-root]/templates/html-design-system.html` (design system), `[sdlc-root]/process/html-rendering.md` (conventions and type profiles)
- **Called by:** All skills that write deliverables to `docs/current_work/` (auto mode), or CD directly (manual mode)
- **Does not dispatch agents.** This is a direct-action skill — CC reads the markdown and generates the HTML directly.
