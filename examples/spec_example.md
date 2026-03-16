# D42: Memory Formation Layer — Specification

> **Note:** This example is included as a reference for what a well-formed spec looks like, not as project content.

**Status:** Complete
**Created:** 2026-01-24

---

## 1. Problem Statement

The system processes events but doesn't automatically create memories from them. Memories are only created via manual API calls.

We need an "attention" mechanism — a layer that decides **when** events become memories and **how** those memories are formed.

---

## 2. Requirements

### Functional
- [ ] Events flow through formation layer before memory creation
- [ ] Formation rules determine which events become memories
- [ ] Rules are configurable per event type
- [ ] Provenance is tracked (where the memory came from)

### Non-Functional
- [ ] Processing latency < 100ms per event
- [ ] Rules can be updated without restart

---

## 3. Design

### Approach

Create a `FormationLayer` module that:
1. Receives domain events
2. Evaluates against formation rules
3. Creates memories for qualifying events
4. Tracks provenance

### Key Components

| Component | Purpose |
|-----------|---------|
| FormationLayer | Orchestrates event → memory flow |
| FormationRules | Rule definitions and evaluation |
| ProvenanceTracker | Records memory origins |

### Data Model

```elixir
# Formation rule
%FormationRule{
  event_type: "party_created",
  action: :create_memory,
  memory_type: "entity_record",
  importance_score: 0.7
}
```

---

## 4. Success Criteria

- [ ] Events automatically create memories based on rules
- [ ] Provenance is recorded for all formed memories
- [ ] Rules can be listed and modified
- [ ] Unit tests cover rule evaluation

---

## 5. Out of Scope

- AI-based importance scoring (future D45)
- User-configurable rules UI (future phase)

---

## 6. Open Questions

- [x] Should rules be stored in database or config? → Database for flexibility
