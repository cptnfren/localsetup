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
$MinGitVersion = [Version]'2.20.0'
$MinPythonVersion = [Version]'3.8.0'

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

function Get-ToolVersion {
    param([string]$ToolName)
    try {
        $cmd = Get-Command $ToolName -ErrorAction Stop
        return $cmd
    } catch {
        return $null
    }
}

function Get-GitVersion {
    try {
        $raw = (& git --version 2>$null)
        if ($raw -match '(\d+\.\d+(\.\d+)?)') {
            return [Version]$Matches[1]
        }
    } catch {}
    return $null
}

function Run-PreflightChecks {
    $requiredFail = $false
    $recommendFail = $false
    $gitStatus = 'MISSING'
    $pythonStatus = 'MISSING (recommended for skill validation/discovery tooling)'
    $pyyamlStatus = "MISSING (python module 'yaml')"

    $gitCmd = Get-ToolVersion -ToolName 'git'
    if ($gitCmd) {
        $gitVer = Get-GitVersion
        if ($gitVer) {
            if ($gitVer -ge $MinGitVersion) {
                $gitStatus = "OK ($gitVer)"
            } else {
                $gitStatus = "TOO OLD ($gitVer, need >= $MinGitVersion)"
                $requiredFail = $true
            }
        } else {
            $gitStatus = 'FOUND (version unknown)'
        }
    } else {
        $requiredFail = $true
    }

    $pythonCmd = Get-ToolVersion -ToolName 'python3'
    if (-not $pythonCmd) { $pythonCmd = Get-ToolVersion -ToolName 'python' }
    if ($pythonCmd) {
        try {
            $pvRaw = (& $pythonCmd.Source --version 2>&1)
            $pvText = "$pvRaw"
            $pvMatch = [regex]::Match($pvText, '(\d+\.\d+(\.\d+)?)')
            if ($pvMatch.Success) {
                $pv = [Version]$pvMatch.Groups[1].Value
                if ($pv -ge $MinPythonVersion) {
                    $pythonStatus = "OK ($pv)"
                } else {
                    $pythonStatus = "TOO OLD ($pv, recommend >= $MinPythonVersion)"
                    $recommendFail = $true
                }
            } else {
                $pythonStatus = "FOUND ($pvText)"
            }

            $null = & $pythonCmd.Source -c "import yaml" 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pyyamlStatus = 'OK (import yaml)'
            } else {
                $pyyamlStatus = "MISSING (python module 'yaml')"
                $recommendFail = $true
            }
        } catch {
            $pythonStatus = 'FOUND (version unknown)'
        }
    }

    Write-Host 'Dependency preflight:'
    Write-Host '  Required:'
    Write-Host "    - git: $gitStatus"
    Write-Host '  Recommended for full framework tooling:'
    Write-Host "    - python: $pythonStatus"
    Write-Host "    - pyyaml module: $pyyamlStatus"

    if ($requiredFail) {
        Write-Host ''
        Write-Host 'Cannot continue: required dependencies are missing or incompatible.' -ForegroundColor Red
        Write-Host 'Install/upgrade the required tools, then run install again.' -ForegroundColor Red
        exit 1
    }

    if ($recommendFail) {
        Write-Host ''
        Write-Host 'Notice: install can continue, but some skill tooling may fail until recommended dependencies are installed.' -ForegroundColor Yellow
        Write-Host 'Try one of:' -ForegroundColor Yellow
        Write-Host '  winget install Python.Python.3.12'
        Write-Host '  py -m pip install "PyYAML>=6.0"'
        Write-Host '  python -m pip install "PyYAML>=6.0"'
    }
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

Run-PreflightChecks

function Get-EngineSource {
    param([string]$BasePath)
    $candidates = @(
        (Join-Path $BasePath '_localsetup'),
        $BasePath,
        (Join-Path $BasePath 'framework')
    )
    foreach ($candidate in $candidates) {
        $deploy = Join-Path $candidate 'tools\deploy.ps1'
        if (Test-Path -LiteralPath $deploy) {
            return $candidate
        }
    }
    return $null
}

function Sync-EngineTree {
    param(
        [string]$SourceDir,
        [string]$TargetDir
    )

    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    # Keep user-local files, but replace framework-managed tree.
    foreach ($name in @('config','discovery','docs','lib','skills','templates','tests','tools')) {
        $p = Join-Path $TargetDir $name
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Recurse -Force
        }
    }
    foreach ($name in @('README.md','requirements.txt')) {
        $p = Join-Path $TargetDir $name
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Force
        }
    }

    Get-ChildItem -LiteralPath $SourceDir -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $TargetDir -Recurse -Force
    }

    # Clean legacy source-repo leftovers from older layouts.
    foreach ($name in @('_localsetup','framework','.github','.git')) {
        $p = Join-Path $TargetDir $name
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Recurse -Force
        }
    }
}

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

$sourceBase = $null
$workDir = $null
try {
    if (Test-Path (Join-Path $FrameworkDir '.git') -PathType Container) {
        Write-Host 'Updating existing _localsetup source clone...'
        Push-Location $FrameworkDir
        try {
            git pull --rebase 2>$null
        } finally {
            Pop-Location
        }
        $sourceBase = $FrameworkDir
    } elseif (Get-EngineSource -BasePath $FrameworkDir) {
        $sourceBase = $FrameworkDir
    } else {
        Write-Host 'Fetching Localsetup v2 source...'
        New-Item -ItemType Directory -Force -Path $TargetDir -ErrorAction Stop | Out-Null
        $workDir = Join-Path ([System.IO.Path]::GetTempPath()) ("localsetup-" + [Guid]::NewGuid().ToString('N'))
        $sourceBase = Join-Path $workDir 'localsetup-source'
        New-Item -ItemType Directory -Force -Path $workDir | Out-Null
        $null = git clone $REPO_URL $sourceBase 2>&1
    }

    $engineSource = Get-EngineSource -BasePath $sourceBase
    if (-not $engineSource) {
        Write-Host "Error: Could not locate framework engine in source." -ForegroundColor Red
        Write-Host "Checked for: tools\deploy.ps1, _localsetup\tools\deploy.ps1, framework\tools\deploy.ps1" -ForegroundColor Red
        exit 1
    }

    if ((Resolve-Path -LiteralPath $engineSource).Path -ne (Resolve-Path -LiteralPath $FrameworkDir -ErrorAction SilentlyContinue).Path) {
        Write-Host "Preparing single-level framework at $FrameworkDir..."
        Sync-EngineTree -SourceDir $engineSource -TargetDir $FrameworkDir
    }

    # Run deploy step from flattened install path
    $DeployScript = Join-Path $FrameworkDir 'tools\deploy.ps1'
    if (Test-Path -LiteralPath $DeployScript) {
        & $DeployScript -Root $TargetDir -Tools $ToolsNormalized
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } else {
        Write-Host "Error: Deploy script not found at '$FrameworkDir\tools\deploy.ps1'" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Show-UsageAndExit "Install failed. Check network and repo URL (set LOCALSETUP_2_REPO to override)."
} finally {
    if ($workDir -and (Test-Path -LiteralPath $workDir)) {
        Remove-Item -LiteralPath $workDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Done. Framework at $FrameworkDir; platform files written to $TargetDir."
