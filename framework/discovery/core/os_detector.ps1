# Localsetup v2 - OS detection (PowerShell)
# Output: os_type|os_version|architecture (same format as os_detector.sh)
# Compatible with Windows PowerShell 5.1 and PowerShell Core 6+.

function Get-DetectedOs {
    $osType = 'unknown'
    $osVersion = 'Unknown'
    $arch = $env:PROCESSOR_ARCHITECTURE
    if (-not $arch) { $arch = 'x86_64' }

    if ($env:OS -eq 'Windows_NT') {
        $osType = 'windows'
        try {
            $caption = (Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction SilentlyContinue).Caption
            if ($caption) { $osVersion = $caption }
        } catch {
            $osVersion = 'Windows'
        }
    } elseif (Get-Variable -Name IsLinux -ErrorAction SilentlyContinue) {
        if ($IsLinux) {
            $osType = 'linux'
            if (Test-Path '/etc/os-release') {
                $content = Get-Content '/etc/os-release' -Raw -ErrorAction SilentlyContinue
                if ($content -match 'PRETTY_NAME="([^"]+)"') { $osVersion = $Matches[1] }
            }
            if ($osVersion -eq 'Unknown') { $osVersion = 'Linux' }
        }
    }
    if ($osType -eq 'unknown' -and (Get-Variable -Name IsMacOS -ErrorAction SilentlyContinue) -and $IsMacOS) {
        $osType = 'macos'
        try {
            $v = (sw_vers -productVersion 2>$null)
            if ($v) { $osVersion = $v }
        } catch { }
    }

    "$osType|$osVersion|$arch"
}
