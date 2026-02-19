# Localsetup v2  - Scan directory for Agent Skills; per-skill brief and security flags.
# Usage: .\skill_importer_scan.ps1 <path>
# On Windows with Git Bash, you can run the Bash script instead: bash skill_importer_scan <path>

param([string]$Path = '')
if (-not $Path) { Write-Error 'Usage: .\skill_importer_scan.ps1 -Path <directory>'; exit 1 }
if (-not (Test-Path -LiteralPath $Path -PathType Container)) { Write-Error "Not a directory: $Path"; exit 1 }
$ScanRoot = (Get-Item -LiteralPath $Path).FullName
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ValidationScript = Join-Path $ScriptDir 'skill_validation_scan.py'

# Ensure skill validation pattern file exists and is not stale (exit 2 if stale for agent to prompt)
if ((Test-Path -LiteralPath $ValidationScript) -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
    $ensureResult = & python3 $ValidationScript --ensure-only --scan-root $ScanRoot 2>&1
    if ($LASTEXITCODE -eq 2) { $ensureResult | Write-Host -ForegroundColor Yellow; exit 2 }
    if ($LASTEXITCODE -eq 1) { $ensureResult | Write-Host; exit 1 }
}

$securityPatterns = 'eval\s*\(|curl\s+.*\|\s*sh\s|Invoke-Expression|/etc/shadow|NOPASSWD'
$count = 0
Get-ChildItem -LiteralPath $ScanRoot -Recurse -Filter 'SKILL.md' -File -ErrorAction SilentlyContinue | ForEach-Object {
    $skillDir = $_.DirectoryName
    $content = Get-Content -LiteralPath $_.FullName -Raw
    if ($content -notmatch '(?s)---\r?\nname:\s*(.+)') { return }
    $name = $Matches[1].Trim().Trim('"').Trim("'")
    $desc = if ($content -match 'description:\s*["'']?([^"''\r\n]+)') { $Matches[1] } else { '(no description)' }
    Write-Host "---"
    Write-Host "Skill: $name"
    Write-Host "Description: $desc"
    foreach ($sub in @('scripts','references','assets')) {
        $subPath = Join-Path $skillDir $sub
        if (Test-Path -LiteralPath $subPath -PathType Container) {
            Write-Host "Has $sub`:"
            Get-ChildItem -LiteralPath $subPath -Recurse -File | ForEach-Object { Write-Host "  - $($_.Name)" }
        }
    }
    $grep = Get-ChildItem -LiteralPath $skillDir -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern $securityPatterns -ErrorAction SilentlyContinue
    if ($grep) { Write-Host "Security: REVIEW (heuristic flags)"; $grep | Select-Object -First 5 | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber)" } }
    else { Write-Host "Security: No heuristic concerns" }
    # Content safety: pattern file + English-only (references only)
    if ((Test-Path -LiteralPath $ValidationScript) -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
        & python3 $ValidationScript --scan-root $ScanRoot $skillDir
        if ($LASTEXITCODE -eq 1) { Write-Host "  Content safety: ERROR (validation script failed)." -ForegroundColor Yellow }
    }
    Write-Host ""
    $script:count++
}
if ($count -eq 0) { Write-Host "No valid skills found." -ForegroundColor Yellow; exit 1 }
exit 0
