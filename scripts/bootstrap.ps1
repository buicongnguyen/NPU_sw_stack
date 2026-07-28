[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts/python.exe"
$imageName = "npu-sw-stack-dev:local"

if (-not (Test-Path -LiteralPath $venvPython)) {
    python -m venv $venvPath
}

& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $projectRoot "requirements-dev.txt")

docker build `
    --tag $imageName `
    --file (Join-Path $projectRoot "tools/docker/Dockerfile") `
    $projectRoot

Write-Host "Bootstrap complete."
