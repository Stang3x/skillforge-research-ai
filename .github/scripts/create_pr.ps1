param()
$owner = 'Stang3x'
$repo = 'skillforge-research-ai'
$head = 'week5-milestones'
$base = 'develop'
$title = 'week5: add PowerShell references, demos, CI/tests'
$body = 'Adds PowerShell references, safe demos, pytest + CI workflow.'
$token = $env:GITHUB_TOKEN
if (-not $token) { $token = $env:GH_TOKEN }
if (-not $token) { Write-Output 'NO_TOKEN'; exit 0 }
$headers = @{ Authorization = "token $token"; 'User-Agent' = 'script' }
try {
    $existing = Invoke-RestMethod -Headers $headers -Method Get -Uri "https://api.github.com/repos/$owner/$repo/pulls?head=$owner`:$head&base=$base"
} catch {
    Write-Output ("ERROR: Failed to query existing PRs - " + $_.Exception.Message)
    exit 1
}
if ($existing -and $existing.Count -gt 0) {
    Write-Output ("PR_EXISTS:" + $existing[0].html_url)
    exit 0
}
$payload = @{ title = $title; head = $head; base = $base; body = $body } | ConvertTo-Json
try {
    $resp = Invoke-RestMethod -Headers $headers -Method Post -Uri "https://api.github.com/repos/$owner/$repo/pulls" -Body $payload -ContentType 'application/json'
    Write-Output ("PR_CREATED:" + $resp.html_url)
} catch {
    Write-Output ("ERROR:" + $_.Exception.Message)
    exit 1
}
