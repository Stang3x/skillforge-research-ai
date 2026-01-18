Set-Location -LiteralPath 'C:/Users/Stang3x/Documents/Gemini projects'
git add -A
$staged = git diff --cached --name-only
if ($staged) {
    git commit -m "tests(integration): add RA transcript, exemplar output, and integration tests; add minimal skills package"
} else {
    Write-Output 'No staged changes to commit'
}
git push -u origin week5-milestones
