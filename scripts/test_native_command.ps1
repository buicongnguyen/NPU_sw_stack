[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$currentShell = (Get-Process -Id $PID).Path
$observedFailure = $false

try {
    Invoke-NativeCommand `
        -FilePath $currentShell `
        -ArgumentList @("-NoProfile", "-NonInteractive", "-Command", "exit 7")
} catch {
    $observedFailure = $_.Exception.Message -match "exit code 7"
}

if (-not $observedFailure) {
    throw "Invoke-NativeCommand did not propagate the controlled exit code."
}

Write-Host "Native-command failure propagation check passed."
