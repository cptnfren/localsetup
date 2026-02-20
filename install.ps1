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
    [ValidateSet('preserve', 'force', 'fail-on-conflict')]
    [string]$UpgradePolicy = 'preserve',
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
            '--upgrade-policy' { if ($i + 1 -lt $args.Count) { $UpgradePolicy = $args[$i + 1]; $i++ } }
            '--help' { $Help = $true }
            '-h'     { $Help = $true }
        }
    }
}

$REPO_URL = if ($env:LOCALSETUP_2_REPO) { $env:LOCALSETUP_2_REPO } else { 'https://github.com/cptnfren/localsetup.git' }
$FRAMEWORK_DIRNAME = '_localsetup'
$ValidTools = @('cursor', 'claude-code', 'codex', 'openclaw')
$MinGitVersion = [Version]'2.20.0'
$MinPythonVersion = [Version]'3.10.0'

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
  -UpgradePolicy    preserve | force | fail-on-conflict (default: preserve)
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
    $pythonStatus = 'MISSING (recommended for Python-first framework tooling)'
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
    Write-Host '  Recommended for full Python framework tooling:'
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

function Get-FileSha256 {
    param([string]$Path)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Build-Manifest {
    param([string]$Root)
    $manifest = @{}
    if (-not (Test-Path -LiteralPath $Root)) { return $manifest }
    Get-ChildItem -LiteralPath $Root -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Root.Length).TrimStart('\','/')
        $manifest[$rel] = Get-FileSha256 -Path $_.FullName
    }
    return $manifest
}

function Load-ManifestTsv {
    param([string]$Path)
    $manifest = @{}
    if (-not (Test-Path -LiteralPath $Path)) { return $manifest }
    Get-Content -LiteralPath $Path | ForEach-Object {
        if (-not $_) { return }
        $parts = $_ -split "`t", 2
        if ($parts.Count -eq 2) {
            $manifest[$parts[0]] = $parts[1]
        }
    }
    return $manifest
}

function Save-ManifestTsv {
    param(
        [hashtable]$Manifest,
        [string]$Path
    )
    $lines = $Manifest.Keys | Sort-Object | ForEach-Object { "$_`t$($Manifest[$_])" }
    Set-Content -LiteralPath $Path -Value $lines
}

function Apply-Upgrade {
    param(
        [string]$SourceDir,
        [string]$TargetDir,
        [string]$Policy,
        [string]$SourceRepo,
        [string]$SourceCommit
    )

    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $metaDir = Join-Path $TargetDir '.localsetup-meta'
    $backupDir = Join-Path $metaDir "backups/$ts"
    $oldManifestPath = Join-Path $metaDir 'managed-manifest.tsv'
    $newManifestPath = Join-Path $metaDir 'new-managed-manifest.tsv'
    New-Item -ItemType Directory -Force -Path $metaDir | Out-Null

    $oldManifest = Load-ManifestTsv -Path $oldManifestPath
    $newManifest = Build-Manifest -Root $SourceDir
    Save-ManifestTsv -Manifest $newManifest -Path $newManifestPath

    $added = New-Object System.Collections.Generic.List[string]
    $updated = New-Object System.Collections.Generic.List[string]
    $removed = New-Object System.Collections.Generic.List[string]
    $preserved = New-Object System.Collections.Generic.List[string]
    $conflicts = New-Object System.Collections.Generic.List[string]

    foreach ($rel in $newManifest.Keys) {
        $targetPath = Join-Path $TargetDir $rel
        $newSha = $newManifest[$rel]
        $oldSha = $oldManifest[$rel]

        if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) {
            $added.Add($rel) | Out-Null
            continue
        }

        $localSha = Get-FileSha256 -Path $targetPath
        if ($oldSha) {
            if ($localSha -eq $oldSha) {
                if ($newSha -ne $oldSha) { $updated.Add($rel) | Out-Null }
            } else {
                if ($newSha -eq $oldSha) {
                    if ($Policy -eq 'force') {
                        $updated.Add($rel) | Out-Null
                    } else {
                        $preserved.Add($rel) | Out-Null
                    }
                } else {
                    if ($Policy -eq 'force') {
                        $updated.Add($rel) | Out-Null
                    } else {
                        $conflicts.Add($rel) | Out-Null
                    }
                }
            }
        } else {
            if ($localSha -ne $newSha) {
                if ($Policy -eq 'force') {
                    $updated.Add($rel) | Out-Null
                } else {
                    $conflicts.Add($rel) | Out-Null
                }
            }
        }
    }

    foreach ($rel in $oldManifest.Keys) {
        if ($newManifest.ContainsKey($rel)) { continue }
        $targetPath = Join-Path $TargetDir $rel
        if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) { continue }
        $localSha = Get-FileSha256 -Path $targetPath
        if ($localSha -eq $oldManifest[$rel] -or $Policy -eq 'force') {
            $removed.Add($rel) | Out-Null
        } else {
            $conflicts.Add($rel) | Out-Null
        }
    }

    if ($conflicts.Count -gt 0 -and $Policy -eq 'fail-on-conflict') {
        Write-Host "Upgrade conflicts detected ($($conflicts.Count)). No changes applied due to -UpgradePolicy fail-on-conflict." -ForegroundColor Yellow
        $conflicts | Select-Object -First 50 | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        exit 2
    }

    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    foreach ($rel in $oldManifest.Keys) {
        $targetPath = Join-Path $TargetDir $rel
        if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) { continue }
        $backupPath = Join-Path $backupDir $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
        Copy-Item -LiteralPath $targetPath -Destination $backupPath -Force
    }

    foreach ($rel in ($added + $updated)) {
        $sourcePath = Join-Path $SourceDir $rel
        $targetPath = Join-Path $TargetDir $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $targetPath) | Out-Null
        Copy-Item -LiteralPath $sourcePath -Destination $targetPath -Force
    }
    foreach ($rel in $removed) {
        $targetPath = Join-Path $TargetDir $rel
        if (Test-Path -LiteralPath $targetPath) { Remove-Item -LiteralPath $targetPath -Force }
    }

    foreach ($name in @('_localsetup','framework','.github','.git')) {
        $p = Join-Path $TargetDir $name
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Recurse -Force
        }
    }

    Save-ManifestTsv -Manifest $newManifest -Path $oldManifestPath

    $state = @{
        installed_at    = $ts
        source_repo     = $SourceRepo
        source_commit   = $SourceCommit
        upgrade_policy  = $Policy
        manifest        = 'managed-manifest.tsv'
    }
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $metaDir 'install-state.json')

    $report = @{
        timestamp = $ts
        policy = $Policy
        source_repo = $SourceRepo
        source_commit = $SourceCommit
        target = $TargetDir
        counts = @{
            added = $added.Count
            updated = $updated.Count
            removed = $removed.Count
            preserved = $preserved.Count
            conflicts = $conflicts.Count
        }
        conflicts = $conflicts
    }
    $reportPath = Join-Path $metaDir "upgrade-report-$ts.json"
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath
    Copy-Item -LiteralPath $reportPath -Destination (Join-Path $metaDir 'upgrade-report-latest.json') -Force

    Write-Host "Upgrade report: $reportPath"
    Write-Host ("Upgrade summary: added {0}, updated {1}, removed {2}, preserved {3}, conflicts {4}." -f $added.Count, $updated.Count, $removed.Count, $preserved.Count, $conflicts.Count)
    if ($conflicts.Count -gt 0) {
        Write-Host 'Conflicts were preserved. Review upgrade report for paths.' -ForegroundColor Yellow
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
$sourceRepo = $REPO_URL
$sourceCommit = 'unknown'
try {
    Write-Host 'Fetching Localsetup v2 source...'
    New-Item -ItemType Directory -Force -Path $TargetDir -ErrorAction Stop | Out-Null
    $workDir = Join-Path ([System.IO.Path]::GetTempPath()) ("localsetup-" + [Guid]::NewGuid().ToString('N'))
    $sourceBase = Join-Path $workDir 'localsetup-source'
    New-Item -ItemType Directory -Force -Path $workDir | Out-Null
    try {
        $null = git clone $REPO_URL $sourceBase 2>&1
    } catch {
        if (Get-EngineSource -BasePath $FrameworkDir) {
            Write-Host 'Warning: Remote fetch failed; using existing local framework copy as source.' -ForegroundColor Yellow
            $sourceBase = $FrameworkDir
            $sourceRepo = 'local-existing'
        } else {
            throw
        }
    }

    $engineSource = Get-EngineSource -BasePath $sourceBase
    if (-not $engineSource) {
        Write-Host "Error: Could not locate framework engine in source." -ForegroundColor Red
        Write-Host "Checked for: tools\deploy.ps1, _localsetup\tools\deploy.ps1, framework\tools\deploy.ps1" -ForegroundColor Red
        exit 1
    }

    if (Test-Path -LiteralPath (Join-Path $sourceBase '.git')) {
        try { $sourceCommit = (git -C $sourceBase rev-parse --short HEAD 2>$null) } catch {}
    }

    Write-Host "Preparing single-level framework at $FrameworkDir..."
    Apply-Upgrade -SourceDir $engineSource -TargetDir $FrameworkDir -Policy $UpgradePolicy -SourceRepo $sourceRepo -SourceCommit $sourceCommit

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
