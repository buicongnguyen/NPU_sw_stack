Set-StrictMode -Version Latest

function Invoke-NativeCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,

        [string[]]$ArgumentList = @()
    )

    & $FilePath @ArgumentList
    $nativeExitCode = $LASTEXITCODE
    if ($nativeExitCode -ne 0) {
        $renderedCommand = (@($FilePath) + $ArgumentList) -join " "
        throw "Native command failed with exit code ${nativeExitCode}: ${renderedCommand}"
    }
}
