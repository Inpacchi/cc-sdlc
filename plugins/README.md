# Plugin Dependencies

## Required

| Plugin | What It Does | Skills That Use It |
|--------|-------------|-------------------|
| **context7** | Provides live library/framework documentation lookups via MCP. Prevents use of stale or incorrect API knowledge from training data. | All SDLC skills that touch external dependencies |

**context7 must be installed for accurate external library usage.** Without it, agents will rely on training data for API signatures, parameter names, and default behaviors — which go stale and cause subtle runtime failures.

See `context7-setup.md` for installation instructions.

## Highly Recommended

| Plugin | What It Does | Skills That Use It |
|--------|-------------|-------------------|
| **LSP** (language-specific) | Type-aware code intelligence — go-to-definition, find-references, hover, diagnostics. Replaces Grep-based guesswork with precise type-system navigation. | All planning and execution skills (discovery, pattern reuse, code verification) |

**Install the LSP plugin for your project's primary language(s).** Without it, agents fall back to Grep for code navigation, missing type relationships, interface implementations, and call hierarchies. See `lsp-setup.md` for the full plugin list and installation instructions.

## Optional

| Plugin | What It Does | Skills That Use It |
|--------|-------------|-------------------|
| **oberskills** | Prompt engineering, writing quality, and multi-dimensional web research utilities. | `sdlc-plan` (research phase), ad hoc prompt improvement |
| **design-for-ai** | Enriches design consultations with design theory from *Design for Hackers*. | `design-consult` |

oberskills provides quality enhancements for prompt engineering (`oberprompt`) and web research (`oberweb`) but is not mandatory for agent dispatch.

See `oberskills-setup.md` for installation instructions.

design-for-ai is a quality enhancement — `design-consult` works without it but produces better output with it.

See `design-for-ai-setup.md` for installation instructions.
