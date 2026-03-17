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

## Which Plugin to Install

Install the LSP plugin matching your project's primary language(s):

| Language | Plugin | Install Command |
|----------|--------|----------------|
| TypeScript / JavaScript | `typescript-lsp` | `npm install -g typescript-language-server typescript` |
| Python | `pyright-lsp` | `npm install -g pyright` or `pip install pyright` |
| Go | `gopls-lsp` | `go install golang.org/x/tools/gopls@latest` |
| Rust | `rust-analyzer-lsp` | Install via rustup or your package manager |
| C / C++ | `clangd-lsp` | Install clangd via your package manager |
| Java | `jdtls-lsp` | Requires Eclipse JDT.LS — see plugin README |
| Kotlin | `kotlin-lsp` | Requires Kotlin Language Server — see plugin README |
| C# | `csharp-lsp` | Requires OmniSharp — see plugin README |
| Ruby | `ruby-lsp` | `gem install ruby-lsp` |
| PHP | `php-lsp` | Requires Intelephense — see plugin README |
| Swift | `swift-lsp` | Requires SourceKit-LSP (bundled with Xcode) |
| Lua | `lua-lsp` | Requires lua-language-server — see plugin README |

**Multi-language projects:** Install all relevant LSP plugins. They coexist without conflict.

### Installation Steps

1. **Install the language server binary** using the install command above
2. **Enable the plugin** in Claude Code: the plugin should be available in your plugin marketplace
3. **Verify** by opening a file in the relevant language and checking that `LSP` tool calls work:
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
