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

### External Ingestion — 2026-04-22 (Generic SQL & ORM patterns from production systems)

- **Multi-tenant isolation must be validated at every CTE hop, not just endpoints.** [NEEDS VALIDATION] When a recursive CTE traverses a graph in a multi-tenant schema, the temptation is to filter `WHERE tenant_id = ?` on the anchor query and assume the recursive step inherits it. It does not — the recursive step joins from the previous level into new rows that may belong to other tenants. Apply the tenant filter on **both** the anchor query AND the recursive step. The same hazard exists in any iterated query (CTEs, repeated joins, graph traversals): isolation must hold at every hop, not just at the entry point.

- **LEFT JOIN filter placement: ON vs WHERE have different semantics.** [NEEDS VALIDATION] On an OUTER join, putting a filter in the `ON` clause keeps the unmatched rows (with NULLs in the joined columns); putting it in the `WHERE` clause removes them, silently turning the LEFT JOIN into an INNER JOIN. Multi-tenant queries get this wrong constantly: `LEFT JOIN child ON child.parent_id = parent.id WHERE child.tenant_id = ?` excludes parents with no children. The fix: `LEFT JOIN child ON child.parent_id = parent.id AND child.tenant_id = ?`. This SQL fundamental belongs in any data-modeling review checklist.

- **ORM-enabled DML still fires `onupdate` hooks even with `synchronize_session=False`.** [NEEDS VALIDATION] In SQLAlchemy (and similar ORMs), `synchronize_session=False` on an UPDATE only suppresses cache synchronization — it does NOT skip column-level `onupdate` hooks (e.g., `updated_at = func.now()`). For true bypass (e.g., a backfill that should not bump `updated_at`), use raw SQL or `synchronize_session=False` plus `bind_arguments={'execution_options': {'compiled_cache': None}}`. The general principle: ORM "skip features" almost never skip everything; verify by reading the generated SQL with `echo=True` or equivalent.

- **Idle-in-transaction timeout requires explicit COMMIT in async code.** [NEEDS VALIDATION] In async runtimes, an implicit transaction can be left open across an `await` boundary if the code path doesn't explicitly commit. The connection sits in `idle in transaction` state, vulnerable to `idle_in_transaction_session_timeout` killing it mid-operation. The pattern: wrap async work in an explicit `async with session.begin():` block, or call `session.commit()` before any long-running async gap. Same hazard exists with explicit savepoints in long-lived sessions.

### Skill Trajectory

```
NOW:     Knowledge store seeded with core patterns from Silverston
SOON:    Enriched with consulting experience and real-world implementations
THEN:    Structured enough to guide AI-assisted data modeling sessions
LATER:   /model-assess — evaluate an existing model against UDM patterns
         /model-apply  — suggest patterns for a new domain
         /model-review — review a proposed model for anti-patterns
```
