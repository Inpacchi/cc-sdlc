#!/usr/bin/env bash
# setup.sh — Install cc-sdlc into a target project
#
# Usage:
#   ./setup.sh [TARGET_DIR]              # Default mode: install, skip existing files
#   ./setup.sh [TARGET_DIR] --diff       # Show what would change, no writes
#   ./setup.sh [TARGET_DIR] --interactive # Prompt before each file
#   ./setup.sh [TARGET_DIR] --force      # Overwrite all existing files
#   ./setup.sh [TARGET_DIR] --with-optional  # Also install optional/ docs
#
# Requires: bash >= 3.2, shasum (macOS/Linux) or sha256sum (Linux fallback)

set -uo pipefail
# Note: set -e intentionally omitted so the script continues on individual file errors.
# Errors are collected and reported at the end.

# ─────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR=""
MODE="default"          # default | diff | interactive | force
WITH_OPTIONAL=false

for arg in "$@"; do
  case "$arg" in
    --diff)        MODE="diff" ;;
    --interactive) MODE="interactive" ;;
    --force)       MODE="force" ;;
    --with-optional) WITH_OPTIONAL=true ;;
    --*)
      echo "Unknown flag: $arg" >&2
      echo "Usage: $0 [TARGET_DIR] [--diff|--interactive|--force] [--with-optional]" >&2
      exit 1
      ;;
    *)
      if [ -z "$TARGET_DIR" ]; then
        TARGET_DIR="$arg"
      else
        echo "Unexpected argument: $arg" >&2
        exit 1
      fi
      ;;
  esac
done

# Default target: current directory
if [ -z "$TARGET_DIR" ]; then
  TARGET_DIR="$(pwd)"
fi

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

# ─────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: target directory does not exist: $TARGET_DIR" >&2
  exit 1
fi

if [ ! -f "$SCRIPT_DIR/skeleton/manifest.json" ]; then
  echo "Error: manifest.json not found at $SCRIPT_DIR/skeleton/manifest.json" >&2
  echo "Run setup.sh from the cc-sdlc directory, or provide the correct path." >&2
  exit 1
fi

# SHA-256 hash function — works on macOS and Linux
sha256() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    echo "Error: neither shasum nor sha256sum found" >&2
    exit 1
  fi
}

# ─────────────────────────────────────────────
# Source validation: verify cc-sdlc directory looks correct
# ─────────────────────────────────────────────

REQUIRED_SOURCE_FILES=(
  "process/overview.md"
  "process/deliverable_lifecycle.md"
  "templates/spec_template.md"
  "BOOTSTRAP.md"
  "README.md"
)

for f in "${REQUIRED_SOURCE_FILES[@]}"; do
  if [ ! -f "$SCRIPT_DIR/$f" ]; then
    echo "Error: cc-sdlc source appears incomplete. Missing: $SCRIPT_DIR/$f" >&2
    echo "Ensure you are running setup.sh from a complete cc-sdlc installation." >&2
    exit 1
  fi
done

# ─────────────────────────────────────────────
# Counter state — use temp files to survive subshells
# ─────────────────────────────────────────────

COUNTER_DIR="$(mktemp -d)"
echo 0 > "$COUNTER_DIR/installed"
echo 0 > "$COUNTER_DIR/skipped"
echo 0 > "$COUNTER_DIR/updated"
echo 0 > "$COUNTER_DIR/would_change"
echo 0 > "$COUNTER_DIR/failed"
FAILED_FILES=()

# Cleanup temp counters on exit
cleanup_counters() {
  rm -rf "$COUNTER_DIR"
}
trap cleanup_counters EXIT

increment() {
  local name="$1"
  local val
  val=$(cat "$COUNTER_DIR/$name")
  echo $((val + 1)) > "$COUNTER_DIR/$name"
}

get_counter() {
  cat "$COUNTER_DIR/$1"
}

# ─────────────────────────────────────────────
# File install logic
# ─────────────────────────────────────────────

# install_file src dst
# Returns 0 on success, 1 on error (but does not abort the script)
install_file() {
  local src="$1"
  local dst="$2"

  # Ensure parent directory exists
  if ! mkdir -p "$(dirname "$dst")" 2>/dev/null; then
    echo "  [ERROR] Cannot create directory for: $dst" >&2
    increment failed
    FAILED_FILES+=("$dst")
    return 1
  fi

  if [ ! -f "$dst" ]; then
    # File doesn't exist — always install
    case "$MODE" in
      diff)
        echo "[NEW] $dst"
        increment would_change
        ;;
      interactive)
        echo -n "Install new file: $dst? [y/N] "
        read -r answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
          if cp "$src" "$dst" 2>/dev/null; then
            echo "  Installed."
            increment installed
          else
            echo "  [ERROR] Failed to copy: $dst" >&2
            increment failed
            FAILED_FILES+=("$dst")
            return 1
          fi
        else
          echo "  Skipped."
          increment skipped
        fi
        ;;
      *)
        if cp "$src" "$dst" 2>/dev/null; then
          increment installed
        else
          echo "  [ERROR] Failed to copy: $dst" >&2
          increment failed
          FAILED_FILES+=("$dst")
          return 1
        fi
        ;;
    esac
    return 0
  fi

  # File exists — check if content differs
  local src_hash dst_hash
  src_hash="$(sha256 "$src")"
  dst_hash="$(sha256 "$dst")"

  if [ "$src_hash" = "$dst_hash" ]; then
    # Files are identical — skip silently
    increment skipped
    return 0
  fi

  # Files differ — handle based on mode
  case "$MODE" in
    default)
      # Skip existing files that have been modified
      increment skipped
      ;;
    diff)
      echo "[CHANGED] $dst"
      increment would_change
      ;;
    interactive)
      echo "File differs: $dst"
      echo -n "  Overwrite? [y/N] "
      read -r answer
      if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        if cp "$src" "$dst" 2>/dev/null; then
          echo "  Updated."
          increment updated
        else
          echo "  [ERROR] Failed to update: $dst" >&2
          increment failed
          FAILED_FILES+=("$dst")
          return 1
        fi
      else
        echo "  Kept existing."
        increment skipped
      fi
      ;;
    force)
      if cp "$src" "$dst" 2>/dev/null; then
        increment updated
      else
        echo "  [ERROR] Failed to overwrite: $dst" >&2
        increment failed
        FAILED_FILES+=("$dst")
        return 1
      fi
      ;;
  esac
  return 0
}

# ─────────────────────────────────────────────
# install_tree src_dir dst_dir
# Installs all files under src_dir into dst_dir, preserving relative paths.
# Continues on individual file errors.
# ─────────────────────────────────────────────
install_tree() {
  local src_dir="$1"
  local dst_dir="$2"
  local strip_prefix="${3:-$src_dir}"

  while IFS= read -r src; do
    local rel="${src#$strip_prefix/}"
    local dst="$dst_dir/$rel"
    install_file "$src" "$dst"
  done < <(find "$src_dir" -type f)
}

# ─────────────────────────────────────────────
# Create directory structure from manifest
# ─────────────────────────────────────────────

echo "cc-sdlc setup → $TARGET_DIR"
OPTIONAL_LABEL=""
[ "$WITH_OPTIONAL" = "true" ] && OPTIONAL_LABEL=" +optional"
echo "Mode: $MODE${OPTIONAL_LABEL}"
echo ""

# Read directories from manifest.json (simple grep — no jq required)
while IFS= read -r dir; do
  # Strip quotes and trailing comma/whitespace
  dir="${dir//\"/}"
  dir="${dir//,/}"
  dir="${dir# }"
  dir="${dir% }"
  [ -z "$dir" ] && continue
  [ "$dir" = "_comment" ] && continue

  full_path="$TARGET_DIR/$dir"
  if [ ! -d "$full_path" ]; then
    if [ "$MODE" = "diff" ]; then
      echo "[DIR] $dir"
    else
      mkdir -p "$full_path" 2>/dev/null || echo "  [WARN] Could not create directory: $dir" >&2
    fi
  fi
done < <(python3 -c "
import json, sys
with open('$SCRIPT_DIR/skeleton/manifest.json') as f:
    data = json.load(f)
for d in data.get('directories', []):
    print(d)
" 2>/dev/null || grep -o '"[^"]*"' "$SCRIPT_DIR/skeleton/manifest.json" | \
  grep -v '_comment\|_version\|directories\|seed_files\|deliverable_catalog' | \
  tr -d '"' | grep '/')

# ─────────────────────────────────────────────
# Install ops/sdlc/ content
# ─────────────────────────────────────────────

SDLC_TARGET="$TARGET_DIR/ops/sdlc"

# Process docs
for dir in process templates examples disciplines playbooks improvement-ideas; do
  if [ -d "$SCRIPT_DIR/$dir" ]; then
    install_tree "$SCRIPT_DIR/$dir" "$SDLC_TARGET/$dir" "$SCRIPT_DIR/$dir"
  fi
done

# Knowledge directory
if [ -d "$SCRIPT_DIR/knowledge" ]; then
  install_tree "$SCRIPT_DIR/knowledge" "$SDLC_TARGET/knowledge" "$SCRIPT_DIR/knowledge"
fi

# Top-level sdlc files (README, BOOTSTRAP, initial-prompt, CLAUDE-SDLC)
for f in README.md BOOTSTRAP.md initial-prompt.md CLAUDE-SDLC.md; do
  if [ -f "$SCRIPT_DIR/$f" ]; then
    install_file "$SCRIPT_DIR/$f" "$SDLC_TARGET/$f"
  fi
done

# ─────────────────────────────────────────────
# Install .claude/skills/
# ─────────────────────────────────────────────

if [ -d "$SCRIPT_DIR/skills" ]; then
  SKILLS_TARGET="$TARGET_DIR/.claude/skills"
  install_tree "$SCRIPT_DIR/skills" "$SKILLS_TARGET" "$SCRIPT_DIR/skills"
fi

# ─────────────────────────────────────────────
# Install .claude/agents/
# ─────────────────────────────────────────────

if [ -d "$SCRIPT_DIR/agents" ]; then
  AGENTS_TARGET="$TARGET_DIR/.claude/agents"
  install_tree "$SCRIPT_DIR/agents" "$AGENTS_TARGET" "$SCRIPT_DIR/agents"
fi

# ─────────────────────────────────────────────
# Optional: install optional/ docs
# ─────────────────────────────────────────────

if [ "$WITH_OPTIONAL" = "true" ] && [ -d "$SCRIPT_DIR/optional" ]; then
  OPTIONAL_TARGET="$TARGET_DIR/ops/sdlc/optional"
  install_tree "$SCRIPT_DIR/optional" "$OPTIONAL_TARGET" "$SCRIPT_DIR/optional"
fi

# ─────────────────────────────────────────────
# Create seed files
# ─────────────────────────────────────────────

# docs/_index.md — deliverable catalog
INDEX_FILE="$TARGET_DIR/docs/_index.md"
if [ ! -f "$INDEX_FILE" ]; then
  if [ "$MODE" = "diff" ]; then
    echo "[NEW] docs/_index.md"
    increment would_change
  elif [ "$MODE" = "interactive" ]; then
    echo -n "Create deliverable catalog at docs/_index.md? [Y/n] "
    read -r answer
    if [ "$answer" != "n" ] && [ "$answer" != "N" ]; then
      cat > "$INDEX_FILE" << 'CATALOG'
# Project Deliverable Catalog

This is the single source of truth for all deliverable IDs and their statuses.

## Active Deliverables

| ID | Name | Status | Spec | Plan | Result |
|----|------|--------|------|------|--------|

## Completed Deliverables

| ID | Name | Chronicle Location |
|----|------|-------------------|

## Notes

- IDs are sequential and never reused (D1, D2, ... Dnn)
- Sub-deliverables use letter suffixes: D1a, D1b
- Status: Draft | Ready | In Progress | Validated | Deployed | Complete | Archived
CATALOG
      increment installed
    fi
  else
    cat > "$INDEX_FILE" << 'CATALOG'
# Project Deliverable Catalog

This is the single source of truth for all deliverable IDs and their statuses.

## Active Deliverables

| ID | Name | Status | Spec | Plan | Result |
|----|------|--------|------|------|--------|

## Completed Deliverables

| ID | Name | Chronicle Location |
|----|------|-------------------|

## Notes

- IDs are sequential and never reused (D1, D2, ... Dnn)
- Sub-deliverables use letter suffixes: D1a, D1b
- Status: Draft | Ready | In Progress | Validated | Deployed | Complete | Archived
CATALOG
    increment installed
  fi
fi

# ─────────────────────────────────────────────
# Generate .sdlc-manifest.json in target directory
# ─────────────────────────────────────────────

generate_manifest() {
  local target="$1"
  local manifest_path="$target/.sdlc-manifest.json"
  local sdlc_dir="$target/ops/sdlc"
  local skills_dir="$target/.claude/skills"
  local agents_dir="$target/.claude/agents"

  # Determine source version (git commit hash if available)
  local source_version="unknown"
  if command -v git >/dev/null 2>&1 && [ -d "$SCRIPT_DIR/.git" ]; then
    source_version="$(git -C "$SCRIPT_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")"
  fi

  local install_date
  install_date="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)"

  # Build JSON — collect file hashes
  local files_json=""
  local first=true

  # Scan all installed files under ops/sdlc, .claude/skills, .claude/agents
  while IFS= read -r filepath; do
    local rel="${filepath#$target/}"
    local hash
    hash="$(sha256 "$filepath" 2>/dev/null || echo "error")"
    if [ "$first" = "true" ]; then
      first=false
    else
      files_json="${files_json},"
    fi
    # Escape backslashes and quotes in rel path (unlikely but safe)
    rel="${rel//\\/\\\\}"
    rel="${rel//\"/\\\"}"
    files_json="${files_json}
      \"${rel}\": \"${hash}\""
  done < <(
    { [ -d "$sdlc_dir" ] && find "$sdlc_dir" -type f; } 2>/dev/null
    { [ -d "$skills_dir" ] && find "$skills_dir" -type f; } 2>/dev/null
    { [ -d "$agents_dir" ] && find "$agents_dir" -type f; } 2>/dev/null
  )

  # Write manifest
  cat > "$manifest_path" << MANIFEST_EOF
{
  "_comment": "Generated by cc-sdlc setup.sh. Do not edit manually.",
  "version": "1.0.0",
  "install_date": "${install_date}",
  "source_version": "${source_version}",
  "files": {${files_json}
  }
}
MANIFEST_EOF

  echo "  Written: $manifest_path"
}

if [ "$MODE" != "diff" ]; then
  generate_manifest "$TARGET_DIR"
fi

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────

INSTALLED=$(get_counter installed)
UPDATED=$(get_counter updated)
SKIPPED=$(get_counter skipped)
WOULD_CHANGE=$(get_counter would_change)
FAILED=$(get_counter failed)

echo ""
if [ "$MODE" = "diff" ]; then
  echo "─────────────────────────────────────────────"
  echo "Diff complete. $WOULD_CHANGE file(s) would change."
  echo "Run without --diff to apply, or use --interactive to review each change."
else
  echo "─────────────────────────────────────────────"
  echo "Setup complete."
  echo "  Installed: $INSTALLED"
  echo "  Updated:   $UPDATED"
  echo "  Skipped:   $SKIPPED (already up to date or user-modified)"
  if [ "$FAILED" -gt 0 ]; then
    echo "  Failed:    $FAILED (see errors above)"
  fi
  echo ""
  echo "Next steps:"
  echo "  1. Add ops/sdlc/CLAUDE-SDLC.md content to your project's CLAUDE.md"
  echo "  2. Review ops/sdlc/process/overview.md for the full workflow"
  echo "  3. Start work: 'Let's implement the SDLC process' in Claude Code"
  if [ "$WITH_OPTIONAL" = "false" ]; then
    echo ""
    echo "Optional plugins: run with --with-optional to install setup guides,"
    echo "  or see optional/ in the cc-sdlc source directory."
  fi
fi

# Exit with error code if any files failed
if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
