# Repository History Rewrite Notice

Date: 2026-01-18

Action taken
- A history rewrite was performed locally and rewritten refs were force-pushed to `origin`.
- Branches rewritten: `main`, `develop`, `week5-milestones`.
- Secrets provided to the scrub script were replaced with the literal `REDACTED_SECRET` via `git filter-repo --replace-text`.

Required immediate actions for all collaborators
1. Rotate/revoke any tokens or credentials that may have been exposed prior to this rewrite.
2. Delete your existing local clones of this repository and re-clone from origin to avoid history divergence.

Recommended commands

PowerShell (recommended — fresh clone):
```powershell
# remove your local copy (optional) and re-clone
Remove-Item -Recurse -Force .\my-repo-folder
git clone https://github.com/<org-or-user>/<repo>.git
```

If you must update an existing clone (advanced — be careful):
```powershell
git fetch --all --prune
git reset --hard origin/main
git clean -fdx
```

Notes and cautions
- This rewrite is destructive: any refs (branches/tags) rewritten will no longer match pre-rewrite commits.
- After re-cloning, verify branch history and confirm that any sensitive values are no longer present.
- If you use Continuous Integration or other integrations, ensure any secrets are rotated and updated in the service configuration.

Contact
- If you need assistance coordinating the re-clone or verifying the scrub, reply here or open an issue.
