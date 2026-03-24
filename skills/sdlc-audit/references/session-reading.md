# Session Reading Reference

How to locate and read Claude Code session JSONL files for audit analysis.

## Session File Location

Session conversations are stored as JSONL files:

```
~/.claude/projects/<project-dir-hash>/<session-id>.jsonl
```

The project directory hash is derived from the absolute path (e.g., `-Users-yovarniyearwood-Projects-myproject`). Each session produces one JSONL file named by its UUID.

Some sessions also have a companion directory (`<session-id>/`) containing subagent data.

## Locating a Session

**By session ID:** Direct file lookup.

**By name or search term:** Scan JSONL files, read early user messages for matching content. Present candidates with timestamps and first user message for disambiguation.

**By timestamp range:** Use file modification times or first/last message timestamps to find sessions overlapping a given time range.

**Extracting session time range:** Walk the JSONL, capture the first and last `timestamp` field. Timestamps are ISO 8601 strings (e.g., `2026-03-17T16:20:00.123Z`).

## Message Types

Each JSONL line is a JSON object with a `type` field:

| Type | Contains | Audit Value |
|------|----------|-------------|
| `user` (role: user) | User prompts, corrections, feedback | **High** — corrections and friction signals |
| `assistant` | Claude responses, tool calls | **High** — reveals actions taken, skills invoked, decisions |
| `user` (toolUseResult) | Tool execution results | **Medium** — shows what succeeded and failed |
| `system` | System messages, hook injections | **Low** — context for session flow |
| `progress` | Subagent progress | **Low** — identifies which agents were dispatched |
| `file-history-snapshot` | File state snapshots | **Low** — git diff is more reliable |

## Extracting User Messages

User messages with `message.role === "user"` contain actual prompts. Content may be a string or array of content blocks.

**Filter out system-generated messages:**
- `isMeta: true` — system-generated
- `userType` present — typically tool results
- Content starting with `<command-name>` — slash command invocations
- Content starting with `<local-command-` — local command outputs

## Extracting Assistant Actions

Assistant `message.content` is an array of content blocks:
- `type: "text"` — reasoning and communication
- `type: "tool_use"` — tool calls with `name` and `input` fields

Tool calls reveal concrete actions:
- `Read` → files consulted
- `Write`/`Edit` → files created/modified
- `Bash` → commands run (installs, migrations, builds)
- `Agent` → domain agents dispatched (extract `prompt` from input for context)
- `Skill` → skills invoked (extract `skill` name)

## Correlating with Git History

Use the session's timestamp range to find commits:

```bash
git log --after="<start>" --before="<end>" --format="%H|%ai|%s" --reverse
```

For each commit, `git diff --stat <hash>~1 <hash>` shows scope. Full diffs for significant commits reveal detail.

## Correction Signals in User Messages

These patterns indicate friction — something went wrong or was missed:

- **Direct corrections:** "No, not that" / "That's wrong" / "Actually, it should be..."
- **Additions:** "We also need to..." / "Don't forget about..." / "What about..."
- **Error reports:** User describes a failure, error message, or unexpected behavior
- **Redirections:** "Stop" / "Let's try a different approach" / "Go back to..."
- **Process bypass:** "Just do it" / "Skip the plan" / "We don't need a spec for this"
