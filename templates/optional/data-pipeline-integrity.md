## Data Pipeline Integrity

When working with data pipelines, seed scripts, scrapers, or allowlists, **never use hallucinated or assumed values.** Every value must be traceable to an official source — a rules document, an API response, an existing codebase constant, or a user decision.

1. **Read from the defined source.** If the plan names an external source (GitHub repo, API, rules document), fetch from it.
2. **Cross-reference codebase constants.** When the codebase already has values, read those files and use the exact values.
3. **When a value cannot be sourced, use `AskUserQuestion`.**
4. **Coupled artifacts must read from each other.** The later file must read the earlier file as its canonical reference.
