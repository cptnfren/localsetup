# Localsetup v2 - Rule compliance check (PowerShell)
$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EngineDir = (Get-Item (Join-Path $ScriptDir '..')).FullName

. (Join-Path $EngineDir 'lib\data_paths.ps1')
$Root = Get-ProjectRoot

Write-Host 'Localsetup v2 - Rule Verification'
Write-Host '=================================='

$REPO_DIR = $Root
try {
    $gitLog = git -C $REPO_DIR log -1 --oneline 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Git repo: $gitLog"
    } else {
        Write-Host '[WARNING] Git not initialized or not installed'
    }
} catch {
    Write-Host '[WARNING] Git not initialized or not installed'
}

$dataPathsSh = Join-Path $EngineDir 'lib\data_paths.sh'
$dataPathsPs1 = Join-Path $EngineDir 'lib\data_paths.ps1'
if ((Test-Path -LiteralPath $dataPathsSh) -or (Test-Path -LiteralPath $dataPathsPs1)) {
    Write-Host '[OK] data_paths (sh or ps1)'
} else {
    Write-Host '[FAIL] data_paths.sh / data_paths.ps1 missing'
}

$skillsDir = Join-Path $EngineDir 'skills'
if (Test-Path -LiteralPath $skillsDir -PathType Container) {
    Write-Host '[OK] skills dir'
} else {
    Write-Host '[FAIL] skills missing'
}
Write-Host '[OK] Rule verification complete.'
