# Testing Knowledge Store — Cross-Project

Knowledge that applies across all projects using our hybrid testing approach.
Project-specific knowledge lives in each project's `docs/testing/knowledge/`.

## Structure

```
knowledge/testing/
├── README.md                          ← This file
├── testing-paradigm.yaml              ← Functional core/imperative shell, test type selection
├── advanced-test-patterns.yaml        ← Chaos hypothesis, property-based testing, feature-flag isolation
├── test-infrastructure-patterns.yaml  ← Suite structure, CI execution, result reporting, flake management
├── tool-patterns.yaml                 ← Reference patterns for Playwright CLI, Playwright MCP, AI browser tools
├── component-catalog.yaml             ← Template: project-populated test strategies for shared UI components
├── gotchas.yaml                       ← Cross-project failure patterns
├── timing-paradigm.yaml               ← Principles for handling timing in tests (wait for signals, not time)
├── timing-defaults.yaml               ← Template: project-populated wait-time profiles with measured values
└── ai-generated-code-verification.yaml ← Verification patterns for AI-generated code; eval-contamination guardrails
```

## How This Gets Used

1. Before a test session, the agent loads relevant cross-project knowledge
2. Project-specific knowledge (app map, element catalog) is loaded next
3. Together they form the context that prevents re-learning

## Maintenance

- Updated after test cycles when a pattern proves generalizable
- Human-reviewed after each project's testing phase concludes
- Component knowledge travels with the component
