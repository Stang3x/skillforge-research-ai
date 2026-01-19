<#
Add `GITHUB_PAT` secret to this repository using the `gh` CLI and dispatch
the `benchmark.yml` workflow with `publish=true`.

Usage:
  - Install GitHub CLI (`gh`) and authenticate: `gh auth login`.
  - Run this script from the repository root in PowerShell.
  - The script prompts for the PAT (secure input), sets the secret, and
    triggers the workflow. The PAT is not stored in the repository.

Note: This script requires the `gh` CLI and permission to create repository
secrets and dispatch workflows. It does not echo the PAT to stdout.
#>

try {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Error "gh CLI not found. Install from https://cli.github.com/ and authenticate with 'gh auth login'."
        exit 1
    }

    Write-Host "This will set the GITHUB_PAT secret for the current repository and dispatch the benchmark workflow."
    $ok = Read-Host "Proceed? (y/n)"
    if ($ok -ne 'y' -and $ok -ne 'Y') {
        Write-Host "Aborted by user."
        exit 0
    }

    # Prompt for PAT securely
    $secure = Read-Host -AsSecureString "Enter your GitHub PAT (input hidden)"
    if (-not $secure) {
        Write-Error "No PAT provided. Aborting."
        exit 1
    }

    # Convert SecureString to plain text only in memory
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)

    try {
        Write-Host "Setting repository secret GITHUB_PAT (via gh)..."
        gh secret set GITHUB_PAT --body "$plain"
    } catch {
        Write-Error "Failed to set secret via gh: $_"
        # clear plain variable before exit
        $plain = $null
        Remove-Variable secure -ErrorAction SilentlyContinue
        exit 1
    }

    # Dispatch the workflow
    Write-Host "Dispatching workflow benchmark.yml with publish=true..."
    gh workflow run benchmark.yml --ref main --field publish=true

    Write-Host "Workflow dispatched. Check Actions in the repo for run status."

    # Clear sensitive data from memory
    $plain = $null
    Remove-Variable secure -ErrorAction SilentlyContinue
    if ($ptr) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }

} catch {
    Write-Error "Unexpected error: $_"
    exit 1
}
