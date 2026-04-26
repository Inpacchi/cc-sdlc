# Recovery / Emergency Restore

If `/sdlc-initialize` crashes, is interrupted, or leaves the workspace in a visibly bad state, this section is how to diagnose and recover.

## Step 1: Diagnose

Check these sources of truth, in order:

**1. Transaction log** (most specific):
```bash
tail -n 100 .sdlc-transaction-log | jq -c '.'
# Find the last `run_start` for sdlc-initialize
# Walk forward: which phases completed (phase_end + result)?
# Where did it stop (last event)? Before or after the point_of_no_return checkpoint?
```

**2. Manifest** (operational-layer truth):
```bash
cat .sdlc-manifest.json 2>/dev/null | jq .
```
- Missing → Phase 1 never completed. Safe to re-run init.
- Present with `source_version` → Phase 1 succeeded; later phases may be partial.
- Present with `installed_files` → drift detection available for next migration.

**3. Filesystem state:**
```bash
ls [sdlc-root]/process/ [sdlc-root]/knowledge/ 2>/dev/null
ls .claude/agents/ .claude/skills/ 2>/dev/null
```
- Populated → Phase 1 file installation ran.
- Agents present → Phase 4 completed for those agents.

## Step 2: Match state to recovery action

| State | Recovery Action |
|-------|-----------------|
| No manifest, no `[sdlc-root]/` | **Full re-run.** `/sdlc-initialize` — workspace is clean. |
| Manifest present, `[sdlc-root]/` incomplete | **Repair mode.** Re-run `/sdlc-initialize`; mode detection identifies this as Repair and reinstalls from Phase 1. |
| Manifest + `[sdlc-root]/` present, no agents | **Resume from Phase 4.** Re-run `/sdlc-initialize`; mode detection identifies "post-skeleton" state. |
| All present but compliance audit failed | **Targeted fix.** The CRITICAL finding identifies what to fix. Apply the fix, then dispatch `sdlc-compliance-auditor` manually. Full re-run is not required. |
| Manifest lacks `installed_files` (pre-drift-detection install) | Next `/sdlc-migrate` will back-fill automatically (see §1.2a of migrate). |

## Step 3: Never do these things

- **Do not delete `[sdlc-root]/` to force a clean retry.** That loses any project customizations and knowledge wiring. Use mode detection + repair instead.
- **Do not delete `.sdlc-manifest.json`.** It tracks version and drift baselines; reconstructing is not trivial.
- **Do not hand-write agent files to skip `/sdlc-create-agent`.** Skipping validation is the fastest way to ship broken agents.

## Step 4: Last resort — reset

Absolute last resort. Requires explicit CD decision.

1. Back up: `git stash` or `cp -r [sdlc-root] [sdlc-root].backup && cp -r .claude .claude.backup`.
2. Re-run `/sdlc-initialize` from scratch.
3. Manually port project customizations back from backup (agent memories, PROJECT-SECTION blocks, discipline parking lot entries).
