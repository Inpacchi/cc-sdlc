# design-for-ai Plugin Setup

The `design-for-ai` plugin enriches design consultations with structured design theory from *Design for Hackers* by David Kadavy.

## What It Provides

| Skill | What It Does | Used By |
|-------|-------------|---------|
| `design-for-ai` | Master skill — apply visual design principles, review or create UI | `design-consult` |
| `/exam` | Theory-backed design audit — find what's wrong and explain why | `design-consult` (existing UI) |
| `/design` | Establish design foundations — purpose, audience, aesthetic direction | `design-consult` (new UI) |
| `/color` | Build a color system from color science up | `design-consult` (color questions) |
| `/fonts` | Select, pair, and configure typography with theory backing | `design-consult` (typography) |
| `/flow` | Add motion, interaction states, and responsive behavior | `design-consult` (interaction) |
| `/hone` | Final quality pass — every design principle checked | `design-consult` (final review) |
| `/brand` | Strip AI design tells and add intentional character | `design-consult` (branding) |

## Reference Materials

The plugin includes reference files from *Design for Hackers* chapters:

| File | Topic |
|------|-------|
| `references/chapter-03-typography.md` | Type principles, pairing, hierarchy |
| `references/chapter-05-proportions.md` | Grid, golden ratio, spatial relationships |
| `references/chapter-06-composition.md` | Eye flow, visual weight, balance |
| `references/chapter-07-visual-hierarchy.md` | Size, contrast, proximity, alignment |
| `references/chapter-08-color-science.md` | Color physics, perception, accessibility |
| `references/chapter-09-color-theory.md` | Hue relationships, palette construction |
| `references/checklists.md` | Actionable design audit checklists |
| `references/ai-tells.md` | Common AI design patterns to avoid |
| `references/motion.md` | Animation principles and timing |
| `references/interaction.md` | Interaction states, affordances |
| `references/responsive.md` | Responsive design patterns |

## Installation

Install via Claude Code's plugin system. The plugin is available from the design-for-ai repository (check the upstream cc-sdlc README for the current installation method).

Once installed, the `[PLUGIN: design-for-ai]` markers in the `design-consult` skill will activate.

## How It Integrates with design-consult

When the `design-consult` skill runs:

1. **Research phase**: The orchestrator reads relevant reference files from the plugin's `references/` directory and pre-extracts principles into the designer's context brief.

2. **Designer dispatch**: The `ui-ux-designer` agent is instructed to run `/exam` (for existing UI) or `/design` (for new UI) as part of the consultation.

3. **Enforcement**: If the designer produces output without citing design theory, the orchestrator re-dispatches with explicit enforcement instructions.

## Degraded Mode (Without Plugin)

If design-for-ai is not installed:
- The `design-consult` skill skips the reference file reading step
- The `ui-ux-designer` agent is prompted to apply general design principles from its training knowledge
- The explicit theory-backing will be weaker, but the consultation workflow remains intact
- Visual mockup generation (via Playwright) still works — it uses your project's actual design tokens, not the plugin

The consultation produces usable output without the plugin, but without the structured *Design for Hackers* framework backing the decisions.
