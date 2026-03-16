# Plugin Dependencies

## Required

| Plugin | What It Does | Skills That Use It |
|--------|-------------|-------------------|
| **oberskills** | Validates agent prompts before dispatch. Selects correct `subagent_type` and model tier. Prevents poorly-scoped agent invocations. | All SDLC skills that dispatch agents |

**oberskills must be installed for the SDLC workflow to function correctly.** Without it, agent dispatches may use incorrect agent types (e.g., `general-purpose` instead of `frontend-developer`) and skip prompt quality validation.

See `oberskills-setup.md` for installation instructions.

## Optional

| Plugin | What It Does | Skills That Use It |
|--------|-------------|-------------------|
| **design-for-ai** | Enriches design consultations with design theory from *Design for Hackers*. | `design-consult` |

design-for-ai is a quality enhancement — `design-consult` works without it but produces better output with it.

See `design-for-ai-setup.md` for installation instructions.
