# Testing Knowledge Store — Cross-Project

Knowledge that applies across all projects using our hybrid testing approach.
Project-specific knowledge lives in each project's `docs/testing/knowledge/`.

## Structure

```
knowledge/testing/
├── README.md                          ← This file
├── testing-paradigm.yaml              ← Functional core/imperative shell, test type selection
├── advanced-test-patterns.yaml        ← Chaos hypothesis, property-based testing, feature-flag isolation
├── tool-patterns.yaml                 ← How to use Playwright CLI, Playwright MCP, etc.
├── component-catalog.yaml             ← Test strategies for shared UI components
├── gotchas.yaml                       ← Cross-project failure patterns
└── timing-defaults.yaml               ← Default wait profiles by component type
```

## How This Gets Used

1. Before a test session, the agent loads relevant cross-project knowledge
2. Project-specific knowledge (app map, element catalog) is loaded next
3. Together they form the context that prevents re-learning

## Maintenance

- Updated after test cycles when a pattern proves generalizable
- Human-reviewed after each project's testing phase concludes
- Component knowledge travels with the component
