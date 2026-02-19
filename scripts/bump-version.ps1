# Localsetup v2  - Version bump (PowerShell, Conventional Commits)
# Usage: .\bump-version.ps1 [-Major] [-Minor] [-Patch] [-MessageFile path] [-NoBump]

param(
    [switch]$Major,
    [switch]$Minor,
    [switch]$Patch,
    [string]$MessageFile = '',
    [switch]$NoBump
)

$ErrorActionPreference = 'Stop'
$RepoRoot = if ($env:GIT_DIR) { $env:GIT_DIR } else { (Get-Item (Join-Path $PSScriptRoot '..')).FullName }
$VersionFile = Join-Path $RepoRoot 'VERSION'
$SyncFiles = @(
    (Join-Path $RepoRoot 'README.md'),
    (Join-Path $RepoRoot 'framework\README.md')
)

function Read-VersionFile {
    if (Test-Path -LiteralPath $VersionFile) {
        $v = (Get-Content -LiteralPath $VersionFile -Raw).Trim()
        return $v -replace '[\r\n].*', ''
    }
    return '0.0.0'
}

function Get-BumpKindFromMessage {
    param([string]$msg)
    $firstLine = ($msg -split "`n")[0]
    if ($firstLine -match '^[a-z]+(!|\([^)]*\)!):') { return 'major' }
    if ($msg -match 'BREAKING CHANGE:') { return 'major' }
    if ($firstLine -match '^feat(\([^)]*\))?:') { return 'minor' }
    if ($firstLine -match '^(fix|docs|chore|style|refactor|perf|test|ci|build)(\([^)]*\))?:') { return 'patch' }
    return 'patch'
}

function Get-BumpedVersion {
    param([string]$current, [string]$kind)
    $parts = $current -split '\.'
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]($parts[2] -replace '-.*', '')
    switch ($kind) {
        'major' { return "$($major + 1).0.0" }
        'minor' { return "$major.$($minor + 1).0" }
        'patch' { return "$major.$minor.$($patch + 1)" }
        default { return '0.0.0' }
    }
}

function Write-VersionAndSync {
    param([string]$newVer)
    Set-Content -LiteralPath $VersionFile -Value $newVer -NoNewline
    $majorMinor = $newVer -replace '\.[0-9]+$', ''

    $pattern = [regex]::Escape('**Version:** ') + '[0-9]+\.[0-9]+\.[0-9]+'
    foreach ($f in $SyncFiles) {
        if (Test-Path -LiteralPath $f) {
            $content = Get-Content -LiteralPath $f -Raw
            $content = $content -replace $pattern, "**Version:** $newVer"
            Set-Content -LiteralPath $f -Value $content -NoNewline
        }
    }

    $versionFmPattern = '(?m)^version:\s*[\d.]+'
    foreach ($docDir in @('framework\docs', 'docs')) {
        $dir = Join-Path $RepoRoot $docDir
        if (-not (Test-Path -LiteralPath $dir -PathType Container)) { continue }
        Get-ChildItem -LiteralPath $dir -Filter '*.md' | ForEach-Object {
            $content = Get-Content -LiteralPath $_.FullName -Raw
            $content = $content -replace $versionFmPattern, "version: $majorMinor"
            Set-Content -LiteralPath $_.FullName -Value $content -NoNewline
        }
    }
}

$current = Read-VersionFile
if ($NoBump) { Write-Output $current; exit 0 }

$bumpKind = $null
if ($Major) { $bumpKind = 'major' }
elseif ($Minor) { $bumpKind = 'minor' }
elseif ($Patch) { $bumpKind = 'patch' }
elseif ($MessageFile -and (Test-Path -LiteralPath $MessageFile)) {
    $msg = Get-Content -LiteralPath $MessageFile -Raw
    if ($msg -match '(?m)^Merge ') { Write-Output $current; exit 0 }
    $bumpKind = Get-BumpKindFromMessage $msg
}

if (-not $bumpKind) {
    Write-Error 'bump-version: need -Major, -Minor, -Patch, -MessageFile path, or -NoBump'
    exit 1
}

$newVer = Get-BumpedVersion $current $bumpKind
Write-VersionAndSync $newVer
Write-Output $newVer
