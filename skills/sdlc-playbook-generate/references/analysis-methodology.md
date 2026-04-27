# Session Analysis Methodology

Detailed extraction patterns for reading session conversations and git history to produce playbook content. This reference supplements the core workflow in SKILL.md.

## Reading Session JSONL Files

Session files are newline-delimited JSON. Each line is a message with a `type` field.

### Message Types

| Type | Contains | Playbook Value |
|------|----------|---------------|
| `user` (role: user) | User prompts, corrections, feedback | **High** — corrections and "oh wait" moments are gap signals |
| `assistant` | Claude responses, tool calls, reasoning | **High** — reveals process steps, agent dispatches, decisions |
| `user` (toolUseResult) | Tool execution results | **Medium** — shows what succeeded and failed |
| `system` | System messages, hook injections | **Low** — context for understanding the session flow |
| `progress` | Subagent progress updates | **Low** — useful for identifying which agents were involved |
| `file-history-snapshot` | File state snapshots | **Low** — git diff is more reliable for change tracking |

### Extracting User Messages

User messages with `message.role === "user"` contain the actual user prompts. Content may be a string or an array of content blocks (text, images). Focus on text content.

**Filter out system-generated user messages:**
- Messages with `isMeta: true` are system-generated
- Messages with `userType` other than undefined are typically tool results
- Messages starting with `<command-name>` are slash command invocations
- Messages starting with `<local-command-` are local command outputs

### Extracting Assistant Actions

Assistant messages contain `message.content` as an array of content blocks:
- `type: "text"` — Claude's reasoning and communication
- `type: "tool_use"` — Tool calls (Read, Write, Edit, Bash, Agent, etc.)

Tool calls reveal the concrete steps taken:
- `Read` calls show which files were consulted
- `Write`/`Edit` calls show what was created or modified
- `Bash` calls show commands run (installs, migrations, builds, tests)
- `Agent` calls show which domain agents were dispatched and with what prompts

## Process Extraction (Track A)

### Step Sequence Reconstruction

Walk the conversation chronologically and extract an ordered list of actions:

1. **Discovery phase** — What files were read? What patterns were identified? What existing code was leveraged?
2. **Planning/scoping** — Was there an explicit plan? What was the stated approach?
3. **Implementation sequence** — What was built, in what order? Which agents did the work?
4. **Configuration/setup** — What env vars, services, databases, and infrastructure were configured?
5. **Testing/verification** — How was the work verified? What was tested?
6. **Iteration** — How many rounds of feedback and fix occurred?

### Agent Dispatch Patterns

Look for `Agent` tool calls in assistant messages. Extract:
- Which agent types were dispatched
- What context was passed in the dispatch prompt
- Whether the agent succeeded on first attempt or required re-dispatch
- Which agents were most effective for which phases

### Knowledge Context Tracking

Identify knowledge sources consulted during the session:
- Explicit `Read [sdlc-root]/knowledge/<file>.yaml` calls
- Context7 lookups for external library docs
- Codebase pattern reads (existing implementations used as reference)
- Any methodology or process files consulted

### Decision Point Identification

Look for moments where multiple options existed and a choice was made:
- User statements like "let's go with X" or "I prefer Y"
- Assistant presenting options and the user selecting
- Architectural choices (which pattern, which library, which approach)
- Scope decisions (what to include/exclude)

## Gap Extraction (Track B)

### Correction Signals

Scan for these patterns in user messages — each is a potential gotcha:

**Direct corrections:**
- "No, not that" / "That's wrong" / "That's not right"
- "We need to also..." / "Don't forget about..."
- "Actually, it should be..." / "Wait, that's not how..."
- "You missed..." / "What about..."

**Error-recovery sequences:**
- User reports an error → assistant diagnoses → fix applied
- A command fails → troubleshooting → different approach
- A test fails → investigation → correction
- Build/deploy fails → environment issue → config fix

**Mid-stream discoveries:**
- "Oh, we also need to set up X"
- "I forgot to mention, we need Y"
- "That reminds me, Z is also required"
- New requirements surfacing during implementation

**Retry patterns:**
- Same file edited multiple times for the same purpose
- Same command run with different arguments
- Agent re-dispatched with corrected context
- Approach abandoned and restarted

### Environment and Infrastructure Gaps

These are the most common source of playbook gotchas. Look for:

**Environment variables:**
- Env vars added mid-session (not part of initial setup)
- Env vars with incorrect values that were corrected
- Missing env vars that caused runtime errors
- Service-specific env vars (database URLs, API keys, signing secrets)

**Service configuration:**
- Database setup steps (migrations, seeding, connection strings)
- External service registration (webhooks, OAuth apps, bot tokens)
- Deployment platform configuration (Railway, Vercel, etc.)
- DNS or networking setup

**Dependency management:**
- Packages installed mid-session (not part of initial plan)
- Version conflicts or compatibility issues
- Peer dependency warnings that required attention
- Build tool configuration changes

### Ordering Analysis

After extracting all process steps and gap items, determine the corrected ordering:

1. List the steps in the order they actually happened
2. For each gap item, identify where it *should* have happened in the sequence
3. Produce the corrected sequence — this becomes the playbook's "Typical Phases"

Example:
```
ACTUAL ORDER:
1. Scaffold bot handler
2. Implement message handling
3. Deploy to Railway
4. Realize SIGNING_SECRET is missing → add to Railway env
5. Realize database table is missing → run migration
6. Fix webhook URL configuration

CORRECTED ORDER (for playbook):
1. Create database migration and run it
2. Configure Railway env vars (including SIGNING_SECRET)
3. Scaffold bot handler
4. Implement message handling
5. Configure webhook URL
6. Deploy to Railway
7. Verify end-to-end
```

## Git History Analysis

### Commit Correlation

Use the session's timestamp range to extract commits:

```bash
git log --after="<start>" --before="<end>" --format="%H|%ai|%an|%s" --reverse
```

For each commit:
- Read the commit message for intent
- Check `git diff --stat <hash>~1 <hash>` for scope
- For significant commits, read the full diff to understand changes

### Commit Patterns That Signal Gaps

| Pattern | Signal |
|---------|--------|
| Multiple small commits to the same file | Iterative correction — something wasn't right on first pass |
| Commit message contains "fix" after a "feat" | Immediate correction — the feature had a gap |
| Config-only commits (`.env`, `railway.json`, etc.) | Infrastructure setup that was missed initially |
| Reverted or amended commits | Approach correction — the first attempt was wrong |
| Migration commits after implementation commits | Database setup done out of order |

### File Change Frequency

Files modified most frequently during the session are candidates for:
- Reference implementations (the main code produced)
- Gotcha targets (if modified 3+ times, something kept needing correction)
- Configuration hotspots (config files changed repeatedly)

## Playbook Section Mapping

### From Analysis to Template

| Analysis Output | Playbook Section | How to Populate |
|----------------|-----------------|-----------------|
| Step sequence (corrected) | Typical Phases | Group steps into phases, add checkboxes |
| Agent dispatch patterns | Recommended Agents | List agents with roles and required/optional |
| Knowledge files consulted | Knowledge Context | List files with "when to include" conditions |
| Existing code leveraged | Reference Implementations | Link to the files with brief descriptions |
| Decision points | Key Decisions to Surface | Frame as tradeoff questions with options |
| Corrections + errors + discoveries | Common Gotchas | Each with what/why/fix structure |
| Full corrected checklist | Checklist Before Complete | Comprehensive, ordered verification list |

### Gotcha Quality Bar

Each gotcha in the playbook must meet this bar:

**What went wrong:** Specific, concrete description of the failure or gap
**Why it wasn't obvious:** What assumption or missing context led to it
**The fix:** Specific command, config value, or action that resolves it

Example of a **good** gotcha:
> **Missing SLACK_SIGNING_SECRET in Railway** — The bot deploys successfully but webhook verification fails silently. Railway doesn't warn about missing env vars at deploy time. Fix: Add `SLACK_SIGNING_SECRET` to Railway service variables before first deploy. Get the value from Slack app settings → Basic Information → Signing Secret.

Example of a **bad** gotcha:
> **Environment variables may be missing** — Make sure all required environment variables are set.

### Generalization Guidelines

The playbook should work for the *task type*, not just the specific session:

- Replace project-specific names with descriptive placeholders where the name isn't reusable
- Keep technical specifics (env var names, service configurations) — these ARE reusable
- Frame phases generically enough to accommodate variations
- But preserve the ordering insights — "do X before Y" is valuable even when generalized
- Include a "Reference Implementation" section pointing to the specific code from this session

## Multi-Source Sessions

Some sessions span multiple concerns. When the session covers more than one task type:

1. Identify the primary task type (the one the user wants a playbook for)
2. Extract only the steps and gaps relevant to that task type
3. Note cross-cutting concerns (auth, deployment, etc.) as their own section if they're reusable
4. If the user's stated playbook purpose doesn't match the session's primary concern, ask for clarification

## Quality Checklist

Before presenting the draft playbook:

- [ ] Every phase has concrete, actionable steps (not abstract descriptions)
- [ ] Gotchas include what/why/fix structure
- [ ] The corrected ordering reflects where setup should happen, not where it actually happened
- [ ] Agent recommendations come from actual session dispatch patterns, not assumptions
- [ ] Knowledge context lists actual files that were consulted and useful
- [ ] Reference implementations point to real files that exist in the codebase
- [ ] Key decisions are framed as questions with tradeoff options
- [ ] The checklist is comprehensive enough that following it would avoid the session's gaps
