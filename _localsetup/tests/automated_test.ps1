# Localsetup v2 - Minimal automated tests (PowerShell)
$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EngineDir = (Get-Item (Join-Path $ScriptDir '..')).FullName
Set-Location $EngineDir

. (Join-Path $EngineDir 'lib\data_paths.ps1')
$PASS = 0
$FAIL = 0

function Run-Test {
    param([scriptblock]$Condition, [string]$Name)
    try {
        $result = & $Condition
        if ($result) {
            Write-Host "[PASS] $Name"
            $script:PASS++
            return $true
        }
    } catch { }
    Write-Host "[FAIL] $Name"
    $script:FAIL++
    return $false
}

Write-Host 'Localsetup v2 - Automated tests'
Write-Host '==============================='

Run-Test { (Get-EngineDir).Length -gt 0 } 'Get-EngineDir'
Run-Test { (Get-UserDataDir).Length -gt 0 } 'Get-UserDataDir'
Run-Test { (Get-ProjectRoot).Length -gt 0 } 'Get-ProjectRoot'

. (Join-Path $EngineDir 'discovery\core\os_detector.ps1')
Run-Test { (Get-DetectedOs).Length -gt 0 } 'Get-DetectedOs'

Run-Test { Test-Path (Join-Path $EngineDir 'lib\json_formatter.sh') } 'json_formatter.sh'
Run-Test { (Test-Path (Join-Path $EngineDir 'tools\deploy')) -or (Test-Path (Join-Path $EngineDir 'tools\deploy.ps1')) } 'deploy'
Run-Test { Test-Path (Join-Path $EngineDir 'skills') -PathType Container } 'skills dir'
Run-Test { Test-Path (Join-Path $EngineDir 'templates') -PathType Container } 'templates dir'

Write-Host ''
Write-Host "Result: $PASS passed, $FAIL failed"
if ($FAIL -gt 0) { exit 1 }
exit 0
