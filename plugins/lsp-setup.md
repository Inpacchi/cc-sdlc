# LSP Setup (Highly Recommended)

Language Server Protocol gives Claude Code type-aware code intelligence — go-to-definition, find-references, hover for type info, and real-time diagnostics. Without LSP, agents rely on Grep and file reads, which miss type relationships, interface implementations, and call hierarchies.

## What LSP Provides

| Capability | Without LSP | With LSP |
|------------|-------------|----------|
| Find function signature | Read the file, search for the function | `hover` — instant type info |
| Find all callers | Grep for the function name (misses renames, aliased imports) | `findReferences` — complete, type-aware |
| Find interface implementations | Grep for class/function name (misses indirect implementations) | `goToImplementation` — all implementations |
| Navigate to source | Glob for filename, then Read | `goToDefinition` — exact location |
| Type errors | Run build command, parse output | Real-time diagnostics as files change |

## Installation

Install the LSP plugin matching your project's primary language(s) via Claude Code:

| Language | Install Command |
|----------|----------------|
| TypeScript / JavaScript | `/plugin install typescript-lsp` |
| Python | `/plugin install pyright-lsp` |
| Go | `/plugin install gopls-lsp` |
| Rust | `/plugin install rust-analyzer-lsp` |
| C / C++ | `/plugin install clangd-lsp` |
| Java | `/plugin install jdtls-lsp` |
| Kotlin | `/plugin install kotlin-lsp` |
| C# | `/plugin install csharp-lsp` |
| Ruby | `/plugin install ruby-lsp` |
| PHP | `/plugin install php-lsp` |
| Swift | `/plugin install swift-lsp` |
| Lua | `/plugin install lua-lsp` |

**Multi-language projects:** Install all relevant LSP plugins. They coexist without conflict.

### Verification

After installation, verify that `LSP` tool calls work:

```
Try: LSP goToDefinition on a function name
Try: LSP hover on a variable
```

## How LSP Is Used in the SDLC

LSP is referenced throughout SDLC skills as the preferred tool for code intelligence:

- **Discovery (sdlc-plan, sdlc-lite-plan):** `goToDefinition`, `findReferences`, `hover` for verifying function signatures, tracing dependencies, and understanding interface contracts during the discovery phase
- **Pattern Reuse Gate (execution skills):** `goToImplementation` for finding existing implementations of interfaces, `findReferences` for tracing hook/utility usage
- **Code Verification Rule:** LSP `hover` for type verification instead of reading files and inferring types
- **Agent dispatch prompts:** Agents with LSP in their tool list can use it for navigating unfamiliar code

### When to Use LSP vs Grep

| Question | Use LSP | Use Grep |
|----------|---------|----------|
| What's the type signature of this function? | `hover` | - |
| Who calls this function? | `findReferences` | - |
| Where is this interface implemented? | `goToImplementation` | - |
| Where is this string literal used? | - | `grep "literal"` |
| Where is this config key referenced? | - | `grep "config_key"` |
| What imports this module? | `findReferences` on the export | Fallback: `grep "from './module'"` |
| Does this type exist? | `goToDefinition` | Fallback: `grep "type TypeName"` |

**Rule of thumb:** LSP for type-system and call-graph questions. Grep for text patterns, string literals, and non-code content (YAML, markdown, config files).
