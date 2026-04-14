---
name: sdlc-design-brand-asset
description: >
  Generate detailed specifications for visual brand assets — dimensions, element positioning,
  color values, typography, and AI image generation prompts. Produces actionable specs that
  can be handed to designers or used with AI image generators.
  Triggers on "design brand asset", "create brand asset", "asset spec for", "how should I design the", "specs for logo",
  "specs for OG image", "generate prompt for", "make me a [logo/favicon/OG image]",
  "what size should the", "where should I position".
  Do NOT use for UI component design — use design-consult.
  Do NOT use for implementing assets in code — use the frontend agent.
  Do NOT use for brand strategy — use brand-officer or chief-product-officer agent.
---

# Brand Asset Specification

Generate detailed, actionable specifications for visual brand assets. This skill produces specs that include exact dimensions, positioning, colors, typography, and AI image generation prompts — everything needed to create consistent brand assets without guesswork.

**Argument:** `$ARGUMENTS` (the asset type or description of what's needed)

## Workflow

```
IDENTIFY ASSET → GATHER BRAND CONTEXT → ASCII MOCKUP → GENERATE SPEC → GENERATE PROMPTS → EXPORT REQUIREMENTS
```

## Preconditions

**Required (gate if missing):**
- Asset type must be identified (ask if unclear)

**Optional (gather in Step 2 if missing):**
- Brand color palette (hex values)
- Typography (font families)
- Existing brand assets in the project's assets directory
- Design language keywords

## Output

This skill produces **inline specification text** — a detailed Markdown spec that the user copies to their design tool, AI image generator, or designer brief. The spec is NOT automatically written to a file.

The spec includes:
- Canvas dimensions and background
- Element positioning with pixel values
- Color hex codes and typography specs
- AI image generation prompts
- Export checklist with file locations

## Asset Types Supported

| Asset | Typical Dimensions | Notes |
|-------|-------------------|-------|
| Logomark | 64x64 base, scalable | Icon-only, must work at 16px |
| Wordmark | Variable width, 48-64px height | Text-based logo |
| Combined Lockup | Variable | Logomark + wordmark together |
| Favicon | 32x32 (with 16x16 variant) | Simplified for small sizes |
| Apple Touch Icon | 180x180 | Solid background, no transparency |
| OG Image (Default) | 1200x630 | OpenGraph for social sharing |
| OG Image (Square) | 1200x1200 | Twitter/X cards |
| Social Avatar | 400x400 (800x800 source) | Profile pictures |
| PWA Icons | 192x192, 512x512 | For web app manifest |

## Steps

### 1. Identify Asset Type

Determine which asset(s) the user needs. Ask if unclear:
- "Which asset are you creating?" (present the table above)
- "Is this a new asset or updating an existing one?"
- "What platforms will this be used on?"

### 2. Gather Brand Context

Read the project's brand context:
- **Color palette** — Check CLAUDE.md, design system files, or existing CSS for brand colors
- **Typography** — Identify display/heading fonts and UI fonts
- **Existing assets** — Check the project's public/assets directory for existing brand files
- **Design language** — Dark mode? Gradients? Minimal? Vibrant?

If brand context is missing, ask the user for:
- Primary brand colors (with hex values)
- Font families for headings and body
- Visual style keywords (minimal, bold, cosmic, etc.)

### 3. Generate ASCII Mockup

Before detailed specs, show a visual ASCII mockup of the asset layout. This helps users validate positioning and composition before implementation.

**Mockup conventions:**
- Use box-drawing characters (`┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼`) for clean lines
- Label dimensions on edges
- Show element names inside boxes
- Use dotted lines (`┄ ┆`) for margins/padding guides
- Indicate alignment with centerlines or edge markers

**Example — OG Image (1200x630):**
```
                              1200px
    ├─────────────────────────────────────────────────────────┤
    ┌─────────────────────────────────────────────────────────┐
    │ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ 80px margin ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
    │ ┆                                                     ┆ │
    │ ┆  ┌──────────┐                                       ┆ │
    │ ┆  │  LOGO    │  64x64                                ┆ │
    │ ┆  │  64x64   │  ← 80px from left, 80px from top      ┆ │
    │ ┆  └──────────┘                                       ┆ │ 630px
    │ ┆                                                     ┆ │
    │ ┆  ┌───────────────────────────────────────────┐      ┆ │
    │ ┆  │ HEADLINE TEXT                             │      ┆ │
    │ ┆  │ 48px Inter Bold                           │      ┆ │
    │ ┆  └───────────────────────────────────────────┘      ┆ │
    │ ┆                                                     ┆ │
    │ ┆  ┌─────────────────────────────┐                    ┆ │
    │ ┆  │ Tagline — 24px Inter Regular│                    ┆ │
    │ ┆  └─────────────────────────────┘                    ┆ │
    │ ┆                                                     ┆ │
    │ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
    └─────────────────────────────────────────────────────────┘
```

**Example — Favicon (32x32):**
```
         32px
    ├───────────┤
    ┌───────────┐
    │  ┌─────┐  │
    │  │ ICO │  │  32px
    │  │ 24  │  │
    │  └─────┘  │
    │    4px    │
    │  padding  │
    └───────────┘
```

**Example — Social Avatar (400x400 centered):**
```
              400px
    ├──────────────────────┤
    ┌──────────────────────┐
    │                      │
    │    ┌──────────┐      │
    │    │          │      │
    │    │  LOGO    │      │  400px
    │    │  CENTER  │      │
    │    │  240x240 │      │
    │    │          │      │
    │    └──────────┘      │
    │         ↕            │
    │    80px padding      │
    └──────────────────────┘
```

**Example — Combined Lockup (horizontal):**
```
              360px
    ├─────────────────────────────────────┤
    ┌─────────────────────────────────────┐
    │                                     │
    │  ┌────────┐    ┌─────────────────┐  │
    │  │ LOGO   │    │   WORDMARK      │  │  64px
    │  │ 48x48  │←──→│   Company Name  │  │
    │  └────────┘ 16 └─────────────────┘  │
    │             px                      │
    └─────────────────────────────────────┘
```

**Guidelines for mockups:**
- Always show canvas dimensions at edges
- Label each element with name and size
- Show spacing values between elements
- Mark margins with dotted guides
- For complex layouts, create multiple mockups (mobile vs desktop)

### 4. Generate Asset Specification

For each asset, output a complete specification (following the ASCII mockup):

#### Canvas Specification
```
**Canvas:** [width]x[height] px
**Background:** [see examples below]
**Format:** [PNG/SVG/WebP] + notes on transparency
```

**Background types (most assets use solid or gradient — no AI needed):**
- **Solid:** `#1a1a2e` (just the hex)
- **Gradient:** `linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)` (CSS syntax)
- **Radial:** `radial-gradient(circle at 30% 70%, #2d1b4e 0%, #1a1a2e 70%)`
- **Transparent:** `transparent` (for logos/icons with no background)
- **AI-generated:** "See AI Prompt section" (only for complex/textured backgrounds)

#### Element Specifications

For each element (logo, text, etc.), provide:

```
**[Element Name]**
- Size: [width]x[height] or [font size]px
- Position: [description] — [X]px from [edge], [Y]px from [edge]
- Color: [hex] or [gradient definition]
- Font: [family], [weight] (if text)
- Additional: [opacity, effects, etc.]
```

#### Composition Rules

- Margins/padding from edges
- Spacing between elements
- Alignment (centered, left-aligned, etc.)
- Visual hierarchy notes

### 5. Generate AI Image Prompts (When Needed)

**Skip this step if the background is:**
- Solid color — just specify the hex in Step 4
- Simple gradient — specify colors, direction, and stops in Step 4
- Transparent — no background needed

**Only generate AI prompts when the asset requires:**
- Textured or patterned backgrounds
- Photographic or illustrated elements
- Abstract/generative artwork
- Complex visual compositions

When AI generation IS needed, provide:

**Background Prompt:**
```
[Detailed prompt for AI image generator — describe style, colors, mood, composition,
what should be in focus, what should be empty/dark for text overlay]
```

**Full Asset Prompt (if generating complete asset):**
```
[Complete prompt including all elements — use when the AI can generate text/logos]
```

**Prompt Guidelines:**
- Include exact color hex values
- Specify dimensions and aspect ratio
- Describe what areas should be left empty for overlays
- Include style keywords (minimal, atmospheric, etc.)
- Specify what NOT to include

### 6. Export Requirements

Provide format and delivery specs:

```
**Export Checklist:**
- [ ] Format: [PNG/WebP/SVG]
- [ ] Dimensions: [exact size]
- [ ] Color space: sRGB
- [ ] Transparency: [yes/no]
- [ ] Variants needed: [list any size variants]
- [ ] File location: [where to save in project]
```

Include framework-specific notes if applicable (e.g., Next.js metadata files, static asset conventions).

## Specification Template

Use this structure for each asset:

> ## [Asset Name] Specification
>
> ### Layout (ASCII Mockup)
> ```
> [ASCII representation showing canvas, elements, dimensions, spacing]
> ```
>
> ### Canvas
> - **Size:** [W]x[H]
> - **Background:** [description + hex]
> - **Format:** [format]
>
> ### Elements
>
> **[Element 1]**
> - Size: [value]
> - Position: [description with pixel values]
> - Color/Style: [details]
>
> **[Element 2]**
> - ...
>
> ### Composition
> - [Spacing rules]
> - [Alignment]
> - [Visual hierarchy]
>
> ### AI Prompt (if applicable)
> [prompt text in a code block]
>
> ### Export
> - Format: [format]
> - Location: [path]
> - Variants: [list]

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll skip the ASCII mockup" | The mockup is how users validate layout before investing in implementation. Always include one. |
| "I'll give approximate sizes like 'medium'" | Use exact pixel values. "Medium" means nothing in production. |
| "The user can figure out positioning" | Specify X/Y offsets from edges in pixels. Remove guesswork. |
| "I'll skip the AI prompt" | If the asset needs AI generation (textures, photos, illustrations), include the prompt. Skip if it's just solid/gradient. |
| "Hex colors are optional" | Never use color names. Always provide hex values. |
| "This asset doesn't need export specs" | Every asset needs format, dimensions, and file location. |
| "I'll design the asset myself" | This skill produces SPECS, not implementations. The user or AI creates the actual asset. |
| "The background can just be 'dark'" | Specify exact hex, opacity, gradients, or effects. |
| "Typography details aren't needed" | Always specify: font family, weight, size in px, letter-spacing if relevant. |
| "The mockup doesn't need exact dimensions" | Show pixel values on the mockup edges and between elements. The mockup IS the spec, visualized. |

## Integration

- **Depends on:** Brand context (CLAUDE.md, existing assets, color palette)
- **Feeds into:** Asset creation in design tools or AI image generators, then frontend agent for implementation
- **Uses:** Brand context from project, existing asset inventory
- **Complements:** `design-consult` (design direction), brand-related agents (brand decisions)
- **Does NOT replace:** `design-consult` (UI/UX design), brand agents (brand strategy), frontend agent (code implementation)
