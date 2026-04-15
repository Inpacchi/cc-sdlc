# Data Modeling Discipline

**Status**: Parking lot — bootstrapping with Len Silverston's Universal Data Model patterns
**Knowledge store**: `[sdlc-root]/knowledge/data-modeling/` (cross-project)

## Scope

Structuring business data: identifying entities, relationships, and patterns that faithfully represent how an organization actually works. This discipline draws heavily on Len Silverston's *Data Model Resource Book* series, which catalogs universal patterns discovered across hundreds of real-world implementations.

## Key Distinction

Len's approach is pedagogical, not technical-first:
- **Business concepts** come first ("People and Organizations", "Products", "Work Effort")
- **Patterns** are introduced as implementation approaches (Party/Role, Product Type/Feature, etc.)
- The business person should recognize their world in the model *before* seeing the abstraction

This matters for how the knowledge store is organized: entries are keyed by business concept, not by pattern name.

## Relationship to Other Disciplines

Data modeling sits at the intersection of several disciplines:
- **Business Analysis** — understanding the domain (what entities exist, how they relate)
- **Architecture** — system design decisions (how to structure schemas, when to normalize/denormalize)
- **Design** — how users interact with modeled data (forms, grids, drill-downs)
- **Testing** — validating that the model handles real-world edge cases

The knowledge store serves all of them. A BA pulls it to understand domain patterns. An architect pulls it to design schemas. A tester pulls it to generate boundary cases.

## The Silverston Contribution

Len Silverston's *Data Model Resource Book* (Volumes 1-3) represents decades of pattern discovery across industries. The key insight: **most businesses model the same core concepts**, and the patterns that work are remarkably universal. What varies is the industry-specific overlay.

Core subject areas (from the books):
1. **People and Organizations** — Party/Role pattern
2. **Products** — Product Type/Feature pattern
3. **Orders and Shipments** — Order/Line Item pattern
4. **Work Effort** — Task/Assignment pattern
5. **Business Transactions** — Account/Transaction pattern
6. **Communication Events** — Interaction/Channel pattern

Industry overlays: Healthcare, Insurance, Financial Services, Telecom, Manufacturing, Professional Services, Travel, E-Commerce, Government

## Parking Lot

*Add data modeling insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **AI agents as modeled entities.** [NEEDS VALIDATION] AI agents can be represented as Parties with Roles in UDM-style systems (meta-pattern: the AI itself is modeled using the same data model it operates on). UDM provides stable "what", AI provides intelligent "how". natural_language_query → UDM_structured_query → business_result workflow. Memory systems enable continuous learning and pattern recognition across UDM entities.

- **Entity-Party-Role (EPR) pattern.** [NEEDS VALIDATION] Entity → has many PartyRoles → Party + Role. Three-tier assignment UX: bulk (fast) → individual with role (medium) → full RACI matrix (detailed). The pattern generalizes: ResourceAssignment, transaction party roles, and account party roles all use EPR.

### Skill Trajectory

```
NOW:     Knowledge store seeded with core patterns from Silverston
SOON:    Enriched with consulting experience and real-world implementations
THEN:    Structured enough to guide AI-assisted data modeling sessions
LATER:   /model-assess — evaluate an existing model against UDM patterns
         /model-apply  — suggest patterns for a new domain
         /model-review — review a proposed model for anti-patterns
```
