# D42: Memory Formation Layer — Implementation Instructions

> **Note:** This example is included as a reference for what a well-formed plan looks like, not as project content.

**Spec:** `d42_memory_formation_layer_spec.md`
**Created:** 2026-01-24

---

## Overview

Implement the Memory Formation Layer that evaluates domain events against formation rules and creates memories for qualifying events.

---

## Prerequisites

- [x] Memory Substrate API available (D1-D6)
- [x] Domain events being published (D49)

---

## Implementation Steps

### Step 1: Create Formation Rule Schema

**Files:** `lib/acme_app/memory/formation_rule.ex`

Create the FormationRule schema:

```elixir
defmodule AcmeApp.Memory.FormationRule do
  use Ecto.Schema

  schema "memory_formation_rules" do
    field :event_type, :string
    field :action, Ecto.Enum, values: [:create_memory, :ignore]
    field :memory_type, :string
    field :importance_score, :float, default: 0.5
    field :enabled, :boolean, default: true
    timestamps()
  end
end
```

### Step 2: Create Migration

**Files:** `priv/repo/migrations/TIMESTAMP_create_memory_formation_rules.exs`

```elixir
def change do
  create table(:memory_formation_rules) do
    add :event_type, :string, null: false
    add :action, :string, null: false
    add :memory_type, :string
    add :importance_score, :float, default: 0.5
    add :enabled, :boolean, default: true
    timestamps()
  end

  create unique_index(:memory_formation_rules, [:event_type])
end
```

### Step 3: Create FormationLayer Module

**Files:** `lib/acme_app/memory/formation_layer.ex`

Implement the core formation logic:
- `process_event/1` — Entry point for events
- `evaluate_rules/2` — Match event against rules
- `form_memory/2` — Create memory from event

### Step 4: Wire Up Event Subscription

**Files:** `lib/acme_app/application.ex`

Subscribe FormationLayer to domain events in the supervision tree.

---

## Testing

### Manual Testing
1. Publish a `party_created` event
2. Verify memory is created with correct provenance
3. Disable the rule, publish again, verify no memory

### Automated Tests
- [ ] Unit tests in `test/acme_app/memory/formation_layer_test.exs`
- [ ] Rule evaluation tests
- [ ] Integration test with real events

---

## Verification Checklist

- [ ] Migration runs successfully
- [ ] FormationRule CRUD works
- [ ] Events create memories based on rules
- [ ] Provenance is tracked
- [ ] All tests pass

---

## Notes

- Start with deterministic rules; AI scoring comes in D45
- Log formation decisions for debugging
