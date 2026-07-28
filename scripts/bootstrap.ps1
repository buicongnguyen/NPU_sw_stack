[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts/python.exe"
$imageName = "npu-sw-stack-dev:local"

if (-not (Test-Path -LiteralPath $venvPython)) {
    Invoke-NativeCommand `
        -FilePath "python" `
        -ArgumentList @("-m", "venv", $venvPath)
}

Invoke-NativeCommand `
    -FilePath $venvPython `
    -ArgumentList @(
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "-r",
        (Join-Path $projectRoot "requirements-dev.txt")
    )

Invoke-NativeCommand `
    -FilePath "docker" `
    -ArgumentList @(
        "build",
        "--tag",
        $imageName,
        "--file",
        (Join-Path $projectRoot "tools/docker/Dockerfile"),
        $projectRoot
    )

Write-Host "Bootstrap complete."
