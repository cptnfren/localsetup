<#
.SYNOPSIS
    Deploy Localsetup v2 into a client repo at _localsetup/ and write platform-specific context and skills.

.DESCRIPTION
    Clones or updates the Localsetup v2 repo into the target directory, then runs deploy to write
    context loaders and skills for the selected tools (Cursor, Claude Code, Codex, OpenClaw).

.PARAMETER Directory
    Client repo root path. Default: current directory (interactive) or . (with -Yes).

.PARAMETER Tools
    Comma-separated list: cursor, claude-code, codex, openclaw. Required when using -Yes.

.PARAMETER Yes
    Non-interactive mode. Requires -Tools. No prompts.

.PARAMETER Help
    Display this help and exit. Also: -? or -h.

.EXAMPLE
    .\install.ps1 -Directory . -Tools cursor -Yes
.EXAMPLE
    .\install.ps1 -Help
#>
param(
    [string]$Directory = '',
    [string]$Tools = '',
    [switch]$Yes,
    [switch]$Help
)

# Support Bash-style --directory/--tools when delegated from install (Git Bash on Windows)
if ($args.Count -gt 0) {
    for ($i = 0; $i -lt $args.Count; $i++) {
        switch ($args[$i]) {
            '--directory' { if ($i + 1 -lt $args.Count) { $Directory = $args[$i + 1]; $i++ } }
            '--tools'     { if ($i + 1 -lt $args.Count) { $Tools = $args[$i + 1]; $i++ } }
            '--yes'       { $Yes = $true }
            '--help' { $Help = $true }
            '-h'     { $Help = $true }
        }
    }
}

$REPO_URL = if ($env:LOCALSETUP_2_REPO) { $env:LOCALSETUP_2_REPO } else { 'https://github.com/cptnfren/localsetup.git' }
$FRAMEWORK_DIRNAME = '_localsetup'
$ValidTools = @('cursor', 'claude-code', 'codex', 'openclaw')

function Show-Usage {
    @'
Localsetup v2  - Front-end install script (PowerShell)

Usage:
  Interactive:    .\install.ps1
  Non-interactive: .\install.ps1 -Directory . -Tools cursor -Yes
  Help:           .\install.ps1 -Help  or  .\install.ps1 -?

Parameters:
  -Directory PATH   Client repo root (default: . or prompt)
  -Tools LIST       Comma-separated: cursor, claude-code, codex, openclaw (required with -Yes)
  -Yes              Non-interactive; no prompts
  -Help, -?, -h     Show this help and exit

Tools (use with -Tools):
  cursor       Cursor IDE (.cursor/rules, .cursor/skills)
  claude-code  Claude Code (.claude/CLAUDE.md, .claude/skills)
  codex        OpenAI Codex CLI (AGENTS.md, .agents/skills)
  openclaw     OpenClaw (skills/, _localsetup/docs/OPENCLAW_CONTEXT.md)

Examples:
  .\install.ps1 -Directory C:\repos\myapp -Tools "cursor,claude-code" -Yes
  .\install.ps1
'@
}

function Show-UsageAndExit {
    param([string]$Message)
    Write-Host "Error: $Message" -ForegroundColor Red
    Show-Usage
    exit 1
}

if ($Help) {
    Show-Usage
    exit 0
}

# Resolve target directory (client repo root)
if (-not $Directory) {
    if ($Yes) {
        $TargetDir = (Get-Location).Path
    } else {
        $inputDir = Read-Host 'Enter client repo root directory (default: .)'
        $TargetDir = if ($inputDir) { $inputDir } else { '.' }
    }
} else {
    $TargetDir = $Directory
}
try {
    $TargetDir = (Get-Item -LiteralPath $TargetDir -ErrorAction Stop).FullName
} catch {
    Show-UsageAndExit "Directory does not exist: $TargetDir"
}
$FrameworkDir = Join-Path $TargetDir $FRAMEWORK_DIRNAME

# Resolve tools
if (-not $Tools) {
    if ($Yes) {
        Show-UsageAndExit '-Tools is required when using -Yes'
    }
    Write-Host 'Select platform(s) to install (comma-separated):'
    Write-Host '  1) cursor'
    Write-Host '  2) claude-code'
    Write-Host '  3) codex'
    Write-Host '  4) openclaw'
    Write-Host 'Example: 1,2 for Cursor and Claude Code'
    $Tools = Read-Host 'Tools'
}
$ToolsNormalized = ($Tools -split ',' | ForEach-Object { $_.Trim().ToLower() }) -join ','
$ToolsNormalized = $ToolsNormalized -replace '1', 'cursor' -replace '2', 'claude-code' -replace '3', 'codex' -replace '4', 'openclaw'
$toolList = $ToolsNormalized -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
foreach ($t in $toolList) {
    if ($t -notin $ValidTools) {
        Show-UsageAndExit "Invalid tool: '$t'. Valid values: cursor, claude-code, codex, openclaw"
    }
}
if (-not $toolList -or $toolList.Count -eq 0) {
    Show-UsageAndExit 'At least one tool must be specified (e.g. -Tools cursor)'
}
$ToolsNormalized = ($toolList -join ',').Trim()

# Clone or update framework
if (Test-Path (Join-Path $FrameworkDir '.git') -PathType Container) {
    Write-Host 'Updating existing _localsetup...'
    Push-Location $FrameworkDir
    try {
        git pull --rebase 2>$null
    } finally {
        Pop-Location
    }
} else {
    Write-Host "Cloning Localsetup v2 into $FrameworkDir..."
    try {
        New-Item -ItemType Directory -Force -Path $TargetDir -ErrorAction Stop | Out-Null
        $null = git clone $REPO_URL $FrameworkDir 2>&1
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Show-UsageAndExit "Clone failed. Check network and repo URL (set LOCALSETUP_2_REPO to override)."
    }
    if (-not (Test-Path (Join-Path $FrameworkDir '.git') -PathType Container)) {
        Write-Host "Error: Clone failed. If repo is not yet published, copy the framework into $FrameworkDir and run:" -ForegroundColor Red
        Write-Host "  & '$FrameworkDir\framework\tools\deploy.ps1' -Tools '$ToolsNormalized' -Root '$TargetDir'"
        exit 1
    }
}

# Run deploy step
$DeployScript = Join-Path $FrameworkDir 'framework\tools\deploy.ps1'
if (-not (Test-Path -LiteralPath $DeployScript)) {
    $DeployScript = Join-Path $FrameworkDir 'tools\deploy.ps1'
}
if (Test-Path -LiteralPath $DeployScript) {
    try {
        & $DeployScript -Root $TargetDir -Tools $ToolsNormalized
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } catch {
        Write-Host "Error: Deploy failed. $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Error: Deploy script not found at $DeployScript" -ForegroundColor Red
    Write-Host "Run manually: & '$DeployScript' -Tools '$ToolsNormalized' -Root '$TargetDir'"
    exit 1
}

Write-Host "Done. Framework at $FrameworkDir; platform files written to $TargetDir."
