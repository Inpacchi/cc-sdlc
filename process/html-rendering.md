# HTML Rendering

Markdown is the source of truth for all SDLC deliverables — agents read it, version control tracks it, templates define its structure. HTML is how a human absorbs it: an explainer with big pictures and few words, produced by `sdlc-explain` (the `/eli5` command). It is opt-in, generated alongside the markdown, never instead of it.

## Philosophy

- **MD for agents and git.** Markdown stays clean, structured, and agent-optimized. No HTML concerns leak into templates or markdown content.
- **HTML explains; it does not transcribe.** The comprehensive read of an artifact belongs to `sdlc-walkthru`. The HTML's job is that a reader who knows nothing about the subject can say its one load-bearing idea back after a single pass.
- **Big pictures, few words.** Humans absorb a picture with a hard limit faster than three paragraphs of prose, and agents drown in prose.

## Visual Doctrine: Big Pictures, Few Words

Every HTML artifact the framework produces — explainers and exploration artifacts — follows one doctrine. It comes from Thariq Shihipar's day-to-day practice with Claude Code artifacts ("use big pictures and few words", the `eli5` plugin) and from a plain observation about agentic work: **one picture plus a hard limit beats three paragraphs of vibe.** Prose is where a human in the loop becomes the bottleneck; pictures are how they stay in the loop. The same instinct as "show me the diff, not the essay."

1. **Picture first.** Anything that has a shape — a mechanism, a flow, a sequence, a structure, a dependency, a comparison, a before/after, a timeline — is drawn before it is described.
2. **Inline SVG is the picture medium.** Self-contained, themeable through design-system tokens, editable by the next person, readable by agents. Build from the design system's diagram vocabulary (`[sdlc-root]/templates/html-design-system.html` § SVG Diagrams). No `<img>`, no Mermaid, no external assets.
3. **Few words, with hard limits.** Captions are one sentence. Labels are nouns. Explainers carry an explicit word budget (`sdlc-explain` step 4); walkthrough parts stay under 350 words (`sdlc-walkthru`). When a limit is hit, add a picture or a real value — never words.
4. **Real names, real values.** `RankingService → score (0–100) → feed` teaches; `Service A → data → Consumer` decorates. Draw from the source's own identifiers.
5. **Big means one picture per screen.** A picture and its caption fill the viewport; labels are legible without zooming.
6. **Gloss jargon at the point of use, inside the picture.** A three-to-six-word annotation beside the term. Never a glossary section.
7. **Lossy, never false.** An explainer leaves most of the document out on purpose. Every claim it does make is verified against the artifact or the code and cited in the footer, and every open decision in the source gets a picture.

What the doctrine does **not** mean: decorative pictures for content with no shape, or diagrams that restate a table. If a section cannot be drawn honestly, it does not get a picture.

## Two Categories of HTML

**Explainers** — Big-pictures-few-words explanations of one subject: a deliverable (spec, plan, result, idea brief, handoff, audit, incident, reference, review), a module, a tradeoff, or an incident. Produced by `sdlc-explain`, static apart from an optional prev/next stepper, inline SVG only, hard word budget. Offered after a skill writes a deliverable; on demand for questions.

**Exploration artifacts** — Interactive HTML files created during `sdlc-idea` exploration and `sdlc-plan` discovery to help CD evaluate options: side-by-side comparisons, interaction prototypes, parameter tuning with sliders, drag-and-drop prioritization. They use the design system for tokens but allow any JavaScript the interaction needs. Demand-driven — built when a text description would not let CD decide confidently.

How the two HTML categories and the walkthrough relate:

| | Explainer (`sdlc-explain`) | Walkthrough (`sdlc-walkthru`) | Exploration artifact |
|---|---|---|---|
| **Input** | A deliverable, module, tradeoff, or incident | A deliverable | An open decision during idea / plan discovery |
| **Output** | One static HTML file | A paced conversation (no file) | An interactive HTML tool |
| **Fidelity** | Lossy by design — never false | Selective — nothing load-bearing omitted | N/A — a tool, not a view |
| **Feeds** | Understanding before a gate, onboarding, incident review | Comprehension and decisions at the gate | One decision |
| **Offered** | After a skill writes a deliverable; on demand | Same offer point, the explainer's peer | Built directly when needed |

## Post-Skill Offer

After a skill writes a deliverable MD file to `docs/current_work/`, CC **asks CD** whether they want an explainer (`sdlc-explain`) or a walkthrough (`sdlc-walkthru`) — never unprompted. The markdown stands on its own; both are optional ways for a human to absorb it. CD picks one, both, or neither. If CD accepts the explainer, it is built with the document type's storyboard defaults (below) and no further Q&A.

**Offer precedes approval — never in sequence with it.** When the deliverable feeds an approval gate (spec approval, the plan-mode execution prompt), the offer is its own interaction, fully resolved before approval is requested: offer, and if accepted, deliver so CD can absorb it *before* being asked to approve. Never bundle the offer into the approval question, and never deliver after approval — a post-approval explainer cannot inform the decision it exists to support.

**Headless runs** (no person present) take the no path: no offer, no explainer, no walkthrough. The run's result lists the offer under `skipped` (`[sdlc-root]/process/headless-mode.md`).

Skills that make the offer, and the storyboard each uses:

| Skill | Deliverable | Storyboard |
|-------|-------------|------------|
| `sdlc-plan` | spec, plan | spec, plan |
| `sdlc-lite-plan` | plan | plan |
| `sdlc-execute`, `sdlc-lite-execute` | result | result |
| `sdlc-idea` | idea brief | exploration |
| `sdlc-handoff` | handoff doc | handoff |
| `sdlc-audit` | audit report | report |
| `sdlc-debug-incident` | incident doc | incident |
| `sdlc-create-reference-doc` | reference doc | reference |
| `sdlc-review-code` | review report | review |

**On demand:** `/sdlc-explain <subject>` or `/eli5 <subject>` at any time, for a deliverable or a question.

## Output Conventions

**File naming.** A deliverable's explainer is written alongside its markdown with the same base name (`d01_feature_spec.md` → `d01_feature_spec.html`; a named audience appends a suffix such as `_leadership`). A question's explainer goes to `docs/current_work/explainers/{slug}.html`.

**Version control.** HTML files are generated artifacts. Projects may gitignore them (regenerate on demand) or track them (useful for links to specific commits). Neither is prescribed; the MD file is always the source of truth.

**Staleness.** An explainer is stale once its source markdown changes after generation — and a stale explainer is dangerous because humans read it and miss what only the markdown says. So:

- If CD opted into an explainer and a skill later updates that deliverable, the skill offers to regenerate it. If none exists, nothing needs keeping current.
- If the markdown is edited outside a skill and an explainer exists, the next skill that touches the file offers to regenerate, or CD invokes `/sdlc-explain` directly.
- When a plan CD has an explainer for undergoes review-fix revisions, regenerate after the final revision and **before the approval prompt** — not after each intermediate revision, never after approval.
- Every explainer's footer carries its generation timestamp; if the markdown is newer, regenerate before relying on it.

## Document-Type Storyboards

The default beats for each document type, in order. `sdlc-explain` starts here and bends the storyboard to the artifact's actual story; budgets (3–8 pictures, word cap) and the beat → picture table live in the skill.

| Type | Detected from | Default storyboard |
|------|---------------|--------------------|
| **Spec** | `docs/current_work/specs/` | The problem → what we are building, in its surroundings (anatomy) → how it works (flow) → what we will not do (constraints) → what is still open (decision cards) → what done looks like (the before/after the spec promises) |
| **Plan** | `docs/current_work/planning/`, `sdlc-lite/*_plan` | The shape of the work (phases as a timeline) → one picture per phase of what changes (before/after or flow; chapters if many) → the risks (tradeoff) → what done looks like → open decisions |
| **Result** | `docs/current_work/results/`, `sdlc-lite/*_result` | Before/after with the deltas named → what shipped (anatomy of the change) → what reviewers found (severity map) → what remains |
| **Exploration** (idea brief) | `docs/current_work/ideas/*_idea-brief` | The problem → each option as a picture (max 4) → the tradeoff picture → the recommendation accented, if there is one |
| **Handoff** | `docs/current_work/ideas/*_handoff` | Where we stopped (done / remaining timeline) → the key files (anatomy) → decisions made → the first step for the next session |
| **Report** (audit) | `docs/current_work/audits/` | The score (one stat picture) → findings by severity (map) → the top findings, one picture each (max 3) → what to fix first |
| **Incident** | `docs/current_work/incidents/` | The timeline → the root cause (zoom on the failing edge) → the blast radius (anatomy) → the fix (before/after) → what prevents recurrence |
| **Reference** | `docs/reference/` | The concept map (anatomy) → each key pattern as a picture → gotchas as danger-edge callouts |
| **Review** (code review) | `docs/reviews/` | The file risk map → each major finding as a picture (max 5) → recurring patterns |

If the path matches nothing, infer the closest type from the markdown's structure.

## Sharing

- **Open locally:** `open docs/current_work/specs/d01_feature_spec.html`
- **Attach to PRs:** upload the HTML to the PR description or a comment.
- **Static hosting or GitHub Pages:** for team-wide access; share the link in Slack, email, or Linear. A link gets read; an attachment doesn't.

The chance of someone actually absorbing a spec, report, or incident is much higher when it is six pictures they can open in a browser.

## Design System Reference

All HTML follows the design system in `[sdlc-root]/templates/html-design-system.html`: tokens for colour, typography, spacing, and radius; component patterns; layout patterns; the SVG diagram conventions (node styles, edge styles, semantic colours, arrow markers); and the Slide Deck component that provides the explainer's optional one-picture-per-screen stepper. The SVG section is the shared picture vocabulary for explainers and exploration artifacts alike. Do not invent visual patterns — if a component is genuinely needed, add it to the design system first.
