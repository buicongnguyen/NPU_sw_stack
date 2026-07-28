[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

python (Join-Path $PSScriptRoot "check_docs.py") $projectRoot
if ($LASTEXITCODE -ne 0) {
    throw "Documentation validation failed with exit code $LASTEXITCODE."
}
