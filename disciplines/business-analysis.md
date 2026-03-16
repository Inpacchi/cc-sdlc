# Business Analysis Discipline

**Status**: Parking lot — capturing ideas as they emerge from other work

## Scope

Requirements elicitation, domain modeling, stakeholder needs, acceptance criteria, user stories.

## Parking Lot

*Add business analysis insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **Test data design is lightweight domain modeling.** When building test data for a feature, you must reason about: What are valid ranges for numeric fields? What states exist? What transitions are allowed? This is domain analysis happening inside the testing discipline. The BA discipline should feed valid domain ranges and business rules into test specs — and test specs should surface domain questions back to BA.

- **Acceptance criteria flow both directions.** BA writes acceptance criteria in specs. Testing verifies them. But testing also *discovers* missing acceptance criteria (e.g., "the spec didn't say what happens when you enter an invalid value in this field"). These discoveries should flow back to BA for future specs.

- **Architect-proposed expected values need domain validation.** For computed or formula-derived values, the architect proposes expected results based on code understanding, but the domain expert validates against real-world knowledge. This is a BA function — ensuring computed values make domain sense.
