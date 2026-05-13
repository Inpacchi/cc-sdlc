# HTML Rendering

Markdown is the source of truth for all SDLC deliverables — agents read it, version control tracks it, templates define its structure. HTML is the human-readable view: richer, more visual, easier to share and easier to actually read.

Every deliverable MD file can be rendered to a self-contained HTML file using `sdlc-render`. The HTML is generated alongside the markdown, not instead of it.

## Philosophy

- **MD for agents and git.** Markdown stays clean, structured, and agent-optimized. No HTML concerns leak into templates or markdown content.
- **HTML for humans.** HTML uses the design system to present the same information with visual hierarchy, diagrams, interactive navigation, and audience-appropriate framing.
- **One source, many views.** A single MD file can produce multiple HTML variants for different audiences. The engineer version is always generated; leadership, design, and marketing versions are generated on request.

## Two Categories of HTML

**Deliverable renders** — Post-write conversions of finished markdown deliverables (specs, plans, results, reviews, etc.) into styled, readable HTML. These use design system tokens and keep JavaScript minimal (tabs, collapsibles). Produced by `sdlc-render` or auto-render steps in skills.

**Exploration artifacts** — Interactive HTML files created during `sdlc-idea` exploration and `sdlc-plan` discovery to help CD evaluate options. These are throwaway working tools: side-by-side approach comparisons, interaction prototypes, parameter tuning with sliders, drag-and-drop prioritization, animation sandboxes. They use the design system for visual tokens but allow any JavaScript needed for the interaction. They are demand-driven — create them when text descriptions would be insufficient for CD to make a confident decision.

## When HTML Is Generated

### Auto-Render (post-skill)

After any skill writes a deliverable MD file to `docs/current_work/`, CC auto-renders an engineer-audience HTML version using document-type defaults. No Q&A — the render happens silently as a final step.

Skills that trigger auto-render:

| Skill | Deliverable | Document Type |
|-------|-------------|---------------|
| `sdlc-plan` | spec, plan | spec, plan |
| `sdlc-lite-plan` | plan | plan |
| `sdlc-execute` | result | result |
| `sdlc-lite-execute` | result | result |
| `sdlc-idea` | idea brief | exploration |
| `sdlc-handoff` | handoff doc | handoff |
| `sdlc-audit` | audit report | report |
| `sdlc-debug-incident` | incident doc | incident |
| `sdlc-create-reference-doc` | reference doc | reference |

### Manual Render (`/sdlc-render`)

CD invokes `/sdlc-render <path>` to generate a tailored HTML version. This opens with an interactive scoping phase — audience selection, purpose, emphasis, and specific requests — before generating. Use this when:

- Sharing a spec with stakeholders who need a different framing
- Preparing a result for leadership review
- Creating a polished version for external communication
- Re-rendering with different emphasis after the auto-generated version

## Output Conventions

### File Naming

HTML files are written alongside their markdown source in the same directory:

```
d01_feature_spec.md                  ← source (unchanged)
d01_feature_spec.html                ← engineer (default, auto-generated)
d01_feature_spec_leadership.html     ← executive framing
d01_feature_spec_design.html         ← visual/UX emphasis
d01_feature_spec_marketing.html      ← user-facing framing
```

The engineer variant uses the base name with `.html`. Audience variants append a suffix before the extension.

### Version Control

HTML files are generated artifacts. Projects may choose to:
- **Gitignore them** — treat as build output, regenerate on demand
- **Track them** — useful when sharing links to specific commits

Neither approach is prescribed. The MD file is always the source of truth.

### Staleness

An HTML render becomes stale when its source markdown is modified after generation. Stale HTML is dangerous — humans read the HTML version and miss updates that only exist in the markdown.

**Auto-render handles this:** When a skill writes or updates a deliverable MD file, the post-write render step regenerates the HTML. This keeps the HTML current as long as changes go through skills.

**Manual edits require re-rendering:** If the markdown is updated outside a skill (direct edit, review-fix revisions, CD feedback incorporated manually), the HTML is now stale. The next skill that touches the file should re-render, or CD can invoke `/sdlc-render` manually.

**Footer timestamps:** Every rendered HTML includes a generation timestamp in the footer. When comparing an HTML file to its source, check this timestamp against the markdown's last-modified date. If the markdown is newer, re-render before using the HTML for review.

**Re-render on plan revision:** When a plan undergoes review-fix revisions (findings incorporated, DECIDE items resolved), re-render the HTML after the final revision — not after each intermediate revision. The HTML should reflect the approved plan, not a mid-revision snapshot.

## Audience Variants

The engineer version is always generated (auto or manual). Additional audiences are selected during manual rendering via multi-select.

| Audience | Suffix | Emphasis | Key Components |
|----------|--------|----------|----------------|
| **Engineer** | _(none)_ | Technical completeness | Full detail, code snippets, architecture diagrams, acceptance criteria, diff viewers |
| **Leadership** | `_leadership` | Decisions and impact | Executive summary up top, stat cards, timeline, risk callouts, implementation details collapsed |
| **Design** | `_design` | Visual and UX | Mockup prominence, component references, interaction flows, spacing/color specs, technical detail collapsed |
| **Marketing** | `_marketing` | User-facing value | Benefit framing, user impact, positioning language, feature descriptions in user terms, internals omitted |

Each variant reshapes the same source content — it does not fabricate new information. The source MD constrains what can appear in any variant.

## Document-Type Defaults

When auto-rendering (no Q&A), the document type determines which components and layout patterns to use.

### Spec

- **Layout:** Header with deliverable ID and status → summary grid (status, priority, owner, target) → table of contents → requirement cards → dependency diagram (SVG) → acceptance criteria checklist → open questions callout
- **Key components:** Requirement cards, callout boxes (open questions, constraints), comparison grid (for alternatives), diagrams
- **Interactive:** Collapsible sections for detailed requirements, tabs for functional vs. non-functional requirements
- **Verbatim content rule:** If the spec includes exact API signatures, schema definitions, or acceptance criteria with specific values, these must appear in the HTML — not summarized. Use collapsible code blocks for lengthy specifications.

### Plan

- **Layout:** Header → summary grid (files, phases, findings, review rounds) → timeline visualization → phased sections with milestone markers → per-phase acceptance criteria → agent dispatch summary table → risk table
- **Key components:** Timeline, stat cards (scope metrics), code blocks, tables, tabs for phase-by-phase view, copy tables (before/after for text replacement plans), file tags for scope
- **Interactive:** Tabs for phases, collapsible implementation details
- **Verbatim content rule:** Code blocks, replacement strings, import lines, and other verbatim content from the source plan MUST appear in the HTML — render in collapsible `<details>` sections if they would dominate a section, but do not summarize them into prose or table abbreviations. The executing agent needs exact text, not paraphrases.
- **Per-phase acceptance criteria:** Render each phase's acceptance criteria at the bottom of that phase's section (as a checklist), not flattened into a single end-of-document list. The consolidated post-execution review checklist remains as a summary, but per-phase criteria give phase-level "what does done look like."
- **Substitution/fallback tables:** If the plan includes icon substitutions, library fallbacks, or alternative approaches, render them in the phase where they apply — don't drop them.

### Result

- **Layout:** Header with completion status → stat cards (before/after metrics) → what shipped summary → diff summary → review findings table → remaining items
- **Key components:** Stat cards with deltas, diff viewer, finding rows, banners (status), tables
- **Interactive:** Collapsible diff views, tabs for shipped vs. remaining

### Exploration (idea brief)

- **Layout:** Header → problem framing → comparison grid of options → tradeoff matrices → recommendation callout → next steps
- **Key components:** Comparison grid, cards for each option, badges for tradeoffs, callout for recommendation
- **Interactive:** Tabs for side-by-side option comparison

### Report (audit)

- **Layout:** Header → banner (overall status) → stat cards (score, findings count) → findings table with severity → detailed findings with severity rows → recommendations
- **Key components:** Banners, stat cards, finding rows, severity badges, tables
- **Interactive:** Collapsible finding details

### Incident

- **Layout:** Header with severity banner → timeline (discovery → triage → fix → verification) → impact summary stat cards → root cause diagram (SVG) → remediation checklist → lessons learned callout
- **Key components:** Timeline, banners (severity), diagrams, stat cards, checklist
- **Interactive:** Collapsible timeline phases

### Reference

- **Layout:** Header → deep table of contents → anchored sections → code blocks → cross-reference links
- **Key components:** TOC, code blocks, tables, callout boxes for gotchas, collapsible sections
- **Interactive:** All detail sections collapsible, deep anchor linking

### Handoff

- **Layout:** Header with status banner → what's done / what's left two-column → key files list → decision log → context for next session
- **Key components:** Banner (status), two-column layout, checklist, callout boxes
- **Interactive:** Collapsible context sections

### Review (code review)

- **Layout:** Header with target description and date → stat cards (finding counts by severity) → file risk map table (per-file changes, severity dots) → annotated diffs with inline margin comments → overengineering summary → CLAUDE.md drift section → agent coverage summary → recurring patterns
- **Key components:** Diff viewer with inline callout annotations, finding rows with severity badges, stat cards, file risk table with severity dots, banners, code blocks
- **Interactive:** Collapsible per-file diff sections, tabs for findings-by-severity vs. findings-by-file views

## Sharing

HTML files are designed to be shared. Common workflows:

- **Open locally:** `open docs/current_work/specs/d01_feature_spec.html` — immediate browser preview
- **Attach to PRs:** Upload the HTML review artifact to the PR description or as a comment. GitHub renders HTML attachments.
- **Upload to S3 / hosting:** For team-wide access, upload to an S3 bucket or static hosting. Share the link in Slack, email, or Linear. A link gets read; an attachment doesn't.
- **GitHub Pages:** For persistent access, push HTML files to a `gh-pages` branch or `docs/` directory with Pages enabled.
- **Email:** HTML files open directly in browsers — attach and recipients can view without any tooling.

The key insight: the chance of someone actually reading your spec, report, or PR writeup is much higher when it's a styled HTML page they can open in a browser.

## Design System Reference

All rendered HTML must follow the design system defined in `[sdlc-root]/templates/html-design-system.html`. That file contains:

- CSS custom properties (tokens) for colors, typography, spacing, borders, and radius
- Component patterns with example HTML for each
- Layout patterns (grids, columns, responsive breakpoints)
- SVG diagram conventions (node styles, edge styles, arrow markers)
- Print styles for graceful degradation

When rendering, read the design system file and apply its tokens and component patterns. Do not invent new visual patterns — use what the design system provides. If a new component is genuinely needed, add it to the design system first.
