---
type: handoff
slug: sdlc-explain-visual-options-artifact
created: 2026-10-03
status: pending
trigger: idea
recommended_next_skill: sdlc-develop-skill
source_session_summary: "Choosing how to update the map pin key in paire-app; CD asked for both candidate designs shown side by side and liked how the generated preview page turned out."
active_deliverable: null
related_files:
  - docs/current_work/ideas/sdlc-explain-visual-options-artifact_reference.html
  - skills/sdlc-explain/SKILL.md
  - skills/sdlc-render/SKILL.md
  - skills/sdlc-walkthru/SKILL.md
  - process/html-rendering.md
---

# Handoff: Teach `sdlc-explain` to produce side-by-side option previews like the pin key page

## Why this is a handoff
The source session was deciding how to update the map pin key in the consumer app (paire-app). CD asked to see two candidate designs, then said they loved how the preview page was generated and asked for the upstream cc-sdlc `sdlc-explain` skill to be modified to match. The skill lives in this repo at `skills/sdlc-explain/SKILL.md`; the handoff was written in the paire-appetit workspace and moved here. The source session should not inherit the pin key work itself (option B was chosen and is being built separately).

The source session could not read `sdlc-explain` (it is not installed in the paire-appetit workspace), so everything below describes what the preview page did, not what the skill does today. The receiving session must read `skills/sdlc-explain/SKILL.md` first and diff it against this description.

## What needs to happen
Update the upstream `sdlc-explain` skill so that, when CD is choosing between visual or UI options, it produces a page like the reference file instead of describing the options in text. The qualities CD liked, as shown in the reference page:

- **Both options on one page, side by side,** each labeled with a plain name and a one-line "what you give up / what you get" subtitle. CD asked for "both" and this let them compare without scrolling between messages.
- **Real project material, not placeholders.** Real pin art from the repo (resized and embedded as images so the page stands alone), and the real wording from the old app, reworded only for current naming. Nothing invented.
- **Shown at real size and in real context.** Each option sits in a card at the true width of the in-app card (300px), on a stand-in map background, so "too long for a small map" is visible, not argued.
- **A short caveats list under the options** naming what the mockup leaves out or approximates (for example, one pin's face is drawn by the app at runtime and is missing from the picture file). This kept the page honest.
- **Plain, specific copy.** Short sentences, no jargon, no code names on the page.
- **Works in light and dark and at phone width.** Colors come from tokens, the page background is set explicitly, the layout stacks to one column when narrow.
- **Published as a private page with a link,** with no code changes to the product made to produce it.
- **The chat reply stayed short and followed the Plain English Deliverable output style:** what we're building, the options in numbered pieces, "things to know", then the decision needed.

Open design choice for the upstream skill: whether this is the default for every explanation or only triggers for visual and UI decisions (recommended: only when two or more concrete visual options exist and the choice is CD's).

## Evidence
- **Reference page (self-contained, open in a browser):** `docs/current_work/ideas/sdlc-explain-visual-options-artifact_reference.html`. Source copy of what was published at https://claude.ai/artifact/EXSfd7KhmdtLosXwFAnALj (private to the owner, so use the file, not the link).
- **Output style CD was using:** a "Plain English Deliverable" style from the paire-appetit workspace (not part of this repo).
- **Closest existing skills here:** `skills/sdlc-explain/SKILL.md` (the target), `skills/sdlc-render/SKILL.md` (renders finished markdown deliverables to HTML) and `skills/sdlc-walkthru/SKILL.md` (paced read of an artifact). Neither produces option comparisons from real project assets.
- **Closest existing convention:** `process/html-rendering.md` § "Two Categories of HTML" already describes "exploration artifacts" such as side-by-side approach comparisons as throwaway working tools. The reference page is a concrete example of that category.
- **CD's words:** "i love how this artifact was generated - create a handoff for cc-sdlc upstream to modify the sdlc-explain skill accordingly."
- **How the page was built (for reproduction):** the pin images were resized to about 72px tall with `sips`, base64-embedded into one HTML file through a small Python substitution over a template with `{{asset}}` placeholders, then published with the Artifact tool using the artifact-design guidance (tokens on `:root`, dark-mode blocks, no external assets).

## Recommended next step
Open a session in this repo (cc-sdlc) and run: **`/sdlc-develop-skill`** (MODIFY mode) on `sdlc-explain`, with this file and the reference HTML as the seed.

Reasoning: this is a change to an existing skill, and the modify mode handles the framework-versus-project-section markers and the DRY check against `sdlc-render` and `sdlc-walkthru`. 

## Open questions
- What does `sdlc-explain` do today? Its description covers single-subject picture explainers with a word budget. Is option comparison a new mode, or a separate skill?
- Should the option preview be a separate mode of that skill, or a hook into `sdlc-idea` exploration artifacts, which already cover this case in `html-rendering.md`?
- Should the skill require real assets from the repo when they exist, and say what to do when they don't (label placeholders clearly)?
- Hosting: the reference was published as a private page. Should the skill default to a local HTML file in `docs/current_work/` when no artifact tool is available?
- Where does the "caveats under the options" list come from, so it stays honest and is never left empty out of habit?

## Out of scope (do NOT pursue)
- The pin key change itself in paire-app, and its wiki and tests.
- Rewriting `sdlc-render`'s design system or document-type profiles.
- Changing the Plain English Deliverable output style.
