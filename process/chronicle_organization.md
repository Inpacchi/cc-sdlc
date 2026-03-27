# Chronicle Organization

## Purpose

Chronicles serve as **long-term memory** for the project. When starting a new session or returning to a feature area, concept chronicles provide:

- Historical context for decisions
- Patterns that worked (or didn't)
- Dependencies between features
- Quick orientation via `_index.md`

---

## Structure

### Chronicle Structure (`docs/chronicle/`)

Organized by concept — the domain or feature area.

```
chronicle/
├── authentication/
│   ├── _index.md        ← Navigation hub
│   ├── specs/
│   ├── planning/
│   ├── results/
│   └── ideas/           ← Archived idea briefs (optional)
└── data_model/
    └── ...
```

Chronological ordering is handled by the deliverable catalog (`docs/_index.md`) and git history — no separate timeline archive is needed.

---

## The `_index.md` Pattern

Every concept must have `_index.md` containing:

```markdown
# NN_concept_name

## Overview
What this concept covers.

## Deliverables
| File | Purpose | Dependencies |
|------|---------|--------------|

## Common Tasks
- "Do X" → file_a.md
- "Do Y" → file_b.md

## Key Decisions
- Decision and rationale
```

**Purpose:** Enables surgical context loading — read index first, then only relevant files.

---

## Principles

### 1. Centralize Related Content

If asked to "work on X," all relevant docs should be in one concept.

**Test:** "Where would I look to understand this feature?" → One concept.

### 2. Extend vs. Create New

**Extend existing** when:
- New work builds on existing foundation
- Understanding new requires understanding old
- Combined size is manageable (<20 files)

**Create new** when:
- Genuinely new domain
- Dependencies are loose
- Existing would become unwieldy

### 3. Exclude Non-Deliverables

**Don't chronicle:**
- BLOCKED results (incomplete)
- paused/ directories
- Active roadmaps/reference docs
- Experimental/customer-specific work

**Do chronicle:**
- Completed specs with COMPLETE results
- Planning documents
- Architectural decisions
- Idea briefs that graduated to deliverables or were abandoned (archived to `ideas/` subdirectory)

---

## Process

### 1. Inventory
```bash
ls current_work/specs/
ls current_work/results/
```

### 2. Categorize

| Deliverable | Concept | Action |
|-------------|---------|--------|
| D42 | 01_memory | Extend |
| D50 | 03_events | Extend |
| D51 | NEW: 12_api | Create |

### 3. Create Structure
```bash
mkdir -p chronicle/concept_name/{specs,planning,results}
```

### 4. Write Index Files

Create `_index.md` **before** copying files.

### 5. Copy Files
```bash
cp current_work/specs/dNN_*.md chronicle/XX/specs/
```

### 6. Verify
```bash
ls chronicle/XX/specs/ | wc -l
```

### 7. Clean Up

Remove chronicled files from `current_work/`.

### 8. Commit
```bash
git commit -m "docs: organize DXX-DYY into chronicles"
```

---

## When to Organize

- Logical milestone reached
- `current_work/` cluttered (>20 items)
- Starting new project phase
- Context refresh needed

---

## Checklist

- [ ] Inventory current_work contents
- [ ] Categorize each deliverable
- [ ] Create new directories if needed
- [ ] Write _index.md for each concept
- [ ] Copy files (verify before cleanup)
- [ ] Clean up current_work
- [ ] Commit with descriptive message
