# Red Flags

| Thought | Reality |
|---------|---------|
| "I'll skip ideation and go straight to scaffolding" | Agents and knowledge seeded without stack context are generic and unhelpful. Define the project first. |
| "I should dispatch an agent for the spec" | No agents exist yet in greenfield. CC writes the spec directly. This is the one exception to the Manager Rule. |
| "The user described the project, I have enough to create agents" | You have enough to create agents when you have an approved spec with tech stack and repo structure. Not before. |
| "I'll write the agent files directly — the skill is slow" | `/sdlc-create-agent` validates frontmatter, descriptions, and template compliance. Hand-written agents skip these gates. |
| "The context map ships with reasonable defaults" | The defaults use generic role names. If they don't match your agent filenames, self-discovery is broken. |
| "Disciplines can be seeded later" | A few bullets now costs 2 minutes; discovering the gap mid-execution costs a review round. |
| "Context7 is optional for now" | Without it, agents will hallucinate library APIs from training data. Install it before any agent work begins. |
| "I'll overwrite their existing CLAUDE.md with a fresh one" | In retrofit mode, ALWAYS augment. Existing project instructions are authoritative. |
| "The project only needs 2 agents" | `software-architect` and `code-reviewer` are mandatory — that's already 2. Add at least one implementer. The minimum viable set is 3+. |
| "We don't need a software-architect or code-reviewer for a small project" | Both are mandatory. The architect mediates debate, reviews plans, and seeds knowledge. The code-reviewer is unconditionally dispatched by every review skill. Without them, review and planning skills are broken. |
| "The agents are created, we're done with Phase 4" | Verify dispatcher wiring (4e). An agent that isn't in the selection tables won't be dispatched by review or planning skills. |
| "I'll seed knowledge from training data" | Verify all library/framework claims via Context7 before writing knowledge files. Training data goes stale. |
| "Installation failed, I'll create the directories manually" | Fix the installation failure. Manual creation misses files and skips version tracking. |
| "Manager Rule applies from the start" | In greenfield Phases 0–3, no agents exist. CC works directly. Manager Rule activates at Phase 4. |
| "I'll batch all the ideation questions" | One question at a time via AskUserQuestion. Batched questions get shallow answers. |
| "I'll implement adapter-specific behavior inside this skill" | Adapter phase logic lives in the adapter's handler doc (see `[sdlc-root]/process/adapter-lifecycle-protocol.md`). This skill handles discovery and phase delegation — it does not implement adapter behavior directly. |
