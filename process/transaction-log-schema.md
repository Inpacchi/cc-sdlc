# Transaction Log — Schema and Recovery Diagnostics

Every phase start/end, gate decision, mutation, and failure writes an append-only JSONL entry to `.sdlc-transaction-log` in the project root. This enables recovery diagnostics — if a session crashes mid-initialization or mid-migration, the next session can read the log to understand what completed and what didn't.

## Log location and lifecycle

- **Path:** `.sdlc-transaction-log` (project root, gitignored — add to `.gitignore` in Phase 1d)
- **Format:** JSONL — one JSON object per line, newline-terminated, append-only
- **Rotation:** On each new init/migrate run, append a `run_start` marker. Logs accumulate history across runs (not truncated).

## Entry schema

```json
{"ts": "2026-04-21T18:30:00Z", "run_id": "init-abc123", "skill": "sdlc-initialize", "event": "run_start", "details": {"mode": "greenfield-fresh"}}
{"ts": "2026-04-21T18:30:02Z", "run_id": "init-abc123", "skill": "sdlc-initialize", "event": "phase_start", "phase": "0", "details": {"phase_name": "Ideation and Spec"}}
{"ts": "2026-04-21T18:32:00Z", "run_id": "init-abc123", "skill": "sdlc-initialize", "event": "gate", "phase": "0", "gate": "spec_approval", "result": "approved"}
{"ts": "2026-04-21T18:35:42Z", "run_id": "init-abc123", "skill": "sdlc-initialize", "event": "mutation", "phase": "1", "details": {"type": "file_install", "count": 127}}
{"ts": "2026-04-21T18:40:00Z", "run_id": "init-abc123", "skill": "sdlc-initialize", "event": "run_end", "details": {"result": "success", "duration_ms": 600000}}
```

## Required event types

| `event` | When to log | Required `details` |
|---------|-------------|---------------------|
| `run_start` | First action when the skill starts | `mode`, `invocation_args` |
| `phase_start` | Entering a phase | `phase`, `phase_name` |
| `phase_end` | Exiting a phase | `phase`, `duration_ms`, `result` (`pass`/`fail`) |
| `gate` | User confirmation or hard-fail gate | `phase`, `gate` (name), `result` (`approved`/`rejected`/`cancelled`) |
| `mutation` | Any action that changes state (file install, git operation, manifest write) | `phase`, `type`, scope details |
| `checkpoint` | Named milestone, including `point_of_no_return` | `phase`, `name` |
| `warning` | Non-fatal issue | `phase`, `category`, `message`, `location` |
| `failure` | Any error condition | `phase`, `error`, remediation hints |
| `run_end` | Final exit | `result` (`success`/`failure`/`cancelled`), `duration_ms` |

## Run ID generation

`run_id = "{skill-shortname}-{6-char-random-hex}"` — e.g., `init-abc123`, `migrate-def456`. Consistent run_id lets future diagnostics filter all events from a single invocation.

## Reading the log for recovery

If a session ended abnormally:

```bash
tail -n 100 .sdlc-transaction-log | jq -c '.'
# Last `run_start` marks the interrupted run
# Last mutation event = what was last committed
# Last phase_start without matching phase_end = where it crashed
# Presence of `checkpoint: point_of_no_return` tells you whether mutations began
```
