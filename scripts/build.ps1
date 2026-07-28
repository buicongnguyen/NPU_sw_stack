[CmdletBinding()]
param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",
    [switch]$Sanitizers
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$projectRoot = Split-Path -Parent $PSScriptRoot
$imageName = "npu-sw-stack-dev:local"
$sanitizerValue = if ($Sanitizers) { "ON" } else { "OFF" }

$image = docker image inspect $imageName 2>$null
if ($LASTEXITCODE -ne 0) {
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
}

$mount = "${projectRoot}:/work"
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
        "cmake",
        "-S",
        ".",
        "-B",
        "build",
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=${Configuration}",
        "-DNPU_ENABLE_SANITIZERS=${sanitizerValue}"
    )

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
        "cmake",
        "--build",
        "build",
        "--parallel"
    )
