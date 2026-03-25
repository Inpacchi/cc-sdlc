# setup.ps1 — Install cc-sdlc into a target project (Windows)
#
# Usage:
#   .\setup.ps1 [TARGET_DIR]                # Install, skip existing files
#   .\setup.ps1 [TARGET_DIR] -Force         # Overwrite all existing files
#
# For content-aware updates to existing projects, use MIGRATE.md instead.

param(
    [string]$TargetDir,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────
# Resolve paths
# ─────────────────────────────────────────────

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

if (-not $TargetDir) {
    $TargetDir = Get-Location
}

$TargetDir = (Resolve-Path $TargetDir).Path

# ─────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────

if (-not (Test-Path $TargetDir -PathType Container)) {
    Write-Error "Error: target directory does not exist: $TargetDir"
    exit 1
}

if (-not (Test-Path "$ScriptDir\skeleton\manifest.json")) {
    Write-Error "Error: manifest.json not found at $ScriptDir\skeleton\manifest.json"
    exit 1
}

$requiredFiles = @(
    "process\overview.md",
    "process\deliverable_lifecycle.md",
    "templates\spec_template.md",
    "BOOTSTRAP.md",
    "README.md"
)

foreach ($f in $requiredFiles) {
    if (-not (Test-Path "$ScriptDir\$f")) {
        Write-Error "Error: cc-sdlc source incomplete. Missing: $f"
        exit 1
    }
}

# ─────────────────────────────────────────────
# Counters
# ─────────────────────────────────────────────

$script:Installed = 0
$script:Skipped = 0
$script:Failed = 0

# ─────────────────────────────────────────────
# File install logic
# ─────────────────────────────────────────────

function Install-SdlcFile {
    param([string]$Src, [string]$Dst)

    $dstDir = Split-Path -Parent $Dst
    if (-not (Test-Path $dstDir)) {
        try { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
        catch {
            Write-Host "  [ERROR] Cannot create dir for: $Dst" -ForegroundColor Red
            $script:Failed++
            return
        }
    }

    if (-not (Test-Path $Dst)) {
        # New file — always install
        try {
            Copy-Item $Src $Dst -Force
            $script:Installed++
        } catch {
            Write-Host "  [ERROR] Failed: $Dst" -ForegroundColor Red
            $script:Failed++
        }
    } elseif ($Force) {
        # Force mode — overwrite
        try {
            Copy-Item $Src $Dst -Force
            $script:Installed++
        } catch {
            Write-Host "  [ERROR] Failed: $Dst" -ForegroundColor Red
            $script:Failed++
        }
    } else {
        # File exists, not force — skip
        $script:Skipped++
    }
}

function Install-SdlcTree {
    param([string]$SrcDir, [string]$DstDir, [string]$StripPrefix)

    if (-not $StripPrefix) { $StripPrefix = $SrcDir }

    Get-ChildItem -Path $SrcDir -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($StripPrefix.Length).TrimStart('\', '/')
        Install-SdlcFile $_.FullName "$DstDir\$relativePath"
    }
}

# ─────────────────────────────────────────────
# Create directory structure
# ─────────────────────────────────────────────

$forceLabel = if ($Force) { " (force)" } else { "" }
Write-Host "cc-sdlc setup -> $TargetDir$forceLabel"
Write-Host ""

try {
    $manifest = Get-Content "$ScriptDir\skeleton\manifest.json" -Raw | ConvertFrom-Json
    foreach ($dir in $manifest.directories) {
        $fullPath = Join-Path $TargetDir $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
    }
} catch {
    # Fallback: parse JSON manually
    $lines = Get-Content "$ScriptDir\skeleton\manifest.json"
    foreach ($line in $lines) {
        if ($line -match '"([^"]+/[^"]+)"') {
            $dir = $Matches[1]
            if ($dir -notmatch '_comment|_version|directories|seed_files|deliverable_catalog') {
                $fullPath = Join-Path $TargetDir $dir
                if (-not (Test-Path $fullPath)) {
                    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
                }
            }
        }
    }
}

# ─────────────────────────────────────────────
# Install content
# ─────────────────────────────────────────────

$sdlcTarget = Join-Path $TargetDir "ops\sdlc"

$contentDirs = @("process", "templates", "examples", "disciplines", "playbooks")
foreach ($dir in $contentDirs) {
    $srcPath = Join-Path $ScriptDir $dir
    if (Test-Path $srcPath -PathType Container) {
        Install-SdlcTree $srcPath "$sdlcTarget\$dir" $srcPath
    }
}

$knowledgePath = Join-Path $ScriptDir "knowledge"
if (Test-Path $knowledgePath -PathType Container) {
    Install-SdlcTree $knowledgePath "$sdlcTarget\knowledge" $knowledgePath
}

$topLevelFiles = @("README.md", "BOOTSTRAP.md", "MIGRATE.md", "CLAUDE-SDLC.md")
foreach ($f in $topLevelFiles) {
    $srcPath = Join-Path $ScriptDir $f
    if (Test-Path $srcPath) {
        Install-SdlcFile $srcPath "$sdlcTarget\$f"
    }
}

$skillsPath = Join-Path $ScriptDir "skills"
if (Test-Path $skillsPath -PathType Container) {
    Install-SdlcTree $skillsPath "$TargetDir\.claude\skills" $skillsPath
}

$agentsPath = Join-Path $ScriptDir "agents"
if (Test-Path $agentsPath -PathType Container) {
    Install-SdlcTree $agentsPath "$TargetDir\.claude\agents" $agentsPath
}

# context7 setup guide is always installed (required dependency)
$ctx7 = Join-Path $ScriptDir "plugins\context7-setup.md"
if (Test-Path $ctx7) { Install-SdlcFile $ctx7 "$sdlcTarget\plugins\context7-setup.md" }

# LSP setup guide is always installed (highly recommended)
$lsp = Join-Path $ScriptDir "plugins\lsp-setup.md"
if (Test-Path $lsp) { Install-SdlcFile $lsp "$sdlcTarget\plugins\lsp-setup.md" }

$pluginsReadme = Join-Path $ScriptDir "plugins\README.md"
if (Test-Path $pluginsReadme) { Install-SdlcFile $pluginsReadme "$sdlcTarget\plugins\README.md" }


# ─────────────────────────────────────────────
# Seed deliverable catalog
# ─────────────────────────────────────────────

$indexFile = Join-Path $TargetDir "docs\_index.md"
if (-not (Test-Path $indexFile)) {
    $docsDir = Join-Path $TargetDir "docs"
    if (-not (Test-Path $docsDir)) { New-Item -ItemType Directory -Path $docsDir -Force | Out-Null }

    @"
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
"@ | Set-Content -Path $indexFile -Encoding UTF8
    $script:Installed++
}

# ─────────────────────────────────────────────
# Write manifest
# ─────────────────────────────────────────────

$manifestPath = Join-Path $TargetDir ".sdlc-manifest.json"

$sourceVersion = "unknown"
try {
    if (Test-Path "$ScriptDir\.git") {
        $sourceVersion = (git -C $ScriptDir rev-parse HEAD 2>$null)
        if (-not $sourceVersion) { $sourceVersion = "unknown" }
    }
} catch { $sourceVersion = "unknown" }

$installDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$fileCount = 0
@("$TargetDir\ops\sdlc", "$TargetDir\.claude\skills", "$TargetDir\.claude\agents") | ForEach-Object {
    if (Test-Path $_) {
        $fileCount += (Get-ChildItem -Path $_ -Recurse -File).Count
    }
}

@"
{
  "_comment": "Generated by cc-sdlc setup.ps1. Used by MIGRATE.md for version tracking.",
  "version": "1.0.0",
  "source_version": "$sourceVersion",
  "install_date": "$installDate",
  "file_count": $fileCount
}
"@ | Set-Content -Path $manifestPath -Encoding UTF8
Write-Host "  Written: $manifestPath"

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────

Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Setup complete."
Write-Host "  Installed: $($script:Installed)"
Write-Host "  Skipped:   $($script:Skipped) (already exist)"
if ($script:Failed -gt 0) { Write-Host "  Failed:    $($script:Failed) (see errors above)" -ForegroundColor Red }
Write-Host ""

if ($script:Skipped -gt 50 -and $script:Installed -lt 5) {
    Write-Host "Looks like this project already has SDLC installed."
    Write-Host "To apply framework updates, say in Claude Code:"
    Write-Host "  'Migrate my SDLC framework to the latest cc-sdlc version'"
    Write-Host "  (This triggers the content-aware migration in ops/sdlc/MIGRATE.md)"
} else {
    Write-Host "Next steps:"
    Write-Host "  1. In Claude Code, say: 'Initialize SDLC in this project'"
    Write-Host "     (This invokes sdlc-initialize, which handles CLAUDE.md, agents, knowledge, and everything else)"
}
Write-Host "  See CLAUDE-SDLC.md for commands and quick reference"

Write-Host ""
Write-Host "IMPORTANT: Install the context7 plugin -- it is required for library doc verification."
Write-Host "  See ops/sdlc/plugins/context7-setup.md for instructions."
Write-Host ""
Write-Host "HIGHLY RECOMMENDED: Install the LSP plugin for your project's language(s)."
Write-Host "  See ops/sdlc/plugins/lsp-setup.md for the full list."
Write-Host ""
if ($script:Failed -gt 0) { exit 1 }
exit 0
