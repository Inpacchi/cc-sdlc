# Design Discipline

**Status**: Active — UX modeling capability
**Knowledge store**: `knowledge/design/` (cross-project)

## Scope

UI/UX design, visual design, interaction patterns, accessibility, component library design.

## UX Modeling

The primary active capability in this discipline. When a feature scope has been defined — often from competitive analysis (`/feature-compare`) or stakeholder requirements — UX modeling determines how the feature integrates into the existing app's IA, navigation, and component patterns.

### When to Invoke

- **New feature areas** — multi-page features that need IA decisions (where in the nav, URL structure, page hierarchy)
- **Page additions** — new views that need layout and component arrangement
- **Navigation changes** — restructuring sidebar, tabs, or breadcrumbs
- **Complex interactions** — features with drag-and-drop, real-time updates, multi-step flows
- **Designer handoff** — when a designer needs a detailed spec to produce high-fi mockups

### Key Principle: Start From Existing State

The agent always examines current routes, components, navigation, and patterns before proposing anything. This prevents designs that are incongruent with the existing app. The methodology in `knowledge/design/ux-modeling-methodology.yaml` codifies this as Phase 1.

### Output Formats

The agent selects the appropriate format(s) based on what's being modeled:

| Format | Best For | Tool |
|--------|----------|------|
| ASCII diagrams | Navigation, page wireframes, IA sections | Inline markdown |
| D2 diagrams | IA site maps, user flows, component relationships | `d2` CLI → PNG/SVG |
| Figma prompts | Detailed UI specs for designer execution | Natural language |

**D2 note**: D2 handles IA and flow diagrams well but is NOT suited for wireframes (it lacks UI primitives like buttons, inputs, cards). ASCII handles low-fi wireframes. Figma prompts handle high-fi specifications.

### How to Use

An agent follows the methodology in `knowledge/design/ux-modeling-methodology.yaml`:
1. **Context** — read existing routes, nav, components, and the feature scope
2. **Analysis** — determine what needs modeling (new pages, changed nav, new interactions)
3. **Production** — generate artifacts using conventions from `knowledge/design/ascii-conventions.yaml`
4. **Review** — present artifacts, call out key decisions, iterate with the product owner

### Skill Trajectory

```
NOW:     Knowledge store with methodology + ASCII conventions
NEXT:    Prove it works on 2-3 real UX modeling sessions (refine methodology)
THEN:    Package as /ux-model skill
```

### Pipeline

Composes with competitive analysis into a pre-spec pipeline:
```
/feature-compare "[feature]"    → comparison + scoping questions
  ↓ (product owner answers)
/ux-model "[feature with scope]" → IA diagrams, wireframes, Figma prompts
  ↓
Normal SDLC: spec → plan → implement
```

## Parking Lot

*Add design insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Accessibility and testability are the same problem.** Promoted → `knowledge/design/accessibility-testability-principles.yaml` (unified_concern section) + `knowledge/testing/gotchas.yaml` (color-only-status-indicators entry)

- **Advanced components as product differentiators.** [NEEDS VALIDATION] Complex UI components (Gantt charts, flowcharts, custom widgets, rich data visualizations) are what make apps look purposeful. The shared component library is a design asset, not just a code asset. Test automation strategies for these components protect design investment.

- **Never convey meaning through color alone.** Promoted → `knowledge/design/accessibility-testability-principles.yaml` (color_meaning_rule section) + `knowledge/testing/gotchas.yaml` (color-only-status-indicators entry)

- **Visual verification requires computed style checks.** [NEEDS VALIDATION] DOM correctness does not equal visual correctness. Design should ensure that visual states have programmatic equivalents (aria attributes, data attributes) that can be verified without pixel comparison.
