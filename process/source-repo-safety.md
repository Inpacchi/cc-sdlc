# Source Repo Safety

## Source Repo Access Rule

**All reads from the cc-sdlc source repo MUST use git commands**, not filesystem reads. This ensures you're reading committed state, not the working tree.

- Read a file: `git -C [cc-sdlc-path] show HEAD:<path>`
- List files: `git -C [cc-sdlc-path] ls-tree -r --name-only HEAD`
- Diff since version: `git -C [cc-sdlc-path] diff [source_version]..HEAD`

Never use `cat`, `cp`, `ls`, or direct file reads against `[cc-sdlc-path]`. The source repo may have uncommitted work in progress.

## Safe File Extraction (CRITICAL)

**Never use direct shell redirection** to extract files: `git show HEAD:<path> > file` is UNSAFE because shell redirection truncates the target file *before* `git show` runs. If `git show` fails for any reason (path doesn't exist, clone was cleaned up, permission error), the target file is left empty — destroying the project's content.

**Safe pattern — verify before overwriting:**
```bash
# Extract to temp, verify content exists, then move
CONTENT=$(git -C [cc-sdlc-path] show HEAD:<path> 2>/dev/null) || {
  echo "ERROR: git show failed for <path> — file NOT overwritten"
  return 1  # or continue to next file
}
if [ -z "$CONTENT" ]; then
  echo "ERROR: <path> has empty content in source — file NOT overwritten"
  return 1
fi
echo "$CONTENT" > [project-path]/[target]
```

**Alternative — use git archive for batch extraction:**
```bash
# Extract specific files to a temp directory, then move
git -C [cc-sdlc-path] archive HEAD:<dir> | tar -x -C /tmp/extract/
# Verify each file before copying to project
```

**Why this matters:** During migration, a single silent `git show` failure can destroy dozens of project files. A 2026-04-15 bug emptied 8 knowledge READMEs because `git show` produced no output after the temp clone was cleaned up — the shell redirect created empty files over the project's content.
