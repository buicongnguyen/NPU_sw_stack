[CmdletBinding()]
param(
    [ValidateSet("all", "numerics", "docs")]
    [string]$Group = "all"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
$imageName = "npu-sw-stack-dev:local"
$mount = "${projectRoot}:/work"

if ($Group -in "all", "docs") {
    & (Join-Path $PSScriptRoot "check_docs.ps1")
}

if ($Group -in "all", "numerics") {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "Python environment missing. Run ./scripts/bootstrap.ps1 first."
    }

    & $venvPython -m pytest tests/python/test_numerics.py -q
    if ($LASTEXITCODE -ne 0) {
        throw "Python numerics tests failed."
    }

    & (Join-Path $PSScriptRoot "build.ps1")

    docker run --rm `
        --volume $mount `
        --workdir /work `
        $imageName `
        ctest --test-dir build --output-on-failure -R numerics_cpp
}
