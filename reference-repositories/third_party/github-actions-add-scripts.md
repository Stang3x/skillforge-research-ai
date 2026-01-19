# GitHub Docs — "Adding scripts to your workflow"

- **Source:** https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/add-scripts
- **Type:** Official documentation (GitHub Actions)

Summary
-------
Guidance on how to run scripts stored in a repository within GitHub Actions workflows: check out the repo, set working-directory defaults, make scripts executable with `chmod` (Linux/Mac), or invoke via an interpreter on Windows runners. Examples show `run` usage, multi-line `run` blocks, and working-directory defaults.

Why this is useful
-------------------
- Directly applicable to the repository's CI workflows (PSScriptAnalyzer, exemplar harness). Helps ensure `tools/` scripts are executed portably across runners and recommends patterns to avoid permission/runtime issues.

Suggested Local Actions
-----------------------
1. Add a short `documentation/ci_scripts.md` snippet referencing canonical invocation patterns (checkout, `defaults.run.working-directory`, `chmod` or `pwsh`/`python` invocation).
2. Update workflows that run scripts to either call the interpreter explicitly (e.g., `python tools/myscript.py`) or ensure the script is executable on the runner.
