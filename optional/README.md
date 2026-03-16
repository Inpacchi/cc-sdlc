# Optional Plugins

The skills in this SDLC framework reference two optional Claude Code plugins. Both are quality-gate enhancements — the skills work without them, but produce better output with them.

## Plugin Summary

| Plugin | What It Does | Skills That Use It |
|--------|-------------|-------------------|
| **oberskills** | Validates agent prompts before dispatch. Prevents vague or poorly-scoped agent invocations. | `sdlc-planning`, `sdlc-execution`, `ad-hoc-planning`, `ad-hoc-execution`, `test-loop`, `create-test-suite`, `design-consult` |
| **design-for-ai** | Enriches design consultations with design theory from *Design for Hackers*. | `design-consult` |

## How Skills Reference Plugins

Skills annotate plugin dependencies with `[PLUGIN: name]` markers. When you see this in a skill, it means:

- The feature works best with the plugin installed
- Without the plugin, the skill will degrade gracefully and skip that step
- Install the plugin if you want the full behavior

Example:

```
[PLUGIN: oberagent] Before dispatching any agent, invoke oberagent first.
```

## Installation

See the setup guides in this directory:

- `oberskills-setup.md` — Install and configure the oberskills plugin
- `design-for-ai-setup.md` — Install and configure the design-for-ai plugin

Both plugins install via Claude Code's plugin system and are available from their respective repositories.
