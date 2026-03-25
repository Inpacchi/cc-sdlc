#!/usr/bin/env bash
# setup.sh — Install cc-sdlc into a target project
#
# Usage:
#   ./setup.sh [TARGET_DIR]                # Install, skip existing files
#   ./setup.sh [TARGET_DIR] --force        # Overwrite all existing files
#
# For content-aware updates to existing projects, use the sdlc-migrate skill instead.

set -uo pipefail

# ─────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR=""
FORCE=false

for arg in "$@"; do
  case "$arg" in
    --force)         FORCE=true ;;
    --*)
      echo "Unknown flag: $arg" >&2
      echo "Usage: $0 [TARGET_DIR] [--force]" >&2
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
  exit 1
fi

for f in process/overview.md process/deliverable_lifecycle.md templates/spec_template.md README.md; do
  if [ ! -f "$SCRIPT_DIR/$f" ]; then
    echo "Error: cc-sdlc source incomplete. Missing: $f" >&2
    exit 1
  fi
done

# ─────────────────────────────────────────────
# Counters (temp files to survive subshells)
# ─────────────────────────────────────────────

COUNTER_DIR="$(mktemp -d)"
echo 0 > "$COUNTER_DIR/installed"
echo 0 > "$COUNTER_DIR/skipped"
echo 0 > "$COUNTER_DIR/failed"
trap 'rm -rf "$COUNTER_DIR"' EXIT

increment() { echo $(( $(cat "$COUNTER_DIR/$1") + 1 )) > "$COUNTER_DIR/$1"; }
get_counter() { cat "$COUNTER_DIR/$1"; }

# ─────────────────────────────────────────────
# File install logic
# ─────────────────────────────────────────────

install_file() {
  local src="$1" dst="$2"

  mkdir -p "$(dirname "$dst")" 2>/dev/null || { echo "  [ERROR] Cannot create dir for: $dst" >&2; increment failed; return 1; }

  if [ ! -f "$dst" ]; then
    # New file — always install
    cp "$src" "$dst" 2>/dev/null && increment installed || { echo "  [ERROR] Failed: $dst" >&2; increment failed; return 1; }
  elif [ "$FORCE" = "true" ]; then
    # Force mode — overwrite
    cp "$src" "$dst" 2>/dev/null && increment installed || { echo "  [ERROR] Failed: $dst" >&2; increment failed; return 1; }
  else
    # File exists, not force — skip
    increment skipped
  fi
}

install_tree() {
  local src_dir="$1" dst_dir="$2" strip_prefix="${3:-$1}"
  while IFS= read -r src; do
    install_file "$src" "$dst_dir/${src#$strip_prefix/}"
  done < <(find "$src_dir" -type f)
}

# ─────────────────────────────────────────────
# Create directory structure
# ─────────────────────────────────────────────

FORCE_LABEL=""
[ "$FORCE" = "true" ] && FORCE_LABEL=" (force)"
echo "cc-sdlc setup → $TARGET_DIR${FORCE_LABEL}"
echo ""

while IFS= read -r dir; do
  dir="${dir//\"/}"; dir="${dir//,/}"; dir="${dir# }"; dir="${dir% }"
  [ -z "$dir" ] && continue
  [ "$dir" = "_comment" ] && continue
  mkdir -p "$TARGET_DIR/$dir" 2>/dev/null
done < <(python3 -c "
import json
with open('$SCRIPT_DIR/skeleton/manifest.json') as f:
    data = json.load(f)
for d in data.get('directories', []):
    print(d)
" 2>/dev/null || grep -o '"[^"]*"' "$SCRIPT_DIR/skeleton/manifest.json" | \
  grep -v '_comment\|_version\|directories\|seed_files\|deliverable_catalog' | \
  tr -d '"' | grep '/')

# ─────────────────────────────────────────────
# Install content
# ─────────────────────────────────────────────

SDLC_TARGET="$TARGET_DIR/ops/sdlc"

for dir in process templates examples disciplines playbooks; do
  [ -d "$SCRIPT_DIR/$dir" ] && install_tree "$SCRIPT_DIR/$dir" "$SDLC_TARGET/$dir" "$SCRIPT_DIR/$dir"
done

[ -d "$SCRIPT_DIR/knowledge" ] && install_tree "$SCRIPT_DIR/knowledge" "$SDLC_TARGET/knowledge" "$SCRIPT_DIR/knowledge"

# Ensure docs/current_work/audits/ exists (audit output directory)
mkdir -p "$TARGET_DIR/docs/current_work/audits" 2>/dev/null

for f in README.md CLAUDE-SDLC.md; do
  [ -f "$SCRIPT_DIR/$f" ] && install_file "$SCRIPT_DIR/$f" "$SDLC_TARGET/$f"
done

[ -d "$SCRIPT_DIR/skills" ] && install_tree "$SCRIPT_DIR/skills" "$TARGET_DIR/.claude/skills" "$SCRIPT_DIR/skills"
[ -d "$SCRIPT_DIR/agents" ] && install_tree "$SCRIPT_DIR/agents" "$TARGET_DIR/.claude/agents" "$SCRIPT_DIR/agents"

# context7 setup guide is always installed (required dependency)
[ -f "$SCRIPT_DIR/plugins/context7-setup.md" ] && install_file "$SCRIPT_DIR/plugins/context7-setup.md" "$SDLC_TARGET/plugins/context7-setup.md"
# LSP setup guide is always installed (highly recommended)
[ -f "$SCRIPT_DIR/plugins/lsp-setup.md" ] && install_file "$SCRIPT_DIR/plugins/lsp-setup.md" "$SDLC_TARGET/plugins/lsp-setup.md"
# oberskills setup guide is always installed (optional but recommended)
[ -f "$SCRIPT_DIR/plugins/oberskills-setup.md" ] && install_file "$SCRIPT_DIR/plugins/oberskills-setup.md" "$SDLC_TARGET/plugins/oberskills-setup.md"
[ -f "$SCRIPT_DIR/plugins/README.md" ] && install_file "$SCRIPT_DIR/plugins/README.md" "$SDLC_TARGET/plugins/README.md"


# ─────────────────────────────────────────────
# Seed deliverable catalog
# ─────────────────────────────────────────────

INDEX_FILE="$TARGET_DIR/docs/_index.md"
if [ ! -f "$INDEX_FILE" ]; then
  mkdir -p "$TARGET_DIR/docs"
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

# ─────────────────────────────────────────────
# Write manifest
# ─────────────────────────────────────────────

MANIFEST_PATH="$TARGET_DIR/.sdlc-manifest.json"

SOURCE_VERSION="unknown"
SOURCE_REPO="unknown"
if command -v git >/dev/null 2>&1 && [ -d "$SCRIPT_DIR/.git" ]; then
  SOURCE_VERSION="$(git -C "$SCRIPT_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")"
  SOURCE_REPO="$(git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || echo "unknown")"
fi

INSTALL_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)"

FILE_COUNT=0
for d in "$TARGET_DIR/ops/sdlc" "$TARGET_DIR/.claude/skills" "$TARGET_DIR/.claude/agents"; do
  [ -d "$d" ] && FILE_COUNT=$(( FILE_COUNT + $(find "$d" -type f 2>/dev/null | wc -l) ))
done

cat > "$MANIFEST_PATH" << EOF
{
  "_comment": "Generated by cc-sdlc setup.sh. Used by sdlc-migrate skill for version tracking.",
  "version": "1.0.0",
  "source_repo": "${SOURCE_REPO}",
  "source_version": "${SOURCE_VERSION}",
  "install_date": "${INSTALL_DATE}",
  "file_count": ${FILE_COUNT}
}
EOF
echo "  Written: $MANIFEST_PATH"

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────

INSTALLED=$(get_counter installed)
SKIPPED=$(get_counter skipped)
FAILED=$(get_counter failed)

echo ""
echo "─────────────────────────────────────────────"
echo "Setup complete."
echo "  Installed: $INSTALLED"
echo "  Skipped:   $SKIPPED (already exist)"
[ "$FAILED" -gt 0 ] && echo "  Failed:    $FAILED (see errors above)"
echo ""

if [ "$SKIPPED" -gt 50 ] && [ "$INSTALLED" -lt 5 ]; then
  echo "Looks like this project already has SDLC installed."
  echo "To apply framework updates, say in Claude Code:"
  echo "  'Migrate my SDLC framework'"
  echo "  (This invokes the sdlc-migrate skill for content-aware updates)"
else
  echo "Next steps:"
  echo "  1. In Claude Code, say: 'Initialize SDLC in this project'"
  echo "     (This invokes sdlc-initialize, which handles CLAUDE.md, agents, knowledge, and everything else)"
fi
echo "  See ops/sdlc/CLAUDE-SDLC.md for commands and quick reference"

echo ""
echo "IMPORTANT: Install the context7 plugin — it is required for library doc verification."
echo "  See ops/sdlc/plugins/context7-setup.md for instructions."
echo ""
echo "HIGHLY RECOMMENDED: Install the LSP plugin for your project's language(s)."
echo "  See ops/sdlc/plugins/lsp-setup.md for the full list."
echo ""
echo "Optional plugins: oberskills (prompt engineering + web research)."
echo "  See ops/sdlc/plugins/README.md for details."

[ "$FAILED" -gt 0 ] && exit 1
exit 0
