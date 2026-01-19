# Git Commit Troubleshooting (concise)

When a `git commit` fails or appears to do nothing, the following checklist diagnoses and fixes the most common causes (ordered by likelihood).

Quick triage (always run these first):

- `git status` — shows staged/unstaged/untracked files and current branch.
- `git diff --cached` — shows exactly what is staged for commit.
- `git diff` — shows unstaged changes.
- `git ls-files --others --exclude-standard` — shows untracked files that `git add -A` might have missed.

Common causes and fixes

1) Nothing to commit / already committed

- Symptom: `nothing to commit, working tree clean` after `git add -A`.
- Fix: verify you are on the intended branch (`git branch --show-current`) and that files are inside the repo root. Repeat `git add -A` and check `git status` to confirm staged files.

2) Wrong branch

- Symptom: you made changes on `main` but expected `develop`.
- Fix: switch branches (or create a branch) and commit there:

```bash
git checkout -b my-branch
git add -A
git commit -m "Your message"
```

3) Commit editor opened unexpectedly

- Symptom: running `git commit` without `-m` opened an editor and then exited with no commit.
- Fix: use `-m` to provide the message inline, or learn the editor's save/exit keys (e.g., `:wq` for vim).

```bash
git commit -m "Brief message"
```

4) Pre-commit hooks failing

- Symptom: commit aborts with hook-related errors (linters/tests failing).
- Diagnosis: check `.git/hooks/pre-commit` or project tooling like `pre-commit` config.
- Quick bypass (use sparingly):

```bash
git commit --no-verify -m "WIP: bypass hooks"
```

- Prefered fix: run the failing formatter/linter/tests locally and fix the issues (examples):

```bash
black .
python -m pip install -r requirements-dev.txt
./run-tests.sh
```

5) index.lock or other repo-level errors

- Symptom: errors mentioning `.git/index.lock` or I/O problems.
- Fix: ensure no other git process is running, then remove lock:

```bash
rm -f .git/index.lock
```

6) GPG signing or file-size limits

- Symptom: GPG signing errors or file-size-related aborts.
- Fix: use `--no-gpg-sign` for a one-off, or configure LFS for large files.

Recommended safe commit sequence

```bash
git status
git add -A
git status            # confirm "Changes to be committed"
git commit -m "Descriptive message"
```

Interactive staging (recommended when repo has many untracked files)

Use interactive patch staging to only stage documentation and CI files without touching other work:

```bash
# Stage only docs and workflow changes interactively
git add -p documentation/ .github/workflows/ documentation/*.md

# Or match markdown + CI YAMLs across the repo
git add -p '**/*.md' .github/workflows/*.yml .github/workflows/*.yaml

# After staging the hunks you want, commit normally
git commit -m "Update documentation and CI workflows"
```

If you accidentally staged everything, unstage safely before recommitting:

```bash
git reset    # unstages everything
git add -p documentation/ .github/workflows/    # re-stage selectively
```

If commits still fail, capture the exact git error and include it when seeking help (supporting logs help root-cause).

Notes for this repo

- CI may run pre-commit hooks or tests; if you see hook failures when committing locally, run the project's linters/tests before committing.
- If you previously ran `git init` in this workspace and saw terminal interruptions, a subsequent `git add`/`git commit` may require repeating the safe sequence above.

## Windows paths in Python (common gotcha)

When Python source or scripts include Windows-style paths like ".\tools\run_psscriptanalyzer.ps1" as plain string literals, Python can interpret sequences such as `\t`, `\r`, or `\U` as escape sequences and raise a `SyntaxError` (unicodeescape). To avoid this:

- Use `pathlib` and pass the `Path` object (or its string) in `subprocess.run` as a list:

```python
from pathlib import Path
import subprocess

script = Path("tools") / "run_psscriptanalyzer.ps1"
subprocess.run([str(script), "-FailOnError"], check=True)
```

- Or use forward slashes or raw strings for literals:

```python
subprocess.run(['./tools/run_psscriptanalyzer.ps1', '-FailOnError'], check=True)
script = r".\tools\run_psscriptanalyzer.ps1"
```

See `documentation/quickfix.txt` for more examples and diagnostics.

### Note for PowerShell users: `; true` pattern

Some examples and copy-pasted command chains use the Bash pattern `; true` at the end
to force a zero exit code (useful in Makefiles or CI). On Windows PowerShell this will
raise an error because `true` is treated as a boolean, not a no-op command. Instead,
use one of these PowerShell-friendly alternatives when you want "always succeed":

- Redirect stderr to null (quiet, common):

```powershell
git add .github/workflows/python-tests.yml ; git commit -m "ci: ..." 2>$null
```

- Force the last exit code to success (explicit):

```powershell
git add ... ; git commit ... ; $LASTEXITCODE = 0
```

- Use try/catch for explicit control:

```powershell
try {
	git add .github/workflows/python-tests.yml
	git commit -m "ci: set workflow permissions and expose GITHUB_TOKEN as GH_TOKEN"
} catch {}
```

Or simply omit the `; true` when running the commands interactively — it's generally
safe to run the `git add` / `git commit` sequence directly.
