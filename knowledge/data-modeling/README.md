# Data Modeling Knowledge Store — Cross-Project

Knowledge for AI-assisted data modeling, rooted in Len Silverston's Universal Data Model patterns.

Organized by **business concept** (how a domain expert thinks about it), not by pattern name (how a data modeler implements it). This follows Silverston's pedagogical approach: recognize the business problem first, then learn the pattern.

## Structure

```
knowledge/data-modeling/
├── README.md                       ← This file
├── patterns/                       ← Core UDM patterns (one YAML per subject area)
│   ├── people-and-organizations.yaml   ← Party/Role (the foundational pattern)
│   ├── products.yaml                   ← (future) Product Type/Feature
│   ├── orders.yaml                     ← (future) Order/Line Item
│   ├── work-effort.yaml                ← (future) Task/Assignment
│   ├── business-transactions.yaml      ← (future) Account/Transaction
│   └── communication-events.yaml       ← (future) Interaction/Channel
├── industries/                     ← Industry-specific overlays
│   └── (future: healthcare.yaml, financial-services.yaml, etc.)
├── anti-patterns/                  ← Common mistakes + why they fail
│   └── common-modeling-mistakes.yaml
├── assessment/                     ← Templates for evaluating existing models
│   └── model-health-check.yaml
└── diagrams/                      ← Visual reference diagrams
    └── party-role-erd.d2
```

## How This Gets Used

1. Someone asks a data modeling question ("how should I model customers and vendors?")
2. The AI loads the relevant pattern file (people-and-organizations.yaml)
3. The response leads with the business concept, introduces the pattern, explains why alternatives fail
4. If applicable, points to real implementations as proof

## Pattern File Structure

Each pattern YAML follows a consistent structure:

```yaml
id: people-and-organizations
business_concept:
  name: "People and Organizations"
  description: "What this is about in business terms"
  questions_it_answers: ["list of real questions people ask"]

pattern:
  name: "Party"
  core_insight: "The key abstraction"
  entities: [...]
  relationships: [...]

why_this_works:
  silverston_reasoning: "Len's explanation of why"
  real_world_evidence: [...]

anti_patterns:
  - name: "The common mistake"
    why_it_fails: "What goes wrong"

implementations:
  - system: "Your Project Name"
    models: [...]
```

## Maintenance

- Updated as Len Silverston reviews and enriches patterns
- New patterns added as subject areas are documented
- Anti-patterns accumulate from real consulting/implementation experience
- Industry overlays added when domain-specific projects exercise them

## Relationship to Testing Knowledge

Same structural philosophy as `[sdlc-root]/knowledge/testing/`:
- Cross-project knowledge lives here
- Project-specific adaptations live in each project's docs
- Knowledge accumulates across engagements
- Each entry is self-contained and AI-parseable
