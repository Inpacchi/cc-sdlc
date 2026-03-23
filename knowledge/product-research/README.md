# Product Research Knowledge Store — Cross-Project

Knowledge for structured competitive analysis and feature scoping during SDLC work. When building a new feature or evaluating a UI component, this knowledge guides an agent through identifying competitors, comparing feature dimensions, and generating scoping questions for the product owner.

## Structure

```
knowledge/product-research/
├── README.md                                  ← This file
├── competitive-analysis-methodology.yaml      ← Process an agent follows end-to-end
├── data-source-evaluation.yaml                ← 4-phase methodology for evaluating external data sources
├── dimension-catalog.yaml                     ← Reusable comparison dimensions by feature archetype
├── product-methodology.yaml                   ← RICE, Kano, Jobs-to-be-Done, North Star metric
└── risk-assessment-framework.yaml             ← Legal/compliance risk assessment, compliance gap analysis
```

## How This Gets Used

1. During SDLC work, someone needs to scope a feature ("we need a Gantt chart" or "add chat to the app")
2. An agent loads the methodology and identifies the feature archetype
3. The dimension catalog provides starter dimensions so research doesn't begin from zero
4. The agent runs web searches, builds a comparison matrix, and generates scoping questions
5. The product owner uses the comparison + questions to define scope for the spec

## Relationship to Other Knowledge Stores

Same structural philosophy as `knowledge/data-modeling/` and `knowledge/testing/`:
- Cross-project knowledge lives here
- Project-specific competitive research lives in the project's docs
- Knowledge accumulates across engagements — dimensions discovered for one project's Gantt research benefit the next project's Gantt evaluation

## Skill Trajectory

This knowledge feeds a future `/feature-compare` skill:
```
/feature-compare "gantt chart widget"
/feature-compare "real-time chat"
/feature-compare "ticketing system"
```

## Maintenance

- Updated when competitive analyses reveal new dimensions worth generalizing
- Dimension catalog grows as new feature archetypes are researched
- Methodology refined based on what produces the most useful output for product owners
