Param(
    [string]$Path = 'reference-repositories/third_party',
    [string]$Settings = 'reference-repositories/PSScriptAnalyzerSettings.psd1',
    [switch]$FailOnError
)

Write-Host "Installing PSScriptAnalyzer (current user scope)..."
Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser

if (-not (Test-Path $Path)) {
    Write-Error "Path not found: $Path"
    exit 2
}

Write-Host "Running Invoke-ScriptAnalyzer on $Path"
$results = Invoke-ScriptAnalyzer -Path $Path -Recurse -Settings $Settings
$reportFile = "psscriptanalyzer_report.json"
$results | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $reportFile
Write-Host "Wrote report to $reportFile"

if ($FailOnError) {
    $errors = $results | Where-Object { $_.Severity -eq 'Error' }
    if ($errors) {
        Write-Host "Errors found: $($errors.Count)"
        $errors | Format-Table -AutoSize
        exit 1
    }
}

exit 0
