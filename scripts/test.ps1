[CmdletBinding()]
param(
    [ValidateSet("all", "numerics", "docs", "tooling")]
    [string]$Group = "all"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
$imageName = "npu-sw-stack-dev:local"
$mount = "${projectRoot}:/work"

if ($Group -in "all", "docs") {
    & (Join-Path $PSScriptRoot "check_docs.ps1")
}

if ($Group -in "all", "tooling") {
    & (Join-Path $PSScriptRoot "test_native_command.ps1")
}

if ($Group -in "all", "numerics") {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "Python environment missing. Run ./scripts/bootstrap.ps1 first."
    }

    Invoke-NativeCommand `
        -FilePath $venvPython `
        -ArgumentList @("-m", "pytest", "tests/python/test_numerics.py", "-q")

    & (Join-Path $PSScriptRoot "build.ps1")

    Invoke-NativeCommand `
        -FilePath "docker" `
        -ArgumentList @(
            "run",
            "--rm",
            "--volume",
            $mount,
            "--workdir",
            "/work",
            $imageName,
            "ctest",
            "--test-dir",
            "build",
            "--output-on-failure",
            "-R",
            "numerics_cpp"
        )
}
