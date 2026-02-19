# Localsetup v2 - Context verification (PowerShell)
$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EngineDir = (Get-Item (Join-Path $ScriptDir '..')).FullName

. (Join-Path $EngineDir 'lib\data_paths.ps1')
$Root = Get-ProjectRoot

Write-Host 'Localsetup v2 - Context Verification'
Write-Host '====================================='

$MDC = Join-Path $Root '.cursor\rules\localsetup-context.mdc'
if (Test-Path -LiteralPath $MDC) {
    $bytes = (Get-Item -LiteralPath $MDC).Length
    Write-Host "[OK] .cursor/rules/localsetup-context.mdc exists ($bytes bytes)"
} else {
    Write-Host '[FAIL] No .cursor/rules/localsetup-context.mdc found. Run install then deploy for Cursor.'
    exit 1
}
Write-Host '[OK] Context verification complete.'
