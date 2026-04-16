# Coding Knowledge Store — Cross-Project

Code quality principles, anti-patterns, and structural rules that apply across all projects using the SDLC framework. Focuses on code structure decisions that affect testability, maintainability, and review quality.

## Structure

```
knowledge/coding/
├── README.md                              ← This file
├── code-quality-principles.yaml           ← Structural rules: testability, mocking stance, code smells
└── typescript-patterns.yaml               ← Branded types, Result types, exhaustiveness, type predicates
```

## How This Gets Used

1. **Code reviewers** consult these principles when evaluating whether code is structured for testability
2. **Architects** reference the structural rules during plan review (checking for I/O-logic entanglement)
3. **Backend/frontend developers** apply the mocking stance and testability rules during implementation
4. **Planning agents** use the testability lens when reviewing proposed designs

## Relationship to Other Knowledge Stores

- **`[sdlc-root]/knowledge/testing/testing-paradigm.yaml`** — the testing-side view of the same principles (test type selection, regression-first). Coding principles are the *code structure* side; testing principles are the *test strategy* side.
- **`[sdlc-root]/knowledge/architecture/`** — architectural decisions that affect code structure (component boundaries, domain separation)

## Maintenance

- Updated when code review sessions reveal new structural anti-patterns worth generalizing
- Entries promoted from `[sdlc-root]/disciplines/coding.md` parking lot after validation through real use
