# Getting Started with SDLC

## For New Projects

After running `setup.sh`, copy and paste this prompt to Claude Code:

```
I'd like to bootstrap the SDLC process in this project.

Please:
1. Read ops/sdlc/BOOTSTRAP.md for instructions
2. Analyze my existing documentation
3. Propose a structure and categorization
4. Wait for my approval before creating anything
```

---

## Migrating to Latest Framework

After updating cc-sdlc and running `setup.sh` again, use this prompt to apply framework changes without losing project customizations:

```
Migrate my SDLC framework to the latest cc-sdlc version.

Please:
1. Read ops/sdlc/MIGRATE.md for instructions
2. Check .sdlc-manifest.json for the previous source version
3. Diff the cc-sdlc changes since that version
4. Apply framework updates while preserving project customizations
5. Show me a summary of what changed before committing
```

---

## For Existing Projects (with docs already organized)

```
This project uses the SDLC process.

Please read:
- ops/sdlc/process/overview.md for workflow
- ./CLAUDE.md for project-specific context
- ./docs/current_work/ for active deliverables
```

---

## Quick Reference

| Task | What to Say |
|------|-------------|
| Start new deliverable | "Let's create a spec for D[next number]: [feature name]" |
| Implement a spec | "Please implement D42 following the planning doc" |
| Archive completed work | "Let's organize the chronicles" |
| **Reconcile ad hoc work** | **"Let's catalog our ad hoc work"** |
| **Audit compliance** | **"Let's run an SDLC compliance audit"** |
| **Create a new agent** | **Use `/plugin-dev:agent-development`** |
| **Migrate framework** | **"Migrate my SDLC framework to the latest cc-sdlc version"** |
| Check process | "What's our SDLC workflow?" |

---

## After Ad Hoc Work

Been doing quick fixes without formal specs? That's fine. When ready to reconcile:

```
Let's catalog our ad hoc work.

Please:
1. Read ops/sdlc/process/ad_hoc_reconciliation.md
2. Review commits since last formal deliverable
3. Propose how to document what we've done
4. Help me update any specs that need it
```

---

## Files CC Should Know About

| File | Purpose |
|------|---------|
| `ops/sdlc/BOOTSTRAP.md` | How to initialize a project |
| `ops/sdlc/MIGRATE.md` | How to update an existing project to latest framework |
| `ops/sdlc/process/overview.md` | The workflow |
| `ops/sdlc/process/ad_hoc_reconciliation.md` | Rejoining process after ad hoc work |
| `ops/sdlc/templates/` | Document templates |
| `agents/AGENT_TEMPLATE.md` | Agent structure reference |
| `agents/AGENT_SUGGESTIONS.md` | Recommended agent roles by project type |
| `./CLAUDE.md` | Project-specific context |
| `./docs/current_work/` | Active deliverables |
