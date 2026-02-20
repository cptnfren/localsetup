# Localsetup v2  - Deploy step (PowerShell): write platform-specific context loaders and skills
# Usage: .\deploy.ps1 -Tools "cursor,claude-code,codex,openclaw" -Root "C:\path\to\client\repo"
# Supported platforms (canonical list): _localsetup/docs/PLATFORM_REGISTRY.md
# Requires: script in _localsetup/tools/; ROOT = client repo root.

param(
    [string]$Root = '',
    [string]$Tools = ''
)
# Support Bash-style --root/--tools when delegated from deploy (Git Bash on Windows)
if ($args.Count -gt 0) {
    for ($i = 0; $i -lt $args.Count; $i++) {
        switch ($args[$i]) {
            '--root'  { if ($i + 1 -lt $args.Count) { $Root = $args[$i + 1]; $i++ } }
            '--tools' { if ($i + 1 -lt $args.Count) { $Tools = $args[$i + 1]; $i++ } }
        }
    }
}

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrameworkDir = (Get-Item (Join-Path $ScriptDir '..')).FullName

if (-not $Root) {
    $parent = (Get-Item (Join-Path $FrameworkDir '..')).FullName
    $grandParent = (Get-Item (Join-Path $parent '..')).FullName
    $parentName = [System.IO.Path]::GetFileName($parent.TrimEnd('\', '/'))
    if ($parentName -eq '_localsetup') { $Root = $grandParent } else { $Root = $parent }
}
$Root = (Get-Item -LiteralPath $Root).FullName

$Templates = Join-Path $FrameworkDir 'templates'
$SkillsSrc = Join-Path $FrameworkDir 'skills'

function Deploy-Cursor {
    $rulesDir = Join-Path $Root '.cursor\rules'
    $skillsDir = Join-Path $Root '.cursor\skills'
    New-Item -ItemType Directory -Force -Path $rulesDir, $skillsDir | Out-Null
    $ctxMdc = Join-Path $Templates 'cursor\localsetup-context.mdc'
    $ctxIndex = Join-Path $Templates 'cursor\localsetup-context-index.md'
    if (Test-Path -LiteralPath $ctxMdc) {
        Copy-Item -LiteralPath $ctxMdc -Destination $rulesDir -Force
        Copy-Item -LiteralPath $ctxIndex -Destination $rulesDir -Force
    }
    Get-ChildItem -Path $SkillsSrc -Directory -Filter 'localsetup-*' | ForEach-Object {
        $name = $_.Name
        $dest = Join-Path $skillsDir $name
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item -Path (Join-Path $_.FullName '*') -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Deploy-ClaudeCode {
    $claudeDir = Join-Path $Root '.claude'
    $skillsDir = Join-Path $Root '.claude\skills'
    New-Item -ItemType Directory -Force -Path $claudeDir, $skillsDir | Out-Null
    $claudeMd = Join-Path $Templates 'claude-code\CLAUDE.md'
    if (Test-Path -LiteralPath $claudeMd) {
        Copy-Item -LiteralPath $claudeMd -Destination $claudeDir -Force
    }
    Get-ChildItem -Path $SkillsSrc -Directory -Filter 'localsetup-*' | ForEach-Object {
        $name = $_.Name
        $dest = Join-Path $skillsDir $name
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item -Path (Join-Path $_.FullName '*') -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Deploy-Codex {
    $skillsDir = Join-Path $Root '.agents\skills'
    New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
    $agentsMd = Join-Path $Templates 'codex\AGENTS.md'
    if (Test-Path -LiteralPath $agentsMd) {
        Copy-Item -LiteralPath $agentsMd -Destination $Root -Force
    }
    Get-ChildItem -Path $SkillsSrc -Directory -Filter 'localsetup-*' | ForEach-Object {
        $name = $_.Name
        $dest = Join-Path $skillsDir $name
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item -Path (Join-Path $_.FullName '*') -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Deploy-OpenClaw {
    $skillsDir = Join-Path $Root 'skills'
    $localsetupBase = Join-Path $Root '_localsetup'
    $docsDir = Join-Path $localsetupBase 'docs'
    New-Item -ItemType Directory -Force -Path $skillsDir, $docsDir | Out-Null
    $openclawMd = Join-Path $Templates 'openclaw\OPENCLAW_CONTEXT.md'
    if (Test-Path -LiteralPath $openclawMd) {
        Copy-Item -LiteralPath $openclawMd -Destination $docsDir -Force
    }
    Get-ChildItem -Path $SkillsSrc -Directory -Filter 'localsetup-*' | ForEach-Object {
        $name = $_.Name
        $dest = Join-Path $skillsDir $name
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item -Path (Join-Path $_.FullName '*') -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Sync docs to _localsetup/docs
$LocalsetupBase = Join-Path $Root '_localsetup'
$DocsSrc = Join-Path $FrameworkDir 'docs'
if (Test-Path -LiteralPath $DocsSrc -PathType Container) {
    $docsDest = Join-Path $LocalsetupBase 'docs'
    New-Item -ItemType Directory -Force -Path $docsDest | Out-Null
    Copy-Item -Path (Join-Path $DocsSrc '*') -Destination $docsDest -Recurse -Force -ErrorAction SilentlyContinue
}

# Main
$toolList = $Tools -split ',' | ForEach-Object { $_.Trim().ToLower() }
foreach ($t in $toolList) {
    switch ($t) {
        'cursor'      { Deploy-Cursor }
        'claude-code' { Deploy-ClaudeCode }
        'codex'       { Deploy-Codex }
        'openclaw'    { Deploy-OpenClaw }
        default       { if ($t) { Write-Error "Unknown tool: $t" } }
    }
}
