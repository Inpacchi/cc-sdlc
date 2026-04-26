# Guarded Rename Rules

## Skill Name References (Guarded Renames)

Driven by `skeleton/contract_changes.yaml`. Read that file from the cc-sdlc source. Select entries with `type: rename_skill` and `id` > the project's `last_applied_contract_id` (stored in `.sdlc-manifest.json`; treat as `"0000"` if absent). Process selected entries in id order; each entry contributes `from → to` pairs to the rename set. If the project's `last_applied_contract_id` is absent, apply the full rename set — this covers projects installed before contract_changes.yaml existed.

For every accumulated rename pair, sweep CLAUDE.md and other project references.

**Guarded rename rule:** Before rewriting any skill reference in the project's CLAUDE.md or other files:
1. Build the project's actual skill inventory: `ls .claude/skills/`
2. Only rewrite if the target skill directory exists in the project
3. If the target doesn't exist (e.g., the project hasn't received the new skill yet), log a warning instead of rewriting:
   ```
   GUARDED RENAME SKIPPED: [old-name] → [new-name] — target directory does not exist in project
   ```
This prevents renaming references to skills that don't exist in the project, which causes silent process failures.

**Chained renames:** If a skill was renamed multiple times (e.g., `diff-review` → `sdlc-review-diff` → `sdlc-review-code`), contract_changes.yaml has a separate entry per hop. Applying entries in id order walks the chain automatically — no special-case logic needed.

**Do NOT hardcode rename pairs in this skill.** Every rename goes in contract_changes.yaml. If you find yourself wanting to add a special case here, add it to the YAML instead.

## Agent Name References in Dispatching Skills (Guarded Renames)

Skills that dispatch subagents (`sdlc-review-code`, `sdlc-review-fix`, `sdlc-execute`, `sdlc-lite-execute`, `sdlc-plan`, `sdlc-lite-plan`) contain agent names in their examples and dispatch logic. If the upstream cc-sdlc uses different agent names than the project (e.g., `frontend-developer` vs `frontend-engineer`), do NOT rename the project's references to match upstream.

**Guarded rename rule for agents:** Before renaming any agent reference in a dispatching skill:
1. Build the project's actual agent inventory: `ls .claude/agents/`
2. Only rename if the target agent file exists in the project
3. If the target doesn't exist, keep the project's original agent name:
   ```
   GUARDED RENAME SKIPPED: [old-agent] → [new-agent] — target agent does not exist in project
   ```

**Why this matters:** Projects customize agent names to match their domain (`frontend-engineer` vs `frontend-developer`, `data-engineer` vs `analytics-engineer`). Renaming references to agents that don't exist causes silent dispatch failures — the skill tries to invoke a nonexistent agent.
